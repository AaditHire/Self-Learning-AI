"""Count frozen DEV2 chat-template tokens; loads tokenizer files only."""

import hashlib
import json
from pathlib import Path

from transformers import AutoTokenizer

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"research/results/PHASE_3C_DEV2/token_budget_audit.json"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists(): raise FileExistsError(OUT)
    old=json.loads((ROOT/"research/protocols/phase3c_dev1_manifest.json").read_text(encoding="utf-8"))
    model=ROOT/old["base_weights"]["local_path"]
    for name,expected in old["tokenizer_file_sha256"].items():
        assert sha(model/name)==expected,(name,"tokenizer changed")
    tok=AutoTokenizer.from_pretrained(model,local_files_only=True)
    system=(ROOT/"prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    conditions={}
    for c in ("isolated","composition"):
        path=ROOT/f"data/phase3c_dev2/a_{c}_training_examples.json"
        rows=json.loads(path.read_text(encoding="utf-8"))
        lengths={}
        for r in rows:
            messages=[{"role":"system","content":system},{"role":"user","content":f"Task {r['example_id']}\n\n{r['prompt']}"}]
            p=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
            f=tok.apply_chat_template(messages+[{"role":"assistant","content":r["target"]}],tokenize=False,add_generation_prompt=False)
            pi=tok(p,add_special_tokens=False)["input_ids"]
            fi=tok(f,add_special_tokens=False)["input_ids"]
            assert fi[:len(pi)]==pi and len(fi)<=320,(r["example_id"],len(fi))
            lengths[r["example_id"]]={"full_tokens":len(fi),"supervised_tokens":len(fi)-len(pi)}
        conditions[c]={"examples":len(rows),"max_full_tokens":max(x["full_tokens"] for x in lengths.values()),
                       "one_epoch_full_tokens":sum(x["full_tokens"] for x in lengths.values()),
                       "one_epoch_supervised_tokens":sum(x["supervised_tokens"] for x in lengths.values()),
                       "by_example":lengths,"dataset_sha256":sha(path)}
    a,b=conditions["isolated"],conditions["composition"]
    full=abs(b["one_epoch_full_tokens"]-a["one_epoch_full_tokens"])/a["one_epoch_full_tokens"]
    supervised=abs(b["one_epoch_supervised_tokens"]-a["one_epoch_supervised_tokens"])/a["one_epoch_supervised_tokens"]
    result={"phase":"3C-DEV2","status":"PRE_GRADIENT_TOKEN_AUDIT","tokenizer_file_sha256":old["tokenizer_file_sha256"],
            "prompt_template_sha256":sha(ROOT/"prompts/phase1t_system.txt"),"max_length":320,"conditions":conditions,
            "full_token_relative_difference_from_isolated":full,
            "supervised_token_relative_difference_from_isolated":supervised,
            "prospective_materiality_threshold":.10,
            "compute_gate":"PASS" if max(full,supervised)<=.10 else "STOP_REDESIGN_BEFORE_GRADIENTS"}
    OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"isolated_full":a["one_epoch_full_tokens"],"composition_full":b["one_epoch_full_tokens"],
                      "full_difference":full,"supervised_difference":supervised,"gate":result["compute_gate"]}))

if __name__=="__main__": main()
