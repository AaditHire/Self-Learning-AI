from copy import deepcopy
import pytest
import state906_inputs as d
from state906_runtime import evidence,mutations,mutate
from self_learning_ai.conf1_v3.state_semantics import static_evidence,trace_agreement
from self_learning_ai.conf1_v3.state_verifier import verify_state_evidence
from self_learning_ai.conf1_v3.core_ir import execute,compile_program
from self_learning_ai.conf1_v3.interfaces import ClosureError,SchemaError

EXPECTED_REASONS={
 "MISSING_INITIALIZATION":"STATE_REQUIRED_INITIALIZATION_MISSING","WRONG_INITIAL_VALUE":"STATE_REQUIRED_INITIAL_VALUE_MISMATCH",
 "WRONG_UPDATE_TARGET":"STATE_WRONG_UPDATE_TARGET","RESET_INSIDE_LOOP":"STATE_UNAUTHORIZED_RESET",
 "AMBIGUOUS_REACHING_DEFINITIONS":"STATE_CONDITIONAL_WRITER_AMBIGUITY","CONDITIONAL_WRITER_AMBIGUITY":"STATE_CONDITIONAL_WRITER_AMBIGUITY",
 "STALE_WRITER":"STATE_STALE_INDICATOR_OR_WRONG_LOOP","UNRELATED_MUTATION":"STATE_EXTRA_LIVE_MUTATION",
 "SAME_OUTPUT_INVALID_RECURRENCE":"STATE_REQUIRED_CONTRIBUTION_MISMATCH","CONTRIBUTION_BYPASSES_PREDICATE":"STATE_REQUIRED_CONTRIBUTION_MISMATCH",
 "WRITE_AFTER_FINAL_READ":"STATE_OUTPUT_NOT_FINAL","DROPPED_REQUIRED_UPDATE":"STATE_REQUIRED_WRITE_ORDER_MISMATCH",
 "PREFIX_PRE_POST_SWAP":"STATE_PREFIX_REQUIRES_PRIOR_STATE","LATER_WRITE_CONTAMINATION":"STATE_PREFIX_REQUIRES_PRIOR_STATE",
 "WRONG_LOOP_READ":"STATE_PREFIX_REQUIRED_READ_MISSING","PREFIX_WRONG_RESET_SCOPE":"STATE_UNAUTHORIZED_RESET",
 "PREFIX_WRONG_INITIALIZATION":"STATE_REQUIRED_INITIAL_VALUE_MISMATCH","WRONG_PASS_ORDER":"STATE_PASS_ORDER_OR_TARGET_MISMATCH",
 "OVERWRITTEN_FIRST_PASS":"STATE_PRESERVED_PASS_STATE_OVERWRITTEN","RECOMPUTED_FIRST_PASS":"STATE_PRESERVED_PASS_STATE_RECOMPUTED",
 "WRONG_FINAL_COMBINATION":"STATE_FINAL_COMBINATION_MISMATCH","CROSS_LOOP_STATE":"STATE_CROSS_LOOP_CONTRIBUTION",
 "UNRELATED_FINAL_STATE":"STATE_STALE_INDICATOR_OR_WRONG_LOOP","INCORRECT_REVERSE_DECREMENT":"STATE_REVERSE_TRAVERSAL_UNPROVED",
 "INCORRECT_REVERSE_BOUND":"STATE_REVERSE_TRAVERSAL_UNPROVED","MISSING_REVERSE_STEP":"STATE_REVERSE_TRAVERSAL_UNPROVED",
 "MUTATED_SOURCE_BOUND":"STATE_IMMUTABLE_BOUND_MUTATED"}

def test_overlap_before_execution():
    assert d.PREFLIGHT["expected_labels_parsed"] is False
    assert d.PREFLIGHT["exact_string_overlap"]==d.PREFLIGHT["recorded_hash_overlap"]==d.PREFLIGHT["recomputed_string_hash_overlap"]==0

@pytest.mark.parametrize("name",d.DECLARATIONS)
@pytest.mark.parametrize("alpha",[False,True])
def test_complete_state_readiness(name,alpha):
    e=evidence(name,alpha);v=verify_state_evidence(e)
    assert v["state_implementation_readiness"]=="STATE_GRAPH_IMPLEMENTATION_READY"
    assert v["scientific_instance_closure"]=="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION"
    for key in ("unresolved_reads","unresolved_writes","extra_live_state_mutations","ambiguous_reaching_definitions"): assert not e["state_graph"][key]
    assert e["state_graph"]["required_state_edges"]==e["state_graph"]["matched_state_edges"]
    assert e["required_computation"]["recurrence_class"]==d.DECLARATIONS[name]["structure"]

@pytest.mark.parametrize("name",d.DECLARATIONS)
def test_pinned_disposable_state_outputs(name):
    from self_learning_ai.conf1_v3.coverage import PinnedCompilerOracle
    oracle=PinnedCompilerOracle(d.ROOT/".tools/jdk-25.0.1+8/bin/java.exe",d.ROOT/".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    for run in evidence(name)["executions"]: assert oracle.run(d.SOURCES[name],run["raw_input"])==run["agreement"]["output"]

@pytest.mark.parametrize("label",d.BAD)
def test_intended_source_adversary_reason(label):
    x=d.BAD[label]
    with pytest.raises((ClosureError,SchemaError),match="^"+EXPECTED_REASONS[label]+"$"):
        static_evidence(d.PLANS[x["name"]],x["source"])

@pytest.mark.parametrize("i",range(10))
def test_serialized_state_mutations(i):
    e=evidence(d.BASE)
    with pytest.raises((ClosureError,SchemaError)): verify_state_evidence(mutate(e,mutations(e)[i]))

def test_verifier_does_not_import_or_call_constructor(monkeypatch):
    e=deepcopy(evidence(d.PREFIX))
    import self_learning_ai.conf1_v3.state_evidence as module
    monkeypatch.setattr(module,"construct_state_evidence",lambda *a:pytest.fail("constructor was called"))
    assert verify_state_evidence(e)["constructor_conclusion_trusted"] is False

@pytest.mark.parametrize("scope",["SCIENTIFIC_TRAINING","SCIENTIFIC_EVALUATION"])
def test_state_scientific_plan_guard_before_parse(scope,monkeypatch):
    import self_learning_ai.conf1_v3.state_semantics as module
    p=deepcopy(d.PLANS[d.BASE]);p["scope"]=scope
    monkeypatch.setattr(module,"compile_program",lambda *a:pytest.fail("scientific source parsed"))
    with pytest.raises(ClosureError,match="SCIENTIFIC_SOURCE_MAPPING_DEFERRED"): static_evidence(p,"FORBIDDEN")

def test_sequential_kill_conditional_union_fixed_point():
    g=evidence(d.BASE)["state_graph"]
    assert g["sequential_kills"] and g["conditional_unions"] and g["loop_fixed_points"]
    for r in g["reads"]:
        if r["binding"]=="st906hitP":
            edges=[e for e in g["required_state_edges"] if e["reader"]==r["reader"]]
            assert len(edges)==2 and all(e["relation"]=="CURRENT_STATE" for e in edges)

def test_prefix_priors_are_not_current_writes():
    g=evidence(d.PREFIX)["state_graph"]
    q=[e for e in g["required_state_edges"] if e["binding"]=="st906seen" and not next(r for r in g["reads"] if r["reader"]==e["reader"])["implicit"]]
    assert {e["relation"] for e in q}=={"INITIAL_OR_SEQUENTIAL_STATE","PRIOR_STATE"}

def test_two_pass_final_reads_preserve_exact_registers():
    e=evidence(d.TWO);g=e["state_graph"];comb=e["required_computation"]["required_updates"][-1]
    r={q["reader"] for q in comb["reads"] if not q["implicit"]}
    assert {x["binding"] for x in g["required_state_edges"] if x["reader"] in r}=={"st906left","st906right"}
    assert any(x["relation"]=="PRESERVED_PASS_STATE" for x in g["required_state_edges"] if x["reader"] in r)

def test_forward_implicit_step_and_update_reads_are_traced():
    e=evidence(d.BASE);kinds={x["kind"] for x in e["executions"][0]["agreement"]["trace"]}
    assert {"IMPLICIT_READ","INDEX_PRIOR_READ","INDEX_INITIALIZE","INDEX_WRITE","LOOP_TEST"}<=kinds

def test_unchanged_default_trace_and_optional_detail():
    p=compile_program(d.PLANS[d.BASE]["program_id"],d.SOURCES[d.BASE]);raw=d.RAW[p.domain][0]
    default=execute(p,raw);detail=execute(p,raw,detailed_state_trace=True)
    assert default.output==detail.output and default.output_dependencies==detail.output_dependencies
    stripped=[{k:v for k,v in t.items() if k not in {"loop_context","sequence"}} for t in detail.state_trace if t["kind"] in {"READ","WRITE","INITIALIZE","INPUT_WRITE"}]
    assert stripped==[{k:v for k,v in t.items() if k!="sequence"} for t in default.state_trace]

def test_same_output_is_not_recurrence_proof():
    x=d.BAD["SAME_OUTPUT_INVALID_RECURRENCE"];raw=d.RAW["numeric_iteration"][1]
    # Both full sources and the boundary raw input are in the preflight inventory.
    p=compile_program(d.PLANS[d.BASE]["program_id"],x["source"])
    assert execute(p,raw).output==evidence(d.BASE)["executions"][1]["agreement"]["output"]
    with pytest.raises(ClosureError,match="STATE_REQUIRED_CONTRIBUTION_MISMATCH"): static_evidence(d.PLANS[d.BASE],x["source"])

def test_runtime_relation_rejects_actual_stale_origin():
    e=evidence(d.BASE);p,g,c=static_evidence(e["plan"],e["source"]);run=execute(p,d.RAW[p.domain][0],detailed_state_trace=True)
    next(t for t in run.state_trace if t["kind"]=="READ")["writer"]="FOREIGN_WRITER"
    with pytest.raises(ClosureError,match="STATE_RUNTIME_STALE_WRITER"): trace_agreement(p,g,run)
