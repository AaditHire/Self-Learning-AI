"""Intended-reason source and serialized-evidence attacks on new data."""
from copy import deepcopy
import bt902_inputs as d
from bt902_runtime import certificate
from self_learning_ai.conf1_v3.boolean_region_checker import check_serialized_mapping
from self_learning_ai.conf1_v3.interfaces import ClosureError

SOURCE_NEGATIVES = (
    ("valid_local_AND_extra_arithmetic", "AND", "EXTRA_ARITHMETIC", "LOCAL_PAIR_JOINT", "INCOMPATIBLE_ORDINARY_STATEMENT_SCAFFOLD", True),
    ("valid_local_OR_extra_Boolean", "OR", "EXTRA_BOOLEAN", "BOOLEAN_OR", "INCOMPATIBLE_ORDINARY_STATEMENT_SCAFFOLD", True),
    ("valid_local_missing_contract_behavior", "REPEATED_AND", "MISSING", "LOCAL_PAIR_JOINT", "BOOLEAN_REGION_INVENTORY_INCOMPLETE", True),
    ("wrong_loop_program", "WRONG_LOOP", "WRONG_LOOP", "LOCAL_PAIR_JOINT", "LOCAL_BOOLEAN_PRECONDITION: indicator use is outside its resetting loop", True),
    ("valid_local_incompatible_downstream", "AND", "DOWNSTREAM", "LOCAL_PAIR_JOINT", "INCOMPATIBLE_ORDINARY_STATEMENT_SCAFFOLD", True),
    ("extra_indicator_contribution", "AND", "EXTRA_INDICATOR", "LOCAL_PAIR_JOINT", "BOOLEAN_REGION_INVENTORY_INCOMPLETE", False),
    ("source_only_state_mutation", "AND", "STATE_MUTATION", "LOCAL_PAIR_JOINT", "LOCAL_BOOLEAN_PRECONDITION: indicator reset/write catalog not proved", False),
    ("same_outputs_invalid_topology", "AND", "SAME_OUTPUT", "LOCAL_PAIR_JOINT", "INCOMPATIBLE_ORDINARY_STATEMENT_SCAFFOLD", True),
    ("same_predicates_wrong_state_boundary", "AND", "WRONG_BOUNDARY", "LOCAL_PAIR_JOINT", "ALPHA_ROLE_MISMATCH", False),
)

MUTATIONS = (
    ("overlapping_region_candidates", "OVERLAPPING_REGION_CANDIDATES"),
    ("source_node_claimed_twice", "SOURCE_DUPLICATE_COVERAGE"),
    ("source_node_claimed_by_two_regions", "OVERLAPPING_REGION_NODES"),
    ("contract_node_uncovered", "CONTRACT_UNCOVERED"),
    ("source_node_uncovered", "SOURCE_UNCOVERED"),
    ("boundary_input_port", "REGION_INPUT_BOUNDARY_PORT_MISMATCH"),
    ("boundary_output_port", "REGION_OUTPUT_BOUNDARY_PORT_MISMATCH"),
    ("wrong_loop_boundary", "REGION_CONTEXT_MUTATION"),
    ("predicate_identity", "LOCAL_V33_SOURCE_FLOW_MISMATCH"),
    ("result_type", "REGION_RESULT_TYPE_MUTATION"),
    ("operand_role", "REGION_INPUT_BOUNDARY_PORT_MISMATCH"),
    ("missing_internal_edge", "REGION_INTERNAL_EDGE_COMPLETENESS"),
    ("missing_region_certificate", "DUPLICATE_OR_MISSING_REGION_ID"),
    ("cycle", "CYCLIC_PROOF_DEPENDENCY"),
    ("missing_dependency", "DAG_REQUIRED_FOUNDATION_MISSING"),
    ("gate_as_root", "DAG_NODE_OR_REGION_REFERENCE_MISMATCH"),
    ("forged_partition", "SAVED_PARTITION_MISMATCH"),
    ("graph_type_mutation", "SERIALIZED_GRAPH_SOURCE_MISMATCH"),
    ("foreign_region_node", "REGION_NODE_COMPLETENESS"),
    ("extra_numeric_contribution", "REGION_SEMANTIC_BOUNDARY_MUTATION"),
    ("ordinary_port", "ORDINARY_EDGE_PORT_ENDPOINT_MISMATCH"),
    ("full_graph_claim", "UNAUTHORIZED_FULL_GRAPH_OR_ATOMIC_KEY_CLAIM"),
)

def mutate(cert, attack):
    z = deepcopy(cert); r = z["regions"][0]
    if attack == "overlapping_region_candidates":
        other = deepcopy(r); other["region_id"] = "overlap_region"; z["regions"].append(other)
    elif attack == "source_node_claimed_by_two_regions":
        other = deepcopy(r); other["region_id"] = "second_region"
        other["source"]["statement_path"] = [907]; other["contract"]["statement_path"] = [907]
        z["regions"].append(other)
    elif attack == "source_node_claimed_twice":
        z["ordinary_correspondence"].append({"source": r["source"]["nodes"][0], "contract": r["contract"]["nodes"][0]})
    elif attack in {"contract_node_uncovered", "source_node_uncovered"}:
        # Removing a bilateral ordinary claim exposes the uncovered node on
        # BOTH sides. Checker reports both instead of hiding the second side.
        z["ordinary_correspondence"].pop(0 if attack == "contract_node_uncovered" else 1)
    elif attack == "boundary_input_port": r["source"]["boundary_input_ports"][0]["port"] += 1
    elif attack == "boundary_output_port": r["source"]["boundary_output_ports"][0]["port"] += 1
    elif attack == "wrong_loop_boundary": r["source"]["loop_paths"] = [[901]]
    elif attack == "predicate_identity": r["local_v33_proof"]["normalized_local_relation"][1][1] = "invented_predicate"
    elif attack == "result_type": r["source"]["expression_result_type"] = "BOOLEAN"
    elif attack == "operand_role": r["source"]["boundary_input_ports"][0]["result_role"] = "OUTPUT"
    elif attack == "missing_internal_edge": r["source"]["internal_edges"].pop()
    elif attack == "missing_region_certificate": z["regions"] = []
    elif attack == "cycle": z["proof_dependency_graph"]["edges"].append(["indicator_evidence", "primitive_recognition"])
    elif attack == "missing_dependency": z["proof_dependency_graph"]["edges"].remove(["reaching_definitions", "region_0"])
    elif attack == "gate_as_root": z["proof_dependency_graph"]["nodes"].append({"id": "INDICATOR_EXTRACTION_COMPLETE", "kind": "ROOT"})
    elif attack == "forged_partition": z["partition"]["source_ordinary_covered"].pop()
    elif attack == "graph_type_mutation": z["source_inventory"]["nodes"][0]["datatype"] = "BOOLEAN"
    elif attack == "foreign_region_node": r["source"]["nodes"].append(z["ordinary_correspondence"][0]["source"])
    elif attack == "extra_numeric_contribution": r["boundary_semantics"]["truth_01_table"][0]["contribution"] = 1
    elif attack == "ordinary_port":
        # Exchange ordinary edge pairings, while coverage itself stays total.
        edges = {e["occurrence_id"]: e for e in z["source_inventory"]["edges"]}
        groups = {}
        for pair in z["ordinary_correspondence"]:
            if pair["source"] not in edges: continue
            e = edges[pair["source"]]
            key = repr(tuple(e[k] for k in ("kind", "operation", "category", "datatype", "operand_types", "operand_roles", "result_role")))
            groups.setdefault(key, []).append(pair)
        a, b = next(rows[:2] for rows in groups.values() if len(rows) > 1)
        a["source"], b["source"] = b["source"], a["source"]
    elif attack == "full_graph_claim": z["complete_graph_equivalence_claim"] = True
    else: raise ValueError(attack)
    return z

def negatives():
    rows = []
    for case, left, right, scope, reason, valid_local in SOURCE_NEGATIVES:
        cert = certificate(left, right, scope)
        if cert["finding"] != "UNRESOLVED" or cert.get("reason") != reason: raise RuntimeError((case, cert.get("reason")))
        if valid_local and not any(p["finding"] == "EQUIVALENT" for p in cert["local_v33_proofs"]): raise RuntimeError("local proof not preserved: " + case)
        rows.append({"case_id": case, "kind": "SOURCE_PROGRAM", "contract_form": left, "source_form": right,
            "finding": cert["finding"], "reason": reason, "valid_local_proof_retained": valid_local,
            "local_proofs": cert["local_v33_proofs"], "partition": cert["partition"]})
    good = certificate("AND", "PRODUCT", "LOCAL_PAIR_JOINT")
    for case, reason in MUTATIONS:
        attacked = mutate(good, case)
        try: check_serialized_mapping(attacked)
        except ClosureError as exc: actual = str(exc)
        else: raise RuntimeError("mutation accepted: " + case)
        if reason not in actual: raise RuntimeError((case, reason, actual))
        rows.append({"case_id": case, "kind": "SERIALIZED_EVIDENCE_MUTATION", "finding": "REJECTED", "reason": actual,
            "expected_reason": reason, "mutation_evidence": attacked})
    return rows
