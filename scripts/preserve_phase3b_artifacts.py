"""Copy the 48 frozen Phase 3B local-only artifacts without changing sources.

The outputs are immutable copies for Git/Git LFS preservation. This script
does not load a model, run an evaluation, or read the sealed holdout.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "research/manifests/infrastructure_checkpoint_artifacts.json"
PROVENANCE = ROOT / "research/results/PHASE_3B/provenance.json"
OUTPUT = ROOT / "research/manifests/phase3b_artifact_preservation.json"
ADAPTER_DEST = Path("research/adapters/phase3b-preserved")
RAW_DEST = Path("research/artifacts/phase3b/raw")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def copy_verified(source_rel: str, destination_rel: Path, expected: str, size: int | None) -> dict:
    source = ROOT / source_rel
    destination = ROOT / destination_rel
    if not source.is_file():
        raise FileNotFoundError(source)
    source_size = source.stat().st_size
    if size is not None and source_size != size:
        raise ValueError(f"Source size mismatch: {source_rel}")
    if sha256(source) != expected:
        raise ValueError(f"Source hash mismatch before copy: {source_rel}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        with source.open("rb") as src, destination.open("xb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
    if destination.stat().st_size != source_size or sha256(destination) != expected:
        raise ValueError(f"Backup copy mismatch: {destination_rel}")
    if source.stat().st_size != source_size or sha256(source) != expected:
        raise ValueError(f"Source changed during copy: {source_rel}")
    return {
        "original_path": source_rel,
        "backup_path": destination_rel.as_posix(),
        "size_bytes": source_size,
        "sha256": expected,
        "local_copy_verification": "PASS: source before/after and backup copy equal inventory SHA-256 and size",
    }


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    if len(inventory["phase3b_adapters"]) != 9 or len(provenance["runtime_source_sha256"]) != 39:
        raise ValueError("Unexpected frozen artifact count")
    adapter_experiments = {(item["seed"], item["artifact_id"].split("-")[-2]): item["producing_experiment"]
                           for item in inventory["phase3b_adapters"]}
    records = []
    for item in inventory["phase3b_adapters"]:
        destination = ADAPTER_DEST / f"{item['artifact_id']}.safetensors"
        record = copy_verified(item["path"], destination, item["sha256"], item["size_bytes"])
        record.update({
            "artifact_id": item["artifact_id"], "kind": "adapter_weights", "storage": "git_lfs",
            "experiment_id": item["producing_experiment"], "seed": item["seed"],
            "lineage_parent": item["lineage_parent"],
        })
        records.append(record)
    for source_rel, expected in provenance["runtime_source_sha256"].items():
        subpath = Path(source_rel).relative_to(Path(".runtime/phase3b"))
        destination = RAW_DEST / subpath
        record = copy_verified(source_rel, destination, expected, None)
        parts = subpath.parts
        seed = None if parts[1] == "base" else int(parts[1])
        if parts[0] == "training":
            condition = subpath.stem
            experiment = adapter_experiments[(seed, condition)]
            lineage = "pinned_3b_base" if condition == "A" else f"phase3b-{seed}-A-adapter"
        else:
            condition = subpath.stem.split("_")[0]
            suite = subpath.stem.split("_")[-1]
            experiment = "EXP-0047" if suite == "regression" else "EXP-0046"
            lineage = "pinned_3b_base" if condition == "base" else f"phase3b-{seed}-{condition}-adapter"
        record.update({
            "artifact_id": "phase3b-raw-" + "-".join(subpath.with_suffix("").parts),
            "kind": "raw_record", "storage": "git", "experiment_id": experiment,
            "seed": seed, "lineage_parent": lineage,
        })
        records.append(record)
    if len(records) != 48:
        raise ValueError("Unexpected preservation count")
    manifest = {
        "source_inventory": INVENTORY.relative_to(ROOT).as_posix(),
        "source_provenance": PROVENANCE.relative_to(ROOT).as_posix(),
        "source_commit": "1c1ee158bacfa6711ff9238a42801038d62bbafd",
        "remote": "https://github.com/AaditHire/Self-Learning-AI.git",
        "mechanism": "immutable Git LFS adapter copies and ordinary Git raw-record copies",
        "adapter_count": 9, "raw_record_count": 39,
        "remote_restore_status": "pending_remote_push_and_fresh_clone",
        "artifacts": records,
    }
    if OUTPUT.exists():
        if json.loads(OUTPUT.read_text(encoding="utf-8")) != manifest:
            raise ValueError("Existing preservation manifest differs")
    else:
        OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Verified 9 adapters and 39 raw records before/after copy and at backup paths")


if __name__ == "__main__":
    main()
