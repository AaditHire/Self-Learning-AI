"""Build prospective CONF1 examples and evaluation without model use."""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from pathlib import Path

from build_phase2b_data import ast_proxy, case, split_numbers
from design_phase3c_conf1 import contribution, numeric_items, array_items, count

ROOT = Path(__file__).resolve().parents[1]
LEDGER = json.loads((ROOT / "research/protocols/phase3c_conf1_slots.json").read_text(encoding="utf-8"))
SEED = LEDGER["construction_seed"]
NUMERIC_PRIMARY = tuple(LEDGER["candidate_policy"]["primary_numeric_cases"])
PREDICATES = {f: {p["name"]: p["expression"] for p in ps}
              for f, ps in LEDGER["predicate_definitions"].items()}
DESCRIPTIONS = {
    "odd_index": "an odd position", "residue_two": "a position congruent to two modulo three",
    "divisor_index": "a positive position dividing the input", "first_half": "a position in the first half",
    "negative_value": "a negative entry", "even_value": "an even entry",
    "large_magnitude": "an entry with square above four",
    "value_exceeds_index": "an entry greater than its zero-based position",
}
GROUP_PROMPTS = {
    "G1": "Count each item once when P and at least one of Q or R holds.",
    "G2": "Add three counts: P with Q, Q with R, and R with S. An item may contribute more than once.",
    "G3": "Add three counts: P with Q, P with R, and P with S. An item may contribute more than once.",
    "G4": "Add the count satisfying R with P or Q, and the separate count satisfying Q with S. An item may contribute twice.",
}
REJECTIONS: list[dict] = []


def write_json(path: Path, obj: object) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rng_for(slot: str, tag: str) -> random.Random:
    raw = f"{SEED}|{slot}|{tag}".encode()
    return random.Random(int.from_bytes(hashlib.sha256(raw).digest(), "big"))


def prefix(family: str) -> str:
    if family == "numeric_iteration":
        return "NUMBER n.\nINPUT(n).\n"
    return split_numbers(["a", "b", "c", "d"]) + "NUMBER[] values=[a,b,c,d].\n"


def loop(family: str, body: str, *, reverse: bool = False, index: str = "i") -> str:
    if family == "numeric_iteration":
        if reverse:
            return f"NUMBER {index}=n.\nLOOP ({index}>=1) {{ {body} {index}-=1. }}\n"
        return f"LOOP (NUMBER {index}=1 TILL {index}<=n, {index}++) {{ {body} }}\n"
    if reverse:
        return f"NUMBER {index}=3.\nLOOP ({index}>=0) {{ {body} {index}-=1. }}\n"
    return f"LOOP (NUMBER {index}=0 TILL {index}<4, {index}++) {{ {body} }}\n"


def prompt_prefix(family: str) -> str:
    return "Read one nonnegative integer. " if family == "numeric_iteration" else "Read four signed integers separated by vertical bars. "


def parse_input(family: str, stdin: str) -> list[tuple[int, tuple[bool, ...]]]:
    if family == "numeric_iteration":
        return numeric_items(int(stdin))
    return array_items(tuple(int(x) for x in stdin.split("|")))


def primitive_truth(family: str, primitive: str, bits: tuple[bool, ...]) -> bool:
    return bits[list(PREDICATES[family]).index(primitive)]


def train_source(condition: str, slot: dict) -> str:
    family, p, q, k = slot["family"], slot["P"], slot["Q"], slot["offset"]
    treatment = "hitP+hitQ" if condition == "isolated" else "hitP*hitQ"
    body = ("hitP=0. hitQ=0. "
            f"IF ({PREDICATES[family][p]}) {{ hitP=1. }} "
            f"IF ({PREDICATES[family][q]}) {{ hitQ=1. }} "
            f"total+=({treatment}).")
    return (prefix(family) + f"NUMBER total={k}.\nNUMBER hitP=0.\nNUMBER hitQ=0.\n"
            + loop(family, body, reverse=slot["reverse"]) + "DISPLAYNL(total).")


def train_expected(condition: str, slot: dict, stdin: str) -> int:
    return slot["offset"] + sum(
        (int(primitive_truth(slot["family"], slot["P"], bits))
         + int(primitive_truth(slot["family"], slot["Q"], bits)))
        if condition == "isolated" else
        int(primitive_truth(slot["family"], slot["P"], bits)
            and primitive_truth(slot["family"], slot["Q"], bits))
        for _, bits in parse_input(slot["family"], stdin)
    )


def primary_source(slot: dict) -> str:
    family, graph, roles = slot["family"], slot["graph"], slot["role_predicates"]
    declarations = "NUMBER total=0.\n" + "".join(f"NUMBER hit{role}=0.\n" for role in "PQRS")
    reset = " ".join(f"hit{role}=0." for role in "PQRS")
    checks = " ".join(f"IF ({PREDICATES[family][roles[role]]}) {{ hit{role}=1. }}" for role in "PQRS")
    treatment = {
        "G1": "IF (hitP*hitQ+hitP*hitR>0) { total+=1. }",
        "G2": "total+=hitP*hitQ+hitQ*hitR+hitR*hitS.",
        "G3": "total+=hitP*hitQ+hitP*hitR+hitP*hitS.",
        "G4": "hitOr=0. IF (hitP+hitQ>0) { hitOr=1. } total+=hitOr*hitR+hitQ*hitS.",
    }[graph]
    if graph == "G4":
        declarations += "NUMBER hitOr=0.\n"
    return prefix(family) + declarations + loop(family, f"{reset} {checks} {treatment}") + "DISPLAYNL(total)."


def primary_expected(slot: dict, stdin: str) -> int:
    return count(slot["graph"], slot["rotation"], parse_input(slot["family"], stdin))


def sanity_source(slot: dict) -> str:
    family, p, k = slot["family"], slot["primitive"], slot["offset"]
    body = f"hit=0. IF ({PREDICATES[family][p]}) {{ hit=1. }} tally+=hit."
    return (prefix(family) + f"NUMBER tally={k}.\nNUMBER hit=0.\n" +
            loop(family, body) + "DISPLAYNL(tally).")


def sanity_expected(slot: dict, stdin: str) -> int:
    return slot["offset"] + sum(int(primitive_truth(slot["family"], slot["primitive"], bits))
                                for _, bits in parse_input(slot["family"], stdin))


def structural_source(slot: dict) -> str:
    family, structure, roles = slot["family"], slot["structure"], slot["role_predicates"]
    p, q = PREDICATES[family][roles["P"]], PREDICATES[family][roles["Q"]]
    if structure == "prefix_running_pair":
        body = f"IF ({q}) {{ total+=seen. }} IF ({p}) {{ seen+=1. }}"
        return prefix(family) + "NUMBER seen=0.\nNUMBER total=0.\n" + loop(family, body) + "DISPLAYNL(total)."
    return (prefix(family) + "NUMBER left=0.\nNUMBER right=0.\n" +
            loop(family, f"IF ({p}) {{ left+=1. }}") +
            loop(family, f"IF ({q.replace('i','j')}) {{ right+=1. }}", index="j") +
            "DISPLAYNL(left*right).")


def structural_expected(slot: dict, stdin: str) -> int:
    family, roles = slot["family"], slot["role_predicates"]
    items = parse_input(family, stdin)
    p = [primitive_truth(family, roles["P"], bits) for _, bits in items]
    q = [primitive_truth(family, roles["Q"], bits) for _, bits in items]
    if slot["structure"] == "two_pass_product":
        return sum(p) * sum(q)
    seen = total = 0
    for a, b in zip(p, q):
        if b:
            total += seen
        if a:
            seen += 1
    return total


def training_cases(slot: dict, eval_array: tuple[str, ...]) -> list[str]:
    r = rng_for(slot["slot_id"], "train-numeric" if slot["family"] == "numeric_iteration" else "train-array")
    if slot["family"] == "numeric_iteration":
        pool = [n for n in range(1, 61) if n not in (12, 13, 14)]
        return [str(x) for x in sorted(r.sample(pool, 5))]
    out = []
    while len(out) < 5:
        candidate = "|".join(str(r.randint(-16, 16)) for _ in range(4))
        if candidate in out or candidate in eval_array:
            REJECTIONS.append({"kind": "training_case", "slot": slot["slot_id"],
                               "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
                               "reason": "duplicate_or_eval_input"})
            continue
        out.append(candidate)
    return out


def select_array_primary(primary_slots: list[dict]) -> tuple[str, ...]:
    r = random.Random(SEED)
    candidates = ["0|0|0|0"]
    for _ in range(4096):
        candidates.append("|".join(str(r.randint(-16, 16)) for _ in range(4)))
    local = [s for s in primary_slots if s["family"] == "array_reduction"]
    pairs = list(itertools.combinations(range(16), 2))
    outputs = [[primary_expected(s, x) for s in local] for x in candidates]
    remaining = set(range(120))
    chosen = [0]
    for _ in range(4):
        best = None
        for ci in range(1, len(candidates)):
            if ci in chosen:
                continue
            covered = {pi for pi in remaining if outputs[ci][pairs[pi][0]] != outputs[ci][pairs[pi][1]]}
            if best is None or len(covered) > len(best[1]):
                best = (ci, covered)
        assert best is not None
        chosen.append(best[0])
        remaining.difference_update(best[1])
    if remaining:
        raise ValueError(f"STOP_PREFREEZE_DESIGN_FAILURE: array five-case discrimination missing {len(remaining)} pairs")
    for ci, candidate in enumerate(candidates):
        if ci not in chosen:
            REJECTIONS.append({"kind": "array_case_candidate", "ordinal": ci,
                               "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
                               "reason": "not_selected_by_frozen_five_case_greedy_rule"})
    return tuple(candidates[ci] for ci in chosen)


def task_prompt(slot: dict) -> str:
    family = slot["family"]
    if slot["group"] == "novel_composition":
        descriptions = "; ".join(f"{role}: {DESCRIPTIONS[p]}" for role, p in slot["role_predicates"].items())
        return prompt_prefix(family) + f"Use these four tests ({descriptions}). " + GROUP_PROMPTS[slot["graph"]] + " Print the total."
    if slot["group"] == "primitive_sanity":
        return prompt_prefix(family) + f"Tally items that are {DESCRIPTIONS[slot['primitive']]}; begin the tally at {slot['offset']}. Print the final tally."
    descriptions = "; ".join(f"{role}: {DESCRIPTIONS[p]}" for role, p in slot["role_predicates"].items() if role in "PQ")
    if slot["structure"] == "prefix_running_pair":
        return prompt_prefix(family) + f"Use tests ({descriptions}). For each Q item, add the number of earlier P items. Print the sum."
    return prompt_prefix(family) + f"Use tests ({descriptions}). Count P and Q separately, then print the product of their counts."


def main() -> None:
    out_train = ROOT / "data/phase3c_conf1"
    out_eval = ROOT / "benchmark/phase3c_conf1"
    out_reject = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE/candidate_attempts.json"
    if out_train.exists() or out_eval.exists() or out_reject.exists():
        raise FileExistsError("CONF1 construction output already exists")
    slots = LEDGER["slots"]
    arr_eval = select_array_primary(slots["primary"])
    eval_inputs = {"numeric_iteration": tuple(str(n) for n in NUMERIC_PRIMARY), "array_reduction": arr_eval}
    for condition in ("isolated", "composition"):
        rows, refs, cases = [], {}, {}
        for slot in slots["training_paired_slots"]:
            sid = slot["slot_id"]
            ident = sid.replace("CONF1-TR", f"CONF1-{condition.upper()}-TR")
            source = train_source(condition, slot)
            p, q = slot["P"], slot["Q"]
            clause = (f"independently tally {DESCRIPTIONS[p]} and {DESCRIPTIONS[q]}"
                      if condition == "isolated" else
                      f"tally items satisfying both {DESCRIPTIONS[p]} and {DESCRIPTIONS[q]}")
            prompt = prompt_prefix(slot["family"]) + f"For each item, {clause}; begin at {slot['offset']} and print the total."
            inputs = training_cases(slot, arr_eval)
            rows.append({"example_id": ident, "slot_id": sid, "family": slot["family"],
                         "archetype": "pair_" + "_".join(slot["unordered_pair"]),
                         "prompt": prompt, "target": source, "semantic_primitives": [p, q],
                         "composition_signature": f"training:{condition}:{p}:{q}",
                         "ast_proxy_signature": ast_proxy(source)})
            refs[ident] = source
            cases[ident] = [case(j + 1, x, train_expected(condition, slot, x)) for j, x in enumerate(inputs)]
        write_json(out_train / f"{condition}_examples.json", rows)
        write_json(out_train / f"{condition}_references.json", refs)
        write_json(out_train / f"{condition}_cases.json", cases)
    rows, refs, cases = [], {}, {}
    for group in ("primary", "primitive_sanity", "structural_transfer"):
        for slot in slots[group]:
            ident, family = slot["task_id"], slot["family"]
            source = (primary_source(slot) if group == "primary" else
                      sanity_source(slot) if group == "primitive_sanity" else structural_source(slot))
            expected = (primary_expected if group == "primary" else
                        sanity_expected if group == "primitive_sanity" else structural_expected)
            rows.append({"task_id": ident, "family": family, "group": slot["group"],
                         "block_id": slot.get("block_id", slot.get("structure", slot.get("primitive"))),
                         "prompt": task_prompt(slot), "semantic_primitives":
                         list(slot["role_predicates"].values()) if "role_predicates" in slot else [slot["primitive"]],
                         "composition_signature": slot.get("composition_signature", slot.get("structure", "single_primitive")),
                         "ast_proxy_signature": ast_proxy(source), "required_regex": []})
            refs[ident] = source
            cases[ident] = [case(j + 1, x, expected(slot, x)) for j, x in enumerate(eval_inputs[family])]
    write_json(out_eval / "tasks.json", rows)
    write_json(out_eval / "references.json", refs)
    write_json(out_eval / "hidden_cases.json", cases)
    write_json(out_reject, {"construction_seed": SEED, "selected_domain_inputs": eval_inputs,
                            "rejections": REJECTIONS,
                            "no_model_outcomes_inspected": True})
    print(json.dumps({"train_per_condition": 60, "primary": 32, "sanity": 16,
                      "structural": 16, "cases": 320, "array_inputs": arr_eval,
                      "rejections": len(REJECTIONS)}))


if __name__ == "__main__":
    main()
