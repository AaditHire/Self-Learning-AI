"""Read-only saved essentiality replay; NO producer/constructor/test imports."""
from pathlib import Path
import gzip,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from audit_conf1_v3_core_closure import verify_protected_inputs
from self_learning_ai.conf1_v3.essentiality_verifier import verify_essentiality_evidence
from self_learning_ai.conf1_v3.essentiality_semantics import context,counterfactual
from self_learning_ai.conf1_v3.essentiality_audit import inventories,readiness_model,dependency_notes,apply_edits,kind_attack,ADVERSARY_INTENT
from self_learning_ai.conf1_v3.state_verifier import essentiality_dependencies
from self_learning_ai.conf1_v3.projection_grammar import require
from self_learning_ai.conf1_v3.projection_binding_verifier import equal
from self_learning_ai.conf1_v3.requirements import digest
from self_learning_ai.conf1_v3.interfaces import ClosureError,SchemaError
from self_learning_ai.conf1_v3.coverage import PinnedCompilerOracle
START="91f8099da40b70c1453e6e2c7b315ec006fcf853"
OUT=ROOT/"research/implementation_notes/coverage_v3_essentiality_implementation"


def read(name):
    v=json.loads((OUT/name).read_bytes())
    require(v.get("schema_version")==1 and v.get("artifact_kind")=="DEVELOPMENT_ONLY_ESSENTIALITY_IMPLEMENTATION_EVIDENCE" and v.get("starting_head")==START,"SAVED_ESSENTIALITY_HEADER_MISMATCH")
    return v


def content(v):
    return {k:x for k,x in v.items() if k not in {"schema_version","artifact_kind","starting_head"}}


def strings(v):
    if isinstance(v,str):yield v
    elif isinstance(v,list):
        for x in v:yield from strings(x)
    elif isinstance(v,dict):
        for k,x in v.items():yield k;yield from strings(x)


def run():
    integrity=verify_protected_inputs();saved=read("protected_integrity.json")
    require(all(equal(integrity[k],saved[k]) for k in ("authorities","normative_regions","preregistration","interface_freeze_sha256_exact_bytes")) and saved["expected_labels_parsed"] is False,"ESSENTIALITY_PROTECTED_INTEGRITY_CHANGED")
    # Permitted string/hash overlap only; this completes BEFORE all executions.
    overlap=read("disposable_overlap.json");old=set();paths=list((ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixtures").glob("*.json"))
    require(len(paths)==13 and overlap["expected_labels_parsed"] is False,"ESSENTIALITY_OVERLAP_BOUNDARY_CHANGED")
    for path in (*paths,ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"):old.update(strings(json.loads(path.read_bytes())))
    inventory=overlap["inventory"];fresh={r["value"] for rows in inventory.values() for r in rows};hashes={hashlib.sha256(x.encode()).hexdigest() for x in fresh}
    require(not fresh&old and not hashes&old and not hashes&{hashlib.sha256(x.encode()).hexdigest() for x in old},"ESSENTIALITY_DISPOSABLE_OVERLAP")
    require(all(hashlib.sha256(r["value"].encode()).hexdigest()==r["sha256_utf8"] for rows in inventory.values() for r in rows) and
        all(overlap[k]==0 for k in ("exact_string_overlap","recorded_hash_overlap","recomputed_string_hash_overlap")),"ESSENTIALITY_OVERLAP_HASH_MISMATCH")
    manifest=read("normal_counterfactual_evidence_records.json")
    require(manifest["payload"]=="essentiality_evidence_records.jsonl.gz" and manifest["encoding"]=="UTF8_JSONL_DETERMINISTIC_GZIP_MEMBERS","ESSENTIALITY_PAYLOAD_FORMAT_CHANGED")
    with gzip.open(OUT/manifest["payload"],"rt",encoding="utf-8") as stream:records=[json.loads(line) for line in stream]
    by_id={r["record_id"]:r for r in records};allowed={k:{r["value"] for r in rows} for k,rows in inventory.items()}
    require(len(records)==74 and len(by_id)==74,"ESSENTIALITY_SOURCE_REALIZATION_INVENTORY_INCOMPLETE")
    for r in records:
        e=r["evidence"];state=e["state"]
        require(state["plan"]["program_id"] in allowed["ids"] and state["source"] in allowed["sources"] and e["mapping"]["reference_source"] in allowed["sources"] and
            all(x["raw_input"] in allowed["raw_inputs"] for x in state["executions"]),"ESSENTIALITY_UNPREFLIGHTED_EXECUTION")
        s=state["source"];expressions=[m[0] for m in re.finditer(r"(?:IF|LOOP) \([^{}]*?\) \{",s)]
        expressions += [m[0] for m in re.finditer(r"(?:ess907|alpha917)[A-Za-z0-9_]*(?:\+=|-=|=)[^{}]*?(?=\.(?![A-Za-z]))",s)]
        require(set(expressions)<=allowed["expressions"],"ESSENTIALITY_UNPREFLIGHTED_SEMANTIC_EXPRESSION")
    oracle=PinnedCompilerOracle(ROOT/".tools/jdk-25.0.1+8/bin/java.exe",ROOT/".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    results=[]
    for r in records:
        e=r["evidence"];require(digest(e)==r["evidence_sha256"],"ESSENTIALITY_SAVED_PACKET_HASH_CHANGED")
        for observation in e["compiler"]["observations"]:
            require(oracle.run(e["state"]["source"],observation["raw_input"])==observation["output"],"NORMAL_COMPILER_REFERENCE_DISAGREEMENT")
        verification=verify_essentiality_evidence(e);require(equal(verification,r["verification"]),"ESSENTIALITY_SAVED_VERIFICATION_CHANGED")
        results.append(dict(record_id=r["record_id"],name=r["name"],alpha=r["alpha"],evidence_sha256=r["evidence_sha256"],verification=verification))
        print("replayed "+r["record_id"],flush=True)
    require(equal(results,manifest["records"]) and equal(results,read("independent_essentiality_verifier_results.json")["records"]),"ESSENTIALITY_MANIFEST_RESULT_INVENTORY_CHANGED")
    inv=inventories(records);deps=essentiality_dependencies(ROOT)
    require(equal(readiness_model(records,inv,deps),content(read("essentiality_implementation_readiness_model.json"))),"ESSENTIALITY_READINESS_LAYER_CHANGED")
    require(len({r["evidence"]["state"]["plan"]["program_id"] for r in records})==37 and
        all({r["alpha"] for r in records if r["evidence"]["state"]["plan"]["program_id"]==pid}=={False,True} for pid in allowed["ids"]),"ESSENTIALITY_ALPHA_INVENTORY_INCOMPLETE")
    require(len(inv["predicates"])==8 and set(inv["classes"])=={"API_DECODER","SEMANTIC_PRIMITIVE","GENERIC_CONSTRUCT","ATOMIC_OPERATOR","ATOMIC_CONTROL_DATAFLOW"} and
        set(inv["case_status_counts"])=={"ACTIVE","INACTIVE","UNRESOLVED"},"ESSENTIALITY_CLASS_OR_STATUS_COVERAGE_INCOMPLETE")
    require({tuple(x) for x in inv["grammar_forms"]}=={(f,c,b) for f in ("numeric_iteration","array_reduction") for c in ("PER_ITEM","PREFIX","TWO_PASS") for b in (False,True)},"ESSENTIALITY_GRAMMAR_COVERAGE_INCOMPLETE")
    for name,key,target in (("frozen_intervention_policy_catalog.json","policy_catalog","rows"),("joint_occurrence_intervention_records.json","joint_records","records"),("state_aware_counterfactual_traces.json","state_trace_index","records"),("essentiality_requirement_kind_coverage.json","kind_matrix","rows")):
        actual=inv[key];stored=read(name)[target]
        if key=="state_trace_index":
            # Runtime references index a content-addressed dictionary. JSON
            # sort_keys changes dictionary iteration order, not its contents.
            # Canonicalize BOTH indexes; retain counts/duplicates and every
            # associated state hash, intervention and output ancestry field.
            actual=[{**r,"runtimes":sorted(r["runtimes"],key=lambda x:x["runtime_ref"])} for r in actual]
            stored=[{**r,"runtimes":sorted(r["runtimes"],key=lambda x:x["runtime_ref"])} for r in stored]
        require(equal(actual,stored),"ESSENTIALITY_COMPONENT_INVENTORY_CHANGED")
    for row in inv["kind_matrix"]:
        try:verify_essentiality_evidence(kind_attack(by_id[row["adversarial_witness"]["base_record_id"]]["evidence"],row))
        except ClosureError as exc:require(str(exc)==row["adversarial_witness"]["intended_reason"],"ESSENTIALITY_KIND_NEGATIVE_REASON_CHANGED")
        else:raise ClosureError("ESSENTIALITY_KIND_ADVERSARY_ACCEPTED")
    negative=read("essentiality_adversarial_results.json")["records"]
    require(len(negative)==len(ADVERSARY_INTENT) and {r["label"] for r in negative}==set(ADVERSARY_INTENT),"ESSENTIALITY_ADVERSARY_INVENTORY_INCOMPLETE")
    for a in negative:
        require(a["reason"]==ADVERSARY_INTENT[a["label"]] and a["changes"],"ESSENTIALITY_ADVERSARY_INTENT_CHANGED")
        try:verify_essentiality_evidence(apply_edits(by_id[a["base_record_id"]]["evidence"],a["changes"]))
        except (ClosureError,SchemaError) as exc:require(str(exc)==a["reason"],"ESSENTIALITY_ADVERSARY_REJECTION_REASON_CHANGED")
        else:raise ClosureError("ESSENTIALITY_ADVERSARY_ACCEPTED")
    loop=read("loop_intervention_resolution.json");diagnostics=loop["diagnostics"]
    require(len(diagnostics)==8 and loop["force_true_terminal_output_fabricated"] is False,"ESSENTIALITY_LOOP_DIAGNOSTICS_INCOMPLETE")
    contexts=set()
    for a in diagnostics:
        e=by_id[a["base_record_id"]]["evidence"];p,g,c=context(e["mapping"],e["state"],e["compiler"]);f=e["findings"][a["finding_index"]];case=f["cases"][a["case_index"]]
        require(case["status"]=="ACTIVE" and case["attempts"][0]["intervention"]["replacement"] is False,"ESSENTIALITY_LOOP_FALSE_WITNESS_MISSING")
        d=e["state"]["plan"]["declaration"];contexts.add((d["family"],d["reverse"],a["label"]))
        require(a["label"] in {"FORCE_TRUE_SOLE_EXIT","EXECUTION_BUDGET_TIMEOUT"},"ESSENTIALITY_LOOP_DIAGNOSTIC_IDENTITY_CHANGED")
        expected_reason="index out of bounds" if d["family"]=="array_reduction" and a["label"]=="FORCE_TRUE_SOLE_EXIT" else "IR_EXECUTION_BUDGET_EXCEEDED"
        request=dict(occurrences=f["bound_requirement"]["joint_occurrences"],replacement=a["label"]=="FORCE_TRUE_SOLE_EXIT",order=1 if a["label"]=="FORCE_TRUE_SOLE_EXIT" else 0)
        budget=4096 if a["label"]=="FORCE_TRUE_SOLE_EXIT" else 1
        require(a["budget"]==budget and equal(a["result"]["intervention"],request),"ESSENTIALITY_LOOP_DIAGNOSTIC_POLICY_CHANGED")
        result=counterfactual(p,g,f["bound_requirement"],f["policy"],case["raw_input"],request,budget)
        require(result["runtime"] is None and result["reason"]==a["intended_reason"]==expected_reason and equal(result,a["result"]),"ESSENTIALITY_LOOP_DIAGNOSTIC_CHANGED")
    require(len(contexts)==8,"ESSENTIALITY_LOOP_ORIENTATION_COVERAGE_INCOMPLETE")
    notes=dependency_notes()
    require(equal(notes["reference_only"],content(read("reference_only_dependency_note.json"))) and equal(notes["value_output"],content(read("value_output_dependency_note.json"))),"ESSENTIALITY_DEPENDENCY_BOUNDARY_CHANGED")
    independent=read("independent_essentiality_verifier_results.json")
    require(independent["constructor_invoked"] is independent["constructor_conclusion_trusted"] is False,"ESSENTIALITY_CONSTRUCTOR_TRUST_FORGE")
    tests=read("verification_test_results.json")
    require(tests["focused"]["failures"]==tests["focused"]["errors"]==tests["regressions"]["failures"]==tests["regressions"]["errors"]==0 and
        tests["pinned_programs"]==74 and tests["pinned_runs"]==sum(len(r["evidence"]["compiler"]["observations"]) for r in records) and
        tests["known_legacy_failures"]["tests"]==tests["known_legacy_failures"]["failures"]==3 and tests["population_test_deselected"] is True,"ESSENTIALITY_TEST_BOUNDARY_CHANGED")
    print(json.dumps(dict(development_records=len(records),requirement_kinds=len(inv["kind_matrix"]),adversaries_rejected=len(negative),kind_adversaries_rejected=len(inv["kind_matrix"]),loop_diagnostics=len(diagnostics),
        implementation="ESSENTIALITY_ENGINE_IMPLEMENTATION_READY",scientific="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION_AND_VALIDATION",old_global_gate=deps["old_essentiality_gate"]["status"],
        case_counts=inv["case_status_counts"],writes=0,constructor_invoked=False,population_producer_invoked=False),indent=2))


if __name__=="__main__":run()
