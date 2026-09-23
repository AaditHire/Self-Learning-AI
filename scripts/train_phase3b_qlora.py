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
    parser.add_argument("--config",type=Path,required=True)
    parser.add_argument("--seed",type=int,required=True)
    parser.add_argument("--condition",choices=["A","naive","replay"],required=True)
    args=parser.parse_args()
    cfg=json.loads(args.config.read_text(encoding="utf-8"))
    if args.seed not in cfg["seeds"]: raise ValueError("Unregistered seed")
    for raw,expected in cfg["input_file_hashes"].items():
        if sha256(Path(raw))!=expected: raise ValueError(f"Frozen input hash mismatch: {raw}")
    model_cfg=cfg["model"]; model_path=Path(model_cfg["local_path"])
    base_before={name:sha256(model_path/name) for name in model_cfg["weight_file_sha256"]}
    if base_before!=model_cfg["weight_file_sha256"]: raise ValueError("Base hash mismatch")
    root=Path(cfg["runtime_root"]); out_dir=root/"adapters"/str(args.seed)/args.condition
    record_path=root/"training"/str(args.seed)/f"{args.condition}.json"
    if out_dir.exists() or record_path.exists(): raise FileExistsError(out_dir if out_dir.exists() else record_path)
    parent=root/"adapters"/str(args.seed)/"A" if args.condition!="A" else None
    parent_hashes=directory_hashes(parent) if parent else None
    if parent:
        if not parent.is_dir(): raise FileNotFoundError(parent)
        prior=json.loads((root/"training"/str(args.seed)/"A.json").read_text(encoding="utf-8"))
        if prior["adapter"]["file_hashes"]!=parent_hashes: raise ValueError("A adapter changed")
    a=json.loads(Path(cfg["data"]["a_training_examples"]).read_text(encoding="utf-8"))
    b=json.loads(Path(cfg["data"]["b_training_examples"]).read_text(encoding="utf-8"))
    if len(a)!=60 or len(b)!=60: raise ValueError("Training data size")
    by_id={r["example_id"]:r for r in a+b}
    if len(by_id)!=120: raise ValueError("Training ID collision")
    random.seed(args.seed); torch.manual_seed(args.seed); torch.cuda.manual_seed_all(args.seed)
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); monitor=RssMonitor(); monitor.start(); started=time.perf_counter()
    tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
    tokenizer.pad_token=tokenizer.eos_token; tokenizer.padding_side="right"
    train=cfg["training"]; system=Path(cfg["prompt"]["system"]).read_text(encoding="utf-8").strip()
    quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_compute_dtype=torch.float16,bnb_4bit_use_double_quant=True)
    model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,quantization_config=quant,device_map={"":0},dtype=torch.float16)
    model.config.use_cache=False
    model=prepare_model_for_kbit_training(model,use_gradient_checkpointing=True,gradient_checkpointing_kwargs={"use_reentrant":False})
    if parent: model=PeftModel.from_pretrained(model,parent,is_trainable=True)
    else:
        lora=train["lora"]
        model=get_peft_model(model,LoraConfig(r=lora["rank"],lora_alpha=lora["alpha"],lora_dropout=lora["dropout"],bias=lora["bias"],task_type="CAUSAL_LM",target_modules=lora["target_modules"]))
    trainable=sum(p.numel() for p in model.parameters() if p.requires_grad)
    if trainable<=0: raise RuntimeError("No trainable adapter parameters")
    load_seconds=time.perf_counter()-started; torch.cuda.reset_peak_memory_stats()
    if args.condition=="A":
        dataset=TokenDataset(a,tokenizer,system,train["max_length"])
        loader=DataLoader(dataset,batch_size=1,shuffle=True,generator=torch.Generator().manual_seed(args.seed),collate_fn=collator(tokenizer.pad_token_id))
        epoch_loaders=[loader]*train["epochs"]
        exposures=[[r["example_id"] for r in a] for _ in range(train["epochs"])]
    else:
        schedule=json.loads(Path(cfg["data"]["replay_schedule"]).read_text(encoding="utf-8"))["by_seed"][str(args.seed)]
        key=f"{args.condition}_example_ids"
        exposures=[e[key] for e in schedule]
        if len(exposures)!=train["epochs"] or any(len(x)!=60 for x in exposures): raise ValueError("Schedule size")
        for epoch_ids in exposures:
            counts={cap:sum(by_id[x]["capability"]==cap for x in epoch_ids) for cap in "AB"}
            if counts!={"A":0 if args.condition=="naive" else 12,"B":60 if args.condition=="naive" else 48}: raise ValueError((args.condition,counts))
        epoch_loaders=[DataLoader(TokenDataset([by_id[x] for x in ids],tokenizer,system,train["max_length"]),batch_size=1,shuffle=False,collate_fn=collator(tokenizer.pad_token_id)) for ids in exposures]
    accumulation=train["gradient_accumulation_steps"]
    expected=math.ceil(60/accumulation)*train["epochs"]
    optimizer=bnb.optim.PagedAdamW8bit((p for p in model.parameters() if p.requires_grad),lr=train["learning_rate"],betas=tuple(train["adam_betas"]),eps=train["adam_epsilon"],weight_decay=train["weight_decay"])
    scheduler=get_linear_schedule_with_warmup(optimizer,num_warmup_steps=min(train["warmup_steps"],max(0,expected-1)),num_training_steps=expected)
    model.train(); optimizer.zero_grad(set_to_none=True)
    log=[]; token_count=0; step=0; train_started=time.perf_counter()
    for epoch,epoch_loader in enumerate(epoch_loaders,1):
        running_loss=0.0; running_micro=0
        for micro,batch in enumerate(epoch_loader,1):
            batch={k:v.to("cuda:0") for k,v in batch.items()}
            token_count+=int((batch["labels"]!=-100).sum().item())
            loss=model(**batch).loss
            if not torch.isfinite(loss): raise FloatingPointError((epoch,micro,"loss"))
            (loss/accumulation).backward(); running_loss+=float(loss.detach()); running_micro+=1
            if micro%accumulation==0 or micro==len(epoch_loader):
                grad=float(torch.nn.utils.clip_grad_norm_((p for p in model.parameters() if p.requires_grad),train["max_grad_norm"]))
                if not math.isfinite(grad): raise FloatingPointError((epoch,micro,"gradient"))
                optimizer.step(); scheduler.step(); optimizer.zero_grad(set_to_none=True); step+=1
                log.append({"optimizer_step":step,"epoch":epoch,"mean_micro_loss":running_loss/running_micro,"grad_norm":grad,"learning_rate":scheduler.get_last_lr()[0],"elapsed_seconds":time.perf_counter()-train_started})
                running_loss=0.0; running_micro=0
    training_seconds=time.perf_counter()-train_started
    if step!=expected: raise RuntimeError((step,expected))
    out_dir.parent.mkdir(parents=True,exist_ok=True)
    model.save_pretrained(out_dir,safe_serialization=True); tokenizer.save_pretrained(out_dir)
    adapter_hashes=directory_hashes(out_dir)
    base_after={name:sha256(model_path/name) for name in model_cfg["weight_file_sha256"]}
    if base_after!=base_before or (parent and directory_hashes(parent)!=parent_hashes): raise RuntimeError("Weights changed unexpectedly")
    peak_rss=monitor.stop()
    record={"phase":"3B","condition":args.condition,"seed":args.seed,"config_sha256":sha256(args.config),"environment":{"platform":platform.platform(),"python":platform.python_version(),"torch":torch.__version__,"transformers":transformers.__version__,"bitsandbytes":bnb.__version__,"peft":peft.__version__,"cuda_runtime":torch.version.cuda,"gpu":torch.cuda.get_device_name(0)},"lineage":{"base_revision":model_cfg["revision"],"base_weight_hashes_before":base_before,"base_weight_hashes_after":base_after,"parent_adapter_path":str(parent).replace('\\','/') if parent else None,"parent_adapter_file_hashes":parent_hashes,"exposures_by_epoch":exposures},"data":{"examples_per_epoch":60,"a_examples_per_epoch":0 if args.condition=="naive" else 12 if args.condition=="replay" else 60,"b_examples_per_epoch":60 if args.condition=="naive" else 48 if args.condition=="replay" else 0,"supervised_tokens":token_count},"training":{"epochs":train["epochs"],"optimizer_steps":step,"expected_optimizer_steps":expected,"load_seconds":load_seconds,"training_seconds":training_seconds,"peak_gpu_allocated_bytes":int(torch.cuda.max_memory_allocated()),"peak_process_rss_bytes":peak_rss,"trainable_parameters":trainable,"log":log},"adapter":{"path":str(out_dir).replace('\\','/'),"file_hashes":adapter_hashes}}
    record_path.parent.mkdir(parents=True,exist_ok=True); record_path.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"seed":args.seed,"condition":args.condition,"steps":step,"first_loss":log[0]["mean_micro_loss"],"last_loss":log[-1]["mean_micro_loss"],"seconds":training_seconds,"adapter_sha256":adapter_hashes.get("adapter_model.safetensors")},indent=2))


if __name__=="__main__": main()
