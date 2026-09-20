from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Any

import bitsandbytes as bnb
import peft
import psutil
import torch
import transformers
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, get_linear_schedule_with_warmup


def sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""):
            digest.update(chunk)
    return digest.hexdigest()


class RssMonitor(threading.Thread):
    def __init__(self)->None:
        super().__init__(daemon=True); self.stop_event=threading.Event(); self.peak=0
    def run(self)->None:
        process=psutil.Process(os.getpid())
        while not self.stop_event.wait(.05):
            self.peak=max(self.peak,process.memory_info().rss)
    def stop(self)->int:
        self.stop_event.set(); self.join(timeout=2); return self.peak


class TokenDataset(Dataset[dict[str,list[int]]]):
    def __init__(self, rows:list[dict[str,Any]], tokenizer:Any, system:str, max_length:int)->None:
        self.items=[]
        for row in rows:
            user=f"Task {row['example_id']}\n\n{row['prompt']}"
            prompt_text=tokenizer.apply_chat_template(
                [{"role":"system","content":system},{"role":"user","content":user}],
                tokenize=False,add_generation_prompt=True,
            )
            full_text=tokenizer.apply_chat_template(
                [{"role":"system","content":system},{"role":"user","content":user},{"role":"assistant","content":row["target"]}],
                tokenize=False,add_generation_prompt=False,
            )
            prompt_ids=tokenizer(prompt_text,add_special_tokens=False)["input_ids"]
            full_ids=tokenizer(full_text,add_special_tokens=False)["input_ids"]
            if full_ids[:len(prompt_ids)]!=prompt_ids:
                raise ValueError(f"Chat-template prefix mismatch: {row['example_id']}")
            if len(full_ids)>max_length:
                raise ValueError(f"Frozen max length exceeded: {row['example_id']}={len(full_ids)}")
            labels=[-100]*len(prompt_ids)+full_ids[len(prompt_ids):]
            self.items.append({"input_ids":full_ids,"labels":labels})
    def __len__(self)->int: return len(self.items)
    def __getitem__(self,index:int)->dict[str,list[int]]: return self.items[index]


def collator(pad_id:int):
    def collate(rows:list[dict[str,list[int]]])->dict[str,torch.Tensor]:
        width=max(len(row["input_ids"]) for row in rows)
        ids=[]; labels=[]; masks=[]
        for row in rows:
            padding=width-len(row["input_ids"])
            ids.append(row["input_ids"]+[pad_id]*padding)
            labels.append(row["labels"]+[-100]*padding)
            masks.append([1]*len(row["input_ids"])+[0]*padding)
        return {"input_ids":torch.tensor(ids,dtype=torch.long),"labels":torch.tensor(labels,dtype=torch.long),"attention_mask":torch.tensor(masks,dtype=torch.long)}
    return collate


def directory_hashes(directory:Path)->dict[str,str]:
    return {str(path.relative_to(directory)).replace("\\","/"):sha256(path) for path in sorted(directory.rglob("*")) if path.is_file()}


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",type=Path,required=True)
    parser.add_argument("--mode",choices=["smoke","train"],required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--adapter-output",type=Path)
    args=parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    if args.mode=="train" and args.adapter_output is None: raise ValueError("--adapter-output is required for train")
    if args.adapter_output and args.adapter_output.exists(): raise FileExistsError(args.adapter_output)

    config=json.loads(args.config.read_text(encoding="utf-8"))
    for raw,expected in config["input_file_hashes"].items():
        actual=sha256(Path(raw))
        if actual!=expected: raise ValueError(f"Frozen input hash mismatch {raw}: {actual}")
    model_cfg=config["model"]
    model_path=Path(model_cfg["local_path"])
    base_hashes={name:sha256(model_path/name) for name in model_cfg["weight_file_sha256"]}
    if base_hashes!=model_cfg["weight_file_sha256"]: raise ValueError("Base weight hash mismatch")
    rows=json.loads(Path(config["data"]["training_examples"]).read_text(encoding="utf-8"))
    if args.mode=="smoke":
        chosen=[]; counts=Counter()
        for row in rows:
            if counts[row["family"]]<2: chosen.append(row); counts[row["family"]]+=1
        rows=chosen

    seed=config["seed"]
    random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    monitor=RssMonitor(); monitor.start()
    started=time.perf_counter()
    tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
    tokenizer.pad_token=tokenizer.eos_token; tokenizer.padding_side="right"
    dataset=TokenDataset(rows,tokenizer,Path(config["prompt"]["system"]).read_text(encoding="utf-8").strip(),config["training"]["max_length"])
    quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_compute_dtype=torch.float16,bnb_4bit_use_double_quant=True)
    model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,quantization_config=quant,device_map={"":0},dtype=torch.float16)
    model.config.use_cache=False
    model=prepare_model_for_kbit_training(model,use_gradient_checkpointing=True,gradient_checkpointing_kwargs={"use_reentrant":False})
    lora=config["training"]["lora"]
    model=get_peft_model(model,LoraConfig(r=lora["rank"],lora_alpha=lora["alpha"],lora_dropout=lora["dropout"],bias="none",task_type="CAUSAL_LM",target_modules=lora["target_modules"]))
    trainable=sum(p.numel() for p in model.parameters() if p.requires_grad); total=sum(p.numel() for p in model.parameters())
    if trainable<=0: raise RuntimeError("No trainable adapter parameters")
    load_seconds=time.perf_counter()-started
    torch.cuda.reset_peak_memory_stats()

    epochs=1 if args.mode=="smoke" else config["training"]["epochs"]
    accumulation=config["training"]["gradient_accumulation_steps"]
    generator=torch.Generator().manual_seed(seed)
    loader=DataLoader(dataset,batch_size=1,shuffle=True,generator=generator,collate_fn=collator(tokenizer.pad_token_id))
    steps_per_epoch=math.ceil(len(loader)/accumulation); total_steps=steps_per_epoch*epochs
    optimizer=bnb.optim.PagedAdamW8bit((p for p in model.parameters() if p.requires_grad),lr=config["training"]["learning_rate"],betas=tuple(config["training"]["adam_betas"]),eps=config["training"]["adam_epsilon"],weight_decay=config["training"]["weight_decay"])
    scheduler=get_linear_schedule_with_warmup(optimizer,num_warmup_steps=min(config["training"]["warmup_steps"],max(0,total_steps-1)),num_training_steps=total_steps)
    model.train(); optimizer.zero_grad(set_to_none=True)
    log=[]; optimizer_step=0; token_count=0; train_started=time.perf_counter(); running_loss=0.0; running_micro=0
    for epoch in range(epochs):
        for micro_index,batch in enumerate(loader,1):
            batch={key:value.to("cuda:0") for key,value in batch.items()}
            supervised=int((batch["labels"]!=-100).sum().item()); token_count+=supervised
            output=model(**batch); raw_loss=output.loss
            if not torch.isfinite(raw_loss): raise FloatingPointError(f"Non-finite loss at epoch {epoch+1} micro {micro_index}")
            (raw_loss/accumulation).backward(); running_loss+=float(raw_loss.detach()); running_micro+=1
            boundary=micro_index%accumulation==0 or micro_index==len(loader)
            if boundary:
                grad_norm=float(torch.nn.utils.clip_grad_norm_((p for p in model.parameters() if p.requires_grad),config["training"]["max_grad_norm"]))
                optimizer.step(); scheduler.step(); optimizer.zero_grad(set_to_none=True); optimizer_step+=1
                log.append({"optimizer_step":optimizer_step,"epoch":epoch+1,"mean_micro_loss":running_loss/running_micro,"learning_rate":scheduler.get_last_lr()[0],"grad_norm":grad_norm,"elapsed_seconds":time.perf_counter()-train_started,"gpu_allocated_bytes":int(torch.cuda.memory_allocated()),"gpu_reserved_bytes":int(torch.cuda.memory_reserved())})
                running_loss=0.0; running_micro=0
    train_seconds=time.perf_counter()-train_started
    peak_rss=monitor.stop()
    peak_alloc=int(torch.cuda.max_memory_allocated()); peak_reserved=int(torch.cuda.max_memory_reserved())
    if optimizer_step!=total_steps: raise RuntimeError((optimizer_step,total_steps))

    adapter_hashes={}
    if args.mode=="train":
        assert args.adapter_output is not None
        args.adapter_output.parent.mkdir(parents=True,exist_ok=True)
        model.save_pretrained(args.adapter_output,safe_serialization=True)
        tokenizer.save_pretrained(args.adapter_output)
        adapter_hashes=directory_hashes(args.adapter_output)
    base_hashes_after={name:sha256(model_path/name) for name in model_cfg["weight_file_sha256"]}
    if base_hashes_after!=base_hashes: raise RuntimeError("Immutable base weights changed")
    result={
        "phase":"2A","mode":args.mode,"config_sha256":sha256(args.config),"seed":seed,
        "environment":{"platform":platform.platform(),"python":platform.python_version(),"torch":torch.__version__,"transformers":transformers.__version__,"bitsandbytes":bnb.__version__,"peft":peft.__version__,"cuda_runtime":torch.version.cuda,"gpu":torch.cuda.get_device_name(0)},
        "model":{"id":model_cfg["id"],"revision":model_cfg["revision"],"base_weight_hashes_before":base_hashes,"base_weight_hashes_after":base_hashes_after,"trainable_parameters":trainable,"total_parameters_loaded":total},
        "data":{"examples":len(rows),"family_counts":dict(sorted(Counter(row["family"] for row in rows).items())),"supervised_tokens":token_count},
        "training":{"epochs":epochs,"optimizer_steps":optimizer_step,"expected_optimizer_steps":total_steps,"load_seconds":load_seconds,"training_seconds":train_seconds,"supervised_tokens_per_second":token_count/train_seconds,"peak_gpu_allocated_bytes":peak_alloc,"peak_gpu_reserved_bytes":peak_reserved,"peak_process_rss_bytes":peak_rss,"log":log},
        "adapter":{"saved":args.mode=="train","path":str(args.adapter_output).replace("\\","/") if args.adapter_output else None,"file_hashes":adapter_hashes},
        "stability":{"all_losses_finite":all(math.isfinite(row["mean_micro_loss"]) for row in log),"completed":True},
    }
    if args.mode=="smoke":
        smoke=config["smoke_gate"]
        result["smoke_gate"]={"max_allocated_bytes":smoke["max_allocated_bytes"],"max_process_rss_bytes":smoke["max_process_rss_bytes"],"passed":peak_alloc<=smoke["max_allocated_bytes"] and peak_rss<=smoke["max_process_rss_bytes"] and result["stability"]["all_losses_finite"]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"mode":args.mode,"optimizer_steps":optimizer_step,"first_loss":log[0]["mean_micro_loss"],"last_loss":log[-1]["mean_micro_loss"],"peak_gpu_allocated_bytes":peak_alloc,"peak_gpu_reserved_bytes":peak_reserved,"peak_process_rss_bytes":peak_rss,"tokens_per_second":token_count/train_seconds,"smoke_gate":result.get("smoke_gate"),"adapter_hashes":adapter_hashes},indent=2))


if __name__=="__main__":
    main()
