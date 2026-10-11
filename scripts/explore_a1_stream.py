"""EXPLORATORY four-stage naive stream; sequential fresh subprocesses."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from self_learning_ai.explore.pools import load_dev_pool, write_json
from self_learning_ai.explore.runlog import append_run

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/explore/a1"


def child(command, seed, stage, operation):
    print(f"A1 CHILD {operation} seed={seed} stage={stage}", flush=True)
    result = subprocess.run([sys.executable, "-B", "-u", *map(str, command)], cwd=ROOT)
    if result.returncode:
        append_run(dict(run="a1_child", status="FAIL", seed=seed, stage=stage, operation=operation,
                        command=list(map(str, command)), exit_code=result.returncode))
        raise RuntimeError(f"STOP child {operation} stage {stage} exited {result.returncode}")


def stream(seed):
    output = DATA / str(seed)
    runtime = ROOT / ".runtime/explore/a1" / str(seed)
    if output.exists() or runtime.exists():
        raise FileExistsError("seed outputs already exist")
    rows = load_dev_pool(DATA / "stream_train.json")
    evaluations, training = {}, {}
    for stage in range(1, 5):
        selected = [r for r in rows if r["stage"] == stage]
        if len(selected) != 72:
            raise ValueError("STOP expected 72 training rows per stage")
        train_rows = output / f"train_rows_stage{stage}.json"
        write_json(train_rows, selected)
        stage_runtime = runtime / f"stage{stage}"
        train_summary = output / f"train_stage{stage}.json"
        command = [ROOT / "scripts/explore_sft.py", "--seed", seed, "--data", train_rows,
                   "--output-dir", stage_runtime, "--summary", train_summary, "--run-name", "a1_train"]
        command += (["--fresh-lora"] if stage == 1 else
                    ["--init-adapter", runtime / f"stage{stage - 1}/adapter_final"])
        child(command, seed, stage, "train")
        training[str(stage)] = json.loads(train_summary.read_bytes())
        eval_summary = output / f"eval_after_s{stage}.json"
        child([ROOT / "scripts/explore_stream_eval.py", "--adapter", stage_runtime / "adapter_final",
               "--rows", DATA / "stream_dev.json", "--stages", ",".join(map(str, range(1, stage + 1))),
               "--out-dir", runtime / f"eval_after_s{stage}", "--summary", eval_summary], seed, stage, "eval")
        evaluations[str(stage)] = json.loads(eval_summary.read_bytes())
    matrix = [[evaluations[str(after)]["stages"][str(stage)]["pass_rate"] if stage <= after else None
               for stage in range(1, 5)] for after in range(1, 5)]
    acquisition = {str(s): matrix[s - 1][s - 1] for s in range(1, 5)}
    forgetting = {str(s): 100 * (acquisition[str(s)] - matrix[3][s - 1]) for s in range(1, 4)}
    result = dict(label="EXPLORATORY", seed=seed, accuracy_matrix=matrix, acquisition=acquisition,
                  final_forgetting_pp=forgetting, mean_final_forgetting_pp=sum(forgetting.values()) / 3,
                  checkpoints={after: e["stages"] for after, e in evaluations.items()},
                  training={s: {key: t[key] for key in ("first_loss", "last_loss", "peak_gpu_allocated_bytes",
                                                       "peak_gpu_reserved_bytes", "seconds", "training_seconds")} for s, t in training.items()})
    write_json(output / "results.json", result)
    append_run(dict(run="a1_stream", status="PASS", summary=result))
    print(f"A1 STREAM PASS seed={seed}", flush=True)


def gate():
    summaries = {}
    for seed in (20291016, 20291017):
        result = json.loads((DATA / str(seed) / "results.json").read_bytes())
        acquired = all(value >= 0.60 for value in result["acquisition"].values())
        forgotten = result["mean_final_forgetting_pp"] >= 50
        summaries[str(seed)] = dict(acquisition=result["acquisition"], final_forgetting_pp=result["final_forgetting_pp"],
                                    mean_final_forgetting_pp=result["mean_final_forgetting_pp"],
                                    acquisition_pass=acquired, forgetting_pass=forgotten, passed=acquired and forgotten)
    summary = dict(label="EXPLORATORY", gate="G1", acquisition_threshold=0.60, forgetting_threshold_pp=50,
                   seeds=summaries, verdict="PASS" if all(r["passed"] for r in summaries.values()) else "FAIL")
    write_json(DATA / "g1_summary.json", summary)
    append_run(dict(run="a1_g1", status="PASS", summary=summary))
    return summary


def main():
    sys.stdout.reconfigure(newline="\n")
    sys.stderr.reconfigure(newline="\n")
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, choices=(20291016, 20291017), required=True)
    args = parser.parse_args()
    try:
        stream(args.seed)
        if args.seed == 20291017:
            print(json.dumps(gate()), flush=True)
    except Exception as exc:
        append_run(dict(run="a1_stream", seed=args.seed, status="FAIL", error=repr(exc)))
        raise


if __name__ == "__main__":
    main()
