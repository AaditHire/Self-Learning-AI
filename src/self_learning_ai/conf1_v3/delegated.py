"""Closed E1--E6 population and scientific decision helpers."""

from __future__ import annotations

import itertools
from collections import Counter
from typing import Any, Mapping, Sequence

from .interfaces import ClosureError, SchemaError, reconcile_rows, rid


def _unique(rows: Sequence[Mapping[str, Any]], key: str = "row_id") -> None:
    values = [row.get(key) for row in rows]
    if any(not isinstance(x, str) or not x for x in values): raise SchemaError("row ID missing")
    if len(values) != len(set(values)): raise ClosureError("DUPLICATE_ROW")


def e1_reference_validation(program_rows: Sequence[Mapping[str, Any]], expected_program_ids: Sequence[str],
                            compiler_identity_id: str, expected_compiler_identity_id: str) -> str:
    _unique(program_rows)
    if compiler_identity_id != expected_compiler_identity_id: return "FAIL"
    if {r.get("program_id") for r in program_rows} != set(expected_program_ids): return "FAIL"
    for row in program_rows:
        cases = row.get("cases", [])
        if len(cases) != 5 or len({c.get("case_id") for c in cases}) != 5: return "FAIL"
        if row.get("compile_status") != "PASS" or any(c.get("semantic_status") != "PASS" for c in cases): return "FAIL"
    return "PASS"


def shared_pair_ids(candidate_ids: Sequence[str], consumed_ids: Sequence[str]) -> list[str]:
    return [rid("PAIR", [candidate, consumed]) for candidate in candidate_ids for consumed in consumed_ids]


def pair_population(rows: Sequence[Mapping[str, Any]], candidate_ids: Sequence[str], consumed_ids: Sequence[str]) -> str:
    actual = [r.get("pair_id") for r in rows]; expected = shared_pair_ids(candidate_ids, consumed_ids)
    return "PASS" if len(actual) == len(set(actual)) and set(actual) == set(expected) else "FAIL"


def e2_ast_decision(classification: str) -> str:
    if classification == "PROHIBITED_STRUCTURAL_TEMPLATE_REUSE": return "FAIL"
    if classification in {"COARSE_AST_EQUALITY_ONLY", "STRUCTURALLY_DISTINCT"}: return "PASS"
    return "UNRESOLVED"


def e3_scaffold(rows: Sequence[Mapping[str, Any]], expected_slot_ids: Sequence[str]) -> str:
    return "PASS" if ({r.get("slot_id") for r in rows} == set(expected_slot_ids) and
                       len(rows) == len(expected_slot_ids) and all(r.get("status") == "PASS" for r in rows)) else "FAIL"


def e3_token(rows: Sequence[Mapping[str, Any]], expected_example_ids: Sequence[str], limit: int = 320) -> str:
    if {r.get("example_id") for r in rows} != set(expected_example_ids) or len(rows) != len(expected_example_ids): return "FAIL"
    return "PASS" if all(not r.get("truncated") and (not r.get("limit_applicable") or r.get("serialized_token_count", limit + 1) <= limit) for r in rows) else "FAIL"


def e3_schedule(cell_rows: Sequence[Mapping[str, Any]], exposure_rows: Sequence[Mapping[str, Any]],
                step_rows: Sequence[Mapping[str, Any]], expected: tuple[int, int, int] = (10, 1800, 240)) -> str:
    for rows in (cell_rows, exposure_rows, step_rows): _unique(rows)
    if tuple(map(len, (cell_rows, exposure_rows, step_rows))) != expected: return "FAIL"
    return "PASS" if all(r.get("status") == "PASS" for rows in (cell_rows, exposure_rows, step_rows) for r in rows) else "FAIL"


def e4_exact_overlap(row: Mapping[str, Any]) -> str:
    if row.get("classification") in {"EXACT_OVERLAP", "NORMALIZED_SOURCE_OVERLAP", "FULL_TEMPLATE_OVERLAP"}: return "FAIL"
    if row.get("classification") == "ALLOWED": return "PASS"
    return "UNRESOLVED"


def complete_contribution_vector(k: int, values: Sequence[int]) -> bool:
    return 0 <= k <= 4 and len(values) == 2 ** k and all(isinstance(x, int) and not isinstance(x, bool) for x in values)


def validate_e5_certificate(cert: Mapping[str, Any]) -> str:
    k = cert.get("role_count"); vector = cert.get("contribution_vector", [])
    if not isinstance(k, int) or not complete_contribution_vector(k, vector): return "UNRESOLVED"
    if cert.get("hidden_or_unrepresented_state") is not False: return "UNRESOLVED"
    needed = ("typed_complete_graph_identity", "aggregation_state_recurrence", "initialization_state",
              "source_contract_completeness")
    return "PASS" if all(cert.get(x) is not None for x in needed) else "UNRESOLVED"


def e5_compare(primary: Mapping[str, Any], training: Mapping[str, Any], comparison: Mapping[str, Any]) -> str:
    if validate_e5_certificate(primary) != "PASS" or validate_e5_certificate(training) != "PASS": return "UNRESOLVED"
    kp, kt = primary["role_count"], training["role_count"]
    if kp != kt: return "NONMATCH"  # includes frozen fewer-role motif resolution
    bijections = comparison.get("role_bijections")
    if not isinstance(bijections, list) or len(bijections) != _factorial(kp): return "UNRESOLVED"
    graph_collision = any(x.get("graph_isomorphic") is True for x in bijections)
    semantic_collision = any(x.get("semantic_signature_equal") is True for x in bijections)
    return "COLLISION" if graph_collision or semantic_collision else "NONMATCH"


def _factorial(value: int) -> int:
    result = 1
    for n in range(2, value + 1): result *= n
    return result


def e5_population(primary: Sequence[Mapping[str, Any]], training: Sequence[Mapping[str, Any]],
                  comparisons: Sequence[Mapping[str, Any]], expected: tuple[int, int, int] = (32, 120, 3840)) -> str:
    for rows in (primary, training, comparisons): _unique(rows)
    if tuple(map(len, (primary, training, comparisons))) != expected: return "FAIL"
    if any(validate_e5_certificate(x) != "PASS" for x in (*primary, *training)): return "UNRESOLVED"
    return "FAIL" if any(x.get("final_result") == "COLLISION" for x in comparisons) else "PASS"


def e6(task_rows: Sequence[Mapping[str, Any]], pair_rows: Sequence[Mapping[str, Any]],
       task_ids: Sequence[str], domain_primary_ids: Mapping[str, Sequence[str]]) -> str:
    _unique(task_rows); _unique(pair_rows)
    if {r.get("task_id") for r in task_rows} != set(task_ids): return "FAIL"
    for row in task_rows:
        cases = row.get("cases", []); witnesses = row.get("behavior_witnesses", [])
        if len(cases) != 5 or len({x.get("case_id") for x in cases}) != 5 or not witnesses: return "FAIL"
        if any(x.get("status") != "PASS" for x in (*cases, *witnesses)): return "FAIL"
    expected = {rid("E6_PAIR", [domain, a, b]) for domain, ids in domain_primary_ids.items()
                for a, b in itertools.combinations(ids, 2)}
    actual = {r.get("row_id") for r in pair_rows if r.get("status") == "PASS" and r.get("observed_difference") is not None}
    return "PASS" if actual == expected and len(pair_rows) == len(expected) else "FAIL"
