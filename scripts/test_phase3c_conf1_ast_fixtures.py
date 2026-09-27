"""Execute frozen synthetic fixture labels, with no model access."""

from __future__ import annotations

import json
from pathlib import Path

from build_phase2b_data import ast_proxy
from phase3c_conf1_structural_overlap import adjudicate

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "research/protocols/phase3c_conf1_ast_fixtures.json"


def main() -> None:
    rows = json.loads(FIXTURES.read_text(encoding="utf-8"))
    tested = 0
    for group in ("positive_controls", "negative_controls"):
        for row in rows[group]:
            coarse = ast_proxy(row["left"]) == ast_proxy(row["right"])
            if row.get("require_coarse_equal") and not coarse:
                raise AssertionError(f"STOP_CONF1_AST_ADJUDICATION_FAILED: {row['name']} lacks coarse equality")
            observed = adjudicate(row["left"], row["right"], coarse)
            if observed != row["expected"]:
                raise AssertionError(f"STOP_CONF1_AST_ADJUDICATION_FAILED: {row['name']}: {observed}")
            tested += 1
    print(json.dumps({"synthetic_fixtures_passed": tested, "positive": len(rows["positive_controls"]),
                      "negative": len(rows["negative_controls"]), "status": "PASS"}))


if __name__ == "__main__":
    main()
