from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import bitsandbytes
import psutil
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from self_learning_ai.benchmark import extract_source_phase1r, load_json, score_source
from self_learning_ai.compiler import GocoCompiler


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class RssMonitor(threading.Thread):
    def __init__(self) -> None:
        super().__init__(daemon=True)
        self.stop_event = threading.Event()
        self.peak = 0

    def run(self) -> None:
        process = psutil.Process(os.getpid())
        while not self.stop_event.wait(0.05):
            self.peak = max(self.peak, process.memory_info().rss)

    def stop(self) -> int:
        self.stop_event.set()
        self.join(timeout=2)
        return self.peak


def load_frozen_model(model_path: Path, runtime: dict[str, Any]) -> Any:
    if runtime["quantization"] == "none":
        model = AutoModelForCausalLM.from_pretrained(
            model_path, local_files_only=True, dtype=torch.float16, low_cpu_mem_usage=False
        ).to(runtime["device"])
    elif runtime["quantization"] == "bitsandbytes_nf4_4bit":
        quantization = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            local_files_only=True,
            quantization_config=quantization,
            device_map={"": 0},
            dtype=torch.float16,
        )
    else:
        raise ValueError(f"Unknown quantization: {runtime['quantization']}")
    model.requires_grad_(False)
    model.eval()
    if any(parameter.requires_grad for parameter in model.parameters()):
        raise RuntimeError("Frozen-model invariant violated")
    return model


def classify_failure(raw: str, normalized: str, record: dict[str, Any]) -> str:
    if record["hidden_pass"]:
        return "success"
    lowered = normalized.casefold()
    if "package main" in lowered or re.search(r'(?m)^\s*import\s+["(]', normalized):
        return "wrong_language"
    if record["error_phase"] in {"lexical", "syntax", "semantic", "runtime", "timeout", "output_limit", "system"}:
        return record["error_phase"]
    if not record["structural_requirements_met"]:
        return "structural_requirement"
    if record["execution_success"]:
        return "hidden_test_semantic"
    return "unknown"


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_level: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_level[row["level"]].append(row)
        by_family[row["family"]].append(row)

    def metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
        recognition_rows = [row for row in rows if row["level"] == "recognition"]
        executable = [row for row in rows if row["level"] != "recognition"]
        result: dict[str, Any] = {"n": len(rows), "failure_taxonomy": dict(sorted(Counter(row["failure_category"] for row in rows).items()))}
        if recognition_rows:
            result["recognition_accuracy"] = sum(row["recognition_correct"] for row in recognition_rows) / len(recognition_rows)
            result["recognition_correct"] = sum(row["recognition_correct"] for row in recognition_rows)
        if executable:
            for key in ("parse_success", "compile_success", "execution_success", "hidden_pass"):
                result[key] = sum(bool(row[key]) for row in executable) / len(executable)
                result[key + "_count"] = sum(bool(row[key]) for row in executable)
        return result

    return {
        "overall": metrics(records),
        "by_level": {name: metrics(rows) for name, rows in sorted(by_level.items())},
        "by_family": {name: metrics(rows) for name, rows in sorted(by_family.items())},
        "by_level_and_family": {
            level: {
                family: metrics([row for row in rows if row["family"] == family])
                for family in sorted({row["family"] for row in rows})
            }
            for level, rows in sorted(by_level.items())
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--model-key", choices=["qwen_1p5b", "qwen_3b"], required=True)
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--jar", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    config = load_json(args.config)
    for raw_path, expected in config["input_file_hashes"].items():
        actual = sha256(Path(raw_path))
        if actual != expected:
            raise ValueError(f"Frozen input hash mismatch for {raw_path}: {actual}")

    runtime = config["models"][args.model_key]
    model_path = Path(runtime["local_path"])
    for relative, expected in runtime["weight_file_sha256"].items():
        actual = sha256(model_path / relative)
        if actual != expected:
            raise ValueError(f"Model weight hash mismatch for {relative}: {actual}")
    tasks = load_json(Path(config["benchmark"]["tasks"]))
    hidden = load_json(Path(config["benchmark"]["hidden_tests"]))
    if any(task["split"] != "phase1s_diagnostic" for task in tasks):
        raise ValueError("Non-diagnostic split in Phase 1S input")

    system = Path(config["prompt"]["system"]).read_text(encoding="utf-8").strip()
    for context_file in config["prompt"]["candidate_c_context_files"]:
        system += f"\n\nTRUSTED GOCO KNOWLEDGE: {Path(context_file).name}\n\n"
        system += Path(context_file).read_text(encoding="utf-8").strip()

    torch.manual_seed(config["seed"])
    torch.cuda.manual_seed_all(config["seed"])
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    monitor = RssMonitor()
    monitor.start()
    load_started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = load_frozen_model(model_path, runtime)
    load_seconds = time.perf_counter() - load_started
    compiler = GocoCompiler(
        args.java, args.jar,
        timeout_seconds=config["scoring"]["compiler_timeout_seconds"],
        output_limit_bytes=config["scoring"]["output_limit_bytes_per_stream"],
    )

    records = []
    total_generation_seconds = 0.0
    total_output_tokens = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for task in tasks:
        rendered = tokenizer.apply_chat_template(
            [{"role": "system", "content": system}, {"role": "user", "content": task["prompt"]}],
            tokenize=False, add_generation_prompt=True,
        )
        inputs = tokenizer(rendered, return_tensors="pt", truncation=False).to(runtime["device"])
        input_tokens = int(inputs["input_ids"].shape[1])
        if input_tokens > config["decoding"]["max_input_tokens"]:
            raise ValueError(f"Input budget exceeded for {task['task_id']}")
        max_new_tokens = config["decoding"]["max_new_tokens_by_level"][task["level"]]
        started = time.perf_counter()
        with torch.inference_mode():
            generated = model.generate(
                **inputs, do_sample=False, num_beams=1,
                max_new_tokens=max_new_tokens, pad_token_id=tokenizer.eos_token_id,
            )
        elapsed = time.perf_counter() - started
        total_generation_seconds += elapsed
        new_tokens = generated[0, input_tokens:]
        total_output_tokens += int(new_tokens.shape[0])
        raw = tokenizer.decode(new_tokens, skip_special_tokens=True)
        normalized = extract_source_phase1r(raw)
        base = {
            "task_id": task["task_id"], "level": task["level"], "family": task["family"],
            "raw_generation": raw, "normalized_output": normalized,
            "input_tokens": input_tokens, "output_tokens": int(new_tokens.shape[0]),
            "generation_ms": round(elapsed * 1000),
        }
        if task["level"] == "recognition":
            correct = normalized == task["answer"]
            record = base | {
                "recognition_answer": task["answer"], "recognition_correct": correct,
                "failure_category": "success" if correct else ("wrong_choice" if normalized in {"A", "B", "C"} else "invalid_choice"),
            }
        else:
            if task["level"] == "local_completion":
                source = task["scaffold_prefix"] + normalized + task["scaffold_suffix"]
            else:
                source = normalized
            scored = score_source(compiler, task, hidden[task["task_id"]], source).as_dict()
            record = base | scored | {"evaluated_source": source}
            record["failure_category"] = classify_failure(raw, normalized, record)
        records.append(record)
        checkpoint = {"model_key": args.model_key, "completed_tasks": len(records), "records": records}
        (args.output.parent / f"{args.output.stem}.{args.model_key}.checkpoint.json").write_text(
            json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8"
        )

    peak_rss = monitor.stop()
    payload = {
        "config": config,
        "config_sha256": sha256(args.config),
        "model_key": args.model_key,
        "model_runtime": runtime,
        "environment": {
            "platform": platform.platform(), "python": platform.python_version(),
            "torch": torch.__version__, "transformers": transformers.__version__,
            "bitsandbytes": bitsandbytes.__version__, "cuda_runtime": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0),
        },
        "hardware": {
            "load_seconds": load_seconds,
            "peak_gpu_memory_bytes": int(torch.cuda.max_memory_allocated()),
            "peak_process_rss_bytes": peak_rss,
            "generation_seconds": total_generation_seconds,
            "output_tokens": total_output_tokens,
            "output_tokens_per_second": total_output_tokens / total_generation_seconds,
        },
        "records": records,
        "summary": summarize(records),
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"model": args.model_key, "hardware": payload["hardware"], "summary": payload["summary"]}, indent=2))


if __name__ == "__main__":
    main()
