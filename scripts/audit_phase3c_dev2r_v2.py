"""Pre-inference validation and leakage/coverage audit for versioned DEV2R v2."""
from __future__ import annotations

import difflib
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.benchmark import score_source
from self_learning_ai.compiler import GocoCompiler
from validate_phase2b_data import jaccard, normalized_code
from audit_phase3c_dev2r_api_coverage import CONSTRUCTS

OUT = ROOT / "research/results/PHASE_3C_DEV2R_AMENDMENT"
HISTORY = ("benchmark/phase3a/a_eval", "benchmark/phase3b/a_eval",
           "benchmark/phase3c/a_eval", "benchmark/phase3c_dev1/a_development_eval",
           "benchmark/phase3c_dev2/a_development_eval",
           "benchmark/phase3c_dev2r/a_development_eval")


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def write(path, value):
    if path.exists(): raise FileExistsError(path)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main():
    stem = "benchmark/phase3c_dev2r_v2/a_development_eval"
    paths = [stem + suffix + ".json" for suffix in ("_tasks", "_references", "_hidden_tests")]
    tasks, refs, tests = map(read, paths)
    old_stem = "benchmark/phase3c_dev2r/a_development_eval"
    old_tasks, old_refs, old_tests = (read(old_stem + suffix + ".json") for suffix in
                                      ("_tasks", "_references", "_hidden_tests"))
    old_by_id = {t["task_id"]: t for t in old_tasks}
    mapping = read("research/results/PHASE_3C_DEV2R_AMENDMENT/replacement_map.json")
    if not (len(tasks) == len(refs) == len(tests)):
        raise ValueError("Suite cardinality")
    if len(tasks) != 48 or len(set(refs)) != 48 or len(mapping) != 16:
        raise ValueError("Suite cardinality")
    if Counter(t["development_group"] for t in tasks) != {
            "primitive_sanity": 16, "novel_composition": 16, "structural_transfer": 16}:
        raise ValueError("Group balance")
    old_unchanged = {t["task_id"] for t in old_tasks if t["development_group"] != "primitive_sanity"}
    for task in tasks:
        tid = task["task_id"]
        if tid in old_unchanged and (task != old_by_id[tid] or refs[tid] != old_refs[tid]
                                      or tests[tid] != old_tests[tid]):
            raise ValueError(f"Protected Novel/Structural item changed: {tid}")
    if old_unchanged != {t["task_id"] for t in tasks if t["development_group"] != "primitive_sanity"}:
        raise ValueError("Protected IDs changed")
    prior_prompts, prior_refs = set(), set()
    for prefix in HISTORY:
        prior_prompts.update(row["prompt"] for row in read(prefix + "_tasks.json"))
        prior_refs.update(read(prefix + "_references.json").values())
    training = {}
    for condition in ("isolated", "composition"):
        prefix = f"data/phase3c_dev2/a_{condition}_training"
        training[condition] = (read(prefix + "_examples.json"), read(prefix + "_references.json"))
        prior_prompts.update(row["prompt"] for row in training[condition][0])
        prior_refs.update(training[condition][1].values())
    sanity = [task for task in tasks if task["development_group"] == "primitive_sanity"]
    if any(task["prompt"] in prior_prompts or refs[task["task_id"]] in prior_refs for task in sanity):
        raise ValueError("Prohibited exact historical reuse")
    if len({task["prompt"] for task in sanity}) != 16 or len({refs[task["task_id"]] for task in sanity}) != 16:
        raise ValueError("Duplicate replacement")
    pairs, nearest, essential = [], [], []
    for task in sanity:
        tid = task["task_id"]
        source = refs[tid]
        required_constructs = {name for name, pattern in CONSTRUCTS.items() if re.search(pattern, source)}
        if "negative_integer_literal" in required_constructs or any(
                float(case["expected_stdout"]) < 0 for case in tests[tid]):
            raise ValueError("Replacement retained negative output/literal")
        if len(tests[tid]) != 5:
            raise ValueError("Replacement schema")
        entry = {"task_id": tid, "required_primitive": task["semantic_primitives"][0],
                 "required_constructs": sorted(required_constructs), "conditions": {}}
        near = {"task_id": tid, "conditions": {}}
        for condition, (rows, train_refs) in training.items():
            same_family = [r for r in rows if r["family"] == task["family"]]
            family_refs = [train_refs[r["example_id"]] for r in same_family]
            primitive_ids = [r["example_id"] for r in same_family
                             if task["semantic_primitives"][0] in r["semantic_primitives"]]
            represented = {name for name, pattern in CONSTRUCTS.items()
                           if any(re.search(pattern, code) for code in family_refs)}
            gaps = sorted(required_constructs - represented)
            if not primitive_ids or gaps:
                raise ValueError(f"Task-essential coverage failure: {tid}, {condition}, {gaps}")
            local = []
            for row in rows:
                eid = row["example_id"]
                tr = train_refs[eid]
                comparison = {"task_id": tid, "condition": condition, "train_id": eid,
                              "train_archetype": row["archetype"],
                              "exact_prompt": task["prompt"] == row["prompt"],
                              "exact_reference": source == tr,
                              "prompt_jaccard": jaccard(task["prompt"], row["prompt"]),
                              "normalized_reference_code_similarity": difflib.SequenceMatcher(
                                  None, normalized_code(source), normalized_code(tr)).ratio(),
                              "ast_proxy_exact": task["ast_proxy_signature"] == row["ast_proxy_signature"]}
                if comparison["exact_prompt"] or comparison["exact_reference"]:
                    raise ValueError("Training exact reuse")
                local.append(comparison)
            pairs.extend(local)
            best_code = max(local, key=lambda x: (x["normalized_reference_code_similarity"], x["train_id"]))
            best_prompt = max(local, key=lambda x: (x["prompt_jaccard"], x["train_id"]))
            near["conditions"][condition] = {
                "nearest_code_id": best_code["train_id"],
                "nearest_code_similarity": best_code["normalized_reference_code_similarity"],
                "nearest_prompt_id": best_prompt["train_id"],
                "nearest_prompt_jaccard": best_prompt["prompt_jaccard"],
                "ast_proxy_exact_pairs": sum(x["ast_proxy_exact"] for x in local),
                "code_pairs_at_least": {str(t): sum(x["normalized_reference_code_similarity"] >= t for x in local)
                                        for t in (.5, .7, .85, .95, .98)}}
            entry["conditions"][condition] = {"primitive_training_example_ids": primitive_ids,
                "missing_required_constructs": gaps, "same_family_training_examples": len(same_family)}
        essential.append(entry); nearest.append(near)
    if len(pairs) != 16 * 60 * 2:
        raise ValueError("Structural pair count")
    old_structural = read("research/results/PHASE_3C_DEV2R/structural_audit.json")["nearest"]
    novel = [row for row in old_structural if row["group"] == "novel_composition"]
    if len(novel) != 16 or any(row["conditions"][c]["missing_primitives"] or
                              row["conditions"][c]["exact_composition_in_training"]
                              for row in novel for c in training):
        raise ValueError("Frozen Novel Composition gate")
    prior_essential = read("research/results/PHASE_3C_DEV2R_ESSENTIALITY/essentiality_audit.json")
    if prior_essential["task_essential_coverage"] != {"passed": 16, "total": 16}:
        raise ValueError("Frozen Structural Transfer essentiality gate")
    cfg = read("research/protocols/phase3c_dev2_config.json")
    if sha(cfg["compiler"]["path"]) != cfg["compiler"]["sha256"]:
        raise ValueError("Compiler hash")
    compiler = GocoCompiler(ROOT / cfg["compiler"]["java"], ROOT / cfg["compiler"]["path"],
                            timeout_seconds=3, output_limit_bytes=65536)
    validation = []
    for task in tasks:
        tid = task["task_id"]
        score = score_source(compiler, {**task, "difficulty": "dev2r_v2_reference_validation"},
                             tests[tid], refs[tid]).as_dict()
        validation.append({"task_id": tid, "group": task["development_group"],
                           "hidden_pass": score["hidden_pass"], "cases_passed": score["cases_passed"],
                           "cases_total": score["cases_total"], "error_phase": score["error_phase"],
                           "case_results": score["case_results"]})
        if not score["hidden_pass"] or score["cases_passed"] != 5:
            raise ValueError(f"Reference failed: {tid}: {score['error_phase']}")
    OUT.mkdir(parents=True, exist_ok=True)
    write(OUT / "replacement_structural_pairs.json", pairs)
    write(OUT / "v2_pre_execution_audit.json", {
        "status": "PASS_PRE_INFERENCE_SCIENTIFIC_GATES",
        "suite_version": "phase3c_dev2r_v2", "input_sha256": {p: sha(p) for p in paths},
        "replacements": 16, "old_non_sanity_tasks_byte_semantics_unchanged": 32,
        "historical_exact_prompt_or_reference_reuse": 0,
        "replacement_training_pairs": len(pairs), "replacement_nearest": nearest,
        "primitive_sanity_essential": essential,
        "final_gate": {"primitive_sanity_task_essential": "16/16",
                       "novel_composition_primitive": "16/16",
                       "novel_composition_signature_absence": "16/16",
                       "structural_transfer_primitive_and_task_essential": "16/16"},
        "similarity_interpretation": "All 1,920 replacement pairs, including below 0.98, are retained; descriptive metrics do not establish independence."})
    write(OUT / "v2_reference_validation.json", {
        "status": "PASS", "references": 48, "semantic_cases": 240,
        "passed_references": 48, "passed_cases": 240,
        "replacement_references": 16, "replacement_cases": 80,
        "compiler_sha256": sha(cfg["compiler"]["path"]), "results": validation})
    print(json.dumps({"replacements": 16, "pairs": len(pairs), "reference_cases_passed": 240}))


if __name__ == "__main__":
    main()
