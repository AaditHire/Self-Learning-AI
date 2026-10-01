"""Fresh source/metadata projections; no scientific rows or expected labels."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
START="26583dd1a6cfd6375455000d8f2ddfb1c5c5c048"
P,Q="creq904Item%2==1","creq904Item%3==2"
HEADER="NUMBER creq904Limit. INPUT(creq904Limit). NUMBER creq904Total=347. "
INDICATORS="NUMBER creq904P=0. NUMBER creq904Q=0. "
PRELUDE=f"creq904P=0. creq904Q=0. IF ({P}) {{ creq904P=1. }} IF ({Q}) {{ creq904Q=1. }} "
AND=f"IF (({P})&&({Q})) {{ creq904Total+=1. }} "
OR=f"IF (({P})||({Q})) {{ creq904Total+=1. }} "
PRODUCT="creq904Total+=(creq904P*creq904Q). "
SUM="IF (creq904P+creq904Q>0) { creq904Total+=1. } "
def source(body,indicators=False):
    return HEADER+(INDICATORS if indicators else "")+"LOOP (NUMBER creq904Item=1 TILL creq904Item<=creq904Limit, creq904Item++) { "+body+"} DISPLAYNL(creq904Total)."
SOURCES={"AND":source(PRELUDE+AND,True),"PRODUCT":source(PRELUDE+PRODUCT,True),"OR":source(PRELUDE+OR,True),"SUM":source(PRELUDE+SUM,True),
    "REPEATED_AND":source(PRELUDE+AND+AND,True),"REPEATED_PRODUCT":source(PRELUDE+PRODUCT+PRODUCT,True),
    "DIRECT":source("creq904Total+=(creq904Limit+creq904Item). "),
    "COMMUTATIVE":source("creq904Total+=(creq904Item+creq904Limit). "),
    "MUL":source("creq904Total+=(creq904Limit*creq904Item). "),
    "MUL_SWAP":source("creq904Total+=(creq904Item*creq904Limit). "),
    "DUPLICATES":source("creq904Total+=((creq904Limit+creq904Item)*(creq904Limit+creq904Item)). "),
    "DUPLICATES_SWAP":source("creq904Total+=((creq904Item+creq904Limit)*(creq904Limit+creq904Item)). "),
    "GT":source("IF (creq904Limit>creq904Item) { creq904Total+=1. } "),
    "LT_REVERSED":source("IF (creq904Item<creq904Limit) { creq904Total+=1. } "),
    "GE":source("IF (creq904Limit>=creq904Item) { creq904Total+=1. } "),
    "LE_REVERSED":source("IF (creq904Item<=creq904Limit) { creq904Total+=1. } "),
    "EQ":source("IF (creq904Limit==creq904Item) { creq904Total+=1. } "),
    "EQ_REVERSED":source("IF (creq904Item==creq904Limit) { creq904Total+=1. } "),
    "ASSOCIATION":source("creq904Total+=((creq904Limit+creq904Item)+5). "),
    "REASSOCIATED":source("creq904Total+=(creq904Limit+(creq904Item+5)). "),
    "BARE_AND":source(AND),
    "EXTRA_LIVE":source("creq904Total+=(creq904Limit+creq904Item). creq904Total+=creq904Item. "),
}
SOURCES["FOLDED"]=SOURCES["DIRECT"].replace("=347.","=(340+7).")
SOURCES["INCIDENTAL"]=SOURCES["DIRECT"].replace("LOOP (","NUMBER creq904Unused=349. LOOP (")
SOURCES["BOOL_AND_SORT"]=source("IF ((creq904Limit%3==2)&&(creq904Item%2==1)) { creq904Total+=1. } ")
SOURCES["BOOL_AND_SORTED"]=source("IF ((creq904Item%2==1)&&(creq904Limit%3==2)) { creq904Total+=1. } ")
SOURCES["BOOL_OR_SORT"]=SOURCES["BOOL_AND_SORT"].replace("&&","||")
SOURCES["BOOL_OR_SORTED"]=SOURCES["BOOL_AND_SORTED"].replace("&&","||")
for name in ("DIRECT","PRODUCT","SUM","REPEATED_PRODUCT"):
    SOURCES["ALPHA_"+name]=SOURCES[name].replace("creq904","projected914")
PAIRS=(("AND","PRODUCT","LOCAL_PAIR_JOINT"),("OR","SUM","BOOLEAN_OR"),("AND","ALPHA_PRODUCT","LOCAL_PAIR_JOINT"),("OR","ALPHA_SUM","BOOLEAN_OR"),("REPEATED_AND","REPEATED_PRODUCT","LOCAL_PAIR_JOINT"),("REPEATED_AND","ALPHA_REPEATED_PRODUCT","LOCAL_PAIR_JOINT"))
NUMERIC={"DIRECT":("n+i","NUMERIC_UPDATE"),"MUL":("n*i","NUMERIC_UPDATE"),"DUPLICATES":("(n+i)*(n+i)","NUMERIC_UPDATE"),"GT":("n>i","COUNT_TRUE"),"GE":("n>=i","COUNT_TRUE"),"EQ":("n==i","COUNT_TRUE"),"ASSOCIATION":("(n+i)+5","NUMERIC_UPDATE"),"INCIDENTAL":("n+i","NUMERIC_UPDATE")}
NUMERIC.update(BOOL_AND_SORT=("(n%3==2)&&(i%2==1)","COUNT_TRUE"),BOOL_OR_SORT=("(n%3==2)||(i%2==1)","COUNT_TRUE"))
RAW=("0000000000000041","0000000000000047","0000000000000059","0000000000000067","0000000000000071")
def declaration(name):
    if name in NUMERIC: expr,mode=NUMERIC[name]; contributions=[dict(expression=expr,mode=mode)]; roles={}
    else:
        expr="P||Q" if name=="OR" else "P&&Q"; mode="COUNT_TRUE"; roles={"P":"odd_index","Q":"residue_two"}
        contributions=[dict(expression=expr,mode=mode) for _ in range(2 if name=="REPEATED_AND" else 1)]
    return dict(program_id="CREQ904-"+name,family="numeric_iteration",role_bindings=roles,contributions=contributions)
def inventory():
    values=dict(ids=["CREQ904-"+n for n in SOURCES],sources=list(SOURCES.values()),expressions=[P,Q,"P&&Q","P||Q",*(x[0] for x in NUMERIC.values())],raw_inputs=list(RAW))
    return {k:[dict(value=v,sha256_utf8=hashlib.sha256(v.encode()).hexdigest()) for v in rows] for k,rows in values.items()}
def overlap():
    def strings(v):
        if isinstance(v,str): yield v
        elif isinstance(v,list):
            for x in v: yield from strings(x)
        elif isinstance(v,dict):
            for k,x in v.items(): yield k; yield from strings(x)
    files=sorted((ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixtures").glob("*.json"))
    if len(files)!=13: raise RuntimeError("protected fixture corpus changed")
    historical=set()
    for path in (*files,ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"):
        historical.update(strings(json.loads(path.read_bytes())))
    new={r["value"] for rows in inventory().values() for r in rows}; hashes={hashlib.sha256(v.encode()).hexdigest() for v in new}
    result=dict(exact_string_overlap=len(new&historical),recorded_hash_overlap=len(hashes&historical),recomputed_string_hash_overlap=len(hashes&{hashlib.sha256(v.encode()).hexdigest() for v in historical}))
    if any(result.values()): raise RuntimeError("new disposable overlap")
    return dict(starting_head=START,historical_fixture_files=13,expected_labels_parsed=False,inventory=inventory(),**result)
