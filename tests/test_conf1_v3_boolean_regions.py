"""New disposable region and independent serialized-certificate tests."""
import json
from dataclasses import replace
import pytest
import bt902_inputs as d
PREFLIGHT = d.overlap()  # Before semantic imports/execution.
from bt902_runtime import certificate
from bt902_adversarial import SOURCE_NEGATIVES, MUTATIONS, mutate
from self_learning_ai.conf1_v3.boolean_region_checker import check_serialized_mapping, extract_indicator_evidence
from self_learning_ai.conf1_v3.core_ir import compile_program, execute
from self_learning_ai.conf1_v3.interfaces import ClosureError


@pytest.mark.parametrize("left,right,scope", d.PAIRS)
def test_total_region_mapping(left, right, scope):
    cert = certificate(left, right, scope)
    assert cert["finding"] == "COMPLETE", cert.get("reason")
    serialized = json.loads(json.dumps(cert))
    checked = check_serialized_mapping(serialized)
    assert checked["finding"] == "VERIFIED_TOTAL"
    for side in ("source", "contract"):
        assert not cert["partition"][side + "_uncovered"]
        assert not cert["partition"][side + "_duplicate_coverage"]
        assert set(cert["partition"][side + "_ordinary_covered"]).isdisjoint(cert["partition"][side + "_region_covered"])
        inv = cert[side + "_inventory"]
        assert len(cert["partition"][side + "_ordinary_covered"]) + len(cert["partition"][side + "_region_covered"]) == len(inv["nodes"]) + len(inv["edges"])
    assert all(r["local_v33_proof"]["finding"] == "EQUIVALENT" for r in cert["regions"])
    assert not cert["complete_graph_equivalence_claim"] and not cert["atomic_key_transport_claim"]
    assert len(extract_indicator_evidence(cert)["records"]) == (4 if left.startswith("REPEATED") else 2)


@pytest.mark.parametrize("case,left,right,scope,reason,valid_local", SOURCE_NEGATIVES)
def test_valid_local_does_not_close_global(case, left, right, scope, reason, valid_local):
    cert = certificate(left, right, scope)
    assert cert["finding"] == "UNRESOLVED" and cert["reason"] == reason
    assert not cert["indicator_evidence_permitted"]
    if valid_local: assert any(p["finding"] == "EQUIVALENT" for p in cert["local_v33_proofs"])
    with pytest.raises(ClosureError, match="COMPLETE_MAPPING_REQUIRED"): extract_indicator_evidence(cert)


@pytest.mark.parametrize("attack,reason", MUTATIONS)
def test_serialized_mutation_rejected(attack, reason):
    cert = certificate("AND", "PRODUCT", "LOCAL_PAIR_JOINT")
    with pytest.raises(ClosureError, match=reason): check_serialized_mapping(mutate(cert, attack))


def test_checker_never_calls_constructor(monkeypatch):
    cert = certificate("AND", "PRODUCT", "LOCAL_PAIR_JOINT")
    import self_learning_ai.conf1_v3.boolean_regions as constructor
    def forbidden(*args, **kwargs): raise AssertionError("constructor called by checker")
    for function in ("total_boolean_mapping", "shape", "assign_edges", "coverage_partition", "scaffold", "dependency_graph"):
        monkeypatch.setattr(constructor, function, forbidden)
    assert check_serialized_mapping(cert)["finding"] == "VERIFIED_TOTAL"


def test_flag_cannot_bypass_indicator_dependency():
    cert = certificate("AND", "EXTRA_ARITHMETIC", "LOCAL_PAIR_JOINT")
    cert["indicator_evidence_permitted"] = True
    with pytest.raises(ClosureError, match="COMPLETE_MAPPING_REQUIRED"): extract_indicator_evidence(cert)


@pytest.mark.parametrize("kind", ("development", "primary"))
def test_internal_mapper_cannot_close_incomplete_or_production_contract(kind):
    from bt902_runtime import contract
    from self_learning_ai.conf1_v3.boolean_regions import total_boolean_mapping
    incomplete = replace(contract("AND"), task_kind=kind, core_gaps=("TASK_ESSENTIALITY_PROOF_INCOMPLETE",))
    with pytest.raises(ClosureError, match="requires a complete development contract"):
        total_boolean_mapping(incomplete, d.SOURCES["PRODUCT"], scope="LOCAL_PAIR_JOINT")


def test_repeated_regions_keep_duplicate_predicates_and_one_edge_owner():
    cert = certificate("REPEATED_AND", "REPEATED_PRODUCT", "LOCAL_PAIR_JOINT")
    assert len(cert["regions"]) == 2
    assert len(cert["contract_inventory"]["predicate_occurrences"]) == 6
    assert len(cert["source_inventory"]["predicate_occurrences"]) == 2
    for side in ("source", "contract"):
        a, b = (set(r[side]["members"]) for r in cert["regions"])
        assert not a & b
    assert check_serialized_mapping(cert)["finding"] == "VERIFIED_TOTAL"


def test_new_primitives_and_independence():
    assert all(PREFLIGHT[k] == 0 for k in ("exact_string_overlap", "recorded_hash_overlap", "recomputed_string_hash_overlap"))
    known = {r["capability"] for name in ("ODD", "RESIDUE", "DIVISOR", "HALF", "ARRAY") for r in compile_program("BTOTAL902-" + name, d.SOURCES[name]).semantic_records}
    assert known == {"odd_index", "residue_two", "divisor_index", "first_half", "negative_value", "even_value", "large_magnitude", "value_exceeds_index"}


def expected(name, raw):
    n = int(raw)
    is_or = name in {"OR", "SUM", "ALPHA_SUM"}
    hits = sum(int((i % 2 == 1 or i % 3 == 2) if is_or else (i % 2 == 1 and i % 3 == 2)) for i in range(1, n + 1))
    return str(181 + hits * (2 if name.startswith("REPEATED") else 1))


def test_new_pinned_compiler_and_normal_ir():
    from self_learning_ai.conf1_v3.coverage import PinnedCompilerOracle
    oracle = PinnedCompilerOracle(d.ROOT / ".tools/jdk-25.0.1+8/bin/java.exe", d.ROOT / ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    for name in ("AND", "PRODUCT", "OR", "SUM", "REPEATED_AND", "REPEATED_PRODUCT", "ALPHA_PRODUCT", "ALPHA_SUM", "SAME_OUTPUT"):
        p = compile_program("BTOTAL902-" + name, d.SOURCES[name])
        for raw in d.RAW:
            assert execute(p, raw).output == oracle.run(p.source, raw) == expected(name, raw)


def test_checkpoint_gates_are_not_toy_passes():
    baseline = json.loads((d.ROOT / "research/implementation_notes/coverage_v3_boolean_mapping/development_gate_evidence.json").read_bytes())
    saved = json.loads((d.ROOT / "research/implementation_notes/coverage_v3_boolean_total_mapping/development_gate_evidence.json").read_bytes())
    targeted = {"INDICATOR_EXTRACTION_COMPLETE", "V32_SEMANTIC_MAPPING_COMPLETE", "V33_REQUIRED_EQUIVALENCE_COMPLETE"}
    for old, new in zip(baseline["gates"], saved["gates"]):
        if old["gate"] not in targeted: assert old == new
        else: assert new["status"] == "UNRESOLVED" and new["remaining_evidence_obligations"]
