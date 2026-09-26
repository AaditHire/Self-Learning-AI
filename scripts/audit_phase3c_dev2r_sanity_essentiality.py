"""Read-only task-essential coverage audit of frozen DEV2R Primitive Sanity."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/results/PHASE_3C_DEV2R_AMENDMENT/primitive_sanity_original_essentiality.json"


def read(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha(relative: str):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    manifest = read("research/protocols/phase3c_dev2r_manifest.json")
    paths = [f"benchmark/phase3c_dev2r/a_development_eval_{suffix}.json"
             for suffix in ("tasks", "references", "hidden_tests")]
    paths += [f"data/phase3c_dev2/a_{condition}_training_{suffix}.json"
              for condition in ("isolated", "composition")
              for suffix in ("examples", "references", "hidden_tests")]
    if any(sha(path) != manifest["input_sha256"][path] for path in paths):
        raise ValueError("Frozen input changed")
    tasks, refs, tests = (read(path) for path in paths[:3])
    old_coverage = read("research/results/PHASE_3C_DEV2R_PREEXEC_STOP/api_construct_coverage.json")
    coverage_by_id = {row["task_id"]: row for row in old_coverage["tasks"]}
    training = {}
    for condition in ("isolated", "composition"):
        prefix = f"data/phase3c_dev2/a_{condition}_training"
        training[condition] = {
            "examples": read(prefix + "_examples.json"),
            "references": read(prefix + "_references.json"),
            "tests": read(prefix + "_hidden_tests.json"),
        }
    rows = []
    for task in tasks:
        if task["development_group"] != "primitive_sanity":
            continue
        tid = task["task_id"]
        if len(task["semantic_primitives"]) != 1 or "print -1 when there is no match" not in task["prompt"].lower():
            raise ValueError(f"Unexpected original Primitive Sanity specification: {tid}")
        if "=-1." not in refs[tid]:
            raise ValueError(f"Missing expected canonical sentinel: {tid}")
        negative_case_count = sum(float(case["expected_stdout"]) < 0 for case in tests[tid])
        conditions = {}
        for condition, data in training.items():
            primitive = task["semantic_primitives"][0]
            same_family = [row for row in data["examples"] if row["family"] == task["family"]]
            primitive_ids = [row["example_id"] for row in same_family
                             if primitive in row["semantic_primitives"]]
            negative_output_ids = [eid for eid, cases in data["tests"].items()
                                   if any(float(case["expected_stdout"]) < 0 for case in cases)]
            negative_literal_ids = [eid for eid, source in data["references"].items()
                                    if re.search(r"(?<![A-Za-z0-9_])-\d+\b", source)]
            frozen_api = coverage_by_id[tid]["conditions"][condition]["constructs"]
            required_apis = task["api_requirements"]
            missing_apis = [api for api in required_apis if not frozen_api[api]["represented_in_training"]]
            conditions[condition] = {
                "required_primitive_examples": len(primitive_ids),
                "required_primitive_example_ids": primitive_ids,
                "missing_required_apis": missing_apis,
                "training_negative_output_example_ids": negative_output_ids,
                "training_negative_literal_reference_ids": negative_literal_ids,
                "negative_output_capability_covered": bool(negative_output_ids),
            }
        rows.append({
            "task_id": tid, "family": task["family"], "archetype": task["archetype"],
            "required_semantic_primitive": task["semantic_primitives"][0],
            "required_apis_language_constructs": task["api_requirements"],
            "task_specification_requires_minus_one_output_if_no_match": True,
            "frozen_semantic_cases_with_negative_output": negative_case_count,
            "canonical_reference_uses_minus_one_sentinel": True,
            "reference_only_construct_gap": "negative_integer_literal syntax can be avoided by a computed negative value; the output requirement cannot be avoided without changing the task",
            "task_essential_value_capability": "emit negative numeric value -1 when no match",
            "negative_input_behavior": "Array predicates may inspect negative entries, which original same-family training already covers" if task["family"] == "array_reduction" else "numeric input is nonnegative",
            "unary_negation_distinction": "The compiler may parse -1 as a signed literal or unary minus; neither spelling is the essential finding. Negative output is required by the task specification.",
            "conditions": conditions,
            "classification": "TASK_ESSENTIAL",
            "coverage_pass": False,
            "justification": "The prompt itself requires -1 on no match. Both original training conditions contain this predicate and the required APIs, but their target/reference programs and frozen training semantic outputs never produce a negative result. A sentinel-free implementation would still have to produce -1 as an output.",
        })
    if len(rows) != 16:
        raise ValueError("Expected 16 Primitive Sanity tasks")
    if any(row["conditions"][c]["missing_required_apis"] or
           row["conditions"][c]["required_primitive_examples"] == 0 or
           row["conditions"][c]["negative_output_capability_covered"]
           for row in rows for c in training):
        raise ValueError("Unexpected training coverage")
    output = {"status": "FAIL_ORIGINAL_PRIMITIVE_SANITY_TASK_ESSENTIAL_COVERAGE",
              "frozen_design_commit": "cdff638153df13c5da2d77b4eda908385c1a6423",
              "input_sha256": {path: sha(path) for path in paths},
              "tasks": 16, "task_essential_coverage_pass": 0,
              "negative_output_requirement_count": 16,
              "cases_with_negative_output": sum(row["frozen_semantic_cases_with_negative_output"] for row in rows),
              "rows": rows}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"task_essential_coverage_pass": 0, "tasks": 16,
                      "cases_with_negative_output": output["cases_with_negative_output"]}))


if __name__ == "__main__":
    main()
