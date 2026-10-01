"""One-shot DEVELOPMENT state evidence; never population/scientific production."""
from pathlib import Path
import argparse,json,sys,subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests"),str(ROOT/"scripts")]
from audit_conf1_v3_core_closure import verify_protected_inputs
from self_learning_ai.conf1_v3.state_verifier import verify_state_evidence,state_kind_inventory,delete_proof,essentiality_dependencies
from self_learning_ai.conf1_v3.state_semantics import static_evidence
from self_learning_ai.conf1_v3.interfaces import ClosureError,SchemaError
from self_learning_ai.conf1_v3.requirements import digest
from check_conf1_v3_generic_binding import junit
OUT=ROOT/"research/implementation_notes/coverage_v3_state_implementation"


def run():
    parser=argparse.ArgumentParser();parser.add_argument("--focused-junit",required=True);parser.add_argument("--legacy-junit",required=True)
    parser.add_argument("--resume-identical-partial",action="store_true");args=parser.parse_args()
    import state906_inputs as d
    if subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()!=d.START: raise RuntimeError("starting HEAD changed")
    if OUT.exists() and not args.resume_identical_partial: raise RuntimeError("state evidence already exists; no refresh")
    integrity=verify_protected_inputs();overlap=d.overlap()
    focused=junit(args.focused_junit);legacy=junit(args.legacy_junit)
    # This pass's pinned test name is distinct from the preceding binding test.
    import xml.etree.ElementTree as ET
    state_pinned=sum(c.attrib["name"].startswith("test_pinned_disposable_state_outputs") for c in ET.parse(args.focused_junit).getroot().iter("testcase"))
    if focused["failures"] or focused["errors"] or state_pinned!=len(d.DECLARATIONS) or legacy["tests"]!=3 or legacy["failures"]!=3: raise RuntimeError("state validation/legacy boundary incomplete")
    from state906_runtime import evidence,mutations,mutate
    from test_conf1_v3_state_readiness import EXPECTED_REASONS
    records=[]
    for name in d.DECLARATIONS:
        for alpha in (False,True):
            e=evidence(name,alpha);v=verify_state_evidence(e)
            records.append(dict(record_id="STATE906-EVIDENCE-"+str(len(records)),name=name,alpha=alpha,evidence=e,evidence_sha256=digest(e),verification=v))
    negatives=[]
    for label,x in d.BAD.items():
        try: static_evidence(d.PLANS[x["name"]],x["source"])
        except (ClosureError,SchemaError) as exc:
            if str(exc)!=EXPECTED_REASONS[label]: raise RuntimeError("state adversary failed for wrong reason")
            negatives.append(dict(kind="SOURCE_REJECTION",label=label,plan=d.PLANS[x["name"]],source=x["source"],reason=str(exc)))
        else: raise RuntimeError("state adversary accepted")
    base=next(r for r in records if r["name"]==d.BASE and not r["alpha"])
    for attack in mutations(base["evidence"]):
        try: verify_state_evidence(mutate(base["evidence"],attack))
        except (ClosureError,SchemaError) as exc: negatives.append(dict(kind="SERIALIZED_MUTATION",label=attack["name"],base_record_id=base["record_id"],attack=attack,reason=str(exc)))
        else: raise RuntimeError("state mutation accepted")
    matrix={}
    for r in records:
        for kind in state_kind_inventory(r["evidence"]):
            if kind["kind_id"] in matrix: continue
            try: verify_state_evidence(delete_proof(r["evidence"],kind["proof_locator"]))
            except ClosureError as exc: reason=str(exc)
            else: raise RuntimeError("state kind deletion accepted")
            matrix[kind["kind_id"]]=dict(**kind,positive_record_id=r["record_id"],source_grammatical_form=r["evidence"]["plan"]["declaration"],
                static_proof_sha256=digest(r["evidence"]["state_graph"]),negative_example="DELETE_STATIC_KIND_PROOF",negative_reason=reason,independent_verifier_result=r["verification"])
    deps=essentiality_dependencies(ROOT)
    model=dict(scope="DEVELOPMENT_ONLY",STATE_IMPLEMENTATION_READINESS="STATE_GRAPH_IMPLEMENTATION_READY",
        STATE_SCIENTIFIC_INSTANCE_CLOSURE="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION",old_global_gate=deps["old_state_gate"],old_global_gate_changed=False,
        scientific_sources_constructed=0,scientific_satisfaction_claims=0,population_producer_invoked=False,historical_8668_authoritative=False,
        scientific_fixture_execution=False,model_execution=False,essentiality_repair=False,
        grammar_forms=sorted({(r["evidence"]["plan"]["declaration"]["family"],r["evidence"]["required_computation"]["recurrence_class"],r["evidence"]["plan"]["declaration"]["reverse"]) for r in records}),
        pre_edit_gap_reproduction=dict(program_id="STATE906-PREFLIGHT",scope="DEVELOPMENT_ONLY",overlap=0,
            existing_rule="structured sequential transfer / branch union / loop least fixed point",required_computation_certificate_present=False,
            temporal_read_phase_present=False,implicit_forward_step_read_present=False,scientific_execution=False),
        preserved_binding_readiness=dict(INDICATOR="IMPLEMENTATION_READY",V32="IMPLEMENTATION_READY",V33="IMPLEMENTATION_READY"),
        kind_quantifier="DEVELOPMENT STATE REQUIREMENT TYPES; all read/write/edge instances separately retained")
    results=[dict(record_id=r["record_id"],evidence_sha256=r["evidence_sha256"],verification=r["verification"]) for r in records]
    files={"state_implementation_readiness_model.json":model,"state_source_evidence.json":dict(records=records),
        "required_computation_certificates.json":dict(records=[dict(record_id=r["record_id"],certificate=r["evidence"]["required_computation"]) for r in records]),
        "static_reaching_definition_graphs.json":dict(records=[dict(record_id=r["record_id"],graph=r["evidence"]["state_graph"]) for r in records]),
        "runtime_static_trace_agreement.json":dict(records=[dict(record_id=r["record_id"],executions=r["evidence"]["executions"]) for r in records]),
        "state_adversarial_results.json":dict(records=negatives),"independent_state_verifier_results.json":dict(records=results,constructor_conclusion_trusted=False),
        "state_requirement_kind_coverage.json":dict(rows=list(matrix.values())),"essentiality_dependency_summary.json":deps,
        "disposable_overlap.json":overlap,"protected_integrity.json":{**integrity,"verifier_baseline_head":integrity["starting_head"],"starting_head":d.START},
        "verification_test_results.json":dict(focused=focused,state_pinned_programs=state_pinned,state_pinned_runs=2*state_pinned,known_legacy_failures=legacy,population_test_deselected=True)}
    for cls,name in (("PER_ITEM","per_item_recurrence_evidence.json"),("PREFIX","prefix_recurrence_evidence.json"),("TWO_PASS","two_pass_recurrence_evidence.json")):
        files[name]=dict(records=[v for v,r in zip(results,records) if r["evidence"]["required_computation"]["recurrence_class"]==cls])
    encoded={}
    for name,value in files.items():
        data={**value,"schema_version":1,"artifact_kind":"DEVELOPMENT_ONLY_STATE_IMPLEMENTATION_EVIDENCE","starting_head":d.START}
        encoded[name]=json.dumps(data,sort_keys=True,separators=(",",":"))+"\n"
    if OUT.exists():
        # Recovery of an interrupted DEVELOPMENT write only. Never overwrite,
        # refresh, or silently discard an existing record or unknown file.
        if any(p.name not in encoded or not p.is_file() or p.read_bytes()!=encoded[p.name].encode() for p in OUT.iterdir()):
            raise RuntimeError("partial evidence differs; no overwrite permitted")
    OUT.mkdir(parents=True,exist_ok=True)
    for name,value in encoded.items():
        if not (OUT/name).exists(): (OUT/name).write_text(value,encoding="utf-8",newline="\n")
    print(json.dumps(dict(records=len(records),state_requirement_kinds=len(matrix),adversaries=len(negatives),implementation=model["STATE_IMPLEMENTATION_READINESS"],scientific=model["STATE_SCIENTIFIC_INSTANCE_CLOSURE"]),indent=2))


if __name__=="__main__":run()
