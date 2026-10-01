from copy import deepcopy
from collections import Counter
import pytest
import ess907_inputs as d
from ess907_runtime import evidence
from ess907_adversaries import INTENT,mutate
from self_learning_ai.conf1_v3.essentiality_verifier import verify_essentiality_evidence
from self_learning_ai.conf1_v3.essentiality_semantics import context,counterfactual
from self_learning_ai.conf1_v3.interfaces import ClosureError,SchemaError

def test_overlap_before_any_execution():
    assert not any(d.PREFLIGHT[k] for k in ("exact_string_overlap","recorded_hash_overlap","recomputed_string_hash_overlap"))
    assert d.PREFLIGHT["expected_labels_parsed"] is False

@pytest.mark.parametrize("name",d.DECLARATIONS)
@pytest.mark.parametrize("alpha",[False,True])
def test_pinned_disposable_essentiality(name,alpha):
    e=evidence(name,alpha);v=verify_essentiality_evidence(e)
    assert v["constructor_conclusion_trusted"] is False
    assert v["scientific_instance_closure"]=="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION_AND_VALIDATION"
    assert any(r["status"]=="ACTIVE" for r in v["cases"])
    assert any(r["reason"]=="NO_ACTIVITY_EVIDENCE_ON_THIS_CASE" for r in v["cases"])

@pytest.mark.parametrize("label",INTENT)
def test_serialized_adversary_intended_reason(label):
    base=evidence(d.TWO if label in {"WRONG_LOOP","CROSS_PASS"} else d.REPEAT)
    with pytest.raises((ClosureError,SchemaError),match="^"+INTENT[label]+"$"):
        verify_essentiality_evidence(mutate(base,label))

@pytest.mark.parametrize("family",["numeric_iteration","array_reduction"])
@pytest.mark.parametrize("reverse",[False,True])
def test_loop_false_terminates_true_has_no_output(family,reverse):
    name=family+"-0-PER_ITEM-"+("REV" if reverse else "FWD");e=evidence(name)
    p,g,c=context(e["mapping"],e["state"],e["compiler"])
    f=next(f for f in e["findings"] if f["bound_requirement"]["capability"]["operation"]=="BOUNDED_LOOP")
    assert f["cases"][0]["status"]=="ACTIVE"
    assert f["cases"][0]["attempts"][0]["intervention"]["replacement"] is False
    request=dict(occurrences=f["bound_requirement"]["joint_occurrences"],replacement=True,order=1)
    a=counterfactual(p,g,f["bound_requirement"],f["policy"],d.RAW[family][0],request,4096)
    assert a["execution_status"]=="UNRESOLVED" and a["runtime"] is None
    assert a["failure_observations"]["complete"] is False and a["failure_observations"]["terminal_output"] is None
    assert a["reason"] in {"IR_EXECUTION_BUDGET_EXCEEDED","index out of bounds","remainder by zero","runtime writer absent from static reaching definitions"}

def test_budget_timeout_is_not_a_terminal_output():
    e=evidence(d.BASE);p,g,c=context(e["mapping"],e["state"],e["compiler"])
    f=next(f for f in e["findings"] if f["bound_requirement"]["capability"]["operation"]=="BOUNDED_LOOP")
    a=counterfactual(p,g,f["bound_requirement"],f["policy"],d.RAW[p.domain][0],dict(occurrences=f["bound_requirement"]["joint_occurrences"],replacement=False,order=0),1)
    assert a["reason"]=="IR_EXECUTION_BUDGET_EXCEEDED" and a["runtime"] is None

def test_constructor_disabled_saved_packet_still_replays(monkeypatch):
    e=evidence(d.PREFIX)
    import self_learning_ai.conf1_v3.essentiality_evidence as module
    monkeypatch.setattr(module,"construct_essentiality_evidence",lambda *a,**k:pytest.fail("constructor called"))
    assert verify_essentiality_evidence(e)["status"]=="VERIFIED"

@pytest.mark.parametrize("scope",["SCIENTIFIC_TRAINING","SCIENTIFIC_EVALUATION"])
def test_namespace_guard_precedes_parse(scope,monkeypatch):
    e=deepcopy(evidence(d.BASE));e["scope"]=scope
    import self_learning_ai.conf1_v3.essentiality_verifier as module
    monkeypatch.setattr(module,"context",lambda *a:pytest.fail("scientific source parsed"))
    with pytest.raises(ClosureError,match="ESSENTIALITY_SCIENTIFIC_LAYER_FORGE"):verify_essentiality_evidence(e)

def test_alpha_joint_semantics_not_occurrence_spelling():
    a=evidence(d.REPEAT);b=evidence(d.REPEAT,True)
    assert [f["policy"] for f in a["findings"]]==[f["policy"] for f in b["findings"]]
    assert [[c["status"] for c in f["cases"]] for f in a["findings"]]==[[c["status"] for c in f["cases"]] for f in b["findings"]]
    assert [len(f["bound_requirement"]["joint_occurrences"]) for f in a["findings"]]==[len(f["bound_requirement"]["joint_occurrences"]) for f in b["findings"]]

def test_inactive_is_exercised_same_case_not_global():
    cases=[c for n in d.DECLARATIONS for f in evidence(n)["findings"] for c in f["cases"] if c["status"]=="INACTIVE"]
    assert cases
    assert all(c["normal_events"] and c["reason"]=="CAPABILITY_PROVED_INACTIVE" and c["status_scope"]=="THIS_DEVELOPMENT_CASE_ONLY" for c in cases)

def test_complete_kind_matrix_and_all_eight_frozen_predicates():
    from self_learning_ai.conf1_v3.essentiality_audit import inventories
    records=[dict(record_id=n,evidence=evidence(n)) for n in d.DECLARATIONS]
    inventory=inventories(records)
    assert len(inventory["predicates"])==8
    assert set(inventory["classes"])=={"API_DECODER","SEMANTIC_PRIMITIVE","GENERIC_CONSTRUCT","ATOMIC_OPERATOR","ATOMIC_CONTROL_DATAFLOW"}
    assert set(inventory["case_status_counts"])=={"ACTIVE","INACTIVE","UNRESOLVED"}
    assert all(row["dead_case_witness"] for row in inventory["kind_matrix"] if row["supported"])

@pytest.mark.parametrize("name",[d.BASE,d.PREFIX,d.TWO])
def test_stateful_activity_uses_verified_relations(name):
    e=evidence(name)
    active=[f for f in e["findings"] if f["cases"][0]["status"]=="ACTIVE"]
    assert active
    for f in active:
        runtime=e["runtimes"][f["cases"][0]["attempts"][0]["runtime_ref"]]
        assert runtime["state"]["all_runtime_reads_resolved"]
        assert all(t["occurrence"] in f["bound_requirement"]["joint_occurrences"] for t in runtime["interventions"])

def test_dead_predicate_masked_by_or_is_not_inactive():
    e=evidence("array_reduction-OR")
    f=next(f for f in e["findings"] if f["bound_requirement"]["capability"]["operation"]=="negative_value")
    assert f["cases"][1]["reason"]=="NO_ACTIVITY_EVIDENCE_ON_THIS_CASE"
    assert f["cases"][3]["status"]=="INACTIVE"

def test_lexical_first_witness_and_no_global_inactivity():
    e=evidence(d.BASE)
    for f in e["findings"]:
        active=sorted((c for c in f["cases"] if c["status"]=="ACTIVE"),key=lambda c:c["case_id"].encode())
        assert f["status_scope"]=="DECLARED_DEVELOPMENT_CASE_SET_ONLY"
        if active:
            assert f["first_active_witness"]["case_id"]==active[0]["case_id"]
            assert f["first_active_witness"]["intervention_order"]==active[0]["attempts"][-1]["intervention"]["order"]
    forged=deepcopy(e);next(f for f in forged["findings"] if f["first_active_witness"])["first_active_witness"]["case_id"]="FORGED"
    with pytest.raises(ClosureError,match="ESSENTIALITY_CASE_SET_OR_FIRST_WITNESS_FORGE"):verify_essentiality_evidence(forged)
