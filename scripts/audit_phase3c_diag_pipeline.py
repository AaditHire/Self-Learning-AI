"""Read-only deterministic audit of the stopped Phase 3C A path.

Uses frozen A training/evaluation data and existing records only. No model
generation, optimizer operation, compiler execution, or holdout access.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from transformers import AutoTokenizer

from train_phase2a_qlora import TokenDataset
from run_phase2a_evaluation import classify, summarize
from phase3c_contract import ROOT, load_frozen, sha256, verify_execution_files
from self_learning_ai.compiler import normalized_program_output


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    verify_execution_files()
    cfg = load_frozen(check_base=True)
    examples = load("data/phase3c/a_training_examples.json")
    train_cases = load("data/phase3c/a_training_hidden_tests.json")
    eval_tasks = load("benchmark/phase3c/a_eval_tasks.json")
    eval_cases = load("benchmark/phase3c/a_eval_hidden_tests.json")
    validation = load("research/results/EXP-0048/data_validation.json")
    ids = [x["example_id"] for x in examples]
    eval_ids = [x["task_id"] for x in eval_tasks]
    if (len(ids) != 60 or len(set(ids)) != 60 or set(train_cases) != set(ids)
            or len(eval_ids) != 32 or len(set(eval_ids)) != 32 or set(eval_cases) != set(eval_ids)
            or set(ids) & set(eval_ids) or any(not x["target"].strip() for x in examples)):
        raise ValueError("Missing, duplicate, colliding, or empty A data")
    if Counter(x["family"] for x in examples) != {"numeric_iteration": 30, "array_reduction": 30}:
        raise ValueError("A training family labels")
    if any(n != 15 for n in Counter(x["archetype"] for x in examples).values()):
        raise ValueError("A training archetype labels")
    if any(n != 8 for n in Counter(x["archetype"] for x in eval_tasks).values()):
        raise ValueError("A evaluation archetype labels")
    verified_refs = validation["verification"]["a_training"] + validation["verification"]["a_eval"]
    if (set(x["item_id"] for x in verified_refs) != set(ids) | set(eval_ids)
            or any(not x["score"]["hidden_pass"] for x in verified_refs)
            or any(len(train_cases[x]) != 5 for x in ids)
            or any(len(eval_cases[x]) != 5 for x in eval_ids)):
        raise ValueError("Frozen reference validation or cases incomplete")

    model_dir = ROOT / cfg["base_weights"]["local_path"]
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    template = (ROOT / "prompts/phase1t_user_template.txt").read_text(encoding="utf-8").strip()
    tokenized = TokenDataset(examples, tokenizer, system, cfg["training"]["max_length"])
    token_stats = []
    for row, item in zip(examples, tokenized.items, strict=True):
        user_training = f"Task {row['example_id']}\n\n{row['prompt']}"
        user_evaluation_style = template.format(task_id=row["example_id"], task_prompt=row["prompt"])
        if user_training != user_evaluation_style:
            raise ValueError(f"Train/eval user formatting differs: {row['example_id']}")
        rendered = tokenizer.apply_chat_template(
            [{"role": "system", "content": system}, {"role": "user", "content": user_training}],
            tokenize=False, add_generation_prompt=True)
        inference_prompt_ids = tokenizer(rendered)["input_ids"]
        labels = item["labels"]
        supervised = [x for x in labels if x != -100]
        if not supervised or len(labels) != len(item["input_ids"]):
            raise ValueError("Empty or misaligned supervised target")
        if labels != [-100] * (len(labels) - len(supervised)) + supervised:
            raise ValueError("Answer mask not a contiguous assistant suffix")
        if item["input_ids"][:len(inference_prompt_ids)] != inference_prompt_ids:
            raise ValueError(f"Train/inference prompt token IDs differ: {row['example_id']}")
        token_stats.append({"example_id": row["example_id"], "total_tokens": len(labels),
                            "supervised_tokens": len(supervised),
                            "prompt_tokens": len(labels) - len(supervised)})

    run_summaries = {}
    for seed in cfg["seeds"]:
        training = load(f"research/artifacts/phase3c/raw/training/{seed}/A.json")
        evaluation = load(f"research/artifacts/phase3c/raw/evaluations/{seed}/A_a.json")
        logs = training["training"]["log"]
        if (len(logs) != 24 or training["training"]["optimizer_steps"] != 24
                or [x["optimizer_step"] for x in logs] != list(range(1, 25))
                or any(not all(math.isfinite(x[k]) for k in ("mean_micro_loss", "grad_norm", "learning_rate"))
                       for x in logs)
                or training["lineage"]["base_weight_hashes_before"] != training["lineage"]["base_weight_hashes_after"]
                or training["data"]["supervised_tokens"] != 3 * sum(x["supervised_tokens"] for x in token_stats)):
            raise ValueError(f"Training log/token mismatch: {seed}")
        if len(evaluation["records"]) != 32 or {r["task_id"] for r in evaluation["records"]} != set(eval_ids):
            raise ValueError(f"Incomplete existing A evaluation: {seed}")
        eval_by_id = {r["task_id"]: r for r in evaluation["records"]}
        for task in eval_tasks:
            user = template.format(task_id=task["task_id"], task_prompt=task["prompt"])
            rendered = tokenizer.apply_chat_template(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                tokenize=False, add_generation_prompt=True)
            token_count = len(tokenizer(rendered, add_special_tokens=True)["input_ids"])
            record = eval_by_id[task["task_id"]]
            if token_count != record["input_tokens"]:
                raise ValueError(f"Evaluation prompt token mismatch: {task['task_id']}")
            if record["failure_category"] != classify(record["normalized_output"], record):
                raise ValueError(f"Failure category mismatch: {task['task_id']}")
            if len(record["case_results"]) != 5:
                raise ValueError(f"Incomplete case results: {task['task_id']}")
            for case, observed in zip(eval_cases[task["task_id"]], record["case_results"], strict=True):
                if (case["case_id"] != observed["case_id"]
                        or observed["normalized_stdout"] != normalized_program_output(observed["stdout"])
                        or observed["expected_stdout"] != case["expected_stdout"].replace("\r\n", "\n").strip()
                        or observed["passed"] != (observed["phase"] == "success" and observed["normalized_stdout"] == observed["expected_stdout"])):
                    raise ValueError(f"Stored scorer case mismatch: {task['task_id']}")
            if record["hidden_pass"] != all(x["passed"] for x in record["case_results"]):
                raise ValueError(f"Stored hidden pass mismatch: {task['task_id']}")
        if summarize(evaluation["records"]) != evaluation["summary"]:
            raise ValueError(f"Stored evaluation summary mismatch: {seed}")
        run_summaries[str(seed)] = {"steps": 24, "finite_logged_losses_gradients_lr": True,
                                    "training_prompt_tokens_match": True,
                                    "stored_eval_task_and_case_scores_match": True,
                                    "base_hashes_match": True}

    result = {"phase": "3C-DIAG", "status": "PASS_DETERMINISTIC_PIPELINE_AUDIT",
              "no_model_generation_or_gradients": True,
              "training_rows": len(ids), "eval_rows": len(eval_ids),
              "training_reference_cases_verified_before_model_run": 300,
              "eval_reference_cases_verified_before_model_run": 160,
              "user_prompt_format_identical": True,
              "train_inference_prompt_token_ids_identical": True,
              "answer_masks_valid": True, "targets_nonempty": True,
              "max_length": cfg["training"]["max_length"],
              "max_observed_train_tokens": max(x["total_tokens"] for x in token_stats),
              "min_supervised_tokens": min(x["supervised_tokens"] for x in token_stats),
              "max_supervised_tokens": max(x["supervised_tokens"] for x in token_stats),
              "training_tokens": token_stats, "run_checks": run_summaries,
              "compiler_sha256": sha256(ROOT / cfg["compiler_artifact"]),
              "interpretation": "No concrete defect found in these deterministic checks; absence of a detected defect is not proof that the complete pipeline is defect-free."}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k != "training_tokens"}, indent=2))


if __name__ == "__main__":
    main()
