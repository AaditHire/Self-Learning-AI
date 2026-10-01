"""Typed attribute mechanics, NOT global/scientific gate completion.

No caller ACTIVE/category flags. Requirements originate in the declaration
grammar/reference mapping, not from an executed source's observed outputs.
"""
from dataclasses import asdict
from .contract_ir import keys_from_ir
from .projection_grammar import require,render_development
from .projection_binding_verifier import equal,reference_sites
from .core_ir import compile_program,execute
from .state_semantics import static_evidence,trace_agreement
from .attribute_reference import output_plan,matches,digest_text
from .requirements import digest
from .interfaces import rid
from .goco import Stmt,_walk_stmt,_walk_expr


def literal_expression_context(p,oid):
    """Exact enclosing expression, with alpha bindings but GROUPs retained.

    Computed keys may fold constant trees. A syntax-essential lexeme must not
    inherit that permission to alter signs/grouping or its active expression.
    """
    roots=[root for top in p.statements for s in _walk_stmt(top) if isinstance(s,Stmt) for root in s.expressions
           if any(p.node_ids.get(id(e))==oid for e in _walk_expr(root))]
    require(len(roots)==1,"VALUE_AMBIGUOUS_LITERAL_EXPRESSION")
    names={n:"binding"+str(i) for i,n in enumerate(p.symbols)}
    def shape(e):return (e.kind,names.get(e.value,e.value) if e.kind=="ID" else e.value,tuple(shape(c) for c in e.children))
    return shape(roots[0])
from .essentiality_semantics import SCIENTIFIC


def value_requirements(e,literals=()):
    d=e["state"]["plan"]["declaration"];ref=e["mapping"]["reference_source"]
    p=compile_program(d["program_id"],ref);sites,_,_=reference_sites(e["state"]["plan"],p)
    keys,sets=keys_from_ir(p)
    result=[dict(requirement_id=digest(["DEVELOPMENT_VALUE_REQUIREMENT",d["program_id"],k.key_id]),key=asdict(k),
                 evidence_kind="VALUE_OR_LITERAL_ATTRIBUTE",contract_occurrences=list(sets[k.key_id]),
                 exact_literal_context=literal_expression_context(p,sets[k.key_id][0]) if k.exact_required_lexeme is not None else None,
                 grammar_paths=[next((path for path,oid in sites.items() if oid==o),None) for o in sets[k.key_id]])
            for k in keys if k.evidence_kind=="VALUE_OR_LITERAL_ATTRIBUTE"]
    require(len({x["grammar_path"] for x in literals})==len(literals),"VALUE_DUPLICATE_SYNTAX_OBLIGATION")
    for obligation in literals:
        require(set(obligation)=={"grammar_path","exact_lexeme"},"VALUE_SYNTAX_OBLIGATION_SCHEMA")
        oid=sites.get(obligation["grammar_path"])
        require(oid is not None and p.item(oid).datatype=="INTEGER" and p.item(oid).operation=="CONSTANT" and
                p.source[slice(*p.item(oid).location)]==obligation["exact_lexeme"],"VALUE_PROSPECTIVE_NUMERIC_LEXEME_MISMATCH")
        base=next((r for r in result if oid in r["contract_occurrences"]),None)
        require(base is not None,"VALUE_SYNTAX_NOT_MAXIMAL_REQUIRED_UNIT")
        key={**base["key"],"operation":"LITERAL_TOKEN:"+obligation["exact_lexeme"],"computed_integer":None,"semantic_role":None,"exact_required_lexeme":obligation["exact_lexeme"]}
        key["key_id"]=rid("KEY",["VALUE_OR_LITERAL",p.domain,key["operation"],key["result_role"],key["parent_key_id"] or "INITIAL_ACCUMULATOR"])
        result.append(dict(requirement_id=digest(["DEVELOPMENT_VALUE_REQUIREMENT",d["program_id"],key["key_id"]]),key=key,
                           evidence_kind="VALUE_OR_LITERAL_ATTRIBUTE",contract_occurrences=[oid],grammar_paths=[obligation["grammar_path"]],
                           exact_literal_context=literal_expression_context(p,oid)))
    return result


def source_attachment(p,oid,key,exact_literal_context=None):
    item=p.item(oid);spec=p.attribute_specs.get(oid)
    require(item.essential and (spec is not None or item.category=="VALUE_OR_LITERAL"),"VALUE_UNSUPPORTED_OR_NONMAXIMAL_ATTACHMENT")
    require(not any(oid in s["members"] and oid!=root for root,s in p.attribute_specs.items()),"VALUE_NONMAXIMAL_CONSTANT")
    require(item.datatype==key["result_type"],"VALUE_TYPE_MISMATCH")
    if key["exact_required_lexeme"] is not None:
        require(item.datatype in {"STRING","INTEGER"} and p.source[slice(*item.location)]==key["exact_required_lexeme"],"VALUE_EXACT_LEXEME_MISMATCH")
        if exact_literal_context is not None:require(equal(literal_expression_context(p,oid),exact_literal_context),"VALUE_LITERAL_EXPRESSION_CONTEXT_MISMATCH")
    else:
        require(spec is not None and spec["computed_integer"]==key["computed_integer"] and spec["semantic_role"]==key["semantic_role"],"VALUE_COMPUTED_VALUE_OR_ROLE_MISMATCH")
    return dict(occurrence_id=oid,parent_occurrence=item.parent,source_location=list(item.location),source_lexeme=p.source[slice(*item.location)],
                type=item.datatype,semantic_role=spec["semantic_role"] if spec else item.result_role,
                computed_integer=key["computed_integer"],exact_required_lexeme=key["exact_required_lexeme"],
                literal_expression_context=literal_expression_context(p,oid) if key["exact_required_lexeme"] is not None else None,
                maximal_constant=spec,interior=[dict(occurrence_id=o,operation=p.item(o).operation,location=list(p.item(o).location)) for o in (spec["members"] if spec else [])])


def value_facts(req,e,p,g,c):
    key=req["key"];table=dict(e["mapping"]["base_mapping"]["ordinary_correspondence"])
    cases=e["state"]["executions"];reason="VALUE_PARENT_UNRESOLVED"
    for co in req["contract_occurrences"]:
        require(co in table,"VALUE_UNBOUND_ATTACHMENT")
        oid=table[co];a=source_attachment(p,oid,key,req["exact_literal_context"]);parent=a["parent_occurrence"]
        for i,case in enumerate(cases):
            cid=p.program_id+"-CASE-"+str(i);active=None;binding=None
            normal=execute(p,case["raw_input"],detailed_state_trace=True)
            if key["attribute_parent_kind"]=="ACTIVE_BEHAVIORAL_PARENT":
                fs=[f for f in e["findings"] if key["parent_key_id"] in f["bound_requirement"]["canonical_keys"] and parent in f["bound_requirement"]["joint_occurrences"]]
                if not fs:
                    reason="VALUE_EXACT_BEHAVIORAL_PARENT_UNBOUND";continue
                eligible=[]
                for f in fs:
                    x=f["cases"][i]
                    if x["status"]=="INACTIVE":reason="VALUE_PARENT_INACTIVE"
                    if x["status"]=="ACTIVE" and any(parent in ev["dependencies"] for ev in x["normal_events"]):eligible.append((f,x))
                if not eligible:continue
                f,x=eligible[0]
                active=dict(requirement_id=f["bound_requirement"]["requirement_id"],canonical_key=key["parent_key_id"],evidence_kind="BEHAVIORAL",
                            parent_occurrence=parent,case_id=cid,normal_ref=x["normal_ref"],counterfactual_ref=x["attempts"][-1]["runtime_ref"],
                            intervention_order=x["attempts"][-1]["intervention"]["order"],essentiality_packet_sha256=digest(e))
            else:
                require(key["attribute_parent_kind"]=="INITIAL_ACCUMULATOR" and key["parent_key_id"] is None,"VALUE_FAKE_INITIAL_PARENT")
                ws=[w for w in g["writes"] if w["writer"]==parent and w["operation"].startswith("DECLARE:")]
                require(len(ws)==1 and ws[0]["binding"] in c["recurrence_registers"],"VALUE_WRONG_INITIAL_STATE")
                init=next((t for t in normal.state_trace if t["kind"]=="INITIALIZE" and t["writer"]==parent),None)
                value=key["computed_integer"] if key["computed_integer"] is not None else p.attribute_specs[oid]["computed_integer"]
                require(init is not None and init["value"]==value,"VALUE_INITIAL_EXECUTION_MISMATCH")
                binding=dict(binding=ws[0]["binding"],initialization=init,state_edges=[x for x in g["required_state_edges"] if x["writer"]==parent],
                             initialization_location=ws[0]["location"],required_computation_sha256=digest(c))
            if oid not in normal.evaluated or parent not in normal.evaluated or oid not in normal.output_dependencies or parent not in normal.output_dependencies:
                reason="VALUE_NO_EXECUTED_OUTPUT_DEPENDENCY";continue
            import json
            expected=json.loads(key["exact_required_lexeme"]) if key["exact_required_lexeme"] is not None and a["type"]=="STRING" else p.attribute_specs[oid]["computed_integer"] if key["exact_required_lexeme"] is not None else key["computed_integer"]
            if expected not in normal.values.get(oid,[]):continue
            return dict(status="COVERED",reason="VERIFIED_EXACT_ATTRIBUTE_PATH",witness=dict(program_id=p.program_id,source_sha256=digest_text(p.source),case_id=cid,raw_input=case["raw_input"],
                attachment=a,active_parent=active,initial_state=binding,executed_values=normal.values[oid],
                state_trace_agreement=trace_agreement(p,g,normal),output_dependencies=sorted(normal.output_dependencies)))
    return dict(status="UNRESOLVED",reason=reason,witness=None)


def output_facts(req,plan,e,p,g,c):
    rows=[]
    for i,r in enumerate(plan["expected_records"]):
        normal=execute(p,r["raw_input"],detailed_state_trace=True)
        require(normal.output==r["expected_output"],"OUTPUT_REFERENCE_EXECUTION_DISAGREEMENT")
        require(p.output_id in normal.evaluated and p.output_id in normal.output_dependencies,"OUTPUT_FINAL_DISPLAY_NOT_EXECUTED")
        rows.append(dict(case_id=r["case_id"],record_id=r["record_id"],expected_output=r["expected_output"],expected_integer=r["expected_integer"],
                         mechanical_match="MATCH" if matches(req["operation"],r["expected_output"]) else "NO_MATCH",final_display=dict(occurrence_id=p.output_id,
                         source_location=list(p.item(p.output_id).location),actual_output=normal.output,type="INTEGER",role="OUTPUT",executed=True,
                         structural_dependency=c["final_output"],state_agreement=trace_agreement(p,g,normal))))
    first=next((r["case_id"] for r in sorted(rows,key=lambda r:r["case_id"].encode()) if r["mechanical_match"]=="MATCH"),None)
    return dict(status="COVERED" if first else "NOT_COVERED",cases=rows,first_matching_case=first)
