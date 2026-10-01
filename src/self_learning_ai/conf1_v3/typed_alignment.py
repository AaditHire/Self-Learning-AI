"""Complete typed alignment with ONLY the actually invoked frozen V3.3 rules.

Original graphs are never rewritten. The alignment is a proof view, with
explicit port permutations and constant-interior accounting. It is usable by
the independent serialized checker without importing the mapping constructor.
"""
from .core_ir import ungroup, infer_type
from .goco import alpha_bijection, _walk_expr
from .interfaces import ClosureError
from .semantic_ir import computed_mapping_view

def align(c, p):
    if c.domain != p.domain: raise ClosureError("ALIGNMENT_DOMAIN_MISMATCH")
    names=dict(zip(c.symbols,p.symbols)); alpha_bijection(c.symbols,p.symbols,names)
    if any(c.roles[x]!=p.roles[y] for x,y in names.items()): raise ClosureError("ALIGNMENT_ALPHA_ROLE_MISMATCH")
    _,ci,ch=computed_mapping_view(c); _,pi,ph=computed_mapping_view(p)
    table={}; ports={}; claims=[]; renamed={n:f"binding{i}" for i,n in enumerate(c.symbols)}
    pn={names[n]:v for n,v in renamed.items()}
    def pair(a,b):
        if a in table and table[a]!=b: raise ClosureError("ALIGNMENT_DUPLICATE_NODE")
        if b in table.values() and table.get(a)!=b: raise ClosureError("ALIGNMENT_NONINJECTIVE")
        table[a]=b
    def norm(e, program, bindings):
        e=ungroup(e); oid=program.node_ids.get(id(e)); spec=program.attribute_specs.get(oid)
        if spec and spec["parent_ontology_supported"] and program.item(oid).essential:
            role="INITIAL_ACCUMULATOR" if spec["attribute_parent_kind"]=="INITIAL_ACCUMULATOR" else "SUPPORTED_COMPUTED_OPERAND"
            return ("COMPUTED",spec["computed_integer"],role),[]
        if e.kind=="ID": return ("ID",bindings[e.value],program.symbols[e.value]),[]
        children=[(norm(x,program,bindings)[0],i,x) for i,x in enumerate(e.children[1:] if e.kind=="CALL" else e.children)]
        op=e.value
        if e.kind=="CALL": op="strings."+e.children[0].value
        if e.kind=="BINARY" and op in {">",">="}:
            op="<" if op==">" else "<="; children.reverse()
        if e.kind=="BINARY" and op in {"+","*","&&","||","=="}:
            children.sort(key=lambda x:repr(x[0]))
        return (e.kind,op,infer_type(e,program.symbols,program.imports),*(x[0] for x in children)),children
    def pure(e):
        from .core_ir import integer_constant
        return not any(n.kind in {"CALL","MEMBER","INDEX"} or n.kind=="BINARY" and n.value=="%" and integer_constant(n.children[1]) in {None,0} for n in _walk_expr(e))
    def ex(a,b):
        a,b=ungroup(a),ungroup(b); ao,bo=c.node_ids[id(a)],p.node_ids[id(b)]
        an,ac=norm(a,c,renamed); bn,bc=norm(b,p,pn)
        if an!=bn: raise ClosureError("INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE")
        pair(ao,bo)
        if ao in c.primitive_aliases:
            if bo not in p.primitive_aliases or c.item(c.primitive_aliases[ao]).operation!=p.item(p.primitive_aliases[bo]).operation:
                raise ClosureError("ALIGNMENT_PRIMITIVE_CHANGED")
            pair(c.primitive_aliases[ao],p.primitive_aliases[bo])
        rules=[]
        if ao in ch or bo in ph:
            rules.append("WHOLLY_INTEGER_CONSTANT_NEG_ADD_SUB_MUL_COMPUTED_KEY_ONLY")
        elif a.kind=="BINARY":
            permutation=[next(y[1] for x,y in zip(ac,bc) if x[1]==i) for i in range(len(ac))]
            for x,y in zip(ac,bc): ports[(ao,x[1])]=y[1]
            if a.value!=b.value:
                if {a.value,b.value} not in ({">","<"},{">=","<="}): raise ClosureError("UNLISTED_ALIGNMENT_REWRITE")
                rules.append("COMPARISON_DIRECTION")
            elif permutation!=list(range(len(permutation))):
                if a.value not in {"+","*","&&","||","=="} or not pure(a) or not pure(b): raise ClosureError("COMMUTATIVE_PURITY_OR_TOTALITY_UNPROVED")
                rules.append("SYMMETRIC_EQUALITY" if a.value=="==" else "PURE_COMMUTATIVE_CHILD_SORT")
            # Port normalization applies to the primitive alias's original
            # comparison input ports too, but never its synthetic value port.
            if ao in c.primitive_aliases:
                for x,y in zip(ac,bc): ports[(c.primitive_aliases[ao],x[1])]=y[1]
        for rule in rules:
            claims.append(dict(frozen_rule_id="V3.3",catalog_rule=rule,
                source_locations=[list(c.item(ao).location),list(p.item(bo).location)],
                operand_types=[list(c.item(ao).operand_types),list(p.item(bo).operand_types)],result_type=p.item(bo).datatype,
                semantic_roles=[c.item(ao).result_role,p.item(bo).result_role],alpha_mapping=names,
                duplicates_retained=True,child_permutation=[next(y[1] for x,y in zip(ac,bc) if x[1]==i) for i in range(len(ac))],
                contract_root=ao,source_root=bo,contract_members=[ao,*ch.get(ao,())],source_members=[bo,*ph.get(bo,())],
                preconditions="typed complete AST and bijective bindings; child permutation only, no reassociation; commutative scalar purity/nonzero constant remainder divisors; computed folding only under existing supported attribute parent"))
        for x,y in zip(ac,bc): ex(x[2],y[2])
    def statements(a,b):
        if len(a)!=len(b): raise ClosureError("UNMATCHED_LIVE_SOURCE_STRUCTURE")
        for x,y in zip(a,b):
            xv,yv=x.value,y.value
            if x.kind=="DECLARE": xt,xn=xv.split(":"); yt,yn=yv.split(":"); xv=(xt,names.get(xn)); yv=(yt,yn)
            if (x.kind,xv,names.get(x.loop_index),len(x.expressions))!=(y.kind,yv,y.loop_index,len(y.expressions)):
                raise ClosureError("UNMATCHED_LIVE_SOURCE_STRUCTURE")
            xo,yo=c.node_ids.get(id(x)),p.node_ids.get(id(y))
            if xo is not None: pair(xo,yo)
            if xo in c.index_nodes:
                if yo not in p.index_nodes: raise ClosureError("ALIGNMENT_INDEX_STATE_MISMATCH")
                for i,j in zip(c.index_nodes[xo],p.index_nodes[yo]): pair(i,j)
            for e,f in zip(x.expressions,y.expressions): ex(e,f)
            statements(x.children,y.children); statements(x.alternate,y.alternate)
    statements(c.statements,p.statements); pair(c.macro_id,p.macro_id)
    if set(table)!={i.occurrence_id for i in ci if i.kind=="NODE"} or set(table.values())!={i.occurrence_id for i in pi if i.kind=="NODE"}:
        raise ClosureError("ALIGNMENT_INCOMPLETE_NODE_ACCOUNTING")
    # AST matching supplies the licensed changes to generated operand-index
    # role labels. Semantic bindings, transmitted types, edge kind, direction
    # and actual destination ports still have to agree independently.
    used=set(); edge_pairs=[]
    for a in (i for i in ci if i.kind=="EDGE"):
        port=ports.get((a.target,a.port),a.port)
        candidates=[b for b in pi if b.kind=="EDGE" and b.occurrence_id not in used and
            (b.operation,b.datatype,b.operand_types,b.source,b.target)==(a.operation,a.datatype,a.operand_types,table[a.source],table[a.target]) and
            (b.port==port or a.operation=="PRIOR_STATE_TO_UPDATE")]
        if len(candidates)!=1: raise ClosureError("ALIGNMENT_TYPED_DIRECTED_EDGE_MISMATCH")
        b=candidates[0]; used.add(b.occurrence_id); edge_pairs.append((a.occurrence_id,b.occurrence_id))
    if used!={i.occurrence_id for i in pi if i.kind=="EDGE"}: raise ClosureError("ALIGNMENT_UNMATCHED_SOURCE_EDGE")
    for a,b in list(table.items())+edge_pairs:
        ca,pa=c.item(a),p.item(b)
        folded=a in c.attribute_specs and b in p.attribute_specs and c.attribute_specs[a]["parent_ontology_supported"] and p.attribute_specs[b]["parent_ontology_supported"]
        if ca.datatype!=pa.datatype or (ca.category!=pa.category and not folded) or ca.essential!=pa.essential or ca.proof!=pa.proof:
            raise ClosureError("ALIGNMENT_TYPE_OR_OBSERVABILITY_MISMATCH")
        if not ca.essential and ca.proof!="PURE_UNUSED_NO_TYPED_PATH_TO_OUTPUT": raise ClosureError("UNPROVED_REFERENCE_ONLY")
    table.update(edge_pairs)
    return dict(correspondence=list(table.items()),equivalence_claims=claims,
        contract_hidden={k:list(v) for k,v in ch.items()},source_hidden={k:list(v) for k,v in ph.items()},
        full_raw_graphs_retained=True,alpha_mapping=names)
