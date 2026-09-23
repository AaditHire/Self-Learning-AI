from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bitsandbytes
import peft
import torch
import transformers
from peft import PeftModel
from transformers import AutoTokenizer

from run_phase2a_evaluation import RssMonitor, classify, dir_hashes, load_base, sha256, summarize
from self_learning_ai.benchmark import extract_source_phase1r, score_source
from self_learning_ai.compiler import GocoCompiler
from phase3c_contract import CONFIG, ROOT, assert_critical_packages, load_frozen, load_items, pre_b_gate_from_records, validate_schedule, verify_execution_files


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--suite",choices=["A","B","regression"],required=True)
    parser.add_argument("--condition",choices=["base","A","naive","replay"],required=True)
    parser.add_argument("--seed",type=int)
    parser.add_argument("--java",type=Path,required=True)
    parser.add_argument("--jar",type=Path,required=True)
    args=parser.parse_args()
    verify_execution_files()
    cfg=load_frozen(check_base=True)
    assert_critical_packages(cfg)
    items=load_items(cfg)
    validate_schedule(cfg,items)
    if (args.seed is None)!=(args.condition=="base"): raise ValueError("Seed required iff adapted")
    if args.seed is not None and args.seed not in cfg["seeds"]: raise ValueError("Unregistered seed")
    if args.condition in ("naive","replay") and not pre_b_gate_from_records(cfg,items)["all_eligible"]:
        raise RuntimeError("STOP_before_B_no_tuning: pre-B A acquisition failed")
    if args.java.resolve()!=(ROOT/cfg["compiler_java"]).resolve() or args.jar.resolve()!=(ROOT/cfg["compiler_artifact"]).resolve():
        raise ValueError("Unpinned compiler/JDK path")
    if sha256(args.jar)!=cfg["compiler_sha256"]: raise ValueError("Compiler jar hash mismatch")
    model_cfg=cfg["base_weights"]; model_path=ROOT/model_cfg["local_path"]
    for name,expected in model_cfg["weight_file_sha256"].items():
        if sha256(model_path/name)!=expected: raise ValueError("Base weight hash mismatch")
    root=ROOT/cfg["runtime_root"]
    seed_label="base" if args.seed is None else str(args.seed)
    output=root/"evaluations"/seed_label/f"{args.condition}_{args.suite.lower()}.json"
    checkpoint=output.with_suffix(".checkpoint.json")
    if output.exists() or checkpoint.exists(): raise FileExistsError(output if output.exists() else checkpoint)
    adapter_path=root/"adapters"/str(args.seed)/args.condition if args.seed is not None else None
    if adapter_path and not adapter_path.is_dir(): raise FileNotFoundError(adapter_path)
    adapter_hashes=dir_hashes(adapter_path) if adapter_path else {}
    if adapter_path:
        record_path=root/"training"/str(args.seed)/f"{args.condition}.json"
        record=json.loads(record_path.read_text(encoding="utf-8"))
        if record["adapter"]["file_hashes"]!=adapter_hashes: raise ValueError("Adapter hash mismatch")
    if args.suite=="regression":
        tasks=json.loads((ROOT/"benchmark/phase2b/general_regression.json").read_text(encoding="utf-8")); tests={}
    else:
        tasks=items[f"{args.suite.lower()}_eval"]
        tests=json.loads((ROOT/f"benchmark/phase3c/{args.suite.lower()}_eval_hidden_tests.json").read_text(encoding="utf-8"))
    runtime_seed=args.seed if args.seed is not None else cfg["seeds"][0]
    torch.manual_seed(runtime_seed); torch.cuda.manual_seed_all(runtime_seed)
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); monitor=RssMonitor(); monitor.start()
    started=time.perf_counter(); tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True); model=load_base(model_path)
    if adapter_path: model=PeftModel.from_pretrained(model,adapter_path,is_trainable=False); model.eval()
    compiler=GocoCompiler(args.java,args.jar,timeout_seconds=cfg["evaluation"]["compiler_timeout_seconds"],output_limit_bytes=cfg["evaluation"]["output_limit_bytes_per_stream"])
    load_seconds=time.perf_counter()-started
    system=(ROOT/"prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    template=(ROOT/"prompts/phase1t_user_template.txt").read_text(encoding="utf-8").strip()
    records=[]; generation_seconds=0.0; total_tokens=0
    output.parent.mkdir(parents=True,exist_ok=True)
    for task in tasks:
        user=task["prompt"] if args.suite=="regression" else template.format(task_id=task["task_id"],task_prompt=task["prompt"])
        runtime_system="You are a precise programming and instruction assistant. Follow the requested answer format exactly and return no explanation." if args.suite=="regression" else system
        rendered=tokenizer.apply_chat_template([{"role":"system","content":runtime_system},{"role":"user","content":user}],tokenize=False,add_generation_prompt=True)
        inputs=tokenizer(rendered,return_tensors="pt",truncation=False).to("cuda:0")
        input_tokens=int(inputs["input_ids"].shape[1])
        if input_tokens>cfg["evaluation"]["max_input_tokens"]: raise ValueError("Input too long")
        begin=time.perf_counter()
        with torch.inference_mode():
            generated=model.generate(**inputs,do_sample=False,num_beams=1,max_new_tokens=cfg["evaluation"]["regression_max_new_tokens"] if args.suite=="regression" else cfg["evaluation"]["max_new_tokens"],pad_token_id=tokenizer.eos_token_id)
        elapsed=time.perf_counter()-begin; new=generated[0,input_tokens:]
        raw=tokenizer.decode(new,skip_special_tokens=True); generation_seconds+=elapsed; total_tokens+=int(new.shape[0])
        if args.suite=="regression":
            normalized=raw.strip()
            row={"task_id":task["task_id"],"category":task["category"],"raw_generation":raw,"normalized_output":normalized,"expected":task["expected"],"passed":normalized==task["expected"],"input_tokens":input_tokens,"output_tokens":int(new.shape[0]),"generation_ms":round(elapsed*1000)}
        else:
            normalized=extract_source_phase1r(raw)
            scored=score_source(compiler,task,tests[task["task_id"]],normalized).as_dict()
            row={"task_id":task["task_id"],"family":task["family"],"raw_generation":raw,"normalized_output":normalized,"input_tokens":input_tokens,"output_tokens":int(new.shape[0]),"generation_ms":round(elapsed*1000)}|scored
            row["failure_category"]=classify(normalized,row)
        records.append(row)
        checkpoint.write_text(json.dumps({"phase":"3C","suite":args.suite,"condition":args.condition,"seed":args.seed,"completed_tasks":len(records),"records":records},indent=2)+"\n",encoding="utf-8")
    peak_rss=monitor.stop()
    if args.suite=="regression":
        correct=sum(r["passed"] for r in records)
        summary={"correct":correct,"total":len(records),"accuracy":correct/len(records),"by_category":{category:{"correct":sum(r["passed"] for r in records if r["category"]==category),"total":sum(r["category"]==category for r in records)} for category in sorted({r["category"] for r in records})}}
    else: summary=summarize(records)
    payload={"phase":"3C","suite":args.suite,"condition":args.condition,"seed":args.seed,"config_sha256":sha256(CONFIG),"adapter_file_hashes":adapter_hashes,"environment":{"platform":platform.platform(),"python":platform.python_version(),"torch":torch.__version__,"transformers":transformers.__version__,"bitsandbytes":bitsandbytes.__version__,"peft":peft.__version__,"cuda_runtime":torch.version.cuda,"gpu":torch.cuda.get_device_name(0)},"hardware":{"load_seconds":load_seconds,"peak_gpu_memory_bytes":int(torch.cuda.max_memory_allocated()),"peak_process_rss_bytes":peak_rss,"generation_seconds":generation_seconds,"output_tokens":total_tokens},"records":records,"summary":summary}
    output.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    checkpoint.unlink()
    print(json.dumps({"suite":args.suite,"condition":args.condition,"seed":args.seed,"summary":summary},indent=2))


if __name__=="__main__": main()
