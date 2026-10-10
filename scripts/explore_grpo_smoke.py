"""EXPLORATORY B0-F1: three minimal group-relative LoRA updates."""
from __future__ import annotations

import gc
import argparse
import hashlib
import json
import math
import random
import shutil
import sys
import time
from pathlib import Path

from explore_b0_sample_check import (
    ADAPTER, ROOT, completions, effective_settings, gpu_preflight, hashes, load_model,
)
from self_learning_ai.explore.pools import load_dev_pool, write_json
from self_learning_ai.explore.runlog import append_run
from self_learning_ai.explore.scoring import score_program


def attempt(adapter, group_size, prompts_per_step, runtime):
    import torch
    import bitsandbytes as bnb
    model, tokenizer, cfg = load_model(adapter, trainable=True)
    parameters = {name: p for name, p in model.named_parameters() if p.requires_grad}
    if not parameters or any("lora_" not in name for name in parameters):
        raise RuntimeError("STOP: trainable parameters must be LoRA only")
    initial = {name: p.detach().float().cpu().clone() for name, p in parameters.items()}
    optimizer = bnb.optim.PagedAdamW8bit(parameters.values(), lr=2e-5,
                                     betas=(0.9, 0.999), eps=1e-8, weight_decay=0)
    rows = [r for r in load_dev_pool() if r["category"] == "pair_and"]
    rng = random.Random(20291012)
    steps = []
    torch.cuda.reset_peak_memory_stats()
    for step_index in range(3):
        step_started = time.perf_counter()
        generation_seconds = scoring_seconds = 0.0
        groups = []
        all_samples = []
        raw_records = []
        model.eval()
        for row in rng.sample(rows, prompts_per_step):
            torch.cuda.synchronize()
            started = time.perf_counter()
            ids, tokens, raw = completions(model, tokenizer, row, group_size, 1.0, cfg["evaluation"]["max_new_tokens"], training=True)
            torch.cuda.synchronize()
            generation_seconds += time.perf_counter() - started
            started = time.perf_counter()
            scores = [score_program(text, row["cases"]) for text in raw]
            rewards = [s["cases_passed"] / s["cases_total"] if s["compiled"] else 0.0 for s in scores]
            scoring_seconds += time.perf_counter() - started
            mean = sum(rewards) / group_size
            std = math.sqrt(sum((r - mean) ** 2 for r in rewards) / group_size)
            advantages = [(r - mean) / (std + 1e-4) for r in rewards]
            if std > 0:
                groups.extend((ids, sequence, a) for sequence, a in zip(tokens, advantages))
            all_samples.extend((ids, sequence) for sequence in tokens)
            raw_records.append(dict(task_id=row["task_id"], model_task_id=row["model_task_id"], raw_samples=raw,
                                    scores=scores, rewards=rewards, advantages=advantages, std=std, skipped=std == 0))
        signal_groups = len(groups) // group_size
        synthetic_backward = not groups
        if synthetic_backward:
            groups = [(ids, sequence, 1.0 if i % 2 == 0 else -1.0)
                      for i, (ids, sequence) in enumerate(all_samples)]
        torch.cuda.empty_cache()
        model.train()
        model.config.use_cache = False
        optimizer.zero_grad(set_to_none=True)
        started = time.perf_counter()
        loss_value = 0.0
        # One completion per micro-batch; divide each contribution by the number
        # of samples in non-skipped groups before accumulating the gradient.
        for ids, sequence, advantage in groups:
            if not sequence:
                raise RuntimeError("STOP: empty completion")
            full = torch.tensor([ids + sequence], dtype=torch.long, device="cuda:0")
            output = model(input_ids=full, attention_mask=torch.ones_like(full), use_cache=False,
                           logits_to_keep=len(sequence) + 1)
            logits = output.logits[:, :-1, :].float()
            targets = full[:, len(ids):]
            token_log_probs = -torch.nn.functional.cross_entropy(
                logits.reshape(-1, logits.shape[-1]), targets.reshape(-1), reduction="none")
            loss = -advantage * token_log_probs.mean() / len(groups)
            if not torch.isfinite(loss):
                raise RuntimeError("STOP: non-finite loss")
            loss.backward()
            loss_value += loss.detach().item()
            del output, logits, full, targets, token_log_probs, loss
        gradients_finite = all(p.grad is None or bool(torch.isfinite(p.grad).all()) for p in parameters.values())
        if not gradients_finite:
            raise RuntimeError("STOP: non-finite gradient")
        if not synthetic_backward:
            optimizer.step()
        torch.cuda.synchronize()
        backward_seconds = time.perf_counter() - started
        weight_l2 = math.sqrt(sum(float(((p.detach().float().cpu() - initial[name]) ** 2).sum()) for name, p in parameters.items()))
        record = dict(step=step_index + 1, generation_seconds=generation_seconds,
                      scoring_seconds=scoring_seconds, backward_seconds=backward_seconds,
                      total_seconds=time.perf_counter() - step_started, loss=loss_value,
                      finite_loss=math.isfinite(loss_value), gradients_finite=gradients_finite,
                      groups_with_signal=signal_groups, skipped_groups=prompts_per_step - signal_groups,
                      synthetic_backward=synthetic_backward, optimizer_update=not synthetic_backward,
                      cumulative_weight_change_l2=weight_l2,
                      max_memory_allocated_bytes=torch.cuda.max_memory_allocated(),
                      max_memory_reserved_bytes=torch.cuda.max_memory_reserved())
        write_json(runtime / f"step_{step_index + 1}.json", dict(record, groups=raw_records))
        steps.append(record)
        print(f"F1 step {step_index + 1}: {record}", flush=True)
    result = dict(status="PASS", group_size=group_size, prompts_per_step=prompts_per_step,
                  micro_batch_completions=1, steps=steps, weight_change_l2=steps[-1]["cumulative_weight_change_l2"],
                  weights_changed=steps[-1]["cumulative_weight_change_l2"] > 0,
                  all_losses_finite=all(s["finite_loss"] for s in steps),
                  real_signal_steps=sum(not s["synthetic_backward"] for s in steps),
                  synthetic_steps=sum(s["synthetic_backward"] for s in steps),
                  generation_settings=effective_settings(model, tokenizer, group_size, 1.0, cfg["evaluation"]["max_new_tokens"], training=True),
                  max_memory_allocated_bytes=torch.cuda.max_memory_allocated(),
                  max_memory_reserved_bytes=torch.cuda.max_memory_reserved())
    del model, optimizer, parameters
    gc.collect()
    torch.cuda.empty_cache()
    return result


def main():
    sys.stdout.reconfigure(newline="\n")
    sys.stderr.reconfigure(newline="\n")
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag")
    args = parser.parse_args()
    if args.tag and (not args.tag.isascii() or not all(c.isalnum() or c in "-_" for c in args.tag)):
        parser.error("tag must contain only ASCII letters, digits, hyphens or underscores")
    suffix = f"_{args.tag}" if args.tag else ""
    runtime = ROOT / f".runtime/explore/b0_f1{suffix}"
    summary_path = ROOT / f"research/explore/b0/f1_summary{suffix}.json"
    attempts = []
    try:
        if runtime.exists() or summary_path.exists():
            raise FileExistsError("run folder or summary already exists")
        preflight = gpu_preflight()
        before = hashes(ADAPTER)
        adapter = runtime / "adapter_init"
        def copy_lf(source, destination):
            source = Path(source)
            destination = Path(destination)
            data = source.read_bytes()
            if source.suffix in {".json", ".md", ".txt", ".jinja"}:
                data = data.replace(b"\r\n", b"\n")
            destination.write_bytes(data)
            return str(destination)
        shutil.copytree(ADAPTER, adapter, copy_function=copy_lf)
        expected_copy = {p.relative_to(ADAPTER).as_posix(): hashlib.sha256(
            p.read_bytes().replace(b"\r\n", b"\n") if p.suffix in {".json", ".md", ".txt", ".jinja"}
            else p.read_bytes()).hexdigest() for p in ADAPTER.rglob("*") if p.is_file()}
        initial_copy_hashes = hashes(adapter)
        if initial_copy_hashes != expected_copy:
            raise RuntimeError("STOP: adapter copy hash mismatch")
        import torch
        for number, (g, n) in enumerate(((8, 2), (4, 1)), 1):
            output = runtime / f"attempt_{number}"
            output.mkdir()
            try:
                result = attempt(adapter, g, n, output)
                attempts.append(result)
                append_run(dict(run="b0_f1_attempt", attempt=number, status="PASS", result=result))
                break
            except torch.cuda.OutOfMemoryError as exc:
                result = dict(status="OOM", group_size=g, prompts_per_step=n, error=str(exc),
                              completed_steps=[json.loads(p.read_bytes()) for p in sorted(output.glob("step_*.json"))],
                              max_memory_allocated_bytes=torch.cuda.max_memory_allocated(),
                              max_memory_reserved_bytes=torch.cuda.max_memory_reserved())
                attempts.append(result)
                write_json(output / "oom.json", result)
                append_run(dict(run="b0_f1_attempt", attempt=number, **result))
                if number == 2:
                    raise
            # Outside the except block: release the traceback and its model
            # tensors before loading the one authorized smaller retry.
            gc.collect()
            torch.cuda.empty_cache()
        if hashes(ADAPTER) != before or hashes(adapter) != initial_copy_hashes:
            raise RuntimeError("STOP: initial adapter changed")
        summary = dict(label="EXPLORATORY", tag=args.tag, preflight=preflight, attempts=attempts, oom_retry=len(attempts) > 1,
                       original_adapter_unchanged=True, original_adapter_hashes=before,
                       initial_adapter_hashes=initial_copy_hashes, copied_text_newlines="LF",
                       reward="cases_passed/5 if compiled, else 0", group_std="population std",
                       optimizer="bitsandbytes.optim.PagedAdamW8bit", learning_rate=2e-5,
                       betas=[0.9, 0.999], eps=1e-8, weight_decay=0, no_kl=True,
                       zero_variance_groups_skipped=True, synthetic_backward_if_no_signal=True)
        write_json(summary_path, summary)
        append_run(dict(run="b0_f1", status="PASS", summary=summary))
    except Exception as exc:
        append_run(dict(run="b0_f1", tag=args.tag, status="FAIL", attempts=attempts, error=repr(exc), preflight=getattr(exc, "preflight", None)))
        raise


if __name__ == "__main__":
    main()
