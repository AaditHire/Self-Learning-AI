from __future__ import annotations

import json
from pathlib import Path

from validate_phase2b_data import file_sha256


def main():
    path=Path("research/protocols/phase3a_config.json")
    if path.exists(): raise FileExistsError(path)
    previous=json.loads(Path("research/protocols/phase2b_config.json").read_text(encoding="utf-8"))
    validation=json.loads(Path("research/results/EXP-0027/data_validation.json").read_text(encoding="utf-8"))
    if any(not r["score"]["hidden_pass"] for rows in validation["verification"].values() for r in rows): raise ValueError("Unverified data")
    if any(v["prior_eval_code_flags_0p98"] for v in validation["structural_audit"].values()): raise ValueError("Prior evaluation near duplicate")
    seeds=[20260923,20261011,20261117]
    data={"a_training_examples":"data/phase3a/a_training_examples.json","a_training_tests":"data/phase3a/a_training_hidden_tests.json","b_training_examples":"data/phase3a/b_training_examples.json","b_training_tests":"data/phase3a/b_training_hidden_tests.json","eval_a_tasks":"benchmark/phase3a/a_eval_tasks.json","eval_a_tests":"benchmark/phase3a/a_eval_hidden_tests.json","eval_a_references":"benchmark/phase3a/a_eval_references.json","eval_b_tasks":"benchmark/phase3a/b_eval_tasks.json","eval_b_tests":"benchmark/phase3a/b_eval_hidden_tests.json","eval_b_references":"benchmark/phase3a/b_eval_references.json","general_regression":"benchmark/phase2b/general_regression.json","validation":"research/results/EXP-0027/data_validation.json"}
    training={k:v for k,v in previous["training"].items() if k not in ("adapter_outputs",)}
    training["adapter_outputs"]={str(s):{"A":f"research/adapters/candidates/c{5+2*i:04d}-phase3a-a-seed-{s}","B":f"research/adapters/candidates/c{6+2*i:04d}-phase3a-a-to-b-seed-{s}"} for i,s in enumerate(seeds)}
    training["record_outputs"]={str(s):{"A":f"research/results/EXP-{28+2*i:04d}/training.json","B":f"research/results/EXP-{29+2*i:04d}/training.json"} for i,s in enumerate(seeds)}
    training["checkpoint_selection"]="Final epoch a priori for both stages; no performance-based selection"
    training["stage_b_policy"]="Continue the exact seed-matched A LoRA weights, fresh optimizer and scheduler, B examples only; no A replay"
    cfg={"phase":"3A-two-stage-naive-sequential-learning-forgetting-baseline","start_commit":"1ded323e036cd93813ab165210e0c3dcf32616df","scientific_status":"sequential acquisition/forgetting baseline; not an anti-forgetting intervention","model":previous["model"],"capabilities":{"A":{"definition":"numeric iterative and array-reduction GOCO programs","subskills":["numeric_iteration","array_reduction"]},"B":{"definition":"string transformations and delimited-field processing GOCO programs","subskills":["string_transform","field_processing"]}},"data":data,"prompt":{"system":previous["prompt"]["system"],"user_template":previous["prompt"]["user_template"],"context":"same no-documentation prompt at all stages; no search"},"training":training,"seeds":seeds,"evaluation":{"do_sample":False,"num_beams":1,"max_input_tokens":8192,"max_new_tokens":512,"regression_max_new_tokens":32,"retry_policy":"none","manual_repair":False,"compiler_timeout_seconds":3,"output_limit_bytes_per_stream":65536,"primary_metric":"task-level hidden-test pass@1","base_seed":seeds[0],"required_conditions":["base_eval_a","a_eval_a","a_eval_b","a_to_b_eval_b","a_to_b_eval_a","base_regression","a_regression","a_to_b_regression"]},"analysis":{"primary_forgetting":"A EVAL_A pass@1 immediately after A training minus seed-matched A->B EVAL_A pass@1","absolute_forgetting_unit":"percentage points","relative_retention":"A->B EVAL_A pass rate divided by A EVAL_A pass rate, undefined if denominator zero","paired_transitions":["pass->pass","pass->fail","fail->pass","fail->fail"],"unit":"32 paired EVAL_A tasks per seed; report each seed, mean and range; seeds are not independent task instances","bootstrap_samples":10000,"bootstrap_seed":20261219,"measurable_forgetting_rule":"descriptive: mean paired drop > 0 and paired task bootstrap 95% CI lower bound > 0; also report individual seed directions; if A acquisition is zero, forgetting is not interpretable","stronger_wording":"catastrophic only for large systematic degradation with substantial A acquisition, not for every negative change"},"input_file_hashes":{},"prohibitions":["A examples in B stage", "replay, EWC, adapter isolation, STABLE, NoRA, gating or other anti-forgetting interventions","base-weight modification or adapter merge","post-freeze data, prompt, seed, hyperparameter or checkpoint selection using evaluation results","sealed final-paper holdout access"]}
    frozen=list(data.values())+["research/results/EXP-0027/structural_overlap_manual_review.md","research/protocols/phase3a_protocol.md",cfg["prompt"]["system"],cfg["prompt"]["user_template"],"scripts/build_phase3a_data.py","scripts/validate_phase3a_data.py","scripts/train_phase3a_qlora.py","scripts/run_phase3a_evaluation.py","scripts/analyze_phase3a.py","scripts/train_phase2a_qlora.py","scripts/run_phase2a_evaluation.py"]
    cfg["input_file_hashes"]={p:file_sha256(Path(p)) for p in frozen}
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(cfg,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"config_sha256":file_sha256(path),"seeds":seeds,"inputs":len(frozen)},indent=2))

if __name__=="__main__": main()
