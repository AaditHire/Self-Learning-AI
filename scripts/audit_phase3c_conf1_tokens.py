"""Count CONF1 serialized chat tokens using tokenizer files only; no model load."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / ".models/Qwen2.5-Coder-3B-Instruct-488639f"
OUT = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE/token_budget_audit.json"
EXPECTED = {"tokenizer.json": "c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539",
            "tokenizer_config.json": "959e7f1d9a1b7641a6d6ce05ca97b75c7894fcb66cbe5a040406458fb1128ee4"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    for name, value in EXPECTED.items():
        if sha(MODEL / name) != value:
            raise ValueError(f"tokenizer hash mismatch: {name}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    conditions = {}
    for condition in ("isolated", "composition"):
        rows = json.loads((ROOT / f"data/phase3c_conf1/{condition}_examples.json").read_text(encoding="utf-8"))
        per_example = []
        for row in rows:
            messages = [{"role": "system", "content": system},
                        {"role": "user", "content": f"Task {row['example_id']}\n\n{row['prompt']}"}]
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            full = tokenizer.apply_chat_template(messages + [{"role": "assistant", "content": row["target"]}],
                                                 tokenize=False, add_generation_prompt=False)
            pi = tokenizer(prompt, add_special_tokens=False)["input_ids"]
            fi = tokenizer(full, add_special_tokens=False)["input_ids"]
            if fi[:len(pi)] != pi or len(fi) > 320:
                raise ValueError(f"token prefix/length failure: {row['example_id']}")
            per_example.append({"example_id": row["example_id"], "full_tokens": len(fi),
                                "supervised_tokens": len(fi) - len(pi)})
        conditions[condition] = {"examples": len(rows), "full_tokens": sum(x["full_tokens"] for x in per_example),
                                 "supervised_tokens": sum(x["supervised_tokens"] for x in per_example),
                                 "max_full_tokens": max(x["full_tokens"] for x in per_example),
                                 "per_example": per_example}
    a, b = conditions["isolated"], conditions["composition"]
    full_diff = abs(b["full_tokens"] - a["full_tokens"]) / a["full_tokens"]
    supervised_diff = abs(b["supervised_tokens"] - a["supervised_tokens"]) / a["supervised_tokens"]
    result = {"status": "NON_MODEL_TOKEN_AUDIT_OF_UNFROZEN_CANDIDATE", "tokenizer_sha256": EXPECTED,
              "conditions": conditions, "full_relative_difference": full_diff,
              "supervised_relative_difference": supervised_diff,
              "full_limit": 0.05, "supervised_limit": 0.02,
              "token_gate_pass": full_diff <= 0.05 and supervised_diff <= 0.02}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"isolated": {k: a[k] for k in ("full_tokens", "supervised_tokens", "max_full_tokens")},
                      "composition": {k: b[k] for k in ("full_tokens", "supervised_tokens", "max_full_tokens")},
                      "full_relative_difference": full_diff,
                      "supervised_relative_difference": supervised_diff,
                      "token_gate_pass": result["token_gate_pass"]}))


if __name__ == "__main__":
    main()
