"""Non-model, contract-driven CONF1 capability coverage auditor v2.

Only synthetic fixtures are evaluated in this recovery. No attempt-004 data is
created or read. The contract grammar and decision rules are versioned in
research/protocols/phase3c_conf1_coverage_v2.md.
"""

from __future__ import annotations

import copy
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.compiler import GocoCompiler, normalized_program_output  # noqa: E402


class CoverageError(ValueError):
    pass


BINARY = {"add", "sub", "mul", "mod", "eq", "ne", "lt", "le", "gt", "ge", "and", "or"}
UNARY = {"neg", "not", "indicator"}
COMMUTATIVE = {"add", "mul", "eq", "ne", "and", "or"}
COMPARISONS = {"eq", "ne", "lt", "le", "gt", "ge"}
OUTPUT_CATEGORIES = {"ZERO", "POSITIVE", "NEGATIVE", "MULTIDIGIT"}
ATOMIC_DATAFLOW = ("PREDICATE_TO_INDICATOR", "NUMERIC_TO_ACCUMULATOR",
                   "LOOP_CARRY", "ACCUMULATOR_TO_OUTPUT", "SUM_AGGREGATION")


def compiler() -> GocoCompiler:
    return GocoCompiler(ROOT / ".tools/jdk-25.0.1+8/bin/java.exe",
                        ROOT / ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar",
                        timeout_seconds=3, output_limit_bytes=65536)


def const_value(node: dict) -> int | None:
    op = node.get("op")
    if op == "const" and type(node.get("value")) is int:
        return node["value"]
    if op == "neg":
        child = const_value(node["arg"])
        return -child if child is not None else None
    if op in {"add", "sub", "mul"}:
        a, b = (const_value(x) for x in node["args"])
        if a is not None and b is not None:
            return {"add": a + b, "sub": a - b, "mul": a * b}[op]
    return None


def canonical_expr(node: dict) -> tuple:
    folded = const_value(node)
    if folded is not None:
        return ("CONST", folded)
    op = node["op"]
    if op == "var":
        return ("VAR", node["name"])
    if op == "pred":
        return ("PRED", node["name"])
    if op in UNARY:
        return (op.upper(), canonical_expr(node["arg"]))
    if op in BINARY:
        a, b = (canonical_expr(x) for x in node["args"])
        if op == "gt":
            return ("LT", b, a)
        if op == "ge":
            return ("LE", b, a)
        if op in COMMUTATIVE and b < a:
            a, b = b, a
        return (op.upper(), a, b)
    raise CoverageError(f"unknown expression operation {op}")


def validate_expr(node: Any, *, predicate_names: set[str], predicate_definition: bool = False) -> None:
    if not isinstance(node, dict) or "op" not in node:
        raise CoverageError("expression node missing op")
    op = node["op"]
    if op == "const":
        if set(node) != {"op", "value"} or type(node["value"]) is not int:
            raise CoverageError("bad integer constant")
    elif op == "var":
        if set(node) != {"op", "name"} or node["name"] not in {"n", "i", "value"}:
            raise CoverageError("bad variable")
    elif op == "pred":
        if predicate_definition or set(node) != {"op", "name"} or node["name"] not in predicate_names:
            raise CoverageError("bad predicate leaf")
    elif op in UNARY:
        if set(node) != {"op", "arg"}:
            raise CoverageError("bad unary node")
        validate_expr(node["arg"], predicate_names=predicate_names,
                      predicate_definition=predicate_definition)
    elif op in BINARY:
        if set(node) != {"op", "args"} or not isinstance(node["args"], list) or len(node["args"]) != 2:
            raise CoverageError("bad binary node")
        for arg in node["args"]:
            validate_expr(arg, predicate_names=predicate_names,
                          predicate_definition=predicate_definition)
    else:
        raise CoverageError(f"unknown operation {op}")


def parse_items(domain: str, stdin: str) -> list[dict[str, int]]:
    if domain == "numeric_iteration":
        try:
            n = int(stdin.strip())
        except ValueError as exc:
            raise CoverageError("invalid numeric stdin") from exc
        if n < 0 or not re.fullmatch(r"\s*\d+\s*", stdin):
            raise CoverageError("numeric input must be nonnegative decimal")
        return [{"n": n, "i": i, "value": i} for i in range(1, n + 1)]
    if domain == "array_reduction":
        parts = stdin.strip().split("|")
        if len(parts) != 4 or any(not re.fullmatch(r"\s*-?\d+\s*", x) for x in parts):
            raise CoverageError("array input must contain four signed decimals")
        values = [int(x) for x in parts]
        return [{"n": 4, "i": i, "value": value} for i, value in enumerate(values)]
    raise CoverageError(f"unknown domain {domain}")


def eval_expr(node: dict, env: dict[str, int], predicates: dict[str, dict]) -> int | bool:
    op = node["op"]
    if op == "const":
        return node["value"]
    if op == "var":
        return env[node["name"]]
    if op == "pred":
        return bool(eval_expr(predicates[node["name"]], env, predicates))
    if op in UNARY:
        value = eval_expr(node["arg"], env, predicates)
        return {"neg": lambda: -int(value), "not": lambda: not bool(value),
                "indicator": lambda: int(bool(value))}[op]()
    a, b = (eval_expr(x, env, predicates) for x in node["args"])
    if op == "add": return int(a) + int(b)
    if op == "sub": return int(a) - int(b)
    if op == "mul": return int(a) * int(b)
    if op == "mod":
        if int(b) == 0:
            raise CoverageError("modulo zero")
        return int(a) % int(b)
    if op == "eq": return a == b
    if op == "ne": return a != b
    if op == "lt": return a < b
    if op == "le": return a <= b
    if op == "gt": return a > b
    if op == "ge": return a >= b
    if op == "and": return bool(a) and bool(b)
    if op == "or": return bool(a) or bool(b)
    raise CoverageError(f"unknown operation {op}")


def evaluate(record: dict, stdin: str, *, aggregator_mutation: bool = False) -> int:
    items = parse_items(record["domain"], stdin)
    predicates = record["predicate_definitions"]
    agg = record["aggregation"]
    kind = agg["kind"]
    if kind == "sum_per_item":
        initial = int(eval_expr(agg["initial"], items[0] if items else
                                {"n": int(stdin.strip()) if record["domain"] == "numeric_iteration" else 4,
                                 "i": 0, "value": 0}, predicates))
        included = items[:-1] if aggregator_mutation else items
        return initial + sum(int(eval_expr(agg["expr"], env, predicates)) for env in included)
    p, q = agg["p"], agg["q"]
    if kind == "prefix_pair":
        seen = total = 0
        for env in items:
            if bool(eval_expr(predicates[q], env, predicates)):
                total += 0 if aggregator_mutation else seen
            if bool(eval_expr(predicates[p], env, predicates)):
                seen += 1
        return total
    if kind == "product_of_counts":
        left = sum(bool(eval_expr(predicates[p], x, predicates)) for x in items)
        right = sum(bool(eval_expr(predicates[q], x, predicates)) for x in items)
        return left + right if aggregator_mutation else left * right
    raise CoverageError(f"unknown aggregator {kind}")


def walk(node: dict, path: tuple = ()):
    yield path, node
    if node["op"] in UNARY:
        yield from walk(node["arg"], path + ("arg",))
    elif node["op"] in BINARY:
        for i, child in enumerate(node["args"]):
            yield from walk(child, path + ("args", i))


def walk_semantic(node: dict, path: tuple = ()):
    """Treat an all-constant subtree as one computed value capability."""
    yield path, node
    if const_value(node) is not None:
        return
    if node["op"] in UNARY:
        yield from walk_semantic(node["arg"], path + ("arg",))
    elif node["op"] in BINARY:
        for i, child in enumerate(node["args"]):
            yield from walk_semantic(child, path + ("args", i))


def at_path(root: dict, path: tuple) -> dict:
    current = root
    for part in path:
        current = current[part]
    return current


def replace_path(root: dict, path: tuple, replacement: dict) -> None:
    parent = at_path(root, path[:-1]) if path else None
    if parent is None:
        root.clear()
        root.update(replacement)
    else:
        parent[path[-1]] = replacement


def mutation(node: dict) -> dict | None:
    op = node["op"]
    if op == "const":
        return {"op": "const", "value": node["value"] + 1}
    if op == "pred":
        return {"op": "const", "value": 0}
    if op in {"neg", "not"}:
        return copy.deepcopy(node["arg"])
    if op == "indicator":
        return {"op": "const", "value": 0}
    if op in BINARY - COMPARISONS:
        return copy.deepcopy(node["args"][0])
    if op in COMPARISONS:
        return {"op": "not", "arg": copy.deepcopy(node)}
    return None


def activity(record: dict, path: tuple, *, aggregator: bool = False) -> dict | None:
    for case in sorted(record["cases"], key=lambda c: c["case_id"]):
        original = evaluate(record, case["stdin"])
        if aggregator:
            changed = evaluate(record, case["stdin"], aggregator_mutation=True)
        else:
            altered = copy.deepcopy(record)
            node = at_path(altered, path)
            replacement = mutation(node)
            if replacement is None:
                continue
            replace_path(altered, path, replacement)
            try:
                changed = evaluate(altered, case["stdin"])
            except (CoverageError, ZeroDivisionError):
                continue
        if original != changed:
            return {"case_id": case["case_id"], "original": original,
                    "counterfactual": changed, "path": list(path)}
    return None


def activity_replace(record: dict, path: tuple, replacement: dict) -> dict | None:
    for case in sorted(record["cases"], key=lambda c: c["case_id"]):
        original = evaluate(record, case["stdin"])
        altered = copy.deepcopy(record)
        replace_path(altered, path, copy.deepcopy(replacement))
        try:
            changed = evaluate(altered, case["stdin"])
        except (CoverageError, ZeroDivisionError):
            continue
        if original != changed:
            return {"case_id": case["case_id"], "original": original,
                    "counterfactual": changed, "path": list(path)}
    return None


def _output_category(value: int, category: str) -> bool:
    return {"ZERO": value == 0, "POSITIVE": value > 0, "NEGATIVE": value < 0,
            "MULTIDIGIT": abs(value) >= 10}[category]


def _source_certificate(record: dict) -> tuple[list[dict], list[str]]:
    """Check the fixed numeric/array input parser chain and source-only extras."""
    source = record["source"]
    failures: list[str] = []
    reference_only: list[dict] = []
    inp = re.search(r"\bINPUT\s*\(\s*([A-Za-z_]\w*)\s*\)", source, re.I)
    if not inp:
        failures.append("API_INPUT_MISSING")
        return reference_only, failures
    input_var = inp.group(1)
    if not re.search(r"\bLOOP\s*\(", source, re.I):
        failures.append("LOOP_MISSING")
    if not re.search(r"\bDISPLAYNL\s*\(", source, re.I):
        failures.append("OUTPUT_MISSING")
    if record["domain"] == "numeric_iteration":
        loop_start = re.search(r"\bLOOP\s*\(", source, re.I)
        if loop_start and input_var not in source[loop_start.start():loop_start.start() + 140]:
            failures.append("NUMERIC_INPUT_NOT_IN_LOOP_BOUND")
    else:
        if not re.search(r"\bIMPORT\s+strings\s*\.", source, re.I):
            failures.append("ARRAY_LIBRARY_IMPORT_MISSING")
        split = re.search(r"\b([A-Za-z_]\w*)\s*=\s*strings\.SPLIT\s*\(\s*" +
                          re.escape(input_var) + r"\s*,\s*\"\|\"\s*\)", source, re.I)
        if not split:
            failures.append("ARRAY_SPLIT_CHAIN_MISSING")
        else:
            parts = split.group(1)
            indices = set(int(x) for x in re.findall(
                r"strings\.TO_NUMBER\s*\(\s*" + re.escape(parts) + r"\s*\[\s*([0-3])\s*\]\s*\)",
                source, re.I))
            if indices != {0, 1, 2, 3}:
                failures.append("ARRAY_CONVERSION_CHAIN_INCOMPLETE")
        if not re.search(r"\bNUMBER\s*\[\s*\]\s+\w+\s*=\s*\[", source, re.I):
            failures.append("ARRAY_VALUES_MISSING")
    used_predicates = set(_predicate_leaves(record))
    if_count = len(re.findall(r"\bIF\s*\(", source, re.I))
    if if_count > len(used_predicates):
        dead = len(re.findall(r"\bIF\s*\(\s*0\s*==\s*1\s*\)", source, re.I))
        if if_count - len(used_predicates) > dead:
            failures.append("UNCLASSIFIED_EXTRA_IF")
        else:
            reference_only.append({"construct": "IF", "count": if_count - len(used_predicates),
                                   "proof_code": "CONSTANT_FALSE_BRANCH"})
    declarations = re.findall(r"\bNUMBER\s+([A-Za-z_]\w*)\s*=", source, re.I)
    for name in declarations:
        if len(re.findall(r"\b" + re.escape(name) + r"\b", source)) == 1:
            reference_only.append({"construct": "NUMBER_DECLARATION", "name": name,
                                   "proof_code": "UNUSED_DECLARATION"})
    return reference_only, failures


def _predicate_leaves(record: dict) -> list[str]:
    agg = record["aggregation"]
    if agg["kind"] == "sum_per_item":
        return [node["name"] for _, node in walk(agg["expr"]) if node["op"] == "pred"]
    return [agg["p"], agg["q"]]


def _typed_operator(node: dict, *, predicate: bool) -> str:
    op = node["op"]
    if op in {"gt", "lt"}: return "COMPARISON_STRICT"
    if op in {"ge", "le"}: return "COMPARISON_INCLUSIVE"
    if op in {"eq", "ne"}: return "COMPARISON_EQUALITY" if op == "eq" else "COMPARISON_INEQUALITY"
    if op in {"and", "or", "not"}: return "BOOLEAN_" + op.upper()
    if op == "mul": return "INTEGER_MULTIPLICATION" if predicate else "INDICATOR_MULTIPLICATION"
    if op == "add": return "INTEGER_ADDITION"
    if op == "sub": return "INTEGER_SUBTRACTION"
    if op == "mod": return "INTEGER_MODULO"
    if op == "neg": return "INTEGER_NEGATION"
    if op == "indicator": return "BOOLEAN_TO_INDICATOR"
    raise CoverageError(f"unknown operator {op}")


def _full_signature(record: dict) -> str:
    agg = record["aggregation"]
    names = sorted(set(_predicate_leaves(record)))
    if agg["kind"] == "sum_per_item":
        vector = []
        for values in itertools.product((False, True), repeat=len(names)):
            truth = dict(zip(names, values))
            def eval_boolean(node: dict) -> int | bool:
                op = node["op"]
                if op == "pred": return truth[node["name"]]
                if op == "const": return node["value"]
                if op in UNARY:
                    x = eval_boolean(node["arg"])
                    return {"neg": lambda: -int(x), "not": lambda: not bool(x),
                            "indicator": lambda: int(bool(x))}[op]()
                a, b = (eval_boolean(x) for x in node["args"])
                if op == "add": return int(a) + int(b)
                if op == "sub": return int(a) - int(b)
                if op == "mul": return int(a) * int(b)
                if op == "and": return bool(a) and bool(b)
                if op == "or": return bool(a) or bool(b)
                if op == "gt": return a > b
                if op == "eq": return a == b
                if op == "ne": return a != b
                if op == "lt": return a < b
                if op == "le": return a <= b
                if op == "ge": return a >= b
                if op == "mod": return int(a) % int(b)
                raise CoverageError(f"unsupported graph signature op {op}")
            vector.append(int(eval_boolean(agg["expr"])))
        signature = ["sum_per_item", names, vector, canonical_expr(agg["initial"])]
    else:
        signature = [agg["kind"], names, agg["p"], agg["q"]]
    return json.dumps(signature, separators=(",", ":"))


def _local_pair_motifs(record: dict) -> int:
    agg = record["aggregation"]
    if agg["kind"] != "sum_per_item":
        return 0
    return sum(node["op"] in {"mul", "and"} and
               all(arg["op"] == "pred" for arg in node["args"])
               for _, node in walk(agg["expr"]) if node["op"] in BINARY)


def _validate_schema(record: dict, condition: str | None) -> None:
    base = {"id", "domain", "predicate_definitions", "aggregation", "output_domain",
            "source", "cases", "task_kind", "literal_token_requirements"}
    needed = base | ({"condition"} if condition is not None else set())
    if set(record) != needed or record.get("condition") != condition:
        raise CoverageError("record schema mismatch")
    if record["domain"] not in {"numeric_iteration", "array_reduction"}:
        raise CoverageError("unknown domain")
    if record["task_kind"] not in {"primary", "secondary", "training"}:
        raise CoverageError("unknown task kind")
    if not isinstance(record["id"], str) or not record["id"]:
        raise CoverageError("bad record ID")
    predicates = record["predicate_definitions"]
    if not isinstance(predicates, dict) or not predicates:
        raise CoverageError("missing predicates")
    for node in predicates.values():
        validate_expr(node, predicate_names=set(predicates), predicate_definition=True)
    agg = record["aggregation"]
    if agg["kind"] == "sum_per_item":
        if set(agg) != {"kind", "expr", "initial"}:
            raise CoverageError("bad sum aggregator")
        validate_expr(agg["expr"], predicate_names=set(predicates))
        validate_expr(agg["initial"], predicate_names=set(predicates))
    elif agg["kind"] in {"prefix_pair", "product_of_counts"}:
        if set(agg) != {"kind", "p", "q"} or any(agg[k] not in predicates for k in ("p", "q")):
            raise CoverageError("bad pair aggregator")
    else:
        raise CoverageError("unknown aggregator")
    if set(predicates) != set(_predicate_leaves(record)):
        raise CoverageError("unused or undeclared predicate")
    output = record["output_domain"]
    if (set(output) != {"required_categories", "exact_sentinels"}
            or not set(output["required_categories"]) <= OUTPUT_CATEGORIES
            or any(type(x) is not int for x in output["exact_sentinels"])):
        raise CoverageError("bad output domain")
    if not isinstance(record["cases"], list) or len(record["cases"]) != 5:
        raise CoverageError("exactly five cases required")
    if len({c["case_id"] for c in record["cases"]}) != 5:
        raise CoverageError("duplicate case ID")
    if (not isinstance(record["literal_token_requirements"], list)
            or any(not isinstance(x, str) or not re.fullmatch(r"-?\d+", x)
                   for x in record["literal_token_requirements"])):
        raise CoverageError("bad literal token requirements")


def _literal_token_witness(record: dict, token: str, go_compiler: GocoCompiler) -> dict | None:
    pattern = (r"(?<![A-Za-z_0-9])-\s*" + re.escape(token[1:]) + r"(?!\d)"
               if token.startswith("-") else
               r"(?<![A-Za-z_0-9])" + re.escape(token) + r"(?!\d)")
    if not re.search(pattern, record["source"]):
        return None
    replacement = str(int(token) + 1)
    changed_source = re.sub(pattern, replacement, record["source"])
    for case in record["cases"]:
        original = evaluate(record, case["stdin"])
        result = go_compiler.run(changed_source, case["stdin"])
        if result.phase != "success":
            continue
        try:
            changed = Decimal(normalized_program_output(result.stdout))
        except Exception:
            continue
        if changed != original:
            return {"case_id": case["case_id"], "original": original,
                    "counterfactual": str(changed), "path": ["source", token]}
    return None


def _add(rows: list[dict], category: str, key: str, witness: dict | None,
         *, rule: str, path: tuple = (), treatment: bool = False) -> None:
    rows.append({"category": category, "canonical_key": key,
                 "classification": "TASK_ESSENTIAL", "rule_type": rule,
                 "activity_witness": witness, "path": list(path),
                 "treatment_contrast": treatment})


def extract(record: dict, go_compiler: GocoCompiler, condition: str | None) -> dict:
    """Validate one source-backed contract and extract all capabilities."""
    _validate_schema(record, condition)
    failures: list[str] = []
    source_only, source_failures = _source_certificate(record)
    failures.extend(source_failures)
    expected_values = []
    for case in record["cases"]:
        expected = evaluate(record, case["stdin"])
        try:
            printed = Decimal(case["expected_stdout"].strip())
        except Exception as exc:
            raise CoverageError("invalid expected stdout") from exc
        if printed != expected:
            failures.append(f"CONTRACT_CASE_MISMATCH:{case['case_id']}")
        result = go_compiler.run(record["source"], case["stdin"])
        try:
            actual = Decimal(normalized_program_output(result.stdout))
        except Exception:
            actual = None
        if result.phase != "success" or actual != expected:
            failures.append(f"SOURCE_CASE_MISMATCH:{case['case_id']}:{result.phase}")
        expected_values.append(expected)
    rows: list[dict] = []
    domain = record["domain"]
    witness = {"case_id": record["cases"][0]["case_id"], "original": expected_values[0],
               "counterfactual": "removed domain decoder", "path": ["domain"]}
    for key in ("INPUT", "BOUNDED_ITERATION", "NUMERIC_ASSIGNMENT_UPDATE", "FINAL_DISPLAY"):
        _add(rows, "LANGUAGE_CONSTRUCT", key, witness, rule="STRUCTURAL_RELATION")
    for api in (("INPUT",) if domain == "numeric_iteration" else
                ("INPUT", "strings.SPLIT", "strings.TO_NUMBER")):
        _add(rows, "API_CAPABILITY", f"{domain}:{api}", witness, rule="EXACT_SYNTACTIC")
    _add(rows, "LITERAL_OR_VALUE_CAPABILITY", f"INPUT_DOMAIN:{domain}", witness,
         rule="VALUE_DOMAIN_CAPABILITY")
    agg = record["aggregation"]
    agg_witness = activity(record, ("aggregation",), aggregator=True)
    if agg_witness is None:
        failures.append("AGGREGATOR_NOT_EXERCISED")
    for key in ("BOUNDED_TRAVERSAL", "CONDITIONAL_ACCUMULATION"):
        _add(rows, "CONTROL_FLOW_CAPABILITY", key, agg_witness, rule="STRUCTURAL_RELATION")
    if len(set(_predicate_leaves(record))) >= 2:
        _add(rows, "CONTROL_FLOW_CAPABILITY", "MULTIPLE_INDEPENDENT_PREDICATE_CHECKS",
             agg_witness, rule="STRUCTURAL_RELATION")
    for key in ATOMIC_DATAFLOW:
        _add(rows, "DATAFLOW_OR_AGGREGATION_CAPABILITY", key, agg_witness,
             rule="STRUCTURAL_RELATION")
    if agg["kind"] == "prefix_pair":
        _add(rows, "DATAFLOW_OR_AGGREGATION_CAPABILITY", "PRIOR_STATE_TO_ACCUMULATOR",
             agg_witness, rule="STRUCTURAL_RELATION")
    elif agg["kind"] == "product_of_counts":
        _add(rows, "DATAFLOW_OR_AGGREGATION_CAPABILITY", "PRODUCT_OF_COUNTS",
             agg_witness, rule="STRUCTURAL_RELATION")
    _add(rows, "OPERATOR_CAPABILITY", "INTEGER_ADDITION", agg_witness,
         rule="SEMANTIC_EQUIVALENCE_CLASS")
    if agg["kind"] == "product_of_counts":
        _add(rows, "OPERATOR_CAPABILITY", "INTEGER_MULTIPLICATION", agg_witness,
             rule="SEMANTIC_EQUIVALENCE_CLASS")
    for name, definition in record["predicate_definitions"].items():
        predicate_paths = []
        if agg["kind"] == "sum_per_item":
            predicate_paths = [("aggregation", "expr") + path for path, node in walk(agg["expr"])
                               if node["op"] == "pred" and node["name"] == name]
        else:
            predicate_paths = [("aggregation", name)]
        for predicate_path in predicate_paths:
            pred_witness = (activity(record, predicate_path) if agg["kind"] == "sum_per_item"
                            else activity_replace(record, ("predicate_definitions", name),
                                                  {"op": "const", "value": 0}))
            if pred_witness is None:
                failures.append(f"PRIMITIVE_NOT_EXERCISED:{name}:{predicate_path}")
            _add(rows, "SEMANTIC_PRIMITIVE", f"{domain}:{name}:{canonical_expr(definition)}",
                 pred_witness, rule="SEMANTIC_EQUIVALENCE_CLASS", path=predicate_path)
        for path, node in walk_semantic(definition):
            folded = const_value(node)
            if folded is not None:
                value_witness = activity(record, ("predicate_definitions", name) + path)
                if value_witness is None:
                    failures.append(f"PREDICATE_VALUE_NOT_EXERCISED:{name}:{path}")
                _add(rows, "LITERAL_OR_VALUE_CAPABILITY",
                     f"COMPUTED_VALUE:{folded}:PREDICATE", value_witness,
                     rule="VALUE_DOMAIN_CAPABILITY", path=("predicate_definitions", name) + path)
                continue
            if node["op"] == "var":
                continue
            op_witness = activity(record, ("predicate_definitions", name) + path)
            if op_witness is None:
                failures.append(f"PREDICATE_OPERATOR_NOT_EXERCISED:{name}:{path}")
            _add(rows, "OPERATOR_CAPABILITY", _typed_operator(node, predicate=True), op_witness,
                 rule="SEMANTIC_EQUIVALENCE_CLASS", path=("predicate_definitions", name) + path)
    if agg["kind"] == "sum_per_item":
        for path, node in walk_semantic(agg["expr"]):
            if node["op"] in {"pred", "var"}:
                continue
            node_witness = activity(record, ("aggregation", "expr") + path)
            if node_witness is None:
                failures.append(f"AGGREGATION_NODE_NOT_EXERCISED:{path}")
            folded = const_value(node)
            if folded is not None:
                _add(rows, "LITERAL_OR_VALUE_CAPABILITY",
                     f"COMPUTED_VALUE:{folded}:AGGREGATION", node_witness,
                     rule="VALUE_DOMAIN_CAPABILITY", path=("aggregation", "expr") + path)
            else:
                pair = (node["op"] in {"mul", "and"} and
                        all(arg["op"] == "pred" for arg in node.get("args", [])))
                if pair:
                    _add(rows, "DATAFLOW_OR_AGGREGATION_CAPABILITY", "LOCAL_PAIR_JOINT",
                         node_witness, rule="STRUCTURAL_RELATION",
                         path=("aggregation", "expr") + path, treatment=True)
                    _add(rows, "OPERATOR_CAPABILITY", "INTEGER_MULTIPLICATION", node_witness,
                         rule="SEMANTIC_EQUIVALENCE_CLASS", path=("aggregation", "expr") + path)
                else:
                    _add(rows, "OPERATOR_CAPABILITY", _typed_operator(node, predicate=False),
                         node_witness, rule="SEMANTIC_EQUIVALENCE_CLASS",
                         path=("aggregation", "expr") + path)
        for path, node in walk_semantic(agg["initial"]):
            folded = const_value(node)
            if folded is not None:
                init_witness = activity(record, ("aggregation", "initial") + path)
                if init_witness is None:
                    failures.append("INITIAL_VALUE_NOT_EXERCISED")
                _add(rows, "LITERAL_OR_VALUE_CAPABILITY",
                     f"COMPUTED_VALUE:{folded}:INITIAL", init_witness,
                     rule="VALUE_DOMAIN_CAPABILITY", path=("aggregation", "initial") + path)
    observed_categories = {category for category in OUTPUT_CATEGORIES
                           if any(_output_category(x, category) for x in expected_values)}
    for category in sorted(set(record["output_domain"]["required_categories"]) | observed_categories):
        found = next((case for case, value in zip(record["cases"], expected_values)
                      if _output_category(value, category)), None)
        if found is None:
            failures.append(f"OUTPUT_CATEGORY_UNWITNESSED:{category}")
        _add(rows, "LITERAL_OR_VALUE_CAPABILITY", f"OUTPUT_{category}",
             {"case_id": found["case_id"], "original": evaluate(record, found["stdin"]),
              "counterfactual": "output category absent", "path": ["output_domain"]} if found else None,
             rule="VALUE_DOMAIN_CAPABILITY")
    for token in record["literal_token_requirements"]:
        literal_witness = _literal_token_witness(record, token, go_compiler)
        if literal_witness is None:
            failures.append(f"LITERAL_TOKEN_NOT_ACTIVE:{token}")
        _add(rows, "LITERAL_OR_VALUE_CAPABILITY", f"LITERAL_TOKEN:{token}",
             literal_witness, rule="EXACT_SYNTACTIC")
    for sentinel in record["output_domain"]["exact_sentinels"]:
        found = next((case for case, value in zip(record["cases"], expected_values)
                      if value == sentinel), None)
        if found is None:
            failures.append(f"OUTPUT_SENTINEL_UNWITNESSED:{sentinel}")
        _add(rows, "LITERAL_OR_VALUE_CAPABILITY", f"OUTPUT_EXACT:{sentinel}",
             {"case_id": found["case_id"], "original": sentinel,
              "counterfactual": "sentinel absent", "path": ["output_domain"]} if found else None,
             rule="VALUE_DOMAIN_CAPABILITY")
    signature = _full_signature(record)
    _add(rows, "STRUCTURAL_SIGNATURE", signature, agg_witness, rule="STRUCTURAL_RELATION")
    return {"id": record["id"], "domain": domain, "task_kind": record["task_kind"],
            "condition": condition, "requirements": rows,
            "reference_only": source_only, "failures": failures,
            "local_pair_motifs": _local_pair_motifs(record),
            "full_signature": signature}


def audit_bundle(bundle: dict, go_compiler: GocoCompiler | None = None) -> dict:
    """Audit two training corpora and evaluation records; report every requirement."""
    if set(bundle) != {"isolated", "composition", "evaluation"}:
        raise CoverageError("bundle schema mismatch")
    engine = go_compiler or compiler()
    training: dict[str, list[dict]] = {}
    for condition in ("isolated", "composition"):
        training[condition] = [extract(record, engine, condition)
                               for record in bundle[condition]]
    evaluations = [extract(record, engine, None) for record in bundle["evaluation"]]
    indexes = {condition: defaultdict(list) for condition in training}
    signatures = {condition: set() for condition in training}
    for condition, rows in training.items():
        for row in rows:
            if row["failures"]:
                continue
            signatures[condition].add(row["full_signature"])
            for req in row["requirements"]:
                if req["activity_witness"] is not None:
                    indexes[condition][(row["domain"], req["category"], req["canonical_key"])].append(
                        {"id": row["id"], "witness": req["activity_witness"]})
    all_failures = [f"TRAINING_INVALID:{r['id']}:{x}" for rows in training.values()
                    for r in rows for x in r["failures"]]
    for row in evaluations:
        row["coverage_failures"] = list(row["failures"])
        for req in row["requirements"]:
            if req["category"] == "STRUCTURAL_SIGNATURE":
                req["isolated_evidence"] = []
                req["composition_evidence"] = []
                if row["task_kind"] == "primary":
                    for condition in ("isolated", "composition"):
                        if row["full_signature"] in signatures[condition]:
                            row["coverage_failures"].append(f"PROHIBITED_FULL_SIGNATURE:{condition}")
                req["pass"] = not any(x.startswith("PROHIBITED_FULL_SIGNATURE")
                                      for x in row["coverage_failures"])
                req["reason"] = "PRIMARY_SIGNATURE_ABSENT_BOTH" if req["pass"] else "FULL_SIGNATURE_REUSED"
                continue
            key = (row["domain"], req["category"], req["canonical_key"])
            for condition in ("isolated", "composition"):
                req[f"{condition}_evidence"] = indexes[condition].get(key, [])
            if req["treatment_contrast"]:
                req["pass"] = (req["activity_witness"] is not None and
                               bool(req["composition_evidence"]))
                req["reason"] = ("INTENDED_PAIR_JOINT_TREATMENT_ASYMMETRY" if req["pass"] else
                                 "PAIR_JOINT_NOT_IN_COMPOSITION_TRAINING")
            else:
                req["pass"] = (req["activity_witness"] is not None and
                               all(req[f"{c}_evidence"] for c in ("isolated", "composition")))
                req["reason"] = ("COVERED_BOTH" if req["pass"] else
                                 "MISSING_BOTH_OR_ONE_CONDITION")
            if not req["pass"]:
                row["coverage_failures"].append(
                    f"UNCOVERED:{req['category']}:{req['canonical_key']}")
        row["pass"] = not row["coverage_failures"]
        all_failures.extend(f"EVALUATION_INVALID:{row['id']}:{x}" for x in row["coverage_failures"])
    counts = Counter(req["category"] for row in evaluations for req in row["requirements"])
    return {"status": "PASS" if not all_failures else "FAIL",
            "training_rows": {c: len(training[c]) for c in training},
            "evaluation_rows": len(evaluations), "category_counts": dict(sorted(counts.items())),
            "failure_count": len(all_failures), "failures": all_failures,
            "training": training, "evaluation": evaluations,
            "no_model_execution": True}
