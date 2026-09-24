"""Freeze DEV2 reference, primitive, API, structural and token audits; no model use."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from self_learning_ai.benchmark import score_source
from self_learning_ai.compiler import GocoCompiler
from validate_phase2b_data import jaccard, normalized_code
from build_phase3c_dev2_data import PREDICATES

ROOT=Path(__file__).resolve().parents[1]
FILES={c:(f"data/phase3c_dev2/a_{c}_training_examples.json",f"data/phase3c_dev2/a_{c}_training_references.json",f"data/phase3c_dev2/a_{c}_training_hidden_tests.json") for c in ("isolated","composition")}
FILES["eval"]=("benchmark/phase3c_dev2/a_development_eval_tasks.json","benchmark/phase3c_dev2/a_development_eval_references.json","benchmark/phase3c_dev2/a_development_eval_hidden_tests.json")
HISTORY=(("benchmark/phase3a/a_eval_tasks.json","benchmark/phase3a/a_eval_references.json"),
         ("benchmark/phase3b/a_eval_tasks.json","benchmark/phase3b/a_eval_references.json"),
         ("benchmark/phase3c/a_eval_tasks.json","benchmark/phase3c/a_eval_references.json"),
         ("benchmark/phase3c_dev1/a_development_eval_tasks.json","benchmark/phase3c_dev1/a_development_eval_references.json"))


def read(rel): return json.loads((ROOT/rel).read_text(encoding="utf-8"))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,default=ROOT/"research/results/PHASE_3C_DEV2")
    args=parser.parse_args()
    out=args.output_dir
    if out.exists() and any(out.iterdir()): raise FileExistsError(out)
    compiler_path=ROOT/".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar"
    java_path=ROOT/".tools/jdk-25.0.1+8/bin/java.exe"
    config=read("research/protocols/phase3c_config.json")
    assert sha(compiler_path)==config["compiler_sha256"]
    compiler=GocoCompiler(java_path,compiler_path,timeout_seconds=3,output_limit_bytes=65536)
    data={c:tuple(read(p) for p in paths) for c,paths in FILES.items()}
    file_hashes={p:sha(ROOT/p) for paths in FILES.values() for p in paths}
    assert all(len(data[c][0])==60 for c in ("isolated","composition")) and len(data["eval"][0])==48
    for c,(rows,refs,tests) in data.items():
        id_key="task_id" if c=="eval" else "example_id"
        ids=[r[id_key] for r in rows]
        assert len(ids)==len(set(ids)) and set(ids)==set(refs)==set(tests)
        assert Counter(r["family"] for r in rows)=={"numeric_iteration":len(rows)//2,"array_reduction":len(rows)//2}
        assert all(len(tests[x])==5 for x in ids)
        if c!="eval": assert all(r["target"]==refs[r[id_key]] for r in rows)
    assert Counter(r["development_group"] for r in data["eval"][0])=={"primitive_sanity":16,"novel_composition":16,"structural_transfer":16}
    prior_prompt=set();prior_refs=set()
    for tasks,refs in HISTORY:
        prior_prompt.update(r["prompt"] for r in read(tasks));prior_refs.update(read(refs).values())
    all_rows=[r for rows,_,_ in data.values() for r in rows]
    all_refs=[v for _,refs,_ in data.values() for v in refs.values()]
    eval_prompts={r["prompt"] for r in data["eval"][0]};eval_refs=set(data["eval"][1].values())
    separation={"prior_prompt_exact":sum(r["prompt"] in prior_prompt for r in all_rows),
                "prior_reference_exact":sum(v in prior_refs for v in all_refs),
                "train_eval_prompt_exact":sum(r["prompt"] in eval_prompts for c in ("isolated","composition") for r in data[c][0]),
                "train_eval_reference_exact":sum(v in eval_refs for c in ("isolated","composition") for v in data[c][1].values())}
    assert all(v==0 for v in separation.values()),separation

    primitive_rows=[];api_rows=[]
    api_patterns={"IMPORT_strings":"IMPORT strings.","SPLIT":"strings.SPLIT", "TO_NUMBER":"strings.TO_NUMBER",
                  "array_index":"values[", "IF":"IF (", "LOOP":"LOOP (", "descending_loop":"i-=1.",
                  "nested_IF":"{ IF ("}
    for family,primitive_map in PREDICATES.items():
        for primitive,(expression,_,_) in primitive_map.items():
            row={"subskill":family,"primitive":primitive,"conditions":{}}
            for c in ("isolated","composition"):
                members=[r for r in data[c][0] if r["family"]==family and primitive in r["semantic_primitives"]]
                actual=sum(data[c][1][r["example_id"]].count(expression) for r in members)
                row["conditions"][c]={"examples_containing":len(members),"reference_occurrences":actual,
                                       "archetypes":sorted({r["archetype"] for r in members}),
                                       "associated_api":["IMPORT strings","strings.SPLIT","strings.TO_NUMBER","array_index","IF","LOOP"] if family=="array_reduction" else ["IF","LOOP"]}
            assert row["conditions"]["isolated"]["examples_containing"]==row["conditions"]["composition"]["examples_containing"]==15
            assert row["conditions"]["isolated"]["reference_occurrences"]==row["conditions"]["composition"]["reference_occurrences"]
            primitive_rows.append(row)
    for name,needle in api_patterns.items():
        counts={c:sum(source.count(needle) for source in data[c][1].values()) for c in ("isolated","composition")}
        assert counts["isolated"]==counts["composition"],(name,counts)
        api_rows.append({"construct":name,"literal_proxy":needle,"reference_occurrences":counts})
    covered={c:{p for r in data[c][0] for p in r["semantic_primitives"]} for c in ("isolated","composition")}
    assert covered["isolated"]==covered["composition"]==set().union(*(set(x) for x in PREDICATES.values()))
    train_signatures={c:{r["composition_signature"] for r in data[c][0]} for c in ("isolated","composition")}
    central=[]
    for task in data["eval"][0]:
        if task["development_group"] not in ("novel_composition","structural_transfer"): continue
        primitives=set(task["semantic_primitives"])
        row={"task_id":task["task_id"],"group":task["development_group"],"required_primitives":sorted(primitives),
             "missing_in_isolated":sorted(primitives-covered["isolated"]),"missing_in_composition":sorted(primitives-covered["composition"]),
             "exact_composition_in_isolated":task["composition_signature"] in train_signatures["isolated"],
             "exact_composition_in_composition":task["composition_signature"] in train_signatures["composition"]}
        assert not row["missing_in_isolated"] and not row["missing_in_composition"]
        if task["development_group"]=="novel_composition":
            assert not row["exact_composition_in_isolated"] and not row["exact_composition_in_composition"]
        central.append(row)
    validation={}
    for c,(rows,refs,tests) in data.items():
        id_key="task_id" if c=="eval" else "example_id"
        outcomes=[]
        for r in rows:
            ident=r[id_key]
            score=score_source(compiler,{"task_id":ident,"family":r["family"],"difficulty":"development_reference","required_regex":[]},tests[ident],refs[ident]).as_dict()
            outcomes.append({"id":ident,"parse_success":score["parse_success"],"compile_success":score["compile_success"],
                             "execution_success":score["execution_success"],"hidden_pass":score["hidden_pass"],
                             "cases_passed":score["cases_passed"],"cases_total":score["cases_total"],
                             "error_phase":score["error_phase"],
                             "first_case_stderr":score["case_results"][0]["stderr"]})
        validation[c]={"references":len(outcomes),"cases":sum(x["cases_total"] for x in outcomes),
                       "passed":sum(x["hidden_pass"] for x in outcomes),"rows":outcomes}
        print(c,validation[c]["passed"],"/",len(outcomes),flush=True)
    if any(v["passed"]!=v["references"] for v in validation.values()):
        raise ValueError("Reference semantic validation failed; fix before freeze")
    pairs=[];nearest=[]
    for task in data["eval"][0]:
        tid=task["task_id"]
        entry={"task_id":tid,"group":task["development_group"],"subskill":task["family"],
               "required_primitives":task["semantic_primitives"],"composition_signature":task["composition_signature"],
               "control_flow":task["control_flow"],"goco_api":["IMPORT strings","strings.SPLIT","strings.TO_NUMBER","array_index","IF","LOOP"] if task["family"]=="array_reduction" else ["IF","LOOP"],
               "conditions":{}}
        for c in ("isolated","composition"):
            local=[]
            for tr in data[c][0]:
                eid=tr["example_id"]
                p={"task_id":tid,"condition":c,"train_id":eid,"train_archetype":tr["archetype"],
                   "prompt_jaccard":jaccard(task["prompt"],tr["prompt"]),
                   "normalized_reference_code_similarity":difflib.SequenceMatcher(None,normalized_code(data["eval"][1][tid]),normalized_code(data[c][1][eid])).ratio(),
                   "ast_proxy_exact":task["ast_proxy_signature"]==tr["ast_proxy_signature"],
                   "exact_prompt":task["prompt"]==tr["prompt"],"exact_reference":data["eval"][1][tid]==data[c][1][eid]}
                local.append(p)
            pairs.extend(local)
            best_code=max(local,key=lambda x:(x["normalized_reference_code_similarity"],x["train_id"]))
            best_prompt=max(local,key=lambda x:(x["prompt_jaccard"],x["train_id"]))
            entry["conditions"][c]={"nearest_code_id":best_code["train_id"],"nearest_code_archetype":best_code["train_archetype"],
                                    "nearest_code_similarity":best_code["normalized_reference_code_similarity"],
                                    "nearest_prompt_id":best_prompt["train_id"],"nearest_prompt_jaccard":best_prompt["prompt_jaccard"],
                                    "ast_proxy_exact_pair_count":sum(x["ast_proxy_exact"] for x in local),
                                    "code_pairs_at_least_0p70":sum(x["normalized_reference_code_similarity"]>=.70 for x in local),
                                    "code_pairs_at_least_0p85":sum(x["normalized_reference_code_similarity"]>=.85 for x in local),
                                    "code_pairs_at_least_0p95":sum(x["normalized_reference_code_similarity"]>=.95 for x in local),
                                    "code_pairs_at_least_0p98":sum(x["normalized_reference_code_similarity"]>=.98 for x in local),
                                    "primitive_coverage":{p:p in covered[c] for p in task["semantic_primitives"]},
                                    "exact_composition_in_training":task["composition_signature"] in train_signatures[c]}
        nearest.append(entry)
    assert len(pairs)==48*60*2
    assert not any(x["exact_prompt"] or x["exact_reference"] for x in pairs)
    audit={"phase":"3C-DEV2","status":"PRE_GRADIENT_REFERENCE_AND_STRUCTURE_AUDIT",
           "compiler_sha256":sha(compiler_path),"input_sha256":file_hashes,"historical_exact_reuse":separation,
           "prospective_matching_tolerance":{"primitive_presence":"exact","primitive_example_frequency":"exact",
                 "primitive_reference_occurrence":"exact","api_construct_occurrence":"exact",
                 "subskill_counts":"30 per condition per subskill"},
           "primitive_frequency":primitive_rows,"api_syntax_frequency":api_rows,
           "central_coverage_proof":central,"reference_validation":validation,"structural_nearest":nearest,
           "structural_pair_count":len(pairs),
           "similarity_interpretation":"Prompt Jaccard, normalized reference SequenceMatcher, and coarse AST proxy are descriptive. All pairs, including those below 0.98, are published. No distance independence is established by a single threshold."}
    out.mkdir(parents=True,exist_ok=True)
    (out/"pre_gradient_audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8")
    (out/"structural_pairs.json").write_text(json.dumps(pairs,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"references":sum(x["references"] for x in validation.values()),
                      "semantic_cases":sum(x["cases"] for x in validation.values()),
                      "structural_pairs":len(pairs),"central_tasks_covered":len(central)}))


if __name__=="__main__": main()
