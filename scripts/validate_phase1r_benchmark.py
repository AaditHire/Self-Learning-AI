from __future__ import annotations

import argparse
import difflib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from self_learning_ai.benchmark import canonical_sha256, load_json, score_source
from self_learning_ai.compiler import GocoCompiler


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def normalized_source_sequence(text: str) -> list[str]:
    text = re.sub(r'"(?:\\.|[^"\\])*"', ' STR ', text)
    text = re.sub(r"'(?:\\.|[^'\\])*'", " CHR ", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\b", " NUM ", text)
    text = re.sub(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", " ID ", text)
    return re.findall(r"ID|STR|CHR|NUM|==|!=|<=|>=|\+\+|--|[{}()[\].,+*/%<>=-]", text)


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def max_pair(rows: list[dict[str, Any]], representations: list[set[str]]) -> dict[str, Any]:
    best = (0.0, "", "")
    for i, left in enumerate(rows):
        for j in range(i + 1, len(rows)):
            score = jaccard(representations[i], representations[j])
            if score > best[0]:
                best = (score, left["task_id"], rows[j]["task_id"])
    return {"similarity": best[0], "left": best[1], "right": best[2]}


def max_sequence_pair(rows: list[dict[str, Any]], representations: list[list[str]]) -> dict[str, Any]:
    best = (0.0, "", "")
    for i, left in enumerate(rows):
        for j in range(i + 1, len(rows)):
            score = difflib.SequenceMatcher(None, representations[i], representations[j]).ratio()
            if score > best[0]:
                best = (score, left["task_id"], rows[j]["task_id"])
    return {"similarity": best[0], "left": best[1], "right": best[2]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--tests", type=Path, required=True)
    parser.add_argument("--references", type=Path, required=True)
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--jar", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite result: {args.output}")

    tasks = load_json(args.tasks)
    hidden = load_json(args.tests)
    references = load_json(args.references)
    ids = [task["task_id"] for task in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate task IDs")
    if set(ids) != set(hidden) or set(ids) != set(references):
        raise ValueError("Task, hidden-test, and reference IDs differ")
    if len({task["template_lineage"] for task in tasks}) != len(tasks):
        raise ValueError("Development template lineage must be unique")
    if len({task["structure"] for task in tasks}) != len(tasks):
        raise ValueError("Development task structure must be unique")

    compiler = GocoCompiler(args.java, args.jar)
    records = []
    for task in tasks:
        record = score_source(compiler, task, hidden[task["task_id"]], references[task["task_id"]]).as_dict()
        records.append(record)

    prompt_representations = [tokens(task["prompt"]) for task in tasks]
    reference_representations = [normalized_source_sequence(references[task["task_id"]]) for task in tasks]
    structure_counts = Counter(task["structure"] for task in tasks)
    lineage_counts = Counter(task["template_lineage"] for task in tasks)
    result = {
        "task_count": len(tasks),
        "family_counts": dict(sorted(Counter(task["family"] for task in tasks).items())),
        "hidden_case_count": sum(len(hidden[task_id]) for task_id in ids),
        "reference_failures": [record for record in records if not record["hidden_pass"]],
        "unique_structures": len(structure_counts),
        "unique_template_lineages": len(lineage_counts),
        "exact_duplicate_prompts": len(tasks) - len({task["prompt"].casefold().strip() for task in tasks}),
        "max_prompt_token_jaccard": max_pair(tasks, prompt_representations),
        "max_normalized_reference_sequence_similarity": max_sequence_pair(tasks, reference_representations),
        "canonical_hashes": {
            "tasks": canonical_sha256(tasks),
            "hidden_tests": canonical_sha256(hidden),
            "reference_solutions": canonical_sha256(references),
        },
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "records"}, indent=2))
    if result["reference_failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
