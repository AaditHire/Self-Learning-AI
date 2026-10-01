"""Read-only serialized state replay; no state evidence constructor import."""
from .state_semantics import static_evidence,trace_agreement
from .core_ir import execute
from .projection_grammar import require
from .projection_binding_verifier import equal,digest_source
from .requirements import digest
from copy import deepcopy


def verify_state_evidence(e):
    fields={"schema_version","artifact_kind","scope","plan","source","source_sha256","state_graph","required_computation","executions",
            "projection_provenance","state_implementation_readiness","scientific_instance_closure"}
    require(set(e)==fields and e["schema_version"]==1 and e["artifact_kind"]=="DEVELOPMENT_ONLY_STATE_EVIDENCE","STATE_EVIDENCE_SCHEMA")
    require(e["scope"]=="DEVELOPMENT_ONLY","STATE_SCIENTIFIC_SOURCE_DEFERRED")
    p,graph,certificate=static_evidence(e["plan"],e["source"])
    require(e["source_sha256"]==digest_source(p.source),"STATE_SOURCE_HASH_MISMATCH")
    require(equal(e["state_graph"],graph),"STATE_GRAPH_OR_EDGE_INVENTORY_MISMATCH")
    require(equal(e["required_computation"],certificate),"STATE_REQUIRED_COMPUTATION_CERTIFICATE_MISMATCH")
    require(e["executions"] and len({r["raw_input"] for r in e["executions"]})==len(e["executions"]),"STATE_RUNTIME_WITNESSES_MISSING_OR_DUPLICATED")
    for r in e["executions"]:
        require(set(r)=={"raw_input","agreement"},"STATE_RUNTIME_RECORD_SCHEMA")
        actual=execute(p,r["raw_input"],detailed_state_trace=True)
        require(equal(r["agreement"],trace_agreement(p,graph,actual)),"STATE_RUNTIME_OR_SOURCE_MAP_MISMATCH")
    require(equal(e["projection_provenance"],dict(declaration_sha256=digest(e["plan"]["declaration"]),scientific_slot_binding=None,scientific_expected_row=False)),"STATE_PROJECTION_PROMOTION_OR_PROVENANCE_MISMATCH")
    # Never infer readiness from this asserted field; compare only after every
    # proof and execution was rebuilt. Changing the field cannot make a proof.
    require(e["state_implementation_readiness"]=="STATE_GRAPH_IMPLEMENTATION_READY" and
            e["scientific_instance_closure"]=="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION","STATE_STATUS_LAYER_MISMATCH")
    return dict(status="VERIFIED",scope="DEVELOPMENT_ONLY",state_implementation_readiness="STATE_GRAPH_IMPLEMENTATION_READY",
                scientific_instance_closure="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION",constructor_conclusion_trusted=False,
                required_computation_sha256=digest(certificate),state_graph_sha256=digest(graph),runtime_static_agreement=True,scientific_satisfaction_claims=0)


def state_kind_inventory(e):
    """Development type witnesses; complete instance accounting stays in graph."""
    g=e["state_graph"];c=e["required_computation"];d=e["plan"]["declaration"];rows=[]
    types={w["binding"]:w["datatype"] for w in g["writes"]}
    def add(cls,path,i,details):
        kind=dict(requirement_class=cls,recurrence_class=c["recurrence_class"],family=d["family"],traversal="REVERSE" if d["reverse"] else "FORWARD",**details)
        rows.append(dict(kind_id=digest(kind),kind=kind,proof_locator=path+[i]))
    for i,w in enumerate(g["writes"]):
        op=w["operation"].split(":");add("STATE_WRITE",["state_graph","writes"],i,dict(operation=op[0]+(":"+op[1] if op[0]=="UPDATE" else ""),datatype=w["datatype"],in_loop=w["loop"] is not None))
    for i,r in enumerate(g["reads"]): add("STATE_READ",["state_graph","reads"],i,dict(datatype=types[r["binding"]],implicit=r["implicit"],in_loop=r["loop"] is not None))
    for i,r in enumerate(g["required_state_edges"]): add("STATE_REACHING_RELATION",["state_graph","required_state_edges"],i,dict(datatype=r["datatype"],relation=r["relation"]))
    for i,r in enumerate(g["dependency_edges"]): add("STATE_CONTROL_DATAFLOW",["state_graph","dependency_edges"],i,dict(operation=r["operation"],datatype=r["datatype"],source_role=r["source_role"],target_role=r["target_role"]))
    for i,r in enumerate(g["loop_fixed_points"]): add("LOOP_FIXED_POINT",["state_graph","loop_fixed_points"],i,dict(pass_order=i))
    for i,r in enumerate(g["sequential_kills"]): add("SEQUENTIAL_KILL",["state_graph","sequential_kills"],i,dict(kill_class="NONEMPTY" if r["killed"] else "EMPTY_INITIALIZATION"))
    for i,r in enumerate(g["conditional_unions"]): add("CONDITIONAL_DEFINITION_UNION",["state_graph","conditional_unions"],i,{})
    return rows


def delete_proof(e,locator):
    r=deepcopy(e);target=r
    for x in locator[:-1]: target=target[x]
    target.pop(locator[-1]);return r


def essentiality_dependencies(root):
    """Read-only inherited gap inventory, not activity/intervention production."""
    import json,hashlib
    gate_path=root/"research/implementation_notes/coverage_v3_semantic_core/semantic_gate_evidence.json"
    trace_path=root/"research/implementation_notes/coverage_v3_semantic_core/state_essentiality_traces.json"
    gates=json.loads(gate_path.read_bytes());old=json.loads(trace_path.read_bytes())
    state=next(r for r in gates["gates"] if r["gate"]=="STATE_GRAPH_COMPLETE")
    essential=next(r for r in gates["gates"] if r["gate"]=="ESSENTIALITY_ENGINE_COMPLETE")
    untested=old["untested_behavioral_obligations"]
    categories={category for category in ("SEMANTIC_PRIMITIVE","API_DECODER","ATOMIC_OPERATOR","GENERIC_CONSTRUCT","ATOMIC_CONTROL_DATAFLOW") if any(category in r["key_id"] for r in untested)}
    return dict(scope="DEVELOPMENT_ONLY",state_proof_available=True,required_computation_known_for_disposable_grammar=True,
        intervention_support=dict(existing="Typed occurrence-set force/replace and contribution suppression in core_ir.execute/CoverageEngine; unchanged",
            missing_or_unresolved=essential["remaining_evidence_obligations"],new_intervention_enumeration_performed=False),
        remaining_behavioral_essentiality_classes=sorted(categories),inherited_development_untested_rows=len(untested),
        reference_only_closure="Only existing mechanically proved pure-unused handling exercised; comprehensive remaining closure deferred",
        scientific_essentiality_closure="DEFERRED; development state proofs do not establish V3.5 events/counterfactuals or future scientific mappings",
        old_state_gate=state,old_essentiality_gate=essential,
        inherited_sources=[dict(path=str(p.relative_to(root)).replace("\\","/"),sha256_exact_bytes=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (gate_path,trace_path)],
        population_work_performed=False,essentiality_repair_performed=False)
