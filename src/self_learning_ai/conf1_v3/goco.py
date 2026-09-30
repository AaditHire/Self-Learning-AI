"""Closed parser and typed expression graph for the builder-generated GOCO subset.

This is deliberately not a general GOCO parser.  Every accepted construct is
listed in ``STATEMENT_HEADS``/``BINARY``; encountering anything else is a
fail-closed error rather than an invitation to infer new language semantics.
"""

from __future__ import annotations

import re
import json
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
COMMUTATIVE = {"+", "*", "==", "&&", "||"}


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
    alternate: tuple["Stmt", ...] = ()
    loop_index: str | None = None


def lex(source: str) -> list[Tok]:
    out: list[Tok] = []
    pos = 0
    while pos < len(source):
        match = TOKEN.match(source, pos)
        if not match:
            raise SchemaError(f"UNSUPPORTED_GOCO_FORM at byte {pos}")
        kind = match.lastgroup or ""
        if kind not in {"WS", "COMMENT"}:
            out.append(Tok(kind, match.group(), len(source[:match.start()].encode("utf-8")),
                           len(source[:match.end()].encode("utf-8"))))
        pos = match.end()
    out.append(Tok("EOF", "", len(source.encode("utf-8")), len(source.encode("utf-8"))))
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
            if name.kind != "ID" or name.text != "strings": raise SchemaError("UNSUPPORTED_GOCO_FORM import")
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
        if head.text in {"INPUT", "DISPLAYNL"}:
            kind = self.take().text; self.take("("); value = self.expr(); self.take(")")
            end = self._terminator().end
            return Stmt(kind, kind, (value,), (), start, end)
        if head.text == "IF":
            kind = self.take().text; self.take("("); cond = self.expr(); self.take(")")
            children = list(self.block())
            return Stmt(kind, kind, (cond,), tuple(children), start, children[-1].end if children else self.tokens[self.i-1].end)
        if head.text == "LOOP":
            self.take(); self.take("(")
            if self.peek("NUMBER"):
                self.take(); index = self.take()
                if index.kind != "ID": raise SchemaError("UNSUPPORTED_GOCO_FORM loop index")
                self.take("="); initial = self.expr(); self.take("TILL")
                condition = self.expr(); self.take(","); step_index = self.take(); step = self.take()
                if step_index.text != index.text or step.text != "++":
                    raise SchemaError("UNSUPPORTED_GOCO_FORM forward step")
                self.take(")"); children = self.block()
                return Stmt("LOOP", "FORWARD", (initial, condition), children, start,
                            self.tokens[self.i-1].end, loop_index=index.text)
            condition = self.expr(); self.take(")")
            children = self.block()
            if condition.kind != "BINARY" or condition.value != ">=" or condition.children[0].kind != "ID":
                raise SchemaError("UNSUPPORTED_GOCO_FORM reverse bound")
            index = condition.children[0].value
            if not children or children[-1].kind != "UPDATE" or children[-1].value != "-=" or children[-1].expressions[0].value != index or children[-1].expressions[1].value != "1":
                raise SchemaError("UNSUPPORTED_GOCO_FORM reverse step")
            return Stmt("LOOP", "REVERSE", (condition,), children, start,
                        self.tokens[self.i-1].end, loop_index=index)
        if head.kind != "ID":
            raise SchemaError(f"UNSUPPORTED_GOCO_FORM {head.text!r} at byte {head.start}")
        lhs = self.expr(7)
        op = self.take()
        if op.text not in {"=", "+=", "-="} or lhs.kind != "ID":
            raise SchemaError(f"UNSUPPORTED_GOCO_FORM assignment operator {op.text!r}")
        rhs = (self.expr(),)
        end = self._terminator().end
        return Stmt("UPDATE", op.text, (lhs, *rhs), (), start, end)

    def _terminator(self) -> Tok:
        if self.peek("."): return self.take()
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
                    (left.kind == "ID" and left.value == "strings")):
                self.take(); member = self.take()
                left = Expr("MEMBER", member.text, (left,), left.start, member.end); continue
            if self.peek("("):
                if left.kind != "MEMBER" or left.children[0].value != "strings" or left.value not in {"SPLIT", "TO_NUMBER"}:
                    raise SchemaError("UNSUPPORTED_GOCO_FORM call")
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
    for child in stmt.alternate: yield from _walk_stmt(child)


def source_occurrence_inventory(program_id: str, source: str) -> dict[str, Any]:
    from .core_ir import compile_program
    program = compile_program(program_id, source)
    return {"schema_version": 1, "phase": PHASE, "program_id": program_id,
            "source_sha256": __import__("hashlib").sha256(source.encode("utf-8")).hexdigest(),
            "nodes": [i.__dict__ for i in program.items if i.kind == "NODE"],
            "edges": [i.__dict__ for i in program.items if i.kind == "EDGE"]}


def canonical_expression(expr: Expr, names: Mapping[str, str] | None = None, *,
                         symbols: Mapping[str, str] | None = None,
                         context: str = "ATOMIC", indicators: frozenset[str] = frozenset()) -> tuple[Any, ...]:
    """Only typed pure catalog operations; no general simplification."""
    from .core_ir import infer_type, integer_constant, ungroup
    expr = ungroup(expr)
    if symbols is None: raise SchemaError("typed equivalence context required")
    if context not in {"ATOMIC", "COMPUTED_VALUE", "LOCAL_PAIR_JOINT", "BOOLEAN_OR"}: raise SchemaError("unlisted equivalence context")
    if context in {"LOCAL_PAIR_JOINT", "BOOLEAN_OR"}:
        raise SchemaError("source-mapped indicator/Boolean flow proof is not implemented; caller indicator sets are not proof")
    if context == "COMPUTED_VALUE":
        value = integer_constant(expr)
        if value is not None: return ("INTEGER_CONSTANT", value)
    typ = infer_type(expr, symbols)
    names = names or {}
    if expr.kind == "ID": return ("ID", names.get(expr.value, expr.value), typ)
    children = [canonical_expression(c, names, symbols=symbols, context=context, indicators=indicators) for c in expr.children]
    op = expr.value
    if expr.kind == "BINARY" and op in {">", ">="}:
        op = "<" if op == ">" else "<="; children.reverse()
    if expr.kind == "BINARY" and op in COMMUTATIVE:
        if any(n.kind in {"CALL", "MEMBER", "INDEX"} for n in _walk_expr(expr)):
            raise SchemaError("commutative purity not proved")
        if any(n.kind=="BINARY" and n.value=="%" and integer_constant(n.children[1]) in {None,0} for n in _walk_expr(expr)):
            raise SchemaError("commutative totality not proved")
        children.sort(key=repr)
    return (expr.kind, op, typ, *children)


def alpha_bijection(left: Mapping[str, str], right: Mapping[str, str], names: Mapping[str, str]) -> None:
    if not isinstance(names, dict) or set(names) != set(left) or set(names.values()) != set(right) or len(set(names.values())) != len(names):
        raise SchemaError("incomplete/non-bijective alpha mapping")
    if any(left[a] != right[b] for a,b in names.items()): raise SchemaError("alpha type mismatch")


def expressions_equivalent(left: Expr, right: Expr, alpha_map: Mapping[str, str] | None = None, *,
                           left_symbols: Mapping[str, str] | None = None,
                           right_symbols: Mapping[str, str] | None = None,
                           context: str = "ATOMIC", indicators: frozenset[str] = frozenset()) -> bool:
    if left_symbols is None or right_symbols is None: raise SchemaError("typed equivalence context required")
    names = dict(alpha_map) if alpha_map is not None else {n:n for n in left_symbols}
    alpha_bijection(left_symbols, right_symbols, names)
    return canonical_expression(left,names,symbols=left_symbols,context=context,indicators=indicators) == canonical_expression(right,symbols=right_symbols,context=context,indicators=frozenset(names[n] for n in indicators))
