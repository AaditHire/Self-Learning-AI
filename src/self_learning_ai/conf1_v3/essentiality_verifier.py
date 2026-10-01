"""Read-only replay, no evidence-constructor imports or final-status trust.

Reconstructs mappings/state, policy and runtime via shared frozen kernels.
Status/event adequacy/order are checked here independently of the constructor.
Pinned compiler observations are audited by the saved-artifact checker and tests.
"""
from .essentiality_semantics import (context,bound_capability,policy,counterfactual,
    runtime_record,event_inventory,SCIENTIFIC,validate_intervention)
from .core_ir import execute
from .projection_grammar import require,development_identity
from .projection_binding_verifier import equal
from .requirements import digest


def verify_essentiality_evidence(e):
    require(set(e)=={"schema_version","artifact_kind","scope","mapping","state","compiler","findings","runtimes","scientific_instance_closure","reference_only_escape"}
        and e["schema_version"]==1 and e["artifact_kind"]=="DEVELOPMENT_ONLY_ESSENTIALITY_EVIDENCE","ESSENTIALITY_EVIDENCE_SCHEMA")
    require(e["scope"]=="DEVELOPMENT_ONLY" and e["scientific_instance_closure"]==SCIENTIFIC,"ESSENTIALITY_SCIENTIFIC_LAYER_FORGE")
    require(e["reference_only_escape"] is False,"ESSENTIALITY_REFERENCE_ONLY_ESCAPE")
    p,g,c=context(e["mapping"],e["state"],e["compiler"])
    ids=[b["requirement_id"] for b in e["mapping"]["bindings"] if b["evidence_kind"]=="BEHAVIORAL"]
    require([f["bound_requirement"]["requirement_id"] for f in e["findings"]]==ids,"ESSENTIALITY_REQUIREMENT_INVENTORY_MISMATCH")
    for f,rid in zip(e["findings"],ids):
        bound=bound_capability(e["mapping"],p,rid);pol=policy(bound,p)
        require(equal(bound,f["bound_requirement"]),"ESSENTIALITY_BOUND_MAPPING_OCCURRENCE_MISMATCH")
        require(equal(pol,f["policy"]),"ESSENTIALITY_POLICY_AUTHORIZATION_MISMATCH")
    require(all(digest(v)==k for k,v in e["runtimes"].items()),"ESSENTIALITY_RUNTIME_HASH_MISMATCH")
    used=set();summary=[]
    for f,rid in zip(e["findings"],ids):
        require(set(f)=={"bound_requirement","policy","cases","first_active_witness","case_set_finding","status_scope"},"ESSENTIALITY_FINDING_SCHEMA")
        bound=bound_capability(e["mapping"],p,rid);pol=policy(bound,p)
        require(equal(bound,f["bound_requirement"]),"ESSENTIALITY_BOUND_MAPPING_OCCURRENCE_MISMATCH")
        require(equal(pol,f["policy"]),"ESSENTIALITY_POLICY_AUTHORIZATION_MISMATCH")
        require(len(f["cases"])==len(e["state"]["executions"]),"ESSENTIALITY_CASE_INVENTORY_MISMATCH")
        for i,(case,input_record) in enumerate(zip(f["cases"],e["state"]["executions"])):
            require(set(case)=={"case_id","raw_input","normal_ref","normal_events","attempts","status","reason","status_scope","budget"},"ESSENTIALITY_CASE_SCHEMA")
            development_identity(case["case_id"])
            raw=input_record["raw_input"]
            require(case["raw_input"]==raw and case["case_id"]==p.program_id+"-CASE-"+str(i),"ESSENTIALITY_SAME_CASE_IDENTITY_MISMATCH")
            require(case["status_scope"]=="THIS_DEVELOPMENT_CASE_ONLY","ESSENTIALITY_GLOBAL_INACTIVITY_FORGE")
            require(type(case["budget"]) is int and 1<=case["budget"]<=100000,"ESSENTIALITY_EXECUTION_BUDGET_INVALID")
            normal=runtime_record(p,g,execute(p,raw,detailed_state_trace=True));ref=case["normal_ref"];used.add(ref)
            require(ref in e["runtimes"] and equal(e["runtimes"][ref],normal),"ESSENTIALITY_NORMAL_RUNTIME_STATE_MISMATCH")
            eligible=event_inventory(bound,normal,p,raw)
            require(equal(eligible,case["normal_events"]),"ESSENTIALITY_NORMAL_EVENT_MISMATCH")
            actual=[]
            if pol["unresolved_reason"]:status="UNRESOLVED";reason=pol["unresolved_reason"]
            elif not eligible:status="UNRESOLVED";reason="NO_ACTIVITY_EVIDENCE_ON_THIS_CASE"
            else:
                status="INACTIVE";reason="CAPABILITY_PROVED_INACTIVE"
                for order,value in enumerate(pol["ordered_replacements"]):
                    request=dict(occurrences=list(bound["joint_occurrences"]),replacement=value,order=order)
                    if len(case["attempts"])>order:
                        supplied=case["attempts"][order]
                        require(supplied["raw_input"]==raw,"ESSENTIALITY_SAME_CASE_IDENTITY_MISMATCH")
                        validate_intervention(bound,pol,supplied["intervention"])
                        require(equal(supplied["intervention"],request),"ESSENTIALITY_INTERVENTION_ORDER_MISMATCH")
                    a=counterfactual(p,g,bound,pol,raw,request,case["budget"])
                    runtime=a.pop("runtime");rref=digest(runtime) if runtime is not None else None;a["runtime_ref"]=rref
                    if runtime is not None:
                        used.add(rref)
                        require(rref in e["runtimes"] and equal(e["runtimes"][rref],runtime),"ESSENTIALITY_COUNTERFACTUAL_RUNTIME_STATE_MISMATCH")
                    actual.append(a)
                    if a["execution_status"]!="TERMINATING":status="UNRESOLVED";reason=a["reason"];break
                    if normal["output"]!=runtime["output"]:status="ACTIVE";reason="VALID_SAME_CASE_OUTPUT_CHANGE_WITH_NORMAL_EVENT";break
            require(equal(actual,case["attempts"]),"ESSENTIALITY_COUNTERFACTUAL_ATTEMPT_INVENTORY_MISMATCH")
            require(case["status"]==status and case["reason"]==reason,"ESSENTIALITY_STATUS_OR_REASON_FORGE")
            summary.append(dict(requirement_id=rid,case_id=case["case_id"],status=status,reason=reason))
        witness=next((c for c in sorted(f["cases"],key=lambda c:c["case_id"].encode()) if c["status"]=="ACTIVE"),None)
        first=dict(case_id=witness["case_id"],intervention_order=witness["attempts"][-1]["intervention"]["order"],
            normal_ref=witness["normal_ref"],counterfactual_ref=witness["attempts"][-1]["runtime_ref"]) if witness else None
        finding="ACTIVE" if witness else "UNRESOLVED" if any(c["status"]=="UNRESOLVED" for c in f["cases"]) else "INACTIVE"
        require(equal(first,f["first_active_witness"]) and finding==f["case_set_finding"] and f["status_scope"]=="DECLARED_DEVELOPMENT_CASE_SET_ONLY","ESSENTIALITY_CASE_SET_OR_FIRST_WITNESS_FORGE")
    require(used==set(e["runtimes"]),"ESSENTIALITY_UNRELATED_RUNTIME_RECORD")
    return dict(status="VERIFIED",scope="DEVELOPMENT_ONLY",cases=summary,constructor_conclusion_trusted=False,
        scientific_instance_closure=SCIENTIFIC,scientific_satisfaction_claims=0)
