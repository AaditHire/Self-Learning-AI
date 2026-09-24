"""Verify every DEV1 artifact retrieved from an independent remote clone."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from safetensors import safe_open

from preflight_phase3c_dev1 import ROOT, sha256


ARTIFACT_COMMIT = "790bcc2a91cfb01a88a44e1468e84e0bc1418faa"
REMOTE = "https://github.com/AaditHire/Self-Learning-AI.git"
OUTPUT = ROOT / "research/manifests/phase3c_dev1_remote_restore_verification.json"


def git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--restore-root", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    restore = args.restore_root.resolve()
    if restore == ROOT.resolve() or not (restore / ".git").is_dir():
        raise ValueError("Restore location must be a separate fresh clone")
    head = git(restore, "rev-parse", "HEAD")
    remote = git(restore, "remote", "get-url", "origin")
    advertised = subprocess.check_output(["git", "ls-remote", REMOTE, "refs/heads/main"], text=True).split()[0]
    if head != ARTIFACT_COMMIT or remote != REMOTE:
        raise ValueError(f"Remote identity or commit mismatch: {head} {remote} {advertised}")
    subprocess.run(["git", "-C", str(restore), "fetch", "origin", "main", "--quiet"], check=True)
    if subprocess.run(["git", "-C", str(restore), "merge-base", "--is-ancestor", ARTIFACT_COMMIT, "origin/main"]).returncode != 0:
        raise ValueError("Artifact commit is not on advertised remote main history")
    manifest_path = ROOT / "research/manifests/phase3c_dev1_artifact_preservation.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    clone_manifest = restore / manifest_path.relative_to(ROOT)
    if sha256(manifest_path) != sha256(clone_manifest):
        raise ValueError("Remote preservation manifest changed")
    rows = []
    for item in manifest["artifacts"]:
        source = ROOT / item["original_path"]
        local_copy = ROOT / item["backup_path"]
        restored = restore / item["backup_path"]
        expected_size, expected_hash = item["size_bytes"], item["sha256"]
        for label, path in (("original", source), ("local_copy", local_copy), ("remote_restore", restored)):
            if not path.is_file() or path.stat().st_size != expected_size or sha256(path) != expected_hash:
                raise ValueError(f"{label} size/SHA-256 mismatch: {item['artifact_id']}: {path}")
        row = {"artifact_id": item["artifact_id"], "original_path": item["original_path"],
               "backup_path": item["backup_path"], "size_bytes": expected_size,
               "sha256": expected_hash, "storage": item["storage"],
               "original_unchanged": True, "local_copy_verified": True,
               "remote_restore_verified": True}
        if restored.name == "adapter_model.safetensors":
            with safe_open(restored, framework="pt", device="cpu") as handle:
                keys = list(handle.keys())
            if not keys:
                raise ValueError(f"Empty restored adapter: {restored}")
            row["adapter_tensor_count"] = len(keys)
        elif restored.suffix == ".json":
            json.loads(restored.read_text(encoding="utf-8"))
            row["json_parse_verified"] = True
        rows.append(row)
    if len(rows) != 81 or sum(row["backup_path"].endswith("adapter_model.safetensors") for row in rows) != 6:
        raise ValueError("Artifact inventory incomplete")
    payload = {"phase": "3C-DEV1", "status": "PASS_FULL_REMOTE_RESTORE",
               "mechanism": manifest["mechanism"], "remote": REMOTE,
               "remote_artifact_commit": ARTIFACT_COMMIT,
               "fresh_clone_path": str(restore), "fresh_clone_head": head,
               "advertised_remote_main_at_verification": advertised,
               "artifacts_restored_and_verified": len(rows),
               "adapter_weights_restored_and_verified": 6,
               "all_originals_unchanged": True,
               "verification": "fresh remote clone; selective Git LFS pull; every restored size and SHA-256 compared to preservation manifest and original; JSON parsed; safetensors headers/keys opened",
               "artifacts": rows}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "artifacts": len(rows),
                      "adapters": payload["adapter_weights_restored_and_verified"]}))


if __name__ == "__main__":
    main()
