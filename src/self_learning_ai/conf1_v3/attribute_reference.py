"""Independent DEVELOPMENT declaration oracle. No IR execution or corpus read.

Shared expression parser, separate declaration-level recurrence evaluator.
Neither expected labels nor overlap metadata are inputs to this function.
"""
from .requirements import expression, frozen_metadata, digest
from .projection_grammar import validate_declaration, require, development_identity
from .contract_ir import output_requirement

AUTHORITY="research/protocols/phase3c_conf1_coverage_v3_proposed.md#v35-semantic-activity--closed-two-level-evidence-rule"


def integer_text(text):
    require(isinstance(text,str),"OUTPUT_NONCANONICAL_INTEGER")
    try: value=int(text)
    except ValueError as exc: raise ValueError("OUTPUT_NONCANONICAL_INTEGER") from exc
    require(str(value)==text,"OUTPUT_NONCANONICAL_INTEGER")
    return value


def ev(e,env):
    if e.kind=="GROUP":return ev(e.children[0],env)
    if e.kind=="NUMBER":return int(e.value)
    if e.kind=="ID":return env[e.value]
    if e.kind=="INDEX":return ev(e.children[0],env)[ev(e.children[1],env)]
    if e.kind=="UNARY":
        v=ev(e.children[0],env);return -v if e.value=="-" else not v
    require(e.kind=="BINARY","REFERENCE_UNSUPPORTED_EXPRESSION")
    a,b=(ev(c,env) for c in e.children)
    operations={"+":lambda:a+b,"-":lambda:a-b,"*":lambda:a*b,"%":lambda:a-abs(a)//abs(b)*(1 if a*b>=0 else -1)*b,
                "==":lambda:a==b,"!=":lambda:a!=b,"<":lambda:a<b,"<=":lambda:a<=b,">":lambda:a>b,">=":lambda:a>=b,
                "&&":lambda:bool(a and b),"||":lambda:bool(a or b)}
    require(e.value in operations,"REFERENCE_UNSUPPORTED_EXPRESSION")
    return operations[e.value]()


def reference_output(d,raw):
    validate_declaration(d);development_identity(raw)
    array=d["family"]=="array_reduction"
    values=[int(x) for x in raw.split("|")] if array else None
    require(len(values)==4 if array else int(raw)>=0,"REFERENCE_INPUT_DOMAIN")
    n=4 if array else int(raw);items=list(range(4)) if array else list(range(1,n+1))
    if d["reverse"]:items.reverse()
    predicates={p["name"]:expression(p["expression"]) for p in frozen_metadata()["predicate_definitions"][d["family"]]}
    hits=[];total=d["offset"];seen=0
    for i in items:
        env=dict(i=i,n=n,values=values)
        p,q=[int(ev(predicates[d["role_bindings"][r]],env)) for r in ("P","Q")]
        hits.append((p,q))
        if d["structure"]=="PREFIX":total+=seen*q;seen+=p
        elif d["structure"]=="PER_ITEM":
            t=d["treatment"]
            v=p+q if t=="ADD" else p*q if t in {"PRODUCT","PAIR_AND"} else int(bool(p or q)) if t in {"OR","SUM_POSITIVE"} else ev(expression(d["expression"]),{**env,"hitP":p,"hitQ":q})
            total+=int(v)*d["repeat"]
    if d["structure"]=="TWO_PASS":total+=sum(p for p,q in hits)*sum(q for p,q in hits)
    return total


def output_plan(d,operations,raw_inputs,source_sha256):
    # Called before any corpus comparison or compiler execution.
    validate_declaration(d);require(len(operations)==len(set(operations)),"OUTPUT_DUPLICATE_REQUIREMENT")
    requirements=[dict(requirement_id=digest(["DEVELOPMENT_OUTPUT_REQUIREMENT",d["program_id"],op]),
                       evidence_kind="OUTPUT_ATTRIBUTE",operation=op,**output_requirement(op)) for op in operations]
    cases=[]
    for i,raw in enumerate(raw_inputs):
        value=reference_output(d,raw);case_id=d["program_id"]+"-CASE-"+str(i)
        body=dict(scope="DEVELOPMENT_ONLY",program_id=d["program_id"],source_sha256=source_sha256,case_id=case_id,
                  raw_input=raw,raw_input_sha256=digest_text(raw),expected_integer=value,expected_output=str(value),
                  oracle="DEVELOPMENT_DECLARATIVE_REFERENCE_V1")
        cases.append(dict(record_id=digest(body),**body))
    return dict(scope="DEVELOPMENT_ONLY",requirements=requirements,expected_records=cases,
                causal_order=["PROSPECTIVE_FROZEN_OUTPUT_REQUIREMENT","DECLARATION_ORACLE_INTEGER","CANONICAL_EXPECTED_TEXT","OVERLAP_COMPARISON","COMPILER_EXECUTION"],
                source_sha256=source_sha256,program_id=d["program_id"])


def digest_text(text):
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def matches(operation,text):
    value=integer_text(text);r=output_requirement(operation)
    if r["output_requirement_kind"]=="EXACT_SENTINEL":return text==r["exact_sentinel"]
    return {"OUTPUT_ZERO":value==0,"OUTPUT_POSITIVE":value>0,"OUTPUT_NEGATIVE":value<0,"OUTPUT_MULTIDIGIT":abs(value)>=10}[operation]
