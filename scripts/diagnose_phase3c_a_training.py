"""Post-STOP, read-only inference on the 60 consumed Phase 3C A training IDs.

This is exploratory diagnosis. It never trains, alters frozen inputs, or reads
the final-paper holdout. The original Phase 3C confirmatory result is fixed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import torch
from peft import PeftModel
from transformers import AutoTokenizer

from run_phase2a_evaluation import classify, dir_hashes, load_base, summarize
from phase3c_contract import ROOT, assert_critical_packages, load_frozen, sha256, verify_execution_files
from self_learning_ai.benchmark import extract_source_phase1r, score_source
from self_learning_ai.compiler import GocoCompiler


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    verify_execution_files()
    cfg = load_frozen(check_base=True)
    assert_critical_packages(cfg)
    if args.seed not in cfg["seeds"]:
        raise ValueError("Seed is outside frozen Phase 3C")
    output = args.output.resolve()
    checkpoint = output.with_suffix(".checkpoint.json")
    if output.exists() or checkpoint.exists():
        raise FileExistsError(output if output.exists() else checkpoint)

    root = ROOT / cfg["runtime_root"]
    gate = json.loads((root / "pre_b_acquisition_gate.json").read_text(encoding="utf-8"))
    if gate["action"] != "STOP_before_B_no_tuning" or gate["all_eligible"]:
        raise RuntimeError("This diagnosis requires the completed acquisition STOP")
    adapter = root / "adapters" / str(args.seed) / "A"
    training_record = root / "training" / str(args.seed) / "A.json"
    original_record = json.loads(training_record.read_text(encoding="utf-8"))
    adapter_hashes_before = dir_hashes(adapter)
    if adapter_hashes_before != original_record["adapter"]["file_hashes"]:
        raise ValueError("Original A adapter differs from its training record")
    preserved = ROOT / "research/adapters/phase3c-preserved" / str(args.seed) / "A/adapter_model.safetensors"
    if sha256(preserved) != adapter_hashes_before["adapter_model.safetensors"]:
        raise ValueError("Preserved adapter differs from original")

    rows = json.loads((ROOT / "data/phase3c/a_training_examples.json").read_text(encoding="utf-8"))
    cases = json.loads((ROOT / "data/phase3c/a_training_hidden_tests.json").read_text(encoding="utf-8"))
    ids = [row["example_id"] for row in rows]
    if len(rows) != 60 or len(set(ids)) != 60 or set(cases) != set(ids):
        raise ValueError("Frozen A training ID/test mismatch")
    jar = ROOT / cfg["compiler_artifact"]
    java = ROOT / cfg["compiler_java"]
    if sha256(jar) != cfg["compiler_sha256"]:
        raise ValueError("Compiler hash mismatch")

    model_dir = ROOT / cfg["base_weights"]["local_path"]
    base_before = {name: sha256(model_dir / name) for name in cfg["base_weights"]["weight_file_sha256"]}
    if base_before != cfg["base_weights"]["weight_file_sha256"]:
        raise ValueError("Base weight hash mismatch")
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    model = PeftModel.from_pretrained(load_base(model_dir), adapter, is_trainable=False)
    model.eval()
    if any(parameter.requires_grad for parameter in model.parameters()):
        raise RuntimeError("Diagnostic inference found trainable parameters")
    compiler = GocoCompiler(java, jar,
                            timeout_seconds=cfg["evaluation"]["compiler_timeout_seconds"],
                            output_limit_bytes=cfg["evaluation"]["output_limit_bytes_per_stream"])
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    template = (ROOT / "prompts/phase1t_user_template.txt").read_text(encoding="utf-8").strip()
    records: list[dict] = []
    output.parent.mkdir(parents=True, exist_ok=True)

    for row in rows:
        item_id = row["example_id"]
        user = template.format(task_id=item_id, task_prompt=row["prompt"])
        rendered = tokenizer.apply_chat_template(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(rendered, return_tensors="pt", truncation=False).to("cuda:0")
        input_tokens = int(inputs["input_ids"].shape[1])
        if input_tokens > cfg["evaluation"]["max_input_tokens"]:
            raise ValueError(f"Diagnostic input exceeds frozen evaluation maximum: {item_id}")
        with torch.inference_mode():
            generated = model.generate(
                **inputs, do_sample=False, num_beams=1,
                max_new_tokens=cfg["evaluation"]["max_new_tokens"],
                pad_token_id=tokenizer.eos_token_id)
        new = generated[0, input_tokens:]
        raw = tokenizer.decode(new, skip_special_tokens=True)
        normalized = extract_source_phase1r(raw)
        task = {"task_id": item_id, "family": row["family"],
                "difficulty": "phase3c_training_posthoc_diagnostic", "required_regex": []}
        scored = score_source(compiler, task, cases[item_id], normalized).as_dict()
        record = {"task_id": item_id, "family": row["family"], "archetype": row["archetype"],
                  "raw_generation": raw, "normalized_output": normalized,
                  "input_tokens": input_tokens, "output_tokens": int(new.shape[0]),
                  "hit_output_cap": int(new.shape[0]) == cfg["evaluation"]["max_new_tokens"],
                  **scored}
        record["failure_category"] = classify(normalized, record)
        records.append(record)
        checkpoint.write_text(json.dumps({"status": "POST_HOC_DIAGNOSTIC_IN_PROGRESS",
                                          "seed": args.seed, "completed": len(records),
                                          "records": records}, indent=2) + "\n", encoding="utf-8")
        if len(records) % 10 == 0:
            print(json.dumps({"seed": args.seed, "completed": len(records)}), flush=True)

    if dir_hashes(adapter) != adapter_hashes_before:
        raise RuntimeError("Original A adapter changed during diagnosis")
    base_after = {name: sha256(model_dir / name) for name in base_before}
    if base_after != base_before:
        raise RuntimeError("Base weights changed during diagnosis")
    payload = {"phase": "3C-DIAG", "status": "POST_HOC_DIAGNOSTIC_CONSUMED_TRAINING_SET",
               "confirmatory_phase3c_result": "STOP_before_B_no_tuning",
               "seed": args.seed, "adapter_sha256": adapter_hashes_before["adapter_model.safetensors"],
               "adapter_hashes_unchanged": True, "base_weight_hashes_unchanged": True,
               "prompt_and_scoring": "same Phase 3C no-docs template, greedy decoding, compiler, and five frozen training hidden cases",
               "records": records, "summary": summarize(records)}
    with output.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    checkpoint.unlink()
    print(json.dumps({"seed": args.seed, "summary": payload["summary"]}), flush=True)


if __name__ == "__main__":
    main()
