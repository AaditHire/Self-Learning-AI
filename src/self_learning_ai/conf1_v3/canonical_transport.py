"""One-way frozen semantic obligation transport above immutable raw graphs."""
from dataclasses import dataclass, asdict
import hashlib
from .interfaces import canonical_json_bytes, rid
from .core_ir import compile_program
from .boolean_region_checker import check_serialized_mapping
from .boolean_regions import json_value

def digest(value): return hashlib.sha256(canonical_json_bytes(value)).hexdigest()

@dataclass(frozen=True)
class CanonicalSemanticTransport:
    transport_id: str
    obligation_id: str
    semantic_key_id: str
    semantic_definition: dict
    frozen_rule_id: str
    catalog_rule: str
    region_id: str
    region_reference: dict
    checker_reference: dict
    total_mapping_reference: dict
    raw_source_members: list
    raw_contract_members: list
    typed_boundary_ports: dict
    roles: dict
    loop_control_context: dict
    alpha_mapping: dict
    indicator_reaching_evidence: list
    activity_destination: dict
    proof_dependencies: list
    authorization_reason: str
    direction: str = "SOURCE_REALIZATION_SATISFIES_FROZEN_OBLIGATION"
    raw_identity_equality_claim: bool = False

def semantic_definition(c, p, cert, region):
    bindings = {cert["alpha_mapping"][name]: f"binding{i}:{c.ir.roles[name]}" for i, name in enumerate(c.ir.symbols)}
    def normalize(v):
        if isinstance(v, str): return bindings.get(v, v)
        if isinstance(v, (tuple, list)): return [normalize(x) for x in v]
        return v
    return {"frozen_rule_id": "V3.3", "scope": region["scope"], "domain": c.domain, "input_domain": c.input_domain,
        "predicate_relation": normalize(region["local_v33_proof"]["normalized_local_relation"]),
        "semantic_operand_types": ["BOOLEAN", "BOOLEAN"], "semantic_result_type": "BOOLEAN",
        "contribution_encoding": "INTEGER_01", "target_role": region["contract"]["target_role"],
        "loop_paths": region["contract"]["loop_paths"], "control_paths": region["contract"]["control_paths"],
        "atomic_AND_MUL_equality_authorized": False}

def transport_dag(region_ids):
    phases = ("frozen_authority", "parsed_typed_source", "primitive_recognition", "reaching_indicator_proof")
    nodes = [{"id": n, "kind": "FOUNDATION"} for n in phases]
    edges = [[phases[i], phases[i + 1]] for i in range(len(phases) - 1)]
    for r in region_ids:
        nodes += [{"id": "local_v33:" + r, "kind": "LOCAL_EQUIVALENCE"}, {"id": "region:" + r, "kind": "REGION_CERTIFICATE"}, {"id": "transport:" + r, "kind": "SEMANTIC_TRANSPORT"}]
        edges += [["reaching_indicator_proof", "local_v33:" + r], ["local_v33:" + r, "region:" + r], ["region:" + r, "independent_verification"], ["total_v32", "transport:" + r], ["transport:" + r, "production_mapping_proof"]]
    nodes += [{"id": "independent_verification", "kind": "INDEPENDENT_CHECK"}, {"id": "total_v32", "kind": "TOTAL_CORRESPONDENCE"}, {"id": "production_mapping_proof", "kind": "MAPPING_PROOF"}, {"id": "activity_semantic_keys", "kind": "DERIVED_ACTIVITY_IDENTITY"}]
    edges += [["independent_verification", "total_v32"], ["production_mapping_proof", "activity_semantic_keys"]]
    return {"nodes": nodes, "edges": edges}

def build_canonical_transport(contract, source, certificate):
    contract.validate()
    from .transport_verifier import verify_canonical_transport
    checked = check_serialized_mapping(certificate)
    p = compile_program(contract.program_id, source)
    mapping_hash, checker_hash = digest(certificate), digest(checked)
    records = []
    for region in certificate["regions"]:
        r = region["region_id"]; definition = semantic_definition(contract, p, certificate, region)
        key = rid("SEMANTIC_OBLIGATION", [canonical_json_bytes(definition).decode()])
        obligation = rid("SEMANTIC_CLAIM", [contract.contract_id, r, key])
        source_root = p.item(region["source"]["expression_node"])
        reason = ("V3.3 permits this proven-01 realization for the local pair-joint obligation only; it does not satisfy an atomic AND key" if region["scope"] == "LOCAL_PAIR_JOINT" else "V3.3 permits this exact typed two-input Boolean OR truth realization; arithmetic nodes remain raw arithmetic nodes")
        records.append(asdict(CanonicalSemanticTransport(
            rid("TRANSPORT", [obligation, digest(region)]), obligation, key, definition, "V3.3", region["frozen_rule"]["catalog_rule"], r,
            {"id": r, "sha256": digest(region)}, {"id": rid("INDEPENDENT_REGION_CHECK", [mapping_hash, checker_hash]), "sha256": checker_hash},
            {"id": rid("TOTAL_V32", [contract.contract_id, mapping_hash]), "sha256": mapping_hash},
            region["source"]["members"], region["contract"]["members"],
            {side: {"inputs": region[side]["boundary_input_ports"], "outputs": region[side]["boundary_output_ports"], "operand_types": region[side]["operand_types"], "raw_result_type": region[side]["expression_result_type"]} for side in ("source", "contract")},
            {side: {"target_binding": region[side]["target_binding"], "target_role": region[side]["target_role"]} for side in ("source", "contract")},
            {side: {name: region[side][name] for name in ("statement_path", "loop_paths", "control_paths")} for side in ("source", "contract")},
            certificate["alpha_mapping"], region["local_v33_proof"]["preconditions_and_flow_proofs"],
            {"occurrence_id": source_root.occurrence_id, "raw_operation": source_root.operation, "raw_type": source_root.datatype, "raw_role": source_root.result_role, "state_update": region["source"]["state_update_node"]},
            ["frozen_authority", "parsed_typed_source", "primitive_recognition", "reaching_indicator_proof", "local_v33:" + r, "region:" + r, "independent_verification", "total_v32"], reason)))
    bundle = {"schema_version": 1, "artifact_kind": "CANONICAL_SEMANTIC_TRANSPORT_NOT_RAW_GRAPH_COLLAPSE", "contract": contract.to_dict(),
        "contract_sha256": digest(contract.to_dict()), "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "total_mapping_certificate": certificate, "independent_checker_result": checked, "transports": records,
        "ordinary_obligations": [{"obligation_id": rid("RAW_TYPED_OBLIGATION", [contract.contract_id, pair["contract"]]), **pair} for pair in certificate["ordinary_correspondence"]],
        "proof_dependency_graph": transport_dag([r["region_id"] for r in certificate["regions"]])}
    bundle = json_value(bundle)
    verify_canonical_transport(bundle)
    return bundle
