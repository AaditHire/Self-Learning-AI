"""Existing typed intervention engine, proof-derived semantic activity identity.

No AST/IR edits, synthetic canonical nodes, caller keys or population producer.
Actual Boolean destinations use false/true; actual numeric destinations use 0/1.
"""
from dataclasses import asdict
import hashlib
from .core_ir import execute
from .interfaces import ClosureError, canonical_json_bytes, rid
from .transport_verifier import verify_canonical_transport

def _run(engine, transports):
    program = engine.mapping.program
    selected = {t["activity_destination"]["occurrence_id"] for t in transports}
    occurrences = tuple(i.occurrence_id for i in program.items if i.occurrence_id in selected)
    types = {program.item(o).datatype for o in occurrences}
    if len(types) != 1: raise ClosureError("MIXED_TYPED_SEMANTIC_INTERVENTION_UNSUPPORTED")
    values = (False, True) if types == {"BOOLEAN"} else (0, 1) if types == {"INTEGER"} else None
    if values is None: raise ClosureError("UNSUPPORTED_SEMANTIC_ACTIVITY_DESTINATION")
    observations, attempts = [], []; witness = None
    for case in sorted(engine.cases, key=lambda c: c.case_id.encode()):
        normal = engine.normals[case.case_id]
        events = [e for e in normal.events if e["delta"] != 0 and selected & e["dependencies"] and e["occurrence_id"] in normal.output_dependencies]
        observations.append({"case_id": case.case_id, "normal_output": normal.output, "actual_compiler_output": engine.compiler_outputs[case.case_id],
            "raw_destination_values": {o: normal.values.get(o, []) for o in occurrences},
            "raw_normal_events": [{**e, "dependencies": sorted(e["dependencies"])} for e in events],
            "raw_state_writes": [r for r in normal.state_trace if r["kind"] == "WRITE" and r["writer"] in {t["activity_destination"]["state_update"] for t in transports}]})
        if not events: continue
        for order, replacement in enumerate(values):
            counter = execute(program, case.raw_input, occurrences=occurrences, replacement=replacement)
            row = {"case_id": case.case_id, "raw_occurrence_ids": occurrences, "raw_replacement": replacement,
                "raw_destination_type": next(iter(types)), "intervention_order": order, "normal_output": normal.output,
                "counterfactual_output": counter.output, "changed": counter.output != normal.output}
            attempts.append(row)
            if witness is None and row["changed"]: witness = row
    return {"finding": "ACTIVE" if witness else "INACTIVE", "status": "PASS", "raw_source_activity_evidence": {
        "raw_destinations": [asdict(program.item(o)) for o in occurrences], "raw_occurrences": occurrences,
        "normal_observations": observations, "intervention_attempts": attempts}, "witness": witness,
        "transport_references": [t["transport_id"] for t in transports],
        "canonical_semantic_key_ids": sorted({t["semantic_key_id"] for t in transports})}

def semantic_activity(engine):
    bundle = engine.mapping.semantic_transport
    if bundle is None: raise ClosureError("VERIFIED_SEMANTIC_TRANSPORT_REQUIRED")
    checked = verify_canonical_transport(bundle)
    groups = {}
    for t in bundle["transports"]: groups.setdefault(t["semantic_key_id"], []).append(t)
    rows = []
    for key, transports in groups.items():
        row = _run(engine, transports)
        row.update(semantic_key_id=key, semantic_definition=transports[0]["semantic_definition"],
            obligation_ids=[t["obligation_id"] for t in transports],
            activity_identity=rid("SEMANTIC_ACTIVITY", [engine.mapping.contract.contract_id, key]),
            mapping_proof_sha256=hashlib.sha256(canonical_json_bytes(engine.mapping.to_record())).hexdigest())
        rows.append(row)
    return {"artifact_kind": "PROOF_DERIVED_SEMANTIC_ACTIVITY_NOT_POPULATION", "records": rows,
        "bound_cases": [{"case_id": c.case_id, "raw_input": c.raw_input, "expected_output": c.expected_output, "expected_output_reference": c.expected_output_reference} for c in engine.cases],
        "source_sha256": engine.mapping.source_sha256,
        "verifier_result": checked, "caller_semantic_key_accepted": False, "raw_graphs_modified": False}

def activity_for_raw_or_key(engine, key_id, resolution):
    # key_id was already resolved from the bound contract and its independently
    # verified MappingProof, never used as a caller-selected semantic identity.
    bundle = engine.mapping.semantic_transport
    verify_canonical_transport(bundle)
    selected = [t for t in bundle["transports"] if t["transport_id"] in resolution["transport_references"]]
    if not selected or any(t["semantic_definition"]["scope"] != "BOOLEAN_OR" for t in selected):
        raise ClosureError("WRONG_FROZEN_OR_ACTIVITY_OBLIGATION")
    result = _run(engine, selected)
    result.update(key_id=key_id, occurrences=engine.mapping.key_occurrences[key_id],
        mapping_method="VERIFIED_REGIONAL_SEMANTIC_TRANSPORT", raw_AND_MUL_key_equality=False)
    engine.findings[key_id] = result
    return result
