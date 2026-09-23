from __future__ import annotations

import argparse
import json
import math
import platform
import random
import time
from pathlib import Path

import bitsandbytes as bnb
import peft
import torch
import transformers
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, get_linear_schedule_with_warmup

from train_phase2a_qlora import RssMonitor, TokenDataset, collator, directory_hashes, sha256


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",type=Path,required=True); parser.add_argument("--seed",type=int,required=True)
    parser.add_argument("--stage",choices=["A","B"],required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    cfg=json.loads(args.config.read_text(encoding="utf-8"))
    if args.seed not in cfg["seeds"]: raise ValueError("Unregistered seed")
    for raw,expected in cfg["input_file_hashes"].items():
        if sha256(Path(raw))!=expected: raise ValueError(f"Frozen input hash mismatch: {raw}")
    model_cfg=cfg["model"]; model_path=Path(model_cfg["local_path"])
    base_before={name:sha256(model_path/name) for name in model_cfg["weight_file_sha256"]}
    if base_before!=model_cfg["weight_file_sha256"]: raise ValueError("Base hash mismatch")
    adapter_path=Path(cfg["training"]["adapter_outputs"][str(args.seed)][args.stage])
    if adapter_path.exists(): raise FileExistsError(adapter_path)
    parent_path=Path(cfg["training"]["adapter_outputs"][str(args.seed)]["A"]) if args.stage=="B" else None
    if parent_path and not parent_path.is_dir(): raise FileNotFoundError(parent_path)
    parent_hashes=directory_hashes(parent_path) if parent_path else None
    if parent_path:
        parent_record=Path(cfg["training"]["record_outputs"][str(args.seed)]["A"])
        parent=json.loads(parent_record.read_text(encoding="utf-8"))
        if parent["adapter"]["file_hashes"]!=parent_hashes: raise ValueError("A parent adapter changed")
    rows=json.loads(Path(cfg["data"][f"{args.stage.lower()}_training_examples"]).read_text(encoding="utf-8"))
    if len(rows)!=60 or any(r["capability"]!=args.stage for r in rows): raise ValueError("Wrong stage data")
    random.seed(args.seed); torch.manual_seed(args.seed); torch.cuda.manual_seed_all(args.seed)
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    monitor=RssMonitor(); monitor.start(); started=time.perf_counter()
    tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
    tokenizer.pad_token=tokenizer.eos_token; tokenizer.padding_side="right"
    train=cfg["training"]
    dataset=TokenDataset(rows,tokenizer,Path(cfg["prompt"]["system"]).read_text(encoding="utf-8").strip(),train["max_length"])
    quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_compute_dtype=torch.float16,bnb_4bit_use_double_quant=True)
    model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,quantization_config=quant,device_map={"":0},dtype=torch.float16)
    model.config.use_cache=False
    model=prepare_model_for_kbit_training(model,use_gradient_checkpointing=True,gradient_checkpointing_kwargs={"use_reentrant":False})
    if parent_path:
        model=PeftModel.from_pretrained(model,parent_path,is_trainable=True)
    else:
        lora=train["lora"]
        model=get_peft_model(model,LoraConfig(r=lora["rank"],lora_alpha=lora["alpha"],lora_dropout=lora["dropout"],bias=lora["bias"],task_type="CAUSAL_LM",target_modules=lora["target_modules"]))
    trainable=sum(p.numel() for p in model.parameters() if p.requires_grad)
    if trainable<=0: raise RuntimeError("No trainable adapter parameters")
    load_seconds=time.perf_counter()-started; torch.cuda.reset_peak_memory_stats()
    loader=DataLoader(dataset,batch_size=train["micro_batch_size"],shuffle=True,generator=torch.Generator().manual_seed(args.seed),collate_fn=collator(tokenizer.pad_token_id))
    accumulation=train["gradient_accumulation_steps"]
    total_steps=math.ceil(len(loader)/accumulation)*train["epochs"]
    optimizer=bnb.optim.PagedAdamW8bit((p for p in model.parameters() if p.requires_grad),lr=train["learning_rate"],betas=tuple(train["adam_betas"]),eps=train["adam_epsilon"],weight_decay=train["weight_decay"])
    scheduler=get_linear_schedule_with_warmup(optimizer,num_warmup_steps=min(train["warmup_steps"],max(0,total_steps-1)),num_training_steps=total_steps)
    model.train(); optimizer.zero_grad(set_to_none=True)
    log=[]; token_count=0; step=0; train_started=time.perf_counter()
    for epoch in range(train["epochs"]):
        running_loss=0.0; running_micro=0
        for micro,batch in enumerate(loader,1):
            batch={k:v.to("cuda:0") for k,v in batch.items()}
            token_count+=int((batch["labels"]!=-100).sum().item())
            loss=model(**batch).loss
            if not torch.isfinite(loss): raise FloatingPointError((epoch,micro,"loss"))
            (loss/accumulation).backward(); running_loss+=float(loss.detach()); running_micro+=1
            if micro%accumulation==0 or micro==len(loader):
                grad=float(torch.nn.utils.clip_grad_norm_((p for p in model.parameters() if p.requires_grad),train["max_grad_norm"]))
                if not math.isfinite(grad): raise FloatingPointError((epoch,micro,"gradient"))
                optimizer.step(); scheduler.step(); optimizer.zero_grad(set_to_none=True); step+=1
                log.append({"optimizer_step":step,"epoch":epoch+1,"mean_micro_loss":running_loss/running_micro,"grad_norm":grad,"learning_rate":scheduler.get_last_lr()[0],"elapsed_seconds":time.perf_counter()-train_started})
                running_loss=0.0; running_micro=0
    training_seconds=time.perf_counter()-train_started
    if step!=total_steps: raise RuntimeError((step,total_steps))
    adapter_path.parent.mkdir(parents=True,exist_ok=True)
    model.save_pretrained(adapter_path,safe_serialization=True); tokenizer.save_pretrained(adapter_path)
    adapter_hashes=directory_hashes(adapter_path)
    base_after={name:sha256(model_path/name) for name in model_cfg["weight_file_sha256"]}
    if base_after!=base_before: raise RuntimeError("Base weights changed")
    if parent_path and directory_hashes(parent_path)!=parent_hashes: raise RuntimeError("Parent adapter changed")
    peak_rss=monitor.stop()
    result={"phase":"3A","stage":args.stage,"seed":args.seed,"config_sha256":sha256(args.config),"environment":{"platform":platform.platform(),"python":platform.python_version(),"torch":torch.__version__,"transformers":transformers.__version__,"bitsandbytes":bnb.__version__,"peft":peft.__version__,"cuda_runtime":torch.version.cuda,"gpu":torch.cuda.get_device_name(0)},"lineage":{"base_revision":model_cfg["revision"],"base_weight_hashes_before":base_before,"base_weight_hashes_after":base_after,"parent_adapter_path":str(parent_path).replace('\\','/') if parent_path else None,"parent_adapter_file_hashes":parent_hashes,"training_capability_only":args.stage,"replay_examples":0},"data":{"examples":len(rows),"supervised_tokens":token_count},"training":{"epochs":train["epochs"],"optimizer_steps":step,"expected_optimizer_steps":total_steps,"load_seconds":load_seconds,"training_seconds":training_seconds,"peak_gpu_allocated_bytes":int(torch.cuda.max_memory_allocated()),"peak_process_rss_bytes":peak_rss,"trainable_parameters":trainable,"log":log},"adapter":{"path":str(adapter_path).replace('\\','/'),"file_hashes":adapter_hashes}}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"seed":args.seed,"stage":args.stage,"steps":step,"first_loss":log[0]["mean_micro_loss"],"last_loss":log[-1]["mean_micro_loss"],"seconds":training_seconds,"adapter_sha256":adapter_hashes.get("adapter_model.safetensors")},indent=2))

if __name__=="__main__": main()
