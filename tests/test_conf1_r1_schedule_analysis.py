"""I5a-v2 fixture validation and explicitly filtered, path-only seed audit."""

import copy
import hashlib
import json
import os
import random
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
EXCLUDED_FILES = {
    "benchmark/tasks.json", "benchmark/hidden_tests.json", "benchmark/reference_solutions.json",
    "research/protocols/phase3c_conf1_v3_synthetic_expected_labels.json",
}
EXCLUDED_COMPONENTS = {".runtime", ".git", ".models", ".artifacts", ".tools"}
CONSUMED = ("phase1r", "phase1s", "phase1t", "phase2a", "phase2b", "phase3a",
            "phase3b", "phase3c", "phase3c_dev1", "phase3c_dev2", "phase3c_dev2r", "phase3c_dev2r_v2")
INCLUDES = ("research/protocols", "research/manifests", "research/results", "docs", "scripts",
            "src", "tests", "prompts", "data") + tuple("benchmark/" + name for name in CONSUMED)


def excluded(relative):
    path = Path(Path(relative).as_posix().casefold())
    return (path.as_posix() in EXCLUDED_FILES or path.name == "hidden_cases.json" or
            any(part in EXCLUDED_COMPONENTS for part in path.parts) or
            path.parts[:2] in (("research", "artifacts"), ("research", "adapters")))


def guard_repository(event, args):
    paths, write = [], False
    if event == "open":
        path, mode, flags = args
        paths = [path]
        write = ((isinstance(mode, str) and any(c in mode for c in "wax+")) or
                 bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
    elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.utime"):
        paths, write = [args[0]], True
    elif event in ("os.rename", "os.link", "os.symlink"):
        paths, write = list(args[:2]), True
    for path in paths:
        if isinstance(path, (str, bytes, os.PathLike)):
            resolved = Path(os.fsdecode(path)).resolve()
            if resolved.is_relative_to(ROOT):
                relative = resolved.relative_to(ROOT)
                if write:
                    raise AssertionError(f"repository write during tests: {event}: {relative}")
                if excluded(relative):
                    raise AssertionError(f"excluded path opened: {relative}")


sys.addaudithook(guard_repository)
import numpy as np
from self_learning_ai.conf1_r1 import analysis, schedule
from self_learning_ai.conf1_r1.gates_primary import GateStop

SEED_LITERALS = ("20280117", "20280223", "20280329", "20280411", "20280507", "20290119", "20290307")


def emit(capsys, label, value):
    with capsys.disabled():
        print(label + ": " + json.dumps(value, sort_keys=True), flush=True)


def snapshot():
    return {p.relative_to(ROOT).as_posix(): (p.stat().st_size, p.stat().st_mtime_ns)
            for p in ROOT.rglob("*") if p.is_file()}


@pytest.fixture(scope="module", autouse=True)
def repository_unchanged():
    before = snapshot()
    yield
    assert snapshot() == before


def fixture_tasks():
    ledger = json.loads((ROOT / "research/protocols/phase3c_conf1_slots.json").read_bytes())
    tasks = []
    for group in ("primary", "primitive_sanity", "structural_transfer"):
        for original in ledger["slots"][group]:
            row = dict(original)
            if row["family"] == "array_reduction" and row.get("graph") == "G3":
                row.update(task_id=row["task_id"].replace("-G3-", "-G3P-"),
                           graph="G3P", block_id="array_reduction:G3P")
            tasks.append(row)
    return tasks


def set_pass(row, passed):
    row["passed"] = bool(passed)
    row["compile_ok"] = True
    for outcome in row["case_outcomes"]:
        outcome.update(passed=bool(passed), execution_ok=True)


def fixture_records(effect=None, tasks=None):
    tasks = fixture_tasks() if tasks is None else tasks
    primary = sorted(t["task_id"] for t in tasks if t["group"] == "novel_composition")
    effect = np.zeros((5, 32), dtype=int) if effect is None else np.asarray(effect)
    positions = {tid: i for i, tid in enumerate(primary)}
    records = []
    for si, seed in enumerate(schedule.SEEDS):
        for condition in schedule.CONDITIONS:
            for task in [dict(s, task_id=s["slot_id"], group="training") for s in schedule.TRAINING_SLOTS] + tasks:
                training = task["group"] == "training"
                row = {k: task[k] for k in ("task_id", "group", "family")}
                row.update(seed=seed, condition=condition, suite="training" if training else "confirmatory",
                           case_outcomes=[{"passed": False, "execution_ok": True, "expected_stdout": value}
                                          for value in ("0.0", "1.0", "10.0", "2.0", "11.0")])
                if training:
                    row["exact_target"] = True
                if task["group"] == "novel_composition":
                    row.update(block_id=task["block_id"], graph=task["graph"])
                    e = int(effect[si, positions[task["task_id"]]])
                    passed = e > 0 if condition == "composition" else e < 0
                else:
                    passed = training
                set_pass(row, passed)
                records.append(row)
    return records, tasks


def compact(report):
    p = report["primary"]
    return {"label": report["label"], "point": p["point"], "sum_E": p["criteria"]["sum_E"],
            "integer_criterion": p["criteria"]["sum_E_at_least_32"],
            "interval": p["bootstrap"]["interval"], "qualifications": p["qualifications"]}


def test_t1_schedule(capsys):
    state = random.getstate()
    for seed in schedule.SEEDS:
        isolated = schedule.training_schedule(seed)
        composition = schedule.training_schedule(seed)
        assert isolated == composition == schedule.training_schedule(seed)
        assert isolated["exposures"] == 180 and isolated["optimizer_steps"] == 24
        assert isolated["checkpoint_epoch"] == 3
        assert Counter(t for e in isolated["epochs"] for t in e["slot_ids"]) == {t: 3 for t in schedule.SLOT_IDS}
        for epoch in isolated["epochs"]:
            expected = sorted(schedule.SLOT_IDS, key=lambda t: t.encode("utf-8"))
            random.Random(seed + 100003 * epoch["epoch"]).shuffle(expected)
            assert epoch["slot_ids"] == expected
            # Independently execute the DEV2 loop's boundary predicate.
            boundaries = [micro for micro in range(1, 61) if micro % 8 == 0 or micro == 60]
            assert epoch["optimizer_step_microbatches"] == boundaries
            assert epoch["accumulation_sizes"] == [8] * 7 + [4] and epoch["loss_divisor"] == 8
        assert [n for e in isolated["epochs"] for n in e["optimizer_step_numbers"]] == list(range(1, 25))
    assert random.getstate() == state
    assert schedule.cell_order() == [{"seed": s, "condition": c} for s in schedule.SEEDS for c in ("isolated", "composition")]
    emit(capsys, "I5a T1", {"cells": schedule.cell_order(), "exposures_per_cell": 180, "steps_per_cell": 24,
         "boundaries": [e["optimizer_step_microbatches"] for e in isolated["epochs"]],
         "global_exposure_boundaries": [e["optimizer_step_exposures"] for e in isolated["epochs"]],
         "steps_at_epoch_ends": [8, 16, 24], "remainder_loss_divisor": 8})


def test_t2_rng_and_order(capsys):
    answers = []
    for seed, tid in ((20280117, "CONF1-NC-NU-G1-R0"), (20280507, "CONF1-TR-AR-23-V4")):
        independent = int.from_bytes(hashlib.sha256(("20290307|" + str(seed) + "|" + tid).encode("utf-8")).digest()[:8],
                                     byteorder="big") % 4294967296
        for condition in ("isolated", "composition"):
            assert schedule.task_rng_seed(seed, tid) == independent
        answers.append({"seed": seed, "task_id": tid, "rng_seed": independent})
    tasks = fixture_tasks()
    groups = {g: [t["task_id"] for t in reversed(tasks) if t["group"] == g] for g in schedule.GROUPS}
    ordered = schedule.confirmatory_order(groups)
    sorted_groups = {g: sorted(groups[g]) for g in schedule.GROUPS}
    expected = [tid for i in range(16) for tid in (sorted_groups["novel_composition"][2*i],
                 sorted_groups["novel_composition"][2*i+1], sorted_groups["primitive_sanity"][i],
                 sorted_groups["structural_transfer"][i])]
    assert ordered == expected and len(ordered) == 64
    dropped = {sorted_groups["primitive_sanity"][0], sorted_groups["structural_transfer"][3]}
    kept = {g: [tid for tid in ids if tid not in dropped] for g, ids in groups.items()}
    assert schedule.confirmatory_order(kept) == [tid for tid in expected if tid not in dropped]
    assert schedule.own_training_order(reversed(schedule.SLOT_IDS)) == list(schedule.SLOT_IDS)
    assert all(set(row) == {"task_id", "group", "family", "graph", "block_id"} for row in schedule.PRIMARY_TASKS)
    emit(capsys, "I5a T2", {"known_answers": answers, "positions": len(ordered),
         "first_eight": ordered[:8], "dropped": sorted(dropped), "kept_positions": 62,
         "drop_positions_skipped": True, "own_training_sorted": True})


def test_t3_all_pass_and_zero(capsys):
    outcomes = {}
    for name, value, label in (("all_composition_pass", 1, analysis.SUPPORT), ("zero_effect", 0, analysis.NOT_CONFIRMED)):
        records, tasks = fixture_records(np.full((5, 32), value))
        report = analysis.analyze(records, tasks)
        assert report["label"] == label and report["primary"]["point"] == value
        assert report["primary"]["bootstrap"]["interval"] == [float(value)] * 2
        json.dumps(report, allow_nan=False)
        outcomes[name] = compact(report)
    emit(capsys, "I5a T3a-b", outcomes)


def test_t3_integer_boundary(capsys):
    tasks = fixture_tasks()
    primary = sorted((t for t in tasks if t["group"] == "novel_composition"), key=lambda t: t["task_id"])
    block_ids = sorted({t["block_id"] for t in primary})
    position = {t["task_id"]: i for i, t in enumerate(primary)}
    first = {block: sorted(t["task_id"] for t in primary if t["block_id"] == block)[0] for block in block_ids}
    effect = np.zeros((5, 32), dtype=int)
    for block in block_ids[:6]:
        effect[:, position[first[block]]] = 1
    effect[:2, position[first[block_ids[6]]]] = 1
    results = {}
    for total in (32, 31):
        records, task_list = fixture_records(effect, tasks)
        report = analysis.analyze(records, task_list)
        assert report["primary"]["criteria"]["sum_E"] == total
        assert report["primary"]["bootstrap"]["interval"][0] > 0
        assert report["primary"]["criteria"]["sum_E_at_least_32"] is (total == 32)
        assert report["label"] == (analysis.SUPPORT if total == 32 else analysis.NOT_CONFIRMED)
        results[str(total)] = compact(report)
        effect[1, position[first[block_ids[6]]]] = 0
    effect[:] = 0
    effect[0, :] = 1
    records, task_list = fixture_records(effect, tasks)
    report = analysis.analyze(records, task_list)
    assert report["primary"]["criteria"]["sum_E_at_least_32"] is True
    assert report["primary"]["bootstrap"]["interval"][0] == 0
    assert report["label"] == analysis.NOT_CONFIRMED
    results["32_lower_bound_zero"] = compact(report)
    emit(capsys, "I5a T3c", results)


def test_t3_acquisition(capsys):
    records, tasks = fixture_records(np.ones((5, 32), dtype=int))
    training = [r for r in records if r["suite"] == "training" and r["seed"] == schedule.SEEDS[0] and r["condition"] == "isolated"]
    for row in training[:7]:
        set_pass(row, False)  # Exact-target flags deliberately remain true.
    gate = analysis.acquisition_gate([r for r in records if r["suite"] == "training"])
    assert gate["passed"] is False and gate["cells"][0]["passed"] == 53
    report = analysis.analyze([r for r in records if r["suite"] == "training"], tasks)
    assert report["label"] == analysis.INDETERMINATE and "primary" not in report
    assert report["descriptive"]["own_training"]["exact_target"]["per_seed"][str(schedule.SEEDS[0])]["isolated"]["passed"] == 60
    first_primary = next(r for r in records if r["group"] == "novel_composition")
    primary_missing = [r for r in records if r is not first_primary]
    with pytest.raises(GateStop, match="confirmatory records forbidden"):
        analysis.analyze(primary_missing, tasks)
    # Inclusive acquisition boundary.
    set_pass(training[6], True)
    assert analysis.acquisition_gate([r for r in records if r["suite"] == "training"])["passed"] is True
    emit(capsys, "I5a T3d", {"53_semantic_60_exact": report["label"], "54_semantic": "ACQUISITION_PASS",
                           "confirmatory_supplied_when_acquisition_fails": "STOP"})


@pytest.mark.parametrize("fault", ["missing", "duplicate", "unknown_task", "unknown_seed", "wrong_block",
                                   "nonboolean", "four_cases", "incoherent_pass", "changed_expected", "unknown_metadata"])
def test_t3_record_refusals(fault, capsys):
    records, tasks = fixture_records()
    primary = next(r for r in records if r["group"] == "novel_composition")
    if fault == "missing":
        records.remove(primary)
    elif fault == "duplicate":
        records.append(copy.deepcopy(primary))
    elif fault == "unknown_task":
        primary["task_id"] = "UNKNOWN"
    elif fault == "unknown_seed":
        primary["seed"] = 1
    elif fault == "wrong_block":
        primary["block_id"] = "wrong"
    elif fault == "nonboolean":
        primary["passed"] = 0
    elif fault == "four_cases":
        primary["case_outcomes"].pop()
    elif fault == "incoherent_pass":
        primary["passed"] = True
    elif fault == "changed_expected":
        primary["case_outcomes"][0]["expected_stdout"] = "2.0"
    else:
        tasks[0]["task_id"] = "UNKNOWN"
    with pytest.raises(GateStop) as stopped:
        analysis.analyze(records, tasks)
    emit(capsys, "I5a T3e " + fault, {"result": "STOP", "reason": str(stopped.value)})


@pytest.mark.parametrize("branch", ["negative_seed", "nonpositive_domain", "three_blocks", "three_positive_seeds"])
def test_t3_heterogeneity(branch, capsys):
    tasks = fixture_tasks()
    primary = sorted((t for t in tasks if t["group"] == "novel_composition"), key=lambda t: t["task_id"])
    effect = np.ones((5, 32), dtype=int)
    if branch == "negative_seed":
        effect[0, :] = 0
        effect[0, 0] = -1
    elif branch == "nonpositive_domain":
        for i, task in enumerate(primary):
            if task["family"] == "numeric_iteration":
                effect[:, i] = 0
    elif branch == "three_blocks":
        effect[:] = 0
        selected = {"numeric_iteration:G1", "array_reduction:G1", "array_reduction:G2"}
        for i, task in enumerate(primary):
            if task["block_id"] in selected:
                effect[:, i] = 1
    else:
        effect[3:, :] = 0
    records, tasks = fixture_records(effect, tasks)
    report = analysis.analyze(records, tasks)
    assert report["label"] == analysis.SUPPORT + "_WITH_HETEROGENEITY"
    expected_failure = {"negative_seed": "every_seed_nonnegative", "nonpositive_domain": "both_domains_positive",
                        "three_blocks": "at_least_six_blocks_positive",
                        "three_positive_seeds": "at_least_four_seeds_positive"}[branch]
    assert report["primary"]["qualifications"][expected_failure] is False
    emit(capsys, "I5a T3f " + branch, compact(report))


@pytest.mark.parametrize("branch", ["boundary", "mean_failure", "seed_failure", "eleven_kept", "none_kept"])
def test_t3_sanity(branch, capsys):
    tasks = fixture_tasks()
    sanity = sorted(t["task_id"] for t in tasks if t["group"] == "primitive_sanity")
    if branch in ("eleven_kept", "none_kept"):
        keep = set(sanity[:11] if branch == "eleven_kept" else [])
        tasks = [t for t in tasks if t["group"] != "primitive_sanity" or t["task_id"] in keep]
    records, tasks = fixture_records(np.ones((5, 32), dtype=int), tasks)
    losses = {"boundary": [4, 1, 1, 1, 1], "mean_failure": [4, 2, 1, 1, 1],
              "seed_failure": [5, 0, 0, 0, 0]}.get(branch)
    if losses:
        for i, seed in enumerate(schedule.SEEDS):
            for row in records:
                if row["seed"] == seed and row["condition"] == "isolated" and row["task_id"] in sanity[:losses[i]]:
                    set_pass(row, True)
    report = analysis.analyze(records, tasks)
    qualifier = report["sanity"]
    assert report["label"] == analysis.SUPPORT  # Sanity never vetoes the primary label.
    expected = "SANITY_NOT_EVALUABLE" if branch.endswith("kept") else "NONCATASTROPHIC" if branch == "boundary" else "CATASTROPHIC"
    assert qualifier["label"] == expected
    if branch == "boundary":
        assert qualifier["mean_difference"] == -0.1
    emit(capsys, "I5a T3g " + branch, qualifier)


def test_descriptive_and_clarification(capsys):
    records, tasks = fixture_records()
    structural = sorted((r for r in records if r["group"] == "structural_transfer" and
                         r["seed"] == schedule.SEEDS[0] and r["condition"] == "isolated"), key=lambda r: r["task_id"])
    set_pass(structural[0], True)
    structural[1]["compile_ok"] = False
    for outcome in structural[1]["case_outcomes"]:
        outcome["execution_ok"] = False
    structural[2]["case_outcomes"][0]["execution_ok"] = False
    report = analysis.analyze(records, tasks)
    stages = report["descriptive"]["structural_transfer"]["failure_stages"][f"{schedule.SEEDS[0]}/isolated"]
    assert stages == {"PASS": 1, "COMPILE": 1, "EXECUTION": 1, "OUTPUT_MISMATCH": 13}
    for condition in schedule.CONDITIONS:
        for domain in schedule.DOMAINS:
            assert report["descriptive"]["K7_expected_output_classes"][condition][domain] == {
                "training": ["ZERO", "POSITIVE", "MULTIDIGIT"], "primary": ["ZERO", "POSITIVE", "MULTIDIGIT"]}
    assert set(report["descriptive"]["OR_by_domain"]) == set(schedule.DOMAINS)
    assert len(report["descriptive"]["own_training"]["by_archetype"]) == 12
    raw = (ROOT / "research/protocols/phase3c_conf1_implementation_clarifications_c12_c14.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "0829e8ad8d4716fd43fd3d49198504a1c345324673933a23d2933161ff859612"
    assert b"\r" not in raw and raw.endswith(b"\n") and not raw.startswith(b"\xef\xbb\xbf")
    emit(capsys, "I5a descriptive", {"failure_stages": stages, "K7_fixture_classes": ["ZERO", "POSITIVE", "MULTIDIGIT"],
                                    "clarification_bytes": len(raw), "clarification_hash_pass": True})


def independent_draws(records, tasks, changed_order=False):
    ids = sorted(t["task_id"] for t in tasks if t["group"] == "novel_composition")
    metadata = {t["task_id"]: t for t in tasks}
    score = {(r["seed"], r["condition"], r["task_id"]): r["passed"] for r in records if r["group"] == "novel_composition"}
    blocks = {d: sorted({metadata[t]["block_id"] for t in ids if metadata[t]["family"] == d})
              for d in ("numeric_iteration", "array_reduction")}
    members = {b: sorted(t for t in ids if metadata[t]["block_id"] == b) for options in blocks.values() for b in options}
    rng = np.random.default_rng(20290119)
    draws = []
    for _ in range(10000):
        if changed_order:
            ni = rng.integers(0, 4, size=4)
            si = rng.integers(0, 5, size=5)
        else:
            si = rng.integers(0, 5, size=5)
            ni = rng.integers(0, 4, size=4)
        ai = rng.integers(0, 4, size=4)
        sampled = [t for j in ni for t in members[blocks["numeric_iteration"][int(j)]]]
        sampled += [t for j in ai for t in members[blocks["array_reduction"][int(j)]]]
        total = 0
        for j in si:
            seed = (20280117, 20280223, 20280329, 20280411, 20280507)[int(j)]
            for tid in sampled:
                total += int(score[seed, "composition", tid]) - int(score[seed, "isolated", tid])
        draws.append(total / 160)
    return np.asarray(draws)


def test_t4_independent_bootstrap(capsys):
    records, tasks = fixture_records()
    fixture_rng = np.random.default_rng(314159)
    for row in records:
        if row["group"] == "novel_composition":
            set_pass(row, fixture_rng.random() < (0.65 if row["condition"] == "composition" else 0.35))
    fixture_rng.shuffle(records)
    fixture_rng.shuffle(tasks)
    report = analysis.primary_analysis(records, tasks)
    independent = independent_draws(records, tasks)
    changed = independent_draws(records, tasks, changed_order=True)
    actual = np.asarray(report["bootstrap"]["draws"])
    assert np.array_equal(actual, independent)
    interval = np.quantile(independent, [0.025, 0.975], method="linear").tolist()
    assert report["bootstrap"]["interval"] == interval
    assert not np.array_equal(changed, independent)
    emit(capsys, "I5a T4", {"fixture_rng_seed": 314159, "draws_exactly_equal": 10000,
         "interval": interval, "point": report["point"],
         "changed_order_different_draws": int(np.count_nonzero(changed != independent)),
         "changed_order_interval": np.quantile(changed, [0.025, 0.975], method="linear").tolist()})


def allowed_audit_path(path, root):
    root = root.resolve()
    absolute = path.resolve()
    if not absolute.is_relative_to(root):
        return False
    relative = absolute.relative_to(root)
    return not excluded(relative) and any(relative.as_posix().casefold().startswith(prefix + "/") for prefix in INCLUDES)


def seed_audit(root):
    """Apply explicit include/exclude filtering before opening every file."""
    paths = set()
    for prefix in INCLUDES:
        directory = root / prefix
        if not directory.is_dir():
            continue
        for folder, directories, filenames in os.walk(directory, followlinks=False):
            directories[:] = [name for name in directories if not excluded((Path(folder) / name).relative_to(root))]
            for name in filenames:
                path = Path(folder) / name
                if allowed_audit_path(path, root):
                    paths.add(path)
    result = {literal: [] for literal in SEED_LITERALS}
    opened = []
    for path in sorted(paths):
        assert allowed_audit_path(path, root), "excluded audit path before open"
        raw = path.read_bytes()
        relative = path.relative_to(root).as_posix()
        opened.append(relative)
        for literal in SEED_LITERALS:
            if literal.encode("ascii") in raw:
                result[literal].append(relative)
    assert all(not excluded(path) for path in opened)
    return result, opened


def test_t5_seed_audit(tmp_path, monkeypatch, capsys):
    # Excluded sentinels demonstrate that filtering precedes file reads.
    fake = tmp_path / "audit"
    sentinel_paths = list(EXCLUDED_FILES) + ["research/results/attempt/hidden_cases.json",
        "research/artifacts/raw.json", "research/adapters/model.json", ".runtime/output.json",
        ".git/index", ".models/weights.bin", ".artifacts/compiler.jar", ".tools/tool.py",
        "benchmark/unlisted/tasks.json", "research/implementation_notes/note.md",
        "docs/.runtime/result.json"]
    for relative in sentinel_paths + ["docs/allowed.md"]:
        path = fake / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(SEED_LITERALS[0], encoding="utf-8")
    original = Path.read_bytes
    opened_actual = []

    def checked_read(path):
        root = fake if path.is_relative_to(fake) else ROOT
        assert allowed_audit_path(path, root), "excluded path was opened by seed audit"
        opened_actual.append(str(path))
        return original(path)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", checked_read)
        fixture_result, fixture_opened = seed_audit(fake)
        assert fixture_opened == ["docs/allowed.md"]
        assert fixture_result[SEED_LITERALS[0]] == ["docs/allowed.md"]
        result, opened = seed_audit(ROOT)
    assert len(opened_actual) == len(opened) + 1
    emit(capsys, "I5a T5", {"files_by_literal": result, "included_files_opened": len(opened),
                           "excluded_paths_opened": 0, "path_filter_sentinel_test": "PASS"})
