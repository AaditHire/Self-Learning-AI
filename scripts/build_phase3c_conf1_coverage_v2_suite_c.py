"""Construct independent validation labels without importing the auditor."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/protocols/phase3c_conf1_coverage_v2_suite_c.json"
NS = (0, 4, 8, 12, 20)


def const(n): return {"op": "const", "value": n}
def var(s): return {"op": "var", "name": s}
def pred(s): return {"op": "pred", "name": s}
def op(name, left, right): return {"op": name, "args": [left, right]}


DEFS = {
    "A": op("eq", op("mod", var("i"), const(4)), const(0)),
    "B": op("le", op("mul", const(3), var("i")), var("n")),
    "C": op("eq", op("mod", var("i"), const(5)), const(0)),
}
CHECKS = {"A": "pos%4==0", "B": "3*pos<=bound", "C": "pos%5==0"}


def hits(name, i, n):
    return {"A": i % 4 == 0, "B": 3 * i <= n, "C": i % 5 == 0}[name]


def numerical(ident, names, graph, *, condition=None, kind="training", initial=0,
              source_initial=None, extra="", alpha=False, literals=()):
    flags = ["flag" + x for x in names]
    declarations = " ".join(f"NUMBER {flag}=0." for flag in flags)
    resets = " ".join(f"{flag}=0." for flag in flags)
    branches = " ".join(f"IF ({CHECKS[name]}) {{ flag{name}=1. }}" for name in names)
    if len(names) == 2:
        relation = "+" if graph == "add" else "*"
        expression = f"score+=(flag{names[0]}{relation}flag{names[1]})."
        tree = op(graph, pred(names[0]), pred(names[1]))
        value = lambda i, n: int(hits(names[0], i, n)) + int(hits(names[1], i, n)) if graph == "add" else int(hits(names[0], i, n) and hits(names[1], i, n))
    else:
        expression = "score+=(flagA*flagB+flagA*flagC)."
        tree = op("add", op("mul", pred("A"), pred("B")),
                  op("mul", pred("A"), pred("C")))
        value = lambda i, n: int(hits("A", i, n) and hits("B", i, n)) + int(hits("A", i, n) and hits("C", i, n))
    source_initial = str(initial) if source_initial is None else source_initial
    source = (f"NUMBER bound. INPUT(bound). NUMBER score={source_initial}. {declarations} {extra} "
              f"LOOP (NUMBER pos=1 TILL pos<=bound, pos++) {{ {resets} {branches} {expression} }} "
              "DISPLAYNL(score).")
    if alpha:
        import re
        names_map = {"bound": "extent", "pos": "cursor", "score": "result"}
        source = re.sub(r"\b(?:bound|pos|score)\b", lambda m: names_map[m.group()], source)
        source = source.replace("LOOP (", "LOOP  (\n  ").replace(" TILL ", "\n  TILL ")
    outputs = [initial + sum(value(i, n) for i in range(1, n + 1)) for n in NS]
    categories = sorted({"ZERO" if n == 0 else "NEGATIVE" if n < 0 else "POSITIVE"
                         for n in outputs})
    rec = {"id": ident, "domain": "numeric_iteration",
           "predicate_definitions": {name: copy.deepcopy(DEFS[name]) for name in names},
           "aggregation": {"kind": "sum_per_item", "expr": tree,
                           "initial": (op("sub", const(0), const(-initial))
                                       if source_initial == "(0-2)" else const(initial))},
           "output_domain": {"required_categories": categories, "exact_sentinels": []},
           "literal_token_requirements": list(literals), "source": source,
           "cases": [{"case_id": f"V{j}", "stdin": str(n), "expected_stdout": str(y)}
                     for j, (n, y) in enumerate(zip(NS, outputs))], "task_kind": kind}
    if condition is not None:
        rec["condition"] = condition
    return rec


def training(initial=0, source_initial=None):
    iso = [numerical(f"C_ISO_{a}{b}", (a, b), "add", condition="isolated",
                     initial=initial, source_initial=source_initial) for a, b in (("A", "B"), ("A", "C"))]
    comp = [numerical(f"C_COMP_{a}{b}", (a, b), "mul", condition="composition",
                      initial=initial, source_initial=source_initial) for a, b in (("A", "B"), ("A", "C"))]
    return iso, comp


def array_record(ident, *, condition=None, kind="secondary", dead=False):
    source = ("IMPORT strings. SENTENCE incoming. INPUT(incoming). "
              "SENTENCE[] segments = strings.SPLIT(incoming, \"|\"). "
              "NUMBER u=strings.TO_NUMBER(segments[0]). "
              "NUMBER v=strings.TO_NUMBER(segments[1]). "
              "NUMBER w=strings.TO_NUMBER(segments[2]). "
              "NUMBER z=strings.TO_NUMBER(segments[3]). "
              f"NUMBER[] data=[u,v,w,{'0' if dead else 'z'}]. NUMBER score=0. "
              "LOOP (NUMBER pos=0 TILL pos<4, pos++) { IF (data[pos]<=-2) { score+=1. } } "
              "DISPLAYNL(score).")
    inputs = ("0|0|0|0", "-2|0|0|0", "-2|-3|0|0", "1|2|3|0",
              "0|0|0|5" if dead else "0|0|0|-2")
    outputs = (0, 1, 2, 0, 0 if dead else 1)
    rec = {"id": ident, "domain": "array_reduction",
           "predicate_definitions": {"D": op("le", var("value"), const(-2))},
           "aggregation": {"kind": "sum_per_item", "expr": pred("D"), "initial": const(0)},
           "output_domain": {"required_categories": ["ZERO", "POSITIVE"],
                             "exact_sentinels": []},
           "literal_token_requirements": [], "source": source,
           "cases": [{"case_id": f"V{j}", "stdin": x, "expected_stdout": str(y)}
                     for j, (x, y) in enumerate(zip(inputs, outputs))], "task_kind": kind}
    if condition is not None:
        rec["condition"] = condition
    return rec


def fixture(name, focus, expected, bundle, reason=""):
    result = {"name": name, "focus_category": focus, "kind": "bundle",
              "expected": expected, "bundle": bundle}
    if reason:
        result["required_failure_substring"] = reason
    return result


def main():
    if OUT.exists(): raise FileExistsError(OUT)
    iso, comp = training()
    fixtures = []
    array_iso = [array_record("C_ARRAY_ISO", condition="isolated", kind="training")]
    array_comp = [array_record("C_ARRAY_COMP", condition="composition", kind="training")]
    fixtures.append(fixture("array_live_new_predicate", "ARRAY_ACTIVITY", "PASS",
                            {"isolated": array_iso, "composition": array_comp,
                             "evaluation": [array_record("C_ARRAY_LIVE")]}))
    fixtures.append(fixture("array_dead_fourth_value", "ARRAY_ACTIVITY", "FAIL",
                            {"isolated": array_iso, "composition": array_comp,
                             "evaluation": [array_record("C_ARRAY_DEAD", dead=True)]},
                            "ARRAY_DATAFLOW_DISCONNECTED"))
    fixtures.append(fixture("numeric_loop_new_predicates", "NUMERIC_LOOP", "PASS",
                            {"isolated": iso, "composition": comp,
                             "evaluation": [numerical("C_NUMERIC_BASE", ("A", "B"), "add",
                                                      kind="secondary")]}))
    fixtures.append(fixture("numeric_loop_alpha_format", "NUMERIC_LOOP", "PASS",
                            {"isolated": iso, "composition": comp,
                             "evaluation": [numerical("C_NUMERIC_ALPHA", ("A", "B"), "add",
                                                      kind="secondary", alpha=True)]}))
    unclassified = numerical("C_EXTRA_BRANCH", ("A", "B"), "add", kind="secondary",
                             extra="IF (bound<0) { score+=7. }")
    fixtures.append(fixture("unproved_extra_branch", "UNCLASSIFIED", "FAIL",
                            {"isolated": iso, "composition": comp, "evaluation": [unclassified]},
                            "UNCLASSIFIED_REQUIREMENT"))
    neg_iso, neg_comp = training(initial=-2, source_initial="(0-2)")
    literal = numerical("C_LITERAL_SYNTAX", ("A", "B"), "mul", kind="secondary",
                        initial=-2, literals=("-2",))
    fixtures.append(fixture("literal_vs_computed_minus_two", "LITERAL_VALUE", "FAIL",
                            {"isolated": neg_iso, "composition": neg_comp,
                             "evaluation": [literal]}, "LITERAL_TOKEN:-2"))
    reference = numerical("C_UNUSED_DECL", ("A", "B"), "add", kind="secondary",
                          extra="NUMBER spare=31.")
    fixtures.append(fixture("proved_unused_declaration", "REFERENCE_ONLY", "PASS",
                            {"isolated": iso, "composition": comp,
                             "evaluation": [reference]}))
    fixtures.append(fixture("fresh_local_pair_motifs", "LOCAL_MOTIF", "PASS",
                            {"isolated": iso, "composition": comp,
                             "evaluation": [numerical("C_LOCAL", ("A", "B", "C"), "local",
                                                      kind="primary")]}))
    cloned = copy.deepcopy(comp[0]); cloned.pop("condition"); cloned["task_kind"] = "primary"
    cloned["id"] = "C_FULL_TEMPLATE"
    fixtures.append(fixture("withheld_full_signature_reuse", "FULL_SIGNATURE", "FAIL",
                            {"isolated": iso, "composition": comp,
                             "evaluation": [cloned]}, "PROHIBITED_FULL_SIGNATURE"))
    left = numerical("C_GRAPH_LEFT", ("A", "B", "C"), "local", kind="primary")
    right = copy.deepcopy(left)
    left["aggregation"]["expr"] = op("mul", op("mul", pred("A"), pred("B")), pred("C"))
    right["aggregation"]["expr"] = op("mul", pred("A"), op("mul", pred("B"), pred("C")))
    fixtures.append({"name": "multiplication_edge_rewire", "focus_category": "TYPED_GRAPH",
                     "kind": "signature_pair", "expected": "DIFFERENT", "left": left,
                     "right": right})
    alpha = copy.deepcopy(left)
    names = {"A": "X", "B": "Y", "C": "Z"}
    alpha["predicate_definitions"] = {names[k]: v for k, v in alpha["predicate_definitions"].items()}
    def rename(node):
        if node["op"] == "pred": node["name"] = names[node["name"]]
        for child in node.get("args", []): rename(child)
    rename(alpha["aggregation"]["expr"])
    fixtures.append({"name": "multiplication_graph_alpha", "focus_category": "TYPED_GRAPH",
                     "kind": "signature_pair", "expected": "SAME", "left": left,
                     "right": alpha})
    OUT.write_text(json.dumps({"version": 2, "suite": "COVERAGE_V2_VALIDATION_SUITE_C",
                               "status": "LABELS_FROZEN_BEFORE_REPAIRED_AUDITOR_RUN",
                               "fixtures": fixtures}, indent=2) + "\n", encoding="utf-8")
    print(f"frozen {len(fixtures)} independent fixtures at {OUT}")


if __name__ == "__main__": main()
