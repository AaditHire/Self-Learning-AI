"""Descriptive structural comparisons for consumed Phase 3C EVAL_A outputs.

No generation, compiler execution, optimization, or dataset edits occur here.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from phase3c_contract import ROOT, load_frozen, verify_execution_files
from validate_phase2b_data import jaccard, normalized_code


def read(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    verify_execution_files()
    cfg = load_frozen(check_base=False)
    train = read("data/phase3c/a_training_examples.json")
    evaluation = read("benchmark/phase3c/a_eval_tasks.json")
    references = read("benchmark/phase3c/a_eval_references.json")
    old_audit = read("research/results/EXP-0048/data_validation.json")["structural_audit"]["a"]
    old_by_id = {x["task_id"]: x for x in old_audit["distance_records"]}
    records = {seed: {x["task_id"]: x for x in read(
        f"research/artifacts/phase3c/raw/evaluations/{seed}/A_a.json")["records"]}
        for seed in cfg["seeds"]}
    if (len(train) != 60 or len(evaluation) != 32 or set(references) != {x["task_id"] for x in evaluation}
            or set(old_by_id) != set(references)
            or any(set(seed_records) != set(references) for seed_records in records.values())):
        raise ValueError("Frozen A task/record sets differ")
    train_code = {x["example_id"]: normalized_code(x["target"]) for x in train}
    output_rows = []
    for task in evaluation:
        tid = task["task_id"]
        old = old_by_id[tid]
        nearest_prompt = next(x for x in train if x["example_id"] == old["nearest_train_prompt_id"])
        nearest_code = next(x for x in train if x["example_id"] == old["nearest_train_code_id"])
        reference_normalized = normalized_code(references[tid])
        if (abs(jaccard(task["prompt"], nearest_prompt["prompt"]) - old["train_prompt_jaccard"]) > 1e-12
                or abs(difflib.SequenceMatcher(None, reference_normalized,
                                               train_code[nearest_code["example_id"]]).ratio()
                       - old["train_code_similarity"]) > 1e-12):
            raise ValueError(f"Existing structural audit mismatch: {tid}")
        per_seed = {}
        for seed, by_id in records.items():
            observation = by_id[tid]
            generated = normalized_code(observation["normalized_output"])
            similar = max(train, key=lambda x: difflib.SequenceMatcher(
                None, generated, train_code[x["example_id"]]).ratio())
            per_seed[str(seed)] = {
                "hidden_pass": observation["hidden_pass"],
                "failure_category": observation["failure_category"],
                "generated_nearest_training_id": similar["example_id"],
                "generated_nearest_training_archetype": similar["archetype"],
                "generated_nearest_training_code_similarity": difflib.SequenceMatcher(
                    None, generated, train_code[similar["example_id"]]).ratio(),
            }
        output_rows.append({
            "task_id": tid, "family": task["family"], "archetype": task["archetype"],
            "eval_prompt": task["prompt"], "eval_semantic_operations": task["semantic_operations"],
            "eval_ast_proxy_signature": task["ast_proxy_signature"],
            "eval_reference_normalized": reference_normalized,
            "nearest_train_prompt_id": nearest_prompt["example_id"],
            "nearest_train_prompt": nearest_prompt["prompt"],
            "train_prompt_jaccard": old["train_prompt_jaccard"],
            "nearest_train_code_id": nearest_code["example_id"],
            "nearest_train_code_archetype": nearest_code["archetype"],
            "nearest_train_code_normalized": train_code[nearest_code["example_id"]],
            "nearest_train_code_semantic_operations": nearest_code["semantic_operations"],
            "nearest_train_code_ast_proxy_signature": nearest_code["ast_proxy_signature"],
            "train_code_similarity": old["train_code_similarity"],
            "train_ast_proxy_exact": old["train_ast_proxy_exact"],
            "semantic_operation_overlap": sorted(set(task["semantic_operations"])
                                                 & set(nearest_code["semantic_operations"])),
            "prior_code_similarity": old["prior_code_similarity"],
            "per_seed": per_seed,
        })
    result = {"phase": "3C-DIAG", "status": "POST_HOC_DESCRIPTIVE_STRUCTURAL_AUDIT",
              "source": "frozen pre-model overlap audit, A manifests/references, and existing pre-B outcomes",
              "interpretation": "String similarity, prompt Jaccard, and coarse AST proxies are descriptive; they do not explain causal transfer.",
              "records": output_rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "tasks": len(output_rows),
                      "triangular": sum(x["archetype"] == "triangular_milestones" for x in output_rows)}))


if __name__ == "__main__":
    main()
