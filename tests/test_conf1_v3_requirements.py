"""Disposable namespace, requirement preservation and integrated mapping tests."""
from copy import deepcopy
from dataclasses import replace
import pytest
import creq904_inputs as d
PREFLIGHT=d.overlap()
from creq904_runtime import plan, contract, mapped
from self_learning_ai.conf1_v3.requirements import derive_training_slot, frozen_metadata, evaluation_namespace, assert_no_scope_transfer, require_scientific_index_eligibility, derive_development
from self_learning_ai.conf1_v3.requirement_verifier import verify_plan, verify_requirement_evidence
from self_learning_ai.conf1_v3.coverage import reconcile_complete_mapping
from self_learning_ai.conf1_v3.boolean_regions import total_boolean_mapping
from self_learning_ai.conf1_v3.interfaces import ClosureError, SchemaError

def test_overlap_before_source_processing():
    assert PREFLIGHT["exact_string_overlap"]==PREFLIGHT["recorded_hash_overlap"]==PREFLIGHT["recomputed_string_hash_overlap"]==0
    assert PREFLIGHT["expected_labels_parsed"] is False

def test_changed_normative_authority_stops_derivation_without_touching_files(monkeypatch):
    from pathlib import Path
    original=Path.read_bytes
    def bytes_for_test(path):
        data=original(path)
        return data+b"\nDISPOSABLE_IN_MEMORY_AUTHORITY_MUTATION" if path.name=="phase3c_conf1_proposed_protocol.md" else data
    monkeypatch.setattr(Path,"read_bytes",bytes_for_test)
    with pytest.raises(ClosureError,match="FROZEN_REQUIREMENT_NORMATIVE_AUTHORITY_CHANGED"):
        derive_training_slot("CONF1-TR-NU-01-V0","COMPOSITION")

@pytest.mark.parametrize("condition",["ISOLATED","COMPOSITION"])
def test_all_training_slots_metadata_only(condition):
    for slot in frozen_metadata()["slots"]["training_paired_slots"]:
        p=derive_training_slot(slot["slot_id"],condition); assert verify_plan(p)["status"]=="VERIFIED"
        assert p["scope"]=="SCIENTIFIC_TRAINING"
        assert all(r["provenance"]["frozen_slot"]==slot for r in p["requirements"])
        assert not any(r["capability"]["operation"] in {"OR","AND"} for r in p["requirements"])
        treatment=next(r for r in p["requirements"] if r["occurrence_requirements"][0]["grammar_path"]=="treatment")
        assert treatment["capability"]["operation"]==("ADD" if condition=="ISOLATED" else "MUL")
        assert all(r["multiplicity"] in {1,4} for r in p["requirements"])
        assert len({r["canonical_contract_key"] for r in p["requirements"]})==len(p["requirements"])
        with pytest.raises(ClosureError,match="V3_5_POPULATION_UNRESOLVED"): require_scientific_index_eligibility(p)

def test_distinct_role_bindings_distinct_required_occurrences():
    a=derive_training_slot("CONF1-TR-NU-01-V0","COMPOSITION"); b=derive_training_slot("CONF1-TR-NU-01-V1","COMPOSITION")
    assert not {r["requirement_id"] for r in a["requirements"]}&{r["requirement_id"] for r in b["requirements"]}
    for p in (a,b):
        for role in ("P","Q"):
            r=next(r for r in p["requirements"] if r["occurrence_requirements"][0]["grammar_path"]==role+"/predicate")
            assert r["capability"]["operation"]==r["provenance"]["frozen_slot"][role]

@pytest.mark.parametrize("name",["OR","REPEATED_AND"])
@pytest.mark.parametrize("scope",["SCIENTIFIC_TRAINING","SCIENTIFIC_EVALUATION"])
def test_development_cannot_enter_scientific_index(name,scope):
    p=plan(name)
    with pytest.raises(ClosureError,match="CROSS_SCOPE"): require_scientific_index_eligibility(p,scope)
    changed=deepcopy(p); changed["scope"]=scope
    with pytest.raises(ClosureError): verify_plan(changed)

def test_evaluation_namespace_only_no_training_transfer():
    slot=frozen_metadata()["slots"]["primary"][0]; p=evaluation_namespace(slot["task_id"])
    assert p["scope"]=="SCIENTIFIC_EVALUATION" and not p["training_requirement_transfer_authorized"]
    with pytest.raises(SchemaError): derive_training_slot(slot["task_id"],"ISOLATED")

@pytest.mark.parametrize("left,right",[("DIRECT","DIRECT"),("DIRECT","ALPHA_DIRECT"),("DIRECT","COMMUTATIVE"),("MUL","MUL_SWAP"),("GT","LT_REVERSED"),("GE","LE_REVERSED"),("EQ","EQ_REVERSED"),("DIRECT","FOLDED"),("DUPLICATES","DUPLICATES_SWAP"),("INCIDENTAL","INCIDENTAL")])
def test_complete_mapping_integrates_only_invoked_rules(left,right):
    m=mapped(left,right); m.validate(); e=m.requirement_evidence
    assert verify_requirement_evidence(e)["status"]=="VERIFIED" and e["before"]==e["after"]
    expected={"ALPHA_DIRECT":"CONSISTENT_ALPHA_RENAMING","COMMUTATIVE":"PURE_COMMUTATIVE_CHILD_SORT","MUL_SWAP":"PURE_COMMUTATIVE_CHILD_SORT","LT_REVERSED":"COMPARISON_DIRECTION","LE_REVERSED":"COMPARISON_DIRECTION","EQ_REVERSED":"SYMMETRIC_EQUALITY","FOLDED":"WHOLLY_INTEGER_CONSTANT_NEG_ADD_SUB_MUL_COMPUTED_KEY_ONLY","DUPLICATES_SWAP":"PURE_COMMUTATIVE_CHILD_SORT"}.get(right)
    rules={x["catalog_rule"] for x in e["integrated_claims"]}
    if expected: assert expected in rules
    else: assert not rules
    assert all(x["duplicates_retained"] for x in e["integrated_claims"])

@pytest.mark.parametrize("left,right,scope",d.PAIRS)
def test_six_transports_bind_development_only_preexisting_requirements(left,right,scope):
    p=plan(left); m=mapped(left,right,scope); e=m.requirement_evidence
    assert e["before"]==p==e["after"]
    assert len(e["bindings"])==(2 if left=="REPEATED_AND" else 1)
    assert all(b["scope"]=="DEVELOPMENT_ONLY" for b in e["bindings"])
    assert all(not r["scientific_requirement_ids"] and not r["scientific_satisfaction_claim"] for r in e["raw_classification"])
    assert m.to_record()["all_raw_atomic_keys_satisfied"] is False
    assert verify_requirement_evidence(e)["scientific_satisfaction_claims"]==0

def test_incidental_nodes_do_not_create_requirements():
    a=d.declaration("DIRECT"); b=deepcopy(a)
    assert derive_development(a)==derive_development(b)
    c=contract("INCIDENTAL"); assert any(not i.essential for i in c.ir.items)
    assert not any("Unused" in str(r) for r in plan("INCIDENTAL")["requirements"])

@pytest.mark.parametrize("left,right,reason",[("MUL","DIRECT","INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE"),("DIRECT","EXTRA_LIVE","UNMATCHED_LIVE_SOURCE_STRUCTURE"),("ASSOCIATION","REASSOCIATED","INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE")])
def test_missing_atomic_extra_live_and_unlisted_reassociation_fail(left,right,reason):
    with pytest.raises(ClosureError,match=reason): mapped(left,right)

def test_required_atomic_mul_is_not_waived_as_pair_joint():
    assert any(r["capability"]["operation"]=="MUL" for r in plan("MUL")["requirements"])
    assert all(r["requirement_class"]=="ONTOLOGY_KEY" for r in plan("MUL")["requirements"])

@pytest.mark.parametrize("left,right",[("BOOL_AND_SORT","BOOL_AND_SORTED"),("BOOL_OR_SORT","BOOL_OR_SORTED")])
def test_pure_boolean_sorting_integrated_without_atomic_and_mul_alias(left,right):
    e=mapped(left,right).requirement_evidence
    assert any(x["catalog_rule"]=="PURE_COMMUTATIVE_CHILD_SORT" for x in e["integrated_claims"])
    assert all(x["catalog_rule"]!="AND_VS_PROVEN_01_PRODUCT_LOCAL_ONLY" for x in e["integrated_claims"])

def test_source_syntax_alone_cannot_create_requirements():
    from self_learning_ai.conf1_v3.core_ir import compile_program
    from self_learning_ai.conf1_v3.contract_ir import graph_record,keys_from_ir
    prospective=plan("DIRECT"); original=contract("DIRECT"); p=compile_program(original.program_id,d.SOURCES["INCIDENTAL"])
    keys,occ=keys_from_ir(p,())
    changed=replace(original,reference_source=p.source,ir=p,complete_expression_graph=graph_record(p),canonical_keys=keys,key_occurrences=occ)
    m=reconcile_complete_mapping(changed,p.source,requirement_plan=prospective)
    assert m.requirement_evidence["before"]==prospective==m.requirement_evidence["after"]
    assert any(not i.essential for i in m.program.items)

def test_mutation_of_both_copies_cannot_invent_a_requirement():
    e=deepcopy(mapped("AND","PRODUCT","LOCAL_PAIR_JOINT").requirement_evidence)
    for side in ("before","after"): e[side]["requirements"].append(deepcopy(e[side]["requirements"][0]))
    with pytest.raises(ClosureError,match="REQUIREMENT_MISSING_OR_INVENTED"): verify_requirement_evidence(e)

def test_metadata_required_atomic_component_remains_scientific_required():
    slot=next(s for s in frozen_metadata()["slots"]["training_paired_slots"] if s["P"]=="first_half" or s["Q"]=="first_half")
    p=derive_training_slot(slot["slot_id"],"ISOLATED")
    assert any(r["capability"]["operation"]=="MUL" and r["scope"]=="SCIENTIFIC_TRAINING" and r["evidence_kind"]=="BEHAVIORAL" for r in p["requirements"])
    assert not any(r["capability"]["operation"]=="LOCAL_PAIR_JOINT" for r in p["requirements"])

def test_ambiguous_unmatched_indicator_scaffold_stays_fail_closed():
    c=contract("BARE_AND"); cert=total_boolean_mapping(c,d.SOURCES["PRODUCT"],scope="LOCAL_PAIR_JOINT")
    assert not cert["indicator_evidence_permitted"]
    with pytest.raises(ClosureError): reconcile_complete_mapping(c,d.SOURCES["PRODUCT"],region_evidence=cert,requirement_plan=plan("BARE_AND"))

@pytest.mark.parametrize("mutation",["promote_training","promote_evaluation","invent","remove","merge","wrong_requirement","change_kind","false_classification","claim_tamper"])
def test_independent_serialized_mutations_reject_intended_reason(mutation):
    e=deepcopy(mapped("REPEATED_AND","REPEATED_PRODUCT","LOCAL_PAIR_JOINT").requirement_evidence)
    if mutation=="promote_training": e["after"]["scope"]="SCIENTIFIC_TRAINING"
    elif mutation=="promote_evaluation": e["after"]["scope"]="SCIENTIFIC_EVALUATION"
    elif mutation=="invent": e["after"]["requirements"].append(deepcopy(e["after"]["requirements"][0]))
    elif mutation=="remove": e["after"]["requirements"].pop()
    elif mutation=="merge": e["bindings"][1]=deepcopy(e["bindings"][0])
    elif mutation=="wrong_requirement": e["bindings"][0]["requirement_id"]=e["bindings"][1]["requirement_id"]
    elif mutation=="change_kind": e["after"]["requirements"][0]["evidence_kind"]="OUTPUT_ATTRIBUTE"
    elif mutation=="false_classification": e["raw_classification"][0]["classification"]="CANONICAL_REQUIRED_DIRECT"
    elif mutation=="claim_tamper": e["integrated_claims"][0]["catalog_rule"]="GENERAL_ALGEBRA"
    reason="REQUIREMENT_SET_OR_SCOPE_CHANGED" if mutation in {"promote_training","promote_evaluation","invent","remove","change_kind"} else "RAW_CLASSIFICATION_TAMPERED" if mutation=="false_classification" else "INVOKED_V33_CLAIMS_TAMPERED" if mutation=="claim_tamper" else "REQUIREMENT_BINDING_TAMPERED_OR_WRONG"
    with pytest.raises(ClosureError,match=reason): verify_requirement_evidence(e)

def test_valid_equivalence_wrong_prospective_relation_rejected():
    m=mapped("AND","PRODUCT","LOCAL_PAIR_JOINT"); wrong=deepcopy(d.declaration("AND")); wrong["contributions"][0]["expression"]="P||Q"
    with pytest.raises(ClosureError,match="VALID_TRANSPORT_WRONG_CANONICAL_REQUIREMENT"):
        reconcile_complete_mapping(m.contract,d.SOURCES["PRODUCT"],transport_evidence=m.semantic_transport,requirement_plan=derive_development(wrong))

def test_scientific_requirement_cannot_be_supplied_by_development_transport():
    m=mapped("AND","PRODUCT","LOCAL_PAIR_JOINT"); science=derive_training_slot("CONF1-TR-NU-01-V0","COMPOSITION")
    with pytest.raises(ClosureError,match="SCIENTIFIC_SOURCE_REQUIREMENT_MAPPING_UNRESOLVED"):
        reconcile_complete_mapping(m.contract,d.SOURCES["PRODUCT"],transport_evidence=m.semantic_transport,requirement_plan=science)

@pytest.mark.parametrize("scope",["SCIENTIFIC_TRAINING","SCIENTIFIC_EVALUATION"])
def test_no_training_evaluation_cross_namespace(scope):
    a=derive_training_slot("CONF1-TR-NU-01-V0","COMPOSITION") if scope=="SCIENTIFIC_TRAINING" else evaluation_namespace(frozen_metadata()["slots"]["primary"][0]["task_id"])
    b=deepcopy(a); b["scope"]="SCIENTIFIC_EVALUATION" if scope=="SCIENTIFIC_TRAINING" else "SCIENTIFIC_TRAINING"
    with pytest.raises(ClosureError,match="REQUIREMENT_SET_OR_SCOPE_CHANGED"): assert_no_scope_transfer(a,b)

def test_unrelated_gaps_deferred_only_under_verified_development_projection():
    c=replace(contract("AND"),core_gaps=("OUTPUT_CASE_OBLIGATIONS_UNRESOLVED","V35_ACTIVITY_UNRESOLVED","E5_SIGNATURE_UNRESOLVED"))
    base=mapped("AND","PRODUCT","LOCAL_PAIR_JOINT")
    m=reconcile_complete_mapping(c,d.SOURCES["PRODUCT"],transport_evidence=base.semantic_transport,requirement_plan=plan("AND")); m.validate()
    assert m.contract.core_gaps==c.core_gaps
    with pytest.raises(ClosureError,match="incomplete prospective contract"): reconcile_complete_mapping(c,d.SOURCES["PRODUCT"],transport_evidence=base.semantic_transport)
    bad=replace(c,core_gaps=("SEMANTIC_PRIMITIVE_AND_PREDICATE_INDICATOR_EXTRACTION_INCOMPLETE",))
    with pytest.raises(ClosureError,match="RELEVANT_BOOLEAN_FOUNDATION_UNRESOLVED"): reconcile_complete_mapping(bad,d.SOURCES["PRODUCT"],transport_evidence=base.semantic_transport,requirement_plan=plan("AND"))
