"""I3 synthetic validation only; tokenizer files and compiler are mandatory."""

import copy
import hashlib
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from self_learning_ai.conf1_r1 import training
from self_learning_ai.conf1_r1.gates_primary import CompilerRunner, GateStop, InterpreterRunner, _memo
from self_learning_ai.conf1_r1.primary import load_primary_slots, primary_source

SYN_ARRAY_EVAL = ("0|0|0|0", "-14|16|-2|-15", "12|2|-1|5", "-16|-10|7|2", "-14|6|-6|4")
SYN_SEEDS = tuple(range(900001, 900006))
SLOTS = json.loads((ROOT / "research/protocols/phase3c_conf1_slots.json").read_bytes())["slots"]["training_paired_slots"]
PRIMARY = load_primary_slots(ROOT)


def emit(capsys, name, report):
    with capsys.disabled():
        print(name + ": " + json.dumps(report, sort_keys=True), flush=True)


@pytest.fixture(scope="module")
def records():
    return training.training_records()


@pytest.fixture(scope="module")
def selections():
    return [training.select_training_cases(slot, SYN_SEEDS[0], SYN_ARRAY_EVAL) for slot in SLOTS]


@pytest.fixture(scope="module")
def compiler():
    return _memo(CompilerRunner(ROOT))  # Never skip or substitute the interpreter.


def cases_for(records, selections):
    by_slot = {s["slot"]["slot_id"]: s for s in selections}
    return {r["record_id"]: [{"case_id": identifier, "stdin": stdin}
                              for identifier, stdin in zip(by_slot[r["slot_id"]]["case_ids"],
                                                           by_slot[r["slot_id"]]["inputs"])] for r in records}


def test_t1_all_units_classify(records, capsys):
    for record in records:
        classified = training.classify(record["target"], record["family"], "training")
        assert classified and all(row["kind"] in ("K1", "K2", "K3", "K4", "K5", "K6") for row in classified)
        from self_learning_ai.conf1_r1.interp import enumerate_mutants
        assert [row["index"] for row in classified] == [m[0] for m in enumerate_mutants(record["target"])[0]]
    for slot in PRIMARY:
        assert training.classify(primary_source(slot), slot["family"], "primary")
    emit(capsys, "I3 T1", {"status": "PASS", "training_programs": 120, "primary_references": 32})


@pytest.mark.parametrize("bad", ["total-=hitP.", "IF (hitP==1 && hitQ==1) { total+=1. }",
                                    "LOOP (NUMBER i=1 TILL i<=n, i++) { }", "DISPLAY(total)."])
def test_t1_known_bad_units_fail(records, bad):
    with pytest.raises(GateStop):
        training.classify(records[0]["target"] + "\n" + bad, "numeric_iteration", "training")


def test_t2_paired_scaffold(records, selections, capsys):
    result = training.p3_paired_scaffold(records, cases_for(records, selections))
    assert result["status"] == "PASS" and result["paired_slots"] == 60
    emit(capsys, "I3 T2", result)


@pytest.mark.parametrize("fault", ["condition_header", "predicate", "offset", "case_input"])
def test_t2_known_bad_scaffolds_fail(records, selections, fault):
    changed = copy.deepcopy(records)
    cases = cases_for(changed, selections)
    if fault == "condition_header":
        for record in changed[:2]:
            record["model_user_message"] = f"Task {record['record_id']}\n\n{record['prompt']}"
    elif fault == "predicate":
        changed[1]["target"] = changed[1]["target"].replace("i%2==1", "i%2==0")
    elif fault == "offset":
        changed[1]["target"] = changed[1]["target"].replace("NUMBER total=0.", "NUMBER total=2.")
        changed[1]["offset"] = 2
    else:
        cases[changed[1]["record_id"]][0]["stdin"] = "1"
    assert training.p3_paired_scaffold(changed, cases)["status"] == "FAIL"


def test_t3_exact_runner_token_parity(records, capsys):
    result = training.p3_token_parity(records, training.TOKENIZER_DIR)
    emit(capsys, "I3 T3", result)
    assert result["status"] == "PASS"
    assert all(values["examples"] == 60 for values in result["totals"].values())
    assert result["relative_differences"]["supervised"] <= 0.02
    assert result["relative_differences"]["full"] <= 0.05
    assert result["above_320"] == []


def test_t4_five_seed_regression(selections, capsys):
    path = "research/results/PHASE_3C_CONF1_PREFREEZE/r2_liveness_feasibility.json"
    expected_sha = next(a["sha256"] for a in training._authorities()[1]["evidence_artifacts"] if a["path"] == path)
    raw = (ROOT / path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected_sha
    evidence = json.loads(raw)
    expected = {(seed["seed"], row["slot"]): row for seed in evidence["e3"]["seeds"] for row in seed["slots"]}
    matched = 0
    for seed in SYN_SEEDS:
        actual = selections if seed == SYN_SEEDS[0] else [
            training.select_training_cases(slot, seed, SYN_ARRAY_EVAL) for slot in SLOTS]
        for selection in actual:
            reference = expected[seed, selection["slot"]["slot_id"]]
            assert selection["inputs"] == reference["inputs"], (seed, selection["slot"]["slot_id"])
            assert selection["selected_stream_indices"] == reference["selected_stream_indices"]
            assert selection["satisfied_after_each_pick"] == reference["satisfied_after_each_pick"]
            matched += 1
        emit(capsys, "I3 T4 seed", {"seed": seed, "matched_slots": len(actual), "mismatches": 0})
    emit(capsys, "I3 T4", {"matched_ordered_selections": matched, "seeds": list(SYN_SEEDS), "mismatches": 0})
    assert matched == 300


def test_t5_compiler_verification(selections, compiler, capsys):
    started, before = time.perf_counter(), compiler.calls
    reports = []
    for index, selection in enumerate(selections, 1):
        reports.append(training.verify_training_cases(selection, compiler))
        if index % 10 == 0:
            emit(capsys, "I3 T5 progress", {"verified_slots": index, "compiler_runs": compiler.calls - before,
                                           "wall_seconds": round(time.perf_counter() - started, 3)})
    result = {"status": "PASS", "verified_slots": len(reports), "compiler_runs": compiler.calls - before,
              "disagreements": sum(r["disagreements"] for r in reports),
              "wall_seconds": round(time.perf_counter() - started, 3)}
    emit(capsys, "I3 T5", result)
    assert len(reports) == 60 and all(r["status"] == "PASS" for r in reports)
    assert result["disagreements"] == 0 and result["compiler_runs"] > 0


def test_t6_catalog_liveness(selections, compiler, capsys):
    result = training.p4_catalog(selections, compiler)
    emit(capsys, "I3 T6", {**result, "rows": [{k: v for k, v in row.items() if k != "witnesses"}
                                               | {"witness_count": len(row["witnesses"])} for row in result["rows"]]})
    assert result["status"] == "PASS"
    assert result["classified_training"] == 120 and result["classified_primary"] == 32
    assert all(row["live"] for row in result["rows"] if row["required"])
    assert all(row["live"] == (row["condition"] == "isolated") for row in result["rows"] if row["row"] == "T-SUM")
    assert all(row["live"] == (row["condition"] == "composition") for row in result["rows"] if row["row"] == "T-JOINT")


def test_t7_primary_novelty(capsys):
    result = training.p5_novelty(PRIMARY)
    assert result["status"] == "PASS" and len(result["slots"]) == 32
    emit(capsys, "I3 T7", {"status": result["status"], "primary_functions": len(result["slots"])})


def test_t7_training_pair_function_fails():
    # G1 with Q and R both residue_two reduces exactly to odd_index*residue_two.
    slot = {"task_id": "synthetic-pair-function", "family": "numeric_iteration", "graph": "G1",
            "role_predicates": {"P": "odd_index", "Q": "residue_two", "R": "residue_two", "S": None}}
    result = training.p5_novelty([slot])
    assert result["status"] == "FAIL"
    assert result["slots"][0]["equals_pair_function"] is True


def test_t8_exhaustive_r2a_subset(records, compiler, capsys):
    manifest = training._authorities()[1]
    frozen = manifest["non_exempt_domain_equivalent_mutants"]
    by_record = {(r["slot_id"], r["condition"]): r for r in records}
    by_primary = {s["task_id"]: s for s in PRIMARY}
    pairs = [(identifier, condition) for identifier, condition, _ in frozen]
    exempt_slots = [slot for slot in SLOTS if training._r2_definitions().domain_disjoint(slot)]
    pairs += [(slot["slot_id"], "composition") for slot in exempt_slots]
    listed = {identifier for identifier, _, _ in frozen}
    others = [slot for slot in SLOTS if slot["slot_id"] not in listed][:5]
    pairs += [(slot["slot_id"], "isolated") for slot in others]
    assert len(pairs) == 27 and len(set(pairs)) == 27
    programs = []
    for identifier, condition in pairs:
        if condition == "primary":
            slot = by_primary[identifier]
            programs.append({"id": identifier, "kind": "primary", "condition": None,
                             "family": slot["family"], "source": primary_source(slot),
                             "exempt": False, "domain_disjoint": False})
        else:
            record = by_record[identifier, condition]
            exempt = any(s["slot_id"] == identifier for s in exempt_slots) and condition == "composition"
            programs.append({"id": identifier, "kind": "training", "condition": condition,
                             "family": record["family"], "source": record["target"],
                             "exempt": exempt, "domain_disjoint": exempt})
    evidence = json.loads((ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE/r2_liveness_feasibility.json").read_bytes())
    exempt_list = sorted([row["id"], row["condition"], m["mutant_index"]]
                         for row in evidence["e1"]["programs"] if row["exempt"] for m in row["equivalents"])
    started = time.perf_counter()
    actual = training.r2a_equivalence(programs, workers=4)
    assert actual == sorted(frozen + exempt_list)
    assert not any(row[0] in {s["slot_id"] for s in others} for row in actual)
    emit(capsys, "I3 T8", {"status": "PASS", "programs": len(programs), "non_exempt": frozen,
                           "domain_disjoint_composition": exempt_list,
                           "other_programs": [[s["slot_id"], "isolated"] for s in others],
                           "other_equivalents": [], "wall_seconds": round(time.perf_counter() - started, 3)})


def test_t9_fault_oracle_stops(compiler, capsys):
    reference = training._builder().train_source("isolated", SLOTS[0])

    class FaultOracle:
        def __init__(self):
            self.delegate = InterpreterRunner()

        def run(self, source, stdin):
            result = self.delegate.run(source, stdin)
            if source == reference and stdin == "0" and result[0] == "ok":
                return "ok", "1.0"
            return result

    selection = training.select_training_cases(SLOTS[0], SYN_SEEDS[0], SYN_ARRAY_EVAL, FaultOracle())
    with pytest.raises(GateStop, match="oracle/verifier disagreement") as caught:
        training.verify_training_cases(selection, compiler)
    report = caught.value.report
    assert report["kind"] == "oracle_verifier_disagreement" and report["stdin"] == "0"
    emit(capsys, "I3 T9", {key: report[key] for key in ("kind", "slot", "stdin", "oracle", "verifier")})
