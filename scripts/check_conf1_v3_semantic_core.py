"""Produce disposable semantic development evidence, never a population index."""
from pathlib import Path
import argparse
from dataclasses import asdict
import importlib.util
import json
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
START="41468f4c831159b5658f14efd87c3ee9407922e8"
OUT=ROOT/"research/implementation_notes/coverage_v3_semantic_core"
REFRESH_DEVELOPMENT_EVIDENCE=False
GENERATED_EVIDENCE=frozenset({"primitive_indicator_extraction.json","state_essentiality_traces.json",
    "attribute_output_attachments.json","semantic_gate_evidence.json"})
sys.path.insert(0,str(ROOT/"tests"))
import sem900_development_inputs as dev


def emit(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/name;raw=(json.dumps(value,indent=2,ensure_ascii=False,sort_keys=name in GENERATED_EVIDENCE,
        default=lambda v:sorted(v) if isinstance(v,(set,frozenset)) else (_ for _ in ()).throw(TypeError(type(v).__name__)))+"\n").encode()
    if path.exists():
        if path.read_bytes()!=raw:
            if not REFRESH_DEVELOPMENT_EVIDENCE or name not in GENERATED_EVIDENCE:
                raise RuntimeError("development artifact already exists with different evidence: "+name)
            # Only this pass's four generated development outputs may refresh.
            # Protected-input and overlap snapshots must remain byte-identical.
            path.write_bytes(raw)
    else:
        with path.open("xb") as f:f.write(raw)


def preflight():
    spec=importlib.util.spec_from_file_location("sem900_integrity",ROOT/"scripts/audit_conf1_v3_core_closure.py")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    integrity=m.verify_protected_inputs();integrity["starting_head"]=START
    emit("protected_input_integrity.json",integrity)
    overlap=dev.overlap();emit("disposable_overlap.json",overlap)
    return overlap


def run():
    preflight()  # No classifier import or execution precedes overlap proof.
    sys.path.insert(0,str(ROOT/"src"))
    from sem900_runtime import engine
    from self_learning_ai.conf1_v3.core_ir import execute
    from self_learning_ai.conf1_v3.goco import Expr,_walk_stmt
    from self_learning_ai.conf1_v3.semantic_ir import source_flow_equivalence
    extraction=[];traces=[];attachments=[];findings=[];equivalences=[];untested=[];production_gaps=[]
    with tempfile.TemporaryDirectory(prefix="sem900-evidence-") as temp:
        for name in dev.SOURCES:
            if name.startswith("BAD_") or name=="ARRAY_LE":continue
            folder=Path(temp)/name;folder.mkdir()
            e=engine(folder,name);p=e.mapping.program
            extraction.append({"program_id":p.program_id,"source":p.source,
                "primitive_occurrences":p.semantic_records,"indicator_proofs":p.indicator_proofs,
                "complete_occurrence_mapping":e.mapping.correspondence,"computed_value_mapping_proofs":e.mapping.equivalence_proofs,
                "bound_inputs":[{"artifact_reference":ref,"exact_utf8_content":e.resolver.read(ref["artifact_id"]).decode("utf-8")} for ref in e.resolver.artifacts.values()]})
            traces.append({"program_id":p.program_id,"state_analysis":p.state_analysis,
                "normal_cases":[{"case_id":c.case_id,"input":c.raw_input,"expected_output":c.expected_output,
                    "actual_normal_output":e.normals[c.case_id].output,"actual_compiler_output":e.compiler_outputs[c.case_id],
                    "compiler_reference_ir_agreement":e.normals[c.case_id].output==e.compiler_outputs[c.case_id]==c.expected_output,
                    "state_trace":e.normals[c.case_id].state_trace,"output_dependencies":sorted(e.normals[c.case_id].output_dependencies),
                    "normal_output_events":e.normals[c.case_id].events} for c in e.cases],"behavioral_findings":[]})
            attachment={"program_id":p.program_id,"maximal_attribute_specs":list(p.attribute_specs.values()),"findings":[]}
            for key in e.mapping.contract.canonical_keys:
                if key.category=="SEMANTIC_PRIMITIVE" or key.operation in {"PREDICATE_TO_INDICATOR","ACCUMULATE","BOUNDED_LOOP"} or key.operation=="MUL" and name=="TWO_PASS":
                    result=e.behavioral(key.key_id);findings.append(result);traces[-1]["behavioral_findings"].append(result)
                    witness=result.get("witness")
                    if witness and key.operation in {"ACCUMULATE","MUL"}:
                        case=next(c for c in e.cases if c.case_id==witness["case_id"])
                        counter=execute(p,case.raw_input,occurrences=e.mapping.key_occurrences[key.key_id],replacement=witness["replacement"])
                        if counter.output!=witness["counterfactual_output"]:raise RuntimeError("counterfactual witness did not reproduce")
                        traces[-1].setdefault("stateful_counterfactual_witnesses",[]).append({"key_id":key.key_id,
                            "case_id":case.case_id,"raw_input":case.raw_input,"complete_mapped_occurrences":e.mapping.key_occurrences[key.key_id],
                            "replacement":witness["replacement"],"actual_normal_output":e.normals[case.case_id].output,
                            "actual_counterfactual_output":counter.output,"counterfactual_state_trace":counter.state_trace,
                            "counterfactual_output_dependencies":sorted(counter.output_dependencies)})
                elif key.evidence_kind=="VALUE_OR_LITERAL_ATTRIBUTE":attachment["findings"].append(e.attribute(key.key_id))
                elif key.evidence_kind=="OUTPUT_ATTRIBUTE":attachment["findings"].append(e.output_attribute(key.key_id))
                elif key.evidence_kind=="BEHAVIORAL":untested.append({"program_id":p.program_id,"key_id":key.key_id,"reason":"not covered by this pass's complete class-specific intervention proof"})
            attachments.append(attachment)
            if name in {"FLOW_AND","FLOW_OR","AMBIGUOUS"}:
                exprs=[x for top in p.statements for x in _walk_stmt(top) if isinstance(x,Expr) and x.kind=="BINARY"]
                if name=="FLOW_AND":a=next(x for x in exprs if x.value=="&&");b=next(x for x in exprs if x.value=="*");context="LOCAL_PAIR_JOINT"
                elif name=="FLOW_OR":a=next(x for x in exprs if x.value=="||");b=next(x for x in exprs if x.value==">");context="BOOLEAN_OR"
                else:a=b=next(x for x in exprs if x.value=="*");context="LOCAL_PAIR_JOINT"
                equivalences.append({"program_id":p.program_id,**source_flow_equivalence(p,a,p,b,context=context)})
    # One pure frozen contract probe; no cases selected or executed, no row IDs
    # or population counts derived. Its unresolved declarations are executable
    # evidence for the development gates, not a manual completion flag.
    from self_learning_ai.conf1_v3.contracts import contract_from_slot
    ledger=json.loads((ROOT/"research/protocols/phase3c_conf1_slots.json").read_bytes())
    probe=contract_from_slot(ledger,ledger["slots"]["training_paired_slots"][0],condition="ISOLATED")
    production_gaps=list(probe.core_gaps)
    # Development gates concern the COMPLETE semantic implementation, not just
    # success on a few toys. Positive evidence narrows a gap; it cannot waive
    # production contract derivation, unsupported parents, or a missing mapping.
    known={r["capability"] for p in extraction for r in p["primitive_occurrences"]}
    required={"odd_index","residue_two","divisor_index","first_half","negative_value","even_value","large_magnitude","value_exceeds_index"}
    required_fields={"capability","authority","source_location","expression_node_id","contract_occurrence_id",
        "input_ports","output_port","operand_types","result_type","control_context","state_relations","structural_output_dependency"}
    supported=known==required and all(required_fields<=set(r) and r["result_type"]=="BOOLEAN" and
        len(r["input_ports"])==len(r["operand_types"])==2 and
        all(port["type"]==r["operand_types"][port["port"]] for port in r["input_ports"]) and
        r["contract_occurrence_id"] in dict(p["complete_occurrence_mapping"]).values()
        for p in extraction for r in p["primitive_occurrences"])
    unresolved_parents=sum(not s["parent_ontology_supported"] for p in attachments for s in p["maximal_attribute_specs"])
    accepted_flows=[p for p in equivalences if p["finding"]=="EQUIVALENT"]
    flow_integration_complete=bool(accepted_flows) and all(p.get("complete_source_mapping_certificate") for p in accepted_flows)
    flow_blockers=[] if flow_integration_complete else ["accepted local-flow proofs do not contain total-source mapping certificates"]
    essentiality_blockers=(["untested behavioral classes"] if untested else [])+sorted({r.get("reason","unresolved intervention") for r in findings if r["finding"]=="UNRESOLVED"})
    gate_details=[
        ("PRIMITIVE_EXTRACTION_COMPLETE",[] if supported else ["frozen predicate catalog/type/port mismatch"],"All eight frozen predicate trees extracted with typed ports; repeated occurrences and alpha are retained","primitive_indicator_extraction.json"),
        ("INDICATOR_EXTRACTION_COMPLETE",flow_blockers,"Range/current-iteration proofs and every indicator write/edge are recorded; ambiguous definitions reject local equivalence","primitive_indicator_extraction.json"),
        ("STATE_GRAPH_COMPLETE",[g for g in production_gaps if g=="TASK_ESSENTIALITY_PROOF_INCOMPLETE"],"Structured reaching definitions and actual-writer traces agree on all three families/reverse; pure frozen probe still lacks recurrence/essentiality certification","state_essentiality_traces.json"),
        ("ESSENTIALITY_ENGINE_COMPLETE",essentiality_blockers,"Joint typed interventions are executed; the untested-key inventory and unresolved loop interventions block full closure","state_essentiality_traces.json"),
        ("VALUE_LITERAL_ATTACHMENT_COMPLETE",["unsupported source parent ontology"] if unresolved_parents else [g for g in production_gaps if g=="COMPUTED_CONSTANT_SUBTREE_ATTACHMENT_INCOMPLETE"],f"Maximal roots and exact initial/active-parent witnesses work; {unresolved_parents} unsupported toy parent attachments remain explicit","attribute_output_attachments.json"),
        ("OUTPUT_ATTACHMENT_COMPLETE",[g for g in production_gaps if g=="OUTPUT_CASE_OBLIGATIONS_UNRESOLVED"],"Bound output nodes/categories/sentinels work; the pure frozen probe emits no completed prospective declaration","attribute_output_attachments.json"),
        ("V32_SEMANTIC_MAPPING_COMPLETE",flow_blockers,"Total identical/alpha and computed-constant mappings exist; local Boolean alternatives do not supply a complete-source mapping","primitive_indicator_extraction.json"),
        ("V33_REQUIRED_EQUIVALENCE_COMPLETE",flow_blockers,"AND/product and OR/indicator proof preconditions succeed, ambiguity rejects; total mapping integration remains missing","attribute_output_attachments.json"),
    ]
    gates={"schema_version":1,"artifact_kind":"DEVELOPMENT_SEMANTIC_GATES_NOT_SCIENTIFIC_BINDER",
        "starting_head":START,"gates":[{"gate":n,"status":"PASS" if not blockers else "UNRESOLVED","remaining_evidence_obligations":blockers,"evidence_file":f,"detail":d} for n,blockers,d,f in gate_details],
        "all_semantic_gates_pass":all(not blockers for _,blockers,_,_ in gate_details),
        "pure_production_probe":{"program_id":probe.program_id,"core_gaps":production_gaps,"case_execution":False,"population_derivation":False},
        "authoritative_population_recount_performed":False,"population_status":"V3_5_POPULATION_UNRESOLVED",
        "diagnostic_8668_status":"historical non-authoritative checkpoint only; not recounted",
        "scientific_17_gate_binder_changed":False,"status":"STOPPED_COVERAGE_V3_CORE_SEMANTIC_CLOSURE_ISSUE"}
    def base(kind,records):return {"schema_version":1,"artifact_kind":kind,"starting_head":START,"disposable_only":True,"records":records}
    emit("primitive_indicator_extraction.json",base("TYPED_DISPOSABLE_EXTRACTION",extraction))
    emit("state_essentiality_traces.json",{**base("ACTUAL_DISPOSABLE_STATE_AND_INTERVENTION",traces),"untested_behavioral_obligations":untested})
    emit("attribute_output_attachments.json",{**base("EXACT_DISPOSABLE_ATTACHMENTS",attachments),"local_equivalence_proofs":equivalences})
    emit("semantic_gate_evidence.json",gates)
    print(json.dumps(gates,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--preflight-only",action="store_true")
    parser.add_argument("--refresh-development-evidence",action="store_true",help="refresh only this pass's four generated toy evidence files")
    args=parser.parse_args()
    REFRESH_DEVELOPMENT_EVIDENCE=args.refresh_development_evidence
    if args.preflight_only:
        p=preflight();print(json.dumps({k:v for k,v in p.items() if k!="inventory"},indent=2))
    else:run()
