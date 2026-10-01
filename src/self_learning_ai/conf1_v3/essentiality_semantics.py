"""Frozen-authorized DEVELOPMENT behavior primitives, not a scientific gate.

Complete typed mapping and state proof are mandatory. Unsupported constructs
stay unresolved; result type alone NEVER authorizes a mutation.
"""
from dataclasses import asdict
from .projection_grammar import require, development_identity
from .projection_binding_verifier import verify_projection_evidence, equal
from .state_verifier import verify_state_evidence
from .state_semantics import static_evidence, trace_agreement
from .contract_ir import keys_from_ir
from .core_ir import execute
from .interfaces import SchemaError, ClosureError

SCIENTIFIC="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION_AND_VALIDATION"
AUTHORITY="research/protocols/phase3c_conf1_coverage_v3_proposed.md#v35-semantic-activity--closed-two-level-evidence-rule"
EDGES={"INPUT_TO_DECODER","VALUE_TO_PREDICATE","PREDICATE_TO_CONTROL","PREDICATE_TO_INDICATOR","VALUE_TO_OPERATOR","OPERATOR_TO_ACCUMULATOR","CONTROL_TO_UPDATE","LOOP_CARRY","PRIOR_STATE_TO_UPDATE","ACCUMULATOR_TO_OUTPUT"}
NUMERIC={"ADD","SUB","MUL","MOD","NEG"}
BOOLEAN={"AND","OR","NOT","EQ","NE","LT","LE","GT","GE"}


def context(mapping,state,compiler):
    verify_projection_evidence(mapping);verify_state_evidence(state)
    require(equal(mapping["plan_before"],state["plan"]) and mapping["source"]==state["source"],"ESSENTIALITY_SOURCE_MAPPING_STATE_MISMATCH")
    p,g,c=static_evidence(state["plan"],state["source"])
    require(set(compiler)=={"source_sha256","observations","oracle"} and compiler["source_sha256"]==state["source_sha256"] and
            compiler["oracle"]=="PINNED_GOCO_COMPILER", "ESSENTIALITY_COMPILER_BINDING_MISMATCH")
    require(equal([dict(raw_input=r["raw_input"],output=r["agreement"]["output"]) for r in state["executions"]],compiler["observations"]),"NORMAL_COMPILER_REFERENCE_DISAGREEMENT")
    return p,g,c


def bound_capability(mapping,p,requirement_id):
    matches=[b for b in mapping["bindings"] if b["requirement_id"]==requirement_id]
    require(len(matches)==1,"ESSENTIALITY_REQUIREMENT_IDENTITY_MISMATCH")
    b=matches[0];require(b["evidence_kind"]=="BEHAVIORAL","ESSENTIALITY_EVIDENCE_KIND_BOUNDARY")
    keys,sets=keys_from_ir(p,())
    # Prospective one-edge kind selectors bind a typed witness. Capability
    # intervention expands to ALL instances of that same complete atomic key.
    joint={};key_ids=[]
    for oid in b["source_occurrences"]:
        item=p.item(oid)
        def same(i,k):
            return (i.category,i.operation,i.datatype,i.operand_types,i.operand_roles,i.result_role)==(k.category,k.operation,k.result_type,k.operand_types,k.operand_roles,k.result_role)
        found=[k for k in keys if k.evidence_kind=="BEHAVIORAL" and same(item,k)]
        if not found:continue # explicit initialization / pair motif: unsupported
        require(len(found)==1,"ESSENTIALITY_AMBIGUOUS_CANONICAL_KEY")
        k=found[0];key_ids.append(k.key_id)
        # Complete graph mapping retains even dead/unused occurrences. A
        # reusable key must have a live required-computation representative;
        # intervene jointly on every typed instance of that SAME key, including
        # the independently checked inline occurrence in a Boolean region.
        for i in p.items:
            if same(i,k):joint[i.occurrence_id]=i
    items=list(joint.values())
    return dict(requirement_id=requirement_id,evidence_kind="BEHAVIORAL",capability=b["capability"],
        bound_occurrences=b["source_occurrences"],canonical_keys=sorted(set(key_ids)),
        joint_occurrences=[i.occurrence_id for i in items],inventory=[asdict(i) for i in items],
        control_state_context=b["control_state_context"],
        state_context_source="VERIFIED_STATE_GRAPH_AND_REQUIRED_COMPUTATION",
        expansion_rule="ALL_COMPLETE_GRAPH_INSTANCES_OF_IDENTICAL_TYPED_CANONICAL_KEY_WITH_LIVE_REQUIRED_REPRESENTATIVE")


def policy(bound,p):
    cap=bound["capability"];cat=cap["category"];op=cap["operation"];typ=cap["result_type"]
    mode=None;values=[];reason=None
    if cat=="API_DECODER" and (op=="INPUT" or op.startswith("INPUT_DOMAIN:")):
        mode="DOMAIN_INPUT_REPLACEMENT";values=["0","1"] if p.domain=="numeric_iteration" else ["0|0|0|0","1|1|1|1"]
    elif cat=="API_DECODER" and op=="strings.SPLIT":mode="FOUR_FIELD_SPLIT";values=[["0"]*4,["1"]*4]
    elif cat=="API_DECODER" and op in {"strings.TO_NUMBER","ARRAY_INDEX"} and typ=="INTEGER":mode="API_NUMERIC_RESULT";values=[0,1]
    elif cat=="SEMANTIC_PRIMITIVE" and typ=="BOOLEAN":mode="BOOLEAN_DECISION";values=[False,True]
    elif cat=="ATOMIC_OPERATOR" and op in BOOLEAN and typ=="BOOLEAN":mode="BOOLEAN_DECISION";values=[False,True]
    elif cat=="ATOMIC_OPERATOR" and op in NUMERIC and typ=="INTEGER":mode="NUMERIC_OPERATOR_RESULT";values=[0,1]
    elif cat=="GENERIC_CONSTRUCT" and op in {"IF","BOUNDED_LOOP"} and typ=="BOOLEAN":mode="BOOLEAN_DECISION";values=[False,True]
    elif cat=="GENERIC_CONSTRUCT" and op=="ACCUMULATE":mode="CONTRIBUTION_SUPPRESSION";values=[0]
    elif cat=="ATOMIC_CONTROL_DATAFLOW" and op in EDGES:
        if op in {"OPERATOR_TO_ACCUMULATOR","LOOP_CARRY"} and cap["result_role"] in {"ACCUMULATOR","DISPLAYED_ACCUMULATOR"}:mode="CONTRIBUTION_SUPPRESSION";values=[0]
        elif typ=="BOOLEAN":mode="BOOLEAN_DECISION";values=[False,True]
        elif typ=="INTEGER":mode="DIRECTED_NUMERIC_VALUE";values=[0,1]
    if not mode or not bound["joint_occurrences"]:reason="UNSUPPORTED_FROZEN_INTERVENTION"
    # Current kernel suppresses ACCUMULATE/carry, and numeric destination
    # replacement on RHS OPERATOR_TO_ACCUMULATOR is exactly contribution zero.
    return dict(authority=AUTHORITY,mode=mode,ordered_replacements=values,result_type=typ,
        joint_all_instances=True,source_edit=False,unrelated_occurrences_permitted=False,
        soundness="Verified complete typed mapping and required recurrence; mutate only the selected destinations; validate all resulting state relations",
        unsafe="Execution errors/budget exhaustion have no terminal output; force TRUE on a sole-exit loop may not terminate",
        unresolved_reason=reason)


def validate_intervention(bound,pol,request):
    require(set(request)=={"occurrences","replacement","order"},"ESSENTIALITY_INTERVENTION_SCHEMA")
    require(equal(request["occurrences"],bound["joint_occurrences"]),"ESSENTIALITY_JOINT_OCCURRENCE_SET_MISMATCH")
    require(pol["unresolved_reason"] is None,"UNSUPPORTED_FROZEN_INTERVENTION")
    require(type(request["order"]) is int and 0<=request["order"]<len(pol["ordered_replacements"]),"UNSUPPORTED_FROZEN_INTERVENTION")
    require(equal(request["replacement"],pol["ordered_replacements"][request["order"]]),"ESSENTIALITY_INTERVENTION_TYPE_OR_POLICY_MISMATCH")


def runtime_record(p,g,run,intervention=None):
    return dict(output=run.output,output_dependencies=sorted(run.output_dependencies),evaluated=sorted(run.evaluated),
        values=run.values,events=[{**e,"dependencies":sorted(e["dependencies"])} for e in run.events],
        state=trace_agreement(p,g,run,authorized_intervention=intervention),
        occurrence_inventory=list(run.intervention_occurrences),
        interventions=[t for t in run.state_trace if t["kind"]=="INTERVENTION"])


def event_inventory(bound,normal,p,raw):
    ids=set(bound["joint_occurrences"])
    eligible=[e for e in normal["events"] if e["delta"]!=0 and ids&set(e["dependencies"]) and e["occurrence_id"] in normal["output_dependencies"] and
        (p.roles.get(e["register"])=="DISPLAYED_ACCUMULATOR" or e.get("event_kind")=="TWO_PASS_PRODUCT_OUTPUT")]
    if not ids&set(normal["evaluated"]):eligible=[]
    if bound["capability"]["result_type"]=="BOOLEAN" and not any(v is True for oid in ids for v in normal["values"].get(oid,[])):
        eligible=[] # a false predicate masked by another OR operand is no selection event
    if p.domain=="numeric_iteration" and int(raw)==0 and bound["capability"]["category"]=="API_DECODER":eligible=[]
    return eligible


def counterfactual(p,g,bound,pol,raw,request,budget):
    validate_intervention(bound,pol,request)
    require(type(budget) is int and 1<=budget<=100000,"ESSENTIALITY_EXECUTION_BUDGET_INVALID")
    try:
        run=execute(p,raw,occurrences=tuple(request["occurrences"]),replacement=request["replacement"],max_steps=budget,detailed_state_trace=True)
        data=runtime_record(p,g,run,request)
        require(all(t["occurrence"] in request["occurrences"] for t in data["interventions"]),"ESSENTIALITY_UNRELATED_STATE_INTERVENTION")
        return dict(raw_input=raw,intervention=request,execution_status="TERMINATING",reason=None,runtime=data,failure_observations=None)
    except (SchemaError,ClosureError) as exc:
        return dict(raw_input=raw,intervention=request,execution_status="UNRESOLVED",reason=str(exc),runtime=None,
            failure_observations=getattr(exc,"partial_observations",None))


def evaluate_case(p,g,bound,pol,raw,case_id,budget=4096):
    development_identity(case_id);normal=runtime_record(p,g,execute(p,raw,detailed_state_trace=True));events=event_inventory(bound,normal,p,raw)
    attempts=[]
    if pol["unresolved_reason"]:status="UNRESOLVED";reason=pol["unresolved_reason"]
    elif not events:status="UNRESOLVED";reason="NO_ACTIVITY_EVIDENCE_ON_THIS_CASE"
    else:
        status="INACTIVE";reason="CAPABILITY_PROVED_INACTIVE"
        for order,value in enumerate(pol["ordered_replacements"]):
            request=dict(occurrences=list(bound["joint_occurrences"]),replacement=value,order=order)
            a=counterfactual(p,g,bound,pol,raw,request,budget);attempts.append(a)
            if a["execution_status"]!="TERMINATING":status="UNRESOLVED";reason=a["reason"];break
            if normal["output"]!=a["runtime"]["output"]:status="ACTIVE";reason="VALID_SAME_CASE_OUTPUT_CHANGE_WITH_NORMAL_EVENT";break
    return dict(case_id=case_id,raw_input=raw,normal=normal,normal_events=events,attempts=attempts,status=status,reason=reason,
        status_scope="THIS_DEVELOPMENT_CASE_ONLY",budget=budget)
