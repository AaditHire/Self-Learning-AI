"""Freeze one 20% replay schedule before any Phase 3C model run."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path


SEEDS = (20260925, 20261013, 20261119)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a-data", type=Path, default=Path("data/phase3c/a_training_examples.json"))
    parser.add_argument("--b-data", type=Path, default=Path("data/phase3c/b_training_examples.json"))
    parser.add_argument("--output", type=Path, default=Path("research/protocols/phase3c_replay_schedule.json"))
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    a = json.loads(args.a_data.read_text(encoding="utf-8"))
    b = json.loads(args.b_data.read_text(encoding="utf-8"))
    if len(a) != 60 or len(b) != 60:
        raise ValueError("Expected 60 examples per capability")
    schedule = {"phase": "3C", "seeds": list(SEEDS), "epochs": 3,
                "micro_batches_per_epoch": 60, "optimizer_steps_per_epoch": 8,
                "replay_fraction": .20,
                "method": "Shuffle B once per seed/epoch. Replace six fixed slots from each B subskill with six disjoint A IDs from each A subskill. Keep naive B order at all unreplaced slots.",
                "by_seed": {}}
    for seed in SEEDS:
        a_groups = {family: [r["example_id"] for r in a if r["family"] == family]
                    for family in ("numeric_iteration", "array_reduction")}
        for index, (family, ids) in enumerate(a_groups.items()):
            if len(ids) != 30:
                raise ValueError(family)
            random.Random(seed + 1009 + index * 7919).shuffle(ids)
        epochs = []
        for epoch in range(3):
            b_rows = list(b)
            random.Random(seed + epoch * 100003).shuffle(b_rows)
            naive = [r["example_id"] for r in b_rows]
            positions = []
            rng = random.Random(seed + epoch * 100003 + 31337)
            for family in ("string_transform", "field_processing"):
                candidates = [i for i, row in enumerate(b_rows) if row["family"] == family]
                if len(candidates) != 30:
                    raise ValueError(family)
                positions.extend(rng.sample(candidates, 6))
            positions.sort()
            replay_a = a_groups["numeric_iteration"][epoch*6:(epoch+1)*6] + a_groups["array_reduction"][epoch*6:(epoch+1)*6]
            random.Random(seed + epoch * 100003 + 65537).shuffle(replay_a)
            replay = list(naive)
            for position, example_id in zip(positions, replay_a):
                replay[position] = example_id
            if len(replay) != 60 or len(set(replay)) != 60:
                raise ValueError("Replay exposure count or uniqueness")
            if Counter(x.startswith("P3C-A-") for x in replay) != Counter({False: 48, True: 12}):
                raise ValueError("Replay mix")
            epochs.append({"epoch": epoch + 1, "naive_example_ids": naive,
                           "replay_example_ids": replay,
                           "replaced_b_positions_zero_based": positions,
                           "replayed_a_example_ids": replay_a})
        all_a = [item for epoch in epochs for item in epoch["replayed_a_example_ids"]]
        if len(all_a) != 36 or len(set(all_a)) != 36:
            raise ValueError("A replay reuse")
        schedule["by_seed"][str(seed)] = epochs
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(schedule, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"seeds": SEEDS, "epochs": 3, "slots_per_epoch": 60,
                      "A_replay_slots_per_epoch": 12, "B_steps_per_branch": 24}))


if __name__ == "__main__":
    main()
