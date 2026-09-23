from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from build_phase2b_data import ast_proxy, case, split_numbers, split_sentences


def add(rows, refs, tests, cap, split, family, algorithm, k, prompt, source, samples, ops):
    tid=f"P3B-{cap}-{'TR' if split=='training' else 'EVAL'}-{family[:2].upper()}-{algorithm.upper()}-{k:02d}"
    if split=="training":
        row={"example_id":tid,"split":f"phase3b_{cap.lower()}_train","family":family,"prompt":prompt,"target":source.strip()}
    else:
        row={"task_id":tid,"split":f"phase3b_eval_{cap.lower()}","level":"full_synthesis","family":family,"difficulty":"phase3b_frozen","prompt":prompt,"required_regex":[]}
    row.update({"capability":cap,"algorithmic_structure":f"p3b_{cap.lower()}_{split}_{algorithm}","control_flow":family,"template_lineage":f"p3b-{cap.lower()}-{split}-{algorithm}-{k}","structural_signature":f"{cap}>{split}>{algorithm}","ast_proxy_signature":ast_proxy(source),"semantic_operations":ops})
    rows.append(row); refs[tid]=source.strip()
    tests[tid]=[case(i+1,stdin,expected) for i,(stdin,expected) in enumerate(samples)]


def build():
    result={}
    values4=([0,1,2,3],[-2,4,0,8],[5,-3,7,-1],[2,2,2,2],[-5,-4,-3,-2])
    strings=(" alpha ","GoCo","xyz"," Hello world "," aAa ")
    fields=(("a","b"),("red","BLUE"),("hello","world"),("x","XYZ"),("cat","dog"))
    for cap in "AB":
        for split in ("training","eval"):
            rows,refs,tests=[],{},{}
            for k in range(1,16 if split=="training" else 9):
                q=k+2; ch="abcdefghijklmno"[k-1]
                if cap=="A" and split=="training":
                    add(rows,refs,tests,cap,split,"numeric_iteration","even_square_offset",k,
                        f"Read nonnegative n. For each even i from 1 through n, add i*i+{k}. Print the total.",
                        f"NUMBER n.\nINPUT(n).\nNUMBER total=0.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (i%2==0) {{ total+=i*i+{k}. }} }}\nDISPLAYNL(total).",
                        [(str(n),sum(i*i+k for i in range(1,n+1) if i%2==0)) for n in (0,1,2,5,8)],
                        ["even_filter","square_offset_sum"])
                    add(rows,refs,tests,cap,split,"numeric_iteration","shifted_mod_sum",k,
                        f"Read nonnegative n. For i=1..n, add i+{k} to a total only when i+{k} is divisible by 4. Print the total.",
                        f"NUMBER n.\nINPUT(n).\nNUMBER total=0.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF ((i+{k})%4==0) {{ total+=i+{k}. }} }}\nDISPLAYNL(total).",
                        [(str(n),sum(i+k for i in range(1,n+1) if (i+k)%4==0)) for n in (0,1,4,7,11)],
                        ["shifted_modulo_filter","value_sum"])
                    add(rows,refs,tests,cap,split,"array_reduction","positive_position_weight",k,
                        f"Read four pipe-delimited numbers into an array. Add (position+1)*value for positive entries, then add {k}.",
                        split_numbers(["a","b","c","d"])+f"NUMBER[] values=[a,b,c,d].\nNUMBER total={k}.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ IF (values[i]>0) {{ total+=(i+1)*values[i]. }} }}\nDISPLAYNL(total).",
                        [("|".join(map(str,xs)),k+sum((i+1)*x for i,x in enumerate(xs) if x>0)) for xs in values4],
                        ["positive_array_filter","position_weight"])
                    add(rows,refs,tests,cap,split,"array_reduction","adjacent_distance",k,
                        f"Read four pipe-delimited numbers into an array. Sum absolute differences between adjacent entries and add {k}.",
                        split_numbers(["a","b","c","d"])+f"IMPORT math.\nNUMBER[] values=[a,b,c,d].\nNUMBER total={k}.\nLOOP (NUMBER i=0 TILL i<3, i++) {{ total+=math.ABS(values[i+1]-values[i]). }}\nDISPLAYNL(total).",
                        [("|".join(map(str,xs)),k+sum(abs(xs[i+1]-xs[i]) for i in range(3))) for xs in values4],
                        ["array_adjacent_difference","absolute_sum"])
                elif cap=="A":
                    add(rows,refs,tests,cap,split,"numeric_iteration","divisor_pair_sum",k,
                        f"Read nonnegative n. For every positive divisor i of n, add i*i+{k}; print the sum.",
                        f"NUMBER n.\nINPUT(n).\nNUMBER total=0.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (n%i==0) {{ NUMBER term=i*i+{k}. total+=term. }} }}\nDISPLAYNL(total).",
                        [(str(n),sum(i*i+k for i in range(1,n+1) if n%i==0)) for n in (0,q,q+1,2*q,3*q+1)],
                        ["divisor_filter","square_offset_sum"])
                    add(rows,refs,tests,cap,split,"numeric_iteration","odd_step_recurrence",k,
                        f"Read nonnegative n. Start x={k}. On each step i, double x, then add i if odd or subtract i if even. Print x.",
                        f"NUMBER n.\nINPUT(n).\nNUMBER x={k}.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (i%2==0) {{ x=2*x-i. }} ELSE {{ x=2*x+i. }} }}\nDISPLAYNL(x).",
                        [(str(n),sum((i if i%2 else -i)*(2**(n-i)) for i in range(1,n+1))+k*(2**n)) for n in (0,1,2,5,8)],
                        ["alternating_doubling_recurrence","indexed_offset"])
                    add(rows,refs,tests,cap,split,"array_reduction","extrema_spread",k,
                        f"Read four pipe-delimited numbers into an array. Find the largest and smallest via a loop, print largest-smallest+{k}.",
                        split_numbers(["a","b","c","d"])+f"NUMBER[] values=[a,b,c,d].\nNUMBER hi=values[0].\nNUMBER lo=values[0].\nLOOP (NUMBER i=1 TILL i<4, i++) {{ IF (values[i]>hi) {{ hi=values[i]. }} IF (values[i]<lo) {{ lo=values[i]. }} }}\nDISPLAYNL(hi-lo+{k}).",
                        [("|".join(map(str,xs)),max(xs)-min(xs)+k) for xs in values4],
                        ["array_extrema_loop","spread"])
                    add(rows,refs,tests,cap,split,"array_reduction","pair_product_gap",k,
                        f"Read four pipe-delimited numbers into an array. Print the absolute difference of the first pair's product and the last pair's product, plus {k}.",
                        split_numbers(["a","b","c","d"])+f"IMPORT math.\nNUMBER[] values=[a,b,c,d].\nDISPLAYNL(math.ABS(values[0]*values[1]-values[2]*values[3])+{k}).",
                        [("|".join(map(str,xs)),abs(xs[0]*xs[1]-xs[2]*xs[3])+k) for xs in values4],
                        ["array_pair_products","absolute_gap"])
                elif split=="training":
                    add(rows,refs,tests,cap,split,"string_transform","trim_reverse_upper",k,
                        f"Read text. Trim spaces at both ends, reverse the result, uppercase it, then append '{ch}'.",
                        f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.CONCAT(strings.UPPER(strings.REVERSE(strings.TRIM(text," "))),"{ch}")).',
                        [(s,s.strip(" ")[::-1].upper()+ch) for s in strings],
                        ["space_trim","reverse","uppercase","suffix"])
                    add(rows,refs,tests,cap,split,"string_transform","lower_replace_prefix",k,
                        f"Read text. Lowercase it, replace '{ch}' with '!', and prefix '{ch}:'.",
                        f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.CONCAT("{ch}:",strings.REPLACE(strings.LOWER(text),"{ch}","!"))).',
                        [(s,ch+":"+s.lower().replace(ch,"!")) for s in strings],
                        ["lowercase","replace","prefix"])
                    add(rows,refs,tests,cap,split,"field_processing","field_length_label",k,
                        f"Read left|right text fields. Print LONG{k} if the left field is longer, otherwise SHORT{k}.",
                        split_sentences(["left","right"])+f'IF (strings.LENGTH(left)>strings.LENGTH(right)) {{ DISPLAYNL("LONG{k}"). }} ELSE {{ DISPLAYNL("SHORT{k}"). }}',
                        [(a+"|"+b,f"LONG{k}" if len(a)>len(b) else f"SHORT{k}") for a,b in fields],
                        ["split_fields","length_compare","branch"])
                    add(rows,refs,tests,cap,split,"field_processing","reverse_upper_join",k,
                        f"Read left|right text fields. Print reversed right, a colon, uppercase left, then '{ch}'.",
                        split_sentences(["left","right"])+f'DISPLAYNL(strings.CONCAT(strings.CONCAT(strings.CONCAT(strings.REVERSE(right),":"),strings.UPPER(left)),"{ch}")).',
                        [(a+"|"+b,b[::-1]+":"+a.upper()+ch) for a,b in fields],
                        ["split_fields","reverse_right","uppercase_left","join"])
                else:
                    add(rows,refs,tests,cap,split,"string_transform","upper_replace_reverse",k,
                        f"Read text. Uppercase it, replace every '{ch.upper()}' with '?', then reverse the result.",
                        f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.REVERSE(strings.REPLACE(strings.UPPER(text),"{ch.upper()}","?"))).',
                        [(s,s.upper().replace(ch.upper(),"?")[::-1]) for s in strings],
                        ["uppercase","replace","reverse"])
                    add(rows,refs,tests,cap,split,"string_transform","trim_duplicate_lower",k,
                        f"Read text. Trim spaces, lowercase the result, and print it twice separated by '{ch}'.",
                        f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nSENTENCE low=strings.LOWER(strings.TRIM(text," ")).\nDISPLAYNL(strings.CONCAT(strings.CONCAT(low,"{ch}"),low)).',
                        [(s,s.strip(" ").lower()+ch+s.strip(" ").lower()) for s in strings],
                        ["space_trim","lowercase","duplicate"])
                    add(rows,refs,tests,cap,split,"field_processing","contains_select",k,
                        f"Read left|right text fields. If left contains '{ch}', print uppercase right; otherwise print lowercase left.",
                        split_sentences(["left","right"])+f'IF (strings.CONTAINS(left,"{ch}")) {{ DISPLAYNL(strings.UPPER(right)). }} ELSE {{ DISPLAYNL(strings.LOWER(left)). }}',
                        [(a+"|"+b,b.upper() if ch in a else a.lower()) for a,b in fields],
                        ["split_fields","contains_branch","case_select"])
                    add(rows,refs,tests,cap,split,"field_processing","weighted_field_count",k,
                        f"Read left|right text fields. Count '{ch}' twice in left and once in right; print that weighted count plus {k}.",
                        split_sentences(["left","right"])+f'DISPLAYNL(2*strings.COUNT(left,"{ch}")+strings.COUNT(right,"{ch}")+{k}).',
                        [(a+"|"+b,2*a.count(ch)+b.count(ch)+k) for a,b in fields],
                        ["split_fields","weighted_substring_count","offset"])
            result[(cap,split)]=(rows,refs,tests)
    return result


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--data-dir",type=Path,default=Path("data/phase3b")); parser.add_argument("--benchmark-dir",type=Path,default=Path("benchmark/phase3b")); args=parser.parse_args()
    for (cap,split),(rows,refs,tests) in build().items():
        out=args.data_dir if split=="training" else args.benchmark_dir
        out.mkdir(parents=True,exist_ok=True)
        stem=f"{cap.lower()}_{split}"
        (out/f"{stem}_{'examples' if split=='training' else 'tasks'}.json").write_text(json.dumps(rows,indent=2)+"\n",encoding="utf-8")
        (out/f"{stem}_hidden_tests.json").write_text(json.dumps(tests,indent=2)+"\n",encoding="utf-8")
        if split=="eval": (out/f"{stem}_references.json").write_text(json.dumps(refs,indent=2)+"\n",encoding="utf-8")
        print(cap,split,len(rows))


if __name__=="__main__": main()
