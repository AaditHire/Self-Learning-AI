"""Statement deletion and a fail-closed interpreter for the I1 builder subset.

This module never executes Python expressions or invokes a model/compiler.
Source offsets refer to the original text; enumeration uses preorder traversal.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Statement:
    kind: str
    start: int
    end: int
    text: str
    header: str = ""
    children: tuple[Statement, ...] = ()


def split_statements(source: str) -> tuple[Statement, ...]:
    """Return simple and block units, raising ValueError for malformed structure."""
    size = len(source)

    def quoted_end(pos: int) -> int:
        pos += 1
        while pos < size:
            if source[pos] == "\\":
                pos += 2
            elif source[pos] == '"':
                return pos + 1
            else:
                pos += 1
        raise ValueError("Unterminated string literal")

    def whitespace(pos: int) -> int:
        while pos < size and source[pos].isspace():
            pos += 1
        return pos

    def sequence(pos: int, in_block: bool) -> tuple[tuple[Statement, ...], int]:
        units = []
        while True:
            pos = whitespace(pos)
            if pos == size:
                if in_block:
                    raise ValueError("Unclosed block")
                return tuple(units), pos
            if source[pos] == "}":
                if not in_block:
                    raise ValueError("Unexpected closing brace")
                return tuple(units), pos + 1
            start = pos
            match = re.match(r"(IF|LOOP)\b", source[pos:])
            if match:
                kind = match[1]
                pos = whitespace(pos + len(kind))
                if pos == size or source[pos] != "(":
                    raise ValueError(f"{kind} requires a parenthesized header")
                opening, depth = pos, 1
                pos += 1
                while pos < size and depth:
                    if source[pos] == '"':
                        pos = quoted_end(pos)
                        continue
                    if source[pos] == "(":
                        depth += 1
                    elif source[pos] == ")":
                        depth -= 1
                    pos += 1
                if depth:
                    raise ValueError(f"Unclosed {kind} header")
                header = source[opening + 1:pos - 1].strip()
                pos = whitespace(pos)
                if pos == size or source[pos] != "{":
                    raise ValueError(f"{kind} requires a brace-delimited body")
                children, pos = sequence(pos + 1, True)
                units.append(Statement(kind, start, pos, source[start:pos], header, children))
                continue
            while pos < size:
                char = source[pos]
                if char == '"':
                    pos = quoted_end(pos)
                    continue
                if char in "{}":
                    raise ValueError("Brace outside IF/LOOP block")
                if char == "." and (pos + 1 == size or not re.match(r"[A-Za-z_]", source[pos + 1])):
                    pos += 1
                    units.append(Statement("simple", start, pos, source[start:pos]))
                    break
                pos += 1
            else:
                raise ValueError("Simple statement lacks terminating period")

    return sequence(0, False)[0]


def enumerate_mutants(source: str) -> tuple[list[tuple[int, str, str]], dict[str, int]]:
    """Delete each complete unit once, including children of deleted blocks."""
    mutants: list[tuple[int, str, str]] = []
    counts = {"total": 0, "simple": 0, "IF": 0, "LOOP": 0}

    def visit(units: tuple[Statement, ...]) -> None:
        for unit in units:
            index = len(mutants)
            description = f"delete {unit.kind} at [{unit.start}:{unit.end}): {unit.text}"
            mutants.append((index, description, source[:unit.start] + source[unit.end:]))
            counts[unit.kind] += 1
            visit(unit.children)

    visit(split_statements(source))
    counts["total"] = len(mutants)
    return mutants, counts


class _Invalid(ValueError):
    pass


class _Timeout(Exception):
    pass


_TOKEN = re.compile(r'\s*("(?:[^"\\]|\\.)*"|\d+|[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)?|==|!=|<=|>=|[+*%<>()\[\],-])')
_NAME = r"[A-Za-z_][A-Za-z_0-9]*"
_PRECEDENCE = {"==": 1, "!=": 1, "<": 1, ">": 1, "<=": 1, ">=": 1,
               "+": 2, "-": 2, "*": 3, "%": 3}


def _expression(text: str) -> tuple:
    tokens, pos = [], 0
    text = text.strip()
    while pos < len(text):
        match = _TOKEN.match(text, pos)
        if not match:
            raise _Invalid("Unsupported expression token")
        tokens.append(match[1])
        pos = match.end()
    cursor = 0

    def take(expected: str | None = None) -> str:
        nonlocal cursor
        if cursor == len(tokens) or (expected is not None and tokens[cursor] != expected):
            raise _Invalid("Malformed expression")
        value = tokens[cursor]
        cursor += 1
        return value

    def peek() -> str:
        return tokens[cursor] if cursor < len(tokens) else ""

    def parse(minimum: int = 0) -> tuple:
        token = take()
        if token in ("+", "-"):
            node = ("unary", token, parse(4))
        elif token == "(":
            node = parse()
            take(")")
        elif token == "[":
            items = []
            if peek() != "]":
                items.append(parse())
                while peek() == ",":
                    take(",")
                    items.append(parse())
            take("]")
            node = ("array", tuple(items))
        elif token.startswith('"'):
            node = ("literal", json.loads(token))
        elif token.isdigit():
            node = ("literal", float(token))
        elif re.fullmatch(_NAME + r"(?:\." + _NAME + r")?", token):
            if peek() == "(":
                take("(")
                args = []
                if peek() != ")":
                    args.append(parse())
                    while peek() == ",":
                        take(",")
                        args.append(parse())
                take(")")
                node = ("call", token, tuple(args))
            else:
                node = ("name", token)
        else:
            raise _Invalid("Unsupported expression")
        while peek() == "[":
            take("[")
            node = ("index", node, parse())
            take("]")
        while peek() in _PRECEDENCE and _PRECEDENCE[peek()] >= minimum:
            operator = take()
            node = ("binary", operator, node, parse(_PRECEDENCE[operator] + 1))
        return node

    result = parse()
    if cursor != len(tokens):
        raise _Invalid("Trailing expression tokens")
    return result


def _type(node: tuple, names: dict[str, str], imported: set[str]) -> str:
    kind = node[0]
    if kind == "literal":
        return "SENTENCE" if isinstance(node[1], str) else "NUMBER"
    if kind == "name":
        if node[1] not in names:
            raise _Invalid(f"Undefined name: {node[1]}")
        return names[node[1]]
    if kind == "array":
        types = {_type(x, names, imported) for x in node[1]}
        if len(types) != 1 or next(iter(types)) not in ("NUMBER", "SENTENCE"):
            raise _Invalid("Unsupported array literal")
        return next(iter(types)) + "[]"
    if kind == "index":
        array = _type(node[1], names, imported)
        if array not in ("NUMBER[]", "SENTENCE[]") or _type(node[2], names, imported) != "NUMBER":
            raise _Invalid("Invalid array index expression")
        return array[:-2]
    if kind == "call":
        function, args = node[1:]
        if "strings" not in imported:
            raise _Invalid("strings module is not imported")
        types = tuple(_type(x, names, imported) for x in args)
        if function == "strings.SPLIT" and types == ("SENTENCE", "SENTENCE") and args[1] == ("literal", "|"):
            return "SENTENCE[]"
        if function == "strings.TO_NUMBER" and types == ("SENTENCE",):
            return "NUMBER"
        raise _Invalid("Unsupported library call")
    operands = node[2:] if kind in ("binary", "unary") else ()
    if not operands or any(_type(x, names, imported) != "NUMBER" for x in operands):
        raise _Invalid("Numeric operands required")
    return "BOOL" if kind == "binary" and node[1] in ("==", "!=", "<", ">", "<=", ">=") else "NUMBER"


def _compile(units: tuple[Statement, ...], names: dict[str, str], imported: set[str]) -> list[tuple]:
    instructions = []

    def expression(text: str, expected: str) -> tuple:
        node = _expression(text)
        if _type(node, names, imported) != expected:
            raise _Invalid(f"Expected {expected} expression")
        return node

    for index, unit in enumerate(units):
        if unit.kind == "IF":
            condition = expression(unit.header, "BOOL")
            instructions.append(("if", condition, _compile(unit.children, names.copy(), imported.copy())))
        elif unit.kind == "LOOP":
            forward = re.fullmatch(r"NUMBER\s+(" + _NAME + r")\s*=\s*(.*?)\s+TILL\s+(.*),\s*(" + _NAME + r")\s*\+\+", unit.header)
            if forward:
                name, initial, condition, increment = forward.groups()
                if name != increment or name in names:
                    raise _Invalid("Invalid forward loop counter")
                initial = expression(initial, "NUMBER")
                local_names = names | {name: "NUMBER"}
                condition = _expression(condition)
                if _type(condition, local_names, imported) != "BOOL":
                    raise _Invalid("Loop condition must be a comparison")
                body = _compile(unit.children, local_names, imported.copy())
                instructions.append(("forward", name, initial, condition, body))
            else:
                condition = expression(unit.header, "BOOL")
                instructions.append(("reverse", condition, _compile(unit.children, names.copy(), imported.copy())))
        else:
            text = unit.text[:-1].strip()
            if text == "IMPORT strings":
                imported.add("strings")
                instructions.append(("import",))
                continue
            declaration = re.fullmatch(r"(NUMBER|SENTENCE)(\[\])?\s+(" + _NAME + r")(?:\s*=\s*(.*))?", text)
            if declaration:
                base, array, name, initial = declaration.groups()
                value_type = base + (array or "")
                if name in names or (array and initial is None):
                    raise _Invalid("Duplicate or unsupported declaration")
                node = expression(initial, value_type) if initial is not None else ("literal", 0.0 if base == "NUMBER" else "")
                names[name] = value_type
                instructions.append(("declare", name, node))
                continue
            input_match = re.fullmatch(r"INPUT\(\s*(" + _NAME + r")\s*\)", text)
            if input_match:
                name = input_match[1]
                if names.get(name) not in ("NUMBER", "SENTENCE"):
                    raise _Invalid("INPUT requires a declared scalar")
                instructions.append(("input", name, names[name]))
                continue
            display = re.fullmatch(r"DISPLAYNL\((.*)\)", text)
            if display:
                instructions.append(("display", expression(display[1], "NUMBER")))
                continue
            assignment = re.fullmatch(r"(" + _NAME + r")\s*(\+=|-=|=)\s*(.*)", text)
            if assignment:
                name, operator, value = assignment.groups()
                # OBSERVED pinned-compiler behavior (A-F): consecutive total+=
                # statements reject a bare indicator or two-indicator product
                # in the first statement (A, C); parentheses permit it (B, D).
                # A closing brace (E) or an intervening IF (F) permits the bare
                # product. This check is limited to these accumulation forms.
                if (name == "total" and operator == "+="
                        and re.fullmatch(r"hit[PQRS](?:\s*\*\s*hit[PQRS])?", value)
                        and index + 1 < len(units)
                        and re.match(r"total\s*\+=", units[index + 1].text)):
                    raise _Invalid("Observed pinned-compiler rejection of consecutive bare accumulations")
                if name not in names or (operator != "=" and names[name] != "NUMBER"):
                    raise _Invalid("Assignment requires a declared compatible name")
                instructions.append(("assign", name, operator, expression(value, names[name])))
                continue
            raise _Invalid(f"Unsupported statement: {text}")
    return instructions


def _evaluate(node: tuple, values: dict) -> object:
    kind = node[0]
    if kind == "literal":
        return node[1]
    if kind == "name":
        return values[node[1]]
    if kind == "array":
        return [_evaluate(x, values) for x in node[1]]
    if kind == "index":
        array, index = _evaluate(node[1], values), _evaluate(node[2], values)
        if index != int(index) or index < 0 or index >= len(array):
            raise _Invalid("Array index out of bounds")
        return array[int(index)]
    if kind == "call":
        args = [_evaluate(x, values) for x in node[2]]
        if node[1] == "strings.SPLIT":
            result = args[0].split("|")
            while len(result) > 1 and result[-1] == "":
                result.pop()
            return result
        return _number(args[0])
    if kind == "unary":
        value = _evaluate(node[2], values)
        return value if node[1] == "+" else -value
    left, right = _evaluate(node[2], values), _evaluate(node[3], values)
    operator = node[1]
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "%":
        return math.fmod(left, right)
    return {"==": lambda: left == right, "!=": lambda: left != right,
            "<": lambda: left < right, ">": lambda: left > right,
            "<=": lambda: left <= right, ">=": lambda: left >= right}[operator]()


def _number(text: str) -> float:
    value = float(text)
    if not math.isfinite(value):
        raise _Invalid("Nonfinite numeric input")
    return value


def interpret(source: str, stdin: str = "", *, step_limit: int = 10_000) -> tuple:
    """Return (ok, stdout), (fail,), or (timeout,); validate even unexecuted code."""
    try:
        if not isinstance(step_limit, int) or step_limit < 1:
            raise _Invalid("Invalid step limit")
        program = _compile(split_statements(source), {}, set())
        values, output = {}, []
        inputs = iter(stdin.splitlines())
        steps = 0

        def tick() -> None:
            nonlocal steps
            steps += 1
            if steps > step_limit:
                raise _Timeout

        def execute(instructions: list[tuple]) -> None:
            for instruction in instructions:
                tick()
                kind, *args = instruction
                if kind == "declare":
                    values[args[0]] = _evaluate(args[1], values)
                elif kind == "input":
                    text = next(inputs)
                    values[args[0]] = _number(text) if args[1] == "NUMBER" else text
                elif kind == "assign":
                    name, operator, node = args
                    value = _evaluate(node, values)
                    values[name] = value if operator == "=" else values[name] + (value if operator == "+=" else -value)
                elif kind == "display":
                    number = _evaluate(args[0], values)
                    if not math.isfinite(number):
                        raise _Invalid("Nonfinite output")
                    output.append(str(float(number)))
                elif kind == "if":
                    if _evaluate(args[0], values):
                        execute(args[1])
                elif kind in ("forward", "reverse"):
                    if kind == "forward":
                        name, initial, condition, body = args
                        values[name] = _evaluate(initial, values)
                    else:
                        condition, body = args
                    while True:
                        tick()
                        if not _evaluate(condition, values):
                            break
                        execute(body)
                        if kind == "forward":
                            values[name] += 1.0
                    if kind == "forward":
                        del values[name]

        execute(program)
        return ("ok", "\n".join(output).strip())
    except _Timeout:
        return ("timeout",)
    except (ValueError, TypeError, KeyError, IndexError, StopIteration, OverflowError, ZeroDivisionError, RecursionError):
        return ("fail",)
