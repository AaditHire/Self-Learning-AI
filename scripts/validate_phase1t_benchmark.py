from __future__ import annotations

import argparse
import difflib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from self_learning_ai.benchmark import canonical_sha256, load_json, score_source
from self_learning_ai.compiler import GocoCompiler


def prompt_tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def code_tokens(text: str) -> list[str]:
    text = re.sub(r'"(?:\\.|[^"\\])*"', " STR ", text)
    text = re.sub(r"'(?:\\.|[^'\\])*'", " CHR ", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\b", " NUM ", text)
    text = re.sub(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", " ID ", text)
    return re.findall(r"ID|STR|CHR|NUM|==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|%=|[{}()[\].,+*/%<>=-]", text)


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def pairs(rows: list[dict[str, Any]], values: list[Any], metric: Callable[[Any, Any], float], threshold: float) -> list[dict[str, Any]]:
    found = []
    for i, left in enumerate(rows):
        for j in range(i + 1, len(rows)):
            score = float(metric(values[i], values[j]))
            if score >= threshold:
                found.append({
                    "similarity": score,
                    "left": left["task_id"],
                    "right": rows[j]["task_id"],
                    "same_family": left["family"] == rows[j]["family"],
                })
    return sorted(found, key=lambda row: (-row["similarity"], row["left"], row["right"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--tests", type=Path, required=True)
    parser.add_argument("--references", type=Path, required=True)
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--jar", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--similarity-review-threshold", type=float, default=0.9)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    task_rows = load_json(args.tasks)
    hidden = load_json(args.tests)
    references = load_json(args.references)
    ids = [row["task_id"] for row in task_rows]
    if len(task_rows) != 64 or len(set(ids)) != 64:
        raise ValueError("Phase 1T requires 64 unique tasks")
    if set(ids) != set(hidden) or set(ids) != set(references):
        raise ValueError("Task, test, and reference IDs differ")
    if Counter(row["family"] for row in task_rows) != Counter({family: 8 for family in {
        "expressions_variables", "conditionals", "loops", "functions", "arrays", "strings", "input_output", "composition_algorithms"
    }}):
        raise ValueError("Family balance is not 8 tasks per family")
    if any(row["split"] != "phase1t_confirmation" or row["level"] != "full_synthesis" for row in task_rows):
        raise ValueError("Unexpected split or level")
    if any(len(hidden[task_id]) < 5 for task_id in ids):
        raise ValueError("Every task requires at least five hidden cases")
    for field in ("algorithmic_structure", "template_lineage", "structural_signature"):
        if len({row[field] for row in task_rows}) != len(task_rows):
            raise ValueError(f"{field} values are not unique")

    compiler = GocoCompiler(args.java, args.jar)
    records = [
        score_source(compiler, row, hidden[row["task_id"]], references[row["task_id"]]).as_dict()
        for row in task_rows
    ]
    prompt_sets = [prompt_tokens(row["prompt"]) for row in task_rows]
    normalized_sources = [code_tokens(references[row["task_id"]]) for row in task_rows]
    prompt_pairs = pairs(task_rows, prompt_sets, jaccard, args.similarity_review_threshold)
    reference_pairs = pairs(
        task_rows, normalized_sources,
        lambda a, b: difflib.SequenceMatcher(None, a, b).ratio(),
        args.similarity_review_threshold,
    )
    duplicate_prompts = len(task_rows) - len({row["prompt"].casefold().strip() for row in task_rows})
    result = {
        "task_count": len(task_rows),
        "hidden_case_count": sum(len(cases) for cases in hidden.values()),
        "minimum_cases_per_task": min(len(hidden[task_id]) for task_id in ids),
        "family_counts": dict(sorted(Counter(row["family"] for row in task_rows).items())),
        "exact_duplicate_prompts": duplicate_prompts,
        "unique_algorithmic_structures": len({row["algorithmic_structure"] for row in task_rows}),
        "unique_control_flow_labels": len({row["control_flow"] for row in task_rows}),
        "unique_template_lineages": len({row["template_lineage"] for row in task_rows}),
        "unique_structural_signatures": len({row["structural_signature"] for row in task_rows}),
        "similarity_review_threshold": args.similarity_review_threshold,
        "prompt_pairs_flagged_for_manual_review": prompt_pairs,
        "reference_pairs_flagged_for_manual_review": reference_pairs,
        "maximum_prompt_token_jaccard": prompt_pairs[0] if prompt_pairs else max(
            pairs(task_rows, prompt_sets, jaccard, 0.0), key=lambda row: row["similarity"]
        ),
        "maximum_normalized_reference_sequence_similarity": reference_pairs[0] if reference_pairs else max(
            pairs(task_rows, normalized_sources, lambda a, b: difflib.SequenceMatcher(None, a, b).ratio(), 0.0),
            key=lambda row: row["similarity"],
        ),
        "manual_review_required": bool(prompt_pairs or reference_pairs),
        "canonical_hashes": {
            "tasks": canonical_sha256(task_rows),
            "hidden_tests": canonical_sha256(hidden),
            "references": canonical_sha256(references),
        },
        "reference_failures": [row for row in records if not row["hidden_pass"]],
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "records"}, indent=2))
    if result["reference_failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
