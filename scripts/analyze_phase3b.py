from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from train_phase2a_qlora import directory_hashes, sha256


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--config",type=Path,required=True); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    cfg=json.loads(args.config.read_text(encoding="utf-8")); root=Path(cfg["runtime_root"])
    seeds=cfg["seeds"]; condition_names=("A","naive","replay")
    schedule=json.loads(Path(cfg["data"]["replay_schedule"]).read_text(encoding="utf-8"))["by_seed"]
    records={}; training={}
    expected_ids={suite:{r["task_id"] for r in json.loads(Path(cfg["data"][f"eval_{suite.lower()}_tasks"]).read_text(encoding="utf-8"))} for suite in "AB"}
    expected_ids["regression"]={r["task_id"] for r in json.loads(Path(cfg["data"]["general_regression"]).read_text(encoding="utf-8"))}
    for condition in ("base",)+condition_names:
        for seed in ([None] if condition=="base" else seeds):
            label="base" if seed is None else str(seed)
            for suite in ("A","B","regression"):
                path=root/"evaluations"/label/f"{condition}_{suite.lower()}.json"
                obj=json.loads(path.read_text(encoding="utf-8"))
                if obj["config_sha256"]!=sha256(args.config) or obj["condition"]!=condition or obj["seed"]!=seed or obj["suite"]!=suite: raise ValueError(f"Evaluation metadata mismatch: {path}")
                rows={r["task_id"]:r for r in obj["records"]}
                if len(rows)!=len(obj["records"]) or set(rows)!=expected_ids[suite]: raise ValueError(f"Evaluation task mismatch: {path}")
                records[(condition,seed,suite)]=rows
    for seed in seeds:
        for condition in condition_names:
            path=root/"training"/str(seed)/f"{condition}.json"
            obj=json.loads(path.read_text(encoding="utf-8"))
            if obj["config_sha256"]!=sha256(args.config) or obj["seed"]!=seed or obj["condition"]!=condition: raise ValueError(f"Training metadata mismatch: {path}")
            if obj["training"]["optimizer_steps"]!=24 or obj["training"]["expected_optimizer_steps"]!=24: raise ValueError(f"Compute mismatch: {path}")
            if any(not isinstance(x["mean_micro_loss"],(int,float)) for x in obj["training"]["log"]): raise ValueError(f"Invalid loss: {path}")
            expected_a={"A":60,"naive":0,"replay":12}[condition]
            expected_b={"A":0,"naive":60,"replay":48}[condition]
            if obj["data"]["a_examples_per_epoch"]!=expected_a or obj["data"]["b_examples_per_epoch"]!=expected_b: raise ValueError(f"Exposure mismatch: {path}")
            adapter_path=Path(obj["adapter"]["path"])
            if directory_hashes(adapter_path)!=obj["adapter"]["file_hashes"]: raise ValueError(f"Adapter files changed: {adapter_path}")
            if condition!="A":
                frozen=[e[f"{condition}_example_ids"] for e in schedule[str(seed)]]
                if obj["lineage"]["exposures_by_epoch"]!=frozen: raise ValueError(f"Schedule mismatch: {path}")
            training[(condition,seed)]=obj
        a_hash=training[("A",seed)]["adapter"]["file_hashes"]
        for condition in ("naive","replay"):
            if training[(condition,seed)]["lineage"]["parent_adapter_file_hashes"]!=a_hash: raise ValueError(f"A parent mismatch: {seed}/{condition}")
    def count(condition,seed,suite):
        field="passed" if suite=="regression" else "hidden_pass"
        return sum(bool(r[field]) for r in records[(condition,seed,suite)].values())
    scores={str(seed):{condition:{suite:count(condition,seed,suite) for suite in ("A","B","regression")} for condition in condition_names} for seed in seeds}
    base={suite:count("base",None,suite) for suite in ("A","B","regression")}
    means={condition:{suite:sum(scores[str(seed)][condition][suite] for seed in seeds)/(len(seeds)*(64 if suite=="regression" else 32)) for suite in ("A","B","regression")} for condition in condition_names}
    a_gain=means["replay"]["A"]-means["naive"]["A"]
    b_fraction=means["replay"]["B"]/means["naive"]["B"] if means["naive"]["B"]>0 else None
    max_drop=cfg["analysis"]["max_regression_drop_items_each_seed_against_naive_and_base"]
    regression_safe=all(scores[str(seed)]["replay"]["regression"]>=scores[str(seed)]["naive"]["regression"]-max_drop and scores[str(seed)]["replay"]["regression"]>=base["regression"]-max_drop for seed in seeds)
    gates={"a_gain_at_least_20pp":a_gain>=cfg["analysis"]["pass_a_gain_pp"]/100-1e-12,"naive_b_positive_and_replay_at_least_75pct":b_fraction is not None and b_fraction>=cfg["analysis"]["minimum_b_fraction_of_naive"]-1e-12,"non_goco_no_severe_regression":regression_safe}
    transitions={}; forgetting={}; subskills={}; taxonomy={}
    for seed in seeds:
        k=str(seed); transitions[k]={}; forgetting[k]={}; subskills[k]={}; taxonomy[k]={}
        for condition in ("naive","replay"):
            a_before=records[("A",seed,"A")]; a_after=records[(condition,seed,"A")]
            transition=Counter(("pass" if a_before[tid]["hidden_pass"] else "fail")+"->"+("pass" if a_after[tid]["hidden_pass"] else "fail") for tid in expected_ids["A"])
            transitions[k][condition]=dict(sorted(transition.items()))
            before=scores[k]["A"]["A"]; after=scores[k][condition]["A"]
            forgetting[k][condition]={"a_before_count":before,"a_after_count":after,"absolute_forgetting_pp":(before-after)/32*100,"relative_retention":after/before if before else None,"b_acquisition_count":scores[k][condition]["B"]-scores[k]["A"]["B"]}
        for condition in condition_names:
            subskills[k][condition]={suite:{family:{"pass":sum(r["hidden_pass"] for r in records[(condition,seed,suite)].values() if r["family"]==family),"total":sum(r["family"]==family for r in records[(condition,seed,suite)].values())} for family in sorted({r["family"] for r in records[(condition,seed,suite)].values()})} for suite in "AB"}
            taxonomy[k][condition]={suite:dict(sorted(Counter(r["failure_category"] for r in records[(condition,seed,suite)].values()).items())) for suite in "AB"}
    task_ids=sorted(expected_ids["A"]); rng=random.Random(cfg["analysis"]["task_cluster_bootstrap_seed"])
    samples=[]
    for _ in range(cfg["analysis"]["task_cluster_bootstrap_draws"]):
        chosen=[rng.choice(task_ids) for _ in task_ids]
        samples.append(sum(int(records[("replay",seed,"A")][tid]["hidden_pass"])-int(records[("naive",seed,"A")][tid]["hidden_pass"]) for tid in chosen for seed in seeds)/(len(chosen)*len(seeds)))
    samples.sort(); n=len(samples); interval=[samples[int(.025*n)],samples[int(.975*n)-1]]
    result={"phase":"3B","config_sha256":sha256(args.config),"seeds":seeds,"base_counts":base,"per_seed_counts":scores,"mean_pass_rates":means,"primary_a_gain_pp":100*a_gain,"b_fraction_of_naive":b_fraction,"gate_components":gates,"decision":"PASS" if all(gates.values()) else "FAIL","a_forgetting_and_retention":forgetting,"a_task_transitions":transitions,"subskill_counts":subskills,"failure_taxonomy":taxonomy,"task_cluster_bootstrap_95pct_a_gain_pp":[100*x for x in interval],"bootstrap_draws":n,"matched_compute":{"b_micro_examples_per_epoch":60,"b_optimizer_steps_each":24,"naive_b_per_epoch":60,"replay_b_per_epoch":48,"replay_a_per_epoch":12},"sealed_holdout_opened":False}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"base":base,"scores":scores,"gates":gates,"decision":result["decision"],"a_gain_pp":result["primary_a_gain_pp"],"b_fraction":b_fraction,"a_gain_interval_pp":result["task_cluster_bootstrap_95pct_a_gain_pp"]},indent=2))


if __name__=="__main__": main()
