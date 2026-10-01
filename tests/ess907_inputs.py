"""Fresh disposable essentiality forms; permitted overlap BEFORE execution."""
from copy import deepcopy
from pathlib import Path
import hashlib,json,re
from gbind905_inputs import DECLARATIONS as FORMS
from self_learning_ai.conf1_v3.projection_grammar import render_development,derive_projection_plan

ROOT=Path(__file__).resolve().parents[1]
START="91f8099da40b70c1453e6e2c7b315ec006fcf853"
DECLARATIONS={}
for name,d in FORMS.items():
    if d["treatment"]=="EXPRESSION":continue
    q=deepcopy(d);q.update(program_id="ESS907-"+name,offset=4597);DECLARATIONS[name]=q
SOURCES={n:render_development(d,"ess907") for n,d in DECLARATIONS.items()}
ALPHA={n:render_development(d,"alpha917") for n,d in DECLARATIONS.items()}
PLANS={n:derive_projection_plan(d) for n,d in DECLARATIONS.items()}
RAW={"numeric_iteration":("000000000000000000000017","000000000000000000000000000"),
     "array_reduction":("-114|0|127|-118","-0000|00000|000000|0000000","000000001|00000001|0000001|000001","-00114|-00116|-00118|-00120")}
BASE="numeric_iteration-ADD"
REPEAT="numeric_iteration-REPEAT"
PREFIX="numeric_iteration-0-PREFIX-FWD"
TWO="numeric_iteration-0-TWO_PASS-FWD"

def strings(v):
    if isinstance(v,str):yield v
    elif isinstance(v,list):
        for x in v:yield from strings(x)
    elif isinstance(v,dict):
        for k,x in v.items():yield k;yield from strings(x)

def overlap(inventory=None):
    sources=[*SOURCES.values(),*ALPHA.values()]
    expressions=[m[0] for s in sources for m in re.finditer(r"(?:IF|LOOP) \([^{}]*?\) \{",s)]
    expressions += [m[0] for s in sources for m in re.finditer(r"(?:ess907|alpha917)[A-Za-z0-9_]*(?:\+=|-=|=)[^{}]*?(?=\.(?![A-Za-z]))",s)]
    vals=dict(ids=[d["program_id"] for d in DECLARATIONS.values()],sources=sources,expressions=expressions,raw_inputs=[v for vs in RAW.values() for v in vs])
    inventory=inventory or {k:[dict(value=x,sha256_utf8=hashlib.sha256(x.encode()).hexdigest()) for x in rows] for k,rows in vals.items()}
    old=set();paths=list((ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixtures").glob("*.json"));assert len(paths)==13
    for p in (*paths,ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"):old.update(strings(json.loads(p.read_bytes())))
    fresh={r["value"] for rows in inventory.values() for r in rows};hashes={hashlib.sha256(x.encode()).hexdigest() for x in fresh}
    assert all(hashlib.sha256(r["value"].encode()).hexdigest()==r["sha256_utf8"] for rows in inventory.values() for r in rows)
    counts=dict(exact_string_overlap=len(fresh&old),recorded_hash_overlap=len(hashes&old),recomputed_string_hash_overlap=len(hashes&{hashlib.sha256(x.encode()).hexdigest() for x in old}))
    assert not any(counts.values()),counts
    return dict(scope="DEVELOPMENT_ONLY",expected_labels_parsed=False,fixture_files=13,inventory=inventory,**counts)

PREFLIGHT=overlap()
