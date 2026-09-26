"""Freeze prospective DEV2R v2 science and infrastructure without model use."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/protocols/phase3c_dev2r_v2_manifest.json"
NEW_INPUTS = (
    "research/protocols/phase3c_dev2r_v2_amendment.md",
    "benchmark/phase3c_dev2r_v2/a_development_eval_tasks.json",
    "benchmark/phase3c_dev2r_v2/a_development_eval_references.json",
    "benchmark/phase3c_dev2r_v2/a_development_eval_hidden_tests.json",
    "research/results/PHASE_3C_DEV2R_AMENDMENT/primitive_sanity_original_essentiality.json",
    "research/results/PHASE_3C_DEV2R_AMENDMENT/replacement_map.json",
    "research/results/PHASE_3C_DEV2R_AMENDMENT/replacement_structural_pairs.json",
    "research/results/PHASE_3C_DEV2R_AMENDMENT/v2_pre_execution_audit.json",
    "research/results/PHASE_3C_DEV2R_AMENDMENT/v2_reference_validation.json",
    "research/results/PHASE_3C_DEV2R_AMENDMENT/report.md",
    "research/results/PHASE_3C_DEV2R_PREEXEC_STOP/api_construct_coverage.json",
    "research/results/PHASE_3C_DEV2R_ESSENTIALITY/essentiality_audit.json",
    "scripts/audit_phase3c_dev2r_sanity_essentiality.py",
    "scripts/build_phase3c_dev2r_v2_sanity.py",
    "scripts/audit_phase3c_dev2r_v2.py",
    "scripts/freeze_phase3c_dev2r_v2.py",
)


def sha(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def portable_sha(path: Path):
    if path.suffix.lower() in {".json", ".md", ".py", ".txt", ".jinja"}:
        return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    return sha(path)


def main():
    if OUT.exists(): raise FileExistsError(OUT)
    old_path = ROOT / "research/protocols/phase3c_dev2r_manifest.json"
    old = json.loads(old_path.read_text(encoding="utf-8"))
    immutable = [rel for rel in old["input_sha256"] if rel.startswith((
        "data/phase3c_dev2/", "benchmark/phase3c_dev2r/", "research/protocols/phase3c_dev2_",
        "research/protocols/phase3c_dev2r_protocol.md", "research/results/PHASE_3C_DEV2R/",
        "prompts/"))]
    if any(sha(ROOT / rel) != old["input_sha256"][rel] for rel in immutable):
        raise ValueError("Original frozen scientific input changed")
    identities = old["adapter_identity"]
    if any(sha(ROOT / item["path"]) != item["sha256"] or
           (ROOT / item["path"]).stat().st_size != item["size_bytes"]
           for item in identities.values()):
        raise ValueError("DEV2 adapter mismatch")
    audit = json.loads((ROOT / "research/results/PHASE_3C_DEV2R_AMENDMENT/v2_pre_execution_audit.json").read_text())
    validation = json.loads((ROOT / "research/results/PHASE_3C_DEV2R_AMENDMENT/v2_reference_validation.json").read_text())
    if audit["status"] != "PASS_PRE_INFERENCE_SCIENTIFIC_GATES" or validation["passed_cases"] != 240:
        raise ValueError("V2 scientific gate incomplete")
    inputs = sorted(set(old["input_sha256"]) | set(NEW_INPUTS))
    current_hashes = {relative: portable_sha(ROOT / relative) for relative in inputs}
    v2_prefix = "benchmark/phase3c_dev2r_v2/a_development_eval_"
    v1_prefix = "benchmark/phase3c_dev2r/a_development_eval_"
    value = {
        "phase": "3C-DEV2R-v2", "status": "FROZEN_PRE_EXECUTION",
        "model_execution_authorized": False,
        "original_design_commit": "cdff638153df13c5da2d77b4eda908385c1a6423",
        "pre_execution_stop_commit": "c5d26366345cb228c3bafb7c64d51ec58d39ca95",
        "structural_essentiality_commit": "1815279f0f8acf4266aab58b1cf2215edf55efe4",
        "amendment_commit_identity": "Git commit containing this manifest (SHA reported after commit creation)",
        "original_design_manifest_normalized_sha256": portable_sha(old_path),
        "hash_policy": "LF-normalized SHA-256 for text inputs; byte-exact SHA-256 for compiler binaries and adapter weights",
        "old_execution_code_sha256": old["input_sha256"]["scripts/evaluate_phase3c_dev2r.py"],
        "new_execution_code_sha256": current_hashes["scripts/evaluate_phase3c_dev2r.py"],
        "input_sha256": current_hashes,
        "suite_version": "phase3c_dev2r_v2",
        "suite_file_sha256": {"v1": {s: portable_sha(ROOT / (v1_prefix + s + ".json"))
                                      for s in ("tasks", "references", "hidden_tests")},
                              "v2": {s: portable_sha(ROOT / (v2_prefix + s + ".json"))
                                      for s in ("tasks", "references", "hidden_tests")}},
        "original_suite_preserved": True,
        "primitive_sanity_replacements": 16,
        "scientific_gates": audit["final_gate"],
        "reference_validation": {"references": 48, "cases": 240, "passed": 240},
        "adapter_identity": identities,
        "historical_own_training_completed": old["historical_own_training_completed"],
        "pending_own_training_cells": old["pending_own_training_cells"],
        "original_dev2_development_status": "CONSUMED_FROM_ATTEMPTED_USE",
        "sealed_final_paper_holdout_touched": False,
        "model_inference_performed_under_dev2r": False,
    }
    OUT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"inputs": len(inputs), "adapters": len(identities),
                      "authorized": value["model_execution_authorized"]}))


if __name__ == "__main__": main()
