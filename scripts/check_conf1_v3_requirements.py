"""Metadata/development-only evidence producer. No V3.5 entry point."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import hashlib
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tests"),str(ROOT/"src"),str(ROOT/"scripts")]
import creq904_inputs as d
from audit_conf1_v3_core_closure import verify_protected_inputs
from self_learning_ai.conf1_v3.requirements import derive_training_slot, frozen_metadata, evaluation_namespace, digest
from self_learning_ai.conf1_v3.requirement_verifier import verify_plan, verify_requirement_evidence
from self_learning_ai.conf1_v3.interfaces import ClosureError, canonical_json_bytes
OUT=ROOT/"research/implementation_notes/coverage_v3_canonical_requirements"
DIRECT_PAIRS=(("DIRECT","DIRECT"),("DIRECT","ALPHA_DIRECT"),("DIRECT","COMMUTATIVE"),("MUL","MUL_SWAP"),("GT","LT_REVERSED"),("GE","LE_REVERSED"),("EQ","EQ_REVERSED"),("DIRECT","FOLDED"),("DUPLICATES","DUPLICATES_SWAP"),("INCIDENTAL","INCIDENTAL"),("BOOL_AND_SORT","BOOL_AND_SORTED"),("BOOL_OR_SORT","BOOL_OR_SORTED"))

def emit(name,value):
    raw=(json.dumps({"schema_version":1,"starting_head":d.START,**value},indent=2,sort_keys=True)+"\n").encode()
    path=OUT/name; OUT.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_bytes().replace(b"\r\n",b"\n")!=raw:
        if sys.argv[1:]!=["--refresh-development-artifacts"]: raise RuntimeError("saved requirement artifact differs: "+name)
        if subprocess.run(["git","ls-files","--error-unmatch",str(path.relative_to(ROOT))],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:
            raise RuntimeError("cannot refresh a committed checkpoint artifact")
        path.write_bytes(raw)
    if not path.exists():
        with path.open("xb") as handle: handle.write(raw)

def run():
    if sys.argv[1:] not in ([],["--refresh-development-artifacts"]): raise RuntimeError("no population/producer options supported")
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    if head!=d.START: raise RuntimeError("requirement producer starting HEAD changed")
    protected=verify_protected_inputs(); protected["starting_head"]=d.START
    overlap=d.overlap()  # Must pass before any new source compilation.
    from creq904_runtime import mapped,contract,plan
    from self_learning_ai.conf1_v3.boolean_regions import total_boolean_mapping
    ledger=frozen_metadata(); science=[]; plans_checked=[]
    for slot in ledger["slots"]["training_paired_slots"]:
        for condition in ("ISOLATED","COMPOSITION"):
            p=derive_training_slot(slot["slot_id"],condition); science.append(p); plans_checked.append(verify_plan(p))
    evaluation=[evaluation_namespace(s["task_id"]) for s in (ledger["slots"]["primary"][0],next(s for s in ledger["slots"]["primary"] if s["graph"]=="G4"))]
    records=[]
    for left,right in DIRECT_PAIRS:
        m=mapped(left,right); m.validate(); records.append(dict(case_id=left+"_TO_"+right,evidence=m.requirement_evidence))
    for left,right,scope in d.PAIRS:
        m=mapped(left,right,scope); m.validate(); records.append(dict(case_id=left+"_TO_"+right,evidence=m.requirement_evidence))
    checked=[dict(case_id=r["case_id"],evidence_sha256=digest(r["evidence"]),verification=verify_requirement_evidence(r["evidence"])) for r in records]
    negatives=[]; repeated=next(r for r in records if r["case_id"]=="REPEATED_AND_TO_REPEATED_PRODUCT")
    changes=[("DEVELOPMENT_TO_TRAINING",["after","scope"],"SCIENTIFIC_TRAINING","REQUIREMENT_SET_OR_SCOPE_CHANGED"),
        ("DEVELOPMENT_TO_EVALUATION",["after","scope"],"SCIENTIFIC_EVALUATION","REQUIREMENT_SET_OR_SCOPE_CHANGED"),
        ("INVENT_REQUIREMENT",["after","requirements"],repeated["evidence"]["after"]["requirements"]+[repeated["evidence"]["after"]["requirements"][0]],"REQUIREMENT_SET_OR_SCOPE_CHANGED"),
        ("DROP_REQUIREMENT",["after","requirements"],repeated["evidence"]["after"]["requirements"][:1],"REQUIREMENT_SET_OR_SCOPE_CHANGED"),
        ("MERGE_OCCURRENCES",["bindings",1],repeated["evidence"]["bindings"][0],"REQUIREMENT_BINDING_TAMPERED_OR_WRONG"),
        ("VALID_PROOF_WRONG_REQUIREMENT",["bindings",0,"requirement_id"],repeated["evidence"]["bindings"][1]["requirement_id"],"REQUIREMENT_BINDING_TAMPERED_OR_WRONG"),
        ("CHANGE_EXPECTED_KIND",["after","requirements",0,"evidence_kind"],"OUTPUT_ATTRIBUTE","REQUIREMENT_SET_OR_SCOPE_CHANGED"),
        ("INCIDENTAL_RAW_PROMOTION",["raw_classification",0,"classification"],"CANONICAL_REQUIRED_DIRECT","RAW_CLASSIFICATION_TAMPERED"),
        ("UNLISTED_ALGEBRA",["integrated_claims",0,"catalog_rule"],"GENERAL_ALGEBRA","INVOKED_V33_CLAIMS_TAMPERED")]
    for name,path,value,reason in changes:
        attacked=deepcopy(repeated["evidence"]); target=attacked
        for part in path[:-1]: target=target[part]
        target[path[-1]]=value
        try: verify_requirement_evidence(attacked)
        except ClosureError as exc:
            if str(exc)!=reason: raise RuntimeError("wrong mutation rejection: "+name) from exc
        else: raise RuntimeError("mutation accepted: "+name)
        negatives.append(dict(case_id=name,base_case_id=repeated["case_id"],replace_path=path,replace_value=value,expected_reason=reason,actual_reason=reason))
    source_negatives=[]
    for left,right,reason in (("MUL","DIRECT","INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE"),("DIRECT","EXTRA_LIVE","UNMATCHED_LIVE_SOURCE_STRUCTURE"),("ASSOCIATION","REASSOCIATED","INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE")):
        try: mapped(left,right)
        except ClosureError as exc:
            if str(exc)!=reason: raise RuntimeError("wrong source rejection") from exc
        else: raise RuntimeError("bad source accepted")
        source_negatives.append(dict(left=left,right=right,reason=reason))
    ambiguous=total_boolean_mapping(contract("BARE_AND"),d.SOURCES["PRODUCT"],scope="LOCAL_PAIR_JOINT")
    if ambiguous["indicator_evidence_permitted"]: raise RuntimeError("ambiguous scaffold accepted")
    raw=[dict(case_id=r["case_id"],records=r["evidence"]["raw_classification"]) for r in records]
    raw_counts=Counter(x["classification"] for r in raw for x in r["records"])
    baseline_path=ROOT/"research/implementation_notes/coverage_v3_boolean_atomic_transport/development_gate_evidence.json"
    baseline=json.loads(baseline_path.read_bytes()); gates=deepcopy(baseline)
    targets={"INDICATOR_EXTRACTION_COMPLETE","V32_SEMANTIC_MAPPING_COMPLETE","V33_REQUIRED_EQUIVALENCE_COMPLETE"}
    blockers={
        "INDICATOR_EXTRACTION_COMPLETE":["No bound source-backed predicate/type/role/current-iteration indicator evidence has been verified across the global frozen source scope: 120 training and 64 evaluation programs. Metadata derivation and development projections are not global source evidence."],
        "V32_SEMANTIC_MAPPING_COMPLETE":["Scientific requirement foundations are metadata-only, not full CoverageContractV3. Actual scientific source/requirement mapping was not attempted; output-case and complete attribute attachment remain deferred outside this pass.","Unmatched live source-only indicator scaffold ownership remains AUTHORITY_AMBIGUOUS; its development adversary is rejected without blocking unrelated mappings."],
        "V33_REQUIRED_EQUIVALENCE_COMPLETE":["All actually invoked rules in these 18 development mappings are independently verified. No complete scientific slot/source pair has been accepted, so its actually required V3.3 invocation inventory is not evidenced."]}
    expected_scientific_sources={p["program_id"] for p in science}|{s["task_id"] for group in ("primary","primitive_sanity","structural_transfer") for s in ledger["slots"][group]}
    for gate in gates["gates"]:
        if gate["gate"] in targets:
            # Recompute from the evidence for the declared GLOBAL prospective
            # scope, not from development success or historical raw-key flags.
            scientific_source_evidence={r["evidence"]["before"]["program_id"] for r in records
                if r["evidence"]["before"]["scope"] in {"SCIENTIFIC_TRAINING","SCIENTIFIC_EVALUATION"} and verify_requirement_evidence(r["evidence"])["status"]=="VERIFIED"}
            global_complete=scientific_source_evidence==expected_scientific_sources
            gate.update(status="PASS" if global_complete else "UNRESOLVED",evidence_file="independent_requirement_verifier_results.json",detail="Scoped development requirement/mapping verification resolved; global frozen scientific source scope has no bound verification records",remaining_evidence_obligations=blockers[gate["gate"]])
    if any(a!=b for a,b in zip(baseline["gates"],gates["gates"]) if a["gate"] not in targets): raise RuntimeError("out-of-scope gate changed")
    gates.update(starting_head=d.START,artifact_kind="SCOPED_REQUIREMENT_REPAIR_DEVELOPMENT_NOT_SCIENTIFIC_BINDER",baseline_gate_artifact_sha256=hashlib.sha256(baseline_path.read_bytes()).hexdigest(),out_of_scope_gate_authority_path=baseline_path.relative_to(ROOT).as_posix(),
        declared_global_scope="FROZEN_TRAINING_AND_EVALUATION_SOURCE_PROGRAMS",expected_scientific_source_records=len(expected_scientific_sources),verified_scientific_source_records=0,
        status="COVERAGE_V3_CANONICAL_REQUIREMENT_REPAIR_COMPLETE",all_semantic_gates_pass=False,authoritative_population_recount_performed=False,
        population_status="V3_5_POPULATION_UNRESOLVED",historical_8668_authoritative=False)
    files={
        "requirement_scope_provenance_model.json":dict(scopes=["SCIENTIFIC_TRAINING","SCIENTIFIC_EVALUATION","DEVELOPMENT_ONLY"],source_independent_identity=True,all_foundation_artifacts_scientific_index_eligible=False,development_to_scientific_transfer="FORBIDDEN",evaluation_to_training_transfer="FORBIDDEN",training_to_evaluation_transfer="FORBIDDEN",evaluation_namespace_metadata=evaluation,global_gate_source_scope=dict(training=120,evaluation=64,scientific_source_records_verified=0)),
        "frozen_training_slot_requirement_derivation.json":dict(artifact_kind="METADATA_ONLY_REQUIREMENT_FOUNDATIONS_NOT_POPULATION",frozen_paired_slots=60,condition_plans=120,records=science,no_generated_source_or_cases=True,no_v35_expected_index=True),
        "development_only_projection_inventory.json":dict(records=[dict(case_id=r["case_id"],projection=r["evidence"]["before"]) for r in records],scientific_slot_bindings_created=0),
        "raw_key_classification.json":dict(records=raw,classification_counts=dict(raw_counts),scientific_raw_keys_classified_satisfied=0,scientific_raw_classification_status="NOT_ATTEMPTED_NO_SCIENTIFIC_SOURCE_CONSTRUCTED",every_development_raw_key_accounted=True),
        "canonical_requirement_evidence_bindings.json":dict(records=records),
        "v33_integrated_equivalence_claims.json":dict(records=[dict(case_id=r["case_id"],claims=r["evidence"]["integrated_claims"]) for r in records],computed_folding="existing restricted production path retained",reassociation_authorized=False),
        "requirement_preservation_no_cross_scope_invariant.json":dict(scientific_metadata_plans=[dict(program_id=p["program_id"],before_sha256=p["requirements_sha256"],after_sha256=p["requirements_sha256"],mapping_run=False) for p in science],development_mappings=checked,scientific_mapping_invariant="NOT_EXERCISED_NO_SCIENTIFIC_SOURCE_MAPPING",development_invariant="INDEPENDENTLY_VERIFIED",cross_scope_transfers=0),
        "independent_requirement_verifier_results.json":dict(scientific_metadata_verification=plans_checked,development_mapping_verification=checked,serialized_mutations=negatives,source_rejections=source_negatives,ambiguous_scaffold=dict(authority_classification="AUTHORITY_AMBIGUOUS_UNMATCHED_INDICATOR_SCAFFOLD",certificate=ambiguous,accepted=False),constructor_final_pass_flag_trusted=False),
        "development_gate_evidence.json":gates,
        "disposable_overlap.json":overlap,
        "protected_input_integrity.json":protected,
    }
    for name,value in files.items(): emit(name,value)
    print(json.dumps(dict(scientific_metadata_plans=120,development_mappings_verified=len(records),serialized_mutations_rejected=len(negatives),raw_classification_counts=dict(raw_counts),global_gates={g["gate"]:g["status"] for g in gates["gates"]},v35_recount=False),indent=2))
if __name__=="__main__": run()
