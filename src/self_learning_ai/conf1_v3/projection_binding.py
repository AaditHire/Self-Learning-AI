"""Production adapter for DEVELOPMENT_ONLY prospective grammar plans.

Scientific namespaces are rejected BEFORE parsing. The resolver and complete
typed kernels are generic, but no development certificate satisfies science.
"""
from copy import deepcopy
from .projection_binding_verifier import (verify_projection_plan, reconstruct_bindings,
    verify_projection_evidence, digest_source, projection_claims)
from .projection_grammar import development_identity
from .core_ir import compile_program
from .contract_ir import graph_record, keys_from_ir
from .contracts import CoverageContractV3, DOMAINS
from .interfaces import PHASE, rid
from .coverage import reconcile_complete_mapping
from .boolean_regions import total_boolean_mapping
from .requirements import digest


def bind_projection(plan, reference_source, source, *, region_scope=None):
    verify_projection_plan(plan)
    development_identity(reference_source); development_identity(source)
    c=compile_program(plan["program_id"],reference_source)
    keys,occurrences=keys_from_ir(c,())
    contract=CoverageContractV3(1,PHASE,rid("CONTRACT",[c.program_id]),c.program_id,c.program_id,
        "development","ISOLATED",c.domain,DOMAINS[c.domain],(),(),
        {"kind":"development_grammar_projection_not_scientific_slot"},graph_record(c),keys,
        ("NO_SCIENTIFIC_CASES",),tuple(c.roles.values()),{},c.source,occurrences,c)
    region=total_boolean_mapping(contract,source,scope=region_scope) if region_scope else None
    # Existing production exact mapping handles the narrow regional transport.
    # The complete typed alignment path handles the other frozen V3.3 families.
    if region:
        proof=reconcile_complete_mapping(contract,source,region_evidence=region)
    else:
        from .typed_alignment import align
        from .coverage import MappingProof
        p=compile_program(c.program_id,source); alignment=align(c,p); table=dict(alignment["correspondence"])
        proof=MappingProof(contract,p,tuple(table.items()),{k:tuple(table[o] for o in ids) for k,ids in occurrences.items()},
                           digest_source(source),tuple(alignment["equivalence_claims"]))
    base=proof.to_record(); p=proof.program; bundle=proof.semantic_transport
    bindings,indicators=reconstruct_bindings(plan,c,p,base,bundle)
    result=dict(schema_version=1,artifact_kind="DEVELOPMENT_ONLY_GENERIC_SOURCE_BINDING",
        plan_before=deepcopy(plan),plan_after=deepcopy(plan),reference_source=c.source,source=p.source,
        contract_graph=graph_record(c),source_graph=graph_record(p),base_mapping=base,transport_bundle=bundle,
        bindings=bindings,indicator_foundations=indicators,claims=projection_claims(c,p,bindings,bundle),
        source_projection_provenance=dict(scope="DEVELOPMENT_ONLY",declaration_sha256=digest(plan["declaration"]),
            reference_source_sha256=digest_source(c.source),source_sha256=digest_source(p.source),
            scientific_slot_binding=None,scientific_requirement_satisfaction=False,scientific_expected_row_index_eligible=False))
    verify_projection_evidence(result)
    return result
