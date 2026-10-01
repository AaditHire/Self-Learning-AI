"""Read-only disposable mapping reproduction; no population or historical execution."""
from pathlib import Path
import sys
import json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tests"));sys.path.insert(0,str(ROOT/"src"))
import bm901_inputs as d
overlap=d.overlap()
from sem900_runtime import contract
from self_learning_ai.conf1_v3.core_ir import compile_program
from self_learning_ai.conf1_v3.goco import Expr,_walk_stmt
from self_learning_ai.conf1_v3.semantic_ir import source_flow_equivalence
from self_learning_ai.conf1_v3.coverage import reconcile_complete_mapping

def run():
    results=[]
    for left,right,scope,op1,op2 in (("AND","PRODUCT","LOCAL_PAIR_JOINT","&&","*"),("OR","SUM_POSITIVE","BOOLEAN_OR","||",">")):
        a=compile_program("BMAP901-"+left,d.SOURCES[left]);b=compile_program("BMAP901-"+left,d.SOURCES[right])
        def expr(p,op):return next(e for s in p.statements for e in _walk_stmt(s) if isinstance(e,Expr) and e.kind=="BINARY" and e.value==op)
        local=source_flow_equivalence(a,expr(a,op1),b,expr(b,op2),context=scope)
        try:reconcile_complete_mapping(contract(a.source,a.program_id),b.source)
        except Exception as exc:failure={"type":type(exc).__name__,"reason":str(exc)}
        else:raise RuntimeError("pre-repair mapping unexpectedly accepted")
        results.append({"contract_form":left,"source_form":right,"local_proof":local,"complete_mapping_failure":failure})
    known={r["capability"] for n in ("ODD","RESIDUE","DIVISOR","HALF","ARRAY") for r in compile_program("BMAP901-"+n,d.SOURCES[n]).semantic_records}
    assert known=={"odd_index","residue_two","divisor_index","first_half","negative_value","even_value","large_magnitude","value_exceeds_index"}
    print(json.dumps({"starting_head":d.START,"reproductions":results,"primitive_catalog":sorted(known),"overlap_counts":{k:v for k,v in overlap.items() if k.endswith("overlap")}},indent=2))

if __name__=="__main__":run()
