"""Frozen-builder grammar adapter and prospective typed key extraction.

Only pure source-template functions are called. Candidate/case selection and
all builder write/entrypoint functions are deliberately never called.
"""
from __future__ import annotations
from dataclasses import asdict
from functools import lru_cache
import importlib.util
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence
from .interfaces import PHASE, SchemaError, rid
from .core_ir import Program, compile_program


@lru_cache(maxsize=1)
def _builder():
    path=Path(__file__).resolve().parents[3]/"scripts"/"build_phase3c_conf1_data.py"
    spec=importlib.util.spec_from_file_location("conf1_frozen_grammar_templates",path)
    if spec is None or spec.loader is None:raise SchemaError("frozen grammar unavailable")
    module=importlib.util.module_from_spec(spec)
    old=list(sys.path)
    try:
        sys.path.insert(0,str(path.parent));spec.loader.exec_module(module)
    finally:sys.path[:]=old
    return module


def graph_record(program:Program) -> dict[str,Any]:
    from .goco import _walk_stmt
    objects=[obj for top in program.statements for obj in _walk_stmt(top)]
    return {"nodes":[asdict(i) for i in program.items if i.kind=="NODE"],
        "edges":[asdict(i) for i in program.items if i.kind=="EDGE"],
        "complete_statement_tree":program.normalized_tree,"bindings":dict(program.roles),
        "semantic_records":program.semantic_records,"indicator_proofs":program.indicator_proofs,
        "state_analysis":program.state_analysis,"attribute_specs":program.attribute_specs,
        "runtime_semantics":{"statements":[asdict(s) for s in program.statements],"symbols":dict(program.symbols),
            "imports":sorted(program.imports),"ast_occurrence_bindings":[program.node_ids.get(id(obj)) for obj in objects],
            "typed_destination_ports":sorted(((dst,port,oid) for (dst,port),oid in program.edge_ids.items())),
            "primitive_aliases":dict(program.primitive_aliases),"index_nodes":dict(program.index_nodes)}}


def keys_from_ir(program:Program,output_obligations:Sequence[str]=()):
    from .contracts import ContractKey
    keys={};occurrences={};parents={};by_id={i.occurrence_id:i for i in program.items}
    constant_members={oid for spec in program.attribute_specs.values() for oid in spec["members"]}
    def put(key,oid):
        key.validate();keys[key.key_id]=key
        if oid not in occurrences.setdefault(key.key_id,[]):occurrences[key.key_id].append(oid)
    for item in program.items:
        if not item.essential or item.category=="VALUE_OR_LITERAL":continue
        if item.occurrence_id in constant_members or item.kind=="EDGE" and item.target in constant_members:continue
        if item.operation=="INITIALIZE" and item.result_role in {"ACCUMULATOR","DISPLAYED_ACCUMULATOR"}:continue
        kid=rid("KEY",[item.category,program.domain,item.operation,item.datatype,*item.operand_types,*item.operand_roles,item.result_role])
        put(ContractKey(kid,item.category,"BEHAVIORAL",program.domain,item.operation,item.operand_roles,item.result_role,"BOTH",operand_types=item.operand_types,result_type=item.datatype),item.occurrence_id)
        parents[item.occurrence_id]=kid
    for item in program.items:
        spec=program.attribute_specs.get(item.occurrence_id)
        if not item.essential or spec is None and item.category!="VALUE_OR_LITERAL":continue
        if spec is None and item.occurrence_id in constant_members:continue
        if spec is not None and not spec["parent_ontology_supported"]:continue
        parent=by_id.get(item.parent)
        if parent is None:raise SchemaError("attribute parent absent")
        initial=parent.operation=="INITIALIZE" and parent.result_role in {"ACCUMULATOR","DISPLAYED_ACCUMULATOR"}
        if not initial and parent.occurrence_id not in parents:raise SchemaError("attribute attachment absent")
        literal=item.datatype=="STRING"
        value=spec["computed_integer"] if spec else int(item.value) if item.datatype=="INTEGER" else None
        role=spec["semantic_role"] if spec else "INITIAL_ACCUMULATOR" if initial else item.result_role
        parent_key=None if initial else parents[parent.occurrence_id]
        op="LITERAL_TOKEN:"+str(item.value) if literal else f"COMPUTED_VALUE:{value}:{role}"
        kid=rid("KEY",["VALUE_OR_LITERAL",program.domain,op,role,parent_key or "INITIAL_ACCUMULATOR"])
        put(ContractKey(kid,"VALUE_OR_LITERAL","VALUE_OR_LITERAL_ATTRIBUTE",program.domain,op,(),role,"BOTH",
            "INITIAL_ACCUMULATOR" if initial else "ACTIVE_BEHAVIORAL_PARENT",parent_key,None if literal else value,
            None if literal else role,item.value if literal else None,result_type=item.datatype),item.occurrence_id)
    for category in output_obligations:
        output_requirement(category)
        kid=rid("KEY",["OUTPUT_CATEGORY",program.domain,category,"OUTPUT"])
        put(ContractKey(kid,"OUTPUT_CATEGORY","OUTPUT_ATTRIBUTE",program.domain,category,(),"OUTPUT","BOTH"),program.output_id)
    return tuple(keys.values()),{k:tuple(v) for k,v in occurrences.items()}


def output_requirement(operation:str) -> dict:
    if operation in {"OUTPUT_ZERO","OUTPUT_POSITIVE","OUTPUT_NEGATIVE","OUTPUT_MULTIDIGIT"}:
        return {"output_requirement_kind":"CATEGORY","output_category":operation,"exact_sentinel":None}
    prefix="OUTPUT_EXACT_SENTINEL:"
    if isinstance(operation,str) and operation.startswith(prefix):
        raw=operation[len(prefix):]
        try:value=int(raw)
        except ValueError as exc:raise SchemaError("invalid exact output sentinel") from exc
        if str(value)!=raw:raise SchemaError("noncanonical exact output sentinel")
        return {"output_requirement_kind":"EXACT_SENTINEL","output_category":None,"exact_sentinel":raw}
    raise SchemaError("unknown output obligation")


def lower_contract(ledger:Mapping[str,Any],slot:Mapping[str,Any],*,condition:str):
    from .contracts import CoverageContractV3, DOMAINS
    builder=_builder()
    if ledger!=builder.LEDGER or slot not in [s for group in ledger["slots"].values() for s in group]:raise SchemaError("not the frozen slot grammar")
    training="slot_id" in slot
    if condition not in {"ISOLATED","COMPOSITION","EVALUATION"} or training!=(condition!="EVALUATION"):raise SchemaError("condition/slot mismatch")
    if training:source=builder.train_source(condition.lower(),dict(slot))
    elif "primitive" in slot:source=builder.sanity_source(dict(slot))
    elif "structure" in slot:source=builder.structural_source(dict(slot))
    else:source=builder.primary_source(dict(slot))
    program_id=slot["slot_id"].replace("CONF1-",f"CONF1-{condition}-",1) if training else slot["task_id"]
    program=compile_program(program_id,source);domain=slot["family"];offset=slot.get("offset",0)
    if type(offset) is not int:raise SchemaError("initialization integer required")
    roles=dict(slot.get("role_predicates",{}))
    if training:roles={"P":slot["P"],"Q":slot["Q"]}
    elif "primitive" in slot:roles={"P":slot["primitive"]}
    elif slot.get("graph")=="G1":roles={r:p for r,p in roles.items() if r!="S"}
    elif "structure" in slot:roles={r:p for r,p in roles.items() if r in {"P","Q"}}
    definitions={x["name"]:x["expression"] for x in ledger["predicate_definitions"][domain]}
    kind=slot.get("structure","sum_per_item")
    recurrence={"sum_per_item":{"initial":offset,"total_next":"total + contribution"},
        "prefix_running_pair":{"initial":{"seen":0,"total":0},"total_next":"total + (seen if Q else 0)","seen_next":"seen + indicator(P)","order":["total_next","seen_next"]},
        "two_pass_product":{"initial":{"left":0,"right":0},"left_next":"left + indicator(P)","right_next":"right + indicator(Q)","output":"left * right","passes":["P","Q"]}}[kind]
    aggregator={"kind":kind,"recurrence":recurrence}
    if training:aggregator["treatment"]="PAIR_INDEPENDENT_ADD" if condition=="ISOLATED" else "PAIR_JOINT_MUL"
    # Offset alone does not declare case/output obligations. Never reproduce
    # the old blanket ZERO/POSITIVE invention while their full derivation is
    # unresolved. Such contracts cannot supply an authoritative row index.
    outputs=()
    keys,occurrences=keys_from_ir(program,outputs)
    primitive_names={item.operation for item in program.items if item.category=="SEMANTIC_PRIMITIVE" and item.essential}
    gaps=[]
    if not set(roles.values())<=primitive_names:gaps.append("SEMANTIC_PRIMITIVE_AND_PREDICATE_INDICATOR_EXTRACTION_INCOMPLETE")
    if any(program.item(oid).essential and not spec["parent_ontology_supported"] for oid,spec in program.attribute_specs.items()):
        gaps.append("COMPUTED_CONSTANT_SUBTREE_ATTACHMENT_INCOMPLETE")
    gaps.extend(("OUTPUT_CASE_OBLIGATIONS_UNRESOLVED","TASK_ESSENTIALITY_PROOF_INCOMPLETE"))
    contract=CoverageContractV3(1,PHASE,rid("CONTRACT",[program_id]),program_id,slot.get("slot_id",slot.get("task_id")),
        "training" if training else "primary" if slot.get("group")=="novel_composition" else "secondary",condition,domain,DOMAINS[domain],
        tuple((p,definitions[p]) for p in dict.fromkeys(roles.values())),tuple(roles.items()),aggregator,graph_record(program),keys,
        ("FIVE_CASES","PAIRED_CASE_INPUT_IDENTITY") if training else ("FIVE_CASES","BEHAVIOR_EXERCISE",*outputs),tuple(dict.fromkeys(program.roles.values())),
        {"role_count":len(roles),"aggregation_state_recurrence":recurrence,"state_registers":{n:r for n,r in program.roles.items() if r in {"ACCUMULATOR","DISPLAYED_ACCUMULATOR"}},
         "fixed_initialization":offset,"completeness_status":"REQUIRES_E5_CERTIFICATION"},source,occurrences,program,
        tuple(gaps))
    contract.validate();return contract
