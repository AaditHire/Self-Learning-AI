"""Compiler-verify Phase 3C references and audit structural overlap only.

This script never loads a model or any Phase 1 mixed-split sealed-holdout file.
"""

from __future__ import annotations

import argparse
import difflib
import json
from collections import Counter
from pathlib import Path

from self_learning_ai.benchmark import canonical_sha256, load_json, score_source
from self_learning_ai.compiler import GocoCompiler
from validate_phase2b_data import file_sha256, jaccard, normalized_code


PRIOR = (
    ("benchmark/phase1r/development_tasks.json", "benchmark/phase1r/development_reference_solutions.json"),
    ("benchmark/phase1s/diagnostic_tasks.json", "benchmark/phase1s/diagnostic_references.json"),
    ("benchmark/phase1t/confirmation_tasks.json", "benchmark/phase1t/confirmation_references.json"),
    ("benchmark/phase2a/development_tasks.json", "benchmark/phase2a/development_references.json"),
    ("benchmark/phase2b/confirmatory_tasks.json", "benchmark/phase2b/confirmatory_references.json"),
    ("benchmark/phase3a/a_eval_tasks.json", "benchmark/phase3a/a_eval_references.json"),
    ("benchmark/phase3a/b_eval_tasks.json", "benchmark/phase3a/b_eval_references.json"),
    ("benchmark/phase3b/a_eval_tasks.json", "benchmark/phase3b/a_eval_references.json"),
    ("benchmark/phase3b/b_eval_tasks.json", "benchmark/phase3b/b_eval_references.json"),
)


def item_id(row: dict) -> str:
    return row.get("task_id", row.get("example_id"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--jar", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    datasets, inputs = {}, []
    for cap in "ab":
        for split in ("training", "eval"):
            folder = Path("data/phase3c" if split == "training" else "benchmark/phase3c")
            stem = f"{cap}_{split}"
            task_path = folder / f"{stem}_{'examples' if split == 'training' else 'tasks'}.json"
            test_path = folder / f"{stem}_hidden_tests.json"
            ref_path = folder / f"{stem}_references.json" if split == "eval" else None
            rows, tests = load_json(task_path), load_json(test_path)
            refs = load_json(ref_path) if ref_path else {r["example_id"]: r["target"] for r in rows}
            expected, per_family, per_archetype = (60, 30, 15) if split == "training" else (32, 16, 8)
            families = ("numeric_iteration", "array_reduction") if cap == "a" else ("string_transform", "field_processing")
            if len(rows) != expected or len({item_id(r) for r in rows}) != expected:
                raise ValueError((cap, split, "count/unique IDs"))
            if Counter(r["family"] for r in rows) != Counter({family: per_family for family in families}):
                raise ValueError((cap, split, "family balance"))
            if any(count != per_archetype for count in Counter(r["archetype"] for r in rows).values()):
                raise ValueError((cap, split, "archetype balance"))
            if len({r["archetype"] for r in rows}) != 4:
                raise ValueError((cap, split, "archetype count"))
            if set(tests) != {item_id(r) for r in rows} or set(refs) != set(tests):
                raise ValueError((cap, split, "reference/test IDs"))
            if any(len(cases) != 5 for cases in tests.values()):
                raise ValueError((cap, split, "five cases"))
            if any(r["capability"].lower() != cap for r in rows):
                raise ValueError((cap, split, "capability"))
            datasets[(cap, split)] = {"rows": rows, "tests": tests, "refs": refs}
            inputs.extend([task_path, test_path] + ([ref_path] if ref_path else []))
    all_rows = [r for d in datasets.values() for r in d["rows"]]
    if len({item_id(r) for r in all_rows}) != len(all_rows):
        raise ValueError("Global ID collision")

    compiler = GocoCompiler(args.java, args.jar, timeout_seconds=3, output_limit_bytes=65536)
    verification, failures = {}, []
    for (cap, split), data in datasets.items():
        verification[f"{cap}_{split}"] = []
        for row in data["rows"]:
            tid = item_id(row)
            task = row if split == "eval" else {"task_id": tid, "family": row["family"],
                                                 "difficulty": "phase3c_training", "required_regex": []}
            result = score_source(compiler, task, data["tests"][tid], data["refs"][tid]).as_dict()
            verification[f"{cap}_{split}"].append({"item_id": tid, "score": result})
            if not result["hidden_pass"]:
                failures.append({"item_id": tid, "error_phase": result["error_phase"],
                                 "cases_passed": result["cases_passed"], "case_results": result["case_results"]})

    prior_rows, prior_refs = [], []
    for task_path, ref_path in PRIOR:
        rows, refs = load_json(Path(task_path)), load_json(Path(ref_path))
        for row in rows:
            if row.get("level", "full_synthesis") == "full_synthesis" and row["task_id"] in refs:
                prior_rows.append(row)
                prior_refs.append((row["task_id"], normalized_code(refs[row["task_id"]])))
    prior_prompts = {r["prompt"] for r in prior_rows}
    exact_consumed_prompt = [item_id(r) for r in all_rows if r["prompt"] in prior_prompts]
    exact_current_prompt = len({r["prompt"] for r in all_rows}) != len(all_rows)
    prior_code_rejects = []
    for data in datasets.values():
        for row in data["rows"]:
            tid = item_id(row)
            code = normalized_code(data["refs"][tid])
            nearest_id, similarity = max(
                ((pid, difflib.SequenceMatcher(None, code, prior_code).ratio()) for pid, prior_code in prior_refs),
                key=lambda pair: pair[1],
            )
            if similarity >= .98:
                prior_code_rejects.append({"item_id": tid, "prior_item_id": nearest_id, "similarity": similarity})

    audits, split_rejects = {}, []
    for cap in "ab":
        train, evaluation = datasets[(cap, "training")], datasets[(cap, "eval")]
        fields = ("algorithmic_structure", "template_lineage", "structural_signature", "semantic_operations")
        overlap = {field: len({json.dumps(r[field], sort_keys=True) for r in train["rows"]} &
                              {json.dumps(r[field], sort_keys=True) for r in evaluation["rows"]}) for field in fields}
        exact_ref = len(set(train["refs"].values()) & set(evaluation["refs"].values()))
        train_ast = {r["ast_proxy_signature"] for r in train["rows"]}
        distances = []
        for row in evaluation["rows"]:
            tid = item_id(row)
            source = normalized_code(evaluation["refs"][tid])
            prompt_near = max(((t["example_id"], jaccard(row["prompt"], t["prompt"])) for t in train["rows"]),
                              key=lambda pair: pair[1])
            code_near = max(((t["example_id"], difflib.SequenceMatcher(None, source, normalized_code(t["target"])).ratio())
                             for t in train["rows"]), key=lambda pair: pair[1])
            prior_prompt_near = max(((p["task_id"], jaccard(row["prompt"], p["prompt"])) for p in prior_rows),
                                    key=lambda pair: pair[1])
            prior_code_near = max(((pid, difflib.SequenceMatcher(None, source, pcode).ratio()) for pid, pcode in prior_refs),
                                  key=lambda pair: pair[1])
            record = {"task_id": tid, "family": row["family"], "archetype": row["archetype"],
                      "nearest_train_prompt_id": prompt_near[0], "train_prompt_jaccard": prompt_near[1],
                      "nearest_train_code_id": code_near[0], "train_code_similarity": code_near[1],
                      "nearest_prior_prompt_id": prior_prompt_near[0], "prior_prompt_jaccard": prior_prompt_near[1],
                      "nearest_prior_code_id": prior_code_near[0], "prior_code_similarity": prior_code_near[1],
                      "train_ast_proxy_exact": row["ast_proxy_signature"] in train_ast,
                      "distance_bucket": "near" if code_near[1] >= .85 else "medium" if code_near[1] >= .70 else "far"}
            distances.append(record)
            if code_near[1] >= .98:
                split_rejects.append({"task_id": tid, "nearest_train": code_near[0], "similarity": code_near[1]})
        audits[cap] = {"exact_metadata_overlap": overlap, "exact_reference_overlap": exact_ref,
                       "distance_records": distances,
                       "flags_train_prompt_0p70": [r for r in distances if r["train_prompt_jaccard"] >= .70],
                       "flags_train_code_0p85": [r for r in distances if r["train_code_similarity"] >= .85],
                       "flags_prior_prompt_0p70": [r for r in distances if r["prior_prompt_jaccard"] >= .70],
                       "flags_prior_code_0p90": [r for r in distances if r["prior_code_similarity"] >= .90],
                       "flags_ast_proxy_exact": [r for r in distances if r["train_ast_proxy_exact"]],
                       "distance_bucket_counts": dict(Counter(r["distance_bucket"] for r in distances))}
    payload = {"phase": "3C", "status": "pre_model_reference_and_structural_audit",
               "counts": {f"{cap}_{split}": len(datasets[(cap, split)]["rows"]) for cap in "ab" for split in ("training", "eval")},
               "verification": verification, "reference_failures": failures,
               "structural_audit": audits, "exact_current_prompt_collision": exact_current_prompt,
               "consumed_prompt_reuse": exact_consumed_prompt, "consumed_code_rejects_0p98": prior_code_rejects,
               "train_eval_code_rejects_0p98": split_rejects,
               "compiler_sha256": file_sha256(args.jar), "sealed_holdout_accessed": False,
               "file_sha256": {p.as_posix(): file_sha256(p) for p in inputs},
               "canonical_sha256": {p.as_posix(): canonical_sha256(load_json(p)) for p in inputs}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    summary = {"counts": payload["counts"], "reference_failures": len(failures),
               "consumed_prompt_reuse": len(exact_consumed_prompt), "prior_code_rejects": len(prior_code_rejects),
               "split_code_rejects": len(split_rejects),
               "audit": {cap: {"train_prompt_0p70": len(audits[cap]["flags_train_prompt_0p70"]),
                                "train_code_0p85": len(audits[cap]["flags_train_code_0p85"]),
                                "prior_prompt_0p70": len(audits[cap]["flags_prior_prompt_0p70"]),
                                "prior_code_0p90": len(audits[cap]["flags_prior_code_0p90"]),
                                "ast_proxy_exact": len(audits[cap]["flags_ast_proxy_exact"]),
                                "distance_buckets": audits[cap]["distance_bucket_counts"]} for cap in "ab"}}
    print(json.dumps(summary, indent=2))
    if failures or exact_current_prompt or exact_consumed_prompt or prior_code_rejects or split_rejects or any(
        a["exact_reference_overlap"] or any(a["exact_metadata_overlap"].values()) for a in audits.values()
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
