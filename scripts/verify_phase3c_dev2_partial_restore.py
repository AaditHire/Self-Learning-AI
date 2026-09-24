"""Verify every available DEV2 STOP artifact from a fresh remote clone."""

import argparse
import json
import subprocess
from pathlib import Path

from safetensors import safe_open

from preflight_phase3c_dev2 import ROOT, sha256

REMOTE = "https://github.com/AaditHire/Self-Learning-AI.git"
ARTIFACT_COMMIT = "9eadaa00ad350593bd799bad7d7b9e178d250ff7"
MANIFEST = ROOT / "research/manifests/phase3c_dev2_partial_artifact_preservation.json"
OUTPUT = ROOT / "research/manifests/phase3c_dev2_partial_remote_restore_verification.json"


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def main():
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
        raise ValueError(f"Fresh clone identity mismatch: {head}, {remote}")
    if subprocess.run(["git", "-C", str(restore), "merge-base", "--is-ancestor", ARTIFACT_COMMIT, "HEAD"]).returncode:
        raise ValueError("Artifact commit missing from fresh clone")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if sha256(MANIFEST) != sha256(restore / MANIFEST.relative_to(ROOT)):
        raise ValueError("Remote preservation manifest differs")
    rows = []
    for item in manifest["artifacts"]:
        source = ROOT / item["original_path"]
        local_copy = ROOT / item["backup_path"]
        restored = restore / item["backup_path"]
        for label, path in (("original", source), ("local_copy", local_copy), ("remote_restore", restored)):
            if not path.is_file() or path.stat().st_size != item["size_bytes"] or sha256(path) != item["sha256"]:
                raise ValueError(f"{label} size/SHA-256 mismatch: {item['artifact_id']}")
        row = {"artifact_id": item["artifact_id"], "original_path": item["original_path"],
               "backup_path": item["backup_path"], "size_bytes": item["size_bytes"],
               "sha256": item["sha256"], "storage": item["storage"],
               "original_unchanged": True, "local_copy_verified": True, "remote_restore_verified": True}
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
    if len(rows) != 70 or sum(x["backup_path"].endswith("adapter_model.safetensors") for x in rows) != 6:
        raise ValueError("Partial artifact inventory incomplete")
    payload = {"phase": "3C-DEV2", "status": "PASS_PARTIAL_STOP_FULL_REMOTE_RESTORE",
               "mechanism": manifest["mechanism"], "remote": REMOTE,
               "remote_artifact_commit": ARTIFACT_COMMIT,
               "fresh_clone_path": str(restore), "fresh_clone_head": head,
               "advertised_remote_main_at_verification": advertised,
               "artifacts_restored_and_verified": len(rows),
               "adapter_weights_restored_and_verified": 6,
               "all_originals_unchanged": True,
               "scientific_status": "STOP_EVALUATION_CODE_DEFECT_NO_RETRY; missing development output cannot be restored",
               "verification": "fresh remote clone; selective Git LFS pull; each restored size/SHA-256 compared with preservation manifest, local copy and original; JSON parsed; safetensors keys opened",
               "artifacts": rows}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "artifacts": len(rows),
                      "adapters": payload["adapter_weights_restored_and_verified"]}))


if __name__ == "__main__":
    main()
