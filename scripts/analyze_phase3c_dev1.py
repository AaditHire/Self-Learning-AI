"""Frozen descriptive DEV1 analysis; requires all six training and development cells."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from preflight_phase3c_dev1 import ROOT, read, sha256


RUNTIME = ROOT / ".runtime/phase3c_dev1"
OUTPUT = RUNTIME / "analysis.json"
BOOTSTRAP_SEED = 20271221
BOOTSTRAP_DRAWS = 10000


def metrics(rows: list[dict]) -> dict:
    return {"passed": sum(bool(x["hidden_pass"]) for x in rows), "total": len(rows),
            "pass_rate": sum(bool(x["hidden_pass"]) for x in rows) / len(rows),
            "failure_taxonomy": dict(sorted(Counter(x["failure_category"] for x in rows).items()))}


def grouped(rows: list[dict], field: str) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[row[field]].append(row)
    return {key: metrics(group) for key, group in sorted(groups.items())}


def ci(values: np.ndarray) -> list[float]:
    return [float(np.quantile(values, .025)), float(np.quantile(values, .975))]


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    manifest = read("research/protocols/phase3c_dev1_manifest.json")
    seeds = manifest["seeds"]
    tasks = read("benchmark/phase3c_dev1/a_development_eval_tasks.json")
    ids = [task["task_id"] for task in tasks]
    if len(ids) != 36 or len(set(ids)) != 36:
        raise ValueError("Development task IDs")
    task_by_id = {task["task_id"]: task for task in tasks}
    records, training, per_seed = {}, {}, {}
    for seed in seeds:
        per_seed[str(seed)] = {}
        for condition in ("dense", "diverse"):
            train_payload = read(str((RUNTIME / "evaluations" / str(seed) / f"{condition}_training.json").relative_to(ROOT)))
            dev_payload = read(str((RUNTIME / "evaluations" / str(seed) / f"{condition}_development.json").relative_to(ROOT)))
            run = read(str((RUNTIME / "training" / str(seed) / f"{condition}.json").relative_to(ROOT)))
            if run["training"]["optimizer_steps"] != 24 or train_payload["adapter_file_hashes"] != run["adapter"]["file_hashes"] or dev_payload["adapter_file_hashes"] != run["adapter"]["file_hashes"]:
                raise ValueError("Training/evaluation lineage")
            train_rows, dev_rows = train_payload["records"], dev_payload["records"]
            if len(train_rows) != 60 or len(dev_rows) != 36 or {r["task_id"] for r in dev_rows} != set(ids):
                raise ValueError("Incomplete evaluation")
            if len({r["task_id"] for r in train_rows}) != 60:
                raise ValueError("Duplicate training outcome")
            records[(seed, condition)] = {r["task_id"]: r for r in dev_rows}
            training[(seed, condition)] = train_rows
            t = metrics(train_rows)
            d = metrics(dev_rows)
            per_seed[str(seed)][condition] = {
                "training": t, "development": d,
                "train_minus_development_gap_pp": 100 * (t["pass_rate"] - d["pass_rate"]),
                "training_by_subskill": grouped(train_rows, "family"),
                "development_by_subskill": grouped(dev_rows, "family"),
                "training_by_archetype": grouped(train_rows, "archetype"),
                "development_by_archetype": grouped(dev_rows, "archetype"),
                "development_by_distance": grouped(dev_rows, "distance_group"),
                "exact_target_reproduction": sum(bool(r["exact_target_reproduction"]) for r in train_rows),
            }
        dense = per_seed[str(seed)]["dense"]["development"]["pass_rate"]
        diverse = per_seed[str(seed)]["diverse"]["development"]["pass_rate"]
        per_seed[str(seed)]["diverse_minus_dense_pp"] = 100 * (diverse - dense)
    paired = np.array([[int(records[(seed, "diverse")][tid]["hidden_pass"]) -
                        int(records[(seed, "dense")][tid]["hidden_pass"]) for tid in ids] for seed in seeds], dtype=float)
    task_effect = paired.mean(axis=0)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    family_cells = {family: [i for i, tid in enumerate(ids) if task_by_id[tid]["family"] == family]
                    for family in ("numeric_iteration", "array_reduction")}
    distance_cells = {(family, distance): [i for i, tid in enumerate(ids)
                                           if task_by_id[tid]["family"] == family and task_by_id[tid]["distance_group"] == distance]
                      for family in family_cells for distance in ("near", "compositional", "far")}
    if any(len(x) != 18 for x in family_cells.values()) or any(len(x) != 6 for x in distance_cells.values()):
        raise ValueError("Frozen stratification")
    overall_draws = np.empty(BOOTSTRAP_DRAWS)
    family_draws = {key: np.empty(BOOTSTRAP_DRAWS) for key in family_cells}
    distance_draws = {key: np.empty(BOOTSTRAP_DRAWS) for key in ("near", "compositional", "far")}
    for draw in range(BOOTSTRAP_DRAWS):
        sampled_family = {family: rng.choice(indices, size=len(indices), replace=True)
                          for family, indices in family_cells.items()}
        overall_draws[draw] = task_effect[np.concatenate(list(sampled_family.values()))].mean()
        for family, sampled in sampled_family.items():
            family_draws[family][draw] = task_effect[sampled].mean()
        sampled_distance = {key: rng.choice(indices, size=len(indices), replace=True)
                            for key, indices in distance_cells.items()}
        for distance in distance_draws:
            distance_draws[distance][draw] = task_effect[np.concatenate([sampled_distance[(family, distance)] for family in family_cells])].mean()
    archetypes = sorted({task["archetype"] for task in tasks})
    archetype_effect = {name: float(task_effect[[i for i, tid in enumerate(ids) if task_by_id[tid]["archetype"] == name]].mean())
                        for name in archetypes}
    block_values = np.array([archetype_effect[name] for name in archetypes])
    block_indices = rng.integers(0, len(archetypes), size=(BOOTSTRAP_DRAWS, len(archetypes)))
    block_draws = block_values[block_indices].mean(axis=1)
    audit = read("research/results/PHASE_3C_DEV1/structural_audit.json")
    nearest = {condition: {row["task_id"]: row for row in audit["nearest_per_eval_task"][condition.upper()]}
               for condition in ("dense", "diverse")}
    similarity_table = []
    for tid in ids:
        row = {"task_id": tid, "family": task_by_id[tid]["family"],
               "archetype": task_by_id[tid]["archetype"], "distance_group": task_by_id[tid]["distance_group"]}
        for condition in ("dense", "diverse"):
            neighbor = nearest[condition][tid]
            row[condition] = {"nearest_code_id": neighbor["nearest_code_id"],
                              "nearest_code_similarity": neighbor["nearest_code_similarity"],
                              "nearest_prompt_id": neighbor["nearest_prompt_id"],
                              "nearest_prompt_jaccard": neighbor["nearest_prompt_jaccard"],
                              "nearest_semantic_id": neighbor["nearest_semantic_id"],
                              "nearest_semantic_operation_jaccard": neighbor["nearest_semantic_operation_jaccard"],
                              "passes_by_seed": {str(seed): bool(records[(seed, condition)][tid]["hidden_pass"]) for seed in seeds}}
        similarity_table.append(row)
    high = [row for row in similarity_table if row["diverse"]["nearest_code_similarity"] >= .95]
    result = {"phase": "3C-DEV1", "status": "DEVELOPMENT_CONSUMED_DESCRIPTIVE_ONLY",
              "seeds": seeds, "per_seed": per_seed,
              "primary": {"definition": "unweighted three-seed mean of diverse minus dense development pass@1, percentage points",
                          "paired_seed_differences_pp": {str(seed): per_seed[str(seed)]["diverse_minus_dense_pp"] for seed in seeds},
                          "mean_difference_pp": float(100 * paired.mean()),
                          "task_cluster_95pct_interval_pp": [100 * x for x in ci(overall_draws)],
                          "archetype_block_sensitivity_95pct_interval_pp": [100 * x for x in ci(block_draws)]},
              "subskill_effect_pp": {family: {"mean": float(100 * task_effect[indices].mean()),
                                               "task_cluster_95pct_interval": [100 * x for x in ci(family_draws[family])]}
                                     for family, indices in family_cells.items()},
              "distance_effect_pp": {distance: {"mean": float(100 * task_effect[[i for i, tid in enumerate(ids) if task_by_id[tid]["distance_group"] == distance]].mean()),
                                               "task_cluster_95pct_interval": [100 * x for x in ci(draws)]}
                                     for distance, draws in distance_draws.items()},
              "archetype_effect_pp": {name: 100 * value for name, value in archetype_effect.items()},
              "bootstrap": {"draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED,
                            "task_strata": "overall and subskill within A subskill; distance within subskill x distance cell",
                            "archetype_blocks": 6, "intervals": "descriptive percentile 2.5/97.5; not a significance or PASS gate"},
              "nearest_training_similarity_by_task": similarity_table,
              "diverse_nearest_code_similarity_at_least_0p95_tasks": high,
              "frozen_manifest_sha256": sha256(ROOT / "research/protocols/phase3c_dev1_manifest.json"),
              "claims_boundary": "Development evidence only; neither suite nor result is untouched confirmatory evidence."}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "mean_difference_pp": result["primary"]["mean_difference_pp"],
                      "paired_seed_differences_pp": result["primary"]["paired_seed_differences_pp"]}))


if __name__ == "__main__":
    main()
