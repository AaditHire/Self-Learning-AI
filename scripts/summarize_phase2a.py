from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with (ROOT / relative).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    config = load("research/protocols/phase2a_config.json")
    validation = load("research/results/EXP-0014/data_validation.json")
    smoke = load("research/results/EXP-0015/smoke.json")
    training = load("research/results/EXP-0016/training.json")
    primary = load("research/results/EXP-0017/primary.json")
    training_eval = load("research/results/EXP-0018/training_performance.json")
    regression = load("research/results/EXP-0019/regression.json")

    base = primary["summaries"]["BASE_NO_DOCS"]
    adapted = primary["summaries"]["ADAPTED_NO_DOCS"]
    paired = primary["paired_comparison"]
    train_summary = training_eval["summaries"]["ADAPTED_NO_DOCS"]

    passing = {
        row["task_id"]
        for row in primary["conditions"]["ADAPTED_NO_DOCS"]
        if row["hidden_pass"]
    }
    flagged = {
        row["evaluation_task_id"]
        for row in validation["structural_split"]["code_flags_at_or_above_0p90"]
    }
    flagged_passes = sorted(passing & flagged)
    unflagged_passes = sorted(passing - flagged)
    family_passes = {
        family: metrics["hidden_pass_count"]
        for family, metrics in adapted["by_family"].items()
    }

    base_regression = regression["summaries"]["BASE_NO_DOCS"]
    adapted_regression = regression["summaries"]["ADAPTED_NO_DOCS"]
    regression_drop_tasks = base_regression["correct"] - adapted_regression["correct"]
    regression_drop_rate = base_regression["accuracy"] - adapted_regression["accuracy"]

    criteria = {
        "improvement_at_least_15_points": paired["paired_risk_difference"] >= 0.15,
        "adapted_pass_rate_at_least_20_percent": adapted["overall"]["hidden_pass"] >= 0.20,
        "successes_in_at_least_four_families": sum(value > 0 for value in family_passes.values()) >= 4,
        "not_explained_by_structural_duplication": (
            validation["structural_split"]["train_eval_lineage_overlap"] == 0
            and validation["structural_split"]["train_eval_algorithm_label_overlap"] == 0
            and not validation["structural_split"]["prompt_flags_at_or_above_0p75"]
            and len(unflagged_passes) > 0
        ),
        "no_severe_general_regression_collapse": regression_drop_rate <= 0.20 and regression_drop_tasks <= 4,
    }

    adapter_dir = ROOT / config["training"]["adapter_output"]
    adapter_hashes = {
        path.name: sha256(str(path.relative_to(ROOT)))
        for path in sorted(adapter_dir.iterdir())
        if path.is_file()
    }
    result_paths = [
        "research/results/EXP-0015/smoke.json",
        "research/results/EXP-0016/training.json",
        "research/results/EXP-0017/primary.json",
        "research/results/EXP-0018/training_performance.json",
        "research/results/EXP-0019/regression.json",
    ]

    summary = {
        "phase": "2A-exploratory-qlora-feasibility",
        "scientific_status": "developmental/exploratory; not confirmatory",
        "start_commit": config["start_commit"],
        "preregistration_commit": "b5fe9b3b5e8d95d319ebc1e14bd14aa1df492f9b",
        "config_sha256": sha256("research/protocols/phase2a_config.json"),
        "phase1t_gate_remains": "FAIL",
        "optional_base_docs_reference": "NOT RUN; optional and barred from checkpoint selection",
        "smoke": {
            "passed": smoke["smoke_gate"]["passed"],
            "optimizer_steps": smoke["training"]["optimizer_steps"],
            "peak_gpu_allocated_bytes": smoke["training"]["peak_gpu_allocated_bytes"],
            "peak_gpu_reserved_bytes": smoke["training"]["peak_gpu_reserved_bytes"],
            "peak_process_rss_bytes": smoke["training"]["peak_process_rss_bytes"],
            "supervised_tokens_per_second": smoke["training"]["supervised_tokens_per_second"],
        },
        "training": {
            "optimizer_steps": training["training"]["optimizer_steps"],
            "expected_optimizer_steps": training["training"]["expected_optimizer_steps"],
            "seconds": training["training"]["training_seconds"],
            "first_logged_mean_micro_loss": training["training"]["log"][0]["mean_micro_loss"],
            "last_logged_mean_micro_loss": training["training"]["log"][-1]["mean_micro_loss"],
            "all_losses_finite": training["stability"]["all_losses_finite"],
            "peak_gpu_allocated_bytes": training["training"]["peak_gpu_allocated_bytes"],
            "peak_gpu_reserved_bytes": training["training"]["peak_gpu_reserved_bytes"],
            "peak_process_rss_bytes": training["training"]["peak_process_rss_bytes"],
            "supervised_tokens_per_second": training["training"]["supervised_tokens_per_second"],
            "base_weight_hashes_unchanged": training["model"]["base_weight_hashes_before"] == training["model"]["base_weight_hashes_after"],
        },
        "primary": {
            "base_no_docs": base["overall"],
            "adapted_no_docs": adapted["overall"],
            "paired": paired,
            "adapted_family_passes": family_passes,
        },
        "overfitting": {
            "training_hidden_pass_count": train_summary["overall"]["hidden_pass_count"],
            "training_total": train_summary["overall"]["n"],
            "training_hidden_pass_rate": train_summary["overall"]["hidden_pass"],
            "heldout_hidden_pass_rate": adapted["overall"]["hidden_pass"],
            "train_minus_heldout_gap": train_summary["overall"]["hidden_pass"] - adapted["overall"]["hidden_pass"],
            "interpretation": "large gap; potential memorization and narrow transfer",
        },
        "structural_audit": {
            "exact_prompt_reuse": validation["structural_split"].get("exact_prompt_reuse", 0),
            "lineage_overlap": validation["structural_split"]["train_eval_lineage_overlap"],
            "algorithm_label_overlap": validation["structural_split"]["train_eval_algorithm_label_overlap"],
            "prompt_flags_at_or_above_0p75": len(validation["structural_split"]["prompt_flags_at_or_above_0p75"]),
            "coarse_code_flags_at_or_above_0p90": len(flagged),
            "flagged_passes": flagged_passes,
            "flagged_pass_rate": len(flagged_passes) / len(flagged),
            "unflagged_passes": unflagged_passes,
            "unflagged_pass_rate": len(unflagged_passes) / (64 - len(flagged)),
            "decision": "operational criterion passes after pretraining manual review; coarse structural correlation remains a major limitation",
        },
        "regression": {
            "base": base_regression,
            "adapted": adapted_regression,
            "drop_tasks": regression_drop_tasks,
            "drop_rate": regression_drop_rate,
            "paired": regression["paired"],
            "severe_collapse": regression_drop_rate > 0.20 or regression_drop_tasks > 4,
        },
        "success_criteria": criteria,
        "decision": "PASS" if all(criteria.values()) else "FAIL",
        "supported_claim": "QLoRA can produce development-set evidence consistent with parameterized GOCO behavioral acquisition in this setup.",
        "unsupported_claims": [
            "continual learning",
            "self-learning",
            "autonomous learning",
            "robust retention",
            "human-like understanding",
            "general parameterized acquisition",
        ],
        "adapter_hashes": adapter_hashes,
        "result_file_hashes": {path: sha256(path) for path in result_paths},
        "protocol_deviations": [],
        "unsuccessful_training_runs": [],
    }

    manifest = {
        "candidate_id": "c0001-phase2a-qlora",
        "parent": {
            "model_id": config["model"]["id"],
            "revision": config["model"]["revision"],
            "weight_file_sha256": config["model"]["weight_file_sha256"],
            "immutable_before_after": summary["training"]["base_weight_hashes_unchanged"],
        },
        "adapter_policy": "versioned PEFT QLoRA adapter; never merged into research base",
        "adapter_files_sha256": adapter_hashes,
        "training_dataset_canonical_sha256": validation["canonical_hashes"]["training"],
        "development_suite_canonical_sha256": validation["canonical_hashes"]["development"],
        "regression_suite_canonical_sha256": validation["canonical_hashes"]["regression"],
        "compiler_sha256": validation["compiler_sha256"],
        "training_config_sha256": summary["config_sha256"],
        "random_seed": config["seed"],
        "preregistration_commit": summary["preregistration_commit"],
        "results": summary["result_file_hashes"],
        "decision": summary["decision"],
    }

    summary_path = ROOT / "research/results/PHASE_2A/summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest_path = ROOT / "research/manifests/phase2a_adapter_c0001.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
