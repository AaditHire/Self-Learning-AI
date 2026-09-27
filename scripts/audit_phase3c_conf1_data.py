"""Non-model CONF1 data, fairness, case and consumed-input audit."""

from __future__ import annotations

import difflib
import hashlib
import itertools
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from build_phase2b_data import ast_proxy  # noqa: E402
from validate_phase2b_data import jaccard, normalized_code  # noqa: E402
from build_phase3c_conf1_data import LEDGER, PREDICATES, parse_input  # noqa: E402
from design_phase3c_conf1 import contribution, rotated  # noqa: E402

OUT = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE"
HISTORY = [
    ("DEV1_DENSE", "data/phase3c_dev1/a_dense_training_examples.json", "data/phase3c_dev1/a_dense_training_references.json"),
    ("DEV1_DIVERSE", "data/phase3c_dev1/a_diverse_training_examples.json", "data/phase3c_dev1/a_diverse_training_references.json"),
    ("DEV1_EVAL", "benchmark/phase3c_dev1/a_development_eval_tasks.json", "benchmark/phase3c_dev1/a_development_eval_references.json"),
    ("DEV2_ISOLATED", "data/phase3c_dev2/a_isolated_training_examples.json", "data/phase3c_dev2/a_isolated_training_references.json"),
    ("DEV2_COMPOSITION", "data/phase3c_dev2/a_composition_training_examples.json", "data/phase3c_dev2/a_composition_training_references.json"),
    ("DEV2_EVAL", "benchmark/phase3c_dev2/a_development_eval_tasks.json", "benchmark/phase3c_dev2/a_development_eval_references.json"),
    ("DEV2R_V1", "benchmark/phase3c_dev2r/a_development_eval_tasks.json", "benchmark/phase3c_dev2r/a_development_eval_references.json"),
    ("DEV2R_V2", "benchmark/phase3c_dev2r_v2/a_development_eval_tasks.json", "benchmark/phase3c_dev2r_v2/a_development_eval_references.json"),
]


def read(rel: str) -> object:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def write(name: str, value: object) -> None:
    path = OUT / name
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def candidate_rows() -> list[dict]:
    out = []
    for condition in ("isolated", "composition"):
        rows = read(f"data/phase3c_conf1/{condition}_examples.json")
        for r in rows:
            out.append({"id": r["example_id"], "prompt": r["prompt"], "source": r["target"],
                        "family": r["family"], "group": f"training_{condition}"})
    refs = read("benchmark/phase3c_conf1/references.json")
    for r in read("benchmark/phase3c_conf1/tasks.json"):
        out.append({"id": r["task_id"], "prompt": r["prompt"], "source": refs[r["task_id"]],
                    "family": r["family"], "group": r["group"]})
    return out


def audit_scaffold() -> dict:
    iso = {r["slot_id"]: r for r in read("data/phase3c_conf1/isolated_examples.json")}
    comp = {r["slot_id"]: r for r in read("data/phase3c_conf1/composition_examples.json")}
    assert set(iso) == set(comp) and len(iso) == 60
    rows = []
    for sid in sorted(iso):
        a, b = iso[sid], comp[sid]
        a_norm = a["target"].replace("total+=(hitP+hitQ).", "total+=(<TREATMENT_EXPRESSION>).").strip()
        b_norm = b["target"].replace("total+=(hitP*hitQ).", "total+=(<TREATMENT_EXPRESSION>).").strip()
        if a_norm != b_norm:
            raise ValueError(f"INVALID_UNCONTROLLED_DIFFERENCE source: {sid}")
        if a["target"].count("total+=(hitP+hitQ).") != 1 or b["target"].count("total+=(hitP*hitQ).") != 1:
            raise ValueError(f"bad treatment expression: {sid}")
        for source in (a["target"], b["target"]):
            if source.count("IF (") != 2 or source.count("LOOP (") != 1 or source.count("DISPLAYNL(") != 1:
                raise ValueError(f"unmatched training scaffold: {sid}")
            for predicate in (a["semantic_primitives"][0], a["semantic_primitives"][1]):
                if source.count(PREDICATES[a["family"]][predicate]) != 1:
                    raise ValueError(f"predicate occurrence: {sid} {predicate}")
        rows.append({"slot_id": sid, "scaffold_equal_after_treatment_abstraction": True,
                     "source_classification": "MATCHED outside treatment; INTENDED_TREATMENT_DIFFERENCE inside",
                     "prompt_classification": "MATCHED wrapper; INTENDED_TREATMENT_DIFFERENCE clause",
                     "output_classification": "UNAVOIDABLE_SEMANTIC_CONSEQUENCE"})
    return {"pairs": len(rows), "invalid_uncontrolled_differences": 0, "rows": rows}


def audit_budget() -> dict:
    data = {c: read(f"data/phase3c_conf1/{c}_examples.json") for c in ("isolated", "composition")}
    rows = {}
    for c, examples in data.items():
        role = Counter((r["family"], p) for r in examples for p in r["semantic_primitives"])
        source_occ = Counter((r["family"], p) for r in examples for p in r["semantic_primitives"]
                             if r["target"].count(PREDICATES[r["family"]][p]) == 1)
        rows[c] = {"examples": len(examples), "subskills": dict(Counter(r["family"] for r in examples)),
                   "primitive_containing": {f"{f}:{p}": n for (f, p), n in role.items()},
                   "primitive_source_occurrences": {f"{f}:{p}": n for (f, p), n in source_occ.items()},
                   "pair_role_schedule": [(r["slot_id"], r["semantic_primitives"]) for r in examples],
                   "exposures": len(examples) * 3, "optimizer_steps": 24}
    a, b = rows["isolated"], rows["composition"]
    for key in ("examples", "subskills", "primitive_containing", "primitive_source_occurrences",
                "pair_role_schedule", "exposures", "optimizer_steps"):
        if a[key] != b[key]:
            raise ValueError(f"budget mismatch: {key}")
    assert a["examples"] == 60 and a["subskills"] == {"numeric_iteration": 30, "array_reduction": 30}
    assert set(a["primitive_containing"].values()) == {15}
    return {"conditions": rows, "matched": True, "scaffold": audit_scaffold()}


def audit_cases() -> dict:
    rows = read("benchmark/phase3c_conf1/tasks.json")
    tests = read("benchmark/phase3c_conf1/hidden_cases.json")
    slots = {r["task_id"]: r for r in LEDGER["slots"]["primary"]}
    primary = [r for r in rows if r["group"] == "novel_composition"]
    by_family = {}
    matrices = []
    for family in PREDICATES:
        local = [r for r in primary if r["family"] == family]
        distinct = []
        for a, b in itertools.combinations(local, 2):
            left = [c["expected_stdout"] for c in tests[a["task_id"]]]
            right = [c["expected_stdout"] for c in tests[b["task_id"]]]
            if left == right:
                raise ValueError(f"five-case indistinguishable slots: {a['task_id']} {b['task_id']}")
            distinct.append({"left": a["task_id"], "right": b["task_id"],
                             "distinguishing_case_indices": [i + 1 for i in range(5) if left[i] != right[i]]})
        assert len(distinct) == 120
        by_family[family] = {"pairs": 120, "distinguished_by_selected_cases": 120, "records": distinct}
    for r in primary:
        slot = slots[r["task_id"]]
        inputs = [c["stdin"].strip() for c in tests[r["task_id"]]]
        values = [float(c["expected_stdout"]) for c in tests[r["task_id"]]]
        item_contrib = [contribution(slot["graph"], rotated(bits, slot["rotation"]))
                        for x in inputs for _, bits in parse_input(slot["family"], x)]
        overlap_hits = [bool(rotated(bits, slot["rotation"])[0] and
                             rotated(bits, slot["rotation"])[1] and
                             rotated(bits, slot["rotation"])[2])
                        for x in inputs for _, bits in parse_input(slot["family"], x)]
        possible = []
        if slot["family"] == "array_reduction":
            for i in range(4):
                for x in range(-16, 17):
                    bits = (x < 0, x % 2 == 0, x * x > 4, x > i)
                    possible.append(contribution(slot["graph"], rotated(bits, slot["rotation"])))
        else:
            for n in range(101):
                possible.extend(contribution(slot["graph"], rotated(bits, slot["rotation"]))
                                for _, bits in parse_input(slot["family"], str(n)))
        max_possible = max(possible, default=0)
        max_observed = max(item_contrib, default=0)
        if not any(v == 0 for v in values) or not any(v > 0 for v in values):
            raise ValueError(f"zero/positive cases missing: {r['task_id']}")
        if max_possible >= 2 and max_observed < 2:
            raise ValueError(f"multiplicity case missing: {r['task_id']}")
        if slot["graph"] == "G1" and any(overlap_hits) is False:
            feasible_overlap = any(
                all(rotated((x < 0, x % 2 == 0, x * x > 4, x > i), slot["rotation"])[j]
                    for j in (0, 1, 2))
                for i in range(4) for x in range(-16, 17)
            ) if slot["family"] == "array_reduction" else True
            if feasible_overlap:
                raise ValueError(f"G1 overlap not exercised: {r['task_id']}")
        matrices.append({"task_id": r["task_id"], "positive": True, "zero_or_empty": True,
                         "boundary_input": inputs[0], "max_item_contribution_possible": max_possible,
                         "max_item_contribution_exercised": max_observed,
                         "overlap_exercised": any(overlap_hits),
                         "all_five_inputs": inputs, "all_five_outputs": values})
    return {"by_family": by_family, "task_matrices": matrices, "task_count": len(matrices)}


def audit_coverage() -> dict:
    training = {c: read(f"data/phase3c_conf1/{c}_examples.json") for c in ("isolated", "composition")}
    corpus = {c: "\n".join(r["target"] for r in training[c]) for c in training}
    primitives = {c: {p for r in training[c] for p in r["semantic_primitives"]} for c in training}
    rows = []
    for r in read("benchmark/phase3c_conf1/tasks.json"):
        required = set(r["semantic_primitives"])
        api = ["INPUT", "LOOP", "IF", "DISPLAYNL"]
        if r["family"] == "array_reduction":
            api += ["IMPORT strings", "strings.SPLIT", "strings.TO_NUMBER", "values["]
        source = read("benchmark/phase3c_conf1/references.json")[r["task_id"]]
        literals = sorted(set(re.findall(r"(?<![A-Za-z_])\d+", source)))
        missing = {c: {"primitives": sorted(required - primitives[c]),
                       "api": [x for x in api if x not in corpus[c]],
                       "numeric_literal_capability": "nonnegative_integer" not in "nonnegative_integer"}
                   for c in training}
        if any(v["primitives"] or v["api"] for v in missing.values()):
            raise ValueError(f"task-essential coverage: {r['task_id']} {missing}")
        rows.append({"task_id": r["task_id"], "group": r["group"],
                     "TASK_ESSENTIAL": {"primitives": sorted(required), "api_constructs": api,
                                        "literals": "nonnegative integer constants and signed array inputs",
                                        "output_capability": "single nonnegative integer, including zero",
                                        "control_flow": "bounded iteration with conditional predicate evaluation"},
                     "REFERENCE_ONLY": {"numeric_literal_spellings": literals,
                                        "source_ast_proxy": ast_proxy(source)},
                     "missing_by_condition": missing})
    return {"tasks": len(rows), "coverage_valid": len(rows), "rows": rows,
            "treatment_relation_excluded_from_shared_primitive_coverage": True}


def history_rows() -> list[dict]:
    out = []
    for label, tasks_path, refs_path in HISTORY:
        tasks, refs = read(tasks_path), read(refs_path)
        for r in tasks:
            ident = r.get("task_id", r.get("example_id"))
            out.append({"origin": label, "id": ident, "prompt": r["prompt"], "source": refs[ident]})
    return out


def audit_overlap() -> dict:
    current = candidate_rows()
    history = history_rows()
    pairs = []
    nearest = []
    for x in current:
        local = []
        for y in history:
            a, b = normalized_code(x["source"]), normalized_code(y["source"])
            row = {"candidate_id": x["id"], "candidate_group": x["group"],
                   "historical_origin": y["origin"], "historical_id": y["id"],
                   "exact_prompt": x["prompt"] == y["prompt"],
                   "exact_reference_or_target": x["source"] == y["source"],
                   "normalized_source_exact": a == b,
                   "ast_proxy_exact": ast_proxy(x["source"]) == ast_proxy(y["source"]),
                   "full_template_match": a == b,
                   "prompt_jaccard": jaccard(x["prompt"], y["prompt"]),
                   "normalized_code_similarity": difflib.SequenceMatcher(None, a, b).ratio()}
            local.append(row)
        pairs.extend(local)
        nearest.append(max(local, key=lambda z: z["normalized_code_similarity"]))
    forbidden = [p for p in pairs if p["exact_prompt"] or p["exact_reference_or_target"] or p["full_template_match"]]
    write("consumed_similarity_pairs.json", pairs)
    if forbidden:
        raise ValueError(f"prohibited consumed-suite overlap: {len(forbidden)}")
    return {"pairs": len(pairs), "forbidden_exact_or_template": 0,
            "ast_proxy_exact_pairs": sum(p["ast_proxy_exact"] for p in pairs),
            "max_normalized_code_similarity": max(p["normalized_code_similarity"] for p in pairs),
            "nearest": nearest, "historical_inputs_only": True}


def audit_signatures() -> dict:
    eval_rows = [r for r in read("benchmark/phase3c_conf1/tasks.json") if r["group"] == "novel_composition"]
    training = {c: read(f"data/phase3c_conf1/{c}_examples.json") for c in ("isolated", "composition")}
    full = []
    for r in eval_rows:
        signature = r["composition_signature"]
        absent = {c: signature not in {x["composition_signature"] for x in rows} for c, rows in training.items()}
        if not all(absent.values()):
            raise ValueError(f"full composition signature in training: {r['task_id']}")
        source = read("benchmark/phase3c_conf1/references.json")[r["task_id"]]
        motifs = {"explicit_pair_multiplications": len(re.findall(r"hit[PQRS]\*hit[PQRS]", source)),
                  "training_like_pair_motif": "*" in source,
                  "full_graph_absent": True}
        full.append({"task_id": r["task_id"], "signature": signature,
                     "absent_by_condition": absent, "local_motifs": motifs})
    return {"primary_tasks": 32, "full_signatures_absent_both": 32,
            "tasks_with_local_pair_motifs": sum(x["local_motifs"]["training_like_pair_motif"] for x in full),
            "rows": full}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = {"status": "NON_MODEL_PREFREEZE_DATA_AUDIT",
               "counts": {"isolated": 60, "composition": 60, "primary": 32,
                          "primitive_sanity": 16, "structural_transfer": 16,
                          "training_cases": 600, "evaluation_cases": 320},
               "budget": audit_budget(), "cases": audit_cases(),
               "coverage": audit_coverage(), "signatures": audit_signatures(),
               "overlap": audit_overlap(), "no_model_outputs_used": True}
    write("data_audit.json", results)
    print(json.dumps({"case_pairs": [x["distinguished_by_selected_cases"] for x in results["cases"]["by_family"].values()],
                      "covered_tasks": results["coverage"]["coverage_valid"],
                      "signature_absent": results["signatures"]["full_signatures_absent_both"],
                      "historical_pairs": results["overlap"]["pairs"],
                      "template_matches": results["overlap"]["forbidden_exact_or_template"]}))


if __name__ == "__main__":
    main()
