"""Seal the reviewed DEV2 design inputs; no model/gradient import."""

import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"research/protocols/phase3c_dev2_manifest.json"
PATHS=(
    "research/protocols/phase3c_dev2_protocol.md",
    "research/protocols/phase3c_dev2_config.json",
    "research/protocols/phase3c_dev2_schedule.json",
    "scripts/build_phase3c_dev2_data.py",
    "scripts/build_phase3c_dev2_schedule.py",
    "scripts/audit_phase3c_dev2.py",
    "scripts/audit_phase3c_dev2_tokens.py",
    "scripts/freeze_phase3c_dev2_manifest.py",
    "data/phase3c_dev2/a_isolated_training_examples.json",
    "data/phase3c_dev2/a_isolated_training_references.json",
    "data/phase3c_dev2/a_isolated_training_hidden_tests.json",
    "data/phase3c_dev2/a_composition_training_examples.json",
    "data/phase3c_dev2/a_composition_training_references.json",
    "data/phase3c_dev2/a_composition_training_hidden_tests.json",
    "benchmark/phase3c_dev2/a_development_eval_tasks.json",
    "benchmark/phase3c_dev2/a_development_eval_references.json",
    "benchmark/phase3c_dev2/a_development_eval_hidden_tests.json",
    "research/results/PHASE_3C_DEV2/pre_gradient_audit.json",
    "research/results/PHASE_3C_DEV2/structural_pairs.json",
    "research/results/PHASE_3C_DEV2/token_budget_audit.json",
)


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n")).hexdigest()


def main():
    if OUT.exists(): raise FileExistsError(OUT)
    audit=json.loads((ROOT/"research/results/PHASE_3C_DEV2/pre_gradient_audit.json").read_text(encoding="utf-8"))
    tokens=json.loads((ROOT/"research/results/PHASE_3C_DEV2/token_budget_audit.json").read_text(encoding="utf-8"))
    schedule=json.loads((ROOT/"research/protocols/phase3c_dev2_schedule.json").read_text(encoding="utf-8"))
    config=json.loads((ROOT/"research/protocols/phase3c_dev2_config.json").read_text(encoding="utf-8"))
    assert audit["status"]=="PRE_GRADIENT_REFERENCE_AND_STRUCTURE_AUDIT"
    assert all(x["passed"]==x["references"] for x in audit["reference_validation"].values())
    assert len(audit["central_coverage_proof"])==32 and all(not r["missing_in_isolated"] and not r["missing_in_composition"] for r in audit["central_coverage_proof"])
    assert tokens["compute_gate"]=="PASS"
    assert schedule["seeds"]==config["seeds"]==[20270925,20271013,20271119]
    assert all((ROOT/p).is_file() for p in PATHS)
    packages={}
    for name in ("python", "torch","transformers","bitsandbytes","peft"):
        packages[name]=platform.python_version() if name=="python" else importlib.metadata.version(name)
    prior=json.loads((ROOT/"research/protocols/phase3c_dev1_manifest.json").read_text(encoding="utf-8"))
    manifest={"phase":"3C-DEV2","status":"FROZEN_DESIGN_PROPOSAL_NO_MODEL_EXECUTION",
              "source_checkpoint_commit":"c0281953ab19eeca863157a99402d3b7162a09db",
              "seeds":config["seeds"],"conditions":config["conditions"],
              "counts":{"isolated_training":60,"composition_training":60,"development":48,
                        "reference_cases_validated":840,"structural_pairs":5760,
                        "slots_per_seed_condition":180,"optimizer_steps_per_seed_condition":24},
              "compiler_sha256":audit["compiler_sha256"],
              "base_weights":config["base_weights"],
              "tokenizer_file_sha256":prior["tokenizer_file_sha256"],
              "environment_at_design_freeze":{"platform":platform.platform(),"packages":packages},
              "file_normalized_sha256":{p:digest(ROOT/p) for p in PATHS},
              "hash_policy":"SHA-256 of file bytes with CRLF normalized to LF for Git text portability; model and compiler binaries use raw hashes",
              "model_execution_authorized":False,"sealed_holdout_accessed":False}
    OUT.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print("froze",len(PATHS),"DEV2 design files")

if __name__=="__main__": main()
