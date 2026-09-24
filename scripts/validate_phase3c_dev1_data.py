"""Compiler/semantic validation of Phase 3C-DEV1 references; no model access."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from phase3c_contract import ROOT, sha256
from self_learning_ai.benchmark import score_source
from self_learning_ai.compiler import GocoCompiler


FILES = {
    "DENSE": ("data/phase3c_dev1/a_dense_training_examples.json",
              "data/phase3c_dev1/a_dense_training_references.json",
              "data/phase3c_dev1/a_dense_training_hidden_tests.json"),
    "DIVERSE": ("data/phase3c_dev1/a_diverse_training_examples.json",
                "data/phase3c_dev1/a_diverse_training_references.json",
                "data/phase3c_dev1/a_diverse_training_hidden_tests.json"),
    "EVAL": ("benchmark/phase3c_dev1/a_development_eval_tasks.json",
             "benchmark/phase3c_dev1/a_development_eval_references.json",
             "benchmark/phase3c_dev1/a_development_eval_hidden_tests.json"),
}
PRIOR_EVAL = (
    ("benchmark/phase3a/a_eval_tasks.json", "benchmark/phase3a/a_eval_references.json"),
    ("benchmark/phase3b/a_eval_tasks.json", "benchmark/phase3b/a_eval_references.json"),
    ("benchmark/phase3c/a_eval_tasks.json", "benchmark/phase3c/a_eval_references.json"),
)


def read(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    compiler_path = ROOT / ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar"
    java = ROOT / ".tools/jdk-25.0.1+8/bin/java.exe"
    frozen = read("research/protocols/phase3c_config.json")
    if sha256(compiler_path) != frozen["compiler_sha256"]:
        raise ValueError("Compiler hash differs from frozen Phase 3C instrument")
    compiler = GocoCompiler(java, compiler_path, timeout_seconds=3, output_limit_bytes=65536)
    prior_prompts, prior_refs = set(), set()
    for task_file, ref_file in PRIOR_EVAL:
        prior_prompts.update(x["prompt"] for x in read(task_file))
        prior_refs.update(read(ref_file).values())
    datasets, seen_ids, verification, file_hashes = {}, set(), {}, {}
    for condition, paths in FILES.items():
        rows, refs, tests = [read(path) for path in paths]
        file_hashes.update({path: sha256(ROOT/path) for path in paths})
        ids = [x.get("example_id", x.get("task_id")) for x in rows]
        expected = 36 if condition == "EVAL" else 60
        if (len(rows) != expected or len(set(ids)) != expected or set(refs) != set(ids)
                or set(tests) != set(ids) or seen_ids & set(ids)
                or Counter(x["family"] for x in rows) != {"numeric_iteration":expected//2,
                                                         "array_reduction":expected//2}
                or any(len(tests[x]) != 5 for x in ids)
                or any(not refs[x].strip() for x in ids)):
            raise ValueError(f"Dataset schema/ID/count error: {condition}")
        seen_ids.update(ids)
        if condition != "EVAL" and any(row["target"] != refs[row["example_id"]] for row in rows):
            raise ValueError("Training target/reference mismatch")
        if condition == "EVAL" and Counter(x["distance_group"] for x in rows) != {
                "near":12,"compositional":12,"far":12}:
            raise ValueError("Evaluation distance groups")
        datasets[condition] = (rows, refs, tests)
        verification[condition] = []
        for row in rows:
            item_id = row.get("example_id", row.get("task_id"))
            task = {"task_id":item_id, "family":row["family"],
                    "difficulty":"development_reference", "required_regex":[]}
            result = score_source(compiler, task, tests[item_id], refs[item_id]).as_dict()
            verification[condition].append({"item_id":item_id, "score":result})
            if not result["hidden_pass"]:
                print(json.dumps({"FAILED_REFERENCE":item_id, "error":result["error_phase"],
                                  "cases_passed":result["cases_passed"]}),flush=True)
        print(json.dumps({"condition":condition, "references":len(rows),
                          "passed":sum(x["score"]["hidden_pass"] for x in verification[condition])}),flush=True)

    current = [r for rows,_,_ in datasets.values() for r in rows]
    current_refs = [ref for _,refs,_ in datasets.values() for ref in refs.values()]
    exact_prior_prompt = [x.get("example_id", x.get("task_id")) for x in current if x["prompt"] in prior_prompts]
    exact_prior_ref = sum(x in prior_refs for x in current_refs)
    eval_rows, eval_refs, _ = datasets["EVAL"]
    eval_prompts = {x["prompt"] for x in eval_rows}
    eval_sources = set(eval_refs.values())
    exact_train_eval_prompt = sum(x["prompt"] in eval_prompts for c in ("DENSE","DIVERSE")
                                  for x in datasets[c][0])
    exact_train_eval_ref = sum(x in eval_sources for c in ("DENSE","DIVERSE")
                               for x in datasets[c][1].values())
    failures = [x["item_id"] for rows in verification.values() for x in rows if not x["score"]["hidden_pass"]]
    result = {"phase":"3C-DEV1", "status":"PASS_REFERENCE_VALIDATION" if not failures and
              not exact_prior_prompt and not exact_prior_ref and not exact_train_eval_prompt and
              not exact_train_eval_ref else "FAIL_REFERENCE_OR_REUSE_AUDIT",
              "counts":{name:len(rows) for name,(rows,_,_) in datasets.items()},
              "semantic_cases_checked":sum(len(tests[x]) for _,_,tests in datasets.values() for x in tests),
              "reference_failures":failures,
              "exact_prior_eval_prompt_reuse":exact_prior_prompt,
              "exact_prior_eval_reference_reuse_count":exact_prior_ref,
              "exact_train_eval_prompt_reuse_count":exact_train_eval_prompt,
              "exact_train_eval_reference_reuse_count":exact_train_eval_ref,
              "compiler_sha256":sha256(compiler_path),"file_sha256":file_hashes,
              "verification":verification,"sealed_holdout_accessed":False,
              "no_model_inference_or_gradients":True}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as handle:
        json.dump(result,handle,indent=2);handle.write("\n")
    print(json.dumps({"status":result["status"],"cases":result["semantic_cases_checked"],
                      "failures":len(failures),"prior_prompt_reuse":len(exact_prior_prompt),
                      "prior_reference_reuse":exact_prior_ref}),flush=True)
    if result["status"] != "PASS_REFERENCE_VALIDATION":
        raise SystemExit(1)


if __name__=="__main__":
    main()
