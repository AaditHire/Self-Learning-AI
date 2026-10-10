"""P1R exact enumeration, signature exclusions and sealed split."""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from collections import Counter
from pathlib import Path

from self_learning_ai.conf1_r1.training import _builder
from self_learning_ai.conf1_r1.primary import (
    load_primary_slots, primary_expected, primary_prompt, primary_source,
)
from self_learning_ai.explore.scoring import score_program

ROOT = Path(__file__).resolve().parents[3]
FAMILIES = ("numeric_iteration", "array_reduction")
CATEGORIES = ("atom_single", "atom_isolated", "pair_and", "graph")
GRAPHS = ("G1", "G2", "G3P", "G4")
OUT = ROOT / "research/explore/b0"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def load_dev_pool(path=None):
    path = Path(path) if path is not None else OUT / "dev_pool.json"
    path = path.resolve()
    explore = (ROOT / "research/explore").resolve()
    if path.is_relative_to(explore) and "sealed" in (p.lower() for p in path.relative_to(explore).parts):
        raise ValueError("sealed pool access forbidden")
    return json.loads(path.read_bytes())


def probes():
    rng = random.Random(20291011)
    return {FAMILIES[0]: [str(n) for n in range(1, 65)],
            FAMILIES[1]: ["|".join(str(rng.randint(-9, 9)) for _ in range(4)) for _ in range(64)]}


def expected(category, slot, stdin):
    builder = _builder()
    if category == "graph":
        return primary_expected(slot, stdin)
    if category == "atom_single":
        return builder.sanity_expected(slot, stdin)
    return builder.train_expected("isolated" if category == "atom_isolated" else "composition", slot, stdin)


def signature(category, slot, inputs):
    return tuple(expected(category, slot, x) for x in inputs[slot["family"]])


def term_dead(slot, inputs, roles):
    builder = _builder()
    names = [slot["role_predicates"][r] for r in roles] if "role_predicates" in slot else [slot["P"], slot["Q"]]
    for stdin in inputs[slot["family"]]:
        for _, bits in builder.parse_input(slot["family"], stdin):
            if all(builder.primitive_truth(slot["family"], name, bits) for name in names):
                return False
    return True


def degenerate(slot, inputs, sig):
    terms = {"G1": ("PQR",), "G2": ("PQ", "QR", "RS"),
             "G3P": ("PQ", "PR"), "G4": ("PQR", "QS")}[slot["graph"]]
    # PQR denotes the OR-containing product, not a three-way conjunction.
    for term in terms:
        if term == "PQR":
            pairs = ("PQ", "PR") if slot["graph"] == "G1" else ("PR", "QR")
            dead = all(term_dead(slot, inputs, pair) for pair in pairs)
        else:
            dead = term_dead(slot, inputs, term)
        if dead:
            return True
    return len(set(sig)) == 1


def enumerate_candidates():
    builder, inputs = _builder(), probes()
    ledger = builder.LEDGER
    primary = load_primary_slots(ROOT)
    primary_sigs = {family: {signature("graph", s, inputs) for s in primary if s["family"] == family}
                    for family in FAMILIES}
    training = {(s["family"], frozenset((s["P"], s["Q"])), s["offset"])
                for s in ledger["slots"]["training_paired_slots"]}
    sanity = {(s["family"], s["primitive"], s["offset"]) for s in ledger["slots"]["primitive_sanity"]}
    construction = random.Random(20291010)
    shuffle = random.Random(20291012)
    excluded = {c: Counter(dict(CONF1_overlap=0, dead=0, degenerate=0, duplicate=0)) for c in CATEGORIES}
    survivors = {c: [] for c in CATEGORIES}
    for category in CATEGORIES:
        candidates = []
        for family in FAMILIES:
            names = list(builder.PREDICATES[family])
            if category == "graph":
                for graph in GRAPHS:
                    used = tuple("PQR" if graph in ("G1", "G3P") else "PQRS")
                    for assignment in itertools.permutations(names, len(used)):
                        candidates.append(dict(family=family, graph=graph, used_roles=used,
                                               role_predicates=dict(zip(used, assignment)),
                                               _predicate_expressions=builder.PREDICATES[family]))
            elif category == "atom_single":
                candidates.extend(dict(family=family, primitive=name, offset=k, group="primitive_sanity")
                                  for name in names for k in range(20))
            else:
                for pair in itertools.combinations(names, 2):
                    for k in range(20):
                        ordered = list(pair)
                        construction.shuffle(ordered)
                        candidates.append(dict(family=family, P=ordered[0], Q=ordered[1], offset=k,
                                               reverse=bool(construction.randrange(2))))
        shuffle.shuffle(candidates)
        seen = set()
        for slot in candidates:
            sig = signature(category, slot, inputs)
            family = slot["family"]
            overlap = (sig in primary_sigs[family] if category == "graph" else
                       (family, slot["primitive"], slot["offset"]) in sanity if category == "atom_single" else
                       (family, frozenset((slot["P"], slot["Q"])), slot["offset"]) in training)
            reason = ("CONF1_overlap" if overlap else
                      "dead" if category == "pair_and" and term_dead(slot, inputs, "PQ") else
                      "degenerate" if category == "graph" and degenerate(slot, inputs, sig) else
                      "duplicate" if sig in seen else None)
            if reason:
                excluded[category][reason] += 1
                continue
            seen.add(sig)
            survivors[category].append(dict(category=category, slot=slot, signature=list(sig)))
    return survivors, {c: dict(v) for c, v in excluded.items()}, primary_sigs


def split_candidates(survivors):
    rng = random.Random(20291012)
    dev, sealed, strata = [], [], {}
    for category in CATEGORIES:
        for family in FAMILIES:
            graphs = GRAPHS if category == "graph" else (None,)
            for graph in graphs:
                rows = [r for r in survivors[category] if r["slot"]["family"] == family
                        and (graph is None or r["slot"]["graph"] == graph)]
                rng.shuffle(rows)
                if graph is None:
                    nd, ns = (48, 16) if category == "pair_and" else (24, 8)
                    if len(rows) < nd + ns:
                        raise ValueError(f"STOP insufficient survivors: {category}/{family}: {len(rows)} < {nd+ns}")
                else:
                    ns = len(rows) // 3
                    nd = len(rows) - ns
                    strata[f"{family}/{graph}"] = dict(survivors=len(rows), dev=nd, sealed=ns)
                sealed.extend(rows[:ns])
                dev.extend(rows[ns:ns + nd])
    return dev, sealed, strata


def materialize(rows, rng):
    builder = _builder()
    for index, row in enumerate(rows):
        category, slot = row["category"], row["slot"]
        family = slot["family"]
        row["task_id"] = f"EXPL-B0-{category.upper()}-{family.upper()}-{index:03d}"
        row["family"] = family
        if category == "graph":
            row.update(prompt=primary_prompt(slot), reference_source=primary_source(slot), graph=slot["graph"])
        elif category == "atom_single":
            row.update(prompt=builder.task_prompt(slot), reference_source=builder.sanity_source(slot))
        else:
            clause = (f"independently tally {builder.DESCRIPTIONS[slot['P']]} and {builder.DESCRIPTIONS[slot['Q']]}"
                      if category == "atom_isolated" else
                      f"tally items satisfying both {builder.DESCRIPTIONS[slot['P']]} and {builder.DESCRIPTIONS[slot['Q']]}")
            row.update(prompt=builder.prompt_prefix(family) + f"For each item, {clause}; begin at {slot['offset']} and print the total.",
                       reference_source=builder.train_source("isolated" if category == "atom_isolated" else "composition", slot))
        for _ in range(50):
            inputs = []
            while len(inputs) < 5:
                candidate = (str(rng.randint(6, 40)) if family == FAMILIES[0] else
                             "|".join(str(rng.randint(-9, 9)) for _ in range(4)))
                if candidate not in inputs:
                    inputs.append(candidate)
            values = [expected(category, slot, x) for x in inputs]
            if len(set(values)) > 1:
                break
        else:
            raise ValueError(f"STOP constant case outputs after 50 attempts: {row['task_id']}")
        row["cases"] = [builder.case(j + 1, x, v) for j, (x, v) in enumerate(zip(inputs, values))]
        score = score_program(row["reference_source"], row["cases"])
        if not score["all_pass"]:
            raise ValueError(f"STOP reference failure: {row['task_id']}: {score}")
        print(f"reference PASS {row['task_id']}", flush=True)


def assign_model_ids(rows):
    shuffled = list(rows)
    random.Random(20291013).shuffle(shuffled)
    for k, row in enumerate(shuffled):
        row["model_task_id"] = f"EXPL-B0-{k:04d}"


def build_pools():
    if any((OUT / p).exists() for p in ("dev_pool.json", "sealed/sealed_pool.json", "pools_manifest.json")):
        raise FileExistsError("pool outputs already exist")
    survivors, excluded, primary_sigs = enumerate_candidates()
    dev, sealed, strata = split_candidates(survivors)
    actual_counts = {c: dict(Counter(r["slot"]["family"] for r in rows)) for c, rows in survivors.items()}
    required_counts = {"atom_single": dict(zip(FAMILIES, (72, 72))),
                       "atom_isolated": dict(zip(FAMILIES, (90, 90))),
                       "pair_and": dict(zip(FAMILIES, (90, 75))),
                       "graph": dict(zip(FAMILIES, (48, 18)))}
    required_strata = {
        f"{family}/{graph}": dict(survivors=n, dev=n - n // 3, sealed=n // 3)
        for family, counts in zip(FAMILIES, ((8, 8, 12, 20), (7, 1, 2, 8)))
        for graph, n in zip(GRAPHS, counts)
    }
    if actual_counts != required_counts or strata != required_strata:
        raise ValueError(f"STOP P1R2 count mismatch: {actual_counts}, {strata}")
    print(json.dumps(dict(survivors={c: dict(Counter(r['slot']['family'] for r in rows)) for c, rows in survivors.items()},
                          excluded=excluded, graph_strata=strata)), flush=True)
    rng = random.Random(20291010)
    assign_model_ids(dev + sealed)
    if len({r["model_task_id"] for r in dev + sealed}) != len(dev) + len(sealed):
        raise ValueError("STOP duplicate model task IDs")
    materialize(dev + sealed, rng)
    for category in CATEGORIES:
        a = {tuple(r["signature"]) for r in dev if r["category"] == category}
        b = {tuple(r["signature"]) for r in sealed if r["category"] == category}
        if a & b:
            raise ValueError("STOP cross-pool signature overlap")
    write_json(OUT / "dev_pool.json", dev)
    write_json(OUT / "sealed/sealed_pool.json", sealed)
    manifest = dict(label="EXPLORATORY", construction_seed=20291010, probe_seed=20291011, shuffle_seed=20291012,
                    model_id_seed=20291013, model_ids_unique=True, survivor_counts=actual_counts,
                    counts={name: {c: dict(Counter(r["family"] for r in rows if r["category"] == c)) for c in CATEGORIES}
                            for name, rows in (("dev", dev), ("sealed", sealed))},
                    sha256={p: hashlib.sha256((OUT / p).read_bytes()).hexdigest()
                            for p in ("dev_pool.json", "sealed/sealed_pool.json")},
                    dedup=dict(excluded=excluded, cross_pool_overlap_by_category={c: 0 for c in CATEGORIES},
                               graph_primary_overlap=0), graph_strata=strata,
                    references_validated=len(dev) + len(sealed))
    write_json(OUT / "pools_manifest.json", manifest)
    return manifest
