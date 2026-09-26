"""Prospective DEV2R evaluation only; run after independent design approval."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.dev2r_evaluation import (
    atomic_new_json, evaluate_task, reject_existing_attempt, require_authorization,
    summarize_own_training, validate_task,
)


def read(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frozen_input_sha256(path: Path):
    if path.suffix.lower() in {".json", ".md", ".py", ".txt", ".jinja"}:
        return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    return sha256(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--condition", choices=("isolated", "composition"), required=True)
    parser.add_argument("--suite", choices=("training", "development"), required=True)
    parser.add_argument("--authorization-check-only", action="store_true",
                        help="Check the manifest authorization without importing or loading a model")
    args = parser.parse_args()
    frozen = read("research/protocols/phase3c_dev2r_v2_manifest.json")
    require_authorization(frozen)
    if args.authorization_check_only:
        print("DEV2R authorization check passed; no model imported")
        return
    # Heavy execution imports occur only after the strict authorization check.
    import torch
    from peft import PeftModel
    from transformers import AutoTokenizer
    from run_phase2a_evaluation import classify, dir_hashes, load_base, summarize
    from self_learning_ai.compiler import GocoCompiler
    cfg = read("research/protocols/phase3c_dev2_config.json")
    if args.seed not in cfg["seeds"]: raise ValueError("Unregistered seed")
    if args.suite == "training" and (args.seed, args.condition) == (20270925, "isolated"):
        raise ValueError("Historical 60/60 own-training cell must not be rerun")
    for rel, expected in frozen["input_sha256"].items():
        if frozen_input_sha256(ROOT / rel) != expected: raise ValueError(f"Frozen input hash mismatch: {rel}")
    old_preflight = read(".runtime/phase3c_dev2/preflight.json")
    if old_preflight["status"] != "PASS_PREGRADIENT_CONTRACT" or sha256(ROOT / "research/protocols/phase3c_dev2_manifest.json") != old_preflight["manifest_sha256"]:
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
                  "prompt": row["prompt"], "difficulty": "development_training",
                  "required_regex": []} for row in rows]
        tests = read(f"data/phase3c_dev2/a_{args.condition}_training_hidden_tests.json")
        refs = read(f"data/phase3c_dev2/a_{args.condition}_training_references.json")
    else:
        tasks = read("benchmark/phase3c_dev2r_v2/a_development_eval_tasks.json")
        tests = read("benchmark/phase3c_dev2r_v2/a_development_eval_hidden_tests.json")
        refs = {}
    if len(tasks) != (60 if args.suite == "training" else 48): raise ValueError("Suite count")
    if len({t["task_id"] for t in tasks}) != len(tasks) or set(t["task_id"] for t in tasks) != set(tests):
        raise ValueError("Suite IDs")
    if args.suite == "training" and set(refs) != set(tests):
        raise ValueError("Own-training target IDs")
    for task in tasks: validate_task(task, tests[task["task_id"]])
    root = ROOT / ".runtime/phase3c_dev2r/evaluations" / str(args.seed) / args.condition / args.suite
    reject_existing_attempt(root)
    for name, expected in cfg["base_weights"]["weight_file_sha256"].items():
        if sha256(ROOT / cfg["base_weights"]["local_path"] / name) != expected:
            raise ValueError("Base weight changed")
    root.mkdir(parents=True)
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
            adapter_identity=identity, checkpoint_dir=root / "tasks",
            target_source=refs.get(task["task_id"]))
        primaries.append(primary)
    rows = []
    for item in primaries:
        row = {**item["task_metadata"], **item["score"],
               "raw_generation": item["raw_generation"], "normalized_output": item["normalized_output"],
               **item["generation_metadata"]}
        if args.suite == "training":
            row["exact_target_reproduction"] = item["exact_target_reproduction"]
        row["failure_category"] = classify(row["normalized_output"], row)
        rows.append(row)
    summary = summarize(rows)
    if args.suite == "training":
        summary["own_training_diagnostics"] = summarize_own_training(rows)
    atomic_new_json(root / "aggregate.json", {"phase": "3C-DEV2R", "suite": args.suite,
        "seed": args.seed, "condition": args.condition, "environment": {"platform": platform.platform(),
        "python": platform.python_version()}, "records": rows, "summary": summary})
    print(json.dumps({"passed": sum(x["hidden_pass"] for x in rows), "total": len(rows)}))


if __name__ == "__main__": main()
