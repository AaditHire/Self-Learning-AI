"""One frozen DEV2 A-only seed-condition run; no B or replay path exists."""

from __future__ import annotations

import argparse
import json
import math
import platform
import random
import time
from pathlib import Path

import bitsandbytes as bnb
import peft
import torch
import transformers
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, get_linear_schedule_with_warmup

from preflight_phase3c_dev2 import MANIFEST, OUTPUT as PREFLIGHT, ROOT, read, sha256
from train_phase2a_qlora import RssMonitor, TokenDataset, collator, directory_hashes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--condition", choices=("isolated", "composition"), required=True)
    args = parser.parse_args()
    if not PREFLIGHT.is_file() or read(str(PREFLIGHT.relative_to(ROOT)))["status"] != "PASS_PREGRADIENT_CONTRACT":
        raise RuntimeError("Preflight missing or failed")
    cfg = read("research/protocols/phase3c_dev2_config.json")
    if sha256(MANIFEST) != read(str(PREFLIGHT.relative_to(ROOT)))["manifest_sha256"]:
        raise ValueError("Frozen manifest changed since preflight")
    if sha256(Path(__file__)) != read(str(PREFLIGHT.relative_to(ROOT)))["execution_code_sha256"]["train"]:
        raise ValueError("Training execution code changed since preflight")
    if args.seed not in cfg["seeds"]:
        raise ValueError("Unregistered seed")
    runtime = ROOT / ".runtime/phase3c_dev2"
    adapter_dir = runtime / "adapters" / str(args.seed) / args.condition
    record_path = runtime / "training" / str(args.seed) / f"{args.condition}.json"
    if adapter_dir.exists() or record_path.exists():
        raise FileExistsError(adapter_dir if adapter_dir.exists() else record_path)
    rows = read(f"data/phase3c_dev2/a_{args.condition}_training_examples.json")
    by_id = {row["example_id"]: row for row in rows}
    schedule = read("research/protocols/phase3c_dev2_schedule.json")["by_seed"][str(args.seed)]
    exposures = [epoch[f"{args.condition}_example_ids"] for epoch in schedule]
    if len(rows) != 60 or len(by_id) != 60 or len(exposures) != 3 or any(set(ids) != set(by_id) for ids in exposures):
        raise ValueError("Frozen exposure contract")
    model_cfg = cfg["base_weights"]
    model_path = ROOT / model_cfg["local_path"]
    base_before = {name: sha256(model_path / name) for name in model_cfg["weight_file_sha256"]}
    if base_before != model_cfg["weight_file_sha256"]:
        raise ValueError("Base model changed")
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    monitor = RssMonitor()
    monitor.start()
    load_start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    train = cfg["training"]
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16,
                               bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, quantization_config=quant,
                                                device_map={"": 0}, dtype=torch.float16)
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
                                           gradient_checkpointing_kwargs={"use_reentrant": False})
    lora = train["lora"]
    model = get_peft_model(model, LoraConfig(r=lora["rank"], lora_alpha=lora["alpha"], lora_dropout=lora["dropout"],
                                           bias=lora["bias"], task_type="CAUSAL_LM", target_modules=lora["target_modules"]))
    trainable = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    if trainable <= 0:
        raise RuntimeError("No trainable adapter parameters")
    loaders = [DataLoader(TokenDataset([by_id[item] for item in ids], tokenizer, system, train["max_length"]),
                          batch_size=1, shuffle=False, collate_fn=collator(tokenizer.pad_token_id)) for ids in exposures]
    load_seconds = time.perf_counter() - load_start
    torch.cuda.reset_peak_memory_stats()
    accumulation = train["gradient_accumulation_steps"]
    expected_steps = math.ceil(60 / accumulation) * train["epochs"]
    if accumulation != 8 or expected_steps != 24 or train["micro_batch_size"] != 1:
        raise ValueError("Optimizer-step contract")
    optimizer = bnb.optim.PagedAdamW8bit((p for p in model.parameters() if p.requires_grad), lr=train["learning_rate"],
                                        betas=tuple(train["adam_betas"]), eps=train["adam_epsilon"], weight_decay=train["weight_decay"])
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=min(train["warmup_steps"], max(0, expected_steps - 1)),
                                                 num_training_steps=expected_steps)
    model.train()
    optimizer.zero_grad(set_to_none=True)
    log = []
    step = supervised_tokens = full_tokens = 0
    train_start = time.perf_counter()
    for epoch, loader in enumerate(loaders, 1):
        running_loss = 0.0
        running_micro = 0
        for micro, batch in enumerate(loader, 1):
            batch = {key: value.to("cuda:0") for key, value in batch.items()}
            supervised_tokens += int((batch["labels"] != -100).sum().item())
            full_tokens += int(batch["attention_mask"].sum().item())
            loss = model(**batch).loss
            if not torch.isfinite(loss):
                raise FloatingPointError((epoch, micro, "loss"))
            (loss / accumulation).backward()
            running_loss += float(loss.detach())
            running_micro += 1
            if micro % accumulation == 0 or micro == len(loader):
                grad = float(torch.nn.utils.clip_grad_norm_((p for p in model.parameters() if p.requires_grad), train["max_grad_norm"]))
                if not math.isfinite(grad):
                    raise FloatingPointError((epoch, micro, "gradient"))
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                step += 1
                log.append({"optimizer_step": step, "epoch": epoch, "mean_micro_loss": running_loss / running_micro,
                            "grad_norm": grad, "learning_rate": scheduler.get_last_lr()[0],
                            "elapsed_seconds": time.perf_counter() - train_start})
                running_loss = 0.0
                running_micro = 0
        print(json.dumps({"condition": args.condition, "seed": args.seed, "epoch": epoch,
                          "steps_completed": step, "supervised_tokens": supervised_tokens}), flush=True)
    training_seconds = time.perf_counter() - train_start
    expected_exposure = read(str(PREFLIGHT.relative_to(ROOT)))["exposure"][args.condition]
    if step != 24 or supervised_tokens != expected_exposure["three_epoch_supervised_tokens"] or full_tokens != expected_exposure["three_epoch_full_tokens"]:
        raise RuntimeError("Observed exposure or step mismatch")
    adapter_dir.parent.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(adapter_dir, safe_serialization=True)
    tokenizer.save_pretrained(adapter_dir)
    adapter_hashes = directory_hashes(adapter_dir)
    base_after = {name: sha256(model_path / name) for name in model_cfg["weight_file_sha256"]}
    if base_after != base_before:
        raise RuntimeError("Base weights changed")
    peak_rss = monitor.stop()
    record = {"phase": "3C-DEV2", "condition": args.condition, "seed": args.seed,
              "frozen_manifest_sha256": sha256(MANIFEST), "preflight_sha256": sha256(PREFLIGHT),
              "environment": {"platform": platform.platform(), "python": platform.python_version(),
                              "torch": torch.__version__, "transformers": transformers.__version__,
                              "bitsandbytes": bnb.__version__, "peft": peft.__version__,
                              "cuda_runtime": torch.version.cuda, "gpu": torch.cuda.get_device_name(0)},
              "lineage": {"base_revision": model_cfg["revision"], "base_weight_hashes_before": base_before,
                          "base_weight_hashes_after": base_after, "exposures_by_epoch": exposures},
              "data": {"examples_per_epoch": 60, "full_tokens": full_tokens, "supervised_tokens": supervised_tokens},
              "training": {"epochs": 3, "optimizer_steps": step, "expected_optimizer_steps": expected_steps,
                           "load_seconds": load_seconds, "training_seconds": training_seconds,
                           "peak_gpu_allocated_bytes": int(torch.cuda.max_memory_allocated()),
                           "peak_process_rss_bytes": peak_rss, "trainable_parameters": trainable,
                           "nan_inf_oom": False, "log": log},
              "adapter": {"path": str(adapter_dir.relative_to(ROOT)).replace("\\", "/"), "file_hashes": adapter_hashes}}
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"condition": args.condition, "seed": args.seed, "steps": step,
                      "training_seconds": training_seconds, "adapter_sha256": adapter_hashes.get("adapter_model.safetensors")}), flush=True)


if __name__ == "__main__":
    main()
