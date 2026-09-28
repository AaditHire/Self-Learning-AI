"""Run immutable Suite A/B labels and prior property tests after the repair."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from phase3c_conf1_coverage_v2 import _full_signature, audit_bundle, compiler
import test_phase3c_conf1_coverage_v2_properties as old_properties

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "research/protocols"
RESULTS = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE"
OUT = RESULTS / "coverage_v2_repaired_regressions.json"
PROPERTY_OUT = RESULTS / "coverage_v2_repaired_prior_properties.json"


def main() -> None:
    if OUT.exists() or PROPERTY_OUT.exists():
        raise FileExistsError("repaired regression result already exists")
    engine = compiler()
    rows = []
    for suite, filename in (("A", "phase3c_conf1_coverage_v2_synthetic_fixtures.json"),
                            ("B", "phase3c_conf1_coverage_v2_suite_b.json")):
        fixtures = json.loads((PROTOCOL / filename).read_text(encoding="utf-8"))["fixtures"]
        for fixture in fixtures:
            try:
                if fixture.get("kind") == "signature_pair":
                    observed = ("SAME" if _full_signature(fixture["left"]) ==
                                _full_signature(fixture["right"]) else "DIFFERENT")
                    failures = []
                else:
                    audit = audit_bundle(fixture["bundle"], engine)
                    observed = audit["status"]
                    failures = audit["failures"]
            except Exception as exc:
                observed = "ERROR"
                failures = [f"{type(exc).__name__}:{exc}"]
            needed = fixture.get("required_failure_substring")
            success = observed == fixture["expected"] and (
                needed is None or any(needed in f for f in failures))
            rows.append({"suite": suite, "name": fixture["name"], "expected": fixture["expected"],
                         "observed": observed, "pass": success, "required_failure": needed,
                         "failures": failures})
            print(f"Suite {suite}: {fixture['name']}: {observed}: {'PASS' if success else 'MISMATCH'}",
                  flush=True)
    properties = {"status": "NOT_RUN"}
    if all(row["pass"] for row in rows):
        old_properties.OUT = PROPERTY_OUT
        try:
            old_properties.main()
            properties = json.loads(PROPERTY_OUT.read_text(encoding="utf-8"))
        except Exception as exc:
            properties = {"status": "FAIL", "error": f"{type(exc).__name__}:{exc}"}
    tally = Counter((row["suite"], row["pass"]) for row in rows)
    report = {"status": "PASS" if all(row["pass"] for row in rows) and
              properties["status"] == "PASS" else "STOP_COVERAGE_V2_REGRESSION_FAILED",
              "suite_a": {"total": sum(x["suite"] == "A" for x in rows),
                          "passed": tally[("A", True)]},
              "suite_b": {"total": sum(x["suite"] == "B" for x in rows),
                          "passed": tally[("B", True)]},
              "prior_properties": {"status": properties["status"],
                                   "algebraic": properties.get("algebraic_equivalence_checks"),
                                   "bundles": properties.get("audited_bundle_properties"),
                                   "error": properties.get("error")},
              "rows": rows, "no_model_execution": True}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in
                      ("status", "suite_a", "suite_b", "prior_properties")}, indent=2))
    if report["status"] != "PASS":
        raise AssertionError("STOP_COVERAGE_V2_REGRESSION_FAILED")


if __name__ == "__main__":
    main()
