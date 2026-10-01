"""Serializable attacks against exact development attribute proof fields."""
from copy import deepcopy

VALUE={
 "FORGED_ACTIVE_PARENT":("N","VALUE_EXACT_ACTIVE_PARENT_WITNESS_MISMATCH"),
 "WRONG_ACTIVE_WITNESS":("N","VALUE_EXACT_ACTIVE_PARENT_WITNESS_MISMATCH"),
 "INACTIVE_PARENT":("Inactive","VALUE_PARENT_INACTIVE"),
 "UNRESOLVED_PARENT":("Inactive","VALUE_EXACT_BEHAVIORAL_PARENT_UNBOUND"),
 "WRONG_OCCURRENCE":("N","VALUE_WRONG_OCCURRENCE"),
 "WRONG_LOOP_PASS":("Two","VALUE_WRONG_PARENT_OCCURRENCE"),
 "NEAREST_TEXT":("N","VALUE_SOURCE_LOCATION_MISMATCH"),
 "NONMAXIMAL_CONSTANT":("Const","VALUE_MAXIMAL_CONSTANT_PROOF_MISMATCH"),
 "WRONG_COMPUTED":("Const","VALUE_COMPUTED_VALUE_MISMATCH"),
 "UNSUPPORTED_CONSTANT_OP":("Const","VALUE_MAXIMAL_CONSTANT_PROOF_MISMATCH"),
 "WRONG_LITERAL_SPELLING":("Lex","VALUE_EXACT_LEXEME_MISMATCH"),
 "FAKE_INITIAL_PARENT":("N","VALUE_EXACT_ACTIVE_PARENT_WITNESS_MISMATCH"),
 "WRONG_INITIAL_VARIABLE":("N","VALUE_EXACT_INITIAL_STATE_MISMATCH"),
 "OUTPUT_INDEPENDENT_VALUE":("N","VALUE_OUTPUT_DEPENDENCY_MISMATCH"),
 "REASSOCIATED_TREE":("Ops","VALUE_MAXIMAL_CONSTANT_PROOF_MISMATCH"),
 "CROSS_PROGRAM_PARENT":("N","VALUE_CROSS_PROGRAM_ATTACHMENT"),
 "WRONG_TYPE":("N","VALUE_TYPE_MISMATCH"),
 "WRONG_ROLE":("N","VALUE_ROLE_MISMATCH"),
 "FORGED_ESSENTIALITY_ACTIVE_STATUS":("Inactive","ESSENTIALITY_STATUS_OR_REASON_FORGE"),
}
OUTPUT={
 "FORGED_CATEGORY_FLAG":("N","OUTPUT_STATUS_OR_EXECUTION_FORGE"),
 "WRONG_CASE":("N","OUTPUT_WRONG_CASE"),
 "WRONG_EXPECTED_RECORD":("N","OUTPUT_WRONG_EXPECTED_RECORD"),
 "WRONG_OUTPUT_NODE":("N","OUTPUT_FINAL_DISPLAY_OR_STATE_DEPENDENCY_MISMATCH"),
 "WRONG_REGISTER_SAME_VALUE":("N","OUTPUT_FINAL_DISPLAY_OR_STATE_DEPENDENCY_MISMATCH"),
 "CATEGORY_MISMATCH":("N","OUTPUT_CATEGORY_OR_SENTINEL_MATCH_FORGE"),
 "SENTINEL_MISMATCH":("Zero","OUTPUT_REQUIREMENT_KIND_OR_SENTINEL_MISMATCH"),
 "NONCANONICAL_SENTINEL":("Zero","noncanonical exact output sentinel"),
 "DEAD_DISPLAY":("N","OUTPUT_FINAL_DISPLAY_OR_STATE_DEPENDENCY_MISMATCH"),
 "COUNTERFACTUAL_OUTPUT_SUBSTITUTE":("N","OUTPUT_EXPECTED_RECORD_OR_CASE_BINDING_MISMATCH"),
 "CROSS_PROGRAM_RECORD":("N","OUTPUT_EXPECTED_RECORD_OR_CASE_BINDING_MISMATCH"),
 "NONCANONICAL_EXPECTED":("Zero","OUTPUT_NONCANONICAL_INTEGER"),
 "EXTRA_LIVE_OUTPUT":("N","OUTPUT_FINAL_DISPLAY_OR_STATE_DEPENDENCY_MISMATCH"),
 "INVALID_COMPUTATION_SAME_VALUE":("N","OUTPUT_FINAL_DISPLAY_OR_STATE_DEPENDENCY_MISMATCH"),
}
CROSS={
 "BEHAVIORAL_AS_VALUE":("N","VALUE_REQUIREMENT_KIND_OR_IDENTITY_MISMATCH"),
 "OUTPUT_AS_VALUE":("N","VALUE_REQUIREMENT_KIND_OR_IDENTITY_MISMATCH"),
 "COUNTERFACTUAL_AS_OUTPUT":("N","OUTPUT_EXPECTED_RECORD_OR_CASE_BINDING_MISMATCH"),
 "OUTPUT_AS_ACTIVE":("N","VALUE_EXACT_ACTIVE_PARENT_WITNESS_MISMATCH"),
 "VALUE_AS_OUTPUT":("N","OUTPUT_REQUIREMENT_KIND_OR_SENTINEL_MISMATCH"),
}
INTENT={**VALUE,**OUTPUT,**CROSS}

def mutate(a,label):
    b=deepcopy(a)
    initial=next(r for r in b["values"] if r["status"]=="COVERED" and r["witness"]["initial_state"])
    active=next((r for r in b["values"] if r["status"]=="COVERED" and r["witness"]["active_parent"]),initial)
    w=active["witness"];at=w["attachment"];out=b["outputs"][0];case=out["cases"][0];display=case["final_display"]
    if label=="FORGED_ACTIVE_PARENT":w["active_parent"]["parent_active"]=True
    elif label=="WRONG_ACTIVE_WITNESS":w["active_parent"]["counterfactual_ref"]=w["active_parent"]["normal_ref"]
    elif label in {"INACTIVE_PARENT","UNRESOLVED_PARENT"}:
        reason="VALUE_PARENT_INACTIVE" if label=="INACTIVE_PARENT" else "VALUE_EXACT_BEHAVIORAL_PARENT_UNBOUND"
        r=next(r for r in b["values"] if r["reason"]==reason);r.update(status="COVERED",witness=deepcopy(w))
    elif label=="WRONG_OCCURRENCE":at["occurrence_id"]=initial["witness"]["attachment"]["occurrence_id"]
    elif label=="WRONG_LOOP_PASS":
        at["parent_occurrence"]=next(r["witness"]["attachment"]["parent_occurrence"] for r in b["values"] if r["status"]=="COVERED" and r["witness"]["active_parent"] and r["requirement"]["key"]["parent_key_id"]==active["requirement"]["key"]["parent_key_id"] and r["witness"]["attachment"]["parent_occurrence"]!=at["parent_occurrence"])
    elif label=="NEAREST_TEXT":at["source_location"]=initial["witness"]["attachment"]["source_location"]
    elif label=="NONMAXIMAL_CONSTANT":at["maximal_constant"]["root_occurrence"]=next(x["occurrence_id"] for x in at["interior"] if x["occurrence_id"]!=at["occurrence_id"])
    elif label=="WRONG_COMPUTED":at["computed_integer"]+=1
    elif label=="UNSUPPORTED_CONSTANT_OP":at["maximal_constant"]["proof"]="DIV is allowed"
    elif label=="WRONG_LITERAL_SPELLING":
        r=next(r for r in b["values"] if r["requirement"]["key"]["exact_required_lexeme"]=="00013");r["witness"]["attachment"]["source_lexeme"]="13"
    elif label=="FAKE_INITIAL_PARENT":initial["witness"]["active_parent"]=deepcopy(w["active_parent"])
    elif label=="WRONG_INITIAL_VARIABLE":initial["witness"]["initial_state"]["binding"]="unrelated_register"
    elif label=="OUTPUT_INDEPENDENT_VALUE":w["output_dependencies"].remove(at["occurrence_id"])
    elif label=="REASSOCIATED_TREE":at["maximal_constant"]["members"].reverse()
    elif label=="CROSS_PROGRAM_PARENT":w["program_id"]="ATTR908-A"
    elif label=="WRONG_TYPE":at["type"]="BOOLEAN"
    elif label=="WRONG_ROLE":at["semantic_role"]="UNRELATED_STATE"
    elif label=="FORGED_ESSENTIALITY_ACTIVE_STATUS":
        from self_learning_ai.conf1_v3.attribute_semantics import value_facts
        from self_learning_ai.conf1_v3.essentiality_semantics import context
        e=b["essentiality"]
        case=next(c for f in e["findings"] for c in f["cases"] if c["status"]=="INACTIVE")
        case.update(status="ACTIVE",reason="VALID_SAME_CASE_OUTPUT_CHANGE_WITH_NORMAL_EVENT")
        p,g,c=context(e["mapping"],e["state"],e["compiler"])
        # A hostile producer repairs every dependent claim/hash. Only actual
        # independent essentiality replay can reject this forged activity.
        b["values"]=[dict(requirement=r["requirement"],**value_facts(r["requirement"],e,p,g,c)) for r in b["values"]]
    elif label=="FORGED_CATEGORY_FLAG":out["category_match"]=True
    elif label=="WRONG_CASE":case["case_id"]="ATTR908-N-CASE-999"
    elif label=="WRONG_EXPECTED_RECORD":case["record_id"]="f"*64
    elif label=="WRONG_OUTPUT_NODE":display["occurrence_id"]=initial["witness"]["attachment"]["parent_occurrence"]
    elif label=="WRONG_REGISTER_SAME_VALUE":display["structural_dependency"]["reads"][0]["binding"]="unrelated_register"
    elif label=="CATEGORY_MISMATCH":case["mechanical_match"]="NO_MATCH"
    elif label=="SENTINEL_MISMATCH":b["outputs"][-1]["requirement"]["exact_sentinel"]="-13138"
    elif label=="NONCANONICAL_SENTINEL":
        b["prospective_output"]["requirements"][-1]["operation"]="OUTPUT_EXACT_SENTINEL:-013139"
    elif label=="DEAD_DISPLAY":display["executed"]=False
    elif label in {"COUNTERFACTUAL_OUTPUT_SUBSTITUTE","COUNTERFACTUAL_AS_OUTPUT"}:
        b["prospective_output"]["expected_records"][0]["oracle"]="BEHAVIORAL_COUNTERFACTUAL"
    elif label=="CROSS_PROGRAM_RECORD":b["prospective_output"]["expected_records"][0]["program_id"]="ATTR908-A"
    elif label=="NONCANONICAL_EXPECTED":b["prospective_output"]["expected_records"][0]["expected_output"]="-0"
    elif label=="EXTRA_LIVE_OUTPUT":display["extra_live_outputs"]=[display["occurrence_id"]]
    elif label=="INVALID_COMPUTATION_SAME_VALUE":display["structural_dependency"]["reachable_nodes"]=[]
    elif label in {"BEHAVIORAL_AS_VALUE","OUTPUT_AS_VALUE"}:active["requirement"]["evidence_kind"]="BEHAVIORAL" if label=="BEHAVIORAL_AS_VALUE" else "OUTPUT_ATTRIBUTE"
    elif label=="OUTPUT_AS_ACTIVE":w["active_parent"]=deepcopy(case)
    elif label=="VALUE_AS_OUTPUT":out["requirement"]["evidence_kind"]="VALUE_OR_LITERAL_ATTRIBUTE"
    else:raise AssertionError(label)
    return b

OVERLAP_INTENT={"ZERO_SOURCE":"PROHIBITED_ATTRIBUTE_OVERLAP","ZERO_INPUT":"PROHIBITED_ATTRIBUTE_OVERLAP","ZERO_EXPRESSION":"PROHIBITED_ATTRIBUTE_OVERLAP",
 "NO_ZERO_REQUIREMENT":"ZERO_WITHOUT_PROSPECTIVE_REQUIREMENT","WRONG_ZERO_CASE":"OVERLAP_WRONG_CASE","FORGED_EXCEPTION":"OVERLAP_FIELD_SCHEMA",
 "WRONG_LITERAL_ALLOWED_HASH":"OVERLAP_LITERAL_HASH_MISMATCH","WRONG_FIELD_ALLOWED_HASH":"PROHIBITED_ATTRIBUTE_OVERLAP",
 "OTHER_OUTPUT":"PROHIBITED_ATTRIBUTE_OVERLAP","ALL_CANONICAL_INTEGERS":"PROHIBITED_ATTRIBUTE_OVERLAP"}

def overlap_mutation(inventory,prospective,old,label):
    from self_learning_ai.conf1_v3.attribute_reference import digest_text,output_plan
    from self_learning_ai.conf1_v3.attribute_overlap import ZERO_HASH
    inv=deepcopy(inventory);ps=deepcopy(prospective);corpus=set(old)
    z=next(r for r in inv["expected_outputs"] if r["value"]=="0")
    if label in {"ZERO_SOURCE","ZERO_INPUT","ZERO_EXPRESSION","WRONG_FIELD_ALLOWED_HASH"}:
        field={"ZERO_SOURCE":"sources","ZERO_INPUT":"raw_inputs","ZERO_EXPRESSION":"expressions","WRONG_FIELD_ALLOWED_HASH":"bindings"}[label]
        inv.setdefault(field,[]).append(dict(value="0",sha256_utf8=ZERO_HASH));corpus.add("0")
    elif label=="NO_ZERO_REQUIREMENT":
        p=next(p for p in ps if p["declaration"]["program_id"]==z["program_id"]);p["operations"].remove("OUTPUT_ZERO")
        p["output_plan"]=output_plan(p["declaration"],p["operations"],p["raw_inputs"],digest_text(p["source"]))
    elif label=="WRONG_ZERO_CASE":z["case_id"]="ATTR908-Zero-CASE-999"
    elif label=="FORGED_EXCEPTION":z["justification"]="FROZEN_CANONICAL_ZERO_OUTPUT"
    elif label=="WRONG_LITERAL_ALLOWED_HASH":z["value"]="1"
    elif label in {"OTHER_OUTPUT","ALL_CANONICAL_INTEGERS"}:
        corpus.add(next(r["value"] for r in inv["expected_outputs"] if r["value"]!="0"))
    else:raise AssertionError(label)
    return inv,ps,corpus
