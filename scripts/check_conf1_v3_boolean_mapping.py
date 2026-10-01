"""New disposable Boolean evidence producer, never a population producer."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tests"));sys.path.insert(0,str(ROOT/"src"))
import bm901_inputs as d
OUT=ROOT/"research/implementation_notes/coverage_v3_boolean_mapping"

def emit(name,value,refresh=False):
    raw=(json.dumps(value,indent=2,sort_keys=True,default=lambda x:sorted(x) if isinstance(x,(set,frozenset)) else (_ for _ in ()).throw(TypeError(type(x).__name__)))+"\n").encode()
    OUT.mkdir(parents=True,exist_ok=True);p=OUT/name
    if p.exists():
        if p.read_bytes()!=raw:
            if not refresh:raise RuntimeError("different saved Boolean evidence: "+name)
            p.write_bytes(raw)
    else:
        with p.open("xb") as f:f.write(raw)

def preflight():
    spec=importlib.util.spec_from_file_location("bm901_integrity",ROOT/"scripts/audit_conf1_v3_core_closure.py")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    integrity=m.verify_protected_inputs();integrity["starting_head"]=d.START
    emit("protected_input_integrity.json",integrity)
    emit("disposable_overlap.json",d.overlap())

def run(refresh=False):
    preflight()
    from bm901_cases import PAIRS,certificate,negatives,expected
    from self_learning_ai.conf1_v3.boolean_mapping import frozen_boolean_catalog,indicator_evidence
    from self_learning_ai.conf1_v3.core_ir import compile_program,execute
    from self_learning_ai.conf1_v3.coverage import PinnedCompilerOracle
    from self_learning_ai.conf1_v3.interfaces import canonical_json_bytes
    certs=[];locals_=[];indicators=[];normal=[]
    for left,right,scope in PAIRS:
        c,cert=certificate(left,right,scope);certs.append({"contract_form":left,"source_form":right,"certificate":cert})
        locals_.append({"contract_form":left,"source_form":right,"local_proofs":cert["local_v33_proofs"],
            "certificate_kind":"V33_WITH_COMPLETE_TYPED_MAPPING" if cert["finding"]=="COMPLETE" else "LOCAL_V33_ONLY",
            "complete_mapping_certificate_sha256":hashlib.sha256(canonical_json_bytes(cert)).hexdigest(),
            "complete_for_total_mapping":cert["finding"]=="COMPLETE","full_signature_audit_performed":False})
        if cert["finding"]=="COMPLETE":indicators.append({"source_form":right,**indicator_evidence(c,d.SOURCES[right],cert)})
        else:indicators.append({"source_form":right,"finding":"UNRESOLVED","records":[],"reason":"complete V3.2 certificate absent; local proof cannot supply indicator evidence"})
    oracle=PinnedCompilerOracle(ROOT/".tools/jdk-25.0.1+8/bin/java.exe",ROOT/".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    for name in ("AND","PRODUCT","OR","SUM_POSITIVE","MATCHING_OUTPUT_INVALID"):
        p=compile_program("BMAP901-"+name,d.SOURCES[name])
        for cid,raw in zip(d.CASE_IDS,d.RAW):
            ir=execute(p,raw).output;compiler=oracle.run(p.source,raw);reference=expected(name,raw)
            if ir!=compiler or ir!=reference:raise RuntimeError("new Boolean normal/reference/compiler mismatch")
            normal.append({"program_id":p.program_id,"case_id":cid,"raw_input":raw,"reference_output":reference,"actual_ir_output":ir,"actual_compiler_output":compiler})
    negative=negatives()
    known={r["capability"] for name in ("ODD","RESIDUE","DIVISOR","HALF","ARRAY") for r in compile_program("BMAP901-"+name,d.SOURCES[name]).semantic_records}
    required={"odd_index","residue_two","divisor_index","first_half","negative_value","even_value","large_magnitude","value_exceeds_index"}
    if known!=required:raise RuntimeError("primitive catalog regression")
    baseline_path=ROOT/"research/implementation_notes/coverage_v3_semantic_core/semantic_gate_evidence.json"
    baseline=json.loads(baseline_path.read_bytes())
    gates=json.loads(baseline_path.read_bytes())
    scoped={"INDICATOR_EXTRACTION_COMPLETE","V32_SEMANTIC_MAPPING_COMPLETE","V33_REQUIRED_EQUIVALENCE_COMPLETE"}
    changed_forms=certs[:2];closed=all(r["certificate"]["finding"]=="COMPLETE" and not r["certificate"]["unmatched_source_inventory"] and not r["certificate"]["unmatched_contract_inventory"] for r in changed_forms)
    for gate in gates["gates"]:
        if gate["gate"] in scoped:
            blockers=[{"contract_form":r["contract_form"],"source_form":r["source_form"],"reason":r["certificate"].get("reason")} for r in changed_forms if r["certificate"]["finding"]!="COMPLETE"]
            gate.update(status="PASS" if closed else "UNRESOLVED",remaining_evidence_obligations=blockers,
                evidence_file="complete_v32_mapping_certificates.json",detail="Local proofs are independent of complete typed mapping; failed topology transport cannot create indicator evidence")
    if any(a!=b for a,b in zip(baseline["gates"],gates["gates"]) if a["gate"] not in scoped):raise RuntimeError("out-of-scope gate changed")
    gates.update(starting_head=d.START,artifact_kind="BOOLEAN_MAPPING_DEVELOPMENT_GATES_NOT_SCIENTIFIC_BINDER",
        out_of_scope_gate_authority_path=baseline_path.relative_to(ROOT).as_posix(),
        all_semantic_gates_pass=all(g["status"]=="PASS" for g in gates["gates"]),baseline_gate_artifact_sha256=hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
        authoritative_population_recount_performed=False,status="COVERAGE_V3_BOOLEAN_MAPPING_CLOSURE_COMPLETE" if closed else "STOPPED_COVERAGE_V3_BOOLEAN_MAPPING_CLOSURE_ISSUE")
    # Do not repeat a production probe or invoke any population routine.
    gates.pop("pure_production_probe",None)
    artifacts={"frozen_boolean_rule_catalog.json":frozen_boolean_catalog(),"v33_equivalence_certificates.json":{"records":locals_},
        "complete_v32_mapping_certificates.json":{"records":certs},"indicator_extraction_evidence.json":{"records":indicators},
        "negative_case_results.json":{"records":negative,"normal_compiler_observations":normal},"development_gate_evidence.json":gates}
    for name,value in artifacts.items():emit(name,{"schema_version":1,"starting_head":d.START,**value},refresh)
    print(json.dumps({"status":gates["status"],"primitive_catalog":sorted(known),"normal_compiler_cases":len(normal),"negative_cases":len(negative),"gates":{g["gate"]:g["status"] for g in gates["gates"]}},indent=2))

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--preflight-only",action="store_true");parser.add_argument("--refresh",action="store_true")
    args=parser.parse_args()
    if args.preflight_only:preflight();print("Boolean preflight unchanged; zero overlap; no classifier execution")
    else:run(args.refresh)
