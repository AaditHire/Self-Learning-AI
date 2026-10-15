"""EXPLORATORY recovery probes and prospective Gate G2 analysis."""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from explore_a1_build import port
from explore_a1_stream import child, stream_paths
from explore_b0_sample_check import completions, generation_kwargs, gpu_preflight, hashes, load_model, prompt_ids
from self_learning_ai.explore.pools import load_dev_pool, write_json
from self_learning_ai.explore.runlog import append_run
from self_learning_ai.explore.scoring import score_program

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/explore/a1"
SEEDS = (20291016, 20291017, 20291018)


def templates():
    return load_dev_pool(DATA / "manifest.json")["stages"]


def forced_prefix(row):
    prompt, reference, *_ = port(row["template"], row["k"])
    if prompt != row["prompt"]:
        raise ValueError(f"STOP re-rendered prompt mismatch: {row['model_task_id']}")
    lines = reference.splitlines()
    end = next(i for i, line in enumerate(lines) if "INPUT(" in line) + 1
    while end < len(lines) and any(token in lines[end] for token in ("strings.SPLIT", "strings.TO_NUMBER", "= parts[")):
        end += 1
    return "\n".join(lines[:end]) + "\n"


def cue_example(row, train, stage_templates):
    ordered = stage_templates[str(row["stage"])]["templates"]
    following = ordered[(ordered.index(row["template"]) + 1) % len(ordered)]
    return min((r for r in train if r["stage"] == row["stage"] and r["template"] == following), key=lambda r: r["k"])


def forgotten_set(dev, own_records, final_records):
    return [r for r in dev if r["stage"] <= 3 and
            own_records[r["model_task_id"]]["score"]["all_pass"] and
            not final_records[r["model_task_id"]]["score"]["all_pass"]]


def prior_records(seed, dev):
    runtime = ROOT / ".runtime/explore/a1" / str(seed)
    own, final = {}, {}
    for row in dev:
        tid = row["model_task_id"]
        own[tid] = load_dev_pool(runtime / f"eval_after_s{row['stage']}" / f"{tid}.json")
        final[tid] = load_dev_pool(runtime / "eval_after_s4" / f"{tid}.json")
    return own, final


def prefix_completion(model, tokenizer, row, prefix):
    import torch
    ids = prompt_ids(tokenizer, row) + tokenizer(prefix, add_special_tokens=False)["input_ids"]
    tensor = torch.tensor([ids], dtype=torch.long, device="cuda:0")
    with torch.inference_mode():
        output = model.generate(input_ids=tensor, attention_mask=torch.ones_like(tensor),
                                **generation_kwargs(tokenizer, 1, 0, 512))
    tokens = output[0, len(ids):].tolist()
    eos = model.generation_config.eos_token_id
    eos = {eos} if isinstance(eos, int) else set(eos)
    for i, token in enumerate(tokens):
        if token in eos:
            tokens = tokens[:i + 1]
            break
    return tokenizer.decode(tokens, skip_special_tokens=True)


def generation(seed):
    runtime = ROOT / ".runtime/explore/a2/probes" / str(seed)
    out = runtime / "generation"
    if out.exists():
        raise FileExistsError(out)
    dev = load_dev_pool(DATA / "stream_dev.json")
    train = load_dev_pool(DATA / "stream_train.json")
    own, final = prior_records(seed, dev)
    forgotten = forgotten_set(dev, own, final)
    prepared = [(r, forced_prefix(r), cue_example(r, train, templates())) for r in forgotten]
    preflight = gpu_preflight()
    adapter = ROOT / ".runtime/explore/a1" / str(seed) / "stage4/adapter_final"
    before = hashes(adapter)
    if not before:
        raise FileNotFoundError(adapter)
    model, tokenizer, _ = load_model(adapter)
    out.mkdir(parents=True)
    records = []
    for row, prefix, example in prepared:
        continuation = prefix_completion(model, tokenizer, row, prefix)
        cue = f"Example task:\n{example['prompt']}\nExample solution:\n{example['target']}\n\nNow solve:\n{row['prompt']}"
        _, _, samples = completions(model, tokenizer, dict(row, prompt=cue), 1, 0, 512)
        record = {key: row[key] for key in ("task_id", "model_task_id", "stage", "template", "k")}
        record.update(prefix=prefix, continuation=continuation, prefix_raw=prefix + continuation,
                      prefix_score=score_program(prefix + continuation, row["cases"]),
                      latest_scaffold_beyond_prefix=row["stage"] in (1, 2) and "strings.SPLIT" in continuation,
                      cue_example_id=example["example_id"], cue_prompt=cue, cue_raw=samples[0],
                      cue_score=score_program(samples[0], row["cases"]))
        write_json(out / f"{row['model_task_id']}.json", record)
        records.append(record)
        print(f"PROBE seed={seed} task={row['model_task_id']} prefix={record['prefix_score']['all_pass']} cue={record['cue_score']['all_pass']}", flush=True)
    if before != hashes(adapter):
        raise RuntimeError("STOP final naive adapter changed")
    write_json(out / "summary.json", dict(label="EXPLORATORY", preflight=preflight, records=records))
    append_run(dict(run="a2_probe_generation", seed=seed, status="PASS", tasks=len(records), preflight=preflight))


def recovery_stats(records, score_key):
    return dict(total=len(records), recovered=sum(r[score_key]["all_pass"] for r in records),
                compile_failure_rate=sum(not r[score_key]["compiled"] for r in records) / len(records) if records else None)


def probes(seed):
    runtime = ROOT / ".runtime/explore/a2/probes" / str(seed)
    output = ROOT / "research/explore/a2/probes" / str(seed)
    if runtime.exists() or output.exists():
        raise FileExistsError("probe outputs already exist")
    dev = load_dev_pool(DATA / "stream_dev.json")
    train = load_dev_pool(DATA / "stream_train.json")
    own, final = prior_records(seed, dev)
    forgotten = forgotten_set(dev, own, final)
    child([ROOT / "scripts/explore_a2_probes.py", "--seed", seed, "--generation-only"], seed, 4, "probes")
    generated = load_dev_pool(runtime / "generation/summary.json")["records"]
    stages = {}
    for stage in range(1, 4):
        selected = random.Random(f"relearn-{seed}-{stage}").sample([r for r in train if r["stage"] == stage], 40)
        data_path = runtime / f"train_rows_stage{stage}.json"
        write_json(data_path, selected)
        group = [r for r in generated if r["stage"] == stage]
        stage_forgotten = [r for r in forgotten if r["stage"] == stage]
        result = dict(forgotten_set_size=len(stage_forgotten),
                      prefix=recovery_stats(group, "prefix_score"), cue=recovery_stats(group, "cue_score"),
                      latest_scaffold_beyond_prefix=sum(r["latest_scaffold_beyond_prefix"] for r in group),
                      per_template={t: dict(prefix=recovery_stats([r for r in group if r["template"] == t], "prefix_score"),
                                            cue=recovery_stats([r for r in group if r["template"] == t], "cue_score"))
                                    for t in templates()[str(stage)]["templates"]})
        for method in ("relearn", "fresh_control"):
            run_dir = runtime / method / f"stage{stage}"
            train_summary = runtime / method / f"train_stage{stage}.json"
            command = [ROOT / "scripts/explore_sft.py", "--seed", seed, "--data", data_path,
                       "--output-dir", run_dir, "--summary", train_summary, "--run-name", f"a2_probe_{method}",
                       "--epochs", 1, "--warmup-steps", 0]
            # SFT makes and checks a byte-exact private initialization copy before training.
            command += (["--init-adapter", ROOT / ".runtime/explore/a1" / str(seed) / "stage4/adapter_final"]
                        if method == "relearn" else ["--fresh-lora"])
            child(command, seed, stage, method)
            training = load_dev_pool(train_summary)
            if training["optimizer_steps"] != 5 or training["exposures"] != 40:
                raise RuntimeError("STOP probe expected five optimizer steps and 40 exposures")
            eval_dir = runtime / method / f"eval_stage{stage}"
            eval_summary = runtime / method / f"eval_stage{stage}.json"
            child([ROOT / "scripts/explore_stream_eval.py", "--adapter", run_dir / "adapter_final",
                   "--rows", DATA / "stream_dev.json", "--stages", stage, "--out-dir", eval_dir,
                   "--summary", eval_summary], seed, stage, f"{method}_eval")
            records = [load_dev_pool(eval_dir / f"{r['model_task_id']}.json") for r in stage_forgotten]
            result[method] = dict(stage_metrics=load_dev_pool(eval_summary)["stages"][str(stage)],
                                  forgotten_set=recovery_stats(records, "score"), optimizer_steps=5)
        stages[str(stage)] = result
    summary = dict(label="EXPLORATORY", seed=seed, stages=stages)
    write_json(output / "summary.json", summary)
    append_run(dict(run="a2_probes", seed=seed, status="PASS", summary=summary))
    print(f"PROBES PASS seed={seed}", flush=True)


def gate_g2(rank=None):
    seeds = {}
    for seed in SEEDS:
        naive_output = DATA / str(seed) if rank is None else stream_paths(seed, "naive", rank)[0]
        naive = load_dev_pool(naive_output / "results.json")
        output = ROOT / "research/explore/a2/opr" / str(seed) if rank is None else stream_paths(seed, "opr", rank)[0]
        opr = load_dev_pool(output / "results.json")
        c = sum(naive["accuracy_matrix"][s][s] for s in range(3)) / 3
        f = sum(opr["accuracy_matrix"][3][:3]) / 3
        replay = {str(s): load_dev_pool(output / f"replay_stage{s}.json")["earlier_stages"] for s in (2, 3, 4)}
        for boundary in replay.values():
            for group in boundary.values():
                group["verification_rate"] = group["verified"] / group["prompts_drawn"]
        seeds[str(seed)] = dict(ceiling_proxy=c, opr_final_retention=f, gap_pp=100 * (c - f),
                                naive_final_retention=sum(naive["accuracy_matrix"][3][:3]) / 3,
                                opr_acquisition=opr["acquisition"], replay=replay,
                                passed=100 * (c - f) >= 15)
        if rank is not None:
            seeds[str(seed)]["regime_valid"] = all(naive["accuracy_matrix"][s][s] >= 0.60 for s in range(4))
    result = dict(label="EXPLORATORY", gate="G2", ceiling_is_proxy=True, threshold_pp=15,
                  rule="gap >= 15 pp in all three seeds", seeds=seeds,
                  verdict="PASS" if all(s["passed"] for s in seeds.values()) else "FAIL")
    output = ROOT / "research/explore/a2/g2_summary.json"
    if rank is not None:
        result.update(lora_rank=rank, regime_valid_all=all(s["regime_valid"] for s in seeds.values()))
        output = ROOT / f"research/explore/a2/r{rank}/g2_summary.json"
    write_json(output, result)
    append_run(dict(run="a2_g2" if rank is None else f"a2_g2_r{rank}", status="PASS", summary=result))
    return result


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, choices=SEEDS)
    parser.add_argument("--generation-only", action="store_true")
    gates = parser.add_mutually_exclusive_group()
    gates.add_argument("--g2", action="store_true")
    gates.add_argument("--g2-rank", type=int)
    return parser


def main():
    sys.stdout.reconfigure(newline="\n")
    sys.stderr.reconfigure(newline="\n")
    parser = argument_parser()
    args = parser.parse_args()
    if not args.g2 and args.g2_rank is None and args.seed is None:
        parser.error("--seed required for probes")
    try:
        if args.g2 or args.g2_rank is not None:
            print(gate_g2(args.g2_rank), flush=True)
        elif args.generation_only:
            generation(args.seed)
        else:
            probes(args.seed)
    except Exception as exc:
        run = ("a2_g2" if args.g2 else f"a2_g2_r{args.g2_rank}") if args.g2 or args.g2_rank is not None else "a2_probes"
        append_run(dict(run=run, seed=args.seed,
                        operation="generation" if args.generation_only else "orchestration", status="FAIL",
                        error=repr(exc), preflight=getattr(exc, "preflight", None)))
        raise


if __name__ == "__main__":
    main()
