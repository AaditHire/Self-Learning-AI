"""Full synthetic I4b rehearsal; all artifact writes remain outside the repo."""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from self_learning_ai.conf1_r1 import candidate, gates_primary as gates, interp, overlap, training
from self_learning_ai.conf1_r1.gates_primary import CompilerRunner, GateStop, InterpreterRunner
from self_learning_ai.conf1_r1.primary import load_primary_slots

SYN_ARRAY_I3 = ["0|0|0|0", "-14|16|-2|-15", "12|2|-1|5", "-16|-10|7|2", "-14|6|-6|4"]
ARRAY = [slot for slot in load_primary_slots(ROOT) if slot["family"] == "array_reduction"]


def emit(capsys, name, value):
    with capsys.disabled():
        print(name + ": " + json.dumps(value, sort_keys=True), flush=True)


def snapshot_repo():
    # Metadata only: never open a prohibited dataset or any model weights.
    return {path.relative_to(ROOT).as_posix(): (path.stat().st_size, path.stat().st_mtime_ns)
            for path in ROOT.rglob("*") if path.is_file()}


def prohibit_repo_writes(event, args):
    paths = []
    if event == "open":
        path, mode, flags = args
        if (isinstance(mode, str) and any(mark in mode for mark in "wax+")) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            paths = [path]
    elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.utime"):
        paths = [args[0]]
    elif event in ("os.rename", "os.link", "os.symlink"):
        paths = list(args[:2])
    for path in paths:
        if isinstance(path, (str, bytes, os.PathLike)) and Path(os.fsdecode(path)).resolve().is_relative_to(ROOT):
            raise GateStop("test attempted a write inside the repository", {"event": event, "path": os.fsdecode(path)})


# The test command also disables startup bytecode and pytest's cache provider.
sys.addaudithook(prohibit_repo_writes)


@pytest.fixture(scope="module")
def rehearsal(tmp_path_factory, request):
    capture = request.config.pluginmanager.getplugin("capturemanager")
    parent = tmp_path_factory.mktemp("conf1-i4b")
    out = parent / "dry"
    before = snapshot_repo()
    started = time.perf_counter()
    try:
        with capture.global_and_fixture_disabled():
            manifest = candidate.build_candidate(900001, out, label="SYNTHETIC_DRY_RUN", workers=8)
    except GateStop as exc:
        with capture.global_and_fixture_disabled():
            print("I4b T2 ACTUAL STOP: " + json.dumps({"out_dir": str(out), "STOP_report": str(out / "STOP_report.json"),
                                           "gate": exc.report.get("gate"), "reason": exc.report.get("reason"),
                                           "evidence": exc.report.get("evidence"),
                                           "wall_seconds": time.perf_counter() - started}), flush=True)
        pytest.exit("STOP: full synthetic dry-run gate failure", returncode=2)
    after = snapshot_repo()
    if before != after:
        changed = sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))
        with capture.global_and_fixture_disabled():
            print("I4b T3 REPO WRITE STOP: " + json.dumps(changed), flush=True)
        pytest.exit("STOP: repository changed during rehearsal", returncode=2)
    return {"out": out, "manifest": manifest, "wall_seconds": time.perf_counter() - started,
            "before": before, "after": after,
            "gates": json.loads((out / "gates/gate_report.json").read_bytes()),
            "log": json.loads((out / "construction_log.json").read_bytes())}


def test_t1_refusals_before_work(tmp_path, monkeypatch, capsys):
    spec = importlib.util.spec_from_file_location("_i4b_cli", ROOT / "scripts/build_phase3c_conf1_candidate.py")
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)

    def forbidden(*args, **kwargs):
        pytest.fail("refusal must precede file or compiler work")

    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", forbidden)
        patch.setattr(Path, "mkdir", forbidden)
        patch.setattr(candidate, "CompilerRunner", forbidden)
        patch.setattr(candidate, "_authorities", forbidden)
        with pytest.raises(GateStop, match="explicit authorization"):
            candidate.build_candidate(candidate.CONSTRUCTION_SEED, tmp_path / "refused",
                                      label="CONF1_CONSTRUCTION", workers=8)
        args = cli.parser().parse_args(["--seed", str(candidate.CONSTRUCTION_SEED), "--out", str(tmp_path / "refused")])
        # Exercise only the shared CLI refusal guard; never run the CLI with this seed.
        with pytest.raises(GateStop, match="explicit authorization"):
            cli.validate_cli(args)
    with pytest.raises(GateStop, match="existing output"):
        candidate.build_candidate(900001, tmp_path, label="SYNTHETIC_DRY_RUN", workers=8)
    assert cli.main(["--seed", "900001", "--out", str(tmp_path)]) == 2
    assert list(tmp_path.iterdir()) == []
    emit(capsys, "I4b T1", {"API_and_CLI_guard_refused_before_work": True, "existing_out_refused": True,
                            "CLI_with_construction_seed_invoked": False})


def test_t2_full_dry_run(rehearsal, capsys):
    result, reports, log = rehearsal["manifest"], rehearsal["gates"], rehearsal["log"]
    assert result["status"] == "CANDIDATE_GATES_PASSED_NOT_FROZEN"
    assert all(value == "PASS" for value in result["gate_summary"].values())
    selected = log["primary_array_selection"]
    ledger, _, _ = training._authorities()
    old = {slot["slot_id"]: training.select_training_cases(slot, 900001, SYN_ARRAY_I3)
           for slot in ledger["slots"]["training_paired_slots"]}
    differences = []
    summaries = []
    for selection in log["training_selections"]:
        identifier = selection["slot"]["slot_id"]
        summaries.append({"slot_id": identifier, "inputs": selection["inputs"],
                          "stream_indices": selection["selected_stream_indices"], "skips": selection["skipped"],
                          "satisfied": selection["satisfied_after_each_pick"], "requirements": selection["requirements_total"]})
        if selection["inputs"] != old[identifier]["inputs"] or selection["selected_stream_indices"] != old[identifier]["selected_stream_indices"]:
            assert selection["slot"]["family"] == "array_reduction"
            old_stream = training.training_case_stream(selection["slot"], 900001, SYN_ARRAY_I3)
            new_stream = training.training_case_stream(selection["slot"], 900001, selected["selected_inputs"])
            assert old_stream != new_stream
            differences.append({"slot_id": identifier, "I3_inputs": old[identifier]["inputs"],
                                "I4b_inputs": selection["inputs"], "reason": "selected synthetic array evaluation exclusions changed",
                                "old_skips": old_stream["skipped"], "new_skips": new_stream["skipped"]})
    p6 = {}
    for domain in training.DOMAINS:
        row = reports["P6_" + domain]
        p6[domain] = {key: row[key] for key in ("status", "pair_requirements", "mutant_requirements", "unkilled_mutants",
                                              "unseparated_pairs", "excluded_r2a", "case_classes")}
    file_list = {p.relative_to(rehearsal["out"]).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(rehearsal["out"].rglob("*")) if p.is_file()}
    p4 = [{key: row[key] for key in ("condition", "domain", "row", "required", "live")} for row in reports["P4"]["rows"]]
    p7 = {key: value for key, value in reports["P7"].items() if key != "descriptive"}
    p7["canonical_descriptive"] = {name: {key: value for key, value in row.items() if key != "by_task"}
                                    for name, row in reports["P7"]["descriptive"].items()}
    emit(capsys, "I4b T2 FULL REPORT", {"output_dir": str(rehearsal["out"]), "status": result["status"],
        "array_inputs": selected["selected_inputs"], "array_pool_indices": selected["selected_indices"],
        "array_satisfied_after_each_pick": selected["requirement_counts_after_each_pick"], "P6": p6,
        "P2_counts": {"primary": len(reports["P2_PRIMARY"]["items"]), "training": len(reports["P2_TRAINING"]["items"])},
        "training_selection_summary": summaries, "I3_selection_differences": differences,
        "P3_scaffold": reports["P3_SCAFFOLD"], "P3_tokens": reports["P3_TOKENS"], "P4_table": p4,
        "R2_A": reports["R2_A_RECOMPUTE"], "secondary": reports["SECONDARY_FINAL"], "P7": p7,
        "consumed_format": reports["CONSUMED_FORMAT"], "files_sha256": file_list,
        "compiler_runs": reports["COMPILER_RUNS"], "total_wall_seconds": rehearsal["wall_seconds"],
        "step_timings_seconds": log["timings_seconds"]})


def test_t3_manifest_integrity_and_repo_snapshot(rehearsal, capsys):
    manifest, out = rehearsal["manifest"], rehearsal["out"]
    assert manifest["model_execution_authorized"] is False
    assert json.loads((out / "candidate_manifest.json").read_bytes()) == manifest
    for name, expected in manifest["file_sha256"].items():
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == expected
    for name, expected in manifest["code_hashes"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
    for name, entry in manifest["authority_hashes"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == entry["sha256"]
    assert rehearsal["before"] == rehearsal["after"] == snapshot_repo()
    assert len(list(p for p in out.rglob("*") if p.is_file())) == 10
    emit(capsys, "I4b T3", {"payload_hashes_verified": len(manifest["file_sha256"]),
                            "model_execution_authorized": False, "repo_snapshot_unchanged": True})


def test_t4_primary_gate_fault(tmp_path, monkeypatch, capsys):
    out = tmp_path / "fault"
    monkeypatch.setattr(gates, "p1_nondegeneracy", lambda slots: {"status": "FAIL", "fault": "synthetic P1 fault"})
    with pytest.raises(GateStop) as stopped:
        candidate.build_candidate(900001, out, label="SYNTHETIC_DRY_RUN", workers=8)
    assert sorted(p.name for p in out.iterdir()) == ["STOP_report.json"]
    report = json.loads((out / "STOP_report.json").read_bytes())
    assert report["gate"] == "P1" and report["evidence"]["status"] == "FAIL"
    assert stopped.value.report == report
    emit(capsys, "I4b T4", {"gate": report["gate"], "STOP_report_only": True, "candidate_data_written": False})


def test_t5_r2a_synthetic_primary_selection(capsys):
    started = time.perf_counter()
    result = gates.select_array_cases(ARRAY, gates.array_pool(777001), verifier=CompilerRunner(ROOT),
                                      excluded_mutants=[("CONF1-NC-AR-G1-R3", 14)])
    assert result["status"] == "PASS"
    assert result["total_requirements"] == result["requirement_counts_after_each_pick"][-1] == 567
    assert result["mutant_requirements"] == 447 and result["pair_requirements"] == 120
    assert result["unkilled_mutants"] == result["unseparated_pairs"] == []
    assert [(row["id"], row["index"]) for row in result["excluded_r2a"]] == [("CONF1-NC-AR-G1-R3", 14)]
    emit(capsys, "I4b T5", {key: result[key] for key in ("status", "total_requirements", "requirement_counts_after_each_pick",
         "selected_indices", "selected_inputs", "excluded_r2a", "unkilled_mutants", "unseparated_pairs")}
         | {"wall_seconds": time.perf_counter() - started})


def test_default_gate_reports_byte_identical():
    raw = subprocess.check_output(["git", "show", "HEAD:src/self_learning_ai/conf1_r1/gates_primary.py"], cwd=ROOT)
    old = {"__file__": str(ROOT / "src/self_learning_ai/conf1_r1/gates_primary.py"), "__name__": "_i4b_original_gates"}
    exec(compile(raw, old["__file__"], "exec"), old)
    slots = ARRAY[:1]
    inputs = ["0|0|0|0", "3|-4|7|-1", "-2|6|1|5", "5|2|-6|0", "-1|-3|4|8"]
    previous = old["p6_check"](slots, inputs, InterpreterRunner())
    current = gates.p6_check(slots, inputs, InterpreterRunner())
    assert json.dumps(previous) == json.dumps(current)


def test_t6_canonical_format(rehearsal, capsys):
    out = rehearsal["out"]
    counts = {}
    for name in ("training/isolated_cases.json", "training/composition_cases.json", "evaluation/hidden_cases.json"):
        population = json.loads((out / name).read_bytes())
        count = 0
        for cases in population.values():
            assert len(cases) == 5
            for case in cases:
                assert set(case) == {"case_id", "stdin", "expected_stdout"}
                assert case["stdin"].endswith("\n") and not case["stdin"].endswith("\n\n")
                value = float(case["expected_stdout"])
                assert value.is_integer() and case["expected_stdout"] == str(float(int(value)))
                count += 1
        counts[name] = count
    inv = rehearsal["gates"]["CONSUMED_INVENTORY"]["inventory"]
    known = next(row for row in overlap._consumed(inv, ("cases",)) if row["value"] == "0\n"
                 and row["expected_stdout"] == "0.0")
    made = candidate.canonical_cases("known-consumed-format", [known["value"]] * 5, [0] * 5)[0]
    assert (made["stdin"], made["expected_stdout"]) == (known["value"], known["expected_stdout"])
    assert interp.interpret("NUMBER n. INPUT(n). DISPLAYNL(n).", made["stdin"]) == ("ok", "0.0")
    emit(capsys, "I4b T6", {"canonical_case_counts": counts, "consumed_case":
                            {key: known[key] for key in ("path", "id", "case_id")}, "identical_parse": True})
