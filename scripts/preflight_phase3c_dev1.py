"""Fail-closed Phase 3C-DEV1 preflight. No gradients or model inference."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

from transformers import AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/protocols/phase3c_dev1_manifest.json"
OUTPUT = ROOT / ".runtime/phase3c_dev1/preflight.json"
FROZEN_HEAD = "359a5eaa70bc8fcb468740b58b2d41ccc0ab5fb2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", FROZEN_HEAD, head], cwd=ROOT)
    if ancestor.returncode != 0:
        raise ValueError(f"Frozen design commit {FROZEN_HEAD} is not an ancestor of HEAD {head}")
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    if status:
        raise ValueError(f"Working tree not clean before gradients: {status}")
    manifest = read("research/protocols/phase3c_dev1_manifest.json")
    for relative, expected in manifest["file_sha256"].items():
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        local = sha256(path)
        normalized = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if local != expected and normalized != manifest["lf_normalized_text_sha256"][relative]:
            raise ValueError(f"Frozen file changed: {relative}")
    validation = read("research/results/PHASE_3C_DEV1/reference_validation.json")
    if validation["status"] != "PASS_REFERENCE_VALIDATION" or validation["semantic_cases_checked"] != 780:
        raise ValueError("Reference validation not frozen/passing")
    audit = read("research/results/PHASE_3C_DEV1/structural_audit.json")
    if len(audit["all_train_eval_pairs"]) != 4320:
        raise ValueError("Structural audit incomplete")
    jar = ROOT / manifest["compiler"]["path"]
    if sha256(jar) != manifest["compiler"]["sha256"]:
        raise ValueError("Compiler changed")
    model_path = ROOT / manifest["base_weights"]["local_path"]
    model_hashes = {}
    for name, expected in manifest["base_weights"]["weight_file_sha256"].items():
        actual = sha256(model_path / name)
        if actual != expected:
            raise ValueError(f"Base weight changed: {name}")
        model_hashes[name] = actual
    support = read("research/protocols/phase3c_execution_manifest.json")["model_support_file_sha256"]
    for relative, expected in support.items():
        if sha256(ROOT / relative) != expected:
            raise ValueError(f"Model support file changed: {relative}")
    for name, expected in manifest["tokenizer_file_sha256"].items():
        if sha256(model_path / name) != expected:
            raise ValueError(f"Tokenizer changed: {name}")
    expected_packages = manifest["environment_at_design_freeze"]["packages"]
    packages = {name: importlib.metadata.version(name) for name in expected_packages}
    if packages != expected_packages or platform.python_version() != manifest["environment_at_design_freeze"]["python"]:
        raise ValueError(f"Critical package/runtime version changed: {packages}")
    rows = {condition: read(f"data/phase3c_dev1/a_{condition}_training_examples.json")
            for condition in ("dense", "diverse")}
    eval_ids = {row["task_id"] for row in read("benchmark/phase3c_dev1/a_development_eval_tasks.json")}
    schedule = read("research/protocols/phase3c_dev1_schedule.json")
    if schedule["seeds"] != manifest["seeds"] or schedule["epochs"] != 3:
        raise ValueError("Schedule seeds/epochs changed")
    by_id = {condition: {row["example_id"]: row for row in group} for condition, group in rows.items()}
    if any(len(group) != 60 or len(by_id[condition]) != 60 for condition, group in rows.items()):
        raise ValueError("Training counts")
    for seed in schedule["seeds"]:
        epochs = schedule["by_seed"][str(seed)]
        if len(epochs) != 3:
            raise ValueError("Epoch count")
        for epoch in epochs:
            families = epoch["slot_families"]
            if len(families) != 60 or families.count("numeric_iteration") != 30 or families.count("array_reduction") != 30:
                raise ValueError("Subskill slots")
            for condition in rows:
                ids = epoch[f"{condition}_example_ids"]
                if set(ids) != set(by_id[condition]) or set(ids) & eval_ids or [by_id[condition][x]["family"] for x in ids] != families:
                    raise ValueError("Schedule ID or family mismatch")
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    exposure = {}
    for condition, group in rows.items():
        full_total = target_total = max_length = 0
        for row in group:
            messages = [{"role": "system", "content": system},
                        {"role": "user", "content": f"Task {row['example_id']}\n\n{row['prompt']}"}]
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            full = tokenizer.apply_chat_template(messages + [{"role": "assistant", "content": row["target"]}], tokenize=False, add_generation_prompt=False)
            prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
            full_ids = tokenizer(full, add_special_tokens=False)["input_ids"]
            if full_ids[:len(prompt_ids)] != prompt_ids:
                raise ValueError("Chat prefix mismatch")
            full_total += len(full_ids)
            target_total += len(full_ids) - len(prompt_ids)
            max_length = max(max_length, len(full_ids))
        exposure[condition] = {"one_epoch_full_tokens": full_total,
                               "one_epoch_supervised_tokens": target_total,
                               "three_epoch_full_tokens": 3 * full_total,
                               "three_epoch_supervised_tokens": 3 * target_total,
                               "max_sequence_tokens": max_length}
    frozen_tokens = read("research/results/PHASE_3C_DEV1/token_budget_audit.json")
    for condition in rows:
        for name in ("one_epoch_full_tokens", "one_epoch_supervised_tokens", "max_full_tokens"):
            observed = exposure[condition]["max_sequence_tokens" if name == "max_full_tokens" else name]
            if observed != frozen_tokens["conditions"][condition][name]:
                raise ValueError(f"Token audit mismatch: {condition}/{name}")
    dense = exposure["dense"]
    diverse = exposure["diverse"]
    full_diff = (diverse["one_epoch_full_tokens"] - dense["one_epoch_full_tokens"]) / dense["one_epoch_full_tokens"]
    target_diff = (diverse["one_epoch_supervised_tokens"] - dense["one_epoch_supervised_tokens"]) / dense["one_epoch_supervised_tokens"]
    if max(abs(full_diff), abs(target_diff)) > 0.10 or max(x["max_sequence_tokens"] for x in exposure.values()) > 320:
        raise ValueError("Prospective token gate failed")
    hardware = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.free", "--format=csv,noheader"], capture_output=True, text=True, check=True).stdout.strip()
    java = subprocess.run([str(ROOT / manifest["compiler"]["java"]), "-version"], capture_output=True, text=True, check=True).stderr.strip()
    payload = {"phase": "3C-DEV1", "status": "PASS_PREGRADIENT_CONTRACT", "frozen_design_head": head,
               "git_status_at_preflight": status, "manifest_sha256": sha256(MANIFEST),
               "compiler_sha256": sha256(jar), "base_weight_sha256": model_hashes,
               "packages": packages, "python": platform.python_version(), "platform": platform.platform(),
               "gpu": hardware, "java": java, "seeds": schedule["seeds"],
               "exposure": exposure, "diverse_minus_dense_full_tokens_per_epoch": diverse["one_epoch_full_tokens"] - dense["one_epoch_full_tokens"],
               "diverse_minus_dense_full_fraction": full_diff,
               "diverse_minus_dense_supervised_tokens_per_epoch": diverse["one_epoch_supervised_tokens"] - dense["one_epoch_supervised_tokens"],
               "diverse_minus_dense_supervised_fraction": target_diff,
               "token_gate": "PASS", "no_model_inference_or_gradients": True}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "full_delta": payload["diverse_minus_dense_full_tokens_per_epoch"],
                      "full_pct": 100 * full_diff, "supervised_delta": payload["diverse_minus_dense_supervised_tokens_per_epoch"],
                      "supervised_pct": 100 * target_diff, "gpu": hardware}))


if __name__ == "__main__":
    main()
