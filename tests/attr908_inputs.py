"""Disposable sources: reference expectations and overlap precede execution."""
from copy import deepcopy
from pathlib import Path
import re
from gbind905_inputs import declaration
from self_learning_ai.conf1_v3.projection_grammar import render_development,derive_projection_plan
from self_learning_ai.conf1_v3.attribute_reference import output_plan,digest_text
from self_learning_ai.conf1_v3.attribute_overlap import compare,permitted_corpus

ROOT=Path(__file__).resolve().parents[1]
START="dfad902a7e1fb595b062723ce8fd6f3380050c59"
DECLARATIONS={};SOURCES={};RAW={};OPERATIONS={}
def add(name,family="numeric_iteration",offset=6571,inputs=None,operations=None,**kwargs):
    d=declaration(name,family,**kwargs);d.update(program_id="ATTR908-"+name,offset=offset)
    DECLARATIONS[name]=d;SOURCES[name]=render_development(d,"attr908"+name)
    RAW[name]=inputs or (["00000000000000000000019","000000000000000000000002"] if family=="numeric_iteration" else ["-0317|0000000|0341|-0331","-00316|-00318|-00320|-00322"])
    OPERATIONS[name]=operations or ["OUTPUT_POSITIVE","OUTPUT_MULTIDIGIT"]

add("N",treatment="ADD",operations=["OUTPUT_POSITIVE","OUTPUT_MULTIDIGIT","OUTPUT_EXACT_SENTINEL:6573"])
add("A",family="array_reduction",offset=7411,treatment="ADD")
add("Nother",pair=1,offset=7681,treatment="ADD")
add("Aother",family="array_reduction",pair=1,offset=7751,treatment="ADD")
add("Const",offset=8039,treatment="EXPRESSION",expression="i*-(13+8)",inputs=["000000000000000000000003"])
add("Ops",offset=8291,treatment="EXPRESSION",expression="i+(13-8)*2",inputs=["0000000000000000000000003"])
add("Lex",offset=8317,treatment="EXPRESSION",expression="i*00013",inputs=["00000000000000000000000003"])
add("Zero",treatment="EXPRESSION",expression="i-(6571+1)",inputs=["00000000000000000000001","000000000000000000000000003"],
    operations=["OUTPUT_ZERO","OUTPUT_NEGATIVE","OUTPUT_MULTIDIGIT","OUTPUT_EXACT_SENTINEL:0","OUTPUT_EXACT_SENTINEL:-13139"])
add("Inactive",family="array_reduction",offset=8513,treatment="OR",inputs=["-00316|-00318|-00320|-00322","0000317|0000319|0000321|0000323"])
add("Two",offset=8627,structure="TWO_PASS")
add("Reverse",offset=8741,structure="PREFIX",reverse=True)
add("Unused",offset=8917,unused=True,treatment="ADD")
for base in ("N","A"):
    name=base+"alpha";DECLARATIONS[name]=deepcopy(DECLARATIONS[base]);DECLARATIONS[name]["program_id"]="ATTR908-"+name
    SOURCES[name]=render_development(DECLARATIONS[name],"alpha918"+name);RAW[name]=RAW[base];OPERATIONS[name]=OPERATIONS[base]
DECLARATIONS["ConstFold"]=deepcopy(DECLARATIONS["Const"]);DECLARATIONS["ConstFold"]["program_id"]="ATTR908-ConstFold"
SOURCES["ConstFold"]=render_development(DECLARATIONS["ConstFold"],"attr908ConstFold").replace("-(13+8)","-21")
RAW["ConstFold"]=RAW["Const"];OPERATIONS["ConstFold"]=OPERATIONS["Const"]
REFERENCE_SOURCES={n:(render_development(q,"attr908ConstFold") if n=="ConstFold" else SOURCES[n]) for n,q in DECLARATIONS.items()}
PLANS={n:derive_projection_plan(d) for n,d in DECLARATIONS.items()}
PROSPECTIVE=[dict(declaration=d,source=SOURCES[n],reference_source=REFERENCE_SOURCES[n],raw_inputs=RAW[n],operations=OPERATIONS[n],
                  output_plan=output_plan(d,OPERATIONS[n],RAW[n],digest_text(SOURCES[n]))) for n,d in DECLARATIONS.items()]
OUTPUTS={n:p["output_plan"] for n,p in zip(DECLARATIONS,PROSPECTIVE)}
LITERALS={n:([dict(grammar_path="/s5/body/s4/e1/a1",exact_lexeme="00013")] if n=="Lex" else []) for n in DECLARATIONS}
LITERALS["N"]=[dict(grammar_path="/s2/e0",exact_lexeme="6571")]
BAD_SOURCES={"UNSUPPORTED_CONSTANT":SOURCES["Const"].replace("-(13+8)","(13%8)"),
             "EXTRA_DISPLAY":SOURCES["N"].replace("DISPLAYNL(","DISPLAYNL(attr908Ntotal). DISPLAYNL("),
             "NORMALIZED_EXACT_LITERAL":SOURCES["Lex"].replace("00013","13")}
BAD_SOURCES["GROUPED_EXACT_LITERAL"]=SOURCES["Lex"].replace("00013","(00013)")
REASSOC=deepcopy(DECLARATIONS["Ops"]);REASSOC.update(program_id="ATTR908-Reassociation",expression="(i+13)+8")
REASSOC_SOURCE=render_development(REASSOC,"attr908Reassoc")
BAD_SOURCES["REASSOCIATION"]=REASSOC_SOURCE.replace("(attr908Reassoci+13)+8","attr908Reassoci+(13+8)")

def inventory():
    sources=[*SOURCES.values(),*REFERENCE_SOURCES.values(),*BAD_SOURCES.values(),REASSOC_SOURCE];expressions=[m[0] for s in sources for m in re.finditer(r"(?:IF|LOOP) \([^{}]*?\) \{|(?:attr908|alpha918)[A-Za-z0-9_]*(?:\+=|-=|=)[^{}]*?(?=\.(?![A-Za-z]))",s)]
    vals=dict(program_ids=[*[d["program_id"] for d in DECLARATIONS.values()],REASSOC["program_id"]],case_ids=[r["case_id"] for p in OUTPUTS.values() for r in p["expected_records"]],
              sources=sources,expressions=expressions,raw_inputs=[r for rows in RAW.values() for r in rows],
              bindings=sorted({m[0] for s in sources for m in re.finditer(r"(?:attr908|alpha918)[A-Za-z0-9_]+",s)}),
              prospectively_required_lexemes=[r["exact_lexeme"] for rs in LITERALS.values() for r in rs])
    rows={k:[dict(value=v,sha256_utf8=digest_text(v)) for v in vs] for k,vs in vals.items()}
    rows["expected_outputs"]=[]
    for p in OUTPUTS.values():
        z=next((q["requirement_id"] for q in p["requirements"] if q["operation"]=="OUTPUT_ZERO"),None)
        for r in p["expected_records"]:
            rows["expected_outputs"].append(dict(value=r["expected_output"],sha256_utf8=digest_text(r["expected_output"]),program_id=r["program_id"],case_id=r["case_id"],requirement_id=z if r["expected_output"]=="0" else None))
    return rows

PREFLIGHT=compare(inventory(),PROSPECTIVE,permitted_corpus(ROOT))
