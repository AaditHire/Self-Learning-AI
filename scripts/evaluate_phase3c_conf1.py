"""CONF1 evaluation; the acquisition gate precedes confirmatory generation."""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.conf1_r1.execution import (
    DEFAULT_RUNTIME, AcquisitionFailed, GateStop, compiler_score, encode_prompt, read, require_execution_authorization,
    c15_reviewed_incident, run_confirmatory_c15_continuation, run_confirmatory, run_own_training, sha256,
)


def generator(cfg, runtime):
    import numpy as np
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    model_path = ROOT / cfg["base_weights"]["local_path"]
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    active = None
    model = None

    def reset(seed):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    def generate(seed, condition, task, messages):
        nonlocal active, model
        if active != (seed, condition):
            if model is not None:
                del model
                model = None
                torch.cuda.empty_cache()
            record = read(runtime / f"training/{seed}/{condition}.json")
            receipt = read(runtime / f"training/{seed}/{condition}.sha256.json")
            if sha256(runtime / f"training/{seed}/{condition}.json") != receipt["sha256"]:
                raise GateStop("training cell record hash mismatch")
            adapter = runtime / f"adapters/{seed}/{condition}"
            hashes = {p.relative_to(adapter).as_posix(): sha256(p) for p in adapter.rglob("*") if p.is_file()}
            if not hashes or hashes != record["adapter"]["file_hashes"]:
                raise GateStop("adapter directory hash mismatch")
            if any(sha256(model_path / name) != expected
                   for name, expected in cfg["base_weights"]["weight_file_sha256"].items()):
                raise GateStop("immutable base weights changed before cell")
            quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
            model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True,
                quantization_config=quant, device_map={"": 0}, dtype=torch.float16)
            model = PeftModel.from_pretrained(model, adapter, is_trainable=False)
            model.eval()
            active = (seed, condition)
            # Loading an adapter can consume RNG; reapply C13 after cell load.
            from self_learning_ai.conf1_r1.schedule import task_rng_seed
            reset(task_rng_seed(seed, task["task_id"]))
        ids = encode_prompt(tokenizer, messages)
        inputs = {"input_ids": torch.tensor([ids], dtype=torch.long, device="cuda:0"),
                  "attention_mask": torch.ones((1, len(ids)), dtype=torch.long, device="cuda:0")}
        length = len(ids)
        if length > cfg["evaluation"]["max_input_tokens"]:
            raise GateStop("evaluation input token limit exceeded")
        with torch.inference_mode():
            output = model.generate(**inputs, do_sample=False, num_beams=1,
                max_new_tokens=cfg["evaluation"]["max_new_tokens"], pad_token_id=tokenizer.eos_token_id)
        return tokenizer.decode(output[0, length:], skip_special_tokens=True)
    return generate, reset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--check-authorization-only", action="store_true")
    parser.add_argument("--c15-continue-confirmatory", action="store_true")
    args = parser.parse_args()
    try:
        manifest = require_execution_authorization(args.candidate_dir)
        reviewed = c15_reviewed_incident(manifest) if args.c15_continue_confirmatory else None
        if args.check_authorization_only:
            print("CONF1 authorization PASS; no model imported")
            return
        from train_phase3c_conf1 import pinned_config
        cfg = pinned_config(manifest)
        from self_learning_ai.compiler import GocoCompiler
        compiler = GocoCompiler(ROOT / cfg["compiler"]["java"], ROOT / cfg["compiler"]["path"],
            timeout_seconds=cfg["evaluation"]["compiler_timeout_seconds"],
            output_limit_bytes=cfg["evaluation"]["output_limit_bytes_per_stream"])
        generate, reset = generator(cfg, DEFAULT_RUNTIME)
        score = compiler_score(compiler)
        if args.c15_continue_confirmatory:
            run_confirmatory_c15_continuation(args.candidate_dir, generate, score, reset=reset,
                                             reviewed_incident=reviewed)
        else:
            run_own_training(args.candidate_dir, generate, score, reset=reset)
            run_confirmatory(args.candidate_dir, generate, score, reset=reset)
    except AcquisitionFailed as exc:
        parser.exit(3, "INDETERMINATE_INSUFFICIENT_ACQUISITION; run_confirmatory was not called\n")
    except GateStop as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__":
    main()
