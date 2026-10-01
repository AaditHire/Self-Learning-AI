"""Read-only saved requirement artifact verification; no constructor/producer."""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from self_learning_ai.conf1_v3.requirement_verifier import verify_plan,verify_requirement_evidence
from self_learning_ai.conf1_v3.requirements import digest,frozen_metadata
from self_learning_ai.conf1_v3.interfaces import ClosureError,canonical_json_bytes
from audit_conf1_v3_core_closure import verify_protected_inputs
OUT=ROOT/"research/implementation_notes/coverage_v3_canonical_requirements"
def read(name): return json.loads((OUT/name).read_bytes())
def run():
    verify_protected_inputs()
    science=read("frozen_training_slot_requirement_derivation.json")["records"]
    expected={s["slot_id"].replace("CONF1-",f"CONF1-{condition}-",1) for s in frozen_metadata()["slots"]["training_paired_slots"] for condition in ("ISOLATED","COMPOSITION")}
    if len(science)!=len(expected) or {p["program_id"] for p in science}!=expected: raise RuntimeError("frozen training metadata plans missing/duplicated/extra")
    checks=read("independent_requirement_verifier_results.json")
    if canonical_json_bytes([verify_plan(p) for p in science])!=canonical_json_bytes(checks["scientific_metadata_verification"]): raise RuntimeError("saved scientific foundation verification differs")
    records=read("canonical_requirement_evidence_bindings.json")["records"]
    actual=[dict(case_id=r["case_id"],evidence_sha256=digest(r["evidence"]),verification=verify_requirement_evidence(r["evidence"])) for r in records]
    if canonical_json_bytes(actual)!=canonical_json_bytes(checks["development_mapping_verification"]): raise RuntimeError("saved development verification differs")
    by_id={r["case_id"]:r["evidence"] for r in records}
    for attack in checks["serialized_mutations"]:
        value=deepcopy(by_id[attack["base_case_id"]]); target=value
        for p in attack["replace_path"][:-1]: target=target[p]
        target[attack["replace_path"][-1]]=attack["replace_value"]
        try: verify_requirement_evidence(value)
        except ClosureError as exc:
            if str(exc)!=attack["expected_reason"] or str(exc)!=attack["actual_reason"]: raise RuntimeError("saved mutation differs") from exc
        else: raise RuntimeError("saved mutation accepted")
    inventory=read("development_only_projection_inventory.json")["records"]
    if canonical_json_bytes(inventory)!=canonical_json_bytes([dict(case_id=r["case_id"],projection=r["evidence"]["before"]) for r in records]): raise RuntimeError("projection inventory changed")
    raw=read("raw_key_classification.json")["records"]
    if canonical_json_bytes(raw)!=canonical_json_bytes([dict(case_id=r["case_id"],records=r["evidence"]["raw_classification"]) for r in records]): raise RuntimeError("raw classification changed")
    claims=read("v33_integrated_equivalence_claims.json")["records"]
    if canonical_json_bytes(claims)!=canonical_json_bytes([dict(case_id=r["case_id"],claims=r["evidence"]["integrated_claims"]) for r in records]): raise RuntimeError("claim inventory changed")
    invariant=read("requirement_preservation_no_cross_scope_invariant.json")
    if canonical_json_bytes(invariant["development_mappings"])!=canonical_json_bytes(actual): raise RuntimeError("saved invariant differs")
    if canonical_json_bytes(invariant["scientific_metadata_plans"])!=canonical_json_bytes([dict(program_id=p["program_id"],before_sha256=p["requirements_sha256"],after_sha256=p["requirements_sha256"],mapping_run=False) for p in science]): raise RuntimeError("scientific preservation record differs")
    gates=read("development_gate_evidence.json"); baseline=ROOT/gates["out_of_scope_gate_authority_path"]
    ledger=frozen_metadata(); source_ids=expected|{s["task_id"] for group in ("primary","primitive_sanity","structural_transfer") for s in ledger["slots"][group]}
    source_witnesses={r["evidence"]["before"]["program_id"] for r in records if r["evidence"]["before"]["scope"] in {"SCIENTIFIC_TRAINING","SCIENTIFIC_EVALUATION"}}
    if gates["declared_global_scope"]!="FROZEN_TRAINING_AND_EVALUATION_SOURCE_PROGRAMS" or gates["expected_scientific_source_records"]!=len(source_ids) or gates["verified_scientific_source_records"]!=len(source_witnesses): raise RuntimeError("global gate source scope changed")
    if hashlib.sha256(baseline.read_bytes()).hexdigest()!=gates["baseline_gate_artifact_sha256"]: raise RuntimeError("baseline gates changed")
    targets={"INDICATOR_EXTRACTION_COMPLETE","V32_SEMANTIC_MAPPING_COMPLETE","V33_REQUIRED_EQUIVALENCE_COMPLETE"}
    if any(a!=b for a,b in zip(json.loads(baseline.read_bytes())["gates"],gates["gates"]) if a["gate"] not in targets): raise RuntimeError("other five gate records changed")
    if any(g["status"]!="UNRESOLVED" for g in gates["gates"] if g["gate"] in targets): raise RuntimeError("unsupported global gate closure")
    print(json.dumps(dict(scientific_metadata_plans_verified=len(science),development_mapping_records_verified=len(records),mutations_rejected=len(checks["serialized_mutations"]),other_five_gates_unchanged=True,writes=0,constructor_invoked=False,population_producer_invoked=False),indent=2))
if __name__=="__main__": run()
