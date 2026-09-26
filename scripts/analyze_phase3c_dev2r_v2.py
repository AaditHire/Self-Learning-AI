"""Read frozen DEV2R v2 outputs; calculate only protocol-specified summaries."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime/phase3c_dev2r/evaluations"
OUTPUT = ROOT / "research/results/PHASE_3C_DEV2R_V2/analysis.json"
SEEDS = (20270925, 20271013, 20271119)
CONDITIONS = ("isolated", "composition")
GROUPS = ("primitive_sanity", "novel_composition", "structural_transfer")
FAMILIES = ("numeric_iteration", "array_reduction")
PENDING = {(20270925, "composition"), (20271013, "isolated"),
           (20271013, "composition"), (20271119, "isolated"),
           (20271119, "composition")}
DRAW_COUNT = 10_000
BOOTSTRAP_SEED = 20270926


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts(rows):
    return {"passed": sum(bool(r["hidden_pass"]) for r in rows), "total": len(rows)}


def bucket(rows, key):
    groups = defaultdict(list)
    for row in rows:
        groups[key(row)].append(row)
    return {name: counts(group) for name, group in sorted(groups.items())}


def transitions(a, b, ids):
    out = Counter()
    for tid in ids:
        left, right = bool(a[tid]["hidden_pass"]), bool(b[tid]["hidden_pass"])
        name = ("both_pass" if left and right else "isolated_only" if left else
                "composition_only" if right else "both_fail")
        out[name] += 1
    return {name: out[name] for name in
            ("both_pass", "both_fail", "isolated_only", "composition_only")}


def checked_cell(seed: int, condition: str, suite: str, expected_ids: set[str]):
    folder = RUNTIME / str(seed) / condition / suite
    aggregate = read(folder / "aggregate.json")
    records = aggregate["records"]
    if (aggregate["seed"] != seed or aggregate["condition"] != condition or
            aggregate["suite"] != suite or len(records) != len(expected_ids)):
        raise ValueError(f"Cell identity/count: {folder}")
    rows = {row["task_id"]: row for row in records}
    if set(rows) != expected_ids:
        raise ValueError(f"Cell task IDs: {folder}")
    for tid, row in rows.items():
        stem = folder / "tasks" / tid
        generation = read(stem.with_suffix(".generation.json"))
        primary = read(stem.with_suffix(".primary.json"))
        if (generation["status"] != "GENERATION_DURABLE" or
                primary["status"] != "PRIMARY_SCORE_DURABLE" or
                generation["raw_generation"] != primary["raw_generation"] or
                primary["raw_generation"] != row["raw_generation"] or
                primary["score"]["hidden_pass"] != row["hidden_pass"] or
                len(primary["score"]["case_results"]) != 5):
            raise ValueError(f"Checkpoint mismatch: {stem}")
        if suite == "training" and primary["exact_target_reproduction"] != row["exact_target_reproduction"]:
            raise ValueError(f"Exact target mismatch: {stem}")
    return aggregate, rows


def bootstrap(effect: np.ndarray, indices_by_scope: dict[str, list[int]],
              blocks: dict[tuple[str, str, str], list[int]]):
    """Two-way paired seed/archetype bootstrap, retaining all block variants."""
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = {scope: np.empty(DRAW_COUNT) for scope in indices_by_scope}
    strata = {(group, family): sorted((key for key in blocks
                                      if key[0] == group and key[1] == family))
              for group in GROUPS for family in FAMILIES}
    for draw in range(DRAW_COUNT):
        seed_ix = rng.integers(0, len(SEEDS), size=len(SEEDS))
        sampled = {}
        for group in GROUPS:
            for family in FAMILIES:
                options = strata[group, family]
                chosen = rng.integers(0, len(options), size=len(options))
                sampled[group, family] = [i for j in chosen for i in blocks[options[j]]]
        for scope, base_indices in indices_by_scope.items():
            allowed = set(base_indices)
            task_ix = [i for block in sampled.values() for i in block if i in allowed]
            draws[scope][draw] = effect[np.ix_(seed_ix, task_ix)].mean()
    return {scope: {"mean_difference_pp": float(100 * effect[:, indices].mean()),
                    "percentile_95_interval_pp": [float(100 * value) for value in
                                                  np.quantile(draws[scope], [.025, .975])]}
            for scope, indices in indices_by_scope.items()}


def main():
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    manifest_path = ROOT / "research/protocols/phase3c_dev2r_v2_manifest.json"
    manifest = read(manifest_path)
    if manifest["model_execution_authorized"] is not True or manifest["status"] != "FROZEN_PRE_EXECUTION":
        raise ValueError("Execution state")
    if set(manifest["pending_own_training_cells"]) != {f"{seed}/{cond}" for seed, cond in PENDING}:
        raise ValueError("Pending diagnostic cells")
    tasks = read(ROOT / "benchmark/phase3c_dev2r_v2/a_development_eval_tasks.json")
    ids = [row["task_id"] for row in tasks]
    if len(ids) != 48 or len(set(ids)) != 48:
        raise ValueError("Development suite IDs")
    by_id = {row["task_id"]: row for row in tasks}
    frozen_nearest = {item["task_id"]: item for item in
                      read(ROOT / "research/results/PHASE_3C_DEV2R/structural_audit.json")["nearest"]}
    frozen_nearest.update({item["task_id"]: item for item in
                           read(ROOT / "research/results/PHASE_3C_DEV2R_AMENDMENT/v2_pre_execution_audit.json")["replacement_nearest"]})
    frozen_nearest = {tid: item for tid, item in frozen_nearest.items() if tid in set(ids)}
    if set(frozen_nearest) != set(ids):
        raise ValueError("Nearest-neighbor audit IDs")
    development, own_training, per_cell, diagnostics = {}, {}, {}, {}
    for seed in SEEDS:
        per_cell[str(seed)] = {}
        for condition in CONDITIONS:
            aggregate, records = checked_cell(seed, condition, "development", set(ids))
            development[seed, condition] = records
            rows = list(records.values())
            per_cell[str(seed)][condition] = {
                "overall": counts(rows),
                "by_group": bucket(rows, lambda r: r["development_group"]),
                "by_family": bucket(rows, lambda r: r["family"]),
                "by_group_family": bucket(rows, lambda r: r["development_group"] + ":" + r["family"]),
                "by_archetype": bucket(rows, lambda r: r["development_group"] + ":" + r["family"] + ":" + r["archetype"]),
                "failure_taxonomy": dict(sorted(Counter(r["failure_category"] for r in rows).items())),
                "failure_by_group_family": {
                    group + ":" + family: dict(sorted(Counter(r["failure_category"] for r in rows
                        if r["development_group"] == group and r["family"] == family).items()))
                    for group in GROUPS for family in FAMILIES},
                "five_case_outcomes": {str(i): {"passed": sum(bool(r["case_results"][i-1]["passed"]) for r in rows),
                                                 "total": len(rows)} for i in range(1, 6)},
                "stage_counts": {name: sum(bool(r[name]) for r in rows)
                                 for name in ("parse_success", "compile_success", "execution_success", "structural_requirements_met")},
                "error_phase": dict(sorted(Counter(str(r["error_phase"]) for r in rows).items())),
            }
            if (seed, condition) in PENDING:
                prefix = ROOT / f"data/phase3c_dev2/a_{condition}_training_examples.json"
                expected = {r["example_id"] for r in read(prefix)}
                training_aggregate, training_rows = checked_cell(seed, condition, "training", expected)
                own_training[seed, condition] = training_rows
                items = list(training_rows.values())
                diagnostics[f"{seed}/{condition}"] = {
                    "evaluator": "DEV2R v2 frozen evaluator", "overall": counts(items),
                    "exact_target_reproduction": sum(bool(r["exact_target_reproduction"]) for r in items),
                    "by_family": {key: {**counts(group), "exact_target_reproduction":
                        sum(bool(r["exact_target_reproduction"]) for r in group)}
                        for key, group in sorted(_group(items, lambda r: r["family"]).items())},
                    "by_family_archetype": {key: {**counts(group), "exact_target_reproduction":
                        sum(bool(r["exact_target_reproduction"]) for r in group)}
                        for key, group in sorted(_group(items, lambda r: r["family"] + ":" + r["archetype"]).items())},
                    "aggregate_sha256": sha(RUNTIME / str(seed) / condition / "training/aggregate.json"),
                }
            else:
                if (RUNTIME / str(seed) / condition / "training").exists():
                    raise ValueError("Historical diagnostic rerun")
    historical_path = ROOT / "research/artifacts/phase3c-dev2/raw/evaluations/20270925/isolated_training.json"
    historical = read(historical_path)["records"]
    diagnostics["20270925/isolated"] = {
        "evaluator": "Historical DEV2 evaluator; not rerun under DEV2R v2",
        "overall": counts(historical),
        "exact_target_reproduction": sum(bool(r["exact_target_reproduction"]) for r in historical),
        "by_family": {key: {**counts(group), "exact_target_reproduction":
            sum(bool(r["exact_target_reproduction"]) for r in group)}
            for key, group in sorted(_group(historical, lambda r: r["family"]).items())},
        "by_family_archetype": {key: {**counts(group), "exact_target_reproduction":
            sum(bool(r["exact_target_reproduction"]) for r in group)}
            for key, group in sorted(_group(historical, lambda r: r["family"] + ":" + r["archetype"]).items())},
        "source_sha256": sha(historical_path),
    }
    transitions_by_seed = {}
    for seed in SEEDS:
        a, b = development[seed, "isolated"], development[seed, "composition"]
        transitions_by_seed[str(seed)] = {
            "overall": transitions(a, b, ids),
            **{group: transitions(a, b, [tid for tid in ids if by_id[tid]["development_group"] == group])
               for group in GROUPS},
        }
    pooled = {scope: {key: sum(transitions_by_seed[str(seed)][scope][key] for seed in SEEDS)
                      for key in ("both_pass", "both_fail", "isolated_only", "composition_only")}
              for scope in ("overall", *GROUPS)}
    effect = np.array([[int(development[seed, "composition"][tid]["hidden_pass"])
                        - int(development[seed, "isolated"][tid]["hidden_pass"]) for tid in ids]
                       for seed in SEEDS], dtype=float)
    scopes = {group: [i for i, tid in enumerate(ids) if by_id[tid]["development_group"] == group]
              for group in GROUPS}
    scopes["overall"] = list(range(len(ids)))
    scopes.update({family: [i for i, tid in enumerate(ids) if by_id[tid]["family"] == family]
                   for family in FAMILIES})
    blocks = defaultdict(list)
    for i, tid in enumerate(ids):
        row = by_id[tid]
        blocks[row["development_group"], row["family"], row["archetype"]].append(i)
    if (len(blocks) != 16 or any(len(v) != (2 if k[0] == "primitive_sanity" else 4)
                                 for k, v in blocks.items())):
        raise ValueError("Frozen archetype blocks")
    bootstrap_result = bootstrap(effect, scopes, blocks)
    primary_ids = [tid for tid in ids if by_id[tid]["development_group"] == "novel_composition"]
    primary = {"definition": "Paired COMPOSITION minus ISOLATED pass@1 on 16 Novel Composition tasks",
               "per_seed": {str(seed): {
                   "isolated": counts([development[seed, "isolated"][tid] for tid in primary_ids]),
                   "composition": counts([development[seed, "composition"][tid] for tid in primary_ids]),
                   "difference_pp": float(100 * effect[j, scopes["novel_composition"]].mean())}
                   for j, seed in enumerate(SEEDS)},
               "pooled_paired_seed_tasks": 48,
               "pooled_transitions": pooled["novel_composition"],
               **bootstrap_result["novel_composition"]}
    nearest_rows = []
    for tid in ids:
        item = frozen_nearest[tid]
        nearest_rows.append({"task_id": tid, "group": by_id[tid]["development_group"],
            "family": by_id[tid]["family"], "archetype": by_id[tid]["archetype"],
            "conditions": {condition: {
                "nearest_code_similarity": item["conditions"][condition]["nearest_code_similarity"],
                "nearest_prompt_jaccard": item["conditions"][condition]["nearest_prompt_jaccard"],
                "passed_by_seed": {str(seed): bool(development[seed, condition][tid]["hidden_pass"])
                                   for seed in SEEDS}}
                for condition in CONDITIONS}})
    result = {"phase": "3C-DEV2R-v2", "status": "DEVELOPMENT_CONSUMED_DESCRIPTIVE_ONLY",
              "authorization_commit": "53ac2ca264239d2c74c08aa47533cb6dacb3650c",
              "authorization_manifest_sha256": sha(manifest_path),
              "per_cell": per_cell, "primary_novel_composition": primary,
              "paired_transitions_by_seed": transitions_by_seed, "pooled_transitions": pooled,
              "bootstrap": {"replicates": DRAW_COUNT, "rng_seed": BOOTSTRAP_SEED,
                  "resampling": "paired seeds and whole archetype blocks with replacement within each group and family; retain all variants",
                  "interval": "descriptive percentile 2.5/97.5", "results": bootstrap_result},
              "own_training_diagnostics": diagnostics,
              "frozen_nearest_pass_fail": nearest_rows,
              "limits": ["development suite only", "correlated variants and three paired seeds",
                         "historical own-training cell uses the original DEV2 evaluator"]}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"primary": primary, "overall": bootstrap_result["overall"]}))


def _group(rows, key):
    out = defaultdict(list)
    for row in rows:
        out[key(row)].append(row)
    return out


if __name__ == "__main__":
    main()
