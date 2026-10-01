"""Proof-backed production bridge on only new disposable data."""
from copy import deepcopy
import json
import pytest
import ct903_inputs as d
PREFLIGHT = d.overlap()
from ct903_runtime import contract, certificate, engine
from ct903_adversarial import MUTATIONS, SOURCE_NEGATIVES, base_bundle, mutate
from self_learning_ai.conf1_v3.coverage import reconcile_complete_mapping
from self_learning_ai.conf1_v3.contract_ir import graph_record
from self_learning_ai.conf1_v3.interfaces import ClosureError, canonical_json_bytes
from self_learning_ai.conf1_v3.transport_verifier import verify_canonical_transport, verify_mapping_proof_record

@pytest.mark.parametrize("left,right,scope", d.PAIRS)
def test_positive_production_bridge(tmp_path, left, right, scope):
    e = engine(tmp_path, left, right, scope); m = e.mapping
    before = canonical_json_bytes(graph_record(m.program))
    bundle = json.loads(json.dumps(m.semantic_transport))
    checked = verify_canonical_transport(bundle)
    assert checked["finding"] == "VERIFIED_CANONICAL_TRANSPORT"
    assert verify_mapping_proof_record(bundle, m.to_record())["key_resolution_recomputed"]
    m.validate()
    activity = e.semantic_activity()
    assert len(activity["records"]) == 1 and activity["records"][0]["finding"] == "ACTIVE"
    row = activity["records"][0]
    assert row["semantic_key_id"] == bundle["transports"][0]["semantic_key_id"]
    assert len(row["raw_source_activity_evidence"]["raw_occurrences"]) == (2 if left.startswith("REPEATED") else 1)
    raw_op = "MUL" if scope == "LOCAL_PAIR_JOINT" else "GT"
    assert all(i["operation"] == raw_op for i in row["raw_source_activity_evidence"]["raw_destinations"])
    assert canonical_json_bytes(graph_record(m.program)) == before
    assert not m.to_record()["raw_graph_equality_claim"]
    assert {r["method"] for r in m.raw_key_resolution} <= {
        "DIRECT_TYPED_CORRESPONDENCE", "VERIFIED_REGIONAL_SEMANTIC_TRANSPORT", "UNRESOLVED_DISTINCT_RAW_REQUIREMENT"}
    if scope == "LOCAL_PAIR_JOINT":
        key = next(k for k in m.contract.canonical_keys if k.operation == "AND")
        with pytest.raises(ClosureError, match="UNSATISFIED_DISTINCT_RAW_KEY"): e.behavioral(key.key_id)
    else:
        key = next(k for k in m.contract.canonical_keys if k.operation == "OR")
        assert e.behavioral(key.key_id)["finding"] == "ACTIVE"
        assert next(r for r in m.raw_key_resolution if r["key_id"] == key.key_id)["method"] == "VERIFIED_REGIONAL_SEMANTIC_TRANSPORT"

@pytest.mark.parametrize("left,right,scope", d.PAIRS[:2])
def test_raw_and_realization_activity_identity_common(tmp_path, left, right, scope):
    a, b = tmp_path / "boolean", tmp_path / "numeric"; a.mkdir(); b.mkdir()
    reference = engine(a, left, left, scope).semantic_activity()["records"][0]
    realization = engine(b, left, right, scope).semantic_activity()["records"][0]
    assert reference["semantic_key_id"] == realization["semantic_key_id"]
    assert reference["activity_identity"] == realization["activity_identity"]
    assert reference["raw_source_activity_evidence"]["raw_destinations"][0]["operation"] != realization["raw_source_activity_evidence"]["raw_destinations"][0]["operation"]

@pytest.mark.parametrize("attack,reason", MUTATIONS)
def test_independent_transport_mutations(attack, reason):
    bundle = base_bundle(attack == "foreign_region")
    attacked = mutate(bundle, attack)
    with pytest.raises(ClosureError, match=reason): verify_canonical_transport(attacked)
    left = "REPEATED_AND" if attack == "foreign_region" else "AND"
    with pytest.raises(ClosureError, match=reason):
        reconcile_complete_mapping(contract(left), bundle["total_mapping_certificate"]["source_inventory"]["source"], transport_evidence=attacked)

@pytest.mark.parametrize("case,left,right,scope,reason", SOURCE_NEGATIVES)
def test_source_semantics_cannot_merge(case, left, right, scope, reason):
    cert = certificate(left, right, scope)
    assert cert["finding"] == "UNRESOLVED" and cert["reason"] == reason
    with pytest.raises(ClosureError, match="COMPLETE_MAPPING_REQUIRED"):
        reconcile_complete_mapping(contract(left), d.SOURCES[right], region_evidence=cert)

@pytest.mark.parametrize("left,right,scope", d.PAIRS[:2])
def test_raw_operator_without_proof_rejected(left, right, scope):
    with pytest.raises(ClosureError, match="INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE"):
        reconcile_complete_mapping(contract(left), d.SOURCES[right])
    with pytest.raises(ClosureError, match="MISSING_REGION_CERTIFICATE"):
        reconcile_complete_mapping(contract(left), d.SOURCES[right], transport_evidence={})

def test_wrong_bound_contract_and_certificate_rejected():
    m = reconcile_complete_mapping(contract("AND"), d.SOURCES["PRODUCT"], region_evidence=certificate(*d.PAIRS[0]))
    with pytest.raises(ClosureError, match="TRANSPORT_WRONG_BOUND_CONTRACT"):
        reconcile_complete_mapping(contract("REPEATED_AND"), d.SOURCES["PRODUCT"], transport_evidence=m.semantic_transport)
    with pytest.raises(ClosureError, match="TRANSPORT_CERTIFICATE_HASH_MISMATCH"):
        reconcile_complete_mapping(m.contract, m.program.source, region_evidence=certificate(*d.PAIRS[4]), transport_evidence=m.semantic_transport)

def test_independent_verifier_does_not_call_constructor(monkeypatch):
    bundle = base_bundle()
    record = reconcile_complete_mapping(contract("AND"), d.SOURCES["PRODUCT"], transport_evidence=bundle).to_record()
    import self_learning_ai.conf1_v3.canonical_transport as constructor
    import self_learning_ai.conf1_v3.coverage as production
    def forbidden(*args, **kwargs): raise AssertionError("constructor invoked")
    for name in ("build_canonical_transport", "semantic_definition", "transport_dag"):
        monkeypatch.setattr(constructor, name, forbidden)
    monkeypatch.setattr(production, "reconcile_complete_mapping", forbidden)
    assert verify_canonical_transport(bundle)["finding"] == "VERIFIED_CANONICAL_TRANSPORT"
    assert verify_mapping_proof_record(bundle, record)["mapping_constructor_invoked"] is False

def test_mapping_record_cannot_forge_raw_AND_satisfaction():
    m = reconcile_complete_mapping(contract("AND"), d.SOURCES["PRODUCT"], region_evidence=certificate(*d.PAIRS[0]))
    record = deepcopy(m.to_record())
    row = next(r for r in record["raw_key_resolution"] if r["operation"] == "AND")
    row["method"] = "VERIFIED_REGIONAL_SEMANTIC_TRANSPORT"
    with pytest.raises(ClosureError, match="MAPPING_PROOF_WRONG_KEY_SATISFACTION"):
        verify_mapping_proof_record(m.semantic_transport, record)

def test_mutable_production_proof_cannot_bypass_checker():
    m = reconcile_complete_mapping(contract("AND"), d.SOURCES["PRODUCT"], region_evidence=certificate(*d.PAIRS[0]))
    m.semantic_transport["transports"][0]["semantic_key_id"] = "forged"
    with pytest.raises(ClosureError, match="TRANSPORT_SEMANTIC_KEY_MISMATCH"): m.validate()

def test_matching_raw_capability_is_not_a_third_mapping_path():
    m = reconcile_complete_mapping(contract("AND"), d.SOURCES["PRODUCT"], region_evidence=certificate(*d.PAIRS[0]))
    record = deepcopy(m.to_record())
    row = next(r for r in record["raw_key_resolution"] if r["method"] == "UNRESOLVED_DISTINCT_RAW_REQUIREMENT")
    row["method"] = "DIRECT_TYPED_CAPABILITY"
    with pytest.raises(ClosureError, match="MAPPING_PROOF_WRONG_KEY_SATISFACTION"):
        verify_mapping_proof_record(m.semantic_transport, record)

def test_activity_accepts_no_caller_semantic_key(tmp_path):
    e = engine(tmp_path, *d.PAIRS[0])
    with pytest.raises(TypeError): e.semantic_activity("caller-selected-key")
    with pytest.raises(ClosureError, match="undeclared canonical key"):
        e.behavioral(e.mapping.semantic_transport["transports"][0]["semantic_key_id"])

def test_matching_outputs_do_not_authorize_transport():
    from self_learning_ai.conf1_v3.core_ir import compile_program, execute
    bad = compile_program("CTRANSPORT903-MATCHING_OUTPUT_INVALID", d.SOURCES["MATCHING_OUTPUT_INVALID"])
    assert all(execute(bad, raw).output == d.expected("PRODUCT", raw) for raw in d.RAW)
    cert = certificate("AND", "MATCHING_OUTPUT_INVALID", "LOCAL_PAIR_JOINT")
    assert cert["finding"] == "UNRESOLVED"

def test_alpha_and_repeated_semantic_key_same_not_same_claim():
    bundles = [reconcile_complete_mapping(contract(a), d.SOURCES[b], region_evidence=certificate(a,b,s)).semantic_transport for a,b,s in (d.PAIRS[0], d.PAIRS[2], d.PAIRS[4], d.PAIRS[5])]
    assert len({b["transports"][0]["semantic_key_id"] for b in bundles}) == 1
    repeated = bundles[2]["transports"]
    assert repeated[0]["obligation_id"] != repeated[1]["obligation_id"]
    assert repeated[0]["semantic_key_id"] == repeated[1]["semantic_key_id"]

def test_independence_zero_overlap():
    assert all(PREFLIGHT[k] == 0 for k in ("exact_string_overlap", "recorded_hash_overlap", "recomputed_string_hash_overlap"))
