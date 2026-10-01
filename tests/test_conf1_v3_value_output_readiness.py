from copy import deepcopy
import pytest
import attr908_inputs as d
from attr908_runtime import evidence
from attr908_adversaries import INTENT,mutate,OVERLAP_INTENT,overlap_mutation
from self_learning_ai.conf1_v3.attribute_verifier import verify_attribute_evidence
from self_learning_ai.conf1_v3.attribute_reference import reference_output,output_plan,integer_text,digest_text
from self_learning_ai.conf1_v3.attribute_overlap import compare,permitted_corpus,ZERO_HASH
from self_learning_ai.conf1_v3.attribute_semantics import source_attachment
from self_learning_ai.conf1_v3.core_ir import compile_program
from self_learning_ai.conf1_v3.projection_grammar import development_identity,render_development

def test_exact_zero_causal_preflight():
    p=d.PREFLIGHT
    assert not p["prohibited_collisions"] and len(p["permitted_normative_collisions"])==1
    r=p["permitted_normative_collisions"][0]
    assert r["literal"]=="0" and r["sha256_utf8"]==digest_text("0")==ZERO_HASH
    assert r["requirement_existed_before_overlap"] and r["development_case_id"]=="ATTR908-Zero-CASE-0"
    assert (p["exact_string_overlap"],p["recorded_hash_overlap"],p["recomputed_string_hash_overlap"])==(1,0,1)

def test_protected_metadata_cannot_choose_output():
    old=permitted_corpus(d.ROOT);before=deepcopy(d.OUTPUTS)
    empty=compare(d.inventory(),d.PROSPECTIVE,set())
    normal=compare(d.inventory(),d.PROSPECTIVE,old)
    assert empty["permitted_normative_collisions"]==[] and len(normal["permitted_normative_collisions"])==1
    assert {n:output_plan(q,d.OPERATIONS[n],d.RAW[n],digest_text(d.SOURCES[n])) for n,q in d.DECLARATIONS.items()}==before

@pytest.mark.parametrize("label",OVERLAP_INTENT)
def test_exception_adversary(label):
    args=overlap_mutation(d.inventory(),d.PROSPECTIVE,permitted_corpus(d.ROOT),label)
    with pytest.raises(ValueError,match="^"+OVERLAP_INTENT[label]+"$"):compare(*args)

@pytest.mark.parametrize("name",d.DECLARATIONS)
def test_pinned_development_value_output(name):
    a=evidence(name);v=verify_attribute_evidence(a)
    assert v["status"]=="VERIFIED" and not v["constructor_conclusion_trusted"]
    assert v["output_covered"]==v["output_requirements"]
    assert [o["output"] for o in a["essentiality"]["compiler"]["observations"]]==[str(reference_output(d.DECLARATIONS[name],r)) for r in d.RAW[name]]

@pytest.mark.parametrize("label",INTENT)
def test_attribute_adversary(label):
    name,reason=INTENT[label]
    with pytest.raises(ValueError,match="^"+reason+"$"):verify_attribute_evidence(mutate(evidence(name),label))

def test_maximal_neg_add_sub_mul_not_interior_requirements():
    a=evidence("Const");row=next(r for r in a["values"] if r["requirement"]["key"]["computed_integer"]==-21)
    spec=row["witness"]["attachment"]["maximal_constant"]
    assert len(spec["members"])==4 and row["witness"]["attachment"]["source_lexeme"]=="-(13+8)"
    assert not {13,8}&{r["requirement"]["key"]["computed_integer"] for r in a["values"]}
    p=compile_program(d.DECLARATIONS["Const"]["program_id"],d.SOURCES["Const"])
    inner=next(i for i in p.items if i.operation=="CONSTANT" and i.occurrence_id in spec["members"])
    with pytest.raises(ValueError,match="VALUE_UNSUPPORTED_OR_NONMAXIMAL_ATTACHMENT|VALUE_NONMAXIMAL_CONSTANT"):
        source_attachment(p,inner.occurrence_id,row["requirement"]["key"])
    ops=evidence("Ops");row=next(r for r in ops["values"] if r["requirement"]["key"]["computed_integer"]==10)
    assert row["witness"]["attachment"]["source_lexeme"]=="(13-8)*2"

def test_exact_numeric_and_string_lexemes_not_normalized():
    a=evidence("Lex");r=next(r for r in a["values"] if r["requirement"]["key"]["exact_required_lexeme"])
    assert r["status"]=="COVERED" and r["witness"]["attachment"]["source_lexeme"]=="00013" and r["witness"]["executed_values"]==[13,13,13]
    s=next(r for r in evidence("A")["values"] if r["requirement"]["key"]["exact_required_lexeme"])
    assert s["status"]=="COVERED" and s["witness"]["attachment"]["source_lexeme"]=='"|"'

def test_initial_state_without_fake_parent():
    for n in ("N","A","Two","Reverse"):
        for r in evidence(n)["values"]:
            if r["status"]=="COVERED" and r["requirement"]["key"]["attribute_parent_kind"]=="INITIAL_ACCUMULATOR":
                assert r["witness"]["active_parent"] is None and r["witness"]["initial_state"]["state_edges"]

def test_real_inactive_unresolved_paths_do_not_borrow_activity():
    a=evidence("Inactive");reasons={r["reason"] for r in a["values"] if r["status"]=="UNRESOLVED"}
    assert {"VALUE_PARENT_INACTIVE","VALUE_EXACT_BEHAVIORAL_PARENT_UNBOUND"}<=reasons

@pytest.mark.parametrize("text",["-0","+0","00","0.0"," 0","0\n","１","1e0"])
def test_noncanonical_integer(text):
    with pytest.raises(ValueError,match="OUTPUT_NONCANONICAL_INTEGER"):integer_text(text)

@pytest.mark.parametrize("identity",["CONF1-TR-NU-01","CONF1-ISOLATED-TR-X","CONF1-NC-NU-X"])
def test_scientific_namespace_rejects_before_parse(identity):
    with pytest.raises(ValueError,match="SCIENTIFIC_IDENTITY"):development_identity(identity)

def test_constructor_disabled_readonly_verifier(monkeypatch):
    a=deepcopy(evidence("Const"))
    import self_learning_ai.conf1_v3.attribute_evidence as producer
    monkeypatch.setattr(producer,"construct_attribute_evidence",lambda *a,**k:(_ for _ in ()).throw(AssertionError("producer called")))
    assert verify_attribute_evidence(a)["status"]=="VERIFIED"

def test_actual_unsupported_constant_operation():
    p=compile_program(d.DECLARATIONS["Const"]["program_id"],d.BAD_SOURCES["UNSUPPORTED_CONSTANT"])
    mod=next(i for i in p.items if i.operation=="MOD" and i.kind=="NODE" and p.source[slice(*i.location)]=="13%8")
    key=next(r["requirement"]["key"] for r in evidence("Const")["values"] if r["requirement"]["key"]["computed_integer"]==-21)
    with pytest.raises(ValueError,match="VALUE_UNSUPPORTED_OR_NONMAXIMAL_ATTACHMENT"):source_attachment(p,mod.occurrence_id,key)

def test_actual_reassociation_not_admitted():
    from self_learning_ai.conf1_v3.state_semantics import static_evidence
    from self_learning_ai.conf1_v3.projection_grammar import derive_projection_plan
    with pytest.raises(ValueError,match="STATE_REQUIRED_CONTRIBUTION_MISMATCH"):
        static_evidence(derive_projection_plan(d.REASSOC),d.BAD_SOURCES["REASSOCIATION"])

def test_actual_extra_live_display_rejects():
    with pytest.raises(ValueError,match="final display"):
        compile_program(d.DECLARATIONS["N"]["program_id"],d.BAD_SOURCES["EXTRA_DISPLAY"])

def test_pure_unused_handling_preserved():
    a=evidence("Unused")
    extras=[i for i in a["essentiality"]["mapping"]["source_graph"]["nodes"] if i["proof"]=="PURE_UNUSED_NO_TYPED_PATH_TO_OUTPUT"]
    assert extras and a["comprehensive_reference_only"] is False

def test_folding_computed_only_not_numeric_lexeme():
    a=evidence("ConstFold")
    r=next(r for r in a["values"] if r["requirement"]["key"]["computed_integer"]==-21)
    assert r["status"]=="COVERED" and r["witness"]["attachment"]["source_lexeme"]=="-21"
    assert a["essentiality"]["mapping"]["claims"][0]["catalog_rule"]=="WHOLLY_INTEGER_CONSTANT_NEG_ADD_SUB_MUL_COMPUTED_KEY_ONLY"
    lex=next(r["requirement"]["key"] for r in evidence("Lex")["values"] if r["requirement"]["key"]["exact_required_lexeme"])
    p=compile_program(d.DECLARATIONS["Lex"]["program_id"],d.BAD_SOURCES["NORMALIZED_EXACT_LITERAL"])
    oid=next(i.occurrence_id for i in p.items if i.kind=="NODE" and i.operation=="CONSTANT" and i.value=="13")
    with pytest.raises(ValueError,match="VALUE_EXACT_LEXEME_MISMATCH"):source_attachment(p,oid,lex)

def test_exact_literal_grouping_is_not_normalized():
    r=next(r["requirement"] for r in evidence("Lex")["values"] if r["requirement"]["key"]["exact_required_lexeme"])
    p=compile_program(d.DECLARATIONS["Lex"]["program_id"],d.BAD_SOURCES["GROUPED_EXACT_LITERAL"])
    oid=next(i.occurrence_id for i in p.items if i.kind=="NODE" and i.operation=="CONSTANT" and i.value=="00013")
    with pytest.raises(ValueError,match="VALUE_LITERAL_EXPRESSION_CONTEXT_MISMATCH"):
        source_attachment(p,oid,r["key"],r["exact_literal_context"])
