"""Grammar-type readiness, not candidate/scientific instance closure."""
from copy import deepcopy
import pytest
import gbind905_inputs as d
from gbind905_runtime import mapped,negative,mutations,apply_mutation,EQUIVALENCES,REGIONAL,PREFLIGHT
from self_learning_ai.conf1_v3.interfaces import ClosureError,SchemaError
from self_learning_ai.conf1_v3.projection_grammar import derive_projection_plan,render_development
from self_learning_ai.conf1_v3.projection_binding import bind_projection
from self_learning_ai.conf1_v3.projection_binding_verifier import verify_projection_evidence,verify_projection_plan


def test_overlap_precedes_parsing():
    assert PREFLIGHT["exact_string_overlap"]==PREFLIGHT["recorded_hash_overlap"]==PREFLIGHT["recomputed_string_hash_overlap"]==0
    assert not PREFLIGHT["expected_labels_parsed"]


@pytest.mark.parametrize("name",d.DECLARATIONS)
def test_every_declared_grammar_form_direct(name):
    e=mapped(name); assert e["plan_before"]==e["plan_after"]
    assert verify_projection_evidence(e)["status"]=="VERIFIED"
    assert not e["claims"]
    for req,b in zip(e["plan_before"]["requirements"],e["bindings"]):
        assert req["requirement_id"]==b["requirement_id"]
        assert req["multiplicity"]==len(b["source_occurrences"])==len(b["contract_occurrences"])
        assert b["scope"]=="DEVELOPMENT_ONLY" and b["unresolved_reason"] is None


@pytest.mark.parametrize("name",d.DECLARATIONS)
def test_complete_alpha_mapping(name):
    e=mapped(name,name+"-ALPHA")
    assert any(c["catalog_rule"]=="CONSISTENT_ALPHA_RENAMING" for c in e["claims"])
    assert verify_projection_evidence(e)["scientific_satisfaction_claims"]==0


@pytest.mark.parametrize("name,variant",EQUIVALENCES)
def test_frozen_equivalence_families(name,variant):
    e=mapped(name,variant); assert e["claims"]
    assert all(c["affected_requirements"] and c["duplicates_retained"] for c in e["claims"])
    assert verify_projection_evidence(e)["status"]=="VERIFIED"


@pytest.mark.parametrize("name,variant,scope",REGIONAL)
def test_regional_and_ordinary_accounting(name,variant,scope):
    e=mapped(name,variant,scope)
    assert any(b["method"]=="AUTHORIZED_V33_EQUIVALENCE" for b in e["bindings"])
    assert any(b["method"]=="DIRECT_TYPED_CORRESPONDENCE" for b in e["bindings"])
    assert all(c["affected_requirements"] for c in e["claims"])
    assert not e["base_mapping"]["all_raw_atomic_keys_satisfied"]
    assert verify_projection_evidence(e)["status"]=="VERIFIED"


SOURCE_ATTACKS=(("numeric_iteration-ADD","STALE"),("numeric_iteration-ADD","WRONG_ROLE"),
 ("numeric_iteration-ADD","AMBIGUOUS"),("numeric_iteration-ADD","EXTRA_LIVE"),
 ("ASSOCIATION","REASSOCIATION"),("MUL_SORT","ARBITRARY_ALGEBRA"),("DUPLICATES","DROPPED_DUPLICATE"),
 ("array_reduction-ADD","LITERAL_REWRITE"),("numeric_iteration-ADD","INCOMPLETE_ALPHA"),
 ("numeric_iteration-PAIR_AND","UNSUPPORTED_BOOLEAN_ARITHMETIC"),("numeric_iteration-ADD","BAD_FOLD"),
 ("numeric_iteration-0-PER_ITEM-FWD","WRONG_DIRECTION"),("numeric_iteration-0-TWO_PASS-FWD","WRONG_LOOP"))

@pytest.mark.parametrize("name,attack",SOURCE_ATTACKS)
def test_invalid_source_fail_closed(name,attack):
    with pytest.raises((ClosureError,SchemaError)): negative(name,attack)


@pytest.mark.parametrize("index",range(16))
def test_serialized_adversaries(index):
    e=mapped("numeric_iteration-ADD"); attack=mutations(e)[index]
    with pytest.raises(ClosureError): verify_projection_evidence(apply_mutation(e,attack))


def test_wrong_equivalence_rule():
    e=deepcopy(mapped("ADD_SORT","ADD_SWAP")); e["claims"][0]["catalog_rule"]="ARBITRARY_ALGEBRA"
    with pytest.raises(ClosureError,match="V33_CLAIMS_CHANGED"): verify_projection_evidence(e)


@pytest.mark.parametrize("scope",["SCIENTIFIC_TRAINING","SCIENTIFIC_EVALUATION"])
def test_scientific_guard_before_source_parsing(scope,monkeypatch):
    import self_learning_ai.conf1_v3.projection_binding as module
    p=derive_projection_plan(d.DECLARATIONS["numeric_iteration-ADD"]); p["scope"]=scope
    monkeypatch.setattr(module,"compile_program",lambda *args:pytest.fail("scientific source was parsed"))
    with pytest.raises(ClosureError,match="SCIENTIFIC_SOURCE_MAPPING_DEFERRED"): bind_projection(p,"FORBIDDEN","FORBIDDEN")


def test_scientific_metadata_plan_cannot_enter_adapter():
    from self_learning_ai.conf1_v3.requirements import derive_training_slot
    p=derive_training_slot("CONF1-TR-NU-01-V0","COMPOSITION")
    with pytest.raises(ClosureError,match="SCIENTIFIC_SOURCE_MAPPING_DEFERRED"): bind_projection(p,"FORBIDDEN","FORBIDDEN")


def test_actual_slot_identity_cannot_be_realized():
    p=deepcopy(d.DECLARATIONS["numeric_iteration-ADD"]); p["program_id"]="CONF1-TR-NU-01-V0"
    with pytest.raises(ClosureError,match="SCIENTIFIC_IDENTITY"): render_development(p,"disposable")


def test_declared_kind_multiplicity_not_inferred_from_parser():
    e=mapped("array_reduction-ADD")
    conversions=[r for r in e["plan_before"]["requirements"] if r["capability"]["operation"]=="strings.TO_NUMBER"]
    assert len(conversions)==1 and conversions[0]["multiplicity"]==4
    assert e["plan_before"]["scientific_expected_row_index_eligible"] is False


def test_reference_only_is_pure_unused_not_a_requirement():
    e=mapped("UNUSED")
    assert any(not n["essential"] and n["proof"]=="PURE_UNUSED_NO_TYPED_PATH_TO_OUTPUT" for n in e["source_graph"]["nodes"])
    assert not any("unused" in str(r) for r in e["plan_before"]["requirements"])


def test_simultaneous_before_after_invention_is_rejected():
    e=deepcopy(mapped("numeric_iteration-ADD"))
    for side in ("plan_before","plan_after"): e[side]["requirements"].pop()
    with pytest.raises(ClosureError,match="PROSPECTIVE_GRAMMAR_PLAN_CHANGED"): verify_projection_evidence(e)


@pytest.mark.parametrize("name",d.DECLARATIONS)
def test_disposable_pinned_compiler_and_actual_indicator_writers(name):
    # These raw inputs were checked BEFORE parsing/execution. This is not a
    # scientific case, V3.5 activity experiment, or expected-output artifact.
    from self_learning_ai.conf1_v3.core_ir import compile_program,execute
    from self_learning_ai.conf1_v3.coverage import PinnedCompilerOracle
    e=mapped(name); p=compile_program(e["plan_before"]["program_id"],e["source"])
    run=execute(p,d.RAW[p.domain])
    oracle=PinnedCompilerOracle(d.ROOT/".tools/jdk-25.0.1+8/bin/java.exe",
                               d.ROOT/".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    assert oracle.run(p.source,d.RAW[p.domain])==run.output
    for foundation in e["indicator_foundations"]["source"]:
        for reading in foundation["reads"]:
            observed=[t for t in run.state_trace if t["kind"]=="READ" and t["reader"]==reading["read"]]
            assert all(t["writer"] in reading["writers"] for t in observed)
