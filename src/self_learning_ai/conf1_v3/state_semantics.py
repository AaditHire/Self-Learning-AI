"""Closed DEVELOPMENT state kernel, independent of evidence constructors.

Structured least-fixed-point facts retain an iteration epoch. A legal branch
union is represented, not guessed away. Source shape proves its legitimacy.
No execution result determines a recurrence or a required state relation.
"""
from .core_ir import compile_program, ungroup, integer_constant
from .goco import _walk_expr
from .interfaces import SchemaError, rid
from .projection_grammar import grammar, require, development_identity
from .projection_binding_verifier import verify_projection_plan, reference_sites, indicator_foundations, equal
from .requirements import expression


def source_program(plan, source):
    verify_projection_plan(plan); development_identity(source)
    try: return compile_program(plan["program_id"],source)
    except SchemaError as exc:
        reason=str(exc)
        if "reverse" in reason: reason="STATE_REVERSE_TRAVERSAL_UNPROVED"
        elif "forward" in reason or "forward bounds" in reason: reason="STATE_FORWARD_TRAVERSAL_UNPROVED"
        elif "final display" in reason: reason="STATE_OUTPUT_NOT_FINAL"
        elif "input binding must not be mutated" in reason: reason="STATE_IMMUTABLE_BOUND_MUTATED"
        raise SchemaError(reason) from exc


def analyze_state(p):
    """An independently rebuilt state graph, including implicit +=/step reads.

    Facts (writer, epoch) have finite height; transfer is kill, conditional
    union, and loop entry/backedge union. Epochs distinguish the same static
    writer in the current and a previous iteration. No variable spelling is
    used to infer this distinction.
    """
    statements={}; contexts={}; writers={}; reads={}; loops=[]; controls={}
    def index(rows,loop=None,branches=()):
        for s in rows:
            if s.kind=="IMPORT": continue
            oid=p.node_ids[id(s)]; statements[oid]=s; contexts[oid]=loop; controls[oid]=list(branches)
            if s.kind=="LOOP":
                loops.append(oid)
                if s.value=="FORWARD":
                    ini,step=p.index_nodes[oid]
                    for w,operation in ((ini,"INDEX_INITIALIZE"),(step,"INDEX_STEP")):
                        writers[w]=dict(binding=s.loop_index,operation=operation,loop=oid,controls=[],location=list(p.item(w).location))
                    reads[step]=dict(binding=s.loop_index,implicit=True,consumer=step,loop=oid,controls=[])
            if s.kind in {"DECLARE","INPUT","UPDATE"}:
                name=s.value.split(":")[1] if s.kind=="DECLARE" else s.expressions[0].value
                writers[oid]=dict(binding=name,operation=s.kind+":"+s.value,loop=loop,controls=list(branches),location=list(p.item(oid).location))
                if s.kind=="UPDATE" and s.value!="=":
                    reads[oid]=dict(binding=name,implicit=True,consumer=oid,loop=loop,controls=list(branches))
            for root in s.expressions[1:] if s.kind=="UPDATE" else () if s.kind=="INPUT" else s.expressions:
                for e in _walk_expr(root):
                    if e.kind=="ID" and e.value in p.symbols and id(e) in p.node_ids:
                        r=p.node_ids[id(e)]
                        reads[r]=dict(binding=e.value,implicit=False,consumer=oid,loop=oid if s.kind=="LOOP" else loop,controls=list(branches))
            index(s.children,oid if s.kind=="LOOP" else loop,branches+(oid,) if s.kind=="IF" else branches)
    index(p.statements)
    reached={r:set() for r in reads}; headers={}; joins=[]; kills=[]
    def join(a,b): return {n:set(a.get(n,set()))|set(b.get(n,set())) for n in set(a)|set(b)}
    def expr(e,env):
        for c in _walk_expr(e):
            if c.kind=="ID" and c.value in p.symbols and id(c) in p.node_ids:
                reached[p.node_ids[id(c)]].update(env.get(c.value,set()))
    def freeze(env): return {n:[dict(writer=w,epoch=epoch) for w,epoch in sorted(f)] for n,f in sorted(env.items())}
    def transfer(rows,incoming,loop=None,collect=False):
        env={n:set(f) for n,f in incoming.items()}
        for s in rows:
            if s.kind=="IMPORT": continue
            oid=p.node_ids[id(s)]
            if s.kind=="LOOP":
                pre={n:set(f) for n,f in env.items()}
                if s.value=="FORWARD":
                    expr(s.expressions[0],pre);pre[s.loop_index]={(p.index_nodes[oid][0],"BEFORE_LOOP")}
                header=pre
                for iteration in range(2*len(writers)+2):
                    expr(s.expressions[-1],header)
                    after=transfer(s.children,header,oid)
                    if s.value=="FORWARD":
                        step=p.index_nodes[oid][1];reached[step].update(after.get(s.loop_index,set()))
                        after[s.loop_index]={(step,"CURRENT_ITERATION")}
                    back={n:{(w,"PREVIOUS_ITERATION" if writers[w]["loop"]==oid and epoch=="CURRENT_ITERATION" else epoch) for w,epoch in facts} for n,facts in after.items()}
                    newer=join(pre,back)
                    if newer==header: break
                    header=newer
                else: raise SchemaError("STATE_FIXED_POINT_UNRESOLVED")
                exit_env={n:{(w,"PASS_FINAL" if writers[w]["loop"]==oid else epoch) for w,epoch in facts} for n,facts in header.items()}
                headers[oid]=dict(loop=oid,iterations=iteration+1,entry=freeze(pre),header=freeze(header),backedge=freeze(back),exit=freeze(exit_env))
                transfer(s.children,header,oid,collect)
                env=exit_env
            elif s.kind=="IF":
                expr(s.expressions[0],env);yes=transfer(s.children,env,loop,collect);merged=join(env,yes)
                if collect: joins.append(dict(control=oid,incoming=freeze(env),taken=freeze(yes),joined=freeze(merged)))
                env=merged
            else:
                for root in s.expressions[1:] if s.kind=="UPDATE" else () if s.kind=="INPUT" else s.expressions: expr(root,env)
                if oid in writers:
                    name=writers[oid]["binding"]
                    if oid in reads: reached[oid].update(env.get(name,set()))
                    if collect: kills.append(dict(writer=oid,binding=name,killed=freeze({name:env.get(name,set())})[name]))
                    env[name]={(oid,"CURRENT_ITERATION" if loop else "INITIAL_OR_SEQUENTIAL")}
        return env
    transfer(p.statements,{},collect=True)
    edges=[]; read_rows=[]
    for r,meta in sorted(reads.items()):
        facts=reached[r]; require(facts,"STATE_UNRESOLVED_READ: "+r)
        relations=[]
        for w,epoch in sorted(facts):
            require(w in writers and writers[w]["binding"]==meta["binding"],"STATE_WRITER_BINDING_MISMATCH")
            phase=("PRIOR_STATE" if epoch=="PREVIOUS_ITERATION" and writers[w]["loop"]==meta["loop"] else
                   "CURRENT_STATE" if epoch=="CURRENT_ITERATION" and writers[w]["loop"]==meta["loop"] else
                   "PRESERVED_PASS_STATE" if epoch=="PASS_FINAL" else "INITIAL_OR_SEQUENTIAL_STATE")
            eid=rid("DEVELOPMENT_STATE_EDGE",[p.program_id,w,r,epoch])
            row=dict(edge_id=eid,writer=w,reader=r,binding=meta["binding"],datatype=p.symbols[meta["binding"]],epoch=epoch,relation=phase,
                     source_state_node=rid("DEVELOPMENT_STATE_NODE",[p.program_id,w,"WRITE"]),target_state_node=rid("DEVELOPMENT_STATE_NODE",[p.program_id,r,"READ"]),
                     defining_loop=writers[w]["loop"],reading_loop=meta["loop"],controls=meta["controls"])
            edges.append(row);relations.append(eid)
        read_rows.append(dict(reader=r,**meta,relations=relations,location=list(p.item(r).location)))
    # Compare the independently computed writer sets with the old IR analysis.
    # The implicit forward-step read is new, and is not fabricated as an old edge.
    for r,meta in reads.items():
        old=p.state_analysis["update_definitions" if meta["implicit"] else "read_definitions"].get(r)
        if old is not None: require(set(old)=={w for w,epoch in reached[r]},"STATE_EXISTING_IR_REACHING_DISAGREEMENT")
        else: require(r in {x[1] for x in p.index_nodes.values()},"STATE_EXISTING_READ_UNACCOUNTED")
    nodes=[dict(writer=w,**meta,datatype=p.symbols[meta["binding"]]) for w,meta in sorted(writers.items())]
    state_nodes=[dict(node_id=rid("DEVELOPMENT_STATE_NODE",[p.program_id,w["writer"],"WRITE"]),node_kind="WRITE",**w) for w in nodes]
    state_nodes += [dict(node_id=rid("DEVELOPMENT_STATE_NODE",[p.program_id,r["reader"],"READ"]),node_kind="READ",**r) for r in read_rows]
    dependency_edges=[dict(edge_id=e.occurrence_id,operation=e.operation,source=e.source,target=e.target,port=e.port,
                           datatype=e.datatype,source_role=list(e.operand_roles),target_role=e.result_role)
                      for e in p.items if e.kind=="EDGE" and e.operation!="PRIOR_STATE_TO_UPDATE"]
    return dict(rule="SEQUENTIAL_KILL_CONDITIONAL_UNION_EPOCH_LOOP_LEAST_FIXED_POINT",writes=nodes,reads=read_rows,
                required_state_nodes=state_nodes,matched_state_nodes=state_nodes,required_state_edges=edges,matched_state_edges=edges,
                dependency_edges=dependency_edges,loop_fixed_points=[headers[o] for o in loops],conditional_unions=joins,sequential_kills=kills,
                unresolved_reads=[],unresolved_writes=[],extra_live_state_mutations=[],ambiguous_reaching_definitions=[])


def required_computation(plan,p,graph):
    """Prove expected source recurrence before assigning its class.

    Prospective grammar is the obligation, not a caller label. All statements,
    contribution trees and order must match; phases then prove prefix prior
    reads and pass-final preservation. No final output value is consulted.
    """
    rows,symbols,_=grammar(plan["declaration"]);d=plan["declaration"]
    require(len(symbols)==len(p.symbols),"STATE_BINDING_INVENTORY_MISMATCH")
    names=dict(zip(symbols,p.symbols)); flat=[]; expected=[]; actual_paths={}
    def walk(block,prefix="",loop=None):
        for i,s in enumerate(block):
            path=prefix+"/s"+str(i);actual_paths[path]=s;flat.append((s,loop,path))
            walk(s.children,path+"/body",p.node_ids[id(s)] if s.kind=="LOOP" else loop)
    walk(p.statements)
    def declared(block,prefix="",loop=None):
        for i,s in enumerate(block):
            path=prefix+"/s"+str(i);expected.append((s,loop,path));declared(s["children"],path+"/body",path if s["kind"]=="LOOP" else loop)
    declared(rows)
    state={names[n] for n in ("total","seen","left","right") if n in names}
    inits={s.value.split(":")[1]:s for s,loop,path in flat if s.kind=="DECLARE"}
    for n in state:
        require(n in inits and bool(inits[n].expressions),"STATE_REQUIRED_INITIALIZATION_MISSING")
        require(integer_constant(inits[n].expressions[0])==(d["offset"] if n==names["total"] else 0),"STATE_REQUIRED_INITIAL_VALUE_MISMATCH")
    for s,loop,path in flat:
        if s.kind=="UPDATE" and s.expressions[0].value in state and s.value=="=":
            raise SchemaError("STATE_UNAUTHORIZED_RESET" if loop else "STATE_PRESERVED_PASS_STATE_OVERWRITTEN")
    edge_by_id={e["edge_id"]:e for e in graph["required_state_edges"]}
    for r in graph["reads"]:
        if r["binding"] in {names["hitP"],names["hitQ"]}:
            require(all(edge_by_id[e]["relation"]=="CURRENT_STATE" for e in r["relations"]),"STATE_STALE_INDICATOR_OR_WRONG_LOOP")
    expected_counts={n:sum(a["kind"]=="UPDATE" and names[a["expressions"][0]]==n for a,l,path in expected) for n in p.symbols}
    actual_counts={n:sum(s.kind=="UPDATE" and s.expressions[0].value==n for s,l,path in flat) for n in p.symbols}
    actual_loops=[s for s in p.statements if s.kind=="LOOP"]
    require(len(actual_loops)==(2 if d["structure"]=="TWO_PASS" else 1),"STATE_LOOP_PASS_COUNT_MISMATCH")
    if d["structure"]=="PREFIX":
        counter=names["seen"];total=names["total"]
        q_reads=[r for r in graph["reads"] if r["binding"]==counter and not r["implicit"] and
                 any(s.kind=="UPDATE" and s.expressions[0].value==total and p.node_ids[id(s)]==r["consumer"] for s,_,_ in flat)]
        require(len(q_reads)==1,"STATE_PREFIX_REQUIRED_READ_MISSING")
        edge_by_id={e["edge_id"]:e for e in graph["required_state_edges"]}
        relations=[edge_by_id[e] for e in q_reads[0]["relations"]]
        require(all(e["relation"] in {"PRIOR_STATE","INITIAL_OR_SEQUENTIAL_STATE"} for e in relations),"STATE_PREFIX_REQUIRES_PRIOR_STATE")
        require(any(e["relation"]=="PRIOR_STATE" for e in relations),"STATE_PREFIX_PRIOR_RECURRENCE_MISSING")
    if d["structure"]=="TWO_PASS":
        for loop,target in zip(actual_loops,(names["left"],names["right"])):
            if target==names["right"]:
                require(not any(s.kind=="UPDATE" and s.expressions[0].value==names["left"] and l==p.node_ids[id(loop)] for s,l,path in flat),"STATE_PRESERVED_PASS_STATE_RECOMPUTED")
            writes=[s for s,l,path in flat if s.kind=="UPDATE" and s.value=="+=" and l==p.node_ids[id(loop)]]
            require(len(writes)==1 and writes[0].expressions[0].value==target,"STATE_PASS_ORDER_OR_TARGET_MISMATCH")
        final_updates=[s for s,l,path in flat if s.kind=="UPDATE" and l is None and s.expressions[0].value==names["total"]]
        require(len(final_updates)==1,"STATE_FINAL_COMBINATION_MISSING")
        e=ungroup(final_updates[0].expressions[1])
        require(e.kind=="BINARY" and e.value=="*" and [ungroup(c).value for c in e.children]==[names["left"],names["right"]],"STATE_FINAL_COMBINATION_MISMATCH")
        final_reads=[r for r in graph["reads"] if r["consumer"]==p.node_ids[id(final_updates[0])] and not r["implicit"]]
        edge_by_id={e["edge_id"]:e for e in graph["required_state_edges"]}
        require(all(any(edge_by_id[x]["relation"]=="PRESERVED_PASS_STATE" for x in r["relations"]) for r in final_reads),"STATE_PASS_FINAL_PRESERVATION_UNPROVED")
    if any(actual_counts[n]>expected_counts[n] for n in p.symbols):
        if any(actual_counts[n]<expected_counts[n] for n in p.symbols): raise SchemaError("STATE_WRONG_UPDATE_TARGET")
        extra_bindings={n for n in p.symbols if actual_counts[n]>expected_counts[n]}
        conditional=any(sum(s.kind=="UPDATE" and s.value=="=" and s.expressions[0].value==n for s,l,path in flat)>
                        sum(a["kind"]=="UPDATE" and a["value"]=="=" and names[a["expressions"][0]]==n for a,l,path in expected) for n in extra_bindings)
        raise SchemaError("STATE_CONDITIONAL_WRITER_AMBIGUITY" if conditional else "STATE_EXTRA_LIVE_MUTATION")
    # Check updates at grammatical sites before the full shape proof to retain
    # a semantic rejection reason for the targeted adversaries.
    def signature(e,rename):
        e=ungroup(e)
        return (e.kind,rename.get(e.value,e.value),tuple(signature(c,rename) for c in e.children))
    for a,loop,path in expected:
        if a["kind"]!="UPDATE": continue
        b=actual_paths.get(path)
        require(b is not None and b.kind=="UPDATE","STATE_REQUIRED_WRITE_ORDER_MISMATCH")
        require(b.expressions[0].value==names[a["expressions"][0]],"STATE_WRONG_UPDATE_TARGET")
        require(b.value==a["value"],"STATE_REQUIRED_UPDATE_RECURRENCE_MISMATCH")
        if loop and any(r["consumer"]==p.node_ids[id(b)] and any(edge_by_id[e]["relation"]=="PRESERVED_PASS_STATE" for e in r["relations"]) for r in graph["reads"]):
            raise SchemaError("STATE_CROSS_LOOP_CONTRIBUTION")
        require(signature(b.expressions[1],{})==signature(expression(a["expressions"][1]),names),"STATE_REQUIRED_CONTRIBUTION_MISMATCH")
    if len(flat)!=len(expected):
        extra=[s for s,l,path in flat if s.kind=="UPDATE" and path not in {q for a,l,q in expected if a["kind"]=="UPDATE"}]
        raise SchemaError("STATE_CONDITIONAL_WRITER_AMBIGUITY" if any(l and s.kind=="IF" for s,l,path in flat) and extra else "STATE_EXTRA_LIVE_MUTATION")
    try: sites,stmts,bijection=reference_sites(plan,p)
    except Exception as exc:
        from .interfaces import ClosureError
        if not isinstance(exc,(ClosureError,SchemaError)): raise
        raise SchemaError("STATE_REQUIRED_COMPUTATION_SOURCE_MISMATCH") from exc
    foundations=indicator_foundations(plan,p,sites,stmts,bijection)
    # Every live write must be declared or an implicit loop-index definition.
    expected_writes={p.node_ids[id(s)] for s,l,path in flat if s.kind in {"DECLARE","INPUT","UPDATE"}}
    expected_writes.update(x for pair in p.index_nodes.values() for x in pair)
    require({w["writer"] for w in graph["writes"]}==expected_writes,"STATE_EXTRA_OR_MISSING_WRITE")
    update_records=[]
    for s,loop,path in flat:
        if s.kind!="UPDATE" or s.expressions[0].value not in state: continue
        oid=p.node_ids[id(s)]
        update_records.append(dict(writer=oid,target=s.expressions[0].value,operator=s.value,loop=loop,grammar_path=path,
            contribution_root=p.node_ids[id(ungroup(s.expressions[1]))],implicit_prior_read=oid,
            recurrence=dict(next_value_operator="ADD_PRIOR_STATE" if s.value=="+=" else s.value,contribution_tree=signature(s.expressions[1],{})),
            reads=[r for r in graph["reads"] if r["consumer"]==oid],controls=next(w["controls"] for w in graph["writes"] if w["writer"]==oid)))
    loop_proofs=[]
    for order,s in enumerate(actual_loops):
        oid=p.node_ids[id(s)];cond=ungroup(s.expressions[-1])
        loop_proofs.append(dict(loop=oid,pass_order=order,traversal=s.value,index=s.loop_index,
            initial=p.index_nodes[oid][0] if s.value=="FORWARD" else p.node_ids[id(inits[s.loop_index])],
            comparison=cond.value,bound_node=p.node_ids[id(ungroup(cond.children[1]))],
            step=p.index_nodes[oid][1] if s.value=="FORWARD" else p.node_ids[id(s.children[-1])],step_delta=1 if s.value=="FORWARD" else -1,
            immutable_input_bound=True,terminal_rule="condition false after unit step; zero iterations allowed for numeric input zero"))
    # Output ancestry is structural, not observed numerical agreement.
    live={p.output_id}
    changed=True
    while changed:
        new={e.source for e in p.items if e.kind=="EDGE" and e.target in live}-live
        changed=bool(new);live.update(new)
    require(all(u["writer"] in live for u in update_records),"STATE_REQUIRED_WRITE_NOT_REACHING_OUTPUT")
    required_variables={w["binding"] for w in graph["writes"] if w["writer"] in live}
    loop_registers={u["target"] for u in update_records if u["loop"] is not None}
    inferred="TWO_PASS" if len(actual_loops)==2 else "PREFIX" if len(loop_registers)==2 else "PER_ITEM"
    require(inferred==d["structure"],"STATE_SOURCE_RECURRENCE_CLASS_MISMATCH")
    return dict(scope="DEVELOPMENT_ONLY",recurrence_class=inferred,class_proof="EXACT_PROSPECTIVE_SOURCE_STRUCTURE_PLUS_EPOCH_STATE_GRAPH",
        required_state_variables=sorted(required_variables),recurrence_registers=sorted(state),
        initialization=[dict(binding=n,writer=p.node_ids[id(inits[n])],value=integer_constant(inits[n].expressions[0])) for n in sorted(state)],
        all_state_definitions=graph["writes"],
        required_updates=update_records,loop_passes=loop_proofs,indicator_foundations=foundations,
        ordering_constraints=[dict(before=a["writer"],after=b["writer"]) for a,b in zip(update_records,update_records[1:])],
        state_reads=graph["reads"],state_dependencies=graph["required_state_edges"],final_output=dict(node=p.output_id,reachable_nodes=sorted(live),
            reads=[r for r in graph["reads"] if r["consumer"]==p.output_id]),
        required_computation_known=True,derived_from_output_agreement=False,scientific_satisfaction_claims=0)


def static_evidence(plan,source):
    p=source_program(plan,source);graph=analyze_state(p);certificate=required_computation(plan,p,graph)
    return p,graph,certificate


def trace_agreement(p,graph,execution):
    """Resolve every dynamic explicit/implicit read to a static epoch relation."""
    edges=graph["required_state_edges"];read_rows={r["reader"]:r for r in graph["reads"]};last={};last_event={};rows=[]
    for t in execution.state_trace:
        context=t["loop_context"];loop=context[-1]["loop"] if context else None;iteration=context[-1]["iteration"] if context else None
        if t["kind"] in {"READ","IMPLICIT_READ","INDEX_PRIOR_READ"}:
            require(t["binding"] in last and last[t["binding"]]==t["writer"],"STATE_RUNTIME_STALE_WRITER")
            prior=last_event[t["binding"]];pc=prior["loop_context"]
            require(equal(prior["value"],t["value"]),"STATE_RUNTIME_READ_VALUE_MISMATCH")
            if pc and pc[-1]["loop"]==loop:
                epoch="BEFORE_LOOP" if prior["kind"]=="INDEX_INITIALIZE" else "CURRENT_ITERATION" if pc[-1]["iteration"]==iteration else "PREVIOUS_ITERATION"
            elif pc: epoch="PASS_FINAL"
            else: epoch="INITIAL_OR_SEQUENTIAL"
            require(t["reader"] in read_rows and read_rows[t["reader"]]["binding"]==t["binding"],"STATE_RUNTIME_READER_UNACCOUNTED")
            match=[e for e in edges if e["writer"]==t["writer"] and e["reader"]==t["reader"] and e["epoch"]==epoch]
            require(len(match)==1,"STATE_RUNTIME_STATIC_EPOCH_MISMATCH")
            rows.append(dict(sequence=t["sequence"],actual_reader=t["reader"],actual_writer=t["writer"],binding=t["binding"],
                             value_before=t["value"],value_after=t["value"],loop=loop,iteration=iteration,
                             static_state_edge=match[0]["edge_id"],relation=match[0]["relation"]))
        elif t["kind"] in {"INITIALIZE","INPUT_WRITE","WRITE","INDEX_INITIALIZE","INDEX_WRITE"}:
            if "prior_writer" in t: require(last.get(t["binding"])==t["prior_writer"],"STATE_RUNTIME_WRITE_PRIOR_MISMATCH")
            if "old_value" in t:
                require(equal(t["old_value"],last_event[t["binding"]]["value"]) and t["value"]==t["old_value"]+t["delta"],"STATE_RUNTIME_WRITE_VALUE_MISMATCH")
            last[t["binding"]]=t["writer"];last_event[t["binding"]]=t
            rows.append(dict(sequence=t["sequence"],actual_writer=t["writer"],binding=t["binding"],value_before=t.get("old_value"),value_after=t["value"],
                             loop=loop,iteration=iteration,static_write=t["writer"]))
    require(set(execution.output_dependencies)<={i.occurrence_id for i in p.items},"STATE_RUNTIME_OUTPUT_DEPENDENCY_UNACCOUNTED")
    return dict(read_write_agreement=rows,trace=execution.state_trace,initial_state=[t for t in execution.state_trace if t["kind"] in {"INITIALIZE","INPUT_WRITE","INDEX_INITIALIZE"}],
                output=execution.output,output_dependencies=sorted(execution.output_dependencies),output_node=p.output_id,
                all_runtime_reads_resolved=True,static_definition_from_runtime=False)
