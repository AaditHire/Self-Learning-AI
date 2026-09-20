from __future__ import annotations

import argparse
import difflib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from self_learning_ai.benchmark import canonical_sha256, load_json, score_source
from self_learning_ai.compiler import GocoCompiler


def lexical_tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def normalized_code_tokens(text: str) -> list[str]:
    text = re.sub(r'"(?:\\.|[^"\\])*"', ' STR ', text)
    text = re.sub(r"'(?:\\.|[^'\\])*'", " CHR ", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\b", " NUM ", text)
    text = re.sub(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", " ID ", text)
    return re.findall(r"ID|STR|CHR|NUM|==|!=|<=|>=|\+\+|--|[{}()[\].,+*/%<>=-]", text)


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def maximum_pair(rows: list[dict[str, Any]], values: list[Any], similarity: Any) -> dict[str, Any]:
    best = (0.0, "", "")
    for i, left in enumerate(rows):
        for j in range(i + 1, len(rows)):
            score = float(similarity(values[i], values[j]))
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
        raise FileExistsError(args.output)

    tasks = load_json(args.tasks)
    hidden = load_json(args.tests)
    references = load_json(args.references)
    ids = [row["task_id"] for row in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate task IDs")
    executable = [row for row in tasks if row["level"] != "recognition"]
    executable_ids = {row["task_id"] for row in executable}
    if executable_ids != set(hidden) or executable_ids != set(references):
        raise ValueError("Executable task/test/reference IDs differ")
    if len({row["template_lineage"] for row in tasks}) != len(tasks):
        raise ValueError("Template lineages are not unique")
    if len({row["structural_signature"] for row in tasks}) != len(tasks):
        raise ValueError("Structural signatures are not unique")

    compiler = GocoCompiler(args.java, args.jar)
    records = []
    full_sources: dict[str, str] = {}
    for task in executable:
        task_id = task["task_id"]
        if task["level"] == "local_completion":
            source = task["scaffold_prefix"] + references[task_id] + task["scaffold_suffix"]
        else:
            source = references[task_id]
        full_sources[task_id] = source
        records.append(score_source(compiler, task, hidden[task_id], source).as_dict())

    by_level: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in tasks:
        by_level[row["level"]].append(row)
    diversity = {}
    for level, rows in sorted(by_level.items()):
        prompts = [lexical_tokens(row["prompt"]) for row in rows]
        entry: dict[str, Any] = {
            "n": len(rows),
            "max_prompt_token_jaccard": maximum_pair(rows, prompts, jaccard),
            "unique_lineages": len({row["template_lineage"] for row in rows}),
            "unique_structural_signatures": len({row["structural_signature"] for row in rows}),
            "control_flow_distribution": dict(sorted(Counter(row["control_flow"] for row in rows).items())),
        }
        if level != "recognition":
            codes = [normalized_code_tokens(full_sources[row["task_id"]]) for row in rows]
            entry["max_normalized_reference_sequence_similarity"] = maximum_pair(
                rows, codes, lambda a, b: difflib.SequenceMatcher(None, a, b).ratio()
            )
        diversity[level] = entry

    result = {
        "task_count": len(tasks),
        "executable_task_count": len(executable),
        "recognition_task_count": len(tasks) - len(executable),
        "hidden_case_count": sum(len(rows) for rows in hidden.values()),
        "level_counts": dict(sorted(Counter(row["level"] for row in tasks).items())),
        "family_counts": dict(sorted(Counter(row["family"] for row in tasks).items())),
        "family_by_level": {
            level: dict(sorted(Counter(row["family"] for row in rows).items()))
            for level, rows in sorted(by_level.items())
        },
        "reference_failures": [row for row in records if not row["hidden_pass"]],
        "exact_duplicate_prompts": len(tasks) - len({row["prompt"].casefold().strip() for row in tasks}),
        "unique_template_lineages": len({row["template_lineage"] for row in tasks}),
        "unique_structural_signatures": len({row["structural_signature"] for row in tasks}),
        "matched_scenario_design": "Each of 24 scenario lineages has one local-completion, one modification, and one full-synthesis item; recognition uses separate syntax lineages.",
        "diversity_by_level": diversity,
        "canonical_hashes": {
            "tasks": canonical_sha256(tasks),
            "hidden_tests": canonical_sha256(hidden),
            "references": canonical_sha256(references),
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
