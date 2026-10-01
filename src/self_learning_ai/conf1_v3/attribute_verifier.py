"""Read-only saved attribute verifier. No constructor imports or PASS trust.

Independently reconstructs declared requirements and checks serialized fields,
then replays the committed essentiality verifier. Shared parser, state/runtime,
attachment and declaration-reference kernels are explicit, not two interpreters.
"""
from .attribute_semantics import value_requirements,value_facts,output_facts
from .attribute_reference import output_plan,integer_text
from .essentiality_semantics import context,SCIENTIFIC
from .essentiality_verifier import verify_essentiality_evidence
from .projection_binding_verifier import equal
from .projection_grammar import require,development_identity


def verify_attribute_evidence(a):
    require(set(a)=={"schema_version","artifact_kind","scope","essentiality","prospective_output","prospective_literals","values","outputs","scientific_value_closure","scientific_output_closure","comprehensive_reference_only"}
            and a["schema_version"]==1 and a["artifact_kind"]=="DEVELOPMENT_ONLY_VALUE_OUTPUT_EVIDENCE","ATTRIBUTE_EVIDENCE_KIND_SCHEMA")
    require(a["scope"]=="DEVELOPMENT_ONLY" and a["scientific_value_closure"]==a["scientific_output_closure"]==SCIENTIFIC and a["comprehensive_reference_only"] is False,"ATTRIBUTE_SCIENTIFIC_OR_REFERENCE_PROMOTION")
    development_identity(a["prospective_output"])
    e=a["essentiality"];p,g,c=context(e["mapping"],e["state"],e["compiler"])
    requirements=value_requirements(e,a["prospective_literals"])
    require(len(requirements)==len(a["values"]),"VALUE_REQUIREMENT_INVENTORY_MISMATCH")
    for r,row in zip(requirements,a["values"]):
        require(equal(r,row["requirement"]),"VALUE_REQUIREMENT_KIND_OR_IDENTITY_MISMATCH")
        actual=value_facts(r,e,p,g,c)
        if actual["status"]=="UNRESOLVED" and row.get("status")=="COVERED":
            require(False,actual["reason"])
        w=row.get("witness");v=actual["witness"]
        if w and v:
            checks=[("program_id","VALUE_CROSS_PROGRAM_ATTACHMENT"),("source_sha256","VALUE_SOURCE_IDENTITY_MISMATCH"),("case_id","VALUE_EXECUTED_CASE_MISMATCH"),
                    ("active_parent","VALUE_EXACT_ACTIVE_PARENT_WITNESS_MISMATCH"),
                    ("initial_state","VALUE_EXACT_INITIAL_STATE_MISMATCH"),("output_dependencies","VALUE_OUTPUT_DEPENDENCY_MISMATCH")]
            for field,reason in checks:require(equal(w.get(field),v[field]),reason)
            for field,reason in (("occurrence_id","VALUE_WRONG_OCCURRENCE"),("parent_occurrence","VALUE_WRONG_PARENT_OCCURRENCE"),
                                 ("source_location","VALUE_SOURCE_LOCATION_MISMATCH"),("source_lexeme","VALUE_EXACT_LEXEME_MISMATCH"),
                                 ("computed_integer","VALUE_COMPUTED_VALUE_MISMATCH"),("maximal_constant","VALUE_MAXIMAL_CONSTANT_PROOF_MISMATCH"),
                                 ("exact_required_lexeme","VALUE_EXACT_LEXEME_MISMATCH"),("type","VALUE_TYPE_MISMATCH"),("semantic_role","VALUE_ROLE_MISMATCH")):
                require(equal(w["attachment"].get(field),v["attachment"][field]),reason)
            require(equal(w["attachment"],v["attachment"]),"VALUE_ATTACHMENT_INVENTORY_MISMATCH")
        require(equal(row,{"requirement":r,**actual}),"VALUE_STATUS_OR_EXECUTION_FORGE")
    plan=a["prospective_output"]
    for r in plan["expected_records"]:integer_text(r["expected_output"])
    expected=output_plan(e["state"]["plan"]["declaration"],[r["operation"] for r in plan["requirements"]],
                         [r["raw_input"] for r in e["state"]["executions"]],e["state"]["source_sha256"])
    require(equal(expected,plan),"OUTPUT_EXPECTED_RECORD_OR_CASE_BINDING_MISMATCH")
    require(len(a["outputs"])==len(expected["requirements"]),"OUTPUT_REQUIREMENT_INVENTORY_MISMATCH")
    for req,row in zip(expected["requirements"],a["outputs"]):
        require(equal(req,row["requirement"]),"OUTPUT_REQUIREMENT_KIND_OR_SENTINEL_MISMATCH")
        actual=output_facts(req,expected,e,p,g,c)
        require(len(row["cases"])==len(actual["cases"]),"OUTPUT_CASE_INVENTORY_MISMATCH")
        for supplied,rebuilt in zip(row["cases"],actual["cases"]):
            for f,reason in (("case_id","OUTPUT_WRONG_CASE"),("record_id","OUTPUT_WRONG_EXPECTED_RECORD"),("final_display","OUTPUT_FINAL_DISPLAY_OR_STATE_DEPENDENCY_MISMATCH"),("mechanical_match","OUTPUT_CATEGORY_OR_SENTINEL_MATCH_FORGE")):
                require(equal(supplied.get(f),rebuilt[f]),reason)
        require(equal(row,{"requirement":req,**actual}),"OUTPUT_STATUS_OR_EXECUTION_FORGE")
    # Status-based ACTIVE claims used above are only admissible AFTER this full
    # independent normal/event/counterfactual replay. They are never proof alone.
    verified=verify_essentiality_evidence(e)
    return dict(status="VERIFIED",scope="DEVELOPMENT_ONLY",value_requirements=len(requirements),value_covered=sum(r["status"]=="COVERED" for r in a["values"]),
                output_requirements=len(a["outputs"]),output_covered=sum(r["status"]=="COVERED" for r in a["outputs"]),essentiality_independently_verified=verified["status"],
                constructor_conclusion_trusted=False,scientific_value_closure=SCIENTIFIC,scientific_output_closure=SCIENTIFIC)
