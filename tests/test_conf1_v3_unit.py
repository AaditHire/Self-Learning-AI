"""Disposable implementation tests; these are not preregistered scientific fixtures."""
import json
from pathlib import Path

import pytest

from self_learning_ai.conf1_v3.binder import GATES, bind_gate_trace
from self_learning_ai.conf1_v3.contracts import (all_contracts, canonical_numeric_witness_slot,
                                                 numeric_training_inputs, v35_expected_row_ids)
from self_learning_ai.conf1_v3.coverage import behavioral_activity, output_attribute_coverage
from self_learning_ai.conf1_v3.goco import Parser, expressions_equivalent, parse, source_occurrence_inventory
from self_learning_ai.conf1_v3.interfaces import SchemaError, ordered_row_id_digest, rid


def ledger():
    return json.loads(Path("research/protocols/phase3c_conf1_slots.json").read_text(encoding="utf-8"))


def test_rid_and_digest_are_framed():
    assert rid("PAIR", ["a", "bc"]) == "PAIR|1:a|2:bc"
    assert ordered_row_id_digest(["a", "b"]) == "bffefdaf121fcb64af95997beee43289ca54128c85c2565d6550f9d69d2e9eb1"


def test_contract_population_is_prospective():
    contracts = all_contracts(ledger())
    assert len(contracts) == 184
    assert len(v35_expected_row_ids(contracts)) == len(set(v35_expected_row_ids(contracts)))


def test_one_slot_rule():
    frozen = ledger(); canonical = canonical_numeric_witness_slot(frozen)
    assert canonical == "CONF1-TR-NU-01-V0"
    values = numeric_training_inputs(frozen, canonical)
    assert len(values) == 5 and values.count("0") == 1
    other = next(x["slot_id"] for x in frozen["slots"]["training_paired_slots"]
                 if x["family"] == "numeric_iteration" and x["slot_id"] != canonical)
    assert "0" not in numeric_training_inputs(frozen, other)


def test_closed_parser_and_occurrences():
    source = "NUMBER n. INPUT(n). NUMBER total=0. LOOP (NUMBER i=1 TILL i<=n, i++) { total+=i. } DISPLAYNL(total)."
    assert len(parse(source)) == 5
    inventory = source_occurrence_inventory("TOY", source)
    assert inventory["nodes"] and len({x["occurrence_id"] for x in inventory["nodes"]}) == len(inventory["nodes"])
    with pytest.raises(SchemaError): parse("WHILE (true) { DISPLAYNL(0). }")


def test_closed_equivalence_catalog():
    left = Parser("a+b").expr(); right = Parser("y+x").expr()
    assert expressions_equivalent(left, right, {"a": "x", "b": "y"})
    reassociated = Parser("(a+b)+c").expr(); other = Parser("a+(b+c)").expr()
    assert not expressions_equivalent(reassociated, other)


def test_joint_intervention_required():
    base = {"mapped_occurrence_ids": ["a", "b"], "joint_intervention_occurrence_ids": ["a", "b"],
            "connected_executed_paths": [1], "normal_run_output_events": [1],
            "ordered_intervention_attempts": [{"occurrence_ids": ["a", "b"], "final_output_changed": True}],
            "intervention_resolved": True}
    assert behavioral_activity(base) == "ACTIVE"
    base["joint_intervention_occurrence_ids"] = ["a"]
    assert behavioral_activity(base) == "INACTIVE"


def test_output_attribute_uses_expected_output_reference():
    assert output_attribute_coverage("CATEGORY", "OUTPUT_ZERO", None,
                                     [{"expected_output_reference": "r", "expected_output_value": "0"}]) == "COVERED"
    assert output_attribute_coverage("CATEGORY", "OUTPUT_ZERO", None,
                                     [{"expected_output_reference": None, "expected_output_value": "0"}]) == "NOT_COVERED"


def test_gate_trace_is_ordered_and_not_aggregate_only():
    trace = [{"gate": gate, "executed": True, "status": "PASS", "input_evidence_references": ["i"],
              "output_evidence_references": ["o"], "verified_row_counts": {"rows": 1},
              "scientific_reason_codes": []} for gate in GATES]
    assert bind_gate_trace(trace) == "PASS"
    with pytest.raises(Exception): bind_gate_trace(trace[::-1])
