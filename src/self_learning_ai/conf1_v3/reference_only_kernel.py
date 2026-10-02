"""Frozen RO constant grammar, independent of certificate constructors/statuses.

This is only the supporting arithmetic kernel. It cannot assign an RO bucket,
prove non-requirement, waive E1, or claim compiler identity/agreement.
"""
from dataclasses import dataclass
import re

from .goco import Expr, Parser

BOUND = 2147483647
INTEGER_TOKEN = re.compile(r"(?:0|[1-9][0-9]{0,9})", re.ASCII)
ARITHMETIC = {"+": "ADD", "-": "SUB", "*": "MUL"}
COMPARISONS = {"==": "EQ", "!=": "NE", "<": "LT", "<=": "LE", ">": "GT", ">=": "GE"}


class ConstantIssue(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True)
class ConstantEvaluation:
    expression: Expr
    operation: str
    child_expressions: tuple[Expr, ...]
    integer_value: int


@dataclass(frozen=True)
class ConstantTree:
    root: Expr
    integer_value: int
    postorder: tuple[ConstantEvaluation, ...]


def parse_expression(text):
    parser = Parser(text)
    expression = parser.expr()
    if parser.peek().kind != "EOF":
        raise ConstantIssue("RO_OUTSIDE_CLOSED_GRAMMAR")
    return expression


def constant_tree(root):
    """Reconstruct every value/order/type/bound from parsed children, no flags."""
    rows = []
    ancestors = set()
    def visit(e):
        if not isinstance(e, Expr) or id(e) in ancestors:
            raise ConstantIssue("RO_PARTIAL_OR_NONEXACT_EVALUATION")
        ancestors.add(id(e))
        children = e.children
        child_values = ()
        if e.kind == "NUMBER" and not children and INTEGER_TOKEN.fullmatch(e.value):
            operation, value = "CONSTANT", int(e.value)
        elif e.kind == "GROUP" and e.value == "()" and len(children) == 1:
            child_values = (visit(children[0]),)
            operation, value = "GROUP", child_values[0]
        elif e.kind == "UNARY" and e.value == "-" and len(children) == 1:
            child_values = (visit(children[0]),)
            operation, value = "NEG", -child_values[0]
        elif e.kind == "BINARY" and e.value in ARITHMETIC and len(children) == 2:
            child_values = (visit(children[0]), visit(children[1]))
            a, b = child_values
            operation = ARITHMETIC[e.value]
            value = a + b if e.value == "+" else a - b if e.value == "-" else a * b
        else:
            raise ConstantIssue("RO_OUTSIDE_CLOSED_GRAMMAR")
        if type(value) is not int or not -BOUND <= value <= BOUND:
            raise ConstantIssue("RO_PARTIAL_OR_NONEXACT_EVALUATION")
        # Simulate the pinned binary64 operation without claiming this alone
        # binds the compiler. All operands/results must also agree exactly.
        if operation == "NEG": binary64 = -float(child_values[0])
        elif operation == "ADD": binary64 = float(child_values[0]) + float(child_values[1])
        elif operation == "SUB": binary64 = float(child_values[0]) - float(child_values[1])
        elif operation == "MUL": binary64 = float(child_values[0]) * float(child_values[1])
        else: binary64 = float(value)
        if binary64 != value:
            raise ConstantIssue("RO_PARTIAL_OR_NONEXACT_EVALUATION")
        rows.append(ConstantEvaluation(e, operation, children, value))
        ancestors.remove(id(e))
        return value
    value = visit(root)
    return ConstantTree(root, value, tuple(rows))


def false_comparison(root):
    guard = root
    while guard.kind == "GROUP" and guard.value == "()" and len(guard.children) == 1:
        guard = guard.children[0]
    if guard.kind != "BINARY" or guard.value not in COMPARISONS or len(guard.children) != 2:
        raise ConstantIssue("RO_OUTSIDE_CLOSED_GRAMMAR")
    left, right = (constant_tree(child) for child in guard.children)
    a, b = left.integer_value, right.integer_value
    result = {"==": a == b, "!=": a != b, "<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b}[guard.value]
    binary64 = {"==": abs(float(a) - float(b)) < 0.000001,
                "!=": abs(float(a) - float(b)) >= 0.000001,
                "<": float(a) < float(b), "<=": float(a) <= float(b),
                ">": float(a) > float(b), ">=": float(a) >= float(b)}[guard.value]
    if result != binary64:
        raise ConstantIssue("RO_PARTIAL_OR_NONEXACT_EVALUATION")
    if result:
        raise ConstantIssue("RO_GUARD_NOT_STATIC_FALSE")
    return guard, COMPARISONS[guard.value], left, right
