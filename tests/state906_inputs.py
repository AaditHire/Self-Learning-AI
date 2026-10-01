"""Fresh state-only DEVELOPMENT sources; overlap precedes all execution."""
from copy import deepcopy
from pathlib import Path
import hashlib,json,re
from self_learning_ai.conf1_v3.projection_grammar import render_development,derive_projection_plan
from gbind905_inputs import DECLARATIONS as FORMS

ROOT=Path(__file__).resolve().parents[1]
START="5e6126f8d050ea9425b742fbcfcefe1c3d2bdf5d"
DECLARATIONS={}
for name,d in FORMS.items():
    if d["treatment"]=="EXPRESSION": continue
    q=deepcopy(d);q["program_id"]="STATE906-"+name;q["offset"]=3571;DECLARATIONS[name]=q
SOURCES={name:render_development(d,"st906") for name,d in DECLARATIONS.items()}
ALPHA={name:render_development(d,"renamed916") for name,d in DECLARATIONS.items()}
PLANS={name:derive_projection_plan(d) for name,d in DECLARATIONS.items()}
RAW={"numeric_iteration":("0000000000000000000013","00000000000000000000000"),
     "array_reduction":("-101|0|107|4","-000|0000|00000|000000")}
BASE="numeric_iteration-ADD";PREFIX="numeric_iteration-0-PREFIX-FWD";TWO="numeric_iteration-0-TWO_PASS-FWD";REV="numeric_iteration-0-PER_ITEM-REV"
BAD={}
def bad(label,name,source): BAD[label]=dict(name=name,source=source)
s=SOURCES[BASE]
bad("MISSING_INITIALIZATION",BASE,s.replace("st906total=3571.","st906total."))
bad("WRONG_INITIAL_VALUE",BASE,s.replace("=3571.","=3572."))
bad("WRONG_UPDATE_TARGET",BASE,s.replace("st906total+=","st906hitQ+=",1))
bad("RESET_INSIDE_LOOP",BASE,s.replace("st906total+=","st906total=(3571). st906total+=",1))
bad("AMBIGUOUS_REACHING_DEFINITIONS",BASE,s.replace("st906total+=","IF (st906i>5) { st906hitP=(1). } st906total+=",1))
bad("CONDITIONAL_WRITER_AMBIGUITY",BASE,s.replace("st906total+=","IF (st906n==13) { st906hitQ=(0). } st906total+=",1))
bad("STALE_WRITER",BASE,s.replace("st906hitP=(0). ","",1))
bad("UNRELATED_MUTATION",BASE,s.replace("st906total+=","st906hitQ+=(0). st906total+=",1))
bad("SAME_OUTPUT_INVALID_RECURRENCE",BASE,s.replace("st906hitP+st906hitQ","0"))
bad("CONTRIBUTION_BYPASSES_PREDICATE",BASE,s.replace("st906hitP+st906hitQ","st906i"))
bad("WRITE_AFTER_FINAL_READ",BASE,s+" st906total+=(0).")
bad("DROPPED_REQUIRED_UPDATE",BASE,s.replace("st906total+=(st906hitP+st906hitQ).",""))
s=SOURCES[PREFIX]
q="IF (st906hitQ==1) { st906total+=(st906seen). }";p="IF (st906hitP==1) { st906seen+=(1). }"
bad("PREFIX_PRE_POST_SWAP",PREFIX,s.replace(q+" "+p,p+" "+q))
bad("LATER_WRITE_CONTAMINATION",PREFIX,s.replace(q,"st906seen+=(1). "+q))
bad("WRONG_LOOP_READ",PREFIX,s.replace("st906total+=(st906seen)","st906total+=(st906hitP)"))
bad("PREFIX_WRONG_RESET_SCOPE",PREFIX,s.replace(q,"st906seen=(0). "+q))
bad("PREFIX_WRONG_INITIALIZATION",PREFIX,s.replace("st906seen=0.","st906seen=1."))
s=SOURCES[TWO]
first=s.index("LOOP (");second=s.index("LOOP (",first+1);end=s.index("st906total+=(st906left*st906right)")
bad("WRONG_PASS_ORDER",TWO,s[:first]+s[second:end]+s[first:second]+s[end:])
bad("OVERWRITTEN_FIRST_PASS",TWO,s[:second]+"st906left=(0). "+s[second:])
bad("RECOMPUTED_FIRST_PASS",TWO,s.replace("st906right+=(st906hitQ)","st906left+=(st906hitP). st906right+=(st906hitQ)"))
bad("WRONG_FINAL_COMBINATION",TWO,s.replace("st906left*st906right","st906left*st906left"))
bad("CROSS_LOOP_STATE",TWO,s.replace("st906right+=(st906hitQ)","st906right+=(st906left)"))
bad("UNRELATED_FINAL_STATE",TWO,s.replace("st906left*st906right","st906hitP*st906hitQ"))
s=SOURCES[REV]
bad("INCORRECT_REVERSE_DECREMENT",REV,s.replace("st906i-=1.","st906i-=2."))
bad("INCORRECT_REVERSE_BOUND",REV,s.replace("st906i>=1","st906i>=0"))
bad("MISSING_REVERSE_STEP",REV,s.replace("st906i-=1.",""))
bad("MUTATED_SOURCE_BOUND",BASE,SOURCES[BASE].replace("LOOP (","st906n+=(1). LOOP (",1))


def strings(v):
    if isinstance(v,str): yield v
    elif isinstance(v,list):
        for x in v: yield from strings(x)
    elif isinstance(v,dict):
        for k,x in v.items(): yield k; yield from strings(x)


def overlap():
    sources=[*SOURCES.values(),*ALPHA.values(),*[x["source"] for x in BAD.values()]]
    # Binding-bearing whole expressions, not shared normative constant tokens.
    expressions=[m[1] for s in sources for m in re.finditer(r"(?:IF|LOOP) \(([^{}]*?)\) \{",s)]
    expressions += [m[0] for s in sources for m in re.finditer(r"(?:st906|renamed916)[A-Za-z0-9_]*(?:\+=|-=|=)[^{}]*?(?=\.(?![A-Za-z]))",s)]
    vals=dict(ids=[d["program_id"] for d in DECLARATIONS.values()],sources=sources,expressions=expressions,raw_inputs=[v for values in RAW.values() for v in values])
    inventory={k:[dict(value=x,sha256_utf8=hashlib.sha256(x.encode()).hexdigest()) for x in rows] for k,rows in vals.items()}
    old=set();paths=sorted((ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixtures").glob("*.json"))
    assert len(paths)==13
    for path in (*paths,ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"): old.update(strings(json.loads(path.read_bytes())))
    fresh={x for rows in vals.values() for x in rows};hashes={hashlib.sha256(x.encode()).hexdigest() for x in fresh}
    counts=dict(exact_string_overlap=len(fresh&old),recorded_hash_overlap=len(hashes&old),recomputed_string_hash_overlap=len(hashes&{hashlib.sha256(x.encode()).hexdigest() for x in old}))
    assert not any(counts.values()),counts
    return dict(scope="DEVELOPMENT_ONLY",expected_labels_parsed=False,fixture_files=13,inventory=inventory,**counts)

PREFLIGHT=overlap()
