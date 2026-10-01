"""Separate local catalog proof, complete V3.2 mapping, and indicator evidence.

This boundary deliberately does not transport an atomic AND key to an integer
MUL node merely because their local pair-joint relation is equal. Unsupported
topology remapping retains explicit unmatched inventories and cannot supply
indicator evidence. No output-agreement fallback or caller indicator sets.
"""
from dataclasses import asdict
import hashlib
from pathlib import Path

from .core_ir import compile_program,ungroup
from .goco import Expr,Stmt,_walk_stmt,alpha_bijection
from .interfaces import ClosureError,SchemaError,canonical_json_bytes
from .semantic_ir import source_flow_equivalence


def frozen_boolean_catalog():
    path=Path(__file__).resolve().parents[3]/"research/protocols/phase3c_conf1_coverage_v3_proposed.md"
    raw=path.read_bytes().replace(b"\r\n",b"\n")
    digest=hashlib.sha256(raw).hexdigest()
    if digest!="a9fb8350c849ce62e2a673e3ca1f1d5a08f556b7f415687f1e2eabdf356030f3":raise SchemaError("frozen Boolean authority changed")
    common={"frozen_rule_id":"V3.3","authority_path":str(path.relative_to(path.parents[2])).replace("\\","/"),
        "catalog_rule_label_kind":"implementation label for an existing frozen V3.3 clause; not a new authority ID",
        "authority_sha256_lf":digest,"authority_section":"V3.3 Uniform extraction and narrow equivalence",
        "complete_graph_equivalence_authorized":False,"general_algebra_authorized":False,
        "frozen_preconditions":["consistent alpha renaming","typed source-mapped operands and result",
            "no unlisted rewrites","no complete-graph equality without full-signature audit"],
        "implementation_safety_restrictions":["both source graphs independently reconstructed",
            "complete injective type/role-compatible alpha map","matching parsed loop contexts",
            "source-recognized frozen predicate identities and exact operand bindings",
            "every indicator write and initializer in {0,1}","one unconditional zero reset each iteration",
            "one predicate-controlled assignment to 1","read after current-iteration definitions",
            "exact reaching definitions; no stale/cross-loop/circular identity","duplicates retained"],
        "purity_totality":"closed typed scalar predicate trees; fixed bounded domain/decoder; no extra API calls",
        "state_order_requirement":"source-derived same-iteration flow; a range proof alone is insufficient",
        "mapping_precondition":"separate complete typed correspondence; no unmatched required source or contract occurrence"}
    return {"schema_version":1,"artifact_kind":"FROZEN_BOOLEAN_CATALOG_NOT_NEW_RULES","rules":[
        {**common,"catalog_rule":"AND_VS_PROVEN_01_PRODUCT_LOCAL_ONLY","scope":"LOCAL_PAIR_JOINT",
         "contract_topology":"and(Boolean,Boolean)","source_topology":"mul(proven indicator01,proven indicator01)",
         "operand_types":[["BOOLEAN","BOOLEAN"],["INTEGER","INTEGER"]],"result_types":["BOOLEAN","INTEGER"],
         "frozen_preconditions":common["frozen_preconditions"]+["both product operands proven 0/1; equality is ONLY for local pair-joint key, not atomic AND/MUL keys"]},
        {**common,"catalog_rule":"BOOLEAN_OR_VS_PROVEN_INDICATOR_SUM_POSITIVE","scope":"BOOLEAN_OR",
         "contract_topology":"or(Boolean,Boolean)","source_topology":"indicator(add(a,b)>0)",
         "operand_types":[["BOOLEAN","BOOLEAN"],["INTEGER","INTEGER"]],"result_types":["BOOLEAN","BOOLEAN-to-01 indicator"],
         "frozen_preconditions":common["frozen_preconditions"]+["both inputs proven Boolean; numeric carriers require actual source-flow truth proof; comparison/indicator typed and source-mapped"]}]}


def _sites(program,scope):
    found=[]
    for top in program.statements:
        for stmt in _walk_stmt(top):
            if not isinstance(stmt,Stmt):continue
            roots=stmt.expressions[:1] if stmt.kind=="IF" else stmt.expressions[1:] if stmt.kind=="UPDATE" else ()
            for root in roots:
                e=ungroup(root)
                if e.kind!="BINARY":continue
                if scope=="LOCAL_PAIR_JOINT" and e.value in {"&&","*"}:found.append(e)
                if scope=="BOOLEAN_OR" and (e.value=="||" or e.value==">" and ungroup(e.children[0]).value=="+"):found.append(e)
    return found


def _inventory(program):
    return {"program_id":program.program_id,"source":program.source,"source_sha256_utf8":hashlib.sha256(program.source.encode()).hexdigest(),
        "nodes":[asdict(i) for i in program.items if i.kind=="NODE"],"edges":[asdict(i) for i in program.items if i.kind=="EDGE"],
        "predicate_occurrences":list(program.semantic_records),"state_dependencies":program.state_analysis,
        "bindings":program.roles,"control_contexts":[{"statement_location":[s.start,s.end],"kind":s.kind,
            "occurrence_id":program.node_ids.get(id(s))} for top in program.statements for s in _walk_stmt(top) if isinstance(s,Stmt) and s.kind in {"IF","LOOP"}]}


def complete_boolean_mapping(contract,source,*,scope,alpha_map=None):
    """Integrate local V3.3 evidence with the actual total V3.2 mapper.

    A failed transport is a certificate of UNRESOLVED, never an accepted
    quotient graph. Full physical inventories remain available for audit.
    """
    frozen_boolean_catalog();contract.validate()
    expected=contract.ir;program=compile_program(contract.program_id,source)
    names=alpha_map if alpha_map is not None else dict(zip(expected.symbols,program.symbols))
    result={"schema_version":1,"artifact_kind":"COMPLETE_BOOLEAN_MAPPING_CERTIFICATE",
        "scope":scope,"contract_id":contract.contract_id,"source_inventory":_inventory(program),
        "contract_inventory":_inventory(expected),"alpha_mapping":names,"local_v33_proofs":[],
        "source_to_contract_occurrences":[],"predicate_correspondence":[],"typed_port_correspondence":[],
        "unmatched_source_inventory":[i.occurrence_id for i in program.items],
        "unmatched_contract_inventory":[i.occurrence_id for i in expected.items],
        "indicator_evidence_permitted":False,"complete_graph_equivalence_claim":False}
    try:
        if scope not in {"LOCAL_PAIR_JOINT","BOOLEAN_OR"}:raise SchemaError("UNLISTED_BOOLEAN_SCOPE")
        if alpha_map is None and len(expected.symbols)!=len(program.symbols):raise ClosureError("SOURCE_ONLY_BINDING_OR_COMPUTATION")
        alpha_bijection(expected.symbols,program.symbols,names)
        if any(expected.roles[a]!=program.roles[b] for a,b in names.items()):raise SchemaError("ALPHA_ROLE_MISMATCH")
        left,right=_sites(expected,scope),_sites(program,scope)
        if not left or len(left)!=len(right):raise ClosureError("BOOLEAN_RELATION_INVENTORY_INCOMPLETE")
        for a,b in zip(left,right):
            proof=source_flow_equivalence(expected,a,program,b,context=scope,alpha_map=names)
            result["local_v33_proofs"].append(proof)
            if proof["finding"]!="EQUIVALENT":raise ClosureError("LOCAL_BOOLEAN_PRECONDITION: "+proof["reason"])
        # This is a separate proof obligation. A local relation cannot change
        # typed atomic requirements, erase a node, or waive a port/state edge.
        from .coverage import reconcile_complete_mapping
        mapping=reconcile_complete_mapping(contract,source)
        if names!=dict(zip(expected.symbols,program.symbols)):
            raise ClosureError("ALPHA_MAPPING_DOES_NOT_MATCH_COMPLETE_BINDING_CORRESPONDENCE")
        table=dict(mapping.correspondence)
        if set(table)!=set(i.occurrence_id for i in expected.items) or set(table.values())!=set(i.occurrence_id for i in program.items):
            raise ClosureError("TOTAL_BOOLEAN_OCCURRENCE_TRANSPORT_UNIMPLEMENTED")
        result["source_to_contract_occurrences"]=[{"source_occurrence":b,"contract_occurrence":a,
            "source_location":program.item(b).location,"contract_location":expected.item(a).location,
            "type":program.item(b).datatype,"role":program.item(b).result_role} for a,b in mapping.correspondence]
        source_predicates={r["contract_occurrence_id"]:r for r in program.semantic_records}
        for r in expected.semantic_records:
            oid=r["contract_occurrence_id"];actual=source_predicates.get(table[oid])
            if actual is None or r["capability"]!=actual["capability"]:raise ClosureError("PREDICATE_CORRESPONDENCE_INCOMPLETE")
            result["predicate_correspondence"].append({"source_predicate":table[oid],"contract_predicate":oid,
                "capability":r["capability"],"source_control_context":actual["control_context"],"contract_control_context":r["control_context"],
                "source_ports":actual["input_ports"],"contract_ports":r["input_ports"],"result_type":r["result_type"]})
        if {p["source_predicate"] for p in result["predicate_correspondence"]}!=set(source_predicates):raise ClosureError("SOURCE_PREDICATE_INVENTORY_INCOMPLETE")
        result["typed_port_correspondence"]=[{"source_edge":table[i.occurrence_id],"contract_edge":i.occurrence_id,
            "source_endpoint":table[i.source],"target_endpoint":table[i.target],"port":i.port,"datatype":i.datatype,
            "source_role":i.operand_roles,"target_role":i.result_role} for i in expected.items if i.kind=="EDGE"]
        result.update(finding="COMPLETE",status="PASS",unmatched_source_inventory=[],unmatched_contract_inventory=[],indicator_evidence_permitted=True,
            mapping_basis="complete source-derived typed/role/port/state correspondence plus independent local V3.3 proofs",
            canonical_key_occurrences=dict(mapping.key_occurrences),equivalence_proofs=list(mapping.equivalence_proofs))
    except (SchemaError,ClosureError) as exc:
        result.update(finding="UNRESOLVED",status="UNRESOLVED",reason=str(exc),
            missing_transport_obligation="local Boolean relation does not supply all typed atomic/source/contract occurrence mappings")
    return result


def verify_complete_boolean_mapping(contract,source,certificate):
    """Independently reconstruct; serialized PASS/mapping/indicator flags are not proof."""
    pairs=certificate.get("predicate_correspondence",[])
    for field in ("source_predicate","contract_predicate"):
        ids=[r[field] for r in pairs]
        if len(ids)!=len(set(ids)):raise ClosureError("DUPLICATE_PREDICATE_MAPPING")
    if certificate.get("finding")=="COMPLETE":
        expected={r["contract_occurrence_id"] for r in contract.ir.semantic_records}
        actual={r["contract_predicate"] for r in pairs}
        if expected!=actual:raise ClosureError("CONTRACT_PREDICATE_INVENTORY_INCOMPLETE")
        p=compile_program(contract.program_id,source)
        if {r["contract_occurrence_id"] for r in p.semantic_records}!={r["source_predicate"] for r in pairs}:
            raise ClosureError("SOURCE_PREDICATE_INVENTORY_INCOMPLETE")
    rebuilt=complete_boolean_mapping(contract,source,scope=certificate.get("scope"),alpha_map=certificate.get("alpha_mapping"))
    if canonical_json_bytes(rebuilt)!=canonical_json_bytes(certificate):raise ClosureError("CERTIFICATE_RECONSTRUCTION_MISMATCH")
    if rebuilt["finding"]!="COMPLETE":raise ClosureError("COMPLETE_BOOLEAN_MAPPING_REQUIRED")
    return rebuilt


def indicator_evidence(contract,source,certificate):
    verified=verify_complete_boolean_mapping(contract,source,certificate)
    p=compile_program(contract.program_id,source)
    records=[];seen=set()
    for local in verified["local_v33_proofs"]:
        for proof in local["preconditions_and_flow_proofs"]:
            read=proof["indicator_read"]
            if read not in {i.occurrence_id for i in p.items}:continue  # Contract-side proof is separate.
            derived=next((r for r in p.indicator_proofs.values() if r==proof["range_proof"]),None)
            if derived is None:continue
            if read in seen:continue
            seen.add(read)
            records.append({"source_indicator_read":read,"source_location":p.item(read).location,
                "source_range_and_write_proof":derived,"current_iteration_reaching_definitions":p.state_analysis["read_definitions"][read],
                "frozen_rule_id":local["frozen_rule_id"],"actual_source_predicate":derived["predicate_definitions"][0]["predicate_occurrence"],
                "complete_source_mapping_sha256":hashlib.sha256(canonical_json_bytes(verified)).hexdigest(),
                "proof_dependency_order":["parsed typed source","frozen predicate recognition","reaching definitions","local V3.3 preconditions","complete V3.2 correspondence","indicator evidence"]})
    return {"schema_version":1,"artifact_kind":"INDICATOR_EVIDENCE_FROM_COMPLETE_MAPPING","records":records,
        "finding":"DERIVED" if records else "NO_USED_INDICATOR_EVIDENCE","complete_mapping_verified":True}
