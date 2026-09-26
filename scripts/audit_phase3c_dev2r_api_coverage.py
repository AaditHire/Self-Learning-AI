"""Audit frozen DEV2R reference constructs against both frozen DEV2 training sets.

This is read-only with respect to scientific inputs and performs no model work.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/results/PHASE_3C_DEV2R_PREEXEC_STOP/api_construct_coverage.json"
FROZEN_DESIGN = "cdff638153df13c5da2d77b4eda908385c1a6423"

# Explicit lexical proxies for every language/API construct in the frozen
# references. Predicate-specific arithmetic/comparisons remain separately
# tracked by their frozen semantic-primitive annotation.
CONSTRUCTS = {
    "IMPORT strings": r"\bIMPORT\s+strings\s*\.",
    "INPUT": r"\bINPUT\s*\(",
    "DISPLAYNL": r"\bDISPLAYNL\s*\(",
    "IF": r"\bIF\s*\(",
    "LOOP": r"\bLOOP\s*\(",
    "TILL": r"\bTILL\b",
    "NUMBER declaration": r"\bNUMBER\s+[A-Za-z_]",
    "NUMBER[] declaration": r"\bNUMBER\s*\[\s*\]\s+[A-Za-z_]",
    "SENTENCE declaration": r"\bSENTENCE\s+[A-Za-z_]",
    "SENTENCE[] declaration": r"\bSENTENCE\s*\[\s*\]\s+[A-Za-z_]",
    "strings.SPLIT": r"\bstrings\.SPLIT\s*\(",
    "strings.TO_NUMBER": r"\bstrings\.TO_NUMBER\s*\(",
    "array_index": r"\b(?:values|parts)\s*\[",
    "array_literal": r"\bvalues\s*=\s*\[",
    "increment": r"\+\+",
    "add_assign": r"\+=",
    "decrement": r"-=",
    "modulo": r"%(?!=)",
    "multiplication": r"(?<![/*])\*(?![/*])",
    "negative_integer_literal": r"(?<![A-Za-z0-9_])-\d+\b",
    "equal_comparison": r"==",
    "less_than": r"(?<![<=>])<(?![=<>])",
    "less_or_equal": r"<=",
    "greater_than": r"(?<![<=>])>(?![=<>])",
    "greater_or_equal": r">=",
}


def read(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha(rel: str):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    manifest = read("research/protocols/phase3c_dev2r_manifest.json")
    tasks_rel = "benchmark/phase3c_dev2r/a_development_eval_tasks.json"
    refs_rel = "benchmark/phase3c_dev2r/a_development_eval_references.json"
    tasks, refs = read(tasks_rel), read(refs_rel)
    training = {}
    for condition in ("isolated", "composition"):
        prefix = f"data/phase3c_dev2/a_{condition}_training"
        training[condition] = (read(prefix + "_examples.json"), read(prefix + "_references.json"))
    if any(sha(p) != manifest["input_sha256"][p] for p in (tasks_rel, refs_rel,
            *(f"data/phase3c_dev2/a_{c}_training_{s}.json" for c in training
              for s in ("examples", "references")))):
        raise ValueError("Frozen input hash mismatch")
    if len(tasks) != 48 or set(refs) != {task["task_id"] for task in tasks}:
        raise ValueError("Frozen suite identity mismatch")
    inventory = {}
    for condition, (examples, train_refs) in training.items():
        by_id = {row["example_id"]: row for row in examples}
        inventory[condition] = {}
        for construct, pattern in CONSTRUCTS.items():
            matches = [(eid, len(re.findall(pattern, code))) for eid, code in train_refs.items()]
            matches = [(eid, count) for eid, count in matches if count]
            inventory[condition][construct] = {
                "reference_occurrences": sum(count for _, count in matches),
                "training_example_ids": sorted(eid for eid, _ in matches),
                "training_archetypes": sorted({by_id[eid]["archetype"] for eid, _ in matches}),
            }
    rows = []
    for task in tasks:
        tid = task["task_id"]
        source = refs[tid]
        required = {name for name, pattern in CONSTRUCTS.items() if re.search(pattern, source)}
        declared = set(task["api_requirements"])
        if not declared <= required:
            raise ValueError(f"Frozen API annotation not present in reference: {tid}: {declared-required}")
        entry = {"task_id": tid, "group": task["development_group"], "family": task["family"],
                 "archetype": task["archetype"], "frozen_api_annotation": sorted(declared),
                 "required_constructs_from_reference": sorted(required),
                 "semantic_primitives": task["semantic_primitives"], "conditions": {}}
        for condition, (examples, _) in training.items():
            construct_evidence = {}
            for construct in sorted(CONSTRUCTS):
                shared = inventory[condition][construct]
                construct_evidence[construct] = {
                    "required_by_evaluation_task": construct in required,
                    "represented_in_training": bool(shared["training_example_ids"]),
                    "reference_occurrences": shared["reference_occurrences"],
                    "training_archetypes": shared["training_archetypes"],
                    "training_example_ids_inventory_ref": [condition, construct],
                }
            covered = {p for row in examples if row["family"] == task["family"]
                       for p in row["semantic_primitives"]}
            missing_primitives = sorted(set(task["semantic_primitives"]) - covered)
            missing_constructs = sorted(name for name, evidence in construct_evidence.items()
                                        if evidence["required_by_evaluation_task"]
                                        and not evidence["represented_in_training"])
            entry["conditions"][condition] = {
                "constructs": construct_evidence, "missing_constructs": missing_constructs,
                "missing_semantic_primitives": missing_primitives,
                "primitive_coverage_pass": not missing_primitives,
                "construct_coverage_pass": not missing_constructs,
            }
        rows.append(entry)
    structural = [r for r in rows if r["group"] == "structural_transfer"]
    primitive_pass = sum(all(r["conditions"][c]["primitive_coverage_pass"]
                             for c in training) for r in structural)
    construct_pass = sum(all(r["conditions"][c]["construct_coverage_pass"]
                             for c in training) for r in structural)
    if len(structural) != 16:
        raise ValueError("Expected 16 Structural Transfer tasks")
    result = {"phase": "3C-DEV2R", "status": "STOP_PREEXECUTION_CONSTRUCT_COVERAGE"
              if construct_pass != 16 else "PASS_PREEXECUTION_CONSTRUCT_COVERAGE",
              "frozen_design_commit": FROZEN_DESIGN,
              "input_sha256": {rel: sha(rel) for rel in (tasks_rel, refs_rel,
                  *(f"data/phase3c_dev2/a_{c}_training_{s}.json" for c in training
                    for s in ("examples", "references")))},
              "method": "Exact regular-expression occurrence scan of frozen reference programs; counts are per source occurrence. Each task/construct row gives its condition and construct key into training_construct_inventory for the full example-ID list.",
              "construct_patterns": CONSTRUCTS,
              "training_construct_inventory": inventory,
              "structural_transfer": {"total": 16, "primitive_coverage_pass": primitive_pass,
                                      "construct_coverage_pass": construct_pass,
                                      "required_pass": 16},
              "tasks": rows}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "structural_primitive_pass": primitive_pass,
                      "structural_construct_pass": construct_pass}))


if __name__ == "__main__":
    main()
