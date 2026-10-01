"""Serialized attacks with explicit independent intended rejection reasons."""
from copy import deepcopy
from self_learning_ai.conf1_v3.requirements import digest

INTENT={
 "CALLER_FORGED_ACTIVE":"ESSENTIALITY_STATUS_OR_REASON_FORGE",
 "CALLER_FORGED_OUTPUT_CHANGED":"ESSENTIALITY_CASE_SCHEMA",
 "MISSING_MAPPED_OCCURRENCE":"ESSENTIALITY_JOINT_OCCURRENCE_SET_MISMATCH",
 "EXTRA_UNRELATED_OCCURRENCE":"ESSENTIALITY_JOINT_OCCURRENCE_SET_MISMATCH",
 "WRONG_TYPE":"ESSENTIALITY_INTERVENTION_TYPE_OR_POLICY_MISMATCH",
 "STALE_STATE":"STATE_GRAPH_OR_EDGE_INVENTORY_MISMATCH",
 "WRONG_LOOP":"ESSENTIALITY_JOINT_OCCURRENCE_SET_MISMATCH",
 "CROSS_PASS":"ESSENTIALITY_JOINT_OCCURRENCE_SET_MISMATCH",
 "UNRELATED_STATE_CHANGE":"ESSENTIALITY_COUNTERFACTUAL_RUNTIME_STATE_MISMATCH",
 "NORMAL_COMPILER_DISAGREEMENT":"NORMAL_COMPILER_REFERENCE_DISAGREEMENT",
 "DEAD_CASE_MISLABELED_INACTIVE":"ESSENTIALITY_STATUS_OR_REASON_FORGE",
 "REPEATED_OCCURRENCE_OMITTED":"ESSENTIALITY_JOINT_OCCURRENCE_SET_MISMATCH",
 "NORMAL_COUNTERFACTUAL_CASE_MISMATCH":"ESSENTIALITY_SAME_CASE_IDENTITY_MISMATCH",
 "RAW_OUTPUT_DIFFERENCE_INVALID_INTERVENTION":"ESSENTIALITY_JOINT_OCCURRENCE_SET_MISMATCH",
 "FABRICATED_REFERENCE_ONLY":"ESSENTIALITY_REFERENCE_ONLY_ESCAPE",
 "UNSUPPORTED_INTERVENTION":"ESSENTIALITY_POLICY_AUTHORIZATION_MISMATCH",
 "FORGED_SAFE_INTERVENTION":"ESSENTIALITY_INTERVENTION_SCHEMA",
 "SCIENTIFIC_TRAINING_PROMOTION":"ESSENTIALITY_SCIENTIFIC_LAYER_FORGE",
 "SCIENTIFIC_EVALUATION_PROMOTION":"ESSENTIALITY_SCIENTIFIC_LAYER_FORGE",
 "MISSING_NORMAL_EVENT":"ESSENTIALITY_NORMAL_EVENT_MISMATCH",
 "WRONG_STATE_EPOCH":"ESSENTIALITY_COUNTERFACTUAL_RUNTIME_STATE_MISMATCH",
 "DROPPED_REQUIREMENT":"ESSENTIALITY_REQUIREMENT_INVENTORY_MISMATCH",
 "FORGED_SCIENTIFIC_CLOSURE":"ESSENTIALITY_SCIENTIFIC_LAYER_FORGE",
}


def mutate(base,label):
    e=deepcopy(base)
    active=next(f for f in e["findings"] if f["cases"][0]["status"]=="ACTIVE" and
        f["policy"]["ordered_replacements"]==[0,1] and f["bound_requirement"]["capability"]["result_type"]=="INTEGER")
    case=active["cases"][0];attempt=case["attempts"][0]
    joint=next(f for f in e["findings"] if f["cases"][0]["attempts"] and len(f["bound_requirement"]["joint_occurrences"])>1)
    dead=next(c for f in e["findings"] for c in f["cases"] if c["reason"]=="NO_ACTIVITY_EVIDENCE_ON_THIS_CASE")
    if label=="CALLER_FORGED_ACTIVE":dead.update(status="ACTIVE",reason="VALID_SAME_CASE_OUTPUT_CHANGE_WITH_NORMAL_EVENT")
    elif label=="CALLER_FORGED_OUTPUT_CHANGED":case["output_changed"]=True
    elif label in {"MISSING_MAPPED_OCCURRENCE","REPEATED_OCCURRENCE_OMITTED"}:joint["cases"][0]["attempts"][0]["intervention"]["occurrences"].pop()
    elif label in {"EXTRA_UNRELATED_OCCURRENCE","WRONG_LOOP","CROSS_PASS","RAW_OUTPUT_DIFFERENCE_INVALID_INTERVENTION"}:
        # A real occurrence from another bound semantic/state/control site, not
        # an arbitrary unknown ID. Two-pass base makes cross-pass distinguishable.
        if label in {"WRONG_LOOP","CROSS_PASS"}:
            primitives=[f for f in e["findings"] if f["bound_requirement"]["capability"]["category"]=="SEMANTIC_PRIMITIVE"]
            attempt=primitives[0]["cases"][0]["attempts"][0]
            foreign=primitives[1]["bound_requirement"]["joint_occurrences"][0]
        else:foreign=next(o for f in e["findings"] for o in f["bound_requirement"]["joint_occurrences"] if o not in attempt["intervention"]["occurrences"])
        attempt["intervention"]["occurrences"].append(foreign)
    elif label=="WRONG_TYPE":attempt["intervention"]["replacement"]=False
    elif label=="STALE_STATE":e["state"]["state_graph"]["required_state_edges"].pop()
    elif label in {"UNRELATED_STATE_CHANGE","WRONG_STATE_EPOCH"}:
        old=attempt["runtime_ref"];runtime=e["runtimes"].pop(old)
        if label=="UNRELATED_STATE_CHANGE":runtime["state"]["trace"][0]["value"]=9999
        else:
            next(t for t in runtime["state"]["trace"] if t["loop_context"])["loop_context"][0]["iteration"]=9999
        new=digest(runtime);e["runtimes"][new]=runtime
        for f in e["findings"]:
            for c in f["cases"]:
                if c["normal_ref"]==old:c["normal_ref"]=new
                for a in c["attempts"]:
                    if a["runtime_ref"]==old:a["runtime_ref"]=new
    elif label=="NORMAL_COMPILER_DISAGREEMENT":e["compiler"]["observations"][0]["output"]="9999"
    elif label=="DEAD_CASE_MISLABELED_INACTIVE":dead.update(status="INACTIVE",reason="CAPABILITY_PROVED_INACTIVE")
    elif label=="NORMAL_COUNTERFACTUAL_CASE_MISMATCH":attempt["raw_input"]=e["state"]["executions"][1]["raw_input"]
    elif label=="FABRICATED_REFERENCE_ONLY":e["reference_only_escape"]=True
    elif label=="UNSUPPORTED_INTERVENTION":active["policy"]["mode"]="ARBITRARY_SOURCE_EDIT"
    elif label=="FORGED_SAFE_INTERVENTION":attempt["intervention"]["safe_intervention"]=True
    elif label in {"SCIENTIFIC_TRAINING_PROMOTION","SCIENTIFIC_EVALUATION_PROMOTION"}:e["scope"]=label.removesuffix("_PROMOTION")
    elif label=="MISSING_NORMAL_EVENT":case["normal_events"]=[]
    elif label=="DROPPED_REQUIREMENT":e["findings"].pop()
    elif label=="FORGED_SCIENTIFIC_CLOSURE":e["scientific_instance_closure"]="PASS"
    else:raise ValueError(label)
    return e
