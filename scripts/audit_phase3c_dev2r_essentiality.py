"""Test reference-only versus task-essential constructs without model use."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.benchmark import score_source
from self_learning_ai.compiler import GocoCompiler
from audit_phase3c_dev2r_api_coverage import CONSTRUCTS
from build_phase3c_dev2_data import PREDICATES, prefix

OUT = ROOT / "research/results/PHASE_3C_DEV2R_ESSENTIALITY/essentiality_audit.json"
FROZEN_DESIGN = "cdff638153df13c5da2d77b4eda908385c1a6423"
STOP_AUDIT = "c5d26366345cb228c3bafb7c64d51ec58d39ca95"


def read(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha(rel: str):
    digest = hashlib.sha256()
    with (ROOT / rel).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def alternative(task: dict) -> str:
    family = task["family"]
    a, b = task["semantic_primitives"]
    A, B = PREDICATES[family][a][0], PREDICATES[family][b][0]
    signature = task["composition_signature"]
    match = re.fullmatch(r"(suffix_after_first|prefix_through_last)\((\w+),(\w+)\)\+(\d+)", signature)
    if not match or (match.group(2), match.group(3)) != (a, b):
        raise ValueError(f"Unrecognized frozen Structural Transfer signature: {task['task_id']}")
    kind, k = match.group(1), int(match.group(4))
    numeric = family == "numeric_iteration"
    if kind == "suffix_after_first":
        # Test Q before setting seen from P, so the first P index is excluded.
        body = f"IF (seen>=1) {{ IF ({B}) {{ count+=1. }} }} IF ({A}) {{ seen+=1. }}"
        loop = (f"LOOP (NUMBER i=1 TILL i<=n, i++) {{ {body} }}" if numeric
                else f"LOOP (NUMBER i=0 TILL i<4, i++) {{ {body} }}")
    else:
        # First P encountered in reverse is the last P in forward order.
        # Test Q after setting seen, so that anchor position is included.
        body = f"IF ({A}) {{ seen+=1. }} IF (seen>=1) {{ IF ({B}) {{ count+=1. }} }}"
        loop = (f"NUMBER i=n.\nLOOP (i>=1) {{ {body} i-=1. }}" if numeric
                else f"NUMBER i=3.\nLOOP (i>=0) {{ {body} i-=1. }}")
    return prefix(family) + f"NUMBER seen=0.\nNUMBER count={k}.\n" + loop + "\nDISPLAYNL(count)."


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    manifest = read("research/protocols/phase3c_dev2r_manifest.json")
    task_rel = "benchmark/phase3c_dev2r/a_development_eval_tasks.json"
    ref_rel = "benchmark/phase3c_dev2r/a_development_eval_references.json"
    cases_rel = "benchmark/phase3c_dev2r/a_development_eval_hidden_tests.json"
    tasks, refs, cases = read(task_rel), read(ref_rel), read(cases_rel)
    original_audit = read("research/results/PHASE_3C_DEV2R_PREEXEC_STOP/api_construct_coverage.json")
    config = read("research/protocols/phase3c_dev2_config.json")
    inputs = [task_rel, ref_rel, cases_rel]
    for condition in ("isolated", "composition"):
        inputs.extend((f"data/phase3c_dev2/a_{condition}_training_examples.json",
                       f"data/phase3c_dev2/a_{condition}_training_references.json"))
    if any(sha(rel) != manifest["input_sha256"][rel] for rel in inputs):
        raise ValueError("Frozen scientific input hash mismatch")
    if sha(config["compiler"]["path"]) != config["compiler"]["sha256"]:
        raise ValueError("Pinned compiler hash mismatch")
    if original_audit["status"] != "STOP_PREEXECUTION_CONSTRUCT_COVERAGE":
        raise ValueError("Pre-execution STOP audit identity mismatch")
    by_id = {row["task_id"]: row for row in original_audit["tasks"]}
    training = {}
    for condition in ("isolated", "composition"):
        examples = read(f"data/phase3c_dev2/a_{condition}_training_examples.json")
        training[condition] = {
            "rows": examples,
            "refs": read(f"data/phase3c_dev2/a_{condition}_training_references.json"),
            "row_by_id": {row["example_id"]: row for row in examples},
        }
    compiler = GocoCompiler(ROOT / config["compiler"]["java"],
                            ROOT / config["compiler"]["path"],
                            timeout_seconds=config["evaluation"]["compiler_timeout_seconds"],
                            output_limit_bytes=config["evaluation"]["output_limit_bytes_per_stream"])
    results = []
    for task in tasks:
        if task["development_group"] != "structural_transfer":
            continue
        tid = task["task_id"]
        reference = refs[tid]
        source = alternative(task)
        reference_constructs = {name for name, pattern in CONSTRUCTS.items() if re.search(pattern, reference)}
        alternative_constructs = {name for name, pattern in CONSTRUCTS.items() if re.search(pattern, source)}
        if source == reference or "negative_integer_literal" in alternative_constructs:
            raise ValueError(f"Diagnostic is not a distinct sentinel-free alternative: {tid}")
        if any(by_id[tid]["conditions"][condition]["missing_constructs"] != ["negative_integer_literal"]
               for condition in ("isolated", "composition")):
            raise ValueError(f"Prior reference-only gap differs from expected: {tid}")
        missing_by_condition = {}
        primitive_by_condition = {}
        covered_evidence = {}
        for condition, tr in training.items():
            same_family = {eid: code for eid, code in tr["refs"].items()
                           if tr["row_by_id"][eid]["family"] == task["family"]}
            present = {name for name, pattern in CONSTRUCTS.items()
                       if any(re.search(pattern, code) for code in same_family.values())}
            missing_by_condition[condition] = sorted(alternative_constructs - present)
            primitive_pool = {p for row in tr["rows"] if row["family"] == task["family"]
                              for p in row["semantic_primitives"]}
            primitive_by_condition[condition] = sorted(set(task["semantic_primitives"]) - primitive_pool)
            covered_evidence[condition] = {
                "same_family_training_examples": len(same_family),
                "alternative_constructs_covered": not missing_by_condition[condition],
                "essential_primitives_covered": not primitive_by_condition[condition],
            }
        score = score_source(compiler, {**task, "difficulty": "diagnostic_reference_only"},
                             cases[tid], source).as_dict()
        pass_all = bool(score["hidden_pass"] and score["cases_passed"] == 5)
        covered = not any(missing_by_condition.values()) and not any(primitive_by_condition.values())
        classification = "REFERENCE_ONLY" if pass_all and covered else "AMBIGUOUS"
        result = {
            "task_id": tid, "family": task["family"], "archetype": task["archetype"],
            "task_prompt": task["prompt"], "composition_signature": task["composition_signature"],
            "frozen_reference_constructs": sorted(reference_constructs),
            "frozen_reference_uses_negative_integer_literal": "negative_integer_literal" in reference_constructs,
            "frozen_reference_minus_one_role": "absent-anchor sentinel; initialized to -1, replaced by a nonnegative matching index when an anchor exists, and tested with anchor>=0 before counting",
            "task_specification_requires_negative_literal_output": False,
            "task_specification_negative_value_behavior": (
                "Array input may contain negative values. Predicate negative_value compares an entry with 0; large_magnitude squares entries. Both primitives occur in both original same-family training conditions."
                if task["family"] == "array_reduction" else
                "Numeric input n is nonnegative; all indices and offset counts are nonnegative."),
            "negative_literal_syntax": "present in frozen reference only; diagnostic alternative uses no unary-negative literal",
            "unary_negation_operator": "The frozen spelling -1 may be parsed as a signed literal or unary minus; this audit does not assume which. The diagnostic alternative uses neither a negative literal nor unary negation.",
            "negative_value_comparison": "present only when the frozen predicate is negative_value; coverage is verified through same-family primitive and construct evidence",
            "negative_value_arithmetic": "present only through large_magnitude squaring of possibly negative array inputs; covered by same-family training primitive/reference evidence",
            "diagnostic_alternative_source": source,
            "diagnostic_alternative_constructs": sorted(alternative_constructs),
            "diagnostic_alternative_semantic_primitives": task["semantic_primitives"],
            "alternative_missing_constructs": missing_by_condition,
            "alternative_missing_primitives": primitive_by_condition,
            "same_family_coverage": covered_evidence,
            "diagnostic_cases_passed": score["cases_passed"],
            "diagnostic_cases_total": score["cases_total"],
            "diagnostic_hidden_pass": score["hidden_pass"],
            "diagnostic_case_results": score["case_results"],
            "reference_only_construct_gaps": {
                condition: by_id[tid]["conditions"][condition]["missing_constructs"]
                for condition in training},
            "task_essential_construct_gaps": missing_by_condition,
            "classification": classification,
            "justification": "A separate covered-construct program passes all five unchanged semantic cases without a negative literal; it uses a nonnegative seen count rather than an absent-anchor sentinel. This proves the missing literal is unnecessary for the frozen five-case task, not that any model can implement the alternative."
                             if classification == "REFERENCE_ONLY" else
                             "No all-case covered-construct alternative was established; task essentiality remains unresolved.",
        }
        results.append(result)
    if len(results) != 16:
        raise ValueError("Expected exactly 16 Structural Transfer tasks")
    coverage = sum(row["classification"] == "REFERENCE_ONLY" for row in results)
    output = {
        "phase": "3C-DEV2R", "status": "ESSENTIALITY_AUDIT_FOR_INDEPENDENT_REVIEW",
        "original_design_commit": FROZEN_DESIGN, "prior_stop_commit": STOP_AUDIT,
        "scientific_input_sha256": {rel: sha(rel) for rel in inputs},
        "compiler_sha256": sha(config["compiler"]["path"]),
        "model_inference_performed": False, "gradients_performed": False,
        "diagnostic_alternatives_attempted": len(results),
        "diagnostic_alternatives_passing_5_of_5": sum(row["diagnostic_hidden_pass"] for row in results),
        "task_essential_coverage": {"passed": coverage, "total": 16},
        "reference_construct_coverage": original_audit["structural_transfer"],
        "interpretation_limit": "The alternatives establish construct sufficiency for the existing frozen cases; they do not measure model ability or justify retroactive reinterpretation of the frozen gate.",
        "tasks": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"attempted": len(results), "passed_5_of_5": output["diagnostic_alternatives_passing_5_of_5"],
                      "task_essential_coverage": coverage}))


if __name__ == "__main__":
    main()
