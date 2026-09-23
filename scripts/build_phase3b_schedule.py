from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path


SEEDS=(20260924,20261012,20261118)


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--a-data",type=Path,default=Path("data/phase3b/a_training_examples.json")); parser.add_argument("--b-data",type=Path,default=Path("data/phase3b/b_training_examples.json")); parser.add_argument("--output",type=Path,default=Path("research/protocols/phase3b_replay_schedule.json")); args=parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    a=json.loads(args.a_data.read_text(encoding="utf-8")); b=json.loads(args.b_data.read_text(encoding="utf-8"))
    if len(a)!=60 or len(b)!=60: raise ValueError("Expected 60 examples per capability")
    schedule={"phase":"3B","method":"for each seed: separately shuffle 30 A IDs in each subskill; use six disjoint IDs per subskill per epoch; independently shuffle all 60 B IDs per epoch; replace six randomly selected B positions per B subskill with a shuffled set of the 12 A IDs; same B order and 60 positions in the naive arm","seeds":list(SEEDS),"epochs":3,"micro_batches_per_epoch":60,"optimizer_steps_per_epoch":8,"replay_fraction":.20,"by_seed":{}}
    for seed in SEEDS:
        a_groups={family:[r["example_id"] for r in a if r["family"]==family] for family in ("numeric_iteration","array_reduction")}
        for idx,(family,ids) in enumerate(a_groups.items()):
            if len(ids)!=30: raise ValueError(family)
            random.Random(seed+1009+idx*7919).shuffle(ids)
        by_epoch=[]
        for epoch in range(3):
            b_rows=list(b)
            random.Random(seed+epoch*100003).shuffle(b_rows)
            b_ids=[r["example_id"] for r in b_rows]
            indices=[]
            position_rng=random.Random(seed+epoch*100003+31337)
            for family in ("string_transform","field_processing"):
                candidates=[i for i,r in enumerate(b_rows) if r["family"]==family]
                if len(candidates)!=30: raise ValueError(family)
                indices.extend(position_rng.sample(candidates,6))
            indices.sort()
            a_ids=a_groups["numeric_iteration"][epoch*6:(epoch+1)*6]+a_groups["array_reduction"][epoch*6:(epoch+1)*6]
            random.Random(seed+epoch*100003+65537).shuffle(a_ids)
            replay_ids=list(b_ids)
            for index,a_id in zip(indices,a_ids): replay_ids[index]=a_id
            if len(replay_ids)!=60 or len(set(replay_ids))!=60 or Counter(x.startswith("P3B-A-") for x in replay_ids)!=Counter({False:48,True:12}): raise ValueError("Replay exposure")
            by_epoch.append({"epoch":epoch+1,"naive_example_ids":b_ids,"replay_example_ids":replay_ids,"replaced_b_positions_zero_based":indices,"replayed_a_example_ids":a_ids})
        all_a=[x for e in by_epoch for x in e["replayed_a_example_ids"]]
        if len(all_a)!=36 or len(set(all_a))!=36: raise ValueError("A sample reuse")
        schedule["by_seed"][str(seed)]=by_epoch
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(schedule,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"seeds":SEEDS,"epochs":3,"examples_per_epoch":60,"replay_per_epoch":12,"total_optimizer_steps":24},indent=2))


if __name__=="__main__": main()
