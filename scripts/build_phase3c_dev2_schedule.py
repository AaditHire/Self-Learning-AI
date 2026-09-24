"""Freeze paired DEV2 A-only exposure slots without loading a model."""

import json
import random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SEEDS=(20270925,20271013,20271119)
OUT=ROOT/"research/protocols/phase3c_dev2_schedule.json"


def main():
    if OUT.exists(): raise FileExistsError(OUT)
    rows={c:json.loads((ROOT/f"data/phase3c_dev2/a_{c}_training_examples.json").read_text(encoding="utf-8")) for c in ("isolated","composition")}
    indexed={c:{(r["family"],r["archetype"],int(r["example_id"].split("-")[-1])):r["example_id"] for r in vals} for c,vals in rows.items()}
    assert len(indexed["isolated"])==len(indexed["composition"])==60 and set(indexed["isolated"])==set(indexed["composition"])
    schedule={"phase":"3C-DEV2","seeds":list(SEEDS),"epochs":3,"slots_per_epoch":60,
              "optimizer_steps_per_epoch":8,"policy":"Each paired slot has the same subskill, predicate pair and constant variant; each condition uses its own independently initialized adapter/optimizer.",
              "by_seed":{}}
    keys=sorted(indexed["isolated"])
    for seed in SEEDS:
        epochs=[]
        for epoch in range(1,4):
            order=list(keys)
            random.Random(seed+100003*epoch).shuffle(order)
            assert len(order)==len(set(order))==60
            record={"epoch":epoch,"slot_families":[x[0] for x in order],
                    "slot_archetypes":[x[1] for x in order],
                    "slot_constant_variants":[x[2] for x in order]}
            for c in indexed:
                record[c+"_example_ids"]=[indexed[c][key] for key in order]
            epochs.append(record)
        schedule["by_seed"][str(seed)]=epochs
    OUT.write_text(json.dumps(schedule,indent=2)+"\n",encoding="utf-8")
    print("3 paired seeds; 180 slots and 24 steps per seed-condition")

if __name__=="__main__": main()
