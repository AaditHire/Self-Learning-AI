"""I5b: fake model, mandatory pinned compiler, external temporary outputs.

The old I5a tests install a global audit hook excluding compiler/tokenizer
files. Authorized I5b instrument reads execute in a separate guarded Python
process, keeping that hook unchanged and forbidding repository writes in both.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import random
import shutil
import types
import runpy
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
HEAVY = {"torch", "transformers", "peft", "bitsandbytes"}


def guard(event, args):
    paths, write = [], False
    if event == "open":
        path, mode, flags = args
        paths = [path]
        write = ((isinstance(mode, str) and any(c in mode for c in "wax+")) or
                 bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
    elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.utime"):
        paths, write = [args[0]], True
    elif event in ("os.rename", "os.link", "os.symlink"):
        paths, write = list(args[:2]), True
    for path in paths:
        if not isinstance(path, (str, bytes, os.PathLike)):
            continue
        resolved = Path(os.fsdecode(path)).resolve()
        if not resolved.is_relative_to(ROOT):
            continue
        relative = resolved.relative_to(ROOT).as_posix().casefold()
        if write:
            raise AssertionError("repository write during I5b tests: " + relative)
        if (relative in {"benchmark/tasks.json", "benchmark/hidden_tests.json", "benchmark/reference_solutions.json",
                         "research/protocols/phase3c_conf1_v3_synthetic_expected_labels.json"}
                or Path(relative).name == "hidden_cases.json" or relative.startswith(".runtime/")):
            raise AssertionError("prohibited repository read: " + relative)
        if relative.startswith(".models/") and Path(relative).name not in {
                "tokenizer.json", "tokenizer_config.json", "config.json", "special_tokens_map.json",
                "vocab.json", "merges.txt", "added_tokens.json", "chat_template.jinja"}:
            raise AssertionError("model weight read during I5b tests: " + relative)


def child(action, candidate, output):
    log = output.parent / (output.name + ".worker.log")
    with log.open("w", encoding="utf-8") as handle:
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--worker", action,
                                 str(candidate), str(output)], cwd=ROOT, text=True, stdout=handle, stderr=subprocess.STDOUT)
    stdout = log.read_text(encoding="utf-8")
    assert result.returncode == 0, stdout
    return json.loads((output / "test_result.json").read_bytes())


@pytest.fixture(scope="session")
def synthetic_candidate(tmp_path_factory):
    parent = tmp_path_factory.mktemp("conf1-i5b-candidate")
    result = child("build", parent / "candidate", parent / "build-report")
    assert result["seed"] == 900001 and result["status"] == "CANDIDATE_GATES_PASSED_NOT_FROZEN"
    return parent / "candidate"


def emit(capsys, label, report):
    with capsys.disabled():
        print("I5b " + label + ": " + json.dumps(report, sort_keys=True), flush=True)


def test_t1_authorization(tmp_path, capsys):
    emit(capsys, "T1", child("authorization", tmp_path / "fixture", tmp_path / "result"))


def test_t2_happy_path(synthetic_candidate, tmp_path, capsys):
    result = child("happy", synthetic_candidate, tmp_path / "result")
    assert result["label"] == "CONFIRMATORY_SUPPORT_UNDER_CONF1"
    assert result["sum_E"] == 160 and result["confirmatory_records"] == 640
    emit(capsys, "T2", result)


def test_t3_acquisition_failure(synthetic_candidate, tmp_path, capsys):
    result = child("acquisition", synthetic_candidate, tmp_path / "result")
    assert result["generation_calls"] == 600 and result["confirmatory_calls"] == 0
    emit(capsys, "T3", result)


def test_t4_fault(synthetic_candidate, tmp_path, capsys):
    result = child("fault", synthetic_candidate, tmp_path / "result")
    assert result["generation_calls"] == 1 and result["raw_checkpoints"] == 1
    emit(capsys, "T4", result)


def test_t5_rng(synthetic_candidate, tmp_path, capsys):
    emit(capsys, "T5", child("rng", synthetic_candidate, tmp_path / "result"))


def test_t6_training(synthetic_candidate, tmp_path, capsys):
    emit(capsys, "T6", child("training", synthetic_candidate, tmp_path / "result"))


def test_t7_atomic(tmp_path, capsys):
    emit(capsys, "T7", child("atomic", tmp_path / "unused", tmp_path / "result"))


BOUND_PATHS = sorted({p.relative_to(ROOT).as_posix() for p in (ROOT / "src/self_learning_ai/conf1_r1").glob("*.py")} | {
    "scripts/train_phase3c_conf1.py", "scripts/evaluate_phase3c_conf1.py", "scripts/analyze_phase3c_conf1.py",
    "scripts/train_phase2a_qlora.py", "scripts/validate_phase2b_data.py", "src/self_learning_ai/dev2r_evaluation.py",
    "src/self_learning_ai/benchmark.py", "src/self_learning_ai/compiler.py",
    "research/protocols/phase3c_conf1_config_proposed.json", "prompts/phase1t_system.txt", "prompts/phase1t_user_template.txt"})


@pytest.mark.parametrize("bound_path", BOUND_PATHS)
def test_h2_each_binding(bound_path, tmp_path, capsys):
    emit(capsys, "H2", child("binding:" + bound_path, tmp_path / "fixture", tmp_path / "result"))


def test_h4_prompt_parity(synthetic_candidate, tmp_path, capsys):
    result = child("parity", synthetic_candidate, tmp_path / "result")
    assert result["training_rows_checked"] == 120 and result["mismatches"] == 0
    emit(capsys, "H4", result)


@pytest.mark.parametrize("fault", [f"F{i}" for i in range(1, 8)])
def test_h5_fault_matrix(fault, synthetic_candidate, tmp_path, capsys):
    emit(capsys, fault, child("matrix:" + fault, synthetic_candidate, tmp_path / "result"))


@pytest.mark.parametrize("fault", ["lock", "missing_training", "bad_training_receipt", "missing_gate", "changed_gate", "missing_complete", "count_mismatch"])
def test_h3_analysis_preconditions(fault, synthetic_candidate, tmp_path, capsys):
    emit(capsys, "H3", child("analysis-precondition:" + fault, synthetic_candidate, tmp_path / "result"))


def test_t9_static(tmp_path, capsys):
    import py_compile
    scripts = [ROOT / f"scripts/{kind}_phase3c_conf1.py" for kind in ("train", "evaluate", "analyze")]
    for path in scripts:
        py_compile.compile(str(path), cfile=str(tmp_path / (path.stem + ".pyc")), doraise=True)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.Import):
                assert all(alias.name.split(".")[0] not in HEAVY for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] not in HEAVY
    cfg = json.loads((ROOT / "research/protocols/phase3c_conf1_config_proposed.json").read_bytes())
    dev = json.loads((ROOT / "research/protocols/phase3c_dev2_config.json").read_bytes())
    for key in ("base_weights", "training", "evaluation", "compiler", "tokenizer_file_sha256", "conditions", "prompt_system_template"):
        assert cfg[key] == dev[key]
    assert cfg["status"] == "PROPOSED_NOT_FROZEN" and cfg["model_execution_authorized"] is False
    emit(capsys, "T9", {"scripts_compiled": 3, "top_level_heavy_imports": 0, "DEV2_config_copy": "exact"})


def worker(action, candidate, out):
    def fixture_guard(event, args):
        guard(event, args)
        paths, write = [], False
        if event == "open":
            path, mode, flags = args
            paths = [path]
            write = ((isinstance(mode, str) and any(c in mode for c in "wax+")) or
                     bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
        elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.utime"):
            paths, write = [args[0]], True
        elif event in ("os.rename", "os.link", "os.symlink"):
            paths, write = list(args[:2]), True
        if write:
            for path in paths:
                if isinstance(path, (str, bytes, os.PathLike)):
                    assert Path(os.fsdecode(path)).resolve().is_relative_to(out.parent.resolve()), "write outside pytest fixture"
    sys.addaudithook(fixture_guard)
    # The mandated builder uses AutoTokenizer. Permit that tokenizer-only path
    # with all model backends disabled; execution/CLI workers block all four.
    if action in ("build", "parity"):
        os.environ.update(USE_TORCH="0", USE_TF="0", USE_FLAX="0")
    for name in HEAVY:
        if name not in ({"transformers", "torch"} if action == "parity" else {"transformers"} if action == "build" else set()):
            sys.modules[name] = None
    def no_weights_or_cuda(event, args):
        if event == "v1.cuda_initialization":
            raise AssertionError("CUDA initialization forbidden")
        if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            assert not os.fsdecode(args[0]).lower().endswith(".safetensors"), "weight file forbidden"
    sys.addaudithook(no_weights_or_cuda)
    from self_learning_ai.conf1_r1 import execution as ex, analysis as an, schedule as sc
    from self_learning_ai.conf1_r1.gates_primary import GateStop
    out.mkdir(parents=True)
    tempfile.tempdir = str(out)
    started = time.perf_counter()

    def stop(call, match=None):
        try:
            call()
        except GateStop as exc:
            if match is not None:
                assert match in str(exc), str(exc)
            return str(exc)
        raise AssertionError("expected STOP")

    def save(result):
        result["wall_seconds"] = time.perf_counter() - started
        (out / "test_result.json").write_text(json.dumps(result, allow_nan=False, indent=2), encoding="utf-8")
        print("I5b worker " + action + ": " + json.dumps(result), flush=True)

    if action == "build":
        from self_learning_ai.conf1_r1.candidate import build_candidate
        from self_learning_ai.conf1_r1.training import _tokenizer, TOKENIZER_DIR
        _tokenizer(TOKENIZER_DIR)  # Fail fast before the expensive compiler gates.
        assert sys.modules["torch"] is None and sys.modules["peft"] is None and sys.modules["bitsandbytes"] is None
        print("I5b tokenizer-only precondition PASS; model backends disabled", flush=True)
        result = build_candidate(900001, candidate, label="SYNTHETIC_DRY_RUN", workers=8)
        # Only the temp manifest's authorization fields change for execution.
        fixture = dict(result, status="SYNTHETIC_EXECUTION_TEST_FIXTURE", model_execution_authorized=True)
        (candidate / "candidate_manifest.json").write_text(json.dumps(fixture, indent=2), encoding="utf-8")
        save({"seed": 900001, "status": result["status"], "counts": result["counts"]})
        return
    def authorization_manifest():
        candidate.mkdir(exist_ok=True)
        (candidate / "payload.json").write_text("{}", encoding="utf-8")
        cfg = ex.read(ROOT / "research/protocols/phase3c_conf1_config_proposed.json")
        prompt = "research/protocols/phase3c_conf1_slots.json"
        return {"phase": "PHASE_3C_CONF1", "construction_seed": 900001,
                "status": "SYNTHETIC_EXECUTION_TEST_FIXTURE", "model_execution_authorized": True,
                "file_sha256": {"payload.json": ex.sha256(candidate / "payload.json")},
                "code_hashes": {name: ex.sha256(ROOT / name) for name in ex.execution_bound_files()},
                "authority_hashes": {prompt: {"sha256": ex.sha256(ROOT / prompt)}},
                "compiler_sha256": cfg["compiler"]["sha256"], "tokenizer_hashes": cfg["tokenizer_file_sha256"]}

    if action == "authorization":
        assert ex.AUTHORIZED_STATUSES == frozenset({"CANDIDATE_FROZEN"})
        assert ex.AUTHORIZED_CONSTRUCTION_SEEDS == frozenset({20290123})
        base = authorization_manifest()
        manifest_path = candidate / "candidate_manifest.json"
        def write(value):
            manifest_path.write_text(json.dumps(value), encoding="utf-8")
        refused = [stop(lambda: ex.require_execution_authorization(candidate))]
        for value in (True, "20290123", 20290124):
            write(base | {"status": "CANDIDATE_FROZEN", "construction_seed": value})
            refused.append(stop(lambda: ex.require_execution_authorization(candidate)))
        write(base)
        refused.append(stop(lambda: ex.require_execution_authorization(candidate)))
        exits = {}
        for kind in ("train", "evaluate", "analyze"):
            sys.argv = [kind, "--candidate-dir", str(candidate), "--check-authorization-only"]
            try:
                runpy.run_path(str(ROOT / f"scripts/{kind}_phase3c_conf1.py"), run_name="__main__")
            except SystemExit as exc:
                assert exc.code == 2
                exits[kind] = exc.code
            else:
                raise AssertionError("script did not refuse synthetic authorized fixture")
        assert all(sys.modules[name] is None for name in HEAVY)
        ex.AUTHORIZED_STATUSES = frozenset({"SYNTHETIC_EXECUTION_TEST_FIXTURE"})
        ex.AUTHORIZED_CONSTRUCTION_SEEDS = frozenset({900001})
        write(base)
        assert ex.require_execution_authorization(candidate) == base
        for value in (False, "true", 1, None):
            write(base | {"model_execution_authorized": value})
            refused.append(stop(lambda: ex.require_execution_authorization(candidate)))
        for changes in ({"phase": "WRONG"}, {"status": "PROPOSED_NOT_FROZEN"}):
            write(base | changes)
            refused.append(stop(lambda: ex.require_execution_authorization(candidate)))
        for field in ("code_hashes", "authority_hashes", "compiler_sha256", "tokenizer_hashes", "file_sha256"):
            incomplete = dict(base)
            incomplete.pop(field)
            write(incomplete)
            refused.append(stop(lambda: ex.require_execution_authorization(candidate), "mandatory"))
        write(base)
        (candidate / "payload.json").write_text('{"tampered":true}', encoding="utf-8")
        refused.append(stop(lambda: ex.require_execution_authorization(candidate), "hash mismatch"))
        save({"production_statuses": ["CANDIDATE_FROZEN"], "production_construction_seeds": [20290123],
              "authorization_refusals": len(refused), "script_exit_codes": exits, "ImportError": False})
        return

    if action.startswith("binding:"):
        name = action.split(":", 1)[1]
        base = authorization_manifest()
        ex.AUTHORIZED_STATUSES = frozenset({"SYNTHETIC_EXECUTION_TEST_FIXTURE"})
        ex.AUTHORIZED_CONSTRUCTION_SEEDS = frozenset({900001})
        manifest_path = candidate / "candidate_manifest.json"
        missing = json.loads(json.dumps(base))
        missing["code_hashes"].pop(name, None)
        missing["authority_hashes"].pop(name, None)
        manifest_path.write_text(json.dumps(missing), encoding="utf-8")
        stop(lambda: ex.require_execution_authorization(candidate), "missing execution bindings")
        replica = out / "repo-copy"
        cfg = ex.read(ROOT / "research/protocols/phase3c_conf1_config_proposed.json")
        copied = set(ex.execution_bound_files()) | {cfg["compiler"]["path"]} | {
            cfg["base_weights"]["local_path"] + "/" + key for key in cfg["tokenizer_file_sha256"]}
        for file in copied:
            target = replica / file
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / file).read_bytes())
        target = replica / name
        raw = target.read_bytes()
        target.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
        manifest_path.write_text(json.dumps(base), encoding="utf-8")
        ex.ROOT = replica
        stop(lambda: ex.require_execution_authorization(candidate), "hash mismatch")
        (replica / "src/self_learning_ai/conf1_r1/new_module.py").write_text("# fixture", encoding="utf-8")
        assert "src/self_learning_ai/conf1_r1/new_module.py" in ex.execution_bound_files()
        stop(lambda: ex.require_execution_authorization(candidate), "missing execution bindings")
        save({"path": name, "missing_refused": True, "one_byte_tamper_refused": True,
              "dynamic_new_module_refused": True, "tampered_repository_files": 0})
        return
    if action == "atomic":
        count = 0
        original = os.fsync
        def fsync(fd):
            nonlocal count
            count += 1
            return original(fd)
        os.fsync = fsync
        store = ex.CheckpointStore(out / "runtime")
        store.write("one.json", {"value": 1})
        digest = ex.sha256(store.path("one.json"))
        stop(lambda: store.write("one.json", {"value": 2}), "existing checkpoint")
        assert ex.sha256(store.path("one.json")) == digest and count >= 1
        assert not list(store.root.glob("*.tmp-*")) and not list(store.root.glob("*.lock"))
        from concurrent.futures import ThreadPoolExecutor
        def competing(value):
            try:
                store.write("race.json", {"value": value})
                return True
            except GateStop:
                return False
        with ThreadPoolExecutor(2) as pool:
            successes = list(pool.map(competing, (1, 2)))
        assert sum(successes) == 1 and ex.read(store.path("race.json"))["value"] in (1, 2)
        save({"fsync_calls": count, "overwrite_refused": True, "concurrent_writers_succeeded": 1,
              "temporary_files_remaining": 0})
        return

    ex.AUTHORIZED_STATUSES = frozenset({"SYNTHETIC_EXECUTION_TEST_FIXTURE"})
    ex.AUTHORIZED_CONSTRUCTION_SEEDS = frozenset({900001})
    path, manifest, tasks, examples, cases = ex._candidate(candidate)
    runtime = out / "runtime"
    calls = []
    references = ex.read(candidate / "evaluation/references.json")
    def good_train(seed, condition, schedule, rows):
        calls.append((seed, condition))
        assert len(rows) == 60 and schedule == sc.training_schedule(seed)
        for row in rows:
            assert row["messages"][1]["content"] == f"Task {row['model_task_id']}\n\n{row['prompt']}"
            assert row["example_id"] not in row["messages"][1]["content"]
        return {"exposures": 180, "optimizer_steps": 24, "losses": [0.25] * 180}

    if action == "parity":
        import torch
        def cuda_forbidden(*args, **kwargs):
            sys.audit("v1.cuda_initialization")
        torch.cuda.init = cuda_forbidden
        torch.cuda._lazy_init = cuda_forbidden
        if hasattr(torch._C, "_cuda_init"):
            torch._C._cuda_init = cuda_forbidden
        from transformers import AutoTokenizer
        cfg = ex.read(ROOT / "research/protocols/phase3c_conf1_config_proposed.json")
        model_path = ROOT / cfg["base_weights"]["local_path"]
        for name, digest in cfg["tokenizer_file_sha256"].items():
            assert ex.sha256(model_path / name) == digest
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        # Import the unchanged TokenDataset module, with unused model/adapter
        # constructors replaced by refusal stubs. Only CPU Dataset is exercised.
        def unused(*args, **kwargs):
            raise AssertionError("model/adapter API forbidden in parity test")
        peft_stub = types.ModuleType("peft")
        for name in ("LoraConfig", "get_peft_model", "prepare_model_for_kbit_training"):
            setattr(peft_stub, name, unused)
        sys.modules["peft"] = peft_stub
        sys.modules["bitsandbytes"] = types.ModuleType("bitsandbytes")
        transformers_stub = types.ModuleType("transformers")
        for name in ("AutoModelForCausalLM", "BitsAndBytesConfig", "get_linear_schedule_with_warmup"):
            setattr(transformers_stub, name, unused)
        transformers_stub.AutoTokenizer = AutoTokenizer
        sys.modules["transformers"] = transformers_stub
        sys.path.insert(0, str(ROOT / "scripts"))
        from train_phase2a_qlora import TokenDataset
        maximum = checked = 0
        for condition in sc.CONDITIONS:
            system, rows = ex.training_rows(list(examples[condition].values()), sc.SLOT_IDS)
            for row in rows:
                item = TokenDataset([row], tokenizer, system, 320)[0]
                prefix_length = sum(label == -100 for label in item["labels"])
                prompt_ids = item["input_ids"][:prefix_length]
                evaluated = ex.encode_prompt(tokenizer, ex.messages(row["model_task_id"], row["prompt"]))
                if prompt_ids != evaluated:
                    evidence = {"slot": row["model_task_id"], "condition": condition,
                                "training_decoded": tokenizer.decode(prompt_ids),
                                "evaluation_decoded": tokenizer.decode(evaluated)}
                    save({"STOP": "H4 parity mismatch", **evidence})
                    raise GateStop("H4 parity mismatch", evidence)
                checked += 1
                maximum = max(maximum, len(item["input_ids"]))
        evaluation_lengths = [len(ex.encode_prompt(tokenizer, ex.messages(t["task_id"], t["prompt"]))) for t in tasks]
        assert max(evaluation_lengths) <= 8192
        assert not torch.cuda.is_initialized()
        save({"training_rows_checked": checked, "mismatches": 0, "max_training_full_length": maximum,
              "evaluation_tasks_checked": len(tasks), "max_evaluation_prompt_length": max(evaluation_lengths),
              "weights_opened": 0, "CUDA_initialized": False, "TokenDataset_module": "scripts/train_phase2a_qlora.py"})
        return

    if action.startswith(("matrix:", "analysis-precondition:")):
        fault = action.split(":", 1)[1]
        def fast_score(raw, task, selected, target, checkpoint_dir):
            return {"passed": True, "compile_ok": True, "exact_target": True,
                    "case_outcomes": [{"passed": True, "execution_ok": True,
                                       "expected_stdout": c["expected_stdout"]} for c in selected]}
        def fail(*args):
            raise RuntimeError("INJECTED_" + fault)
        model_calls = 0
        def fake_generate(*args):
            nonlocal model_calls
            model_calls += 1
            if fault == "F2":
                return fail()
            return "FAKE_RAW"
        if action.startswith("analysis-precondition:"):
            ex.run_training_cells(candidate, good_train, runtime_root=runtime)
            ex.run_own_training(candidate, fake_generate, fast_score, reset=random.seed, runtime_root=runtime)
            store = ex.CheckpointStore(runtime)
            stem = f"training/{sc.SEEDS[0]}/{sc.CONDITIONS[0]}"
            if fault == "lock":
                store.path("stray.lock").write_text("reservation", encoding="utf-8")
            elif fault == "missing_training":
                store.path(stem + ".json").unlink()
            elif fault == "bad_training_receipt":
                store.path(stem + ".sha256.json").write_text('{"sha256":"WRONG"}', encoding="utf-8")
            elif fault == "missing_gate":
                store.path("acquisition_gate.json").unlink()
            elif fault == "changed_gate":
                gate = ex.read(store.path("acquisition_gate.json"))
                gate["passed"] = False
                store.path("acquisition_gate.json").write_text(json.dumps(gate), encoding="utf-8")
            elif fault == "count_mismatch":
                store.write("confirmatory_complete.json", {"records": 10 * len(tasks), "tasks_per_cell": len(tasks)})
            elif fault != "missing_complete":
                raise AssertionError(fault)
            reason = stop(lambda: ex.run_analysis(candidate, runtime))
            assert (runtime / "incidents").exists() and not (runtime / "analysis.json").exists()
            save({"fault": fault, "reason": reason, "analysis_refused": True,
                  "incident_written": True, "analysis_written": False})
            return
        if fault == "F1":
            train_calls = 0
            def fail_train(*args):
                nonlocal train_calls
                train_calls += 1
                return fail()
            stage = lambda: ex.run_training_cells(candidate, fail_train, runtime_root=runtime)
        else:
            ex.run_training_cells(candidate, good_train, runtime_root=runtime)
            scorer = fast_score
            if fault == "F3":
                scorer = fail
            if fault == "F5":
                def scorer(*args):
                    raise GateStop("compiler infrastructure fault", {"phase": "system"})
            original_write = ex.CheckpointStore.write
            if fault == "F4":
                def fail_receipt(self, name, value):
                    if name.endswith(".score.sha256.json"):
                        raise OSError("INJECTED_F4_RECEIPT_WRITE")
                    return original_write(self, name, value)
                ex.CheckpointStore.write = fail_receipt
            stage = lambda: ex.run_own_training(candidate, fake_generate, scorer, reset=random.seed, runtime_root=runtime)
            if fault in ("F6", "F7"):
                stage()
                if fault == "F6":
                    raw_path = next(runtime.glob("evaluations/*/*/training/*.raw.json"))
                    raw = raw_path.read_bytes()
                    raw_path.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
                else:
                    (runtime / "stray.tmp-INJECTED_F7").write_text("partial", encoding="utf-8")
                stage = lambda: ex.run_analysis(candidate, runtime)
        reason = stop(stage)
        if fault == "F6":
            assert "raw checkpoint hash mismatch" in reason
        if fault == "F7":
            assert "incident-free" in reason
        incidents = list((runtime / "incidents").glob("*.json"))
        assert incidents and not (runtime / "analysis.json").exists()
        previous = train_calls if fault == "F1" else model_calls
        stop(stage)
        assert (train_calls if fault == "F1" else model_calls) == previous
        stop(lambda: ex.run_analysis(candidate, runtime), "incident-free")
        assert not (runtime / "analysis.json").exists()
        if fault == "F1":
            assert list((runtime / "training").rglob("*.started.json")) and train_calls == 1
        if fault == "F2":
            assert not list(runtime.glob("evaluations/*/*/training/*.raw.json"))
        if fault == "F4":
            assert len(list(runtime.glob("evaluations/*/*/training/*.score.json"))) == 1
            assert not list(runtime.glob("evaluations/*/*/training/*.score.sha256.json"))
        save({"fault": fault, "first_reason": reason, "incident_written": True,
              "retry_refused": True, "new_model_calls_on_retry": 0, "analysis_refused": True,
              "generation_calls": model_calls, "training_calls": train_calls if fault == "F1" else 10})
        return

    if action == "training":
        result = ex.run_training_cells(candidate, good_train, runtime_root=runtime)
        expected = [(cell["seed"], cell["condition"]) for cell in sc.cell_order()]
        assert calls == expected and len(result) == 10
        stop(lambda: ex.run_training_cells(candidate, good_train, runtime_root=runtime), "retry forbidden")
        assert calls == expected
        faults = {"23_steps": {"optimizer_steps": 23}, "179_exposures": {"exposures": 179}, "NaN_loss": {"losses": [float("nan")]}}
        fault_calls = {}
        for name, changes in faults.items():
            count = 0
            def bad(*args):
                nonlocal count
                count += 1
                return {"exposures": 180, "optimizer_steps": 24, "losses": [1.0]} | changes
            stop(lambda: ex.run_training_cells(candidate, bad, runtime_root=out / name))
            assert count == 1
            fault_calls[name] = count
        save({"cell_order": calls, "cells_called_once": 10, "fault_call_counts": fault_calls})
        return

    generated = []
    def generate(seed, condition, task, messages):
        generated.append((seed, condition, task["task_id"]))
        if task["group"] == "training":
            return examples[condition][task["task_id"]]["target"]
        return "DISPLAYNL(99999)." if condition == "isolated" and task["group"] == sc.GROUPS[0] else references[task["task_id"]]

    if action == "rng":
        outputs, seeds = [], []
        subset = tasks[:8]
        def rng_generate(seed, condition, task, messages):
            return str(random.getrandbits(64))
        def reset(seed):
            random.seed(seed)
            seeds.append(seed)
        def flags(raw, task, cases, target, checkpoint_dir):
            return {"passed": False, "compile_ok": True,
                    "case_outcomes": [{"passed": False, "execution_ok": True, "expected_stdout": "0.0"} for _ in range(5)]}
        for i, (condition, shuffled) in enumerate((("isolated", False), ("composition", False), ("isolated", True))):
            order = list(subset)
            if shuffled:
                random.Random(333).shuffle(order)
            store = ex.CheckpointStore(out / str(i))
            mapping = {}
            for task in order:
                row = ex._task(store, sc.SEEDS[0], condition, "confirmatory", task, [], None, rng_generate, flags, reset)
                stem = f"evaluations/{sc.SEEDS[0]}/{condition}/confirmatory/{task['task_id']}.raw.json"
                mapping[task["task_id"]] = ex.read(store.path(stem))["raw_generation"]
                assert row["rng_seed"] == sc.task_rng_seed(sc.SEEDS[0], task["task_id"])
            outputs.append(mapping)
        assert outputs[0] == outputs[1] == outputs[2]
        assert seeds[:8] == seeds[8:16]
        save({"tasks": len(subset), "identical_per_task_outputs": True, "paired_condition_seeds_equal": True,
              "seeds": seeds[:8], "outputs_sha256": hashlib.sha256(json.dumps(outputs[0], sort_keys=True).encode()).hexdigest()})
        return
    if action == "fault":
        def fault_score(*args):
            raise RuntimeError("INJECTED_AFTER_RAW_BEFORE_SCORE")
        stop(lambda: ex.run_own_training(candidate, generate, fault_score, reset=random.seed, runtime_root=runtime))
        store = ex.CheckpointStore(runtime)
        incidents = [ex.read(p) for p in store.path("incidents").glob("*.json")]
        assert any(i["reason"] == "INJECTED_AFTER_RAW_BEFORE_SCORE" for i in incidents)
        stop(lambda: ex.run_own_training(candidate, generate, fault_score, reset=random.seed, runtime_root=runtime), "retry forbidden")
        assert len(generated) == 1
        assert len(list(runtime.glob("evaluations/*/*/training/*.raw.json"))) == 1
        assert not list(runtime.glob("evaluations/*/*/training/*.score.json"))
        save({"generation_calls": 1, "raw_checkpoints": 1, "score_checkpoints": 0, "incident": incidents[0]})
        return

    # Compiler memoization is fixture-only: every distinct source/stdin pair is
    # actually evaluated by the pinned instrument. Seed repetitions reuse that
    # immutable result; the production scorer never memoizes model programs.
    from self_learning_ai.compiler import GocoCompiler
    cfg = ex.read(ROOT / "research/protocols/phase3c_dev2_config.json")
    assert ex.sha256(ROOT / cfg["compiler"]["path"]) == cfg["compiler"]["sha256"]
    compiler = GocoCompiler(ROOT / cfg["compiler"]["java"], ROOT / cfg["compiler"]["path"], timeout_seconds=3)
    cache = {}
    class MemoCompiler:
        def run(self, source, stdin):
            key = (source, stdin)
            if key not in cache:
                cache[key] = compiler.run(source, stdin)
            return cache[key]
    score = ex.compiler_score(MemoCompiler())
    if action == "happy":
        ex.run_training_cells(candidate, good_train, runtime_root=runtime)
        gate = ex.run_own_training(candidate, generate, score, reset=random.seed, runtime_root=runtime)
        assert gate["passed"] and all(cell["passed"] == 60 for cell in gate["cells"])
        primary = ex.run_confirmatory(candidate, generate, score, reset=random.seed, runtime_root=runtime)
        assert len(primary) == 10 * 64 and len(generated) == 1240
        expected_training = [(c["seed"], c["condition"], tid) for c in sc.cell_order() for tid in sc.SLOT_IDS]
        ordered = sc.confirmatory_order({g: [t["task_id"] for t in tasks if t["group"] == g] for g in sc.GROUPS})
        expected_confirmatory = [(c["seed"], c["condition"], tid) for c in sc.cell_order() for tid in ordered]
        assert generated == expected_training + expected_confirmatory
        report = ex.run_analysis(candidate, runtime)
        assert report["label"] == an.SUPPORT and report["primary"]["criteria"]["sum_E"] == 160
        assert report["primary"]["bootstrap"]["interval"] == [1.0, 1.0]
        assert all(p["passed"] == 60 for p in report["acquisition"]["cells"])
        inventory = ex.read(runtime / "output_inventory.json")
        assert all(ex.sha256(runtime / p) == h for p, h in inventory.items())
        # First-fence extraction even with a second complete block.
        first = score('```goco\nDISPLAYNL(99999).\n```\n```goco\nDISPLAYNL(0).\n```', tasks[0],
                      ex.read(candidate / "evaluation/hidden_cases.json")[tasks[0]["task_id"]], None, out / "first-fence")
        assert first["passed"] is False
        # C13's no-newline fallback preserves a valid one-line source containing
        # backticks in a string. Re-fencing that source would change extraction.
        literal_cases = [{"case_id": f"LITERAL-{i}", "stdin": "", "expected_stdout": "0.0"} for i in range(5)]
        literal = score('SENTENCE junk="```". DISPLAYNL(0).', tasks[0], literal_cases, None, out / "literal-fence")
        assert literal["passed"] is True
        from self_learning_ai.dev2r_evaluation import extract_source_phase1r
        assert extract_source_phase1r('```goco\nA\n```\n```goco\nB\n```').startswith('```')
        save({"label": report["label"], "sum_E": 160, "interval": [1.0, 1.0], "generation_calls": len(generated),
              "confirmatory_records": len(primary), "acquisition_counts": [c["passed"] for c in gate["cells"]],
              "distinct_compiler_runs": len(cache), "output_hashes_verified": len(inventory), "first_fence": "PASS",
              "literal_fence_fallback": "PASS", "historical_extractor_unchanged": True})
        return
    if action == "acquisition":
        ex.run_training_cells(candidate, good_train, runtime_root=runtime)
        bad_ids = set(sc.SLOT_IDS[:7])
        original_generate = generate
        def fail_seven(seed, condition, task, messages):
            raw = original_generate(seed, condition, task, messages)
            return "DISPLAYNL(99999)." if seed == sc.SEEDS[0] and condition == "isolated" and task["task_id"] in bad_ids else raw
        try:
            ex.run_own_training(candidate, fail_seven, score, reset=random.seed, runtime_root=runtime)
        except ex.AcquisitionFailed as exc:
            assert an.INDETERMINATE in str(exc)
        else:
            raise AssertionError("AcquisitionFailed required")
        assert len(generated) == 600
        gate = ex.read(runtime / "acquisition_gate.json")
        assert gate["cells"][0]["passed"] == 53 and gate["passed"] is False
        assert not (runtime / "incidents").exists()
        assert gate["outcome"] == an.INDETERMINATE
        assert len(generated) == 600 and not list(runtime.glob("evaluations/*/*/confirmatory/*"))
        planted_runtime = out / "G2"
        shutil.copytree(runtime, planted_runtime)
        ex.CheckpointStore(planted_runtime).write("evaluations/20280117/isolated/confirmatory/planted.raw.json", {})
        stop(lambda: ex.run_analysis(candidate, planted_runtime), "confirmatory checkpoints forbidden")
        assert (planted_runtime / "incidents").exists() and not (planted_runtime / "analysis.json").exists()
        report = ex.run_analysis(candidate, runtime)
        assert report["label"] == an.INDETERMINATE and "primary" not in report
        training_records = ex._score_records(ex.CheckpointStore(runtime), "training")
        extra = {"suite": "confirmatory"}
        stop(lambda: an.analyze(training_records + [extra], tasks), "confirmatory records forbidden")
        save({"label": report["label"], "generation_calls": len(generated), "confirmatory_calls": 0,
              "first_cell_passes": 53, "training_records": 600, "primary_analysis": False,
              "confirmatory_records_after_FAIL": "STOP", "distinct_compiler_runs": len(cache),
              "G1": {"AcquisitionFailed": True, "incident": False, "analysis": an.INDETERMINATE},
              "G2": {"planted_confirmatory_refused": True, "incident": True, "analysis_written": False}})
        return
    raise AssertionError("unknown worker action")


if __name__ == "__main__":
    assert sys.argv[1] == "--worker"
    worker(sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]))
