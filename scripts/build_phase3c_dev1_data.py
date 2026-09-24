"""Construct Phase 3C-DEV1 development-only A data without model access."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_phase2b_data import ast_proxy, case, split_numbers


NUMERIC_INPUTS = (0, 1, 3, 6, 9)
ARRAY_INPUTS = ((0, 0, 0, 0), (-3, 1, 4, -2), (5, -1, 2, 7),
                (-4, -3, -2, -1), (2, 2, -5, 2))
FAR_NUMERIC_INPUTS = (0, 1, 4, 15, 30)
ARRAY_PREFIX = split_numbers(["a", "b", "c", "d"]) + "NUMBER[] values=[a,b,c,d].\n"

TRAIN_ARCHETYPES = {
    "numeric_iteration": ("fourth_square", "nontriple_count", "alternating_weight",
                          "divisor_tally", "descending_odd", "quadratic_balance"),
    "array_reduction": ("negative_tally", "neighbor_products", "positive_position",
                        "range_span", "alternating_positions", "even_square_total"),
}
SHARED_DENSE = {"fourth_square", "nontriple_count", "negative_tally", "neighbor_products"}
EVAL_ARCHETYPES = {
    "numeric_iteration": (("near", "fourth_square_step"),
                          ("compositional", "nontriple_divisor_mix"),
                          ("far", "square_threshold_crossing")),
    "array_reduction": (("near", "negative_tally_unrolled"),
                        ("compositional", "range_neighbor_mix"),
                        ("far", "positive_run_length")),
}


def arr_stdin(xs: tuple[int, ...]) -> str:
    return "|".join(map(str, xs))


def train_item(name: str, k: int) -> tuple[str, str, list[tuple[str, int]], list[str], str]:
    p = ARRAY_PREFIX
    if name == "fourth_square":
        prompt = f"Read nonnegative n. Sum the squares of positive indices divisible by four up to n, then add {k}."
        source = f"NUMBER n.\nINPUT(n).\nNUMBER total={k}.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (i%4==0) {{ total+=i*i. }} }}\nDISPLAYNL(total)."
        samples = [(str(n), k + sum(i*i for i in range(1, n+1) if i % 4 == 0)) for n in NUMERIC_INPUTS]
        return prompt, source, samples, ["multiple_of_four", "square_sum", "offset"], "loop_if"
    if name == "nontriple_count":
        prompt = f"Read nonnegative n. Count positive indices up to n that are not divisible by three; print twice the count plus {k}."
        source = f"NUMBER n.\nINPUT(n).\nNUMBER count=0.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (i%3!=0) {{ count+=1. }} }}\nDISPLAYNL(2*count+{k})."
        samples = [(str(n), 2*sum(i % 3 != 0 for i in range(1, n+1))+k) for n in NUMERIC_INPUTS]
        return prompt, source, samples, ["not_multiple_three", "count", "affine_output"], "loop_if"
    if name == "alternating_weight":
        prompt = f"Read nonnegative n. From 1 through n, add {k} times odd indices and subtract even indices; print the total."
        source = f"NUMBER n.\nINPUT(n).\nNUMBER total=0.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (i%2==1) {{ total+={k}*i. }} ELSE {{ total-=i. }} }}\nDISPLAYNL(total)."
        samples = [(str(n), sum(k*i if i % 2 else -i for i in range(1, n+1))) for n in NUMERIC_INPUTS]
        return prompt, source, samples, ["parity_branch", "weighted_alternation"], "loop_if_else"
    if name == "divisor_tally":
        prompt = f"Read nonnegative n. Count positive divisors of n from 1 through n and add {k}."
        source = f"NUMBER n.\nINPUT(n).\nNUMBER count={k}.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (n%i==0) {{ count+=1. }} }}\nDISPLAYNL(count)."
        samples = [(str(n), k+sum(n % i == 0 for i in range(1, n+1))) for n in NUMERIC_INPUTS]
        return prompt, source, samples, ["divisor_test", "count", "offset"], "loop_if"
    if name == "descending_odd":
        prompt = f"Read nonnegative n. Walk downward from n to 1 and add each odd index plus {k}; print the sum."
        source = f"NUMBER n.\nINPUT(n).\nNUMBER total=0.\nNUMBER i=n.\nLOOP (i>=1) {{ IF (i%2==1) {{ total+=i+{k}. }} i-=1. }}\nDISPLAYNL(total)."
        samples = [(str(n), sum(i+k for i in range(n, 0, -1) if i % 2)) for n in NUMERIC_INPUTS]
        return prompt, source, samples, ["descending_loop", "odd_index_filter", "affine_sum"], "descending_loop_if"
    if name == "quadratic_balance":
        prompt = f"Read nonnegative n. For every index 1 through n, add its square and subtract {k} times the index; print the result."
        source = f"NUMBER n.\nINPUT(n).\nNUMBER total=0.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ total+=i*i-{k}*i. }}\nDISPLAYNL(total)."
        samples = [(str(n), sum(i*i-k*i for i in range(1, n+1))) for n in NUMERIC_INPUTS]
        return prompt, source, samples, ["quadratic_term", "linear_term", "sum"], "loop_arithmetic"
    if name == "negative_tally":
        prompt = f"Read four pipe-delimited numbers as an array. Count strictly negative entries and add {k}."
        source = p+f"NUMBER count={k}.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ IF (values[i]<0) {{ count+=1. }} }}\nDISPLAYNL(count)."
        samples = [(arr_stdin(xs), k+sum(x<0 for x in xs)) for xs in ARRAY_INPUTS]
        return prompt, source, samples, ["negative_filter", "count", "offset"], "array_loop_if"
    if name == "neighbor_products":
        prompt = f"Read four pipe-delimited numbers as an array. Sum products of neighboring pairs, then add {k}."
        source = p+f"NUMBER total={k}.\nLOOP (NUMBER i=0 TILL i<3, i++) {{ total+=values[i]*values[i+1]. }}\nDISPLAYNL(total)."
        samples = [(arr_stdin(xs), k+sum(xs[i]*xs[i+1] for i in range(3))) for xs in ARRAY_INPUTS]
        return prompt, source, samples, ["neighbor_products", "array_sum", "offset"], "array_loop_arithmetic"
    if name == "positive_position":
        prompt = f"Read four pipe-delimited numbers as an array. Add each positive entry times its one-based position, then add {k}."
        source = p+f"NUMBER total={k}.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ IF (values[i]>0) {{ total+=values[i]*(i+1). }} }}\nDISPLAYNL(total)."
        samples = [(arr_stdin(xs), k+sum(x*(i+1) for i,x in enumerate(xs) if x>0)) for xs in ARRAY_INPUTS]
        return prompt, source, samples, ["positive_filter", "position_weight", "array_sum"], "array_loop_if"
    if name == "range_span":
        prompt = f"Read four pipe-delimited numbers as an array. Subtract the minimum from the maximum and add {k}."
        source = p+f"NUMBER lo=values[0].\nNUMBER hi=values[0].\nLOOP (NUMBER i=1 TILL i<4, i++) {{ IF (values[i]<lo) {{ lo=values[i]. }} IF (values[i]>hi) {{ hi=values[i]. }} }}\nDISPLAYNL(hi-lo+{k})."
        samples = [(arr_stdin(xs), max(xs)-min(xs)+k) for xs in ARRAY_INPUTS]
        return prompt, source, samples, ["array_minimum", "array_maximum", "range", "offset"], "array_loop_two_if"
    if name == "alternating_positions":
        prompt = f"Read four pipe-delimited numbers as an array. Add entries at even zero-based positions, subtract entries at odd positions, then add {k}."
        source = p+f"NUMBER total={k}.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ IF (i%2==0) {{ total+=values[i]. }} ELSE {{ total-=values[i]. }} }}\nDISPLAYNL(total)."
        samples = [(arr_stdin(xs), k+sum(x if i%2==0 else -x for i,x in enumerate(xs))) for xs in ARRAY_INPUTS]
        return prompt, source, samples, ["position_parity", "alternating_array_sum"], "array_loop_if_else"
    if name == "even_square_total":
        prompt = f"Read four pipe-delimited numbers as an array. Sum squares of even-valued entries and add {k}."
        source = p+f"NUMBER total={k}.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ IF (values[i]%2==0) {{ total+=values[i]*values[i]. }} }}\nDISPLAYNL(total)."
        samples = [(arr_stdin(xs), k+sum(x*x for x in xs if x%2==0)) for xs in ARRAY_INPUTS]
        return prompt, source, samples, ["even_value_filter", "square_sum", "array_sum"], "array_loop_if"
    raise KeyError(name)


def eval_item(name: str, k: int) -> tuple[str, str, list[tuple[str, int]], list[str], str]:
    p = ARRAY_PREFIX
    if name == "fourth_square_step":
        prompt = f"Read nonnegative n. Starting at four, visit multiples of four no greater than n. Add each visited index squared, then print the sum plus {k}."
        source = f"NUMBER n.\nINPUT(n).\nNUMBER total={k}.\nLOOP (NUMBER step=1 TILL 4*step<=n, step++) {{ total+=16*step*step. }}\nDISPLAYNL(total)."
        samples = [(str(n), k+sum(i*i for i in range(4,n+1,4))) for n in NUMERIC_INPUTS]
        return prompt, source, samples, ["multiple_of_four", "square_sum", "offset"], "stepped_loop"
    if name == "nontriple_divisor_mix":
        prompt = f"Read nonnegative n. Count indices from 1 to n not divisible by three, and also count n's positive divisors. Print their combined count plus {k}."
        source = f"NUMBER n.\nINPUT(n).\nNUMBER total={k}.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (i%3!=0) {{ total+=1. }} IF (n%i==0) {{ total+=1. }} }}\nDISPLAYNL(total)."
        samples = [(str(n), k+sum(i%3!=0 for i in range(1,n+1))+sum(n%i==0 for i in range(1,n+1))) for n in NUMERIC_INPUTS]
        return prompt, source, samples, ["not_multiple_three", "count", "divisor_test", "recomposition"], "loop_two_if"
    if name == "square_threshold_crossing":
        prompt = f"Read nonnegative threshold n. Find the smallest positive index whose cumulative sum of squares reaches at least n plus {k}; print the index."
        source = f"NUMBER n.\nINPUT(n).\nNUMBER total=0.\nNUMBER i=0.\nLOOP (total<n+{k}) {{ i+=1. total+=i*i. }}\nDISPLAYNL(i)."
        samples = []
        for n in FAR_NUMERIC_INPUTS:
            total=i=0
            while total<n+k:
                i+=1; total+=i*i
            samples.append((str(n),i))
        return prompt, source, samples, ["cumulative_square_threshold", "first_crossing"], "conditioned_loop"
    if name == "negative_tally_unrolled":
        prompt = f"Read a pipe-separated array of four numbers. Check each position for a negative value and print how many are negative, plus {k}."
        source = p+f"NUMBER count={k}.\nIF (a<0) {{ count+=1. }}\nIF (b<0) {{ count+=1. }}\nIF (c<0) {{ count+=1. }}\nIF (d<0) {{ count+=1. }}\nDISPLAYNL(count)."
        samples = [(arr_stdin(xs), k+sum(x<0 for x in xs)) for xs in ARRAY_INPUTS]
        return prompt, source, samples, ["negative_filter", "count", "offset"], "unrolled_array_if"
    if name == "range_neighbor_mix":
        prompt = f"Read four pipe-delimited numbers as an array. Add the product of each neighboring pair and the array's maximum-minus-minimum range, then add {k}."
        source = p+f"NUMBER lo=values[0].\nNUMBER hi=values[0].\nNUMBER total={k}.\nLOOP (NUMBER i=0 TILL i<3, i++) {{ total+=values[i]*values[i+1]. }}\nLOOP (NUMBER j=1 TILL j<4, j++) {{ IF (values[j]<lo) {{ lo=values[j]. }} IF (values[j]>hi) {{ hi=values[j]. }} }}\nDISPLAYNL(total+hi-lo)."
        samples = [(arr_stdin(xs), k+sum(xs[i]*xs[i+1] for i in range(3))+max(xs)-min(xs)) for xs in ARRAY_INPUTS]
        return prompt, source, samples, ["neighbor_products", "array_minimum", "array_maximum", "range", "recomposition"], "two_array_loops"
    if name == "positive_run_length":
        prompt = f"Read four pipe-delimited numbers as an array. Find the length of its longest consecutive run of strictly positive entries and add {k}."
        source = p+f"NUMBER run=0.\nNUMBER best=0.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ IF (values[i]>0) {{ run+=1. IF (run>best) {{ best=run. }} }} ELSE {{ run=0. }} }}\nDISPLAYNL(best+{k})."
        samples=[]
        for xs in ARRAY_INPUTS:
            run=best=0
            for x in xs:
                run=run+1 if x>0 else 0
                best=max(best,run)
            samples.append((arr_stdin(xs),best+k))
        return prompt, source, samples, ["positive_run", "longest_segment"], "array_loop_nested_if"
    raise KeyError(name)


def emit(condition: str, split: str, family: str, archetype: str, k: int,
         item: tuple[str, str, list[tuple[str, int]], list[str], str],
         rows: list[dict], refs: dict, tests: dict) -> None:
    prompt, source, samples, operations, flow = item
    if split == "training":
        item_id = f"P3CDEV1-{condition}-TR-{family[:2].upper()}-{archetype.upper()}-{k:02d}"
        row = {"example_id": item_id, "split": f"phase3c_dev1_{condition.lower()}_training",
               "family": family, "prompt": prompt, "target": source}
    else:
        item_id = f"P3CDEV1-EVAL-{family[:2].upper()}-{archetype.upper()}-{k:02d}"
        row = {"task_id": item_id, "split": "phase3c_dev1_development_eval",
               "level": "full_synthesis", "difficulty": "development_only",
               "family": family, "prompt": prompt, "required_regex": []}
    row.update({"capability": "A", "archetype": archetype,
                "algorithmic_structure": f"dev1_{split}_{archetype}",
                "control_flow": flow, "template_lineage": f"dev1-{split}-{archetype}-{k}",
                "structural_signature": f"A>{split}>{archetype}",
                "ast_proxy_signature": ast_proxy(source), "semantic_operations": operations})
    if split == "evaluation":
        row["distance_group"] = next(group for group, name in EVAL_ARCHETYPES[family] if name == archetype)
    rows.append(row)
    refs[item_id] = source
    tests[item_id] = [case(i+1, stdin, expected) for i,(stdin,expected) in enumerate(samples)]


def build():
    result = {}
    for condition in ("DENSE", "DIVERSE"):
        rows, refs, tests = [], {}, {}
        for family, archetypes in TRAIN_ARCHETYPES.items():
            names = tuple(x for x in archetypes if condition == "DIVERSE" or x in SHARED_DENSE)
            for name in names:
                for k in range(1, 6 if condition == "DIVERSE" else 16):
                    emit(condition, "training", family, name, k, train_item(name,k),rows,refs,tests)
        result[condition] = (rows, refs, tests)
    rows, refs, tests = [], {}, {}
    for family, archetypes in EVAL_ARCHETYPES.items():
        for _, name in archetypes:
            for k in range(21,27):
                emit("EVAL", "evaluation", family, name, k, eval_item(name,k),rows,refs,tests)
    result["EVAL"] = (rows,refs,tests)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir",type=Path,default=Path("data/phase3c_dev1"))
    parser.add_argument("--benchmark-dir",type=Path,default=Path("benchmark/phase3c_dev1"))
    args=parser.parse_args()
    for condition,(rows,refs,tests) in build().items():
        folder=args.benchmark_dir if condition=="EVAL" else args.data_dir
        folder.mkdir(parents=True,exist_ok=True)
        stem="a_development_eval" if condition=="EVAL" else f"a_{condition.lower()}_training"
        files={f"{stem}_{'tasks' if condition=='EVAL' else 'examples'}.json":rows,
               f"{stem}_hidden_tests.json":tests,
               f"{stem}_references.json":refs}
        for name,value in files.items():
            with (folder/name).open("x",encoding="utf-8") as handle:
                json.dump(value,handle,indent=2);handle.write("\n")
        print(condition,len(rows),sum(r["family"]=="numeric_iteration" for r in rows))


if __name__=="__main__":
    main()
