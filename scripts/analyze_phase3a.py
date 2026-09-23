from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from train_phase2a_qlora import sha256


def filename(condition,suite,seed):
    return f"{condition}_{suite}"+(f"_seed_{seed}" if seed is not None else "")+".json"


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--config",type=Path,required=True); parser.add_argument("--eval-dir",type=Path,required=True); parser.add_argument("--regression-dir",type=Path,required=True); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    cfg=json.loads(args.config.read_text(encoding="utf-8")); seeds=cfg["seeds"]
    def load(condition,suite,seed):
        path=(args.regression_dir if suite=="regression" else args.eval_dir)/filename(condition,suite,seed)
        row=json.loads(path.read_text(encoding="utf-8"))
        if row["config_sha256"]!=sha256(args.config) or row["condition"]!=condition or row["suite"]!=suite or row["seed"]!=seed: raise ValueError(path)
        return row
    base_a=load("base","A",None); base_reg=load("base","regression",None)
    rows=[]; deltas_by_task=defaultdict(list)
    for seed in seeds:
        a_a=load("A","A",seed); a_b=load("A","B",seed)
        b_a=load("AtoB","A",seed); b_b=load("AtoB","B",seed)
        a_reg=load("A","regression",seed); b_reg=load("AtoB","regression",seed)
        before={r["task_id"]:r for r in a_a["records"]}; after={r["task_id"]:r for r in b_a["records"]}
        if set(before)!=set(after) or len(before)!=32: raise ValueError("A paired tasks mismatch")
        transition=Counter(); family=defaultdict(lambda:{"before":0,"after":0,"lost":0,"gained":0,"n":0})
        for tid,pre in before.items():
            post=after[tid]; bp=bool(pre["hidden_pass"]); ap=bool(post["hidden_pass"])
            transition[f"{'pass' if bp else 'fail'}->{'pass' if ap else 'fail'}"]+=1
            f=family[pre["family"]]; f["before"]+=bp; f["after"]+=ap; f["lost"]+=bp and not ap; f["gained"]+=not bp and ap; f["n"]+=1
            deltas_by_task[tid].append(int(bp)-int(ap))
        a_rate=a_a["summary"]["overall"]["hidden_pass"]
        post_rate=b_a["summary"]["overall"]["hidden_pass"]
        rows.append({"seed":seed,"base_eval_a":base_a["summary"]["overall"]["hidden_pass"],"a_eval_a":a_rate,"a_eval_b":a_b["summary"]["overall"]["hidden_pass"],"a_to_b_eval_b":b_b["summary"]["overall"]["hidden_pass"],"a_to_b_eval_a":post_rate,"forgetting_pp":100*(a_rate-post_rate),"relative_retention":post_rate/a_rate if a_rate else None,"b_gain_pp":100*(b_b["summary"]["overall"]["hidden_pass"]-a_b["summary"]["overall"]["hidden_pass"]),"paired_transitions":dict(transition),"by_family":dict(family),"failure_taxonomy":{"a_eval_a":a_a["summary"]["overall"]["failure_taxonomy"],"a_eval_b":a_b["summary"]["overall"]["failure_taxonomy"],"a_to_b_eval_a":b_a["summary"]["overall"]["failure_taxonomy"],"a_to_b_eval_b":b_b["summary"]["overall"]["failure_taxonomy"]},"regression":{"base":base_reg["summary"],"a":a_reg["summary"],"a_to_b":b_reg["summary"]}})
    task_ids=sorted(deltas_by_task)
    if any(len(deltas_by_task[t])!=len(seeds) for t in task_ids): raise ValueError("Task seed mismatch")
    rng=random.Random(cfg["analysis"]["bootstrap_seed"]); samples=[]
    for _ in range(cfg["analysis"]["bootstrap_samples"]):
        sample=[rng.choice(task_ids) for _ in task_ids]
        samples.append(100*statistics.mean(statistics.mean(deltas_by_task[t]) for t in sample))
    samples.sort(); lower=samples[int(.025*len(samples))]; upper=samples[int(.975*len(samples))-1]
    aggregate={"mean_forgetting_pp":statistics.mean(r["forgetting_pp"] for r in rows),"range_forgetting_pp":[min(r["forgetting_pp"] for r in rows),max(r["forgetting_pp"] for r in rows)],"paired_task_bootstrap_95_ci_pp":[lower,upper],"measurable_forgetting_by_preregistered_rule":statistics.mean(r["forgetting_pp"] for r in rows)>0 and lower>0 and all(r["a_eval_a"]>0 for r in rows),"mean_a_acquisition_pp":statistics.mean(100*(r["a_eval_a"]-r["base_eval_a"]) for r in rows),"mean_b_acquisition_pp":statistics.mean(r["b_gain_pp"] for r in rows),"mean_relative_retention":statistics.mean(r["relative_retention"] for r in rows if r["relative_retention"] is not None) if any(r["relative_retention"] is not None for r in rows) else None,"task_level_mean_deltas":{t:statistics.mean(deltas_by_task[t]) for t in task_ids}}
    result={"phase":"3A","config_sha256":sha256(args.config),"seeds":seeds,"by_seed":rows,"aggregate":aggregate}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"by_seed":[{k:v for k,v in r.items() if k in ("seed","a_eval_a","a_eval_b","a_to_b_eval_a","a_to_b_eval_b","forgetting_pp","relative_retention","paired_transitions")} for r in rows],"aggregate":{k:v for k,v in aggregate.items() if k!="task_level_mean_deltas"}},indent=2))

if __name__=="__main__": main()
