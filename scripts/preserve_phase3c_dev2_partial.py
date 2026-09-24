"""Preserve the finalized DEV2 artifacts available at the evaluation STOP."""

import json
import shutil
from pathlib import Path

from preflight_phase3c_dev2 import ROOT, sha256

RUNTIME = ROOT / ".runtime/phase3c_dev2"
SOURCE_MANIFEST = RUNTIME / "artifact_manifest.json"
OUTPUT = ROOT / "research/manifests/phase3c_dev2_partial_artifact_preservation.json"
SEEDS = (20270925, 20271013, 20271119)
CONDITIONS = ("isolated", "composition")


def main():
    if SOURCE_MANIFEST.exists() or OUTPUT.exists():
        raise FileExistsError(SOURCE_MANIFEST if SOURCE_MANIFEST.exists() else OUTPUT)
    incident = json.loads((RUNTIME / "incident.json").read_text(encoding="utf-8"))
    if incident["status"] != "STOP_EVALUATION_CODE_DEFECT_NO_RETRY":
        raise ValueError("Expected evaluation STOP")
    paths = [RUNTIME / "preflight.json", RUNTIME / "incident.json"]
    for seed in SEEDS:
        for condition in CONDITIONS:
            adapter = RUNTIME / "adapters" / str(seed) / condition
            paths.extend(sorted(x for x in adapter.rglob("*") if x.is_file()))
            paths.append(RUNTIME / "training" / str(seed) / f"{condition}.json")
    paths.append(RUNTIME / "evaluations/20270925/isolated_training.json")
    if any(not x.is_file() for x in paths):
        raise FileNotFoundError([str(x) for x in paths if not x.is_file()])
    if list(RUNTIME.rglob("*.checkpoint.json")) or len(paths) != len(set(paths)):
        raise ValueError("Incomplete checkpoint or repeated artifact")
    sources = [{"original_path": x.relative_to(ROOT).as_posix(),
                "relative_runtime_path": x.relative_to(RUNTIME).as_posix(),
                "filename": x.name, "size_bytes": x.stat().st_size,
                "sha256": sha256(x)} for x in paths]
    if len(sources) != 69 or sum(x["filename"] == "adapter_model.safetensors" for x in sources) != 6:
        raise ValueError("Incomplete partial artifact inventory")
    SOURCE_MANIFEST.write_text(json.dumps({"phase": "3C-DEV2", "status": "PARTIAL_STOP_SOURCE_INVENTORY",
                                           "artifacts": sources}, indent=2) + "\n", encoding="utf-8")
    sources.append({"original_path": SOURCE_MANIFEST.relative_to(ROOT).as_posix(),
                    "relative_runtime_path": SOURCE_MANIFEST.relative_to(RUNTIME).as_posix(),
                    "filename": SOURCE_MANIFEST.name,
                    "size_bytes": SOURCE_MANIFEST.stat().st_size,
                    "sha256": sha256(SOURCE_MANIFEST)})
    output_rows = []
    for item in sources:
        source = ROOT / item["original_path"]
        relative = Path(item["relative_runtime_path"])
        if relative.parts[0] == "adapters" and relative.name == "adapter_model.safetensors":
            destination = ROOT / "research/adapters/phase3c-dev2-preserved" / relative.parts[1] / relative.parts[2] / relative.name
            storage = "git_lfs"
        elif relative.parts[0] == "adapters":
            destination = ROOT / "research/artifacts/phase3c-dev2/raw" / relative
            storage = "git_lfs"
        else:
            destination = ROOT / "research/artifacts/phase3c-dev2/raw" / relative
            storage = "git"
        if source.stat().st_size != item["size_bytes"] or sha256(source) != item["sha256"]:
            raise ValueError(f"Original changed before copy: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as src, destination.open("xb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
        if destination.stat().st_size != item["size_bytes"] or sha256(destination) != item["sha256"]:
            raise ValueError(f"Local backup copy mismatch: {destination}")
        if source.stat().st_size != item["size_bytes"] or sha256(source) != item["sha256"]:
            raise ValueError(f"Original changed during copy: {source}")
        seed = relative.parts[1] if relative.parts[0] in ("adapters", "training", "evaluations") else None
        condition = relative.parts[2] if relative.parts[0] == "adapters" else relative.stem.split("_")[0] if relative.parts[0] in ("training", "evaluations") else None
        output_rows.append({"artifact_id": "phase3c-dev2:" + item["relative_runtime_path"],
                            "original_path": item["original_path"],
                            "backup_path": destination.relative_to(ROOT).as_posix(),
                            "filename": item["filename"], "seed": seed, "condition": condition,
                            "size_bytes": item["size_bytes"], "sha256": item["sha256"],
                            "storage": storage, "local_copy_verification": "PASS"})
    payload = {"phase": "3C-DEV2", "status": "PARTIAL_STOP_LOCAL_COPY_VERIFIED_REMOTE_RESTORE_PENDING",
               "mechanism": "GitHub origin with Git LFS for adapter weights/support files and ordinary Git for available raw records",
               "remote": "https://github.com/AaditHire/Self-Learning-AI.git",
               "frozen_design_commit": "886cf3c69c2babb3f735776ab7b28ce36b2de62d",
               "execution_code_commit": "80e5897", "source_manifest": SOURCE_MANIFEST.relative_to(ROOT).as_posix(),
               "incident_status": incident["status"], "remote_restore_status": "PENDING_PUSH_AND_FRESH_CLONE_RESTORE",
               "artifacts": output_rows}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"artifacts": len(output_rows), "adapters": 6,
                      "local_copy_verification": "PASS", "remote_restore_status": payload["remote_restore_status"]}))


if __name__ == "__main__":
    main()
