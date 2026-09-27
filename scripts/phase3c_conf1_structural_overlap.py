"""Candidate-independent GOCO structural-overlap adjudication.

This module is frozen before CONF1 attempt 004 construction.  It does not read
candidate data, historical outcomes, or the sealed holdout.
"""

from __future__ import annotations

import re

TOKEN = re.compile(
    r"(?P<WS>\s+)|(?P<COMMENT>//[^\n]*|/\*[\s\S]*?\*/)|"
    r'(?P<STRING>"(?:\\.|[^"\\])*")|'
    r"(?P<API>[A-Za-z_][A-Za-z_0-9]*\.[A-Za-z_][A-Za-z_0-9]*)|"
    r"(?P<NUMERIC>\d+(?:\.\d+)?)|"
    r"(?P<OP>\+=|-=|\*=|/=|==|!=|<=|>=|\+\+|--|&&|\|\||[+*/%<>=!\-])|"
    r"(?P<IDENT>[A-Za-z_][A-Za-z_0-9]*)|(?P<PUNCT>[\[\](){},.;])"
)
RESERVED = {
    "NUMBER", "SENTENCE", "BOOLEAN", "INPUT", "IMPORT", "LOOP", "TILL",
    "IF", "ELSE", "DISPLAY", "DISPLAYNL", "TRUE", "FALSE", "RETURN",
    "STRINGS", "AND", "OR", "NOT",
}


def enhanced_signature(source: str) -> tuple[str, ...]:
    """Alpha-normalized token tree in source order, preserving all syntax edges.

    Balanced parentheses/braces/brackets and repeated variable identities retain
    control-flow nesting, predicate placement, operators, APIs, assignments,
    accumulator/dataflow, aggregation, and output-expression topology. Numeric
    magnitudes and string contents are normalized; signs/operators are retained.
    """
    out: list[str] = []
    names: dict[str, str] = {}
    pos = 0
    nesting: list[str] = []
    pairs = {")": "(", "]": "[", "}": "{"}
    while pos < len(source):
        match = TOKEN.match(source, pos)
        if match is None:
            raise ValueError(f"unrecognized GOCO token at character {pos}")
        pos = match.end()
        kind, value = match.lastgroup, match.group()
        if kind in {"WS", "COMMENT"}:
            continue
        if value in "([{":
            nesting.append(value)
        elif value in ")]}":
            if not nesting or nesting.pop() != pairs[value]:
                raise ValueError("unbalanced GOCO grouping")
        if kind == "IDENT":
            upper = value.upper()
            if upper in RESERVED:
                out.append(upper)
            else:
                out.append(names.setdefault(value, f"VAR{len(names)}"))
        elif kind == "API":
            out.append("API:" + value.upper())
        elif kind == "NUMERIC":
            out.append("NUM")
        elif kind == "STRING":
            out.append("STRING")
        else:
            out.append(value)
    if nesting:
        raise ValueError("unbalanced GOCO grouping")
    return tuple(out)


def adjudicate(candidate: str, consumed: str, coarse_equal: bool) -> str:
    """Exact rule: equality of enhanced signature is prohibited regardless of coarse flag."""
    if enhanced_signature(candidate) == enhanced_signature(consumed):
        return "PROHIBITED_STRUCTURAL_TEMPLATE_REUSE"
    if coarse_equal:
        return "COARSE_AST_EQUALITY_ONLY"
    return "NO_STRUCTURAL_TEMPLATE_REUSE"
