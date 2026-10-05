"""I1 subset and compiler agreement; generated programs remain in memory."""

import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import build_phase3c_conf1_data as builder

from self_learning_ai.compiler import GocoCompiler, normalized_program_output
from self_learning_ai.conf1_r1.interp import enumerate_mutants, interpret, split_statements
from self_learning_ai.conf1_r1.primary import load_primary_slots, primary_source

SLOTS = load_primary_slots(ROOT)
INPUTS = {
    "numeric_iteration": ("0", "1", "7", "12", "70"),
    "array_reduction": ("0|0|0|0", "3|-4|7|-1", "-2|6|1|5", "5|2|-6|0", "-1|-3|4|8"),
}
MUTANT_COUNTS = {
    "numeric_iteration": {"G1": 16, "G2": 24, "G3": 24, "G4": 25},
    "array_reduction": {"G1": 23, "G2": 31, "G3P": 26, "G4": 32},
}


def pinned_compiler():
    jar = ROOT / ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar"
    java = ROOT / ".tools/jdk-25.0.1+8/bin/java.exe"
    assert java.is_file(), f"STOP: pinned JDK missing: {java}"
    assert jar.is_file(), f"STOP: pinned compiler JAR missing: {jar}"
    digest = hashlib.sha256(jar.read_bytes()).hexdigest()
    assert digest == "42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb", f"STOP: JAR SHA-256 mismatch: {digest}"
    return GocoCompiler(java, jar)


PROBES = (
    ("A", "total+=hitP*hitQ. total+=hitQ*hitR. total+=hitR*hitS.", "syntax", "",
     "Syntax Error: Missing statement terminator '.' at line 8, column 182\r\n"),
    ("B", "total+=(hitP*hitQ). total+=(hitQ*hitR). total+=(hitR*hitS).", "success", "Enter value for n: 2.0\r\n", ""),
    ("C", "total+=hitP. total+=hitQ.", "syntax", "",
     "Syntax Error: Missing statement terminator '.' at line 8, column 177\r\n"),
    ("D", "total+=(hitP). total+=(hitQ).", "success", "Enter value for n: 6.0\r\n", ""),
    ("E", "total+=hitP*hitQ.", "success", "Enter value for n: 1.0\r\n", ""),
    ("F", "total+=hitP*hitQ. IF (i%2==1) { hitP=1. }", "success", "Enter value for n: 1.0\r\n", ""),
)


@pytest.mark.compiler_cross_validation
@pytest.mark.parametrize("letter,accumulations,phase,stdout,stderr", PROBES, ids=[probe[0] for probe in PROBES])
def test_observed_compiler_probes(letter, accumulations, phase, stdout, stderr, capsys):
    slot = next(slot for slot in SLOTS if slot["task_id"] == "CONF1-NC-NU-G2-R0")
    canonical = primary_source(slot)
    parenthesized = "total+=(hitP*hitQ). total+=(hitQ*hitR). total+=(hitR*hitS)."
    assert canonical.count(parenthesized) == 1
    source = canonical.replace(parenthesized, accumulations)
    if letter == "E":
        source = source.replace("total+=hitP*hitQ. }", "total+=hitP*hitQ.}")
    result = pinned_compiler().run(source, "7\n")
    assert (result.phase, result.stdout, result.stderr) == (phase, stdout, stderr)
    expected = ("ok", normalized_program_output(stdout)) if phase == "success" else ("fail",)
    assert interpret(source, "7") == expected
    with capsys.disabled():
        print("I1 probe: " + json.dumps({"probe": letter, "phase": result.phase,
                                         "stdout": result.stdout, "stderr": result.stderr}), flush=True)


def test_scanner_periods_strings_blocks_and_preorder_deletion():
    source = ('IMPORT strings. SENTENCE line="a.b\\\".c". '
              'SENTENCE[] parts=strings.SPLIT(line,"|"). '
              'NUMBER i=1. LOOP (i>=1) { IF (i==1) { i-=1. } DISPLAYNL(i). }')
    units = split_statements(source)
    assert [unit.kind for unit in units] == ["simple"] * 4 + ["LOOP"]
    assert units[0].text == "IMPORT strings."
    assert units[2].text == 'SENTENCE[] parts=strings.SPLIT(line,"|").'
    assert [unit.kind for unit in units[-1].children] == ["IF", "simple"]
    mutants, counts = enumerate_mutants(source)
    assert counts == {"total": 8, "simple": 6, "IF": 1, "LOOP": 1}
    assert "LOOP" not in mutants[4][2]
    assert "IF" not in mutants[5][2] and "LOOP" in mutants[5][2]
    assert "i-=1." not in mutants[6][2] and "IF" in mutants[6][2]
    assert "DISPLAYNL(i)." not in mutants[7][2]


@pytest.mark.parametrize("slot", SLOTS, ids=lambda s: s["task_id"])
def test_mutants_stable_complete_and_exactly_one_span_removed(slot):
    source = primary_source(slot)
    mutants, counts = enumerate_mutants(source)
    assert (mutants, counts) == enumerate_mutants(source)
    assert counts["total"] == MUTANT_COUNTS[slot["family"]][slot["graph"]]
    assert counts["total"] == counts["simple"] + counts["IF"] + counts["LOOP"]
    assert counts["LOOP"] == 1
    assert counts["IF"] == {"G1": 3, "G2": 4, "G3": 4, "G3P": 3, "G4": 5}[slot["graph"]]
    flattened = []

    def visit(units):
        for unit in units:
            flattened.append(unit)
            visit(unit.children)

    visit(split_statements(source))
    assert len(mutants) == len(flattened)
    for (index, description, mutant), unit in zip(mutants, flattened):
        assert index == flattened.index(unit)
        assert mutant != source
        assert mutant == source[:unit.start] + source[unit.end:]
        assert f"[{unit.start}:{unit.end})" in description


@pytest.mark.parametrize("source", [
    "NUMBER x=0", "NUMBER x=0. IF (x==0) { x=1.", "NUMBER x=0. }",
    "DISPLAYNL(missing).", "NUMBER x=0. IF (x<0) { DISPLAYNL(missing). }",
    "NUMBER x=0. WHILE (x<1) { x+=1. }", "NUMBER x=0. DISPLAYNL(x/2).",
    "NUMBER x=0. IF (x==0 && x<1) { x=1. }", "NUMBER x=0. DISPLAY(x).",
    'IMPORT strings. SENTENCE x="unterminated.',
    'SENTENCE x="1". NUMBER n=strings.TO_NUMBER(x). DISPLAYNL(n).',
    'IMPORT strings. SENTENCE x="1". NUMBER n=strings.UNKNOWN(x). DISPLAYNL(n).',
    'IMPORT strings. SENTENCE x="1". SENTENCE[] a=strings.SPLIT(x,",").',
    "NUMBER[] x=[1,2]. DISPLAYNL(x[-1]).", "NUMBER x=0. NUMBER x=1.",
    "NUMBER x=0. LOOP (NUMBER i=1 TILL i<2, j++) { x+=1. }",
    "NUMBER x=0. IF (x) { x=1. }",
])
def test_fail_closed(source):
    assert interpret(source) == ("fail",)


def test_reverse_loop_timeout_and_signed_remainder():
    assert interpret("NUMBER i=3. LOOP (i>=0) { i-=1. } DISPLAYNL(i).") == ("ok", "-1.0")
    assert interpret("NUMBER i=1. LOOP (i>=0) {}", step_limit=20) == ("timeout",)
    assert interpret("NUMBER x=-3. DISPLAYNL(x%2).") == ("ok", "-1.0")
    assert interpret("NUMBER x. INPUT(x). DISPLAYNL(x).", "bad") == ("fail",)


@pytest.mark.compiler_cross_validation
def test_all_references_mutants_and_training_against_pinned_compiler(capsys):
    """Run with the compiler_cross_validation marker registered via pytest -o.

    Missing/mismatched dependencies fail the task; this test is never skipped.
    Non-success and timeout outcomes compare as failure, per I1.
    """
    compiler = pinned_compiler()
    programs, mutant_total = [], 0
    for slot in SLOTS:
        source = primary_source(slot)
        programs.append((slot["task_id"], slot["family"], source))
        mutants, counts = enumerate_mutants(source)
        mutant_total += counts["total"]
        programs.extend((f"{slot['task_id']} mutant {index}: {description}", slot["family"], mutant)
                        for index, description, mutant in mutants)
    # The task explicitly authorizes these 60 training slots and both treatments.
    ledger = json.loads((ROOT / "research/protocols/phase3c_conf1_slots.json").read_bytes())
    training = ledger["slots"]["training_paired_slots"]
    assert len(training) == 60
    for slot in training:
        for condition in ("isolated", "composition"):
            programs.append((f"{slot['slot_id']} {condition}", slot["family"], builder.train_source(condition, slot)))
    assert mutant_total == 804 and len(programs) == 956
    jobs = [(name, source, stdin) for name, family, source in programs for stdin in INPUTS[family]]
    assert len(jobs) == 4780

    def compare(job):
        name, source, stdin = job
        result = compiler.run(source, stdin + "\n")
        compiled = ("ok", normalized_program_output(result.stdout)) if result.phase == "success" else ("fail",)
        interpreted = interpret(source, stdin)
        compared = interpreted if interpreted[0] == "ok" else ("fail",)
        if compared != compiled:
            return (name, source, stdin, interpreted, compiled, result.as_dict())
        return None

    started, completed = time.perf_counter(), 0
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Bounded batches stop promptly at a disagreement and retain the exact case.
        for start in range(0, len(jobs), 100):
            outcomes = list(executor.map(compare, jobs[start:start + 100]))
            completed += len(outcomes)
            disagreements = [result for result in outcomes if result is not None]
            if disagreements:
                with capsys.disabled():
                    print(f"I1 cross-validation stopped: runs={completed}, disagreements={len(disagreements)}, wall_seconds={time.perf_counter() - started:.3f}", flush=True)
                pytest.fail("Interpreter/compiler disagreement:\n" + json.dumps(disagreements, indent=2))
            if completed % 400 == 0:
                with capsys.disabled():
                    print(f"I1 compiler comparison: {completed}/{len(jobs)} agreed", flush=True)
    statistics = {"primary_references": 32, "mutants": mutant_total, "training_programs": 120,
                  "programs": len(programs), "inputs_per_program": 5,
                  "distinct_inputs": 10, "compiler_runs": completed, "disagreements": 0,
                  "wall_seconds": round(time.perf_counter() - started, 3),
                  "mutants_per_reference_by_domain_graph": MUTANT_COUNTS}
    with capsys.disabled():
        print("I1 cross-validation: " + json.dumps(statistics, sort_keys=True), flush=True)
