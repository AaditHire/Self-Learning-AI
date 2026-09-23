"""Analyze only completed future Phase 3C records under frozen decision rules."""

from __future__ import annotations

import json
import random
from pathlib import Path

from phase3c_contract import (CONFIG, ROOT, a_eligibility, a_endpoints, b_gate, complete_outcomes,
                              joint_decision, load_frozen, load_items, regression_gate, sha256, transitions,
                              verify_execution_files)


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def interval(values: list[float], skipped: int = 0) -> dict:
    if not values:
        raise ValueError("No valid bootstrap draws")
    return {"lower_2p5": percentile(values, .025), "upper_97p5": percentile(values, .975),
            "valid_draws": len(values), "zero_denominator_draws_discarded": skipped,
            "interpretation": "descriptive; never a gate criterion"}


def bootstrap_a(cfg: dict, tasks: list[dict], pre: dict, naive: dict, replay: dict,
                *, block: bool = False) -> dict:
    ids = [x["task_id"] for x in tasks]
    archetypes = {name: [x["task_id"] for x in tasks if x["archetype"] == name]
                  for name in sorted({x["archetype"] for x in tasks})}
    rng = random.Random(cfg["bootstrap"]["seed"])
    retention, aggregate, discarded = [], [], 0
    for _ in range(cfg["bootstrap"]["task_cluster_draws"]):
        sampled = ([tid for name in rng.choices(list(archetypes), k=4) for tid in archetypes[name]]
                   if block else rng.choices(ids, k=32))
        seed_retention, seed_aggregate = [], []
        for seed in cfg["seeds"]:
            acquired = [tid for tid in sampled if pre[seed][tid]]
            if not acquired:
                discarded += 1
                break
            seed_retention.append((sum(replay[seed][tid] for tid in acquired)
                                   - sum(naive[seed][tid] for tid in acquired)) / len(acquired) * 100)
            seed_aggregate.append((sum(replay[seed][tid] for tid in sampled)
                                   - sum(naive[seed][tid] for tid in sampled)) / len(sampled) * 100)
        else:
            retention.append(sum(seed_retention) / 3)
            aggregate.append(sum(seed_aggregate) / 3)
    return {"retention_difference_pp": interval(retention, discarded),
            "aggregate_a_difference_pp": interval(aggregate, discarded),
            "resampling_unit": "whole archetype block" if block else "task ID with all seed/branch observations"}


def bootstrap_b(cfg: dict, tasks: list[dict], pre: dict, naive: dict, replay: dict,
                *, block: bool = False) -> dict:
    ids = [x["task_id"] for x in tasks]
    archetypes = {name: [x["task_id"] for x in tasks if x["archetype"] == name]
                  for name in sorted({x["archetype"] for x in tasks})}
    rng = random.Random(cfg["bootstrap"]["seed"])
    naive_values, replay_values, differences = [], [], []
    for _ in range(cfg["bootstrap"]["task_cluster_draws"]):
        sampled = ([tid for name in rng.choices(list(archetypes), k=4) for tid in archetypes[name]]
                   if block else rng.choices(ids, k=32))
        n = sum(sum(naive[seed][tid] - pre[seed][tid] for tid in sampled) / len(sampled) for seed in cfg["seeds"]) / 3 * 100
        r = sum(sum(replay[seed][tid] - pre[seed][tid] for tid in sampled) / len(sampled) for seed in cfg["seeds"]) / 3 * 100
        naive_values.append(n); replay_values.append(r); differences.append(r - n)
    return {"naive_net_gain_pp": interval(naive_values), "replay_net_gain_pp": interval(replay_values),
            "replay_minus_naive_gain_pp": interval(differences),
            "resampling_unit": "whole archetype block" if block else "task ID with all seed/branch observations"}


def bootstrap_regression(cfg: dict, base: dict, post_a: dict, naive: dict, replay: dict) -> dict:
    ids = sorted(base)
    rng = random.Random(cfg["bootstrap"]["seed"])
    values = {name: [] for name in ("post_a_minus_base_pp", "naive_minus_base_pp",
                                    "replay_minus_base_pp", "replay_minus_naive_pp")}
    for _ in range(cfg["bootstrap"]["task_cluster_draws"]):
        sampled = rng.choices(ids, k=64)
        for name, block, comparator in (("post_a_minus_base_pp", post_a, None),
                                         ("naive_minus_base_pp", naive, None),
                                         ("replay_minus_base_pp", replay, None),
                                         ("replay_minus_naive_pp", replay, naive)):
            difference = sum(sum(block[seed][tid] - (base[tid] if comparator is None else comparator[seed][tid])
                                 for tid in sampled) / 64 for seed in cfg["seeds"]) / 3 * 100
            values[name].append(difference)
    return {name: interval(draws) for name, draws in values.items()}


def grouped_results(tasks: list[dict], pre: dict, naive: dict, replay: dict) -> dict:
    result = {}
    for seed in pre:
        groups = {"all": tasks}
        for key in ("family", "archetype"):
            for value in sorted({r[key] for r in tasks}):
                groups[f"{key}:{value}"] = [r for r in tasks if r[key] == value]
        result[seed] = {}
        for name, rows in groups.items():
            ids = [r["task_id"] for r in rows]
            before = {tid: pre[seed][tid] for tid in ids}
            result[seed][name] = {"total": len(ids), "pre_b_pass": sum(before.values()),
                                  "naive_post_b_pass": sum(naive[seed][tid] for tid in ids),
                                  "replay_post_b_pass": sum(replay[seed][tid] for tid in ids),
                                  "naive_transitions": transitions(before, {tid: naive[seed][tid] for tid in ids}),
                                  "replay_transitions": transitions(before, {tid: replay[seed][tid] for tid in ids})}
    return result


def main() -> None:
    verify_execution_files()
    cfg = load_frozen(check_base=True)
    items = load_items(cfg)
    root = ROOT / cfg["runtime_root"]
    output = root / "analysis.json"
    if output.exists():
        raise FileExistsError(output)

    def read(condition: str, suite: str, seed: int | None, tasks: list[dict], key: str) -> dict:
        label = "base" if seed is None else str(seed)
        path = root / "evaluations" / label / f"{condition}_{suite.lower()}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (payload.get("phase") != "3C" or payload.get("suite") != suite
                or payload.get("condition") != condition or payload.get("seed") != seed
                or payload.get("config_sha256") != sha256(CONFIG)):
            raise ValueError(f"Evaluation provenance mismatch: {path}")
        return complete_outcomes(tasks, payload["records"], score_key=key)

    pre_a = {seed: read("A", "A", seed, items["a_eval"], "hidden_pass") for seed in cfg["seeds"]}
    base_a = read("base", "A", None, items["a_eval"], "hidden_pass")
    base_b = read("base", "B", None, items["b_eval"], "hidden_pass")
    pre_b = {seed: read("A", "B", seed, items["b_eval"], "hidden_pass") for seed in cfg["seeds"]}
    naive_a = {seed: read("naive", "A", seed, items["a_eval"], "hidden_pass") for seed in cfg["seeds"]}
    replay_a = {seed: read("replay", "A", seed, items["a_eval"], "hidden_pass") for seed in cfg["seeds"]}
    naive_b = {seed: read("naive", "B", seed, items["b_eval"], "hidden_pass") for seed in cfg["seeds"]}
    replay_b = {seed: read("replay", "B", seed, items["b_eval"], "hidden_pass") for seed in cfg["seeds"]}
    regression_tasks = json.loads((ROOT / "benchmark/phase2b/general_regression.json").read_text(encoding="utf-8"))
    regression_base = read("base", "regression", None, regression_tasks, "passed")
    regression_a = {seed: read("A", "regression", seed, regression_tasks, "passed") for seed in cfg["seeds"]}
    regression_naive = {seed: read("naive", "regression", seed, regression_tasks, "passed") for seed in cfg["seeds"]}
    regression_replay = {seed: read("replay", "regression", seed, regression_tasks, "passed") for seed in cfg["seeds"]}

    a_gate = a_eligibility(cfg, items["a_eval"], pre_a)
    if not a_gate["all_eligible"]:
        raise RuntimeError("Post-B records cannot exist after failed A eligibility")
    a = a_endpoints(cfg, items["a_eval"], pre_a, naive_a, replay_a)
    b = b_gate(cfg, items["b_eval"], pre_b, naive_b, replay_b)
    regression = regression_gate(cfg, regression_base, regression_a, regression_naive, regression_replay)
    payload = {"phase": "3C", "status": joint_decision(a_gate, a, b, regression),
               "base_controls": {"A_pass_of_32": sum(base_a.values()), "B_pass_of_32": sum(base_b.values())},
               "pre_b_a_eligibility": a_gate, "co_primary_a": a, "b_acquisition": b,
               "a_by_seed_and_slice": grouped_results(items["a_eval"], pre_a, naive_a, replay_a),
               "b_by_seed_and_slice": grouped_results(items["b_eval"], pre_b, naive_b, replay_b),
               "a_task_transitions": {seed: {tid: {"pre_b": pre_a[seed][tid], "naive_post_b": naive_a[seed][tid],
                                                       "replay_post_b": replay_a[seed][tid]}
                                              for tid in sorted(pre_a[seed])} for seed in cfg["seeds"]},
               "b_task_transitions": {seed: {tid: {"pre_b": pre_b[seed][tid], "naive_post_b": naive_b[seed][tid],
                                                       "replay_post_b": replay_b[seed][tid]}
                                              for tid in sorted(pre_b[seed])} for seed in cfg["seeds"]},
               "non_goco_regression": regression,
               "uncertainty": {"a_task_cluster": bootstrap_a(cfg, items["a_eval"], pre_a, naive_a, replay_a),
                               "a_archetype_block_sensitivity": bootstrap_a(cfg, items["a_eval"], pre_a, naive_a, replay_a, block=True),
                               "b_task_cluster": bootstrap_b(cfg, items["b_eval"], pre_b, naive_b, replay_b),
                               "b_archetype_block_sensitivity": bootstrap_b(cfg, items["b_eval"], pre_b, naive_b, replay_b, block=True),
                               "non_goco_task_cluster": bootstrap_regression(cfg, regression_base, regression_a, regression_naive, regression_replay)},
               "decision_intervals_are_descriptive": True}
    with output.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"status": payload["status"], "h1": a["h1_pass"], "h2": a["h2_pass"],
                      "h3": b["h3_pass"], "h4": regression["h4_pass"]}))


if __name__ == "__main__":
    main()
