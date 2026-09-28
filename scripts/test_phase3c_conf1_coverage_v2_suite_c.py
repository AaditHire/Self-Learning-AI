"""One-pass independent Suite C validation against precommitted labels."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from phase3c_conf1_coverage_v2 import _full_signature, audit_bundle, compiler

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "research/protocols/phase3c_conf1_coverage_v2_suite_c.json"
OUT = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE/coverage_v2_suite_c_validation.json"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))["fixtures"]
    engine = compiler()
    rows = []
    confusion = Counter()
    for fixture in fixtures:
        try:
            if fixture["kind"] == "signature_pair":
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
        expected = fixture["expected"]
        required = fixture.get("required_failure_substring")
        correct = (observed == expected and
                   (required is None or any(required in failure for failure in failures)))
        confusion[(expected, observed)] += 1
        rows.append({"name": fixture["name"], "focus_category": fixture["focus_category"],
                     "expected": expected, "observed": observed, "pass": correct,
                     "required_failure": required, "failures": failures})
        print(f"{fixture['name']}: {expected} -> {observed}: {'PASS' if correct else 'MISMATCH'}",
              flush=True)
    report = {"status": "PASS" if all(row["pass"] for row in rows) else
              "STOP_COVERAGE_V2_INDEPENDENT_VALIDATION_FAILED",
              "fixture_count": len(rows), "passed": sum(row["pass"] for row in rows),
              "focus_counts": dict(sorted(Counter(row["focus_category"] for row in rows).items())),
              "class_counts": dict(sorted(Counter(row["expected"] for row in rows).items())),
              "confusion": [{"expected": a, "observed": b, "count": n}
                            for (a, b), n in sorted(confusion.items())],
              "rows": rows, "no_model_execution": True}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "fixture_count", "passed",
                                                "focus_counts", "class_counts", "confusion")},
                     indent=2))
    if report["status"] != "PASS":
        raise AssertionError("STOP_COVERAGE_V2_INDEPENDENT_VALIDATION_FAILED")


if __name__ == "__main__":
    main()
