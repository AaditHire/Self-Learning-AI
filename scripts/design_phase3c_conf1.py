"""Create the prospective CONF1 semantic ledger and non-model graph audit only."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN_SEED = 20290123
FAMILIES = {
    "numeric_iteration": [
        ("odd_index", "i%2==1"),
        ("residue_two", "i%3==2"),
        ("divisor_index", "n%i==0"),
        ("first_half", "2*i<=n"),
    ],
    "array_reduction": [
        ("negative_value", "values[i]<0"),
        ("even_value", "values[i]%2==0"),
        ("large_magnitude", "values[i]*values[i]>4"),
        ("value_exceeds_index", "values[i]>i"),
    ],
}
GRAPHS = {
    "G1": "(P&Q)|(P&R) counted once",
    "G2": "(P&Q)+(Q&R)+(R&S)",
    "G3": "(P&Q)+(P&R)+(P&S)",
    "G4": "((P|Q)&R)+(Q&S)",
}


def contribution(graph: str, bits: tuple[bool, ...]) -> int:
    p, q, r, s = bits
    return {
        "G1": int((p and q) or (p and r)),
        "G2": int(p and q) + int(q and r) + int(r and s),
        "G3": int(p and q) + int(p and r) + int(p and s),
        "G4": int((p or q) and r) + int(q and s),
    }[graph]


def rotated(bits: tuple[bool, ...], rotation: int) -> tuple[bool, ...]:
    return tuple(bits[(j + rotation) % 4] for j in range(4))


def numeric_items(n: int) -> list[tuple[int, tuple[bool, ...]]]:
    return [
        (i, (i % 2 == 1, i % 3 == 2, n % i == 0, 2 * i <= n))
        for i in range(1, n + 1)
    ]


def array_items(values: tuple[int, ...]) -> list[tuple[int, tuple[bool, ...]]]:
    return [
        (i, (x < 0, x % 2 == 0, x * x > 4, x > i))
        for i, x in enumerate(values)
    ]


def count(graph: str, rotation: int, items: list[tuple[int, tuple[bool, ...]]]) -> int:
    return sum(contribution(graph, rotated(bits, rotation)) for _, bits in items)


def mask(bits: tuple[bool, ...]) -> str:
    return "".join(str(int(x)) for x in bits)


def signatures() -> dict:
    assignments = list(itertools.product((False, True), repeat=4))
    permutations = list(itertools.permutations(range(4)))
    out = {}
    for graph in GRAPHS:
        raw = [contribution(graph, b) for b in assignments]
        canonical = min(
            tuple(contribution(graph, tuple(b[j] for j in perm)) for b in assignments)
            for perm in permutations
        )
        out[graph] = {
            "formula": GRAPHS[graph],
            "truth_rows": [{"PQRS": mask(b), "contribution": contribution(graph, b)} for b in assignments],
            "canonical_under_24_renamings": list(canonical),
            "rotations": {
                str(r): [{"PQRS": mask(b), "contribution": contribution(graph, rotated(b, r))} for b in assignments]
                for r in range(4)
            },
        }
    assert len({tuple(v["canonical_under_24_renamings"]) for v in out.values()}) == 4
    return out


def build_slots() -> dict:
    primary, sanity, structural, training = [], [], [], []
    pair_extras = {(0, 1): 0, (0, 2): 2, (0, 3): 3, (1, 2): 1, (1, 3): 1, (2, 3): 2}
    for family, predicates in FAMILIES.items():
        keys = [p[0] for p in predicates]
        tag = "NU" if family == "numeric_iteration" else "AR"
        for graph in GRAPHS:
            for rotation in range(4):
                primary.append({
                    "task_id": f"CONF1-NC-{tag}-{graph}-R{rotation}", "family": family,
                    "group": "novel_composition", "graph": graph, "rotation": rotation,
                    "block_id": f"{family}:{graph}",
                    "role_predicates": dict(zip("PQRS", keys[rotation:] + keys[:rotation])),
                    "composition_signature": f"{family}:{graph}:R{rotation}",
                })
        for pi, primitive in enumerate(keys):
            for variant in range(2):
                sanity.append({"task_id": f"CONF1-PS-{tag}-P{pi}-V{variant}", "family": family,
                               "group": "primitive_sanity", "primitive": primitive,
                               "variant": variant, "offset": 0 if variant == 0 else 3})
        for structure in ("prefix_running_pair", "two_pass_product"):
            for rotation in range(4):
                structural.append({"task_id": f"CONF1-ST-{tag}-{structure}-R{rotation}",
                                   "family": family, "group": "structural_transfer",
                                   "structure": structure, "rotation": rotation,
                                   "role_predicates": dict(zip("PQRS", keys[rotation:] + keys[:rotation]))})
        for pair in itertools.combinations(range(4), 2):
            for variant in range(5):
                extra = pair_extras[pair]
                first = extra if variant % 2 == 0 else next(x for x in pair if x != extra)
                second = next(x for x in pair if x != first)
                training.append({"slot_id": f"CONF1-TR-{tag}-{pair[0]}{pair[1]}-V{variant}",
                                 "family": family, "P": keys[first], "Q": keys[second],
                                 "unordered_pair": [keys[j] for j in pair], "variant": variant,
                                 "offset": (0, 2, 4, 6, 8)[variant],
                                 "reverse": (sum(pair) + variant) % 2 == 1})
    assert (len(primary), len(sanity), len(structural), len(training)) == (32, 16, 16, 60)
    return {"primary": primary, "primitive_sanity": sanity, "structural_transfer": structural,
            "training_paired_slots": training}


def witnesses(slots: list[dict]) -> dict:
    out = {}
    for family in FAMILIES:
        local = [x for x in slots if x["family"] == family]
        if family == "numeric_iteration":
            candidates = [{"input": str(n), "items": numeric_items(n)} for n in range(101)]
        else:
            candidates = []
            for index in range(4):
                for value in range(-15, 16):
                    values = [0, 0, 0, 0]
                    values[index] = value
                    candidates.append({"input": "|".join(map(str, values)), "items": array_items(tuple(values))})
        records = []
        for a, b in itertools.combinations(local, 2):
            found = None
            for candidate in candidates:
                ai = count(a["graph"], a["rotation"], candidate["items"])
                bi = count(b["graph"], b["rotation"], candidate["items"])
                if ai == bi:
                    continue
                distinguisher = next(
                    {"index": i, "PQRS": mask(bits),
                     "left_contribution": contribution(a["graph"], rotated(bits, a["rotation"])),
                     "right_contribution": contribution(b["graph"], rotated(bits, b["rotation"]))}
                    for i, bits in candidate["items"]
                    if contribution(a["graph"], rotated(bits, a["rotation"]))
                    != contribution(b["graph"], rotated(bits, b["rotation"]))
                )
                found = {"left": a["task_id"], "right": b["task_id"],
                         "whole_input": candidate["input"], "left_output": ai, "right_output": bi,
                         "distinguishing_item": distinguisher}
                break
            if found is None:
                raise ValueError(f"STOP_PREFREEZE_DESIGN_FAILURE: {family} {a['task_id']} {b['task_id']}")
            records.append(found)
        assert len(records) == 120
        out[family] = {"pair_count": 120, "distinguished": len(records), "records": records}
    return out


def main() -> None:
    ledger_path = ROOT / "research/protocols/phase3c_conf1_slots.json"
    audit_path = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE/graph_feasibility.json"
    if ledger_path.exists() or audit_path.exists():
        raise FileExistsError("CONF1 design outputs already exist")
    slots = build_slots()
    ledger = {
        "status": "PROSPECTIVE_DESIGN_LEDGER_BEFORE_DATA_OR_MODEL_USE",
        "design_baseline_commit": "ebe5b1d90b1d44dce8551e29de3ebb8a807cfaa3",
        "construction_seed": DESIGN_SEED,
        "predicate_definitions": {k: [{"name": n, "expression": e} for n, e in v] for k, v in FAMILIES.items()},
        "training_semantics": {"isolated": "per-item hitP+hitQ", "composition": "per-item hitP*hitQ"},
        "graphs": GRAPHS,
        "slots": slots,
        "candidate_policy": {
            "generator": "scripts/build_phase3c_conf1_data.py; deterministic from this ledger and construction_seed",
            "selection": "first candidate in deterministic order satisfying frozen semantic, case-discrimination, coverage and overlap constraints",
            "rejection_log": "record every attempted candidate ID, input/prompt/reference hash, and rejection reason before accepting successor",
            "no_model_feedback": True,
            "after_model_use": "no replacement or regeneration",
            "training_case_pool": "numeric 0..60; array signed values -16..16; case identity is task specification plus stdin plus expected output",
            "evaluation_case_pool": "numeric 0..100; array signed values -16..16; exclude exact accepted training case triples and consumed exact task/case triples; record raw-stdin overlap separately",
            "boundary_exception": "numeric n=0 may recur as a raw input because it uniquely exercises the empty loop under this schema; it is a new semantic case for a new task and its raw-input reuse is disclosed",
            "evaluation_selection": "fixed-seed candidate ordering; first five satisfying each task's positive, zero, overlap, boundary, multiplicity and pairwise-distinguishing matrix; reject task if impossible",
            "no_semantically_dead_code": True,
            "training_numeric_cases": "for each slot use random.Random(SHA256(construction_seed,slot_id,'train-numeric')) to sample five distinct n from 1..60 excluding 12,13,14; sort ascending",
            "training_array_cases": "for each slot use random.Random(SHA256(construction_seed,slot_id,'train-array')) to draw five unique 4-tuples from -16..16, rejection logged; exclude tuples selected for evaluation",
            "primary_numeric_cases": [0, 70, 12, 13, 14],
            "primary_array_cases": "prepend all-zero tuple; draw 4096 four-tuples using random.Random(construction_seed), each component -16..16; greedily choose four further tuples maximizing newly distinguished pairs among 120, ties by candidate index; require all 120 pairs, otherwise STOP",
            "secondary_cases": "reuse the five preselected domain inputs from primary but expected outputs derive from each fresh secondary specification",
            "training_prompt_rule": "same wrapper; only separate-count versus overlap-count treatment clause differs",
            "primary_prompt_rule": "fixed graph-specific text in prospective builder; no model-based edits",
        },
    }
    audit = {
        "status": "NON_MODEL_DESIGN_FEASIBILITY",
        "boolean_signatures": signatures(),
        "domain_witnesses": witnesses(slots["primary"]),
        "domain_block_interpretation": "two subskills realize four abstract graph families; eight blocks are not eight algebras",
        "candidate_inputs_are_feasibility_witnesses_not_final_hidden_cases": True,
    }
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ledger_sha256": hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
                      "numeric_pairs": audit["domain_witnesses"]["numeric_iteration"]["distinguished"],
                      "array_pairs": audit["domain_witnesses"]["array_reduction"]["distinguished"]}))


if __name__ == "__main__":
    main()
