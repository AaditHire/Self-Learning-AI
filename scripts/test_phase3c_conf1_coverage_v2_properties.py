"""Synthetic metamorphic checks derived from the frozen coverage v2 rule."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

from phase3c_conf1_coverage_v2 import audit_bundle, canonical_expr, compiler

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "research/protocols/phase3c_conf1_coverage_v2_synthetic_fixtures.json"
OUT = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE/coverage_v2_properties.json"


def c(value: int) -> dict:
    return {"op": "const", "value": value}


def v(name: str) -> dict:
    return {"op": "var", "name": name}


def b(op: str, a: dict, d: dict) -> dict:
    return {"op": op, "args": [a, d]}


def rename_source(source: str) -> str:
    mapping = {"n": "limit", "i": "position", "total": "accumulator",
               "hitP": "firstFlag", "hitQ": "secondFlag", "hitR": "thirdFlag"}
    return re.sub(r"\b(?:n|i|total|hitP|hitQ|hitR)\b",
                  lambda match: mapping[match.group()], source)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    fixture_rows = json.loads(FIXTURES.read_text(encoding="utf-8"))["fixtures"]
    by_name = {row["name"]: row for row in fixture_rows}
    algebraic = 0
    for value in range(-25, 25):
        assert canonical_expr(c(value)) == canonical_expr(b("sub", c(value + 1), c(1)))
        assert canonical_expr(b("add", v("i"), c(value))) == canonical_expr(
            b("add", c(value), v("i")))
        assert canonical_expr(b("gt", v("i"), c(value))) == canonical_expr(
            b("lt", c(value), v("i")))
        algebraic += 3
    engine = compiler()
    bundle_checks = []

    def check(name: str, bundle: dict, expected: str, required: str | None = None) -> None:
        audit = audit_bundle(bundle, engine)
        passed = audit["status"] == expected and (required is None or
                 any(required in failure for failure in audit["failures"]))
        bundle_checks.append({"name": name, "expected": expected, "observed": audit["status"],
                              "required_failure": required, "pass": passed})
        if not passed:
            raise AssertionError(f"property failed: {name}: {audit['failures'][:5]}")

    base = copy.deepcopy(by_name["equivalent_comparison_operands"]["bundle"])
    renamed = copy.deepcopy(base)
    for group in renamed.values():
        for record in group:
            record["source"] = rename_source(record["source"])
    check("alpha_renaming_preserves_coverage", renamed, "PASS")

    dead = copy.deepcopy(base)
    for group in dead.values():
        for record in group:
            record["source"] = record["source"].replace(" LOOP (", " IF (0==1) { total+=999. } LOOP (")
    check("constant_false_branch_does_not_create_capability", dead, "PASS")

    api_removed = copy.deepcopy(base)
    api_removed["evaluation"][0]["source"] = api_removed["evaluation"][0]["source"].replace(
        "INPUT(n).", "n=0.", 1)
    check("required_input_api_removed", api_removed, "FAIL", "API_INPUT_MISSING")

    branch_absent = copy.deepcopy(by_name["dead_if_does_not_cover_independent_checks"]["bundle"])
    check("dead_if_not_independent_checks", branch_absent, "FAIL",
          "MULTIPLE_INDEPENDENT_PREDICATE_CHECKS")

    negative = copy.deepcopy(by_name["computed_negative_one_equivalence"]["bundle"])
    for condition in ("isolated", "composition"):
        for record in negative[condition]:
            record["aggregation"]["initial"] = c(0)
            record["source"] = record["source"].replace("NUMBER total=(0-1).", "NUMBER total=0.")
            for case in record["cases"]:
                case["expected_stdout"] = str(int(case["expected_stdout"]) + 1)
            values = [int(case["expected_stdout"]) for case in record["cases"]]
            record["output_domain"]["required_categories"] = sorted(
                {"ZERO" if x == 0 else "POSITIVE" for x in values})
    check("negative_output_capability_removed", negative, "FAIL", "OUTPUT_NEGATIVE")

    local = copy.deepcopy(by_name["local_pair_motifs_without_full_graph"]["bundle"])
    check("local_pair_motif_permitted", local, "PASS")
    full = copy.deepcopy(local)
    cloned = copy.deepcopy(full["composition"][0])
    del cloned["condition"]
    cloned["id"] = "SYNTHETIC_PRIMARY_CLONE"
    cloned["task_kind"] = "primary"
    full["evaluation"] = [cloned]
    check("full_signature_inserted", full, "FAIL", "PROHIBITED_FULL_SIGNATURE")

    report = {"status": "PASS", "algebraic_equivalence_checks": algebraic,
              "audited_bundle_properties": len(bundle_checks), "bundle_results": bundle_checks,
              "no_model_execution": True}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
