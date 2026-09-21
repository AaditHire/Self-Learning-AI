from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def keyed(payload: dict[str, Any], field: str) -> dict[str, bool]:
    return {row["task_id"]: bool(row[field]) for row in payload["records"]}


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def bootstrap_differences(base: dict[str, bool], adapters: list[dict[str, bool]], task_ids: list[str], samples: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    draws = []
    for _ in range(samples):
        chosen = [task_ids[rng.randrange(len(task_ids))] for _ in task_ids]
        draws.append(mean(mean(int(adapter[task_id]) for adapter in adapters) - int(base[task_id]) for task_id in chosen))
    observed = mean(mean(int(adapter[task_id]) for adapter in adapters) - int(base[task_id]) for task_id in task_ids)
    return {"unit": "paired task cluster; three seeds treated as repeated models within task", "samples": samples, "seed": seed, "observed": observed, "ci_95": [percentile(draws, 0.025), percentile(draws, 0.975)]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--base-primary", type=Path, required=True)
    parser.add_argument("--docs-primary", type=Path, required=True)
    parser.add_argument("--adapter-primary", type=Path, nargs=3, required=True)
    parser.add_argument("--training-run", type=Path, nargs=3, required=True)
    parser.add_argument("--training-eval", type=Path, nargs=3, required=True)
    parser.add_argument("--base-regression", type=Path, required=True)
    parser.add_argument("--adapter-regression", type=Path, nargs=3, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    config = load(args.config)
    base_payload = load(args.base_primary)
    docs_payload = load(args.docs_primary)
    adapter_payloads = [load(path) for path in args.adapter_primary]
    training_runs = [load(path) for path in args.training_run]
    training_payloads = [load(path) for path in args.training_eval]
    base_regression_payload = load(args.base_regression)
    adapter_regression_payloads = [load(path) for path in args.adapter_regression]
    seeds = [payload["seed"] for payload in adapter_payloads]
    if seeds != config["seeds"]:
        raise ValueError((seeds, config["seeds"]))
    if [payload["seed"] for payload in training_payloads] != seeds or [payload["seed"] for payload in adapter_regression_payloads] != seeds or [payload["seed"] for payload in training_runs] != seeds:
        raise ValueError("Seed/result ordering mismatch")

    base = keyed(base_payload, "hidden_pass")
    docs = keyed(docs_payload, "hidden_pass")
    adapters = [keyed(payload, "hidden_pass") for payload in adapter_payloads]
    task_ids = list(base)
    tasks = {row["task_id"]: row for row in base_payload["records"]}
    families = sorted({row["family"] for row in base_payload["records"]})
    primary_by_seed = []
    for seed, adapter in zip(seeds, adapters):
        family = {}
        for name in families:
            ids = [task_id for task_id in task_ids if tasks[task_id]["family"] == name]
            passed = sum(adapter[task_id] for task_id in ids)
            family[name] = {"passed": passed, "total": len(ids), "rate": passed / len(ids)}
        adapted_rate = mean(int(adapter[task_id]) for task_id in task_ids)
        base_rate = mean(int(base[task_id]) for task_id in task_ids)
        base_only = sum(base[task_id] and not adapter[task_id] for task_id in task_ids)
        adapted_only = sum(adapter[task_id] and not base[task_id] for task_id in task_ids)
        primary_by_seed.append({"seed": seed, "passed": sum(adapter.values()), "total": len(task_ids), "rate": adapted_rate, "improvement": adapted_rate - base_rate, "families_with_success": sum(value["passed"] > 0 for value in family.values()), "paired": {"base_only": base_only, "adapted_only": adapted_only, "both": sum(base[task_id] and adapter[task_id] for task_id in task_ids), "neither": sum(not base[task_id] and not adapter[task_id] for task_id in task_ids)}, "by_family": family})

    family_aggregate = {}
    for family in families:
        rates = [row["by_family"][family]["rate"] for row in primary_by_seed]
        family_aggregate[family] = {"mean": mean(rates), "range": [min(rates), max(rates)], "seed_rates": dict(zip(map(str, seeds), rates))}
    seed_rates = [row["rate"] for row in primary_by_seed]
    base_rate = mean(base.values())
    mean_adapter_rate = mean(seed_rates)

    nonnear_ids = [task_id for task_id in task_ids if tasks[task_id].get("distance_bucket") in {"far", "medium"}]
    successful_instances = [(task_id, adapter[task_id]) for adapter in adapters for task_id in task_ids]
    total_successes = sum(passed for _, passed in successful_instances)
    nonnear_successes = sum(passed and task_id in nonnear_ids for task_id, passed in successful_instances)
    nonnear_adapter_rate = mean(int(adapter[task_id]) for adapter in adapters for task_id in nonnear_ids)
    nonnear_base_rate = mean(int(base[task_id]) for task_id in nonnear_ids)
    structural_gate = {"nonnear_tasks": len(nonnear_ids), "successful_seed_task_instances": total_successes, "nonnear_successful_instances": nonnear_successes, "nonnear_share_of_successes": nonnear_successes / total_successes if total_successes else 0.0, "nonnear_mean_improvement": nonnear_adapter_rate - nonnear_base_rate}
    structural_gate["passed"] = structural_gate["nonnear_share_of_successes"] >= 0.5 or structural_gate["nonnear_mean_improvement"] >= 0.10

    training_diagnostics = []
    for seed, payload, primary in zip(seeds, training_payloads, primary_by_seed):
        training_rate = payload["summary"]["overall"]["hidden_pass"]
        training_diagnostics.append({"seed": seed, "training_pass_rate": training_rate, "confirmatory_pass_rate": primary["rate"], "generalization_gap": training_rate - primary["rate"]})

    base_regression = keyed(base_regression_payload, "passed")
    regression = []
    for seed, payload in zip(seeds, adapter_regression_payloads):
        adapter = keyed(payload, "passed")
        base_accuracy = mean(base_regression.values())
        adapter_accuracy = mean(adapter.values())
        regression.append({"seed": seed, "base_accuracy": base_accuracy, "adapted_accuracy": adapter_accuracy, "change": adapter_accuracy - base_accuracy, "drop": base_accuracy - adapter_accuracy, "severe_collapse": base_accuracy - adapter_accuracy > config["success_gate"]["regression_max_drop"]})

    feasibility = [{"seed": run["seed"], "completed": run["stability"]["completed"], "all_losses_and_gradients_finite": run["stability"]["all_losses_finite"], "optimizer_steps": run["training"]["optimizer_steps"], "peak_gpu_allocated_bytes": run["training"]["peak_gpu_allocated_bytes"], "peak_process_rss_bytes": run["training"]["peak_process_rss_bytes"]} for run in training_runs]
    gate = config["success_gate"]
    criteria = {
        "mean_adapted_at_least_20pct": mean_adapter_rate >= gate["mean_adapted_hidden_pass_rate_minimum"],
        "mean_improvement_at_least_15pp": mean_adapter_rate - base_rate >= gate["mean_absolute_improvement_minimum"],
        "each_seed_gain_at_least_10pp": all(row["improvement"] >= gate["each_seed_improvement_minimum"] for row in primary_by_seed),
        "each_seed_at_least_four_families": all(row["families_with_success"] >= gate["minimum_families_with_success_each_seed"] for row in primary_by_seed),
        "not_dominated_by_near_duplicates": structural_gate["passed"],
        "no_severe_regression_collapse": all(not row["severe_collapse"] for row in regression),
        "all_three_training_runs_feasible": all(row["completed"] and row["all_losses_and_gradients_finite"] for row in feasibility),
    }
    result = {
        "phase": "2B", "analysis_policy": "paired task analysis; task-cluster bootstrap; seeds are repeated trained models and are not counted as 384 independent observations", "seeds": seeds,
        "primary": {"base": {"passed": sum(base.values()), "total": len(base), "rate": base_rate}, "base_docs_descriptive": {"passed": sum(docs.values()), "total": len(docs), "rate": mean(docs.values())}, "adapter_by_seed": primary_by_seed, "adapter_mean_rate": mean_adapter_rate, "adapter_rate_range": [min(seed_rates), max(seed_rates)], "mean_improvement": mean_adapter_rate - base_rate, "family_aggregate": family_aggregate, "task_cluster_bootstrap": bootstrap_differences(base, adapters, task_ids, config["analysis"]["bootstrap_samples"], config["analysis"]["bootstrap_seed"])},
        "structural_distance_analysis": structural_gate,
        "training_diagnostics": training_diagnostics,
        "training_feasibility": feasibility,
        "regression": regression,
        "success_criteria": criteria,
        "overall_success": all(criteria.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"primary": result["primary"], "structural_distance_analysis": structural_gate, "regression": regression, "success_criteria": criteria, "overall_success": result["overall_success"]}, indent=2))


if __name__ == "__main__":
    main()
