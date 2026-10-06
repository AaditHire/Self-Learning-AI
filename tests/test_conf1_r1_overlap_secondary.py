"""I4a mechanical consumed comparisons and synthetic compiler validation only."""

import builtins
import copy
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from self_learning_ai.conf1_r1 import overlap, secondary, training
from self_learning_ai.conf1_r1.gates_primary import CompilerRunner, GateStop
from self_learning_ai.conf1_r1.primary import load_primary_slots, primary_expected, primary_prompt, primary_source

SYN_ARRAY_EVAL = ["0|0|0|0", "-14|16|-2|-15", "12|2|-1|5", "-16|-10|7|2", "-14|6|-6|4"]
DOMAIN_INPUTS = {"numeric_iteration": ["0", "5", "9", "31", "64"], "array_reduction": SYN_ARRAY_EVAL}
EXPECTED_DIRECTORIES = {
    "benchmark/phase1r": 3, "benchmark/phase1s": 3, "benchmark/phase1t": 3,
    "benchmark/phase2a": 4, "benchmark/phase2b": 4,
    "benchmark/phase3a": 6, "benchmark/phase3b": 6, "benchmark/phase3c": 6,
    "benchmark/phase3c_dev1": 3, "benchmark/phase3c_dev2": 3,
    "benchmark/phase3c_dev2r": 3, "benchmark/phase3c_dev2r_v2": 3,
    "data/phase2a": 2, "data/phase2b": 2, "data/phase3a": 4, "data/phase3b": 4,
    "data/phase3c": 4, "data/phase3c_dev1": 6, "data/phase3c_dev2": 6,
}


def emit(capsys, name, report):
    with capsys.disabled():
        print(name + ": " + json.dumps(report, sort_keys=True), flush=True)


@pytest.fixture(scope="module")
def inventory():
    opened = []
    original_path_open, original_open = Path.open, builtins.open

    def guard(path):
        resolved = Path(path).resolve()
        if resolved.is_relative_to(ROOT / "benchmark") or resolved.is_relative_to(ROOT / "data"):
            relative = resolved.relative_to(ROOT).as_posix()
            assert relative not in overlap.EXCLUDED, "excluded holdout path must never be opened"
            assert relative.rsplit("/", 1)[0] in EXPECTED_DIRECTORIES
            opened.append(relative)

    def path_open(path, *args, **kwargs):
        guard(path)
        return original_path_open(path, *args, **kwargs)

    def builtin_open(path, *args, **kwargs):
        if not isinstance(path, int):
            guard(path)
        return original_open(path, *args, **kwargs)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(Path, "open", path_open)
        patch.setattr(builtins, "open", builtin_open)
        result = overlap.consumed_inventory()
    result["guarded_opened_paths"] = sorted(set(opened))
    return result


@pytest.fixture(scope="module")
def definitions():
    primary = load_primary_slots(ROOT)
    tasks = secondary.sanity_tasks() + secondary.structural_tasks()
    records = training.training_records()
    return primary, tasks, records


@pytest.fixture(scope="module")
def noncase_items(definitions):
    primary, tasks, records = definitions
    return ([{"id": slot["task_id"], "role": "primary", "prompt": primary_prompt(slot),
              "source": primary_source(slot)} for slot in primary]
            + [{"id": task["task_id"], "role": "secondary", "group": task["group"],
                "prompt": task["prompt"], "source": task["source"]} for task in tasks]
            + [{"id": record["record_id"], "slot_id": record["slot_id"], "role": "training",
                "prompt": record["prompt"], "model_user_message": record["model_user_message"],
                "source": record["target"]} for record in records])


def test_t1_inventory(inventory, capsys):
    assert inventory["directories"] == EXPECTED_DIRECTORIES
    assert inventory["total_files"] == 75
    assert inventory["records_by_kind"] == {"cases": 7734, "prompts": 1836, "references": 964, "targets": 1000}
    assert set(inventory["guarded_opened_paths"]) == {row["path"] for row in inventory["files"]}
    assert set(inventory["guarded_opened_paths"]).isdisjoint(overlap.EXCLUDED)
    assert all(len(row["sha256"]) == 64 and len(row["git_blob"]) == 40 for row in inventory["files"])
    assert inventory["phase1_baseline_outside_corpus"] is True
    emit(capsys, "I4a T1", {k: v for k, v in inventory.items() if k not in ("files", "guarded_opened_paths")})


def test_t2_actual_noncase_overlap(noncase_items, inventory, capsys):
    assert len(noncase_items) == 184
    try:
        result = overlap.p7_overlap(noncase_items, inventory)
    except GateStop as exc:
        emit(capsys, "I4a T2 STOP FULL REPORT", exc.report)
        pytest.exit("STOP: actual primary/training P7 overlap", returncode=2)
    assert result["status"] == "PASS"
    assert result["blocking"] == []
    assert result["sanity_count"] == 16 and not result["SANITY_NOT_EVALUABLE"]
    started = time.perf_counter()
    nearest = overlap.nearest_descriptive(noncase_items, inventory)
    summary = {name: {k: v for k, v in row.items() if k != "rows"} for name, row in nearest.items()}
    for name, row in nearest.items():
        summary[name]["closest"] = max(row["rows"], key=lambda r: r["similarity"])
    emit(capsys, "I4a T2", {"blocking": result["blocking"], "primary": 32, "secondary": 32,
                            "training": 120, "prompt_texts_including_C9": 304, "sources": 184,
                            "nearest_descriptive": summary, "nearest_wall_seconds": time.perf_counter() - started})


@pytest.mark.parametrize("rule", ["a", "b", "primary_training_b"])
def test_t3_known_bad(rule, inventory, noncase_items, capsys):
    primary = copy.deepcopy(noncase_items[0])
    if rule == "a":
        primary["prompt"] = overlap._consumed(inventory, ("prompts",))[0]["value"]
        items = [primary]
    elif rule == "b":
        primary["source"] = overlap._consumed(inventory, ("references",))[0]["value"]
        items = [primary]
    else:
        target = copy.deepcopy(next(item for item in noncase_items if item["role"] == "training"))
        primary["source"] = target["source"]
        items = [primary, target]
    with pytest.raises(GateStop) as stopped:
        overlap.p7_overlap(items, inventory)
    result = stopped.value.report
    assert result["status"] == "STOP" and primary["id"] in result["fatal_items"]
    assert any(row["rule"] == ("a" if rule == "a" else "b") for row in result["blocking"])
    emit(capsys, "I4a T3 " + rule, {"status": "PASS", "detected": result["blocking"]})


def test_t3_case_identity_requires_specification_match(noncase_items, inventory):
    primary = copy.deepcopy(noncase_items[0])
    target = copy.deepcopy(next(item for item in noncase_items if item["role"] == "training"))
    primary["cases"] = target["cases"] = [{"stdin": "5", "expected_stdout": "1"}]
    result = overlap.p7_overlap([primary, target], inventory)
    assert result["blocking"] == []
    assert result["descriptive"]["conf1_training"]["raw_matching_cases"] == 1
    assert result["descriptive"]["conf1_training"]["pair_matching_cases"] == 1
    primary["source"] = target["source"]
    with pytest.raises(GateStop) as stopped:
        overlap.p7_overlap([primary, target], inventory)
    assert any(row["rule"] == "c" and row["specification_rule"] == "b" for row in stopped.value.report["blocking"])


def test_t3_secondary_drop_preserves_primary(noncase_items, inventory):
    primary = copy.deepcopy(noncase_items[0])
    sanity = copy.deepcopy(noncase_items[32])
    sanity["prompt"] = primary["prompt"]
    result = overlap.p7_overlap([primary, sanity], inventory)
    assert result["status"] == "PASS" and result["fatal_items"] == []
    assert result["secondary_drops"] == [{"id": sanity["id"], "reason": "P7_FAIL_CANDIDATES_EXHAUSTED"}]
    assert result["SANITY_NOT_EVALUABLE"]
    target = copy.deepcopy(next(item for item in noncase_items if item["role"] == "training"))
    sanity["prompt"] = "synthetic different secondary prompt"
    sanity["source"] = target["source"]
    result = overlap.p7_overlap([target, sanity], inventory)
    assert result["status"] == "PASS" and result["fatal_items"] == []
    assert len(result["secondary_drops"]) == 1


def test_t4_synthetic_case_overlap(definitions, noncase_items, inventory, capsys):
    primary, tasks, records = definitions
    ledger, _, _ = training._authorities()
    selections = {slot["slot_id"]: training.select_training_cases(slot, 900001, SYN_ARRAY_EVAL)
                  for slot in ledger["slots"]["training_paired_slots"]}
    assert len(selections) == 60 and all(s["status"] == "PASS" for s in selections.values())
    items = copy.deepcopy(noncase_items)
    by_id = {item["id"]: item for item in items}
    for slot in primary:
        by_id[slot["task_id"]]["cases"] = [{"stdin": stdin, "expected_stdout": str(primary_expected(slot, stdin))}
                                          for stdin in DOMAIN_INPUTS[slot["family"]]]
    for task in tasks:
        by_id[task["task_id"]]["cases"] = secondary.secondary_cases(task, DOMAIN_INPUTS)
    builder = training._builder()
    for record in records:
        selection = selections[record["slot_id"]]
        by_id[record["record_id"]]["cases"] = [
            {"stdin": stdin, "expected_stdout": str(builder.train_expected(record["condition"], selection["slot"], stdin))}
            for stdin in selection["inputs"]]
    result = overlap.p7_overlap(items, inventory)
    assert result["status"] == "PASS" and result["blocking"] == []
    summary = {name: {key: value for key, value in row.items() if key != "by_task"}
               for name, row in result["descriptive"].items()}
    # Also distinguish the primary and secondary descriptive counts explicitly.
    for role in ("primary", "secondary"):
        subset = [item for item in items if item["role"] in (role, "training")]
        subreport = overlap.p7_overlap(subset, inventory)["descriptive"]
        summary[role] = {name: {key: value for key, value in row.items() if key != "by_task"}
                         for name, row in subreport.items()}
    emit(capsys, "I4a T4", {"status": result["status"], "blocking": result["blocking"], "synthetic_seed": 900001,
                            "comparison": "literal stdin and expected_stdout strings; no whitespace normalization",
                            "consumed_stdin_fields_with_trailing_newline": sum(row["value"].endswith("\n")
                                                                              for row in overlap._consumed(inventory, ("cases",))),
                            "training_cases": 600, "descriptive": summary})


def test_t5_secondary_e1_compiler(definitions, capsys):
    _, tasks, _ = definitions
    started = time.perf_counter()
    result = secondary.secondary_e1(tasks, DOMAIN_INPUTS, runner=CompilerRunner(ROOT))
    assert len(result["kept"]) + len(result["dropped"]) == 32
    assert result["sanity_count"] == sum(task["group"] == "primitive_sanity" for task in result["kept"])
    assert result["SANITY_NOT_EVALUABLE"] == (result["sanity_count"] < 12)
    rows = [{"task_id": row["id"], "decision": "kept" if row["status"] == "PASS" else "dropped",
             "reason": None if row["status"] == "PASS" else "E1_FAIL_CANDIDATES_EXHAUSTED",
             "failures": row["failures"]} for row in result["items"]]
    emit(capsys, "I4a T5", {"kept": len(result["kept"]), "dropped": len(result["dropped"]),
                            "sanity_count": result["sanity_count"], "SANITY_NOT_EVALUABLE": result["SANITY_NOT_EVALUABLE"],
                            "compiler_runs": result["runner_calls"], "tasks": rows,
                            "wall_seconds": time.perf_counter() - started})


def test_t6_historical_condition_ids(inventory, capsys):
    # Descriptive only: record these findings without a pass/fail assertion on them.
    files = []
    for file in inventory["files"]:
        if file["path"].startswith("data/phase3c_dev2/") and file["path"].endswith("_examples.json"):
            ids = [record["task_id"] for record in file["records"]["prompts"]]
            files.append({"path": file["path"], "example_ids_contain_condition_labels":
                          any(label in identifier.casefold() for identifier in ids for label in ("isolated", "composition")),
                          "labelled_id_count": sum(any(label in identifier.casefold() for label in ("isolated", "composition"))
                                                   for identifier in ids), "example_count": len(ids), "quoted_ids": ids[:2]})
    dev2 = (ROOT / "scripts/train_phase3c_dev2.py").read_text(encoding="utf-8")
    token_source = (ROOT / "scripts/train_phase2a_qlora.py").read_text(encoding="utf-8")
    report = {"files": files, "train_phase3c_dev2_uses_TokenDataset":
              "from train_phase2a_qlora import RssMonitor, TokenDataset" in dev2 and "DataLoader(TokenDataset(" in dev2,
              "TokenDataset_user_wrapper": 'Task {example_id}',
              "wrapper_definition_present": 'user=f"Task {row[\'example_id\']}\\n\\n{row[\'prompt\']}"' in token_source}
    emit(capsys, "I4a T6 DESCRIPTIVE", report)


@pytest.mark.parametrize("path, obj", [
    ("benchmark/phase2a/development_hidden_tests.json", {"id": [{"stdin": "0", "expected_stdout": "0"}]}),
    ("benchmark/phase2a/development_references.json", {"id": {"source": "DISPLAYNL(0)."}}),
    ("data/phase2a/training_examples.json", [{"example_id": "id", "prompt": "text", "target": "DISPLAYNL(0)."}]),
])
def test_unknown_schema_stops(path, obj):
    with pytest.raises(GateStop, match="unrecognized consumed schema") as stopped:
        overlap._extract(path, obj)
    assert stopped.value.report["path"] == path


def test_unknown_file_family_stops_before_read():
    with pytest.raises(GateStop, match="unrecognized consumed file family"):
        overlap._family("data/phase2a/unrecognized.json")


@pytest.mark.parametrize("directory, name", [("benchmark", "unexpected"),
                                             ("data", "unexpected.txt"),
                                             ("benchmark/phase1r", "unexpected.txt"),
                                             ("data/phase2a", "nested")])
def test_unexpected_entry_stops_before_corpus_reads(monkeypatch, directory, name):
    original = Path.iterdir

    def entries(path):
        values = list(original(path))
        if path == ROOT / directory:
            values.append(path / name)
        return iter(values)

    def forbidden_read(path):
        pytest.fail("corpus must be fully enumerated before any file read")

    monkeypatch.setattr(Path, "iterdir", entries)
    monkeypatch.setattr(Path, "read_bytes", forbidden_read)
    with pytest.raises(GateStop, match="unexpected corpus file or directory"):
        overlap.consumed_inventory()
