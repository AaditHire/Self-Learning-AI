from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import bitsandbytes
import peft
import torch
import transformers
from peft import PeftModel
from transformers import AutoTokenizer

from run_phase2a_evaluation import RssMonitor, classify, dir_hashes, load_base, sha256, summarize
from self_learning_ai.benchmark import extract_source_phase1r, score_source
from self_learning_ai.compiler import GocoCompiler


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--plan", choices=["primary", "training", "regression"], required=True)
    parser.add_argument("--condition", choices=["BASE_NO_DOCS", "BASE_DOCS", "ADAPTED_NO_DOCS"], required=True)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--jar", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.condition == "ADAPTED_NO_DOCS":
        if args.seed is None or args.adapter is None:
            raise ValueError("Adapted evaluation requires --seed and --adapter")
    elif args.seed is not None or args.adapter is not None:
        raise ValueError("Base conditions do not accept --seed or --adapter")
    if args.condition == "BASE_DOCS" and args.plan != "primary":
        raise ValueError("BASE_DOCS is descriptive on the primary suite only")
    if args.plan == "training" and args.condition != "ADAPTED_NO_DOCS":
        raise ValueError("Training diagnostics are adapter-only")

    config = json.loads(args.config.read_text(encoding="utf-8"))
    for raw, expected in config["input_file_hashes"].items():
        actual = sha256(Path(raw))
        if actual != expected:
            raise ValueError(f"Frozen input hash mismatch {raw}: {actual}")
    if args.condition == "ADAPTED_NO_DOCS":
        assert args.seed is not None and args.adapter is not None
        if args.seed not in config["seeds"]:
            raise ValueError("Seed is not preregistered")
        expected_adapter = Path(config["training"]["adapter_outputs"][str(args.seed)])
        if args.adapter != expected_adapter:
            raise ValueError(f"Adapter path must be {expected_adapter}")

    model_cfg = config["model"]
    model_path = Path(model_cfg["local_path"])
    for name, expected in model_cfg["weight_file_sha256"].items():
        if sha256(model_path / name) != expected:
            raise ValueError(f"Weight hash mismatch {name}")
    adapter_hashes = dir_hashes(args.adapter) if args.adapter else {}
    base_system = Path(config["prompt"]["system"]).read_text(encoding="utf-8").strip()
    docs_system = base_system
    for path in config["prompt"]["candidate_c_context_files"]:
        docs_system += f"\n\nTRUSTED GOCO KNOWLEDGE: {Path(path).name}\n\n" + Path(path).read_text(encoding="utf-8").strip()
    template = Path(config["prompt"]["user_template"]).read_text(encoding="utf-8").strip()

    if args.plan == "primary":
        tasks = json.loads(Path(config["data"]["confirmatory_tasks"]).read_text(encoding="utf-8"))
        tests = json.loads(Path(config["data"]["confirmatory_tests"]).read_text(encoding="utf-8"))
    elif args.plan == "training":
        examples = json.loads(Path(config["data"]["training_examples"]).read_text(encoding="utf-8"))
        tests = json.loads(Path(config["data"]["training_tests"]).read_text(encoding="utf-8"))
        tasks = [{"task_id": row["example_id"], "family": row["family"], "difficulty": "phase2b_training", "prompt": row["prompt"], "required_regex": []} for row in examples]
    else:
        tasks = json.loads(Path(config["data"]["general_regression"]).read_text(encoding="utf-8"))
        tests = {}

    runtime_seed = args.seed if args.seed is not None else config["evaluation"]["base_seed"]
    torch.manual_seed(runtime_seed)
    torch.cuda.manual_seed_all(runtime_seed)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    monitor = RssMonitor()
    monitor.start()
    load_started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = load_base(model_path)
    if args.condition == "ADAPTED_NO_DOCS":
        assert args.adapter is not None
        model = PeftModel.from_pretrained(model, args.adapter, is_trainable=False)
        model.eval()
    compiler = GocoCompiler(args.java, args.jar, timeout_seconds=config["evaluation"]["compiler_timeout_seconds"], output_limit_bytes=config["evaluation"]["output_limit_bytes_per_stream"])
    load_seconds = time.perf_counter() - load_started
    distance = {}
    if args.plan == "primary":
        validation = json.loads(Path(config["data"]["validation"]).read_text(encoding="utf-8"))
        distance = {row["task_id"]: row["distance_bucket"] for row in validation["structural_split"]["distance_records"]}

    system = docs_system if args.condition == "BASE_DOCS" else base_system
    records = []
    generation_seconds = 0.0
    total_tokens = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = args.output.parent / f"{args.output.stem}.checkpoint.json"
    for task in tasks:
        user = task["prompt"] if args.plan == "regression" else template.format(task_id=task["task_id"], task_prompt=task["prompt"])
        runtime_system = "You are a precise programming and instruction assistant. Follow the requested answer format exactly and return no explanation." if args.plan == "regression" else system
        rendered = tokenizer.apply_chat_template([{"role": "system", "content": runtime_system}, {"role": "user", "content": user}], tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(rendered, return_tensors="pt", truncation=False).to("cuda:0")
        input_tokens = int(inputs["input_ids"].shape[1])
        if input_tokens > config["evaluation"]["max_input_tokens"]:
            raise ValueError(f"Input too long {task['task_id']}")
        started = time.perf_counter()
        with torch.inference_mode():
            generated = model.generate(**inputs, do_sample=False, num_beams=1, max_new_tokens=config["evaluation"]["regression_max_new_tokens"] if args.plan == "regression" else config["evaluation"]["max_new_tokens"], pad_token_id=tokenizer.eos_token_id)
        elapsed = time.perf_counter() - started
        new = generated[0, input_tokens:]
        raw = tokenizer.decode(new, skip_special_tokens=True)
        generation_seconds += elapsed
        total_tokens += int(new.shape[0])
        if args.plan == "regression":
            normalized = raw.strip()
            record = {"condition": args.condition, "seed": args.seed, "task_id": task["task_id"], "category": task["category"], "raw_generation": raw, "normalized_output": normalized, "expected": task["expected"], "passed": normalized == task["expected"], "input_tokens": input_tokens, "output_tokens": int(new.shape[0]), "generation_ms": round(elapsed * 1000)}
        else:
            normalized = extract_source_phase1r(raw)
            scored = score_source(compiler, task, tests[task["task_id"]], normalized).as_dict()
            record = {"condition": args.condition, "seed": args.seed, "task_id": task["task_id"], "family": task["family"], "distance_bucket": distance.get(task["task_id"]), "raw_generation": raw, "normalized_output": normalized, "input_tokens": input_tokens, "output_tokens": int(new.shape[0]), "generation_ms": round(elapsed * 1000)} | scored
            record["failure_category"] = classify(normalized, record)
        records.append(record)
        checkpoint.write_text(json.dumps({"phase": "2B", "plan": args.plan, "condition": args.condition, "seed": args.seed, "completed_tasks": len(records), "records": records}, indent=2) + "\n", encoding="utf-8")

    peak_rss = monitor.stop()
    if args.plan == "regression":
        correct = sum(row["passed"] for row in records)
        summary = {"correct": correct, "total": len(records), "accuracy": correct / len(records), "by_category": {category: {"correct": sum(row["passed"] for row in records if row["category"] == category), "total": sum(row["category"] == category for row in records)} for category in sorted({row["category"] for row in records})}}
    else:
        summary = summarize(records)
    payload = {"phase": "2B", "plan": args.plan, "condition": args.condition, "seed": args.seed, "config_sha256": sha256(args.config), "adapter_file_hashes": adapter_hashes, "environment": {"platform": platform.platform(), "python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__, "bitsandbytes": bitsandbytes.__version__, "peft": peft.__version__, "cuda_runtime": torch.version.cuda, "gpu": torch.cuda.get_device_name(0)}, "hardware": {"load_seconds": load_seconds, "peak_gpu_memory_bytes": int(torch.cuda.max_memory_allocated()), "peak_process_rss_bytes": peak_rss, "generation_seconds": generation_seconds, "output_tokens": total_tokens, "output_tokens_per_second": total_tokens / generation_seconds}, "records": records, "summary": summary}
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"plan": args.plan, "condition": args.condition, "seed": args.seed, "hardware": payload["hardware"], "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
