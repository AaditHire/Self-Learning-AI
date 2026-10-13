"""EXPLORATORY verified on-policy replay, earlier train prompts only."""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from explore_b0_sample_check import completions, gpu_preflight, hashes, load_model
from self_learning_ai.benchmark import extract_source
from self_learning_ai.explore.pools import load_dev_pool, write_json
from self_learning_ai.explore.runlog import append_run
from self_learning_ai.explore.scoring import score_program

ROOT = Path(__file__).resolve().parents[1]


def draw_prompts(rows, seed, stage):
    if stage not in (2, 3, 4):
        raise ValueError("replay boundary must be 2, 3 or 4")
    return [row for earlier in range(1, stage)
            for row in random.Random(f"opr-{seed}-{stage}-{earlier}").sample(
                [r for r in rows if r["stage"] == earlier], 18 // (stage - 1))]


def verify(row, samples):
    if len(row["cases"]) != 5 or len(samples) != 4:
        raise ValueError("expected five cases and four samples")
    scores = [score_program(text, row["cases"]) for text in samples]
    first = next((i for i, score in enumerate(scores)
                  if score["all_pass"] and score["cases_passed"] == 5), None)
    replay = None if first is None else dict(row, target=extract_source(samples[first]))
    return replay, scores, first


def sample(args):
    if args.output.exists():
        raise FileExistsError(args.output)
    preflight = gpu_preflight()
    rows = draw_prompts(load_dev_pool(ROOT / "research/explore/a1/stream_train.json"), args.seed, args.stage)
    before = hashes(args.adapter)
    if not before:
        raise FileNotFoundError(args.adapter)
    model, tokenizer, _ = load_model(args.adapter)
    import torch
    from train_phase2a_qlora import TokenDataset
    sampling_seed = 20291019 + 1000 * args.stage + args.seed % 1000
    torch.manual_seed(sampling_seed)
    torch.cuda.manual_seed_all(sampling_seed)
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    replay, records = [], []
    summaries = {str(s): dict(prompts_drawn=0, verified=0, over_length_dropped=0,
                              retained=0, pass_counts_per_sample=[0] * 4) for s in range(1, args.stage)}
    for row in rows:
        _, _, samples = completions(model, tokenizer, dict(row, model_task_id=row["example_id"]), 4, 0.8, 512)
        kept, scores, first = verify(row, samples)
        group = summaries[str(row["stage"])]
        group["prompts_drawn"] += 1
        for i, score in enumerate(scores):
            group["pass_counts_per_sample"][i] += int(score["all_pass"])
        dropped = False
        if kept is not None:
            group["verified"] += 1
            try:
                TokenDataset([kept], tokenizer, system, 320)
            except ValueError as exc:
                if not str(exc).startswith("Frozen max length exceeded:"):
                    raise
                group["over_length_dropped"] += 1
                dropped = True
            else:
                replay.append(kept)
                group["retained"] += 1
        records.append(dict(example_id=row["example_id"], stage=row["stage"], samples=samples,
                            scores=scores, first_passing_sample=first, over_length_dropped=dropped))
        print(f"OPR boundary={args.stage} prompt={row['example_id']} first={first} dropped={dropped}", flush=True)
    if before != hashes(args.adapter):
        raise RuntimeError("STOP sampling adapter changed")
    result = dict(label="EXPLORATORY", seed=args.seed, stage=args.stage, sampling_seed=sampling_seed,
                  preflight=preflight, rows=replay, earlier_stages=summaries, records=records)
    write_json(args.output, result)
    append_run(dict(run="a2_opr_sample", status="PASS", summary=result))


def main():
    sys.stdout.reconfigure(newline="\n")
    sys.stderr.reconfigure(newline="\n")
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--stage", type=int, choices=(2, 3, 4), required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        sample(args)
    except Exception as exc:
        append_run(dict(run="a2_opr_sample", seed=args.seed, stage=args.stage, status="FAIL",
                        error=repr(exc), preflight=getattr(exc, "preflight", None)))
        raise


if __name__ == "__main__":
    main()
