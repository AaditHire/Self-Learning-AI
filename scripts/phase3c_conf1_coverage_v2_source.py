"""Closed, offset-preserving GOCO source inventory for coverage-v2 certificates.

This parser recognizes the fixed CONF1 subset. Unknown tokens and statements fail
closed; it is not a replacement for the pinned compiler's syntax or semantics.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    value: str
    offset: int


@dataclass
class Statement:
    kind: str
    offset: int
    name: str = ""
    operator: str = ""
    expression: tuple[Token, ...] = ()
    header: tuple[Token, ...] = ()
    children: tuple["Statement", ...] = ()


TOKEN = re.compile(r'\s+|"(?:[^"\\]|\\.)*"|[A-Za-z_]\w*|\d+|<=|>=|==|!=|\+=|-=|\+\+|--|&&|\|\||[{}()\[\],.%+*<>=!-]')
IDENT = re.compile(r"[A-Za-z_]\w*\Z")


def tokenize(source: str) -> tuple[Token, ...]:
    tokens = []
    cursor = 0
    for match in TOKEN.finditer(source):
        if match.start() != cursor:
            raise ValueError(f"UNCLASSIFIED_REQUIREMENT:TOKEN:{cursor}")
        cursor = match.end()
        if not match.group().isspace():
            tokens.append(Token(match.group(), match.start()))
    if cursor != len(source):
        raise ValueError(f"UNCLASSIFIED_REQUIREMENT:TOKEN:{cursor}")
    return tuple(tokens)


def words(tokens: tuple[Token, ...]) -> tuple[str, ...]:
    return tuple(token.value for token in tokens)


def identifiers(tokens: tuple[Token, ...]) -> set[str]:
    return {x.value for x in tokens if IDENT.fullmatch(x.value)} - {
        "NUMBER", "SENTENCE", "INPUT", "DISPLAYNL", "LOOP", "TILL", "IF", "IMPORT",
        "strings", "SPLIT", "TO_NUMBER"}


class Parser:
    def __init__(self, source: str):
        self.tokens = tokenize(source)
        self.pos = 0

    def peek(self) -> str:
        return self.tokens[self.pos].value if self.pos < len(self.tokens) else ""

    def take(self, value: str | None = None) -> Token:
        if self.pos >= len(self.tokens):
            raise ValueError("UNCLASSIFIED_REQUIREMENT:UNEXPECTED_EOF")
        token = self.tokens[self.pos]
        if value is not None and token.value != value:
            raise ValueError(f"UNCLASSIFIED_REQUIREMENT:EXPECTED_{value}:{token.offset}")
        self.pos += 1
        return token

    def group(self, left: str, right: str) -> tuple[Token, ...]:
        self.take(left)
        start = self.pos
        depth = 1
        while self.pos < len(self.tokens):
            token = self.take()
            if token.value == left:
                depth += 1
            elif token.value == right:
                depth -= 1
                if depth == 0:
                    return self.tokens[start:self.pos - 1]
        raise ValueError(f"UNCLASSIFIED_REQUIREMENT:UNCLOSED_{left}")

    def expression(self) -> tuple[Token, ...]:
        start = self.pos
        paren = bracket = 0
        while self.pos < len(self.tokens):
            value = self.peek()
            member = (value == "." and self.pos > start and self.pos + 1 < len(self.tokens)
                      and self.tokens[self.pos - 1].value == "strings"
                      and self.tokens[self.pos + 1].value in {"SPLIT", "TO_NUMBER"})
            if value == "." and paren == 0 and bracket == 0 and not member:
                break
            if value == "(": paren += 1
            elif value == ")": paren -= 1
            elif value == "[": bracket += 1
            elif value == "]": bracket -= 1
            if paren < 0 or bracket < 0:
                raise ValueError("UNCLASSIFIED_REQUIREMENT:EXPRESSION_GROUP")
            self.pos += 1
        if self.pos >= len(self.tokens) or paren or bracket:
            raise ValueError("UNCLASSIFIED_REQUIREMENT:EXPRESSION_END")
        result = self.tokens[start:self.pos]
        self.take(".")
        if not result:
            raise ValueError("UNCLASSIFIED_REQUIREMENT:EMPTY_EXPRESSION")
        self.validate_expression(result)
        return result

    @staticmethod
    def validate_expression(tokens: tuple[Token, ...]) -> None:
        vals = words(tokens)
        for i, value in enumerate(vals):
            if value == ".":
                if not (i > 0 and i + 1 < len(vals) and vals[i - 1] == "strings"
                        and vals[i + 1] in {"SPLIT", "TO_NUMBER"}):
                    raise ValueError(f"UNCLASSIFIED_REQUIREMENT:MEMBER:{tokens[i].offset}")
            elif IDENT.fullmatch(value) and i + 1 < len(vals) and vals[i + 1] == "(":
                if value not in {"SPLIT", "TO_NUMBER"}:
                    raise ValueError(f"UNCLASSIFIED_REQUIREMENT:CALL:{tokens[i].offset}")
            elif value.startswith('"') and value != '"|"':
                raise ValueError(f"UNCLASSIFIED_REQUIREMENT:STRING:{tokens[i].offset}")
            elif value in {"&&", "||", "!", "!="}:
                raise ValueError(f"UNCLASSIFIED_REQUIREMENT:OPERATOR:{tokens[i].offset}")

    def block(self, *, nested: bool = False) -> tuple[Statement, ...]:
        if nested:
            self.take("{")
        result = []
        while self.peek() and self.peek() != "}":
            result.append(self.statement())
        if nested:
            self.take("}")
        elif self.peek() == "}":
            raise ValueError("UNCLASSIFIED_REQUIREMENT:EXTRA_BRACE")
        return tuple(result)

    def statement(self) -> Statement:
        token = self.take()
        kind = token.value
        if kind == "IMPORT":
            name = self.take().value
            self.take(".")
            return Statement("IMPORT", token.offset, name=name)
        if kind in {"NUMBER", "SENTENCE"}:
            array = False
            if self.peek() == "[":
                self.take("["); self.take("]")
                array = True
            name = self.take().value
            if not IDENT.fullmatch(name):
                raise ValueError(f"UNCLASSIFIED_REQUIREMENT:DECLARATION:{token.offset}")
            if self.peek() == "=":
                self.take("=")
                expr = self.expression()
            else:
                self.take(".")
                expr = ()
            return Statement(f"{kind}{'_ARRAY' if array else ''}_DECLARATION", token.offset,
                             name=name, expression=expr)
        if kind in {"INPUT", "DISPLAYNL"}:
            expr = self.group("(", ")")
            self.take(".")
            self.validate_expression(expr)
            return Statement(kind, token.offset, expression=expr)
        if kind in {"LOOP", "IF"}:
            header = self.group("(", ")")
            self.validate_expression(header) if kind == "IF" else None
            return Statement(kind, token.offset, header=header,
                             children=self.block(nested=True))
        if IDENT.fullmatch(kind):
            operator = self.take().value
            if operator not in {"=", "+=", "-=", "++", "--"}:
                raise ValueError(f"UNCLASSIFIED_REQUIREMENT:ASSIGNMENT:{token.offset}")
            if operator in {"++", "--"}:
                self.take(".")
                expr = ()
            else:
                expr = self.expression()
            return Statement("ASSIGNMENT", token.offset, name=kind, operator=operator,
                             expression=expr)
        raise ValueError(f"UNCLASSIFIED_REQUIREMENT:STATEMENT:{token.offset}:{kind}")


def parse(source: str) -> tuple[Statement, ...]:
    parser = Parser(source)
    statements = parser.block()
    if parser.pos != len(parser.tokens):
        raise ValueError("UNCLASSIFIED_REQUIREMENT:TRAILING_SOURCE")
    return statements


def flatten(statements: tuple[Statement, ...]):
    for statement in statements:
        yield statement
        yield from flatten(statement.children)


def source_certificate(record: dict) -> tuple[list[dict], list[str], list[dict]]:
    """Return reference-only proofs, failures, and offset-preserving inventory."""
    try:
        statements = parse(record["source"])
    except ValueError as exc:
        return [], [str(exc)], []
    flat = list(flatten(statements))
    inventory = [{"construct": x.kind, "offset": x.offset, "name": x.name,
                  "operator": x.operator, "classification": "TASK_ESSENTIAL"} for x in flat]
    failures = []
    reference_only = []
    inputs = [s for s in flat if s.kind == "INPUT"]
    loops = [s for s in flat if s.kind == "LOOP"]
    displays = [s for s in flat if s.kind == "DISPLAYNL"]
    if len(inputs) != 1 or len(words(inputs[0].expression)) != 1:
        failures.append("API_INPUT_MISSING")
        return reference_only, failures, inventory
    input_var = words(inputs[0].expression)[0]
    if not loops:
        failures.append("LOOP_MISSING")
    if len(displays) != 1 or len(words(displays[0].expression)) != 1:
        failures.append("OUTPUT_MISSING")
    output_var = words(displays[0].expression)[0] if displays else ""
    if record["domain"] == "numeric_iteration":
        _numeric_certificate(statements, loops, input_var, output_var, failures)
    else:
        _array_certificate(statements, loops, input_var, output_var, failures)
    _classify_extras(record, statements, flat, reference_only, failures, inventory)
    _inventory_expression_tokens(record, flat, inventory, failures)
    return reference_only, failures, inventory


def _numeric_certificate(statements, loops, input_var, output_var, failures):
    if len(loops) != 1:
        failures.append("NUMERIC_LOOP_COUNT")
        return
    loop = loops[0]
    header = words(loop.header)
    # Closed forms: counted FOR-style TILL header or explicit condition plus
    # body update. Identifier spelling and formatting are incidental.
    if "TILL" in header:
        try:
            till = header.index("TILL")
            comma = header.index(",", till)
            init = header[:till]
            cond = header[till + 1:comma]
            update = header[comma + 1:]
            if (len(init) < 4 or init[0] != "NUMBER" or init[2] != "="
                    or len(cond) < 3 or cond[0] != init[1]
                    or cond[1] not in {"<", "<="} or input_var not in cond[2:]
                    or update != (init[1], "++")):
                raise ValueError
        except (ValueError, IndexError):
            failures.append("NUMERIC_LOOP_HEADER_INVALID")
            return
        iterator = init[1]
    else:
        if (len(header) < 3 or header[1] not in {"<", "<=", ">", ">="}
                or input_var not in header[2:]):
            failures.append("NUMERIC_LOOP_HEADER_INVALID")
            return
        iterator = header[0]
        initializers = [s for s in statements if s.kind == "NUMBER_DECLARATION" and s.name == iterator]
        updates = [s for s in loop.children if s.kind == "ASSIGNMENT" and
                   s.name == iterator and s.operator in {"++", "--", "+=", "-="}]
        if len(initializers) != 1 or len(updates) != 1:
            failures.append("NUMERIC_LOOP_HEADER_INVALID")
    if not any(s.kind == "ASSIGNMENT" and s.name == output_var for s in flatten(loop.children)):
        failures.append("NUMERIC_ACCUMULATOR_DISCONNECTED")
    if not any(s.kind == "NUMBER_DECLARATION" and s.name == output_var for s in statements):
        failures.append("NUMERIC_OUTPUT_UNDECLARED")


def _array_certificate(statements, loops, input_var, output_var, failures):
    imports = [s for s in statements if s.kind == "IMPORT" and s.name == "strings"]
    if len(imports) != 1:
        failures.append("ARRAY_LIBRARY_IMPORT_MISSING")
    parts = []
    for s in statements:
        if s.kind == "SENTENCE_ARRAY_DECLARATION" and words(s.expression) == (
                "strings", ".", "SPLIT", "(", input_var, ",", '"|"', ")"):
            parts.append(s.name)
    if len(parts) != 1:
        failures.append("ARRAY_SPLIT_CHAIN_MISSING")
        return
    conversions = {}
    for s in statements:
        expr = words(s.expression)
        if (s.kind == "NUMBER_DECLARATION" and len(expr) == 9
                and expr[:5] == ("strings", ".", "TO_NUMBER", "(", parts[0])
                and expr[5] == "[" and expr[7:] == ("]", ")")
                and expr[6] in {"0", "1", "2", "3"}):
            conversions[int(expr[6])] = s.name
    if set(conversions) != {0, 1, 2, 3}:
        failures.append("ARRAY_CONVERSION_CHAIN_INCOMPLETE")
        return
    arrays = [s for s in statements if s.kind == "NUMBER_ARRAY_DECLARATION"]
    if len(arrays) != 1:
        failures.append("ARRAY_VALUES_MISSING")
        return
    array = arrays[0]
    expected = ("[", conversions[0], ",", conversions[1], ",", conversions[2],
                ",", conversions[3], "]")
    if words(array.expression) != expected:
        failures.append("ARRAY_DATAFLOW_DISCONNECTED")
        return
    if len(loops) != 1:
        failures.append("ARRAY_ITERATION_DISCONNECTED")
        return
    loop = loops[0]
    header = words(loop.header)
    try:
        till = header.index("TILL")
        comma = header.index(",", till)
        iterator = header[1]
        if not (header[:till] == ("NUMBER", iterator, "=", "0")
                and header[till + 1:comma] == (iterator, "<", "4")
                and header[comma + 1:] == (iterator, "++")):
            raise ValueError
    except (ValueError, IndexError):
        failures.append("ARRAY_ITERATION_DISCONNECTED")
        return
    indexed = (array.name, "[", iterator, "]")
    active = False
    for branch in loop.children:
        if branch.kind != "IF":
            continue
        condition = words(branch.header)
        if not any(condition[i:i + 4] == indexed for i in range(len(condition) - 3)):
            continue
        if any(s.kind == "ASSIGNMENT" and s.name == output_var and
               s.operator in {"+=", "=", "-="} for s in flatten(branch.children)):
            active = True
    if not active:
        failures.append("ARRAY_DATAFLOW_DISCONNECTED")
    if not any(s.kind == "NUMBER_DECLARATION" and s.name == output_var for s in statements):
        failures.append("ARRAY_OUTPUT_UNDECLARED")


def _classify_extras(record, statements, flat, reference_only, failures, inventory):
    domain = record["domain"]
    declared = {s.name for s in flat if s.kind.endswith("_DECLARATION")}
    loop_iterators = set()
    for s in flat:
        if s.kind == "LOOP":
            vals = words(s.header)
            if vals:
                loop_iterators.add(vals[1] if vals[0] == "NUMBER" and len(vals) > 1 else vals[0])
    known_targets = declared | loop_iterators
    for s in flat:
        if s.kind == "IMPORT" and (domain != "array_reduction" or s.name != "strings"):
            failures.append(f"UNCLASSIFIED_REQUIREMENT:IMPORT:{s.offset}")
        if s.kind == "ASSIGNMENT" and s.name not in known_targets:
            failures.append(f"UNCLASSIFIED_REQUIREMENT:ASSIGNMENT_TARGET:{s.offset}")
        if s.kind.endswith("_DECLARATION") and s.expression:
            count = sum(s.name in identifiers(x.expression) or s.name in identifiers(x.header)
                        for x in flat if x is not s)
            if count == 0 and s.name not in {"total"}:
                reference_only.append({"construct": s.kind, "name": s.name,
                                       "offset": s.offset, "proof_code": "UNUSED_DECLARATION"})
                for entry in inventory:
                    if entry["offset"] == s.offset:
                        entry["classification"] = "REFERENCE_ONLY"
                        entry["proof_code"] = "UNUSED_DECLARATION"
    active_predicates = len(set(_predicate_leaves(record)))
    graph_nodes = 0
    agg = record["aggregation"]
    if agg["kind"] == "sum_per_item":
        graph_nodes = sum(node["op"] in {"or", "and", "gt", "ge", "lt", "le"}
                          for node in _walk(agg["expr"]))
    branches = [s for s in flat if s.kind == "IF"]
    live = [s for s in branches if words(s.header) != ("0", "==", "1")]
    for s in branches:
        if s not in live:
            reference_only.append({"construct": "IF", "offset": s.offset,
                                   "proof_code": "CONSTANT_FALSE_BRANCH"})
            for entry in inventory:
                if entry["offset"] == s.offset:
                    entry["classification"] = "REFERENCE_ONLY"
                    entry["proof_code"] = "CONSTANT_FALSE_BRANCH"
            for child in flatten(s.children):
                for entry in inventory:
                    if entry["offset"] == child.offset:
                        entry["classification"] = "REFERENCE_ONLY"
                        entry["proof_code"] = "CONSTANT_FALSE_BRANCH"
    if len(live) > active_predicates + graph_nodes:
        failures.append("UNCLASSIFIED_REQUIREMENT:EXTRA_IF")


def _inventory_expression_tokens(record, flat, inventory, failures):
    """Record every API call/index occurrence; reject unsupported live forms."""
    domain = record["domain"]
    calls = []
    indices = []
    for statement in flat:
        for tokens in (statement.expression, statement.header):
            vals = words(tokens)
            for i, token in enumerate(tokens):
                if i + 3 < len(vals) and vals[i:i + 3] == ("strings", ".", "SPLIT"):
                    calls.append(("strings.SPLIT", token.offset))
                elif i + 3 < len(vals) and vals[i:i + 3] == ("strings", ".", "TO_NUMBER"):
                    calls.append(("strings.TO_NUMBER", token.offset))
                if (i + 2 < len(vals) and IDENT.fullmatch(vals[i])
                        and vals[i + 1] == "[" and vals[i + 2] != "]"):
                    indices.append((vals[i], token.offset))
    for name, offset in calls:
        inventory.append({"construct": "API_CALL", "name": name, "offset": offset,
                          "classification": "TASK_ESSENTIAL"})
    for name, offset in indices:
        inventory.append({"construct": "ARRAY_INDEX", "name": name, "offset": offset,
                          "classification": "TASK_ESSENTIAL"})
    counts = {name: sum(call == name for call, _ in calls)
              for name in ("strings.SPLIT", "strings.TO_NUMBER")}
    if domain == "array_reduction":
        if counts != {"strings.SPLIT": 1, "strings.TO_NUMBER": 4}:
            failures.append("UNCLASSIFIED_REQUIREMENT:ARRAY_API_CALL_COUNT")
        if len(indices) != 5:
            failures.append("UNCLASSIFIED_REQUIREMENT:ARRAY_INDEX_COUNT")
    elif calls or indices:
        failures.append("UNCLASSIFIED_REQUIREMENT:UNEXPECTED_API_OR_INDEX")


def _walk(node):
    yield node
    for child in node.get("args", []):
        yield from _walk(child)
    if "arg" in node:
        yield from _walk(node["arg"])


def _predicate_leaves(record):
    agg = record["aggregation"]
    if agg["kind"] == "sum_per_item":
        return [x["name"] for x in _walk(agg["expr"]) if x["op"] == "pred"]
    return [agg["p"], agg["q"]]
