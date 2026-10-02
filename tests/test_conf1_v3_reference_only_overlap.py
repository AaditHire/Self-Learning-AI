"""Prospective RO fixture-overlap policy tests; all collisions here synthetic.

The real historical comparison is a separately recorded preflight, never a
source of test constants. These tests do not establish RO semantic readiness.
"""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import re

import pytest

from self_learning_ai.conf1_v3 import reference_only_overlap as ro

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "research/implementation_notes/coverage_v3_reference_only_implementation" / ro.SCHEDULE_NAME


@pytest.fixture
def saved():
    return ro.load_schedule(SCHEDULE)


def synthetic(value, kind="VALUE", pointer="/test/value"):
    return ro.CorpusString("DEVELOPMENT_ONLY_SYNTHETIC_OVERLAP_METADATA.json", pointer, kind, value)


def result_for(row, saved):
    return ro.compare([row], saved, [synthetic(row["value"])])


def test_exact_serialized_schedule_and_independent_derivation(saved):
    assert saved.payload == ro.canonical(ro.witness_schedule())
    assert len(saved.value()["non_boundary"]) == 43
    assert len(saved.value()["boundaries"]) == 3
    assert saved.sha256_utf8 == "e8720d7196bbbf4d166ecc7b72388287ad455ec0718d6ee2a60207a794983198"
    for r in saved.value()["non_boundary"]:
        h = ro.digest(ro.SEED + "|" + r["label"])
        assert r["digest"] == h
        assert r["literal"] == str(r["low"] + int(h, 16) % (r["high"] - r["low"] + 1))
        assert r["sha256_utf8"] == ro.digest(r["literal"])
        assert r["literal"] not in ("2", "8")


@pytest.mark.parametrize("index,admitted", [(0, True), (1, True), (2, False)])
def test_normative_token_boundary_behavior(saved, index, admitted):
    # Actually test the corresponding frozen N token/bound behavior. This is
    # not a constant-tree certificate or compiler-agreement claim.
    r = saved.value()["boundaries"][index]
    grammar = re.fullmatch(r"0|[1-9][0-9]{0,9}", r["literal"], flags=re.ASCII)
    assert bool(grammar and int(r["literal"]) <= 2147483647) is admitted
    assert ro.digest(r["literal"]) == r["sha256_utf8"]


@pytest.mark.parametrize("index", range(3))
def test_exact_boundary_collision_only(saved, index):
    r = result_for(ro.scheduled_inventory(saved)[index], saved)
    assert r["status"] == "PASS"
    assert r["permitted_collision_count"] == 1
    assert r["prohibited_collisions"] == []
    assert r["permitted_normative_collisions"][0]["match_location_count"] == 1


@pytest.mark.parametrize("field", ["sources", "raw_inputs", "expected_outputs", "task_text", "prompt", "case_data", "program_id", "metadata", "candidate_artifact", "scientific_row", "model_input", "model_output"])
def test_zero_wrong_field_cannot_borrow_ro_exception(saved, field):
    row = ro.scheduled_inventory(saved)[0]
    row["field"] = field
    r = result_for(row, saved)
    assert r["status"] == "STOP"
    assert r["permitted_normative_collisions"] == []
    assert r["prohibited_collision_count"] == 1


@pytest.mark.parametrize("change", [
    {"boundary_rule": "FROZEN_CANONICAL_ZERO_OUTPUT"},
    {"boundary_rule": "FROZEN_RO_INTEGER_MAX_BOUNDARY"},
    {"sha256_utf8": ro.BOUNDARIES[1][2]},
    {"value": "2147483647"},
    {"path": "metadata/0/literal"},
    {"development_case_id": "DEVELOPMENT_ONLY_RO_DIFFERENT_CASE"},
    {"scope": "SCIENTIFIC"},
    {"implementation_test": "VALUE_OUTPUT"},
])
def test_forged_reason_hash_literal_path_scope_or_case_reject(saved, change):
    row = ro.scheduled_inventory(saved)[0]
    row.update(change)
    r = result_for(row, saved)
    assert r["status"] == "STOP"
    assert r["permitted_normative_collisions"] == []


@pytest.mark.parametrize("value", ["2", "8", "1", "987654321"])
def test_other_numeric_collision_is_prohibited_despite_caller_flags(saved, value):
    row = ro.scheduled_inventory(saved)[0]
    row.update(value=value, sha256_utf8=ro.digest(value), normative=True)
    r = result_for(row, saved)
    assert r["prohibited_collision_count"] == 1
    assert r["permitted_collision_count"] == 0
    with pytest.raises(ro.OverlapIssue, match="PROHIBITED_RO_OVERLAP"):
        ro.require_clear(r)


def test_metadata_removal_change_and_collisions_cannot_resample(saved):
    before = ro.canonical(ro.witness_schedule())
    rows = ro.scheduled_inventory(saved)
    assert ro.compare(rows, saved, [])["status"] == "PASS"
    colliding = [synthetic(r["value"]) for r in rows]
    r = ro.compare(rows, saved, colliding)
    assert r["prohibited_collision_count"] == 43
    assert r["permitted_collision_count"] == 3
    with pytest.raises(ro.OverlapIssue):
        ro.require_clear(r)
    assert before == ro.canonical(ro.witness_schedule()) == saved.payload == SCHEDULE.read_bytes()
    ro.compare(rows, saved, [synthetic("different protected metadata")])
    assert before == ro.canonical(ro.witness_schedule())
    with pytest.raises(TypeError):
        ro.witness_schedule(protected_metadata=colliding)


def test_all_exact_and_hash_locations_retained(saved):
    row = ro.scheduled_inventory(saved)[0]
    corpus = [synthetic("0", pointer="/first"), synthetic("0", "KEY", "/second"),
              synthetic(row["sha256_utf8"], pointer="/recorded_hash")]
    r = ro.compare([row], saved, corpus)
    locations = r["permitted_normative_collisions"][0]["match_locations"]
    assert len(locations) == 3
    assert locations[0]["match_modes"] == ["EXACT_STRING", "RECOMPUTED_STRING_HASH"]
    assert locations[2]["match_modes"] == ["RECORDED_HASH"]


def test_schedule_must_exist_and_validate_before_corpus_query(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(ro, "load_raw_corpus", lambda root: (calls.append("CORPUS_READ") or (), []))
    missing = tmp_path / ro.SCHEDULE_NAME
    with pytest.raises(FileNotFoundError):
        ro.preflight(ROOT, missing)
    assert calls == []
    # Mechanical generated test data, not a fixture selection after a query.
    missing.write_bytes(ro.canonical(ro.witness_schedule()))
    original = ro.load_schedule
    def traced(path):
        out = original(path)
        calls.append("SCHEDULE_VERIFIED")
        return out
    monkeypatch.setattr(ro, "load_schedule", traced)
    r = ro.preflight(ROOT, missing)
    assert calls == ["SCHEDULE_VERIFIED", "CORPUS_READ"]
    assert [e["event"] for e in r["causal_sequence"]] == ["SERIALIZED_SCHEDULE_VERIFIED", "PROTECTED_RAW_CORPUS_READ_STARTED"]
    assert r["causal_sequence"][0]["time_unix_ns"] <= r["causal_sequence"][1]["time_unix_ns"]


def test_changed_serialized_schedule_and_forged_snapshot_reject(saved, tmp_path):
    value = saved.value()
    value["non_boundary"][0]["literal"] = "987654321"
    p = tmp_path / ro.SCHEDULE_NAME
    p.write_bytes(ro.canonical(value))
    with pytest.raises(ro.OverlapIssue, match="SCHEDULE_CHANGED"):
        ro.load_schedule(p)
    with pytest.raises(ro.OverlapIssue, match="FORGED_SCHEDULE"):
        ro.boundary_permitted(ro.scheduled_inventory(saved)[0], replace(saved, payload=ro.canonical(value)))
    detached = saved.value()
    detached["boundaries"].clear()
    assert len(saved.value()["boundaries"]) == 3


def test_real_scan_provenance_and_no_schedule_mutation(monkeypatch, saved):
    calls = []
    def fake_loader(root):
        calls.append(saved.path.read_bytes())
        return (synthetic("0"),), [dict(path="DEVELOPMENT_ONLY_SYNTHETIC_METADATA")]
    monkeypatch.setattr(ro, "load_raw_corpus", fake_loader)
    r = ro.preflight(ROOT, saved.path)
    assert calls == [saved.payload]
    assert r["schedule_existed_before_scan"]
    assert not r["expected_labels_parsed"]
    assert not r["scientific_overlap_permissions_changed"]
    assert not r["value_output_exception_imported"]
    assert not r["resampling_occurred"]
    assert ro.scheduled_inventory(saved) == r["inventory"]


def test_raw_walk_keeps_keys_duplicate_values_and_escaped_paths():
    rows = list(ro._raw_strings({"a/b": ["value", "value"], "t~k": "other"}, "DEV_ONLY.json"))
    assert [(r.json_pointer, r.kind) for r in rows] == [
        ("/a~1b", "KEY"), ("/a~1b/0", "VALUE"), ("/a~1b/1", "VALUE"),
        ("/t~0k", "KEY"), ("/t~0k", "VALUE")]
