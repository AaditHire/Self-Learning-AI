"""Complete pass-specific disposable inventory, classifier-free preflight."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
RAW=("000000","000003","000007","000011","000019")
ARRAY_RAW=("-37|0|43|2","-41|6|0|47","8|-53|0|59","0|0|-61|67","-71|10|13|0")
PREDICATES=("sem900Index%2==1","sem900Index%3==2","sem900Bound%sem900Index==0","2*sem900Index<=sem900Bound")
ARRAY_PREDICATES=("sem900Values[sem900Index]<0","sem900Values[sem900Index]%2==0",
                  "sem900Values[sem900Index]*sem900Values[sem900Index]>4","sem900Values[sem900Index]>sem900Index")
PREFIX="NUMBER sem900Bound. INPUT(sem900Bound). "
def loop(body):
    return "LOOP (NUMBER sem900Index=1 TILL sem900Index<=sem900Bound, sem900Index++) { "+body+" } DISPLAYNL(sem900Total)."
SOURCES={}
for name,p in zip(("ODD","RESIDUE","DIVISOR","HALF"),PREDICATES):
    SOURCES[name]=PREFIX+"NUMBER sem900Total=37. "+loop("IF ("+p+") { sem900Total+=1. }")
SOURCES["REPEAT"]=PREFIX+"NUMBER sem900Total=37. "+loop("IF ("+PREDICATES[0]+") { sem900Total+=1. } IF ("+PREDICATES[0]+") { sem900Total+=1. }")
SOURCES["PREFIX"]=PREFIX+"NUMBER sem900Seen=0. NUMBER sem900Total=37. "+loop("IF ("+PREDICATES[1]+") { sem900Total+=sem900Seen. } IF ("+PREDICATES[0]+") { sem900Seen+=1. }")
SOURCES["TWO_PASS"]=PREFIX+"NUMBER sem900Left=0. NUMBER sem900Right=0. LOOP (NUMBER sem900Index=1 TILL sem900Index<=sem900Bound, sem900Index++) { IF ("+PREDICATES[0]+") { sem900Left+=1. } } LOOP (NUMBER sem900Second=1 TILL sem900Second<=sem900Bound, sem900Second++) { IF (sem900Second%3==2) { sem900Right+=1. } } DISPLAYNL(sem900Left*sem900Right)."
SOURCES["REVERSE"]=PREFIX+"NUMBER sem900Total=37. NUMBER sem900Index=sem900Bound. LOOP (sem900Index>=1) { IF ("+PREDICATES[0]+") { sem900Total+=1. } sem900Index-=1. } DISPLAYNL(sem900Total)."
SOURCES["INITIAL"]=PREFIX+"NUMBER sem900Total=-(13+8). NUMBER sem900Hit=0. "+loop("sem900Hit=0. IF ("+PREDICATES[0]+") { sem900Hit=1. } sem900Total+=sem900Hit.")
SOURCES["INITIAL_FOLDED"]=SOURCES["INITIAL"].replace("-(13+8)","-21")
SOURCES["THRESHOLD"]=PREFIX+"NUMBER sem900Total=37. "+loop("IF (sem900Index>(3*5+2)) { sem900Total+=1. }")
pair_body="sem900First=0. sem900Next=0. IF ("+PREDICATES[0]+") { sem900First=1. } IF ("+PREDICATES[1]+") { sem900Next=1. } "
pair_prefix=PREFIX+"NUMBER sem900Total=37. NUMBER sem900First=0. NUMBER sem900Next=0. "
SOURCES["FLOW_AND"]=pair_prefix+loop(pair_body+"sem900Total+=sem900First*sem900Next. IF (("+PREDICATES[0]+")&&("+PREDICATES[1]+")) { sem900Total+=1. }")
SOURCES["FLOW_OR"]=pair_prefix+loop(pair_body+"IF (sem900First+sem900Next>0) { sem900Total+=1. } IF (("+PREDICATES[0]+")||("+PREDICATES[1]+")) { sem900Total+=1. }")
SOURCES["AMBIGUOUS"]=pair_prefix+loop(pair_body+"IF (sem900Index>9) { sem900First=1. } sem900Total+=sem900First*sem900Next.")
ARRAY_PREFIX='IMPORT strings. SENTENCE sem900Raw. INPUT(sem900Raw). SENTENCE[] sem900Fields=strings.SPLIT(sem900Raw,"|"). NUMBER sem900North=strings.TO_NUMBER(sem900Fields[0]). NUMBER sem900East=strings.TO_NUMBER(sem900Fields[1]). NUMBER sem900South=strings.TO_NUMBER(sem900Fields[2]). NUMBER sem900West=strings.TO_NUMBER(sem900Fields[3]). NUMBER[] sem900Values=[sem900North,sem900East,sem900South,sem900West]. NUMBER sem900Total=37. '
SOURCES["ARRAY"]=ARRAY_PREFIX+"LOOP (NUMBER sem900Index=0 TILL sem900Index<4, sem900Index++) { "+" ".join("IF ("+p+") { sem900Total+=1. }" for p in ARRAY_PREDICATES)+" } DISPLAYNL(sem900Total)."
SOURCES["ARRAY_LE"]=SOURCES["ARRAY"].replace(ARRAY_PREDICATES[0],ARRAY_PREDICATES[0].replace("<0","<=0"))
SOURCES["ALPHA"]=SOURCES["FLOW_AND"].replace("sem900","alias903")
SOURCES["BAD_IMPORT"]="IMPORT sem900UnknownModule."
SOURCES["BAD_LOOP"]="WHILE (sem900UnknownFlag) { DISPLAYNL(73). }"
EXPRESSIONS=(*PREDICATES,*ARRAY_PREDICATES,ARRAY_PREDICATES[0].replace("<0","<=0"),"-(13+8)","-21","3*5+2","sem900First*sem900Next",
             "sem900First+sem900Next>0","("+PREDICATES[0]+")&&("+PREDICATES[1]+")",
             "("+PREDICATES[0]+")||("+PREDICATES[1]+")")
IDS=tuple("SEMCORE-900-"+name for name in SOURCES)
CASE_IDS=tuple("SEMCORE-900-CASE-"+str(n) for n in range(5))
IDENTIFIERS=(*IDS,*CASE_IDS,"SEMCORE-900-SOURCE-ARTIFACT","SEMCORE-900-CASE-ARTIFACT")


def inventory():
    return {name:[{"value":v,"sha256_utf8":hashlib.sha256(v.encode()).hexdigest(),"size_bytes_utf8":len(v.encode())} for v in values]
            for name,values in {"ids":IDENTIFIERS,"sources":tuple(SOURCES.values()),"expressions":EXPRESSIONS,"raw_inputs":(*RAW,*ARRAY_RAW,"00003")}.items()}


def overlap():
    def strings(v):
        if isinstance(v,str):yield v
        elif isinstance(v,list):
            for x in v:yield from strings(x)
        elif isinstance(v,dict):
            for k,x in v.items():yield k;yield from strings(x)
    folder=ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixtures"
    paths=sorted(folder.glob("*.json"))
    if len(paths)!=13:raise RuntimeError("historical fixture population changed")
    historical=set()
    for p in (*paths,ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"):
        historical.update(strings(json.loads(p.read_bytes())))
    new={row["value"] for rows in inventory().values() for row in rows}
    hashes={hashlib.sha256(v.encode()).hexdigest() for v in new}
    collisions=new&historical
    recorded=hashes&historical
    computed=hashes&{hashlib.sha256(v.encode()).hexdigest() for v in historical}
    if collisions or recorded or computed:raise RuntimeError("non-independent disposable inventory")
    return {"schema_version":1,"artifact_kind":"DISPOSABLE_SEMANTIC_CORE_OVERLAP","historical_fixture_files":len(paths),
            "exact_string_overlap":0,"recorded_hash_overlap":0,"computed_string_hash_overlap":0,
            "expected_labels_parsed":False,"classifiers_invoked":False,"inventory":inventory()}


def expected(name,raw):
    # Independent elementary reference formulas; no classifier/fixture labels.
    if name=="ARRAY":
        a=[int(x) for x in raw.split("|")]
        return 37+sum(int(x<0)+int(x%2==0)+int(x*x>4)+int(x>i) for i,x in enumerate(a))
    n=int(raw)
    odd=(n+1)//2;residue=(n+1)//3
    if name in {"ODD","REVERSE"}:return 37+odd
    if name=="RESIDUE":return 37+residue
    if name=="DIVISOR":return 37+sum(n%i==0 for i in range(1,n+1))
    if name=="HALF":return 37+n//2
    if name=="REPEAT":return 37+2*odd
    if name=="PREFIX":return 37+sum(i//2 for i in range(1,n+1) if i%3==2)
    if name=="TWO_PASS":return odd*residue
    if name in {"INITIAL","INITIAL_FOLDED"}:return -21+odd
    if name=="THRESHOLD":return 37+max(0,n-17)
    if name in {"FLOW_AND","ALPHA"}:return 37+2*sum(i%2==1 and i%3==2 for i in range(1,n+1))
    if name=="FLOW_OR":return 37+2*sum(i%2==1 or i%3==2 for i in range(1,n+1))
    if name=="AMBIGUOUS":return 37+sum((i%2==1 or i>9) and i%3==2 for i in range(1,n+1))
    raise ValueError("no disposable reference formula")
