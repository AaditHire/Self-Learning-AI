"""Verified primary slots and the exact I1 canonical reference templates."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path


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
    "G3P": "Add two counts: P with Q, and P with R. An item may contribute more than once.",
}
_PREDICATE_FUNCTIONS = {
    "i%2==1": lambda n, i, values: i % 2 == 1,
    "i%3==2": lambda n, i, values: i % 3 == 2,
    "n%i==0": lambda n, i, values: n % i == 0,
    "2*i<=n": lambda n, i, values: 2 * i <= n,
    "values[i]<0": lambda n, i, values: values[i] < 0,
    "values[i]%2==0": lambda n, i, values: values[i] % 2 == 0,
    "values[i]*values[i]>4": lambda n, i, values: values[i] * values[i] > 4,
    "values[i]>i": lambda n, i, values: values[i] > i,
}


def load_primary_slots(root: str | Path) -> list[dict]:
    """Read verified authorities; retain numeric metadata and attach read-only inputs.

    ``used_roles`` and ``_predicate_expressions`` are implementation annotations;
    all original numeric slot fields remain unchanged. No cases are constructed.
    """
    root = Path(root)
    manifest_path = root / "research/protocols/phase3c_conf1_rebaseline_r1_freeze.json"
    try:
        manifest = json.loads(manifest_path.read_bytes())
        proposal_path = root / "research/protocols/phase3c_conf1_rebaseline_r1_proposed.md"
        proposal = proposal_path.read_bytes().replace(b"\r\n", b"\n")
        actual = hashlib.sha256(proposal).hexdigest()
        expected = manifest["frozen_amendment_sha256_lf_normalized"]
        if actual != expected:
            raise ValueError(f"R1 LF-normalized SHA-256 mismatch: expected {expected}, actual {actual}")
        ledger_path = root / "research/protocols/phase3c_conf1_slots.json"
        ledger_bytes = ledger_path.read_bytes()
        actual = hashlib.sha256(ledger_bytes).hexdigest()
        expected = manifest["frozen_slot_ledger_sha256_byte_exact"]
        if actual != expected:
            raise ValueError(f"Ledger byte-exact SHA-256 mismatch: expected {expected}, actual {actual}")
        text = proposal.decode("utf-8")
        section = text.split("## §7 Primary ledger delta\n", 1)[1].split("\n## §8 ", 1)[0]
        blocks = re.findall(r"^```json\s*\n(.*?)\n```\s*$", section, re.M | re.S)
        if len(blocks) != 1:
            raise ValueError(f"R1 section 7 fenced JSON block count: expected 1, actual {len(blocks)}")
        array = json.loads(blocks[0])
        ledger = json.loads(ledger_bytes)
        numeric = [s for s in ledger["slots"]["primary"] if s["family"] == "numeric_iteration"]
        definitions = ledger["predicate_definitions"]
        for slots, domain, code, graphs in (
            (array, "array_reduction", "AR", ("G1", "G2", "G3P", "G4")),
            (numeric, "numeric_iteration", "NU", ("G1", "G2", "G3", "G4")),
        ):
            if not isinstance(slots, list) or len(slots) != 16:
                raise ValueError(f"{domain} primary slot count: expected 16")
            ids = [s["task_id"] for s in slots]
            expected_ids = {f"CONF1-NC-{code}-{g}-R{r}" for g in graphs for r in range(4)}
            if len(set(ids)) != 16 or set(ids) != expected_ids:
                raise ValueError(f"{domain} primary ID mismatch: expected {sorted(expected_ids)}, actual {ids}")
            for slot in slots:
                graph, rotation = slot["graph"], slot["rotation"]
                if (slot["family"] != domain or graph not in graphs
                        or slot["task_id"] != f"CONF1-NC-{code}-{graph}-R{rotation}"):
                    raise ValueError(f"Primary slot metadata mismatch: {slot['task_id']}")
        result = []
        for original in [*numeric, *array]:
            slot = copy.deepcopy(original)
            domain = slot["family"]
            expressions = {p["name"]: p["expression"] for p in definitions[domain]}
            if len(expressions) != 4:
                raise ValueError(f"Predicate definition count mismatch: {domain}")
            used = tuple("PQR" if slot["graph"] in ("G1", "G3P") else "PQRS")
            for role in used:
                predicate = slot["role_predicates"][role]
                if predicate not in expressions:
                    raise ValueError(f"Unknown role predicate: {slot['task_id']} {role}={predicate}")
                if expressions[predicate] not in _PREDICATE_FUNCTIONS:
                    raise ValueError(f"Unsupported ledger predicate expression: {expressions[predicate]}")
            slot["used_roles"] = used
            slot["_predicate_expressions"] = expressions
            result.append(slot)
        return result
    except (OSError, KeyError, IndexError, TypeError, json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError(f"Primary authority verification failed: {exc}") from exc


def contribution(graph: str, p: int, q: int, r: int, s: int = 0) -> int:
    if graph == "G1":
        return int(p & (q | r))
    if graph == "G2":
        return (p & q) + (q & r) + (r & s)
    if graph == "G3":
        return (p & q) + (p & r) + (p & s)
    if graph == "G3P":
        return (p & q) + (p & r)
    if graph == "G4":
        return ((p | q) & r) + (q & s)
    raise ValueError(f"Unknown primary graph: {graph}")


def _predicate(slot: dict, role: str) -> str:
    return slot["_predicate_expressions"][slot["role_predicates"][role]]


def primary_expected(slot: dict, stdin: str) -> int:
    if slot["family"] == "numeric_iteration":
        n, values = int(stdin), None
        if n < 0:
            raise ValueError("Numeric input must be nonnegative")
        indices = range(1, n + 1)
    elif slot["family"] == "array_reduction":
        n, values = None, [int(x) for x in stdin.strip().split("|")]
        if len(values) != 4:
            raise ValueError("Array input must have exactly four signed integer fields")
        indices = range(4)
    else:
        raise ValueError(f"Unknown primary domain: {slot['family']}")
    total = 0
    for i in indices:
        bits = {role: int(_PREDICATE_FUNCTIONS[_predicate(slot, role)](n, i, values))
                for role in slot["used_roles"]}
        total += contribution(slot["graph"], *(bits.get(role, 0) for role in "PQRS"))
    return total


def prefix(family: str) -> str:
    if family == "numeric_iteration":
        return "NUMBER n.\nINPUT(n).\n"
    if family == "array_reduction":
        declarations = "\n".join(
            f"NUMBER {name} = strings.TO_NUMBER(parts[{index}])."
            for index, name in enumerate(("a", "b", "c", "d"))
        )
        return ('IMPORT strings.\nSENTENCE line.\nINPUT(line).\n'
                'SENTENCE[] parts = strings.SPLIT(line, "|").\n'
                + declarations + '\nNUMBER[] values=[a,b,c,d].\n')
    raise ValueError(f"Unknown primary domain: {family}")


def prompt_prefix(family: str) -> str:
    if family == "numeric_iteration":
        return "Read one nonnegative integer. "
    if family == "array_reduction":
        return "Read four signed integers separated by vertical bars. "
    raise ValueError(f"Unknown primary domain: {family}")


def primary_source(slot: dict) -> str:
    graph, family = slot["graph"], slot["family"]
    if graph == "G1":
        indicators = ("hitP", "hitOr")
        sets = (("P", "hitP"), ("Q", "hitOr"), ("R", "hitOr"))
        products = ("hitP*hitOr",)
    elif graph in ("G2", "G3", "G3P"):
        roles = "PQR" if graph == "G3P" else "PQRS"
        indicators = tuple("hit" + role for role in roles)
        sets = tuple((role, "hit" + role) for role in roles)
        products = {"G2": ("hitP*hitQ", "hitQ*hitR", "hitR*hitS"),
                    "G3": ("hitP*hitQ", "hitP*hitR", "hitP*hitS"),
                    "G3P": ("hitP*hitQ", "hitP*hitR")}[graph]
    elif graph == "G4":
        indicators = ("hitOr", "hitQ", "hitR", "hitS")
        sets = (("P", "hitOr"), ("Q", "hitOr"), ("Q", "hitQ"), ("R", "hitR"), ("S", "hitS"))
        products = ("hitOr*hitR", "hitQ*hitS")
    else:
        raise ValueError(f"Unknown primary graph: {graph}")
    declarations = "NUMBER total=0.\n" + ''.join(f"NUMBER {name}=0.\n" for name in indicators)
    tokens = [f"{name}=0." for name in indicators]
    tokens += [f"IF ({_predicate(slot, role)}) {{ {name}=1. }}" for role, name in sets]
    tokens += [f"total+=({product})." for product in products]
    bound = "NUMBER i=1 TILL i<=n" if family == "numeric_iteration" else "NUMBER i=0 TILL i<4"
    return prefix(family) + declarations + f"LOOP ({bound}, i++) {{ {' '.join(tokens)} }}\nDISPLAYNL(total)."


def primary_prompt(slot: dict) -> str:
    roles = slot["used_roles"]
    descriptions = "; ".join(f"{role}: {DESCRIPTIONS[slot['role_predicates'][role]]}" for role in roles)
    count = "three" if len(roles) == 3 else "four"
    return (prompt_prefix(slot["family"]) + f"Use these {count} tests ({descriptions}). "
            + GROUP_PROMPTS[slot["graph"]] + " Print the total.")
