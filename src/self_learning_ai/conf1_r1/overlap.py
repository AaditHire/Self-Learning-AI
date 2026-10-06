"""C10 exact P7/E4 overlap and a fail-closed, read-only consumed inventory.

Input items are dictionaries with id, role (primary/secondary/training),
optional prompt, model_user_message, source, and cases. Training items also
carry the condition-neutral slot_id. Cases use stdin and expected_stdout
strings. Group identifies the two secondary populations for C11 accounting.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from self_learning_ai.conf1_r1.gates_primary import ROOT, GateStop
from self_learning_ai.conf1_r1.training import _definitions


CORPUS_DIRS = {
    "benchmark": ("phase1r", "phase1s", "phase1t", "phase2a", "phase2b", "phase3a", "phase3b",
                  "phase3c", "phase3c_dev1", "phase3c_dev2", "phase3c_dev2r", "phase3c_dev2r_v2"),
    "data": ("phase2a", "phase2b", "phase3a", "phase3b", "phase3c", "phase3c_dev1", "phase3c_dev2"),
}
EXCLUDED = frozenset("benchmark/" + name for name in
                     ("tasks.json", "hidden_tests.json", "reference_solutions.json"))

# Explicit file families, not a search over JSON-looking objects or field guesses.
_STEMS = {
    "benchmark/phase1r": ("development",), "benchmark/phase1s": ("diagnostic",),
    "benchmark/phase1t": ("confirmation",), "benchmark/phase2a": ("development",),
    "benchmark/phase2b": ("confirmatory",),
    **{f"benchmark/{phase}": ("a_eval", "b_eval") for phase in ("phase3a", "phase3b", "phase3c")},
    **{f"benchmark/{phase}": ("a_development_eval",) for phase in
       ("phase3c_dev1", "phase3c_dev2", "phase3c_dev2r", "phase3c_dev2r_v2")},
    **{f"data/{phase}": ("training",) for phase in ("phase2a", "phase2b")},
    **{f"data/{phase}": ("a_training", "b_training") for phase in ("phase3a", "phase3b", "phase3c")},
    "data/phase3c_dev1": ("a_dense_training", "a_diverse_training"),
    "data/phase3c_dev2": ("a_composition_training", "a_isolated_training"),
}


def _keys(text):
    return frozenset(text.split())


_TASK_KEYS = {
    "phase1r": _keys("constructs difficulty family input_shape prompt required_regex split structure task_id template_lineage"),
    "phase1t": _keys("algorithmic_structure constructs control_flow difficulty family level prompt required_regex split structural_signature task_id template_lineage"),
    "phase2a": _keys("algorithmic_structure control_flow difficulty family level prompt required_regex split structural_signature task_id template_lineage"),
    "phase2b": _keys("algorithmic_structure ast_proxy_signature control_flow difficulty family level prompt required_regex semantic_operations split structural_signature task_id template_lineage"),
    "phase3a": _keys("algorithmic_structure ast_proxy_signature capability control_flow difficulty family level prompt required_regex semantic_operations split structural_signature task_id template_lineage"),
    "phase3c_dev2": _keys("archetype ast_proxy_signature capability composition_signature control_flow development_group family level prompt required_regex semantic_primitives split task_id"),
    "phase3c_dev2r": _keys("api_requirements archetype ast_proxy_signature capability composition_signature control_flow development_group family prompt required_regex semantic_primitives split task_id"),
}
_TASK_KEYS["phase3b"] = _TASK_KEYS["phase3a"]
_TASK_KEYS["phase3c"] = _TASK_KEYS["phase3a"] | {"archetype"}
_TASK_KEYS["phase3c_dev1"] = _TASK_KEYS["phase3c"] | {"distance_group"}
_TASK_KEYS["phase3c_dev2r_v2"] = _TASK_KEYS["phase3c_dev2r"]
_S1S = _keys("constructs control_flow difficulty family level matched_scenario prompt split structural_signature task_id template_lineage")
_S1S_KEYS = (_S1S | {"answer"}, _S1S | {"required_regex"},
             _S1S | {"required_regex", "scaffold_prefix", "scaffold_suffix"})
_EXAMPLE_KEYS = {
    "phase2a": _keys("algorithmic_structure control_flow example_id family prompt split structural_signature target template_lineage"),
    "phase2b": _keys("algorithmic_structure ast_proxy_signature control_flow example_id family prompt semantic_operations split structural_signature target template_lineage"),
    "phase3a": _keys("algorithmic_structure ast_proxy_signature capability control_flow example_id family prompt semantic_operations split structural_signature target template_lineage"),
    "phase3c_dev2": _keys("archetype ast_proxy_signature capability composition_signature control_flow example_id family prompt semantic_primitives split target"),
}
_EXAMPLE_KEYS["phase3b"] = _EXAMPLE_KEYS["phase3a"]
_EXAMPLE_KEYS["phase3c"] = _EXAMPLE_KEYS["phase3a"] | {"archetype"}
_EXAMPLE_KEYS["phase3c_dev1"] = _EXAMPLE_KEYS["phase3c"]
_REGRESSION_KEYS = _keys("category expected prompt split task_id template_lineage")


@lru_cache(maxsize=1)
def _normalizer():
    # Definitions only: this script's writing/evaluating main is never invoked.
    return _definitions("validate_phase2b_data")


def _family(path):
    directory, filename = path.rsplit("/", 1)
    stems = _STEMS[directory]
    for stem in stems:
        if filename == stem + "_hidden_tests.json":
            return "cases"
        reference_suffix = "_reference_solutions.json" if directory == "benchmark/phase1r" else "_references.json"
        if filename == stem + reference_suffix:
            return "references"
        suffix = "_tasks.json" if directory.startswith("benchmark/") else "_examples.json"
        if filename == stem + suffix:
            return "prompts" if directory.startswith("benchmark/") else "examples"
    if directory in ("benchmark/phase2a", "benchmark/phase2b") and filename == "general_regression.json":
        return "regression"
    raise GateStop("unrecognized consumed file family", {"path": path})


def _extract(path, obj):
    family = _family(path)
    records = defaultdict(list)

    def check(valid):
        if not valid:
            raise GateStop("unrecognized consumed schema", {"path": path, "family": family})

    def record(kind, identifier, value, **extra):
        check(isinstance(identifier, str) and isinstance(value, str))
        records[kind].append({"task_id": identifier, "value": value, **extra})

    if family in ("references", "cases"):
        check(isinstance(obj, dict) and bool(obj))
        for identifier, value in obj.items():
            if family == "references":
                record("references", identifier, value)
            else:
                check(isinstance(identifier, str) and isinstance(value, list) and bool(value))
                for case in value:
                    check(isinstance(case, dict) and set(case) == {"case_id", "stdin", "expected_stdout"}
                          and all(isinstance(v, str) for v in case.values()))
                    record("cases", identifier, case["stdin"], expected_stdout=case["expected_stdout"],
                           case_id=case["case_id"])
    else:
        check(isinstance(obj, list) and bool(obj))
        phase = path.split("/")[1]
        schemas = ((_REGRESSION_KEYS,) if family == "regression" else
                   (_EXAMPLE_KEYS[phase],) if family == "examples" else
                   _S1S_KEYS if phase == "phase1s" else (_TASK_KEYS[phase],))
        identifiers = []
        for row in obj:
            check(isinstance(row, dict) and frozenset(row) in schemas)
            identifier = row["example_id" if family == "examples" else "task_id"]
            record("prompts", identifier, row["prompt"])
            identifiers.append(identifier)
            if family == "examples":
                record("targets", identifier, row["target"])
        check(len(set(identifiers)) == len(identifiers))
        # Phase1S recognition answers are option letters, not GOCO references.
        # General regression expected answers have no stdin and are not cases.
    return dict(records), len(obj) if family != "cases" else len(records["cases"])


def consumed_inventory(root=ROOT):
    """Enumerate the complete C10 allowlist before opening any corpus file.

    SHA-256 binds working-tree bytes; git_blob is the corresponding HEAD blob.
    Every excluded path is filtered before opening, hashing or Git inspection.
    """
    root = Path(root).resolve()
    paths, directories = [], {}
    for area, allowed in CORPUS_DIRS.items():
        base = root / area
        if not base.is_dir() or base.is_symlink():
            raise GateStop("consumed corpus directory unavailable", {"path": area})
        found = set()
        for entry in sorted(base.iterdir()):
            relative = entry.relative_to(root).as_posix()
            if relative in EXCLUDED:
                if not entry.is_file() or entry.is_symlink():
                    raise GateStop("excluded corpus path is not a regular file", {"path": relative})
                continue
            if entry.name not in allowed or not entry.is_dir() or entry.is_symlink():
                raise GateStop("unexpected corpus file or directory", {"path": relative})
            found.add(entry.name)
            files = sorted(entry.iterdir())
            for path in files:
                name = path.relative_to(root).as_posix()
                if not path.is_file() or path.is_symlink() or path.suffix != ".json":
                    raise GateStop("unexpected corpus file or directory", {"path": name})
                _family(name)  # Recognize all file families before any file read.
                paths.append(path)
            directories[relative] = len(files)
        if found != set(allowed):
            raise GateStop("consumed corpus directory population mismatch",
                           {"area": area, "missing": sorted(set(allowed) - found)})
    files, totals = [], Counter()
    for path in paths:
        relative = path.relative_to(root).as_posix()
        raw = path.read_bytes()
        try:
            obj = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise GateStop("invalid consumed JSON", {"path": relative}) from exc
        records, count = _extract(relative, obj)
        blob = subprocess.run(["git", "rev-parse", f"HEAD:{relative}"], cwd=root,
                              capture_output=True, text=True, check=False)
        if blob.returncode:
            raise GateStop("consumed file has no HEAD Git blob", {"path": relative})
        counts = {kind: len(rows) for kind, rows in records.items()}
        totals.update(counts)
        files.append({"path": relative, "sha256": hashlib.sha256(raw).hexdigest(),
                      "git_blob": blob.stdout.strip(), "record_kind": list(records),
                      "record_count": count, "records_by_kind": counts, "records": records})
    return {"directories": dict(sorted(directories.items())), "files": files,
            "total_files": len(files), "records_by_kind": dict(sorted(totals.items())),
            "excluded": sorted(EXCLUDED), "phase1_baseline_outside_corpus": True}


def _consumed(inventory, kinds):
    return [{"path": file["path"], "id": record["task_id"], **record}
            for file in inventory["files"] for kind in kinds
            for record in file["records"].get(kind, [])]


def _prepare(items):
    items = list(items)
    if len({item["id"] for item in items}) != len(items):
        raise GateStop("duplicate CONF1 overlap item ID")
    for item in items:
        if item["role"] not in ("primary", "secondary", "training"):
            raise GateStop("unknown CONF1 overlap item role", {"id": item["id"]})
        if item["role"] == "training" and not isinstance(item.get("slot_id"), str):
            raise GateStop("training overlap item requires condition-neutral slot_id")
        for field in ("prompt", "model_user_message", "source"):
            if field in item and not isinstance(item[field], str):
                raise GateStop("overlap text must be a string", {"id": item["id"], "field": field})
        for case in item.get("cases", []):
            if any(not isinstance(case.get(field), str) for field in ("stdin", "expected_stdout")):
                raise GateStop("overlap cases require stdin and expected_stdout strings", {"id": item["id"]})
    return items


def _prompts(item):
    return {item[field] for field in ("prompt", "model_user_message") if field in item}


def _identity(item):
    return ("slot", item["slot_id"]) if item["role"] == "training" else ("task", item["id"])


def _descriptive_cases(items, inventory):
    consumed = _consumed(inventory, ("cases",))
    training = [case for item in items if item["role"] == "training" for case in item.get("cases", [])]
    populations = {"consumed": [(row["value"], row["expected_stdout"]) for row in consumed],
                   "conf1_training": [(row["stdin"], row["expected_stdout"]) for row in training]}
    report = {}
    evaluation = [(item["id"], case) for item in items if item["role"] != "training"
                  for case in item.get("cases", [])]
    for name, cases in populations.items():
        raw, pairs = Counter(x[0] for x in cases), Counter(cases)
        rows = []
        for identifier, case in evaluation:
            pair = case["stdin"], case["expected_stdout"]
            rows.append({"id": identifier, "raw_matches": raw[pair[0]], "pair_matches": pairs[pair]})
        report[name] = {"evaluation_cases": len(evaluation), "comparison_cases": len(cases),
                        "raw_matching_cases": sum(row["raw_matches"] > 0 for row in rows),
                        "pair_matching_cases": sum(row["pair_matches"] > 0 for row in rows),
                        "raw_match_pairs": sum(row["raw_matches"] for row in rows),
                        "pair_match_pairs": sum(row["pair_matches"] for row in rows),
                        "by_task": {identifier: {"raw_matches": sum(r["raw_matches"] for r in rows if r["id"] == identifier),
                                                 "pair_matches": sum(r["pair_matches"] for r in rows if r["id"] == identifier)}
                                    for identifier in sorted({r["id"] for r in rows})}}
    return report


def p7_overlap(conf1_items, inventory):
    """Enforce C10(a)-(c). Primary/training failures raise STOP with full evidence.

    In a collision involving a secondary slot, C11 drops that secondary slot;
    it cannot change or block the primary/training population. No successor
    secondary generator exists. Raw case overlaps alone never affect a gate.
    """
    items = _prepare(conf1_items)
    norm = _normalizer().normalized_code
    prompts = _consumed(inventory, ("prompts",))
    sources = _consumed(inventory, ("references", "targets"))
    consumed_cases = defaultdict(list)
    for row in _consumed(inventory, ("cases",)):
        consumed_cases[row["path"].rsplit("/", 1)[0], row["id"]].append(row)
    prompt_index, source_index = defaultdict(list), defaultdict(list)
    for row in prompts:
        prompt_index[row["value"]].append(row)
    for row in sources:
        source_index[norm(row["value"])].append(row)
    blocking = []

    def match(rule, left, right, field, affected, consumed=False):
        blocking.append({"rule": rule, "left": left["id"], "right": right["id"], "field": field,
                         "consumed_path": right.get("path") if consumed else None, "affected": affected})
        left_pairs = {(c["stdin"], c["expected_stdout"]) for c in left.get("cases", [])}
        other_cases = (consumed_cases[right["path"].rsplit("/", 1)[0], right["id"]] if consumed
                       else right.get("cases", []))
        shared = left_pairs & {(c.get("stdin", c.get("value")), c["expected_stdout"]) for c in other_cases}
        if shared:
            blocking.append({"rule": "c", "left": left["id"], "right": right["id"],
                             "specification_rule": rule, "consumed_path": right.get("path") if consumed else None,
                             "case_pairs": sorted(shared), "affected": affected})

    for item in items:
        for text in sorted(_prompts(item)):
            for row in prompt_index[text]:
                match("a", item, row, "prompt", [item["id"]], consumed=True)
        if "source" in item:
            for row in source_index[norm(item["source"])]:
                match("b", item, row, "normalized_source", [item["id"]], consumed=True)
    for index, left in enumerate(items):
        for right in items[index + 1:]:
            affected = [item["id"] for item in (left, right) if item["role"] == "secondary"]
            if not affected:
                affected = [left["id"], right["id"]]
            if _identity(left) != _identity(right) and _prompts(left) & _prompts(right):
                match("a", left, right, "prompt", affected)
            if ((left["role"] == "training") != (right["role"] == "training")
                    and "source" in left and "source" in right and norm(left["source"]) == norm(right["source"])):
                match("b", left, right, "normalized_source", affected)
    affected = {identifier for row in blocking for identifier in row["affected"]}
    secondary = [item for item in items if item["role"] == "secondary"]
    kept = [item for item in secondary if item["id"] not in affected]
    fatal = sorted(item["id"] for item in items if item["role"] != "secondary" and item["id"] in affected)
    report = {"status": "STOP" if fatal else "PASS", "blocking": blocking, "fatal_items": fatal,
              "secondary_drops": [{"id": item["id"], "reason": "P7_FAIL_CANDIDATES_EXHAUSTED"}
                                  for item in secondary if item["id"] in affected],
              "kept_secondary": [item["id"] for item in kept],
              "sanity_count": sum(item.get("group") == "primitive_sanity" for item in kept),
              "descriptive": _descriptive_cases(items, inventory)}
    report["SANITY_NOT_EVALUABLE"] = report["sanity_count"] < 12
    if fatal:
        raise GateStop("P7 blocking overlap on primary or training items", report)
    return report


def nearest_descriptive(conf1_items, inventory):
    """Existing Phase2B Jaccard/normalized-code SequenceMatcher, without a gate.

    Return each nearest consumed record and evaluation-to-training neighbor;
    counts of all compared pairs include duplicate corpus records. No new
    similarity threshold is introduced. Ties retain the first inventory record.
    """
    items = _prepare(conf1_items)
    authority = _normalizer()
    norm = authority.normalized_code
    result = {}
    for kind in ("prompt", "source"):
        candidates = (_consumed(inventory, ("prompts",)) if kind == "prompt" else
                      _consumed(inventory, ("references", "targets")))
        transform = (lambda value: value) if kind == "prompt" else norm
        metric = authority.jaccard if kind == "prompt" else lambda a, b: difflib.SequenceMatcher(None, a, b).ratio()
        queries = [(item, field, item[field]) for item in items
                   for field in (("prompt", "model_user_message") if kind == "prompt" else ("source",))
                   if field in item]
        training = [{"id": item["id"], "value": item[field]} for item in items if item["role"] == "training"
                    for field in (("prompt", "model_user_message") if kind == "prompt" else ("source",)) if field in item]
        for population, values in (("consumed", candidates), ("conf1_training", training)):
            unique = {}
            for row in values:
                unique.setdefault(transform(row["value"]), row)
            cache, rows = {}, []
            for item, field, value in queries:
                if population == "conf1_training" and item["role"] == "training":
                    continue
                text = transform(value)
                if text not in cache:
                    scored = [(metric(text, candidate), row) for candidate, row in unique.items()]
                    cache[text] = max(scored, key=lambda pair: pair[0]) if scored else (None, None)
                score, row = cache[text]
                rows.append({"id": item["id"], "field": field, "nearest_id": row["id"] if row else None,
                             "nearest_path": row.get("path") if row else None, "similarity": score})
            scores = [row["similarity"] for row in rows if row["similarity"] is not None]
            result[kind + "_" + population] = {"query_count": len(rows), "candidate_count": len(values),
                                               "compared_pairs": len(rows) * len(values), "nearest_count": len(scores),
                                               "min_similarity": min(scores) if scores else None,
                                               "max_similarity": max(scores) if scores else None, "rows": rows}
    return result
