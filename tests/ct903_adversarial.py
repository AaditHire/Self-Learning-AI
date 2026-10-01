"""New intended-reason transport, MappingProof, and source attacks."""
from copy import deepcopy
from ct903_runtime import contract, certificate
import ct903_inputs as d
from self_learning_ai.conf1_v3.coverage import reconcile_complete_mapping
from self_learning_ai.conf1_v3.interfaces import ClosureError
from self_learning_ai.conf1_v3.transport_verifier import verify_canonical_transport

SOURCE_NEGATIVES = (
    ("non_Boolean_MUL", "AND", "NON_BOOLEAN_MUL", "LOCAL_PAIR_JOINT", "ALPHA_ROLE_MISMATCH"),
    ("sum_extra_contribution", "OR", "EXTRA_SUM", "BOOLEAN_OR", "LOCAL_BOOLEAN_PRECONDITION: operand is neither Boolean nor a source-proved indicator"),
    ("wrong_arity", "AND", "ARITY", "LOCAL_PAIR_JOINT", "LOCAL_BOOLEAN_PRECONDITION: operand is neither Boolean nor a source-proved indicator"),
    ("wrong_predicate", "AND", "WRONG_PREDICATE", "LOCAL_PAIR_JOINT", "LOCAL_BOOLEAN_PRECONDITION: local operand is not one source-mapped frozen predicate; compound/unlisted predicates are not atomic pair inputs"),
    ("stale_read", "AND", "STALE", "LOCAL_PAIR_JOINT", "LOCAL_BOOLEAN_PRECONDITION: indicator use is not after current-iteration definition"),
    ("wrong_target", "AND", "TARGET", "LOCAL_PAIR_JOINT", "ALPHA_ROLE_MISMATCH"),
    ("increment_two", "OR", "INCREMENT", "BOOLEAN_OR", "INCOMPATIBLE_REGION_DOWNSTREAM_CONSUMER"),
    ("downstream_role", "AND", "DOWNSTREAM", "LOCAL_PAIR_JOINT", "ALPHA_ROLE_MISMATCH"),
    ("matching_outputs_invalid", "AND", "MATCHING_OUTPUT_INVALID", "LOCAL_PAIR_JOINT", "INCOMPATIBLE_ORDINARY_STATEMENT_SCAFFOLD"),
    ("wrong_loop", "WRONG_LOOP", "WRONG_LOOP", "LOCAL_PAIR_JOINT", "LOCAL_BOOLEAN_PRECONDITION: indicator use is outside its resetting loop"),
)
MUTATIONS = (
    ("forged_key", "TRANSPORT_SEMANTIC_KEY_MISMATCH"), ("wrong_obligation", "TRANSPORT_WRONG_CONTRACT_OBLIGATION"),
    ("wrong_rule", "UNSUPPORTED_TRANSPORT_RULE"), ("failed_checker", "INDEPENDENT_CHECKER_RESULT_MISMATCH"),
    ("incomplete_total", "COMPLETE_MAPPING_REQUIRED"), ("duplicate_claim", "DUPLICATE_SEMANTIC_OBLIGATION_CLAIM"),
    ("ordinary_double_claim", "ORDINARY_TRANSPORT_DOUBLE_CLAIM"), ("missing_certificate", "MISSING_REGION_CERTIFICATE"),
    ("region_id", "TRANSPORT_REGION_NOT_FOUND"), ("region_hash", "TRANSPORT_REGION_HASH_MISMATCH"),
    ("total_hash", "TRANSPORT_TOTAL_MAPPING_HASH_MISMATCH"), ("checker_hash", "TRANSPORT_CHECKER_HASH_MISMATCH"),
    ("role", "TRANSPORT_ROLE_MISMATCH"), ("loop", "TRANSPORT_LOOP_CONTROL_MISMATCH"),
    ("type", "TRANSPORT_BOUNDARY_TYPE_PORT_MISMATCH"), ("boundary_port", "TRANSPORT_BOUNDARY_TYPE_PORT_MISMATCH"),
    ("stale_evidence", "TRANSPORT_STALE_INDICATOR_EVIDENCE"), ("cycle", "TRANSPORT_DEPENDENCY_CYCLE"),
    ("missing_foundation", "TRANSPORT_DAG_MISSING_FOUNDATION"), ("gate_root", "TRANSPORT_DAG_GATE_OR_CALLER_ROOT"),
    ("caller_key_root", "TRANSPORT_DAG_GATE_OR_CALLER_ROOT"), ("raw_relabel", "TRANSPORT_ACTIVITY_DESTINATION_MISMATCH"),
    ("wrong_semantic_definition", "TRANSPORT_SEMANTIC_KEY_MISMATCH"), ("foreign_region", "TRANSPORT_REGION_HASH_MISMATCH"),
    ("uncovered_region", "SOURCE_UNCOVERED"), ("duplicate_region_owner", "SOURCE_DUPLICATE_COVERAGE"),
)
def mutate(bundle, attack):
    z = deepcopy(bundle); t = z["transports"][0]
    if attack == "forged_key": t["semantic_key_id"] = "caller-selected-semantic-key"
    elif attack == "wrong_obligation": t["obligation_id"] = "another-contract-obligation"
    elif attack == "wrong_rule": t["frozen_rule_id"] = "V3.7"
    elif attack == "failed_checker": z["independent_checker_result"]["finding"] = "FAIL"
    elif attack == "incomplete_total": z["total_mapping_certificate"]["finding"] = "UNRESOLVED"
    elif attack == "duplicate_claim": z["transports"].append(deepcopy(t))
    elif attack == "ordinary_double_claim": z["ordinary_obligations"].append({"obligation_id": "double-claim", "source": t["raw_source_members"][0], "contract": t["raw_contract_members"][0]})
    elif attack == "missing_certificate": z.pop("total_mapping_certificate")
    elif attack == "region_id": t["region_id"] = "nonexistent-region"
    elif attack == "region_hash": t["region_reference"]["sha256"] = "0" * 64
    elif attack == "total_hash": t["total_mapping_reference"]["sha256"] = "0" * 64
    elif attack == "checker_hash": t["checker_reference"]["sha256"] = "0" * 64
    elif attack == "role": t["roles"]["source"]["target_role"] = "INDICATOR"
    elif attack == "loop": t["loop_control_context"]["source"]["loop_paths"] = [[913]]
    elif attack == "type": t["typed_boundary_ports"]["source"]["raw_result_type"] = "BOOLEAN"
    elif attack == "boundary_port": t["typed_boundary_ports"]["source"]["inputs"][0]["port"] += 1
    elif attack == "stale_evidence": t["indicator_reaching_evidence"][0]["current_iteration_reaching_definitions"].pop()
    elif attack == "cycle": z["proof_dependency_graph"]["edges"].append(["activity_semantic_keys", "primitive_recognition"])
    elif attack == "missing_foundation": z["proof_dependency_graph"]["edges"].remove(["primitive_recognition", "reaching_indicator_proof"])
    elif attack == "gate_root": z["proof_dependency_graph"]["nodes"].append({"id": "INDICATOR_EXTRACTION_COMPLETE", "kind": "FOUNDATION"})
    elif attack == "caller_key_root": z["proof_dependency_graph"]["nodes"].append({"id": "caller-semantic-key", "kind": "FOUNDATION"})
    elif attack == "raw_relabel": t["activity_destination"]["raw_operation"] = "AND"
    elif attack == "wrong_semantic_definition": t["semantic_definition"]["scope"] = "BOOLEAN_OR"
    elif attack == "foreign_region": t["region_id"] = z["transports"][1]["region_id"]
    elif attack == "uncovered_region": z["total_mapping_certificate"]["ordinary_correspondence"].pop()
    elif attack == "duplicate_region_owner": z["total_mapping_certificate"]["ordinary_correspondence"].append(deepcopy(z["total_mapping_certificate"]["ordinary_correspondence"][0]))
    else: raise ValueError(attack)
    return z

def base_bundle(repeated=False):
    pair = d.PAIRS[4] if repeated else d.PAIRS[0]
    return reconcile_complete_mapping(contract(pair[0]), d.SOURCES[pair[1]], region_evidence=certificate(*pair)).semantic_transport

def changes(base, changed, path=()):
    """Serialized replace operations keep artifacts reconstructable, not huge copies."""
    if isinstance(base, dict) and isinstance(changed, dict) and set(base) == set(changed):
        out = []
        for key in base: out += changes(base[key], changed[key], path + (key,))
        return out
    if isinstance(base, list) and isinstance(changed, list) and len(base) == len(changed):
        out = []
        for i, (a, b) in enumerate(zip(base, changed)): out += changes(a, b, path + (i,))
        return out
    return [] if base == changed else [{"path": list(path), "value": changed}]

def apply_changes(base, replacements):
    z = deepcopy(base)
    for op in replacements:
        if not op["path"]: z = op["value"]; continue
        target = z
        for part in op["path"][:-1]: target = target[part]
        target[op["path"][-1]] = op["value"]
    return z

def negatives():
    records = []
    for case, left, right, scope, reason in SOURCE_NEGATIVES:
        cert = certificate(left, right, scope)
        if cert["finding"] != "UNRESOLVED" or cert["reason"] != reason: raise RuntimeError((case, cert.get("reason")))
        try: reconcile_complete_mapping(contract(left), d.SOURCES[right], region_evidence=cert)
        except ClosureError as exc: rejected = str(exc)
        else: raise RuntimeError("invalid source transport accepted")
        records.append({"case_id": case, "kind": "SOURCE", "left": left, "right": right, "region_rejection": reason, "production_rejection": rejected})
    for case, reason in MUTATIONS:
        base = base_bundle(case == "foreign_region"); attacked = mutate(base, case)
        try: verify_canonical_transport(attacked)
        except ClosureError as exc: actual = str(exc)
        else: raise RuntimeError("mutation accepted: " + case)
        if reason not in actual: raise RuntimeError((case, reason, actual))
        records.append({"case_id": case, "kind": "SERIALIZED_MUTATION", "base_pair_index": 4 if case == "foreign_region" else 0,
            "expected_reason": reason, "actual_reason": actual, "replace_operations": changes(base, attacked)})
    for left, right, scope in d.PAIRS[:2]:
        try: reconcile_complete_mapping(contract(left), d.SOURCES[right])
        except ClosureError as exc: actual = str(exc)
        else: raise RuntimeError("raw operator without proof accepted")
        records.append({"case_id": "raw_" + right + "_without_proof", "kind": "MISSING_REGIONAL_PROOF", "actual_reason": actual})
    return records
