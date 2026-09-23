"""Construct fresh Phase 3C examples and references; no model is loaded."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_phase2b_data import ast_proxy, case, split_numbers, split_sentences


NUMBERS = ([0, 1, 2, 3], [-2, 4, 0, 8], [5, -3, 7, -1], [2, 2, 2, 2], [-5, -4, -3, -2])
TEXTS = (" alpha ", "GoCo", "xyz", " Hello world ", " aAa ")


def emit(rows, refs, tests, cap, split, family, archetype, k, prompt, source, samples, operations):
    item_id = f"P3C-{cap}-{'TR' if split == 'training' else 'EVAL'}-{family[:2].upper()}-{archetype.upper()}-{k:02d}"
    if split == "training":
        row = {"example_id": item_id, "split": f"phase3c_{cap.lower()}_training", "family": family,
               "prompt": prompt, "target": source.strip()}
    else:
        row = {"task_id": item_id, "split": f"phase3c_eval_{cap.lower()}", "level": "full_synthesis",
               "family": family, "difficulty": "phase3c_frozen", "prompt": prompt, "required_regex": []}
    row.update({
        "capability": cap, "archetype": archetype,
        "algorithmic_structure": f"p3c_{cap.lower()}_{split}_{archetype}",
        "control_flow": family,
        "template_lineage": f"p3c-{cap.lower()}-{split}-{archetype}-{k}",
        "structural_signature": f"{cap}>{split}>{archetype}",
        "ast_proxy_signature": ast_proxy(source), "semantic_operations": operations,
    })
    rows.append(row)
    refs[item_id] = source.strip()
    tests[item_id] = [case(i + 1, stdin, expected) for i, (stdin, expected) in enumerate(samples)]


def build():
    result = {}
    for cap in "AB":
        for split in ("training", "eval"):
            rows, refs, tests = [], {}, {}
            for k in range(1, 16 if split == "training" else 9):
                ch = "abcdefghijklmno"[k - 1]
                field_pairs = ((ch + "x", "red"), ("blue", ch + "Z"), ("hello", "WORLD"),
                               ("x", "xyz"), (ch + ch, ch))
                if cap == "A" and split == "training":
                    emit(rows, refs, tests, cap, split, "numeric_iteration", "odd_linear_bonus", k,
                         f"Read nonnegative n. For each odd i from 1 through n, add 2*i+{k}; print the total.",
                         f"NUMBER n.\nINPUT(n).\nNUMBER total=0.\nNUMBER i=1.\nLOOP (i<=n) {{ total+=2*i+{k}. i+=2. }}\nDISPLAYNL(total).",
                         [(str(n), sum(2*i+k for i in range(1, n+1) if i%2)) for n in (0, 1, 2, 5, 8)],
                         ["odd_index_filter", "linear_weighted_sum"])
                    emit(rows, refs, tests, cap, split, "numeric_iteration", "even_count_shift", k,
                         f"Read nonnegative n. Count even integers from 1 through n; print three times the count plus {k}.",
                         f"NUMBER n.\nINPUT(n).\nNUMBER count=0.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (i%2==0) {{ count+=1. }} }}\nDISPLAYNL(3*count+{k}).",
                         [(str(n), 3*(n//2)+k) for n in (0, 1, 2, 5, 8)],
                         ["even_index_filter", "count", "affine_output"])
                    emit(rows, refs, tests, cap, split, "array_reduction", "positive_square_sum", k,
                         f"Read four pipe-delimited numbers into an array. Sum squares of positive entries and add {k}.",
                         split_numbers(["a", "b", "c", "d"])+f"NUMBER[] values=[a,b,c,d].\nNUMBER total={k}.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ IF (values[i]>0) {{ total+=values[i]*values[i]. }} }}\nDISPLAYNL(total).",
                         [("|".join(map(str, xs)), k+sum(x*x for x in xs if x>0)) for xs in NUMBERS],
                         ["positive_array_filter", "square_sum"])
                    emit(rows, refs, tests, cap, split, "array_reduction", "count_above_shift", k,
                         f"Read four pipe-delimited numbers into an array. Count entries strictly above {k}; print count plus {k}.",
                         split_numbers(["a", "b", "c", "d"])+f"NUMBER[] values=[a,b,c,d].\nNUMBER count=0.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ IF (values[i]>{k}) {{ count+=1. }} }}\nDISPLAYNL(count+{k}).",
                         [("|".join(map(str, xs)), k+sum(x>k for x in xs)) for xs in NUMBERS],
                         ["array_threshold", "count", "offset"])
                elif cap == "A":
                    emit(rows, refs, tests, cap, split, "numeric_iteration", "triangular_milestones", k,
                         f"Read nonnegative n. Maintain the running sum of integers 1 through i. At each i divisible by three, add that running sum to an answer initially {k}. Print the answer.",
                         f"NUMBER n.\nINPUT(n).\nNUMBER running=0.\nNUMBER answer={k}.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ running+=i. IF (i%3==0) {{ answer+=running. }} }}\nDISPLAYNL(answer).",
                         [(str(n), k+sum(i*(i+1)//2 for i in range(1, n+1) if i%3==0)) for n in (0, 2, 3, 6, 10)],
                         ["running_triangular", "multiple_of_three_milestone"])
                    emit(rows, refs, tests, cap, split, "numeric_iteration", "alternating_accumulator", k,
                         f"Read nonnegative n. Start total at {k}; from i=1 through n add odd i and subtract even i; print total.",
                         f"NUMBER n.\nINPUT(n).\nNUMBER total={k}.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (i%2==0) {{ total-=i. }} ELSE {{ total+=i. }} }}\nDISPLAYNL(total).",
                         [(str(n), k+sum(i if i%2 else -i for i in range(1, n+1))) for n in (0, 1, 2, 5, 8)],
                         ["parity_branch", "alternating_sum"])
                    emit(rows, refs, tests, cap, split, "array_reduction", "negative_position_weight", k,
                         f"Read four pipe-delimited numbers into an array. For each negative entry add its magnitude times its one-based position; then add {k}.",
                         split_numbers(["a", "b", "c", "d"])+f"NUMBER[] values=[a,b,c,d].\nNUMBER total={k}.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ IF (values[i]<0) {{ total+=(0-values[i])*(i+1). }} }}\nDISPLAYNL(total).",
                         [("|".join(map(str, xs)), k+sum(-x*(i+1) for i, x in enumerate(xs) if x<0)) for xs in NUMBERS],
                         ["negative_array_filter", "position_weighted_magnitude"])
                    emit(rows, refs, tests, cap, split, "array_reduction", "outer_inner_gap", k,
                         f"Read four pipe-delimited numbers into an array. Print the absolute difference between the sum of the outer pair and the sum of the inner pair, plus {k}.",
                         split_numbers(["a", "b", "c", "d"])+f"IMPORT math.\nNUMBER[] values=[a,b,c,d].\nDISPLAYNL(math.ABS(values[0]+values[3]-values[1]-values[2])+{k}).",
                         [("|".join(map(str, xs)), abs(xs[0]+xs[3]-xs[1]-xs[2])+k) for xs in NUMBERS],
                         ["outer_inner_pair_sums", "absolute_gap"])
                elif split == "training":
                    emit(rows, refs, tests, cap, split, "string_transform", "upper_replace_suffix", k,
                         f"Read text. Uppercase it, replace each '{ch.upper()}' with '*', then append '{ch}'.",
                         f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.CONCAT(strings.REPLACE(strings.UPPER(text),"{ch.upper()}","*"),"{ch}")).',
                         [(s, s.upper().replace(ch.upper(), "*")+ch) for s in (*TEXTS[:-1], ch+ch+"Z")],
                         ["uppercase", "replace", "suffix"])
                    emit(rows, refs, tests, cap, split, "string_transform", "trim_reverse_prefix", k,
                         f"Read text. Trim spaces, reverse it, then prefix '{ch}:'.",
                         f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.CONCAT("{ch}:",strings.REVERSE(strings.TRIM(text," ")))).',
                         [(s, ch+":"+s.strip(" ")[::-1]) for s in TEXTS],
                         ["space_trim", "reverse", "prefix"])
                    emit(rows, refs, tests, cap, split, "field_processing", "right_count_left_length", k,
                         f"Read left|right text fields. Count '{ch}' in right and add the length of left; print the number.",
                         split_sentences(["left", "right"])+f'NUMBER count=strings.COUNT(right,"{ch}").\nDISPLAYNL(count+strings.LENGTH(left)).',
                         [(a+"|"+b, b.count(ch)+len(a)) for a, b in field_pairs],
                         ["split_fields", "right_substring_count", "left_length_sum"])
                    emit(rows, refs, tests, cap, split, "field_processing", "longer_field_tag", k,
                         f"Read left|right text fields. Print '{ch}:' followed by the longer field; choose right on a tie.",
                         split_sentences(["left", "right"])+f'IF (strings.LENGTH(left)>strings.LENGTH(right)) {{ DISPLAYNL(strings.CONCAT("{ch}:",left)). }} ELSE {{ DISPLAYNL(strings.CONCAT("{ch}:",right)). }}',
                         [(a+"|"+b, ch+":"+(a if len(a)>len(b) else b)) for a, b in field_pairs],
                         ["split_fields", "length_branch", "selected_field"])
                else:
                    emit(rows, refs, tests, cap, split, "string_transform", "reverse_lower_suffix", k,
                         f"Read text. Reverse it, lowercase the reversed text, then append '{ch}'.",
                         f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.CONCAT(strings.LOWER(strings.REVERSE(text)),"{ch}")).',
                         [(s, s[::-1].lower()+ch) for s in TEXTS],
                         ["reverse", "lowercase", "suffix"])
                    emit(rows, refs, tests, cap, split, "string_transform", "replace_upper_prefix", k,
                         f"Read text. Replace every '{ch}' with '?', uppercase the result, then prefix '{ch}:'.",
                         f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.CONCAT("{ch}:",strings.UPPER(strings.REPLACE(text,"{ch}","?")))).',
                         [(s, ch+":"+s.replace(ch, "?").upper()) for s in (*TEXTS[:-1], ch+ch+"Z")],
                         ["replace", "uppercase", "prefix"])
                    emit(rows, refs, tests, cap, split, "field_processing", "select_reversed_field", k,
                         f"Read left|right text fields. Reverse the longer field, choosing right on a tie, then append '{ch}'.",
                         split_sentences(["left", "right"])+f'IF (strings.LENGTH(left)>strings.LENGTH(right)) {{ DISPLAYNL(strings.CONCAT(strings.REVERSE(left),"{ch}")). }} ELSE {{ DISPLAYNL(strings.CONCAT(strings.REVERSE(right),"{ch}")). }}',
                         [(a+"|"+b, (a if len(a)>len(b) else b)[::-1]+ch) for a, b in field_pairs],
                         ["split_fields", "length_branch", "reverse_selected"])
                    emit(rows, refs, tests, cap, split, "field_processing", "combined_field_length", k,
                         f"Read left|right text fields. Print the sum of their lengths plus {k}.",
                         split_sentences(["left", "right"])+f'DISPLAYNL(strings.LENGTH(left)+strings.LENGTH(right)+{k}).',
                         [(a+"|"+b, len(a)+len(b)+k) for a, b in field_pairs],
                         ["split_fields", "length_sum", "offset"])
            result[(cap, split)] = (rows, refs, tests)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("data/phase3c"))
    parser.add_argument("--benchmark-dir", type=Path, default=Path("benchmark/phase3c"))
    args = parser.parse_args()
    for (cap, split), (rows, refs, tests) in build().items():
        output = args.data_dir if split == "training" else args.benchmark_dir
        output.mkdir(parents=True, exist_ok=True)
        stem = f"{cap.lower()}_{split}"
        (output / f"{stem}_{'examples' if split == 'training' else 'tasks'}.json").write_text(
            json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        (output / f"{stem}_hidden_tests.json").write_text(json.dumps(tests, indent=2) + "\n", encoding="utf-8")
        if split == "eval":
            (output / f"{stem}_references.json").write_text(json.dumps(refs, indent=2) + "\n", encoding="utf-8")
        print(cap, split, len(rows))


if __name__ == "__main__":
    main()
