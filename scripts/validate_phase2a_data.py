from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from self_learning_ai.benchmark import canonical_sha256, load_json, score_source
from self_learning_ai.compiler import GocoCompiler


FAMILIES = {
    "expressions_variables", "conditionals", "loops", "functions",
    "arrays", "strings", "input_output", "composition_algorithms",
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prompt_tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def jaccard(left: str, right: str) -> float:
    a, b = prompt_tokens(left), prompt_tokens(right)
    return len(a & b) / len(a | b) if a | b else 1.0


def normalized_code(text: str) -> str:
    text = re.sub(r'"(?:\\.|[^"\\])*"', '"STR"', text)
    text = re.sub(r"'(?:\\.|[^'\\])'", "'CHR'", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\b", "NUM", text)
    keywords = {
        "IMPORT", "NUMBER", "SENTENCE", "LETTER", "LOGIC", "TRUE", "FALSE",
        "INPUT", "DISPLAY", "DISPLAYNL", "IF", "ELSEIF", "ELSE", "LOOP",
        "TILL", "DO", "BREAK", "CONTINUE", "FUNCTION", "RETURN", "RETURNS",
        "NEW", "AND", "OR", "NOT",
    }
    def replace_identifier(match: re.Match[str]) -> str:
        token = match.group(0)
        return token.upper() if token.upper() in keywords else "ID"
    text = re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\b", replace_identifier, text)
    return re.sub(r"\s+", " ", text).strip()


def nearest(
    queries: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    query_value: callable,
    candidate_value: callable,
    metric: callable,
) -> list[dict[str, Any]]:
    rows=[]
    for query in queries:
        scored=[(metric(query_value(query), candidate_value(candidate)), candidate) for candidate in candidates]
        similarity, candidate=max(scored, key=lambda row: row[0])
        rows.append({"evaluation_task_id":query["task_id"],"nearest_task_id":candidate["task_id"],"similarity":similarity})
    return rows


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--training",type=Path,required=True)
    parser.add_argument("--training-tests",type=Path,required=True)
    parser.add_argument("--development",type=Path,required=True)
    parser.add_argument("--development-tests",type=Path,required=True)
    parser.add_argument("--development-references",type=Path,required=True)
    parser.add_argument("--regression",type=Path,required=True)
    parser.add_argument("--java",type=Path,required=True)
    parser.add_argument("--jar",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    training=load_json(args.training); train_tests=load_json(args.training_tests)
    development=load_json(args.development); dev_tests=load_json(args.development_tests)
    dev_refs=load_json(args.development_references); regression=load_json(args.regression)
    if len(training)!=200 or Counter(row["family"] for row in training)!=Counter({f:25 for f in FAMILIES}):
        raise ValueError("Training balance/count invariant failed")
    if len(development)!=64 or Counter(row["family"] for row in development)!=Counter({f:8 for f in FAMILIES}):
        raise ValueError("Development balance/count invariant failed")
    if len(regression)!=24:
        raise ValueError("Regression count invariant failed")
    train_ids={row["example_id"] for row in training}; dev_ids={row["task_id"] for row in development}
    if len(train_ids)!=200 or len(dev_ids)!=64 or train_ids & dev_ids:
        raise ValueError("ID uniqueness invariant failed")
    if set(train_tests)!=train_ids or set(dev_tests)!=dev_ids or set(dev_refs)!=dev_ids:
        raise ValueError("Task/test/reference key mismatch")
    for collection, id_key in ((training,"example_id"),(development,"task_id")):
        for field in ("algorithmic_structure","control_flow","template_lineage","structural_signature"):
            if any(not row[field] for row in collection):
                raise ValueError(f"Missing {field}")
        if len({row["template_lineage"] for row in collection})!=len(collection):
            raise ValueError(f"Duplicate lineages in {id_key}")
    if {r["template_lineage"] for r in training} & {r["template_lineage"] for r in development}:
        raise ValueError("Train/development lineage overlap")
    if {r["algorithmic_structure"] for r in training} & {r["algorithmic_structure"] for r in development}:
        raise ValueError("Train/development algorithm label overlap")

    compiler=GocoCompiler(args.java,args.jar,timeout_seconds=3,output_limit_bytes=65536)
    train_verification=[]
    for row in training:
        task={"task_id":row["example_id"],"family":row["family"],"difficulty":"phase2a_training_verification","required_regex":[]}
        scored=score_source(compiler,task,train_tests[row["example_id"]],row["target"]).as_dict()
        train_verification.append({
            "example_id":row["example_id"],"family":row["family"],
            "prompt_sha256":hashlib.sha256(row["prompt"].encode()).hexdigest(),
            "target_sha256":hashlib.sha256(row["target"].encode()).hexdigest(),
            "hidden_tests_sha256":canonical_sha256(train_tests[row["example_id"]]),
            "score":scored,
        })
    dev_verification=[]
    for row in development:
        scored=score_source(compiler,row,dev_tests[row["task_id"]],dev_refs[row["task_id"]]).as_dict()
        dev_verification.append({"task_id":row["task_id"],"reference_sha256":hashlib.sha256(dev_refs[row["task_id"]].encode()).hexdigest(),"score":scored})
    train_fail=[r["example_id"] for r in train_verification if not r["score"]["hidden_pass"]]
    dev_fail=[r["task_id"] for r in dev_verification if not r["score"]["hidden_pass"]]

    train_as_tasks=[{"task_id":r["example_id"],**r} for r in training]
    prompt_neighbors=nearest(development,train_as_tasks,lambda x:x["prompt"],lambda x:x["prompt"],jaccard)
    code_queries=[{"task_id":row["task_id"],"source":dev_refs[row["task_id"]]} for row in development]
    code_candidates=[{"task_id":row["example_id"],"source":row["target"]} for row in training]
    code_neighbors=nearest(code_queries,code_candidates,lambda x:normalized_code(x["source"]),lambda x:normalized_code(x["source"]),lambda a,b:difflib.SequenceMatcher(None,a,b).ratio())

    prior_tasks=[]; prior_refs=[]
    for tasks_path, refs_path in [
        (Path("benchmark/phase1r/development_tasks.json"),Path("benchmark/phase1r/development_reference_solutions.json")),
        (Path("benchmark/phase1s/diagnostic_tasks.json"),Path("benchmark/phase1s/diagnostic_references.json")),
        (Path("benchmark/phase1t/confirmation_tasks.json"),Path("benchmark/phase1t/confirmation_references.json")),
    ]:
        prior_tasks.extend(load_json(tasks_path))
        refs=load_json(refs_path)
        prior_refs.extend({"task_id":task_id,"source":source} for task_id,source in refs.items())
    if any(row["prompt"] in {p["prompt"] for p in prior_tasks} for row in development):
        raise ValueError("Exact development prompt reused from a consumed suite")
    prior_prompt_neighbors=nearest(development,prior_tasks,lambda x:x["prompt"],lambda x:x["prompt"],jaccard)
    prior_code_neighbors=nearest(code_queries,prior_refs,lambda x:normalized_code(x["source"]),lambda x:normalized_code(x["source"]),lambda a,b:difflib.SequenceMatcher(None,a,b).ratio())

    inputs=[args.training,args.training_tests,args.development,args.development_tests,args.development_references,args.regression]
    payload={
        "counts":{"training_examples":len(training),"development_tasks":len(development),"general_regression_tasks":len(regression),"training_hidden_cases":sum(map(len,train_tests.values())),"development_hidden_cases":sum(map(len,dev_tests.values()))},
        "family_counts":{"training":dict(sorted(Counter(r["family"] for r in training).items())),"development":dict(sorted(Counter(r["family"] for r in development).items()))},
        "canonical_hashes":{"training":canonical_sha256(training),"training_tests":canonical_sha256(train_tests),"development":canonical_sha256(development),"development_tests":canonical_sha256(dev_tests),"development_references":canonical_sha256(dev_refs),"regression":canonical_sha256(regression)},
        "file_hashes":{str(path).replace("\\","/"):file_sha256(path) for path in inputs},
        "compiler_sha256":file_sha256(args.jar),
        "training_verification":{"passed":len(training)-len(train_fail),"failed":train_fail,"records":train_verification},
        "development_reference_verification":{"passed":len(development)-len(dev_fail),"failed":dev_fail,"records":dev_verification},
        "structural_split":{"train_eval_lineage_overlap":0,"train_eval_algorithm_label_overlap":0,"nearest_prompt_neighbors":prompt_neighbors,"nearest_code_neighbors":code_neighbors,"prompt_flags_at_or_above_0p75":[r for r in prompt_neighbors if r["similarity"]>=.75],"code_flags_at_or_above_0p90":[r for r in code_neighbors if r["similarity"]>=.90]},
        "consumed_suite_audit":{"suites":["phase1r","phase1s","phase1t"],"sealed_phase1_holdout_opened":False,"exact_prompt_reuse":0,"nearest_prompt_neighbors":prior_prompt_neighbors,"nearest_code_neighbors":prior_code_neighbors,"prompt_flags_at_or_above_0p75":[r for r in prior_prompt_neighbors if r["similarity"]>=.75],"code_flags_at_or_above_0p90":[r for r in prior_code_neighbors if r["similarity"]>=.90]},
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"counts":payload["counts"],"train_failures":train_fail,"development_failures":dev_fail,"train_eval_prompt_flags":len(payload["structural_split"]["prompt_flags_at_or_above_0p75"]),"train_eval_code_flags":len(payload["structural_split"]["code_flags_at_or_above_0p90"]),"prior_prompt_flags":len(payload["consumed_suite_audit"]["prompt_flags_at_or_above_0p75"]),"prior_code_flags":len(payload["consumed_suite_audit"]["code_flags_at_or_above_0p90"])},indent=2))
    if train_fail or dev_fail:
        raise SystemExit(1)


if __name__=="__main__":
    main()
