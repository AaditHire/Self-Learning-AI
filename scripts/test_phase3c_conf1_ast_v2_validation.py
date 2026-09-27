"""One-pass validation of prospectively frozen v2 synthetic labels."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from build_phase2b_data import ast_proxy
from phase3c_conf1_structural_overlap_v2 import adjudicate_v2

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "research/protocols/phase3c_conf1_ast_v2_validation_fixtures.json"


def main() -> None:
    rows = json.loads(FIXTURES.read_text(encoding="utf-8"))["fixtures"]
    matrix: Counter[tuple[str, str]] = Counter()
    details = []
    for row in rows:
        coarse = ast_proxy(row["left"]) == ast_proxy(row["right"])
        observed = adjudicate_v2(row["left"], row["right"], coarse)
        expected = row["expected"]
        passed = observed == expected and (not row.get("require_coarse_equal") or coarse)
        matrix[(expected, observed)] += 1
        details.append({"name": row["name"], "expected": expected, "observed": observed,
                        "coarse_equal": coarse, "pass": passed})
    report = {"fixture_count": len(rows), "passed": sum(r["pass"] for r in details),
              "confusion": [{"expected": a, "observed": b, "count": n}
                            for (a, b), n in sorted(matrix.items())], "rows": details}
    print(json.dumps(report, indent=2))
    if not all(r["pass"] for r in details):
        raise AssertionError("STOP_AST_V2_INDEPENDENT_VALIDATION_FAILED")


if __name__ == "__main__":
    main()
