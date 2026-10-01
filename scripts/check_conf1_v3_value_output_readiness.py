"""One-shot DEVELOPMENT producer. Refuses overwrite; no population entry point."""
from pathlib import Path
import argparse,gzip,json,subprocess,sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests"),str(ROOT/"scripts")]
from audit_conf1_v3_core_closure import verify_protected_inputs
from self_learning_ai.conf1_v3.attribute_verifier import verify_attribute_evidence
from self_learning_ai.conf1_v3.attribute_audit import inventories,models,reference_dependency,kind_attack
from self_learning_ai.conf1_v3.essentiality_audit import edits
from self_learning_ai.conf1_v3.requirements import digest
from self_learning_ai.conf1_v3.attribute_overlap import compare,permitted_corpus
OUT=ROOT/"research/implementation_notes/coverage_v3_value_output_implementation"

def junit(path):
    root=ET.parse(path).getroot();cs=list(root.iter("testcase"));ss=list(root.iter("testsuite"))
    return dict(tests=len(cs),failures=sum(int(s.attrib.get("failures",0)) for s in ss),errors=sum(int(s.attrib.get("errors",0)) for s in ss),
                skipped=sum(int(s.attrib.get("skipped",0)) for s in ss),
                failed_cases=[dict(name=c.attrib["classname"]+"::"+c.attrib["name"],message=c.find("failure").attrib.get("message","")) for c in cs if c.find("failure") is not None])

def rejected(call,reason):
    try:call()
    except ValueError as exc:
        if str(exc)!=reason:raise RuntimeError("wrong rejection reason: "+str(exc)+" != "+reason)
    else:raise RuntimeError("adversary accepted")

def run():
    parser=argparse.ArgumentParser()
    for arg in ("focused-junit","legacy-junit","regression-junit"):parser.add_argument("--"+arg,required=True)
    args=parser.parse_args()
    import attr908_inputs as d
    from attr908_runtime import evidence
    from attr908_adversaries import INTENT,VALUE,OUTPUT,CROSS,mutate,OVERLAP_INTENT,overlap_mutation
    if OUT.exists():raise RuntimeError("value/output evidence exists; no refresh")
    if subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()!=d.START:raise RuntimeError("starting HEAD changed")
    integrity=verify_protected_inputs();focused=junit(args.focused_junit);legacy=junit(args.legacy_junit);reg=junit(args.regression_junit)
    if focused["failures"] or focused["errors"] or reg["failures"] or reg["errors"] or legacy["tests"]!=3 or legacy["failures"]!=3:raise RuntimeError("test boundary incomplete")
    old=permitted_corpus(ROOT);overlap=compare(d.inventory(),d.PROSPECTIVE,old)
    records=[];payload=[]
    for name in d.DECLARATIONS:
        e=evidence(name);v=verify_attribute_evidence(e)
        r=dict(record_id="ATTR908-EVIDENCE-"+name,name=name,evidence=e,evidence_sha256=digest(e),verification=v)
        records.append(r);payload.append(gzip.compress((json.dumps(r,sort_keys=True,separators=(",",":"))+"\n").encode(),mtime=0))
        print("verified "+r["record_id"],flush=True)
    by_name={r["name"]:r for r in records};by_id={r["record_id"]:r for r in records};inv=inventories(records);negative=[]
    for label,(name,reason) in INTENT.items():
        base=by_name[name];attack=mutate(base["evidence"],label);rejected(lambda:verify_attribute_evidence(attack),reason)
        negative.append(dict(label=label,base_record_id=base["record_id"],changes=edits(base["evidence"],attack),reason=reason,
                             kind="VALUE_OR_LITERAL" if label in VALUE else "OUTPUT_ATTRIBUTE" if label in OUTPUT else "EVIDENCE_KIND_SEPARATION"))
    for row in inv["value_kind_matrix"]+inv["output_kind_matrix"]:
        base=by_id[row["negative_witness"]["record_id"]]
        rejected(lambda:verify_attribute_evidence(kind_attack(base["evidence"],row)),row["negative_witness"]["intended_reason"])
    on=[];base=dict(inventory=d.inventory(),prospective=d.PROSPECTIVE,corpus_extra=[])
    for label,reason in OVERLAP_INTENT.items():
        inventory,prospective,corpus=overlap_mutation(d.inventory(),d.PROSPECTIVE,old,label)
        rejected(lambda:compare(inventory,prospective,corpus),reason)
        forged=dict(inventory=inventory,prospective=prospective,corpus_extra=sorted(corpus-old))
        on.append(dict(label=label,changes=edits(base,forged),reason=reason))
    gates=json.loads((ROOT/"research/implementation_notes/coverage_v3_semantic_core/semantic_gate_evidence.json").read_bytes())
    old_gates={r["gate"]:r for r in gates["gates"]};value,output=models(records,inv,old_gates)
    manifest=[{k:r[k] for k in ("record_id","name","evidence_sha256","verification")} for r in records]
    files={
      "value_literal_implementation_readiness_model.json":value,
      "active_parent_attribute_records.json":dict(records=inv["active_parent_records"]),
      "initial_state_attribute_records.json":dict(records=inv["initial_state_records"]),
      "maximal_constant_attachment_records.json":dict(records=inv["maximal_constant_records"]),
      "value_adversarial_results.json":dict(records=[r for r in negative if r["label"] in VALUE]),
      "output_attribute_implementation_readiness_model.json":output,
      "development_expected_output_records.json":dict(records=inv["development_expected_records"],prospective_literals=d.LITERALS),
      "output_category_evidence.json":dict(records=inv["output_category_records"]),
      "exact_sentinel_evidence.json":dict(records=inv["exact_sentinel_records"]),
      "output_adversarial_results.json":dict(records=[r for r in negative if r["label"] in OUTPUT]),
      "evidence_kind_separation_checks.json":dict(records=[r for r in negative if r["label"] in CROSS],behavioral_outputs_are_not_expected_records=True,output_records_do_not_establish_active=True),
      "independent_value_output_verifier_results.json":dict(records=manifest,payload="value_output_evidence_records.jsonl.gz",encoding="UTF8_JSONL_DETERMINISTIC_GZIP_MEMBERS",constructor_invoked=False,constructor_conclusion_trusted=False),
      "requirement_kind_coverage_matrices.json":dict(value=inv["value_kind_matrix"],output=inv["output_kind_matrix"]),
      "reference_only_dependency_summary.json":reference_dependency(),
      "disposable_overlap.json":dict(**overlap,exception_adversaries=on,causal_independence_test="test_protected_metadata_cannot_choose_output",preflight_failure_reproduced=True,
        original_stop="Canonical ZERO string collision; no edits/executions in stopped attempt",exception_development_only=True),
      "protected_integrity.json":{**integrity,"verifier_baseline_head":integrity["starting_head"]},
      "verification_test_results.json":dict(focused=focused,regressions=reg,known_legacy_failures=legacy,population_test_deselected=True,
        junit_paths=dict(focused=args.focused_junit,legacy=args.legacy_junit,regressions=args.regression_junit),pinned_programs=len(records),pinned_runs=sum(len(d.RAW[n]) for n in d.DECLARATIONS),
        inherited_saved_verifiers=["requirements","boolean_regions","canonical_transport","generic_binding","state_readiness","essentiality_readiness"],
        preflight_all_six_passed=True,inherited_gap_reproduction=dict(value="GENUINE_REQUIRED_COMPONENT_UNBOUND for fresh maximal -(13+8) declaration",output="Zero OUTPUT_ATTRIBUTE requirements in inherited generic projection plan",source_execution=False),
        additional_source_adversaries=dict(unsupported_constant="VALUE_UNSUPPORTED_OR_NONMAXIMAL_ATTACHMENT",reassociation="STATE_REQUIRED_CONTRIBUTION_MISMATCH",extra_display="final display parser rejection",
            exact_literal_grouping="VALUE_LITERAL_EXPRESSION_CONTEXT_MISMATCH"))}
    encoded={name:(json.dumps({**body,"schema_version":1,"artifact_kind":"DEVELOPMENT_ONLY_VALUE_OUTPUT_IMPLEMENTATION_EVIDENCE","starting_head":d.START},sort_keys=True,separators=(",",":"))+"\n").encode() for name,body in files.items()}
    encoded["value_output_evidence_records.jsonl.gz"]=b"".join(payload)
    OUT.mkdir(parents=True)
    for name,data in encoded.items():(OUT/name).write_bytes(data)
    print(json.dumps(dict(records=len(records),value_kinds=len(inv["value_kind_matrix"]),output_kinds=len(inv["output_kind_matrix"]),attribute_adversaries=len(negative),overlap_adversaries=len(on),pinned_runs=files["verification_test_results.json"]["pinned_runs"]),indent=2))

if __name__=="__main__":run()
