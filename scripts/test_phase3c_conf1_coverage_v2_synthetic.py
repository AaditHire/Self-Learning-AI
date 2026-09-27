"""One-pass synthetic coverage validation using frozen labels and pinned GOCO."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from phase3c_conf1_coverage_v2 import CoverageError, audit_bundle, compiler

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "research/protocols/phase3c_conf1_coverage_v2_synthetic_fixtures.json"
OUT = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE/coverage_v2_synthetic_validation.json"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))["fixtures"]
    engine = compiler()
    results = []
    confusion: Counter[tuple[str, str]] = Counter()
    category_counts: Counter[str] = Counter()
    for fixture in fixtures:
        category_counts[fixture["focus_category"]] += 1
        try:
            audit = audit_bundle(fixture["bundle"], engine)
            observed = audit["status"]
            failures = audit["failures"]
        except Exception as exc:
            observed = "ERROR"
            failures = [f"{type(exc).__name__}:{exc}"]
            audit = None
        expected = fixture["expected"]
        needed = fixture.get("required_failure_substring")
        passed = observed == expected and (needed is None or any(needed in x for x in failures))
        confusion[(expected, observed)] += 1
        results.append({"name": fixture["name"], "focus_category": fixture["focus_category"],
                        "expected": expected, "observed": observed, "pass": passed,
                        "required_failure_substring": needed, "failures": failures,
                        "audit": audit})
        print(f"{fixture['name']}: {observed} {'PASS' if passed else 'MISMATCH'}", flush=True)
    report = {"status": "PASS" if all(x["pass"] for x in results) else
              "STOP_COVERAGE_V2_VALIDATION_FAILED",
              "fixture_count": len(results), "passed": sum(x["pass"] for x in results),
              "focus_category_counts": dict(sorted(category_counts.items())),
              "confusion": [{"expected": e, "observed": o, "count": n}
                            for (e, o), n in sorted(confusion.items())],
              "results": results, "no_model_execution": True}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "fixture_count", "passed",
                                                "focus_category_counts", "confusion")}, indent=2))
    if report["status"] != "PASS":
        raise AssertionError("STOP_COVERAGE_V2_VALIDATION_FAILED")


if __name__ == "__main__":
    main()
