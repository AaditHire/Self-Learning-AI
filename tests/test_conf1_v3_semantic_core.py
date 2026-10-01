"""New disposable semantic-core cases. No preregistered scientific execution."""
import json
from dataclasses import replace
import pytest
import sem900_development_inputs as dev

PREFLIGHT=dev.overlap()

from sem900_runtime import contract,engine
from self_learning_ai.conf1_v3.core_ir import compile_program,execute
from self_learning_ai.conf1_v3.coverage import reconcile_complete_mapping
from self_learning_ai.conf1_v3.goco import Expr,Stmt,_walk_stmt,Parser,expressions_equivalent
from self_learning_ai.conf1_v3.interfaces import SchemaError,ClosureError
from self_learning_ai.conf1_v3.semantic_ir import source_flow_equivalence


@pytest.fixture(scope="module")
def engines(tmp_path_factory):
    return {name:engine(tmp_path_factory.mktemp("sem900-"+name),name) for name in dev.SOURCES if not name.startswith("BAD_") and name!="ARRAY_LE"}


def expression(program,operator):
    return next(x for top in program.statements for x in _walk_stmt(top) if isinstance(x,Expr) and x.kind=="BINARY" and x.value==operator)


def test_saved_preflight_precedes_execution():
    saved=json.loads((dev.ROOT/"research/implementation_notes/coverage_v3_semantic_core/disposable_overlap.json").read_bytes())
    assert saved==PREFLIGHT
    assert saved["exact_string_overlap"]==saved["computed_string_hash_overlap"]==saved["recorded_hash_overlap"]==0
    assert not saved["expected_labels_parsed"]


@pytest.mark.parametrize("name,primitive",[("ODD","odd_index"),("RESIDUE","residue_two"),("DIVISOR","divisor_index"),("HALF","first_half")])
def test_numeric_frozen_primitives_are_typed_source_mapped(engines,name,primitive):
    e=engines[name];records=e.mapping.program.semantic_records
    assert {r["capability"] for r in records}=={primitive}
    for r in records:
        assert r["operand_types"]==["INTEGER","INTEGER"] and r["result_type"]=="BOOLEAN"
        assert len(r["input_ports"])==2 and r["structural_output_dependency"]
        assert r["contract_occurrence_id"] in dict(e.mapping.correspondence).values()
    key=next(k for k in e.mapping.contract.canonical_keys if k.category=="SEMANTIC_PRIMITIVE")
    finding=e.behavioral(key.key_id)
    assert finding["finding"]=="ACTIVE"
    assert all(a["normal_output"]!=a["counterfactual_output"] for a in finding["attempts"] if a["changed"])


def test_array_all_four_primitives_and_exact_operator_distinction(engines):
    p=engines["ARRAY"].mapping.program
    assert {r["capability"] for r in p.semantic_records}=={"negative_value","even_value","large_magnitude","value_exceeds_index"}
    # A distinct <= predicate must never be recognized as the frozen < primitive.
    p=compile_program("SEMCORE-900-ARRAY_LE",dev.SOURCES["ARRAY_LE"])
    assert "negative_value" not in {r["capability"] for r in p.semantic_records}
    assert any(i.operation=="LE" for i in p.items)


def test_repeated_primitives_remain_distinct_and_joint(engines):
    e=engines["REPEAT"]
    records=e.mapping.program.semantic_records
    assert len(records)==2 and len({r["contract_occurrence_id"] for r in records})==2
    key=next(k for k in e.mapping.contract.canonical_keys if k.category=="SEMANTIC_PRIMITIVE")
    result=e.behavioral(key.key_id)
    assert len(result["occurrences"])==2 and result["finding"]=="ACTIVE"
    assert all(a["occurrence_ids"]==result["occurrences"] for a in result["attempts"])
    assert result["witness"]["counterfactual_output"]=="37"


def test_semantic_predicate_input_edge_changes_actual_comparison(engines):
    p=engines["ODD"].mapping.program
    edge=p.semantic_records[0]["input_ports"][0]["edge_id"]
    normal=execute(p,dev.RAW[1])
    counter=execute(p,dev.RAW[1],occurrences=(edge,),replacement=0)
    assert normal.output=="39" and counter.output=="37"


def test_indicator_every_write_range_and_predicate_edge(engines):
    p=engines["INITIAL"].mapping.program
    proof=p.indicator_proofs["sem900Hit"]
    assert proof["range"]==[0,1] and len(proof["writes"])==2
    assert len(proof["predicate_definitions"])==1
    edge=p.item(proof["predicate_definitions"][0]["edge_id"])
    assert edge.operation=="PREDICATE_TO_INDICATOR" and edge.datatype=="BOOLEAN"
    key=next(k for k in engines["INITIAL"].mapping.contract.canonical_keys if k.operation=="PREDICATE_TO_INDICATOR")
    assert engines["INITIAL"].behavioral(key.key_id)["finding"]=="ACTIVE"


@pytest.mark.parametrize("name",["PREFIX","TWO_PASS","REVERSE","REPEAT"])
def test_state_families_normal_compiler_agreement_and_reaching_writers(engines,name):
    e=engines[name];p=e.mapping.program
    assert p.state_analysis["loop_fixed_points"]
    for case in e.cases:
        normal=e.normals[case.case_id]
        assert normal.output==str(dev.expected(name,case.raw_input))
        for row in normal.state_trace:
            if row["kind"]=="READ":
                assert row["writer"] in p.state_analysis["read_definitions"][row["reader"]]
                edge=p.item(row["state_edge"])
                assert edge.source==row["writer"] and edge.target==row["reader"]
    update=next(k for k in e.mapping.contract.canonical_keys if k.operation=="ACCUMULATE" and k.result_role=="DISPLAYED_ACCUMULATOR")
    result=e.behavioral(update.key_id)
    assert result["finding"]=="ACTIVE"
    assert all(a["occurrence_ids"]==result["occurrences"] for a in result["attempts"])


def test_prefix_reads_prior_iteration_not_later_current_write(engines):
    e=engines["PREFIX"];normal=e.normals[dev.CASE_IDS[2]]
    seen=[r for r in normal.state_trace if r["kind"]=="READ" and r["binding"]=="sem900Seen"]
    # Q at positions 2 and 5 sees 1 and 2 earlier odd positions, respectively.
    assert [r["value"] for r in seen]==[1,2]


def test_two_pass_final_product_depends_on_both_registers(engines):
    p=engines["TWO_PASS"].mapping.program
    normal=engines["TWO_PASS"].normals[dev.CASE_IDS[-1]]
    writes={r["writer"] for r in normal.state_trace if r["kind"]=="WRITE" and r["binding"] in {"sem900Left","sem900Right"}}
    assert writes<=normal.output_dependencies
    assert len(writes)==2
    key=next(k for k in engines["TWO_PASS"].mapping.contract.canonical_keys if k.operation=="MUL")
    assert engines["TWO_PASS"].behavioral(key.key_id)["finding"]=="ACTIVE"


def test_maximal_initial_accumulator_has_no_fabricated_parent(engines):
    e=engines["INITIAL"]
    attrs=[k for k in e.mapping.contract.canonical_keys if k.attribute_parent_kind=="INITIAL_ACCUMULATOR"]
    assert len(attrs)==1 and attrs[0].computed_integer==-21 and attrs[0].parent_key_id is None
    finding=e.attribute(attrs[0].key_id)
    assert finding["finding"]=="COVERED"
    assert finding["witness"]["initialization_value"]==-21
    assert finding["witness"]["initial_accumulator_binding"]=="sem900Total"
    assert finding["witness"]["parent_occurrence_id"] in finding["witness"]["output_dependencies"]
    assert not any(k.computed_integer in {13,8} for k in e.mapping.contract.canonical_keys)


def test_maximal_computed_threshold_has_exact_active_parent(engines):
    e=engines["THRESHOLD"]
    key=next(k for k in e.mapping.contract.canonical_keys if k.computed_integer==17)
    result=e.attribute(key.key_id)
    assert result["finding"]=="COVERED"
    oid=result["witness"]["occurrence_id"];spec=e.mapping.program.attribute_specs[oid]
    assert spec["parent_occurrence"] in e.mapping.key_occurrences[key.parent_key_id]
    assert e.behavioral(key.parent_key_id)["witness"]["case_id"]==result["witness"]["case_id"]
    assert len(spec["members"])>1


def test_output_categories_and_exact_sentinel_are_bound_to_executed_output(engines):
    e=engines["INITIAL"]
    for key in e.mapping.contract.canonical_keys:
        if key.evidence_kind=="OUTPUT_ATTRIBUTE":
            result=e.output_attribute(key.key_id)
            assert result["finding"]=="COVERED"
            assert result["output_attachment"]["occurrence_id"]==e.mapping.program.output_id
            if result["exact_sentinel"] is not None:
                assert result["witness"]["expected_output_value"]=="-19"
    zero=next(k for k in engines["TWO_PASS"].mapping.contract.canonical_keys if k.operation=="OUTPUT_ZERO")
    assert engines["TWO_PASS"].output_attribute(zero.key_id)["finding"]=="COVERED"


def test_alpha_semantic_state_mapping_is_total(engines):
    c=engines["FLOW_AND"].mapping.contract
    proof=reconcile_complete_mapping(c,dev.SOURCES["ALPHA"])
    assert len(proof.correspondence)==len(c.ir.items)
    assert len({b for _,b in proof.correspondence})==len(c.ir.items)


def test_computed_value_mapping_accounts_for_constant_interiors(engines):
    e=engines["INITIAL"]
    proof=reconcile_complete_mapping(e.mapping.contract,dev.SOURCES["INITIAL_FOLDED"])
    assert proof.equivalence_proofs
    key=next(k for k in e.mapping.contract.canonical_keys if k.computed_integer==-21)
    assert proof.key_occurrences[key.key_id]
    for rule in proof.equivalence_proofs:
        assert rule["frozen_rule_id"]=="V3.3" and rule["computed_integer"]==-21
        assert rule["contract_accounted_occurrences"]


@pytest.mark.parametrize("name,context,operators",[("FLOW_AND","LOCAL_PAIR_JOINT",("&&","*")),("FLOW_OR","BOOLEAN_OR",("||",">"))])
def test_source_proved_local_boolean_alternatives(engines,name,context,operators):
    p=engines[name].mapping.program
    proof=source_flow_equivalence(p,expression(p,operators[0]),p,expression(p,operators[1]),context=context)
    assert proof["finding"]=="EQUIVALENT",proof
    assert proof["frozen_rule_id"]=="V3.3" and proof["preconditions_and_flow_proofs"]
    assert proof["not_complete_graph_equivalence"] and len(proof["affected_occurrences"])==2


def test_ambiguous_indicator_attachment_and_caller_proofs_fail_closed(engines):
    p=engines["AMBIGUOUS"].mapping.program
    product=expression(p,"*")
    proof=source_flow_equivalence(p,product,p,product,context="LOCAL_PAIR_JOINT")
    assert proof["finding"]=="UNRESOLVED" and "ambiguous" in proof["reason"]
    with pytest.raises(SchemaError):expressions_equivalent(product,product,left_symbols=p.symbols,right_symbols=p.symbols,
        context="LOCAL_PAIR_JOINT",indicators=frozenset(p.indicator_proofs))


@pytest.mark.parametrize("name",["BAD_IMPORT","BAD_LOOP"])
def test_unsupported_syntax_remains_fail_closed(name):
    with pytest.raises(SchemaError):compile_program("SEMCORE-900-"+name,dev.SOURCES[name])


def test_untyped_and_nonterminating_interventions_are_unresolved(engines):
    p=engines["ODD"].mapping.program
    predicate=next(i for i in p.items if i.category=="SEMANTIC_PRIMITIVE")
    with pytest.raises(SchemaError,match="UNTYPED_INTERVENTION"):
        execute(p,dev.RAW[1],occurrences=(predicate.occurrence_id,),replacement=1)
    loop=next(i for i in p.items if i.operation=="BOUNDED_LOOP")
    with pytest.raises(SchemaError,match="BUDGET"):
        execute(p,dev.RAW[1],occurrences=(loop.occurrence_id,),replacement=True,max_steps=100)
    key=next(k for k in engines["ODD"].mapping.contract.canonical_keys if k.operation=="BOUNDED_LOOP")
    assert engines["ODD"].behavioral(key.key_id)["finding"]=="UNRESOLVED"


def test_unsupported_attribute_parent_has_explicit_unresolved_inventory(engines):
    p=engines["INITIAL"].mapping.program
    unsupported=[s for oid,s in p.attribute_specs.items() if p.item(oid).essential and not s["parent_ontology_supported"]]
    assert unsupported
    assert all(s["parent_occurrence"] is not None and s["exact_required_lexeme"] is None for s in unsupported)


def test_runtime_mapping_mutation_cannot_supply_activity(engines):
    e=engines["ODD"];p=e.mapping.program
    key=next(k for k in e.mapping.contract.canonical_keys if k.category=="SEMANTIC_PRIMITIVE")
    original=dict(p.primitive_aliases)
    try:
        p.primitive_aliases.clear()
        with pytest.raises(ClosureError,match="IR changed"):
            e.behavioral(key.key_id)
    finally:p.primitive_aliases.update(original)


def test_local_flow_cannot_cross_loop_state_contexts(engines):
    p=engines["TWO_PASS"].mapping.program
    exprs=[x for top in p.statements for x in _walk_stmt(top) if isinstance(x,Expr) and x.kind=="BINARY" and x.value=="=="]
    proof=source_flow_equivalence(p,exprs[0],p,exprs[1],context="LOCAL_PAIR_JOINT")
    assert proof["finding"]=="UNRESOLVED" and "loop/state contexts" in proof["reason"]
    p=engines["FLOW_AND"].mapping.program
    proof=source_flow_equivalence(p,expression(p,"&&"),p,expression(p,"*"),context="LOCAL_PAIR_JOINT",alpha_map={})
    assert proof["finding"]=="UNRESOLVED" and "alpha mapping" in proof["reason"]


def test_saved_artifacts_bind_actual_outputs_and_fail_closed_gates():
    import hashlib
    folder=dev.ROOT/"research/implementation_notes/coverage_v3_semantic_core"
    gates=json.loads((folder/"semantic_gate_evidence.json").read_bytes())
    expected_gates={"PRIMITIVE_EXTRACTION_COMPLETE","INDICATOR_EXTRACTION_COMPLETE","STATE_GRAPH_COMPLETE",
        "ESSENTIALITY_ENGINE_COMPLETE","VALUE_LITERAL_ATTACHMENT_COMPLETE","OUTPUT_ATTACHMENT_COMPLETE",
        "V32_SEMANTIC_MAPPING_COMPLETE","V33_REQUIRED_EQUIVALENCE_COMPLETE"}
    assert {g["gate"] for g in gates["gates"]}==expected_gates
    assert len(gates["gates"])==8
    assert not gates["all_semantic_gates_pass"] and not gates["authoritative_population_recount_performed"]
    assert gates["population_status"]=="V3_5_POPULATION_UNRESOLVED"
    assert all((g["status"]=="UNRESOLVED")==bool(g["remaining_evidence_obligations"]) for g in gates["gates"])
    extraction=json.loads((folder/"primitive_indicator_extraction.json").read_bytes())
    case_sets={}
    for record in extraction["records"]:
        for artifact in record["bound_inputs"]:
            ref=artifact["artifact_reference"];raw=artifact["exact_utf8_content"].encode()
            assert hashlib.sha256(raw).hexdigest()==ref["sha256"]
            if ref["artifact_role"]=="CASE_SET":case_sets[record["program_id"]]=json.loads(raw)
    traces=json.loads((folder/"state_essentiality_traces.json").read_bytes())
    for record in traces["records"]:
        cases={c["case_id"]:c for c in case_sets[record["program_id"]]["cases"]}
        for normal in record["normal_cases"]:
            assert normal["actual_normal_output"]==normal["actual_compiler_output"]==cases[normal["case_id"]]["expected_output"]
            assert normal["input"]==cases[normal["case_id"]]["input"]
        for finding in record["behavioral_findings"]:
            for attempt in finding.get("attempts",[]):
                assert set(attempt["occurrence_ids"])==set(finding["occurrences"])
                assert attempt["changed"]==(attempt["normal_output"]!=attempt["counterfactual_output"])
        for witness in record.get("stateful_counterfactual_witnesses",[]):
            assert witness["actual_normal_output"]!=witness["actual_counterfactual_output"]
            assert witness["counterfactual_state_trace"]
