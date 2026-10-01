"""Evidence assembly for new Boolean cases; no population entry point."""
from copy import deepcopy
import bm901_inputs as d
PREFLIGHT=d.overlap()
from sem900_runtime import contract
from self_learning_ai.conf1_v3.core_ir import compile_program,execute
from self_learning_ai.conf1_v3.goco import Expr,_walk_stmt
from self_learning_ai.conf1_v3.semantic_ir import source_flow_equivalence
from self_learning_ai.conf1_v3.boolean_mapping import complete_boolean_mapping,indicator_evidence,verify_complete_boolean_mapping
from self_learning_ai.conf1_v3.interfaces import ClosureError,SchemaError

PAIRS=(("AND","PRODUCT","LOCAL_PAIR_JOINT"),("OR","SUM_POSITIVE","BOOLEAN_OR"),
    ("PRODUCT","ALPHA_PRODUCT","LOCAL_PAIR_JOINT"),("SUM_POSITIVE","ALPHA_SUM_POSITIVE","BOOLEAN_OR"),
    ("REPEATED","ALPHA_REPEATED","LOCAL_PAIR_JOINT"))

def certificate(left,right,scope="LOCAL_PAIR_JOINT",alpha_map=None):
    c=contract(d.SOURCES[left],"BMAP901-"+left)
    return c,complete_boolean_mapping(c,d.SOURCES[right],scope=scope,alpha_map=alpha_map)

def negatives():
    rows=[]
    def add(name,fn,expected):
        try:r=fn();reason=r.get("reason","");finding=r.get("finding")
        except (ClosureError,SchemaError) as exc:reason=str(exc);finding="REJECTED"
        if finding not in {"UNRESOLVED","REJECTED"} or expected not in reason:
            raise AssertionError((name,finding,reason,expected))
        rows.append({"case":name,"finding":finding,"reason":reason,"required_semantic_reason":expected})
    add("incomplete_alpha",lambda:certificate("AND","PRODUCT",alpha_map={})[1],"alpha mapping")
    for name,left,scope,reason in (
        ("OMITTED","AND","LOCAL_PAIR_JOINT","INVENTORY_INCOMPLETE"),
        ("EXTRA_TERM","OR","BOOLEAN_OR","compound/unlisted"),
        ("COMPOUND","AND","LOCAL_PAIR_JOINT","compound/unlisted"),
        ("AMBIGUOUS","AND","LOCAL_PAIR_JOINT","ambiguous"),
        ("CONDITIONAL_RESET","AND","LOCAL_PAIR_JOINT","unconditional"),
        ("READ_BEFORE_WRITE","AND","LOCAL_PAIR_JOINT","after current-iteration"),
        ("STATE_ORDER","AND","LOCAL_PAIR_JOINT","INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE"),
        ("WRONG_TYPE","AND","LOCAL_PAIR_JOINT","expression type/operator"),
        ("MATCHING_OUTPUT_INVALID","AND","LOCAL_PAIR_JOINT","INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE"),
        ("SOURCE_ONLY","AND","LOCAL_PAIR_JOINT","SOURCE_ONLY_BINDING_OR_COMPUTATION"),
        ("UNLISTED","AND","LOCAL_PAIR_JOINT","compound/unlisted"),
        ("CIRCULAR","AND","LOCAL_PAIR_JOINT","circular indicator foundation")):
        add(name,lambda n=name,l=left,s=scope:certificate(l,n,s)[1],reason)
    c,good=certificate("PRODUCT","ALPHA_PRODUCT")
    dup=deepcopy(good);dup["predicate_correspondence"].append(deepcopy(dup["predicate_correspondence"][0]))
    add("duplicate_predicate_mapping",lambda:verify_complete_boolean_mapping(c,d.SOURCES["ALPHA_PRODUCT"],dup),"DUPLICATE_PREDICATE_MAPPING")
    missing=deepcopy(good);missing["predicate_correspondence"].pop()
    add("missing_contract_predicate",lambda:verify_complete_boolean_mapping(c,d.SOURCES["ALPHA_PRODUCT"],missing),"CONTRACT_PREDICATE_INVENTORY_INCOMPLETE")
    omitted=deepcopy(good);omitted["predicate_correspondence"][0]["source_predicate"]=good["source_inventory"]["nodes"][0]["occurrence_id"]
    add("omitted_source_predicate",lambda:verify_complete_boolean_mapping(c,d.SOURCES["ALPHA_PRODUCT"],omitted),"SOURCE_PREDICATE_INVENTORY_INCOMPLETE")
    p=compile_program("BMAP901-CROSS_LOOP",d.SOURCES["CROSS_LOOP"])
    exprs=[e for top in p.statements for e in _walk_stmt(top) if isinstance(e,Expr) and e.kind=="BINARY"]
    a=next(e for e in exprs if e.value=="&&");b=next(e for e in exprs if e.value=="*")
    add("cross_loop",lambda:source_flow_equivalence(p,a,p,b,context="LOCAL_PAIR_JOINT"),"loop/state contexts")
    # Range survives this candidate, but truth never gets assumed from it.
    p=compile_program("BMAP901-CIRCULAR",d.SOURCES["CIRCULAR"])
    assert p.indicator_proofs["bm901P"]["range"]==[0,1]
    return rows

def expected(name,raw):
    n=int(raw)
    if name in {"AND","PRODUCT","MATCHING_OUTPUT_INVALID"}:return str(79+sum(i%2==1 and i%3==2 for i in range(1,n+1)))
    if name in {"OR","SUM_POSITIVE"}:return str(79+sum(i%2==1 or i%3==2 for i in range(1,n+1)))
    raise ValueError("unlisted new development reference")
