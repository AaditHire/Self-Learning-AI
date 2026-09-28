"""Freeze targeted labels before changing the coverage-v2 implementation.

This builder uses only the already frozen Suite A inputs, never an auditor result.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/protocols/phase3c_conf1_coverage_v2_synthetic_fixtures.json"
OUT = ROOT / "research/protocols/phase3c_conf1_coverage_v2_suite_b.json"


def bundle(name: str) -> dict:
    fixtures = json.loads(SOURCE.read_text(encoding="utf-8"))["fixtures"]
    return copy.deepcopy(next(item["bundle"] for item in fixtures if item["name"] == name))


def fixture(name: str, expected: str, data: dict, reason: str = "") -> dict:
    item = {"name": name, "kind": "bundle", "expected": expected, "bundle": data}
    if reason:
        item["required_failure_substring"] = reason
    return item


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    fixtures = []
    live = bundle("task_essential_array_api_absent")
    original = live["evaluation"][0]
    for condition, target in (("isolated", "isolated"), ("composition", "composition")):
        row = copy.deepcopy(original)
        row["condition"] = condition
        row["task_kind"] = "training"
        row["id"] = f"B_ARRAY_TRAIN_{condition.upper()}"
        live[target] = [row]
    fixtures.append(fixture("live_array_parser_chain", "PASS", copy.deepcopy(live)))

    dead = copy.deepcopy(live)
    row = dead["evaluation"][0]
    row["id"] = "B_ARRAY_DEAD_CONVERSION"
    row["source"] = row["source"].replace("values=[a,b,c,d]", "values=[a,b,c,c]")
    inputs = ("0|0|0|0", "-1|0|0|0", "-1|-2|0|0", "1|2|3|3", "0|0|-1|-1")
    outputs = ("0", "1", "2", "0", "2")
    for case, stdin, output in zip(row["cases"], inputs, outputs):
        case["stdin"] = stdin
        case["expected_stdout"] = output
    fixtures.append(fixture("dead_array_conversion_disconnected", "FAIL", dead,
                            "ARRAY_DATAFLOW_DISCONNECTED"))

    numeric = bundle("equivalent_comparison_operands")
    row = numeric["evaluation"][0]
    source = row["source"]
    import re
    source = re.sub(r"\bi\b", "cursor", source)
    source = re.sub(r"\bn\b", "limit", source)
    row["source"] = source.replace("LOOP (", "LOOP  (\n  ").replace(" TILL ", "\n TILL ")
    row["id"] = "B_NUMERIC_ALPHA_FORMAT"
    fixtures.append(fixture("numeric_loop_alpha_and_whitespace", "PASS", numeric))

    unclassified = bundle("equivalent_comparison_operands")
    unclassified["evaluation"][0]["source"] = "IMPORT math. " + unclassified["evaluation"][0]["source"]
    unclassified["evaluation"][0]["id"] = "B_UNCLASSIFIED_IMPORT"
    fixtures.append(fixture("unclassified_import", "FAIL", unclassified,
                            "UNCLASSIFIED_REQUIREMENT"))

    base = bundle("local_pair_motifs_without_full_graph")["evaluation"][0]
    left = copy.deepcopy(base)
    right = copy.deepcopy(base)
    p, q, r = ({"op": "pred", "name": x} for x in ("P", "Q", "R"))
    left["aggregation"]["expr"] = {"op": "add", "args": [{"op": "add", "args": [p, q]}, r]}
    right["aggregation"]["expr"] = {"op": "add", "args": [p, {"op": "add", "args": [q, r]}]}
    fixtures.append({"name": "equal_inventory_distinct_typed_topology", "kind": "signature_pair",
                     "expected": "DIFFERENT", "left": left, "right": right})

    alpha = copy.deepcopy(left)
    rename = {"P": "X", "Q": "Y", "R": "Z"}
    alpha["predicate_definitions"] = {rename[k]: v for k, v in alpha["predicate_definitions"].items()}
    def rename_expr(node: dict) -> None:
        if node["op"] == "pred":
            node["name"] = rename[node["name"]]
        for child in node.get("args", []):
            rename_expr(child)
    rename_expr(alpha["aggregation"]["expr"])
    fixtures.append({"name": "alpha_renamed_identical_graph", "kind": "signature_pair",
                     "expected": "SAME", "left": left, "right": alpha})

    OUT.write_text(json.dumps({"version": 2, "suite": "COVERAGE_V2_REGRESSION_SUITE_B",
                               "status": "LABELS_FROZEN_BEFORE_IMPLEMENTATION_REPAIR",
                               "fixtures": fixtures}, indent=2) + "\n", encoding="utf-8")
    print(f"frozen {len(fixtures)} fixtures at {OUT}")


if __name__ == "__main__":
    main()
