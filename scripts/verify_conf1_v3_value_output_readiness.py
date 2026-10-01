"""Read-only saved replay. No producer, constructor, or test imports."""
from pathlib import Path
import gzip,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from audit_conf1_v3_core_closure import verify_protected_inputs
from self_learning_ai.conf1_v3.attribute_verifier import verify_attribute_evidence
from self_learning_ai.conf1_v3.attribute_audit import inventories,models,reference_dependency,kind_attack
from self_learning_ai.conf1_v3.attribute_overlap import compare,permitted_corpus
from self_learning_ai.conf1_v3.attribute_reference import output_plan,digest_text
from self_learning_ai.conf1_v3.projection_grammar import require
from self_learning_ai.conf1_v3.projection_binding_verifier import equal
from self_learning_ai.conf1_v3.essentiality_audit import apply_edits
from self_learning_ai.conf1_v3.coverage import PinnedCompilerOracle
from self_learning_ai.conf1_v3.requirements import digest
START="dfad902a7e1fb595b062723ce8fd6f3380050c59"
OUT=ROOT/"research/implementation_notes/coverage_v3_value_output_implementation"

def read(name):
    v=json.loads((OUT/name).read_bytes())
    require(v["schema_version"]==1 and v["artifact_kind"]=="DEVELOPMENT_ONLY_VALUE_OUTPUT_IMPLEMENTATION_EVIDENCE" and v["starting_head"]==START,"SAVED_ATTRIBUTE_HEADER_MISMATCH")
    return v

def body(v):return {k:x for k,x in v.items() if k not in {"schema_version","artifact_kind","starting_head"}}

def reject(call,reason):
    try:call()
    except ValueError as exc:require(str(exc)==reason,"ATTRIBUTE_NEGATIVE_REASON_CHANGED: "+str(exc))
    else:raise ValueError("ATTRIBUTE_ADVERSARY_ACCEPTED")

def run():
    integrity=verify_protected_inputs();saved=read("protected_integrity.json")
    require(all(equal(integrity[k],saved[k]) for k in ("authorities","normative_regions","preregistration","interface_freeze_sha256_exact_bytes")) and saved["expected_labels_parsed"] is False,"ATTRIBUTE_PROTECTED_INTEGRITY_CHANGED")
    # Both reference expectation derivation and exact exception precede ALL runs.
    overlap=read("disposable_overlap.json");old=permitted_corpus(ROOT)
    checked=compare(overlap["inventory"],overlap["prospective"],old)
    require(all(equal(checked[k],overlap[k]) for k in checked),"SAVED_ATTRIBUTE_OVERLAP_CHANGED")
    require(not checked["prohibited_collisions"] and len(checked["permitted_normative_collisions"])==1,"ATTRIBUTE_ZERO_EXCEPTION_BOUNDARY_CHANGED")
    require(overlap["exception_development_only"] is True and overlap["preflight_failure_reproduced"] is True,"ATTRIBUTE_EXCEPTION_PROMOTION")
    # Causal independence: changing corpus metadata changes collisions, not the
    # deterministic expected-output plans (this check also occurs before runs).
    empty=compare(overlap["inventory"],overlap["prospective"],set())
    require(empty["permitted_normative_collisions"]==[],"ATTRIBUTE_CORPUS_CHOSE_OUTPUT")
    inv=overlap["inventory"];allowed={k:{r["value"] for r in rs} for k,rs in inv.items()}
    for p in overlap["prospective"]:
        plan=p["output_plan"]
        require(p["source"] in allowed["sources"] and p["reference_source"] in allowed["sources"] and plan["program_id"] in allowed["program_ids"] and all(r["case_id"] in allowed["case_ids"] and r["raw_input"] in allowed["raw_inputs"] for r in plan["expected_records"]),"ATTRIBUTE_UNPREFLIGHTED_SOURCE_CASE")
        expr=[m[0] for m in re.finditer(r"(?:IF|LOOP) \([^{}]*?\) \{|(?:attr908|alpha918)[A-Za-z0-9_]*(?:\+=|-=|=)[^{}]*?(?=\.(?![A-Za-z]))",p["source"])]
        require(set(expr)<=allowed["expressions"],"ATTRIBUTE_UNPREFLIGHTED_EXPRESSION")
    manifest=read("independent_value_output_verifier_results.json")
    require(manifest["payload"]=="value_output_evidence_records.jsonl.gz" and manifest["constructor_invoked"] is manifest["constructor_conclusion_trusted"] is False,"ATTRIBUTE_CONSTRUCTOR_TRUST_FORGE")
    with gzip.open(OUT/manifest["payload"],"rt",encoding="utf-8") as stream:records=[json.loads(line) for line in stream]
    require(len(records)==15 and len({r["record_id"] for r in records})==15,"ATTRIBUTE_RECORD_INVENTORY_CHANGED")
    prospective={p["output_plan"]["program_id"]:p for p in overlap["prospective"]}
    literal_saved=read("development_expected_output_records.json")["prospective_literals"]
    require(len(prospective)==len(records),"ATTRIBUTE_PROSPECTIVE_INVENTORY_CHANGED")
    oracle=PinnedCompilerOracle(ROOT/".tools/jdk-25.0.1+8/bin/java.exe",ROOT/".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    results=[]
    for r in records:
        a=r["evidence"];e=a["essentiality"];state=e["state"];p=prospective[state["plan"]["program_id"]]
        require(state["source"]==p["source"] and e["mapping"]["reference_source"]==p["reference_source"] and equal(state["plan"]["declaration"],p["declaration"]) and equal(a["prospective_output"],p["output_plan"]) and
                [x["raw_input"] for x in state["executions"]]==p["raw_inputs"],"ATTRIBUTE_UNPREFLIGHTED_EXECUTION")
        require(equal(a["prospective_literals"],literal_saved[r["name"]]) and all(x["exact_lexeme"] in allowed["prospectively_required_lexemes"] for x in a["prospective_literals"]),"ATTRIBUTE_UNPREFLIGHTED_LITERAL")
        require(digest(a)==r["evidence_sha256"],"ATTRIBUTE_SAVED_PACKET_HASH_CHANGED")
        for observation in e["compiler"]["observations"]:require(oracle.run(state["source"],observation["raw_input"])==observation["output"],"ATTRIBUTE_PINNED_COMPILER_DISAGREEMENT")
        v=verify_attribute_evidence(a);require(equal(v,r["verification"]),"ATTRIBUTE_SAVED_VERIFICATION_CHANGED")
        results.append({k:r[k] for k in ("record_id","name","evidence_sha256","verification")});print("replayed "+r["record_id"],flush=True)
    require(equal(results,manifest["records"]),"ATTRIBUTE_VERIFIER_MANIFEST_CHANGED")
    by_id={r["record_id"]:r for r in records};derived=inventories(records)
    components=[("active_parent_attribute_records.json","active_parent_records"),("initial_state_attribute_records.json","initial_state_records"),
                ("maximal_constant_attachment_records.json","maximal_constant_records"),("development_expected_output_records.json","development_expected_records"),
                ("output_category_evidence.json","output_category_records"),("exact_sentinel_evidence.json","exact_sentinel_records")]
    for filename,key in components:require(equal(derived[key],read(filename)["records"]),"ATTRIBUTE_COMPONENT_INVENTORY_CHANGED")
    matrix=read("requirement_kind_coverage_matrices.json")
    require(equal(derived["value_kind_matrix"],matrix["value"]) and equal(derived["output_kind_matrix"],matrix["output"]),"ATTRIBUTE_KIND_MATRIX_CHANGED")
    for row in matrix["value"]+matrix["output"]:reject(lambda:verify_attribute_evidence(kind_attack(by_id[row["negative_witness"]["record_id"]]["evidence"],row)),row["negative_witness"]["intended_reason"])
    negatives=[]
    for filename in ("value_adversarial_results.json","output_adversarial_results.json","evidence_kind_separation_checks.json"):
        negatives.extend(read(filename)["records"])
    require(len(negatives)==38 and len({r["label"] for r in negatives})==38,"ATTRIBUTE_ADVERSARY_INVENTORY_CHANGED")
    for r in negatives:reject(lambda:verify_attribute_evidence(apply_edits(by_id[r["base_record_id"]]["evidence"],r["changes"])),r["reason"])
    base=dict(inventory=overlap["inventory"],prospective=overlap["prospective"],corpus_extra=[])
    require(len(overlap["exception_adversaries"])==10,"ATTRIBUTE_EXCEPTION_NEGATIVES_INCOMPLETE")
    for r in overlap["exception_adversaries"]:
        a=apply_edits(base,r["changes"]);reject(lambda:compare(a["inventory"],a["prospective"],old|set(a["corpus_extra"])),r["reason"])
    gates=json.loads((ROOT/"research/implementation_notes/coverage_v3_semantic_core/semantic_gate_evidence.json").read_bytes())
    value,output=models(records,derived,{r["gate"]:r for r in gates["gates"]})
    require(equal(value,body(read("value_literal_implementation_readiness_model.json"))) and equal(output,body(read("output_attribute_implementation_readiness_model.json"))),"ATTRIBUTE_READINESS_OR_OLD_GATE_CHANGED")
    require(equal(reference_dependency(),body(read("reference_only_dependency_summary.json"))),"ATTRIBUTE_REFERENCE_ONLY_BOUNDARY_CHANGED")
    tests=read("verification_test_results.json")
    require(tests["focused"]["failures"]==tests["focused"]["errors"]==tests["regressions"]["failures"]==tests["regressions"]["errors"]==0 and tests["known_legacy_failures"]["failures"]==3 and tests["population_test_deselected"] is True,"ATTRIBUTE_TEST_BOUNDARY_CHANGED")
    require(tests["pinned_runs"]==sum(len(r["evidence"]["essentiality"]["compiler"]["observations"]) for r in records),"ATTRIBUTE_PINNED_RUN_COUNT_CHANGED")
    print(json.dumps(dict(records=len(records),value_kinds=len(matrix["value"]),output_kinds=len(matrix["output"]),adversaries_rejected=len(negatives),kind_adversaries=len(matrix["value"])+len(matrix["output"]),
          exception_adversaries=10,permitted_zero_collisions=1,prohibited_collisions=0,value="VALUE_LITERAL_IMPLEMENTATION_READY",output="OUTPUT_ATTRIBUTE_IMPLEMENTATION_READY",
          scientific=value["scientific_instance_closure"],old_global_value_gate=value["old_global_gate"]["status"],old_global_output_gate=output["old_global_gate"]["status"],writes=0,constructor_invoked=False,population_producer_invoked=False),indent=2))

if __name__=="__main__":run()
