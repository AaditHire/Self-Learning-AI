"""I1 specification tests; all random inputs use the explicit test seed."""

import copy
import hashlib
import itertools
import json
import random
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import build_phase3c_conf1_data as builder

from self_learning_ai.conf1_r1.interp import interpret, split_statements
from self_learning_ai.conf1_r1.primary import (
    DESCRIPTIONS, GROUP_PROMPTS, contribution, load_primary_slots,
    prefix, primary_expected, primary_prompt, primary_source, prompt_prefix,
)

SLOTS = load_primary_slots(ROOT)


@pytest.fixture
def authority_root():
    # Isolated OS temporary copies; no pytest --basetemp or repository fixtures.
    with tempfile.TemporaryDirectory(prefix="conf1-r1-i1-authority-") as directory:
        yield Path(directory)


def authority_copy(tmp_path):
    directory = tmp_path / "research/protocols"
    directory.mkdir(parents=True)
    for filename in ("phase3c_conf1_rebaseline_r1_proposed.md",
                     "phase3c_conf1_rebaseline_r1_freeze.json", "phase3c_conf1_slots.json"):
        (directory / filename).write_bytes((ROOT / "research/protocols" / filename).read_bytes())
    return directory


def test_verified_slots_and_preserved_numeric_fields():
    assert len(SLOTS) == 32
    array = [s for s in SLOTS if s["family"] == "array_reduction"]
    assert {s["task_id"] for s in array} == {
        f"CONF1-NC-AR-{graph}-R{rotation}"
        for graph in ("G1", "G2", "G3P", "G4") for rotation in range(4)
    }
    ledger = json.loads((ROOT / "research/protocols/phase3c_conf1_slots.json").read_bytes())
    numeric = [s for s in ledger["slots"]["primary"] if s["family"] == "numeric_iteration"]
    loaded_numeric = [s for s in SLOTS if s["family"] == "numeric_iteration"]
    assert [{k: v for k, v in s.items() if k not in ("used_roles", "_predicate_expressions")}
            for s in loaded_numeric] == numeric
    for slot in SLOTS:
        assert slot["used_roles"] == tuple("PQR" if slot["graph"] in ("G1", "G3P") else "PQRS")


@pytest.mark.parametrize("filename,reason", [
    ("phase3c_conf1_rebaseline_r1_proposed.md", "R1 LF-normalized SHA-256 mismatch"),
    ("phase3c_conf1_slots.json", "Ledger byte-exact SHA-256 mismatch"),
])
def test_hash_verification_rejects_tampered_copy(authority_root, filename, reason):
    directory = authority_copy(authority_root)
    path = directory / filename
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match=reason):
        load_primary_slots(authority_root)


def test_proposal_hash_is_lf_normalized(authority_root):
    directory = authority_copy(authority_root)
    path = directory / "phase3c_conf1_rebaseline_r1_proposed.md"
    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert len(load_primary_slots(authority_root)) == 32


def test_slot_id_verification_after_hash_check(authority_root):
    directory = authority_copy(authority_root)
    path = directory / "phase3c_conf1_rebaseline_r1_proposed.md"
    content = path.read_bytes().replace(b"CONF1-NC-AR-G1-R0", b"CONF1-NC-AR-G1-R9")
    path.write_bytes(content)
    manifest_path = directory / "phase3c_conf1_rebaseline_r1_freeze.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["frozen_amendment_sha256_lf_normalized"] = hashlib.sha256(content.replace(b"\r\n", b"\n")).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="array_reduction primary ID mismatch"):
        load_primary_slots(authority_root)


def test_boolean_contributions_exhaustively():
    for p, q, r, s in itertools.product((0, 1), repeat=4):
        assert contribution("G1", p, q, r, s) == int(bool(p and (q or r)))
        assert contribution("G2", p, q, r, s) == sum((p and q, q and r, r and s))
        assert contribution("G3", p, q, r, s) == sum((p and q, p and r, p and s))
        assert contribution("G3P", p, q, r, s) == sum((p and q, p and r))
        assert contribution("G4", p, q, r, s) == sum(((p or q) and r, q and s))
    with pytest.raises(ValueError, match="Unknown primary graph"):
        contribution("unknown", 0, 0, 0, 0)


def test_expected_uses_explicit_roles_and_ignores_rotation_metadata():
    for slot in SLOTS:
        changed = copy.deepcopy(slot)
        changed["rotation"] = 999
        stdin = "19" if slot["family"] == "numeric_iteration" else "3|-4|7|-1"
        assert primary_expected(changed, stdin) == primary_expected(slot, stdin)
        assert primary_source(changed) == primary_source(slot)


@pytest.mark.parametrize("slot", SLOTS, ids=lambda s: s["task_id"])
def test_expected_matches_interpreter_on_twelve_seeded_inputs(slot):
    rng = random.Random(12345)  # TEST seed, unrelated to construction or model seeds.
    for _ in range(12):
        stdin = (str(rng.randint(0, 60)) if slot["family"] == "numeric_iteration"
                 else "|".join(str(rng.randint(-16, 16)) for _ in range(4)))
        assert interpret(primary_source(slot), stdin) == ("ok", str(float(primary_expected(slot, stdin))))


def test_shared_text_equals_unchanged_builder():
    assert DESCRIPTIONS == builder.DESCRIPTIONS
    assert {key: GROUP_PROMPTS[key] for key in builder.GROUP_PROMPTS} == builder.GROUP_PROMPTS
    assert GROUP_PROMPTS["G3P"] == "Add two counts: P with Q, and P with R. An item may contribute more than once."
    for family in ("numeric_iteration", "array_reduction"):
        assert prefix(family) == builder.prefix(family)
        assert prompt_prefix(family) == builder.prompt_prefix(family)
    for slot in SLOTS:
        used = slot["used_roles"]
        descriptions = "; ".join(f"{role}: {builder.DESCRIPTIONS[slot['role_predicates'][role]]}" for role in used)
        wrapper = (builder.prompt_prefix(slot["family"]) +
                   f"Use these {'three' if len(used) == 3 else 'four'} tests ({descriptions}). ")
        assert primary_prompt(slot) == wrapper + GROUP_PROMPTS[slot["graph"]] + " Print the total."
        if len(used) == 3:
            assert "S: " not in primary_prompt(slot)


@pytest.mark.parametrize("slot", SLOTS, ids=lambda s: s["task_id"])
def test_every_reference_satisfies_rcf_and_exact_accumulations(slot):
    source = primary_source(slot)
    assert not any(token in source for token in ("&&", "||", "!"))
    units = split_statements(source)
    loops = [unit for unit in units if unit.kind == "LOOP"]
    assert len(loops) == 1
    body = loops[0].children
    indicators = re.findall(r"^NUMBER (hit[A-Za-z]+)=0\.$", source, re.M)
    expected_indicators = {"G1": ["hitP", "hitOr"], "G2": ["hitP", "hitQ", "hitR", "hitS"],
                           "G3": ["hitP", "hitQ", "hitR", "hitS"], "G3P": ["hitP", "hitQ", "hitR"],
                           "G4": ["hitOr", "hitQ", "hitR", "hitS"]}[slot["graph"]]
    assert indicators == expected_indicators
    assert [unit.text for unit in body[:len(indicators)]] == [f"{name}=0." for name in indicators]
    accumulations = [unit.text for unit in body if unit.text.startswith("total+=")]
    expected_accumulations = {
        "G1": ["hitP*hitOr"], "G2": ["hitP*hitQ", "hitQ*hitR", "hitR*hitS"],
        "G3": ["hitP*hitQ", "hitP*hitR", "hitP*hitS"], "G3P": ["hitP*hitQ", "hitP*hitR"],
        "G4": ["hitOr*hitR", "hitQ*hitS"],
    }[slot["graph"]]
    assert accumulations == [f"total+=({product})." for product in expected_accumulations]
    reads = set()
    for statement in accumulations:
        term = statement[len("total+="):-1]
        assert term.startswith("(") and term.endswith(")")
        term = term[1:-1]  # Strip exactly the single required pair.
        factors = term.split("*")
        assert len(factors) in (1, 2) and all(name in indicators for name in factors)
        reads.update(factors)
    writes = {unit.children[0].text.split("=")[0] for unit in body if unit.kind == "IF"}
    assert writes == reads == set(indicators)
    for unit in body:
        if unit.kind == "IF":
            assert len(unit.children) == 1 and unit.children[0].kind == "simple"
            assert re.fullmatch(r"hit[A-Za-z]+=1\.", unit.children[0].text)
    assert source.endswith("DISPLAYNL(total).")
