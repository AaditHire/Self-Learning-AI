"""Deterministic, non-model CONF1 R1 specification enumeration (stdlib only).

Reads only predicate_definitions, graphs and slots from the ledger. No compiler,
repository implementation, candidate cases, consumed data or model is loaded.
The ledger's raw bytes are also hashed as explicitly required by the task.
"""

import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve()
LEDGER = ROOT / "research/protocols/phase3c_conf1_slots.json"
RESULTS = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE"
JSON_OUTPUT = RESULTS / "r1_specification_feasibility.json"
MD_OUTPUT = RESULTS / "r1_specification_feasibility.md"
ROLES = ("P", "Q", "R", "S")
GRAPHS = ("G1", "G2", "G3", "G3P", "G4")


def odd_index(n, i):
    return i % 2 == 1


def residue_two(n, i):
    return i % 3 == 2


def divisor_index(n, i):
    return n % i == 0


def first_half(n, i):
    return 2 * i <= n


def negative_value(x, i):
    return x < 0


def even_value(x, i):
    return x % 2 == 0


def large_magnitude(x, i):
    return x * x > 4


def value_exceeds_index(x, i):
    return x > i


PREDICATES = {
    "numeric_iteration": (
        ("odd_index", "i%2==1", odd_index),
        ("residue_two", "i%3==2", residue_two),
        ("divisor_index", "n%i==0", divisor_index),
        ("first_half", "2*i<=n", first_half),
    ),
    "array_reduction": (
        ("negative_value", "values[i]<0", negative_value),
        ("even_value", "values[i]%2==0", even_value),
        ("large_magnitude", "values[i]*values[i]>4", large_magnitude),
        ("value_exceeds_index", "values[i]>i", value_exceeds_index),
    ),
}


def contribution(graph, p, q, r, s):
    if graph == "G1":
        return int((p and q) or (p and r))
    if graph == "G2":
        return (p & q) + (q & r) + (r & s)
    if graph == "G3":
        return (p & q) + (p & r) + (p & s)
    if graph == "G3P":
        return (p & q) + (p & r)
    if graph == "G4":
        return ((p | q) & r) + (q & s)
    raise ValueError(f"Unknown graph: {graph}")


def terms(graph, p, q, r, s):
    if graph in ("G1", "G3P"):
        return {"P&Q": p & q, "P&R": p & r}
    if graph == "G2":
        return {"P&Q": p & q, "Q&R": q & r, "R&S": r & s}
    if graph == "G3":
        return {"P&Q": p & q, "P&R": p & r, "P&S": p & s}
    if graph == "G4":
        return {"(P|Q)&R": (p | q) & r, "Q&S": q & s}
    raise ValueError(f"Unknown graph: {graph}")


# Literal transcription of the proposed array table; None means unused "-".
R1_ARRAY_MAPS = {
    "G1": (
        ("negative_value", "even_value", "large_magnitude", None),
        ("even_value", "negative_value", "large_magnitude", None),
        ("large_magnitude", "even_value", "value_exceeds_index", None),
        ("value_exceeds_index", "even_value", "large_magnitude", None),
    ),
    "G2": (
        ("negative_value", "even_value", "large_magnitude", "value_exceeds_index"),
        ("negative_value", "even_value", "value_exceeds_index", "large_magnitude"),
        ("even_value", "negative_value", "large_magnitude", "value_exceeds_index"),
        ("large_magnitude", "negative_value", "even_value", "value_exceeds_index"),
    ),
    "G3P": (
        ("negative_value", "even_value", "large_magnitude", None),
        ("even_value", "large_magnitude", "value_exceeds_index", None),
        ("large_magnitude", "negative_value", "even_value", None),
        ("value_exceeds_index", "even_value", "large_magnitude", None),
    ),
    "G4": (
        ("negative_value", "even_value", "large_magnitude", "value_exceeds_index"),
        ("even_value", "large_magnitude", "negative_value", "value_exceeds_index"),
        ("large_magnitude", "even_value", "negative_value", "value_exceeds_index"),
        ("value_exceeds_index", "even_value", "large_magnitude", "negative_value"),
    ),
}


def feasible_patterns(domain):
    predicates = PREDICATES[domain]
    if domain == "numeric_iteration":
        inputs = ((n, i) for n in range(1, 401) for i in range(1, n + 1))
    elif domain == "array_reduction":
        inputs = ((x, i) for i in range(4) for x in range(-40, 41))
    else:
        raise ValueError(domain)
    return sorted({tuple(int(fn(a, i)) for _, _, fn in predicates) for a, i in inputs})


def comparison_functions(patterns):
    pair_functions = set()
    for a, b in itertools.combinations(range(4), 2):
        pair_functions.add(tuple(pattern[a] * pattern[b] for pattern in patterns))
        pair_functions.add(tuple(pattern[a] + pattern[b] for pattern in patterns))
    consumed_functions = set()
    for a, b, c, d in itertools.permutations(range(4)):
        consumed_functions.add(tuple(
            (pattern[a] & pattern[b]) + (pattern[c] & pattern[d])
            for pattern in patterns
        ))
        consumed_functions.add(tuple(
            int((pattern[a] & pattern[b]) or (pattern[c] & pattern[d]))
            for pattern in patterns
        ))
    return pair_functions, consumed_functions


def inspect_slot(slot, patterns, pair_functions, consumed_functions, require_qr=True):
    domain, graph = slot["family"], slot["graph"]
    names = [name for name, _, _ in PREDICATES[domain]]
    role_map = slot["role_predicates"]
    used_roles = ROLES[:3] if graph in ("G1", "G3P") else ROLES
    assert len({role_map[role] for role in used_roles}) == len(used_roles)
    role_indices = {role: names.index(role_map[role]) for role in used_roles}
    role_bits = [tuple(pattern[role_indices[role]] if role in used_roles else 0
                       for role in ROLES) for pattern in patterns]
    function = tuple(contribution(graph, *bits) for bits in role_bits)
    term_values = [terms(graph, *bits) for bits in role_bits]
    dead_terms = [term for term in term_values[0]
                  if not any(values[term] for values in term_values)]
    function_by_pattern = dict(zip(patterns, function))
    non_influential = []
    for role in used_roles:
        index = role_indices[role]
        influential = False
        for pattern in patterns:
            flipped = list(pattern)
            flipped[index] = 1 - flipped[index]
            flipped = tuple(flipped)
            if (flipped in function_by_pattern
                    and function_by_pattern[pattern] != function_by_pattern[flipped]):
                influential = True
                break
        if not influential:
            non_influential.append(role)
    qr_infeasible = (graph in ("G1", "G3P")
                     and not any(q and r for _, q, r, _ in role_bits))
    equals_pair = function in pair_functions
    equals_consumed = function in consumed_functions
    degenerate = bool(dead_terms or non_influential or equals_pair or equals_consumed
                      or (require_qr and qr_infeasible))
    return {
        **slot,
        "function": list(function),
        "dead_terms": dead_terms,
        "non_influential_roles": non_influential,
        "equals_pair_fn": equals_pair,
        "equals_consumed_fn": equals_consumed,
        "QR_infeasible": qr_infeasible,
        "QR_requirement_applied": require_qr and graph in ("G1", "G3P"),
        "degenerate": degenerate,
    }


def add_collisions(rows, split_graph=False):
    groups = defaultdict(list)
    by_id = {row["task_id"]: row for row in rows}
    for row in rows:
        groups[(row["family"], tuple(row["function"]))].append(row["task_id"])
    for row in rows:
        peers = sorted(task_id for task_id in groups[(row["family"], tuple(row["function"]))]
                       if task_id != row["task_id"])
        row["same_domain_function_collisions"] = peers
        if split_graph:
            row["within_graph_function_collisions"] = [
                task_id for task_id in peers if by_id[task_id]["graph"] == row["graph"]
            ]
            row["cross_graph_function_collisions"] = [
                task_id for task_id in peers if by_id[task_id]["graph"] != row["graph"]
            ]


def assignment_groups(domain, graph, patterns, pair_functions, consumed_functions):
    names = [name for name, _, _ in PREDICATES[domain]]
    groups = defaultdict(list)
    accepted_assignment_count = 0
    for assignment in itertools.permutations(names):
        row = inspect_slot(
            {"family": domain, "graph": graph, "role_predicates": dict(zip(ROLES, assignment))},
            patterns, pair_functions, consumed_functions, require_qr=False,
        )
        groups[tuple(row["function"])].append({
            key: row[key] for key in (
                "role_predicates", "dead_terms", "non_influential_roles",
                "equals_pair_fn", "equals_consumed_fn", "QR_infeasible", "degenerate",
            )
        })
        accepted_assignment_count += int(not row["degenerate"])
    grouped = [{"function": list(function), "assignments": assignments,
                "non_degenerate": any(not row["degenerate"] for row in assignments)}
               for function, assignments in sorted(groups.items())]
    return {
        "assignments_enumerated": 24,
        "QR_requirement_applied": False,
        "non_degenerate_assignment_count": accepted_assignment_count,
        "distinct_non_degenerate_function_count": sum(g["non_degenerate"] for g in grouped),
        "function_groups": grouped,
    }


def short_id(row):
    return row["graph"] + "R" + str(row["rotation"])


def validate_expected(report):
    frozen = report["frozen_primary_slots"]
    numeric = [row for row in frozen if row["family"] == "numeric_iteration"]
    array = [row for row in frozen if row["family"] == "array_reduction"]
    assert len(frozen) == 32 and len(numeric) == len(array) == 16
    checks = []

    def check(name, expected, actual):
        checks.append({"check": name, "expected": expected, "actual": actual,
                       "matched": expected == actual})

    check("feasible_pattern_counts", {"numeric_iteration": 16, "array_reduction": 11},
          {domain: data["feasible_pattern_count"] for domain, data in report["domains"].items()})
    check("frozen_numeric_degenerate_slots", [], [short_id(row) for row in numeric if row["degenerate"]])
    check("frozen_numeric_colliding_slots", [],
          [short_id(row) for row in numeric if row["same_domain_function_collisions"]])
    for flag, expected in (
        ("dead_terms", ["G1R3", "G2R1", "G2R2", "G2R3", "G3R0", "G3R3"]),
        ("equals_pair_fn", ["G1R3"]),
        ("equals_consumed_fn", ["G2R2", "G4R2"]),
        ("degenerate", ["G1R2", "G1R3", "G2R1", "G2R2", "G2R3", "G3R0", "G3R3", "G4R2"]),
    ):
        check("frozen_array_" + flag, expected, sorted(short_id(row) for row in array if row[flag]))
    for domain, expected in (
        ("array_reduction", {"G1": 8, "G2": 6, "G3": 2, "G3P": 8, "G4": 12}),
        ("numeric_iteration", {"G1": 12, "G2": 12, "G3": 4, "G3P": 12, "G4": 24}),
    ):
        check(domain + "_non_degenerate_function_counts_without_QR", expected,
              {graph: data["distinct_non_degenerate_function_count"]
               for graph, data in report["assignment_enumeration"][domain].items()})
    r1 = report["r1_array_primary_slots"]
    check("r1_array_slot_count", 16, len(r1))
    check("r1_array_degenerate_slots", [], [short_id(row) for row in r1 if row["degenerate"]])
    check("r1_array_colliding_slots", [],
          [short_id(row) for row in r1 if row["same_domain_function_collisions"]])
    check("domain_disjoint_array_training_slots", [f"CONF1-TR-AR-03-V{v}" for v in range(5)],
          report["domain_disjoint_array_training_slots"])
    report["expected_result_comparison"] = checks
    report["all_expected_results_matched"] = all(check["matched"] for check in checks)
    return checks


def markdown(report):
    lines = [
        "# CONF1 R1 non-model specification feasibility audit", "",
        "Specification enumeration only; no compiler, model, training, evaluation or candidate construction.", "",
        "Numeric enumeration: n=1..400, i=1..n. Array enumeration: i=0..3, x=-40..40.",
        "Patterns are sorted lexicographically in the predicate orders recorded below.",
        "Per-item functions are contribution vectors over those sorted feasible patterns.",
        "The slot audits apply QR_FEASIBLE to G1/G3P; the 24-assignment enumeration omits that requirement.", "",
        "## Input identities", "",
        "| Artifact | SHA-256 (raw bytes) |", "|---|---|",
    ]
    for artifact in report["input_artifacts"]:
        lines.append(f"| `{artifact['path']}` | `{artifact['sha256']}` |")
    lines += ["", "## Feasible patterns", ""]
    for domain, data in report["domains"].items():
        lines += [f"### {domain}", "", f"Predicate order: {', '.join(data['predicate_order'])}.",
                  f"Feasible patterns: **{data['feasible_pattern_count']}**.", "",
                  "```text", *(''.join(map(str, pattern)) for pattern in data["feasible_patterns"]),
                  "```", ""]
    lines += ["## Distinct non-degenerate functions over 24 assignments (without QR_FEASIBLE)", "",
              "| Domain | G1 | G2 | G3 | G3P | G4 |", "|---|---:|---:|---:|---:|---:|"]
    for domain, graphs in report["assignment_enumeration"].items():
        counts = [str(graphs[graph]["distinct_non_degenerate_function_count"]) for graph in GRAPHS]
        lines.append("| " + " | ".join([domain, *counts]) + " |")
    for title, rows in (
        ("Frozen primary slots", report["frozen_primary_slots"]),
        ("R1 proposed array primary slots", report["r1_array_primary_slots"]),
    ):
        lines += ["", "## " + title, "",
                  "| Slot | P,Q,R,S | Dead terms | Non-influential roles | Pair equality | Consumed equality | QR infeasible | Degenerate | Same-domain collisions |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for row in rows:
            role_map = ','.join(row["role_predicates"].get(role) or '-' for role in ROLES)
            values = [row["task_id"], role_map, ','.join(row["dead_terms"]) or '-',
                      ','.join(row["non_influential_roles"]) or '-',
                      str(row["equals_pair_fn"]), str(row["equals_consumed_fn"]),
                      str(row["QR_infeasible"]), str(row["degenerate"]),
                      ','.join(row["same_domain_function_collisions"]) or '-']
            lines.append("| " + " | ".join(value.replace('|', '\\|') for value in values) + " |")
        lines += ["", "### Per-item contribution vectors", "",
                  "| Slot | Function over sorted feasible patterns |", "|---|---|"]
        for row in rows:
            lines.append(f"| {row['task_id']} | `{json.dumps(row['function'])}` |")
    lines += ["", "### R1 array collision breakdown", "",
              "| Slot | Within graph | Cross graph |", "|---|---|---|"]
    for row in report["r1_array_primary_slots"]:
        lines.append(f"| {row['task_id']} | {','.join(row['within_graph_function_collisions']) or '-'} | "
                     f"{','.join(row['cross_graph_function_collisions']) or '-'} |")
    lines += ["", "## Array DOMAIN_DISJOINT_PAIR training slots", "",
              "Unordered pair: {negative_value, value_exceeds_index}.", "",
              *('- ' + slot for slot in report["domain_disjoint_array_training_slots"]), "",
              "## Expected versus actual", "",
              "| Check | Expected | Actual | Matched |", "|---|---|---|---|"]
    for check in report["expected_result_comparison"]:
        lines.append(f"| {check['check']} | `{json.dumps(check['expected'], sort_keys=True)}` | "
                     f"`{json.dumps(check['actual'], sort_keys=True)}` | {check['matched']} |")
    lines += ["", "All expected results matched: " + str(report["all_expected_results_matched"]) + ".", ""]
    return '\n'.join(lines)


def main():
    ledger_bytes = LEDGER.read_bytes()
    # Project only the three authorized fields; no other ledger fields are used.
    projected = {key: value for key, value in json.loads(ledger_bytes).items()
                 if key in ("predicate_definitions", "graphs", "slots")}
    for domain, predicates in PREDICATES.items():
        transcribed = [{"name": name, "expression": expression} for name, expression, _ in predicates]
        assert transcribed == projected["predicate_definitions"][domain], \
            f"Predicate transcription/order mismatch: {domain}"
    assert projected["graphs"] == {
        "G1": "(P&Q)|(P&R) counted once", "G2": "(P&Q)+(Q&R)+(R&S)",
        "G3": "(P&Q)+(P&R)+(P&S)", "G4": "((P|Q)&R)+(Q&S)",
    }, "Frozen graph transcription mismatch"
    domains = {}
    frozen_rows = []
    enumeration = {}
    r1_rows = []
    for domain, predicates in PREDICATES.items():
        patterns = feasible_patterns(domain)
        pair_functions, consumed_functions = comparison_functions(patterns)
        domains[domain] = {
            "predicate_order": [name for name, _, _ in predicates],
            "feasible_pattern_count": len(patterns), "feasible_patterns": patterns,
        }
        for slot in projected["slots"]["primary"]:
            if slot["family"] == domain:
                frozen_rows.append(inspect_slot(slot, patterns, pair_functions, consumed_functions))
        enumeration[domain] = {graph: assignment_groups(domain, graph, patterns,
                                                        pair_functions, consumed_functions)
                               for graph in GRAPHS}
        if domain == "array_reduction":
            for graph, maps in R1_ARRAY_MAPS.items():
                for rotation, assignment in enumerate(maps):
                    slot = {
                        "task_id": f"CONF1-NC-AR-{graph}-R{rotation}", "family": domain,
                        "group": "novel_composition", "graph": graph, "rotation": rotation,
                        "block_id": f"{domain}:{graph}", "role_predicates": dict(zip(ROLES, assignment)),
                        "composition_signature": f"{domain}:{graph}:R{rotation}",
                    }
                    r1_rows.append(inspect_slot(slot, patterns, pair_functions, consumed_functions))
    add_collisions(frozen_rows)
    add_collisions(r1_rows, split_graph=True)
    disjoint_slots = sorted(slot["slot_id"] for slot in projected["slots"]["training_paired_slots"]
                            if slot["family"] == "array_reduction"
                            and set(slot["unordered_pair"]) == {"negative_value", "value_exceeds_index"})
    report = {
        "status": "NON_MODEL_SPECIFICATION_ANALYSIS_PROPOSED_R1_NOT_FROZEN",
        "domains": domains, "frozen_primary_slots": frozen_rows,
        "assignment_enumeration": enumeration, "r1_array_primary_slots": r1_rows,
        "domain_disjoint_array_training_slots": disjoint_slots,
        "input_artifacts": [
            {"path": SCRIPT.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(SCRIPT.read_bytes()).hexdigest()},
            {"path": LEDGER.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(ledger_bytes).hexdigest()},
        ],
    }
    checks = validate_expected(report)
    RESULTS.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_bytes((json.dumps(report, indent=2, sort_keys=True) + '\n').encode('utf-8'))
    MD_OUTPUT.write_bytes(markdown(report).encode('utf-8'))
    for check in checks:
        print(json.dumps(check, sort_keys=True))
    if not report["all_expected_results_matched"]:
        raise SystemExit("STOP: expected-result mismatch; do not adjust the specification.")
    print("PASS: all specified feasibility expectations matched.")


if __name__ == "__main__":
    main()
