from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from build_phase2b_data import ast_proxy, case, split_numbers, split_sentences


def emit(rows, refs, tests, cap, split, subskill, archetype, k, prompt, source, samples, ops):
    prefix = "TR" if split == "train" else "EVAL"
    task_id = f"P3A-{cap}-{prefix}-{subskill[:2].upper()}-{archetype.upper()}-{k:02d}"
    if split == "train":
        row = {"example_id": task_id, "split": f"phase3a_{cap.lower()}_train", "family": subskill,
               "prompt": prompt, "target": source.strip()}
    else:
        row = {"task_id": task_id, "split": f"phase3a_eval_{cap.lower()}", "level": "full_synthesis",
               "family": subskill, "difficulty": "phase3a_frozen", "prompt": prompt, "required_regex": []}
    row.update({"capability": cap, "algorithmic_structure": f"p3a_{cap.lower()}_{split}_{archetype}",
                "control_flow": "numeric_iteration" if subskill == "numeric_iteration" else "array_reduction" if subskill == "array_reduction" else "string_transform" if subskill == "string_transform" else "field_processing",
                "template_lineage": f"p3a-{cap.lower()}-{split}-{archetype}-{k}",
                "structural_signature": f"{cap}>{split}>{archetype}",
                "ast_proxy_signature": ast_proxy(source), "semantic_operations": ops})
    rows.append(row)
    refs[task_id] = source.strip()
    tests[task_id] = [case(i + 1, stdin, expected) for i, (stdin, expected) in enumerate(samples)]


def build():
    result = {}
    for cap in ("A", "B"):
        for split in ("train", "eval"):
            rows, refs, tests = [], {}, {}
            limit = 15 if split == "train" else 8
            for k in range(1, limit + 1):
                p = k + 2
                if cap == "A":
                    if split == "train":
                        emit(rows, refs, tests, cap, split, "numeric_iteration", "square_stride", k,
                             f"Read nonnegative n; for i from 1 through n, add i*i only when i is divisible by {p}; print the total plus {k}.",
                             f"NUMBER n.\nINPUT(n).\nNUMBER total={k}.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (i%{p}==0) {{ total+=i*i. }} }}\nDISPLAYNL(total).",
                             [(str(n), k+sum(i*i for i in range(1,n+1) if i%p==0)) for n in (0,p,p+2,2*p+1,3*p)],
                             ["squared_divisible_filter", "sum"])
                        emit(rows, refs, tests, cap, split, "numeric_iteration", "affine_recurrence", k,
                             f"Read nonnegative n. Start x at {k}; repeat n times: double x and add {p}. Print x.",
                             f"NUMBER n.\nINPUT(n).\nNUMBER x={k}.\nLOOP (NUMBER i=0 TILL i<n, i++) {{ x=x*2+{p}. }}\nDISPLAYNL(x).",
                             [(str(n), (2**n)*k+p*(2**n-1)) for n in (0,1,2,3,4)],
                             ["affine_recurrence", "iteration"])
                        emit(rows, refs, tests, cap, split, "array_reduction", "threshold_weighted", k,
                             f"Read four pipe-delimited numbers. Keep values strictly greater than {k}; add twice each kept value; print the result.",
                             split_numbers(["a","b","c","d"])+f"NUMBER[] values=[a,b,c,d].\nNUMBER total=0.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ IF (values[i]>{k}) {{ total+=2*values[i]. }} }}\nDISPLAYNL(total).",
                             [("|".join(map(str,xs)), 2*sum(x for x in xs if x>k)) for xs in ([0,1,2,3],[k,k+1,-2,k+3],[k+5,k+2,k+1,k-1],[-4,-3,-2,-1],[10,0,10,0])],
                             ["array_threshold", "weighted_sum"])
                        emit(rows, refs, tests, cap, split, "array_reduction", "indexed_difference", k,
                             f"Read four pipe-delimited numbers into an array. Print the last minus the first, plus {k} times the third minus the second.",
                             split_numbers(["a","b","c","d"])+f"NUMBER[] values=[a,b,c,d].\nDISPLAYNL(values[3]-values[0]+{k}*(values[2]-values[1])).",
                             [("|".join(map(str,xs)), xs[3]-xs[0]+k*(xs[2]-xs[1])) for xs in ([0,1,2,3],[4,0,-2,8],[-5,3,3,-2],[1,1,1,1],[9,-2,5,0])],
                             ["array_indexed_differences", "weighted_gap"])
                    else:
                        emit(rows, refs, tests, cap, split, "numeric_iteration", "odd_cube_sum", k,
                             f"Read nonnegative n; sum the cubes of odd i from 1 through n, then subtract {k}.",
                             f"NUMBER n.\nINPUT(n).\nNUMBER total=0.\nNUMBER cube=0.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ cube=i*i*i. IF (i%2!=0) {{ total+=cube. }} }}\nDISPLAYNL(total-{k}).",
                             [(str(n), sum(i**3 for i in range(1,n+1) if i%2)-k) for n in (0,1,2,5,8)],
                             ["odd_cube_filter", "sum", "subtraction"])
                        emit(rows, refs, tests, cap, split, "numeric_iteration", "descending_product", k,
                             f"Read nonnegative n. Multiply the values {k}+i for i from 0 up to but not including n; print the product minus n.",
                             f"NUMBER n.\nINPUT(n).\nNUMBER product=1.\nLOOP (NUMBER i=0 TILL i<n, i++) {{ product*=i+{k}. }}\nDISPLAYNL(product-n).",
                             [(str(n), math.prod(i+k for i in range(n))-n) for n in (0,1,2,3,5)],
                             ["offset_product", "length_subtraction"])
                        emit(rows, refs, tests, cap, split, "array_reduction", "negative_square", k,
                             f"Read four pipe-delimited numbers into an array; sum squares of negative entries, then add {k}.",
                             split_numbers(["a","b","c","d"])+f"NUMBER[] values=[a,b,c,d].\nNUMBER total={k}.\nNUMBER current=0.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ current=values[i]. IF (current<0) {{ total+=current*current. }} }}\nDISPLAYNL(total).",
                             [("|".join(map(str,xs)), k+sum(x*x for x in xs if x<0)) for xs in ([0,1,2,3],[-1,0,-2,4],[-3,-2,-1,-4],[5,5,5,5],[0,-5,0,2])],
                             ["array_negative_filter", "squared_sum"])
                        emit(rows, refs, tests, cap, split, "array_reduction", "pairwise_products", k,
                             f"Read four pipe-delimited numbers into an array; multiply first by last and second by third; print their sum plus {k}.",
                             split_numbers(["a","b","c","d"])+f"NUMBER[] values=[a,b,c,d].\nDISPLAYNL(values[0]*values[3]+values[1]*values[2]+{k}).",
                             [("|".join(map(str,xs)), xs[0]*xs[3]+xs[1]*xs[2]+k) for xs in ([0,1,2,3],[4,0,-2,8],[-5,3,3,-2],[1,1,1,1],[9,-2,5,0])],
                             ["array_pairwise_products", "offset"])
                else:
                    chars = "abcdefghijklmno"
                    ch = chars[k-1]
                    if split == "train":
                        emit(rows, refs, tests, cap, split, "string_transform", "upper_reverse", k,
                             f"Read text. Reverse it, convert it to uppercase, and append '{ch}'.",
                             f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.CONCAT(strings.UPPER(strings.REVERSE(text)),"{ch}")).',
                             [(s, s[::-1].upper()+ch) for s in ("alpha","GoCo","xyz","Hello world","a")],
                             ["reverse", "uppercase", "suffix"])
                        emit(rows, refs, tests, cap, split, "string_transform", "replace_lower", k,
                             f"Read text. Replace every '{ch}' with '#', then lowercase the result.",
                             f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.LOWER(strings.REPLACE(text,"{ch}","#"))).',
                             [(s, s.replace(ch,"#").lower()) for s in ("alpha","GoCo","xyz","Hello world",ch+ch+"Z")],
                             ["replace", "lowercase"])
                        emit(rows, refs, tests, cap, split, "field_processing", "swap_tag", k,
                             f"Read left|right as text fields. Print right, then '/', then left, then '{ch}'.",
                             split_sentences(["left","right"])+f'DISPLAYNL(strings.CONCAT(strings.CONCAT(strings.CONCAT(right,"/"),left),"{ch}")).',
                             [(a+"|"+b, b+"/"+a+ch) for a,b in (("A","B"),("red","BLUE"),("hello","world"),("x","y"),("cat","dog"))],
                             ["split_fields", "reorder", "tag"])
                        emit(rows, refs, tests, cap, split, "field_processing", "count_fields", k,
                             f"Read left|right as text fields. Count '{ch}' in each field and print the total plus {k}.",
                             split_sentences(["left","right"])+f'DISPLAYNL(strings.COUNT(left,"{ch}")+strings.COUNT(right,"{ch}")+{k}).',
                             [(a+"|"+b, a.count(ch)+b.count(ch)+k) for a,b in (("A","B"),("red","BLUE"),("hello","world"),(ch+ch,"x"),("cat",ch))],
                             ["split_fields", "substring_count", "offset"])
                    else:
                        emit(rows, refs, tests, cap, split, "string_transform", "trim_lower_suffix", k,
                             f"Read text. Trim spaces from both ends, lowercase it, and append '{ch}'.",
                             f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.CONCAT(strings.LOWER(strings.TRIM(text," ")),"{ch}")).',
                             [(s, s.strip(" ").lower()+ch) for s in (" Alpha ","GoCo","  xyz","Hello world  "," a ")],
                             ["trim", "lowercase", "suffix"])
                        emit(rows, refs, tests, cap, split, "string_transform", "reverse_replace", k,
                             f"Read text. Reverse it, then replace each '{ch}' with '!'.",
                             f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nSENTENCE reversed=strings.REVERSE(text).\nDISPLAYNL(strings.REPLACE(reversed,"{ch}","!")).',
                             [(s, s[::-1].replace(ch,"!")) for s in ("alpha","GoCo","xyz","Hello world",ch+ch+"Z")],
                             ["reverse", "replace"])
                        emit(rows, refs, tests, cap, split, "field_processing", "case_join", k,
                             f"Read left|right as text fields. Print uppercase left, a colon, then lowercase right, followed by '{ch}'.",
                             split_sentences(["left","right"])+f'DISPLAYNL(strings.CONCAT(strings.CONCAT(strings.CONCAT(strings.UPPER(left),":"),strings.LOWER(right)),"{ch}")).',
                             [(a+"|"+b, a.upper()+":"+b.lower()+ch) for a,b in (("A","B"),("red","BLUE"),("hello","WORLD"),("x","y"),("Cat","Dog"))],
                             ["split_fields", "case_transform", "join"])
                        emit(rows, refs, tests, cap, split, "field_processing", "contains_branch", k,
                             f"Read left|right as text fields. Print YES if left contains '{ch}' and right contains '{ch}'; otherwise print NO.",
                             split_sentences(["left","right"])+f'IF (strings.CONTAINS(left,"{ch}") AND strings.CONTAINS(right,"{ch}")) {{ DISPLAYNL("YES"). }} ELSE {{ DISPLAYNL("NO"). }}',
                             [(a+"|"+b, "YES" if ch in a and ch in b else "NO") for a,b in ((ch,"x"),(ch,ch),("hello","WORLD"),("x",ch),(ch+"a",ch+"b"))],
                             ["split_fields", "dual_contains", "branch"])
            result[(cap,split)] = (rows, refs, tests)
    return result


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--output-dir",type=Path,default=Path("data/phase3a")); parser.add_argument("--benchmark-dir",type=Path,default=Path("benchmark/phase3a")); args=parser.parse_args()
    for (cap,split),(rows,refs,tests) in build().items():
        out=args.output_dir if split=="train" else args.benchmark_dir
        out.mkdir(parents=True,exist_ok=True)
        stem=f"{cap.lower()}_{'training' if split=='train' else 'eval'}"
        (out/f"{stem}_{'examples' if split=='train' else 'tasks'}.json").write_text(json.dumps(rows,indent=2)+"\n",encoding="utf-8")
        (out/f"{stem}_hidden_tests.json").write_text(json.dumps(tests,indent=2)+"\n",encoding="utf-8")
        if split=="eval": (out/f"{stem}_references.json").write_text(json.dumps(refs,indent=2)+"\n",encoding="utf-8")
        print(cap,split,len(rows))

if __name__=="__main__": main()
