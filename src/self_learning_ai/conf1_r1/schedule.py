"""Pure CONF1 C12/C13 schedule functions over immutable ledger metadata.

Import reads only the authorized slot ledger. No model, tokenizer, compiler,
candidate or construction RNG is used. Returned orders are fresh lists.
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from self_learning_ai.conf1_r1.gates_primary import GateStop

ROOT = Path(__file__).resolve().parents[3]
SEEDS = (20280117, 20280223, 20280329, 20280411, 20280507)
CONDITIONS = ("isolated", "composition")
DOMAINS = ("numeric_iteration", "array_reduction")
GROUPS = ("novel_composition", "primitive_sanity", "structural_transfer")
EVALUATION_SEED = 20290307
LEDGER = json.loads((ROOT / "research/protocols/phase3c_conf1_slots.json").read_bytes())
TRAINING_SLOTS = tuple(LEDGER["slots"]["training_paired_slots"])
SLOT_IDS = tuple(sorted((s["slot_id"] for s in TRAINING_SLOTS), key=lambda s: s.encode("utf-8")))
if len(SLOT_IDS) != 60 or len(set(SLOT_IDS)) != 60:
    raise GateStop("C12 requires exactly 60 unique ledger slots")

# Identity metadata only: R1 §7's delta, without exporting superseded role maps.
PRIMARY_TASKS = tuple(
    {"task_id": row["task_id"].replace("-G3-", "-G3P-") if row["family"] == "array_reduction" else row["task_id"],
     "group": row["group"], "family": row["family"],
     "graph": "G3P" if row["family"] == "array_reduction" and row["graph"] == "G3" else row["graph"],
     "block_id": "array_reduction:G3P" if row["family"] == "array_reduction" and row["graph"] == "G3" else row["block_id"]}
    for row in LEDGER["slots"]["primary"]
)
EVALUATION_TASKS = PRIMARY_TASKS + tuple(
    {key: row[key] for key in ("task_id", "group", "family", "structure") if key in row}
    for group in GROUPS[1:] for row in LEDGER["slots"][group]
)
FULL_GROUP_IDS = {
    group: tuple(sorted((r["task_id"] for r in EVALUATION_TASKS if r["group"] == group),
                        key=lambda s: s.encode("utf-8"))) for group in GROUPS
}


def _seed(seed):
    if type(seed) is not int or seed not in SEEDS:
        raise GateStop("unknown paired training seed", {"seed": seed})


def training_schedule(seed):
    """C12: 60 microbatches/epoch, including an unrescaled remainder of four."""
    _seed(seed)
    epochs = []
    for epoch in range(1, 4):
        order = list(SLOT_IDS)
        random.Random(seed + 100003 * epoch).shuffle(order)
        boundaries = [micro for micro in range(1, 61) if micro % 8 == 0 or micro == 60]
        epochs.append({
            "epoch": epoch, "slot_ids": order,
            "optimizer_step_microbatches": boundaries,
            "optimizer_step_numbers": [(epoch - 1) * 8 + i for i in range(1, 9)],
            "optimizer_step_exposures": [(epoch - 1) * 60 + n for n in boundaries],
            "accumulation_sizes": [8] * 7 + [4], "loss_divisor": 8,
        })
    steps = sum(len(row["optimizer_step_microbatches"]) for row in epochs)
    if steps != 24:
        raise GateStop("DEV2 optimizer-step semantics do not reproduce 24 steps")
    return {"seed": seed, "epochs": epochs, "exposures": 180,
            "optimizer_steps": steps, "checkpoint_epoch": 3}


def cell_order():
    return [{"seed": seed, "condition": condition} for seed in SEEDS for condition in CONDITIONS]


def task_rng_seed(training_seed, task_id):
    _seed(training_seed)
    if not isinstance(task_id, str) or not task_id:
        raise GateStop("task RNG requires a nonempty task ID")
    text = f"{EVALUATION_SEED}|{training_seed}|{task_id}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(text).digest()[:8], "big") % (2 ** 32)


def own_training_order(slot_ids):
    ids = list(slot_ids)
    if any(not isinstance(s, str) for s in ids) or len(set(ids)) != len(ids) or not set(ids) <= set(SLOT_IDS):
        raise GateStop("unknown or duplicate own-training slot ID")
    return sorted(ids, key=lambda s: s.encode("utf-8"))


def confirmatory_order(task_ids_by_group):
    """Form the full 64-position order first, then skip dropped secondary IDs."""
    if set(task_ids_by_group) != set(GROUPS):
        raise GateStop("confirmatory order requires all three group keys")
    kept = {}
    for group in GROUPS:
        ids = list(task_ids_by_group[group])
        if any(not isinstance(s, str) for s in ids) or len(ids) != len(set(ids)) or not set(ids) <= set(FULL_GROUP_IDS[group]):
            raise GateStop("unknown or duplicate confirmatory task ID", {"group": group})
        kept[group] = set(ids)
    if kept[GROUPS[0]] != set(FULL_GROUP_IDS[GROUPS[0]]):
        raise GateStop("primary tasks cannot be dropped")
    positions = {group: 0 for group in GROUPS}
    order = []
    while any(positions[g] < len(FULL_GROUP_IDS[g]) for g in GROUPS):
        for group in (GROUPS[0], GROUPS[0], GROUPS[1], GROUPS[2]):
            i = positions[group]
            if i < len(FULL_GROUP_IDS[group]):
                identifier = FULL_GROUP_IDS[group][i]
                positions[group] += 1
                if identifier in kept[group]:
                    order.append(identifier)
    return order
