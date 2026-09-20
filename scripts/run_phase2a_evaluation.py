from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import bitsandbytes
import peft
import psutil
import torch
import transformers
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from self_learning_ai.benchmark import extract_source_phase1r, paired_comparison, score_source
from self_learning_ai.compiler import GocoCompiler


def sha256(path:Path)->str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()


def dir_hashes(directory:Path)->dict[str,str]:
    return {str(p.relative_to(directory)).replace("\\","/"):sha256(p) for p in sorted(directory.rglob("*")) if p.is_file()}


class RssMonitor(threading.Thread):
    def __init__(self)->None: super().__init__(daemon=True); self.stop_event=threading.Event(); self.peak=0
    def run(self)->None:
        process=psutil.Process(os.getpid())
        while not self.stop_event.wait(.05): self.peak=max(self.peak,process.memory_info().rss)
    def stop(self)->int: self.stop_event.set(); self.join(timeout=2); return self.peak


def load_base(path:Path)->Any:
    quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_compute_dtype=torch.float16,bnb_4bit_use_double_quant=True)
    model=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,quantization_config=quant,device_map={"":0},dtype=torch.float16)
    model.requires_grad_(False); model.eval()
    return model


def classify(normalized:str,record:dict[str,Any])->str:
    if record["hidden_pass"]: return "success"
    lowered=normalized.casefold()
    if "package main" in lowered or re.search(r'(?m)^\s*import\s+["(]',normalized): return "wrong_language"
    if record["error_phase"] in {"lexical","syntax","semantic","runtime","timeout","output_limit","system"}: return record["error_phase"]
    if not record["structural_requirements_met"]: return "structural_requirement"
    if record["execution_success"]: return "hidden_test_semantic"
    return "unknown"


def summarize(rows:list[dict[str,Any]])->dict[str,Any]:
    by_family:dict[str,list[dict[str,Any]]]=defaultdict(list)
    for row in rows: by_family[row["family"]].append(row)
    def metrics(values:list[dict[str,Any]])->dict[str,Any]:
        result={"n":len(values),"failure_taxonomy":dict(sorted(Counter(v["failure_category"] for v in values).items()))}
        for key in ("parse_success","compile_success","execution_success","hidden_pass"):
            count=sum(bool(v[key]) for v in values); result[key+"_count"]=count; result[key]=count/len(values)
        return result
    return {"overall":metrics(rows),"by_family":{family:metrics(values) for family,values in sorted(by_family.items())}}


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",type=Path,required=True)
    parser.add_argument("--plan",choices=["primary","training","regression","docs_reference"],required=True)
    parser.add_argument("--adapter",type=Path)
    parser.add_argument("--java",type=Path,required=True)
    parser.add_argument("--jar",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    if args.plan in {"primary","training","regression"} and args.adapter is None: raise ValueError("--adapter required")
    config=json.loads(args.config.read_text(encoding="utf-8"))
    for raw,expected in config["input_file_hashes"].items():
        actual=sha256(Path(raw))
        if actual!=expected: raise ValueError(f"Frozen input hash mismatch {raw}: {actual}")
    model_cfg=config["model"]; model_path=Path(model_cfg["local_path"])
    for name,expected in model_cfg["weight_file_sha256"].items():
        if sha256(model_path/name)!=expected: raise ValueError(f"Weight hash mismatch {name}")
    adapter_hashes=dir_hashes(args.adapter) if args.adapter else {}
    base_system=Path(config["prompt"]["system"]).read_text(encoding="utf-8").strip()
    docs_system=base_system
    for path in config["prompt"]["candidate_c_context_files"]:
        docs_system+=f"\n\nTRUSTED GOCO KNOWLEDGE: {Path(path).name}\n\n"+Path(path).read_text(encoding="utf-8").strip()
    template=Path(config["prompt"]["user_template"]).read_text(encoding="utf-8").strip()

    if args.plan=="primary":
        tasks=json.loads(Path(config["data"]["development_tasks"]).read_text()); tests=json.loads(Path(config["data"]["development_tests"]).read_text()); conditions=["BASE_NO_DOCS","ADAPTED_NO_DOCS"]
    elif args.plan=="training":
        examples=json.loads(Path(config["data"]["training_examples"]).read_text()); tests=json.loads(Path(config["data"]["training_tests"]).read_text())
        tasks=[{"task_id":r["example_id"],"family":r["family"],"difficulty":"phase2a_training","prompt":r["prompt"],"required_regex":[]} for r in examples]; conditions=["ADAPTED_NO_DOCS"]
    elif args.plan=="docs_reference":
        tasks=json.loads(Path(config["data"]["development_tasks"]).read_text()); tests=json.loads(Path(config["data"]["development_tests"]).read_text()); conditions=["BASE_DOCS"]
    else:
        tasks=json.loads(Path(config["data"]["general_regression"]).read_text()); tests={}; conditions=["BASE_NO_DOCS","ADAPTED_NO_DOCS"]

    torch.manual_seed(config["seed"]); torch.cuda.manual_seed_all(config["seed"]); torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    monitor=RssMonitor(); monitor.start(); load_started=time.perf_counter()
    tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True); model=load_base(model_path)
    compiler=GocoCompiler(args.java,args.jar,timeout_seconds=config["evaluation"]["compiler_timeout_seconds"],output_limit_bytes=config["evaluation"]["output_limit_bytes_per_stream"])
    load_seconds=time.perf_counter()-load_started; total_seconds=0.0; total_tokens=0; outputs={}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for condition in conditions:
        if condition=="ADAPTED_NO_DOCS" and not isinstance(model,PeftModel):
            assert args.adapter is not None
            model=PeftModel.from_pretrained(model,args.adapter,is_trainable=False); model.eval()
        system=docs_system if condition=="BASE_DOCS" else base_system
        records=[]
        for task in tasks:
            user=task["prompt"] if args.plan=="regression" else template.format(task_id=task["task_id"],task_prompt=task["prompt"])
            regression_system="You are a precise programming and instruction assistant. Follow the requested answer format exactly and return no explanation." if args.plan=="regression" else system
            rendered=tokenizer.apply_chat_template([{"role":"system","content":regression_system},{"role":"user","content":user}],tokenize=False,add_generation_prompt=True)
            inputs=tokenizer(rendered,return_tensors="pt",truncation=False).to("cuda:0"); input_tokens=int(inputs["input_ids"].shape[1])
            if input_tokens>config["evaluation"]["max_input_tokens"]: raise ValueError(f"Input too long {task['task_id']}")
            started=time.perf_counter()
            with torch.inference_mode(): generated=model.generate(**inputs,do_sample=False,num_beams=1,max_new_tokens=config["evaluation"]["regression_max_new_tokens"] if args.plan=="regression" else config["evaluation"]["max_new_tokens"],pad_token_id=tokenizer.eos_token_id)
            elapsed=time.perf_counter()-started; new=generated[0,input_tokens:]; raw=tokenizer.decode(new,skip_special_tokens=True); total_seconds+=elapsed; total_tokens+=int(new.shape[0])
            if args.plan=="regression":
                normalized=raw.strip(); passed=normalized==task["expected"]
                record={"condition":condition,"task_id":task["task_id"],"category":task["category"],"raw_generation":raw,"normalized_output":normalized,"expected":task["expected"],"passed":passed,"input_tokens":input_tokens,"output_tokens":int(new.shape[0]),"generation_ms":round(elapsed*1000)}
            else:
                normalized=extract_source_phase1r(raw); scored=score_source(compiler,task,tests[task["task_id"]],normalized).as_dict()
                record={"condition":condition,"task_id":task["task_id"],"family":task["family"],"raw_generation":raw,"normalized_output":normalized,"input_tokens":input_tokens,"output_tokens":int(new.shape[0]),"generation_ms":round(elapsed*1000)}|scored
                record["failure_category"]=classify(normalized,record)
            records.append(record)
            checkpoint={"plan":args.plan,"completed_condition":condition,"completed_tasks":len(records),"conditions":outputs|{condition:records}}
            (args.output.parent/f"{args.output.stem}.{args.plan}.checkpoint.json").write_text(json.dumps(checkpoint,indent=2)+"\n",encoding="utf-8")
        outputs[condition]=records
    peak_rss=monitor.stop()
    payload={"phase":"2A","plan":args.plan,"config_sha256":sha256(args.config),"condition_order":conditions,"adapter_file_hashes":adapter_hashes,"environment":{"platform":platform.platform(),"python":platform.python_version(),"torch":torch.__version__,"transformers":transformers.__version__,"bitsandbytes":bitsandbytes.__version__,"peft":peft.__version__,"cuda_runtime":torch.version.cuda,"gpu":torch.cuda.get_device_name(0)},"hardware":{"load_seconds":load_seconds,"peak_gpu_memory_bytes":int(torch.cuda.max_memory_allocated()),"peak_process_rss_bytes":peak_rss,"generation_seconds":total_seconds,"output_tokens":total_tokens,"output_tokens_per_second":total_tokens/total_seconds},"conditions":outputs}
    if args.plan=="regression":
        payload["summaries"]={c:{"correct":sum(r["passed"] for r in rows),"total":len(rows),"accuracy":sum(r["passed"] for r in rows)/len(rows),"by_category":{cat:{"correct":sum(r["passed"] for r in rows if r["category"]==cat),"total":sum(r["category"]==cat for r in rows)} for cat in sorted({r["category"] for r in rows})}} for c,rows in outputs.items()}
        if len(conditions)==2:
            a={r["task_id"]:r["passed"] for r in outputs[conditions[0]]}; b={r["task_id"]:r["passed"] for r in outputs[conditions[1]]}
            payload["paired"]={"base_only":sum(a[k] and not b[k] for k in a),"adapted_only":sum(b[k] and not a[k] for k in a),"both":sum(a[k] and b[k] for k in a),"neither":sum(not a[k] and not b[k] for k in a),"accuracy_difference":sum(b.values())/len(b)-sum(a.values())/len(a)}
    else:
        payload["summaries"]={c:summarize(rows) for c,rows in outputs.items()}
        if args.plan=="primary": payload["paired_comparison"]=paired_comparison(outputs["BASE_NO_DOCS"],outputs["ADAPTED_NO_DOCS"],bootstrap_seed=config["evaluation"]["bootstrap_seed"],bootstrap_samples=config["evaluation"]["bootstrap_samples"])
    args.output.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"plan":args.plan,"hardware":payload["hardware"],"summaries":payload["summaries"],"paired":payload.get("paired_comparison",payload.get("paired"))},indent=2))


if __name__=="__main__":
    main()
