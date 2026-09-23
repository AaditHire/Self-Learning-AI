from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    config_path=Path("research/protocols/phase3a_config.json")
    cfg=read(config_path); config_hash=digest(config_path)
    for name,expected in cfg["input_file_hashes"].items():
        if digest(Path(name))!=expected: raise ValueError(f"Frozen input changed: {name}")
    base_path=Path(cfg["model"]["local_path"])
    for name,expected in cfg["model"]["weight_file_sha256"].items():
        if digest(base_path/name)!=expected: raise ValueError(f"Base changed: {name}")
    def evaluation(condition: str,suite: str,seed: int|None):
        directory=Path("research/results/EXP-0035" if suite=="regression" else "research/results/EXP-0034")
        name=f"{condition}_{suite}"+(f"_seed_{seed}" if seed is not None else "")+".json"
        result=read(directory/name)
        expected_n=64 if suite=="regression" else 32
        if result["config_sha256"]!=config_hash or result["condition"]!=condition or result["suite"]!=suite or result["seed"]!=seed or len(result["records"])!=expected_n: raise ValueError(name)
        pass_key="passed" if suite=="regression" else "hidden_pass"
        count=sum(bool(r[pass_key]) for r in result["records"])
        if suite=="regression":
            if count!=result["summary"]["correct"]: raise ValueError(name)
        elif count!=result["summary"]["overall"]["hidden_pass_count"]: raise ValueError(name)
        if len({r["task_id"] for r in result["records"]})!=expected_n: raise ValueError(name)
        return result,count
    base_a,base_a_count=evaluation("base","A",None)
    _,base_regression=evaluation("base","regression",None)
    if base_a_count!=0 or base_regression!=47: raise ValueError("Base counts")
    seed_rows=[]
    for seed in cfg["seeds"]:
        record_paths=cfg["training"]["record_outputs"][str(seed)]
        a=read(Path(record_paths["A"])); b=read(Path(record_paths["B"]))
        for stage,row in (("A",a),("B",b)):
            if row["config_sha256"]!=config_hash or row["stage"]!=stage or row["seed"]!=seed or row["training"]["optimizer_steps"]!=24 or row["lineage"]["replay_examples"]!=0 or row["lineage"]["base_weight_hashes_before"]!=row["lineage"]["base_weight_hashes_after"]: raise ValueError((seed,stage))
            adapter_path=Path(cfg["training"]["adapter_outputs"][str(seed)][stage])
            for name,expected in row["adapter"]["file_hashes"].items():
                if digest(adapter_path/name)!=expected: raise ValueError((seed,stage,name))
        if b["lineage"]["parent_adapter_file_hashes"]!=a["adapter"]["file_hashes"]: raise ValueError((seed,"parent mismatch"))
        a_a,a_before=evaluation("A","A",seed)
        _,b_before=evaluation("A","B",seed)
        _,a_regression=evaluation("A","regression",seed)
        _,b_after=evaluation("AtoB","B",seed)
        b_a,a_after=evaluation("AtoB","A",seed)
        _,b_regression=evaluation("AtoB","regression",seed)
        pre={r["task_id"]:r["hidden_pass"] for r in a_a["records"]}
        post={r["task_id"]:r["hidden_pass"] for r in b_a["records"]}
        if set(pre)!=set(post): raise ValueError((seed,"paired ID mismatch"))
        transitions=dict(Counter(("pass" if pre[k] else "fail")+"->"+("pass" if post[k] else "fail") for k in pre))
        if a_before!=sum(pre.values()) or a_after!=sum(post.values()): raise ValueError((seed,"paired count mismatch"))
        seed_rows.append({"seed":seed,"a_before":a_before,"a_after":a_after,"b_before":b_before,"b_after":b_after,"regression_base":base_regression,"regression_a":a_regression,"regression_a_to_b":b_regression,"transitions":transitions,"adapter_parent_verified":True,"base_verified":True})
    analysis=read(Path("research/results/PHASE_3A/analysis.json"))
    if analysis["config_sha256"]!=config_hash or [r["seed"] for r in analysis["by_seed"]]!=cfg["seeds"]: raise ValueError("Analysis lineage")
    for row,analysed in zip(seed_rows,analysis["by_seed"]):
        if abs(analysed["forgetting_pp"]-100*(row["a_before"]-row["a_after"])/32)>1e-9 or analysed["paired_transitions"]!=row["transitions"]: raise ValueError("Analysis mismatch")
    out={"phase":"3A","config_sha256":config_hash,"frozen_input_hashes_verified":len(cfg["input_file_hashes"]),"base_weight_shards_verified":len(cfg["model"]["weight_file_sha256"]),"training_runs_verified":6,"evaluation_conditions_verified":20,"seeds":seed_rows,"all_checks_passed":True}
    path=Path("research/results/PHASE_3A/completion_verification.json")
    if path.exists(): raise FileExistsError(path)
    path.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"all_checks_passed":True,"training_runs":6,"evaluation_conditions":20,"seed_counts":seed_rows},indent=2))


if __name__=="__main__": main()
