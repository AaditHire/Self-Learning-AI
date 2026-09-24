"""Descriptive analysis of the six frozen DEV2 seed-condition cells."""

import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from preflight_phase3c_dev2 import ROOT, read, sha256

RUNTIME = ROOT / ".runtime/phase3c_dev2"
OUTPUT = RUNTIME / "analysis.json"
SEEDS = (20270925, 20271013, 20271119)
CONDITIONS = ("isolated", "composition")
GROUPS = ("primitive_sanity", "novel_composition", "structural_transfer")
FAMILIES = ("numeric_iteration", "array_reduction")
DRAWS = 10000
BOOTSTRAP_SEED = 20281221


def metrics(rows):
    passed = sum(bool(x["hidden_pass"]) for x in rows)
    return {"passed": passed, "total": len(rows), "pass_rate": passed / len(rows),
            "failure_taxonomy": dict(sorted(Counter(x["failure_category"] for x in rows).items()))}


def groups(rows, key):
    buckets = defaultdict(list)
    for row in rows:
        buckets[key(row)].append(row)
    return {name: metrics(group) for name, group in sorted(buckets.items())}


def interval(values):
    return [float(np.quantile(values, .025)), float(np.quantile(values, .975))]


def main():
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    manifest = read("research/protocols/phase3c_dev2_manifest.json")
    if manifest["seeds"] != list(SEEDS):
        raise ValueError("Frozen seeds")
    preflight = read(str((RUNTIME / "preflight.json").relative_to(ROOT)))
    if preflight["status"] != "PASS_PREGRADIENT_CONTRACT" or preflight["manifest_sha256"] != sha256(ROOT / "research/protocols/phase3c_dev2_manifest.json"):
        raise ValueError("Preflight lineage")
    if preflight["execution_code_sha256"]["analyze"] != sha256(Path(__file__)):
        raise ValueError("Analysis code changed since preflight")
    tasks = read("benchmark/phase3c_dev2/a_development_eval_tasks.json")
    ids = [x["task_id"] for x in tasks]
    by_id = {x["task_id"]: x for x in tasks}
    if len(ids) != 48 or len(by_id) != 48:
        raise ValueError("Development IDs")
    records, per_seed = {}, {}
    for seed in SEEDS:
        per_seed[str(seed)] = {}
        for condition in CONDITIONS:
            run = read(str((RUNTIME / "training" / str(seed) / f"{condition}.json").relative_to(ROOT)))
            own = read(str((RUNTIME / "evaluations" / str(seed) / f"{condition}_training.json").relative_to(ROOT)))
            dev = read(str((RUNTIME / "evaluations" / str(seed) / f"{condition}_development.json").relative_to(ROOT)))
            if run["training"]["optimizer_steps"] != 24 or own["adapter_file_hashes"] != run["adapter"]["file_hashes"] or dev["adapter_file_hashes"] != run["adapter"]["file_hashes"]:
                raise ValueError("Run/evaluation lineage")
            tr, dv = own["records"], dev["records"]
            own_ids = {x["example_id"] for x in read(f"data/phase3c_dev2/a_{condition}_training_examples.json")}
            if (len(tr) != 60 or len(dv) != 48 or {x["task_id"] for x in tr} != own_ids
                    or {x["task_id"] for x in dv} != set(ids)
                    or len({x["task_id"] for x in tr}) != 60 or len({x["task_id"] for x in dv}) != 48):
                raise ValueError("Incomplete evaluation cell")
            records[seed, condition] = {x["task_id"]: x for x in dv}
            per_seed[str(seed)][condition] = {
                "own_training": metrics(tr),
                "exact_target_reproduction": sum(bool(x["exact_target_reproduction"]) for x in tr),
                "training_by_subskill": groups(tr, lambda x: x["family"]),
                "training_by_archetype": groups(tr, lambda x: x["family"] + ":" + x["archetype"]),
                "training_by_primitive_presence": {
                    p: metrics([x for x in tr if p in x["semantic_primitives"]])
                    for p in sorted({p for x in tr for p in x["semantic_primitives"]})},
                "development": metrics(dv),
                "development_by_group": groups(dv, lambda x: x["development_group"]),
                "development_by_subskill": groups(dv, lambda x: x["family"]),
                "development_by_group_subskill": groups(dv, lambda x: x["development_group"] + ":" + x["family"]),
                "development_by_archetype": groups(dv, lambda x: x["family"] + ":" + x["archetype"]),
                "primitive_sanity_by_primitive": groups([x for x in dv if x["development_group"] == "primitive_sanity"],
                                                        lambda x: x["semantic_primitives"][0]),
                "failure_stage_by_group_subskill": {
                    g + ":" + f: dict(sorted(Counter(x["failure_category"] for x in dv
                                                      if x["development_group"] == g and x["family"] == f).items()))
                    for g in GROUPS for f in FAMILIES},
            }
        per_seed[str(seed)]["paired_group_difference_pp"] = {
            g: 100 * (per_seed[str(seed)]["composition"]["development_by_group"][g]["pass_rate"]
                      - per_seed[str(seed)]["isolated"]["development_by_group"][g]["pass_rate"])
            for g in GROUPS}
    effects = np.array([[int(records[seed, "composition"][tid]["hidden_pass"])
                         - int(records[seed, "isolated"][tid]["hidden_pass"]) for tid in ids]
                        for seed in SEEDS], dtype=float)
    task_effect = effects.mean(axis=0)
    strata = {(g, f, a): [i for i, tid in enumerate(ids) if
                          (by_id[tid]["development_group"], by_id[tid]["family"], by_id[tid]["archetype"]) == (g, f, a)]
              for g in GROUPS for f in FAMILIES
              for a in sorted({x["archetype"] for x in tasks if x["development_group"] == g and x["family"] == f})}
    if len(strata) != 16 or any(len(v) != (2 if k[0] == "primitive_sanity" else 4) for k, v in strata.items()):
        raise ValueError("Frozen archetype strata")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = {g: np.empty(DRAWS) for g in GROUPS}
    draws["overall"] = np.empty(DRAWS)
    block = {g: np.empty(DRAWS) for g in GROUPS}
    for draw in range(DRAWS):
        sampled = {k: rng.choice(ix, size=len(ix), replace=True) for k, ix in strata.items()}
        for g in GROUPS:
            draws[g][draw] = task_effect[np.concatenate([v for k, v in sampled.items() if k[0] == g])].mean()
            chosen = []
            for f in FAMILIES:
                options = [ix for k, ix in strata.items() if k[0] == g and k[1] == f]
                chosen.extend(task_effect[options[j]].mean() for j in rng.integers(0, len(options), size=len(options)))
            block[g][draw] = np.mean(chosen)
        draws["overall"][draw] = task_effect[np.concatenate(list(sampled.values()))].mean()
    frozen = {x["task_id"]: x for x in read("research/results/PHASE_3C_DEV2/pre_gradient_audit.json")["structural_nearest"]}
    nearest = []
    for tid in ids:
        item = by_id[tid]
        row = {"task_id": tid, "group": item["development_group"], "subskill": item["family"],
               "archetype": item["archetype"], "composition_signature": item["composition_signature"],
               "required_primitives": item["semantic_primitives"], "control_flow": item["control_flow"],
               "goco_api": frozen[tid]["goco_api"], "conditions": {}}
        for condition in CONDITIONS:
            row["conditions"][condition] = frozen[tid]["conditions"][condition] | {
                "passes_by_seed": {str(seed): bool(records[seed, condition][tid]["hidden_pass"]) for seed in SEEDS}}
        nearest.append(row)
    primary_ix = [i for i, tid in enumerate(ids) if by_id[tid]["development_group"] == "novel_composition"]
    primary = {"definition": "COMPOSITION minus ISOLATED pass@1 on 16 Novel Composition IDs, unweighted mean across three paired seeds, percentage points",
               "paired_seed_differences_pp": {str(seed): per_seed[str(seed)]["paired_group_difference_pp"]["novel_composition"] for seed in SEEDS},
               "mean_difference_pp": float(100 * task_effect[primary_ix].mean()),
               "task_cluster_95pct_interval_pp": [100 * x for x in interval(draws["novel_composition"])],
               "archetype_block_sensitivity_95pct_interval_pp": [100 * x for x in interval(block["novel_composition"])]}
    result = {"phase": "3C-DEV2", "status": "DEVELOPMENT_CONSUMED_DESCRIPTIVE_ONLY",
              "seeds": list(SEEDS), "per_seed": per_seed, "primary": primary,
              "group_effect_pp": {g: {"mean": float(100 * task_effect[[i for i, tid in enumerate(ids) if by_id[tid]["development_group"] == g]].mean()),
                                      "task_cluster_95pct_interval": [100 * x for x in interval(draws[g])],
                                      "archetype_block_sensitivity_95pct_interval": [100 * x for x in interval(block[g])]}
                                  for g in GROUPS},
              "overall_effect_pp": {"mean": float(100 * task_effect.mean()),
                                    "task_cluster_95pct_interval": [100 * x for x in interval(draws["overall"])]},
              "archetype_effect_pp": {f + ":" + a: float(100 * task_effect[ix].mean()) for (g, f, a), ix in strata.items()},
              "bootstrap": {"draws": DRAWS, "seed": BOOTSTRAP_SEED,
                            "unit": "task ID with all six seed-condition outcomes retained",
                            "task_strata": "group x subskill x archetype",
                            "archetype_sensitivity": "whole archetype blocks resampled within subskill; four primary blocks, unstable",
                            "intervals": "descriptive percentile 2.5/97.5, no significance or PASS gate"},
              "structural_nearest_by_task": nearest,
              "high_similarity_at_least_0p95": [x["task_id"] for x in nearest if x["conditions"]["composition"]["nearest_code_similarity"] >= .95],
              "frozen_manifest_sha256": sha256(ROOT / "research/protocols/phase3c_dev2_manifest.json"),
              "claims_boundary": "Development-consumed evidence, not confirmatory continual-learning evidence."}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "primary_effect_pp": primary["mean_difference_pp"],
                      "paired_seed_effects_pp": primary["paired_seed_differences_pp"]}), flush=True)


if __name__ == "__main__":
    main()
