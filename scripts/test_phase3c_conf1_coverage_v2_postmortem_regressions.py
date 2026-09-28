"""Regression only: A/B labels, consumed C rule-derived labels and prior properties."""

from __future__ import annotations

import json
from pathlib import Path

from phase3c_conf1_coverage_v2 import _full_signature, audit_bundle, compiler
import test_phase3c_conf1_coverage_v2_properties as prior

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "research/protocols"
RESULTS = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE"
OUT = RESULTS / "coverage_v2_postmortem_regressions.json"
PROPERTY_OUT = RESULTS / "coverage_v2_postmortem_prior_properties.json"
POSTMORTEM = RESULTS / "coverage_v2_suite_c_postmortem_matrix.json"


def observed(fixture: dict, engine) -> tuple[str, list[str]]:
    if fixture.get("kind") == "signature_pair":
        return ("SAME" if _full_signature(fixture["left"]) ==
                _full_signature(fixture["right"]) else "DIFFERENT"), []
    result = audit_bundle(fixture["bundle"], engine)
    return result["status"], result["failures"]


def main() -> None:
    if OUT.exists() or PROPERTY_OUT.exists():
        raise FileExistsError("postmortem regression result already exists")
    engine = compiler()
    rows = []
    specs = (
        ("A", PROTOCOL / "phase3c_conf1_coverage_v2_synthetic_fixtures.json"),
        ("B", PROTOCOL / "phase3c_conf1_coverage_v2_suite_b.json"),
        ("C_CONSUMED_REGRESSION", PROTOCOL / "phase3c_conf1_coverage_v2_suite_c.json"),
    )
    derived = {row["fixture_id"]: row for row in
               json.loads(POSTMORTEM.read_text(encoding="utf-8"))["rows"]}
    for suite, path in specs:
        fixtures = json.loads(path.read_text(encoding="utf-8"))["fixtures"]
        for fixture in fixtures:
            try:
                label, reasons = observed(fixture, engine)
            except Exception as exc:
                label, reasons = "ERROR", [f"{type(exc).__name__}:{exc}"]
            if suite == "C_CONSUMED_REGRESSION":
                normative = derived[fixture["name"]]["rule_derived"]
                expected = normative.split(" with ")[0]
                required = ("PROHIBITED_FULL_SIGNATURE:composition" if
                            fixture["name"] == "withheld_full_signature_reuse" else
                            fixture.get("required_failure_substring") if
                            fixture["name"] in {"array_dead_fourth_value",
                                                   "unproved_extra_branch",
                                                   "literal_vs_computed_minus_two"} else None)
            else:
                expected = fixture["expected"]
                required = fixture.get("required_failure_substring")
            passed = label == expected and (required is None or
                                            any(required in reason for reason in reasons))
            rows.append({"suite": suite, "id": fixture["name"], "expected": expected,
                         "observed": label, "required_reason": required,
                         "required_reason_present": required is None or
                         any(required in reason for reason in reasons),
                         "pass": passed, "reasons": reasons})
            print(f"{suite}:{fixture['name']}: {'PASS' if passed else 'MISMATCH'}", flush=True)
    property_result = {"status": "NOT_RUN"}
    if all(row["pass"] for row in rows):
        prior.OUT = PROPERTY_OUT
        try:
            prior.main()
            property_result = json.loads(PROPERTY_OUT.read_text(encoding="utf-8"))
        except Exception as exc:
            property_result = {"status": "FAIL", "error": f"{type(exc).__name__}:{exc}"}
    report = {"status": "PASS" if all(row["pass"] for row in rows) and
              property_result["status"] == "PASS" else "STOP_COVERAGE_V2_REGRESSION_FAILED",
              "counts": {suite: {"total": sum(x["suite"] == suite for x in rows),
                                 "passed": sum(x["suite"] == suite and x["pass"] for x in rows)}
                         for suite, _ in specs},
              "prior_property_result": property_result,
              "rows": rows, "suite_c_role": "CONSUMED_REGRESSION_ONLY", "no_model_execution": True}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "counts": report["counts"],
                      "prior_properties": property_result["status"]}, indent=2))
    if report["status"] != "PASS":
        raise AssertionError(report["status"])


if __name__ == "__main__": main()
