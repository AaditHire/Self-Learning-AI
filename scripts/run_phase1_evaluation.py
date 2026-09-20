from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from self_learning_ai.benchmark import extract_source, load_json, paired_comparison, score_source
from self_learning_ai.compiler import GocoCompiler


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def summarize(scores: list[dict[str, Any]]) -> dict[str, Any]:
    def rate(key: str, rows: list[dict[str, Any]]) -> float:
        return sum(bool(row[key]) for row in rows) / len(rows) if rows else 0.0

    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_difficulty: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scores:
        by_family[row["family"]].append(row)
        by_difficulty[row["difficulty"]].append(row)
    metrics = ["parse_success", "compile_success", "execution_success", "hidden_pass"]
    return {
        "n_tasks": len(scores),
        "overall": {key: rate(key, scores) for key in metrics},
        "by_family": {
            name: {key: rate(key, rows) for key in metrics} | {"n": len(rows)}
            for name, rows in sorted(by_family.items())
        },
        "by_difficulty": {
            name: {key: rate(key, rows) for key in metrics} | {"n": len(rows)}
            for name, rows in sorted(by_difficulty.items())
        },
        "error_phases": dict(
            sorted(
                {
                    phase: sum(row["error_phase"] == phase for row in scores)
                    for phase in {row["error_phase"] for row in scores if row["error_phase"]}
                }.items()
            )
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--jar", type=Path, required=True)
    parser.add_argument("--tasks", type=Path, default=Path("benchmark/tasks.json"))
    parser.add_argument("--tests", type=Path, default=Path("benchmark/hidden_tests.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite result: {args.output}")

    config = load_json(args.config)
    paths = {
        "benchmark_tasks_sha256": args.tasks,
        "benchmark_hidden_tests_sha256": args.tests,
        "documentation_sha256": Path("docs/goco_language_reference.md"),
        "model_weights_sha256": args.model / "model.safetensors",
        "system_prompt_sha256": Path(config["prompt_files"]["system"]),
        "user_template_sha256": Path(config["prompt_files"]["user_template"]),
    }
    for key, path in paths.items():
        actual = sha256(path)
        if actual != config["input_hashes"][key]:
            raise ValueError(f"Frozen input hash mismatch for {path}: {actual}")

    tasks = [item for item in load_json(args.tasks) if item["split"] == config["split"]]
    if any(item["split"] == "final_paper" for item in tasks):
        raise ValueError("Final-paper tasks are prohibited in Phase 1 evaluation")
    hidden = load_json(args.tests)
    system_prompt = Path(config["prompt_files"]["system"]).read_text(encoding="utf-8").strip()
    user_template = Path(config["prompt_files"]["user_template"]).read_text(encoding="utf-8")
    documentation = Path("docs/goco_language_reference.md").read_text(encoding="utf-8")

    torch.manual_seed(config["seed"])
    torch.cuda.manual_seed_all(config["seed"])
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        local_files_only=True,
        dtype=torch.float16,
        low_cpu_mem_usage=False,
    ).to(config["model"]["device"])
    model.requires_grad_(False)
    model.eval()
    if any(parameter.requires_grad for parameter in model.parameters()):
        raise RuntimeError("Frozen-model invariant violated")

    compiler = GocoCompiler(
        args.java,
        args.jar,
        timeout_seconds=config["scoring"]["compiler_timeout_seconds"],
        output_limit_bytes=config["scoring"]["output_limit_bytes_per_stream"],
    )
    payload: dict[str, Any] = {
        "config": config,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "cuda_runtime": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0),
        },
        "conditions": {},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)

    for condition in config["condition_order"]:
        condition_system = system_prompt
        if config["conditions"][condition]["documentation"]:
            condition_system += "\n\nTRUSTED GOCO DOCUMENTATION\n\n" + documentation
        records = []
        torch.cuda.reset_peak_memory_stats()
        for task in tasks:
            user_prompt = user_template.format(task_id=task["task_id"], task_prompt=task["prompt"])
            messages = [
                {"role": "system", "content": condition_system},
                {"role": "user", "content": user_prompt},
            ]
            rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(
                rendered,
                return_tensors="pt",
                truncation=False,
            ).to(config["model"]["device"])
            input_tokens = int(inputs["input_ids"].shape[1])
            if input_tokens > config["decoding"]["max_input_tokens"]:
                raise ValueError(f"Input token budget exceeded for {task['task_id']}: {input_tokens}")
            started = time.perf_counter()
            with torch.inference_mode():
                generated = model.generate(
                    **inputs,
                    do_sample=False,
                    num_beams=config["decoding"]["num_beams"],
                    max_new_tokens=config["decoding"]["max_new_tokens"],
                    pad_token_id=tokenizer.eos_token_id,
                )
            generation_ms = round((time.perf_counter() - started) * 1000)
            new_tokens = generated[0, input_tokens:]
            raw = tokenizer.decode(new_tokens, skip_special_tokens=True)
            source = extract_source(raw)
            score = score_source(compiler, task, hidden[task["task_id"]], source).as_dict()
            records.append(
                {
                    **score,
                    "raw_generation": raw,
                    "extracted_source": source,
                    "input_tokens": input_tokens,
                    "output_tokens": int(new_tokens.shape[0]),
                    "generation_ms": generation_ms,
                }
            )
            checkpoint = {
                "condition": condition,
                "completed_tasks": len(records),
                "records": records,
            }
            (args.output.parent / f"{args.output.stem}.{condition}.checkpoint.json").write_text(
                json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8"
            )
        payload["conditions"][condition] = {
            "records": records,
            "summary": summarize(records),
            "peak_gpu_memory_bytes": int(torch.cuda.max_memory_allocated()),
        }

    payload["paired_comparison"] = paired_comparison(
        payload["conditions"]["BASE_NO_DOCS"]["records"],
        payload["conditions"]["BASE_WITH_DOCS"]["records"],
        bootstrap_seed=config["paired_analysis"]["bootstrap_seed"],
        bootstrap_samples=config["paired_analysis"]["bootstrap_samples"],
    )
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "baseline": payload["conditions"]["BASE_NO_DOCS"]["summary"],
        "docs": payload["conditions"]["BASE_WITH_DOCS"]["summary"],
        "paired": payload["paired_comparison"],
    }, indent=2))


if __name__ == "__main__":
    main()
