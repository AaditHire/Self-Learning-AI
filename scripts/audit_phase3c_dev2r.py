"""Freeze DEV2R structural/leakage and reference audits; no model inference."""
from __future__ import annotations

import difflib
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from self_learning_ai.benchmark import score_source
from self_learning_ai.compiler import GocoCompiler
from validate_phase2b_data import jaccard, normalized_code
from build_phase3c_dev2_data import PREDICATES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/results/PHASE_3C_DEV2R"
HISTORY = ("benchmark/phase3a/a_eval", "benchmark/phase3b/a_eval",
           "benchmark/phase3c/a_eval", "benchmark/phase3c_dev1/a_development_eval",
           "benchmark/phase3c_dev2/a_development_eval")


def read(path): return json.loads((ROOT / path).read_text(encoding="utf-8"))
def sha(path): return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
def write(path, value):
    if path.exists(): raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main():
    stem = "benchmark/phase3c_dev2r/a_development_eval"
    paths = [stem + suffix + ".json" for suffix in ("_tasks", "_references", "_hidden_tests")]
    tasks, refs, tests = map(read, paths)
    assert len(tasks) == len(refs) == len(tests) == 48
    assert len({t["task_id"] for t in tasks}) == 48
    assert Counter(t["development_group"] for t in tasks) == {"primitive_sanity": 16,
               "novel_composition": 16, "structural_transfer": 16}
    assert Counter(t["family"] for t in tasks) == {"numeric_iteration": 24, "array_reduction": 24}
    assert all(len(tests[t["task_id"]]) == 5 for t in tasks)
    train = {}
    for condition in ("isolated", "composition"):
        prefix = f"data/phase3c_dev2/a_{condition}_training"
        train[condition] = (read(prefix + "_examples.json"), read(prefix + "_references.json"))
    historical_prompts, historical_refs = set(), set()
    for prefix in HISTORY:
        historical_prompts.update(t["prompt"] for t in read(prefix + "_tasks.json"))
        historical_refs.update(read(prefix + "_references.json").values())
    assert not any(t["prompt"] in historical_prompts or refs[t["task_id"]] in historical_refs for t in tasks)
    pairs, nearest = [], []
    for task in tasks:
        tid, family = task["task_id"], task["family"]
        primitives = task["semantic_primitives"]
        assert set(primitives) <= set(PREDICATES[family])
        record = {"task_id": tid, "group": task["development_group"], "family": family,
                  "semantic_primitives": primitives, "composition_signature": task["composition_signature"],
                  "api_requirements": task["api_requirements"], "conditions": {}}
        for condition, (rows, training_refs) in train.items():
            covered = {p for row in rows if row["family"] == family for p in row["semantic_primitives"]}
            missing = sorted(set(primitives) - covered)
            signatures = {row["composition_signature"] for row in rows}
            assert not missing
            if task["development_group"] == "novel_composition":
                assert task["composition_signature"] not in signatures
            local = []
            for row in rows:
                train_source = training_refs[row["example_id"]]
                comparison = {"task_id": tid, "condition": condition, "train_id": row["example_id"],
                              "train_archetype": row["archetype"],
                              "exact_prompt": task["prompt"] == row["prompt"],
                              "exact_reference": refs[tid] == train_source,
                              "prompt_jaccard": jaccard(task["prompt"], row["prompt"]),
                              "normalized_reference_code_similarity": difflib.SequenceMatcher(
                                  None, normalized_code(refs[tid]), normalized_code(train_source)).ratio(),
                              "ast_proxy_exact": task["ast_proxy_signature"] == row["ast_proxy_signature"]}
                assert not comparison["exact_prompt"] and not comparison["exact_reference"]
                local.append(comparison)
            pairs.extend(local)
            best_code = max(local, key=lambda x: (x["normalized_reference_code_similarity"], x["train_id"]))
            best_prompt = max(local, key=lambda x: (x["prompt_jaccard"], x["train_id"]))
            record["conditions"][condition] = {
                "missing_primitives": missing,
                "primitive_examples_containing": {p: sum(p in row["semantic_primitives"] for row in rows) for p in primitives},
                "exact_composition_in_training": task["composition_signature"] in signatures,
                "nearest_code_id": best_code["train_id"],
                "nearest_code_similarity": best_code["normalized_reference_code_similarity"],
                "nearest_prompt_id": best_prompt["train_id"],
                "nearest_prompt_jaccard": best_prompt["prompt_jaccard"],
                "ast_proxy_exact_pairs": sum(x["ast_proxy_exact"] for x in local),
                "code_pairs_at_least": {str(threshold): sum(x["normalized_reference_code_similarity"] >= threshold
                                                          for x in local) for threshold in (.5, .7, .85, .95, .98)}}
        nearest.append(record)
    assert len(pairs) == 48 * 60 * 2
    config = read("research/protocols/phase3c_dev2_config.json")
    compiler_path = config["compiler"]["path"]
    assert sha(compiler_path) == config["compiler"]["sha256"]
    compiler = GocoCompiler(ROOT / config["compiler"]["java"], ROOT / compiler_path,
                            timeout_seconds=3, output_limit_bytes=65536)
    validation = []
    for task in tasks:
        tid = task["task_id"]
        score = score_source(compiler, {**task, "difficulty": "dev2r_reference_validation"},
                             tests[tid], refs[tid]).as_dict()
        validation.append({"task_id": tid, "hidden_pass": score["hidden_pass"],
                           "cases_passed": score["cases_passed"], "cases_total": score["cases_total"],
                           "error_phase": score["error_phase"],
                           "case_results": score["case_results"]})
        if not score["hidden_pass"]: raise ValueError(f"Reference failed: {tid}: {score['error_phase']}")
    write(OUT / "structural_pairs.json", pairs)
    write(OUT / "structural_audit.json", {"status": "FROZEN_PRE_INFERENCE", "pairs": len(pairs),
          "historical_exact_prompt_or_reference_reuse": 0, "training_exact_prompt_or_reference_reuse": 0,
          "nearest": nearest, "similarity_note": "All pair scores are retained, including below 0.98; metrics are descriptive."})
    write(OUT / "reference_validation.json", {"status": "PASS", "references": 48,
          "semantic_cases": 240, "passed_references": 48, "passed_cases": 240,
          "compiler_sha256": sha(compiler_path), "results": validation})
    print(json.dumps({"tasks": 48, "pairs": len(pairs), "passed_cases": 240}))


if __name__ == "__main__": main()
