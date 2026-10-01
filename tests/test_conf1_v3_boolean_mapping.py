"""Scoped Boolean certificates; local equivalence never implies total mapping."""
from copy import deepcopy
import json
import pytest
import bm901_inputs as d
PREFLIGHT=d.overlap()
from bm901_cases import PAIRS,certificate,negatives,expected
from sem900_runtime import contract
from self_learning_ai.conf1_v3.boolean_mapping import frozen_boolean_catalog,indicator_evidence,verify_complete_boolean_mapping
from self_learning_ai.conf1_v3.core_ir import compile_program,execute
from self_learning_ai.conf1_v3.coverage import PinnedCompilerOracle
from self_learning_ai.conf1_v3.interfaces import ClosureError


@pytest.mark.parametrize("left,right,scope",PAIRS)
def test_local_and_complete_certificates_are_distinct(left,right,scope):
    c,proof=certificate(left,right,scope)
    assert proof["local_v33_proofs"] and all(p["finding"]=="EQUIVALENT" for p in proof["local_v33_proofs"])
    assert all(p["not_complete_graph_equivalence"] for p in proof["local_v33_proofs"])
    if right in {"PRODUCT","SUM_POSITIVE"}:
        assert proof["finding"]=="UNRESOLVED"
        assert proof["unmatched_source_inventory"] and proof["unmatched_contract_inventory"]
        assert not proof["indicator_evidence_permitted"]
        with pytest.raises(ClosureError):indicator_evidence(c,d.SOURCES[right],proof)
    else:
        assert proof["finding"]=="COMPLETE"
        assert not proof["unmatched_source_inventory"] and not proof["unmatched_contract_inventory"]
        assert not proof["complete_graph_equivalence_claim"]
        verify_complete_boolean_mapping(c,d.SOURCES[right],proof)
        pairs=proof["source_to_contract_occurrences"]
        assert len(pairs)==len({p["source_occurrence"] for p in pairs})==len({p["contract_occurrence"] for p in pairs})
        assert {p["source_occurrence"] for p in pairs}=={i["occurrence_id"] for k in ("nodes","edges") for i in proof["source_inventory"][k]}
        assert {p["contract_occurrence"] for p in pairs}=={i["occurrence_id"] for k in ("nodes","edges") for i in proof["contract_inventory"][k]}


@pytest.fixture(scope="module")
def negative_results():return {r["case"]:r for r in negatives()}


@pytest.mark.parametrize("name",["incomplete_alpha","OMITTED","EXTRA_TERM","COMPOUND","AMBIGUOUS",
    "CONDITIONAL_RESET","READ_BEFORE_WRITE","STATE_ORDER","WRONG_TYPE","MATCHING_OUTPUT_INVALID",
    "SOURCE_ONLY","UNLISTED","CIRCULAR","duplicate_predicate_mapping","missing_contract_predicate",
    "omitted_source_predicate","cross_loop"])
def test_negative_cases_fail_for_semantic_reason(negative_results,name):
    row=negative_results[name]
    assert row["finding"] in {"UNRESOLVED","REJECTED"}
    assert row["required_semantic_reason"] in row["reason"]


def test_indicator_evidence_has_non_circular_foundation_and_total_mapping():
    c,proof=certificate("PRODUCT","ALPHA_PRODUCT")
    evidence=indicator_evidence(c,d.SOURCES["ALPHA_PRODUCT"],proof)
    assert len(evidence["records"])==2
    for record in evidence["records"]:
        assert record["actual_source_predicate"] in {p["source_predicate"] for p in proof["predicate_correspondence"]}
        assert record["current_iteration_reaching_definitions"]
        assert record["proof_dependency_order"]==["parsed typed source","frozen predicate recognition","reaching definitions",
            "local V3.3 preconditions","complete V3.2 correspondence","indicator evidence"]
    c,bad=certificate("AND","CIRCULAR")
    p=compile_program(c.program_id,d.SOURCES["CIRCULAR"])
    assert p.indicator_proofs["bm901P"]["range"]==[0,1]
    assert "circular" in bad["reason"]
    with pytest.raises(ClosureError):indicator_evidence(c,d.SOURCES["CIRCULAR"],bad)


def test_repeated_predicates_have_complete_distinct_correspondence():
    _,proof=certificate("REPEATED","ALPHA_REPEATED")
    pairs=proof["predicate_correspondence"]
    assert len(pairs)==6
    assert len({p["source_predicate"] for p in pairs})==len({p["contract_predicate"] for p in pairs})==6


def test_forged_pass_and_changed_port_or_type_are_not_evidence():
    c,proof=certificate("AND","PRODUCT")
    forged=deepcopy(proof);forged.update(finding="COMPLETE",status="PASS",indicator_evidence_permitted=True,
        unmatched_source_inventory=[],unmatched_contract_inventory=[])
    with pytest.raises(ClosureError):indicator_evidence(c,d.SOURCES["PRODUCT"],forged)
    c,proof=certificate("PRODUCT","ALPHA_PRODUCT")
    for field,value in (("datatype","BOOLEAN"),("port",999)):
        forged=deepcopy(proof);forged["typed_port_correspondence"][0][field]=value
        with pytest.raises(ClosureError,match="RECONSTRUCTION_MISMATCH"):
            verify_complete_boolean_mapping(c,d.SOURCES["ALPHA_PRODUCT"],forged)


def test_bijective_alpha_must_match_actual_complete_binding_mapping():
    c,_=certificate("PRODUCT","ALPHA_PRODUCT")
    from self_learning_ai.conf1_v3.boolean_mapping import complete_boolean_mapping
    p=compile_program(c.program_id,d.SOURCES["ALPHA_PRODUCT"])
    names=dict(zip(c.ir.symbols,p.symbols))
    names["bm901P"],names["bm901Q"]=names["bm901Q"],names["bm901P"]
    proof=complete_boolean_mapping(c,p.source,scope="LOCAL_PAIR_JOINT",alpha_map=names)
    assert proof["finding"]=="UNRESOLVED" and "COMPLETE_BINDING_CORRESPONDENCE" in proof["reason"]


@pytest.mark.parametrize("name",["AND","PRODUCT","OR","SUM_POSITIVE","MATCHING_OUTPUT_INVALID"])
def test_new_disposable_compiler_reference_agreement_not_mapping_fallback(name):
    p=compile_program("BMAP901-"+name,d.SOURCES[name])
    oracle=PinnedCompilerOracle(d.ROOT/".tools/jdk-25.0.1+8/bin/java.exe",d.ROOT/".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    for raw in d.RAW:
        assert oracle.run(p.source,raw)==execute(p,raw).output==expected(name,raw)
    if name=="MATCHING_OUTPUT_INVALID":
        _,proof=certificate("AND",name)
        assert proof["finding"]=="UNRESOLVED" and "TYPED_STRUCTURE" in proof["reason"]


def test_new_primitive_catalog_and_frozen_rule_limits():
    known={r["capability"] for name in ("ODD","RESIDUE","DIVISOR","HALF","ARRAY") for r in compile_program("BMAP901-"+name,d.SOURCES[name]).semantic_records}
    assert known=={"odd_index","residue_two","divisor_index","first_half","negative_value","even_value","large_magnitude","value_exceeds_index"}
    rules=frozen_boolean_catalog()["rules"]
    assert {r["scope"] for r in rules}=={"LOCAL_PAIR_JOINT","BOOLEAN_OR"}
    assert all(not r["complete_graph_equivalence_authorized"] and not r["general_algebra_authorized"] for r in rules)


def test_saved_artifacts_independent_reconstruction_and_untouched_gates():
    folder=d.ROOT/"research/implementation_notes/coverage_v3_boolean_mapping"
    assert json.loads((folder/"disposable_overlap.json").read_bytes())==PREFLIGHT
    rows=json.loads((folder/"complete_v32_mapping_certificates.json").read_bytes())["records"]
    for row in rows:
        c=contract(d.SOURCES[row["contract_form"]],"BMAP901-"+row["contract_form"])
        if row["certificate"]["finding"]=="COMPLETE":
            verify_complete_boolean_mapping(c,d.SOURCES[row["source_form"]],row["certificate"])
        else:
            assert row["certificate"]["unmatched_source_inventory"] and row["certificate"]["unmatched_contract_inventory"]
    baseline=json.loads((d.ROOT/"research/implementation_notes/coverage_v3_semantic_core/semantic_gate_evidence.json").read_bytes())
    updated=json.loads((folder/"development_gate_evidence.json").read_bytes())
    scoped={"INDICATOR_EXTRACTION_COMPLETE","V32_SEMANTIC_MAPPING_COMPLETE","V33_REQUIRED_EQUIVALENCE_COMPLETE"}
    assert all(a==b for a,b in zip(baseline["gates"],updated["gates"]) if a["gate"] not in scoped)
    assert all(g["status"]=="UNRESOLVED" and g["remaining_evidence_obligations"] for g in updated["gates"] if g["gate"] in scoped)
    assert updated["population_status"]=="V3_5_POPULATION_UNRESOLVED" and not updated["authoritative_population_recount_performed"]
