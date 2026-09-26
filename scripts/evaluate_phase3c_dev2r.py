"""Prospective DEV2R evaluation only; run after independent design approval."""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import torch
from peft import PeftModel
from transformers import AutoTokenizer
from preflight_phase3c_dev2 import MANIFEST as OLD_MANIFEST, read, sha256
from run_phase2a_evaluation import classify, dir_hashes, load_base, summarize
from self_learning_ai.compiler import GocoCompiler
from self_learning_ai.dev2r_evaluation import atomic_new_json, evaluate_task, validate_task


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--condition", choices=("isolated", "composition"), required=True)
    parser.add_argument("--suite", choices=("training", "development"), required=True)
    args = parser.parse_args()
    cfg = read("research/protocols/phase3c_dev2_config.json")
    frozen = read("research/protocols/phase3c_dev2r_manifest.json")
    if frozen["status"] != "FROZEN_PRE_INFERENCE" or frozen["model_execution_authorized"]:
        raise RuntimeError("DEV2R manifest has no execution authorization; independent review is required")
    # This script remains gated until a separately reviewed, prospective authorization changes
    # the manifest and establishes a new execution-code hash. No design-phase model use.
    if args.seed not in cfg["seeds"]: raise ValueError("Unregistered seed")
    if args.suite == "training" and (args.seed, args.condition) == (20270925, "isolated"):
        raise ValueError("Historical 60/60 own-training cell must not be rerun")
    for rel, expected in frozen["input_sha256"].items():
        if sha256(ROOT / rel) != expected: raise ValueError(f"Frozen input hash mismatch: {rel}")
    old_preflight = read(".runtime/phase3c_dev2/preflight.json")
    if old_preflight["status"] != "PASS_PREGRADIENT_CONTRACT" or sha256(OLD_MANIFEST) != old_preflight["manifest_sha256"]:
        raise ValueError("Original DEV2 lineage mismatch")
    adapter = ROOT / ".runtime/phase3c_dev2/adapters" / str(args.seed) / args.condition
    record = read(f".runtime/phase3c_dev2/training/{args.seed}/{args.condition}.json")
    hashes = dir_hashes(adapter)
    if hashes != record["adapter"]["file_hashes"]: raise ValueError("Adapter file hashes changed")
    identity = frozen["adapter_identity"][f"{args.seed}/{args.condition}"]
    if hashes["adapter_model.safetensors"] != identity["sha256"]: raise ValueError("Frozen adapter SHA changed")
    if args.suite == "training":
        rows = read(f"data/phase3c_dev2/a_{args.condition}_training_examples.json")
        tasks = [{"task_id": row["example_id"], "family": row["family"],
                  "archetype": row["archetype"], "development_group": "own_training",
                  "semantic_primitives": row["semantic_primitives"],
                  "composition_signature": row["composition_signature"],
                  "prompt": row["prompt"], "required_regex": []} for row in rows]
        tests = read(f"data/phase3c_dev2/a_{args.condition}_training_hidden_tests.json")
    else:
        tasks = read("benchmark/phase3c_dev2r/a_development_eval_tasks.json")
        tests = read("benchmark/phase3c_dev2r/a_development_eval_hidden_tests.json")
    if len(tasks) != (60 if args.suite == "training" else 48): raise ValueError("Suite count")
    if len({t["task_id"] for t in tasks}) != len(tasks) or set(t["task_id"] for t in tasks) != set(tests):
        raise ValueError("Suite IDs")
    for task in tasks: validate_task(task, tests[task["task_id"]])
    root = ROOT / ".runtime/phase3c_dev2r/evaluations" / str(args.seed) / args.condition / args.suite
    if root.exists(): raise FileExistsError(root)
    root.mkdir(parents=True)
    for name, expected in cfg["base_weights"]["weight_file_sha256"].items():
        if sha256(ROOT / cfg["base_weights"]["local_path"] / name) != expected:
            raise ValueError("Base weight changed")
    torch.manual_seed(args.seed); torch.cuda.manual_seed_all(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(ROOT / cfg["base_weights"]["local_path"], local_files_only=True)
    model = load_base(ROOT / cfg["base_weights"]["local_path"])
    model = PeftModel.from_pretrained(model, adapter, is_trainable=False)
    model.eval()
    compiler = GocoCompiler(ROOT / cfg["compiler"]["java"], ROOT / cfg["compiler"]["path"],
                            timeout_seconds=cfg["evaluation"]["compiler_timeout_seconds"],
                            output_limit_bytes=cfg["evaluation"]["output_limit_bytes_per_stream"])
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    template = (ROOT / "prompts/phase1t_user_template.txt").read_text(encoding="utf-8").strip()
    primaries = []
    for task in tasks:
        user = template.format(task_id=task["task_id"], task_prompt=task["prompt"])
        rendered = tokenizer.apply_chat_template([{"role": "system", "content": system},
            {"role": "user", "content": user}], tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(rendered, return_tensors="pt", truncation=False).to("cuda:0")
        length = int(inputs["input_ids"].shape[1])
        if length > cfg["evaluation"]["max_input_tokens"]: raise ValueError("Evaluation input too long")
        begin = time.perf_counter()
        with torch.inference_mode():
            generated = model.generate(**inputs, do_sample=False, num_beams=1,
                max_new_tokens=cfg["evaluation"]["max_new_tokens"], pad_token_id=tokenizer.eos_token_id)
        new = generated[0, length:]
        raw = tokenizer.decode(new, skip_special_tokens=True)
        primary = evaluate_task(compiler=compiler, task=task, cases=tests[task["task_id"]],
            raw_generation=raw, generation_metadata={"input_tokens": length,
            "output_tokens": int(new.shape[0]), "generation_ms": round((time.perf_counter()-begin)*1000)},
            adapter_identity=identity, checkpoint_dir=root / "tasks")
        primaries.append(primary)
    rows = []
    for item in primaries:
        row = {**item["task_metadata"], **item["score"],
               "raw_generation": item["raw_generation"], "normalized_output": item["normalized_output"],
               **item["generation_metadata"]}
        row["failure_category"] = classify(row["normalized_output"], row)
        rows.append(row)
    atomic_new_json(root / "aggregate.json", {"phase": "3C-DEV2R", "suite": args.suite,
        "seed": args.seed, "condition": args.condition, "environment": {"platform": platform.platform(),
        "python": platform.python_version()}, "records": rows, "summary": summarize(rows)})
    print(json.dumps({"passed": sum(x["hidden_pass"] for x in rows), "total": len(rows)}))


if __name__ == "__main__": main()
