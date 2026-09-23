from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from collections import Counter
from pathlib import Path

from self_learning_ai.benchmark import canonical_sha256, load_json, score_source
from self_learning_ai.compiler import GocoCompiler
from validate_phase2b_data import file_sha256, jaccard, normalized_code


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--java",type=Path,required=True); parser.add_argument("--jar",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    datasets={}; paths=[]
    for cap in "ab":
        for split in ("training","eval"):
            base=Path("data/phase3a" if split=="training" else "benchmark/phase3a")
            prefix=f"{cap}_{split}"
            taskpath=base/f"{prefix}_{'examples' if split=='training' else 'tasks'}.json"
            testpath=base/f"{prefix}_hidden_tests.json"
            refpath=base/f"{prefix}_references.json" if split=="eval" else None
            rows=load_json(taskpath); tests=load_json(testpath); refs=load_json(refpath) if refpath else {r["example_id"]:r["target"] for r in rows}
            datasets[(cap,split)]={"rows":rows,"tests":tests,"refs":refs}
            paths.extend([taskpath,testpath]+([refpath] if refpath else []))
            expected=60 if split=="training" else 32
            key="example_id" if split=="training" else "task_id"
            if len(rows)!=expected or len({r[key] for r in rows})!=expected: raise ValueError((cap,split,"count"))
            if split=="training" and Counter(r["family"] for r in rows)!=(Counter({"numeric_iteration":30,"array_reduction":30}) if cap=="a" else Counter({"string_transform":30,"field_processing":30})): raise ValueError((cap,split,"balance"))
            if split=="eval" and Counter(r["family"] for r in rows)!=(Counter({"numeric_iteration":16,"array_reduction":16}) if cap=="a" else Counter({"string_transform":16,"field_processing":16})): raise ValueError((cap,split,"eval balance"))
            if set(tests)!={r[key] for r in rows} or set(refs)!={r[key] for r in rows}: raise ValueError((cap,split,"keys"))
            if any(len(cases)!=5 for cases in tests.values()): raise ValueError((cap,split,"case balance"))
    allrows=[r for d in datasets.values() for r in d["rows"]]
    if len({r.get("task_id",r.get("example_id")) for r in allrows})!=184: raise ValueError("Global ID collision")
    compiler=GocoCompiler(args.java,args.jar,timeout_seconds=3,output_limit_bytes=65536)
    verified={}; failures=[]
    for (cap,split),d in datasets.items():
        verified[f"{cap}_{split}"]=[]
        for r in d["rows"]:
            task_id=r.get("task_id",r.get("example_id"))
            task=r if split=="eval" else {"task_id":task_id,"family":r["family"],"difficulty":"phase3a_train","required_regex":[]}
            score=score_source(compiler,task,d["tests"][task_id],d["refs"][task_id]).as_dict()
            verified[f"{cap}_{split}"].append({"task_id":task_id,"score":score})
            if not score["hidden_pass"]: failures.append(task_id)
    prior=[]
    for path in ("benchmark/phase1r/development_tasks.json","benchmark/phase1s/diagnostic_tasks.json","benchmark/phase1t/confirmation_tasks.json","benchmark/phase2a/development_tasks.json","benchmark/phase2b/confirmatory_tasks.json"):
        prior.extend(load_json(Path(path)))
    prior_prompts={r["prompt"] for r in prior}
    prior_codes=[]
    for path in ("benchmark/phase1r/development_reference_solutions.json","benchmark/phase1s/diagnostic_references.json","benchmark/phase1t/confirmation_references.json","benchmark/phase2a/development_references.json","benchmark/phase2b/confirmatory_references.json"):
        prior_codes.extend(load_json(Path(path)).values())
    audits={}; rejects=[]
    for cap in "ab":
        training=datasets[(cap,"training")]; evaluation=datasets[(cap,"eval")]
        tr=training["rows"]; ev=evaluation["rows"]
        fields=("algorithmic_structure","template_lineage","structural_signature","semantic_operations")
        overlaps={f:len({json.dumps(r[f],sort_keys=True) for r in tr}&{json.dumps(r[f],sort_keys=True) for r in ev}) for f in fields}
        if any(overlaps.values()): raise ValueError((cap,"metadata overlap",overlaps))
        prompt_flags=[]; code_flags=[]; ast_matches=[]; distances=[]; prior_flags=[]; prior_prompt_flags=[]; prior_code_flags=[]
        train_ast={r["ast_proxy_signature"] for r in tr}
        for r in ev:
            tid=r["task_id"]; source=evaluation["refs"][tid]
            prompt_sim,near_prompt=max((jaccard(r["prompt"],t["prompt"]),t["example_id"]) for t in tr)
            code_sim,near_code=max((difflib.SequenceMatcher(None,normalized_code(source),normalized_code(t["target"])).ratio(),t["example_id"]) for t in tr)
            if prompt_sim>=.70: prompt_flags.append({"eval":tid,"train":near_prompt,"similarity":prompt_sim})
            if code_sim>=.85: code_flags.append({"eval":tid,"train":near_code,"similarity":code_sim})
            if code_sim>=.98: rejects.append({"eval":tid,"train":near_code,"similarity":code_sim})
            if r["ast_proxy_signature"] in train_ast: ast_matches.append(tid)
            distances.append({"task_id":tid,"family":r["family"],"nearest_prompt_similarity":prompt_sim,"nearest_code_similarity":code_sim,"distance_bucket":"near" if code_sim>=.85 else "medium" if code_sim>=.70 else "far"})
            prior_sim=max(difflib.SequenceMatcher(None,normalized_code(source),normalized_code(p)).ratio() for p in prior_codes)
            prior_prompt_sim=max(jaccard(r["prompt"],p["prompt"]) for p in prior)
            if prior_prompt_sim>=.70: prior_prompt_flags.append({"task_id":tid,"prompt_similarity":prior_prompt_sim})
            if prior_sim>=.90: prior_code_flags.append({"task_id":tid,"code_similarity":prior_sim})
            if prior_sim>=.98: prior_flags.append({"task_id":tid,"code_similarity":prior_sim})
        exact_prior=[r.get("task_id",r.get("example_id")) for r in tr+ev if r["prompt"] in prior_prompts]
        if exact_prior or prior_flags: raise ValueError((cap,"prior evaluation reuse/near-duplicate",exact_prior,prior_flags))
        audits[cap]={"metadata_exact_overlaps":overlaps,"exact_train_eval_prompt_reuse":len({r["prompt"] for r in tr}&{r["prompt"] for r in ev}),"prompt_flags_0p70":prompt_flags,"code_flags_0p85":code_flags,"ast_proxy_exact":ast_matches,"distance_records":distances,"distance_bucket_counts":dict(Counter(r["distance_bucket"] for r in distances)),"exact_prior_eval_prompt_reuse":exact_prior,"prior_eval_prompt_flags_0p70":prior_prompt_flags,"prior_eval_code_flags_0p90":prior_code_flags,"prior_eval_code_flags_0p98":prior_flags}
    cross_prompt=set(r["prompt"] for r in datasets[("a","training")]["rows"]+datasets[("a","eval")]["rows"]) & set(r["prompt"] for r in datasets[("b","training")]["rows"]+datasets[("b","eval")]["rows"])
    if cross_prompt: raise ValueError("Cross-capability prompt reuse")
    if failures or rejects: raise ValueError({"reference_failures":failures,"code_rejects":rejects})
    payload={"counts":{k:len(d["rows"]) for k,d in ((f"{cap}_{split}",datasets[(cap,split)]) for cap in "ab" for split in ("training","eval"))},"verification":verified,"structural_audit":audits,"cross_capability_exact_prompt_reuse":0,"sealed_holdout_opened":False,"compiler_sha256":file_sha256(args.jar),"file_sha256":{str(p).replace('\\','/'):file_sha256(p) for p in paths},"canonical_sha256":{str(p).replace('\\','/'):canonical_sha256(load_json(p)) for p in paths}}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"counts":payload["counts"],"verified":{k:sum(r["score"]["hidden_pass"] for r in v) for k,v in verified.items()},"structural_summary":{k:{"prompt_flags":len(v["prompt_flags_0p70"]),"code_flags":len(v["code_flags_0p85"]),"ast_matches":len(v["ast_proxy_exact"]),"distances":v["distance_bucket_counts"],"prior_prompt_flags":len(v["prior_eval_prompt_flags_0p70"]),"prior_code_flags":len(v["prior_eval_code_flags_0p90"]),"prior_0p98_flags":len(v["prior_eval_code_flags_0p98"])} for k,v in audits.items()}},indent=2))

if __name__=="__main__": main()
