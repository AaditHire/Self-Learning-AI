from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from self_learning_ai.benchmark import canonical_sha256, load_json, score_source
from self_learning_ai.compiler import GocoCompiler


FAMILIES = {
    "expressions_variables", "conditionals", "loops", "functions",
    "arrays", "strings", "input_output", "composition_algorithms",
}


def file_sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()


def prompt_tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+",text.casefold()))


def jaccard(a: str,b: str)->float:
    left,right=prompt_tokens(a),prompt_tokens(b)
    return len(left&right)/len(left|right) if left|right else 1.0


def normalized_code(text: str)->str:
    text=re.sub(r'"(?:\\.|[^"\\])*"','"STR"',text)
    text=re.sub(r"\b\d+(?:\.\d+)?\b","NUM",text)
    keywords={"IMPORT","NUMBER","SENTENCE","LETTER","LOGIC","TRUE","FALSE","INPUT","DISPLAY","DISPLAYNL","IF","ELSEIF","ELSE","LOOP","TILL","DO","BREAK","CONTINUE","FUNCTION","RETURN","RETURNS","NEW","AND","OR","NOT"}
    def repl(match:re.Match[str])->str:
        token=match.group(0); return token.upper() if token.upper() in keywords else "ID"
    text=re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\b",repl,text)
    return re.sub(r"\s+"," ",text).strip()


def nearest(queries:list[dict[str,Any]],candidates:list[dict[str,Any]],qvalue:Callable,cvalue:Callable,metric:Callable)->list[dict[str,Any]]:
    rows=[]
    for query in queries:
        scored=[(metric(qvalue(query),cvalue(candidate)),candidate) for candidate in candidates]
        similarity,candidate=max(scored,key=lambda row:row[0])
        rows.append({"evaluation_task_id":query["task_id"],"nearest_task_id":candidate["task_id"],"similarity":similarity})
    return rows


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--training",type=Path,required=True); parser.add_argument("--training-tests",type=Path,required=True)
    parser.add_argument("--evaluation",type=Path,required=True); parser.add_argument("--evaluation-tests",type=Path,required=True)
    parser.add_argument("--evaluation-references",type=Path,required=True); parser.add_argument("--regression",type=Path,required=True)
    parser.add_argument("--java",type=Path,required=True); parser.add_argument("--jar",type=Path,required=True); parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    training=load_json(args.training); train_tests=load_json(args.training_tests)
    evaluation=load_json(args.evaluation); eval_tests=load_json(args.evaluation_tests); eval_refs=load_json(args.evaluation_references); regression=load_json(args.regression)
    if len(training)!=200 or Counter(r["family"] for r in training)!=Counter({f:25 for f in FAMILIES}): raise ValueError("Training balance/count")
    if len(evaluation)!=128 or Counter(r["family"] for r in evaluation)!=Counter({f:16 for f in FAMILIES}): raise ValueError("Evaluation balance/count")
    if len(regression)!=64: raise ValueError("Regression count")
    train_ids={r["example_id"] for r in training}; eval_ids={r["task_id"] for r in evaluation}
    if len(train_ids)!=200 or len(eval_ids)!=128 or train_ids&eval_ids: raise ValueError("ID uniqueness")
    if set(train_tests)!=train_ids or set(eval_tests)!=eval_ids or set(eval_refs)!=eval_ids: raise ValueError("Test/reference keys")
    fields=("algorithmic_structure","control_flow","template_lineage","structural_signature","ast_proxy_signature","semantic_operations")
    for collection,id_key in ((training,"example_id"),(evaluation,"task_id")):
        for field in fields:
            if any(not row[field] for row in collection): raise ValueError(f"Missing {field}")
        if len({r["template_lineage"] for r in collection})!=len(collection): raise ValueError(f"Duplicate lineage {id_key}")
    exact_overlaps={field:len({json.dumps(r[field],sort_keys=True) for r in training}&{json.dumps(r[field],sort_keys=True) for r in evaluation}) for field in fields}
    if exact_overlaps["template_lineage"] or exact_overlaps["algorithmic_structure"] or exact_overlaps["structural_signature"] or exact_overlaps["semantic_operations"]:
        raise ValueError(f"Strong split exact overlap: {exact_overlaps}")
    exact_prompt_reuse=len({r["prompt"] for r in training}&{r["prompt"] for r in evaluation})
    if exact_prompt_reuse: raise ValueError("Exact train/eval prompt reuse")

    compiler=GocoCompiler(args.java,args.jar,timeout_seconds=3,output_limit_bytes=65536)
    train_verification=[]
    for row in training:
        task={"task_id":row["example_id"],"family":row["family"],"difficulty":"phase2b_training_verification","required_regex":[]}
        score=score_source(compiler,task,train_tests[row["example_id"]],row["target"]).as_dict()
        train_verification.append({"example_id":row["example_id"],"family":row["family"],"prompt_sha256":hashlib.sha256(row["prompt"].encode()).hexdigest(),"target_sha256":hashlib.sha256(row["target"].encode()).hexdigest(),"hidden_tests_sha256":canonical_sha256(train_tests[row["example_id"]]),"score":score})
    eval_verification=[]
    for row in evaluation:
        score=score_source(compiler,row,eval_tests[row["task_id"]],eval_refs[row["task_id"]]).as_dict()
        eval_verification.append({"task_id":row["task_id"],"reference_sha256":hashlib.sha256(eval_refs[row["task_id"]].encode()).hexdigest(),"hidden_tests_sha256":canonical_sha256(eval_tests[row["task_id"]]),"score":score})
    train_fail=[r["example_id"] for r in train_verification if not r["score"]["hidden_pass"]]
    eval_fail=[r["task_id"] for r in eval_verification if not r["score"]["hidden_pass"]]

    train_tasks=[{"task_id":r["example_id"],**r} for r in training]
    prompt_neighbors=nearest(evaluation,train_tasks,lambda x:x["prompt"],lambda x:x["prompt"],jaccard)
    code_queries=[{"task_id":r["task_id"],"source":eval_refs[r["task_id"]]} for r in evaluation]
    code_candidates=[{"task_id":r["example_id"],"source":r["target"]} for r in training]
    code_neighbors=nearest(code_queries,code_candidates,lambda x:normalized_code(x["source"]),lambda x:normalized_code(x["source"]),lambda a,b:difflib.SequenceMatcher(None,a,b).ratio())
    ast_exact=[]
    train_ast={r["ast_proxy_signature"]:r["example_id"] for r in training}
    for row in evaluation:
        if row["ast_proxy_signature"] in train_ast: ast_exact.append({"evaluation_task_id":row["task_id"],"training_task_id":train_ast[row["ast_proxy_signature"]],"ast_proxy_signature":row["ast_proxy_signature"]})

    prior_tasks=[]; prior_refs=[]
    for tasks_path,refs_path in [
        (Path("benchmark/phase1r/development_tasks.json"),Path("benchmark/phase1r/development_reference_solutions.json")),
        (Path("benchmark/phase1s/diagnostic_tasks.json"),Path("benchmark/phase1s/diagnostic_references.json")),
        (Path("benchmark/phase1t/confirmation_tasks.json"),Path("benchmark/phase1t/confirmation_references.json")),
        (Path("benchmark/phase2a/development_tasks.json"),Path("benchmark/phase2a/development_references.json")),
    ]:
        prior_tasks.extend(load_json(tasks_path)); refs=load_json(refs_path); prior_refs.extend({"task_id":k,"source":v} for k,v in refs.items())
    phase2a_training=load_json(Path("data/phase2a/training_examples.json"))
    prior_tasks.extend({"task_id":r["example_id"],"prompt":r["prompt"]} for r in phase2a_training)
    prior_refs.extend({"task_id":r["example_id"],"source":r["target"]} for r in phase2a_training)
    prior_prompt_exact=[r["task_id"] for r in evaluation if r["prompt"] in {p["prompt"] for p in prior_tasks}]
    training_prior_eval_exact=[r["example_id"] for r in training if r["prompt"] in {p["prompt"] for p in prior_tasks if not str(p["task_id"]).startswith("P2A-TR-")}]
    if prior_prompt_exact or training_prior_eval_exact: raise ValueError((prior_prompt_exact,training_prior_eval_exact))
    prior_prompt_neighbors=nearest(evaluation,prior_tasks,lambda x:x["prompt"],lambda x:x["prompt"],jaccard)
    prior_code_neighbors=nearest(code_queries,prior_refs,lambda x:normalized_code(x["source"]),lambda x:normalized_code(x["source"]),lambda a,b:difflib.SequenceMatcher(None,a,b).ratio())

    inputs=[args.training,args.training_tests,args.evaluation,args.evaluation_tests,args.evaluation_references,args.regression]
    distance=[]
    by_code={r["evaluation_task_id"]:r for r in code_neighbors}; by_prompt={r["evaluation_task_id"]:r for r in prompt_neighbors}
    for row in evaluation:
        code_sim=by_code[row["task_id"]]["similarity"]; prompt_sim=by_prompt[row["task_id"]]["similarity"]
        bucket="near" if code_sim>=.85 else "medium" if code_sim>=.70 else "far"
        distance.append({"task_id":row["task_id"],"family":row["family"],"prompt_similarity":prompt_sim,"code_similarity":code_sim,"distance_bucket":bucket,"nearest_training_prompt":by_prompt[row["task_id"]]["nearest_task_id"],"nearest_training_code":by_code[row["task_id"]]["nearest_task_id"]})
    payload={
        "counts":{"training_examples":len(training),"confirmatory_tasks":len(evaluation),"general_regression_tasks":len(regression),"training_hidden_cases":sum(map(len,train_tests.values())),"confirmatory_hidden_cases":sum(map(len,eval_tests.values()))},
        "family_counts":{"training":dict(sorted(Counter(r["family"] for r in training).items())),"evaluation":dict(sorted(Counter(r["family"] for r in evaluation).items()))},
        "canonical_hashes":{"training":canonical_sha256(training),"training_tests":canonical_sha256(train_tests),"evaluation":canonical_sha256(evaluation),"evaluation_tests":canonical_sha256(eval_tests),"evaluation_references":canonical_sha256(eval_refs),"regression":canonical_sha256(regression)},
        "file_hashes":{str(p).replace("\\","/"):file_sha256(p) for p in inputs},"compiler_sha256":file_sha256(args.jar),
        "training_verification":{"passed":len(training)-len(train_fail),"failed":train_fail,"records":train_verification},
        "evaluation_reference_verification":{"passed":len(evaluation)-len(eval_fail),"failed":eval_fail,"records":eval_verification},
        "structural_split":{"exact_prompt_reuse":exact_prompt_reuse,"exact_metadata_overlaps":exact_overlaps,"nearest_prompt_neighbors":prompt_neighbors,"nearest_code_neighbors":code_neighbors,"prompt_flags_at_or_above_0p70":[r for r in prompt_neighbors if r["similarity"]>=.70],"code_flags_at_or_above_0p85":[r for r in code_neighbors if r["similarity"]>=.85],"code_rejects_at_or_above_0p98":[r for r in code_neighbors if r["similarity"]>=.98],"ast_proxy_exact_matches":ast_exact,"distance_records":distance,"distance_bucket_counts":dict(sorted(Counter(r["distance_bucket"] for r in distance).items()))},
        "consumed_artifact_audit":{"suites":["phase1r","phase1s","phase1t","phase2a_training","phase2a_development"],"sealed_phase1_holdout_opened":False,"exact_evaluation_prompt_reuse":prior_prompt_exact,"training_reuses_prior_evaluation_prompt":training_prior_eval_exact,"nearest_evaluation_prompt_neighbors":prior_prompt_neighbors,"nearest_evaluation_code_neighbors":prior_code_neighbors,"prompt_flags_at_or_above_0p70":[r for r in prior_prompt_neighbors if r["similarity"]>=.70],"code_flags_at_or_above_0p90":[r for r in prior_code_neighbors if r["similarity"]>=.90]},
    }
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"counts":payload["counts"],"train_failures":train_fail,"evaluation_failures":eval_fail,"exact_metadata_overlaps":exact_overlaps,"train_eval_prompt_flags":len(payload["structural_split"]["prompt_flags_at_or_above_0p70"]),"train_eval_code_flags":len(payload["structural_split"]["code_flags_at_or_above_0p85"]),"code_rejects":len(payload["structural_split"]["code_rejects_at_or_above_0p98"]),"ast_proxy_exact":len(ast_exact),"distance_buckets":payload["structural_split"]["distance_bucket_counts"],"prior_prompt_flags":len(payload["consumed_artifact_audit"]["prompt_flags_at_or_above_0p70"]),"prior_code_flags":len(payload["consumed_artifact_audit"]["code_flags_at_or_above_0p90"])},indent=2))
    if train_fail or eval_fail or payload["structural_split"]["code_rejects_at_or_above_0p98"]: raise SystemExit(1)


if __name__=="__main__": main()
