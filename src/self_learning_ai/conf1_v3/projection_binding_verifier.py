"""Read-only replay of disposable grammatical binding; no mapping constructor.

Shares parsing/type/grammar primitives, independently rebuilds the declaration,
all bindings, multiplicity, graph inventories, claims and indicator foundations.
Never accepts constructor PASS flags, scientific plans, or caller classifications.
"""
from dataclasses import asdict
from .interfaces import canonical_json_bytes, ClosureError
from .requirements import digest, expression
from .projection_grammar import grammar, derive_projection_plan, development_identity, require
from .core_ir import compile_program, ungroup
from .contract_ir import graph_record
from .typed_alignment import align
from .requirement_verifier import expected_claims
from .boolean_region_checker import check_serialized_mapping
from .transport_verifier import verify_canonical_transport, verify_mapping_proof_record


def equal(a,b):
    return canonical_json_bytes(a)==canonical_json_bytes(b)


def verify_projection_plan(plan):
    require(plan.get("scope")=="DEVELOPMENT_ONLY", "SCIENTIFIC_SOURCE_MAPPING_DEFERRED")
    development_identity(plan)
    expected=derive_projection_plan(plan["declaration"])
    require(equal(plan,expected), "PROSPECTIVE_GRAMMAR_PLAN_CHANGED")
    return dict(status="VERIFIED",scope="DEVELOPMENT_ONLY",requirements_sha256=plan["requirements_sha256"],
                source_used_for_requirement_derivation=False,scientific_satisfaction_claims=0)


def reference_sites(plan,p):
    rows,symbols,roles=grammar(plan["declaration"])
    require(p.domain==plan["declaration"]["family"] and len(p.symbols)==len(symbols), "PROJECTION_DOMAIN_OR_BINDING_COUNT")
    names=dict(zip(symbols,p.symbols))
    require(all(symbols[n]==p.symbols[v] and roles[n]==p.roles[v] for n,v in names.items()), "PROJECTION_BINDING_TYPE_ROLE")
    sites={}; statements={}
    def signature(e, rename):
        e=ungroup(e)
        return (e.kind,rename.get(e.value,e.value),tuple(signature(x,rename) for x in e.children))
    def ex(e,path):
        e=ungroup(e); sites[path]=p.node_ids[id(e)]
        for i,c in enumerate(e.children[1:] if e.kind=="CALL" else e.children): ex(c,path+"/a"+str(i))
    def block(expected,actual,prefix=""):
        require(len(expected)==len(actual), "PROJECTION_GRAMMAR_STATEMENT_COUNT")
        for i,(a,b) in enumerate(zip(expected,actual)):
            path=prefix+"/s"+str(i); av=a["value"] or a["kind"]
            if a["kind"]=="DECLARE": typ,n=av.split(":"); av=typ+":"+names[n]
            require((a["kind"],av,names.get(a["index"]),len(a["expressions"]))==
                    (b.kind,b.value,b.loop_index,len(b.expressions)), "PROJECTION_GRAMMAR_STRUCTURE")
            require(not b.alternate, "PROJECTION_UNDECLARED_ALTERNATE")
            statements[path]=b
            if id(b) in p.node_ids: sites[path]=p.node_ids[id(b)]
            for j,(text,e) in enumerate(zip(a["expressions"],b.expressions)):
                require(signature(expression(text),names)==signature(e,{}), "REFERENCE_NOT_PROSPECTIVE_GRAMMAR")
                if a["kind"]=="INPUT" or a["kind"]=="UPDATE" and j==0: continue
                ex(e,path+"/e"+str(j))
            block(a["children"],b.children,path+"/body")
    block(rows,p.statements)
    return sites,statements,names


def indicator_foundations(plan,p,sites,statements,names):
    """Exact declared reset/IF write sites and structured current-iteration reads.

    A reaching union {reset,true-write} is intentional; any other definition,
    stale read, wrong loop, or extra predicate writer is unresolved.
    """
    from .goco import _walk_expr
    d=plan["declaration"]; rows,_,_=grammar(d); result=[]
    def visit(block,prefix="",loop=None):
        for i,s in enumerate(block):
            path=prefix+"/s"+str(i)
            if s["kind"]=="LOOP": visit(s["children"],path+"/body",path)
            elif s["kind"]=="IF": visit(s["children"],path+"/body",loop)
            if s["kind"]=="IF" and s["children"] and s["children"][0]["kind"]=="UPDATE" and s["children"][0]["expressions"][0] in {"hitP","hitQ"}:
                role=s["children"][0]["expressions"][0][-1]; name=names["hit"+role]
                write=sites[path+"/body/s0"]; reset_paths=[q for q,t in statements.items() if q.startswith(loop+"/body/") and q.rsplit("/",1)[0]==loop+"/body" and t.kind=="UPDATE" and t.value=="=" and t.expressions[0].value==name]
                require(len(reset_paths)==1,"INDICATOR_RESET_AMBIGUOUS")
                reset=sites[reset_paths[0]]; proof=p.indicator_proofs.get(name)
                require(proof is not None and proof["range"]==[0,1], "INDICATOR_RANGE_UNPROVED")
                definitions=[x for x in proof["predicate_definitions"] if x["write"]==write]
                require(len(definitions)==1 and p.item(definitions[0]["predicate_occurrence"]).operation==d["role_bindings"][role], "INDICATOR_WRONG_PREDICATE_ROLE")
                require(definitions[0]["control_context"]==[sites[loop],sites[path]], "INDICATOR_WRONG_LOOP_OR_CONTROL")
                reads=[]
                for q,t in statements.items():
                    if not q.startswith(loop+"/body/"): continue
                    for root in t.expressions[1:] if t.kind=="UPDATE" else t.expressions:
                        for e in _walk_expr(root):
                            if e.kind=="ID" and e.value==name:
                                oid=p.node_ids[id(e)]; writers=p.state_analysis["read_definitions"].get(oid,[])
                                require(set(writers)=={reset,write}, "INDICATOR_STALE_OR_AMBIGUOUS_REACHING")
                                reads.append(dict(read=oid,writers=writers,location=list(p.item(oid).location)))
                # Some scaffold indicators are intentionally unconsumed in a
                # direct Boolean realization; they supply no activity claim.
                result.append(dict(role=role,predicate=d["role_bindings"][role],loop=sites[loop],binding=name,
                                   reset=reset,write=write,range_proof=proof,reads=reads,
                                   current_iteration=True,scientific_activity_claim=False))
    visit(rows)
    require(result,"INDICATOR_FOUNDATION_MISSING")
    return result


def reconstruct_bindings(plan,c,p,base,bundle=None):
    verify_projection_plan(plan); development_identity(c.source); development_identity(p.source)
    sites,statements,names=reference_sites(plan,c)
    indicators=indicator_foundations(plan,c,sites,statements,names)
    source_indicators=indicator_foundations_from_reference(plan,p,bundle)
    if bundle:
        verify_canonical_transport(bundle); verify_mapping_proof_record(bundle,base)
        check_serialized_mapping(bundle["total_mapping_certificate"])
        table=dict(base["ordinary_correspondence"]); alignment=None
    else:
        alignment=align(c,p); table=dict(alignment["correspondence"])
        require(equal(base["ordinary_correspondence"],alignment["correspondence"]), "COMPLETE_TYPED_MAPPING_CHANGED")
        require(base["source_sha256"]==digest_source(p.source),"MAPPING_SOURCE_HASH_CHANGED")
    regions=(bundle or {}).get("total_mapping_certificate",{}).get("regions",[])
    bindings=[]; occupied=set()
    for req in plan["requirements"]:
        pairs=[]; evidence=[]
        for occurrence in req["occurrence_requirements"]:
            sel=occurrence["selector"]; kind=sel["kind"]; cap=req["capability"]
            if kind=="REGION":
                row=next((r for r in regions if r["contract"]["statement_location"]==[statements[sel["path"]].start,statements[sel["path"]].end]),None)
                if row:
                    require(row["scope"]==("LOCAL_PAIR_JOINT" if cap["operation"]=="LOCAL_PAIR_JOINT" else "BOOLEAN_OR"),"REGION_WRONG_REQUIREMENT")
                    ao,bo=row["contract"]["expression_node"],row["source"]["expression_node"]
                    claim=next(t for t in bundle["transports"] if t["region_id"]==row["region_id"])
                    evidence.append(claim["transport_id"])
                else:
                    require(not bundle,"MISSING_REQUIRED_REGION")
                    ao=sites[sel["path"]+"/e0"]; bo=table[ao]
                    from .semantic_ir import source_flow_equivalence
                    context="LOCAL_PAIR_JOINT" if cap["operation"]=="LOCAL_PAIR_JOINT" else "BOOLEAN_OR"
                    local=source_flow_equivalence(c,statements[sel["path"]].expressions[0],c,statements[sel["path"]].expressions[0],context=context)
                    require(local["finding"]=="EQUIVALENT","DIRECT_RELATION_NOT_REALIZED")
            elif kind=="EDGE_KIND":
                candidates=[i for i in c.items if i.kind=="EDGE" and i.operation==sel["operation"] and i.datatype==sel["datatype"] and i.operand_roles==(sel["source_role"],) and i.result_role==sel["target_role"] and i.occurrence_id in table]
                if not candidates and bundle:
                    # The certified regional interface preserves the exact
                    # accumulator write boundary, not its internal AND/MUL
                    # atomic nodes. Bind only identical typed edges through
                    # that boundary; never transport an internal operator key.
                    endpoints=dict(table); transports={}
                    for region,t in zip(regions,bundle["transports"]):
                        endpoints[region["contract"]["state_update_node"]]=region["source"]["state_update_node"]
                        transports[region["contract"]["state_update_node"]]=t["transport_id"]
                    for edge in c.items:
                        if edge.kind!="EDGE" or edge.operation!=sel["operation"] or edge.datatype!=sel["datatype"] or edge.operand_roles!=(sel["source_role"],) or edge.result_role!=sel["target_role"]: continue
                        if edge.source not in endpoints or edge.target not in endpoints: continue
                        matches=[b for b in p.items if b.kind=="EDGE" and b.operation==edge.operation and b.datatype==edge.datatype and b.operand_types==edge.operand_types and b.operand_roles==edge.operand_roles and b.result_role==edge.result_role and b.source==endpoints[edge.source] and b.target==endpoints[edge.target] and (b.port==edge.port or edge.operation=="PRIOR_STATE_TO_UPDATE")]
                        if len(matches)==1:
                            table[edge.occurrence_id]=matches[0].occurrence_id; candidates=[edge]
                            evidence += sorted({transports[o] for o in (edge.source,edge.target) if o in transports})
                            break
                require(candidates,"REQUIRED_TYPED_EDGE_UNBOUND: "+sel["operation"])
                ao=candidates[0].occurrence_id; bo=table[ao]
            else:
                ao=c.macro_id if kind=="DOMAIN" else c.primitive_aliases.get(sites[sel["path"]]) if kind=="PRIMITIVE" else c.index_nodes[sites[sel["path"]]][0 if sel["part"]=="initial" else 1] if kind=="INDEX_STATE" else sites[sel["path"]]
                require(ao in table,"GENUINE_REQUIRED_COMPONENT_UNBOUND")
                bo=table[ao]; actual=c.item(ao)
                require(actual.operation==cap["operation"] or cap["operation"] in {"COMPUTED_VALUE","LITERAL_TOKEN"} and actual.operation=="CONSTANT", "REQUIREMENT_OPERATION_MISMATCH")
                require(actual.datatype==cap["result_type"] and list(actual.operand_types)==cap["operand_types"] and list(actual.operand_roles)==cap["operand_roles"] and actual.result_role==cap["result_role"], "REQUIREMENT_TYPE_ROLE_MISMATCH")
                if cap["value"] is not None:
                    require((int(actual.value) if cap["operation"]=="COMPUTED_VALUE" else actual.value)==cap["value"],"REQUIREMENT_VALUE_MISMATCH")
            require((ao,bo) not in occupied,"DUPLICATE_REQUIREMENT_SATISFACTION"); occupied.add((ao,bo))
            pairs.append((ao,bo))
        claims=[] if alignment is None else [x for x in alignment["equivalence_claims"] if any(a in x["contract_members"] or c.item(a).kind=="EDGE" and c.item(a).target==x["contract_root"] for a,b in pairs)]
        bindings.append(dict(requirement_id=req["requirement_id"],canonical_contract_key=req["canonical_contract_key"],scope="DEVELOPMENT_ONLY",capability=req["capability"],
                             evidence_kind=req["evidence_kind"],family=req["family"],input_domain=req["input_domain"],multiplicity=req["multiplicity"],
                             contract_occurrences=[a for a,b in pairs],source_occurrences=[b for a,b in pairs],
                             method="AUTHORIZED_V33_EQUIVALENCE" if evidence or claims else "DIRECT_TYPED_CORRESPONDENCE",
                             evidence_id=evidence or (digest(claims) if claims else None),
                             source_locations=[list(p.item(b).location) for a,b in pairs],source_bindings=p.roles,
                             control_state_context=[dict(occurrence=b,parent=p.item(b).parent,source=p.item(b).source,target=p.item(b).target,port=p.item(b).port) for a,b in pairs],
                             dependency_edges=[asdict(e) for e in p.items if e.kind=="EDGE" and any(e.source==b or e.target==b for a,b in pairs)],
                             unresolved_reason=None))
    require(len(bindings)==len(plan["requirements"]),"MISSING_REQUIREMENT_SATISFACTION")
    return bindings,dict(reference=indicators,source=source_indicators)


def digest_source(source):
    import hashlib
    return hashlib.sha256(source.encode()).hexdigest()


def projection_claims(c,p,bindings,bundle):
    if not bundle:
        return expected_claims(c,p,bindings)
    flat=[]
    for b in bindings:
        for evidence_id in b["evidence_id"] if isinstance(b["evidence_id"],list) else []:
            flat.append({**b,"evidence_id":evidence_id})
    return expected_claims(c,p,flat,bundle)


def indicator_foundations_from_reference(plan,p,bundle):
    # For nonregional forms the whole prospective grammar must match the
    # source modulo a COMPLETE typed V3.3 alignment, so use its source prelude.
    # Regional forms share exactly that same prelude, certified independently.
    rows,_,_=grammar(plan["declaration"])
    sites={}; statements={}
    def visit(block,prefix=""):
        for i,s in enumerate(block):
            path=prefix+"/s"+str(i); statements[path]=s
            if id(s) in p.node_ids: sites[path]=p.node_ids[id(s)]
            visit(s.children,path+"/body")
    visit(p.statements)
    _,symbols,_=grammar(plan["declaration"])
    names=dict(zip(symbols,p.symbols))
    return indicator_foundations(plan,p,sites,statements,names)


def verify_direct_base(c,p,base):
    from .contract_ir import keys_from_ir
    from .interfaces import rid
    a=align(c,p); table=dict(a["correspondence"]); _,occ=keys_from_ir(c,())
    expected=dict(contract_id=rid("CONTRACT",[c.program_id]),program_id=p.program_id,source_sha256=digest_source(p.source),
                  ordinary_correspondence=a["correspondence"],key_occurrences={k:[table[o] for o in ids] for k,ids in occ.items()},
                  equivalence_proofs=a["equivalence_claims"],semantic_transport_sha256=None,
                  obligation_satisfaction=dict(direct=a["correspondence"],regional=[]),raw_key_resolution=[],
                  mapping_status="STRICT_TYPED_MAPPING",all_raw_atomic_keys_satisfied=True,raw_graph_equality_claim=None)
    require(equal(base,expected),"PROJECTION_COMPLETE_BASE_RECORD_CHANGED")


def verify_projection_evidence(e):
    fields={"schema_version","artifact_kind","plan_before","plan_after","reference_source","source","contract_graph","source_graph","base_mapping","transport_bundle","bindings","indicator_foundations","claims","source_projection_provenance"}
    require(set(e)==fields and e["schema_version"]==1 and e["artifact_kind"]=="DEVELOPMENT_ONLY_GENERIC_SOURCE_BINDING", "PROJECTION_EVIDENCE_SCHEMA")
    require(equal(e["plan_before"],e["plan_after"]),"PROJECTION_PLAN_OR_NAMESPACE_CHANGED")
    plan=e["plan_before"]; verify_projection_plan(plan)
    development_identity(e["source"]); development_identity(e["reference_source"])
    c=compile_program(plan["program_id"],e["reference_source"]); p=compile_program(plan["program_id"],e["source"])
    if not e["transport_bundle"]: verify_direct_base(c,p,e["base_mapping"])
    require(equal(graph_record(c),e["contract_graph"]) and equal(graph_record(p),e["source_graph"]),"PROJECTION_RAW_GRAPH_CHANGED")
    bindings,indicators=reconstruct_bindings(plan,c,p,e["base_mapping"],e["transport_bundle"])
    require(equal(bindings,e["bindings"]),"PROJECTION_BINDINGS_CHANGED")
    require(equal(indicators,e["indicator_foundations"]),"PROJECTION_INDICATOR_FOUNDATIONS_CHANGED")
    require(equal(projection_claims(c,p,bindings,e["transport_bundle"]),e["claims"]),"PROJECTION_V33_CLAIMS_CHANGED")
    expected=dict(scope="DEVELOPMENT_ONLY",declaration_sha256=digest(plan["declaration"]),reference_source_sha256=digest_source(c.source),source_sha256=digest_source(p.source),scientific_slot_binding=None,scientific_requirement_satisfaction=False,scientific_expected_row_index_eligible=False)
    require(equal(expected,e["source_projection_provenance"]),"PROJECTION_PROVENANCE_OR_PROMOTION_CHANGED")
    return dict(status="VERIFIED",scope="DEVELOPMENT_ONLY",requirements_sha256=plan["requirements_sha256"],
                complete_typed_accounting=True,multiplicity_preserved=True,constructor_pass_flag_trusted=False,
                scientific_satisfaction_claims=0,scientific_instance_closure="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION")
