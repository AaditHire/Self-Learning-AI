"""Development state certificate constructor, never a scientific gate producer."""
from copy import deepcopy
from .core_ir import execute
from .state_semantics import static_evidence,trace_agreement
from .requirements import digest
from .projection_binding_verifier import digest_source


def construct_state_evidence(plan,source,raw_inputs):
    p,graph,certificate=static_evidence(plan,source)
    packet=dict(schema_version=1,artifact_kind="DEVELOPMENT_ONLY_STATE_EVIDENCE",scope="DEVELOPMENT_ONLY",plan=deepcopy(plan),source=source,
        source_sha256=digest_source(source),state_graph=graph,required_computation=certificate,
        executions=[dict(raw_input=raw,agreement=trace_agreement(p,graph,execute(p,raw,detailed_state_trace=True))) for raw in raw_inputs],
        projection_provenance=dict(declaration_sha256=digest(plan["declaration"]),scientific_slot_binding=None,scientific_expected_row=False),
        state_implementation_readiness="STATE_GRAPH_IMPLEMENTATION_READY",scientific_instance_closure="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION")
    from .state_verifier import verify_state_evidence
    verify_state_evidence(packet)
    return packet
