"""R2-EVIDENCE-v2: bounded non-model feasibility evidence, never construction.

Scientific outputs are deterministic; measured wall times are observations.
Only the two named evidence files are written, exclusively and after all checks.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from self_learning_ai.conf1_r1 import interp, primary
from self_learning_ai.conf1_r1.gates_primary import CompilerRunner, GateStop, p6_check
from build_phase3c_conf1_data import train_source

OUT = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE"
OUTPUTS = (OUT / "r2_liveness_feasibility.json", OUT / "r2_liveness_feasibility.md")
SYN_ARRAY_EVAL = ("0|0|0|0", "-14|16|-2|-15", "12|2|-1|5", "-16|-10|7|2", "-14|6|-6|4")
SYN_NUM_EVAL = ("0", "5", "9", "31", "64")
SYN_SEEDS = tuple(range(900001, 900013))
CONDITIONS = ("isolated", "composition")
POSITIVE_POOL = tuple(n for n in range(1, 61) if n not in (12, 13, 14))
CANONICAL = "CONF1-TR-NU-01-V0"
_ORIGINAL_SPLIT, _ORIGINAL_COMPILE = interp.split_statements, interp._compile
_CACHE_INSTALLED = False


def budget(deadline):
    if time.monotonic() > deadline:
        raise GateStop("runtime budget exceeded")


def install_cache():
    """Cache only the accepted parser/typechecker's immutable top-level result.

    The accepted interpret() runtime still executes every requested input.
    Its execution never mutates the compiled instruction tree. Namespace-bearing
    recursive compilation uses the original compiler with its original context.
    """
    global _CACHE_INSTALLED
    if _CACHE_INSTALLED:
        return

    @lru_cache(maxsize=4096)
    def prepared(units):
        try:
            return _ORIGINAL_COMPILE(units, {}, set())
        except (ValueError, TypeError, KeyError, IndexError, RecursionError):
            return None

    def cached_compile(units, names, imported):
        if names or imported:
            return _ORIGINAL_COMPILE(units, names, imported)
        instructions = prepared(units)
        if instructions is None:
            raise ValueError("cached input-independent static failure")
        return instructions

    interp.split_statements = lru_cache(maxsize=4096)(_ORIGINAL_SPLIT)
    interp._compile = cached_compile
    _CACHE_INSTALLED = True


def outcome(source, stdin):
    result = interp.interpret(source, stdin)
    return result if result[0] == "ok" else ("fail",)


def deleted_text(description):
    return description.split("): ", 1)[1]


def domain_disjoint(slot):
    return slot["slot_id"] in {f"CONF1-TR-AR-03-V{v}" for v in range(5)}


def populations():
    primaries = primary.load_primary_slots(ROOT)  # Verifies R1 and ledger hashes.
    ledger = json.loads((ROOT / "research/protocols/phase3c_conf1_slots.json").read_bytes())
    slots = ledger["slots"]["training_paired_slots"]
    if len(slots) != 60 or len({s["slot_id"] for s in slots}) != 60:
        raise GateStop("training population mismatch")
    numeric = sorted(s["slot_id"].encode("utf-8") for s in slots if s["family"] == "numeric_iteration")
    if len(numeric) != 30 or numeric[0].decode() != CANONICAL:
        raise GateStop("canonical numeric slot mismatch")
    programs = [{"id": s["task_id"], "kind": "primary", "condition": None,
                 "family": s["family"], "source": primary.primary_source(s), "exempt": False, "domain_disjoint": False}
                for s in primaries]
    programs += [{"id": s["slot_id"], "kind": "training", "condition": c,
                  "family": s["family"], "source": train_source(c, s),
                  "exempt": domain_disjoint(s) and c == "composition", "domain_disjoint": domain_disjoint(s)}
                 for s in slots for c in CONDITIONS]
    if len(programs) != 152:
        raise GateStop("program population mismatch")
    return primaries, slots, programs, ledger


def pattern_coverage(ledger):
    definitions = ledger["predicate_definitions"]["array_reduction"]
    rows = []
    for i in range(4):
        sets = []
        for bound in (5, 16):
            patterns = {tuple(int(primary._PREDICATE_FUNCTIONS[p["expression"]](None, i, [x] * 4))
                              for p in definitions) for x in range(-bound, bound + 1)}
            sets.append(sorted(patterns))
        rows.append({"position": i, "minus5_to5": sets[0], "minus16_to16": sets[1],
                     "equal": sets[0] == sets[1]})
    if not all(row["equal"] for row in rows):
        raise GateStop("E1 per-position predicate-pattern coverage fails", {"coverage": rows})
    return {"status": "PASS", "predicate_order": [p["name"] for p in definitions], "positions": rows}


def cache_crosscheck(programs, deadline):
    # Compare cached and unmodified I1 interpretation on every reference and
    # every mutant, including forward/reverse and static failures. No RNG.
    jobs = [(source, SYN_NUM_EVAL[2] if p["family"] == "numeric_iteration" else SYN_ARRAY_EVAL[1])
            for p in programs for source in [p["source"], *(m[2] for m in interp.enumerate_mutants(p["source"])[0])]]
    expected = [outcome(source, stdin) for source, stdin in jobs]
    install_cache()
    for job, old in zip(jobs, expected):
        budget(deadline)
        new = outcome(*job)
        if new != old:
            raise GateStop("cached/original interpreter disagreement", {"source": job[0], "stdin": job[1],
                                                                       "original": old, "cached": new})
    return {"comparisons": len(jobs), "disagreements": 0}


def e1_program(job):
    index, program, deadline = job
    install_cache()
    started = time.perf_counter()
    inputs = ([str(n) for n in range(201)] if program["family"] == "numeric_iteration" else
              ["|".join(map(str, values)) for values in itertools.product(range(-5, 6), repeat=4)])
    references = [outcome(program["source"], stdin) for stdin in inputs]
    if any(result[0] != "ok" for result in references):
        raise GateStop("E1 reference interpreter failure", {"program": program["id"]})
    equivalents, counterexamples = [], []
    mutants, counts = interp.enumerate_mutants(program["source"])
    for mutant_index, description, source in mutants:
        first = None
        matches = 0
        for case, (stdin, reference) in enumerate(zip(inputs, references)):
            if case % 128 == 0:
                budget(deadline)
            actual = outcome(source, stdin)
            if actual == reference:
                matches += 1
            elif first is None:
                first = {"stdin": stdin, "reference": reference, "mutant": actual}
        if first is None:
            equivalents.append({"mutant_index": mutant_index, "deleted_statement": deleted_text(description),
                                "description": description, "matching_inputs": matches})
        else:
            counterexamples.append({"mutant_index": mutant_index, "matching_inputs": matches, "first": first})
    return index, {k: v for k, v in program.items() if k != "source"} | {
        "reference_sha256": hashlib.sha256(program["source"].encode()).hexdigest(),
        "input_count": len(inputs), "mutant_counts": counts, "equivalents": equivalents,
        "non_equivalent_counterexamples": counterexamples,
        "interpreter_runs": len(inputs) * (counts["total"] + 1),
        "wall_seconds": round(time.perf_counter() - started, 3)}


def expected_equivalents():
    return {(s, c, index) for s, index in [
        *((f"CONF1-TR-NU-03-V{v}", 7) for v in (0, 2, 4)),
        *((f"CONF1-TR-NU-13-V{v}", 7) for v in (1, 3)),
        *((f"CONF1-TR-NU-23-V{v}", 8) for v in (0, 2, 4))] for c in CONDITIONS}


def enumerate_e1(programs, workers, deadline):
    started = time.perf_counter()
    rows = [None] * len(programs)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(e1_program, (i, p, deadline)) for i, p in enumerate(programs)]
        for completed, future in enumerate(as_completed(futures), 1):
            index, row = future.result()
            rows[index] = row
            print(f"E1 exhaustive programs completed: {completed}/{len(programs)}", flush=True)
            budget(deadline)
    primary_actual = {(r["id"], e["mutant_index"]) for r in rows if r["kind"] == "primary" for e in r["equivalents"]}
    training_actual = {(r["id"], r["condition"], e["mutant_index"]) for r in rows
                       if r["kind"] == "training" and not r["domain_disjoint"] for e in r["equivalents"]}
    expected_training = expected_equivalents()
    return {"programs": rows, "interpreter_runs": sum(r["interpreter_runs"] for r in rows),
            "prediction": {"primary_expected": [["CONF1-NC-AR-G1-R3", 14]],
                           "primary_actual": sorted(primary_actual),
                           "primary_match": primary_actual == {("CONF1-NC-AR-G1-R3", 14)},
                           "training_nonexempt_expected": sorted(expected_training),
                           "training_nonexempt_actual": sorted(training_actual),
                           "training_nonexempt_match": training_actual == expected_training,
                           "training_missing": sorted(expected_training - training_actual),
                           "training_unexpected": sorted(training_actual - expected_training)},
            "wall_seconds": round(time.perf_counter() - started, 3)}


def compiler_confirmations(e1, programs, deadline):
    started = time.perf_counter()
    compiler = CompilerRunner(ROOT)
    sources, checks = {}, []
    for row, program in zip(e1["programs"], programs):
        inputs = ([str(n) for n in range(20)] if row["family"] == "numeric_iteration" else
                  ["|".join(map(str, v)) for v in itertools.islice(
                      (v for v in itertools.product(range(-5, 6), repeat=4) if any(v)), 20)])
        mutants = {m[0]: m[2] for m in interp.enumerate_mutants(program["source"])[0]}
        for equivalent in row["equivalents"]:
            mutant = mutants[equivalent["mutant_index"]]
            checks.append((row, equivalent, inputs, program["source"], mutant))
            for stdin in inputs:
                sources.setdefault((program["source"], stdin), None)
                sources.setdefault((mutant, stdin), None)
    def run(job):
        budget(deadline)
        return compiler.run(*job)
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(run, sources))
    outcomes = dict(zip(sources, results))
    for row, equivalent, inputs, reference, mutant in checks:
        records = []
        for stdin in inputs:
            a, b = outcomes[reference, stdin], outcomes[mutant, stdin]
            predicted = outcome(mutant, stdin)
            if a[0] != "ok" or a != b or predicted != a:
                raise GateStop("E1 compiler confirmation disagreement", {"id": row["id"],
                               "condition": row["condition"], "mutant_index": equivalent["mutant_index"],
                               "stdin": stdin, "reference": a, "mutant": b, "interpreter": predicted})
            records.append({"stdin": stdin, "reference": a, "mutant": b, "agreed": True})
        equivalent["compiler_confirmation"] = {"status": "PASS", "cases": records}
    return {"equivalent_mutants": len(checks), "comparisons": len(checks) * 20,
            "distinct_compiler_runs": len(sources), "disagreements": 0,
            "wall_seconds": round(time.perf_counter() - started, 3)}


def rng_for(seed, slot):
    if seed not in SYN_SEEDS:
        raise GateStop("unapproved synthetic seed")
    tag = "train-numeric" if slot["family"] == "numeric_iteration" else "train-array"
    raw = f"{seed}|{slot['slot_id']}|{tag}".encode("utf-8")
    return random.Random(int.from_bytes(hashlib.sha256(raw).digest(), "big"))


def draw_cases(seed, slot, alternative):
    rng = rng_for(seed, slot)
    skips = {"duplicate": 0, "synthetic_evaluation_input": 0, "total": 0}
    if slot["family"] == "numeric_iteration":
        size = len(POSITIVE_POOL) if alternative else 4 if slot["slot_id"] == CANONICAL else 5
        cases = rng.sample(POSITIVE_POOL, size)
        if not alternative:
            if slot["slot_id"] == CANONICAL:
                cases.append(0)
            cases.sort()
        return list(map(str, cases)), skips
    count, cases, seen = (256 if alternative else 5), [], set()
    while len(cases) < count:
        value = "|".join(str(rng.randint(-16, 16)) for _ in range(4))
        reason = "duplicate" if value in seen else "synthetic_evaluation_input" if value in SYN_ARRAY_EVAL else None
        if reason:
            skips[reason] += 1
            skips["total"] += 1
        else:
            cases.append(value)
            seen.add(value)
    return cases, skips


def truth_items(slot, stdin, definitions):
    expressions = {p["name"]: p["expression"] for p in definitions[slot["family"]]}
    n, values = (int(stdin), None) if slot["family"] == "numeric_iteration" else (None, list(map(int, stdin.split("|"))))
    indices = range(1, n + 1) if n is not None else range(4)
    return [tuple(bool(primary._PREDICATE_FUNCTIONS[expressions[slot[role]]](n, i, values)) for role in ("P", "Q"))
            for i in indices]


def requirements(slot, equivalent_map):
    rows, source_map = [], {}
    for condition in CONDITIONS:
        source = train_source(condition, slot)
        source_map[condition] = source
        if condition == "composition" and domain_disjoint(slot):
            continue
        exempt_indices = equivalent_map[slot["slot_id"], condition]
        for index, description, mutant in interp.enumerate_mutants(source)[0]:
            if index not in exempt_indices:
                rows.append(({"gate": "P4(iii)", "condition": condition, "mutant_index": index,
                              "deleted_statement": deleted_text(description)}, mutant))
        for role in ("P", "Q"):
            for value in (False, True):
                rows.append(({"gate": "P4(iv)", "condition": condition, "predicate": role, "truth": value}, None))
        if condition == "composition":
            rows.append(({"gate": "P4(iv)", "condition": condition, "requirement": "both_true"}, None))
    if not domain_disjoint(slot):
        rows.append(({"gate": "P4(v)", "condition": "paired", "requirement": "outputs_differ"}, None))
    return rows, source_map


def case_mask(slot, stdin, rows, sources, definitions):
    references = {c: outcome(source, stdin) for c, source in sources.items()}
    if any(r[0] != "ok" for r in references.values()):
        raise GateStop("training simulation reference failure", {"slot": slot["slot_id"], "stdin": stdin})
    items = [tuple(item) for item in truth_items(slot, stdin, definitions)]
    mask = 0
    for index, (requirement, mutant) in enumerate(rows):
        gate, condition = requirement["gate"], requirement["condition"]
        if gate == "P4(iii)":
            satisfied = outcome(mutant, stdin) != references[condition]
        elif gate == "P4(v)":
            satisfied = references["isolated"] != references["composition"]
        elif requirement.get("requirement") == "both_true":
            satisfied = any(p and q for p, q in items)
        else:
            role = 0 if requirement["predicate"] == "P" else 1
            satisfied = any(item[role] == requirement["truth"] for item in items)
        if satisfied:
            mask |= 1 << index
    return mask, {c: int(float(r[1])) for c, r in references.items()}


def simulate_slot(job):
    slot, equivalent_map, definitions, deadline, selected_seed, alternative = job
    install_cache()
    rows, sources = requirements(slot, equivalent_map)
    all_required = (1 << len(rows)) - 1
    cache = {}
    def score(stdin):
        if stdin not in cache:
            budget(deadline)
            cache[stdin] = case_mask(slot, stdin, rows, sources, definitions)
        return cache[stdin]
    records = {"e2": [], "e3": []}
    for seed in (() if alternative else (selected_seed,)):
        started = time.perf_counter()
        inputs, skips = draw_cases(seed, slot, False)
        covered = 0
        for stdin in inputs:
            covered |= score(stdin)[0]
        unmet = [row for index, (row, _) in enumerate(rows) if not (covered >> index) & 1]
        records["e2"].append({"seed": seed, "slot": slot["slot_id"], "domain": slot["family"],
                              "inputs": inputs, "skips": skips, "unmet": unmet,
                              "outputs": {c: [score(stdin)[1][c] for stdin in inputs] for c in CONDITIONS},
                              "wall_seconds": round(time.perf_counter() - started, 3)})
    for seed in ((selected_seed,) if alternative else ()):
        started = time.perf_counter()
        stream, skips = draw_cases(seed, slot, True)
        masks = [score(stdin)[0] for stdin in stream]
        indices, inputs, counts, covered = [], [], [], 0
        if slot["slot_id"] == CANONICAL:
            inputs.append("0")
            indices.append(None)  # Forced zero is outside the positive stream.
            covered = score("0")[0]
            counts.append(covered.bit_count())
        chosen = set()
        while len(inputs) < 5:
            index = max((i for i in range(len(stream)) if i not in chosen),
                        key=lambda i: ((covered | masks[i]).bit_count(), -i))
            chosen.add(index)
            indices.append(index)
            inputs.append(stream[index])
            covered |= masks[index]
            counts.append(covered.bit_count())
        unmet = [row for index, (row, _) in enumerate(rows) if not (covered >> index) & 1]
        records["e3"].append({"seed": seed, "slot": slot["slot_id"], "domain": slot["family"],
                              "selected_stream_indices": indices, "inputs": inputs, "skips": skips,
                              "requirements_total": len(rows), "satisfied_after_each_pick": counts,
                              "all_satisfied": covered == all_required, "unmet": unmet,
                              "outputs": {c: [score(stdin)[1][c] for stdin in inputs] for c in CONDITIONS},
                              "wall_seconds": round(time.perf_counter() - started, 3)})
    return records


def aggregate(records, field, seeds, elapsed, seed_elapsed):
    result = []
    for seed in seeds:
        slots = [row for record in records for row in record[field] if row["seed"] == seed]
        counts = {gate: {"failed_programs" if gate != "P4(v)" else "failed_pairs": 0, "unmet_requirements": 0}
                  for gate in ("P4(iii)", "P4(iv)", "P4(v)")}
        for row in slots:
            for gate, summary in counts.items():
                unmet = [u for u in row["unmet"] if u["gate"] == gate]
                summary[next(iter(summary))] += len({u["condition"] for u in unmet})
                summary["unmet_requirements"] += len(unmet)
        result.append({"seed": seed, "counts": counts,
                       "unmet_slots": [{"slot": row["slot"], "unmet": row["unmet"]} for row in slots if row["unmet"]],
                       "skips": {key: sum(row["skips"][key] for row in slots) for key in ("duplicate", "synthetic_evaluation_input", "total")},
                       "slot_wall_seconds_sum": round(sum(row["wall_seconds"] for row in slots), 3),
                       "wall_seconds": seed_elapsed[seed],
                       "slot_wall_seconds_max": max(row["wall_seconds"] for row in slots), "slots": slots})
    return {"seeds": result, "combined_simulation_wall_seconds": elapsed}


def output_class(value):
    if value < 0:
        raise GateStop("negative output outside K7 classes")
    return "ZERO" if value == 0 else "POSITIVE" if value < 10 else "MULTIDIGIT"


def e4_classes(primaries, e3):
    order = ("ZERO", "POSITIVE", "MULTIDIGIT")
    def ordered(values):
        return [c for c in order if c in values]
    primary_classes = {domain: set() for domain in ("numeric_iteration", "array_reduction")}
    for slot in primaries:
        inputs = SYN_NUM_EVAL if slot["family"] == "numeric_iteration" else SYN_ARRAY_EVAL
        primary_classes[slot["family"]].update(output_class(primary.primary_expected(slot, stdin)) for stdin in inputs)
    records = []
    for seed in e3["seeds"]:
        classes = []
        for domain, required in primary_classes.items():
            for condition in CONDITIONS:
                present = {output_class(value) for slot in seed["slots"] if slot["domain"] == domain
                           for value in slot["outputs"][condition]}
                classes.append({"domain": domain, "condition": condition, "training_classes": ordered(present),
                                "primary_classes": ordered(required), "missing": ordered(required - present),
                                "k7": "PASS" if required <= present else "FAIL"})
        records.append({"seed": seed["seed"], "classes": classes,
                        "k7": "PASS" if all(c["k7"] == "PASS" for c in classes) else "FAIL"})
    return {"primary_classes": {d: ordered(c) for d, c in primary_classes.items()}, "seeds": records}


def e5_exclusion(primaries, e1):
    started = time.perf_counter()
    slots = [s for s in primaries if s["family"] == "array_reduction"]
    checked = p6_check(slots, SYN_ARRAY_EVAL, CompilerRunner)
    equivalent = {(r["id"], e["mutant_index"]) for r in e1["programs"] if r["kind"] == "primary"
                  and r["family"] == "array_reduction" for e in r["equivalents"]}
    unkilled = [(m["id"], m["index"]) for m in checked["unkilled_mutants"]]
    remaining = [m for m in unkilled if m not in equivalent]
    total = checked["pair_requirements"] + checked["mutant_requirements"] - len(equivalent)
    satisfied = total - len(checked["unseparated_pairs"]) - len(remaining)
    return {"inputs": list(SYN_ARRAY_EVAL), "original_r1_status": checked["status"],
            "original_satisfied": checked["pair_requirements"] + checked["mutant_requirements"] - len(unkilled) - len(checked["unseparated_pairs"]),
            "original_total": checked["pair_requirements"] + checked["mutant_requirements"],
            "compiler_runs": checked["runner_calls"], "wall_seconds": round(time.perf_counter() - started, 3),
            "excluded": sorted(equivalent), "satisfied": satisfied, "total": total,
            "unseparated_pairs": checked["unseparated_pairs"], "remaining_unkilled": remaining,
            "case_classes": checked["case_classes"], "prediction_match": (satisfied, total) == (567, 567),
            "interpretation": "Evidence-only equivalent exclusion; frozen R1 is unchanged."}


def render(report):
    lines = ["# CONF1 R2 non-model liveness-feasibility evidence", "",
             "Evidence only. No methodology change, candidate construction or model use.", "",
             "DOMAIN_EQUIVALENT below means equality on the task's exhaustive finite input sets; numeric n>200 and array values outside -5..5 were not exhaustively executed.", "",
             f"Source HEAD: `{report['source_head']}`. Interpreter caching crosscheck: {report['cache_crosscheck']}. Patterns: PASS.", "",
             "## E1 equivalent mutants", "",
             "| Kind | Slot | Condition | Mutant | Deleted statement | Compiler cases |",
             "|---|---|---|---:|---|---:|"]
    for row in report["e1"]["programs"]:
        for eq in row["equivalents"]:
            text = eq["deleted_statement"].replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {row['kind']} | {row['id']} | {row['condition'] or 'primary'} | {eq['mutant_index']} | `{text}` | 20 PASS |")
    lines += ["", "Prediction and compiler confirmation:", "", "```json",
              json.dumps({"prediction": report["e1"]["prediction"], "compiler": report["e1"]["compiler"]}, indent=2), "```", "",
              "## E2 frozen-rule synthetic simulations", "",
              "Counts are failed programs for P4(iii)/(iv), failed matched pairs for P4(v); unmet requirements are also recorded. All slot inputs, outputs and failures are in the JSON.", "",
              "| Seed | iii programs / mutants | iv programs / requirements | v pairs | Array skips (duplicate / eval) |",
              "|---:|---:|---:|---:|---:|"]
    for seed in report["e2"]["seeds"]:
        counts, skips = seed["counts"], seed["skips"]
        lines.append(f"| {seed['seed']} | {counts['P4(iii)']['failed_programs']} / {counts['P4(iii)']['unmet_requirements']} | {counts['P4(iv)']['failed_programs']} / {counts['P4(iv)']['unmet_requirements']} | {counts['P4(v)']['failed_pairs']} | {skips['duplicate']} / {skips['synthetic_evaluation_input']} |")
        examples = seed["unmet_slots"][:3]
        lines += ["", f"Seed {seed['seed']} examples:", "", "```json", json.dumps(examples, indent=2), "```", ""]
    lines += ["## E3 kill-directed synthetic simulations", "",
              "Each seed's full unmet list follows. Per-slot timings, cases, stream indices, cumulative scores and skips are in the JSON; summed worker times are not elapsed wall time.", ""]
    for seed in report["e3"]["seeds"]:
        lines += [f"Seed {seed['seed']}: wall time {seed['wall_seconds']} s; skips {seed['skips']}; summed slot time {seed['slot_wall_seconds_sum']} s; maximum slot time {seed['slot_wall_seconds_max']} s.", "",
                  "```json", json.dumps(seed["unmet_slots"], indent=2), "```", ""]
    lines += ["## E4 output classes and K7", "", "| Seed | Domain | Condition | Primary | Training | K7 |",
              "|---:|---|---|---|---|---|"]
    for seed in report["e4"]["seeds"]:
        for row in seed["classes"]:
            lines.append(f"| {seed['seed']} | {row['domain']} | {row['condition']} | {', '.join(row['primary_classes'])} | {', '.join(row['training_classes'])} | {row['k7']} |")
    lines += ["", "## E5 fixed I2 synthetic primary selection with equivalent exclusion", "", "```json",
              json.dumps(report["e5"], indent=2), "```", "", "## Timings and boundaries", "",
              "```json", json.dumps(report["timings"], indent=2), "```", "",
              "Only authorized synthetic seeds were drawn. Numeric training excludes exactly 12,13,14; array training streams exclude SYN_ARRAY_EVAL and their own accepted duplicates. The canonical numeric E3 zero has no stream index. Each condition has separate witness requirements; treatment discrimination is one requirement per matched pair. DOMAIN_DISJOINT COMPOSITION is exempt from P4(iii)-(v), and E1 equivalents are excluded from simulated P4(iii) only. No frozen numeric primary evaluation set or real array pool was run.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--budget-seconds", type=float, default=7200)
    args = parser.parse_args()
    if args.workers < 1 or not 0 < args.budget_seconds <= 7200:
        parser.error("positive workers and budget <=7200 seconds required")
    if any(path.exists() for path in OUTPUTS):
        raise FileExistsError("Refusing to overwrite either R2 evidence file")
    started = time.perf_counter()
    deadline = time.monotonic() + args.budget_seconds
    primaries, slots, programs, ledger = populations()
    coverage = pattern_coverage(ledger)
    print("E1 per-position predicate-pattern coverage: PASS", flush=True)
    crosscheck = cache_crosscheck(programs, deadline)
    print(f"Cached/original I1 crosscheck: {crosscheck}", flush=True)
    e1 = enumerate_e1(programs, args.workers, deadline)
    print(f"E1 prediction: {e1['prediction']}", flush=True)
    e1["compiler"] = compiler_confirmations(e1, programs, deadline)
    print(f"E1 compiler confirmations: {e1['compiler']}", flush=True)
    equivalent_map = {(row["id"], row["condition"]): {e["mutant_index"] for e in row["equivalents"]}
                      for row in e1["programs"] if row["kind"] == "training"}
    simulation_started = time.perf_counter()
    records, seed_elapsed = [], {"e2": {}, "e3": {}}
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for field, alternative, seeds in (("e2", False, SYN_SEEDS), ("e3", True, SYN_SEEDS[:5])):
            for seed in seeds:
                seed_started = time.perf_counter()
                records.extend(executor.map(simulate_slot, [(slot, equivalent_map, ledger["predicate_definitions"], deadline, seed, alternative) for slot in slots]))
                seed_elapsed[field][seed] = round(time.perf_counter() - seed_started, 3)
                print(f"{field.upper()} seed {seed} complete in {seed_elapsed[field][seed]} s", flush=True)
    simulation_elapsed = round(time.perf_counter() - simulation_started, 3)
    e2 = aggregate(records, "e2", SYN_SEEDS, simulation_elapsed, seed_elapsed["e2"])
    e3 = aggregate(records, "e3", SYN_SEEDS[:5], simulation_elapsed, seed_elapsed["e3"])
    e4, e5 = e4_classes(primaries, e3), e5_exclusion(primaries, e1)
    budget(deadline)
    report = {"schema": "conf1_r2_liveness_feasibility_v2", "status": "NON_MODEL_EVIDENCE_ONLY",
              "source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "synthetic_array_evaluation_inputs": list(SYN_ARRAY_EVAL), "synthetic_numeric_primary_inputs": list(SYN_NUM_EVAL),
              "numeric_training_exclusion": [12, 13, 14], "synthetic_seeds": list(SYN_SEEDS),
              "pattern_coverage": coverage, "cache_crosscheck": crosscheck,
              "e1": e1, "e2": e2, "e3": e3, "e4": e4, "e5": e5,
              "timings": {"e1_exhaustive_wall_seconds": e1["wall_seconds"],
                          "e1_compiler_wall_seconds": e1["compiler"]["wall_seconds"],
                          "e2_e3_combined_wall_seconds": simulation_elapsed,
                          "total_audit_wall_seconds": round(time.perf_counter() - started, 3),
                          "workers": args.workers, "budget_seconds": args.budget_seconds},
              "limitations": ["DOMAIN_EQUIVALENT is the task-defined finite-set result, not an unbounded numeric proof.",
                              "Simulated equivalent exclusion and alternative selection do not amend frozen R1.",
                              "The pinned compiler confirms equivalents on 20 prescribed inputs; simulations use the I1 interpreter."]}
    json_text, markdown = json.dumps(report, indent=2, ensure_ascii=False) + "\n", render(report)
    budget(deadline)
    for path, text in zip(OUTPUTS, (json_text, markdown)):
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
    print(json.dumps({"timings": report["timings"], "e2": [{k: s[k] for k in ("seed", "counts", "skips")} for s in e2["seeds"]],
                      "e3": [{k: s[k] for k in ("seed", "unmet_slots", "skips", "wall_seconds", "slot_wall_seconds_sum")} for s in e3["seeds"]],
                      "e4": e4, "e5": {k: e5[k] for k in ("satisfied", "total", "prediction_match")}}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
