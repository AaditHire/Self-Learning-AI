from __future__ import annotations

import argparse
import difflib
import json
from collections import Counter
from pathlib import Path

from self_learning_ai.benchmark import canonical_sha256, load_json, score_source
from self_learning_ai.compiler import GocoCompiler
from validate_phase2b_data import file_sha256, jaccard, normalized_code


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--java",type=Path,required=True); parser.add_argument("--jar",type=Path,required=True); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    datasets={}; inputs=[]
    for cap in "ab":
        for split in ("training","eval"):
            folder=Path("data/phase3b" if split=="training" else "benchmark/phase3b")
            stem=f"{cap}_{split}"
            task_path=folder/f"{stem}_{'examples' if split=='training' else 'tasks'}.json"
            test_path=folder/f"{stem}_hidden_tests.json"
            ref_path=folder/f"{stem}_references.json" if split=="eval" else None
            rows=load_json(task_path); tests=load_json(test_path)
            refs=load_json(ref_path) if ref_path else {r["example_id"]:r["target"] for r in rows}
            key="example_id" if split=="training" else "task_id"
            expected=60 if split=="training" else 32
            family_n=30 if split=="training" else 16
            balance=Counter({"numeric_iteration":family_n,"array_reduction":family_n}) if cap=="a" else Counter({"string_transform":family_n,"field_processing":family_n})
            if len(rows)!=expected or len({r[key] for r in rows})!=expected or Counter(r["family"] for r in rows)!=balance: raise ValueError((cap,split,"count/balance"))
            if set(tests)!={r[key] for r in rows} or set(refs)!={r[key] for r in rows} or any(len(c)!=5 for c in tests.values()): raise ValueError((cap,split,"keys/cases"))
            if any(r["capability"].lower()!=cap for r in rows): raise ValueError((cap,split,"capability"))
            datasets[(cap,split)]={"rows":rows,"tests":tests,"refs":refs}
            inputs.extend([task_path,test_path]+([ref_path] if ref_path else []))
    all_ids=[r.get("task_id",r.get("example_id")) for d in datasets.values() for r in d["rows"]]
    if len(all_ids)!=len(set(all_ids)): raise ValueError("Global ID overlap")
    compiler=GocoCompiler(args.java,args.jar,timeout_seconds=3,output_limit_bytes=65536)
    verification={}; failures=[]
    for (cap,split),d in datasets.items():
        key=f"{cap}_{split}"; verification[key]=[]
        for row in d["rows"]:
            tid=row.get("task_id",row.get("example_id"))
            task=row if split=="eval" else {"task_id":tid,"family":row["family"],"difficulty":"phase3b_train","required_regex":[]}
            result=score_source(compiler,task,d["tests"][tid],d["refs"][tid]).as_dict()
            verification[key].append({"task_id":tid,"score":result})
            if not result["hidden_pass"]: failures.append({"task_id":tid,"error_phase":result["error_phase"],"cases_passed":result["cases_passed"],"first_case":result["case_results"][0]})
    prior_tasks=[]; prior_refs=[]
    for task_path,ref_path in (
        ("benchmark/phase1r/development_tasks.json","benchmark/phase1r/development_reference_solutions.json"),
        ("benchmark/phase1s/diagnostic_tasks.json","benchmark/phase1s/diagnostic_references.json"),
        ("benchmark/phase1t/confirmation_tasks.json","benchmark/phase1t/confirmation_references.json"),
        ("benchmark/phase2a/development_tasks.json","benchmark/phase2a/development_references.json"),
        ("benchmark/phase2b/confirmatory_tasks.json","benchmark/phase2b/confirmatory_references.json"),
        ("benchmark/phase3a/a_eval_tasks.json","benchmark/phase3a/a_eval_references.json"),
        ("benchmark/phase3a/b_eval_tasks.json","benchmark/phase3a/b_eval_references.json"),
    ):
        prior_tasks.extend(load_json(Path(task_path))); prior_refs.extend(load_json(Path(ref_path)).values())
    prior_prompt_set={r["prompt"] for r in prior_tasks}
    prior_code=[normalized_code(s) for s in prior_refs]
    audits={}; rejects=[]
    for cap in "ab":
        training=datasets[(cap,"training")]; evaluation=datasets[(cap,"eval")]
        tr=training["rows"]; ev=evaluation["rows"]
        fields=("algorithmic_structure","template_lineage","structural_signature","semantic_operations")
        overlaps={f:len({json.dumps(r[f],sort_keys=True) for r in tr}&{json.dumps(r[f],sort_keys=True) for r in ev}) for f in fields}
        exact_prompt=len({r["prompt"] for r in tr}&{r["prompt"] for r in ev})
        if exact_prompt or any(overlaps.values()): raise ValueError((cap,"exact split overlap",exact_prompt,overlaps))
        consumed_prompt=[r.get("task_id",r.get("example_id")) for r in tr+ev if r["prompt"] in prior_prompt_set]
        if consumed_prompt: raise ValueError((cap,"consumed evaluation prompt reuse",consumed_prompt))
        prompt_flags=[]; code_flags=[]; prior_prompt_flags=[]; prior_code_flags=[]; ast_matches=[]; distances=[]
        train_ast={r["ast_proxy_signature"] for r in tr}
        for row in ev:
            tid=row["task_id"]; source=normalized_code(evaluation["refs"][tid])
            prompt_sim,nearest_prompt=max((jaccard(row["prompt"],t["prompt"]),t["example_id"]) for t in tr)
            code_sim,nearest_code=max((difflib.SequenceMatcher(None,source,normalized_code(t["target"])).ratio(),t["example_id"]) for t in tr)
            prior_prompt=max(jaccard(row["prompt"],t["prompt"]) for t in prior_tasks)
            prior_similarity=max(difflib.SequenceMatcher(None,source,p).ratio() for p in prior_code)
            if prompt_sim>=.70: prompt_flags.append({"task_id":tid,"train":nearest_prompt,"similarity":prompt_sim})
            if code_sim>=.85: code_flags.append({"task_id":tid,"train":nearest_code,"similarity":code_sim})
            if prior_prompt>=.70: prior_prompt_flags.append({"task_id":tid,"similarity":prior_prompt})
            if prior_similarity>=.90: prior_code_flags.append({"task_id":tid,"similarity":prior_similarity})
            if row["ast_proxy_signature"] in train_ast: ast_matches.append(tid)
            if code_sim>=.98 or prior_similarity>=.98: rejects.append({"task_id":tid,"train_similarity":code_sim,"consumed_similarity":prior_similarity})
            distances.append({"task_id":tid,"family":row["family"],"nearest_prompt_similarity":prompt_sim,"nearest_code_similarity":code_sim,"prior_prompt_similarity":prior_prompt,"prior_code_similarity":prior_similarity,"distance_bucket":"near" if code_sim>=.85 else "medium" if code_sim>=.70 else "far"})
        audits[cap]={"exact_prompt_overlap":exact_prompt,"exact_metadata_overlaps":overlaps,"consumed_eval_prompt_reuse":consumed_prompt,"prompt_flags_0p70":prompt_flags,"code_flags_0p85":code_flags,"prior_prompt_flags_0p70":prior_prompt_flags,"prior_code_flags_0p90":prior_code_flags,"ast_proxy_exact":ast_matches,"distance_records":distances,"distance_bucket_counts":dict(Counter(r["distance_bucket"] for r in distances))}
    cross={r["prompt"] for r in datasets[("a","training")]["rows"]+datasets[("a","eval")]["rows"]}&{r["prompt"] for r in datasets[("b","training")]["rows"]+datasets[("b","eval")]["rows"]}
    if cross: raise ValueError("Cross-capability prompt overlap")
    payload={"phase":"3B","counts":{f"{cap}_{split}":len(datasets[(cap,split)]["rows"]) for cap in "ab" for split in ("training","eval")},"verification":verification,"reference_failures":failures,"structural_audit":audits,"code_rejects_0p98":rejects,"cross_capability_exact_prompt_overlap":0,"sealed_holdout_opened":False,"compiler_sha256":file_sha256(args.jar),"file_sha256":{str(p).replace('\\','/'):file_sha256(p) for p in inputs},"canonical_sha256":{str(p).replace('\\','/'):canonical_sha256(load_json(p)) for p in inputs}}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    summary={"counts":payload["counts"],"reference_failures":failures,"code_rejects_0p98":rejects,"audit":{cap:{"prompt_flags":len(x["prompt_flags_0p70"]),"code_flags":len(x["code_flags_0p85"]),"prior_prompt_flags":len(x["prior_prompt_flags_0p70"]),"prior_code_flags":len(x["prior_code_flags_0p90"]),"ast_matches":len(x["ast_proxy_exact"]),"distance_buckets":x["distance_bucket_counts"]} for cap,x in audits.items()}}
    print(json.dumps(summary,indent=2))
    if failures or rejects: raise SystemExit(1)


if __name__=="__main__": main()
