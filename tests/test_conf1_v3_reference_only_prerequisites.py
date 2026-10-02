"""Partial foundation checks, NOT REFERENCE_ONLY implementation readiness.

Disposable predetermined sources only. The constructor guard is deliberately
tested as rejection, not weakened to turn retained dependency evidence into a
new prospective requirement. No compiler/scientific producer is invoked.
"""
from copy import deepcopy
from pathlib import Path

import pytest

from self_learning_ai.conf1_v3.interfaces import ClosureError, canonical_json_bytes
from self_learning_ai.conf1_v3.reference_only_context import (
    PreDispositionMappingContextV1, build_pre_context, prior_bindings,
    prospective_structure, required_selector_audit,
)
from self_learning_ai.conf1_v3.reference_only_development import fixture_plan, executable_overlap_inventory
from self_learning_ai.conf1_v3.reference_only_inventory import source_inventory, ref
from self_learning_ai.conf1_v3.reference_only_kernel import constant_tree, parse_expression, ConstantIssue
from self_learning_ai.conf1_v3.reference_only_overlap import load_schedule, load_raw_corpus, compare, require_clear
from self_learning_ai.conf1_v3.reference_only_state import state_record

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def checked_sources():
    saved = load_schedule(ROOT / "research/implementation_notes/coverage_v3_reference_only_implementation/predetermined_witness_schedule.json")
    fixtures = fixture_plan()
    inventory = executable_overlap_inventory(fixtures)
    corpus, _ = load_raw_corpus(ROOT)
    require_clear(compare(inventory, saved, corpus))
    return fixtures


def inputs(f):
    p, inv, graph = source_inventory(f["program_id"], f["source"],
        ref("DEVELOPMENT_ONLY_INPUT", f["development_case_id"], "SOURCE", f["source"]),
        training=f["program_group"] == "TRAINING")
    state, diagnostic = state_record(p, inv, graph, direct_artifact_id="DEVELOPMENT_ONLY_DIRECT")
    return p, inv, graph, state, diagnostic


@pytest.mark.parametrize("group", ["TRAINING", "PRIMARY_EVALUATION", "PRIMITIVE_SANITY", "STRUCTURAL_TRANSFER"])
def test_full_dependency_retention_does_not_authorize_head_selector(group, checked_sources):
    f = next(f for f in checked_sources if f["program_group"] == group and f["variant"] == "BASE")
    c = prospective_structure(f["prospective"])
    bindings = prior_bindings(f["prospective"], c)
    footprint = {oid for b in bindings for oid in b["contract_occurrences"]}
    footprint.update(e["occurrence_id"] for b in bindings for e in b["dependency_edges"])
    # This passes: a missing raw dependency inventory is NOT the blocker.
    assert footprint == {i.occurrence_id for i in c.items}
    unsupported = required_selector_audit(f["prospective"], c, bindings)
    assert unsupported
    assert all(r["proposed_dependency_occurrence_id"] != r["selected_requirement_occurrence_id"] for r in unsupported)
    assert any(r["selected_kind"] == "NODE" and r["proposed_kind"] == "EDGE" for r in unsupported)
    # The positive complete source has no surplus RO syntax. Even here the
    # footprint-as-selector adapter must not manufacture a CLOSED context.
    p, inv, graph, state, _ = inputs(f)
    original = canonical_json_bytes([f["prospective"], inv, graph, state])
    with pytest.raises(ClosureError, match="DEPENDENCY_IS_NOT_REQUIRED_SELECTOR"):
        build_pre_context(f["prospective"], p, inv, graph, state,
            ref("DEVELOPMENT_ONLY_CONTRACT", "DEVELOPMENT_ONLY_CONTRACT_RECORD", "COVERAGE_CONTRACT"),
            direct_artifact_id="DEVELOPMENT_ONLY_DIRECT")
    assert canonical_json_bytes([f["prospective"], inv, graph, state]) == original


def test_concrete_input_node_vs_decoder_edge_counterexample(checked_sources):
    f = next(f for f in checked_sources if f["program_group"] == "TRAINING" and f["variant"] == "BASE")
    c = prospective_structure(f["prospective"])
    audit = required_selector_audit(f["prospective"], c, prior_bindings(f["prospective"], c))
    assert any(r["selected_operation"] == "INPUT" and r["selected_kind"] == "NODE"
               and r["proposed_operation"] == "INPUT_TO_DECODER" and r["proposed_kind"] == "EDGE" for r in audit)


def test_raw_false_body_and_reaching_definitions_retained(checked_sources):
    f = next(f for f in checked_sources if f["program_group"] == "TRAINING"
             and f["variant"] == "FALSE_REQUIRED_ACCUMULATOR_EXTRA")
    p, inv, graph, state, diagnostic = inputs(f)
    ids = [r["occurrence"]["occurrence_id"] for r in inv["occurrences"]]
    assert set(ids) == set(graph["node_ids"]) | set(graph["edge_ids"])
    assert len(ids) == len(set(ids))
    assert [r["inventory_ordinal"] for r in inv["occurrences"]] == list(range(1, len(ids) + 1))
    assert inv["eligible_v3_5_occurrence_ids"] == ids
    extra_writer = next(w for w in diagnostic["writes"] if w["binding"] == "rototal"
                        and p.item(w["writer"]).location[0] > f["source"].rfind("IF ("))
    assert any(d["writer_occurrence_id"] == extra_writer["writer"] for d in state["definitions"])
    assert any(e["source_occurrence_id"] == extra_writer["writer"] and e["relation"] == "MAY_REACHING"
               for e in state["dependency_edges"])
    assert extra_writer["writer"] in state["output_ancestry"]


def test_snapshot_bytes_do_not_alias_returned_value():
    original = {"schema_version": 1, "values": [{"nested": []}]}
    sealed = PreDispositionMappingContextV1(canonical_json_bytes(original))
    returned = sealed.value()
    returned["values"][0]["nested"].append("DEVELOPMENT_ONLY_MUTATION")
    original["values"].clear()
    assert sealed.value() == {"schema_version": 1, "values": [{"nested": []}]}


@pytest.mark.parametrize("literal,admitted", [("0", True), ("2147483647", True), ("2147483648", False)])
def test_exact_scheduled_boundary_kernel(literal, admitted):
    saved = load_schedule(ROOT / "research/implementation_notes/coverage_v3_reference_only_implementation/predetermined_witness_schedule.json")
    assert literal in [b["literal"] for b in saved.value()["boundaries"]]
    if admitted:
        tree = constant_tree(parse_expression(literal))
        assert tree.integer_value == int(literal)
        assert len(tree.postorder) == 1
    else:
        with pytest.raises(ConstantIssue, match="RO_PARTIAL_OR_NONEXACT_EVALUATION"):
            constant_tree(parse_expression(literal))


def test_nested_constant_preserves_original_postorder(checked_sources):
    f = next(f for f in checked_sources if f["variant"] == "NESTED_CONSTANT")
    expression = parse_expression(f["semantic_constant_witness"])
    tree = constant_tree(expression)
    assert tree.postorder[-1].expression is expression
    assert tree.postorder[-1].operation == "GROUP"
    assert [r.operation for r in tree.postorder] == ["CONSTANT", "CONSTANT", "ADD", "GROUP", "CONSTANT", "MUL", "CONSTANT", "SUB", "GROUP"]

