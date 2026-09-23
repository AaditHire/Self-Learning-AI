"""Write an immutable manifest for completed or acquisition-STOP Phase 3C files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase3c_contract import (CONFIG, ROOT, load_frozen, sha256, verify_execution_files,
                              write_manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--partial-stop", action="store_true")
    args = parser.parse_args()
    verify_execution_files()
    cfg = load_frozen(check_base=True)
    root = ROOT / cfg["runtime_root"]
    output = root / "artifact_manifest.json"
    if output.exists():
        raise FileExistsError(output)
    runtime_files = sorted(p for p in root.rglob("*") if p.is_file())
    if any(p.name.endswith(".checkpoint.json") for p in runtime_files):
        raise RuntimeError("Incomplete evaluation checkpoint exists")
    training = list((root / "training").rglob("*.json"))
    evaluations = list((root / "evaluations").rglob("*.json"))
    weights = list((root / "adapters").rglob("adapter_model.safetensors"))
    if args.partial_stop:
        gate = json.loads((root / "pre_b_acquisition_gate.json").read_text(encoding="utf-8"))
        if gate["all_eligible"] or len(training) != 3 or len(evaluations) != 12 or len(weights) != 3:
            raise ValueError("Partial STOP manifest requires exactly three A runs and ineligible gate")
    elif len(training) != 9 or len(evaluations) != 30 or len(weights) != 9 or not (root / "analysis.json").is_file():
        raise ValueError("Complete Phase 3C artifact set is missing")
    fixed = [CONFIG, ROOT / "research/protocols/phase3c_protocol.md",
             ROOT / "research/protocols/phase3c_replay_schedule.json",
             ROOT / "research/protocols/phase3c_execution_manifest.json"]
    paths = runtime_files + fixed
    metadata = {}
    for path in runtime_files:
        rel = path.relative_to(root)
        entry = {"artifact_id": "phase3c-" + "-".join(rel.with_suffix("").parts)}
        if len(rel.parts) >= 3 and rel.parts[0] in ("adapters", "training", "evaluations"):
            entry["seed"] = None if rel.parts[1] == "base" else int(rel.parts[1])
            entry["condition"] = rel.parts[2] if rel.parts[0] == "adapters" else path.stem.split("_")[0]
            entry["lineage_parent"] = ("pinned_base" if entry["condition"] in ("A", "base")
                                        else f"phase3c-{entry['seed']}-A-adapter")
        metadata[str(path)] = entry
    lineage = {"frozen_design_commit": "a2fb247d090d3d2b00e7fcc4a4f71325723b7086",
               "config_sha256": sha256(CONFIG), "base_revision": cfg["base_weights"]["revision"],
               "base_weight_sha256": cfg["base_weights"]["weight_file_sha256"],
               "schedule_sha256": sha256(ROOT / "research/protocols/phase3c_replay_schedule.json"),
               "status": "STOP_acquisition_ineligible" if args.partial_stop else "complete_pre_archive"}
    manifest = write_manifest(paths, output, lineage, metadata)
    print(json.dumps({"status": lineage["status"], "artifacts": len(manifest["artifacts"]),
                      "manifest": str(output)}))


if __name__ == "__main__":
    main()
