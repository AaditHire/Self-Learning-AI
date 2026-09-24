"""Descriptive train-versus-held-out summary after the Phase 3C STOP.

No new decision gate or inferential statistic is introduced.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

from phase3c_contract import ROOT, load_frozen, verify_execution_files


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def metrics(rows: list[dict]) -> dict:
    n = len(rows)
    return {"passed": sum(bool(x["hidden_pass"]) for x in rows), "n": n,
            "pass_at_1": sum(bool(x["hidden_pass"]) for x in rows) / n,
            "failure_taxonomy": dict(sorted(Counter(x["failure_category"] for x in rows).items())),
            "parse_success": sum(bool(x["parse_success"]) for x in rows),
            "compile_success": sum(bool(x["compile_success"]) for x in rows),
            "execution_success": sum(bool(x["execution_success"]) for x in rows),
            "max_output_tokens": max(x["output_tokens"] for x in rows),
            "output_cap_count": sum(x["output_tokens"] >= 512 for x in rows)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    verify_execution_files()
    cfg = load_frozen(check_base=False)
    gate = read(ROOT / "research/artifacts/phase3c/raw/pre_b_acquisition_gate.json")
    if gate["action"] != "STOP_before_B_no_tuning":
        raise ValueError("The confirmatory STOP must remain fixed")
    train_data = read(ROOT / "data/phase3c/a_training_examples.json")
    eval_data = read(ROOT / "benchmark/phase3c/a_eval_tasks.json")
    train_by_id = {x["example_id"]: x for x in train_data}
    eval_by_id = {x["task_id"]: x for x in eval_data}
    by_seed = {}
    for seed in cfg["seeds"]:
        training = read(ROOT / f"research/results/PHASE_3C_DIAG/training_{seed}.json")
        existing = read(ROOT / f"research/artifacts/phase3c/raw/evaluations/{seed}/A_a.json")
        original_run = read(ROOT / f"research/artifacts/phase3c/raw/training/{seed}/A.json")
        if training["status"] != "POST_HOC_DIAGNOSTIC_CONSUMED_TRAINING_SET":
            raise ValueError("Training diagnostic status missing")
        tr, ev = training["records"], existing["records"]
        if ({x["task_id"] for x in tr} != set(train_by_id)
                or {x["task_id"] for x in ev} != set(eval_by_id)
                or len(tr) != 60 or len(ev) != 32):
            raise ValueError(f"Incomplete task-level diagnosis: {seed}")
        if training["adapter_sha256"] != original_run["adapter"]["file_hashes"]["adapter_model.safetensors"]:
            raise ValueError(f"Diagnostic adapter lineage mismatch: {seed}")
        families = {}
        for family in ("numeric_iteration", "array_reduction"):
            tr_subset = [x for x in tr if x["family"] == family]
            ev_subset = [x for x in ev if x["family"] == family]
            train_metric = metrics(tr_subset)
            eval_metric = metrics(ev_subset)
            families[family] = {"training": train_metric, "heldout": eval_metric,
                                "training_minus_heldout_pp": 100 * (train_metric["pass_at_1"] - eval_metric["pass_at_1"])}
        train_metric, eval_metric = metrics(tr), metrics(ev)
        step_log = original_run["training"]["log"]
        if len(step_log) != 24 or not all(math.isfinite(item[field]) for item in step_log
                                            for field in ("mean_micro_loss", "grad_norm", "learning_rate")):
            raise ValueError(f"Original run logs incomplete or nonfinite: {seed}")
        epoch_log = {}
        for epoch in (1, 2, 3):
            subset = [item for item in step_log if item["epoch"] == epoch]
            if len(subset) != 8:
                raise ValueError(f"Original epoch steps incomplete: {seed}/{epoch}")
            epoch_log[str(epoch)] = {
                "first_step_loss": subset[0]["mean_micro_loss"],
                "last_step_loss": subset[-1]["mean_micro_loss"],
                "mean_step_loss": sum(item["mean_micro_loss"] for item in subset) / 8,
                "gradient_norm_min": min(item["grad_norm"] for item in subset),
                "gradient_norm_max": max(item["grad_norm"] for item in subset),
                "learning_rate_first": subset[0]["learning_rate"],
                "learning_rate_last": subset[-1]["learning_rate"],
            }
        by_seed[str(seed)] = {
            "training": train_metric, "heldout": eval_metric,
            "training_minus_heldout_pp": 100 * (train_metric["pass_at_1"] - eval_metric["pass_at_1"]),
            "families": families,
            "training_archetypes": {name: metrics([x for x in tr if x["archetype"] == name])
                                    for name in sorted({x["archetype"] for x in tr})},
            "heldout_archetypes": {name: metrics([x for x in ev if eval_by_id[x["task_id"]]["archetype"] == name])
                                   for name in sorted({x["archetype"] for x in eval_data})},
            "exact_training_target_matches": sum(
                x["normalized_output"] == train_by_id[x["task_id"]]["target"].strip() for x in tr),
            "heldout_pass_task_ids": [x["task_id"] for x in ev if x["hidden_pass"]],
            "training_failed_task_ids": [x["task_id"] for x in tr if not x["hidden_pass"]],
            "existing_training_integrity": {
                "optimizer_steps": original_run["training"]["optimizer_steps"],
                "trainable_parameters": original_run["training"]["trainable_parameters"],
                "supervised_tokens": original_run["data"]["supervised_tokens"],
                "base_revision": original_run["lineage"]["base_revision"],
                "parent_adapter_path": original_run["lineage"]["parent_adapter_path"],
                "base_hashes_before_after_equal": original_run["lineage"]["base_weight_hashes_before"] == original_run["lineage"]["base_weight_hashes_after"],
                "adapter_sha256": original_run["adapter"]["file_hashes"]["adapter_model.safetensors"],
                "final_checkpoint_rule": "final step 24, no metric selection",
                "nan_inf_logged": False,
                "oom_recorded": False,
                "learning_rate_first": step_log[0]["learning_rate"],
                "learning_rate_peak": max(item["learning_rate"] for item in step_log),
                "learning_rate_final": step_log[-1]["learning_rate"],
                "gradient_norm_min": min(item["grad_norm"] for item in step_log),
                "gradient_norm_max": max(item["grad_norm"] for item in step_log),
                "epoch_log": epoch_log,
                "step_log": step_log,
            },
        }
    result = {"phase": "3C-DIAG", "status": "POST_HOC_DESCRIPTIVE_ANALYSIS",
              "confirmatory_phase3c_decision": gate["action"],
              "training_set_consumed_for_diagnosis": True,
              "phase3c_eval_a_consumed_for_confirmatory_reuse": True,
              "gap_definition": "training pass@1 minus previously observed EVAL_A pass@1 in percentage points",
              "warning": "Train/eval gaps are descriptive across different archetypes; no new pass/fail gate or causal effect estimate.",
              "by_seed": by_seed}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({seed: {"training": row["training"]["passed"],
                             "heldout": row["heldout"]["passed"]}
                      for seed, row in by_seed.items()}))


if __name__ == "__main__":
    main()
