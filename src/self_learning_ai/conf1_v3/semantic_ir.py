"""Typed primitive recognition, structured reaching definitions and attributes.

No cases or labels select the ontology. Recognition compares parsed typed trees
with the eight frozen ledger definitions. This is not a general simplifier.
"""
from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path

from .core_ir import Item, Program, infer_type, integer_constant, ungroup
from .goco import Expr, Stmt, Parser, _walk_expr, _walk_stmt
from .interfaces import SchemaError, rid


def predicate_signature(e: Expr, symbols: dict, roles: dict) -> tuple:
    e=ungroup(e)
    value=integer_constant(e)
    if value is not None:return ("INTEGER",value)
    if e.kind=="ID":return ("READ",roles.get(e.value),symbols.get(e.value))
    if e.kind=="NUMBER":return ("INTEGER",int(e.value))
    if e.kind=="INDEX":return ("INDEX",*(predicate_signature(c,symbols,roles) for c in e.children))
    if e.kind=="BINARY":
        children=[predicate_signature(c,symbols,roles) for c in e.children];op=e.value
        if op in {">",">="}:op={">":"<",">=":"<="}[op];children.reverse()
        # These catalog trees are read-only integer expressions; an indexed
        # domain item is in bounds by the closed loop/decoder schema. This
        # normalization recognizes only an exact frozen predicate tree.
        if op in {"*","=="}:children.sort(key=repr)
        return ("BINARY",op,*children)
    return (e.kind,e.value,*(predicate_signature(c,symbols,roles) for c in e.children))


def frozen_predicates(domain: str) -> dict:
    path=Path(__file__).resolve().parents[3]/"research/protocols/phase3c_conf1_slots.json"
    raw=path.read_bytes()
    if hashlib.sha256(raw.replace(b"\r\n",b"\n")).hexdigest()!="83436eecda3affe813b785e868e3f8936fa59afc35ded0eb6a54290edb41dc88":
        raise SchemaError("frozen predicate ledger changed")
    ledger=json.loads(raw)
    symbols={"i":"INTEGER","n":"INTEGER","values":"INTEGER_ARRAY"}
    roles={"i":"DOMAIN_ITEM" if domain=="numeric_iteration" else "ITEM_INDEX","n":"INPUT_LIMIT","values":"DOMAIN_SEQUENCE"}
    return {predicate_signature(Parser(p["expression"]).expr(),symbols,roles):p["name"]
            for p in ledger["predicate_definitions"][domain]}


def enrich_semantics(program: Program) -> Program:
    nodes=[i for i in program.items if i.kind=="NODE"]
    # Replace the old all-writers overapproximation, not merely append a proof.
    edges=[i for i in program.items if i.kind=="EDGE" and i.operation!="PRIOR_STATE_TO_UPDATE"
           and not (i.operation=="LOOP_CARRY" and program.item(i.target).operation=="ASSIGN")]
    for key,oid in list(program.edge_ids.items()):
        if oid not in {e.occurrence_id for e in edges}:del program.edge_ids[key]
    by_id={i.occurrence_id:i for i in nodes};records=[]
    def node(oid,operation,typ,role,location,parent=None,operand_types=(),operand_roles=()):
        item=Item(oid,"NODE",operation,"SEMANTIC_PRIMITIVE" if operation in set(catalog.values()) else "GENERIC_CONSTRUCT",
                  typ,operand_types,operand_roles,role,location,parent=parent)
        nodes.append(item);by_id[oid]=item;return oid
    def edge(src,dst,operation,port,typ,sr,dr):
        oid=rid("OCC",[program.program_id,"SEMANTIC_EDGE",str(len(edges))])
        edges.append(Item(oid,"EDGE",operation,"ATOMIC_CONTROL_DATAFLOW",typ,(typ,),(sr,),dr,by_id[dst].location,src,dst,port))
        program.edge_ids[(dst,port)]=oid;return oid
    catalog=frozen_predicates(program.domain)
    expressions={id(e):e for top in program.statements for e in _walk_stmt(top) if isinstance(e,Expr)}
    for e in expressions.values():
        if e.kind=="GROUP" or id(e) not in program.node_ids:continue
        primitive=catalog.get(predicate_signature(e,program.symbols,program.roles))
        if primitive is None:continue
        if infer_type(e,program.symbols,program.imports)!="BOOLEAN":raise SchemaError("primitive result type")
        root=program.node_ids[id(e)];original=by_id[root]
        oid=rid("OCC",[program.program_id,"PRIMITIVE",str(e.start),primitive])
        node(oid,primitive,"BOOLEAN","PREDICATE_BOOLEAN",(e.start,e.end),original.parent,original.operand_types,original.operand_roles)
        ports=[]
        for port,child in enumerate(e.children):
            source=program.node_ids[id(ungroup(child))]
            eid=edge(source,oid,"VALUE_TO_PREDICATE",port,original.operand_types[port],original.operand_roles[port],"PREDICATE_BOOLEAN")
            ports.append({"port":port,"source_occurrence_id":source,"edge_id":eid,"type":original.operand_types[port]})
        # Route the actual comparison value through the semantic occurrence.
        # Existing consumers retain original AST ports; execution observes both.
        program.primitive_aliases[root]=oid
        for index,item in enumerate(edges):
            if item.source==root:edges[index]=replace(item,source=oid)
        edge(root,oid,"VALUE_TO_PREDICATE",900,"BOOLEAN","PREDICATE_BOOLEAN","PREDICATE_BOOLEAN")
        records.append({"capability":primitive,"authority":"phase3c_conf1_slots.json/predicate_definitions",
                        "source_location":[e.start,e.end],"expression_node_id":root,"contract_occurrence_id":oid,
                        "input_ports":ports,"output_port":{"port":0,"type":"BOOLEAN"},
                        "operand_types":list(original.operand_types),"result_type":"BOOLEAN"})
    # Range proof includes the declaration and EVERY write, not supplied flags.
    statements=[s for top in program.statements for s in _walk_stmt(top) if isinstance(s,Stmt)]
    for name,role in program.roles.items():
        if role!="INDICATOR":continue
        decl=[s for s in statements if s.kind=="DECLARE" and s.value.split(":")[1]==name]
        writes=[s for s in statements if s.kind=="UPDATE" and s.expressions[0].value==name]
        if len(decl)!=1 or not decl[0].expressions or integer_constant(decl[0].expressions[0]) not in {0,1} or any(
                s.value!="=" or integer_constant(s.expressions[1]) not in {0,1} for s in writes):
            raise SchemaError("indicator range proof incomplete")
        program.indicator_proofs[name]={"binding":name,"type":"INTEGER","range":[0,1],
            "initialization":program.node_ids[id(decl[0])],
            "writes":[{"occurrence_id":program.node_ids[id(s)],"value":integer_constant(s.expressions[1]),"source_location":[s.start,s.end]} for s in writes],
            "proof_rule":"declaration in {0,1}; every syntactic write is assignment in {0,1}; no INPUT or arithmetic update to binding",
            "predicate_definitions":[]}
    def contexts(rows,control=()):
        for s in rows:
            oid=program.node_ids.get(id(s))
            if s.kind=="UPDATE" and s.expressions[0].value in program.indicator_proofs:
                for write in program.indicator_proofs[s.expressions[0].value]["writes"]:
                    if write["occurrence_id"]==oid:write["control_context"]=list(control)
            if s.kind=="IF":
                e=ungroup(s.expressions[0]);root=program.node_ids[id(e)];predicate=program.primitive_aliases.get(root,root)
                for child in s.children:
                    if child.kind=="UPDATE" and child.value=="=" and child.expressions[0].value in program.indicator_proofs and integer_constant(child.expressions[1])==1:
                        target=program.node_ids[id(child)];proof=program.indicator_proofs[child.expressions[0].value]
                        eid=edge(predicate,target,"PREDICATE_TO_INDICATOR",150,"BOOLEAN","PREDICATE_BOOLEAN","INDICATOR")
                        proof["predicate_definitions"].append({"predicate_occurrence":predicate,"expression_node_id":root,"condition_location":[e.start,e.end],"write":target,"edge_id":eid,"control_context":list(control)+( [oid] )})
                contexts(s.children,control+(oid,))
            elif s.kind=="LOOP":contexts(s.children,control+(oid,))
            for record in records:
                if record["expression_node_id"] in {program.node_ids.get(id(e)) for expr in s.expressions for e in _walk_expr(expr)}:
                    record["control_context"]=list(control)
    contexts(program.statements)
    # Forward index initialization/step are explicit typed state definitions.
    for s in statements:
        if s.kind=="LOOP" and s.value=="FORWARD":
            oid=program.node_ids[id(s)];role=program.roles[s.loop_index]
            initial=node(rid("OCC",[program.program_id,"INDEX_INITIAL",str(s.start)]),"LOOP_INDEX_INITIALIZE","INTEGER",role,(s.start,s.end))
            step=node(rid("OCC",[program.program_id,"INDEX_STEP",str(s.start)]),"LOOP_INDEX_STEP","INTEGER",role,(s.start,s.end))
            program.index_nodes[oid]=(initial,step)
    # Structured may-reaching definitions: sequential transfer, branch join,
    # loop least fixed point. Reads before a write never see that current write;
    # they may see its previous-iteration definition at the loop header.
    reached={};updates={};iterations=[]
    def read_expr(e,env):
        for child in _walk_expr(e):
            if child.kind=="ID" and id(child) in program.node_ids and child.value in program.symbols:
                reached.setdefault(program.node_ids[id(child)],set()).update(env.get(child.value,set()))
    def join(a,b):return {name:set(a.get(name,set()))|set(b.get(name,set())) for name in set(a)|set(b)}
    def transfer(rows,incoming):
        env={name:set(ids) for name,ids in incoming.items()}
        for s in rows:
            if s.kind=="IMPORT":continue
            oid=program.node_ids[id(s)]
            if s.kind=="LOOP":
                pre={name:set(ids) for name,ids in env.items()}
                if s.value=="FORWARD":
                    read_expr(s.expressions[0],env);pre[s.loop_index]={program.index_nodes[oid][0]}
                header=pre
                for iteration in range(len(nodes)+1):
                    read_expr(s.expressions[-1],header)
                    after=transfer(s.children,header)
                    if s.value=="FORWARD":after[s.loop_index]={program.index_nodes[oid][1]}
                    newer=join(pre,after)
                    if newer==header:break
                    header=newer
                else:raise SchemaError("state analysis did not reach a finite fixed point")
                iterations.append({"loop":oid,"iterations":iteration+1,"header_definitions":{k:sorted(v) for k,v in header.items()}})
                env=header
            elif s.kind=="IF":
                read_expr(s.expressions[0],env);env=join(env,transfer(s.children,env))
            else:
                for expr in (s.expressions[1:] if s.kind=="UPDATE" else s.expressions if s.kind!="INPUT" else ()):
                    read_expr(expr,env)
                if s.kind=="DECLARE":env[s.value.split(":")[1]]={oid}
                elif s.kind=="INPUT":env[s.expressions[0].value]={oid}
                elif s.kind=="UPDATE":
                    name=s.expressions[0].value
                    if s.value!="=":updates.setdefault(oid,set()).update(env.get(name,set()))
                    env[name]={oid}
        return env
    transfer(program.statements,{})
    node_order={i.occurrence_id:n for n,i in enumerate(nodes)}
    for target,writers in (*reached.items(),*updates.items()):
        for port,writer in enumerate(sorted(writers,key=lambda oid:node_order[oid]),300):
            t=by_id[target];edge(writer,target,"PRIOR_STATE_TO_UPDATE",port,t.datatype,by_id[writer].result_role,t.result_role)
    program.state_analysis={"rule":"structured sequential transfer / branch union / loop least fixed point",
                            "read_definitions":{k:sorted(v) for k,v in reached.items()},
                            "update_definitions":{k:sorted(v) for k,v in updates.items()},"loop_fixed_points":iterations}
    # Maximal integer constant subtrees are attribute units, not leaf tokens.
    def attributes(e,parent_constant=False):
        e=ungroup(e);value=integer_constant(e);oid=program.node_ids.get(id(e))
        if value is not None and not parent_constant and oid:
            item=by_id[oid];members={program.node_ids[id(ungroup(c))] for c in _walk_expr(e) if id(ungroup(c)) in program.node_ids}
            parent=by_id.get(item.parent)
            initial=parent and parent.operation=="INITIALIZE" and parent.result_role in {"ACCUMULATOR","DISPLAYED_ACCUMULATOR"}
            program.attribute_specs[oid]={"root_occurrence":oid,"source_location":[e.start,e.end],"computed_integer":value,
                "semantic_role":"INITIAL_ACCUMULATOR" if initial else item.result_role,"exact_required_lexeme":None,
                "parent_occurrence":item.parent,"attribute_parent_kind":"INITIAL_ACCUMULATOR" if initial else "ACTIVE_BEHAVIORAL_PARENT",
                "members":sorted(members),"parent_ontology_supported":bool(initial or parent and parent.category in {"ATOMIC_OPERATOR","SEMANTIC_PRIMITIVE"}),
                "proof":"maximal wholly integer-constant neg/add/sub/mul subtree; exact mathematical integer"}
        for child in e.children:attributes(child,value is not None)
    for s in statements:
        for e in s.expressions:attributes(e)
    reachable={program.output_id};changed=True
    while changed:
        new={e.source for e in edges if e.target in reachable}-reachable
        changed=bool(new);reachable.update(new)
    program.items=tuple(replace(i,essential=i.occurrence_id in reachable if i.kind=="NODE" else i.source in reachable and i.target in reachable,
                                proof=None if (i.occurrence_id in reachable if i.kind=="NODE" else i.source in reachable and i.target in reachable) else "PURE_UNUSED_NO_TYPED_PATH_TO_OUTPUT") for i in (*nodes,*edges))
    for record in records:
        oid=record["contract_occurrence_id"]
        record["state_relations"]=[e.occurrence_id for e in edges if e.source==oid or e.target==oid]
        record["structural_output_dependency"]=oid in reachable
    program.semantic_records=tuple(records)
    return program


def source_flow_equivalence(left: Program, left_expr: Expr, right: Program, right_expr: Expr, *,
                            context: str, alpha_map: dict | None = None) -> dict:
    """Local frozen Boolean equivalence, never complete-program equivalence.

    Both expressions must belong to reconstructed source graphs. A supplied
    indicator set or range flag is not accepted by this API.
    """
    from .core_ir import compile_program
    from .contract_ir import graph_record
    from .goco import alpha_bijection
    try:
        if context not in {"LOCAL_PAIR_JOINT","BOOLEAN_OR"}:raise SchemaError("unlisted source-flow context")
        for p,e in ((left,left_expr),(right,right_expr)):
            if graph_record(compile_program(p.program_id,p.source))!=graph_record(p):raise SchemaError("source graph changed")
            if id(ungroup(e)) not in p.node_ids:raise SchemaError("expression is not source mapped")
        names=alpha_map if alpha_map is not None else dict(zip(left.symbols,right.symbols))
        alpha_bijection(left.symbols,right.symbols,names)
        if any(left.roles[a]!=right.roles[b] for a,b in names.items()):raise SchemaError("alpha role mismatch")
        # Local catalog proofs can compare different source spellings. They
        # never authorize whole-source correspondence or atomic-key transport.
        # Reconstructed source graphs, bindings, and loop identities remain
        # mandatory; a separate complete mapping certificate is required.
        def loop_context(p,target):
            found=[]
            def visit(rows,path=(),loops=()):
                for index,s in enumerate(rows):
                    here=path+(index,)
                    if any(id(e)==id(ungroup(target)) for root in s.expressions for e in _walk_expr(root)):
                        found.append(loops)
                    visit(s.children,here,loops+(here,) if s.kind=="LOOP" else loops)
            visit(p.statements)
            if len(found)!=1:raise SchemaError("local expression control context ambiguous")
            return found[0]
        if loop_context(left,left_expr)!=loop_context(right,right_expr):
            raise SchemaError("local expressions have different loop/state contexts")
        evidence=[]
        def normalized(p,e,rename,seen=frozenset()):
            e=ungroup(e)
            if e.kind=="ID" and e.value in p.indicator_proofs:
                if e.value in seen:raise SchemaError("circular indicator foundation")
                proof=p.indicator_proofs[e.value];definitions=proof["predicate_definitions"]
                if len(definitions)!=1:raise SchemaError("indicator predicate attachment ambiguous")
                definition=definitions[0];positive=definition["write"]
                zero=[w for w in proof["writes"] if w["value"]==0]
                one=[w for w in proof["writes"] if w["value"]==1]
                if len(zero)!=1 or len(one)!=1 or one[0]["occurrence_id"]!=positive:raise SchemaError("indicator reset/write catalog not proved")
                context_ids=zero[0].get("control_context",[])
                if len(context_ids)!=1 or p.item(context_ids[0]).operation!="BOUNDED_LOOP" or definition["control_context"][:-1]!=context_ids:
                    raise SchemaError("unconditional same-loop zero reset not proved")
                lo,hi=p.item(context_ids[0]).location
                if not lo<=e.start<e.end<=hi:raise SchemaError("indicator use is outside its resetting loop")
                if not zero[0]["source_location"][0]<one[0]["source_location"][0]<e.start:
                    raise SchemaError("indicator use is not after current-iteration definition")
                read=p.node_ids[id(e)];reaching=set(p.state_analysis["read_definitions"].get(read,[]))
                if reaching!={zero[0]["occurrence_id"],positive}:raise SchemaError("indicator use has other reaching definitions")
                candidates=[x for top in p.statements for x in _walk_stmt(top) if isinstance(x,Expr) and
                            [x.start,x.end]==definition["condition_location"] and x.kind!="GROUP"]
                if len(candidates)!=1:raise SchemaError("condition selector ambiguous")
                evidence.append({"indicator_read":read,"source_location":[e.start,e.end],"range_proof":proof,
                                 "current_iteration_reaching_definitions":sorted(reaching)})
                return normalized(p,candidates[0],rename,seen|{e.value})
            if infer_type(e,p.symbols,p.imports)=="BOOLEAN":
                if any(n.kind=="ID" and n.value in seen for n in _walk_expr(e)):
                    raise SchemaError("circular indicator foundation")
                alias=p.primitive_aliases.get(p.node_ids[id(e)])
                if alias:
                    bindings={name:rename.get(name,name) for name in p.symbols}
                    return ("BOOLEAN_PRIMITIVE",p.item(alias).operation,predicate_signature(e,p.symbols,bindings))
                raise SchemaError("local operand is not one source-mapped frozen predicate; compound/unlisted predicates are not atomic pair inputs")
            raise SchemaError("operand is neither Boolean nor a source-proved indicator")
        def relation(p,e,rename):
            e=ungroup(e)
            if context=="LOCAL_PAIR_JOINT" and e.kind=="BINARY" and e.value in {"&&","*"}:
                operands=[normalized(p,c,rename) for c in e.children]
                return ("LOCAL_PAIR_JOINT",*sorted(operands,key=repr))
            if context=="BOOLEAN_OR" and e.kind=="BINARY" and e.value=="||":
                return ("BOOLEAN_OR",*sorted((normalized(p,c,rename) for c in e.children),key=repr))
            if context=="BOOLEAN_OR" and e.kind=="BINARY" and e.value==">" and integer_constant(e.children[1])==0:
                addition=ungroup(e.children[0])
                if addition.kind!="BINARY" or addition.value!="+":raise SchemaError("OR indicator must be add(a,b)>0")
                return ("BOOLEAN_OR",*sorted((normalized(p,c,rename) for c in addition.children),key=repr))
            raise SchemaError("expression is not a permitted local flow alternative")
        a,b=relation(left,left_expr,names),relation(right,right_expr,{})
        if a!=b:raise SchemaError("local operands differ")
        return {"finding":"EQUIVALENT","frozen_rule_id":"V3.3","catalog_rule":"AND_VS_PROVEN_01_PRODUCT_LOCAL_ONLY" if context=="LOCAL_PAIR_JOINT" else "BOOLEAN_OR_VS_PROVEN_INDICATOR_SUM_POSITIVE",
                "scope":context,"not_complete_graph_equivalence":True,
                "source_locations":[[left_expr.start,left_expr.end],[right_expr.start,right_expr.end]],
                "operand_types":[[infer_type(c,p.symbols,p.imports) for c in ungroup(e).children] for p,e in ((left,left_expr),(right,right_expr))],
                "result_types":[infer_type(left_expr,left.symbols,left.imports),infer_type(right_expr,right.symbols,right.imports)],
                "alpha_bijection":names,"preconditions_and_flow_proofs":evidence,"normalized_local_relation":a,
                "affected_occurrences":[left.node_ids[id(ungroup(left_expr))],right.node_ids[id(ungroup(right_expr))]]}
    except SchemaError as exc:
        return {"finding":"UNRESOLVED","scope":context,"reason":str(exc),"frozen_rule_id":"V3.3","accepted":False}


def computed_mapping_view(program: Program) -> tuple:
    """Account for closed constant interiors under V3.3, without graph erasure.

    The original full graph remains serialized. This proof view changes ONLY
    supported computed-value attribute roots, never literal spelling, unrelated
    source-only trees, state/order, or complete Boolean topology.
    """
    specs={oid:s for oid,s in program.attribute_specs.items() if s["parent_ontology_supported"] and program.item(oid).essential}
    hidden={}
    for oid,spec in specs.items():
        members=set(spec["members"])
        interiors=(members-{oid})|{i.occurrence_id for i in program.items if i.kind=="EDGE" and i.target in members}
        if interiors:hidden[oid]=tuple(sorted(interiors))
    excluded={oid for ids in hidden.values() for oid in ids}
    names={n:f"binding{i}" for i,n in enumerate(program.symbols)}
    def expr(e):
        e=ungroup(e);oid=program.node_ids.get(id(e))
        if oid in specs:return ("COMPUTED_INTEGER_ATTRIBUTE",specs[oid]["computed_integer"],specs[oid]["semantic_role"])
        if e.kind=="ID":return ("ID",names.get(e.value,e.value),program.symbols.get(e.value))
        return (e.kind,e.value,*(expr(c) for c in e.children))
    def stmt(s):
        value=s.value
        if s.kind=="DECLARE":typ,name=value.split(":");value=(typ,names[name])
        return (s.kind,value,names.get(s.loop_index) if s.loop_index else None,tuple(expr(e) for e in s.expressions),tuple(stmt(c) for c in s.children))
    return tuple(stmt(s) for s in program.statements),tuple(i for i in program.items if i.occurrence_id not in excluded),hidden
