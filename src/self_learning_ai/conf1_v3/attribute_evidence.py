"""Producer for DEVELOPMENT attribute evidence; no scientific gate writes."""
from copy import deepcopy
from .essentiality_verifier import verify_essentiality_evidence
from .essentiality_semantics import context,SCIENTIFIC
from .attribute_semantics import value_requirements,value_facts,output_facts
from .attribute_reference import output_plan
from .projection_binding_verifier import equal
from .projection_grammar import require


def construct_attribute_evidence(essentiality,prospective_output,prospective_literals=()):
    verify_essentiality_evidence(essentiality)
    e=essentiality;p,g,c=context(e["mapping"],e["state"],e["compiler"])
    expected=output_plan(e["state"]["plan"]["declaration"],[r["operation"] for r in prospective_output["requirements"]],
                         [r["raw_input"] for r in e["state"]["executions"]],e["state"]["source_sha256"])
    require(equal(expected,prospective_output),"OUTPUT_PROSPECTIVE_PLAN_MISMATCH")
    values=[dict(requirement=r,**value_facts(r,e,p,g,c)) for r in value_requirements(e,prospective_literals)]
    outputs=[dict(requirement=r,**output_facts(r,expected,e,p,g,c)) for r in expected["requirements"]]
    return dict(schema_version=1,artifact_kind="DEVELOPMENT_ONLY_VALUE_OUTPUT_EVIDENCE",scope="DEVELOPMENT_ONLY",essentiality=deepcopy(e),
                prospective_output=deepcopy(expected),prospective_literals=deepcopy(list(prospective_literals)),values=values,outputs=outputs,scientific_value_closure=SCIENTIFIC,scientific_output_closure=SCIENTIFIC,
                comprehensive_reference_only=False)
