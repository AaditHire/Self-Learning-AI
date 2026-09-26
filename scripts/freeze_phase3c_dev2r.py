"""Record immutable DEV2R design and six original adapter identities; no model use."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/protocols/phase3c_dev2r_manifest.json"
INPUTS = (
    "research/protocols/phase3c_dev2_config.json",
    "research/protocols/phase3c_dev2_protocol.md",
    "research/protocols/phase3c_dev2_schedule.json",
    "research/protocols/phase3c_dev2r_protocol.md",
    "benchmark/phase3c_dev2r/a_development_eval_tasks.json",
    "benchmark/phase3c_dev2r/a_development_eval_references.json",
    "benchmark/phase3c_dev2r/a_development_eval_hidden_tests.json",
    "research/results/PHASE_3C_DEV2R/structural_pairs.json",
    "research/results/PHASE_3C_DEV2R/structural_audit.json",
    "research/results/PHASE_3C_DEV2R/reference_validation.json",
    "data/phase3c_dev2/a_isolated_training_examples.json",
    "data/phase3c_dev2/a_isolated_training_references.json",
    "data/phase3c_dev2/a_isolated_training_hidden_tests.json",
    "data/phase3c_dev2/a_composition_training_examples.json",
    "data/phase3c_dev2/a_composition_training_references.json",
    "data/phase3c_dev2/a_composition_training_hidden_tests.json",
    "prompts/phase1t_system.txt", "prompts/phase1t_user_template.txt",
    "scripts/build_phase3c_dev2r_data.py", "scripts/audit_phase3c_dev2r.py",
    "scripts/freeze_phase3c_dev2r.py",
    "scripts/evaluate_phase3c_dev2r.py", "src/self_learning_ai/dev2r_evaluation.py",
    "tests/test_phase3c_dev2r_evaluation.py", "src/self_learning_ai/benchmark.py",
    "src/self_learning_ai/compiler.py", ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar",
)


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()


def main():
    if OUT.exists(): raise FileExistsError(OUT)
    preservation = json.loads((ROOT / "research/manifests/phase3c_dev2_partial_artifact_preservation.json").read_text())
    stored = {item["original_path"]: item for item in preservation["artifacts"]}
    identities = {}
    for seed in (20270925, 20271013, 20271119):
        for condition in ("isolated", "composition"):
            rel = f".runtime/phase3c_dev2/adapters/{seed}/{condition}/adapter_model.safetensors"
            expected = stored[rel]
            actual = sha(ROOT / rel)
            size = (ROOT / rel).stat().st_size
            if actual != expected["sha256"] or size != expected["size_bytes"]:
                raise ValueError(f"Adapter mismatch: {rel}")
            record = json.loads((ROOT / f".runtime/phase3c_dev2/training/{seed}/{condition}.json").read_text())
            if actual != record["adapter"]["file_hashes"]["adapter_model.safetensors"]:
                raise ValueError(f"Training lineage mismatch: {rel}")
            identities[f"{seed}/{condition}"] = {"path": rel, "sha256": actual,
                "size_bytes": size, "preservation_backup_path": expected["backup_path"],
                "training_record": f".runtime/phase3c_dev2/training/{seed}/{condition}.json"}
    value = {"phase": "3C-DEV2R", "status": "FROZEN_PRE_INFERENCE",
        "original_dev2_development_status": "CONSUMED_FROM_ATTEMPTED_USE",
        "model_execution_authorized": False, "base_config": "research/protocols/phase3c_dev2_config.json",
        "input_sha256": {rel: sha(ROOT / rel) for rel in INPUTS},
        "adapter_identity": identities, "design_task_count": 48,
        "reference_semantic_cases_passed": 240,
        "structural_training_pairs": 5760,
        "historical_own_training_completed": "20270925/isolated:60/60",
        "pending_own_training_cells": [f"{s}/{c}" for s in (20270925,20271013,20271119)
            for c in ("isolated","composition") if (s,c) != (20270925,"isolated")]}
    OUT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"adapters_verified": len(identities), "input_hashes": len(INPUTS)}))


if __name__ == "__main__": main()
