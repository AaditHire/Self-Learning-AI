"""Prospective Primitive Sanity replacement; preserve the frozen v1 suite."""
from __future__ import annotations

import json
from pathlib import Path

from build_phase2b_data import ast_proxy, case
from build_phase3c_dev2_data import PREDICATES, prefix

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark/phase3c_dev2r_v2"
MAP = ROOT / "research/results/PHASE_3C_DEV2R_AMENDMENT/replacement_map.json"


def replace_sanity(task: dict, old_cases: list[dict]) -> tuple[dict, str, list[dict]]:
    family = task["family"]
    primitive = task["semantic_primitives"][0]
    expression, predicate, description = PREDICATES[family][primitive]
    numeric = family == "numeric_iteration"
    variant = 1 if task["archetype"].startswith("first_") else 2
    tid = f"P3CDEV2R2-{family[:2].upper()}-PRIMITIVE_SANITY-COUNT_{primitive.upper()}-{variant:02d}"
    prompt = (f"Read {'nonnegative n' if numeric else 'four pipe-separated numbers'}. "
              f"Determine how many {'positive indices through n' if numeric else 'array positions'} "
              f"satisfy the property {description}. Print that count plus {variant}.")
    loop = (f"LOOP (NUMBER i=1 TILL i<=n, i++) {{ IF ({expression}) {{ matches+=1. }} }}"
            if numeric else
            f"LOOP (NUMBER i=0 TILL i<4, i++) {{ IF ({expression}) {{ matches+=1. }} }}")
    source = prefix(family) + "NUMBER matches=0.\n" + loop + f"\nDISPLAYNL(matches+{variant})."
    row = {"task_id": tid, "split": "phase3c_dev2r_v2_development", "family": family,
           "capability": "A", "development_group": "primitive_sanity",
           "archetype": f"count_{primitive}", "prompt": prompt,
           "semantic_primitives": [primitive], "composition_signature": f"count({primitive})+{variant}",
           "control_flow": "forward_count", "ast_proxy_signature": ast_proxy(source),
           "required_regex": [], "api_requirements": task["api_requirements"]}
    cases = []
    for item in old_cases:
        stdin = item["stdin"]
        if numeric:
            n, values = int(stdin.strip()), None
            indices = range(1, n + 1)
        else:
            values = [int(part) for part in stdin.strip().split("|")]
            if len(values) != 4:
                raise ValueError(f"Unexpected frozen array input: {task['task_id']}")
            n, indices = 0, range(4)
        expected = variant + sum(int(predicate(i, n, values)) for i in indices)
        rebuilt = case(int(item["case_id"].removeprefix("case-")), stdin, expected)
        if rebuilt["stdin"] != stdin or rebuilt["case_id"] != item["case_id"]:
            raise ValueError("Frozen case input/identity changed")
        cases.append(rebuilt)
    return row, source, cases


def build():
    base = ROOT / "benchmark/phase3c_dev2r"
    old_tasks = json.loads((base / "a_development_eval_tasks.json").read_text(encoding="utf-8"))
    old_refs = json.loads((base / "a_development_eval_references.json").read_text(encoding="utf-8"))
    old_tests = json.loads((base / "a_development_eval_hidden_tests.json").read_text(encoding="utf-8"))
    tasks, refs, tests, mapping = [], {}, {}, []
    for task in old_tasks:
        old_id = task["task_id"]
        if task["development_group"] == "primitive_sanity":
            row, source, cases = replace_sanity(task, old_tests[old_id])
            mapping.append({"old_task_id": old_id, "new_task_id": row["task_id"],
                            "reason": "Original task requires a negative -1 output on no match, absent from both original training target/output distributions; replacement tests the same primitive with a nonnegative offset count.",
                            "same_semantic_primitive": task["semantic_primitives"] == row["semantic_primitives"],
                            "same_frozen_case_stdin": [x["stdin"] for x in old_tests[old_id]] == [x["stdin"] for x in cases]})
        else:
            row, source, cases = task, old_refs[old_id], old_tests[old_id]
        tid = row["task_id"]
        tasks.append(row)
        refs[tid] = source
        tests[tid] = cases
    if not (len(tasks) == len(refs) == len(tests)):
        raise ValueError("Suite count mismatch")
    if len(tasks) != 48 or len(mapping) != 16 or len(set(refs)) != 48:
        raise ValueError("Replacement cardinality mismatch")
    return tasks, refs, tests, mapping


def main():
    if (OUT.exists() and any(OUT.iterdir())) or MAP.exists():
        raise FileExistsError("Prospective v2 output already exists")
    tasks, refs, tests, mapping = build()
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, value in (("a_development_eval_tasks.json", tasks),
                            ("a_development_eval_references.json", refs),
                            ("a_development_eval_hidden_tests.json", tests)):
        (OUT / filename).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    MAP.parent.mkdir(parents=True, exist_ok=True)
    MAP.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tasks": len(tasks), "replacements": len(mapping),
                      "cases": sum(map(len, tests.values()))}))


if __name__ == "__main__":
    main()
