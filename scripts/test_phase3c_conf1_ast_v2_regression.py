"""Run the unchanged v1 development fixtures against prospective v2."""

from __future__ import annotations

import json
from pathlib import Path

from build_phase2b_data import ast_proxy
from phase3c_conf1_structural_overlap_v2 import adjudicate_v2

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "research/protocols/phase3c_conf1_ast_fixtures.json"
LEGACY_LABEL = {"NO_STRUCTURAL_TEMPLATE_REUSE": "STRUCTURALLY_DISTINCT"}


def main() -> None:
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    result = []
    for group in ("positive_controls", "negative_controls"):
        for row in fixtures[group]:
            coarse = ast_proxy(row["left"]) == ast_proxy(row["right"])
            expected = LEGACY_LABEL.get(row["expected"], row["expected"])
            observed = adjudicate_v2(row["left"], row["right"], coarse)
            passed = observed == expected and (not row.get("require_coarse_equal") or coarse)
            result.append({"name": row["name"], "expected": expected, "observed": observed,
                           "coarse_equal": coarse, "pass": passed})
    print(json.dumps({"suite": "ADJUDICATOR_DEVELOPMENT_REGRESSION_FIXTURES_V1",
                      "total": len(result), "passed": sum(r["pass"] for r in result), "rows": result}, indent=2))
    if not all(r["pass"] for r in result):
        raise AssertionError("STOP_AST_V2_REGRESSION_FAILED")


if __name__ == "__main__":
    main()
