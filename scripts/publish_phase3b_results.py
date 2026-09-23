"""Publish compact immutable Phase 3B records once all runtime conditions pass audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from train_phase2a_qlora import sha256


def dump(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--config",type=Path,required=True); parser.add_argument("--analysis",type=Path,required=True); parser.add_argument("--output-dir",type=Path,required=True); args=parser.parse_args()
    if args.output_dir.exists(): raise FileExistsError(args.output_dir)
    cfg=json.loads(args.config.read_text(encoding="utf-8"))
    analysis=json.loads(args.analysis.read_text(encoding="utf-8"))
    if analysis["config_sha256"]!=sha256(args.config) or analysis["decision"] not in ("PASS","FAIL"): raise ValueError("Incomplete analysis")
    root=Path(cfg["runtime_root"]); evals=[]; tasks=[]; training=[]; source_hashes={}
    for condition in ("base","A","naive","replay"):
        for seed in ([None] if condition=="base" else cfg["seeds"]):
            label="base" if seed is None else str(seed)
            if condition!="base":
                path=root/"training"/label/f"{condition}.json"
                obj=json.loads(path.read_text(encoding="utf-8")); source_hashes[str(path).replace('\\','/')]=sha256(path)
                if obj["config_sha256"]!=sha256(args.config): raise ValueError(path)
                training.append({"seed":seed,"condition":condition,"adapter_sha256":obj["adapter"]["file_hashes"]["adapter_model.safetensors"],"parent_adapter_file_hashes":obj["lineage"]["parent_adapter_file_hashes"],"base_weight_hashes_before":obj["lineage"]["base_weight_hashes_before"],"base_weight_hashes_after":obj["lineage"]["base_weight_hashes_after"],"examples_per_epoch":obj["data"]["examples_per_epoch"],"a_examples_per_epoch":obj["data"]["a_examples_per_epoch"],"b_examples_per_epoch":obj["data"]["b_examples_per_epoch"],"optimizer_steps":obj["training"]["optimizer_steps"],"supervised_tokens":obj["data"]["supervised_tokens"],"training_seconds":obj["training"]["training_seconds"],"peak_gpu_allocated_bytes":obj["training"]["peak_gpu_allocated_bytes"]})
            for suite in ("A","B","regression"):
                path=root/"evaluations"/label/f"{condition}_{suite.lower()}.json"
                obj=json.loads(path.read_text(encoding="utf-8")); source_hashes[str(path).replace('\\','/')]=sha256(path)
                if obj["config_sha256"]!=sha256(args.config) or len(obj["records"])!=(64 if suite=="regression" else 32): raise ValueError(path)
                evals.append({"seed":seed,"condition":condition,"suite":suite,"summary":obj["summary"],"adapter_file_hashes":obj["adapter_file_hashes"],"generation_seconds":obj["hardware"]["generation_seconds"],"output_tokens":obj["hardware"]["output_tokens"]})
                for row in obj["records"]:
                    if suite=="regression":
                        tasks.append({"seed":seed,"condition":condition,"suite":suite,"task_id":row["task_id"],"category":row["category"],"passed":row["passed"]})
                    else:
                        tasks.append({"seed":seed,"condition":condition,"suite":suite,"task_id":row["task_id"],"family":row["family"],"hidden_pass":row["hidden_pass"],"parse_success":row["parse_success"],"compile_success":row["compile_success"],"execution_success":row["execution_success"],"failure_category":row["failure_category"]})
    if len(training)!=9 or len(evals)!=30 or len(tasks)!=1280: raise ValueError((len(training),len(evals),len(tasks)))
    # 3 base suites: 32+32+64 = 128; 27 adapted suites: 9*(32+32+64) = 1152.
    if any(sha256(Path(p))!=h for p,h in cfg["input_file_hashes"].items()): raise ValueError("Frozen input changed")
    if any(t["base_weight_hashes_before"]!=cfg["model"]["weight_file_sha256"] or t["base_weight_hashes_after"]!=cfg["model"]["weight_file_sha256"] for t in training): raise ValueError("Base model changed")
    args.output_dir.mkdir(parents=True)
    dump(args.output_dir/"analysis.json",analysis)
    dump(args.output_dir/"task_outcomes.json",tasks)
    dump(args.output_dir/"evaluation_summary.json",evals)
    dump(args.output_dir/"training_summary.json",training)
    dump(args.output_dir/"provenance.json",{"phase":"3B","preregistration_commit":"002395e","config_sha256":sha256(args.config),"validation_sha256":sha256(Path(cfg["data"]["validation"])),"compiler_sha256":cfg["compiler_sha256"],"base_model_revision":cfg["model"]["revision"],"runtime_source_sha256":source_hashes,"sealed_holdout_opened":False,"mutable_runtime_untracked":True})
    print(json.dumps({"output_dir":str(args.output_dir),"training_records":len(training),"evaluation_records":len(evals),"task_outcomes":len(tasks),"decision":analysis["decision"]},indent=2))


if __name__=="__main__": main()
