"""Final fail-closed 17-gate binder."""
from __future__ import annotations
from typing import Any, Mapping, Sequence
from .interfaces import ClosureError, SchemaError

GATES=("V3.1_CONTRACTS","V3.2_TYPED_SOURCE_MAPPING","V3.3_CLOSED_EQUIVALENCE","E1_REFERENCE_VALIDATION","V3.5_ACTIVITY","V3.4_ATOMIC_COVERAGE","V3.4_INPUT_DOMAIN_CLASSES","V3.6_TREATMENT_SYMMETRY","E3_SCAFFOLD","E3_TOKEN_BUDGET","E3_SCHEDULE","V3.7_E5_FULL_SIGNATURE","E2_AST_V2","E4_SIMILARITY_PAIRS","E4_EXACT_OVERLAP","E6_HIDDEN_CASE_DISCRIMINATION","V3.8_FINAL_CLOSURE")

def bind_gate_trace(trace: Sequence[Mapping[str, Any]]) -> str:
    if len(trace)!=len(GATES): raise ClosureError("GATE_TRACE_POPULATION_MISMATCH")
    names=[row.get("gate") for row in trace]
    if names!=list(GATES) or len(names)!=len(set(names)): raise ClosureError("GATE_TRACE_ORDER_MISMATCH")
    required={"gate","executed","status","input_evidence_references","output_evidence_references","verified_row_counts","scientific_reason_codes"}
    for row in trace:
        if set(row)!=required: raise SchemaError("malformed gate row")
        if row["executed"] is not True: return "FAIL"
        if row["status"]=="UNRESOLVED": return "UNRESOLVED"
        if row["status"]!="PASS" or not row["input_evidence_references"] or not row["output_evidence_references"]: return "FAIL"
        counts=row["verified_row_counts"]
        if not isinstance(counts,dict) or not counts or any(not isinstance(x,int) or isinstance(x,bool) or x<0 for x in counts.values()): return "FAIL"
    return "PASS"

def final_bind(candidate_input: Mapping[str,Any], candidate_evidence: Mapping[str,Any], reports: Sequence[Mapping[str,Any]], provenances: Sequence[Mapping[str,Any]], trace: Sequence[Mapping[str,Any]]) -> str:
    if candidate_input.get("model_execution_authorized") is not False or candidate_evidence.get("model_execution_authorized") is not False: return "FAIL"
    if len(reports)!=10 or len(candidate_evidence.get("report_execution_map",[]))!=10: return "FAIL"
    if any(r.get("status")!="PASS" for r in reports): return "UNRESOLVED" if any(r.get("status")=="UNRESOLVED" for r in reports) else "FAIL"
    if any(p.get("status")!="PASS" for p in provenances): return "UNRESOLVED" if any(p.get("status")=="UNRESOLVED" for p in provenances) else "FAIL"
    return bind_gate_trace(trace)
