"""Frozen Phase 3C execution contract. Standard library only; no model import."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "research/protocols/phase3c_config.json"
EXECUTION_MANIFEST = ROOT / "research/protocols/phase3c_execution_manifest.json"
FROZEN_CONFIG_SHA256 = "3d9b1d05d55a5fdfe69a25a4a376b3174f7323e86a5a3a936442d5499b4fe679"
FROZEN_CONFIG_GIT_SHA256 = "1f8e812df853ae64740ca0b693e6928e2b9dae6303fcadd44b374e7fd0c729d8"
FROZEN_HEAD = "a2fb247d090d3d2b00e7fcc4a4f71325723b7086"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def verify_execution_files() -> dict:
    manifest = json.loads(EXECUTION_MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("frozen_design_commit") != FROZEN_HEAD or manifest.get("frozen_config_sha256") != FROZEN_CONFIG_SHA256:
        raise ValueError("Execution manifest does not match frozen preregistration")
    for name, expected in manifest["code_git_text_sha256"].items():
        if normalized_sha256(ROOT / name) != expected:
            raise ValueError(f"Execution code changed: {name}")
    for name, expected in manifest["model_support_file_sha256"].items():
        if sha256(ROOT / name) != expected:
            raise ValueError(f"Pinned tokenizer/model support file changed: {name}")
    return manifest


def load_frozen(*, check_base: bool = True) -> dict:
    if sha256(CONFIG) != FROZEN_CONFIG_SHA256 and normalized_sha256(CONFIG) != FROZEN_CONFIG_GIT_SHA256:
        raise ValueError("Frozen Phase 3C config hash mismatch")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    if cfg["seeds"] != [20260925, 20261013, 20261119]:
        raise ValueError("Frozen seeds changed")
    for name, local_hash in cfg["file_sha256"].items():
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(path)
        if sha256(path) != local_hash and normalized_sha256(path) != cfg["git_text_content_sha256"][name]:
            raise ValueError(f"Frozen input changed: {name}")
    if sha256(ROOT / cfg["compiler_artifact"]) != cfg["compiler_sha256"]:
        raise ValueError("Frozen compiler changed")
    if check_base:
        base = ROOT / cfg["base_weights"]["local_path"]
        for name, expected in cfg["base_weights"]["weight_file_sha256"].items():
            if sha256(base / name) != expected:
                raise ValueError(f"Frozen base weight changed: {name}")
    return cfg


def assert_critical_packages(cfg: dict) -> dict[str, str]:
    expected = cfg["environment_at_design_freeze"]["packages"]
    actual = {name: importlib.metadata.version(name) for name in expected}
    if actual != expected:
        raise ValueError("Critical package versions changed from frozen design")
    return actual


def load_items(cfg: dict) -> dict:
    def read(name: str):
        return json.loads((ROOT / name).read_text(encoding="utf-8"))
    return {
        "a_train": read("data/phase3c/a_training_examples.json"),
        "b_train": read("data/phase3c/b_training_examples.json"),
        "a_eval": read("benchmark/phase3c/a_eval_tasks.json"),
        "b_eval": read("benchmark/phase3c/b_eval_tasks.json"),
        "schedule": read("research/protocols/phase3c_replay_schedule.json"),
    }


def validate_schedule(cfg: dict, items: dict) -> dict:
    a = {r["example_id"]: r for r in items["a_train"]}
    b = {r["example_id"]: r for r in items["b_train"]}
    eval_ids = {r["task_id"] for r in items["a_eval"] + items["b_eval"]}
    if len(a) != 60 or len(b) != 60 or len(eval_ids) != 64 or set(a) & set(b) or (set(a) | set(b)) & eval_ids:
        raise ValueError("Training/evaluation ID separation failed")
    evaluation_prompts = {r["prompt"] for r in items["a_eval"] + items["b_eval"]}
    if any(r["prompt"] in evaluation_prompts for r in items["a_train"] + items["b_train"]):
        raise ValueError("Evaluation prompt entered training")
    schedule = items["schedule"]
    train_cfg = cfg["training"]
    if (schedule["seeds"] != cfg["seeds"] or schedule["epochs"] != train_cfg["epochs"] != 3
            or schedule["micro_batches_per_epoch"] != 60 or schedule["optimizer_steps_per_epoch"] != 8
            or schedule["replay_fraction"] != .20 or set(schedule["by_seed"]) != {str(x) for x in cfg["seeds"]}):
        raise ValueError("Frozen schedule header mismatch")
    if train_cfg["micro_batch_size"] != 1 or train_cfg["gradient_accumulation_steps"] != 8:
        raise ValueError("Frozen batch policy changed")
    for seed, epochs in schedule["by_seed"].items():
        if len(epochs) != 3:
            raise ValueError("Schedule epoch count")
        all_replay_a = []
        for n, epoch in enumerate(epochs, 1):
            naive, replay = epoch["naive_example_ids"], epoch["replay_example_ids"]
            positions = epoch["replaced_b_positions_zero_based"]
            listed_a = epoch["replayed_a_example_ids"]
            if epoch["epoch"] != n or len(naive) != len(replay) != 60:
                raise ValueError("Schedule length/epoch")
            if len(naive) != 60 or len(replay) != 60 or len(set(naive)) != 60 or set(naive) != set(b):
                raise ValueError("Naive schedule differs from frozen B set")
            if len(set(replay)) != 60 or set(replay) - (set(a) | set(b)) or set(replay) & eval_ids:
                raise ValueError("Replay contains nontraining item")
            changed = [i for i, (left, right) in enumerate(zip(naive, replay)) if left != right]
            if changed != positions or len(changed) != 12 or [replay[i] for i in positions] != listed_a:
                raise ValueError("Replacement positions/IDs changed")
            if Counter(b[naive[i]]["family"] for i in positions) != Counter({"string_transform": 6, "field_processing": 6}):
                raise ValueError("Replaced B subskill mix")
            if Counter(a[x]["family"] for x in listed_a) != Counter({"numeric_iteration": 6, "array_reduction": 6}):
                raise ValueError("Replay A subskill mix")
            if sum(x in a for x in replay) != 12 or sum(x in b for x in replay) != 48:
                raise ValueError("Replay ratio changed")
            all_replay_a.extend(listed_a)
        if len(all_replay_a) != 36 or len(set(all_replay_a)) != 36:
            raise ValueError("Replay A uniqueness changed")
    steps = math.ceil(60 / train_cfg["gradient_accumulation_steps"]) * train_cfg["epochs"]
    if steps != 24:
        raise ValueError("Optimizer-step budget changed")
    return {"seeds": len(cfg["seeds"]), "epochs_per_seed": 3, "slots_per_branch_seed": 180,
            "optimizer_steps_per_branch_seed": steps, "replay_slots_per_branch_seed": 36,
            "evaluation_ids_in_schedule": 0}


def complete_outcomes(tasks: list[dict], rows: list[dict], *, score_key: str = "hidden_pass") -> dict[str, bool]:
    ids = {r["task_id"] for r in tasks}
    if len(ids) != len(tasks) or len(rows) != len(tasks):
        raise ValueError("Incomplete or duplicate outcome rows")
    outcome = {}
    for row in rows:
        tid = row["task_id"]
        if tid not in ids or tid in outcome or type(row.get(score_key)) is not bool:
            raise ValueError("Invalid outcome row")
        outcome[tid] = row[score_key]
    if set(outcome) != ids:
        raise ValueError("Missing task outcomes")
    return outcome


def a_eligibility(cfg: dict, tasks: list[dict], outcomes: dict[int, dict[str, bool]]) -> dict:
    if set(outcomes) != set(cfg["seeds"]):
        raise ValueError("All three A seeds required before B")
    rule = cfg["pre_b_eligibility"]
    result = {}
    for seed in cfg["seeds"]:
        passed = outcomes[seed]
        if set(passed) != {r["task_id"] for r in tasks}:
            raise ValueError(f"Incomplete pre-B A outcomes for seed {seed}")
        overall = sum(passed.values())
        subskills = {name: sum(passed[r["task_id"]] for r in tasks if r["family"] == name)
                     for name in ("numeric_iteration", "array_reduction")}
        archetypes = {name: sum(passed[r["task_id"]] for r in tasks if r["archetype"] == name)
                      for name in sorted({r["archetype"] for r in tasks})}
        eligible = (overall >= rule["overall_pass_min_of_32_each_seed"]
                    and all(x >= rule["each_a_subskill_pass_min_of_16_each_seed"] for x in subskills.values())
                    and len(archetypes) == 4
                    and all(x >= rule["each_a_archetype_pass_min_of_8_each_seed"] for x in archetypes.values()))
        result[seed] = {"overall": overall, "subskills": subskills, "archetypes": archetypes, "eligible": eligible}
    return {"by_seed": result, "all_eligible": all(r["eligible"] for r in result.values()),
            "action": "B_ALLOWED" if all(r["eligible"] for r in result.values()) else "STOP_before_B_no_tuning"}


def pre_b_gate_from_records(cfg: dict, items: dict) -> dict:
    """Read all three immutable pre-B A records; never use contents to select replay IDs."""
    root = ROOT / cfg["runtime_root"]
    outcomes = {}
    for seed in cfg["seeds"]:
        path = root / "evaluations" / str(seed) / "A_a.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (payload.get("phase") != "3C" or payload.get("suite") != "A"
                or payload.get("condition") != "A" or payload.get("seed") != seed
                or payload.get("config_sha256") != sha256(CONFIG)):
            raise ValueError(f"Invalid pre-B A evaluation provenance: {path}")
        training = json.loads((root / "training" / str(seed) / "A.json").read_text(encoding="utf-8"))
        if payload.get("adapter_file_hashes") != training["adapter"]["file_hashes"]:
            raise ValueError(f"Pre-B evaluation adapter mismatch: {seed}")
        outcomes[seed] = complete_outcomes(items["a_eval"], payload["records"])
    return a_eligibility(cfg, items["a_eval"], outcomes)


def transitions(pre: dict[str, bool], post: dict[str, bool]) -> dict:
    if set(pre) != set(post):
        raise ValueError("Transition task IDs differ")
    counts = Counter((pre[tid], post[tid]) for tid in pre)
    denominator = sum(pre.values())
    return {"PASS_PASS": counts[True, True], "PASS_FAIL": counts[True, False],
            "FAIL_PASS": counts[False, True], "FAIL_FAIL": counts[False, False],
            "pre_b_pass": denominator,
            "retention": counts[True, True] / denominator if denominator else None,
            "forgetting": counts[True, False] / denominator if denominator else None}


def a_endpoints(cfg: dict, tasks: list[dict], pre: dict[int, dict], naive: dict[int, dict], replay: dict[int, dict]) -> dict:
    ids = {r["task_id"] for r in tasks}
    if len(ids) != 32 or any(set(block) != set(cfg["seeds"]) for block in (pre, naive, replay)):
        raise ValueError("A task/seed set mismatch")
    by_seed = {}
    for seed in cfg["seeds"]:
        if any(set(block[seed]) != ids for block in (pre, naive, replay)):
            raise ValueError("Incomplete A outcomes")
        n = transitions(pre[seed], naive[seed])
        r = transitions(pre[seed], replay[seed])
        if n["pre_b_pass"] != r["pre_b_pass"] or not n["pre_b_pass"]:
            raise ValueError("Undefined or mismatched acquired-task denominator")
        by_seed[seed] = {"naive": n, "replay": r,
                         "retention_difference_pp": 100 * (r["retention"] - n["retention"]),
                         "aggregate_a_difference_pp": 100 * (sum(replay[seed].values()) - sum(naive[seed].values())) / 32}
    mean_retention_diff = sum(x["retention_difference_pp"] for x in by_seed.values()) / 3
    mean_aggregate_diff = sum(x["aggregate_a_difference_pp"] for x in by_seed.values()) / 3
    rule = cfg["co_primary"]
    return {"by_seed": by_seed, "mean_retention_difference_pp": mean_retention_diff,
            "mean_aggregate_a_difference_pp": mean_aggregate_diff,
            "h1_pass": mean_retention_diff >= rule["retention_replay_minus_naive_mean_min_pp"]
                       and all(x["replay"]["retention"] >= rule["retention_replay_min_fraction_each_seed"] for x in by_seed.values()),
            "h2_pass": mean_aggregate_diff >= rule["aggregate_a_replay_minus_naive_mean_min_pp"]}


def joint_decision(a_gate: dict, a_effect: dict | None, b_effect: dict | None, regression: dict | None) -> str:
    if not a_gate["all_eligible"]:
        return "STOP_acquisition_ineligible"
    if any(x is None for x in (a_effect, b_effect, regression)):
        return "STOP_incomplete"
    return "PASS" if all((a_effect["h1_pass"], a_effect["h2_pass"], b_effect["h3_pass"],
                          regression["h4_pass"])) else "FAIL"


def b_gate(cfg: dict, tasks: list[dict], pre: dict[int, dict], naive: dict[int, dict], replay: dict[int, dict]) -> dict:
    if set(pre) != set(cfg["seeds"]) or set(naive) != set(pre) or set(replay) != set(pre):
        raise ValueError("B seed sets differ")
    rule = cfg["b_acquisition"]
    by_seed = {}
    for seed in cfg["seeds"]:
        before, n, r = pre[seed], naive[seed], replay[seed]
        ids = {x["task_id"] for x in tasks}
        if set(before) != ids or set(n) != ids or set(r) != ids:
            raise ValueError("Incomplete B task IDs")
        overall_gain = sum(n.values()) - sum(before.values())
        subskill_gain = {family: sum(n[x["task_id"]] - before[x["task_id"]] for x in tasks if x["family"] == family)
                         for family in ("string_transform", "field_processing")}
        archetype_gain = {name: sum(n[x["task_id"]] - before[x["task_id"]] for x in tasks if x["archetype"] == name)
                          for name in sorted({x["archetype"] for x in tasks})}
        replay_subskill_gain = {family: sum(r[x["task_id"]] - before[x["task_id"]] for x in tasks if x["family"] == family)
                                for family in subskill_gain}
        naive_eligible = (overall_gain >= rule["naive_overall_net_gain_min_of_32_each_seed"]
                          and all(x >= rule["naive_each_subskill_net_gain_min_of_16_each_seed"] for x in subskill_gain.values())
                          and len(archetype_gain) == 4
                          and all(x >= rule["naive_each_archetype_net_gain_min_of_8_each_seed"] for x in archetype_gain.values()))
        by_seed[seed] = {"naive_overall_net_gain": overall_gain, "naive_subskill_net_gain": subskill_gain,
                         "naive_archetype_net_gain": archetype_gain, "naive_broad_eligible": naive_eligible,
                         "replay_overall_net_gain": sum(r.values()) - sum(before.values()),
                         "replay_subskill_net_gain": replay_subskill_gain,
                         "replay_minus_naive_post_b_count": sum(r.values()) - sum(n.values())}
    broad = all(x["naive_broad_eligible"] for x in by_seed.values())
    mean_naive = sum(x["naive_overall_net_gain"] for x in by_seed.values()) / 3
    mean_replay = sum(x["replay_overall_net_gain"] for x in by_seed.values()) / 3
    h3 = (broad and mean_replay >= rule["replay_mean_gain_fraction_of_naive_min"] * mean_naive
          and all(all(v > 0 for v in x["replay_subskill_net_gain"].values()) for x in by_seed.values())
          and all(x["replay_minus_naive_post_b_count"] >= -rule["replay_overall_score_max_drop_from_naive_each_seed"] for x in by_seed.values()))
    return {"by_seed": by_seed, "naive_broad_eligible": broad, "mean_naive_gain": mean_naive,
            "mean_replay_gain": mean_replay, "h3_pass": h3,
            "broad_plasticity_claim_allowed": broad and h3}


def regression_gate(cfg: dict, base: dict, post_a: dict[int, dict], naive: dict[int, dict], replay: dict[int, dict]) -> dict:
    ids = set(base)
    if len(ids) != 64 or set(post_a) != set(naive) or set(naive) != set(replay) or set(replay) != set(cfg["seeds"]):
        raise ValueError("Regression item/seed mismatch")
    base_count = sum(base.values())
    result = {}
    for seed in cfg["seeds"]:
        if any(set(x[seed]) != ids for x in (post_a, naive, replay)):
            raise ValueError("Incomplete regression rows")
        counts = {"post_a": sum(post_a[seed].values()), "naive": sum(naive[seed].values()),
                  "replay": sum(replay[seed].values())}
        severe = any(base_count - value > cfg["regression_max_drop_items_of_64"] for value in counts.values())
        severe |= counts["naive"] - counts["replay"] > cfg["regression_max_drop_items_of_64"]
        result[seed] = {"counts": counts, "severe_collapse": severe}
    return {"base": base_count, "by_seed": result, "h4_pass": not any(x["severe_collapse"] for x in result.values())}


def write_manifest(paths: list[Path], output: Path, lineage: dict,
                   artifact_metadata: dict[str, dict] | None = None) -> dict:
    """Record existing finalized files once; never overwrite or create adapter data."""
    if output.exists():
        raise FileExistsError(output)
    rows = []
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        before_size, before_hash = path.stat().st_size, sha256(path)
        after_size, after_hash = path.stat().st_size, sha256(path)
        if (before_size, before_hash) != (after_size, after_hash):
            raise ValueError(f"Artifact changed during manifest: {path}")
        rows.append({"path": str(path), "name": path.name, "size_bytes": before_size,
                     "sha256": before_hash, **(artifact_metadata or {}).get(str(path), {})})
    payload = {"phase": "3C", "lineage": lineage, "artifacts": rows,
               "remote_restore_status": "pending_off_machine_copy_and_full_restore"}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return payload
