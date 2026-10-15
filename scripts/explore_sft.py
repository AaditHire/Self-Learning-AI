"""EXPLORATORY SFT continuation on a byte-exact private adapter copy."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.explore.pools import load_dev_pool, write_json
from self_learning_ai.explore.runlog import append_run
from explore_b0_sample_check import ADAPTER, gpu_preflight, hashes

SEED = 20291014


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def lora_settings(rank=16):
    lora = json.loads((ROOT / "research/protocols/phase3a_config.json").read_bytes())["training"]["lora"]
    return dict(r=rank, lora_alpha=2 * rank, lora_dropout=lora["dropout"],
                bias=lora["bias"], task_type="CAUSAL_LM", target_modules=lora["target_modules"])


def train(args):
    started = time.perf_counter()
    runtime, summary_path = args.output_dir.resolve(), args.summary.resolve()
    if runtime.exists() or summary_path.exists():
        raise FileExistsError("SFT runtime or summary already exists")
    preflight = gpu_preflight()
    import bitsandbytes as bnb
    import peft
    import torch
    import transformers
    from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
    from torch.utils.data import DataLoader
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, get_linear_schedule_with_warmup
    from train_phase2a_qlora import TokenDataset, collator

    cfg = json.loads((ROOT / "research/protocols/phase3c_conf1_config_proposed.json").read_bytes())
    model_path = ROOT / cfg["base_weights"]["local_path"]
    pinned = cfg["base_weights"]["weight_file_sha256"] | cfg["tokenizer_file_sha256"]
    before_base = {name: sha256(model_path / name) for name in pinned}
    if before_base != pinned or sha256(ROOT / cfg["compiler"]["path"]) != cfg["compiler"]["sha256"]:
        raise RuntimeError("STOP pinned model/tokenizer/compiler hash mismatch")
    source_adapter = None if args.fresh_lora else args.init_adapter.resolve()
    before_adapter = {} if args.fresh_lora else hashes(source_adapter)
    if not args.fresh_lora and not before_adapter:
        raise FileNotFoundError("source adapter missing")
    adapter_init, adapter_final = runtime / "adapter_init", runtime / "adapter_final"
    if not args.fresh_lora:
        shutil.copytree(source_adapter, adapter_init)
        if hashes(adapter_init) != before_adapter:
            raise RuntimeError("STOP byte-exact adapter copy hash mismatch")
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.cuda.empty_cache()
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    rows = load_dev_pool(args.data)
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    dataset = TokenDataset(rows, tokenizer, system, 320)
    if not len(dataset):
        raise ValueError("empty training dataset")
    print(f"SFT tokens PASS: {len(dataset)} examples, max {max(len(r['input_ids']) for r in dataset.items)}", flush=True)
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                              bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True,
        quantization_config=quant, device_map={"": 0}, dtype=torch.float16)
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
                                            gradient_checkpointing_kwargs={"use_reentrant": False})
    if args.fresh_lora:
        torch.manual_seed(args.seed)
        torch.cuda.manual_seed_all(args.seed)
        model = get_peft_model(model, LoraConfig(**lora_settings(args.lora_rank)))
    else:
        model = PeftModel.from_pretrained(model, adapter_init, is_trainable=True)
    parameters = [p for p in model.parameters() if p.requires_grad]
    if not parameters:
        raise RuntimeError("STOP no trainable adapter parameters")
    optimizer = bnb.optim.PagedAdamW8bit(parameters, lr=2e-4, betas=(0.9, 0.999), eps=1e-8, weight_decay=0)
    steps_per_epoch = math.ceil(len(dataset) / 8)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=args.warmup_steps, num_training_steps=args.epochs * steps_per_epoch)
    torch.cuda.reset_peak_memory_stats()
    model.train()
    optimizer.zero_grad(set_to_none=True)
    losses, log, orders = [], [], []
    exposures = steps = 0
    train_started = time.perf_counter()
    for epoch in range(args.epochs):
        order = list(range(len(dataset)))
        random.Random(args.seed + 100003 * epoch).shuffle(order)
        orders.append([rows[i]["example_id"] for i in order])
        loader = DataLoader(dataset, batch_size=1, sampler=order, collate_fn=collator(tokenizer.pad_token_id))
        for micro, batch in enumerate(loader, 1):
            batch = {key: value.to("cuda:0") for key, value in batch.items()}
            loss = model(**batch).loss
            if not torch.isfinite(loss):
                raise FloatingPointError("STOP nonfinite training loss")
            losses.append(float(loss.detach()))
            exposures += 1
            (loss / 8).backward()
            if micro % 8 == 0 or micro == len(loader):
                grad = float(torch.nn.utils.clip_grad_norm_(parameters, 1.0))
                if not math.isfinite(grad):
                    raise FloatingPointError("STOP nonfinite training gradient")
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                steps += 1
                record = dict(epoch=epoch, microbatch=micro, optimizer_step=steps,
                              mean_micro_loss=sum(losses[-(micro % 8 or 8):]) / (micro % 8 or 8),
                              grad_norm=grad, learning_rate=scheduler.get_last_lr()[0],
                              seconds=time.perf_counter() - train_started)
                log.append(record)
                print(f"SFT {steps}/{args.epochs * steps_per_epoch} epoch={epoch} loss={record['mean_micro_loss']:.6f}", flush=True)
    train_seconds = time.perf_counter() - train_started
    if exposures != args.epochs * len(dataset) or steps != args.epochs * steps_per_epoch:
        raise RuntimeError("STOP exposure/optimizer-step mismatch")
    model.save_pretrained(adapter_final, safe_serialization=True)
    tokenizer.save_pretrained(adapter_final)
    # New generated text is LF-only; the byte-exact initialization copy is untouched.
    for path in adapter_final.rglob("*"):
        if path.is_file() and path.suffix in (".json", ".txt", ".md"):
            raw = path.read_bytes()
            if b"\r\n" in raw:
                path.write_bytes(raw.replace(b"\r\n", b"\n"))
    if not args.fresh_lora and (hashes(source_adapter) != before_adapter or hashes(adapter_init) != before_adapter):
        raise RuntimeError("STOP source or initialization adapter changed")
    after_base = {name: sha256(model_path / name) for name in pinned}
    if after_base != before_base:
        raise RuntimeError("STOP immutable base/tokenizer changed")
    summary = dict(label="EXPLORATORY", seed=args.seed, preflight=preflight,
                   data=args.data.as_posix(), data_sha256=sha256(args.data), examples=len(rows),
                   source_adapter=source_adapter.as_posix() if source_adapter else None, source_adapter_hashes=before_adapter,
                   source_adapter_unchanged=True if not args.fresh_lora else None,
                   source_adapter_check="skipped_fresh_lora" if args.fresh_lora else "PASS",
                   fresh_lora=args.fresh_lora, adapter_init_hashes=hashes(adapter_init),
                   adapter_final=adapter_final.as_posix(), adapter_final_hashes=hashes(adapter_final),
                   base_hashes_before=before_base, base_hashes_after=after_base,
                   recipe=dict(quantization="NF4", compute_dtype="fp16", double_quant=True,
                               use_reentrant=False, optimizer="PagedAdamW8bit", learning_rate=2e-4,
                               betas=[0.9, 0.999], epsilon=1e-8, weight_decay=0,
                               scheduler="linear", warmup_steps=args.warmup_steps, max_grad_norm=1.0,
                               micro_batch_size=1, gradient_accumulation_steps=8, epochs=args.epochs, max_length=320,
                               lora_rank=model.peft_config["default"].r,
                               lora_alpha=model.peft_config["default"].lora_alpha,
                               epoch_shuffle_seeds=[args.seed + 100003 * e for e in range(args.epochs)]),
                   exposures=exposures, optimizer_steps=steps, losses=losses, log=log, epoch_orders=orders,
                   first_loss=losses[0], last_loss=losses[-1],
                   peak_gpu_allocated_bytes=int(torch.cuda.max_memory_allocated()),
                   peak_gpu_reserved_bytes=int(torch.cuda.max_memory_reserved()),
                   training_seconds=train_seconds, seconds=time.perf_counter() - started,
                   environment=dict(python=platform.python_version(), platform=platform.platform(),
                                    torch=torch.__version__, transformers=transformers.__version__,
                                    peft=peft.__version__, bitsandbytes=bnb.__version__,
                                    cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0)))
    write_json(summary_path, summary)
    append_run(dict(run=args.run_name, status="PASS", summary=summary))
    print(f"SFT PASS: first={losses[0]}, last={losses[-1]}, minutes={summary['seconds'] / 60}", flush=True)


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".runtime/explore/da_sft")
    parser.add_argument("--summary", type=Path, default=ROOT / "research/explore/da/sft_summary.json")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--run-name", default="da_sft")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--warmup-steps", type=int, default=5)
    parser.add_argument("--lora-rank", type=int, default=16)
    initialization = parser.add_mutually_exclusive_group()
    initialization.add_argument("--init-adapter", type=Path, default=ADAPTER)
    initialization.add_argument("--fresh-lora", action="store_true")
    return parser


def main():
    sys.stdout.reconfigure(newline="\n")
    sys.stderr.reconfigure(newline="\n")
    parser = argument_parser()
    args = parser.parse_args()
    try:
        train(args)
    except Exception as exc:
        append_run(dict(run=args.run_name, seed=args.seed, status="FAIL", error=repr(exc), preflight=getattr(exc, "preflight", None)))
        raise


if __name__ == "__main__":
    main()
