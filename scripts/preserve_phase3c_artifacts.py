"""Stage byte-verified Phase 3C copies for the established Git/Git LFS remote.

Run only after a future authorized execution. This does not push or claim a
remote backup; a fresh remote-clone restore must pass separately.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from phase3c_contract import ROOT, load_frozen, sha256, verify_execution_files


def main() -> None:
    verify_execution_files()
    cfg = load_frozen(check_base=True)
    runtime = ROOT / cfg["runtime_root"]
    source_manifest = runtime / "artifact_manifest.json"
    manifest = json.loads(source_manifest.read_text(encoding="utf-8"))
    output = ROOT / "research/manifests/phase3c_artifact_preservation.json"
    if output.exists():
        raise FileExistsError(output)
    rows = []
    source_rows = list(manifest["artifacts"]) + [{"path": str(source_manifest), "name": source_manifest.name,
                                                    "size_bytes": source_manifest.stat().st_size,
                                                    "sha256": sha256(source_manifest), "artifact_id": "phase3c-artifact-manifest"}]
    for item in source_rows:
        source = Path(item["path"])
        if not source.is_relative_to(runtime):
            continue  # Frozen design inputs are already committed under their original paths.
        relative = source.relative_to(runtime)
        if relative.name == "adapter_model.safetensors" and relative.parts[0] == "adapters":
            destination_rel = Path("research/adapters/phase3c-preserved") / relative.parts[1] / relative.parts[2] / relative.name
            storage = "git_lfs"
        else:
            destination_rel = Path("research/artifacts/phase3c/raw") / relative
            storage = "git"
        destination = ROOT / destination_rel
        if source.stat().st_size != item["size_bytes"] or sha256(source) != item["sha256"]:
            raise ValueError(f"Source manifest mismatch: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as src, destination.open("xb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
        if destination.stat().st_size != item["size_bytes"] or sha256(destination) != item["sha256"]:
            raise ValueError(f"Copy mismatch: {destination}")
        if source.stat().st_size != item["size_bytes"] or sha256(source) != item["sha256"]:
            raise ValueError(f"Source changed during copy: {source}")
        rows.append({**item, "original_path": str(source.relative_to(ROOT)).replace("\\", "/"),
                     "backup_path": destination_rel.as_posix(), "storage": storage,
                     "local_copy_verification": "PASS"})
    result = {"phase": "3C", "mechanism": "existing project GitHub origin; Git LFS adapter weights; ordinary Git raw records",
              "remote": "https://github.com/AaditHire/Self-Learning-AI.git",
              "source_manifest": str(source_manifest.relative_to(ROOT)).replace("\\", "/"),
              "remote_restore_status": "PENDING_PUSH_AND_FRESH_CLONE_RESTORE",
              "artifacts": rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"copied": len(rows), "remote_restore_status": result["remote_restore_status"]}))


if __name__ == "__main__":
    main()
