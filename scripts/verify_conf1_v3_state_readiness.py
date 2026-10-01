"""Read-only SAVED state replay. No constructor/producer/input-generator import."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from audit_conf1_v3_core_closure import verify_protected_inputs
from self_learning_ai.conf1_v3.state_verifier import verify_state_evidence,state_kind_inventory,delete_proof,essentiality_dependencies
from self_learning_ai.conf1_v3.state_semantics import static_evidence
from self_learning_ai.conf1_v3.projection_grammar import require
from self_learning_ai.conf1_v3.projection_binding_verifier import equal
from self_learning_ai.conf1_v3.requirements import digest
from self_learning_ai.conf1_v3.interfaces import ClosureError,SchemaError
START="5e6126f8d050ea9425b742fbcfcefe1c3d2bdf5d"
OUT=ROOT/"research/implementation_notes/coverage_v3_state_implementation"
REQUIRED_SOURCE={"MISSING_INITIALIZATION","WRONG_INITIAL_VALUE","WRONG_UPDATE_TARGET","RESET_INSIDE_LOOP","AMBIGUOUS_REACHING_DEFINITIONS",
    "CONDITIONAL_WRITER_AMBIGUITY","STALE_WRITER","UNRELATED_MUTATION","SAME_OUTPUT_INVALID_RECURRENCE","CONTRIBUTION_BYPASSES_PREDICATE",
    "WRITE_AFTER_FINAL_READ","DROPPED_REQUIRED_UPDATE","PREFIX_PRE_POST_SWAP","LATER_WRITE_CONTAMINATION","WRONG_LOOP_READ","PREFIX_WRONG_RESET_SCOPE",
    "PREFIX_WRONG_INITIALIZATION","WRONG_PASS_ORDER","OVERWRITTEN_FIRST_PASS","RECOMPUTED_FIRST_PASS","WRONG_FINAL_COMBINATION","CROSS_LOOP_STATE",
    "UNRELATED_FINAL_STATE","INCORRECT_REVERSE_DECREMENT","INCORRECT_REVERSE_BOUND","MISSING_REVERSE_STEP","MUTATED_SOURCE_BOUND"}
REQUIRED_MUTATIONS={"MISSING_STATE_EDGE","DUPLICATE_STATE_EDGE","FABRICATED_RECURRENCE_LABEL","STALE_RUNTIME_WRITER","WRONG_SOURCE_RUNTIME_MAP",
    "CONSTRUCTOR_READINESS_FORGE","SCIENTIFIC_TRAINING_PROMOTION","SCIENTIFIC_EVALUATION_PROMOTION","SCIENTIFIC_SLOT_INJECTION","SCIENTIFIC_CLOSURE_FORGE"}
SOURCE_INTENT={}
for reason,labels in {
    "STATE_REQUIRED_INITIALIZATION_MISSING":["MISSING_INITIALIZATION"],
    "STATE_REQUIRED_INITIAL_VALUE_MISMATCH":["WRONG_INITIAL_VALUE","PREFIX_WRONG_INITIALIZATION"],
    "STATE_WRONG_UPDATE_TARGET":["WRONG_UPDATE_TARGET"],"STATE_UNAUTHORIZED_RESET":["RESET_INSIDE_LOOP","PREFIX_WRONG_RESET_SCOPE"],
    "STATE_CONDITIONAL_WRITER_AMBIGUITY":["AMBIGUOUS_REACHING_DEFINITIONS","CONDITIONAL_WRITER_AMBIGUITY"],
    "STATE_STALE_INDICATOR_OR_WRONG_LOOP":["STALE_WRITER","UNRELATED_FINAL_STATE"],"STATE_EXTRA_LIVE_MUTATION":["UNRELATED_MUTATION"],
    "STATE_REQUIRED_CONTRIBUTION_MISMATCH":["SAME_OUTPUT_INVALID_RECURRENCE","CONTRIBUTION_BYPASSES_PREDICATE"],
    "STATE_OUTPUT_NOT_FINAL":["WRITE_AFTER_FINAL_READ"],"STATE_REQUIRED_WRITE_ORDER_MISMATCH":["DROPPED_REQUIRED_UPDATE"],
    "STATE_PREFIX_REQUIRES_PRIOR_STATE":["PREFIX_PRE_POST_SWAP","LATER_WRITE_CONTAMINATION"],"STATE_PREFIX_REQUIRED_READ_MISSING":["WRONG_LOOP_READ"],
    "STATE_PASS_ORDER_OR_TARGET_MISMATCH":["WRONG_PASS_ORDER"],"STATE_PRESERVED_PASS_STATE_OVERWRITTEN":["OVERWRITTEN_FIRST_PASS"],
    "STATE_PRESERVED_PASS_STATE_RECOMPUTED":["RECOMPUTED_FIRST_PASS"],"STATE_FINAL_COMBINATION_MISMATCH":["WRONG_FINAL_COMBINATION"],
    "STATE_CROSS_LOOP_CONTRIBUTION":["CROSS_LOOP_STATE"],"STATE_REVERSE_TRAVERSAL_UNPROVED":["INCORRECT_REVERSE_DECREMENT","INCORRECT_REVERSE_BOUND","MISSING_REVERSE_STEP"],
    "STATE_IMMUTABLE_BOUND_MUTATED":["MUTATED_SOURCE_BOUND"]}.items():
    SOURCE_INTENT.update({label:reason for label in labels})


def read(name):
    v=json.loads((OUT/name).read_bytes())
    require(v.get("schema_version")==1 and v.get("artifact_kind")=="DEVELOPMENT_ONLY_STATE_IMPLEMENTATION_EVIDENCE" and v.get("starting_head")==START,"SAVED_STATE_ARTIFACT_HEADER_CHANGED")
    return v


def mutation(e,a):
    r=deepcopy(e);target=r
    for x in a["path"][:-1]:target=target[x]
    target[a["path"][-1]]=deepcopy(a["value"]);return r


def strings(v):
    if isinstance(v,str):yield v
    elif isinstance(v,list):
        for x in v:yield from strings(x)
    elif isinstance(v,dict):
        for k,x in v.items():yield k;yield from strings(x)


def run():
    integrity=verify_protected_inputs();saved=read("protected_integrity.json")
    require(all(equal(integrity[k],saved[k]) for k in ("authorities","normative_regions","preregistration","interface_freeze_sha256_exact_bytes")) and saved["expected_labels_parsed"] is False,"STATE_PROTECTED_INTEGRITY_CHANGED")
    # This overlap MUST precede execution by the independent packet verifier.
    overlap=read("disposable_overlap.json");old=set();paths=sorted((ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixtures").glob("*.json"))
    require(len(paths)==13 and overlap["expected_labels_parsed"] is False,"STATE_OVERLAP_BOUNDARY_CHANGED")
    for path in (*paths,ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"):old.update(strings(json.loads(path.read_bytes())))
    values={r["value"] for rows in overlap["inventory"].values() for r in rows};hashes={hashlib.sha256(x.encode()).hexdigest() for x in values}
    require(not values&old and not hashes&old and not hashes&{hashlib.sha256(x.encode()).hexdigest() for x in old},"STATE_DISPOSABLE_OVERLAP_CHANGED")
    require(all(hashlib.sha256(r["value"].encode()).hexdigest()==r["sha256_utf8"] for rows in overlap["inventory"].values() for r in rows) and
            all(overlap[k]==0 for k in ("exact_string_overlap","recorded_hash_overlap","recomputed_string_hash_overlap")),"STATE_OVERLAP_HASH_OR_STATUS_CHANGED")
    records=read("state_source_evidence.json")["records"];by_id={r["record_id"]:r for r in records}
    require(records and len(by_id)==len(records),"STATE_RECORDS_MISSING_OR_DUPLICATED")
    allowed_sources={r["value"] for r in overlap["inventory"]["sources"]};allowed_inputs={r["value"] for r in overlap["inventory"]["raw_inputs"]}
    require(all(r["evidence"]["source"] in allowed_sources and all(x["raw_input"] in allowed_inputs for x in r["evidence"]["executions"]) for r in records),"STATE_UNPREFLIGHTED_EXECUTION")
    results=[];kinds={}
    for r in records:
        require(digest(r["evidence"])==r["evidence_sha256"],"SAVED_STATE_EVIDENCE_HASH_CHANGED")
        v=verify_state_evidence(r["evidence"]);require(equal(v,r["verification"]),"SAVED_STATE_VERIFICATION_CHANGED")
        results.append(dict(record_id=r["record_id"],evidence_sha256=r["evidence_sha256"],verification=v))
        for k in state_kind_inventory(r["evidence"]):kinds[k["kind_id"]]=k["kind"]
    require(equal(results,read("independent_state_verifier_results.json")["records"]),"STATE_VERIFICATION_INVENTORY_CHANGED")
    require(read("independent_state_verifier_results.json")["constructor_conclusion_trusted"] is False,"STATE_CONSTRUCTOR_TRUST_FORGE")
    for name,key,sub in (("required_computation_certificates.json","required_computation","certificate"),("static_reaching_definition_graphs.json","state_graph","graph"),("runtime_static_trace_agreement.json","executions","executions")):
        require(equal([dict(record_id=r["record_id"],**{sub:r["evidence"][key]}) for r in records],read(name)["records"]),"STATE_COMPONENT_INVENTORY_CHANGED")
    for cls,name in (("PER_ITEM","per_item_recurrence_evidence.json"),("PREFIX","prefix_recurrence_evidence.json"),("TWO_PASS","two_pass_recurrence_evidence.json")):
        require(equal([v for v,r in zip(results,records) if r["evidence"]["required_computation"]["recurrence_class"]==cls],read(name)["records"]),"STATE_RECURRENCE_INVENTORY_CHANGED")
    negatives=read("state_adversarial_results.json")["records"]
    require(all(a["kind"] in {"SOURCE_REJECTION","SERIALIZED_MUTATION"} for a in negatives) and len(negatives)==len(REQUIRED_SOURCE)+len(REQUIRED_MUTATIONS) and
            {a["label"] for a in negatives if a["kind"]=="SOURCE_REJECTION"}==REQUIRED_SOURCE and
            {a["label"] for a in negatives if a["kind"]=="SERIALIZED_MUTATION"}==REQUIRED_MUTATIONS,"STATE_ADVERSARIAL_INVENTORY_INCOMPLETE")
    for a in negatives:
        require(a["source"] in allowed_sources and a["reason"]==SOURCE_INTENT[a["label"]] if a["kind"]=="SOURCE_REJECTION" else a["label"]==a["attack"]["name"],"STATE_ADVERSARY_NOT_BOUND_TO_INTENDED_OBLIGATION")
        try:
            if a["kind"]=="SOURCE_REJECTION":static_evidence(a["plan"],a["source"])
            else:verify_state_evidence(mutation(by_id[a["base_record_id"]]["evidence"],a["attack"]))
        except (ClosureError,SchemaError) as exc:require(str(exc)==a["reason"],"STATE_ADVERSARY_REASON_CHANGED")
        else:raise ClosureError("STATE_ADVERSARY_ACCEPTED")
    matrix=read("state_requirement_kind_coverage.json")["rows"]
    require(len(matrix)==len(kinds) and {r["kind_id"] for r in matrix}==set(kinds),"STATE_KIND_COVERAGE_INCOMPLETE")
    for row in matrix:
        base=by_id[row["positive_record_id"]];e=base["evidence"]
        require(equal(row["kind"],kinds[row["kind_id"]]) and any(equal(dict(kind_id=row["kind_id"],kind=row["kind"],proof_locator=row["proof_locator"]),k) for k in state_kind_inventory(e)) and
                equal(row["source_grammatical_form"],e["plan"]["declaration"]) and row["static_proof_sha256"]==digest(e["state_graph"]) and equal(row["independent_verifier_result"],base["verification"]),"STATE_KIND_NOT_BOUND_TO_PROOF")
        try:verify_state_evidence(delete_proof(e,row["proof_locator"]))
        except ClosureError as exc:require(str(exc)==row["negative_reason"],"STATE_KIND_NEGATIVE_REASON_CHANGED")
        else:raise ClosureError("STATE_KIND_DELETION_ACCEPTED")
    deps=essentiality_dependencies(ROOT);require(equal(deps,{k:v for k,v in read("essentiality_dependency_summary.json").items() if k not in {"schema_version","artifact_kind","starting_head"}}),"STATE_ESSENTIALITY_DEPENDENCY_SUMMARY_CHANGED")
    model=read("state_implementation_readiness_model.json")
    forms=sorted({(r["evidence"]["plan"]["declaration"]["family"],r["evidence"]["required_computation"]["recurrence_class"],r["evidence"]["plan"]["declaration"]["reverse"]) for r in records})
    require(set(forms)=={(f,c,b) for f in ("numeric_iteration","array_reduction") for c in ("PER_ITEM","PREFIX","TWO_PASS") for b in (False,True)} and equal(model["grammar_forms"],[list(x) for x in forms]),"STATE_GRAMMAR_COVERAGE_INCOMPLETE")
    require(model["scope"]=="DEVELOPMENT_ONLY" and model["STATE_IMPLEMENTATION_READINESS"]=="STATE_GRAPH_IMPLEMENTATION_READY" and model["STATE_SCIENTIFIC_INSTANCE_CLOSURE"]=="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION" and
            model["scientific_sources_constructed"]==model["scientific_satisfaction_claims"]==0 and
            not any(model[k] for k in ("population_producer_invoked","historical_8668_authoritative","scientific_fixture_execution","model_execution","essentiality_repair","old_global_gate_changed")) and
            equal(model["old_global_gate"],deps["old_state_gate"]) and model["old_global_gate"]["status"]=="UNRESOLVED","STATE_READINESS_OR_SCIENTIFIC_LAYER_CHANGED")
    require(equal(model["preserved_binding_readiness"],dict(INDICATOR="IMPLEMENTATION_READY",V32="IMPLEMENTATION_READY",V33="IMPLEMENTATION_READY")),"STATE_INHERITED_READINESS_CHANGED")
    tests=read("verification_test_results.json")
    require(tests["focused"]["failures"]==tests["focused"]["errors"]==0 and tests["state_pinned_programs"]==len({r["name"] for r in records}) and tests["state_pinned_runs"]==2*tests["state_pinned_programs"] and
            tests["known_legacy_failures"]["tests"]==tests["known_legacy_failures"]["failures"]==3 and tests["population_test_deselected"] is True,"STATE_TEST_BOUNDARY_CHANGED")
    print(json.dumps(dict(development_state_records=len(records),state_requirement_kinds=len(matrix),adversaries_rejected=len(negatives),
        implementation=model["STATE_IMPLEMENTATION_READINESS"],scientific=model["STATE_SCIENTIFIC_INSTANCE_CLOSURE"],old_global_state_gate=model["old_global_gate"]["status"],
        writes=0,constructor_invoked=False,population_producer_invoked=False),indent=2))


if __name__=="__main__":run()
