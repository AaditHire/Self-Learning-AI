from __future__ import annotations

import argparse
import json
import math
import platform
import random
import time
from collections import Counter
from pathlib import Path

import bitsandbytes as bnb
import peft
import torch
import transformers
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, get_linear_schedule_with_warmup

from train_phase2a_qlora import RssMonitor, TokenDataset, collator, directory_hashes, sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--adapter-output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.adapter_output.exists():
        raise FileExistsError(args.adapter_output)

    config = json.loads(args.config.read_text(encoding="utf-8"))
    if args.seed not in config["seeds"]:
        raise ValueError(f"Seed is not preregistered: {args.seed}")
    expected_adapter = Path(config["training"]["adapter_outputs"][str(args.seed)])
    if args.adapter_output != expected_adapter:
        raise ValueError(f"Adapter path must be {expected_adapter}")
    for raw, expected in config["input_file_hashes"].items():
        actual = sha256(Path(raw))
        if actual != expected:
            raise ValueError(f"Frozen input hash mismatch {raw}: {actual}")

    model_cfg = config["model"]
    model_path = Path(model_cfg["local_path"])
    base_hashes = {name: sha256(model_path / name) for name in model_cfg["weight_file_sha256"]}
    if base_hashes != model_cfg["weight_file_sha256"]:
        raise ValueError("Base weight hash mismatch")
    rows = json.loads(Path(config["data"]["training_examples"]).read_text(encoding="utf-8"))

    seed = args.seed
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    monitor = RssMonitor()
    monitor.start()
    started = time.perf_counter()

    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    training = config["training"]
    dataset = TokenDataset(rows, tokenizer, Path(config["prompt"]["system"]).read_text(encoding="utf-8").strip(), training["max_length"])
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, quantization_config=quant, device_map={"": 0}, dtype=torch.float16)
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True, gradient_checkpointing_kwargs={"use_reentrant": False})
    lora = training["lora"]
    model = get_peft_model(model, LoraConfig(r=lora["rank"], lora_alpha=lora["alpha"], lora_dropout=lora["dropout"], bias=lora["bias"], task_type="CAUSAL_LM", target_modules=lora["target_modules"]))
    trainable = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    total = sum(parameter.numel() for parameter in model.parameters())
    if trainable <= 0:
        raise RuntimeError("No trainable adapter parameters")
    load_seconds = time.perf_counter() - started
    torch.cuda.reset_peak_memory_stats()

    accumulation = training["gradient_accumulation_steps"]
    generator = torch.Generator().manual_seed(seed)
    loader = DataLoader(dataset, batch_size=training["micro_batch_size"], shuffle=True, generator=generator, collate_fn=collator(tokenizer.pad_token_id))
    steps_per_epoch = math.ceil(len(loader) / accumulation)
    total_steps = steps_per_epoch * training["epochs"]
    optimizer = bnb.optim.PagedAdamW8bit((parameter for parameter in model.parameters() if parameter.requires_grad), lr=training["learning_rate"], betas=tuple(training["adam_betas"]), eps=training["adam_epsilon"], weight_decay=training["weight_decay"])
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=min(training["warmup_steps"], max(0, total_steps - 1)), num_training_steps=total_steps)
    model.train()
    optimizer.zero_grad(set_to_none=True)
    log = []
    optimizer_step = 0
    token_count = 0
    train_started = time.perf_counter()
    running_loss = 0.0
    running_micro = 0
    for epoch in range(training["epochs"]):
        for micro_index, batch in enumerate(loader, 1):
            batch = {key: value.to("cuda:0") for key, value in batch.items()}
            token_count += int((batch["labels"] != -100).sum().item())
            raw_loss = model(**batch).loss
            if not torch.isfinite(raw_loss):
                raise FloatingPointError(f"Non-finite loss at epoch {epoch + 1} micro {micro_index}")
            (raw_loss / accumulation).backward()
            running_loss += float(raw_loss.detach())
            running_micro += 1
            if micro_index % accumulation == 0 or micro_index == len(loader):
                grad_norm = float(torch.nn.utils.clip_grad_norm_((parameter for parameter in model.parameters() if parameter.requires_grad), training["max_grad_norm"]))
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                optimizer_step += 1
                log.append({"optimizer_step": optimizer_step, "epoch": epoch + 1, "mean_micro_loss": running_loss / running_micro, "learning_rate": scheduler.get_last_lr()[0], "grad_norm": grad_norm, "elapsed_seconds": time.perf_counter() - train_started, "gpu_allocated_bytes": int(torch.cuda.memory_allocated()), "gpu_reserved_bytes": int(torch.cuda.memory_reserved())})
                running_loss = 0.0
                running_micro = 0
    training_seconds = time.perf_counter() - train_started
    peak_rss = monitor.stop()
    if optimizer_step != total_steps:
        raise RuntimeError((optimizer_step, total_steps))

    args.adapter_output.parent.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.adapter_output, safe_serialization=True)
    tokenizer.save_pretrained(args.adapter_output)
    adapter_hashes = directory_hashes(args.adapter_output)
    base_hashes_after = {name: sha256(model_path / name) for name in model_cfg["weight_file_sha256"]}
    if base_hashes_after != base_hashes:
        raise RuntimeError("Immutable base weights changed")
    result = {
        "phase": "2B", "mode": "confirmatory_train", "config_sha256": sha256(args.config), "seed": seed,
        "environment": {"platform": platform.platform(), "python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__, "bitsandbytes": bnb.__version__, "peft": peft.__version__, "cuda_runtime": torch.version.cuda, "gpu": torch.cuda.get_device_name(0)},
        "model": {"id": model_cfg["id"], "revision": model_cfg["revision"], "base_weight_hashes_before": base_hashes, "base_weight_hashes_after": base_hashes_after, "trainable_parameters": trainable, "total_parameters_loaded": total},
        "data": {"examples": len(rows), "family_counts": dict(sorted(Counter(row["family"] for row in rows).items())), "supervised_tokens": token_count},
        "training": {"epochs": training["epochs"], "optimizer_steps": optimizer_step, "expected_optimizer_steps": total_steps, "load_seconds": load_seconds, "training_seconds": training_seconds, "supervised_tokens_per_second": token_count / training_seconds, "peak_gpu_allocated_bytes": int(torch.cuda.max_memory_allocated()), "peak_gpu_reserved_bytes": int(torch.cuda.max_memory_reserved()), "peak_process_rss_bytes": peak_rss, "log": log},
        "adapter": {"saved": True, "path": str(args.adapter_output).replace("\\", "/"), "file_hashes": adapter_hashes},
        "stability": {"all_losses_finite": all(math.isfinite(row["mean_micro_loss"]) and math.isfinite(row["grad_norm"]) for row in log), "completed": True},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"seed": seed, "optimizer_steps": optimizer_step, "first_loss": log[0]["mean_micro_loss"], "last_loss": log[-1]["mean_micro_loss"], "peak_gpu_allocated_bytes": result["training"]["peak_gpu_allocated_bytes"], "peak_process_rss_bytes": peak_rss, "adapter_hashes": adapter_hashes}, indent=2))


if __name__ == "__main__":
    main()
