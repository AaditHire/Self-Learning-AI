"""Serialized requirement checker. Does not import coverage or its constructor.

The frozen grammar catalog is shared data/interpretation, not a PASS oracle.
This checker independently reconstructs IDs, schemas, scope, multiplicity,
typed source correspondence, evidence bindings and raw-accounting partitions.
"""
import hashlib
from collections import Counter
from .interfaces import ClosureError, canonical_json_bytes, rid
from .contracts import DOMAINS, CATEGORIES
from .requirements import frozen_metadata, training_recipe, development_recipe, digest, SCOPES
from .core_ir import compile_program, ungroup
from .goco import Stmt, _walk_stmt, expressions_equivalent
from .contract_ir import graph_record, keys_from_ir
from .typed_alignment import align

def require(test, reason):
    if not test: raise ClosureError(reason)

def verify_plan(plan):
    require(set(plan)=={"schema_version","artifact_kind","scope","program_id","declaration","requirements","requirements_sha256","scientific_expected_row_index_eligible","completion","deferred_obligations"},"REQUIREMENT_PLAN_SCHEMA")
    require(plan["schema_version"]==1 and plan["scope"] in SCOPES,"REQUIREMENT_SCOPE_OR_VERSION")
    require(plan["artifact_kind"]=="PROSPECTIVE_REQUIREMENT_FOUNDATION_NOT_V35_POPULATION" and plan["scientific_expected_row_index_eligible"] is False and plan["completion"]=="FOUNDATION_ONLY_NOT_FULL_CONTRACT","REQUIREMENT_NOT_A_SCIENTIFIC_INDEX")
    ledger=frozen_metadata(); decl=plan["declaration"]; scope=plan["scope"]
    if scope=="SCIENTIFIC_TRAINING":
        require(set(decl)=={"slot_id","condition"},"SCIENTIFIC_DECLARATION_SCHEMA")
        slots=[s for s in ledger["slots"]["training_paired_slots"] if s["slot_id"]==decl["slot_id"]]
        require(len(slots)==1,"SCIENTIFIC_FROZEN_SLOT_REQUIRED"); slot=slots[0]
        pid=slot["slot_id"].replace("CONF1-",f"CONF1-{decl['condition']}-",1); family=slot["family"]
        recipe=training_recipe(slot,decl["condition"],ledger)
        provenance=dict(authority_path="research/protocols/phase3c_conf1_slots.json",authority_sha256_lf="83436eecda3affe813b785e868e3f8936fa59afc35ded0eb6a54290edb41dc88",slot_id=slot["slot_id"],sections=["Coverage V3.1/V3.2/V3.6","CONF1 protocol §6"],frozen_slot=slot,frozen_training_semantics=ledger["training_semantics"],condition=decl["condition"])
        require(plan["deferred_obligations"]==["OUTPUT_CASE_OBLIGATIONS_UNRESOLVED","VALUE_LITERAL_ATTACHMENT_COMPLETE_UNRESOLVED","COMPLETE_TYPED_SOURCE_MAPPING_NOT_RUN"],"SCIENTIFIC_COMPLETION_INVENTED")
    elif scope=="DEVELOPMENT_ONLY":
        recipe=development_recipe(decl,ledger); pid=decl["program_id"]; family=decl["family"]
        provenance=dict(authority_path="research/protocols/phase3c_conf1_slots.json",slot_id=None,frozen_role_map_created=False,scientific_slot_binding=None,authority_sections=["Coverage V3.3 implementation projection only"],declaration_sha256=digest(decl))
        require(plan["deferred_obligations"]==[],"DEVELOPMENT_PLAN_SCHEMA")
    else: raise ClosureError("EVALUATION_REQUIREMENT_DERIVATION_NOT_IMPLEMENTED")
    require(plan["program_id"]==pid,"REQUIREMENT_PROGRAM_ID")
    # Group repeated scientific occurrences by prospective capability key.
    # Development stress projections deliberately keep their separate paths.
    groups={}
    for u in recipe:
        cap={k:v for k,v in u.items() if k!="path"}; identity=digest(cap) if scope=="SCIENTIFIC_TRAINING" else u["path"]
        groups.setdefault(identity,[]).append(u)
    rows=plan["requirements"]; require(len(rows)==len(groups),"REQUIREMENT_MISSING_OR_INVENTED")
    require(len({r["requirement_id"] for r in rows})==len(rows),"DUPLICATE_REQUIREMENT_ID")
    row_fields={"scope","program_id","canonical_contract_key","requirement_id","capability","requirement_class","evidence_kind","family","input_domain","semantic_role","operand_types","result_type","occurrence_requirements","multiplicity","provenance","derivation_reason"}
    for r,units in zip(rows,groups.values()):
        u=units[0]
        require(set(r)==row_fields,"REQUIREMENT_RECORD_SCHEMA")
        cap={k:v for k,v in u.items() if k!="path"}; kind="VALUE_OR_LITERAL_ATTRIBUTE" if cap["category"]=="VALUE_OR_LITERAL" else "BEHAVIORAL"
        key=rid(scope+"_KEY",[family,DOMAINS[family],digest(cap)]); req=rid(scope+"_REQUIREMENT",[pid,key] if scope=="SCIENTIFIC_TRAINING" else [pid,key,u["path"]])
        require(cap["category"] in CATEGORIES or cap["category"] is None and cap["operation"]=="LOCAL_PAIR_JOINT","UNAUTHORIZED_REQUIREMENT_ONTOLOGY")
        checks={"scope":scope,"program_id":pid,"canonical_contract_key":key,"requirement_id":req,"capability":cap,"evidence_kind":kind,"family":family,"input_domain":DOMAINS[family],"semantic_role":cap["semantic_role"],"operand_types":cap["operand_types"],"result_type":cap["result_type"],"multiplicity":1,"provenance":provenance,"requirement_class":"LOCAL_PAIR_JOINT_RELATION_EXCEPTION" if cap["category"] is None else "ONTOLOGY_KEY","occurrence_requirements":[dict(occurrence_id=rid(scope+"_OCCURRENCE",[req,u["path"]]),grammar_path=u["path"])],"derivation_reason":"Required by declared semantic grammar before parsing/mapping; raw syntax, outputs and evidence outcomes are not inputs"}
        checks["multiplicity"]=len(units)
        checks["occurrence_requirements"]=[dict(occurrence_id=rid(scope+"_OCCURRENCE",[req,x["path"]]),grammar_path=x["path"]) for x in units]
        require(canonical_json_bytes(r)==canonical_json_bytes(checks),"REQUIREMENT_DERIVATION_OR_NAMESPACE_MISMATCH")
    require(plan["requirements_sha256"]==digest(rows),"REQUIREMENT_SET_HASH")
    return dict(status="VERIFIED",scope=scope,program_id=pid,requirements_sha256=digest(rows),source_or_output_used_to_derive_requirements=False)

def expected_bindings(plan,c,p,base,bundle=None):
    verify_plan(plan); require(plan["program_id"]==c.program_id,"WRONG_REQUIREMENT_PROGRAM")
    if plan["scope"]!="DEVELOPMENT_ONLY":
        require(c.program_id==plan["program_id"] and c.task_kind=="training" and c.slot_id==plan["declaration"]["slot_id"] and c.condition==plan["declaration"]["condition"],"SCIENTIFIC_SLOT_BINDING_REQUIRED")
        # No candidate construction/source acceptance is performed by this pass.
        raise ClosureError("SCIENTIFIC_SOURCE_REQUIREMENT_MAPPING_UNRESOLVED")
    require(c.task_kind=="development","DEVELOPMENT_TO_SCIENTIFIC_PROMOTION_FORBIDDEN")
    table=dict(base["ordinary_correspondence"]); result=[]
    if bundle is not None:
        from .transport_verifier import verify_canonical_transport, verify_mapping_proof_record
        verify_canonical_transport(bundle); verify_mapping_proof_record(bundle,base)
        regions=bundle["total_mapping_certificate"]["regions"]
        require(len(regions)==len(plan["requirements"]),"MISSING_OR_MERGED_REQUIRED_OCCURRENCE")
        for req,region,t in zip(plan["requirements"],regions,bundle["transports"]):
            cap=req["capability"]; expected_scope="LOCAL_PAIR_JOINT" if cap["operation"]=="LOCAL_PAIR_JOINT" else "BOOLEAN_OR" if cap["operation"]=="OR" else None
            relation=region["local_v33_proof"]["normalized_local_relation"]
            require(region["scope"]==expected_scope and sorted(x[1] for x in relation[1:])==sorted(cap["dependencies"]),"VALID_TRANSPORT_WRONG_CANONICAL_REQUIREMENT")
            require(req["operand_types"]==["BOOLEAN","BOOLEAN"] and req["result_type"]=="BOOLEAN" and req["family"]==c.domain and req["input_domain"]==c.input_domain,"REQUIREMENT_TRANSPORT_TYPE_DOMAIN")
            result.append(dict(requirement_id=req["requirement_id"],canonical_contract_key=req["canonical_contract_key"],scope=req["scope"],evidence_kind=req["evidence_kind"],method="AUTHORIZED_V33_EQUIVALENCE",contract_occurrences=[region["contract"]["expression_node"]],source_occurrences=[region["source"]["expression_node"]],evidence_id=t["transport_id"]))
    else:
        alignment=align(c.ir,p)
        require(dict(alignment["correspondence"])==table,"SERIALIZED_TYPED_MAPPING_MISMATCH")
        require(base["program_id"]==c.program_id and base["contract_id"]==rid("CONTRACT",[c.program_id]),"SERIALIZED_MAPPING_ID_CHANGED")
        require(canonical_json_bytes(base["key_occurrences"])==canonical_json_bytes({k:[table[o] for o in ids] for k,ids in c.key_occurrences.items()}),"SERIALIZED_RAW_KEY_OCCURRENCES_CHANGED")
        require(canonical_json_bytes(base["obligation_satisfaction"])==canonical_json_bytes({"direct":base["ordinary_correspondence"],"regional":[]}),"SERIALIZED_OBLIGATION_ACCOUNTING_CHANGED")
        expected=alignment["equivalence_claims"]
        if base["equivalence_proofs"] and "contract_root" not in base["equivalence_proofs"][0]:
            # Legacy restricted computed-value proof shape, reconstructed from
            # independently aligned roots; no generic folding implementation.
            converted=[]
            for x in expected:
                require(x["catalog_rule"]=="WHOLLY_INTEGER_CONSTANT_NEG_ADD_SUB_MUL_COMPUTED_KEY_ONLY","SERIALIZED_EQUIVALENCE_CLAIM_MISSING")
                a,b=x["contract_root"],x["source_root"]
                converted.append(dict(frozen_rule_id="V3.3",catalog_rule=x["catalog_rule"],source_locations=[c.ir.item(a).location,p.item(b).location],result_type="INTEGER",computed_integer=c.ir.attribute_specs[a]["computed_integer"],semantic_role=c.ir.attribute_specs[a]["semantic_role"],contract_accounted_occurrences=alignment["contract_hidden"].get(a,[]),source_accounted_occurrences=alignment["source_hidden"].get(b,[]),affected_occurrence_mapping=[a,b],preconditions="maximal source-mapped pure integer constant tree; neg/add/sub/mul only; same exact value and role; no literal-token obligation"))
            expected=converted
        require(canonical_json_bytes(base["equivalence_proofs"])==canonical_json_bytes(expected),"SERIALIZED_INVOKED_EQUIVALENCE_CLAIMS_CHANGED")
        updates=[]
        def sites(rows, parent=None):
            for s in rows:
                if s.kind=="UPDATE" and c.ir.roles[s.expressions[0].value]=="DISPLAYED_ACCUMULATOR": updates.append((s,parent))
                sites(s.children,s)
        sites(c.ir.statements)
        declaration=plan["declaration"]; require(len(updates)==len(declaration["contributions"]),"MISSING_REQUIRED_CONTRIBUTION")
        from .requirements import expression
        def binding(role):
            found=[n for n,r in c.ir.roles.items() if r==role]
            require(len(found)==1,"REQUIREMENT_DOMAIN_ROLE_AMBIGUOUS"); return found[0]
        abstract_names={"n":binding("INPUT_LIMIT"),"i":binding("DOMAIN_ITEM")}
        # Whole-symbol bijection is not needed here: this is grammar embedding,
        # not the independently checked complete-program alpha correspondence.
        def embedding(e):
            from dataclasses import replace
            return replace(e,value=abstract_names.get(e.value,e.value),children=tuple(embedding(x) for x in e.children))
        paths={}
        def collect(e,path):
            e=ungroup(e); oid=c.ir.node_ids[id(e)]; paths[path]=oid
            for i,child in enumerate(e.children):
                cp=path+f"/operand/{i}"; collect(child,cp)
                edge=[x for x in c.ir.items if x.kind=="EDGE" and x.target==oid and x.port==i and x.operation=="VALUE_TO_OPERATOR"]
                require(len(edge)==1,"REQUIREMENT_EDGE_MISSING"); paths[cp+"/edge"]=edge[0].occurrence_id
        for i,(decl,(update,parent)) in enumerate(zip(declaration["contributions"],updates)):
            if decl["mode"]=="COUNT_TRUE":
                require(parent is not None and parent.kind=="IF" and len(parent.children)==1 and update.value=="+=" and ungroup(update.expressions[1]).value=="1","COUNT_PROJECTION_SINGLETON_BRIDGE_REQUIRED")
                b=ungroup(parent.expressions[0])
            else: b=ungroup(update.expressions[1])
            a=embedding(expression(decl["expression"]))
            require(expressions_equivalent(a,b,left_symbols=c.ir.symbols,right_symbols=c.ir.symbols),"REFERENCE_DOES_NOT_REALIZE_PROSPECTIVE_GRAMMAR")
            collect(b,f"contribution/{i}")
        for req in plan["requirements"]:
            path=req["occurrence_requirements"][0]["grammar_path"]; require(path in paths,"REQUIREMENT_GRAMMAR_LOCATION_MISSING")
            ao=paths[path]; require(ao in table,"GENUINE_REQUIRED_ATOMIC_COMPONENT_MISSING")
            bo=table[ao]; cap=req["capability"]; actual=c.ir.item(ao)
            require(actual.operation==cap["operation"] or cap["operation"]=="COMPUTED_VALUE" and actual.category=="VALUE_OR_LITERAL","REQUIREMENT_ATOMIC_OPERATION_CHANGED")
            claims=[x for x in alignment["equivalence_claims"] if ao in x["contract_members"] or actual.kind=="EDGE" and actual.target==x["contract_root"]]
            result.append(dict(requirement_id=req["requirement_id"],canonical_contract_key=req["canonical_contract_key"],scope=req["scope"],evidence_kind=req["evidence_kind"],method="AUTHORIZED_V33_EQUIVALENCE" if claims else "DIRECT_TYPED_CORRESPONDENCE",contract_occurrences=[ao],source_occurrences=[bo],evidence_id=digest(claims) if claims else None))
    require(len({r["requirement_id"] for r in result})==len(plan["requirements"]),"DUPLICATE_OR_MISSING_REQUIREMENT_SATISFACTION")
    require(len({r["source_occurrences"][0] for r in result})==len(result),"MERGED_REQUIRED_OCCURRENCES")
    return result

def classify_raw(c,base,bindings,bundle=None):
    by_oid={o:b for b in bindings for o in b["contract_occurrences"]}
    internal={o for t in (bundle or {}).get("transports",[]) for o in t["raw_contract_members"]}
    resolutions={r["key_id"]:r for r in base["raw_key_resolution"]}; out=[]
    for key in c.canonical_keys:
        ids=c.key_occurrences[key.key_id]; science=[by_oid[o]["requirement_id"] for o in ids if o in by_oid and by_oid[o]["scope"]!="DEVELOPMENT_ONLY"]
        support=[by_oid[o]["requirement_id"] for o in ids if o in by_oid and by_oid[o]["scope"]=="DEVELOPMENT_ONLY"]
        if science: label="CANONICAL_REQUIRED_VIA_EQUIVALENCE" if any(by_oid[o]["method"]=="AUTHORIZED_V33_EQUIVALENCE" for o in ids if o in by_oid) else "CANONICAL_REQUIRED_DIRECT"; reason="Exact prospectively bound scientific requirement"
        elif set(ids)&internal: label="AUTHORIZED_EQUIVALENCE_INTERNAL"; reason="Retained local V3.3 implementation members; no scientific slot created this development raw identity"
        elif all(not c.ir.item(o).essential for o in ids): label="REFERENCE_ONLY_CANDIDATE"; reason="Pure unused structure requires its existing source non-observability proof; not a scientific requirement"
        else: label="IMPLEMENTATION_ONLY_DIAGNOSTIC"; reason="Raw identity of an explicitly development-only program; no frozen training/evaluation slot binding; cannot supply scientific evidence"
        ordinary=dict(base["ordinary_correspondence"]); member_accounting=[]
        for oid in ids:
            refs=[t["transport_id"] for t in (bundle or {}).get("transports",[]) if oid in t["raw_contract_members"]]
            method="DIRECT_TYPED_CORRESPONDENCE" if oid in ordinary else "AUTHORIZED_EQUIVALENCE_INTERNAL" if refs else "UNACCOUNTED_RAW_MEMBER"
            require(method!="UNACCOUNTED_RAW_MEMBER","UNACCOUNTED_RELEVANT_RAW_MEMBER")
            member_accounting.append(dict(contract_occurrence=oid,method=method,source_occurrence=ordinary.get(oid),transport_references=refs))
        out.append(dict(raw_key_id=key.key_id,operation=key.operation,classification=label,reason=reason,raw_contract_occurrences=list(ids),raw_member_accounting=member_accounting,
            raw_resolution=resolutions.get(key.key_id),scientific_requirement_ids=science,development_projection_support_ids=support,scientific_satisfaction_claim=False))
    require(len(out)==len(c.canonical_keys),"RAW_KEY_ACCOUNTING_INCOMPLETE")
    return out

def verify_requirement_evidence(evidence):
    require(set(evidence)=={"schema_version","artifact_kind","before","after","reference_source","source","contract_graph","source_graph","base_mapping","transport_bundle","bindings","raw_classification","integrated_claims","dependency_scope"},"REQUIREMENT_EVIDENCE_SCHEMA")
    before,after=evidence["before"],evidence["after"]
    require(canonical_json_bytes(before)==canonical_json_bytes(after),"REQUIREMENT_SET_OR_SCOPE_CHANGED"); checked=verify_plan(before)
    pid=before["program_id"]; c=compile_program(pid,evidence["reference_source"]); p=compile_program(pid,evidence["source"])
    require(canonical_json_bytes(graph_record(c))==canonical_json_bytes(evidence["contract_graph"]) and canonical_json_bytes(graph_record(p))==canonical_json_bytes(evidence["source_graph"]),"REQUIREMENT_RAW_GRAPH_TRACE_CHANGED")
    base=evidence["base_mapping"]; require(base["source_sha256"]==hashlib.sha256(p.source.encode()).hexdigest(),"REQUIREMENT_SOURCE_HASH")
    # A tiny structural adapter, not CoverageContractV3 construction.
    from types import SimpleNamespace
    keys,occurrences=keys_from_ir(c,())
    adapter=SimpleNamespace(program_id=pid,task_kind="development",ir=c,domain=c.domain,input_domain=DOMAINS[c.domain],canonical_keys=keys,key_occurrences=occurrences)
    bindings=expected_bindings(before,adapter,p,base,evidence["transport_bundle"])
    require(canonical_json_bytes(bindings)==canonical_json_bytes(evidence["bindings"]),"REQUIREMENT_BINDING_TAMPERED_OR_WRONG")
    require(canonical_json_bytes(classify_raw(adapter,base,bindings,evidence["transport_bundle"]))==canonical_json_bytes(evidence["raw_classification"]),"RAW_CLASSIFICATION_TAMPERED")
    require(canonical_json_bytes(expected_claims(c,p,bindings,evidence["transport_bundle"]))==canonical_json_bytes(evidence["integrated_claims"]),"INVOKED_V33_CLAIMS_TAMPERED")
    require(canonical_json_bytes(dependency_scope(evidence["dependency_scope"]["deferred_contract_gaps"],before))==canonical_json_bytes(evidence["dependency_scope"]),"UNPROVED_BOOLEAN_DEPENDENCY_SCOPE")
    return dict(status="VERIFIED",scope=checked["scope"],requirements_sha256=checked["requirements_sha256"],
        preservation="EXACT_BEFORE_AFTER",cross_scope_transfers=0,satisfaction_paths=len(bindings),raw_keys_accounted=len(keys),
        scientific_satisfaction_claims=0,constructor_pass_flag_trusted=False,raw_atomic_equality_required=False)

DEFERRED_DEVELOPMENT_GAPS={"COMPUTED_CONSTANT_SUBTREE_ATTACHMENT_INCOMPLETE","OUTPUT_CASE_OBLIGATIONS_UNRESOLVED","TASK_ESSENTIALITY_PROOF_INCOMPLETE","V35_ACTIVITY_UNRESOLVED","E5_SIGNATURE_UNRESOLVED","V3_5_POPULATION_UNRESOLVED"}

def dependency_scope(gaps,plan):
    verify_plan(plan)
    require(plan["scope"]=="DEVELOPMENT_ONLY" or not gaps,"SCIENTIFIC_FOUNDATION_NOT_CLEARED_BY_DEVELOPMENT_PROJECTION")
    require(set(gaps)<=DEFERRED_DEVELOPMENT_GAPS,"RELEVANT_BOOLEAN_FOUNDATION_UNRESOLVED")
    return dict(deferred_contract_gaps=list(gaps),scope=plan["scope"],
        required_foundations=["PROSPECTIVE_DECLARATION","TYPED_SOURCE_DOMAIN_ROLE","PRIMITIVE_IDENTITY_WHEN_USED","CURRENT_ITERATION_REACHING_WHEN_USED","COMPLETE_RAW_STRUCTURE_ACCOUNTING","ACTUALLY_INVOKED_V33_RULE"],
        scientific_contract_completion_claim=False,all_catalog_rules_required=False,raw_atomic_key_equality_required=False,
        output_activity_population_dependencies=False,
        reason="Independent development projection foundation and proof-specific types/flow must resolve; deferred full scientific contract gaps remain open, never waived")

def expected_claims(c,p,bindings,bundle=None):
    if bundle:
        out=[]
        for t,r in zip(bundle["transports"],bundle["total_mapping_certificate"]["regions"]):
            affected=[b["requirement_id"] for b in bindings if b["evidence_id"]==t["transport_id"]]
            out.append(dict(frozen_rule_id="V3.3",catalog_rule=t["catalog_rule"],source_locations=r["local_v33_proof"]["source_locations"] if "source_locations" in r["local_v33_proof"] else [c.item(r["contract"]["expression_node"]).location,p.item(r["source"]["expression_node"]).location],
                operand_types=r["local_v33_proof"]["operand_types"],result_type=p.item(r["source"]["expression_node"]).datatype,
                semantic_roles=t["roles"],alpha_mapping=t["alpha_mapping"],duplicates_retained=True,
                preconditions=t["indicator_reaching_evidence"],affected_requirements=affected,contract_members=t["raw_contract_members"],source_members=t["raw_source_members"],
                scientific_requirement_transfer=False))
        return out
    alignment=align(c,p); out=[]
    if any(x!=y for x,y in alignment["alpha_mapping"].items()):
        out.append(dict(frozen_rule_id="V3.3",catalog_rule="CONSISTENT_ALPHA_RENAMING",alpha_mapping=alignment["alpha_mapping"],source_locations=[[0,len(c.source.encode())],[0,len(p.source.encode())]],operand_types={"contract":c.symbols,"source":p.symbols},result_type="COMPLETE_TYPED_BINDINGS",semantic_roles={"contract":c.roles,"source":p.roles},duplicates_retained=True,preconditions="bijective type/role-preserving declaration/use bindings",contract_members=[a for a,b in alignment["correspondence"]],source_members=[b for a,b in alignment["correspondence"]],affected_requirements=[b["requirement_id"] for b in bindings],scientific_requirement_transfer=False))
    for claim in alignment["equivalence_claims"]:
        affected=[b["requirement_id"] for b in bindings if set(b["contract_occurrences"])&set(claim["contract_members"]) or c.item(b["contract_occurrences"][0]).target==claim["contract_root"]]
        out.append({**claim,"affected_requirements":affected,"scientific_requirement_transfer":False})
    return out
