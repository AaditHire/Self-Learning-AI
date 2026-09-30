"""Population guard tests, not Coverage-v3 scientific classification."""
from dataclasses import replace
import json

import pytest

import conf1_core_development_inputs as dev

# Before collection imports any Coverage-v3 code.
OVERLAP = dev.assert_zero_historical_overlap()

from self_learning_ai.conf1_v3.contracts import all_contracts, v35_expected_row_ids
from self_learning_ai.conf1_v3.interfaces import SchemaError, rid
from test_conf1_v3_unit import toy_contract


@pytest.fixture
def disposable_contract():
    return toy_contract(dev.CLOSURE_SOURCE, dev.CLOSURE_PROGRAM_ID)


@pytest.fixture(scope="module")
def frozen_contracts():
    # Pure source-template lowering only, no candidate/case selection or run.
    ledger = json.loads((dev.ROOT / "research/protocols/phase3c_conf1_slots.json").read_bytes())
    return all_contracts(ledger)


def test_empty_inventory_cannot_be_authoritative():
    with pytest.raises(SchemaError, match="V3_5_POPULATION_UNRESOLVED"):
        v35_expected_row_ids([])
    assert v35_expected_row_ids([], diagnostic_incomplete=True) == []


def test_partial_or_toy_inventory_cannot_be_authoritative(disposable_contract):
    with pytest.raises(SchemaError, match="missing or unexpected"):
        v35_expected_row_ids([disposable_contract])


def test_duplicate_program_rejected_even_in_diagnostic_mode(disposable_contract):
    with pytest.raises(SchemaError, match="duplicate contract program"):
        v35_expected_row_ids([disposable_contract, disposable_contract], diagnostic_incomplete=True)


@pytest.mark.parametrize("value", [1, "false", None])
def test_diagnostic_flag_must_be_actual_boolean(disposable_contract, value):
    with pytest.raises(SchemaError, match="actual boolean"):
        v35_expected_row_ids([disposable_contract], diagnostic_incomplete=value)


def test_duplicate_key_rejected_before_row_generation(disposable_contract):
    malformed = replace(disposable_contract, canonical_keys=(*disposable_contract.canonical_keys,
                                                           disposable_contract.canonical_keys[0]))
    with pytest.raises(SchemaError, match="unique"):
        v35_expected_row_ids([malformed], diagnostic_incomplete=True)


def test_orphan_occurrence_rejected(disposable_contract):
    mapping = dict(disposable_contract.key_occurrences)
    mapping[next(iter(mapping))] = ("DEV-CLOSURE-UNKNOWN-OCCURRENCE-20260930",)
    malformed = replace(disposable_contract, key_occurrences=mapping)
    with pytest.raises(SchemaError, match="unknown prospective key occurrence"):
        v35_expected_row_ids([malformed], diagnostic_incomplete=True)


def test_missing_obligation_inventory_rejected(disposable_contract):
    mapping = dict(disposable_contract.key_occurrences)
    mapping.pop(next(iter(mapping)))
    with pytest.raises(SchemaError, match="inventory incomplete"):
        v35_expected_row_ids([replace(disposable_contract, key_occurrences=mapping)], diagnostic_incomplete=True)


def test_rows_are_framed_without_observed_findings_and_utf8_ordered(disposable_contract):
    rows = v35_expected_row_ids([disposable_contract], diagnostic_incomplete=True)
    # A development contract is deliberately not part of the training universe.
    assert rows == []
    training_toy = replace(disposable_contract, task_kind="training", core_gaps=("DISPOSABLE_INCOMPLETE",))
    rows = v35_expected_row_ids([training_toy], diagnostic_incomplete=True)
    assert rows == sorted((rid("V3.5", [training_toy.program_id, k.key_id])
                           for k in training_toy.canonical_keys), key=lambda r: r.encode("utf-8"))


def test_shrinking_frozen_inventory_cannot_be_authoritative(frozen_contracts):
    with pytest.raises(SchemaError, match="missing or unexpected"):
        v35_expected_row_ids(frozen_contracts[:-1])


def test_relabeling_frozen_inventory_as_development_cannot_bypass_gate(frozen_contracts):
    altered = [replace(c, task_kind="development", core_gaps=()) for c in frozen_contracts]
    with pytest.raises(SchemaError, match="metadata mismatch"):
        v35_expected_row_ids(altered)


def test_frozen_incompleteness_still_blocks_and_diagnostics_reorder_stably(frozen_contracts):
    with pytest.raises(SchemaError, match="V3_5_POPULATION_UNRESOLVED"):
        v35_expected_row_ids(frozen_contracts)
    assert v35_expected_row_ids(frozen_contracts, diagnostic_incomplete=True) == v35_expected_row_ids(
        list(reversed(frozen_contracts)), diagnostic_incomplete=True)


def test_persisted_overlap_artifact_precedes_execution():
    path = dev.ROOT / "research/implementation_notes/coverage_v3_core_closure/disposable_overlap.json"
    artifact = json.loads(path.read_bytes())
    assert {key: artifact[key] for key in OVERLAP} == OVERLAP
    assert artifact["inventory"] == dev.disposable_inventory()
    assert artifact["computed_historical_string_hash_overlap"] == 0
    assert not artifact["expected_labels_loaded"]


def test_partial_derivation_reconstructs_only_diagnostic_rows(frozen_contracts):
    path = dev.ROOT / "research/implementation_notes/coverage_v3_core_closure/partial_derivation.json"
    artifact = json.loads(path.read_bytes())
    catalog = {row["catalog_record"]: row["canonical_key"] for row in artifact["provisional_key_catalog"]}
    reconstructed = []
    for contract in artifact["contracts"]:
        assert contract["core_gaps"]
        for obligation in contract["provisional_obligations"]:
            assert obligation["authoritative_expected_row_id"] is None
            assert obligation["occurrence_source_spans"]
            identity = obligation["diagnostic_row_identity"]
            if identity is not None:
                reconstructed.append(rid(identity["label"], [identity["program_id"],
                    catalog[identity["key_catalog_record"]]["key_id"]]))
        for absent in contract["required_primitive_roles"]:
            assert absent["canonical_contract_key_id"] is None
            assert absent["expected_v3_5_row_id"] is None
            assert len(absent["authority_trace"]) == 4
    assert len(reconstructed) == len(set(reconstructed))
    assert sorted(reconstructed, key=lambda r: r.encode("utf-8")) == v35_expected_row_ids(
        frozen_contracts, diagnostic_incomplete=True)
    assert not artifact["authoritative"] and not artifact["contains_expected_row_index"]
    assert artifact["summary"]["authoritative_v3_5_rows"] is None
    assert len(artifact["input_domain_classes"]["ordered_diagnostic_row_ids"]) == 14


def test_unresolved_inventory_has_no_population_success_claim(frozen_contracts):
    path = dev.ROOT / "research/implementation_notes/coverage_v3_core_closure/unresolved_obligations.json"
    artifact = json.loads(path.read_bytes())
    expected = {(c.program_id, gap) for c in frozen_contracts for gap in c.core_gaps}
    actual = [(row["program_id"], row["code"]) for row in artifact["contract_gaps"]]
    assert set(actual) == expected and len(actual) == len(expected)
    assert artifact["population_status"] == "V3_5_POPULATION_UNRESOLVED"
    assert artifact["authoritative_v3_5_rows"] is None
    assert artifact["not_a_claim_of_authority_contradiction"]
    assert not artifact["delegated_phase_started"]
