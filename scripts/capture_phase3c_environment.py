"""Capture execution-host provenance without loading a model or running inference."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

from phase3c_contract import CONFIG, EXECUTION_MANIFEST, ROOT, load_frozen, sha256, verify_execution_files


def command(args: list[str]) -> dict:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=15, check=False)
        return {"returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"error": type(exc).__name__, "detail": str(exc)}


def capture() -> dict:
    verify_execution_files()
    cfg = load_frozen(check_base=True)
    packages = {name: importlib.metadata.version(name) for name in
                ("torch", "transformers", "peft", "bitsandbytes", "accelerate", "numpy", "safetensors")}
    if packages != cfg["environment_at_design_freeze"]["packages"]:
        raise ValueError("Critical package versions changed; no silent upgrade permitted")
    import torch  # Hardware inspection only; no model object is constructed.
    gpu = []
    for index in range(torch.cuda.device_count()):
        properties = torch.cuda.get_device_properties(index)
        gpu.append({"index": index, "name": properties.name, "total_memory_bytes": properties.total_memory,
                    "compute_capability": [properties.major, properties.minor]})
    if not gpu:
        raise RuntimeError("Phase 3C QLoRA execution requires a CUDA GPU")
    java = ROOT / cfg["compiler_java"]
    payload = {
        "phase": "3C", "kind": "pre_execution_environment", "frozen_config_sha256": sha256(CONFIG),
        "execution_manifest_sha256": sha256(EXECUTION_MANIFEST),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": sys.version, "platform": platform.platform(), "packages": packages,
        "package_manifest": sorted({d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
                                    if d.metadata.get("Name")}.items()),
        "cuda_runtime": torch.version.cuda, "torch_cuda_available": torch.cuda.is_available(),
        "gpu": gpu,
        "nvidia_smi": command(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"]),
        "jdk": command([str(java), "-version"]), "java_sha256": sha256(java),
        "compiler_jar_sha256": sha256(ROOT / cfg["compiler_artifact"]),
        "tokenizer_model_revision": cfg["base_weights"]["revision"],
        "tokenizer_file_sha256": {p.name: sha256(p) for p in sorted((ROOT / cfg["base_weights"]["local_path"]).glob("tokenizer*")) if p.is_file()},
        "determinism": {
            "torch_deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
            "cudnn_deterministic": torch.backends.cudnn.deterministic,
            "cudnn_benchmark": torch.backends.cudnn.benchmark,
            "cuda_matmul_allow_tf32": torch.backends.cuda.matmul.allow_tf32,
            "cudnn_allow_tf32": torch.backends.cudnn.allow_tf32,
            "CUBLAS_WORKSPACE_CONFIG": os.getenv("CUBLAS_WORKSPACE_CONFIG"),
        },
    }
    if payload["nvidia_smi"].get("returncode") != 0 or payload["jdk"].get("returncode") != 0:
        raise RuntimeError("GPU driver or pinned JDK information unavailable")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    payload = capture()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"gpu": payload["gpu"], "driver": payload["nvidia_smi"]["stdout"],
                      "config_sha256": payload["frozen_config_sha256"]}))


if __name__ == "__main__":
    main()
