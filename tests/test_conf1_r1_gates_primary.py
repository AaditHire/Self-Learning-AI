"""I2 synthetic validation only; compiler dependencies are mandatory."""

import copy
import json
import random
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from self_learning_ai.conf1_r1.gates_primary import (
    CompilerRunner, GateStop, InterpreterRunner, array_pool, kill_matrix,
    p1_nondegeneracy, p2_e1, p6_check, select_array_cases,
)
from self_learning_ai.conf1_r1.primary import load_primary_slots, primary_source

SLOTS = load_primary_slots(ROOT)
ARRAY = [slot for slot in SLOTS if slot["family"] == "array_reduction"]
NUMERIC = [slot for slot in SLOTS if slot["family"] == "numeric_iteration"]
SYNTHETIC_NUMERIC = (0, 5, 9, 31, 64)
SYNTHETIC_ARRAY = ("0|0|0|0", "3|-4|7|-1", "-2|6|1|5", "5|2|-6|0", "-1|-3|4|8")


@pytest.fixture(scope="module")
def compiler():
    return CompilerRunner(ROOT)  # Never skip: missing/mismatched tools are STOP.


def emit(capsys, name, record):
    with capsys.disabled():
        print(name + ": " + json.dumps(record, sort_keys=True), flush=True)


def test_t1_p1_matches_committed_functions(capsys):
    result = p1_nondegeneracy(SLOTS)
    assert result["status"] == "PASS"
    recorded = json.loads((ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE/r1_specification_feasibility.json").read_bytes())
    expected = {row["task_id"]: row["function"] for row in recorded["frozen_primary_slots"]
                if row["family"] == "numeric_iteration"}
    expected.update({row["task_id"]: row["function"] for row in recorded["r1_array_primary_slots"]})
    assert {row["task_id"]: row["function"] for row in result["slots"]} == expected
    emit(capsys, "T1", {"status": result["status"], "matched_functions": len(expected),
                       "degenerate": [], "colliding": []})


def test_t2_pre_r1_array_degeneracy(capsys):
    ledger = json.loads((ROOT / "research/protocols/phase3c_conf1_slots.json").read_bytes())
    old_array = [slot for slot in ledger["slots"]["primary"] if slot["family"] == "array_reduction"]
    result = p1_nondegeneracy(old_array)
    bad = {row["graph"] + "R" + str(row["rotation"]) for row in result["slots"] if row["degenerate"]}
    assert result["status"] == "FAIL"
    assert bad == {"G1R2", "G1R3", "G2R1", "G2R2", "G2R3", "G3R0", "G3R3", "G4R2"}
    emit(capsys, "T2", {"status": result["status"], "degenerate": sorted(bad)})


@pytest.mark.slow
def test_t3_deletion_liveness(compiler):
    source = primary_source(NUMERIC[0])
    good = kill_matrix(source, SYNTHETIC_NUMERIC, compiler)
    assert good["status"] == "PASS" and good["unkilled"] == []
    assert "hitP=0. hitOr=0." in source
    duplicate = source.replace("hitP=0. hitOr=0.", "hitP=0. hitP=0. hitOr=0.")
    bad = kill_matrix(duplicate, SYNTHETIC_NUMERIC, compiler)
    assert bad["status"] == "FAIL" and len(bad["unkilled"]) >= 2
    with pytest.raises(GateStop, match="reference fails"):
        kill_matrix("NUMBER total=. DISPLAYNL(total).", SYNTHETIC_NUMERIC, compiler)


@pytest.mark.slow
def test_t4_p2_wrong_expected_and_bad_source(compiler):
    source = "NUMBER total=2. DISPLAYNL(total)."
    result = p2_e1([
        ("correct", source, [("7", 2)]),
        ("wrong", source, [("7", 3)]),
        ("syntax", "NUMBER total=. DISPLAYNL(total).", [("7", 2)]),
    ], compiler)
    assert result["status"] == "FAIL"
    assert [row["status"] for row in result["items"]] == ["PASS", "FAIL", "FAIL"]
    assert p2_e1([("correct", source, [("7", 2)])], compiler)["status"] == "PASS"


@pytest.mark.slow
def test_t5_p6_pair_and_class_failures(compiler):
    duplicate = copy.deepcopy(ARRAY[0])
    duplicate["task_id"] = "synthetic-duplicate"
    identical = p6_check([ARRAY[0], duplicate], SYNTHETIC_ARRAY, compiler)
    assert identical["status"] == "FAIL"
    assert identical["unseparated_pairs"] == [(ARRAY[0]["task_id"], "synthetic-duplicate")]
    no_zero = ("1|-2|3|-4", "3|-4|7|-1", "-2|6|1|5", "5|2|-6|1", "-1|-3|4|8")
    array_result = p6_check([ARRAY[0]], no_zero, compiler)
    assert array_result["status"] == "FAIL"
    assert array_result["case_classes"]["missing"] == ["ZERO_PRESENT"]
    numeric_result = p6_check([NUMERIC[0]], (1, 5, 9, 31, 64), compiler)
    assert numeric_result["status"] == "FAIL"
    assert set(numeric_result["case_classes"]["missing"]) == {"SIGN_ZERO", "EMPTY_LOOP", "LOWER_DOMAIN_BOUNDARY"}


@pytest.mark.slow
def test_t6_oracle_fault_stops(compiler, capsys):
    target = primary_source(ARRAY[0])

    class FaultOracle:
        def __init__(self):
            self.delegate = InterpreterRunner()

        def run(self, source, stdin):
            result = self.delegate.run(source, stdin)
            if source == target and stdin == "0|0|0|0" and result[0] == "ok":
                return "ok", str(float(result[1]) + 1.0)
            return result

    with pytest.raises(GateStop, match="oracle/verifier disagreement") as caught:
        select_array_cases([ARRAY[0]], SYNTHETIC_ARRAY, FaultOracle(), compiler)
    record = caught.value.report
    assert record["kind"] == "oracle_verifier_disagreement"
    assert record["stdin"] == "0|0|0|0"
    emit(capsys, "T6", {key: record[key] for key in ("kind", "stdin", "oracle", "verifier", "selected_indices", "selected_inputs")})


def test_explicit_pool_order_and_lowest_index_ties():
    # A tiny synthetic fixture checks the exact greedy tie rule, independently
    # of the full synthetic feasibility run and its observed outcome.
    pool = array_pool(seed=777002)
    assert len(pool) == 4097 and pool[0] == "0|0|0|0"
    rng = random.Random(777002)
    assert pool[1:4] == ["|".join(str(rng.randint(-16, 16)) for _ in range(4)) for _ in range(3)]

    class ConstantRunner:
        def run(self, source, stdin):
            return "ok", "0.0"

    # Zero-valued oracle/verifier output makes all pair and kill scores tie.
    # To avoid invented expected semantics, use a zero-only domain fixture:
    # the reference expected check is zero on every repeated-zero input.
    with pytest.raises(GateStop) as caught:
        select_array_cases([ARRAY[0]], ["0|0|0|0"] * 7, ConstantRunner(), ConstantRunner())
    assert caught.value.report["kind"] == "selection_unsatisfied"
    assert caught.value.report["selected_indices"] == [0, 1, 2, 3, 4]
    assert caught.value.report["requirement_counts_after_each_pick"] == [0] * 5


@pytest.mark.slow
def test_t7_synthetic_array_selection(compiler, capsys):
    class ProgressOracle:
        def __init__(self):
            self.delegate = InterpreterRunner()
            self.calls = 0
            self.last = time.perf_counter()

        def run(self, source, stdin):
            self.calls += 1
            now = time.perf_counter()
            if now - self.last >= 30:
                with capsys.disabled():
                    print(f"T7 synthetic selector: {self.calls} oracle runs", flush=True)
                self.last = now
            return self.delegate.run(source, stdin)

    started = time.perf_counter()
    try:
        result = select_array_cases(ARRAY, array_pool(seed=777001), ProgressOracle(), compiler)
    except GateStop as stop:
        # A synthetic gate failure is evidence. Disagreements remain hard STOP.
        if stop.report.get("kind") != "selection_unsatisfied":
            raise
        result = stop.report
    assert result["disagreements"] == 0
    assert len(result["selected_indices"]) == len(result["selected_inputs"]) == 5
    assert result["pair_requirements"] == 120 and result["mutant_requirements"] == 448
    assert result["status"] == result["verification"]["status"]
    assert result["status"] in ("PASS", "FAIL")
    record = {key: value for key, value in result.items() if key != "verification"}
    record["unkilled_count"] = len(result["unkilled_mutants"])
    record["unseparated_count"] = len(result["unseparated_pairs"])
    record["wall_seconds"] = round(time.perf_counter() - started, 3)
    emit(capsys, "T7 SYNTHETIC FEASIBILITY ONLY", record)


@pytest.mark.slow
def test_t8_synthetic_numeric_check(compiler, capsys):
    started = time.perf_counter()
    result = p6_check(NUMERIC, SYNTHETIC_NUMERIC, compiler)
    assert result["pair_requirements"] == 120 and result["mutant_requirements"] == 356
    assert result["status"] in ("PASS", "FAIL")
    record = {key: value for key, value in result.items() if key != "kill_matrices"}
    record["unkilled_count"] = len(result["unkilled_mutants"])
    record["unseparated_count"] = len(result["unseparated_pairs"])
    record["wall_seconds"] = round(time.perf_counter() - started, 3)
    emit(capsys, "T8 SYNTHETIC FEASIBILITY ONLY", record)
