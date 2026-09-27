"""Build labeled synthetic coverage fixtures without invoking the auditor."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/protocols/phase3c_conf1_coverage_v2_synthetic_fixtures.json"
N = (0, 2, 3, 4, 6)


def const(value: int) -> dict:
    return {"op": "const", "value": value}


def var(name: str) -> dict:
    return {"op": "var", "name": name}


def pred(name: str) -> dict:
    return {"op": "pred", "name": name}


def binary(op: str, a: dict, b: dict) -> dict:
    return {"op": op, "args": [a, b]}


P = binary("eq", binary("mod", var("i"), const(2)), const(0))
Q = binary("ge", binary("mul", const(2), var("i")), var("n"))
Q_SWAP = binary("le", var("n"), binary("mul", const(2), var("i")))
R = binary("eq", binary("mod", var("i"), const(3)), const(0))
A = binary("lt", var("value"), const(0))
DEFS = {"P": P, "Q": Q, "R": R}


def truth(name: str, i: int, n: int) -> int:
    return int({"P": i % 2 == 0, "Q": 2 * i >= n, "R": i % 3 == 0}[name])


def numeric_source(names: tuple[str, ...], expression: str, *, offset: str = "0",
                   q_swapped: bool = False, extra: str = "", prefix: bool = False) -> str:
    checks = {
        "P": "i%2==0",
        "Q": "n<=2*i" if q_swapped else "2*i>=n",
        "R": "i%3==0",
    }
    if prefix:
        return ("NUMBER n. INPUT(n). NUMBER seen=0. NUMBER total=0. "
                "LOOP (NUMBER i=1 TILL i<=n, i++) { "
                f"IF ({checks['Q']}) {{ total+=seen. }} "
                f"IF ({checks['P']}) {{ seen+=1. }} "
                "} DISPLAYNL(total).")
    declarations = " ".join(f"NUMBER hit{name}=0." for name in names)
    resets = " ".join(f"hit{name}=0." for name in names)
    branches = " ".join(f"IF ({checks[name]}) {{ hit{name}=1. }}" for name in names)
    return (f"NUMBER n. INPUT(n). NUMBER total={offset}. {declarations} {extra} "
            f"LOOP (NUMBER i=1 TILL i<=n, i++) {{ {resets} {branches} {expression} }} "
            "DISPLAYNL(total).")


def numeric_record(ident: str, names: tuple[str, ...], op: str, *, condition: str | None,
                   task_kind: str, ns: tuple[int, ...] = N, initial: dict | None = None,
                   offset: str = "0", q_swapped: bool = False, extra: str = "",
                   literal_tokens: tuple[str, ...] = ()) -> dict:
    initial = copy.deepcopy(initial if initial is not None else const(0))
    defs = {name: copy.deepcopy(Q_SWAP if name == "Q" and q_swapped else DEFS[name]) for name in names}
    if len(names) == 1:
        expr = pred(names[0])
        source_expression = f"total+=hit{names[0]}."
    else:
        expr = binary(op, pred(names[0]), pred(names[1]))
        source_expression = (f"total+=(hit{names[0]}+hit{names[1]})." if op == "add" else
                             f"total+=(hit{names[0]}*hit{names[1]})." if op == "mul" else
                             f"IF (hit{names[0]}+hit{names[1]}>0) {{ total+=1. }}")
    source = numeric_source(names, source_expression, offset=offset,
                            q_swapped=q_swapped, extra=extra)
    start = -1 if initial == const(-1) or initial == binary("sub", const(0), const(1)) else 0
    values = []
    for n in ns:
        total = start
        for i in range(1, n + 1):
            hits = [truth(name, i, n) for name in names]
            total += (hits[0] if len(hits) == 1 else
                      sum(hits) if op == "add" else
                      hits[0] * hits[1] if op == "mul" else int(any(hits)))
        values.append(total)
    categories = sorted({"ZERO" if x == 0 else "NEGATIVE" if x < 0 else "POSITIVE"
                         for x in values} | ({"MULTIDIGIT"} if any(abs(x) >= 10 for x in values) else set()))
    record = {"id": ident, "domain": "numeric_iteration", "predicate_definitions": defs,
              "aggregation": {"kind": "sum_per_item", "expr": expr, "initial": initial},
              "output_domain": {"required_categories": categories, "exact_sentinels": []},
              "literal_token_requirements": list(literal_tokens), "source": source,
              "cases": [{"case_id": f"C{j + 1}", "stdin": str(n), "expected_stdout": str(value)}
                        for j, (n, value) in enumerate(zip(ns, values))],
              "task_kind": task_kind}
    if condition is not None:
        record["condition"] = condition
    return record


def base_training(*, negative_initial: bool = False) -> tuple[list[dict], list[dict]]:
    initial = binary("sub", const(0), const(1)) if negative_initial else const(0)
    offset = "(0-1)" if negative_initial else "0"
    ns = (0, 1, 2, 4, 6) if negative_initial else N
    iso, comp = [], []
    for names in (("P", "Q"), ("P", "R")):
        tag = "".join(names)
        iso.append(numeric_record(f"ISO_{tag}", names, "add", condition="isolated",
                                  task_kind="training", ns=ns, initial=initial, offset=offset))
        comp.append(numeric_record(f"COMP_{tag}", names, "mul", condition="composition",
                                   task_kind="training", ns=ns, initial=initial, offset=offset))
    return iso, comp


def fixture(name: str, focus: str, expected: str, iso: list[dict], comp: list[dict],
            evaluation: dict, reason: str | None = None) -> dict:
    result = {"name": name, "focus_category": focus, "expected": expected,
              "bundle": {"isolated": iso, "composition": comp, "evaluation": [evaluation]}}
    if reason:
        result["required_failure_substring"] = reason
    return result


def array_api_eval() -> dict:
    source = ("IMPORT strings. SENTENCE line. INPUT(line). "
              "SENTENCE[] parts = strings.SPLIT(line, \"|\"). "
              "NUMBER a = strings.TO_NUMBER(parts[0]). "
              "NUMBER b = strings.TO_NUMBER(parts[1]). "
              "NUMBER c = strings.TO_NUMBER(parts[2]). "
              "NUMBER d = strings.TO_NUMBER(parts[3]). "
              "NUMBER[] values=[a,b,c,d]. NUMBER total=0. "
              "LOOP (NUMBER i=0 TILL i<4, i++) { IF (values[i]<0) { total+=1. } } "
              "DISPLAYNL(total).")
    inputs = ("0|0|0|0", "-1|0|0|0", "-1|-2|0|0", "1|2|3|4", "0|0|0|-1")
    values = (0, 1, 2, 0, 1)
    return {"id": "ARRAY_API_EVAL", "domain": "array_reduction",
            "predicate_definitions": {"A": A},
            "aggregation": {"kind": "sum_per_item", "expr": pred("A"), "initial": const(0)},
            "output_domain": {"required_categories": ["ZERO", "POSITIVE"], "exact_sentinels": []},
            "literal_token_requirements": [], "source": source,
            "cases": [{"case_id": f"C{j+1}", "stdin": x, "expected_stdout": str(y)}
                      for j, (x, y) in enumerate(zip(inputs, values))],
            "task_kind": "secondary"}


def local_graph_eval() -> dict:
    source = numeric_source(("P", "Q", "R"),
                            "total+=(hitP*hitQ+hitP*hitR).")
    ns = N
    values = [sum(truth("P", i, n) * truth("Q", i, n) +
                  truth("P", i, n) * truth("R", i, n) for i in range(1, n + 1))
              for n in ns]
    return {"id": "LOCAL_GRAPH_EVAL", "domain": "numeric_iteration",
            "predicate_definitions": copy.deepcopy(DEFS),
            "aggregation": {"kind": "sum_per_item",
                            "expr": binary("add", binary("mul", pred("P"), pred("Q")),
                                           binary("mul", pred("P"), pred("R"))),
                            "initial": const(0)},
            "output_domain": {"required_categories": ["ZERO", "POSITIVE"], "exact_sentinels": []},
            "literal_token_requirements": [], "source": source,
            "cases": [{"case_id": f"C{j+1}", "stdin": str(n), "expected_stdout": str(v)}
                      for j, (n, v) in enumerate(zip(ns, values))],
            "task_kind": "primary"}


def prefix_eval() -> dict:
    source = numeric_source(("P", "Q"), "", prefix=True)
    values = []
    for n in N:
        seen = total = 0
        for i in range(1, n + 1):
            if truth("Q", i, n): total += seen
            if truth("P", i, n): seen += 1
        values.append(total)
    return {"id": "PREFIX_EVAL", "domain": "numeric_iteration",
            "predicate_definitions": {"P": copy.deepcopy(P), "Q": copy.deepcopy(Q)},
            "aggregation": {"kind": "prefix_pair", "p": "P", "q": "Q"},
            "output_domain": {"required_categories": ["ZERO", "POSITIVE"], "exact_sentinels": []},
            "literal_token_requirements": [], "source": source,
            "cases": [{"case_id": f"C{j+1}", "stdin": str(n), "expected_stdout": str(v)}
                      for j, (n, v) in enumerate(zip(N, values))],
            "task_kind": "secondary"}


def main() -> None:
    iso, comp = base_training()
    fixtures = []
    fixtures.append(fixture("equivalent_comparison_operands", "SEMANTIC_PRIMITIVE", "PASS",
                            iso, comp, numeric_record("EQ_COMPARE", ("P", "Q"), "add",
                                                      condition=None, task_kind="secondary",
                                                      q_swapped=True)))
    fixtures.append(fixture("commutative_pair_order", "OPERATOR_CAPABILITY", "PASS",
                            iso, comp, numeric_record("COMMUTE", ("Q", "P"), "add",
                                                      condition=None, task_kind="secondary")))
    unused = numeric_record("REFERENCE_ONLY", ("P", "Q"), "add", condition=None,
                            task_kind="secondary", extra="NUMBER unused=99.")
    fixtures.append(fixture("unused_reference_declaration", "LANGUAGE_CONSTRUCT", "PASS",
                            iso, comp, unused))
    fixtures.append(fixture("local_pair_motifs_without_full_graph", "STRUCTURAL_SIGNATURE", "PASS",
                            iso, comp, local_graph_eval()))
    neg_iso, neg_comp = base_training(negative_initial=True)
    eval_negative = numeric_record("VALUE_DERIVED", ("P", "Q"), "mul", condition=None,
                                   task_kind="secondary", ns=(0, 1, 2, 4, 6),
                                   initial=const(-1), offset="-1")
    fixtures.append(fixture("computed_negative_one_equivalence", "LITERAL_OR_VALUE_CAPABILITY", "PASS",
                            neg_iso, neg_comp, eval_negative))
    literal_eval = copy.deepcopy(eval_negative)
    literal_eval["id"] = "EXACT_LITERAL_EVAL"
    literal_eval["literal_token_requirements"] = ["-1"]
    fixtures.append(fixture("literal_token_not_value", "LITERAL_OR_VALUE_CAPABILITY", "FAIL",
                            neg_iso, neg_comp, literal_eval, "LITERAL_TOKEN:-1"))
    fixtures.append(fixture("task_essential_array_api_absent", "API_CAPABILITY", "FAIL",
                            iso, comp, array_api_eval(), "UNCOVERED:API_CAPABILITY"))
    no_branch_iso = [numeric_record(f"ISO_SINGLE_{x}", (x,), "add", condition="isolated",
                                    task_kind="training", extra="IF (0==1) { total+=99. }")
                     for x in ("P", "Q")]
    no_branch_comp = [numeric_record(f"COMP_SINGLE_{x}", (x,), "add", condition="composition",
                                     task_kind="training", extra="IF (0==1) { total+=99. }")
                      for x in ("P", "Q")]
    fixtures.append(fixture("dead_if_does_not_cover_independent_checks", "CONTROL_FLOW_CAPABILITY", "FAIL",
                            no_branch_iso, no_branch_comp,
                            numeric_record("TWO_CHECKS", ("P", "Q"), "add", condition=None,
                                           task_kind="secondary"),
                            "MULTIPLE_INDEPENDENT_PREDICATE_CHECKS"))
    fixtures.append(fixture("boolean_or_operator_absent", "OPERATOR_CAPABILITY", "FAIL",
                            iso, comp, numeric_record("OR_EVAL", ("P", "Q"), "or",
                                                      condition=None, task_kind="secondary"),
                            "BOOLEAN_OR"))
    fixtures.append(fixture("prior_state_dataflow_absent", "DATAFLOW_OR_AGGREGATION_CAPABILITY", "FAIL",
                            iso, comp, prefix_eval(), "PRIOR_STATE_TO_ACCUMULATOR"))
    fixtures.append(fixture("full_primary_signature_reused", "STRUCTURAL_SIGNATURE", "FAIL",
                            iso, comp, numeric_record("FULL_REUSE", ("P", "Q"), "mul",
                                                      condition=None, task_kind="primary"),
                            "PROHIBITED_FULL_SIGNATURE:composition"))
    negative_without_training = copy.deepcopy(eval_negative)
    negative_without_training["id"] = "NEGATIVE_UNCOVERED"
    fixtures.append(fixture("negative_output_capability_absent", "LITERAL_OR_VALUE_CAPABILITY", "FAIL",
                            iso, comp, negative_without_training, "OUTPUT_NEGATIVE"))
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.write_text(json.dumps({"version": 2, "status": "LABELS_FROZEN_BEFORE_AUDITOR_RUN",
                               "fixtures": fixtures}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"fixtures": len(fixtures), "pass": sum(x["expected"] == "PASS" for x in fixtures),
                      "fail": sum(x["expected"] == "FAIL" for x in fixtures)}))


if __name__ == "__main__":
    main()
