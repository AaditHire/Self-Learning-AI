"""Development-only essentiality constructor. Conclusions are not proof."""
from .essentiality_semantics import context,bound_capability,policy,evaluate_case,SCIENTIFIC
from .requirements import digest
from .projection_grammar import require
from copy import deepcopy


def construct_essentiality_evidence(mapping,state,compiler,*,budget=4096):
    p,g,c=context(mapping,state,compiler);findings=[];runtimes={}
    def intern(value):
        if value is None:return None
        key=digest(value);runtimes[key]=value;return key
    for b in mapping["bindings"]:
        if b["evidence_kind"]!="BEHAVIORAL":continue
        bound=bound_capability(mapping,p,b["requirement_id"]);pol=policy(bound,p);cases=[]
        for i,r in enumerate(state["executions"]):
            case=evaluate_case(p,g,bound,pol,r["raw_input"],p.program_id+"-CASE-"+str(i),budget)
            case["normal_ref"]=intern(case.pop("normal"))
            for a in case["attempts"]:a["runtime_ref"]=intern(a.pop("runtime"))
            cases.append(case)
        witness=next((c for c in sorted(cases,key=lambda c:c["case_id"].encode()) if c["status"]=="ACTIVE"),None)
        first=dict(case_id=witness["case_id"],intervention_order=witness["attempts"][-1]["intervention"]["order"],
            normal_ref=witness["normal_ref"],counterfactual_ref=witness["attempts"][-1]["runtime_ref"]) if witness else None
        finding="ACTIVE" if witness else "UNRESOLVED" if any(c["status"]=="UNRESOLVED" for c in cases) else "INACTIVE"
        findings.append(dict(bound_requirement=bound,policy=pol,cases=cases,first_active_witness=first,case_set_finding=finding,
            status_scope="DECLARED_DEVELOPMENT_CASE_SET_ONLY"))
    return dict(schema_version=1,artifact_kind="DEVELOPMENT_ONLY_ESSENTIALITY_EVIDENCE",scope="DEVELOPMENT_ONLY",
        mapping=deepcopy(mapping),state=deepcopy(state),compiler=deepcopy(compiler),findings=findings,runtimes=runtimes,
        scientific_instance_closure=SCIENTIFIC,reference_only_escape=False)
