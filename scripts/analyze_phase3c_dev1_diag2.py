"""Post-hoc DEV1 transfer audit. Reads frozen JSON only; never imports a model/scorer."""

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/results/PHASE_3C_DEV1_DIAG2"
SEEDS = (20270925, 20271013, 20271119)
RAW = ROOT / "research/artifacts/phase3c-dev1/raw"

# Curated from the frozen prompts and reference programs. These are semantic
# requirements, not model-observed labels. Generic I/O and output offsets are
# recorded separately. A composite operation is split into its essential parts.
SPEC = {
    "fourth_square": ("numeric_iteration", "bounded ascending loop with one filter", "scalar", ["multiple_four", "square_accumulate"], "filter multiples of four, accumulate squared indices", []),
    "nontriple_count": ("numeric_iteration", "bounded ascending loop with one filter", "scalar", ["not_multiple_three", "count"], "count indices not divisible by three; affine output", []),
    "alternating_weight": ("numeric_iteration", "bounded ascending loop with IF/ELSE", "scalar", ["parity_branch", "position_weight", "signed_accumulate"], "add weighted odd positions and subtract even positions", []),
    "divisor_tally": ("numeric_iteration", "bounded ascending loop with one filter", "scalar", ["divisor_test", "count"], "count divisors of the input", []),
    "descending_odd": ("numeric_iteration", "condition-controlled descending loop", "scalar", ["descending_loop", "odd_filter", "affine_accumulate"], "filter odd descending indices and sum offset values", []),
    "quadratic_balance": ("numeric_iteration", "bounded ascending loop", "scalar", ["square_accumulate", "linear_subtract"], "accumulate quadratic term minus linear term", []),
    "negative_tally": ("array_reduction", "indexed loop with one filter", "four-element array", ["negative_filter", "count"], "parse four values, count negatives", ["strings.SPLIT", "strings.TO_NUMBER"]),
    "neighbor_products": ("array_reduction", "indexed loop", "four-element array", ["neighbor_product", "array_accumulate"], "sum products of adjacent array elements", ["strings.SPLIT", "strings.TO_NUMBER"]),
    "positive_position": ("array_reduction", "indexed loop with one filter", "four-element array", ["positive_filter", "position_weight", "array_accumulate"], "filter positive values, weight by index plus one", ["strings.SPLIT", "strings.TO_NUMBER"]),
    "range_span": ("array_reduction", "indexed loop with two filters", "four-element array", ["minimum_track", "maximum_track", "range_combine"], "track min and max, subtract at output", ["strings.SPLIT", "strings.TO_NUMBER"]),
    "alternating_positions": ("array_reduction", "indexed loop with IF/ELSE", "four-element array", ["parity_branch", "signed_accumulate", "array_accumulate"], "alternating index-parity add and subtract", ["strings.SPLIT", "strings.TO_NUMBER"]),
    "even_square_total": ("array_reduction", "indexed loop with one filter", "four-element array", ["even_value_filter", "square_accumulate", "array_accumulate"], "filter even values and sum squares", ["strings.SPLIT", "strings.TO_NUMBER"]),
    "fourth_square_step": ("numeric_iteration", "bounded step-index loop", "scalar", ["multiple_four", "square_accumulate"], "reindex multiples of four, accumulate equivalent squares", []),
    "nontriple_divisor_mix": ("numeric_iteration", "one bounded loop with two independent IFs", "scalar", ["not_multiple_three", "divisor_test", "count"], "sum nonmultiple-three and divisor counts in one loop", []),
    "square_threshold_crossing": ("numeric_iteration", "accumulator-controlled loop", "scalar", ["square_accumulate", "threshold_termination", "first_crossing"], "add consecutive squares until cumulative threshold crossed; output first crossing index", []),
    "negative_tally_unrolled": ("array_reduction", "four unrolled IFs", "four-element array", ["negative_filter", "count"], "parse array; independently test each of four values", ["strings.SPLIT", "strings.TO_NUMBER"]),
    "range_neighbor_mix": ("array_reduction", "two indexed loops", "four-element array", ["neighbor_product", "array_accumulate", "minimum_track", "maximum_track", "range_combine"], "sum neighbor products, then track extrema, then combine", ["strings.SPLIT", "strings.TO_NUMBER"]),
    "positive_run_length": ("array_reduction", "indexed loop with nested IF and ELSE reset", "four-element array", ["positive_filter", "run_increment", "run_reset", "maximum_track"], "carry and reset positive-run length; track maximum segment", ["strings.SPLIT", "strings.TO_NUMBER"]),
}

# Surface signatures are deliberately weak evidence: detection does not prove
# correct semantics, and absence in invalid code need not prove absence of intent.
SIGNATURES = {
    "multiple_four": r"(?:%\s*4|4\s*\*\s*\w+)",
    "square_accumulate": r"\b\w+\s*\*\s*\w+",
    "not_multiple_three": r"%\s*3\s*!=\s*0",
    "divisor_test": r"\bn\s*%\s*\w+\s*==\s*0",
    "count": r"\+=\s*1\b",
    "parity_branch": r"%\s*2",
    "position_weight": r"\*\s*\(?\s*\w+\s*\+\s*1",
    "signed_accumulate": r"-=",
    "descending_loop": r"\w+\s*-=\s*1",
    "odd_filter": r"%\s*2\s*==\s*1",
    "affine_accumulate": r"\+=\s*\w+\s*\+",
    "linear_subtract": r"-\s*\w+\s*\*\s*\w+",
    "negative_filter": r"<\s*0",
    "neighbor_product": r"(?:\w+\s*\[\s*\w+\s*\]\s*\*\s*\w+\s*\[\s*\w+\s*\+\s*1\s*\]|\ba\s*\*\s*b\b|\bb\s*\*\s*c\b)",
    "array_accumulate": r"\+=\s*\w+\s*\[",
    "positive_filter": r">\s*0",
    "minimum_track": r"(?:<\s*(?:lo|min)|(?:lo|min)\s*=)",
    "maximum_track": r"(?:>\s*(?:hi|max|best)|(?:hi|max|best)\s*=)",
    "range_combine": r"(?:hi|max)\s*-\s*(?:lo|min)",
    "even_value_filter": r"%\s*2\s*==\s*0",
    "threshold_termination": r"LOOP\s*\(\s*(?:total|sum)\s*<",
    "first_crossing": r"DISPLAYNL\s*\(\s*(?:i|index|step)\s*\)",
    "run_increment": r"(?:run|count)\s*\+=\s*1",
    "run_reset": r"(?:run|count)\s*=\s*0",
}
EXTRA_SURFACES = {
    "unsupported_or_unexpected_BREAK": r"\bBREAK\b",
    "unexpected_INPUT_inside_loop": r"LOOP[\s\S]*\bINPUT\s*\(",
    "comma_declaration": r"\bNUMBER\s+\w+\s*=\s*[^.\n]+,\s*\w+\s*=",
    "value_equality_in_run_task": r"values\s*\[[^]]+\]\s*==\s*values\s*\[",
}
SOURCE_MOTIFS = {
    "not_multiple_three": "nontriple_count", "divisor_test": "divisor_tally",
    "neighbor_product": "neighbor_products", "minimum_track": "range_span",
    "maximum_track": "range_span", "range_combine": "range_span",
    "positive_filter": "positive_position", "square_accumulate": "fourth_square",
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_spec(a):
    family, control, structure, operations, order, api = SPEC[a]
    return dict(archetype=a, subskill=family, control_flow=control, data_structure=structure,
                required_primitives=operations, composition_order=order, goco_api=api)


def main():
    files = {}
    def load(rel):
        path = ROOT / rel
        files[rel] = sha(path)
        return read(path)

    training = {c: load(f"data/phase3c_dev1/a_{c}_training_examples.json") for c in ("dense", "diverse")}
    train_refs = {c: load(f"data/phase3c_dev1/a_{c}_training_references.json") for c in ("dense", "diverse")}
    tasks = load("benchmark/phase3c_dev1/a_development_eval_tasks.json")
    eval_refs = load("benchmark/phase3c_dev1/a_development_eval_references.json")
    analysis = load("research/artifacts/phase3c-dev1/raw/analysis.json")
    structural = load("research/results/PHASE_3C_DEV1/structural_audit.json")
    records = {}
    for seed in SEEDS:
        for condition in ("dense", "diverse"):
            rel = f"research/artifacts/phase3c-dev1/raw/evaluations/{seed}/{condition}_development.json"
            records[condition, seed] = load(rel)["records"]
    # All observed task IDs, references, conditions and seed counts must agree.
    assert len(tasks) == len(eval_refs) == 36
    assert {t["task_id"] for t in tasks} == set(eval_refs)
    assert all(len(v) == 36 for v in records.values())
    assert all({x["task_id"] for x in v} == set(eval_refs) for v in records.values())
    assert {x["archetype"] for x in tasks} | {x["archetype"] for v in training.values() for x in v} == set(SPEC)
    assert len(training["dense"]) == len(training["diverse"]) == 60
    assert all(x["target"] == train_refs[c][x["example_id"]] for c in training for x in training[c])
    # Ground the manual inventory in the actual references and prompts.
    for c in training:
        for x in training[c]:
            s = record_spec(x["archetype"])
            assert s["subskill"] == x["family"]
            assert x["prompt"] and x["target"]
            for api in s["goco_api"]:
                assert api in x["target"]
    for x in tasks:
        s = record_spec(x["archetype"])
        assert s["subskill"] == x["family"] and x["prompt"] and eval_refs[x["task_id"]]
        for api in s["goco_api"]:
            assert api in eval_refs[x["task_id"]]

    train_arch = {c: sorted({x["archetype"] for x in training[c]}) for c in training}
    coverage = {c: sorted({p for a in train_arch[c] for p in SPEC[a][3]}) for c in training}
    sim = {x["task_id"]: x for x in analysis["nearest_training_similarity_by_task"]}
    assert len(sim) == 36
    inventory = {"source_hashes": files, "training": {}, "development": {}, "primitive_vocabulary": sorted(SIGNATURES),
                 "interpretation": "Essential primitives are manually curated from frozen prompt/reference behavior; output-token signatures are separate weak observations."}
    for c in training:
        inventory["training"][c] = [dict(record_spec(a), example_ids=[x["example_id"] for x in training[c] if x["archetype"] == a],
                                           representative_prompt=next(x["prompt"] for x in training[c] if x["archetype"] == a),
                                           representative_reference=train_refs[c][next(x["example_id"] for x in training[c] if x["archetype"] == a)]) for a in train_arch[c]]
    inventory["training_coverage"] = coverage
    for a in dict.fromkeys(x["archetype"] for x in tasks):
        inventory["development"][a] = dict(record_spec(a), task_ids=[x["task_id"] for x in tasks if x["archetype"] == a],
                                            representative_prompt=next(x["prompt"] for x in tasks if x["archetype"] == a),
                                            representative_reference=eval_refs[next(x["task_id"] for x in tasks if x["archetype"] == a)])

    matrix = []
    for task in tasks:
        a, tid = task["archetype"], task["task_id"]
        row = {"task_id": tid, "archetype": a, "subskill": task["family"], "distance_group": task["distance_group"],
               "required_primitives": SPEC[a][3], "control_flow": SPEC[a][1], "data_structure": SPEC[a][2], "conditions": {}}
        for c in training:
            present = {p: p in coverage[c] for p in SPEC[a][3]}
            missing = [p for p, yes in present.items() if not yes]
            analogue = {"fourth_square_step": "fourth_square", "negative_tally_unrolled": "negative_tally"}.get(a)
            if analogue not in train_arch[c]:
                analogue = None
            labels = []
            if missing:
                labels.append("MISSING_PRIMITIVE")
            elif not analogue:
                labels.append("KNOWN_PRIMITIVES_NOVEL_COMPOSITION")
            if a in ("square_threshold_crossing", "positive_run_length", "range_neighbor_mix", "negative_tally_unrolled", "fourth_square_step"):
                labels.append("NEW_CONTROL_OR_DATA_STRUCTURE")
            if analogue:
                labels.append("NEAR_STRUCTURAL_ANALOGUE")
            row["conditions"][c] = {"primitive_present_in_training": present, "missing_primitives": missing,
                                     "semantic_combination_present": bool(analogue), "exact_control_flow_present": False,
                                     "direct_structural_analogue": analogue,
                                     "novelty_labels": labels, "frozen_nearest_training": sim[tid][c],
                                     "observed_by_seed": {str(seed): next(x for x in records[c, seed] if x["task_id"] == tid)["failure_category"] for seed in SEEDS}}
        matrix.append(row)

    all_rows = []
    stages = Counter()
    for c in training:
        for seed in SEEDS:
            for x in records[c, seed]:
                stages[(c, x["distance_group"], x["family"], x["archetype"], x["failure_category"])] += 1
                if x["distance_group"] == "near":
                    continue
                source = x["normalized_output"]
                detected = sorted(p for p, pattern in SIGNATURES.items() if re.search(pattern, source, re.I))
                required = SPEC[x["archetype"]][3]
                extras = sorted(k for k, pattern in EXTRA_SURFACES.items() if re.search(pattern, source, re.I))
                visible_sources = sorted({SOURCE_MOTIFS[p] for p in detected if p in SOURCE_MOTIFS and SOURCE_MOTIFS[p] in train_arch[c]})
                if x["archetype"] == "range_neighbor_mix":
                    for label, pattern in {"extra_whole_array_sum": r"total\s*\+=\s*values\s*\[\s*i\s*\]", "wraparound_product": r"values\s*\[\s*3\s*\]\s*\*\s*values\s*\[\s*0\s*\]", "range_added_per_neighbor": r"\+=\s*values\s*\[[^]]+\]\s*\*\s*values\s*\[[^]]+\]\s*\+\s*range"}.items():
                        if re.search(pattern, source, re.I): extras.append(label)
                if x["archetype"] == "nontriple_divisor_mix" and re.search(r"i\s*\*\s*i\s*<=\s*n", source, re.I):
                    extras.append("sqrt_divisor_loop_requires_pair_accounting")
                if x["archetype"] == "positive_run_length" and re.search(r"(?:current|count|longest)\s*=\s*1", source, re.I):
                    extras.append("run_counter_initialized_or_reset_to_one")
                case_phases = Counter(y["phase"] for y in x["case_results"])
                all_rows.append({"condition": c, "seed": seed, "task_id": x["task_id"], "archetype": x["archetype"],
                                 "subskill": x["family"], "distance_group": x["distance_group"],
                                 "parse_success": x["parse_success"], "compile_success": x["compile_success"],
                                 "execution_success": x["execution_success"], "hidden_semantic_pass": x["hidden_pass"],
                                 "failure_category": x["failure_category"], "error_phase": x["error_phase"],
                                 "cases_passed": x["cases_passed"], "cases_total": x["cases_total"],
                                 "case_phase_counts": dict(case_phases), "first_case_stderr": x["case_results"][0]["stderr"],
                                 "generated_code": source, "generated_surface_signatures": detected,
                                 "required_signatures_not_detected": sorted(set(required)-set(detected)),
                                 "unexpected_surface_signals": extras,
                                 "visible_training_archetype_motifs": visible_sources,
                                 "frozen_nearest_training_reference": sim[x["task_id"]][c]["nearest_code_id"],
                                 "frozen_nearest_training_code_similarity": sim[x["task_id"]][c]["nearest_code_similarity"],
                                 "scaffold_observation": ("Visible motifs from separately trained archetypes, plus common GOCO scaffold" if len(visible_sources)>1 else "Visible motif from one trained archetype, plus common GOCO scaffold" if visible_sources else "Generic GOCO scaffold visible" if "INPUT(" in source and "LOOP" in source and "DISPLAYNL(" in source else "Full input/loop/output scaffold not visible")})
    assert len(all_rows) == 144 and all(not x["hidden_semantic_pass"] for x in all_rows)
    assert sum(v for k,v in stages.items() if k[0]=="dense" and k[-1]=="syntax") == 67
    assert sum(v for k,v in stages.items() if k[0]=="dense" and k[-1]=="semantic") == 11
    assert sum(v for k,v in stages.items() if k[0]=="dense" and k[-1]=="hidden_test_semantic") == 12
    assert sum(v for k,v in stages.items() if k[0]=="diverse" and k[-1]=="syntax") == 29
    assert sum(v for k,v in stages.items() if k[0]=="diverse" and k[-1]=="semantic") == 17
    assert sum(v for k,v in stages.items() if k[0]=="diverse" and k[-1]=="hidden_test_semantic") == 26
    assert structural  # frozen structural audit was loaded and hashed, not recomputed
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = {"operation_inventory.json": inventory, "coverage_matrix.json": matrix,
               "failure_audit.json": {"scope": "144 frozen COMPOSITIONAL/FAR seed-task-condition failures", "rows": all_rows,
                                      "surface_signature_caveat": "Regex-visible tokens are neither verified semantic operations nor proof of copying. Nearest similarities compare frozen evaluation references with frozen training references, not generated code."},
               "failure_stages.json": [{"condition": k[0], "distance_group": k[1], "subskill": k[2], "archetype": k[3], "failure_category": k[4], "count": v} for k,v in sorted(stages.items())]}
    for name, value in outputs.items():
        (OUT/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print("Wrote", ", ".join(outputs), "; audited", len(all_rows), "saved failures")


if __name__ == "__main__":
    main()
