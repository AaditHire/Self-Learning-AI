"""One authorized, non-scientific infrastructure smoke on consumed DEV2 only."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime/phase3c_conf1_smoke"
EVIDENCE = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE/infrastructure_smoke.json"
SEED = 20280117
CHECKS = ("imports_ok", "weights_and_tokenizer_hashes_ok", "training_contract_ok",
          "base_immutable_ok", "adapter_hashes_ok", "generation_ok", "scoring_ok",
          "rng_reset_ok", "repeat_generation_identical")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def main():
    sys.dont_write_bytecode = True
    RUNTIME.mkdir(parents=True, exist_ok=True)
    # Exclusive marker prevents any second invocation, including after failure.
    with (RUNTIME / "smoke.started").open("x", encoding="utf-8") as handle:
        handle.write("One training cell; at most nine generations; no retry.\n")
    scratch = RUNTIME / "tmp"
    scratch.mkdir(exist_ok=True)
    tempfile.tempdir = str(scratch)
    for key, folder in {
        "TEMP": "tmp", "TMP": "tmp", "TMPDIR": "tmp", "HF_HOME": "hf",
        "HF_HUB_CACHE": "hf/hub", "TRANSFORMERS_CACHE": "hf/transformers",
        "TORCH_HOME": "torch", "TORCH_EXTENSIONS_DIR": "torch_extensions",
        "TRITON_CACHE_DIR": "triton", "CUDA_CACHE_PATH": "cuda_cache",
        "XDG_CACHE_HOME": "cache", "MPLCONFIGDIR": "matplotlib",
        "NUMBA_CACHE_DIR": "numba",
    }.items():
        path = RUNTIME / folder
        path.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(path)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["PYTHONPYCACHEPREFIX"] = str(RUNTIME / "pycache")
    sys.path.insert(0, str(ROOT / "src"))

    def audit(event, args):
        paths = []
        if event == "open":
            path, mode, flags = args
            if isinstance(path, (str, bytes, os.PathLike)):
                if (mode and any(c in mode for c in "wax+")) or flags & (
                        os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                    paths = [path]
        elif event in {"os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.utime"}:
            paths = [args[0]]
        elif event in {"os.rename", "os.link", "os.symlink"}:
            paths = list(args[:2])
        for path in paths:
            resolved = Path(os.fsdecode(path)).resolve()
            if not resolved.is_relative_to(RUNTIME) and resolved != EVIDENCE:
                raise RuntimeError(f"STOP: attempted write outside smoke scope: {resolved}")

    sys.addaudithook(audit)
    evidence = {
        "status": "INFRASTRUCTURE_SMOKE_NON_SCIENTIFIC_CONSUMED_DEV2_DATA",
        "command": "python -B scripts/smoke_phase3c_conf1_infrastructure.py",
        "start_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "script_sha256_as_run": digest(__file__),
        "checks": dict.fromkeys(CHECKS, False), "completed_checks": [],
        "exceptions": [], "generations": [], "generation_calls": 0,
        "non_scientific_pass_counts": {"passed": 0, "scored": 0},
        "wall_seconds": {}, "peak_gpu_memory_bytes": {},
        "environment": {"python": platform.python_version(), "executable": sys.executable},
        "training_record": None,
    }
    for name in ("torch", "transformers", "peft", "bitsandbytes", "numpy"):
        try:
            evidence["environment"][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            evidence["environment"][name] = None
    start = time.perf_counter()
    stage = "imports_ok"
    torch = None

    def check(name, value):
        evidence["checks"][name] = bool(value)
        evidence["completed_checks"].append(name)
        if not value:
            raise RuntimeError(f"STOP: {name} failed")

    def timed(name, function):
        began = time.perf_counter()
        try:
            return function()
        finally:
            evidence["wall_seconds"][name] = time.perf_counter() - began

    def peak(name):
        if torch is not None and torch.cuda.is_available():
            evidence["peak_gpu_memory_bytes"][name] = {
                "allocated": torch.cuda.max_memory_allocated(0),
                "reserved": torch.cuda.max_memory_reserved(0)}

    try:
        print("Smoke: imports", flush=True)
        import numpy as np
        import torch
        import bitsandbytes
        import peft
        import transformers
        from self_learning_ai.conf1_r1 import execution, schedule
        from self_learning_ai.compiler import GocoCompiler
        from train_phase3c_conf1 import trainer
        from evaluate_phase3c_conf1 import generator
        check(stage, True)
        evidence["environment"].update(
            cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0),
            deterministic_algorithms=torch.are_deterministic_algorithms_enabled(),
            cudnn_deterministic=torch.backends.cudnn.deterministic,
            cudnn_benchmark=torch.backends.cudnn.benchmark)
        evidence["environment"]["driver_query"] = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=driver_version,name", "--format=csv,noheader"], text=True).strip()
        stage = "weights_and_tokenizer_hashes_ok"
        cfg = read("research/protocols/phase3c_conf1_config_proposed.json")
        model_path = ROOT / cfg["base_weights"]["local_path"]
        expected = cfg["base_weights"]["weight_file_sha256"] | cfg["tokenizer_file_sha256"]
        actual = timed("hash_verification", lambda: {name: digest(model_path / name) for name in expected})
        evidence["verified_hashes"] = actual
        evidence["compiler_sha256"] = digest(ROOT / cfg["compiler"]["path"])
        check(stage, actual == expected and evidence["compiler_sha256"] == cfg["compiler"]["sha256"])
        original = read("data/phase3c_dev2/a_isolated_training_examples.json")
        if len(original) != 60:
            raise RuntimeError("STOP: DEV2 training example count")
        examples = [dict(model_task_id=f"SMOKE-{i:02d}", prompt=row["prompt"], target=row["target"],
                         messages=execution.messages(f"SMOKE-{i:02d}", row["prompt"]))
                    for i, row in enumerate(original, 1)]
        plan = schedule.training_schedule(SEED)
        bijection = {sid: f"SMOKE-{i:02d}" for i, sid in enumerate(schedule.SLOT_IDS, 1)}
        for epoch in plan["epochs"]:
            epoch["slot_ids"] = [bijection[sid] for sid in epoch["slot_ids"]]
        stage = "training_contract_ok"
        train_cell = trainer(cfg, RUNTIME)
        torch.cuda.reset_peak_memory_stats(0)
        print("Smoke: one training cell", flush=True)
        try:
            record = timed("training", lambda: train_cell(SEED, "isolated", plan, examples))
        finally:
            peak("training")
        record = dict(record, seed=SEED, condition="isolated")
        evidence["training_record"] = record
        check(stage, record["exposures"] == 180 and record["optimizer_steps"] == 24
              and len(record["losses"]) == 180 and all(math.isfinite(v) for v in record["losses"]))
        stage = "base_immutable_ok"
        check(stage, record["base_hashes_before"] == record["base_hashes_after"])
        store = execution.CheckpointStore(RUNTIME)
        stem = f"training/{SEED}/isolated"
        receipt = store.write(stem + ".json", record)
        store.write(stem + ".sha256.json", {"sha256": receipt})
        stage = "adapter_hashes_ok"
        adapter = Path(record["adapter"]["path"])
        hashes = {p.relative_to(adapter).as_posix(): digest(p) for p in adapter.rglob("*") if p.is_file()}
        check(stage, bool(hashes) and hashes == record["adapter"]["file_hashes"])
        stage = "generation_ok"
        generate, reset = generator(cfg, RUNTIME)
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        compiler = GocoCompiler(ROOT / cfg["compiler"]["java"], ROOT / cfg["compiler"]["path"],
            timeout_seconds=cfg["evaluation"]["compiler_timeout_seconds"],
            output_limit_bytes=cfg["evaluation"]["output_limit_bytes_per_stream"])
        score = execution.compiler_score(compiler)
        tasks = read("benchmark/phase3c_dev2/a_development_eval_tasks.json")[:4]
        eval_cases = read("benchmark/phase3c_dev2/a_development_eval_hidden_tests.json")
        train_cases = read("data/phase3c_dev2/a_isolated_training_hidden_tests.json")
        inputs = [(dict(task_id=r["task_id"], prompt=r["prompt"], family=r["family"],
                        group=r["development_group"]), eval_cases[r["task_id"]][:5], None) for r in tasks]
        inputs += [(dict(task_id=e["model_task_id"], prompt=e["prompt"], family=r["family"],
                         group="own_training"), train_cases[r["example_id"]][:5], e["target"])
                   for r, e in zip(original[:4], examples[:4])]
        torch.cuda.reset_peak_memory_stats(0)

        def call(task, label):
            if evidence["generation_calls"] >= 9:
                raise RuntimeError("STOP: generation limit")
            reset(schedule.task_rng_seed(SEED, task["task_id"]))
            evidence["generation_calls"] += 1
            return timed(label, lambda: generate(SEED, "isolated", task,
                                                 execution.messages(task["task_id"], task["prompt"])))

        for i, (task, cases, target) in enumerate(inputs):
            stage = "generation_ok"
            print(f"Smoke: generation {i + 1}/8", flush=True)
            raw = call(task, f"generation_{i + 1}")
            if not isinstance(raw, str) or not raw:
                raise RuntimeError("STOP: empty/non-string generation")
            row = dict(task_id=task["task_id"], raw_text=raw,
                       raw_sha256=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                       input_token_length=len(execution.encode_prompt(tokenizer, execution.messages(task["task_id"], task["prompt"]))))
            evidence["generations"].append(row)
            stage = "scoring_ok"
            row["verdict"] = timed(f"scoring_{i + 1}", lambda: score(raw, task, cases, target, RUNTIME / "scores"))
            evidence["non_scientific_pass_counts"]["scored"] += 1
            evidence["non_scientific_pass_counts"]["passed"] += int(row["verdict"]["passed"])
        check("generation_ok", len(evidence["generations"]) == 8)
        check("scoring_ok", all(len(r["verdict"]["case_outcomes"]) == 5 for r in evidence["generations"]))
        stage = "rng_reset_ok"
        seeds = [schedule.task_rng_seed(SEED, r["task_id"]) for r in tasks[:2]]

        def draws(order):
            result = {}
            for seed in order:
                reset(seed)
                result[str(seed)] = [random.random(), float(np.random.rand()),
                                     float(torch.rand(1).item()), float(torch.rand(1, device="cuda").item())]
            return result

        evidence["rng_draws"] = {"AB": draws(seeds), "BA": draws(list(reversed(seeds)))}
        check(stage, evidence["rng_draws"]["AB"] == evidence["rng_draws"]["BA"])
        stage = "repeat_generation_identical"
        repeat = call(inputs[0][0], "generation_repeat")
        evidence["repeat_raw_text"] = repeat
        evidence["repeat_raw_sha256"] = hashlib.sha256(repeat.encode("utf-8")).hexdigest()
        evidence["checks"][stage] = repeat.encode("utf-8") == evidence["generations"][0]["raw_text"].encode("utf-8")
        evidence["completed_checks"].append(stage)
        evidence["repeat_limitation"] = None if evidence["checks"][stage] else "CUDA nondeterminism; informational"
    except BaseException as exc:
        evidence["checks"][stage] = False
        evidence["exceptions"].append({"stage": stage, "type": type(exc).__name__,
                                       "message": str(exc), "traceback": traceback.format_exc()})
        print(evidence["exceptions"][-1]["traceback"], flush=True)
    finally:
        peak("generation") if evidence["generation_calls"] else None
        evidence["wall_seconds"]["total"] = time.perf_counter() - start
        evidence["outcome"] = "STOP_EXCEPTION_NO_RETRY" if evidence["exceptions"] else "COMPLETED"
        with EVIDENCE.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(evidence, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
        print(evidence["outcome"], flush=True)
    return 1 if evidence["exceptions"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
