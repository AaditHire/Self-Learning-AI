"""Freeze reviewed execution-code and local tokenizer/support hashes once."""

from __future__ import annotations

import json
from pathlib import Path

from phase3c_contract import (CONFIG, EXECUTION_MANIFEST, FROZEN_CONFIG_SHA256, FROZEN_HEAD,
                              ROOT, load_frozen, normalized_sha256, sha256)


CODE = (
    ".gitattributes",
    "scripts/phase3c_contract.py",
    "scripts/train_phase3c_qlora.py",
    "scripts/run_phase3c_evaluation.py",
    "scripts/run_phase3c.py",
    "scripts/analyze_phase3c.py",
    "scripts/finalize_phase3c_artifacts.py",
    "scripts/capture_phase3c_environment.py",
    "scripts/preserve_phase3c_artifacts.py",
    "scripts/verify_phase3c_remote_restore.py",
    "scripts/audit_phase3c_train_eval_separation.py",
    "scripts/freeze_phase3c_execution_manifest.py",
    "scripts/train_phase2a_qlora.py",
    "scripts/run_phase2a_evaluation.py",
    "src/self_learning_ai/benchmark.py",
    "src/self_learning_ai/compiler.py",
    "tests/test_phase3c_execution_contract.py",
)

SUPPORT = (
    "config.json", "generation_config.json", "model.safetensors.index.json",
    "merges.txt", "vocab.json", "tokenizer_config.json", "tokenizer.json",
)


def main() -> None:
    if EXECUTION_MANIFEST.exists():
        raise FileExistsError(EXECUTION_MANIFEST)
    cfg = load_frozen(check_base=False)
    if sha256(CONFIG) != FROZEN_CONFIG_SHA256:
        raise ValueError("Frozen Phase 3C config differs from reviewed Windows bytes")
    model = Path(cfg["base_weights"]["local_path"])
    payload = {
        "phase": "3C", "status": "pre_execution_implementation_frozen_no_model_run",
        "frozen_design_commit": FROZEN_HEAD,
        "frozen_config_sha256": FROZEN_CONFIG_SHA256,
        "code_git_text_sha256": {name: normalized_sha256(ROOT / name) for name in CODE},
        "model_support_file_sha256": {(model / name).as_posix(): sha256(ROOT / model / name) for name in SUPPORT},
        "required_action_before_training": "independent scientific review and explicit future authorization",
    }
    EXECUTION_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with EXECUTION_MANIFEST.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"code_files": len(CODE), "model_support_files": len(SUPPORT),
                      "manifest_sha256": sha256(EXECUTION_MANIFEST)}))


if __name__ == "__main__":
    main()
