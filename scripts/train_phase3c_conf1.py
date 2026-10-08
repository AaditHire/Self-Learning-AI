"""CONF1 training runner; authorization is checked before heavy imports."""
from __future__ import annotations

import argparse
import json
import math
import platform
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.conf1_r1.execution import (
    DEFAULT_RUNTIME, GateStop, read, require_execution_authorization, run_training_cells, sha256, training_rows,
)


def pinned_config(manifest):
    path = "research/protocols/phase3c_conf1_config_proposed.json"
    # A future authorization must bind this concrete config and prompt bytes.
    hashes = manifest.get("code_hashes", {}) | {
        p: v["sha256"] for p, v in manifest.get("authority_hashes", {}).items()}
    for name in (path, "prompts/phase1t_system.txt", "prompts/phase1t_user_template.txt"):
        if hashes.get(name) != sha256(ROOT / name):
            raise GateStop("execution config or prompt is not hash-bound", {"path": name})
    cfg = read(ROOT / path)
    model_path = ROOT / cfg["base_weights"]["local_path"]
    for name, expected in (cfg["base_weights"]["weight_file_sha256"] | cfg["tokenizer_file_sha256"]).items():
        if sha256(model_path / name) != expected:
            raise GateStop("base weight or tokenizer hash mismatch", {"path": name})
    if sha256(ROOT / cfg["compiler"]["path"]) != cfg["compiler"]["sha256"]:
        raise GateStop("compiler hash mismatch")
    return cfg


def trainer(cfg, runtime):
    import bitsandbytes as bnb
    import peft
    import torch
    import transformers
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from torch.utils.data import DataLoader
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, get_linear_schedule_with_warmup
    from train_phase2a_qlora import TokenDataset, collator, directory_hashes

    def train_cell(seed, condition, schedule, examples):
        adapter = runtime / "adapters" / str(seed) / condition
        if adapter.exists():
            raise GateStop("existing adapter; retry forbidden")
        adapter.mkdir(parents=True)
        model_path = ROOT / cfg["base_weights"]["local_path"]
        before = {name: sha256(model_path / name) for name in cfg["base_weights"]["weight_file_sha256"]}
        if before != cfg["base_weights"]["weight_file_sha256"]:
            raise GateStop("immutable base weights changed before cell")
        random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.cuda.empty_cache()
        train = cfg["training"]
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                   bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
        model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True,
            quantization_config=quant, device_map={"": 0}, dtype=torch.float16)
        model.config.use_cache = False
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
                                                gradient_checkpointing_kwargs={"use_reentrant": False})
        lora = train["lora"]
        model = get_peft_model(model, LoraConfig(r=lora["rank"], lora_alpha=lora["alpha"],
            lora_dropout=lora["dropout"], bias=lora["bias"], task_type="CAUSAL_LM", target_modules=lora["target_modules"]))
        if not any(p.requires_grad for p in model.parameters()):
            raise GateStop("no trainable adapter parameters")
        loaders = []
        for epoch in schedule["epochs"]:
            system, rows = training_rows(examples, epoch["slot_ids"])
            loaders.append(DataLoader(TokenDataset(rows, tokenizer, system, train["max_length"]),
                batch_size=1, shuffle=False, collate_fn=collator(tokenizer.pad_token_id)))
        optimizer = bnb.optim.PagedAdamW8bit((p for p in model.parameters() if p.requires_grad),
            lr=train["learning_rate"], betas=tuple(train["adam_betas"]), eps=train["adam_epsilon"],
            weight_decay=train["weight_decay"])
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=train["warmup_steps"],
                                                   num_training_steps=schedule["optimizer_steps"])
        model.train()
        optimizer.zero_grad(set_to_none=True)
        losses, log = [], []
        steps = exposures = 0
        for epoch, loader in zip(schedule["epochs"], loaders):
            for micro, batch in enumerate(loader, 1):
                batch = {k: v.to("cuda:0") for k, v in batch.items()}
                loss = model(**batch).loss
                if not torch.isfinite(loss):
                    raise GateStop("nonfinite training loss")
                losses.append(float(loss.detach()))
                exposures += 1
                (loss / epoch["loss_divisor"]).backward()
                if micro in epoch["optimizer_step_microbatches"]:
                    grad = float(torch.nn.utils.clip_grad_norm_((p for p in model.parameters() if p.requires_grad), train["max_grad_norm"]))
                    if not math.isfinite(grad):
                        raise GateStop("nonfinite training gradient")
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad(set_to_none=True)
                    steps += 1
                    log.append({"epoch": epoch["epoch"], "microbatch": micro, "step": steps, "grad_norm": grad})
        if exposures != 180 or steps != 24:
            raise GateStop("training exposure or step mismatch")
        model.save_pretrained(adapter, safe_serialization=True)
        tokenizer.save_pretrained(adapter)
        after = {name: sha256(model_path / name) for name in before}
        if before != after:
            raise GateStop("immutable base weights changed")
        record = {"exposures": exposures, "optimizer_steps": steps, "losses": losses, "log": log,
                  "adapter": {"path": str(adapter), "file_hashes": directory_hashes(adapter)},
                  "base_hashes_before": before, "base_hashes_after": after,
                  "schedule": schedule,
                  "environment": {"python": platform.python_version(), "platform": platform.platform(),
                    "torch": torch.__version__, "transformers": transformers.__version__, "peft": peft.__version__,
                    "bitsandbytes": bnb.__version__, "cuda": torch.version.cuda,
                    "gpu": torch.cuda.get_device_name(0),
                    "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
                    "cudnn_deterministic": torch.backends.cudnn.deterministic,
                    "cudnn_benchmark": torch.backends.cudnn.benchmark}}
        del model, optimizer, scheduler, loaders
        torch.cuda.empty_cache()
        return record
    return train_cell


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--check-authorization-only", action="store_true")
    args = parser.parse_args()
    try:
        manifest = require_execution_authorization(args.candidate_dir)
        if args.check_authorization_only:
            print("CONF1 authorization PASS; no model imported")
            return
        cfg = pinned_config(manifest)
        run_training_cells(args.candidate_dir, trainer(cfg, DEFAULT_RUNTIME))
    except GateStop as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__":
    main()
