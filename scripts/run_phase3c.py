"""Future Phase 3C executor. Never run during pre-execution review."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from phase3c_contract import (ROOT, load_frozen, load_items,
                              pre_b_gate_from_records, sha256, validate_schedule, verify_execution_files)


def run(script: str, *arguments: str) -> None:
    try:
        subprocess.run([sys.executable, str(ROOT / "scripts" / script), *arguments], cwd=ROOT, check=True)
    except subprocess.CalledProcessError as exc:
        root = ROOT / ".runtime/phase3c"
        stop = root / "stop.json"
        if root.is_dir() and not stop.exists():
            with stop.open("x", encoding="utf-8") as handle:
                json.dump({"phase": "3C", "status": "STOP_incomplete", "failed_script": script,
                           "returncode": exc.returncode, "arguments": list(arguments),
                           "no_rerun_or_method_change": True}, handle, indent=2)
                handle.write("\n")
        raise


def evaluate(suite: str, condition: str, seed: int | None, cfg: dict) -> None:
    args = ["--suite", suite, "--condition", condition,
            "--java", str(ROOT / cfg["compiler_java"]), "--jar", str(ROOT / cfg["compiler_artifact"])]
    if seed is not None:
        args += ["--seed", str(seed)]
    run("run_phase3c_evaluation.py", *args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Explicitly authorize the frozen model run")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("Phase 3C execution is disabled without --execute; review only")
    verify_execution_files()
    cfg = load_frozen(check_base=True)
    items = load_items(cfg)
    validate_schedule(cfg, items)
    root = ROOT / cfg["runtime_root"]
    if root.exists() and any(root.iterdir()):
        raise FileExistsError("Phase 3C runtime already contains artifacts; no rerun/override")
    root.mkdir(parents=True, exist_ok=True)
    run("capture_phase3c_environment.py", "--output", str(root / "environment.json"))

    for suite in ("A", "B", "regression"):
        evaluate(suite, "base", None, cfg)
    for seed in cfg["seeds"]:
        run("train_phase3c_qlora.py", "--seed", str(seed), "--condition", "A")
        for suite in ("A", "B", "regression"):
            evaluate(suite, "A", seed, cfg)

    # All three A records must exist and pass before *any* B branch is launched.
    gate = pre_b_gate_from_records(cfg, items)
    gate_path = root / "pre_b_acquisition_gate.json"
    with gate_path.open("x", encoding="utf-8") as handle:
        json.dump({"phase": "3C", "config_sha256": sha256(ROOT / "research/protocols/phase3c_config.json"),
                   **gate}, handle, indent=2)
        handle.write("\n")
    if not gate["all_eligible"]:
        run("finalize_phase3c_artifacts.py", "--partial-stop")
        run("preserve_phase3c_artifacts.py")
        raise SystemExit("STOP_before_B_no_tuning: one or more seeds failed A acquisition")

    for seed in cfg["seeds"]:
        parent = root / "training" / str(seed) / "A.json"
        expected = json.loads(parent.read_text(encoding="utf-8"))["adapter"]["file_hashes"]
        for condition in ("naive", "replay"):
            # The training script also independently checks the every-seed gate and parent hashes.
            run("train_phase3c_qlora.py", "--seed", str(seed), "--condition", condition)
            record = json.loads((root / "training" / str(seed) / f"{condition}.json").read_text(encoding="utf-8"))
            if record["lineage"]["parent_adapter_file_hashes"] != expected:
                raise RuntimeError("Matched B branches did not start from identical A adapter bytes")
            if record["training"]["optimizer_steps"] != 24 or sum(len(x) for x in record["lineage"]["exposures_by_epoch"]) != 180:
                raise RuntimeError("B compute budget mismatch")
            for suite in ("A", "B", "regression"):
                evaluate(suite, condition, seed, cfg)
    run("analyze_phase3c.py")
    run("finalize_phase3c_artifacts.py")
    run("preserve_phase3c_artifacts.py")
    print("Phase 3C local preservation copies ready; push and fresh-clone restore remain required before archival claim")


if __name__ == "__main__":
    main()
