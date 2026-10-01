"""One-shot DEVELOPMENT essentiality evidence; no population entry point."""
from pathlib import Path
import argparse,json,sys,subprocess,gzip
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests"),str(ROOT/"scripts")]
from audit_conf1_v3_core_closure import verify_protected_inputs
from check_conf1_v3_generic_binding import junit
from self_learning_ai.conf1_v3.essentiality_verifier import verify_essentiality_evidence
from self_learning_ai.conf1_v3.essentiality_semantics import context,counterfactual
from self_learning_ai.conf1_v3.essentiality_audit import inventories,readiness_model,dependency_notes,edits,kind_attack,ADVERSARY_INTENT
from self_learning_ai.conf1_v3.state_verifier import essentiality_dependencies
from self_learning_ai.conf1_v3.projection_binding_verifier import equal
from self_learning_ai.conf1_v3.requirements import digest
from self_learning_ai.conf1_v3.interfaces import ClosureError,SchemaError
OUT=ROOT/"research/implementation_notes/coverage_v3_essentiality_implementation"


def run():
    parser=argparse.ArgumentParser();parser.add_argument("--focused-junit",required=True);parser.add_argument("--legacy-junit",required=True);parser.add_argument("--regression-junit",required=True);a=parser.parse_args()
    import ess907_inputs as d
    from ess907_runtime import evidence
    from ess907_adversaries import INTENT,mutate
    if OUT.exists():raise RuntimeError("essentiality evidence exists; no refresh")
    if subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()!=d.START:raise RuntimeError("starting HEAD changed")
    integrity=verify_protected_inputs();overlap=d.overlap();focused=junit(a.focused_junit);legacy=junit(a.legacy_junit);regression=junit(a.regression_junit)
    import xml.etree.ElementTree as ET
    pinned=sum(c.attrib["name"].startswith("test_pinned_disposable_essentiality") for c in ET.parse(a.focused_junit).getroot().iter("testcase"))
    if focused["failures"] or focused["errors"] or pinned!=2*len(d.DECLARATIONS) or regression["failures"] or regression["errors"]:raise RuntimeError("test boundary incomplete")
    if legacy["tests"]!=3 or legacy["failures"]!=3:raise RuntimeError("legacy boundary incomplete")
    assert equal(INTENT,ADVERSARY_INTENT)
    records=[];payload=[]
    for name in d.DECLARATIONS:
        for alpha in (False,True):
            e=evidence(name,alpha);v=verify_essentiality_evidence(e)
            r=dict(record_id="ESS907-EVIDENCE-"+str(len(records)),name=name,alpha=alpha,evidence=e,evidence_sha256=digest(e),verification=v);records.append(r)
            # Independently readable deterministic gzip members containing JSONL.
            # No abbreviated traces or lost state relations; avoids huge plain
            # JSON blobs caused by repeated loop-context/dependency identities.
            payload.append(gzip.compress((json.dumps(r,sort_keys=True,separators=(",",":"))+"\n").encode(),mtime=0))
            print("verified "+r["record_id"],flush=True)
    by_id={r["record_id"]:r for r in records};inventory=inventories(records);negative=[]
    for label,reason in INTENT.items():
        name=d.TWO if label in {"WRONG_LOOP","CROSS_PASS"} else d.REPEAT
        base=next(r for r in records if r["name"]==name and not r["alpha"]);forged=mutate(base["evidence"],label)
        try:verify_essentiality_evidence(forged)
        except (ClosureError,SchemaError) as exc:
            if str(exc)!=reason:raise RuntimeError("wrong intended reason: "+label+": "+str(exc))
        else:raise RuntimeError("adversary accepted")
        negative.append(dict(label=label,base_record_id=base["record_id"],changes=edits(base["evidence"],forged),reason=reason))
    for row in inventory["kind_matrix"]:
        base=by_id[row["adversarial_witness"]["base_record_id"]]
        try:verify_essentiality_evidence(kind_attack(base["evidence"],row))
        except ClosureError as exc:
            if str(exc)!=row["adversarial_witness"]["intended_reason"]:raise RuntimeError("kind attack wrong reason")
        else:raise RuntimeError("kind attack accepted")
    diagnostics=[]
    for family in ("numeric_iteration","array_reduction"):
        for reverse in (False,True):
            name=family+"-0-PER_ITEM-"+("REV" if reverse else "FWD");r=next(r for r in records if r["name"]==name and not r["alpha"]);e=r["evidence"]
            p,g,c=context(e["mapping"],e["state"],e["compiler"]);fi=next(i for i,f in enumerate(e["findings"]) if f["bound_requirement"]["capability"]["operation"]=="BOUNDED_LOOP");f=e["findings"][fi]
            for label,value,order,budget in (("FORCE_TRUE_SOLE_EXIT",True,1,4096),("EXECUTION_BUDGET_TIMEOUT",False,0,1)):
                request=dict(occurrences=f["bound_requirement"]["joint_occurrences"],replacement=value,order=order)
                result=counterfactual(p,g,f["bound_requirement"],f["policy"],d.RAW[family][0],request,budget)
                reason="IR_EXECUTION_BUDGET_EXCEEDED" if family=="numeric_iteration" or label=="EXECUTION_BUDGET_TIMEOUT" else "index out of bounds"
                assert result["runtime"] is None and result["reason"]==reason
                diagnostics.append(dict(label=label,base_record_id=r["record_id"],finding_index=fi,case_index=0,budget=budget,result=result,intended_reason=reason))
    deps=essentiality_dependencies(ROOT);model=readiness_model(records,inventory,deps);notes=dependency_notes()
    manifest=[dict(record_id=r["record_id"],name=r["name"],alpha=r["alpha"],evidence_sha256=r["evidence_sha256"],verification=r["verification"]) for r in records]
    files={
        "essentiality_implementation_readiness_model.json":model,
        "frozen_intervention_policy_catalog.json":dict(rows=inventory["policy_catalog"]),
        "normal_counterfactual_evidence_records.json":dict(payload="essentiality_evidence_records.jsonl.gz",encoding="UTF8_JSONL_DETERMINISTIC_GZIP_MEMBERS",records=manifest),
        "joint_occurrence_intervention_records.json":dict(records=inventory["joint_records"]),
        "state_aware_counterfactual_traces.json":dict(records=inventory["state_trace_index"],full_traces="essentiality_evidence_records.jsonl.gz"),
        "essentiality_requirement_kind_coverage.json":dict(rows=inventory["kind_matrix"]),
        "loop_intervention_resolution.json":dict(authority="V3.5 Boolean predicate/operator or branch decision: false then true",resolution="FIRST_AUTHORIZED_FALSE_WITNESS_TERMINATES_WITHOUT_SOURCE_OR_BOUND_EDITS",diagnostics=diagnostics,force_true_terminal_output_fabricated=False),
        "essentiality_adversarial_results.json":dict(records=negative),
        "independent_essentiality_verifier_results.json":dict(records=manifest,constructor_invoked=False,constructor_conclusion_trusted=False),
        "reference_only_dependency_note.json":notes["reference_only"],
        "value_output_dependency_note.json":notes["value_output"],
        "disposable_overlap.json":overlap,
        "protected_integrity.json":{**integrity,"verifier_baseline_head":integrity["starting_head"]},
        "verification_test_results.json":dict(focused=focused,regressions=regression,known_legacy_failures=legacy,pinned_programs=pinned,pinned_runs=sum(len(r["evidence"]["compiler"]["observations"]) for r in records),population_test_deselected=True,
            junit_paths=dict(focused=a.focused_junit,legacy=a.legacy_junit,regressions=a.regression_junit))}
    encoded={name:(json.dumps({**v,"schema_version":1,"artifact_kind":"DEVELOPMENT_ONLY_ESSENTIALITY_IMPLEMENTATION_EVIDENCE","starting_head":d.START},sort_keys=True,separators=(",",":"))+"\n").encode() for name,v in files.items()}
    encoded["essentiality_evidence_records.jsonl.gz"]=b"".join(payload)
    OUT.mkdir(parents=True)
    for name,data in encoded.items():(OUT/name).write_bytes(data)
    print(json.dumps(dict(records=len(records),kinds=len(inventory["kind_matrix"]),adversaries=len(negative),diagnostics=len(diagnostics),case_counts=inventory["case_status_counts"],compressed_bytes=len(encoded["essentiality_evidence_records.jsonl.gz"])),indent=2))


if __name__=="__main__":run()
