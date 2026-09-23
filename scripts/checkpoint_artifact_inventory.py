"""Read-only hash audit for the post-Phase-3B infrastructure checkpoint.

Writes only the requested small inventory file. Never loads benchmark tasks,
executes the compiler, or loads a model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def checked_file(relative: str, expected: str | None = None) -> dict:
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(relative)
    actual = digest(path)
    if expected is not None and actual != expected:
        raise ValueError(f"SHA-256 mismatch: {relative}")
    return {"path": relative, "sha256": actual, "size_bytes": path.stat().st_size}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    frozen = json.loads((ROOT / "research/protocols/phase3b_config.json").read_text(encoding="utf-8"))
    provenance = json.loads((ROOT / "research/results/PHASE_3B/provenance.json").read_text(encoding="utf-8"))
    training = json.loads((ROOT / "research/results/PHASE_3B/training_summary.json").read_text(encoding="utf-8"))

    frozen_inputs = [checked_file(path, expected) for path, expected in frozen["input_file_hashes"].items()]
    runtime_sources = [checked_file(path, expected) for path, expected in provenance["runtime_source_sha256"].items()]

    experiment_ids = {
        (20260924, "A"): "EXP-0037", (20261012, "A"): "EXP-0038", (20261118, "A"): "EXP-0039",
        (20260924, "naive"): "EXP-0040", (20261012, "naive"): "EXP-0041", (20261118, "naive"): "EXP-0042",
        (20260924, "replay"): "EXP-0043", (20261012, "replay"): "EXP-0044", (20261118, "replay"): "EXP-0045",
    }
    adapters = []
    for record in training:
        seed, condition = record["seed"], record["condition"]
        relative = f".runtime/phase3b/adapters/{seed}/{condition}/adapter_model.safetensors"
        item = checked_file(relative, record["adapter_sha256"])
        item.update({
            "artifact_id": f"phase3b-{seed}-{condition}-adapter",
            "storage": "ignored_local_runtime_only",
            "producing_experiment": experiment_ids[(seed, condition)],
            "seed": seed,
            "lineage_parent": "pinned_3b_base" if condition == "A" else f"phase3b-{seed}-A-adapter",
        })
        adapters.append(item)

    historical = [
        ("c0001-phase2a-qlora", "EXP-0016", 20260920, "pinned_3b_base"),
        ("c0002-phase2b-seed-20260921", "EXP-0021", 20260921, "pinned_3b_base"),
        ("c0003-phase2b-seed-20261007", "EXP-0022", 20261007, "pinned_3b_base"),
        ("c0004-phase2b-seed-20261103", "EXP-0023", 20261103, "pinned_3b_base"),
        ("c0005-phase3a-a-seed-20260923", "EXP-0028", 20260923, "pinned_3b_base"),
        ("c0006-phase3a-a-to-b-seed-20260923", "EXP-0029", 20260923, "c0005-phase3a-a-seed-20260923"),
        ("c0007-phase3a-a-seed-20261011", "EXP-0030", 20261011, "pinned_3b_base"),
        ("c0008-phase3a-a-to-b-seed-20261011", "EXP-0031", 20261011, "c0007-phase3a-a-seed-20261011"),
        ("c0009-phase3a-a-seed-20261117", "EXP-0032", 20261117, "pinned_3b_base"),
        ("c0010-phase3a-a-to-b-seed-20261117", "EXP-0033", 20261117, "c0009-phase3a-a-seed-20261117"),
    ]
    lfs_adapters = []
    for identifier, experiment, seed, parent in historical:
        item = checked_file(f"research/adapters/candidates/{identifier}/adapter_model.safetensors")
        item.update({"artifact_id": identifier, "storage": "git_lfs", "producing_experiment": experiment,
                     "seed": seed, "lineage_parent": parent})
        lfs_adapters.append(item)

    base = []
    for name, expected in frozen["model"]["weight_file_sha256"].items():
        item = checked_file(f"{frozen['model']['local_path']}/{name}", expected)
        item.update({"storage": "ignored_local_model_cache_only", "model_revision": frozen["model"]["revision"]})
        base.append(item)
    compiler = checked_file(".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar", frozen["compiler_sha256"])
    compiler["storage"] = "ignored_local_build_artifact_only"

    # The legacy sealed split shares these three files with other Phase 1 splits.
    # Hash bytes only; do not parse or inspect any task or test contents.
    holdout_manifest = json.loads((ROOT / "research/manifests/phase1_benchmark.json").read_text(encoding="utf-8"))
    sealed_containers = [checked_file(path, expected) for path, expected in holdout_manifest["file_sha256"].items()]

    output = {
        "checkpoint_source_commit": "38a0de06c6329f9805cd211157fdaca7a01aa9eb",
        "scope": "metadata_and_byte_hashes_only; no scientific evaluation",
        "phase3b_config_sha256": digest(ROOT / "research/protocols/phase3b_config.json"),
        "frozen_input_count": len(frozen_inputs),
        "frozen_input_total_bytes": sum(item["size_bytes"] for item in frozen_inputs),
        "runtime_source_count": len(runtime_sources),
        "runtime_source_total_bytes": sum(item["size_bytes"] for item in runtime_sources),
        "phase3b_adapters": adapters,
        "historical_lfs_adapters": lfs_adapters,
        "base_model_shards": base,
        "compiler_jar": compiler,
        "sealed_v1_container_hashes": sealed_containers,
    }
    destination = ROOT / args.output
    if destination.exists():
        existing = json.loads(destination.read_text(encoding="utf-8"))
        if existing != output:
            raise ValueError(f"Existing checkpoint inventory differs: {destination}")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {len(frozen_inputs)} frozen inputs, {len(runtime_sources)} runtime records, "
          f"{len(adapters)} runtime adapters, {len(lfs_adapters)} LFS adapters, {len(base)} base shards, compiler, "
          f"and {len(sealed_containers)} sealed-split containers by hash.")


if __name__ == "__main__":
    main()
