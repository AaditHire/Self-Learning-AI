"""R1/R2 gate orchestration; construction requires explicit caller authorization.

Scientific payloads are deterministic. Timings are observations. No model is
loaded. Nothing is published until every primary gate has passed; a gate STOP
writes only a STOP report in the new, exclusively reserved output directory.
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
import time
from pathlib import Path

from self_learning_ai.conf1_r1 import gates_primary as gates, interp, overlap, secondary, training
from self_learning_ai.conf1_r1.gates_primary import ROOT, CompilerRunner, GateStop, _memo
from self_learning_ai.conf1_r1.execution import EXECUTION_BOUND_FILES, execution_bound_files
from self_learning_ai.conf1_r1.primary import load_primary_slots, primary_expected, primary_prompt, primary_source


LEDGER_PATH = "research/protocols/phase3c_conf1_slots.json"
# Read the authority once at import, so a refused call does no file/compiler work.
CONSTRUCTION_SEED = json.loads((ROOT / LEDGER_PATH).read_bytes())["construction_seed"]
SYNTHETIC_LABEL = "SYNTHETIC_DRY_RUN"
MANIFEST_PINS = {
    "research/protocols/phase3c_conf1_rebaseline_r1_freeze.json":
        "58d2ca7a453246ac97aa956be6c499a416bd523abadc65b7a402195b986f96b1",
    training.R2_MANIFEST: training.R2_MANIFEST_SHA256,
    "research/protocols/phase3c_conf1_input_domain_case_classes_and_training_amendment_freeze.json":
        "de4a353d58515b5c53210664ea1a642731ac6f1734f23afef4ae512fb8c2627a",
    "research/protocols/phase3c_conf1_paired_scaffold_normalization_freeze.json":
        "ff1a9610b10ff559ac1859361fb7a31668210ed33e97c2864e592981bd9cfea2",
}
CLARIFICATION_PINS = {
    "research/protocols/phase3c_conf1_r1_implementation_clarifications.md":
        "9fbe75fa2caf6a27ecbac943bec6a99f69c87a604669d533b73cc83e3bfcd328",
    "research/protocols/phase3c_conf1_r2_implementation_clarifications.md":
        "43849d3fdf8c33a0243f416ace9e3006eb864e87b26356bb6268e092e76b75ff",
    "research/protocols/phase3c_conf1_implementation_clarifications_c10_c11.md":
        "d314bf168ea53c1f4a6ba0f1dc1f41a2fdd68be0fc6ba615a032a560e3c47b92",
}
USED_SCRIPTS = (
    "audit_phase3c_conf1_r1_specification_feasibility.py",
    "audit_phase3c_conf1_r2_liveness_feasibility.py", "build_phase3c_conf1_data.py",
    "build_phase2b_data.py", "design_phase3c_conf1.py", "validate_phase2b_data.py",
    "build_phase3c_conf1_candidate.py",
)


def validate_request(seed, *, label, authorized_construction=False, workers):
    """Shared API/CLI refusal check, before any per-call file/compiler work."""
    if seed == CONSTRUCTION_SEED and authorized_construction is not True:
        raise GateStop("construction seed requires explicit authorization", {"seed": seed})
    if type(seed) is not int or type(workers) is not int or workers < 1:
        raise GateStop("seed and positive worker count must be integers")
    if seed != CONSTRUCTION_SEED and label != SYNTHETIC_LABEL:
        raise GateStop("a non-construction seed requires SYNTHETIC_DRY_RUN")
    if not isinstance(label, str) or not label:
        raise GateStop("candidate label must be a nonempty string")


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _authorities():
    hashes, manifests = {}, {}

    def verify(path, expected, lf=False):
        raw = (ROOT / path).read_bytes()
        actual = hashlib.sha256(raw.replace(b"\r\n", b"\n") if lf else raw).hexdigest()
        if actual != expected:
            raise GateStop("authority SHA-256 mismatch", {"path": path, "expected": expected, "actual": actual})
        hashes[path] = {"sha256": hashlib.sha256(raw).hexdigest(), "verified_sha256": actual,
                        "verification": "LF-normalized" if lf else "byte-exact"}
        return raw

    for path, expected in MANIFEST_PINS.items():
        manifests[path] = json.loads(verify(path, expected))
    for path, manifest in manifests.items():
        verify(manifest["frozen_amendment_path"], manifest["frozen_amendment_sha256_lf_normalized"], lf=True)
    r1 = manifests[next(iter(MANIFEST_PINS))]
    ledger = json.loads(verify(LEDGER_PATH, r1["frozen_slot_ledger_sha256_byte_exact"]))
    if ledger["construction_seed"] != CONSTRUCTION_SEED:
        raise GateStop("ledger construction seed changed after import")
    for path, expected in CLARIFICATION_PINS.items():
        verify(path, expected)
    r2 = manifests[training.R2_MANIFEST]
    for manifest, name in ((r1, "audit_phase3c_conf1_r1_specification_feasibility.py"),
                           (r2, "audit_phase3c_conf1_r2_liveness_feasibility.py")):
        artifact = next(a for a in manifest["evidence_artifacts"] if a["path"] == "scripts/" + name)
        verify(artifact["path"], artifact["sha256"])
    artifact = next(a for a in r2["evidence_artifacts"] if a["path"].endswith("/r2_liveness_feasibility.json"))
    evidence = json.loads(verify(artifact["path"], artifact["sha256"]))
    disjoint = sorted([row["id"], row["condition"], mutant["mutant_index"]]
                      for row in evidence["e1"]["programs"] if row["exempt"]
                      for mutant in row["equivalents"])
    verify(".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar", gates.JAR_SHA256)
    for name, expected in training.TOKENIZER_HASHES.items():
        verify((training.TOKENIZER_DIR / name).relative_to(ROOT).as_posix(), expected)
    system = "prompts/phase1t_system.txt"
    hashes[system] = {"sha256": _sha(ROOT / system), "verification": "recorded runner input"}
    code = {p.relative_to(ROOT).as_posix(): _sha(p)
            for p in sorted((ROOT / "src/self_learning_ai/conf1_r1").glob("*.py"))}
    for name in USED_SCRIPTS:
        code["scripts/" + name] = _sha(ROOT / "scripts" / name)
    for name in ("compiler.py", "benchmark.py"):
        code["src/self_learning_ai/" + name] = _sha(ROOT / "src/self_learning_ai" / name)
    for name in EXECUTION_BOUND_FILES | execution_bound_files():
        code[name] = _sha(ROOT / name)
    return {"status": "PASS", "authority_hashes": hashes, "code_hashes": code,
            "compiler_sha256": gates.JAR_SHA256, "tokenizer_hashes": training.TOKENIZER_HASHES,
            "ledger": ledger, "r2_manifest": r2, "audit_domain_disjoint_equivalents": disjoint}


def canonical_cases(identifier, inputs, expected):
    """Serialize integer computations using the I4b case convention.

    Training uses its model_task_id (the neutral slot_id), preserving the
    frozen requirement for identical ordered case IDs within a matched pair.
    """
    inputs, expected = list(inputs), list(expected)
    if len(inputs) != 5 or len(expected) != 5 or any(type(value) is not int for value in expected):
        raise GateStop("canonical cases require five inputs and five integer expected outputs")
    return [{"case_id": f"{identifier}-C{i + 1}", "stdin": str(stdin).removesuffix("\n") + "\n",
             "expected_stdout": str(float(value))} for i, (stdin, value) in enumerate(zip(inputs, expected))]


def consumed_format_report(inventory):
    """Verify newline inputs and integer-output formatting without altering cases."""
    rows = overlap._consumed(inventory, ("cases",))
    report = {"cases": len(rows), "stdin_one_trailing_newline": 0, "canonical_integer_float_outputs": 0,
              "other_integer_outputs": 0, "noninteger_or_text_outputs": 0}
    for row in rows:
        text = row["expected_stdout"]
        report["stdin_one_trailing_newline"] += row["value"].endswith("\n") and not row["value"].endswith("\n\n")
        try:
            value = float(text)
            if not math.isfinite(value) or not value.is_integer():
                raise ValueError
        except ValueError:
            report["noninteger_or_text_outputs"] += 1
        else:
            report["canonical_integer_float_outputs" if text == str(float(int(value)))
                   else "other_integer_outputs"] += 1
    return report


def _jsonable(value):
    if isinstance(value, functools.partial):
        return {"function": value.func.__name__, "module": value.func.__module__,
                "args": _jsonable(value.args), "keywords": _jsonable(value.keywords)}
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(_jsonable(value), indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    with path.open("xb") as handle:
        handle.write(raw)
    return hashlib.sha256(raw).hexdigest()


def build_candidate(seed, out_dir, *, label, authorized_construction=False, workers):
    validate_request(seed, label=label, authorized_construction=authorized_construction, workers=workers)
    requested = Path(out_dir)
    if requested.exists() or requested.is_symlink():
        raise GateStop("refusing an existing output path", {"out_dir": str(requested)})
    out = requested.resolve()
    if out.exists():
        raise GateStop("refusing an existing output path", {"out_dir": str(out)})
    if not out.parent.is_dir():
        raise GateStop("output parent directory must already exist", {"out_dir": str(out)})
    try:
        out.mkdir()  # The parent must already exist; no writes outside out_dir.
    except FileExistsError as exc:
        raise GateStop("refusing an existing output path", {"out_dir": str(out)}) from exc
    started = time.perf_counter()
    reports, log = {}, {"seed": seed, "label": label, "workers": workers, "timings_seconds": {}}
    current = "AUTHORITIES"

    def gate(name, operation):
        nonlocal current
        current = name
        print(f"I4b gate {name}: started", flush=True)
        before = time.perf_counter()
        try:
            result = operation()
            reports[name] = result
            if result["status"] != "PASS":
                raise GateStop(name + " failed", result)
            return result
        finally:
            log["timings_seconds"][name] = time.perf_counter() - before

    try:
        authority = gate("AUTHORITIES", _authorities)
        ledger, manifest = authority["ledger"], authority["r2_manifest"]
        runner = _memo(CompilerRunner(ROOT))
        primary = load_primary_slots(ROOT)
        gate("P1", lambda: gates.p1_nondegeneracy(primary))
        gate("P5", lambda: training.p5_novelty(primary))
        exclusions = [(identifier, index) for identifier, condition, index in
                      manifest["non_exempt_domain_equivalent_mutants"] if condition == "primary"]
        domains = {domain: [slot for slot in primary if slot["family"] == domain] for domain in training.DOMAINS}
        selection = gate("P6_ARRAY_SELECTION", lambda: gates.select_array_cases(
            domains["array_reduction"], gates.array_pool(seed), verifier=runner, excluded_mutants=exclusions))
        inputs = {"numeric_iteration": list(map(str, ledger["candidate_policy"]["primary_numeric_cases"])),
                  "array_reduction": selection["selected_inputs"]}
        log["primary_array_selection"] = selection
        for domain in training.DOMAINS:
            gate("P6_" + domain, lambda domain=domain: gates.p6_check(
                domains[domain], inputs[domain], runner, excluded_mutants=exclusions))
        primary_expected_values = {slot["task_id"]: [primary_expected(slot, stdin) for stdin in inputs[slot["family"]]]
                                   for slot in primary}
        gate("P2_PRIMARY", lambda: gates.p2_e1([(slot["task_id"], primary_source(slot),
              list(zip(inputs[slot["family"]], primary_expected_values[slot["task_id"]]))) for slot in primary], runner))
        records = training.training_records()

        def select_training():
            selections = []
            log["training_selections"] = selections
            for index, slot in enumerate(ledger["slots"]["training_paired_slots"], 1):
                selections.append(training.select_training_cases(slot, seed, inputs["array_reduction"]))
                print(f"I4b training selection {index}/60", flush=True)
            return {"status": "PASS", "selections": selections}

        selections = gate("R2_B_SELECTION", select_training)["selections"]
        selected = {row["slot"]["slot_id"]: row for row in selections}

        def verify_training():
            rows = []
            for index, item in enumerate(selections, 1):
                rows.append(training.verify_training_cases(item, runner))
                print(f"I4b training compiler verification {index}/60", flush=True)
            return {"status": "PASS", "slots": rows}

        gate("R2_B_COMPILER", verify_training)
        builder = training._builder()
        training_expected_values = {record["record_id"]: [builder.train_expected(record["condition"],
                                   selected[record["slot_id"]]["slot"], stdin)
                                   for stdin in selected[record["slot_id"]]["inputs"]] for record in records}
        gate("P2_TRAINING", lambda: gates.p2_e1([(record["record_id"], record["target"],
              list(zip(selected[record["slot_id"]]["inputs"], training_expected_values[record["record_id"]])))
              for record in records], runner))
        internal_cases = {record["record_id"]: [{"case_id": identifier, "stdin": stdin}
                          for identifier, stdin in zip(selected[record["slot_id"]]["case_ids"],
                                                       selected[record["slot_id"]]["inputs"])] for record in records}
        gate("P4", lambda: training.p4_catalog(selections, runner))
        gate("P3_SCAFFOLD", lambda: training.p3_paired_scaffold(records, internal_cases))
        gate("P3_TOKENS", lambda: training.p3_token_parity(records, training.TOKENIZER_DIR))

        def equivalence():
            programs = [{"id": slot["task_id"], "kind": "primary", "condition": None,
                         "family": slot["family"], "source": primary_source(slot), "exempt": False,
                         "domain_disjoint": False} for slot in primary]
            programs += [{"id": record["slot_id"], "kind": "training", "condition": record["condition"],
                          "family": record["family"], "source": record["target"],
                          "exempt": selected[record["slot_id"]]["domain_disjoint_composition_exempt"]
                                    and record["condition"] == "composition",
                          "domain_disjoint": selected[record["slot_id"]]["domain_disjoint_composition_exempt"]}
                         for record in records]
            actual = training.r2a_equivalence(programs, workers)
            expected = sorted(manifest["non_exempt_domain_equivalent_mutants"] +
                              authority["audit_domain_disjoint_equivalents"])
            return {"status": "PASS" if actual == expected else "FAIL", "programs": len(programs),
                    "actual": actual, "expected": expected,
                    "missing": sorted(set(map(tuple, expected)) - set(map(tuple, actual))),
                    "unexpected": sorted(set(map(tuple, actual)) - set(map(tuple, expected)))}

        gate("R2_A_RECOMPUTE", equivalence)
        tasks = secondary.sanity_tasks() + secondary.structural_tasks()
        e1 = gate("SECONDARY_E1", lambda: secondary.secondary_e1(tasks, inputs, runner))
        evaluation_cases = {slot["task_id"]: canonical_cases(slot["task_id"], inputs[slot["family"]],
                            primary_expected_values[slot["task_id"]]) for slot in primary}
        evaluation_cases.update({task["task_id"]: canonical_cases(task["task_id"], inputs[task["family"]],
                                 [task["expected_fn"](stdin) for stdin in inputs[task["family"]]]) for task in tasks})
        training_cases = {record["record_id"]: canonical_cases(record["slot_id"], selected[record["slot_id"]]["inputs"],
                          training_expected_values[record["record_id"]]) for record in records}
        items = ([{"id": slot["task_id"], "role": "primary", "prompt": primary_prompt(slot),
                   "source": primary_source(slot), "cases": evaluation_cases[slot["task_id"]]} for slot in primary]
                 + [{"id": task["task_id"], "role": "secondary", "group": task["group"], "prompt": task["prompt"],
                     "source": task["source"], "cases": evaluation_cases[task["task_id"]]} for task in tasks]
                 + [{"id": record["record_id"], "slot_id": record["slot_id"], "role": "training", "prompt": record["prompt"],
                     "model_user_message": record["model_user_message"], "source": record["target"],
                     "cases": training_cases[record["record_id"]]} for record in records])
        inventory = gate("CONSUMED_INVENTORY", lambda: {"status": "PASS", "inventory": overlap.consumed_inventory()})["inventory"]
        p7 = gate("P7", lambda: overlap.p7_overlap(items, inventory))
        reports["CONSUMED_FORMAT"] = consumed_format_report(inventory)
        kept_ids = {task["task_id"] for task in e1["kept"]} & set(p7["kept_secondary"])
        kept = [task for task in tasks if task["task_id"] in kept_ids]
        log["secondary_drops"] = [{"task_id": task["task_id"], "reasons":
                                   (["E1_FAIL_CANDIDATES_EXHAUSTED"] if task["task_id"] not in
                                    {row["task_id"] for row in e1["kept"]} else []) +
                                   (["P7_FAIL_CANDIDATES_EXHAUSTED"] if task["task_id"] not in p7["kept_secondary"] else [])}
                                  for task in tasks if task["task_id"] not in kept_ids]
        sanity_count = sum(task["group"] == "primitive_sanity" for task in kept)
        reports["SECONDARY_FINAL"] = {"status": "PASS", "kept": sorted(kept_ids), "dropped": log["secondary_drops"],
                                      "sanity_count": sanity_count, "SANITY_NOT_EVALUABLE": sanity_count < 12}
        current = "WRITE"
        before = time.perf_counter()
        payload = {}
        for condition in training.CONDITIONS:
            members = [record for record in records if record["condition"] == condition]
            payload[f"training/{condition}_examples.json"] = [
                {"example_id": record["record_id"], "model_task_id": record["slot_id"], "slot_id": record["slot_id"],
                 "family": record["family"], "prompt": record["prompt"], "target": record["target"],
                 "semantic_primitives": [record["P"], record["Q"]]} for record in members]
            payload[f"training/{condition}_cases.json"] = {record["record_id"]: training_cases[record["record_id"]]
                                                           for record in members}
        payload["evaluation/tasks.json"] = [{key: value for key, value in slot.items() if not key.startswith("_")}
                                           | {"group": "novel_composition", "prompt": primary_prompt(slot)} for slot in primary]
        payload["evaluation/tasks.json"] += [{key: task[key] for key in ("task_id", "family", "group", "prompt")}
                                            for task in kept]
        payload["evaluation/references.json"] = {slot["task_id"]: primary_source(slot) for slot in primary}
        payload["evaluation/references.json"].update({task["task_id"]: task["source"] for task in kept})
        payload["evaluation/hidden_cases.json"] = {task["task_id"]: evaluation_cases[task["task_id"]]
                                                  for task in payload["evaluation/tasks.json"]}
        reports["COMPILER_RUNS"] = runner.calls
        payload["gates/gate_report.json"] = reports
        file_hashes = {name: _write(out / name, value) for name, value in payload.items()}
        log["timings_seconds"]["WRITE_DATA"] = time.perf_counter() - before
        log["wall_seconds_before_manifest"] = time.perf_counter() - started
        file_hashes["construction_log.json"] = _write(out / "construction_log.json", log)
        result = {"phase": "PHASE_3C_CONF1", "label": label, "construction_seed": seed,
                  "status": "CANDIDATE_GATES_PASSED_NOT_FROZEN", "model_execution_authorized": False,
                  "authority_hashes": authority["authority_hashes"], "code_hashes": authority["code_hashes"],
                  "compiler_sha256": authority["compiler_sha256"], "tokenizer_hashes": authority["tokenizer_hashes"],
                  "file_sha256": file_hashes,
                  "file_hash_scope": "All written payload files; manifest hash reported externally to avoid self-reference",
                  "gate_summary": {name: row["status"] for name, row in reports.items()
                                   if isinstance(row, dict) and "status" in row},
                  "counts": {"training": {condition: 60 for condition in training.CONDITIONS}, "primary": 32,
                             "secondary_kept": len(kept), "secondary_dropped": len(tasks) - len(kept),
                             "sanity_kept": sanity_count, "evaluation": 32 + len(kept), "training_cases": 600,
                             "evaluation_cases": 5 * (32 + len(kept))}}
        _write(out / "candidate_manifest.json", result)
        return result
    except GateStop as exc:
        stop = {"gate": current, "reason": str(exc), "evidence": exc.report,
                "completed_gate_reports": reports, "partial_construction_log": log}
        _write(out / "STOP_report.json", stop)
        raise GateStop(str(exc).removeprefix("STOP: "), stop) from exc
