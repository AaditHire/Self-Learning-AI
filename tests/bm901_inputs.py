"""New classifier-free Boolean mapping inventory and overlap guard."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
START="c13996834f3895c013b460f43cf2a0303c892360"
RAW=("0000000","0000005","0000009","0000013","0000023")
ARRAY_RAW=("-83|0|89|2","-97|6|0|101","8|-103|0|107","0|0|-109|113","-127|10|13|0")
P="bm901Item%2==1"
Q="bm901Item%3==2"
HEADER="NUMBER bm901Limit. INPUT(bm901Limit). NUMBER bm901Total=79. NUMBER bm901P=0. NUMBER bm901Q=0. "
BODY="bm901P=0. bm901Q=0. IF ("+P+") { bm901P=1. } IF ("+Q+") { bm901Q=1. } "
def source(body):
    return HEADER+"LOOP (NUMBER bm901Item=1 TILL bm901Item<=bm901Limit, bm901Item++) { "+body+" } DISPLAYNL(bm901Total)."
AND_BOOL="IF (("+P+")&&("+Q+")) { bm901Total+=1. }"
OR_BOOL="IF (("+P+")||("+Q+")) { bm901Total+=1. }"
SOURCES={
    "AND":source(BODY+AND_BOOL),
    "PRODUCT":source(BODY+"bm901Total+=bm901P*bm901Q."),
    "OR":source(BODY+OR_BOOL),
    "SUM_POSITIVE":source(BODY+"IF (bm901P+bm901Q>0) { bm901Total+=1. }"),
    "REPEATED":source(BODY+AND_BOOL+AND_BOOL),
    "OMITTED":source(BODY+"IF ("+P+") { bm901Total+=1. }"),
    "EXTRA_TERM":source(BODY+"IF (("+P+")||("+Q+")||(bm901Item>77)) { bm901Total+=1. }"),
    "COMPOUND":source(BODY+"IF (("+P+")&&(("+Q+")||("+P+"))) { bm901Total+=1. }"),
    "AMBIGUOUS":source(BODY+"IF (bm901Item>77) { bm901P=1. } bm901Total+=bm901P*bm901Q."),
    "CONDITIONAL_RESET":source(BODY.replace("bm901P=0.","IF (bm901Item>77) { bm901P=0. }")+"bm901Total+=bm901P*bm901Q."),
    "READ_BEFORE_WRITE":source("bm901Total+=bm901P*bm901Q. "+BODY),
    "STATE_ORDER":source(BODY+"bm901Total+=bm901P*bm901Q. bm901Total=79."),
    "WRONG_TYPE":source(BODY+"bm901Total+=("+P+")*bm901Q."),
    "MATCHING_OUTPUT_INVALID":source(BODY+"IF (("+P+")&&("+Q+")) { bm901Total+=1. } IF (bm901Item>77) { bm901Total+=1. }"),
    "SOURCE_ONLY":source(BODY+AND_BOOL+"NUMBER bm901Extra=bm901Item+83."),
    "UNLISTED":source(BODY+"IF (!("+P+")&&("+Q+")) { bm901Total+=1. }"),
    "CIRCULAR":source("bm901P=0. bm901Q=0. IF (bm901P==1) { bm901P=1. } IF ("+Q+") { bm901Q=1. } bm901Total+=bm901P*bm901Q."),
    "CROSS_LOOP":HEADER+"LOOP (NUMBER bm901Item=1 TILL bm901Item<=bm901Limit, bm901Item++) { "+BODY+AND_BOOL+" } LOOP (NUMBER bm901Later=1 TILL bm901Later<=bm901Limit, bm901Later++) { bm901Total+=bm901P*bm901Q. } DISPLAYNL(bm901Total).",
}
SOURCES["ALPHA"]=SOURCES["AND"].replace("bm901","bmap904")
SOURCES["ALPHA_OR"]=SOURCES["OR"].replace("bm901","bmap904")
SOURCES["ALPHA_PRODUCT"]=SOURCES["PRODUCT"].replace("bm901","bmap904")
SOURCES["ALPHA_SUM_POSITIVE"]=SOURCES["SUM_POSITIVE"].replace("bm901","bmap904")
SOURCES["ALPHA_REPEATED"]=SOURCES["REPEATED"].replace("bm901","bmap904")
for name,p in zip(("ODD","RESIDUE","DIVISOR","HALF"),(P,Q,"bm901Limit%bm901Item==0","2*bm901Item<=bm901Limit")):
    SOURCES[name]=source(BODY+"IF ("+p+") { bm901Total+=1. }")
ARRAY_PREDICATES=("bm901Values[bm901Item]<0","bm901Values[bm901Item]%2==0","bm901Values[bm901Item]*bm901Values[bm901Item]>4","bm901Values[bm901Item]>bm901Item")
SOURCES["ARRAY"]='IMPORT strings. SENTENCE bm901Raw. INPUT(bm901Raw). SENTENCE[] bm901Fields=strings.SPLIT(bm901Raw,"|"). NUMBER bm901A=strings.TO_NUMBER(bm901Fields[0]). NUMBER bm901B=strings.TO_NUMBER(bm901Fields[1]). NUMBER bm901C=strings.TO_NUMBER(bm901Fields[2]). NUMBER bm901D=strings.TO_NUMBER(bm901Fields[3]). NUMBER[] bm901Values=[bm901A,bm901B,bm901C,bm901D]. NUMBER bm901Total=79. LOOP (NUMBER bm901Item=0 TILL bm901Item<4, bm901Item++) { '+" ".join("IF ("+p+") { bm901Total+=1. }" for p in ARRAY_PREDICATES)+' } DISPLAYNL(bm901Total).'
EXPRESSIONS=(P,Q,"bm901Limit%bm901Item==0","2*bm901Item<=bm901Limit",*ARRAY_PREDICATES,
    "("+P+")&&("+Q+")","("+P+")||("+Q+")","bm901P*bm901Q","bm901P+bm901Q>0",
    "bm901Item>77","bm901Item+83","bm901P==1","!("+P+")&&("+Q+")",
    "("+P+")&&(("+Q+")||("+P+"))","("+P+")||("+Q+")||(bm901Item>77)","("+P+")*bm901Q")
CASE_IDS=tuple("BMAP901-CASE-"+str(i) for i in range(5))
IDS=(*("BMAP901-"+n for n in SOURCES),*CASE_IDS,"BMAP901-SOURCE-ARTIFACT","BMAP901-CASE-ARTIFACT")

def inventory():
    return {k:[{"value":v,"sha256_utf8":hashlib.sha256(v.encode()).hexdigest()} for v in values]
        for k,values in {"ids":IDS,"sources":tuple(SOURCES.values()),"expressions":EXPRESSIONS,"raw_inputs":(*RAW,*ARRAY_RAW)}.items()}

def overlap():
    def strings(v):
        if isinstance(v,str):yield v
        elif isinstance(v,list):
            for x in v:yield from strings(x)
        elif isinstance(v,dict):
            for k,x in v.items():yield k;yield from strings(x)
    paths=sorted((ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixtures").glob("*.json"))
    if len(paths)!=13:raise RuntimeError("historical fixture population changed")
    historical=set()
    for path in (*paths,ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"):
        historical.update(strings(json.loads(path.read_bytes())))
    new={r["value"] for rows in inventory().values() for r in rows}
    hashes={hashlib.sha256(v.encode()).hexdigest() for v in new}
    counts={"exact_string_overlap":len(new&historical),"recorded_hash_overlap":len(hashes&historical),
        "recomputed_string_hash_overlap":len(hashes&{hashlib.sha256(v.encode()).hexdigest() for v in historical})}
    if any(counts.values()):raise RuntimeError("disposable overlap")
    return {"schema_version":1,"starting_head":START,"historical_fixture_files":13,"expected_labels_parsed":False,
        **counts,"inventory":inventory()}

if __name__=="__main__":
    print(json.dumps({k:v for k,v in overlap().items() if k!="inventory"},indent=2))
