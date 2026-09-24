"""Measure frozen DEV1 token exposure using the pinned local tokenizer; no model load."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from transformers import AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/results/PHASE_3C_DEV1/token_budget_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    prior = json.loads((ROOT / "research/protocols/phase3c_config.json").read_text(encoding="utf-8"))
    model = ROOT / prior["base_weights"]["local_path"]
    tokenizer = AutoTokenizer.from_pretrained(model, local_files_only=True)
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    max_length = prior["training"]["max_length"]
    conditions = {}
    for name in ("dense", "diverse"):
        path = ROOT / f"data/phase3c_dev1/a_{name}_training_examples.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        lengths = {}
        for row in rows:
            messages = [{"role": "system", "content": system},
                        {"role": "user", "content": f"Task {row['example_id']}\n\n{row['prompt']}"}]
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            full = tokenizer.apply_chat_template(messages + [{"role": "assistant", "content": row["target"]}],
                                                 tokenize=False, add_generation_prompt=False)
            prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
            full_ids = tokenizer(full, add_special_tokens=False)["input_ids"]
            if full_ids[:len(prompt_ids)] != prompt_ids:
                raise ValueError(f"Prefix mismatch {row['example_id']}")
            if len(full_ids) > max_length:
                raise ValueError(f"Over frozen length {row['example_id']}={len(full_ids)}")
            lengths[row["example_id"]] = {"full_tokens": len(full_ids),
                                           "supervised_tokens": len(full_ids) - len(prompt_ids)}
        conditions[name] = {"examples": len(rows), "max_full_tokens": max(x["full_tokens"] for x in lengths.values()),
                            "one_epoch_full_tokens": sum(x["full_tokens"] for x in lengths.values()),
                            "one_epoch_supervised_tokens": sum(x["supervised_tokens"] for x in lengths.values()),
                            "by_example": lengths, "dataset_sha256": sha256(path)}
    dense = conditions["dense"]["one_epoch_full_tokens"]
    diverse = conditions["diverse"]["one_epoch_full_tokens"]
    residual = abs(diverse - dense) / dense
    dense_supervised = conditions["dense"]["one_epoch_supervised_tokens"]
    diverse_supervised = conditions["diverse"]["one_epoch_supervised_tokens"]
    supervised_residual = abs(diverse_supervised - dense_supervised) / dense_supervised
    payload = {"phase": "3C-DEV1", "status": "PRE_MODEL_TOKEN_AUDIT", "tokenizer_path": str(model.relative_to(ROOT)).replace('\\', '/'),
               "tokenizer_file_sha256": {p.name: sha256(p) for p in sorted(model.glob("*token*")) if p.is_file()},
               "max_length": max_length, "conditions": conditions,
               "full_token_relative_difference_from_dense": residual,
               "supervised_token_relative_difference_from_dense": supervised_residual,
               "prospective_materiality_threshold": 0.10,
               "compute_gate": "PASS" if max(residual, supervised_residual) <= 0.10 else "STOP_REDESIGN_BEFORE_GRADIENTS"}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"dense_full": dense, "diverse_full": diverse,
                      "full_residual": residual, "supervised_residual": supervised_residual,
                      "compute_gate": payload["compute_gate"]}))


if __name__ == "__main__":
    main()
