"""R1 primary gates and deterministic selection; no construction or file writes.

Calling the selector on a construction pool requires separate authorization.
The compiler supplies gate verdicts; the accepted I1 interpreter is an oracle.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import random
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from self_learning_ai.compiler import GocoCompiler, normalized_program_output
from self_learning_ai.conf1_r1 import interp
from self_learning_ai.conf1_r1.primary import primary_expected, primary_source


ROOT = Path(__file__).resolve().parents[3]
JAR_SHA256 = "42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb"
_spec = importlib.util.spec_from_file_location(
    "_conf1_r1_feasibility_authority", ROOT / "scripts/audit_phase3c_conf1_r1_specification_feasibility.py"
)
if _spec is None or _spec.loader is None:
    raise ImportError("R1 feasibility authority unavailable")
_audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_audit)  # Definitions only; never call its writing main().


class GateStop(ValueError):
    """A STOP with structured evidence, including synthetic feasibility failures."""

    def __init__(self, message: str, report: dict | None = None):
        super().__init__("STOP: " + message)
        self.report = report or {}


class CompilerRunner:
    parallel_safe = True

    def __init__(self, root: str | Path = ROOT):
        root = Path(root)
        jar = root / ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar"
        java = root / ".tools/jdk-25.0.1+8/bin/java.exe"
        if not java.is_file() or not jar.is_file():
            raise GateStop("pinned JDK or JAR unavailable")
        digest = hashlib.sha256(jar.read_bytes()).hexdigest()
        if digest != JAR_SHA256:
            raise GateStop(f"pinned JAR SHA-256 mismatch: expected {JAR_SHA256}, actual {digest}")
        self.compiler = GocoCompiler(java, jar)

    def run(self, source: str, stdin: str) -> tuple[str, str]:
        result = self.compiler.run(source, stdin if stdin.endswith("\n") else stdin + "\n")
        if result.phase == "success":
            return "ok", normalized_program_output(result.stdout)
        return "fail", result.phase


class InterpreterRunner:
    """I1 execution with only input-independent static failures cached."""

    parallel_safe = False

    def __init__(self):
        self._static_failures: dict[str, bool] = {}

    def run(self, source: str, stdin: str) -> tuple[str, str]:
        if source not in self._static_failures:
            try:
                interp._compile(interp.split_statements(source), {}, set())
            except (ValueError, TypeError, KeyError, IndexError, RecursionError):
                self._static_failures[source] = True
            else:
                self._static_failures[source] = False
        if self._static_failures[source]:
            return "fail", "interpreter_static"
        outcome = interp.interpret(source, stdin)
        return outcome if outcome[0] == "ok" else ("fail", outcome[0])


def _runner(runner):
    return runner() if isinstance(runner, type) else runner


def _comparison(outcome: tuple[str, str]) -> tuple:
    # I1 convention: all non-success phases, including timeouts, compare as fail.
    return outcome if outcome[0] == "ok" else ("fail",)


class _MemoRunner:
    """Per-invocation caching; parallel prefetch does not alter outcome order."""

    def __init__(self, runner):
        self.runner = _runner(runner)
        self.cache: dict[tuple[str, str], tuple[str, str]] = {}
        self.calls = 0

    def run(self, source, stdin):
        key = (source, stdin)
        if key not in self.cache:
            self.cache[key] = self.runner.run(source, stdin)
            self.calls += 1
        return self.cache[key]

    def prefetch(self, jobs):
        missing = list(dict.fromkeys(job for job in jobs if job not in self.cache))
        if getattr(self.runner, "parallel_safe", False) and missing:
            with ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(lambda job: self.runner.run(*job), missing))
            self.cache.update(zip(missing, results))
            self.calls += len(missing)
        else:
            for source, stdin in missing:
                self.run(source, stdin)


def _memo(runner):
    return runner if isinstance(runner, _MemoRunner) else _MemoRunner(runner)


def p1_nondegeneracy(slots) -> dict:
    """Use the committed audit's exact feasible-pattern and slot definitions."""
    rows, domains = [], {}
    for slot in slots:
        domain = slot["family"]
        if domain not in domains:
            patterns = _audit.feasible_patterns(domain)
            pair, consumed = _audit.comparison_functions(patterns)
            domains[domain] = (patterns, pair, consumed)
        rows.append(_audit.inspect_slot(slot, *domains[domain], require_qr=True))
    _audit.add_collisions(rows)
    for row in rows:
        row["status"] = "FAIL" if row["degenerate"] or row["same_domain_function_collisions"] else "PASS"
    return {"status": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL",
            "slots": rows,
            "feasible_patterns": {domain: patterns for domain, (patterns, _, _) in domains.items()}}


def kill_matrix(reference_source: str, inputs, runner=CompilerRunner) -> dict:
    inputs = tuple(str(value) for value in inputs)
    engine = _memo(runner)
    mutants, counts = interp.enumerate_mutants(reference_source)
    engine.prefetch((source, stdin) for source in [reference_source, *(m[2] for m in mutants)] for stdin in inputs)
    references = [engine.run(reference_source, stdin) for stdin in inputs]
    for stdin, outcome in zip(inputs, references):
        if outcome[0] != "ok":
            raise GateStop("reference fails on an input", {"kind": "reference_failure", "source": reference_source,
                                                           "stdin": stdin, "outcome": outcome})
    rows = []
    for index, description, source in mutants:
        outcomes = [engine.run(source, stdin) for stdin in inputs]
        killed = [outcome[0] != "ok" or outcome[1] != reference[1]
                  for outcome, reference in zip(outcomes, references)]
        rows.append({"index": index, "description": description, "killed_on": killed,
                     "killed": any(killed), "outcomes": outcomes})
    unkilled = [row["index"] for row in rows if not row["killed"]]
    return {"status": "FAIL" if unkilled else "PASS", "inputs": list(inputs), "counts": counts,
            "reference_outcomes": references, "mutants": rows, "unkilled": unkilled}


def p2_e1(items, runner=CompilerRunner) -> dict:
    engine = _memo(runner)
    items = [(identifier, source, [(str(stdin), expected) for stdin, expected in cases])
             for identifier, source, cases in items]
    engine.prefetch((source, stdin) for _, source, cases in items for stdin, _ in cases)
    rows = []
    for identifier, source, cases in items:
        failures = []
        for stdin, expected in cases:
            if not isinstance(expected, int):
                raise ValueError("P2 expected values must be integers")
            outcome = engine.run(source, stdin)
            normalized = str(float(expected))
            if outcome != ("ok", normalized):
                failures.append({"stdin": stdin, "expected": normalized, "outcome": outcome})
        rows.append({"id": identifier, "status": "FAIL" if failures else "PASS", "failures": failures})
    return {"status": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL",
            "items": rows, "runner_calls": engine.calls}


def _case_classes(domain: str, inputs) -> dict:
    witnesses = ({name: [] for name in ("SIGN_ZERO", "SIGN_POSITIVE", "EMPTY_LOOP", "LOWER_DOMAIN_BOUNDARY")}
                 if domain == "numeric_iteration" else
                 {name: [] for name in ("NEGATIVE_PRESENT", "ZERO_PRESENT", "POSITIVE_PRESENT")})
    invalid = []
    for case, stdin in enumerate(inputs):
        fields = stdin.strip().split("|") if domain == "array_reduction" else [stdin.strip()]
        if (len(fields) != (4 if domain == "array_reduction" else 1)
                or any(not re.fullmatch(r"[+-]?\d+", field) for field in fields)):
            invalid.append(case)
            continue
        values = [int(field) for field in fields]
        if domain == "numeric_iteration":
            if values[0] < 0:
                invalid.append(case)
            else:
                for name in witnesses:
                    if (values[0] > 0) == (name == "SIGN_POSITIVE"):
                        witnesses[name].append({"case": case, "value": values[0]})
        else:
            for index, value in enumerate(values):
                name = "NEGATIVE_PRESENT" if value < 0 else "POSITIVE_PRESENT" if value > 0 else "ZERO_PRESENT"
                witnesses[name].append({"case": case, "element_index": index, "value": value})
    missing = [name for name, cases in witnesses.items() if not cases]
    return {"status": "FAIL" if invalid or missing else "PASS", "witnesses": witnesses,
            "missing": missing, "invalid_cases": invalid}


def _population(slots):
    slots = list(slots)
    if not slots or len({slot["family"] for slot in slots}) != 1:
        raise ValueError("P6 requires a nonempty single-domain population")
    domain = slots[0]["family"]
    if domain not in ("numeric_iteration", "array_reduction"):
        raise ValueError("Unknown P6 domain")
    if len({slot["task_id"] for slot in slots}) != len(slots):
        raise ValueError("P6 requires unique task IDs")
    return slots, domain


def p6_check(domain_slots, inputs, runner=CompilerRunner, excluded_mutants=()) -> dict:
    slots, domain = _population(domain_slots)
    excluded = set(excluded_mutants)
    inputs = tuple(str(value) for value in inputs)
    if len(inputs) != 5:
        raise ValueError("P6 requires exactly five inputs")
    classes = _case_classes(domain, inputs)
    if classes["invalid_cases"]:
        raise GateStop("invalid domain inputs", {"kind": "invalid_input", "case_classes": classes})
    engine = _memo(runner)
    before = engine.calls
    sources = [primary_source(slot) for slot in slots]
    engine.prefetch((program, stdin) for source in sources
                    for program in [source, *(m[2] for m in interp.enumerate_mutants(source)[0])]
                    for stdin in inputs)
    kills, outputs, expected = {}, {}, {}
    unkilled = []
    for slot, source in zip(slots, sources):
        identifier = slot["task_id"]
        matrix = kill_matrix(source, inputs, engine)
        if excluded:
            matrix["excluded_r2a"] = [row for row in matrix["mutants"]
                                      if (identifier, row["index"]) in excluded]
            matrix["mutants"] = [row for row in matrix["mutants"]
                                 if (identifier, row["index"]) not in excluded]
            matrix["unkilled"] = [index for index in matrix["unkilled"]
                                  if (identifier, index) not in excluded]
            matrix["status"] = "FAIL" if matrix["unkilled"] else "PASS"
        expected[identifier] = [primary_expected(slot, stdin) for stdin in inputs]
        outputs[identifier] = [outcome[1] for outcome in matrix["reference_outcomes"]]
        for stdin, value, output in zip(inputs, expected[identifier], outputs[identifier]):
            if output != str(float(value)):
                raise GateStop("reference/expected output disagreement", {"kind": "reference_expected_disagreement",
                               "id": identifier, "source": source, "stdin": stdin,
                               "expected": str(float(value)), "output": output})
        kills[identifier] = matrix
        unkilled.extend({"id": identifier, "index": index} for index in matrix["unkilled"])
    unseparated = [(a["task_id"], b["task_id"]) for a, b in itertools.combinations(slots, 2)
                   if outputs[a["task_id"]] == outputs[b["task_id"]]]
    report = {"status": "FAIL" if unseparated or unkilled or classes["status"] == "FAIL" else "PASS",
            "domain": domain, "inputs": list(inputs), "expected_outputs": expected,
            "reference_outputs": outputs, "unseparated_pairs": unseparated,
            "unkilled_mutants": unkilled, "case_classes": classes, "kill_matrices": kills,
            "pair_requirements": len(slots) * (len(slots) - 1) // 2,
            "mutant_requirements": sum(matrix["counts"]["total"] - len(matrix.get("excluded_r2a", []))
                                       for matrix in kills.values()),
            "runner_calls": engine.calls - before}
    if excluded:
        report["excluded_r2a"] = [{"id": identifier, **row} for identifier, matrix in kills.items()
                                  for row in matrix["excluded_r2a"]]
    return report


def array_pool(seed: int) -> list[str]:
    """C5 ordered pool; callers supply an explicitly authorized seed."""
    rng = random.Random(seed)
    return ["0|0|0|0", *("|".join(str(rng.randint(-16, 16)) for _ in range(4)) for _ in range(4096))]


def select_array_cases(array_slots, pool, oracle=InterpreterRunner, verifier=CompilerRunner,
                       excluded_mutants=()) -> dict:
    """C5 cumulative greedy, lowest-index ties, then compiler verification.

    Scores omit already satisfied requirements, exactly preserving cumulative
    maximization. Cached outcomes never substitute for selected-case verification.
    Smaller explicit pools are supported for synthetic fault-injection fixtures.
    """
    slots, domain = _population(array_slots)
    excluded = set(excluded_mutants)
    pool = list(pool)
    if domain != "array_reduction" or len(pool) < 5 or pool[0] != "0|0|0|0":
        raise ValueError("Array selector requires an ordered pool beginning with zero and at least five entries")
    if _case_classes(domain, pool)["invalid_cases"]:
        raise ValueError("Invalid array pool entry")
    oracle_engine, verifier_engine = _memo(oracle), _memo(verifier)
    sources = [primary_source(slot) for slot in slots]
    pairs = list(itertools.combinations(range(len(slots)), 2))
    mutations = [(reference, index, mutant) for reference, source in enumerate(sources)
                 for index, _, mutant in interp.enumerate_mutants(source)[0]
                 if (slots[reference]["task_id"], index) not in excluded]
    total = len(pairs) + len(mutations)
    full = (1 << total) - 1

    def coverage(stdin, remaining):
        if not remaining:
            return 0
        references = [oracle_engine.run(source, stdin) for source in sources]
        if any(outcome[0] != "ok" for outcome in references):
            raise GateStop("oracle reference failure", {"kind": "oracle_reference_failure", "stdin": stdin})
        mask = 0
        for index, (a, b) in enumerate(pairs):
            bit = 1 << index
            if remaining & bit and references[a][1] != references[b][1]:
                mask |= bit
        for index, (reference, _, source) in enumerate(mutations, len(pairs)):
            bit = 1 << index
            if remaining & bit:
                outcome = oracle_engine.run(source, stdin)
                if outcome[0] != "ok" or outcome[1] != references[reference][1]:
                    mask |= bit
        return mask

    selected, counts = [0], []
    covered = coverage(pool[0], full)
    counts.append(covered.bit_count())
    while len(selected) < 5:
        remaining = full ^ covered
        best_index, best_mask, best_count = None, 0, -1
        for index in range(1, len(pool)):
            if index in selected:
                continue
            mask = coverage(pool[index], remaining)
            count = (covered | mask).bit_count()
            if count > best_count:
                best_index, best_mask, best_count = index, mask, count
        selected.append(best_index)
        covered |= best_mask
        counts.append(covered.bit_count())
    inputs = [pool[index] for index in selected]
    verification = p6_check(slots, inputs, verifier_engine, excluded_mutants=excluded)
    for source in [*sources, *(mutant for _, _, mutant in mutations)]:
        for stdin in inputs:
            predicted = oracle_engine.run(source, stdin)
            observed = verifier_engine.run(source, stdin)
            if _comparison(predicted) != _comparison(observed):
                raise GateStop("oracle/verifier disagreement", {"kind": "oracle_verifier_disagreement",
                               "source": source, "stdin": stdin, "oracle": predicted, "verifier": observed,
                               "selected_indices": selected, "selected_inputs": inputs})
    report = {"status": verification["status"], "selected_indices": selected, "selected_inputs": inputs,
              "requirement_counts_after_each_pick": counts, "total_requirements": total,
              "pair_requirements": len(pairs), "mutant_requirements": len(mutations),
              "unseparated_pairs": verification["unseparated_pairs"],
              "unkilled_mutants": verification["unkilled_mutants"], "case_classes": verification["case_classes"],
              "compiler_verification_runs": verifier_engine.calls, "disagreements": 0,
              "oracle_runs": oracle_engine.calls, "verification": verification}
    if excluded:
        report["excluded_r2a"] = verification["excluded_r2a"]
    if verification["status"] != "PASS":
        raise GateStop("selected five cases do not meet P6", {"kind": "selection_unsatisfied", **report})
    return report
