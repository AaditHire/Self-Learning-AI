"""Freeze full pre-model structural-distance distributions for DEV1."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from phase3c_contract import ROOT, sha256
from validate_phase2b_data import jaccard, normalized_code


def read(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def bucket(value: float) -> str:
    edges = (0,.25,.50,.60,.70,.80,.85,.90,.95,.98,1.0000001)
    for low, high in zip(edges, edges[1:]):
        if low <= value < high:
            return f"[{low:.2f},{min(high,1):.2f}{']' if high>1 else ')'}"
    raise ValueError(value)


def summarize(pairs: list[dict], field: str) -> dict:
    scores = sorted(x[field] for x in pairs)
    bins = dict(sorted(Counter(bucket(x) for x in scores).items()))
    return {"n":len(scores), "min":scores[0], "median":scores[len(scores)//2],
            "max":scores[-1], "at_least_0p70":sum(x>=.70 for x in scores),
            "at_least_0p85":sum(x>=.85 for x in scores),
            "at_least_0p90":sum(x>=.90 for x in scores),
            "at_least_0p95":sum(x>=.95 for x in scores),
            "at_least_0p98":sum(x>=.98 for x in scores),
            "histogram":bins}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    validation = read("research/results/PHASE_3C_DEV1/reference_validation.json")
    if validation["status"] != "PASS_REFERENCE_VALIDATION":
        raise ValueError("Reference validation must pass before structural freeze")
    eval_rows = read("benchmark/phase3c_dev1/a_development_eval_tasks.json")
    eval_refs = read("benchmark/phase3c_dev1/a_development_eval_references.json")
    if len(eval_rows) != 36:
        raise ValueError("Expected 36 evaluation tasks")
    all_pairs, by_condition, per_eval = [], {}, {}
    for condition in ("DENSE", "DIVERSE"):
        train = read(f"data/phase3c_dev1/a_{condition.lower()}_training_examples.json")
        train_refs = read(f"data/phase3c_dev1/a_{condition.lower()}_training_references.json")
        pairs = []
        for task in eval_rows:
            tid = task["task_id"]
            target_code = normalized_code(eval_refs[tid])
            target_ops = set(task["semantic_operations"])
            for example in train:
                eid = example["example_id"]
                ops = set(example["semantic_operations"])
                record = {"condition":condition,"eval_task_id":tid,"eval_family":task["family"],
                          "eval_archetype":task["archetype"],"distance_group":task["distance_group"],
                          "train_example_id":eid,"train_family":example["family"],
                          "train_archetype":example["archetype"],
                          "exact_prompt":task["prompt"]==example["prompt"],
                          "exact_reference":eval_refs[tid]==train_refs[eid],
                          "prompt_jaccard":jaccard(task["prompt"],example["prompt"]),
                          "normalized_code_similarity":difflib.SequenceMatcher(
                              None,target_code,normalized_code(train_refs[eid])).ratio(),
                          "ast_proxy_exact":task["ast_proxy_signature"]==example["ast_proxy_signature"],
                          "semantic_operation_overlap_count":len(target_ops & ops),
                          "semantic_operation_union_count":len(target_ops | ops),
                          "semantic_operation_jaccard":len(target_ops & ops)/len(target_ops | ops)}
                pairs.append(record)
        if len(pairs) != 36*60:
            raise ValueError("Pair enumeration incomplete")
        all_pairs.extend(pairs)
        by_condition[condition] = {
            "pairs":len(pairs),
            "exact_prompt_overlap_count":sum(x["exact_prompt"] for x in pairs),
            "exact_reference_overlap_count":sum(x["exact_reference"] for x in pairs),
            "ast_proxy_exact_pair_count":sum(x["ast_proxy_exact"] for x in pairs),
            "semantic_operation_overlap_pair_count":sum(x["semantic_operation_overlap_count"]>0 for x in pairs),
            "all_pair_distributions":{field:summarize(pairs,field) for field in
                                      ("prompt_jaccard","normalized_code_similarity",
                                       "semantic_operation_jaccard")},
        }
        nearest_rows = []
        for task in eval_rows:
            tid=task["task_id"]
            subset=[x for x in pairs if x["eval_task_id"]==tid]
            nearest_prompt=max(subset,key=lambda x:(x["prompt_jaccard"],x["train_example_id"]))
            nearest_code=max(subset,key=lambda x:(x["normalized_code_similarity"],x["train_example_id"]))
            nearest_semantic=max(subset,key=lambda x:(x["semantic_operation_jaccard"],x["train_example_id"]))
            nearest_rows.append({"task_id":tid,"family":task["family"],"archetype":task["archetype"],
                                 "distance_group":task["distance_group"],
                                 "nearest_prompt_id":nearest_prompt["train_example_id"],
                                 "nearest_prompt_jaccard":nearest_prompt["prompt_jaccard"],
                                 "nearest_code_id":nearest_code["train_example_id"],
                                 "nearest_code_archetype":nearest_code["train_archetype"],
                                 "nearest_code_similarity":nearest_code["normalized_code_similarity"],
                                 "nearest_ast_proxy_exact":nearest_code["ast_proxy_exact"],
                                 "nearest_semantic_id":nearest_semantic["train_example_id"],
                                 "nearest_semantic_operation_jaccard":nearest_semantic["semantic_operation_jaccard"],
                                 "semantic_operation_overlap_any":any(x["semantic_operation_overlap_count"]>0 for x in subset),
                                 "exact_prompt_any":any(x["exact_prompt"] for x in subset),
                                 "exact_reference_any":any(x["exact_reference"] for x in subset)})
        per_eval[condition]=nearest_rows
        by_condition[condition]["nearest_distributions"]={field:summarize(nearest_rows,field) for field in
            ("nearest_prompt_jaccard","nearest_code_similarity","nearest_semantic_operation_jaccard")}
        by_condition[condition]["by_distance_group"]={group:{
            "n_tasks":sum(x["distance_group"]==group for x in nearest_rows),
            "nearest_code_similarity":summarize([x for x in nearest_rows if x["distance_group"]==group],
                                                  "nearest_code_similarity"),
            "nearest_prompt_jaccard":summarize([x for x in nearest_rows if x["distance_group"]==group],
                                                "nearest_prompt_jaccard")}
            for group in ("near","compositional","far")}
    result={"phase":"3C-DEV1","status":"PRE_MODEL_FULL_STRUCTURAL_AUDIT",
            "metric_definitions":{"prompt":"token-set Jaccard from existing structural audit",
                                  "code":"difflib SequenceMatcher on identifier/number/string-normalized GOCO source",
                                  "ast_proxy":"exact coarse token-proxy string equality",
                                  "semantic":"Jaccard of declared semantic-operation tags"},
            "by_condition":by_condition,"nearest_per_eval_task":per_eval,
            "all_train_eval_pairs":all_pairs,
            "input_sha256":{path:sha256(ROOT/path) for path in (
                "data/phase3c_dev1/a_dense_training_examples.json",
                "data/phase3c_dev1/a_dense_training_references.json",
                "data/phase3c_dev1/a_diverse_training_examples.json",
                "data/phase3c_dev1/a_diverse_training_references.json",
                "benchmark/phase3c_dev1/a_development_eval_tasks.json",
                "benchmark/phase3c_dev1/a_development_eval_references.json")},
            "interpretation":"Distance groups were assigned by predeclared operation relationships, not by these similarity scores. Values are descriptive proxies; complete pairs and lower-threshold histograms are retained."}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as handle:
        json.dump(result,handle,indent=2);handle.write("\n")
    print(json.dumps({condition:{"exact_prompt":by_condition[condition]["exact_prompt_overlap_count"],
                                 "exact_reference":by_condition[condition]["exact_reference_overlap_count"],
                                 "ast_pairs":by_condition[condition]["ast_proxy_exact_pair_count"],
                                 "max_code":by_condition[condition]["nearest_distributions"]["nearest_code_similarity"]["max"]}
                      for condition in ("DENSE","DIVERSE")}))


if __name__=="__main__":
    main()
