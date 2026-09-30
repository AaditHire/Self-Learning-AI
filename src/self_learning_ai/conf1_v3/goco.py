"""Closed parser and typed expression graph for the builder-generated GOCO subset.

This is deliberately not a general GOCO parser.  Every accepted construct is
listed in ``STATEMENT_HEADS``/``BINARY``; encountering anything else is a
fail-closed error rather than an invitation to infer new language semantics.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Mapping, Sequence

from .interfaces import PHASE, SchemaError, rid

TOKEN = re.compile(
    r'(?P<WS>\s+)|(?P<COMMENT>//[^\n]*|/\*.*?\*/)|(?P<STRING>"(?:\\.|[^"\\])*")|'
    r'(?P<NUMBER>\d+)|(?P<ID>[A-Za-z_][A-Za-z0-9_]*)|'
    r'(?P<OP>==|!=|<=|>=|\+\+|--|\+=|-=|&&|\|\||[+\-*/%<>=!.,;(){}\[\]])', re.S)

TYPES = {"NUMBER", "SENTENCE", "LOGIC"}
STATEMENT_HEADS = TYPES | {"IMPORT", "INPUT", "DISPLAY", "DISPLAYNL", "IF", "ELSEIF", "ELSE", "LOOP"}
BINARY = {"||": 1, "&&": 2, "==": 3, "!=": 3, "<": 4, "<=": 4,
          ">": 4, ">=": 4, "+": 5, "-": 5, "*": 6, "/": 6, "%": 6}
COMMUTATIVE = {"+", "*", "==", "!=", "&&", "||"}


@dataclass(frozen=True)
class Tok:
    kind: str
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class Expr:
    kind: str
    value: str
    children: tuple["Expr", ...]
    start: int
    end: int


@dataclass(frozen=True)
class Stmt:
    kind: str
    value: str
    expressions: tuple[Expr, ...]
    children: tuple["Stmt", ...]
    start: int
    end: int


def lex(source: str) -> list[Tok]:
    out: list[Tok] = []
    pos = 0
    while pos < len(source):
        match = TOKEN.match(source, pos)
        if not match:
            raise SchemaError(f"UNSUPPORTED_GOCO_FORM at byte {pos}")
        kind = match.lastgroup or ""
        if kind not in {"WS", "COMMENT"}:
            out.append(Tok(kind, match.group(), match.start(), match.end()))
        pos = match.end()
    out.append(Tok("EOF", "", len(source), len(source)))
    return out


class Parser:
    def __init__(self, source: str):
        self.source, self.tokens, self.i = source, lex(source), 0

    def peek(self, text: str | None = None) -> Tok | bool:
        token = self.tokens[self.i]
        return token if text is None else token.text == text

    def take(self, text: str | None = None) -> Tok:
        token = self.tokens[self.i]
        if text is not None and token.text != text:
            raise SchemaError(f"UNSUPPORTED_GOCO_FORM expected {text!r} at byte {token.start}")
        self.i += 1
        return token

    def program(self) -> tuple[Stmt, ...]:
        rows = []
        while self.peek().kind != "EOF":
            rows.append(self.statement())
        return tuple(rows)

    def block(self) -> tuple[Stmt, ...]:
        self.take("{"); rows = []
        while not self.peek("}"):
            if self.peek().kind == "EOF": raise SchemaError("UNSUPPORTED_GOCO_FORM unterminated block")
            rows.append(self.statement())
        self.take("}")
        return tuple(rows)

    def statement(self) -> Stmt:
        head = self.peek()
        start = head.start
        if head.text == "IMPORT":
            self.take(); name = self.take()
            if name.kind != "ID": raise SchemaError("UNSUPPORTED_GOCO_FORM invalid import")
            end = self._terminator().end
            return Stmt("IMPORT", name.text, (), (), start, end)
        if head.text in TYPES:
            typ = self.take().text
            if self.peek("["): self.take(); self.take("]"); typ += "[]"
            name = self.take()
            if name.kind != "ID": raise SchemaError("UNSUPPORTED_GOCO_FORM invalid declaration")
            exprs: tuple[Expr, ...] = ()
            if self.peek("="):
                self.take("="); exprs = (self.expr(),)
            end = self._terminator().end
            return Stmt("DECLARE", f"{typ}:{name.text}", exprs, (), start, end)
        if head.text in {"INPUT", "DISPLAY", "DISPLAYNL"}:
            kind = self.take().text; self.take("("); value = self.expr(); self.take(")")
            end = self._terminator().end
            return Stmt(kind, kind, (value,), (), start, end)
        if head.text in {"IF", "ELSEIF"}:
            kind = self.take().text; self.take("("); cond = self.expr(); self.take(")")
            children = list(self.block())
            if self.peek("ELSEIF"): children.append(self.statement())
            elif self.peek("ELSE"):
                e = self.take(); nested = self.block()
                children.append(Stmt("ELSE", "ELSE", (), nested, e.start,
                                     nested[-1].end if nested else self.tokens[self.i - 1].end))
            return Stmt(kind, kind, (cond,), tuple(children), start, children[-1].end if children else self.tokens[self.i-1].end)
        if head.text == "LOOP":
            self.take(); opening = self.take("("); depth = 1; header: list[Tok] = []
            while depth:
                token = self.take()
                if token.kind == "EOF": raise SchemaError("UNSUPPORTED_GOCO_FORM unterminated LOOP header")
                if token.text == "(": depth += 1
                elif token.text == ")":
                    depth -= 1
                    if depth == 0: break
                header.append(token)
            header_text = " ".join(token.text for token in header)
            if not re.fullmatch(r"NUMBER\s+[A-Za-z_]\w*\s*=.+\s+TILL\s+.+,\s*[A-Za-z_]\w*\s*(?:\+\+|--)", header_text):
                raise SchemaError("UNSUPPORTED_GOCO_FORM invalid LOOP header")
            header_expr = Expr("LOOP_HEADER", header_text, (), opening.start, token.end)
            children = self.block()
            return Stmt("LOOP", "LOOP", (header_expr,), children, start,
                        children[-1].end if children else self.tokens[self.i-1].end)
        if head.kind != "ID":
            raise SchemaError(f"UNSUPPORTED_GOCO_FORM {head.text!r} at byte {head.start}")
        lhs = self.expr(7)
        op = self.take()
        if op.text not in {"=", "+=", "-=", "++", "--"}:
            raise SchemaError(f"UNSUPPORTED_GOCO_FORM assignment operator {op.text!r}")
        rhs = () if op.text in {"++", "--"} else (self.expr(),)
        end = self._terminator().end
        return Stmt("UPDATE", op.text, (lhs, *rhs), (), start, end)

    def _terminator(self) -> Tok:
        if self.peek(".") or self.peek(";"): return self.take()
        raise SchemaError(f"UNSUPPORTED_GOCO_FORM missing terminator at byte {self.peek().start}")

    def expr(self, minimum: int = 0) -> Expr:
        token = self.take()
        if token.text in {"-", "!"}:
            child = self.expr(7); left = Expr("UNARY", token.text, (child,), token.start, child.end)
        elif token.text == "(":
            left = self.expr(); close = self.take(")")
            left = Expr("GROUP", "()", (left,), token.start, close.end)
        elif token.text == "[":
            children = []
            if not self.peek("]"):
                children.append(self.expr())
                while self.peek(","): self.take(); children.append(self.expr())
            close = self.take("]"); left = Expr("ARRAY", "[]", tuple(children), token.start, close.end)
        elif token.kind in {"ID", "NUMBER", "STRING"}:
            left = Expr(token.kind, token.text, (), token.start, token.end)
        else:
            raise SchemaError(f"UNSUPPORTED_GOCO_FORM expression at byte {token.start}")
        while True:
            if (self.peek(".") and self.tokens[self.i + 1].kind == "ID" and
                    ((left.kind == "ID" and left.value in {"strings", "math"}) or left.kind == "MEMBER")):
                self.take(); member = self.take()
                left = Expr("MEMBER", member.text, (left,), left.start, member.end); continue
            if self.peek("("):
                self.take(); args = []
                if not self.peek(")"):
                    args.append(self.expr())
                    while self.peek(","): self.take(); args.append(self.expr())
                close = self.take(")"); left = Expr("CALL", "CALL", (left, *args), left.start, close.end); continue
            if self.peek("["):
                self.take(); index = self.expr(); close = self.take("]")
                left = Expr("INDEX", "INDEX", (left, index), left.start, close.end); continue
            op = self.peek().text
            precedence = BINARY.get(op, -1)
            if precedence < minimum: break
            self.take(); right = self.expr(precedence + 1)
            left = Expr("BINARY", op, (left, right), left.start, right.end)
        return left


def parse(source: str) -> tuple[Stmt, ...]:
    return Parser(source).program()


def _walk_expr(expr: Expr) -> Iterator[Expr]:
    yield expr
    for child in expr.children: yield from _walk_expr(child)


def _walk_stmt(stmt: Stmt) -> Iterator[Stmt | Expr]:
    yield stmt
    for expr in stmt.expressions: yield from _walk_expr(expr)
    for child in stmt.children: yield from _walk_stmt(child)


def source_occurrence_inventory(program_id: str, source: str) -> dict[str, Any]:
    """Assign IDs by lexical source order; do not perform mapping/activity."""
    nodes: list[dict[str, Any]] = []
    for ordinal, node in enumerate(sorted((n for s in parse(source) for n in _walk_stmt(s)),
                                           key=lambda n: (n.start, n.end, type(n).__name__))):
        kind = f"{type(node).__name__.upper()}:{node.kind}"
        nodes.append({"occurrence_id": rid("OCC", [program_id, kind, str(node.start), str(ordinal)]),
                      "kind": kind, "source_location": {"start": node.start, "end": node.end},
                      "graph_location": f"nodes/{ordinal}", "eligible_for_v3_5": True})
    edges = []
    for ordinal in range(max(0, len(nodes) - 1)):
        edges.append({"occurrence_id": rid("OCC_EDGE", [program_id, str(ordinal)]),
                      "kind": "LEXICAL_SUCCESSOR", "source_location": None,
                      "graph_location": f"edges/{ordinal}", "from": nodes[ordinal]["occurrence_id"],
                      "to": nodes[ordinal + 1]["occurrence_id"], "eligible_for_v3_5": True})
    return {"schema_version": 1, "phase": PHASE, "program_id": program_id,
            "nodes": nodes, "edges": edges}


def canonical_expression(expr: Expr, names: Mapping[str, str] | None = None) -> tuple[Any, ...]:
    """Frozen alpha/commutative/comparison-direction/Boolean catalog only."""
    names = names or {}
    if expr.kind == "ID": return ("ID", names.get(expr.value, expr.value))
    children = [canonical_expression(c, names) for c in expr.children]
    if expr.kind == "GROUP": return children[0]
    op = expr.value
    if expr.kind == "BINARY" and op in {">", ">="}:
        op = "<" if op == ">" else "<="; children.reverse()
    if expr.kind == "BINARY" and op in COMMUTATIVE:
        children.sort(key=repr)
    if expr.kind == "UNARY" and op == "!" and expr.children[0].kind == "BINARY":
        inverse = {"==": "!=", "!=": "==", "<": ">=", "<=": ">", ">": "<=", ">=": "<"}
        child = expr.children[0]
        if child.value in inverse:
            return canonical_expression(Expr("BINARY", inverse[child.value], child.children, child.start, child.end), names)
    return (expr.kind, op, *children)


def expressions_equivalent(left: Expr, right: Expr, alpha_map: Mapping[str, str] | None = None) -> bool:
    return canonical_expression(left, alpha_map) == canonical_expression(right)
