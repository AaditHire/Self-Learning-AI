"""Freeze design inputs and audit evidence; this script never loads a model."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/protocols/phase3c_dev1_manifest.json"
FILES = (
    "research/protocols/phase3c_dev1_protocol.md",
    "research/protocols/phase3c_dev1_schedule.json",
    "research/results/PHASE_3C_DEV1/reference_validation.json",
    "research/results/PHASE_3C_DEV1/structural_audit.json",
    "research/results/PHASE_3C_DEV1/token_budget_audit.json",
    "data/phase3c_dev1/a_dense_training_examples.json",
    "data/phase3c_dev1/a_dense_training_references.json",
    "data/phase3c_dev1/a_dense_training_hidden_tests.json",
    "data/phase3c_dev1/a_diverse_training_examples.json",
    "data/phase3c_dev1/a_diverse_training_references.json",
    "data/phase3c_dev1/a_diverse_training_hidden_tests.json",
    "benchmark/phase3c_dev1/a_development_eval_tasks.json",
    "benchmark/phase3c_dev1/a_development_eval_references.json",
    "benchmark/phase3c_dev1/a_development_eval_hidden_tests.json",
    "scripts/build_phase3c_dev1_data.py",
    "scripts/validate_phase3c_dev1_data.py",
    "scripts/audit_phase3c_dev1_structure.py",
    "scripts/audit_phase3c_dev1_tokens.py",
    "scripts/build_phase3c_dev1_schedule.py",
    "scripts/freeze_phase3c_dev1_manifest.py",
    "scripts/train_phase3b_qlora.py",
    "scripts/train_phase2a_qlora.py",
    "scripts/run_phase3c_evaluation.py",
    "src/self_learning_ai/benchmark.py",
    "src/self_learning_ai/compiler.py",
    "research/protocols/phase3c_config.json",
    "prompts/phase1t_system.txt",
    "prompts/phase1t_user_template.txt",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    prior = json.loads((ROOT / "research/protocols/phase3c_config.json").read_text(encoding="utf-8"))
    validation = json.loads((ROOT / "research/results/PHASE_3C_DEV1/reference_validation.json").read_text(encoding="utf-8"))
    token = json.loads((ROOT / "research/results/PHASE_3C_DEV1/token_budget_audit.json").read_text(encoding="utf-8"))
    structural = json.loads((ROOT / "research/results/PHASE_3C_DEV1/structural_audit.json").read_text(encoding="utf-8"))
    schedule = json.loads((ROOT / "research/protocols/phase3c_dev1_schedule.json").read_text(encoding="utf-8"))
    if validation["status"] != "PASS_REFERENCE_VALIDATION" or validation["semantic_cases_checked"] != 780:
        raise ValueError("Reference audit not complete")
    if token["compute_gate"] != "PASS":
        raise ValueError("Token exposure gate failed")
    if len(structural["all_train_eval_pairs"]) != 4320:
        raise ValueError("Structural audit incomplete")
    for condition in ("DENSE", "DIVERSE"):
        audited = structural["by_condition"][condition]
        if audited["exact_prompt_overlap_count"] or audited["exact_reference_overlap_count"]:
            raise ValueError("Exact overlap")
    if len(schedule["seeds"]) != 3 or schedule["epochs"] != 3:
        raise ValueError("Schedule shape")
    for seed in schedule["seeds"]:
        for epoch in schedule["by_seed"][str(seed)]:
            for condition in ("dense", "diverse"):
                if len(epoch[f"{condition}_example_ids"]) != 60 or len(set(epoch[f"{condition}_example_ids"])) != 60:
                    raise ValueError("Invalid schedule exposure")
    jar = ROOT / prior["compiler_artifact"]
    if sha256(jar) != prior["compiler_sha256"]:
        raise ValueError("Compiler changed")
    packages = {}
    for name in ("torch", "transformers", "peft", "bitsandbytes", "accelerate", "numpy", "safetensors"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    payload = {
        "phase": "3C-DEV1",
        "status": "FROZEN_DESIGN_PROPOSAL_NO_MODEL_EXECUTION",
        "seeds": schedule["seeds"],
        "counts": {"dense_training": 60, "diverse_training": 60, "fresh_development_eval": 36,
                   "semantic_cases_validated": 780, "structural_pairs_audited": 4320,
                   "slots_per_seed_condition": 180, "optimizer_steps_per_seed_condition": 24},
        "base_weights": prior["base_weights"],
        "training": prior["training"],
        "evaluation": prior["evaluation"],
        "compiler": {"path": prior["compiler_artifact"], "sha256": prior["compiler_sha256"],
                     "java": prior["compiler_java"]},
        "tokenizer_file_sha256": token["tokenizer_file_sha256"],
        "file_sha256": {relative: sha256(ROOT / relative) for relative in FILES},
        "lf_normalized_text_sha256": {
            relative: hashlib.sha256((ROOT / relative).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            for relative in FILES
        },
        "environment_at_design_freeze": {"python": sys.version.split()[0],
                                          "platform": platform.platform(), "packages": packages},
        "future_archive_policy": "Versioned off-machine adapters and raw evaluation records; retrieve from fresh clone and verify every SHA-256 before declaring archived.",
        "execution_authorization": "STOP_FOR_INDEPENDENT_REVIEW",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "files_hashed": len(FILES), "seeds": schedule["seeds"]}))


if __name__ == "__main__":
    main()
