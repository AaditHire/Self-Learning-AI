"""F1 one-pass candidate freeze; no model imports or execution authorization."""
from __future__ import annotations

import ast
import copy
import ctypes
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import py_compile
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.conf1_r1 import analysis, execution, schedule
from self_learning_ai.compiler import GocoCompiler

START = "2da5b8523088a8238228b1d6fbb15f314cef9ba4"
PREFREEZE = "2f59b59f372ccd6f54529415881c3e2940e7969cffbc31b418946204852c087a"
BASE = "research/results/PHASE_3C_CONF1_PREFREEZE/"
CANDIDATE = BASE + "attempt_004/"
FREEZE = BASE + "attempt_004_freeze/"
SCRIPT = "scripts/freeze_phase3c_conf1_candidate.py"
MANIFEST = CANDIDATE + "candidate_manifest.json"
EXPECTED = FREEZE + "expected_result_ids.json"
REPORT = FREEZE + "freeze_report.json"
FORBIDDEN_IMPORTS = {"torch", "transformers", "peft", "bitsandbytes", "accelerate"}
REFUSAL = "CONF1 model execution is not explicitly authorized"


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(value, reason):
    if not value:
        raise execution.GateStop(reason)


def git(*args):
    return subprocess.check_output(["git", "--no-optional-locks", *args], cwd=ROOT, text=True).rstrip("\r\n")


def read(name):
    return json.loads((ROOT / name).read_bytes())


def verify(manifest):
    for name, digest in manifest["file_sha256"].items():
        require(sha(ROOT / CANDIDATE / name) == digest, "payload hash mismatch: " + name)
    for name, digest in manifest["code_hashes"].items():
        require(sha(ROOT / name) == digest, "code hash mismatch: " + name)
    for name, info in manifest["authority_hashes"].items():
        require(sha(ROOT / name) == info["sha256"], "authority byte hash mismatch: " + name)
        if "verified_sha256" in info:
            raw = (ROOT / name).read_bytes()
            if info["verification"] == "LF-normalized":
                raw = raw.replace(b"\r\n", b"\n")
            require(hashlib.sha256(raw).hexdigest() == info["verified_sha256"], "authority verification mismatch: " + name)
    require(execution.execution_bound_files() <= (manifest["code_hashes"].keys() | manifest["authority_hashes"].keys()),
            "missing execution bindings")
    require(sha(ROOT / ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar") == manifest["compiler_sha256"], "compiler hash")
    model = ROOT / ".models/Qwen2.5-Coder-3B-Instruct-488639f"
    for name, digest in manifest["tokenizer_hashes"].items():
        require(sha(model / name) == digest, "tokenizer hash: " + name)


def source(name, needle):
    lines = (ROOT / name).read_text(encoding="utf-8").splitlines()
    matches = [i for i, line in enumerate(lines, 1) if needle in line]
    require(bool(matches), "missing generation source: " + needle)
    return name + ":" + str(matches[0])


def main():
    started = time.perf_counter()
    require(git("branch", "--show-current") == "main" and git("rev-parse", "HEAD") == START, "start branch/HEAD")
    # The newly written freeze script is the sole permitted pre-run addition.
    status = git("status", "--porcelain", "--untracked-files=all")
    require(status == "?? " + SCRIPT, "start scope must contain only the new freeze script")
    require(not execution.DEFAULT_RUNTIME.exists(), "CONF1 runtime exists")
    require(git("diff", "--name-only", "a456e9f", START, "--", "src", "tests", "scripts") ==
            "scripts/smoke_phase3c_conf1_infrastructure.py", "implementation start diff")
    require(sha(ROOT / MANIFEST) == PREFREEZE, "pre-freeze manifest hash")
    require(not (ROOT / FREEZE).exists(), "freeze directory already exists")
    original_bytes = (ROOT / MANIFEST).read_bytes()
    original = json.loads(original_bytes)
    require(original["status"] == "CANDIDATE_GATES_PASSED_NOT_FROZEN" and original["model_execution_authorized"] is False,
            "pre-freeze status/authorization")
    require(original["construction_seed"] == 20290123 and original["phase"] == "PHASE_3C_CONF1", "candidate identity")
    require(set(original["gate_summary"].values()) == {"PASS"}, "candidate gates")
    verify(original)
    cfg = read("research/protocols/phase3c_conf1_config_proposed.json")
    smoke = read(BASE + "infrastructure_smoke.json")
    tasks = read(CANDIDATE + "evaluation/tasks.json")
    gates = read(CANDIDATE + "gates/gate_report.json")
    examples = {}
    for condition in schedule.CONDITIONS:
        rows = read(CANDIDATE + f"training/{condition}_examples.json")
        require(len(rows) == 60 and {r["model_task_id"] for r in rows} == set(schedule.SLOT_IDS), "training population")
        examples[condition] = {r["model_task_id"]: dict(r, messages=execution.messages(r["model_task_id"], r["prompt"])) for r in rows}
    # _candidate's metadata enrichment and validation, without opening any cases.
    catalog = {t["task_id"]: t for t in schedule.EVALUATION_TASKS}
    tasks = [dict(t, **{k: v for k, v in catalog[t["task_id"]].items() if k not in t}) for t in tasks]
    analysis._catalog(tasks)
    order = schedule.confirmatory_order({g: [t["task_id"] for t in tasks if t["group"] == g] for g in schedule.GROUPS})
    cells = schedule.cell_order()
    paths = [f"training/{c['seed']}/{c['condition']}.json" for c in cells]
    own_count = confirm_count = 0
    for suite in ("training", "confirmatory"):
        for cell in cells:
            ids = schedule.own_training_order(examples[cell["condition"]]) if suite == "training" else order
            if suite == "training":
                own_count += len(ids)
            else:
                confirm_count += len(ids)
            for identifier in ids:
                stem = f"evaluations/{cell['seed']}/{cell['condition']}/{suite}/{identifier}"
                paths.extend([stem + ".raw.json", stem + ".score.json"])
    paths.extend(["acquisition_gate.json", "confirmatory_complete.json", "analysis.json", "output_inventory.json"])
    counts = {"cells": len(cells), "own_training_tasks": own_count, "confirmatory_tasks": confirm_count,
              "confirmatory_per_cell": len(order), "secondary_drops": original["counts"]["secondary_dropped"], "paths": len(paths)}
    require(counts == {"cells":10,"own_training_tasks":600,"confirmatory_tasks":640,"confirmatory_per_cell":64,"secondary_drops":0,"paths":2494}, "expected-result counts")
    expected = {"schema_version":"PHASE_3C_CONF1_EXPECTED_RESULT_IDS_1", "runtime_root":execution.DEFAULT_RUNTIME.relative_to(ROOT).as_posix(),
                "counts":counts, "ordered_paths":paths, "excluded_companions":[".started.json", ".sha256.json"],
                "scope":"Primary checkpoint files for a complete acquired execution; failed acquisition stops before confirmatory outputs."}
    expected_bytes = canonical(expected)
    added = ["research/protocols/phase3c_conf1_proposed_protocol.md",
             "research/protocols/phase3c_conf1_implementation_clarifications_c12_c14.md"]
    added += ["tests/test_conf1_r1_" + name + ".py" for name in
              ("primary", "interp", "gates_primary", "training", "overlap_secondary", "candidate", "schedule_analysis", "execution")]
    added += [SCRIPT, EXPECTED, BASE + "step4_synthetic_validation.json", BASE + "infrastructure_smoke.json"]
    if "scripts/build_phase3c_conf1_candidate.py" not in original["code_hashes"]:
        added.append("scripts/build_phase3c_conf1_candidate.py")
    frozen = copy.deepcopy(original)
    for name in added:
        require(name not in frozen["authority_hashes"], "existing authority entry must not change")
        digest = hashlib.sha256(expected_bytes).hexdigest() if name == EXPECTED else sha(ROOT / name)
        frozen["authority_hashes"][name] = {"sha256":digest, "verification":"byte-exact", "verified_sha256":digest}
    versions = {name:importlib.metadata.version(name) for name in
                ("torch","transformers","peft","bitsandbytes","accelerate","numpy","safetensors","tokenizers")}
    compiler = GocoCompiler(ROOT / cfg["compiler"]["java"], ROOT / cfg["compiler"]["path"])
    java = subprocess.run([str(compiler.java_executable), "-version"], capture_output=True, text=True, check=True)
    gpu_csv = subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"], text=True).strip()
    gpu_rows = [line.split(",") for line in gpu_csv.splitlines()]
    require(len(gpu_rows) == 1, "expected one GPU")
    gpu_name, driver, memory = [s.strip() for s in gpu_rows[0]]
    header = subprocess.check_output(["nvidia-smi"], text=True)
    cuda = __import__("re").search(r"(CUDA(?: UMD)? Version):\s*([\d.]+)", header)  # Driver-supported CUDA version; recorded only, not compared.
    require(cuda is not None, "missing nvidia-smi CUDA header")
    class MemoryStatus(ctypes.Structure):
        _fields_ = [("length",ctypes.c_ulong),("load",ctypes.c_ulong)] + [(n,ctypes.c_ulonglong) for n in
                    ("total_phys","avail_phys","total_page","avail_page","total_virtual","avail_virtual","avail_extended")]
    ram = MemoryStatus()
    ram.length = ctypes.sizeof(ram)
    require(bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ram))), "RAM query")
    environment = {"python":platform.python_version(),"executable":sys.executable,"packages":versions,
                   "java_executable":str(compiler.java_executable),"java_version":java.stdout + java.stderr,
                   "gpu":gpu_name,"driver":driver,"gpu_memory_total":memory,"nvidia_smi_query":gpu_csv,
                   "nvidia_smi_header":header,"cuda_header_label":cuda.group(1),"cuda_header_version":cuda.group(2),
                   "platform":platform.platform(),"processor":platform.processor(),"total_ram_bytes":ram.total_phys}
    comparisons = {n:{"current":versions[n],"smoke":smoke["environment"][n],"equal":versions[n]==smoke["environment"][n]}
                   for n in ("torch","transformers","peft","bitsandbytes")}
    comparisons["gpu"] = {"current":gpu_name,"smoke":smoke["environment"]["gpu"],"equal":gpu_name==smoke["environment"]["gpu"]}
    smoke_driver = smoke["environment"]["driver_query"].split(",",1)[0].strip()
    comparisons["driver"] = {"current":driver,"smoke":smoke_driver,"equal":driver==smoke_driver}
    require(all(v["equal"] for v in comparisons.values()), "smoke environment mismatch: " + json.dumps(comparisons))
    model = ROOT / cfg["base_weights"]["local_path"]
    model_names = {"config.json","generation_config.json","model.safetensors.index.json","model-00001-of-00002.safetensors",
                   "model-00002-of-00002.safetensors","merges.txt","vocab.json","tokenizer.json","tokenizer_config.json","LICENSE","README.md",".gitattributes"}
    model_files = [p for p in model.rglob("*") if p.is_file() and ".cache" not in p.relative_to(model).parts]
    require({p.relative_to(model).as_posix() for p in model_files} == model_names, "model inventory")
    inventory_names = set(frozen["code_hashes"]) | set(frozen["authority_hashes"])
    inventory_names |= {CANDIDATE + n for n in original["file_sha256"]}
    inventory_names |= {cfg["compiler"]["path"]} | {p.relative_to(ROOT).as_posix() for p in model_files}
    inventory = {}
    for name in sorted(inventory_names):
        info = frozen["authority_hashes"].get(name, {})
        policy = "LF-normalized" if info.get("verification") == "LF-normalized" else "byte-exact"
        digest = hashlib.sha256(expected_bytes).hexdigest() if name == EXPECTED else sha(ROOT / name)
        inventory[name] = {"sha256":digest,"bytes":len(expected_bytes) if name == EXPECTED else (ROOT / name).stat().st_size,"policy":policy}
    for name, digest in (cfg["base_weights"]["weight_file_sha256"] | cfg["tokenizer_file_sha256"]).items():
        require(inventory[(model / name).relative_to(ROOT).as_posix()]["sha256"] == digest, "model pin mismatch: " + name)
    blocks = {}
    for task in tasks:
        if task["group"] == "novel_composition":
            row = blocks.setdefault(task["block_id"], {"family":task["family"],"task_ids":[],"composition_signatures":[]})
            row["task_ids"].append(task["task_id"])
            row["composition_signatures"].append(task["composition_signature"])
    for row in blocks.values():
        row["task_ids"].sort()
        row["composition_signatures"] = sorted(set(row["composition_signatures"]))
    require(len(blocks)==8 and all(len(r["task_ids"])==4 for r in blocks.values()) and
            all(sum(r["family"]==d for r in blocks.values())==4 for d in schedule.DOMAINS), "primary blocks")
    parents = {key:git("rev-parse", ref) for key,ref in {
        "r1_freeze":"622b8cd","r2_freeze":"e0e48de","c12_c14":"9002fd7",
        "i1":"36b9298","i2":"6192040","i3":"ad29adb","i4a":"410e7f2","i4b":"2670093","i5a":"9002fd7","i5b":"034ff88",
        "step4":"a456e9f","smoke":"097b74b","construction":"2da5b85"}.items()}
    eval_source = "scripts/evaluate_phase3c_conf1.py"
    def sourced(value, name, needle):
        return {"value":value,"source":source(name, needle)}
    require(cfg["evaluation"]["max_new_tokens"]==512 and cfg["evaluation"]["compiler_timeout_seconds"]==3, "generation pins")
    generation = {"do_sample":sourced(False,eval_source,"do_sample=False"),"num_beams":sourced(1,eval_source,"num_beams=1"),
                  "max_new_tokens":sourced(512,"research/protocols/phase3c_conf1_config_proposed.json",'"max_new_tokens"'),
                  "pad_token_id":sourced("eos_token_id",eval_source,"pad_token_id=tokenizer.eos_token_id"),
                  "system_prompt":sourced("prompts/phase1t_system.txt","src/self_learning_ai/conf1_r1/execution.py","system = (ROOT"),
                  "user_prompt":sourced("prompts/phase1t_user_template.txt","src/self_learning_ai/conf1_r1/execution.py","template = (ROOT"),
                  "extractor":sourced("self_learning_ai.benchmark.extract_source (first fence)","src/self_learning_ai/conf1_r1/execution.py","source = extract_source(raw)"),
                  "compiler_timeout_seconds":sourced(3,"research/protocols/phase3c_conf1_config_proposed.json",'"compiler_timeout_seconds"'),
                  "cases_per_task":sourced(5,"src/self_learning_ai/dev2r_evaluation.py","len(cases) != 5"),
                  "evaluation_seed":sourced(schedule.EVALUATION_SEED,"src/self_learning_ai/conf1_r1/schedule.py","EVALUATION_SEED ="),
                  "task_rng_rule":sourced("First 8 bytes big-endian SHA-256(20290307|training_seed|task_id) modulo 2^32; reset Python/NumPy/Torch CPU/CUDA before generation",
                                          "src/self_learning_ai/conf1_r1/schedule.py","def task_rng_seed")}
    frozen.update(status="CANDIDATE_FROZEN", schema_version="PHASE_3C_CONF1_FREEZE_1",
                  prefreeze_manifest_sha256=PREFREEZE, construction_commit=START)
    frozen["freeze"] = {
        "parent_commits":parents,"hash_policy":"Byte-exact for binaries, adapters and all new entries; LF normalization only where an existing authority entry declares it. Inventory sha256 and sizes always identify disk bytes.",
        "inventory":inventory,"environment":environment,"counts":original["counts"],"primary_blocks":blocks,
        "schedule":{"SEEDS":list(schedule.SEEDS),"cell_order":cells,"exposures_per_cell":180,"optimizer_steps_per_cell":24,
                    "training_schedule_sha256":{str(s):hashlib.sha256(canonical(schedule.training_schedule(s))).hexdigest() for s in schedule.SEEDS},
                    "schedule_hash_serialization":"indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False, UTF-8 LF, trailing newline",
                    "P3_token_totals":gates["P3_TOKENS"]["totals"],"exposures_per_condition":900,"optimizer_steps_per_condition":120},
        "generation":generation,"checkpoints":{"runtime_root":execution.DEFAULT_RUNTIME.relative_to(ROOT).as_posix(),
            "patterns":["training/<seed>/<condition>.json","evaluations/<seed>/<condition>/training/<slot>.raw.json",
                        "evaluations/<seed>/<condition>/training/<slot>.score.json","evaluations/<seed>/<condition>/confirmatory/<task_id>.raw.json",
                        "evaluations/<seed>/<condition>/confirmatory/<task_id>.score.json","acquisition_gate.json","confirmatory_complete.json","analysis.json","output_inventory.json"]},
        "expected_result_ids":{"path":EXPECTED,"sha256":hashlib.sha256(expected_bytes).hexdigest(),"counts":counts},
        "analysis":{"BOOTSTRAP_SEED":analysis.BOOTSTRAP_SEED,"DRAW_COUNT":analysis.DRAW_COUNT,"sum_E_minimum":32,"lower_bound_strictly_greater_than":0,
                    "acquisition":{"minimum":54,"tasks_per_cell":60,"cells_required":10},"sanity":{"mean_minimum_pp":-10,"per_seed_minimum_pp":-25,"minimum_kept":12},
                    "heterogeneity":{"every_seed_nonnegative":True,"minimum_positive_seeds":4,"both_domains_positive":True,"minimum_positive_blocks":6,
                                     "source":"research/protocols/phase3c_conf1_implementation_clarifications_c12_c14.md:C14"},
                    "labels":[analysis.INDETERMINATE,analysis.SUPPORT,analysis.NOT_CONFIRMED],"heterogeneity_suffix":"_WITH_HETEROGENEITY",
                    "bootstrap":{"draw_order":["seeds","numeric_blocks","array_blocks"],"seed_draws":5,"blocks_per_domain":4,"tasks_per_block":4,"quantiles":[0.025,0.975],"quantile_method":"linear"}},
        "audit_outputs":{n:sha(ROOT/n) for n in (CANDIDATE+"gates/gate_report.json",CANDIDATE+"construction_log.json",BASE+"step4_synthetic_validation.json",BASE+"infrastructure_smoke.json",BASE+"r2_liveness_feasibility.json")}}
    compare = copy.deepcopy(frozen)
    for name in ("schema_version","prefreeze_manifest_sha256","construction_commit","freeze"):
        compare.pop(name)
    compare["status"] = original["status"]
    for name in added:
        compare["authority_hashes"].pop(name)
    require(compare==original, "V1 existing manifest values changed")
    audit_files = ["src/self_learning_ai/conf1_r1/"+n+".py" for n in
                   ("candidate","gates_primary","training","overlap","secondary","primary","interp","schedule","__init__")]
    audit_files += ["scripts/"+n+".py" for n in ("build_phase3c_conf1_candidate","build_phase3c_conf1_data",
                    "audit_phase3c_conf1_r2_liveness_feasibility","audit_phase3c_conf1_r1_specification_feasibility",
                    "design_phase3c_conf1","build_phase2b_data","validate_phase2b_data")]
    audit_files += ["src/self_learning_ai/compiler.py","src/self_learning_ai/benchmark.py"]
    occurrences = []
    tokenizer_function = None
    class ConstructionAudit(ast.NodeVisitor):
        def __init__(self, filename):
            self.filename = filename
            self.functions = []

        def record(self, node, kind):
            occurrences.append({"file":self.filename,"line":node.lineno,
                                "enclosing_function":self.functions[-1] if self.functions else None,
                                "kind":kind,"text":ast.unparse(node)})

        def visit_FunctionDef(self, node):
            nonlocal tokenizer_function
            if self.filename == "src/self_learning_ai/conf1_r1/training.py" and node.name == "_tokenizer":
                require(tokenizer_function is None, "duplicate tokenizer function")
                tokenizer_function = node
            self.functions.append(node.name)
            self.generic_visit(node)
            self.functions.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Import(self, node):
            if any(alias.name.split(".")[0] in FORBIDDEN_IMPORTS for alias in node.names):
                self.record(node, "Import")
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if (node.module or "").split(".")[0] in FORBIDDEN_IMPORTS:
                self.record(node, "ImportFrom")
            self.generic_visit(node)

        def visit_Attribute(self, node):
            if node.attr in {"generate","backward","from_pretrained"} or node.attr.startswith("AutoModel"):
                self.record(node, "Attribute")
            self.generic_visit(node)

        def visit_Name(self, node):
            if node.id.startswith("AutoModel"):
                self.record(node, "Name")
            self.generic_visit(node)

    for name in audit_files:
        tree = ast.parse((ROOT/name).read_text(encoding="utf-8"))
        ConstructionAudit(name).visit(tree)
    allowlist = [
        {"file":"src/self_learning_ai/conf1_r1/training.py","line":396,"enclosing_function":"_tokenizer",
         "kind":"ImportFrom","text":"from transformers import AutoTokenizer"},
        {"file":"src/self_learning_ai/conf1_r1/training.py","line":397,"enclosing_function":"_tokenizer",
         "kind":"Attribute","text":"AutoTokenizer.from_pretrained"}]
    require(tokenizer_function is not None, "missing tokenizer function")
    tokenizer_nodes = list(ast.walk(tokenizer_function))
    tokenizer_imports = [node for node in tokenizer_nodes if isinstance(node,ast.ImportFrom) and node.module == "transformers"]
    tokenizer_calls = [node for node in tokenizer_nodes if isinstance(node,ast.Call)
                       and isinstance(node.func,ast.Attribute) and node.func.attr == "from_pretrained"
                       and isinstance(node.func.value,ast.Name) and node.func.value.id == "AutoTokenizer"]
    import_only_tokenizer = (len(tokenizer_imports)==1 and len(tokenizer_imports[0].names)==1
                             and tokenizer_imports[0].names[0].name=="AutoTokenizer"
                             and tokenizer_imports[0].names[0].asname is None)
    keyword_checks = {}
    if len(tokenizer_calls)==1:
        keywords = {kw.arg:kw.value for kw in tokenizer_calls[0].keywords}
        for name,value in (("local_files_only",True),("trust_remote_code",False)):
            keyword_checks[name] = isinstance(keywords.get(name),ast.Constant) and keywords[name].value is value
    hash_reference_before_import = (len(tokenizer_imports)==1 and any(
        isinstance(node,ast.Name) and node.id=="TOKENIZER_HASHES" and node.lineno<tokenizer_imports[0].lineno
        for node in tokenizer_nodes))
    static_passed = (occurrences==allowlist and import_only_tokenizer and len(tokenizer_calls)==1
                     and keyword_checks=={"local_files_only":True,"trust_remote_code":True}
                     and hash_reference_before_import)
    static = {"audited_files":audit_files,"occurrences":occurrences,"allowlist":allowlist,
              "allowlist_rationale":"C8 P3 token counting loads the hash-pinned tokenizer only; no weights, inference or gradient",
              "checks":{"import_only_AutoTokenizer":import_only_tokenizer,"keyword_constants":keyword_checks,
                        "TOKENIZER_HASHES_referenced_before_import":hash_reference_before_import},"passed":static_passed}
    history = git("log","--all","--format=%H","--",CANDIDATE.rstrip("/")).splitlines()
    runtime_dirs = sorted(p.name for p in (ROOT/".runtime").iterdir() if p.is_dir())
    require(history==[START] and static["passed"] and smoke["status"]=="INFRASTRUCTURE_SMOKE_NON_SCIENTIFIC_CONSUMED_DEV2_DATA",
            "prefreeze no-model audit")
    require(not (FORBIDDEN_IMPORTS & sys.modules.keys()), "forbidden heavy module imported")
    audit = {"a_runtime_absent":True,"b_attempt_commit_history":history,"c_no_model_static_audit":static,
             "d_smoke_status":smoke["status"],"e_runtime_directory_names":runtime_dirs,
             "e_no_conf1_runtime":not execution.DEFAULT_RUNTIME.exists(),
             "scope_note":"phase3c_conf1_smoke contains authorized consumed-DEV2 smoke artifacts; it is not CONF1 execution."}
    frozen_bytes = canonical(frozen)
    written = False
    try:
        (ROOT/FREEZE).mkdir()
        (ROOT/EXPECTED).write_bytes(expected_bytes)
        written = True
        (ROOT/MANIFEST).write_bytes(frozen_bytes)
        validation = {"V1":{"passed":True,"changed_existing_keys":["status"],"added_keys":["schema_version","prefreeze_manifest_sha256","construction_commit","freeze"],"added_authorities":added}}
        def refusal(path, text):
            try:
                execution.require_execution_authorization(path)
            except execution.GateStop as exc:
                require(text in str(exc), "unexpected authorization refusal: "+str(exc))
                return str(exc)
            raise execution.GateStop("authorization unexpectedly accepted")
        real_refusal = refusal(ROOT/CANDIDATE,REFUSAL)
        cli = {}
        for verb in ("train","evaluate","analyze"):
            script = "scripts/"+verb+"_phase3c_conf1.py"
            result = subprocess.run([sys.executable,"-B",str(ROOT/script),"--candidate-dir",str(ROOT/CANDIDATE),"--check-authorization-only"],
                                    cwd=ROOT,capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"))
            require(result.returncode!=0 and REFUSAL in result.stderr, "V2 CLI refusal failed: "+verb)
            cli[script] = {"exit_code":result.returncode,"stdout":result.stdout,"stderr":result.stderr}
        validation["V2"] = {"passed":True,"real_refusal":real_refusal,"cli":cli}
        with tempfile.TemporaryDirectory(prefix="conf1-freeze-validation-") as temp:
            temp_root = Path(temp).resolve()
            require(not temp_root.is_relative_to(ROOT), "V3 copies must be external")
            good,bad = temp_root/"authorized_copy",temp_root/"negative_copy"
            for target in (good,bad):
                shutil.copytree(ROOT/CANDIDATE,target)
                value = json.loads((target/"candidate_manifest.json").read_bytes())
                value["model_execution_authorized"] = True
                (target/"candidate_manifest.json").write_bytes(canonical(value))
            execution.require_execution_authorization(good)
            negative = bad/"training/isolated_examples.json"
            raw = negative.read_bytes()
            negative.write_bytes(bytes([raw[0]^1])+raw[1:])
            negative_refusal = refusal(bad,"manifest file hash mismatch")
        validation["V3"] = {"passed":True,"simulated_authorization":"accepted","negative_refusal":negative_refusal,"temporary_copies_deleted":not temp_root.exists(),"real_boolean":False}
        reread = read(MANIFEST)
        require(reread==frozen,"V4 manifest serialization")
        verify(reread)
        for name,info in reread["freeze"]["inventory"].items():
            require(sha(ROOT/name)==info["sha256"] and (ROOT/name).stat().st_size==info["bytes"],"V4 inventory: "+name)
        validation["V4"] = {"passed":True,"inventory_entries":len(inventory),"authority_entries":len(frozen["authority_hashes"]),"code_entries":len(frozen["code_hashes"]),"payload_entries":len(frozen["file_sha256"])}
        with tempfile.TemporaryDirectory(prefix="conf1-freeze-compile-") as temp:
            py_compile.compile(str(ROOT/SCRIPT),cfile=str(Path(temp)/"freeze.pyc"),doraise=True)
        diffcheck = subprocess.run(["git","diff","--check"],cwd=ROOT,capture_output=True,text=True)
        require(diffcheck.returncode==0,"V5 diff check: "+diffcheck.stdout+diffcheck.stderr)
        allowed = {SCRIPT,MANIFEST,EXPECTED,REPORT}
        scope = git("status","--porcelain","--untracked-files=all").splitlines()
        require(all(line[3:] in allowed for line in scope),"V5 scope")
        changed_bound = git("diff","--name-only",START,"--","src","tests","research/protocols","scripts").splitlines()
        require(not changed_bound,"V5 existing code/test/protocol changed")
        require(not execution.DEFAULT_RUNTIME.exists(),"V5 CONF1 runtime exists")
        validation["V5"] = {"passed":True,"py_compile":"passed; pyc in deleted external temporary directory","git_diff_check":"passed",
                            "scope_paths_before_report":[line[3:] for line in scope],"existing_code_test_protocol_changes":changed_bound,"conf1_runtime_absent":True}
        report = {"status":"CANDIDATE_FROZEN_MODEL_EXECUTION_NOT_AUTHORIZED","prefreeze_manifest_sha256":PREFREEZE,
                  "frozen_manifest_sha256":hashlib.sha256(frozen_bytes).hexdigest(),"command":"PYTHONDONTWRITEBYTECODE=1 python scripts/freeze_phase3c_conf1_candidate.py",
                  "start_head":START,"freeze_script_sha256":sha(ROOT/SCRIPT),"validation":validation,"prefreeze_audit":audit,
                  "environment":environment,"smoke_comparison":comparisons,"parent_commits":parents,"primary_blocks":blocks,
                  "expected_result_counts":counts,"added_authority_entries":added,"wall_seconds":time.perf_counter()-started}
        (ROOT/REPORT).write_bytes(canonical(report))
        require(not (FORBIDDEN_IMPORTS & sys.modules.keys()),"forbidden model import")
        print(json.dumps({"status":report["status"],"frozen_manifest_sha256":report["frozen_manifest_sha256"],"V1_V5":"PASS","counts":counts},indent=2))
    except BaseException:
        # Roll back only this transaction's authorized outputs; never payloads.
        if written:
            (ROOT/MANIFEST).write_bytes(original_bytes)
        for name in (REPORT,EXPECTED):
            (ROOT/name).unlink(missing_ok=True)
        if (ROOT/FREEZE).is_dir():
            (ROOT/FREEZE).rmdir()
        raise


if __name__ == "__main__":
    main()
