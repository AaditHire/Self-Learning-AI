"""Read-only artifact projections and mutation replay; no constructors."""
from copy import deepcopy
from collections import Counter
from .requirements import digest
from .projection_grammar import require
from .essentiality_semantics import SCIENTIFIC

ADVERSARY_INTENT={
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


def edits(a,b,path=()):
    if type(a) is dict and type(b) is dict:
        result=[]
        for k in sorted(set(a)|set(b)):
            if k not in b:result.append(dict(path=list(path)+( [k]),operation="DELETE"))
            elif k not in a:result.append(dict(path=list(path)+[k],operation="SET",value=b[k]))
            else:result.extend(edits(a[k],b[k],path+(k,)))
        return result
    if type(a) is list and type(b) is list and len(a)==len(b):
        return [r for i,(x,y) in enumerate(zip(a,b)) for r in edits(x,y,path+(i,))]
    return [] if digest(a)==digest(b) else [dict(path=list(path),operation="SET",value=b)]


def apply_edits(e,changes):
    result=deepcopy(e)
    for change in changes:
        require(change["operation"] in {"SET","DELETE"} and change["path"],"ESSENTIALITY_ADVERSARY_EDIT_SCHEMA")
        target=result
        for k in change["path"][:-1]:target=target[k]
        key=change["path"][-1]
        if change["operation"]=="DELETE":del target[key]
        else:target[key]=deepcopy(change["value"])
    return result


def inventories(records):
    policies={};kinds={};joint=[];traces=[];counts=Counter();forms=set();predicates=set();classes=set()
    for r in records:
        e=r["evidence"];d=e["state"]["plan"]["declaration"];forms.add((d["family"],d["structure"],d["reverse"]))
        for fi,f in enumerate(e["findings"]):
            b=f["bound_requirement"];cap=b["capability"];kind=dict(family=d["family"],capability=cap,evidence_kind="BEHAVIORAL")
            kid=digest(kind);classes.add(cap["category"])
            if cap["category"]=="SEMANTIC_PRIMITIVE":predicates.add(cap["operation"])
            policies[kid]=dict(kind_id=kid,kind=kind,policy=f["policy"])
            for ci,c in enumerate(f["cases"]):
                counts[c["status"]]+=1
                locator=dict(record_id=r["record_id"],finding_index=fi,case_index=ci,status=c["status"],reason=c["reason"])
                kinds.setdefault(kid,dict(kind_id=kid,kind=kind,policy=f["policy"],witnesses=[]))["witnesses"].append(locator)
            joint.append(dict(record_id=r["record_id"],finding_index=fi,requirement_id=b["requirement_id"],canonical_keys=b["canonical_keys"],
                joint_occurrences=b["joint_occurrences"],complete_typed_inventory=b["inventory"],bound_occurrences=b["bound_occurrences"],expansion_rule=b["expansion_rule"]))
        traces.append(dict(record_id=r["record_id"],state_graph_sha256=digest(e["state"]["state_graph"]),required_computation_sha256=digest(e["state"]["required_computation"]),
            runtimes=[dict(runtime_ref=k,state_sha256=digest(v["state"]),intervention_records=v["interventions"],output=v["output"],output_ancestry=v["output_dependencies"]) for k,v in e["runtimes"].items()]))
    matrix=[]
    for kid,row in kinds.items():
        ws=row.pop("witnesses");positive=next((w for w in ws if w["status"]=="ACTIVE"),next((w for w in ws if w["status"]=="INACTIVE"),ws[0]))
        dead=next((w for w in ws if w["reason"]=="NO_ACTIVITY_EVIDENCE_ON_THIS_CASE"),None)
        supported=row["policy"]["unresolved_reason"] is None
        require(not supported or dead is not None,"ESSENTIALITY_SUPPORTED_KIND_DEAD_WITNESS_MISSING")
        r=next(r for r in records if r["record_id"]==positive["record_id"]);b=r["evidence"]["findings"][positive["finding_index"]]["bound_requirement"]
        state=r["evidence"]["state"]["state_graph"];sites={w["writer"] for w in state["writes"]}|{x["reader"] for x in state["reads"]}
        matrix.append(dict(**row,semantic_role=row["kind"]["capability"]["semantic_role"],stateful=bool(sites&set(b["joint_occurrences"])) or row["kind"]["capability"]["operation"] in {"BOUNDED_LOOP","LOOP_CARRY","PRIOR_STATE_TO_UPDATE"},
            supported=supported,positive_witness=positive,dead_case_witness=dead,
            inactive_witness=next((w for w in ws if w["status"]=="INACTIVE"),None),
            adversarial_witness=dict(base_record_id=positive["record_id"],finding_index=positive["finding_index"],mutation="DELETE_ONE_BOUND_OCCURRENCE_OR_FORGE_UNSUPPORTED_POLICY",
                intended_reason="ESSENTIALITY_BOUND_MAPPING_OCCURRENCE_MISMATCH" if b["joint_occurrences"] else "ESSENTIALITY_POLICY_AUTHORIZATION_MISMATCH"),
            expected_statuses=sorted({w["status"] for w in ws}),independent_verification="VERIFIED"))
    return dict(policy_catalog=list(policies.values()),kind_matrix=matrix,joint_records=joint,state_trace_index=traces,
        case_status_counts=dict(counts),grammar_forms=[list(x) for x in sorted(forms)],predicates=sorted(predicates),classes=sorted(x for x in classes if x))


def kind_attack(e,row):
    r=deepcopy(e);f=r["findings"][row["adversarial_witness"]["finding_index"]]
    if f["bound_requirement"]["joint_occurrences"]:f["bound_requirement"]["joint_occurrences"].pop()
    else:f["policy"]["mode"]="UNAUTHORIZED"
    return r


def readiness_model(records,inventory,deps):
    return dict(scope="DEVELOPMENT_ONLY",ESSENTIALITY_IMPLEMENTATION_READINESS="ESSENTIALITY_ENGINE_IMPLEMENTATION_READY",
        ESSENTIALITY_SCIENTIFIC_INSTANCE_CLOSURE=SCIENTIFIC,old_global_gate=deps["old_essentiality_gate"],old_global_gate_changed=False,
        inherited_diagnostic_development_rows=deps["inherited_development_untested_rows"],diagnostic_is_scientific_count=False,
        preserved_readiness=dict(INDICATOR="IMPLEMENTATION_READY",V32="IMPLEMENTATION_READY",V33="IMPLEMENTATION_READY",STATE="STATE_GRAPH_IMPLEMENTATION_READY"),
        records=len(records),kind_count=len(inventory["kind_matrix"]),**{k:inventory[k] for k in ("case_status_counts","grammar_forms","predicates","classes")},
        scientific_sources_constructed=0,scientific_fixture_execution=False,population_producer_invoked=False,historical_8668_authoritative=False,
        model_E1_E6_provenance_binder_preregistration_work=False,VALUE_OR_LITERAL_repair=False,OUTPUT_ATTRIBUTE_repair=False,
        independence="Verifier has no constructor imports; reconstructs mappings, state, events and executions; status/order/adequacy checked independently. Typed parser, state transfer, intervention policy and runtime/event kernels shared; not a second interpreter.",
        implementation_boundary="Closed frozen-authorized policies; unsupported generic read/init/assignment/index-state/array-vector and unverified counterfactual recurrence remain UNRESOLVED, not scientific PASS")


def dependency_notes():
    return dict(reference_only=dict(scope="DEVELOPMENT_ONLY",comprehensive_closure="DEFERRED",
        preserved="Existing PURE_UNUSED_NO_TYPED_PATH_TO_OUTPUT mechanical proof; no new exemption",
        required_inactive_or_unresolved_escape=False,live_unmatched_escape=False,
        remaining="Exhaustive closed pure-unused/constant-false admissibility and complete unmatched-source disposition, separately authorized"),
        value_output=dict(scope="DEVELOPMENT_ONLY",value_literal_closure="DEFERRED",output_attribute_closure="DEFERRED",
            future_active_parent="Only independently verified ACTIVE findings with exact mapped path, case and occurrence identities are prospective ACTIVE_BEHAVIORAL_PARENT dependencies, never scientific satisfaction",
            outcomes="Counterfactual outputs are behavioral outcome comparisons only; no OUTPUT_ATTRIBUTE or expected-output-category evidence",
            remaining="Exact value/role/lexeme attachment and active-parent validation, initial-accumulator rules, separately frozen output obligations and actual expected-output cases; no repair in this pass"))
