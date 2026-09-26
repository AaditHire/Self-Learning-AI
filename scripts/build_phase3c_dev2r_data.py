"""Deterministically construct fresh DEV2R development tasks from frozen primitives only."""
from __future__ import annotations

import json
import re
from pathlib import Path

from build_phase2b_data import ast_proxy, case
from build_phase3c_dev2_data import PREDICATES, ARRAY_PREFIX

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark/phase3c_dev2r"
NUMBERS = (0, 2, 7, 11, 19)
ARRAYS = ((0, 0, 0, 0), (-7, 4, -3, 8), (5, -6, 2, -1), (1, 9, -5, -2), (-4, -8, 7, 3))


def build():
    tasks, refs, tests = [], {}, {}
    for family, definitions in PREDICATES.items():
        keys = list(definitions)
        numeric = family == "numeric_iteration"
        prefix = "NUMBER n.\nINPUT(n).\n" if numeric else ARRAY_PREFIX
        start, end = ("1", "n") if numeric else ("0", "3")
        contexts = [(str(n), n, None) for n in NUMBERS] if numeric else [("|".join(map(str, xs)), 0, xs) for xs in ARRAYS]
        indices = lambda n: range(1, n + 1) if numeric else range(4)

        def add(group, archetype, variant, primitives, signature, prompt, source, answer, control):
            tid = f"P3CDEV2R-{family[:2].upper()}-{group.upper()}-{archetype.upper()}-{variant:02d}"
            source = (prefix + source).strip()
            tasks.append({"task_id": tid, "split": "phase3c_dev2r_development", "family": family,
                          "capability": "A", "development_group": group, "archetype": archetype,
                          "prompt": prompt, "semantic_primitives": primitives,
                          "composition_signature": signature, "control_flow": control,
                          "ast_proxy_signature": ast_proxy(source), "required_regex": [],
                          "api_requirements": ["INPUT", "DISPLAYNL", "IF", "LOOP"] +
                          ([] if numeric else ["IMPORT strings", "strings.SPLIT", "strings.TO_NUMBER", "array_index"])})
            refs[tid] = source
            tests[tid] = [case(j, stdin, answer(n, xs)) for j, (stdin, n, xs) in enumerate(contexts, 1)]

        for p in keys:
            expr, fn, description = definitions[p]
            for variant, first in enumerate((True, False), 1):
                body = (f"IF (found<0) {{ IF ({expr}) {{ found=i. }} }}" if first
                        else f"IF ({expr}) {{ found=i. }}")
                source = ("NUMBER found=-1.\n" +
                          f"LOOP (NUMBER i={start} TILL i<={end}, i++) {{ {body} }}\n" +
                          "DISPLAYNL(found).")
                def answer(n, xs, fn=fn, first=first):
                    hits = [i for i in indices(n) if fn(i, n, xs)]
                    return (hits[0] if first else hits[-1]) if hits else -1
                prompt = (f"Read {'nonnegative n' if numeric else 'four pipe-separated numbers'}. "
                          f"Print the {'first' if first else 'last'} {'positive index through n' if numeric else 'zero-based position'} "
                          f"that is {description}; print -1 when there is no match.")
                add("primitive_sanity", f"{'first' if first else 'last'}_{p}", variant,
                    [p], f"{'first' if first else 'last'}_index({p})", prompt, source, answer, "scan_store_index")

        pairs = ((keys[0], keys[1], keys[2], keys[3]), (keys[0], keys[2], keys[1], keys[3]))
        for pair_index, (a, b, c, d) in enumerate(pairs, 1):
            A, B, C, D = (definitions[x][0] for x in (a, b, c, d))
            for variant in range(1, 5):
                # Union counts one item even when both intersections hold.
                union_body = (f"IF ({A}) {{ IF ({B}) {{ hit=1. }} }} "
                              f"IF ({C}) {{ IF ({D}) {{ hit=1. }} }} "
                              "IF (hit==1) { count+=1. }")
                source = (f"NUMBER count={variant}.\n"
                          f"LOOP (NUMBER i={start} TILL i<={end}, i++) {{ NUMBER hit=0. {union_body} }}\n"
                          "DISPLAYNL(count).")
                def answer(n, xs, a=a, b=b, c=c, d=d, k=variant):
                    return k + sum(int((definitions[a][1](i,n,xs) and definitions[b][1](i,n,xs)) or
                                       (definitions[c][1](i,n,xs) and definitions[d][1](i,n,xs))) for i in indices(n))
                prompt = (f"Read {'nonnegative n' if numeric else 'four pipe-separated numbers'}. "
                          f"Count each item once if it satisfies both {definitions[a][2]} and {definitions[b][2]}, "
                          f"or both {definitions[c][2]} and {definitions[d][2]}. Add {variant}.")
                add("novel_composition", f"union_pairs{pair_index}", variant, [a,b,c,d],
                    f"union(intersect({a},{b}),intersect({c},{d}))+{variant}", prompt,
                    source, answer, "one_pass_union_flag")

        for pair_index, (a, b) in enumerate(((keys[0],keys[1]), (keys[2],keys[3])), 1):
            A, B = definitions[a][0], definitions[b][0]
            for variant in range(1, 5):
                first = pair_index == 1
                find = f"IF (anchor<0) {{ IF ({A}) {{ anchor=i. }} }}" if first else f"IF ({A}) {{ anchor=i. }}"
                relation = "j>anchor" if first else "j<=anchor"
                second_expr = re.sub(r"\bi\b", "j", B)
                source = (f"NUMBER anchor=-1.\nNUMBER count={variant}.\n"
                          f"LOOP (NUMBER i={start} TILL i<={end}, i++) {{ {find} }}\n"
                          f"LOOP (NUMBER j={start} TILL j<={end}, j++) {{ IF (anchor>=0) {{ IF ({relation}) {{ IF ({second_expr}) {{ count+=1. }} }} }} }}\n"
                          "DISPLAYNL(count).")
                def answer(n, xs, a=a, b=b, first=first, k=variant):
                    hits = [i for i in indices(n) if definitions[a][1](i,n,xs)]
                    if not hits: return k
                    anchor = hits[0] if first else hits[-1]
                    return k + sum(int(definitions[b][1](i,n,xs)) for i in indices(n)
                                   if (i > anchor if first else i <= anchor))
                prompt = (f"Read {'nonnegative n' if numeric else 'four pipe-separated numbers'}. "
                          f"Find the {'first' if first else 'last'} position that is {definitions[a][2]}. "
                          f"In a separate traversal count positions {'strictly after' if first else 'through'} it "
                          f"that are {definitions[b][2]}; if no anchor exists count zero. Add {variant}.")
                add("structural_transfer", f"anchored_{'suffix' if first else 'prefix'}{pair_index}",
                    variant, [a,b], f"{'suffix_after_first' if first else 'prefix_through_last'}({a},{b})+{variant}",
                    prompt, source, answer, "two_pass_dependent_anchor")
    return tasks, refs, tests


if __name__ == "__main__":
    tasks, refs, tests = build()
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in (("a_development_eval_tasks.json", tasks),
                        ("a_development_eval_references.json", refs),
                        ("a_development_eval_hidden_tests.json", tests)):
        (OUT / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(len(tasks), sum(map(len, tests.values())))
