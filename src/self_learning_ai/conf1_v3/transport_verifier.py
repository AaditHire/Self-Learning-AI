"""Independent serialized canonical transport consumer; never calls constructor."""
from collections import Counter
import hashlib
from .interfaces import ClosureError, canonical_json_bytes, rid
from .core_ir import compile_program
from .contracts import DOMAINS
from .contract_ir import graph_record, keys_from_ir
from .boolean_region_checker import check_serialized_mapping
from .boolean_mapping import frozen_boolean_catalog

def need(ok, reason):
    if not ok: raise ClosureError(reason)
def same(a, b): return canonical_json_bytes(a) == canonical_json_bytes(b)
def sha(value): return hashlib.sha256(canonical_json_bytes(value)).hexdigest()

def verify_canonical_transport(bundle):
    need("total_mapping_certificate" in bundle, "MISSING_REGION_CERTIFICATE")
    fields = {"schema_version", "artifact_kind", "contract", "contract_sha256", "source_sha256", "total_mapping_certificate", "independent_checker_result", "transports", "ordinary_obligations", "proof_dependency_graph"}
    need(set(bundle) == fields, "UNSUPPORTED_TRANSPORT_FIELDS")
    need(type(bundle.get("schema_version")) is int and bundle.get("schema_version") == 1 and bundle.get("artifact_kind") == "CANONICAL_SEMANTIC_TRANSPORT_NOT_RAW_GRAPH_COLLAPSE", "UNSUPPORTED_TRANSPORT_SCHEMA")
    cert = bundle["total_mapping_certificate"]
    check = check_serialized_mapping(cert)
    need(same(check, bundle["independent_checker_result"]), "INDEPENDENT_CHECKER_RESULT_MISMATCH")
    c = bundle["contract"]
    need(sha(c) == bundle["contract_sha256"], "TRANSPORT_CONTRACT_HASH_MISMATCH")
    cp = compile_program(c["program_id"], cert["contract_inventory"]["source"])
    p = compile_program(cert["source_inventory"]["program_id"], cert["source_inventory"]["source"])
    need(c["task_kind"] == "development" and not c["core_gaps"], "INCOMPLETE_OR_UNSUPPORTED_PRODUCTION_CONTRACT")
    need(c["domain"] == cp.domain and c["input_domain"] == DOMAINS[cp.domain], "FROZEN_CONTRACT_DOMAIN_MISMATCH")
    need(same(graph_record(cp), c["complete_expression_graph"]), "TRANSPORT_CONTRACT_GRAPH_MISMATCH")
    outputs = [k["operation"] for k in c["canonical_keys"] if k["category"] == "OUTPUT_CATEGORY"]
    keys, occurrences = keys_from_ir(cp, outputs)
    need(same([k.to_dict() for k in keys], c["canonical_keys"]) and same(occurrences, c["key_occurrences"]), "TRANSPORT_FROZEN_RAW_KEY_INVENTORY_MISMATCH")
    need(cert["contract_inventory"]["program_id"] == c["program_id"], "TRANSPORT_WRONG_CONTRACT_OBLIGATION")
    need(hashlib.sha256(p.source.encode()).hexdigest() == bundle["source_sha256"], "TRANSPORT_SOURCE_HASH_MISMATCH")
    region_by_id = {r["region_id"]: r for r in cert["regions"]}
    records = bundle["transports"]
    claims = [t["obligation_id"] for t in records]
    need(len(claims) == len(set(claims)), "DUPLICATE_SEMANTIC_OBLIGATION_CLAIM")
    need(len(records) == len(region_by_id), "TRANSPORT_REGION_OBLIGATION_INCOMPLETE")
    seen_regions = set(); semantic_keys = []
    rules = {r["scope"]: r for r in frozen_boolean_catalog()["rules"]}
    expected_map = {"id": rid("TOTAL_V32", [c["contract_id"], sha(cert)]), "sha256": sha(cert)}
    expected_check = {"id": rid("INDEPENDENT_REGION_CHECK", [sha(cert), sha(check)]), "sha256": sha(check)}
    for t in records:
        transport_fields = {"transport_id", "obligation_id", "semantic_key_id", "semantic_definition", "frozen_rule_id", "catalog_rule", "region_id", "region_reference", "checker_reference", "total_mapping_reference", "raw_source_members", "raw_contract_members", "typed_boundary_ports", "roles", "loop_control_context", "alpha_mapping", "indicator_reaching_evidence", "activity_destination", "proof_dependencies", "authorization_reason", "direction", "raw_identity_equality_claim"}
        need(set(t) == transport_fields, "UNSUPPORTED_TRANSPORT_RECORD_FIELDS")
        region_id = t["region_id"]
        need(region_id in region_by_id, "TRANSPORT_REGION_NOT_FOUND")
        need(region_id not in seen_regions, "DUPLICATE_SEMANTIC_OBLIGATION_CLAIM"); seen_regions.add(region_id)
        r = region_by_id[region_id]; scope = r["scope"]
        need(t["frozen_rule_id"] == "V3.3" and t["catalog_rule"] == rules[scope]["catalog_rule"], "UNSUPPORTED_TRANSPORT_RULE")
        need(same(t["region_reference"], {"id": region_id, "sha256": sha(r)}), "TRANSPORT_REGION_HASH_MISMATCH")
        need(same(t["total_mapping_reference"], expected_map), "TRANSPORT_TOTAL_MAPPING_HASH_MISMATCH")
        need(same(t["checker_reference"], expected_check), "TRANSPORT_CHECKER_HASH_MISMATCH")
        # Key derivation is recomputed here, not imported from the constructor.
        names = {cert["alpha_mapping"][name]: f"binding{i}:{cp.roles[name]}" for i, name in enumerate(cp.symbols)}
        def canonical(v):
            if isinstance(v, str): return names.get(v, v)
            if isinstance(v, (list, tuple)): return [canonical(x) for x in v]
            return v
        definition = {"frozen_rule_id": "V3.3", "scope": scope, "domain": cp.domain, "input_domain": DOMAINS[cp.domain],
            "predicate_relation": canonical(r["local_v33_proof"]["normalized_local_relation"]),
            "semantic_operand_types": ["BOOLEAN", "BOOLEAN"], "semantic_result_type": "BOOLEAN", "contribution_encoding": "INTEGER_01",
            "target_role": r["contract"]["target_role"], "loop_paths": r["contract"]["loop_paths"], "control_paths": r["contract"]["control_paths"], "atomic_AND_MUL_equality_authorized": False}
        key = rid("SEMANTIC_OBLIGATION", [canonical_json_bytes(definition).decode()])
        need(t["semantic_key_id"] == key and same(t["semantic_definition"], definition), "TRANSPORT_SEMANTIC_KEY_MISMATCH")
        obligation = rid("SEMANTIC_CLAIM", [c["contract_id"], region_id, key])
        need(t["obligation_id"] == obligation, "TRANSPORT_WRONG_CONTRACT_OBLIGATION")
        need(t["transport_id"] == rid("TRANSPORT", [obligation, sha(r)]), "TRANSPORT_ID_MISMATCH")
        for side in ("source", "contract"):
            need(same(t["raw_" + side + "_members"], r[side]["members"]), "TRANSPORT_RAW_MEMBER_MISMATCH")
            role = {"target_binding": r[side]["target_binding"], "target_role": r[side]["target_role"]}
            need(same(t["roles"][side], role), "TRANSPORT_ROLE_MISMATCH")
            context = {name: r[side][name] for name in ("statement_path", "loop_paths", "control_paths")}
            need(same(t["loop_control_context"][side], context), "TRANSPORT_LOOP_CONTROL_MISMATCH")
            ports = {"inputs": r[side]["boundary_input_ports"], "outputs": r[side]["boundary_output_ports"], "operand_types": r[side]["operand_types"], "raw_result_type": r[side]["expression_result_type"]}
            need(same(t["typed_boundary_ports"][side], ports), "TRANSPORT_BOUNDARY_TYPE_PORT_MISMATCH")
        need(same(t["alpha_mapping"], cert["alpha_mapping"]), "TRANSPORT_ALPHA_MISMATCH")
        need(same(t["indicator_reaching_evidence"], r["local_v33_proof"]["preconditions_and_flow_proofs"]), "TRANSPORT_STALE_INDICATOR_EVIDENCE")
        raw = p.item(r["source"]["expression_node"])
        destination = {"occurrence_id": raw.occurrence_id, "raw_operation": raw.operation, "raw_type": raw.datatype, "raw_role": raw.result_role, "state_update": r["source"]["state_update_node"]}
        need(same(t["activity_destination"], destination), "TRANSPORT_ACTIVITY_DESTINATION_MISMATCH")
        reason = ("V3.3 permits this proven-01 realization for the local pair-joint obligation only; it does not satisfy an atomic AND key" if scope == "LOCAL_PAIR_JOINT" else "V3.3 permits this exact typed two-input Boolean OR truth realization; arithmetic nodes remain raw arithmetic nodes")
        need(t["authorization_reason"] == reason and t["direction"] == "SOURCE_REALIZATION_SATISFIES_FROZEN_OBLIGATION" and t["raw_identity_equality_claim"] is False, "TRANSPORT_AUTHORIZATION_OR_DIRECTION_MISMATCH")
        deps = ["frozen_authority", "parsed_typed_source", "primitive_recognition", "reaching_indicator_proof", "local_v33:" + region_id, "region:" + region_id, "independent_verification", "total_v32"]
        need(same(t["proof_dependencies"], deps), "TRANSPORT_FOUNDATION_REFERENCE_MISMATCH")
        semantic_keys.append(key)
    need(seen_regions == set(region_by_id), "TRANSPORT_REGION_OBLIGATION_INCOMPLETE")
    ordinary = bundle["ordinary_obligations"]
    region_members = {s for r in cert["regions"] for s in r["source"]["members"]}
    need(not any(pair["source"] in region_members for pair in ordinary), "ORDINARY_TRANSPORT_DOUBLE_CLAIM")
    need(len({r["obligation_id"] for r in ordinary}) == len(ordinary), "DUPLICATE_DIRECT_OBLIGATION_CLAIM")
    expected = [{"obligation_id": rid("RAW_TYPED_OBLIGATION", [c["contract_id"], pair["contract"]]), **pair} for pair in cert["ordinary_correspondence"]]
    need(same(ordinary, expected), "DIRECT_OBLIGATION_INVENTORY_MISMATCH")
    # Exact required DAG and topological sort, independently of transport_dag.
    dag = bundle["proof_dependency_graph"]
    kinds = {n["id"]: n["kind"] for n in dag["nodes"]}
    need(len(kinds) == len(dag["nodes"]), "TRANSPORT_DAG_DUPLICATE_NODE")
    base = ("frozen_authority", "parsed_typed_source", "primitive_recognition", "reaching_indicator_proof")
    expected_kinds = {n: "FOUNDATION" for n in base}
    expected_edges = {(base[i], base[i + 1]) for i in range(3)}
    for r in region_by_id:
        expected_kinds.update({"local_v33:" + r: "LOCAL_EQUIVALENCE", "region:" + r: "REGION_CERTIFICATE", "transport:" + r: "SEMANTIC_TRANSPORT"})
        expected_edges |= {("reaching_indicator_proof", "local_v33:" + r), ("local_v33:" + r, "region:" + r), ("region:" + r, "independent_verification"), ("total_v32", "transport:" + r), ("transport:" + r, "production_mapping_proof")}
    expected_kinds.update(independent_verification="INDEPENDENT_CHECK", total_v32="TOTAL_CORRESPONDENCE", production_mapping_proof="MAPPING_PROOF", activity_semantic_keys="DERIVED_ACTIVITY_IDENTITY")
    expected_edges |= {("independent_verification", "total_v32"), ("production_mapping_proof", "activity_semantic_keys")}
    need(kinds == expected_kinds, "TRANSPORT_DAG_GATE_OR_CALLER_ROOT")
    edges = [tuple(e) for e in dag["edges"]]
    need(len(edges) == len(set(edges)) and all(a in kinds and b in kinds for a, b in edges), "TRANSPORT_DAG_INVALID_REFERENCE")
    degree = Counter(b for a, b in edges); pending = [n for n in kinds if degree[n] == 0]; order = []
    while pending:
        n = pending.pop(); order.append(n)
        for a, b in edges:
            if a == n:
                degree[b] -= 1
                if degree[b] == 0: pending.append(b)
    need(len(order) == len(kinds), "TRANSPORT_DEPENDENCY_CYCLE")
    need(set(edges) == expected_edges, "TRANSPORT_DAG_MISSING_FOUNDATION")
    return {"finding": "VERIFIED_CANONICAL_TRANSPORT", "semantic_key_ids": semantic_keys, "obligation_ids": claims,
        "direct_obligation_count": len(ordinary), "regional_obligation_count": len(records), "dependency_order": order,
        "constructor_invoked": False, "region_constructor_invoked": False, "raw_graph_equality_claim": False}

def verify_mapping_proof_record(bundle, record):
    """Recompute the production adapter's key resolution without MappingProof."""
    checked = verify_canonical_transport(bundle)
    fields = {"contract_id", "program_id", "source_sha256", "ordinary_correspondence", "key_occurrences", "equivalence_proofs", "semantic_transport_sha256", "obligation_satisfaction", "raw_key_resolution", "mapping_status", "all_raw_atomic_keys_satisfied", "raw_graph_equality_claim"}
    need(set(record) == fields, "UNSUPPORTED_MAPPING_PROOF_FIELDS")
    cert, contract = bundle["total_mapping_certificate"], bundle["contract"]
    p = compile_program(contract["program_id"], cert["source_inventory"]["source"])
    direct = {r["contract"]: r["source"] for r in cert["ordinary_correspondence"]}
    by_root = {r["contract"]["expression_node"]: r for r in cert["regions"]}
    transports = {t["region_id"]: t for t in bundle["transports"]}
    rows, resolved = [], {}
    for key in contract["canonical_keys"]:
        required = contract["key_occurrences"][key["key_id"]]; refs = []
        if all(o in direct for o in required):
            method = "DIRECT_TYPED_CORRESPONDENCE"; actual = [direct[o] for o in required]
        elif key["evidence_kind"] == "BEHAVIORAL" and key["operation"] == "OR" and all(o in by_root and by_root[o]["scope"] == "BOOLEAN_OR" for o in required):
            method = "VERIFIED_REGIONAL_SEMANTIC_TRANSPORT"; actual = [by_root[o]["source"]["expression_node"] for o in required]
            refs = [transports[by_root[o]["region_id"]]["transport_id"] for o in required]
            need(all(p.item(o).datatype == "BOOLEAN" for o in actual), "MAPPING_PROOF_BOUNDARY_TYPE_MISMATCH")
        else: method = "UNRESOLVED_DISTINCT_RAW_REQUIREMENT"; actual = []
        if actual: resolved[key["key_id"]] = actual
        rows.append({"key_id": key["key_id"], "operation": key["operation"], "method": method,
            "contract_occurrences": required, "source_occurrences": actual, "transport_references": refs})
    need(same(record["raw_key_resolution"], rows) and same(record["key_occurrences"], resolved), "MAPPING_PROOF_WRONG_KEY_SATISFACTION")
    need(same(record["ordinary_correspondence"], list(direct.items())), "MAPPING_PROOF_ORDINARY_CORRESPONDENCE_MISMATCH")
    need(same(record["obligation_satisfaction"], {"direct": bundle["ordinary_obligations"], "regional": bundle["transports"]}), "MAPPING_PROOF_OBLIGATION_SATISFACTION_MISMATCH")
    need(same(record["equivalence_proofs"], bundle["transports"]), "MAPPING_PROOF_EQUIVALENCE_REFERENCE_MISMATCH")
    need(record["semantic_transport_sha256"] == sha(bundle) and record["source_sha256"] == bundle["source_sha256"], "MAPPING_PROOF_HASH_MISMATCH")
    need(record["contract_id"] == contract["contract_id"] and record["program_id"] == contract["program_id"], "MAPPING_PROOF_WRONG_CONTRACT")
    need(record["mapping_status"] == "TOTAL_CORRESPONDENCE_WITH_VERIFIED_SEMANTIC_TRANSPORT" and record["raw_graph_equality_claim"] is False, "MAPPING_PROOF_UNAUTHORIZED_GRAPH_CLAIM")
    need(record["all_raw_atomic_keys_satisfied"] == all(r["method"] != "UNRESOLVED_DISTINCT_RAW_REQUIREMENT" for r in rows), "MAPPING_PROOF_UNPROVED_RAW_KEY_COMPLETION")
    return {"finding": "VERIFIED_PRODUCTION_MAPPING_FOR_INTENDED_SEMANTIC_OBLIGATIONS", "semantic_obligation_ids": checked["obligation_ids"],
        "unresolved_raw_keys": [r for r in rows if r["method"] == "UNRESOLVED_DISTINCT_RAW_REQUIREMENT"],
        "mapping_constructor_invoked": False, "key_resolution_recomputed": True}
