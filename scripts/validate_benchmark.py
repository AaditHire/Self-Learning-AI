from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from self_learning_ai.benchmark import canonical_sha256, load_json, score_source
from self_learning_ai.compiler import GocoCompiler


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / len(left | right) if left | right else 1.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--jar", type=Path, required=True)
    parser.add_argument("--tasks", type=Path, default=Path("benchmark/tasks.json"))
    parser.add_argument("--tests", type=Path, default=Path("benchmark/hidden_tests.json"))
    parser.add_argument(
        "--solutions", type=Path, default=Path("benchmark/reference_solutions.json")
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-final-paper", action="store_true")
    args = parser.parse_args()

    tasks = load_json(args.tasks)
    hidden = load_json(args.tests)
    solutions = load_json(args.solutions)
    ids = [task["task_id"] for task in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate task IDs")
    if set(ids) != set(hidden) or set(ids) != set(solutions):
        raise ValueError("Task, test, and reference-solution IDs differ")

    templates = [task["template_id"] for task in tasks]
    duplicate_templates = sorted(k for k, v in Counter(templates).items() if v > 1)
    if duplicate_templates:
        raise ValueError(f"Template IDs reused across tasks: {duplicate_templates}")

    pairs = []
    for index, left in enumerate(tasks):
        for right in tasks[index + 1 :]:
            if left["split"] == right["split"]:
                continue
            pairs.append(
                {
                    "left": left["task_id"],
                    "right": right["task_id"],
                    "prompt_token_jaccard": jaccard(tokens(left["prompt"]), tokens(right["prompt"])),
                }
            )
    pairs.sort(key=lambda item: item["prompt_token_jaccard"], reverse=True)

    compiler = GocoCompiler(args.java, args.jar)
    validation = []
    for task in tasks:
        if task["split"] == "final_paper" and not args.allow_final_paper:
            validation.append({"task_id": task["task_id"], "status": "SEALED_NOT_RUN"})
            continue
        score = score_source(compiler, task, hidden[task["task_id"]], solutions[task["task_id"]])
        validation.append({"task_id": task["task_id"], "status": "PASS" if score.hidden_pass else "FAIL", "score": score.as_dict()})

    split_counts = Counter(task["split"] for task in tasks)
    family_counts = Counter(task["family"] for task in tasks)
    failures = [item for item in validation if item["status"] == "FAIL"]
    payload = {
        "summary": {
            "task_count": len(tasks),
            "split_counts": dict(sorted(split_counts.items())),
            "family_counts": dict(sorted(family_counts.items())),
            "reference_failures": len(failures),
            "sealed_final_tasks_not_run": sum(item["status"] == "SEALED_NOT_RUN" for item in validation),
            "unique_template_ids": len(set(templates)),
            "exact_duplicate_prompts": len(tasks) - len({task["prompt"] for task in tasks}),
            "maximum_cross_split_prompt_token_jaccard": pairs[0] if pairs else None,
        },
        "hashes": {
            "tasks_canonical_sha256": canonical_sha256(tasks),
            "hidden_tests_canonical_sha256": canonical_sha256(hidden),
            "reference_solutions_canonical_sha256": canonical_sha256(solutions),
        },
        "highest_cross_split_similarities": pairs[:20],
        "validation": validation,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    print(json.dumps(payload["hashes"], indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
