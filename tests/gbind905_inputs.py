"""Fresh disposable grammar declarations and pre-parsing overlap inventory."""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import re
from self_learning_ai.conf1_v3.projection_grammar import render_development

ROOT=Path(__file__).resolve().parents[1]
START="654c1745ae4148a9d8a4200c818ffc288fb8bb36"
RAW={"numeric_iteration":"0000000000000000000083","array_reduction":"-83|0|89|4"}
PAIRS={"numeric_iteration":(("odd_index","residue_two"),("divisor_index","first_half")),
       "array_reduction":(("negative_value","even_value"),("large_magnitude","value_exceeds_index"))}


def declaration(name,family="numeric_iteration",pair=0,structure="PER_ITEM",reverse=False,treatment="PRODUCT",repeat=1,expression=None,unused=False):
    p,q=PAIRS[family][pair]
    return dict(program_id="GBIND905-"+name,family=family,role_bindings=dict(P=p,Q=q),structure=structure,
                treatment=treatment,reverse=reverse,offset=1297,repeat=repeat,expression=expression,unused=unused)


DECLARATIONS={}
for family in PAIRS:
    for pair in range(2):
        for structure in ("PER_ITEM","PREFIX","TWO_PASS"):
            for reverse in (False,True):
                name=family+"-"+str(pair)+"-"+structure+("-REV" if reverse else "-FWD")
                DECLARATIONS[name]=declaration(name,family,pair,structure,reverse)
for family in PAIRS:
    for treatment in ("ADD","PAIR_AND","OR","SUM_POSITIVE"):
        name=family+"-"+treatment
        DECLARATIONS[name]=declaration(name,family,treatment=treatment)
    name=family+"-REPEAT"
    DECLARATIONS[name]=declaration(name,family,repeat=2)
    name=family+"-SHARED"
    DECLARATIONS[name]=declaration(name,family)
    DECLARATIONS[name]["role_bindings"]["Q"]=DECLARATIONS[name]["role_bindings"]["P"]
for name,expr in (("ADD_SORT","n+i"),("MUL_SORT","n*i"),("AND_SORT","(n%3==2)&&(i%2==1)"),
                  ("OR_SORT","(n%3==2)||(i%2==1)"),("GT","n>i"),("GE","n>=i"),("EQ","n==i"),
                  ("DUPLICATES","(n+i)*(n+i)"),("ASSOCIATION","(n+i)+7")):
    # The contribution is a number; Boolean forms use a unit IF, below.
    DECLARATIONS[name]=declaration(name,treatment="EXPRESSION",expression=expr)
DECLARATIONS["LINKED_BOOLEAN"]=declaration("LINKED_BOOLEAN",treatment="EXPRESSION",expression="((i%2==1)&&(n%i==0))||((i%3==2)&&(2*i<=n))")
DECLARATIONS["UNUSED"]=declaration("UNUSED",unused=True)
SOURCES={n:render_development(d,"gbind905") for n,d in DECLARATIONS.items()}
VARIANTS={}
for n,s in SOURCES.items():
    VARIANTS[n+"-ALPHA"]=s.replace("gbind905","bound915")
VARIANTS["FOLDED"]=SOURCES["numeric_iteration-ADD"].replace("=1297.","=(-(-1200)+10*10-3).")
VARIANTS["ADD_SWAP"]=SOURCES["ADD_SORT"].replace("gbind905n+gbind905i","gbind905i+gbind905n")
VARIANTS["MUL_SWAP"]=SOURCES["MUL_SORT"].replace("gbind905n*gbind905i","gbind905i*gbind905n")
VARIANTS["AND_SWAP"]=SOURCES["AND_SORT"].replace("(gbind905n%3==2)&&(gbind905i%2==1)","(gbind905i%2==1)&&(gbind905n%3==2)")
VARIANTS["OR_SWAP"]=SOURCES["OR_SORT"].replace("(gbind905n%3==2)||(gbind905i%2==1)","(gbind905i%2==1)||(gbind905n%3==2)")
for n,old,new in (("GT","gbind905n>gbind905i","gbind905i<gbind905n"),
                  ("GE","gbind905n>=gbind905i","gbind905i<=gbind905n"),("EQ","gbind905n==gbind905i","gbind905i==gbind905n"),
                  ("DUPLICATES","gbind905n+gbind905i","gbind905i+gbind905n")):
    VARIANTS[n+"_REVERSED"]=SOURCES[n].replace(old,new)
BAD={
    "STALE":SOURCES["numeric_iteration-ADD"].replace("gbind905hitP=(0). ","",1),
    "WRONG_ROLE":SOURCES["numeric_iteration-ADD"].replace("gbind905hitP=(1)","gbind905hitQ=(1)"),
    "AMBIGUOUS":SOURCES["numeric_iteration-ADD"].replace("gbind905total+=(gbind905hitP+gbind905hitQ)","IF (gbind905i>17) { gbind905hitP=(1). } gbind905total+=(gbind905hitP+gbind905hitQ)"),
    "EXTRA_LIVE":SOURCES["numeric_iteration-ADD"].replace("DISPLAYNL", "gbind905total+=(11). DISPLAYNL"),
    "REASSOCIATION":SOURCES["ASSOCIATION"].replace("(gbind905n+gbind905i)+7","gbind905n+(gbind905i+7)"),
    "ARBITRARY_ALGEBRA":SOURCES["MUL_SORT"].replace("gbind905n*gbind905i","gbind905n+gbind905i"),
    "DROPPED_DUPLICATE":SOURCES["DUPLICATES"].replace("(gbind905n+gbind905i)*(gbind905n+gbind905i)","gbind905n+gbind905i"),
    "LITERAL_REWRITE":SOURCES["array_reduction-ADD"].replace('"|"','";"'),
    "INCOMPLETE_ALPHA":SOURCES["numeric_iteration-ADD"].replace("INPUT(gbind905n)","INPUT(bound915n)"),
    "UNSUPPORTED_BOOLEAN_ARITHMETIC":SOURCES["numeric_iteration-PAIR_AND"].replace("&&","*"),
    "BAD_FOLD":SOURCES["numeric_iteration-ADD"].replace("=1297.","=((1297%1000)+1000)."),
    "WRONG_DIRECTION":SOURCES["numeric_iteration-0-PER_ITEM-REV"],
    "WRONG_LOOP":SOURCES["numeric_iteration-0-TWO_PASS-FWD"].replace("gbind905hitP=(0). ","",1),
}


def inventory():
    source_rows=[*SOURCES.values(),*VARIANTS.values(),*BAD.values()]
    # Only disposable expressions, not the shared normative predicate catalog.
    expressions=[m[0] for s in source_rows for m in re.finditer(r"(?:IF|LOOP) \([^{}]*?\) \{",s)]
    values=dict(ids=[d["program_id"] for d in DECLARATIONS.values()],sources=source_rows,
                expressions=expressions,raw_inputs=list(RAW.values()))
    return {k:[dict(value=v,sha256_utf8=hashlib.sha256(v.encode()).hexdigest()) for v in vs] for k,vs in values.items()}


def overlap():
    # Pure string/hash overlap only. Never open the protected expected-label file.
    def strings(v):
        if isinstance(v,str): yield v
        elif isinstance(v,list):
            for x in v: yield from strings(x)
        elif isinstance(v,dict):
            for k,x in v.items(): yield k; yield from strings(x)
    files=sorted((ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixtures").glob("*.json"))
    if len(files)!=13: raise RuntimeError("protected fixture corpus changed")
    old=set()
    for p in (*files,ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"):
        old.update(strings(json.loads(p.read_bytes())))
    new={r["value"] for vs in inventory().values() for r in vs}; hashes={hashlib.sha256(v.encode()).hexdigest() for v in new}
    counts=dict(exact_string_overlap=len(new&old),recorded_hash_overlap=len(hashes&old),recomputed_string_hash_overlap=len(hashes&{hashlib.sha256(v.encode()).hexdigest() for v in old}))
    if any(counts.values()): raise RuntimeError("disposable overlap")
    return dict(scope="DEVELOPMENT_ONLY",expected_labels_parsed=False,fixture_files=13,inventory=inventory(),**counts)
