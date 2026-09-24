"""Freeze paired, family-balanced DEV1 exposure order without loading a model."""

from __future__ import annotations

import json
import random
from pathlib import Path


SEEDS = (20270925, 20271013, 20271119)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/protocols/phase3c_dev1_schedule.json"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    conditions = {}
    for name in ("dense", "diverse"):
        rows = json.loads((ROOT / f"data/phase3c_dev1/a_{name}_training_examples.json").read_text(encoding="utf-8"))
        ids = {family: [r["example_id"] for r in rows if r["family"] == family]
               for family in ("numeric_iteration", "array_reduction")}
        if len(rows) != 60 or any(len(group) != 30 for group in ids.values()):
            raise ValueError(name)
        conditions[name] = ids
    schedule = {"phase": "3C-DEV1", "seeds": list(SEEDS), "epochs": 3,
                "slots_per_epoch": 60, "optimizer_steps_per_epoch": 8,
                "policy": "Each seed/epoch uses the same shuffled numeric/array slot mask in both conditions; shuffle the 30 within-family IDs independently and deterministically; each ID occurs once per epoch.",
                "by_seed": {}}
    for seed in SEEDS:
        schedule["by_seed"][str(seed)] = []
        for epoch in range(3):
            families = ["numeric_iteration"] * 30 + ["array_reduction"] * 30
            random.Random(seed + epoch * 100003).shuffle(families)
            record = {"epoch": epoch + 1, "slot_families": families}
            for condition in ("dense", "diverse"):
                pools = {family: list(ids) for family, ids in conditions[condition].items()}
                for family_index, family in enumerate(pools):
                    random.Random(seed + epoch * 100003 + 1009 + family_index * 7919).shuffle(pools[family])
                cursors = {family: 0 for family in pools}
                exposure = []
                for family in families:
                    exposure.append(pools[family][cursors[family]])
                    cursors[family] += 1
                if len(exposure) != 60 or len(set(exposure)) != 60:
                    raise ValueError((seed, epoch, condition))
                record[f"{condition}_example_ids"] = exposure
            schedule["by_seed"][str(seed)].append(record)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(schedule, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"seeds": list(SEEDS), "conditions": 2, "slots_per_seed_condition": 180,
                      "steps_per_seed_condition": 24}))


if __name__ == "__main__":
    main()
