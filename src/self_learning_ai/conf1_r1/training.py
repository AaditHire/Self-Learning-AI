"""R1 + R2 training gates; deterministic functions with no artifact writes.

Selectors require a caller-authorized seed and explicit array evaluation inputs.
The interpreter ranks cases; the pinned compiler establishes selected verdicts.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import random
import re
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

from self_learning_ai.conf1_r1 import interp
from self_learning_ai.conf1_r1.gates_primary import (
    ROOT, CompilerRunner, GateStop, InterpreterRunner, _audit, _comparison, _memo,
)
from self_learning_ai.conf1_r1.primary import load_primary_slots, primary_source


R2_MANIFEST = "research/protocols/phase3c_conf1_rebaseline_r2_freeze.json"
R2_MANIFEST_SHA256 = "e498f31a66caeb19633bdf1a229716b8942dd180c16910dac1246c5d93693375"
TOKENIZER_DIR = ROOT / ".models/Qwen2.5-Coder-3B-Instruct-488639f"
TOKENIZER_HASHES = {
    "tokenizer.json": "c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539",
    "tokenizer_config.json": "959e7f1d9a1b7641a6d6ce05ca97b75c7894fcb66cbe5a040406458fb1128ee4",
}
CONDITIONS = ("isolated", "composition")
DOMAINS = ("numeric_iteration", "array_reduction")
CANONICAL = "CONF1-TR-NU-01-V0"


def _definitions(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    if spec is None or spec.loader is None:
        raise GateStop("required implementation definitions unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Definitions only: never invoke a writing main().
    return module


@lru_cache(maxsize=1)
def _builder():
    # The audit installs the scripts import path needed by the historical builder.
    _r2_definitions()
    return _definitions("build_phase3c_conf1_data")


@lru_cache(maxsize=1)
def _r2_definitions():
    return _definitions("audit_phase3c_conf1_r2_liveness_feasibility")


def _authorities():
    load_primary_slots(ROOT)  # Verifies R1 amendment and byte-exact slot ledger.
    raw = (ROOT / R2_MANIFEST).read_bytes()
    if hashlib.sha256(raw).hexdigest() != R2_MANIFEST_SHA256:
        raise GateStop("R2 freeze manifest SHA-256 mismatch")
    manifest = json.loads(raw)
    amendment = (ROOT / manifest["frozen_amendment_path"]).read_bytes().replace(b"\r\n", b"\n")
    if hashlib.sha256(amendment).hexdigest() != manifest["frozen_amendment_sha256_lf_normalized"]:
        raise GateStop("R2 amendment SHA-256 mismatch")
    ledger = json.loads((ROOT / "research/protocols/phase3c_conf1_slots.json").read_bytes())
    slots = ledger["slots"]["training_paired_slots"]
    if len(slots) != 60 or len({slot["slot_id"] for slot in slots}) != 60:
        raise GateStop("training slot population mismatch")
    exclusions = defaultdict(set)
    for identifier, condition, index in manifest["non_exempt_domain_equivalent_mutants"]:
        exclusions[identifier, condition].add(index)
    return ledger, manifest, exclusions


def _slot(slot):
    ledger, _, exclusions = _authorities()
    matches = [s for s in ledger["slots"]["training_paired_slots"] if s["slot_id"] == slot["slot_id"]]
    if len(matches) != 1 or any(slot.get(key) != value for key, value in matches[0].items()):
        raise GateStop("slot differs from frozen training ledger")
    return copy.deepcopy(matches[0]), ledger["predicate_definitions"], exclusions


def _clause(record):
    descriptions = _builder().DESCRIPTIONS
    p, q = descriptions[record["P"]], descriptions[record["Q"]]
    if record["condition"] == "isolated":
        return f"independently tally {p} and {q}"
    if record["condition"] == "composition":
        return f"tally items satisfying both {p} and {q}"
    raise GateStop("unknown training condition")


def training_records():
    """Return the 120 targets/prompts; record IDs never enter the C9 wrapper."""
    ledger, _, _ = _authorities()
    builder = _builder()
    records = []
    for slot in ledger["slots"]["training_paired_slots"]:
        for condition in CONDITIONS:
            record = {key: slot[key] for key in ("slot_id", "family", "P", "Q", "offset", "reverse")}
            record.update(condition=condition,
                          record_id=slot["slot_id"].replace("CONF1-TR-", f"CONF1-{condition.upper()}-TR-", 1))
            record["prompt"] = (builder.prompt_prefix(slot["family"]) + "For each item, "
                                + _clause(record) + "; begin at " + str(slot["offset"])
                                + " and print the total.")
            record["target"] = builder.train_source(condition, slot)
            record["model_user_message"] = f"Task {slot['slot_id']}\n\n{record['prompt']}"
            records.append(record)
    return records


def classify(source, domain, role):
    """C7 preorder rows, indexed exactly like the accepted deletion enumerator."""
    if domain not in DOMAINS or role not in ("training", "primary"):
        raise GateStop("unknown classification domain or role")
    ledger, _, _ = _authorities()
    predicates = {p["expression"]: p["name"] for p in ledger["predicate_definitions"][domain]}
    try:
        units = interp.split_statements(source)
    except ValueError as exc:
        raise GateStop("unclassified source structure") from exc
    decode = ({"NUMBER n.", "INPUT(n)."} if domain == "numeric_iteration" else
              {"IMPORT strings.", "SENTENCE line.", "INPUT(line).",
               'SENTENCE[] parts = strings.SPLIT(line, "|").', "NUMBER[] values=[a,b,c,d].",
               *(f"NUMBER {name} = strings.TO_NUMBER(parts[{i}])." for i, name in enumerate("abcd"))})
    forward = "NUMBER i=1 TILL i<=n, i++" if domain == "numeric_iteration" else "NUMBER i=0 TILL i<4, i++"
    reverse = "i>=1" if domain == "numeric_iteration" else "i>=0"
    counter = "NUMBER i=n." if domain == "numeric_iteration" else "NUMBER i=3."
    rows = []
    loop_count = 0

    def visit(sequence, parent=None):
        nonlocal loop_count
        for unit in sequence:
            row = {"index": len(rows), "text": unit.text, "kind": None}
            text = unit.text.strip()
            if unit.kind == "LOOP":
                loop_count += 1
                if parent is None and unit.header == forward:
                    row.update(kind="K2", traversal="forward")
                elif parent is None and role == "training" and unit.header == reverse:
                    row.update(kind="K2", traversal="reverse")
            elif unit.kind == "IF":
                if (parent == "LOOP" and unit.header in predicates and len(unit.children) == 1
                        and re.fullmatch(r"hit[A-Za-z]+\s*=\s*1\.", unit.children[0].text.strip())):
                    row.update(kind="K3", predicate=predicates[unit.header])
            elif text in decode and parent is None:
                row["kind"] = "K1"
            elif role == "training" and ((text == counter and parent is None)
                                         or (text == "i-=1." and parent == "LOOP")):
                row.update(kind="K2", traversal="reverse")
            elif ((parent is None and re.fullmatch(r"NUMBER hit[A-Za-z]+=0\.", text))
                  or (parent == "LOOP" and re.fullmatch(r"hit[A-Za-z]+=0\.", text))
                  or (parent == "IF" and re.fullmatch(r"hit[A-Za-z]+=1\.", text))):
                row["kind"] = "K4"
            elif parent is None and re.fullmatch(r"NUMBER total=\d+\.", text):
                row["kind"] = "K5"
            elif parent == "LOOP":
                match = re.fullmatch(r"total\+=\((hit[A-Za-z]+)([+*])(hit[A-Za-z]+)\)\.", text)
                if match and ((role == "training" and match[1] == "hitP" and match[3] == "hitQ")
                              or (role == "primary" and match[2] == "*")):
                    row.update(kind="K5", treatment="T-SUM" if match[2] == "+" else "T-JOINT")
            if row["kind"] is None and text == "DISPLAYNL(total)." and parent is None:
                row["kind"] = "K6"
            if row["kind"] is None:
                raise GateStop("unit outside C7", {"domain": domain, "role": role, "unit": text})
            row["row"] = "K3 PRED[" + row["predicate"] + "]" if row["kind"] == "K3" else row["kind"]
            rows.append(row)
            visit(unit.children, unit.kind)

    visit(units)
    if loop_count != 1:
        raise GateStop("canonical scaffold requires exactly one traversal")
    declarations = re.findall(r"\bNUMBER (hit[A-Za-z]+)=0\.", source)
    reads = set(re.findall(r"total\+=\((hit[A-Za-z]+)[+*](hit[A-Za-z]+)\)\.", source))
    if set(declarations) - {name for pair in reads for name in pair}:
        raise GateStop("R-CF3 unread indicator")
    return rows


def training_case_stream(slot, seed, array_eval_inputs):
    slot, _, _ = _slot(slot)
    tag = "train-numeric" if slot["family"] == "numeric_iteration" else "train-array"
    raw = f"{seed}|{slot['slot_id']}|{tag}".encode("utf-8")
    rng = random.Random(int.from_bytes(hashlib.sha256(raw).digest(), "big"))
    skipped, inputs = [], []
    if slot["family"] == "numeric_iteration":
        pool = [n for n in range(1, 61) if n not in (12, 13, 14)]
        inputs = [str(n) for n in rng.sample(pool, len(pool))]
    else:
        evaluation = list(array_eval_inputs)
        if len(evaluation) != 5 or len(set(evaluation)) != 5:
            raise GateStop("array training stream requires the five selected evaluation inputs")
        excluded, seen = set(evaluation), set()
        while len(inputs) < 256:
            value = "|".join(str(rng.randint(-16, 16)) for _ in range(4))
            reason = "duplicate" if value in seen else "evaluation_input" if value in excluded else None
            if reason:
                skipped.append({"input": value, "reason": reason})
            else:
                inputs.append(value)
                seen.add(value)
    return {"inputs": inputs, "skipped": skipped}


def _requirements(slot, exclusions):
    return _r2_definitions().requirements(slot, exclusions)


def _mask(slot, stdin, requirements, sources, definitions, engine, remaining=None, witnesses=None):
    references = {condition: engine.run(source, stdin) for condition, source in sources.items()}
    if any(result[0] != "ok" for result in references.values()):
        raise GateStop("training reference fails", {"slot": slot["slot_id"], "stdin": stdin})
    if witnesses is None:
        items = _r2_definitions().truth_items(slot, stdin, definitions)
        witnesses = {(role, value): any(item[position] == value for item in items)
                     for position, role in enumerate(("P", "Q")) for value in (False, True)}
        witnesses["both_true"] = any(p and q for p, q in items)
    mask = 0
    for index, (requirement, mutant) in enumerate(requirements):
        if remaining is not None and not (remaining >> index) & 1:
            continue
        condition = requirement["condition"]
        if requirement["gate"] == "P4(iii)":
            actual = engine.run(mutant, stdin)
            satisfied = actual[0] != "ok" or actual[1] != references[condition][1]
        elif requirement["gate"] == "P4(v)":
            satisfied = references["isolated"] != references["composition"]
        elif requirement.get("requirement") == "both_true":
            satisfied = witnesses["both_true"]
        else:
            satisfied = witnesses[requirement["predicate"], requirement["truth"]]
        if satisfied:
            mask |= 1 << index
    return mask, references


def select_training_cases(slot, seed, array_eval_inputs, oracle=InterpreterRunner):
    """R2-B cumulative greedy; a maximum score ends the earliest-index search."""
    slot, definitions, exclusions = _slot(slot)
    stream = training_case_stream(slot, seed, array_eval_inputs)
    requirements, sources = _requirements(slot, exclusions)
    engine = _memo(oracle)
    full = (1 << len(requirements)) - 1
    indices, inputs, counts, covered = [], [], [], 0
    if slot["slot_id"] == CANONICAL:
        inputs.append("0")
        indices.append(None)
        covered = _mask(slot, "0", requirements, sources, definitions, engine)[0]
        counts.append(covered.bit_count())
    chosen = set()
    while len(inputs) < 5:
        remaining = full ^ covered
        best_index, best_mask, best_count = None, 0, -1
        for index, stdin in enumerate(stream["inputs"]):
            if index in chosen:
                continue
            mask = _mask(slot, stdin, requirements, sources, definitions, engine, remaining)[0] if remaining else 0
            score = (covered | mask).bit_count()
            if score > best_count:
                best_index, best_mask, best_count = index, mask, score
            if score == len(requirements):
                break  # All later equal maxima lose the frozen earliest-position tie.
        chosen.add(best_index)
        indices.append(best_index)
        inputs.append(stream["inputs"][best_index])
        covered |= best_mask
        counts.append(covered.bit_count())
    all_masks = [_mask(slot, stdin, requirements, sources, definitions, engine)[0] for stdin in inputs]
    unmet = [row for i, (row, _) in enumerate(requirements) if not any(mask >> i & 1 for mask in all_masks)]
    if unmet:
        raise GateStop("R2-B requirements unmet after five cases", {"slot": slot["slot_id"], "unmet": unmet})
    return {"status": "PASS", "slot": slot, "seed": seed, "inputs": inputs,
            "case_ids": [f"{slot['slot_id']}-C{i + 1}" for i in range(5)],
            "selected_stream_indices": indices, "skipped": stream["skipped"],
            "satisfied_after_each_pick": counts, "requirements_total": len(requirements),
            "oracle_outcomes": [(source, stdin, list(outcome)) for (source, stdin), outcome in engine.cache.items()
                                if stdin in inputs], "oracle_masks": all_masks,
            "domain_disjoint_composition_exempt": _r2_definitions().domain_disjoint(slot)}


def verify_training_cases(selection, verifier=CompilerRunner):
    """Recompute every selected (iii)-(v) verdict and compare oracle outcomes."""
    slot, definitions, exclusions = _slot(selection["slot"])
    inputs = selection["inputs"]
    if len(inputs) != 5 or len(set(inputs)) != 5 or len(selection["case_ids"]) != 5:
        raise GateStop("training selection must contain five distinct ordered cases")
    requirements, sources = _requirements(slot, exclusions)
    engine = _memo(verifier)
    before = engine.calls
    jobs = [(source, stdin) for source in [*sources.values(), *(m for _, m in requirements if m is not None)]
            for stdin in inputs]
    # Diagnostic probes retain the frozen decoder, traversal and predicate code.
    # Only the displayed count is instrumented: one predicate's indicator sum,
    # from offset zero. These are compiler witnesses, never training targets.
    probe_base = sources["isolated"].replace(f"NUMBER total={slot['offset']}.", "NUMBER total=0.", 1)
    probes = {role: probe_base.replace("total+=(hitP+hitQ).", f"total+=(hit{role}).", 1)
              for role in ("P", "Q")}
    engine.prefetch([*jobs, *((source, stdin) for source in probes.values() for stdin in inputs)])
    oracle = {(source, stdin): tuple(result) for source, stdin, result in selection["oracle_outcomes"]}
    for source, stdin in dict.fromkeys(jobs):
        if (source, stdin) not in oracle:
            raise GateStop("missing selected-case oracle verdict")
        observed = engine.run(source, stdin)
        if _comparison(oracle[source, stdin]) != _comparison(observed):
            raise GateStop("oracle/verifier disagreement", {"kind": "oracle_verifier_disagreement",
                           "slot": slot["slot_id"], "stdin": stdin, "oracle": oracle[source, stdin],
                           "verifier": observed, "source": source})
    masks = []
    for stdin in inputs:
        items = _r2_definitions().truth_items(slot, stdin, definitions)
        witnesses = {}
        for position, role in enumerate(("P", "Q")):
            expected_count = sum(item[position] for item in items)
            observed = engine.run(probes[role], stdin)
            if observed != ("ok", str(float(expected_count))):
                raise GateStop("oracle/verifier predicate disagreement", {"slot": slot["slot_id"],
                               "stdin": stdin, "predicate": role, "expected": expected_count,
                               "verifier": observed})
            true_count = int(float(observed[1]))
            witnesses[role, True] = true_count > 0
            witnesses[role, False] = true_count < len(items)
        composition = engine.run(sources["composition"], stdin)
        joint_expected = sum(p and q for p, q in items)
        if composition != ("ok", str(float(slot["offset"] + joint_expected))):
            raise GateStop("oracle/verifier joint-predicate disagreement", {"slot": slot["slot_id"], "stdin": stdin})
        witnesses["both_true"] = int(float(composition[1])) - slot["offset"] > 0
        masks.append(_mask(slot, stdin, requirements, sources, definitions, engine, witnesses=witnesses)[0])
    if masks != selection["oracle_masks"]:
        raise GateStop("oracle/verifier requirement disagreement")
    rows = [{**row, "satisfied": any(mask >> index & 1 for mask in masks)}
            for index, (row, _) in enumerate(requirements)]
    if not all(row["satisfied"] for row in rows):
        raise GateStop("compiler-verified training requirements unmet", {"requirements": rows})
    return {"status": "PASS", "slot_id": slot["slot_id"], "requirements": rows,
            "compiler_runs": engine.calls - before, "disagreements": 0,
            "reference_outcomes": {c: [engine.run(s, stdin) for stdin in inputs] for c, s in sources.items()}}


def p4_catalog(selections, verifier=CompilerRunner):
    """Canonical conformance and C7 live-row coverage, excluding R2-A mutants."""
    selections = list(selections)
    expected = training_records()
    ledger, _, _ = _authorities()
    selection_by_id = {s["slot"]["slot_id"]: s for s in selections}
    if len(selections) != 60 or set(selection_by_id) != {r["slot_id"] for r in expected}:
        raise GateStop("P4 requires all 60 matched training selections")
    engine = _memo(verifier)
    verified = {identifier: verify_training_cases(selection, engine)
                for identifier, selection in selection_by_id.items()}
    primary = load_primary_slots(ROOT)
    for slot in primary:
        classify(primary_source(slot), slot["family"], "primary")
    witnesses = defaultdict(list)
    for record in expected:
        units = classify(record["target"], record["family"], "training")
        report = verified[record["slot_id"]]
        killed = {row["mutant_index"] for row in report["requirements"]
                  if row["gate"] == "P4(iii)" and row["condition"] == record["condition"] and row["satisfied"]}
        for unit in units:
            if unit["index"] not in killed:
                continue
            rows = [unit["row"]]
            if unit["kind"] == "K2":
                rows = ["K2 " + unit["traversal"]]
            if unit.get("treatment"):
                rows.append(unit["treatment"])
            for row in rows:
                witnesses[record["condition"], record["family"], row].append(
                    {"slot_id": record["slot_id"], "mutant_index": unit["index"]})
    table = []
    for condition in CONDITIONS:
        for domain in DOMAINS:
            predicates = {s["role_predicates"][role] for s in primary if s["family"] == domain
                          for role in s["used_roles"]}
            required = ["K1", "K2 forward", "K4", "K5", "K6"] + [
                "K3 PRED[" + p["name"] + "]" for p in ledger["predicate_definitions"][domain]
                if p["name"] in predicates]
            for row in [*required, "K2 reverse", "T-SUM", "T-JOINT"]:
                live = witnesses[condition, domain, row]
                table.append({"condition": condition, "domain": domain, "row": row,
                              "required": row in required, "live": bool(live), "witnesses": live})
    return {"status": "PASS" if all(r["live"] for r in table if r["required"]) else "FAIL",
            "classified_training": len(expected), "classified_primary": len(primary), "rows": table}


def _tokenizer(tokenizer_dir):
    directory = Path(tokenizer_dir)
    for name, expected in TOKENIZER_HASHES.items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != expected:
            raise GateStop("pinned tokenizer SHA-256 mismatch: " + name)
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(directory, local_files_only=True, trust_remote_code=False)


def _chat(tokenizer, user, target=None):
    system = (ROOT / "prompts/phase1t_system.txt").read_text(encoding="utf-8").strip()
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    if target is not None:
        messages.append({"role": "assistant", "content": target})
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=target is None)


def p3_paired_scaffold(records, cases):
    records = list(records)
    groups, failures = defaultdict(list), []
    tokenizer = _tokenizer(TOKENIZER_DIR)
    for record in records:
        groups[record["slot_id"]].append(record)
    ledger, _, _ = _authorities()
    if set(groups) != {s["slot_id"] for s in ledger["slots"]["training_paired_slots"]}:
        failures.append({"reason": "slot population"})
    for identifier, pair in groups.items():
        if len(pair) != 2 or {r["condition"] for r in pair} != set(CONDITIONS):
            failures.append({"slot_id": identifier, "reason": "missing or duplicate pair"})
            continue
        abstract_sources, abstract_chats, fields, paired_cases = [], [], [], []
        for record in sorted(pair, key=lambda r: CONDITIONS.index(r["condition"])):
            expression = "hitP+hitQ" if record["condition"] == "isolated" else "hitP*hitQ"
            marked = "total+=(" + expression + ")."
            source = record["target"]
            try:
                units = classify(source, record["family"], "training")
                updates = [row for row in units if row["text"] == marked]
            except GateStop:
                updates = []
            clause, user = _clause(record), record["model_user_message"]
            if (len(updates) != 1 or source.count(marked) != 1 or user.count(clause) != 1
                    or record["prompt"].count(clause) != 1
                    or user != f"Task {identifier}\n\n{record['prompt']}"):
                failures.append({"slot_id": identifier, "reason": "marked span or C9 wrapper"})
                continue
            abstract_sources.append(source.replace(marked, "total+=(<TREATMENT_EXPRESSION>).", 1))
            abstract_chats.append(_chat(tokenizer, user.replace(clause, "<TREATMENT_DESCRIPTION>", 1)))
            fields.append(tuple(record[key] for key in ("slot_id", "family", "P", "Q", "offset", "reverse")))
            selected = cases.get(record["record_id"])
            if selected is None or len(selected) != 5:
                failures.append({"slot_id": identifier, "reason": "missing ordered cases"})
                continue
            paired_cases.append([(case["case_id"], case["stdin"]) for case in selected])
        if not all(len(values) == 2 and values[0] == values[1]
                   for values in (abstract_sources, abstract_chats, fields, paired_cases)):
            failures.append({"slot_id": identifier, "reason": "paired scaffold difference"})
    return {"status": "FAIL" if failures else "PASS", "paired_slots": len(groups), "failures": failures}


def p3_token_parity(records, tokenizer_dir):
    tokenizer = _tokenizer(tokenizer_dir)
    totals = {c: {"examples": 0, "full": 0, "supervised": 0, "max_full": 0} for c in CONDITIONS}
    failures = []
    for record in records:
        condition = record["condition"]
        if condition not in totals:
            raise GateStop("unknown training condition")
        prompt_ids = tokenizer(_chat(tokenizer, record["model_user_message"]), add_special_tokens=False)["input_ids"]
        full_ids = tokenizer(_chat(tokenizer, record["model_user_message"], record["target"]),
                             add_special_tokens=False)["input_ids"]
        if full_ids[:len(prompt_ids)] != prompt_ids:
            raise GateStop("runner chat-template prefix mismatch")
        values = totals[condition]
        values["examples"] += 1
        values["full"] += len(full_ids)
        values["supervised"] += len(full_ids) - len(prompt_ids)
        values["max_full"] = max(values["max_full"], len(full_ids))
        if len(full_ids) > 320:
            failures.append({"record_id": record["record_id"], "full": len(full_ids)})
    differences = {key: abs(totals["composition"][key] - totals["isolated"][key]) / totals["isolated"][key]
                   if totals["isolated"][key] else float("inf") for key in ("full", "supervised")}
    passed = (all(row["examples"] == 60 for row in totals.values()) and not failures
              and differences["full"] <= 0.05 and differences["supervised"] <= 0.02)
    return {"status": "PASS" if passed else "FAIL", "totals": totals,
            "relative_differences": differences, "above_320": failures}


def p5_novelty(primary_slots):
    rows = []
    domains = {}
    for slot in primary_slots:
        domain = slot["family"]
        if domain not in domains:
            patterns = _audit.feasible_patterns(domain)
            domains[domain] = (patterns, *_audit.comparison_functions(patterns))
        patterns, pairs, consumed = domains[domain]
        names = [name for name, _, _ in _audit.PREDICATES[domain]]
        used = "PQR" if slot["graph"] in ("G1", "G3P") else "PQRS"
        indices = {role: names.index(slot["role_predicates"][role]) for role in used}
        bits = [tuple(pattern[indices[r]] if r in used else 0 for r in "PQRS") for pattern in patterns]
        function = tuple(_audit.contribution(slot["graph"], *b) for b in bits)
        terms = [_audit.terms(slot["graph"], *b) for b in bits]
        live = [term for term in terms[0] if any(values[term] for values in terms)]
        by_pattern = dict(zip(patterns, function))
        influential = []
        for predicate in dict.fromkeys(slot["role_predicates"][r] for r in used):
            index = names.index(predicate)
            for pattern in patterns:
                changed = list(pattern)
                changed[index] = 1 - changed[index]
                changed = tuple(changed)
                if changed in by_pattern and by_pattern[pattern] != by_pattern[changed]:
                    influential.append(predicate)
                    break
        equals_pair, equals_consumed = function in pairs, function in consumed
        passed = not equals_pair and not equals_consumed and len(influential) >= 3 and len(live) >= 2
        rows.append({"task_id": slot["task_id"], "status": "PASS" if passed else "FAIL",
                     "equals_pair_function": equals_pair, "equals_consumed_function": equals_consumed,
                     "influential_predicates": influential, "live_terms": live,
                     "normalized_offset": slot.get("offset", 0), "function": list(function)})
    return {"status": "PASS" if rows and all(row["status"] == "PASS" for row in rows) else "FAIL", "slots": rows}


def _equivalence_job(job):
    # E1's accepted cache is confined to this worker process, never the selector.
    return _r2_definitions().e1_program(job)


def r2a_equivalence(programs, workers):
    """Recompute E1's entire input enumeration, returning all equivalent triples."""
    _authorities()
    programs = list(programs)
    if workers < 1 or len({(p["id"], p["condition"]) for p in programs}) != len(programs):
        raise GateStop("invalid E1 program population or worker count")
    jobs = [(i, p, float("inf")) for i, p in enumerate(programs)]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(_equivalence_job, jobs))
    return sorted([row["id"], row["condition"] or "primary", mutant["mutant_index"]]
                  for _, row in rows for mutant in row["equivalents"])
