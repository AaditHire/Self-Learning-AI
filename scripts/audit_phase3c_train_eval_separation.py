"""Machine-check frozen replay provenance without loading a model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase3c_contract import ROOT, load_frozen, load_items, validate_schedule


def audit() -> dict:
    cfg = load_frozen(check_base=False)
    items = load_items(cfg)
    schedule_summary = validate_schedule(cfg, items)
    a_train = {row["example_id"]: row for row in items["a_train"]}
    eval_rows = items["a_eval"] + items["b_eval"]
    eval_ids = {row["task_id"] for row in eval_rows}
    eval_prompts = {row["prompt"] for row in eval_rows}
    a_references = json.loads((ROOT / "benchmark/phase3c/a_eval_references.json").read_text(encoding="utf-8"))
    b_references = json.loads((ROOT / "benchmark/phase3c/b_eval_references.json").read_text(encoding="utf-8"))
    eval_references = set(a_references.values()) | set(b_references.values())
    replay_ids = [tid for epochs in items["schedule"]["by_seed"].values()
                  for epoch in epochs for tid in epoch["replayed_a_example_ids"]]
    if (len(replay_ids) != 108 or set(replay_ids) - set(a_train) or set(replay_ids) & eval_ids
            or any(a_train[tid]["prompt"] in eval_prompts or a_train[tid]["target"] in eval_references
                   for tid in replay_ids)):
        raise ValueError("Evaluation information entered A replay")
    if any(tid not in a_train for tid in replay_ids):
        raise ValueError("Replay source outside frozen A training set")
    return {"phase": "3C", "status": "PASS_pre_model_train_eval_separation",
            "a_training_ids": len(a_train), "evaluation_ids": len(eval_ids),
            "replay_a_slots_all_seeds": len(replay_ids),
            "replay_ids_outside_a_training": 0, "evaluation_ids_in_replay": 0,
            "exact_eval_prompt_in_replay": 0, "exact_eval_reference_in_replay": 0,
            "schedule": schedule_summary,
            "causal_boundary": "Only pre-B PASS/FAIL flags may enter the hard eligibility gate; fixed replay IDs and order come exclusively from preregistered schedule and A training examples."}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
