"""Verify every Phase 3B preserved artifact after a fresh remote clone.

Only file bytes and Git commit identity are read. No model or compiler runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRESERVATION = ROOT / "research/manifests/phase3b_artifact_preservation.json"
OUTPUT = ROOT / "research/manifests/phase3b_remote_restore_verification.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify(path: Path, expected_hash: str, expected_size: int) -> None:
    if not path.is_file() or path.stat().st_size != expected_size or sha256(path) != expected_hash:
        raise ValueError(f"Missing or mismatched file: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--restore-root", type=Path, required=True)
    args = parser.parse_args()
    restored = args.restore_root.resolve(strict=True)
    if restored == ROOT:
        raise ValueError("Restore must be a separate checkout")
    remote_commit = subprocess.check_output(
        ["git", "-C", str(restored), "rev-parse", "HEAD"], text=True
    ).strip()
    manifest = json.loads(PRESERVATION.read_text(encoding="utf-8"))
    if len(manifest["artifacts"]) != 48:
        raise ValueError("Unexpected artifact count")
    results = []
    for artifact in manifest["artifacts"]:
        expected_hash = artifact["sha256"]
        expected_size = artifact["size_bytes"]
        source = ROOT / artifact["original_path"]
        local_backup = ROOT / artifact["backup_path"]
        remote_restore = restored / artifact["backup_path"]
        for path in (source, local_backup, remote_restore):
            verify(path, expected_hash, expected_size)
        results.append({
            "artifact_id": artifact["artifact_id"],
            "original_path": artifact["original_path"],
            "backup_path": artifact["backup_path"],
            "experiment_id": artifact["experiment_id"],
            "seed": artifact["seed"],
            "lineage_parent": artifact["lineage_parent"],
            "size_bytes": expected_size,
            "sha256": expected_hash,
            "verification": "PASS: original, committed backup, fresh remote restore",
        })
    report = {
        "remote": manifest["remote"],
        "remote_commit": remote_commit,
        "restore_method": "fresh shallow clone with LFS smudge disabled, then selective git lfs pull",
        "restore_root_at_verification": str(restored),
        "adapter_count": 9,
        "raw_record_count": 39,
        "verified_count": len(results),
        "failed_count": 0,
        "results": results,
        "model_gradients_run": False,
        "scientific_evaluation_run": False,
        "sealed_holdout_inspected_or_evaluated": False,
    }
    if OUTPUT.exists():
        if json.loads(OUTPUT.read_text(encoding="utf-8")) != report:
            raise ValueError("Existing restore report differs")
    else:
        OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {len(results)} remote-restored artifacts at {remote_commit}")


if __name__ == "__main__":
    main()
