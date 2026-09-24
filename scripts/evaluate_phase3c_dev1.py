"""Single greedy, no-documentation evaluation of one final DEV1 adapter."""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bitsandbytes
import peft
import torch
import transformers
from peft import PeftModel
from transformers import AutoTokenizer

from preflight_phase3c_dev1 import MANIFEST, OUTPUT as PREFLIGHT, ROOT, read, sha256
from run_phase2a_evaluation import RssMonitor, classify, dir_hashes, load_base, summarize
from self_learning_ai.benchmark import extract_source_phase1r, score_source
from self_learning_ai.compiler import GocoCompiler


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--condition", choices=("dense", "diverse"), required=True)
    parser.add_argument("--suite", choices=("training", "development"), required=True)
    args = parser.parse_args()
    preflight = read(str(PREFLIGHT.relative_to(ROOT)))
    cfg = read("research/protocols/phase3c_dev1_manifest.json")
    if preflight["status"] != "PASS_PREGRADIENT_CONTRACT" or sha256(MANIFEST) != preflight["manifest_sha256"]:
        raise RuntimeError("Preflight or manifest mismatch")
    if args.seed not in cfg["seeds"]:
        raise ValueError("Unregistered seed")
    root = ROOT / ".runtime/phase3c_dev1"
    adapter = root / "adapters" / str(args.seed) / args.condition
    training_record = read(str((root / "training" / str(args.seed) / f"{args.condition}.json").relative_to(ROOT)))
    adapter_hashes = dir_hashes(adapter)
    if adapter_hashes != training_record["adapter"]["file_hashes"] or training_record["training"]["optimizer_steps"] != 24:
        raise ValueError("Adapter lineage or integrity mismatch")
    output = root / "evaluations" / str(args.seed) / f"{args.condition}_{args.suite}.json"
    checkpoint = output.with_suffix(".checkpoint.json")
    if output.exists() or checkpoint.exists():
        raise FileExistsError(output if output.exists() else checkpoint)
    if args.suite == "training":
        rows = read(f"data/phase3c_dev1/a_{args.condition}_training_examples.json")
        tasks = [{"task_id": row["example_id"], "family": row["family"],
                  "archetype": row["archetype"], "difficulty": "development_training",
                  "prompt": row["prompt"], "required_regex": []} for row in rows]
        tests = read(f"data/phase3c_dev1/a_{args.condition}_training_hidden_tests.json")
        refs = read(f"data/phase3c_dev1/a_{args.condition}_training_references.json")
    else:
        tasks = read("benchmark/phase3c_dev1/a_development_eval_tasks.json")
        tests = read("benchmark/phase3c_dev1/a_development_eval_hidden_tests.json")
        refs = {}
    expected_count = 60 if args.suite == "training" else 36
    if len(tasks) != expected_count or len({t["task_id"] for t in tasks}) != expected_count:
        raise ValueError("Suite count/IDs")
    model_path = ROOT / cfg["base_weights"]["local_path"]
    for name, expected in cfg["base_weights"]["weight_file_sha256"].items():
        if sha256(model_path / name) != expected:
            raise ValueError("Base weight changed")
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    monitor = RssMonitor()
    monitor.start()
    start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = load_base(model_path)
    model = PeftModel.from_pretrained(model, adapter, is_trainable=False)
    model.eval()
    compiler = GocoCompiler(ROOT / cfg["compiler"]["java"], ROOT / cfg["compiler"]["path"],
                            timeout_seconds=cfg["evaluation"]["compiler_timeout_seconds"],
                            output_limit_bytes=cfg["evaluation"]["output_limit_bytes_per_stream"])
    load_seconds = time.perf_counter() - start
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    template = (ROOT / "prompts/phase1t_user_template.txt").read_text(encoding="utf-8").strip()
    records = []
    generation_seconds = 0.0
    output_tokens = 0
    output.parent.mkdir(parents=True, exist_ok=True)
    for task in tasks:
        user = template.format(task_id=task["task_id"], task_prompt=task["prompt"])
        rendered = tokenizer.apply_chat_template([{"role": "system", "content": system},
                                                   {"role": "user", "content": user}], tokenize=False,
                                                  add_generation_prompt=True)
        inputs = tokenizer(rendered, return_tensors="pt", truncation=False).to("cuda:0")
        input_length = int(inputs["input_ids"].shape[1])
        if input_length > cfg["evaluation"]["max_input_tokens"]:
            raise ValueError("Evaluation input too long")
        begin = time.perf_counter()
        with torch.inference_mode():
            generated = model.generate(**inputs, do_sample=False, num_beams=1,
                                       max_new_tokens=cfg["evaluation"]["max_new_tokens"],
                                       pad_token_id=tokenizer.eos_token_id)
        elapsed = time.perf_counter() - begin
        new = generated[0, input_length:]
        raw = tokenizer.decode(new, skip_special_tokens=True)
        normalized = extract_source_phase1r(raw)
        score = score_source(compiler, task, tests[task["task_id"]], normalized).as_dict()
        row = {"task_id": task["task_id"], "family": task["family"], "archetype": task["archetype"],
               "distance_group": task.get("distance_group"), "prompt": task["prompt"],
               "raw_generation": raw, "normalized_output": normalized,
               "input_tokens": input_length, "output_tokens": int(new.shape[0]),
               "generation_ms": round(elapsed * 1000)} | score
        row["failure_category"] = classify(normalized, row)
        if args.suite == "training":
            row["exact_target_reproduction"] = normalized == refs[task["task_id"]]
        records.append(row)
        generation_seconds += elapsed
        output_tokens += int(new.shape[0])
        checkpoint.write_text(json.dumps({"phase": "3C-DEV1", "condition": args.condition, "seed": args.seed,
                                          "suite": args.suite, "completed_tasks": len(records),
                                          "records": records}, indent=2) + "\n", encoding="utf-8")
        if len(records) % 12 == 0:
            print(json.dumps({"condition": args.condition, "seed": args.seed,
                              "suite": args.suite, "completed": len(records)}), flush=True)
    peak_rss = monitor.stop()
    payload = {"phase": "3C-DEV1", "suite": args.suite, "condition": args.condition, "seed": args.seed,
               "manifest_sha256": sha256(MANIFEST), "adapter_file_hashes": adapter_hashes,
               "environment": {"platform": platform.platform(), "python": platform.python_version(),
                               "torch": torch.__version__, "transformers": transformers.__version__,
                               "bitsandbytes": bitsandbytes.__version__, "peft": peft.__version__,
                               "cuda_runtime": torch.version.cuda, "gpu": torch.cuda.get_device_name(0)},
               "hardware": {"load_seconds": load_seconds, "peak_gpu_memory_bytes": int(torch.cuda.max_memory_allocated()),
                            "peak_process_rss_bytes": peak_rss, "generation_seconds": generation_seconds,
                            "output_tokens": output_tokens}, "records": records, "summary": summarize(records)}
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    checkpoint.unlink()
    print(json.dumps({"suite": args.suite, "condition": args.condition, "seed": args.seed,
                      "passed": sum(row["hidden_pass"] for row in records), "total": len(records)}), flush=True)


if __name__ == "__main__":
    main()
