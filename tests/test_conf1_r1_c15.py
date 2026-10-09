"""C15 child-process fixtures; no real runtime or model reads."""
from __future__ import annotations

import errno
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

import pytest

from test_conf1_r1_execution import ROOT, HEAVY, guard, synthetic_candidate


def child(action, candidate, output):
    output.mkdir()
    log = output / "worker.log"
    with log.open("w", encoding="utf-8") as handle:
        result = subprocess.run([sys.executable, "-B", __file__, action, str(candidate), str(output)],
                                cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, text=True)
    assert result.returncode == 0, log.read_text(encoding="utf-8")
    return json.loads((output / "result.json").read_bytes())


def test_c15_system_reinvocation(tmp_path):
    report = child("retries", tmp_path / "unused", tmp_path / "result")
    assert report["system_success"] == 2 and report["system_stop"] == 3
    assert all(v == 1 for v in report["non_system_calls"].values())


def test_c15_continuation_equivalence_and_refusals(synthetic_candidate, tmp_path, capsys):
    report = child("continuation", synthetic_candidate, tmp_path / "result")
    assert report["generation_count"] == 1240
    assert report["identical_rows"] and report["analysis_equal"] and report["prefix_unchanged"]
    assert report["incident_hash_matches_real"]
    assert len(report["continuation_refusals"]) == 12
    assert len(report["analysis_refusals"]) == 3
    with capsys.disabled():
        print("C15 T-C3/T-C4/T-C5: " + json.dumps(report, sort_keys=True), flush=True)


def test_c15_script_import_guard(tmp_path):
    report = child("script", tmp_path / "candidate", tmp_path / "result")
    assert report["exits"] == {"unauthorized": 2, "missing": 2, "mismatched": 2}
    assert report["heavy_imports"] == 0


def worker(action, candidate, out):
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.addaudithook(guard)
    for name in HEAVY:
        sys.modules[name] = None
    tempfile.tempdir = str(out)
    from self_learning_ai.conf1_r1 import execution as ex, schedule as sc, analysis as an
    from self_learning_ai.compiler import CompilerResult, GocoCompiler
    from self_learning_ai.conf1_r1.gates_primary import GateStop

    def save(value):
        (out / "result.json").write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def stop(call):
        try:
            call()
        except GateStop:
            return
        raise AssertionError("GateStop required")

    def inventory(root):
        return {p.relative_to(root).as_posix(): ex.sha256(p) for p in root.rglob("*") if p.is_file()}

    if action == "retries":
        from self_learning_ai import dev2r_evaluation as dev, benchmark
        # Isolate one run(source, stdin) while keeping the real durable evaluator.
        original_score = benchmark.score_source
        dev.score_source = lambda compiler, task, cases, source: original_score(compiler, task, cases[:1], source)
        sleeps = []
        ex.time.sleep = sleeps.append
        task = dict(sc.EVALUATION_TASKS[0], prompt="fixture")
        cases = [{"case_id": str(i), "stdin": "fixture", "expected_stdout": "0"} for i in range(5)]

        def exercise(name, phases):
            calls = []
            class Fake:
                def run(self, source, stdin):
                    calls.append((source, stdin))
                    phase = phases[min(len(calls) - 1, len(phases) - 1)]
                    return CompilerResult(phase, 0 if phase == "success" else 1, "0", "fixture" * 50,
                                          1, phase == "timeout", phase == "output_limit", phase == "success")
            path = out / name
            scorer = ex.compiler_score(Fake())
            if phases == ["system"]:
                try:
                    scorer("DISPLAYNL(0).", task, cases, None, path)
                except GateStop as exc:
                    assert str(exc) == "STOP: compiler infrastructure fault"
                else:
                    raise AssertionError("compiler infrastructure GateStop required")
            else:
                row = scorer("DISPLAYNL(0).", task, cases, None, path)
                if name == "system_success":
                    assert row["passed"]
            log = path / "c15_system_retries.json"
            if "system" in phases:
                entries = ex.read(log)["attempts"]
                assert len(entries) == len(calls)
                assert all(set(a) <= {"case_index", "attempt_number", "is_system", "exit_code",
                                      "timed_out", "elapsed_ms", "stderr", "einval"} for a in entries)
                assert all(a["einval"] is False for a in entries)
                assert all(len(a.get("stderr", "")) <= 200 for a in entries)
                assert len(set(calls)) == 1
            else:
                assert not log.exists()
            return len(calls)
        success = exercise("system_success", ["system", "success"])
        failure = exercise("system_stop", ["system"])
        phases = {p: exercise(p, [p]) for p in
                  ["timeout", "output_limit", "lexical", "syntax", "semantic", "runtime", "success"]}
        def exercise_error(name, error_number, succeeds):
            calls = []
            class FakeError:
                def run(self, source, stdin):
                    calls.append((source, stdin))
                    if not succeeds or len(calls) == 1:
                        raise OSError(error_number, "fixture error")
                    return CompilerResult("success", 0, "0", "", 1, False, False, True)
            path = out / name
            scorer = ex.compiler_score(FakeError())
            try:
                row = scorer("DISPLAYNL(0).", task, cases, None, path)
            except OSError as exc:
                assert not succeeds and exc.errno == error_number
            else:
                assert succeeds and row["passed"]
            log = path / "c15_system_retries.json"
            if error_number == errno.EINVAL:
                entries = ex.read(log)["attempts"]
                assert len(entries) == len(calls) == (2 if succeeds else 3)
                assert entries[0]["einval"] is True
                assert [a["einval"] for a in entries] == ([True, False] if succeeds else [True] * 3)
                assert len(set(calls)) == 1
            else:
                assert len(calls) == 1 and not log.exists()
            return len(calls)
        errors = {"einval_success": exercise_error("einval_success", errno.EINVAL, True),
                  "einval_stop": exercise_error("einval_stop", errno.EINVAL, False),
                  "eacces": exercise_error("eacces", errno.EACCES, False)}
        assert sleeps == [2, 2, 10, 2, 2, 10]
        save({"system_success": success, "system_stop": failure, "non_system_calls": phases,
              "error_calls": errors})
        return

    if action == "script":
        import evaluate_phase3c_conf1 as script
        manifest = {"authority_hashes": {}}
        exits = {}
        for name in ["unauthorized", "missing", "mismatched"]:
            if name == "unauthorized":
                def refuse(*args):
                    raise GateStop("CONF1 model execution is not explicitly authorized")
                script.require_execution_authorization = refuse
            else:
                script.require_execution_authorization = lambda *a: manifest
                ex.C15_REVIEWED_INCIDENT = str(out / "fixture-record.json")
                if name == "mismatched":
                    Path(ex.C15_REVIEWED_INCIDENT).write_text("{}", encoding="utf-8")
                    manifest["authority_hashes"][ex.C15_REVIEWED_INCIDENT] = {
                        "verification": "byte-exact", "sha256": "WRONG", "verified_sha256": "WRONG"}
            sys.argv = ["evaluate", "--candidate-dir", str(candidate), "--c15-continue-confirmatory"]
            try:
                script.main()
            except SystemExit as exc:
                exits[name] = exc.code
            else:
                raise AssertionError("CLI must refuse before generator")
        assert all(sys.modules.get(name) is None for name in HEAVY)
        save({"exits": exits, "heavy_imports": 0})
        return

    ex.AUTHORIZED_STATUSES = frozenset({"SYNTHETIC_EXECUTION_TEST_FIXTURE"})
    ex.AUTHORIZED_CONSTRUCTION_SEEDS = frozenset({900001})
    _, manifest, tasks, examples, _ = ex._candidate(candidate)
    references = ex.read(candidate / "evaluation/references.json")
    generated = []
    def generate(seed, condition, task, messages):
        suite = "training" if task["group"] == "training" else "confirmatory"
        generated.append((seed, condition, suite, task["task_id"]))
        if suite == "training":
            return examples[condition][task["task_id"]]["target"]
        return "DISPLAYNL(99999)." if condition == "isolated" and task["group"] == sc.GROUPS[0] else references[task["task_id"]]
    def train(*args):
        return {"exposures": 180, "optimizer_steps": 24, "losses": [0.25] * 180}
    cfg = ex.read(ROOT / "research/protocols/phase3c_dev2_config.json")
    instrument = GocoCompiler(ROOT / cfg["compiler"]["java"], ROOT / cfg["compiler"]["path"], timeout_seconds=3)
    cache = {}
    fault = {"armed": False, "fired": False}
    class Memo:
        def run(self, source, stdin):
            key = source, stdin
            if key not in cache:
                cache[key] = instrument.run(source, stdin)
            return cache[key]
    from self_learning_ai import dev2r_evaluation as dev
    original_score = dev.score_source
    def injected_score_source(*args, **kwargs):
        if fault["armed"] and not fault["fired"]:
            fault["fired"] = True
            raise OSError(errno.EINVAL, "Invalid argument")
        return original_score(*args, **kwargs)
    dev.score_source = injected_score_source
    score = ex.compiler_score(Memo())
    a, b = out / "A", out / "B"
    for runtime in [a, b]:
        ex.run_training_cells(candidate, train, runtime_root=runtime)
        ex.run_own_training(candidate, generate, score, reset=random.seed, runtime_root=runtime)
        if runtime == a:
            ex.run_confirmatory(candidate, generate, score, reset=random.seed, runtime_root=a)
            report_a = ex.run_analysis(candidate, a)
            generated.clear()
    count = 0
    def injected(raw, task, cases, target, checkpoint_dir):
        nonlocal count
        fault["armed"] = count == 128
        count += 1
        try:
            return score(raw, task, cases, target, checkpoint_dir)
        finally:
            fault["armed"] = False
    stop(lambda: ex.run_confirmatory(candidate, generate, injected, reset=random.seed, runtime_root=b))
    assert fault["fired"] is True
    r_stem = b / "evaluations/20280223/isolated/confirmatory/CONF1-NC-AR-G1-R0"
    assert {p.name for p in Path(str(r_stem) + ".compiler").iterdir()} == {
        "CONF1-NC-AR-G1-R0.generation.json"}
    assert Path(str(r_stem) + ".raw.json").is_file()
    assert Path(str(r_stem) + ".started.json").is_file()
    assert not Path(str(r_stem) + ".score.json").exists()
    assert len(list(b.glob("evaluations/*/*/confirmatory/*.score.json"))) == 128
    incident = next((b / "incidents").glob("*.json"))
    expected_incident = {"error_type": "OSError", "evidence": {}, "reason": "[Errno 22] Invalid argument",
                         "stage": "confirmatory", "status": "STOP"}
    assert ex.read(incident) == expected_incident
    incident_hash = ex.sha256(incident)
    real_hash = "8563276e0f24ad726f9508e15ca449d759a6718748cf6f6cc9e0d7a4fa4d0db9"
    assert incident_hash == real_hash
    order = [(c["seed"], c["condition"], tid) for c in sc.cell_order() for tid in sc.confirmatory_order(
        {g: [t["task_id"] for t in tasks if t["group"] == g] for g in sc.GROUPS})]
    seed, condition, tid = order[128]
    assert (seed, condition, tid) == (20280223, "isolated", "CONF1-NC-AR-G1-R0")
    reviewed = {"amendment": "C15", "incident": incident.relative_to(b).as_posix(),
                "incident_sha256": incident_hash, "resume_index": 128,
                "resume_task": {"seed": seed, "condition": condition, "task_id": tid}}
    # Point the fixed production loader at an independently hash-bound fixture
    # repository; no production argument or bypass is introduced.
    replica = out / "fixture-repository"
    for name in ex.execution_bound_files() | set(manifest["code_hashes"]) | set(manifest["authority_hashes"]) | {
            cfg["compiler"]["path"], *[cfg["base_weights"]["local_path"] + "/" + n
                                      for n in manifest["tokenizer_hashes"]]}:
        target = replica / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    record = replica / ex.C15_REVIEWED_INCIDENT
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps(reviewed), encoding="utf-8")
    candidate_copy = out / "candidate-copy"
    shutil.copytree(candidate, candidate_copy)
    info = {"sha256": ex.sha256(record), "verified_sha256": ex.sha256(record), "verification": "byte-exact"}
    manifest["authority_hashes"][ex.C15_REVIEWED_INCIDENT] = info
    (candidate_copy / "candidate_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    ex.ROOT = replica
    candidate = candidate_copy
    broken = out / "broken"
    shutil.copytree(b, broken)
    prefix = {p.relative_to(b).as_posix(): p.read_bytes() for p in b.glob("evaluations/*/*/confirmatory/*.score.json")}
    assert len(prefix) == 128
    ex.run_confirmatory_c15_continuation(candidate, generate, score, reset=random.seed,
                                        reviewed_incident=reviewed, runtime_root=b)
    assert all((b / p).read_bytes() == raw for p, raw in prefix.items())
    assert len(generated) == 1240 and len(set(generated)) == 1240
    assert generated.count((seed, condition, "confirmatory", tid)) == 1
    rows_a = ex._score_records(ex.CheckpointStore(a), "confirmatory")
    rows_b = ex._score_records(ex.CheckpointStore(b), "confirmatory")
    assert len(rows_a) == len(rows_b) == 640 and rows_a == rows_b
    report_b = ex.run_analysis(candidate, b)
    assert report_a == report_b

    refusals = []
    stem = f"evaluations/{seed}/{condition}/confirmatory/{tid}"
    next_seed, next_condition, next_tid = order[129]
    faults = ["wrong_sha", "two_incidents", "no_incident", "marker", "complete", "later_started",
              "missing_raw", "present_score", "tampered_score", "stray", "wrong_index", "unauthorized"]
    for fault in faults:
        runtime = out / ("refusal-" + fault)
        shutil.copytree(broken, runtime)
        decision = json.loads(json.dumps(reviewed))
        if fault == "wrong_sha":
            decision["incident_sha256"] = "WRONG"
        elif fault == "two_incidents":
            (runtime / "incidents/extra.json").write_text("{}", encoding="utf-8")
        elif fault == "no_incident":
            shutil.rmtree(runtime / "incidents")
        elif fault == "marker":
            (runtime / "confirmatory_c15_continuation.started.json").write_text("{}", encoding="utf-8")
        elif fault == "complete":
            (runtime / "confirmatory_complete.json").write_text("{}", encoding="utf-8")
        elif fault == "later_started":
            ex.CheckpointStore(runtime).write(f"evaluations/{next_seed}/{next_condition}/confirmatory/{next_tid}.started.json", {})
        elif fault == "missing_raw":
            (runtime / (stem + ".raw.json")).unlink()
        elif fault == "present_score":
            (runtime / (stem + ".score.json")).write_text("{}", encoding="utf-8")
        elif fault == "tampered_score":
            next(runtime.glob("evaluations/*/*/confirmatory/*.score.json")).write_text("{}", encoding="utf-8")
        elif fault == "stray":
            (runtime / "evaluations/20280117/isolated/confirmatory/stray").write_text("extra", encoding="utf-8")
        elif fault == "wrong_index":
            decision["resume_index"] = 127
        elif fault == "unauthorized":
            manifest["model_execution_authorized"] = False
            (candidate / "candidate_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        before = inventory(runtime)
        stop(lambda: ex.run_confirmatory_c15_continuation(candidate, generate, score, reset=random.seed,
                                                        reviewed_incident=decision, runtime_root=runtime))
        after = inventory(runtime)
        assert all(after.get(p) == h for p, h in before.items())
        assert {p: h for p, h in after.items() if "/confirmatory/" in p} == {
            p: h for p, h in before.items() if "/confirmatory/" in p}
        refusals.append(fault)
    manifest["model_execution_authorized"] = True
    (candidate / "candidate_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    analysis_refusals = []
    for fault in ["unreviewed", "no_marker", "second_incident"]:
        runtime = out / ("analysis-" + fault)
        shutil.copytree(broken if fault == "no_marker" else b, runtime)
        (runtime / "analysis.json").unlink(missing_ok=True)
        (runtime / "output_inventory.json").unlink(missing_ok=True)
        if fault == "unreviewed":
            (runtime / reviewed["incident"]).write_text("{}", encoding="utf-8")
        elif fault == "second_incident":
            (runtime / "incidents/second.json").write_text("{}", encoding="utf-8")
        stop(lambda: ex.run_analysis(candidate, runtime))
        assert not (runtime / "analysis.json").exists()
        analysis_refusals.append(fault)
    save({"generation_count": len(generated), "prefix_unchanged": True, "identical_rows": True,
          "analysis_equal": True, "legitimate_analysis_differences": [], "incident_sha256": incident_hash,
          "incident_hash_matches_real": True, "continuation_refusals": refusals,
          "analysis_refusals": analysis_refusals, "distinct_compiler_runs": len(cache)})


if __name__ == "__main__":
    worker(sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]))
