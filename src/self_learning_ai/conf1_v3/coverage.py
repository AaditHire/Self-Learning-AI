"""Coverage-v3 mapping, activity, class, coverage and symmetry decisions."""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from .contracts import CoverageContractV3, input_domain_classes
from .goco import Expr, expressions_equivalent
from .interfaces import ClosureError, SchemaError, rid


def reconcile_complete_mapping(contract: CoverageContractV3,
                               occurrence_ids: Sequence[str],
                               rows: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    """V3.2 is a total, single-key mapping over task-essential occurrences."""
    contract.validate(); keys = {k.key_id for k in contract.canonical_keys}
    counts = Counter(str(row.get("occurrence_id")) for row in rows)
    if any(count != 1 for count in counts.values()): raise ClosureError("DUPLICATE_ROW")
    mapped = {str(row.get("occurrence_id")): str(row.get("canonical_contract_key_id")) for row in rows}
    if set(mapped) != set(occurrence_ids): raise ClosureError("INCOMPLETE_SOURCE_MAPPING")
    if any(key not in keys for key in mapped.values()): raise ClosureError("UNEXPECTED_CONTRACT_KEY")
    return mapped


def closed_equivalence(left: Expr, right: Expr, alpha_map: Mapping[str, str] | None = None) -> str:
    """Return a resolved catalog result; never performs general algebra."""
    try:
        return "EQUIVALENT" if expressions_equivalent(left, right, alpha_map) else "NOT_EQUIVALENT"
    except (KeyError, TypeError, ValueError):
        return "UNRESOLVED"


def behavioral_activity(evidence: Mapping[str, Any]) -> str:
    required = {"mapped_occurrence_ids", "joint_intervention_occurrence_ids", "connected_executed_paths",
                "normal_run_output_events", "ordered_intervention_attempts", "intervention_resolved"}
    if set(evidence) != required: raise SchemaError("malformed behavioral evidence")
    mapped = list(evidence["mapped_occurrence_ids"])
    if not evidence["intervention_resolved"]: return "UNRESOLVED"
    if not mapped or evidence["joint_intervention_occurrence_ids"] != mapped: return "INACTIVE"
    if not evidence["connected_executed_paths"] or not evidence["normal_run_output_events"]: return "INACTIVE"
    attempts = evidence["ordered_intervention_attempts"]
    if any(attempt.get("occurrence_ids") != mapped for attempt in attempts): return "INACTIVE"
    return "ACTIVE" if any(attempt.get("final_output_changed") is True for attempt in attempts) else "INACTIVE"


def value_or_literal_coverage(key: Mapping[str, Any], evidence: Mapping[str, Any],
                              parent_activity: str | None = None) -> str:
    kind = key.get("attribute_parent_kind")
    subtype = evidence.get("attribute_subtype")
    if subtype not in {"COMPUTED_VALUE", "LITERAL_TOKEN"}: return "UNRESOLVED"
    if kind == "ACTIVE_BEHAVIORAL_PARENT":
        if evidence.get("initial_accumulator_evidence") is not None: raise SchemaError("parent null matrix")
        if parent_activity != "ACTIVE": return "NOT_COVERED"
        parent = evidence.get("active_behavioral_parent_evidence") or {}
        necessities = ("source_location", "graph_location", "frozen_witness_case_id", "parent_path_execution_evidence")
        if any(parent.get(x) is None for x in necessities): return "NOT_COVERED"
        if subtype == "LITERAL_TOKEN" and parent.get("mapped_active_expression_reference") is None: return "NOT_COVERED"
    elif kind == "INITIAL_ACCUMULATOR":
        if evidence.get("active_behavioral_parent_evidence") is not None or evidence.get("mapped_parent_behavioral_key_id") is not None:
            raise SchemaError("fake behavioral parent for initial accumulator")
        init = evidence.get("initial_accumulator_evidence") or {}
        necessities = ("mapped_source_initialization_reference", "initialization_execution_evidence",
                       "displayed_accumulator_membership_evidence", "mapped_initialization_expression_reference")
        if any(init.get(x) is None for x in necessities): return "NOT_COVERED"
    else: raise SchemaError("unknown attribute parent kind")
    if subtype == "COMPUTED_VALUE":
        return "COVERED" if (evidence.get("computed_integer") == key.get("computed_integer") and
                             evidence.get("semantic_role") == key.get("semantic_role") and
                             evidence.get("exact_required_lexeme") is None) else "NOT_COVERED"
    return "COVERED" if (evidence.get("exact_required_lexeme") == key.get("exact_required_lexeme") and
                         evidence.get("computed_integer") is None and evidence.get("semantic_role") is None) else "NOT_COVERED"


def output_attribute_coverage(requirement_kind: str, category: str | None, sentinel: str | None,
                              cases: Sequence[Mapping[str, Any]]) -> str:
    if requirement_kind not in {"CATEGORY", "EXACT_SENTINEL"}: raise SchemaError("unknown output requirement")
    if requirement_kind == "CATEGORY" and (category not in {"OUTPUT_ZERO", "OUTPUT_POSITIVE", "OUTPUT_NEGATIVE", "OUTPUT_MULTIDIGIT"} or sentinel is not None):
        raise SchemaError("output category null rule")
    if requirement_kind == "EXACT_SENTINEL" and (category is not None or not isinstance(sentinel, str)):
        raise SchemaError("output sentinel null rule")
    for case in cases:
        if not case.get("expected_output_reference"): continue
        raw = str(case.get("expected_output_value")); match = False
        if requirement_kind == "EXACT_SENTINEL": match = raw == sentinel
        else:
            try: value = int(raw)
            except ValueError: continue
            match = {"OUTPUT_ZERO": value == 0, "OUTPUT_POSITIVE": value > 0,
                     "OUTPUT_NEGATIVE": value < 0, "OUTPUT_MULTIDIGIT": len(str(abs(value))) >= 2}[category]
        if match: return "COVERED"
    return "NOT_COVERED"


def input_domain_obligations(case_rows: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    required = {(condition, domain, label) for condition in ("ISOLATED", "COMPOSITION")
                for domain, labels in (("numeric_iteration", ("SIGN_ZERO", "SIGN_POSITIVE", "EMPTY_LOOP", "LOWER_DOMAIN_BOUNDARY")),
                                       ("array_reduction", ("NEGATIVE_PRESENT", "ZERO_PRESENT", "POSITIVE_PRESENT")))
                for label in labels}
    found = set()
    for row in case_rows:
        classes = input_domain_classes(row["domain"], row["raw_input"])
        for label in classes: found.add((row["condition"], row["domain"], label))
    return {rid("INPUT_DOMAIN_CLASS", list(item)): "PASS" if item in found else "FAIL" for item in sorted(required)}


PROTECTED_FIELDS = ("decoder", "loop", "predicates", "initialization", "outside_treatment_arithmetic", "prompt_wrapper")


def paired_symmetry(isolated: Mapping[str, Any], composition: Mapping[str, Any]) -> str:
    """V3.6 comparison: treatment expression/description and mechanical outputs are exceptions."""
    if isolated.get("case_ids") != composition.get("case_ids") or isolated.get("inputs") != composition.get("inputs"):
        return "FAIL"
    if any(isolated.get(field) != composition.get(field) for field in PROTECTED_FIELDS): return "FAIL"
    if isolated.get("feature_count") != 2 or composition.get("feature_count") != 2: return "FAIL"
    return "PASS" if isolated.get("treatment_expression") != composition.get("treatment_expression") else "FAIL"


def atomic_coverage(required_rows: Sequence[Mapping[str, Any]], evidence_rows: Sequence[Mapping[str, Any]]) -> str:
    actual = {(x.get("key_id"), x.get("condition")) for x in evidence_rows if x.get("finding") in {"ACTIVE", "COVERED"}}
    needed = {(x["key_id"], x["required_condition"]) for x in required_rows}
    return "PASS" if needed <= actual else "FAIL"
