from __future__ import annotations

import json
import shutil
from pathlib import Path

from validate_phase2b_data import file_sha256


def main():
    cfg_path=Path("research/protocols/phase3b_config.json")
    validation_path=Path("research/results/EXP-0036/data_validation.json")
    source_validation=Path(".runtime/phase3b/data_validation_attempt_03.json")
    if cfg_path.exists() or validation_path.exists(): raise FileExistsError("Phase 3B already frozen")
    validation=json.loads(source_validation.read_text(encoding="utf-8"))
    if validation["reference_failures"] or validation["code_rejects_0p98"] or any(not r["score"]["hidden_pass"] for rows in validation["verification"].values() for r in rows): raise ValueError("Data audit failed")
    previous=json.loads(Path("research/protocols/phase3a_config.json").read_text(encoding="utf-8"))
    schedule=json.loads(Path("research/protocols/phase3b_replay_schedule.json").read_text(encoding="utf-8"))
    seeds=[20260924,20261012,20261118]
    if schedule["seeds"]!=seeds or schedule["replay_fraction"]!=.2: raise ValueError("Replay schedule")
    data={"a_training_examples":"data/phase3b/a_training_examples.json","a_training_tests":"data/phase3b/a_training_hidden_tests.json","b_training_examples":"data/phase3b/b_training_examples.json","b_training_tests":"data/phase3b/b_training_hidden_tests.json","eval_a_tasks":"benchmark/phase3b/a_eval_tasks.json","eval_a_tests":"benchmark/phase3b/a_eval_hidden_tests.json","eval_a_references":"benchmark/phase3b/a_eval_references.json","eval_b_tasks":"benchmark/phase3b/b_eval_tasks.json","eval_b_tests":"benchmark/phase3b/b_eval_hidden_tests.json","eval_b_references":"benchmark/phase3b/b_eval_references.json","general_regression":"benchmark/phase2b/general_regression.json","replay_schedule":"research/protocols/phase3b_replay_schedule.json","validation":str(validation_path).replace('\\','/')}
    for path,expected in validation["file_sha256"].items():
        if file_sha256(Path(path))!=expected: raise ValueError(f"Validated input changed: {path}")
    train={k:v for k,v in previous["training"].items() if k not in ("adapter_outputs","record_outputs","stage_b_policy")}
    train["checkpoint_selection"]="Final epoch a priori, no performance-based selection"
    train["stage_b_policy"]="Naive and 20% replay branch from same seed-matched A adapter; fresh optimizer and scheduler, fixed 60 examples and 24 optimizer steps per branch"
    cfg={"phase":"3B-fixed-budget-20-percent-experience-replay","start_commit":"000311f724155d0a643d99bff22c6cac848a15be","preregistration_status":"frozen before gradients/evaluations","runtime_root":".runtime/phase3b","compiler_sha256":validation["compiler_sha256"],"model":previous["model"],"capabilities":previous["capabilities"],"data":data,"prompt":previous["prompt"],"training":train,"seeds":seeds,"evaluation":previous["evaluation"]|{"base_seed":seeds[0],"required_conditions":["base_A","base_B","base_regression","A_A","A_B","A_regression","naive_A","naive_B","naive_regression","replay_A","replay_B","replay_regression"]},"analysis":{"primary_metric":"unweighted three-seed mean replay post-B EVAL_A pass@1 minus naive post-B EVAL_A pass@1","pass_a_gain_pp":20,"minimum_b_fraction_of_naive":.75,"require_naive_b_positive":True,"max_regression_drop_items_each_seed_against_naive_and_base":9,"task_cluster_bootstrap_draws":10000,"task_cluster_bootstrap_seed":20261220},"input_file_hashes":{},"prohibitions":["post-freeze data, seed, example mix, prompt, hyperparameter, checkpoint or gate changes using model results","EWC, NoRA, adapter isolation, gating, STABLE or any other method","base-weight modification or adapter merge","sealed final-paper holdout access","writes to GOCO product repository","mutable runtime under Git/LFS"]}
    validation_path.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source_validation,validation_path)
    frozen=list(data.values())+["research/results/EXP-0036/structural_overlap_manual_review.md","research/protocols/phase3b_protocol.md",cfg["prompt"]["system"],cfg["prompt"]["user_template"],"scripts/build_phase3b_data.py","scripts/validate_phase3b_data.py","scripts/build_phase3b_schedule.py","scripts/train_phase3b_qlora.py","scripts/run_phase3b_evaluation.py","scripts/train_phase2a_qlora.py","scripts/run_phase2a_evaluation.py"]
    cfg["input_file_hashes"]={p:file_sha256(Path(p)) for p in dict.fromkeys(frozen)}
    cfg_path.write_text(json.dumps(cfg,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"config_sha256":file_sha256(cfg_path),"validation_sha256":file_sha256(validation_path),"seeds":seeds,"inputs":len(cfg["input_file_hashes"])},indent=2))


if __name__=="__main__": main()
