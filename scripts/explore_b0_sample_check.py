"""EXPLORATORY B0-F2: sample and greedy reward availability."""
from __future__ import annotations

import ctypes
import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.conf1_r1.execution import encode_prompt, messages
from self_learning_ai.explore.pools import CATEGORIES, FAMILIES, GRAPHS, load_dev_pool, write_json
from self_learning_ai.explore.runlog import append_run
from self_learning_ai.explore.scoring import score_program

ADAPTER = ROOT / ".runtime/phase3c_conf1/adapters/20280117/isolated"


def gpu_preflight():
    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise RuntimeError("PYTHONDONTWRITEBYTECODE=1 required")

    class PowerStatus(ctypes.Structure):
        _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte),
                    ("BatteryLifePercent", ctypes.c_ubyte), ("SystemStatusFlag", ctypes.c_ubyte),
                    ("BatteryLifeTime", ctypes.c_ulong), ("BatteryFullLifeTime", ctypes.c_ulong)]

    power = PowerStatus()
    if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(power)) or power.ACLineStatus != 1:
        raise RuntimeError("STOP: machine is not confirmed on AC power")
    output = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "$p = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' } | Select-Object ProcessId,ParentProcessId,Name); ConvertTo-Json -InputObject $p -Compress; exit 0"], text=True, encoding="utf-8", errors="replace")
    processes = json.loads(output)
    by_pid = {p["ProcessId"]: (p["ParentProcessId"], p["Name"]) for p in processes}
    this_run = []
    pid = os.getpid()
    while pid in by_pid and pid not in this_run:
        this_run.append(pid)
        pid = by_pid[pid][0]
    other = [p for p in processes if p["ProcessId"] not in this_run]
    if other:
        raise RuntimeError(f"STOP: other Python processes: {other}")
    gpu_processes = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,process_name", "--format=csv,noheader"], text=True, encoding="utf-8", errors="replace").strip()
    samples = []
    for index in range(5):
        if index:
            time.sleep(1)
        output = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
                                         text=True, encoding="utf-8", errors="replace").strip()
        used, total, utilization = (float(field.strip()) for field in output.split(","))
        samples.append(dict(memory_used_mib=used, memory_total_mib=total, utilization_gpu_percent=utilization, raw=output))
    peak_used = max(s["memory_used_mib"] for s in samples)
    mean_utilization = sum(s["utilization_gpu_percent"] for s in samples) / len(samples)
    result = dict(ac_power=True, this_run_chain=[dict(ProcessId=pid, ParentProcessId=by_pid[pid][0], Name=by_pid[pid][1]) for pid in this_run],
                  other_python_processes=other, gpu_compute_processes=gpu_processes, gpu_samples=samples,
                  max_memory_used_mib=peak_used, mean_utilization_gpu_percent=mean_utilization,
                  memory_threshold_mib=1600, utilization_record_only=True)
    print(json.dumps(dict(preflight=result)), flush=True)
    reasons = []
    if peak_used > 1600:
        reasons.append(f"max memory.used {peak_used} MiB > 1600 MiB")
    if reasons:
        error = RuntimeError(f"STOP: GPU preflight: {'; '.join(reasons)}; listed apps: {gpu_processes}")
        error.preflight = result
        raise error
    return result


def hashes(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob("*")) if p.is_file()}


def load_model(adapter=ADAPTER, trainable=False):
    import numpy as np
    import torch
    from peft import PeftModel, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    cfg = json.loads((ROOT / "research/protocols/phase3c_conf1_config_proposed.json").read_bytes())
    model_path = ROOT / cfg["base_weights"]["local_path"]
    for name, wanted in (cfg["base_weights"]["weight_file_sha256"] | cfg["tokenizer_file_sha256"]).items():
        with (model_path / name).open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != wanted:
            raise RuntimeError(f"STOP: pinned model/tokenizer hash mismatch: {name}")
    if hashlib.sha256((ROOT / cfg["compiler"]["path"]).read_bytes()).hexdigest() != cfg["compiler"]["sha256"]:
        raise RuntimeError("STOP: compiler hash mismatch")
    random.seed(20291012)
    np.random.seed(20291012)
    torch.manual_seed(20291012)
    torch.cuda.manual_seed_all(20291012)
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                              bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True,
        quantization_config=quant, device_map={"": 0}, dtype=torch.float16)
    if trainable:
        model.config.use_cache = False
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
                                                gradient_checkpointing_kwargs={"use_reentrant": False})
    model = PeftModel.from_pretrained(model, adapter, is_trainable=trainable)
    model.eval()
    torch.manual_seed(20291012)
    torch.cuda.manual_seed_all(20291012)
    return model, tokenizer, cfg


def prompt_ids(tokenizer, row):
    return encode_prompt(tokenizer, messages(row["model_task_id"], row["prompt"]))


def generation_kwargs(tokenizer, count, temperature, max_new_tokens, training=False):
    kwargs = dict(do_sample=temperature > 0, num_beams=1,
                  max_new_tokens=max_new_tokens, pad_token_id=tokenizer.eos_token_id)
    if temperature > 0:
        kwargs.update(temperature=temperature, top_p=1.0, top_k=0, repetition_penalty=1.0,
                      num_return_sequences=count)
    if training:
        kwargs["use_cache"] = True
    return kwargs


def effective_settings(model, tokenizer, count, temperature, max_new_tokens, training=False):
    settings = model.generation_config.to_dict()
    settings.update(generation_kwargs(tokenizer, count, temperature, max_new_tokens, training))
    return settings


def completions(model, tokenizer, row, count, temperature, max_new_tokens, training=False):
    import torch
    ids = prompt_ids(tokenizer, row)
    input_ids = torch.tensor([ids], dtype=torch.long, device="cuda:0")
    kwargs = generation_kwargs(tokenizer, count, temperature, max_new_tokens, training)
    context = torch.no_grad if training else torch.inference_mode
    with context():
        outputs = model.generate(input_ids=input_ids, attention_mask=torch.ones_like(input_ids), **kwargs)
    eos_ids = model.generation_config.eos_token_id
    eos_ids = {eos_ids} if isinstance(eos_ids, int) else set(eos_ids)
    sequences = []
    for tokens in outputs[:, len(ids):].tolist():
        for index, token in enumerate(tokens):
            if token in eos_ids:
                tokens = tokens[:index + 1]
                break
        sequences.append(tokens)
    return ids, sequences, [tokenizer.decode(tokens, skip_special_tokens=True) for tokens in sequences]


def sample_prompts(pool):
    rng = random.Random(20291012)
    chosen = []
    for category in CATEGORIES:
        if category != "graph":
            for family in FAMILIES:
                chosen.extend(rng.sample([r for r in pool if r["category"] == category and r["family"] == family], 8))
        else:
            for graph in GRAPHS:
                buckets = [[r for r in pool if r["category"] == "graph" and r["family"] == f and r["graph"] == graph] for f in FAMILIES]
                counts = [min(2, len(bucket)) for bucket in buckets]
                for i in range(2):
                    counts[i] += min(4 - sum(counts), len(buckets[i]) - counts[i])
                if sum(counts) != 4:
                    raise ValueError(f"STOP insufficient graph prompts: {graph}")
                for bucket, n in zip(buckets, counts):
                    chosen.extend(rng.sample(bucket, n))
    return chosen


def metrics(records):
    scores = [s for row in records for s in row["scores"]]
    partial = [[s["cases_passed"] / s["cases_total"] for s in row["scores"]] for row in records]
    return dict(prompts=len(records), samples=len(scores),
                mean_sample_pass_rate=sum(s["all_pass"] for s in scores) / len(scores),
                pass_at_8=sum(any(s["all_pass"] for s in row["scores"]) for row in records) / len(records),
                compile_failure_rate=sum(not s["compiled"] for s in scores) / len(scores),
                mean_partial_reward=sum(sum(group) for group in partial) / len(scores),
                groups_with_signal=sum(len(set(group)) > 1 for group in partial) / len(records),
                greedy_pass_rate=sum(row["greedy_score"]["all_pass"] for row in records) / len(records))


def main():
    sys.stdout.reconfigure(newline="\n")
    sys.stderr.reconfigure(newline="\n")
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag")
    args = parser.parse_args()
    if args.tag and (not args.tag.isascii() or not all(c.isalnum() or c in "-_" for c in args.tag)):
        parser.error("tag must contain only ASCII letters, digits, hyphens or underscores")
    suffix = f"_{args.tag}" if args.tag else ""
    started = time.perf_counter()
    runtime = ROOT / f".runtime/explore/b0_f2{suffix}"
    summary_path = ROOT / f"research/explore/b0/f2_summary{suffix}.json"
    try:
        if runtime.exists() or summary_path.exists():
            raise FileExistsError("run folder or summary already exists")
        preflight = gpu_preflight()
        before = hashes(ADAPTER)
        pool = load_dev_pool()
        rows = sample_prompts(pool)
        model, tokenizer, cfg = load_model()
        runtime.mkdir(parents=True)
        records = []
        for row in rows:
            _, _, raw = completions(model, tokenizer, row, 8, 0.8, cfg["evaluation"]["max_new_tokens"])
            scores = [score_program(text, row["cases"]) for text in raw]
            _, _, greedy = completions(model, tokenizer, row, 1, 0, cfg["evaluation"]["max_new_tokens"])
            record = dict(task_id=row["task_id"], model_task_id=row["model_task_id"], category=row["category"],
                          family=row["family"], graph=row.get("graph"), raw_samples=raw, scores=scores,
                          greedy_raw=greedy[0], greedy_score=score_program(greedy[0], row["cases"]))
            write_json(runtime / f"{row['model_task_id']}.json", record)
            records.append(record)
            print(f"F2 {len(records)}/64 {row['task_id']}: {sum(s['all_pass'] for s in scores)}/8", flush=True)
        if before != hashes(ADAPTER):
            raise RuntimeError("STOP: source adapter changed")
        summary = dict(label="EXPLORATORY", seed=20291012, preflight=preflight,
                       model=cfg["base_weights"], adapter=ADAPTER.relative_to(ROOT).as_posix(),
                       adapter_hashes=before, source_adapter_unchanged=True,
                       tag=args.tag,
                       generation_settings=dict(sampled=effective_settings(model, tokenizer, 8, 0.8, cfg["evaluation"]["max_new_tokens"]),
                                                greedy=effective_settings(model, tokenizer, 1, 0, cfg["evaluation"]["max_new_tokens"])),
                       categories={c: metrics([r for r in records if r["category"] == c]) for c in CATEGORIES},
                       graphs={g: metrics([r for r in records if r["graph"] == g]) for g in GRAPHS},
                       prompt_counts={c: {f: sum(r["category"] == c and r["family"] == f for r in records) for f in FAMILIES} for c in CATEGORIES},
                       seconds=time.perf_counter() - started)
        write_json(summary_path, summary)
        append_run(dict(run="b0_f2", status="PASS", summary=summary))
    except Exception as exc:
        append_run(dict(run="b0_f2", tag=args.tag, status="FAIL", error=repr(exc), preflight=getattr(exc, "preflight", None)))
        raise


if __name__ == "__main__":
    main()
