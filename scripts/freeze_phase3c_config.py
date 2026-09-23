"""Freeze Phase 3C design inputs and code hashes, without loading a model."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path


FILES = (
    "research/protocols/phase3c_protocol.md",
    "research/protocols/phase3c_replay_schedule.json",
    "research/results/EXP-0048/data_validation.json",
    "research/results/EXP-0048/construction_attempts.json",
    "research/results/EXP-0048/structural_overlap_manual_review.md",
    "data/phase3c/a_training_examples.json",
    "data/phase3c/a_training_hidden_tests.json",
    "data/phase3c/b_training_examples.json",
    "data/phase3c/b_training_hidden_tests.json",
    "benchmark/phase3c/a_eval_tasks.json",
    "benchmark/phase3c/a_eval_hidden_tests.json",
    "benchmark/phase3c/a_eval_references.json",
    "benchmark/phase3c/b_eval_tasks.json",
    "benchmark/phase3c/b_eval_hidden_tests.json",
    "benchmark/phase3c/b_eval_references.json",
    "benchmark/phase2b/general_regression.json",
    "prompts/phase1t_system.txt",
    "prompts/phase1t_user_template.txt",
    "scripts/build_phase3c_data.py",
    "scripts/validate_phase3c_data.py",
    "scripts/build_phase3c_schedule.py",
    "scripts/freeze_phase3c_config.py",
    "scripts/train_phase3b_qlora.py",
    "scripts/run_phase3b_evaluation.py",
    "src/self_learning_ai/benchmark.py",
    "src/self_learning_ai/compiler.py",
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repository_text_sha(path: Path) -> str:
    """Hash LF-normalized content as stored by Git text normalization."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> None:
    output = Path("research/protocols/phase3c_config.json")
    if output.exists():
        raise FileExistsError(output)
    prior = json.loads(Path("research/protocols/phase3b_config.json").read_text(encoding="utf-8"))
    audit = json.loads(Path("research/results/EXP-0048/data_validation.json").read_text(encoding="utf-8"))
    if audit["compiler_sha256"] != prior["compiler_sha256"] or sha(Path(".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")) != prior["compiler_sha256"]:
        raise ValueError("Compiler hash mismatch")
    if audit["reference_failures"] or audit["consumed_prompt_reuse"] or audit["consumed_code_rejects_0p98"] or audit["train_eval_code_rejects_0p98"] or audit["exact_current_prompt_collision"]:
        raise ValueError("Phase 3C data audit did not pass")
    hashes = {name: sha(Path(name)) for name in FILES}
    if any(hashes.get(name) != value for name, value in audit["file_sha256"].items()):
        raise ValueError("Dataset changed after compiler audit")
    for name in ("benchmark/phase2b/general_regression.json", "prompts/phase1t_system.txt",
                 "prompts/phase1t_user_template.txt", "scripts/train_phase3b_qlora.py",
                 "scripts/run_phase3b_evaluation.py"):
        if hashes[name] != prior["input_file_hashes"][name]:
            raise ValueError(f"Frozen Phase 3B comparator changed: {name}")
    packages = {name: importlib.metadata.version(name) for name in
                ("torch", "transformers", "peft", "bitsandbytes", "accelerate", "numpy", "safetensors")}
    cases_passed = sum(len(r["score"]["case_results"])
                       for rows in audit["verification"].values() for r in rows)
    if cases_passed != 920:
        raise ValueError("Expected 920 verified semantic cases")
    config = {
        "phase": "3C-retention-valid-20-percent-fixed-budget-replay",
        "status": "proposed_frozen_design_before_model_execution",
        "base_weights": prior["model"],
        "compiler_sha256": prior["compiler_sha256"],
        "compiler_artifact": ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar",
        "compiler_java": ".tools/jdk-25.0.1+8/bin/java.exe",
        "seeds": [20260925, 20261013, 20261119],
        "capabilities": prior["capabilities"],
        "training": prior["training"],
        "evaluation": {key: value for key, value in prior["evaluation"].items()
                       if key not in ("primary_metric", "base_seed", "required_conditions")},
        "pre_b_eligibility": {"overall_pass_min_of_32_each_seed": 24,
                              "each_a_subskill_pass_min_of_16_each_seed": 10,
                              "each_a_archetype_pass_min_of_8_each_seed": 2,
                              "on_failure": "STOP_before_B_no_tuning"},
        "co_primary": {"retention_replay_minus_naive_mean_min_pp": 20,
                       "retention_replay_min_fraction_each_seed": .50,
                       "aggregate_a_replay_minus_naive_mean_min_pp": 10},
        "b_acquisition": {"naive_overall_net_gain_min_of_32_each_seed": 12,
                          "naive_each_subskill_net_gain_min_of_16_each_seed": 4,
                          "naive_each_archetype_net_gain_min_of_8_each_seed": 2,
                          "replay_mean_gain_fraction_of_naive_min": .75,
                          "replay_each_subskill_gain_each_seed": "positive",
                          "replay_overall_score_max_drop_from_naive_each_seed": 9},
        "regression_max_drop_items_of_64": 9,
        "bootstrap": {"task_cluster_draws": 10000, "seed": 20261221,
                      "preserve_seed_and_branch_observations_per_task": True,
                      "archetype_block_sensitivity": True},
        "data_counts": audit["counts"],
        "reference_semantic_cases_passed": cases_passed,
        "file_sha256": hashes,
        "git_text_content_sha256": {name: repository_text_sha(Path(name)) for name in FILES},
        "environment_at_design_freeze": {"python": sys.version.split()[0],
                                         "platform": platform.platform(), "packages": packages},
        "runtime_root": ".runtime/phase3c",
        "archive_policy": "final adapters and essential raw records in versioned off-machine storage; independent remote hash and full restore verification",
        "prohibitions": ["model training during design", "confirmatory model evaluation during design",
                         "sealed final-paper holdout access", "replay-ratio sweep", "other intervention",
                         "base-weight modification", "GOCO product repository modification"],
    }
    output.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"{output}: {sha(output)}")


if __name__ == "__main__":
    main()
