"""EXPLORATORY greedy checkpoint evaluation, dev rows only."""
from __future__ import annotations

import argparse
import sys
import time
from collections import Counter
from pathlib import Path

from explore_b0_sample_check import completions, effective_settings, gpu_preflight, hashes, load_model
from self_learning_ai.explore.pools import load_dev_pool, write_json
from self_learning_ai.explore.runlog import append_run
from self_learning_ai.explore.scoring import score_program


def evaluate(args):
    started = time.perf_counter()
    if args.out_dir.exists() or args.summary.exists():
        raise FileExistsError("evaluation output already exists")
    preflight = gpu_preflight()
    stages = [int(s) for s in args.stages.split(",")]
    rows = [r for r in load_dev_pool(args.rows) if r["stage"] in stages]
    if not rows or any(sum(r["stage"] == s for r in rows) != 24 for s in stages):
        raise ValueError("STOP expected 24 dev rows per stage")
    before = hashes(args.adapter)
    if not before:
        raise FileNotFoundError("adapter missing")
    model, tokenizer, cfg = load_model(args.adapter)
    args.out_dir.mkdir(parents=True)
    records = []
    for row in rows:
        _, _, raw = completions(model, tokenizer, row, 1, 0, cfg["evaluation"]["max_new_tokens"])
        score = score_program(raw[0], row["cases"])
        record = {key: row[key] for key in ("task_id", "model_task_id", "stage", "template", "k")}
        record.update(raw=raw[0], score=score)
        write_json(args.out_dir / f"{row['model_task_id']}.json", record)
        records.append(record)
        print(f"A1 EVAL {len(records)}/{len(rows)} S{row['stage']} {row['template']} k={row['k']} pass={score['all_pass']}", flush=True)
    if before != hashes(args.adapter):
        raise RuntimeError("STOP adapter changed during evaluation")
    summaries = {}
    for stage in stages:
        group = [r for r in records if r["stage"] == stage]
        counts = Counter(r["template"] for r in group)
        if len(counts) != 8 or set(counts.values()) != {3}:
            raise ValueError("STOP expected 8 templates with 3 dev rows")
        summaries[str(stage)] = dict(tasks=len(group), pass_rate=sum(r["score"]["all_pass"] for r in group) / len(group),
            mean_partial_reward=sum(r["score"]["cases_passed"] / 5 for r in group) / len(group),
            compile_failure_rate=sum(not r["score"]["compiled"] for r in group) / len(group),
            per_template={t: dict(passed=sum(r["score"]["all_pass"] for r in group if r["template"] == t), total=3) for t in counts})
    summary = dict(label="EXPLORATORY", preflight=preflight, adapter=args.adapter.as_posix(), adapter_hashes=before,
                   adapter_unchanged=True, rows=args.rows.as_posix(), stages=summaries,
                   greedy_settings=effective_settings(model, tokenizer, 1, 0, cfg["evaluation"]["max_new_tokens"]),
                   seconds=time.perf_counter() - started)
    write_json(args.summary, summary)
    append_run(dict(run="a1_eval", status="PASS", summary=summary))
    print(f"A1 EVAL PASS stages={args.stages}", flush=True)


def main():
    sys.stdout.reconfigure(newline="\n")
    sys.stderr.reconfigure(newline="\n")
    parser = argparse.ArgumentParser()
    for name in ("adapter", "rows", "out-dir", "summary"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--stages", required=True)
    args = parser.parse_args()
    try:
        evaluate(args)
    except Exception as exc:
        append_run(dict(run="a1_eval", status="FAIL", error=repr(exc), preflight=getattr(exc, "preflight", None)))
        raise


if __name__ == "__main__":
    main()
