from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import psutil
import torch
from transformers import AutoTokenizer

from run_phase1s_evaluation import load_frozen_model, sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    runtime = config["models"]["qwen_3b"]
    model_path = Path(runtime["local_path"])
    for relative, expected in runtime["weight_file_sha256"].items():
        if sha256(model_path / relative) != expected:
            raise ValueError(f"Weight hash mismatch: {relative}")
    system = Path(config["prompt"]["system"]).read_text(encoding="utf-8").strip()
    for context_file in config["prompt"]["candidate_c_context_files"]:
        system += f"\n\nTRUSTED GOCO KNOWLEDGE: {Path(context_file).name}\n\n"
        system += Path(context_file).read_text(encoding="utf-8").strip()
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    rss_before = psutil.Process().memory_info().rss
    started = time.perf_counter()
    model = load_frozen_model(model_path, runtime)
    load_seconds = time.perf_counter() - started
    rendered = tokenizer.apply_chat_template([
        {"role": "system", "content": system},
        {"role": "user", "content": "Return only a complete GOCO program that displays the number 1 with a newline."},
    ], tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(rendered, return_tensors="pt").to(runtime["device"])
    started = time.perf_counter()
    with torch.inference_mode():
        generated = model.generate(**inputs, do_sample=False, num_beams=1, max_new_tokens=32, pad_token_id=tokenizer.eos_token_id)
    generation_seconds = time.perf_counter() - started
    new_tokens = generated[0, inputs["input_ids"].shape[1]:]
    result = {
        "success": True,
        "config_sha256": sha256(args.config),
        "model": runtime,
        "input_tokens": int(inputs["input_ids"].shape[1]),
        "output_tokens": int(new_tokens.shape[0]),
        "generation_seconds": generation_seconds,
        "tokens_per_second": int(new_tokens.shape[0]) / generation_seconds,
        "load_seconds": load_seconds,
        "peak_gpu_memory_bytes": int(torch.cuda.max_memory_allocated()),
        "process_rss_before_bytes": rss_before,
        "process_rss_after_bytes": psutil.Process().memory_info().rss,
        "raw_generation": tokenizer.decode(new_tokens, skip_special_tokens=True),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
