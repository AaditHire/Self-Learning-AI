"""Build fresh DEV2 A-only design data; no model or consumed-suite execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_phase2b_data import ast_proxy, case, split_numbers

ROOT = Path(__file__).resolve().parents[1]
PREDICATES = {
    "numeric_iteration": {
        "odd_index": ("i%2==1", lambda i, n, xs: i % 2 == 1, "odd index"),
        "residue_two": ("i%3==2", lambda i, n, xs: i % 3 == 2, "index with remainder two modulo three"),
        "divisor_index": ("n%i==0", lambda i, n, xs: n % i == 0, "positive divisor of n"),
        "first_half": ("2*i<=n", lambda i, n, xs: 2*i <= n, "index in the first half through n"),
    },
    "array_reduction": {
        "negative_value": ("values[i]<0", lambda i, n, xs: xs[i] < 0, "negative entry"),
        "even_value": ("values[i]%2==0", lambda i, n, xs: xs[i] % 2 == 0, "even-valued entry"),
        "large_magnitude": ("values[i]*values[i]>4", lambda i, n, xs: xs[i]*xs[i] > 4, "entry whose square exceeds four"),
        "value_exceeds_index": ("values[i]>i", lambda i, n, xs: xs[i] > i, "entry greater than its zero-based position"),
    },
}
PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
NUMERIC_CASES = (0, 1, 5, 10, 18)
ARRAY_CASES = ((0, 0, 0, 0), (-4, -1, 2, 7), (3, -6, 0, 5), (1, 2, -3, -8), (-5, 4, -2, 0))
EVAL_ARRAY_CASES = ((1, 1, 1, 1), (-4, -6, -8, -10), (3, 3, 3, 3),
                    (-1, 2, -3, 4), (5, -5, 1, -1))
ARRAY_PREFIX = split_numbers(["a", "b", "c", "d"]) + "NUMBER[] values=[a,b,c,d].\n"


def names(family):
    return list(PREDICATES[family])


def describe(family, key):
    return PREDICATES[family][key][2]


def expression(family, key):
    return PREDICATES[family][key][0]


def predicate(family, key, i, n, xs):
    return PREDICATES[family][key][1](i, n, xs)


def loop(family, reverse, body, index="i"):
    if family == "numeric_iteration":
        if reverse:
            return f"NUMBER {index}=n.\nLOOP ({index}>=1) {{ {body} {index}-=1. }}\n"
        return f"LOOP (NUMBER {index}=1 TILL {index}<=n, {index}++) {{ {body} }}\n"
    if reverse:
        return f"NUMBER {index}=3.\nLOOP ({index}>=0) {{ {body} {index}-=1. }}\n"
    return f"LOOP (NUMBER {index}=0 TILL {index}<4, {index}++) {{ {body} }}\n"


def prefix(family):
    return "NUMBER n.\nINPUT(n).\n" if family == "numeric_iteration" else ARRAY_PREFIX


def examples(family, evaluation=False):
    if family == "numeric_iteration":
        return [(str(n), n, None) for n in NUMERIC_CASES]
    return [("|".join(map(str, xs)), 0, xs) for xs in (EVAL_ARRAY_CASES if evaluation else ARRAY_CASES)]


def indices(family, n):
    return range(1, n+1) if family == "numeric_iteration" else range(4)


def train_program(condition, family, p, q, k, reverse):
    P, Q = expression(family, p), expression(family, q)
    if condition == "isolated":
        body = f"IF ({P}) {{ IF ({P}) {{ left+=1. }} }} IF ({Q}) {{ right+=1. }}"
        signature = f"count({p})+count({q}); redundant inner {p} guard"
        prompt = (f"Read {'nonnegative n' if family=='numeric_iteration' else 'four pipe-separated numbers'}. "
                  f"Separately count {describe(family,p)} and {describe(family,q)}; add the two counts and {k}.")
    else:
        body = f"IF ({P}) {{ IF ({Q}) {{ left+=1. }} }} IF ({P}) {{ right+=1. }}"
        signature = f"count({p} AND {q})+count({p})"
        prompt = (f"Read {'nonnegative n' if family=='numeric_iteration' else 'four pipe-separated numbers'}. "
                  f"Count items satisfying both {describe(family,p)} and {describe(family,q)}; also count {describe(family,p)}. Add both counts and {k}.")
    source = prefix(family)+f"NUMBER left={k}.\nNUMBER right=0.\n"+loop(family,reverse,body)+"DISPLAYNL(left+right)."
    samples = []
    for stdin,n,xs in examples(family):
        pv = sum(predicate(family,p,i,n,xs) for i in indices(family,n))
        qv = sum(predicate(family,q,i,n,xs) for i in indices(family,n))
        joint = sum(predicate(family,p,i,n,xs) and predicate(family,q,i,n,xs) for i in indices(family,n))
        samples.append((stdin, k+(pv+qv if condition=="isolated" else joint+pv)))
    return prompt,source,samples,[p,q],signature


def eval_program(group, family, variant, k):
    keys = names(family)
    if group == "primitive_sanity":
        p=keys[variant]; P=expression(family,p)
        prompt=f"Read {'nonnegative n' if family=='numeric_iteration' else 'four pipe-separated numbers'}. Count {describe(family,p)} and then add {k}."
        source=prefix(family)+f"NUMBER count={k}.\n"+loop(family,False,f"IF ({P}) {{ count+=1. }}")+"DISPLAYNL(count)."
        op=[p]; signature=f"count({p})"
        fn=lambda i,n,xs: int(predicate(family,p,i,n,xs))
    elif group == "novel_composition":
        pairings = ((0,1,2,3),(0,2,1,3))
        a,b,c,d=[keys[j] for j in pairings[variant]]
        A,B,C,D=[expression(family,x) for x in (a,b,c,d)]
        prompt=(f"Read {'nonnegative n' if family=='numeric_iteration' else 'four pipe-separated numbers'}. "
                f"Count items satisfying both {describe(family,a)} and {describe(family,b)}; also count items satisfying both {describe(family,c)} and {describe(family,d)}. Add {k}.")
        body=f"IF ({A}) {{ IF ({B}) {{ count+=1. }} }} IF ({C}) {{ IF ({D}) {{ count+=1. }} }}"
        source=prefix(family)+f"NUMBER count={k}.\n"+loop(family,variant==1,body)+"DISPLAYNL(count)."
        op=[a,b,c,d]; signature=f"count({a} AND {b})+count({c} AND {d})"
        fn=lambda i,n,xs: int(predicate(family,a,i,n,xs) and predicate(family,b,i,n,xs))+int(predicate(family,c,i,n,xs) and predicate(family,d,i,n,xs))
    else:
        a,b=keys[0],keys[1] if variant==0 else keys[2]
        A,B=expression(family,a),expression(family,b)
        if variant==0:
            prompt=(f"Read {'nonnegative n' if family=='numeric_iteration' else 'four pipe-separated numbers'}. Traverse indices downward and count items satisfying both {describe(family,a)} and {describe(family,b)}; add {k}.")
            source=prefix(family)+f"NUMBER count={k}.\n"+loop(family,True,f"IF ({A}) {{ IF ({B}) {{ count+=1. }} }}")+"DISPLAYNL(count)."
            signature=f"descending count({a} AND {b})"
            fn=lambda i,n,xs: int(predicate(family,a,i,n,xs) and predicate(family,b,i,n,xs))
        else:
            prompt=(f"Read {'nonnegative n' if family=='numeric_iteration' else 'four pipe-separated numbers'}. In two separate traversals count {describe(family,a)} and {describe(family,b)}, then add their counts and {k}.")
            body1=f"IF ({A}) {{ left+=1. }}"
            body2=f"IF ({B.replace('i','j')}) {{ right+=1. }}"
            source=prefix(family)+f"NUMBER left={k}.\nNUMBER right=0.\n"+loop(family,False,body1,"i")+loop(family,False,body2,"j")+"DISPLAYNL(left+right)."
            signature=f"two_pass count({a})+count({b})"
            fn=lambda i,n,xs: int(predicate(family,a,i,n,xs))+int(predicate(family,b,i,n,xs))
        op=[a,b]
    samples=[(stdin,k+sum(fn(i,n,xs) for i in indices(family,n))) for stdin,n,xs in examples(family,evaluation=True)]
    return prompt,source,samples,op,signature


def emit(rows,refs,tests,condition,group,family,archetype,k,item):
    prompt,source,samples,ops,signature=item
    is_eval=condition=="eval"
    ident=f"P3CDEV2-{'EVAL' if is_eval else condition.upper()+'-TR'}-{family[:2].upper()}-{archetype.upper()}-{k:02d}"
    row={"task_id" if is_eval else "example_id":ident,
         "split":f"phase3c_dev2_{'development_eval' if is_eval else condition+'_training'}",
         "family":family,"capability":"A","archetype":archetype,"prompt":prompt,
         "semantic_primitives":ops,"composition_signature":signature,
         "control_flow":"two_pass" if "two_pass" in signature else "reverse" if "NUMBER i=n." in source or "NUMBER i=3." in source else "forward",
         "ast_proxy_signature":ast_proxy(source)}
    if is_eval:
        row.update({"development_group":group,"level":"full_synthesis","required_regex":[]})
    else:
        row["target"]=source
    rows.append(row);refs[ident]=source;tests[ident]=[case(i+1,stdin,expected) for i,(stdin,expected) in enumerate(samples)]


def build():
    result={}
    for condition in ("isolated","composition"):
        rows,refs,tests=[],{},{}
        for family in PREDICATES:
            keys=names(family)
            for index,(a,b) in enumerate(PAIRS,1):
                for k in range(1,6):
                    emit(rows,refs,tests,condition,"training",family,f"pair{index}",k,
                         train_program(condition,family,keys[a],keys[b],k,index in (2,4,6)))
        result[condition]=(rows,refs,tests)
    rows,refs,tests=[],{},{}
    for family in PREDICATES:
        for variant in range(4):
            for k in (31,32):
                emit(rows,refs,tests,"eval","primitive_sanity",family,f"sanity{variant+1}",k,eval_program("primitive_sanity",family,variant,k))
        for group in ("novel_composition","structural_transfer"):
            for variant in range(2):
                for k in range(41,45) if group=="novel_composition" else range(51,55):
                    emit(rows,refs,tests,"eval",group,family,f"{group}{variant+1}",k,eval_program(group,family,variant,k))
    result["eval"]=(rows,refs,tests)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=ROOT)
    args=parser.parse_args()
    for condition,(rows,refs,tests) in build().items():
        folder=args.root/("benchmark/phase3c_dev2" if condition=="eval" else "data/phase3c_dev2")
        folder.mkdir(parents=True,exist_ok=True)
        stem="a_development_eval" if condition=="eval" else f"a_{condition}_training"
        for suffix,payload in (("tasks" if condition=="eval" else "examples",rows),("references",refs),("hidden_tests",tests)):
            path=folder/f"{stem}_{suffix}.json"
            with path.open("x",encoding="utf-8") as handle:
                json.dump(payload,handle,indent=2);handle.write("\n")
        print(condition,len(rows))


if __name__=="__main__": main()
