"""Attach evidence to an immutable prospective plan; never derive rows here."""
from copy import deepcopy
from .contract_ir import graph_record
from .requirement_verifier import verify_plan, expected_bindings, classify_raw, expected_claims, dependency_scope, verify_requirement_evidence

def build_requirement_evidence(plan,contract,program,base):
    verify_plan(plan); dependencies=dependency_scope(contract.core_gaps,plan)
    bindings=expected_bindings(plan,contract,program,base.to_record(),base.semantic_transport)
    result=dict(schema_version=1,artifact_kind="REQUIREMENT_BOUND_MAPPING_NOT_SCIENTIFIC_ACTIVITY",before=deepcopy(plan),after=deepcopy(plan),
        reference_source=contract.reference_source,source=program.source,contract_graph=graph_record(contract.ir),source_graph=graph_record(program),
        base_mapping=base.to_record(),transport_bundle=base.semantic_transport,bindings=bindings,
        raw_classification=classify_raw(contract,base.to_record(),bindings,base.semantic_transport),
        integrated_claims=expected_claims(contract.ir,program,bindings,base.semantic_transport),dependency_scope=dependencies)
    verify_requirement_evidence(result)
    return result
