"""Verify future Phase 3C artifacts restored from a fresh remote clone."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from phase3c_contract import ROOT, sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh-clone", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    clone = args.fresh_clone.resolve()
    if clone == ROOT.resolve() or not (clone / ".git").exists():
        raise ValueError("Restore requires a separate fresh Git clone")
    if args.output.exists():
        raise FileExistsError(args.output)
    actual_commit = subprocess.check_output(["git", "-C", str(clone), "rev-parse", "HEAD"], text=True).strip()
    if actual_commit != args.expected_commit:
        raise ValueError("Fresh clone is not at the preservation commit")
    manifest = json.loads((clone / "research/manifests/phase3c_artifact_preservation.json").read_text(encoding="utf-8"))
    rows = []
    for item in manifest["artifacts"]:
        restored = clone / item["backup_path"]
        original = ROOT / item["original_path"]
        ok = (restored.is_file() and original.is_file()
              and restored.stat().st_size == original.stat().st_size == item["size_bytes"]
              and sha256(restored) == sha256(original) == item["sha256"])
        rows.append({"artifact_id": item["artifact_id"], "backup_path": item["backup_path"],
                     "sha256": item["sha256"], "restore_verified": ok})
    payload = {"phase": "3C", "remote_commit": actual_commit,
               "manifest_sha256": sha256(clone / "research/manifests/phase3c_artifact_preservation.json"),
               "artifacts_checked": len(rows), "artifacts_passed": sum(r["restore_verified"] for r in rows),
               "status": "PASS" if all(r["restore_verified"] for r in rows) else "FAIL", "results": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    if payload["status"] != "PASS":
        raise RuntimeError("Remote restoration failed; archival claim forbidden")
    print(json.dumps({"status": payload["status"], "restored": payload["artifacts_passed"]}))


if __name__ == "__main__":
    main()
