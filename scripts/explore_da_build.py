"""EXPLORATORY diverse-format atomic examples; no composition training."""
from __future__ import annotations

import copy
import hashlib
import itertools
import random
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.conf1_r1.training import _builder
from self_learning_ai.explore.pools import FAMILIES, load_dev_pool, write_json
from self_learning_ai.explore.runlog import append_run
from self_learning_ai.explore.scoring import score_program
from explore_b0_sample_check import sample_prompts

SEED = 20291014
OUT = ROOT / "research/explore/da"
WORDINGS = {
    "atom_single": (
        "Count the items that are {d}, starting the count at {k}, and print the count.",
        "Start a counter at {k}. Add one for every item that is {d}. Print the counter.",
        "Print {k} plus the number of items that are {d}.",
        "How many items are {d}? Add {k} to that number and print the result.",
        "Begin at {k} and increase by one for each item that is {d}; output the final value.",
    ),
    "atom_isolated": (
        "Starting from {k}, add one for each item that is {dP} and add one for each item that is {dQ}; print the total.",
        "Print {k} plus the number of items that are {dP} plus the number of items that are {dQ}.",
        "Count the items that are {dP}, count the items that are {dQ}, add both counts to {k}, and print the result.",
        "Start a total at {k}. For every item, add one if it is {dP}, and add one more if it is {dQ}. Print the total.",
        "Output {k} increased by the count of items that are {dP} and by the count of items that are {dQ}.",
    ),
}


def render(category, slot, wording):
    builder = _builder()
    values = dict(k=slot["offset"])
    if category == "atom_single":
        values["d"] = builder.DESCRIPTIONS[slot["primitive"]]
    else:
        values.update(dP=builder.DESCRIPTIONS[slot["P"]], dQ=builder.DESCRIPTIONS[slot["Q"]])
    return builder.prompt_prefix(slot["family"]) + WORDINGS[category][wording - 1].format(**values)


def validation_cases(category, slot, rng):
    builder = _builder()
    for _ in range(50):
        inputs = []
        while len(inputs) < 5:
            value = (str(rng.randint(6, 40)) if slot["family"] == FAMILIES[0] else
                     "|".join(str(rng.randint(-9, 9)) for _ in range(4)))
            if value not in inputs:
                inputs.append(value)
        values = [(builder.sanity_expected(slot, x) if category == "atom_single" else
                   builder.train_expected("isolated", slot, x)) for x in inputs]
        if len(set(values)) > 1:
            return [builder.case(j + 1, x, v) for j, (x, v) in enumerate(zip(inputs, values))]
    raise ValueError(f"STOP constant case outputs after 50 attempts: {category}: {slot}")


def training_examples():
    builder, rng = _builder(), random.Random(SEED)
    rows = []
    for category in WORDINGS:
        for family in FAMILIES:
            names = list(builder.PREDICATES[family])
            definitions = names if category == "atom_single" else list(itertools.combinations(names, 2))
            for definition in definitions:
                for wording in range(1, 5):
                    for offset in rng.sample(range(20, 40), 5):
                        slot = dict(family=family, offset=offset)
                        if category == "atom_single":
                            slot.update(primitive=definition, group="primitive_sanity")
                            target = builder.sanity_source(slot)
                        else:
                            ordered = list(definition)
                            rng.shuffle(ordered)
                            slot.update(P=ordered[0], Q=ordered[1], reverse=bool(rng.randrange(2)))
                            target = builder.train_source("isolated", slot)
                        rows.append(dict(category=category, family=family, slot=slot,
                                         group=slot.get("group", "atom_isolated"), wording=f"W{wording}",
                                         prompt=render(category, slot, wording), target=target))
    shuffled = list(rows)
    rng.shuffle(shuffled)
    for index, row in enumerate(shuffled):
        row["example_id"] = f"EXPL-DA-{index:04d}"
    for row in rows:
        row["cases"] = validation_cases(row["category"], row["slot"], rng)
    return rows


def held_out_examples():
    rows = []
    for original in sample_prompts(load_dev_pool()):
        category = original["category"]
        if category not in WORDINGS:
            continue
        row = copy.deepcopy(original)
        row.update(category=category + "_w5", wording="W5", prompt=render(category, row["slot"], 5))
        rows.append(row)
    return rows


def main():
    sys.stdout.reconfigure(newline="\n")
    sys.stderr.reconfigure(newline="\n")
    started = time.perf_counter()
    try:
        if OUT.exists():
            raise FileExistsError("DA output directory already exists")
        rows, evaluation = training_examples(), held_out_examples()
        counts = dict(Counter(r["category"] for r in rows))
        if counts != dict(atom_single=160, atom_isolated=240) or len(evaluation) != 32:
            raise ValueError(f"STOP unexpected DA counts: {counts}, eval={len(evaluation)}")
        for index, row in enumerate(rows, 1):
            score = score_program(row["target"], row["cases"])
            if not score["all_pass"]:
                raise ValueError(f"STOP reference failure: {row['example_id']}: {score}")
            print(f"DA reference PASS {index}/{len(rows)} {row['example_id']}", flush=True)
        write_json(OUT / "train.json", rows)
        write_json(OUT / "eval_w5.json", evaluation)
        manifest = dict(label="EXPLORATORY", seed=SEED, f2_sample_seed=20291012,
                        counts=dict(training=counts, eval_w5=dict(Counter(r["category"] for r in evaluation))),
                        family_counts={c: dict(Counter(r["family"] for r in rows if r["category"] == c)) for c in WORDINGS},
                        training_wordings=["W1", "W2", "W3", "W4"], evaluation_wording="W5",
                        training_offset_range=[20, 39], references_validated=len(rows),
                        sha256={p: hashlib.sha256((OUT / p).read_bytes()).hexdigest() for p in ("train.json", "eval_w5.json")})
        write_json(OUT / "manifest.json", manifest)
        append_run(dict(run="da_build", status="PASS", manifest=manifest, seconds=time.perf_counter() - started))
        print(manifest, flush=True)
    except Exception as exc:
        append_run(dict(run="da_build", status="FAIL", error=repr(exc)))
        raise


if __name__ == "__main__":
    main()
