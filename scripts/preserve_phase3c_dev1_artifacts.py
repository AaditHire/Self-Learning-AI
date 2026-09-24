"""Copy every finalized DEV1 runtime artifact into versioned Git/Git LFS paths."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from preflight_phase3c_dev1 import ROOT, sha256


RUNTIME = ROOT / ".runtime/phase3c_dev1"
OUTPUT = ROOT / "research/manifests/phase3c_dev1_artifact_preservation.json"
SOURCE_MANIFEST = RUNTIME / "artifact_manifest.json"


def main() -> None:
    if OUTPUT.exists() or SOURCE_MANIFEST.exists():
        raise FileExistsError(OUTPUT if OUTPUT.exists() else SOURCE_MANIFEST)
    preflight = RUNTIME / "preflight.json"
    analysis = RUNTIME / "analysis.json"
    if not preflight.is_file() or not analysis.is_file():
        raise FileNotFoundError("Preflight and complete analysis required")
    cfg = json.loads((ROOT / "research/protocols/phase3c_dev1_manifest.json").read_text(encoding="utf-8"))
    paths = [preflight, analysis]
    for seed in cfg["seeds"]:
        for condition in ("dense", "diverse"):
            adapter = RUNTIME / "adapters" / str(seed) / condition
            record = RUNTIME / "training" / str(seed) / f"{condition}.json"
            paths.extend(sorted(path for path in adapter.rglob("*") if path.is_file()))
            paths.append(record)
            for suite in ("training", "development"):
                paths.append(RUNTIME / "evaluations" / str(seed) / f"{condition}_{suite}.json")
    if any(not path.is_file() for path in paths):
        raise FileNotFoundError([str(path) for path in paths if not path.is_file()])
    if list(RUNTIME.rglob("*.checkpoint.json")):
        raise ValueError("Incomplete evaluation checkpoint exists")
    if len(paths) != len(set(paths)):
        raise ValueError("Repeated artifact path")
    source_rows = [{"original_path": path.relative_to(ROOT).as_posix(),
                    "relative_runtime_path": path.relative_to(RUNTIME).as_posix(),
                    "filename": path.name, "size_bytes": path.stat().st_size,
                    "sha256": sha256(path)} for path in paths]
    SOURCE_MANIFEST.write_text(json.dumps({"phase": "3C-DEV1", "status": "FINALIZED_LOCAL_ARTIFACT_INVENTORY",
                                           "artifacts": source_rows}, indent=2) + "\n", encoding="utf-8")
    source_rows.append({"original_path": SOURCE_MANIFEST.relative_to(ROOT).as_posix(),
                        "relative_runtime_path": SOURCE_MANIFEST.relative_to(RUNTIME).as_posix(),
                        "filename": SOURCE_MANIFEST.name, "size_bytes": SOURCE_MANIFEST.stat().st_size,
                        "sha256": sha256(SOURCE_MANIFEST)})
    output_rows = []
    for row in source_rows:
        source = ROOT / row["original_path"]
        relative = Path(row["relative_runtime_path"])
        if relative.parts[0] == "adapters" and relative.name == "adapter_model.safetensors":
            destination = ROOT / "research/adapters/phase3c-dev1-preserved" / relative.parts[1] / relative.parts[2] / relative.name
            storage = "git_lfs"
        elif relative.parts[0] == "adapters":
            destination = ROOT / "research/artifacts/phase3c-dev1/raw" / relative
            storage = "git_lfs"
        else:
            destination = ROOT / "research/artifacts/phase3c-dev1/raw" / relative
            storage = "git"
        if source.stat().st_size != row["size_bytes"] or sha256(source) != row["sha256"]:
            raise ValueError(f"Original changed before copy: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as input_stream, destination.open("xb") as output_stream:
            shutil.copyfileobj(input_stream, output_stream, length=1024 * 1024)
        if destination.stat().st_size != row["size_bytes"] or sha256(destination) != row["sha256"]:
            raise ValueError(f"Local backup copy mismatch: {destination}")
        if source.stat().st_size != row["size_bytes"] or sha256(source) != row["sha256"]:
            raise ValueError(f"Original changed during copy: {source}")
        if relative.parts[0] == "adapters":
            seed, condition = relative.parts[1:3]
        elif relative.parts[0] in ("training", "evaluations"):
            seed, condition = relative.parts[1], relative.stem.split("_")[0]
        else:
            seed = condition = None
        output_rows.append({"artifact_id": "phase3c-dev1:" + row["relative_runtime_path"],
                            "original_path": row["original_path"],
                            "backup_path": destination.relative_to(ROOT).as_posix(),
                            "filename": row["filename"], "seed": seed, "condition": condition,
                            "size_bytes": row["size_bytes"], "sha256": row["sha256"],
                            "storage": storage, "local_copy_verification": "PASS"})
    payload = {"phase": "3C-DEV1", "status": "LOCAL_COPY_VERIFIED_REMOTE_RESTORE_PENDING",
               "mechanism": "GitHub origin with Git LFS for six adapter_model.safetensors files and their support files; ordinary Git for essential raw records",
               "remote": "https://github.com/AaditHire/Self-Learning-AI.git",
               "frozen_design_commit": "359a5eaa70bc8fcb468740b58b2d41ccc0ab5fb2",
               "source_manifest": SOURCE_MANIFEST.relative_to(ROOT).as_posix(),
               "artifacts": output_rows, "remote_restore_status": "PENDING_PUSH_AND_FRESH_CLONE_RESTORE"}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"artifacts": len(output_rows), "lfs_adapters": sum(r["storage"] == "git_lfs" for r in output_rows),
                      "local_copy_verification": "PASS", "remote_restore_status": payload["remote_restore_status"]}))


if __name__ == "__main__":
    main()
