"""Pure C14 analysis of supplied scores; no data/model/output files are opened.

Interface: tasks is the kept evaluation-task metadata list (all 32 primary
tasks, plus any kept secondary tasks). Records use lowercase conditions,
suite='training' or 'confirmatory', and group='training' for own diagnostics.
Each of five case_outcomes is {passed: bool, execution_ok: bool,
expected_stdout: str}. These flags are evaluator verdicts, not inferred from
target reproduction. expected_stdout supplies R2-C's expected-output classes;
execution_ok distinguishes execution failures from output mismatches.
Training records additionally require exact_target: bool. Primary records
require block_id and graph. Public primary/sanity analysis accepts the same
complete record population as analyze; acquisition_gate accepts only training
records. Missing, unknown, duplicate or incoherent records raise GateStop.
"""

from __future__ import annotations

from collections import Counter
from decimal import Decimal, InvalidOperation

import numpy as np

from self_learning_ai.conf1_r1.gates_primary import GateStop
from self_learning_ai.conf1_r1.schedule import (
    CONDITIONS, DOMAINS, EVALUATION_TASKS, GROUPS, SEEDS, TRAINING_SLOTS,
)

BOOTSTRAP_SEED = 20290119
DRAW_COUNT = 10_000
INDETERMINATE = "INDETERMINATE_INSUFFICIENT_ACQUISITION"
SUPPORT = "CONFIRMATORY_SUPPORT_UNDER_CONF1"
NOT_CONFIRMED = "NOT_CONFIRMED_UNDER_CONF1"
TRAINING = {row["slot_id"]: dict(row, task_id=row["slot_id"], group="training") for row in TRAINING_SLOTS}
CANONICAL = {row["task_id"]: row for row in EVALUATION_TASKS}


def _stop(reason, **evidence):
    raise GateStop(reason, evidence)


def _catalog(tasks):
    catalog = {}
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("task_id"), str):
            _stop("invalid task metadata")
        identifier = task["task_id"]
        if identifier not in CANONICAL or identifier in catalog:
            _stop("unknown or duplicate task", task_id=identifier)
        expected = CANONICAL[identifier]
        keys = ["group", "family"]
        if expected["group"] == GROUPS[0]:
            keys += ["block_id", "graph"]
        if any(task.get(key) != expected[key] for key in keys):
            _stop("task metadata differs from frozen population", task_id=identifier)
        catalog[identifier] = expected
    primary = {k for k, v in CANONICAL.items() if v["group"] == GROUPS[0]}
    actual = {k for k, v in catalog.items() if v["group"] == GROUPS[0]}
    if actual != primary:
        _stop("incomplete primary task population", missing=sorted(primary - actual))
    return catalog


def _expected_number(text):
    if not isinstance(text, str):
        _stop("expected_stdout must be a string")
    try:
        value = Decimal(text)
    except InvalidOperation:
        _stop("invalid expected integer output")
    if not value.is_finite() or value < 0 or value != value.to_integral_value():
        _stop("expected output is not a nonnegative integer")
    return int(value)


def _row(record, metadata):
    if not isinstance(record, dict):
        _stop("score record must be an object")
    seed, condition, suite = (record.get(key) for key in ("seed", "condition", "suite"))
    identifier = record.get("task_id")
    if type(seed) is not int or seed not in SEEDS or condition not in CONDITIONS or suite not in ("training", "confirmatory"):
        _stop("unknown cell or suite", seed=seed, condition=condition, suite=suite)
    if not isinstance(identifier, str) or identifier not in metadata:
        _stop("unknown task record", task_id=identifier)
    task = metadata[identifier]
    if (suite == "training") != (task["group"] == "training"):
        _stop("task in wrong suite", task_id=identifier)
    keys = ["group", "family"] + (["block_id", "graph"] if task["group"] == GROUPS[0] else [])
    if any(record.get(key) != task[key] for key in keys):
        _stop("score metadata mismatch", task_id=identifier)
    flags = ["passed", "compile_ok"] + (["exact_target"] if suite == "training" else [])
    if any(type(record.get(key)) is not bool for key in flags):
        _stop("score flags must be JSON booleans", task_id=identifier)
    outcomes = record.get("case_outcomes")
    if not isinstance(outcomes, list) or len(outcomes) != 5:
        _stop("exactly five case outcomes required", task_id=identifier)
    for outcome in outcomes:
        if not isinstance(outcome, dict) or any(type(outcome.get(k)) is not bool for k in ("passed", "execution_ok")):
            _stop("invalid case outcome flags", task_id=identifier)
        _expected_number(outcome.get("expected_stdout"))
        if outcome["passed"] and not outcome["execution_ok"]:
            _stop("case pass without successful execution", task_id=identifier)
        if outcome["execution_ok"] and not record["compile_ok"]:
            _stop("execution without successful compilation", task_id=identifier)
    if record["passed"] != (record["compile_ok"] and all(o["passed"] for o in outcomes)):
        _stop("task pass differs from five-case semantic verdict", task_id=identifier)
    return seed, condition, suite, identifier


def _index(records, metadata, expected_keys):
    indexed, expected_outputs = {}, {}
    for record in records:
        key = _row(record, metadata)
        if key not in expected_keys:
            _stop("unexpected score record", key=list(key))
        if key in indexed:
            _stop("duplicate score record", key=list(key))
        signature = tuple(o["expected_stdout"] for o in record["case_outcomes"])
        output_key = (key[1] if key[2] == "training" else "both_conditions", key[2], key[3])
        if output_key in expected_outputs and expected_outputs[output_key] != signature:
            _stop("frozen expected outputs differ across cells", key=list(key))
        expected_outputs[output_key] = signature
        indexed[key] = record
    if set(indexed) != expected_keys:
        _stop("incomplete score records", missing=[list(k) for k in sorted(expected_keys - set(indexed))])
    return indexed


def _keys(suite, identifiers):
    return {(seed, condition, suite, identifier)
            for seed in SEEDS for condition in CONDITIONS for identifier in identifiers}


def validate_records(records, tasks):
    catalog = _catalog(tasks)
    metadata = TRAINING | catalog
    indexed = _index(records, metadata, _keys("training", TRAINING) | _keys("confirmatory", catalog))
    return indexed, catalog


def _acquisition(indexed):
    cells = []
    for seed in SEEDS:
        for condition in CONDITIONS:
            passed = sum(indexed[seed, condition, "training", tid]["passed"] for tid in TRAINING)
            cells.append({"seed": seed, "condition": condition, "passed": passed, "total": 60,
                          "threshold": 54, "acquired": passed >= 54})
    acquired = all(row["acquired"] for row in cells)
    return {"passed": acquired, "label": "ACQUISITION_PASS" if acquired else INDETERMINATE, "cells": cells}


def acquisition_gate(records):
    """Validate all 600 own-training records before applying the 54/60 gate."""
    return _acquisition(_index(records, TRAINING, _keys("training", TRAINING)))


def _counts(rows, flag="passed"):
    rows = list(rows)
    passed = sum(row[flag] for row in rows)
    return {"passed": passed, "total": len(rows), "rate": passed / len(rows) if rows else None}


def _paired(indexed, suite, identifiers, flag="passed"):
    identifiers = sorted(identifiers)
    per_seed = {}
    for seed in SEEDS:
        cells = {condition: _counts((indexed[seed, condition, suite, tid] for tid in identifiers), flag)
                 for condition in CONDITIONS}
        delta = (cells["composition"]["passed"] - cells["isolated"]["passed"]) / len(identifiers) if identifiers else None
        per_seed[str(seed)] = cells | {"difference": delta, "difference_pp": 100 * delta if delta is not None else None}
    pooled = {condition: _counts((indexed[seed, condition, suite, tid] for seed in SEEDS for tid in identifiers), flag)
              for condition in CONDITIONS}
    mean = sum(row["difference"] for row in per_seed.values()) / 5 if identifiers else None
    return {"per_seed": per_seed, "pooled": pooled, "mean_difference": mean,
            "mean_difference_pp": 100 * mean if mean is not None else None}


def _discordance(indexed, suite, identifiers, flag="passed"):
    names = ("both_pass", "both_fail", "isolated_only", "composition_only")
    per_seed = {}
    for seed in SEEDS:
        counts = Counter()
        for tid in identifiers:
            a, b = (indexed[seed, c, suite, tid][flag] for c in CONDITIONS)
            counts["both_pass" if a and b else "isolated_only" if a else "composition_only" if b else "both_fail"] += 1
        per_seed[str(seed)] = {name: counts[name] for name in names}
    return {"per_seed": per_seed, "pooled": {name: sum(row[name] for row in per_seed.values()) for name in names}}


def _primary(indexed, catalog, acquired):
    tasks = sorted(t for t, row in catalog.items() if row["group"] == GROUPS[0])
    positions = {tid: i for i, tid in enumerate(tasks)}
    blocks = {block: sorted(t for t in tasks if catalog[t]["block_id"] == block)
              for block in sorted({catalog[t]["block_id"] for t in tasks})}
    by_domain = {d: sorted(b for b in blocks if catalog[blocks[b][0]]["family"] == d) for d in DOMAINS}
    if len(tasks) != 32 or any(len(v) != 4 for v in blocks.values()) or any(len(v) != 4 for v in by_domain.values()):
        _stop("primary bootstrap requires eight four-task blocks")
    effect = np.array([[int(indexed[s, "composition", "confirmatory", t]["passed"]) -
                        int(indexed[s, "isolated", "confirmatory", t]["passed"]) for t in tasks]
                       for s in SEEDS], dtype=np.int8)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = np.empty(DRAW_COUNT)
    for replicate in range(DRAW_COUNT):
        seed_indices = rng.integers(0, 5, size=5)
        numeric_indices = rng.integers(0, 4, size=4)
        array_indices = rng.integers(0, 4, size=4)
        task_indices = [positions[t] for domain, chosen in zip(DOMAINS, (numeric_indices, array_indices))
                        for i in chosen for t in blocks[by_domain[domain][int(i)]]]
        draws[replicate] = effect[np.ix_(seed_indices, task_indices)].mean()
    interval = np.quantile(draws, [0.025, 0.975], method="linear").tolist()
    domain_sums = {d: int(effect[:, [positions[t] for t in tasks if catalog[t]["family"] == d]].sum()) for d in DOMAINS}
    block_sums = {b: int(effect[:, [positions[t] for t in ids]].sum()) for b, ids in blocks.items()}
    seed_sums = effect.sum(axis=1).tolist()
    qualifications = {
        "every_seed_nonnegative": all(n >= 0 for n in seed_sums),
        "at_least_four_seeds_positive": sum(n > 0 for n in seed_sums) >= 4,
        "both_domains_positive": all(n > 0 for n in domain_sums.values()),
        "at_least_six_blocks_positive": sum(n > 0 for n in block_sums.values()) >= 6,
    }
    total = int(effect.sum())
    criteria = {"sum_E": total, "sum_E_at_least_32": total >= 32, "lower_bound_strictly_positive": interval[0] > 0}
    label = SUPPORT if criteria["sum_E_at_least_32"] and criteria["lower_bound_strictly_positive"] else NOT_CONFIRMED
    if label == SUPPORT and not all(qualifications.values()):
        label += "_WITH_HETEROGENEITY"
    if not acquired:
        label = INDETERMINATE
    return {"label": label, "point": float(effect.mean()), "point_pp": 100 * float(effect.mean()),
            "criteria": criteria, "paired_seed_tasks": 160, "task_ids": tasks, "seed_order": list(SEEDS),
            "effect": effect.tolist(), "seed_sums": seed_sums, "domain_sums": domain_sums,
            "block_sums": block_sums, "qualifications": qualifications,
            "paired_rates": _paired(indexed, "confirmatory", tasks),
            "domains": {d: _paired(indexed, "confirmatory", [t for t in tasks if catalog[t]["family"] == d]) for d in DOMAINS},
            "blocks": {b: _paired(indexed, "confirmatory", ids) for b, ids in blocks.items()},
            "discordance": _discordance(indexed, "confirmatory", tasks),
            "bootstrap": {"rng_seed": BOOTSTRAP_SEED, "replicates": DRAW_COUNT,
                          "draw_order": ["seeds", "numeric_blocks", "array_blocks"],
                          "blocks_by_domain": by_domain, "quantile_method": "linear",
                          "draws": draws.tolist(), "interval": interval, "interval_pp": [100 * x for x in interval]}}


def primary_analysis(records, tasks):
    indexed, catalog = validate_records(records, tasks)
    return _primary(indexed, catalog, _acquisition(indexed)["passed"])


def _sanity(indexed, catalog):
    ids = [t for t, row in catalog.items() if row["group"] == GROUPS[1]]
    rates = _paired(indexed, "confirmatory", ids)
    if len(ids) < 12:
        return {"label": "SANITY_NOT_EVALUABLE", "kept": len(ids), "noncatastrophic": None, **rates}
    sums = [rates["per_seed"][str(s)]["composition"]["passed"] - rates["per_seed"][str(s)]["isolated"]["passed"] for s in SEEDS]
    # Integer comparisons make the inclusive -10 pp/-25 pp boundaries exact.
    mean_ok = 10 * sum(sums) >= -5 * len(ids)
    seeds_ok = all(4 * n >= -len(ids) for n in sums)
    return {"label": "NONCATASTROPHIC" if mean_ok and seeds_ok else "CATASTROPHIC",
            "kept": len(ids), "noncatastrophic": mean_ok and seeds_ok,
            "mean_at_least_minus_10_pp": mean_ok, "no_seed_below_minus_25_pp": seeds_ok, **rates}


def sanity_qualifier(records, tasks):
    indexed, catalog = validate_records(records, tasks)
    return _sanity(indexed, catalog)


def _failure_stage(row):
    if row["passed"]:
        return "PASS"
    if not row["compile_ok"]:
        return "COMPILE"
    if any(not outcome["execution_ok"] for outcome in row["case_outcomes"]):
        return "EXECUTION"
    return "OUTPUT_MISMATCH"


def _descriptive(indexed, catalog):
    primary = [t for t, r in catalog.items() if r["group"] == GROUPS[0]]
    structural = [t for t, r in catalog.items() if r["group"] == GROUPS[2]]
    or_split = {
        d: {name: _paired(indexed, "confirmatory", [t for t in primary if catalog[t]["family"] == d and
                                                 (catalog[t]["graph"] in ("G1", "G4")) == has_or])
            for name, has_or in (("OR_containing", True), ("OR_free", False))} for d in DOMAINS}
    own = {"semantic": _paired(indexed, "training", TRAINING),
           "exact_target": _paired(indexed, "training", TRAINING, "exact_target"),
           "by_family": {d: {flag: _paired(indexed, "training", [t for t, r in TRAINING.items() if r["family"] == d], flag)
                             for flag in ("passed", "exact_target")} for d in DOMAINS},
           "by_archetype": {f"{d}:{pair}": {flag: _paired(indexed, "training", [t for t, r in TRAINING.items()
                              if r["family"] == d and t.split("-")[-2] == pair], flag)
                              for flag in ("passed", "exact_target")}
                              for d in DOMAINS for pair in ("01", "02", "03", "12", "13", "23")}}
    failure_stages = {
        f"{s}/{c}": {stage: sum(_failure_stage(indexed[s, c, "confirmatory", t]) == stage for t in structural)
                     for stage in ("PASS", "COMPILE", "EXECUTION", "OUTPUT_MISMATCH")}
        for s in SEEDS for c in CONDITIONS}
    output_classes = {}
    for condition in CONDITIONS:
        output_classes[condition] = {}
        for domain in DOMAINS:
            output_classes[condition][domain] = {}
            for suite, ids in (("training", [t for t, r in TRAINING.items() if r["family"] == domain]),
                               ("primary", [t for t in primary if catalog[t]["family"] == domain])):
                classes = set()
                for seed in SEEDS:
                    for tid in ids:
                        record = indexed[seed, condition, "training" if suite == "training" else "confirmatory", tid]
                        for outcome in record["case_outcomes"]:
                            value = _expected_number(outcome["expected_stdout"])
                            classes.add("ZERO" if value == 0 else "POSITIVE" if value < 10 else "MULTIDIGIT")
                output_classes[condition][domain][suite] = [c for c in ("ZERO", "POSITIVE", "MULTIDIGIT") if c in classes]
    return {"OR_by_domain": or_split, "own_training": own,
            "structural_transfer": {"rates": _paired(indexed, "confirmatory", structural),
                "by_family": {d: _paired(indexed, "confirmatory", [t for t in structural if catalog[t]["family"] == d]) for d in DOMAINS},
                "by_block": {f"{d}:{structure}": _paired(indexed, "confirmatory", [t for t in structural if
                            catalog[t]["family"] == d and catalog[t]["structure"] == structure])
                            for d in DOMAINS for structure in ("prefix_running_pair", "two_pass_product")},
                "failure_stages": failure_stages},
            "paired_discordance": {**{g: _discordance(indexed, "confirmatory", [t for t, r in catalog.items() if r["group"] == g]) for g in GROUPS},
                "own_training_semantic": _discordance(indexed, "training", TRAINING),
                "own_training_exact_target": _discordance(indexed, "training", TRAINING, "exact_target")},
            "K7_expected_output_classes": output_classes}


def descriptive_blocks(records, tasks):
    indexed, catalog = validate_records(records, tasks)
    return _descriptive(indexed, catalog)


def analyze(records, tasks):
    records = list(records)
    training_records = [r for r in records if isinstance(r, dict) and r.get("suite") == "training"]
    acquisition = acquisition_gate(training_records)
    if not acquisition["passed"]:
        if len(training_records) != len(records):
            _stop("confirmatory records forbidden after failed acquisition")
        indexed = _index(training_records, TRAINING, _keys("training", TRAINING))
        return {"label": INDETERMINATE, "acquisition": acquisition,
                "descriptive": {"own_training": _descriptive(indexed, {})["own_training"]},
                "counts": {"records": len(indexed), "training_slots": 60}}
    indexed, catalog = validate_records(records, tasks)
    primary = _primary(indexed, catalog, acquisition["passed"])
    return {"label": primary["label"], "acquisition": acquisition, "primary": primary,
            "sanity": _sanity(indexed, catalog), "descriptive": _descriptive(indexed, catalog),
            "counts": {"records": len(indexed), "training_slots": 60, "primary_tasks": 32,
                       "sanity_kept": sum(r["group"] == GROUPS[1] for r in catalog.values()),
                       "structural_kept": sum(r["group"] == GROUPS[2] for r in catalog.values())}}
