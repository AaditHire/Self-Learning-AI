"""Prospective CONF1 v2 structural-template adjudicator; no model access."""

from __future__ import annotations

import re


TOKEN = re.compile(
    r"(?P<WS>\s+)|(?P<COMMENT>//[^\n]*|/\*[\s\S]*?\*/)|"
    r'(?P<STRING>"(?:\\.|[^"\\])*")|'
    r"(?P<CHAR>'(?:\\.|[^'\\])?')|"
    r"(?P<NUMERIC>\d+(?:\.\d+)?)|"
    r"(?P<OP>\+=|-=|\*=|/=|%=|==|!=|<=|>=|\+\+|--|&&|\|\||[+*/%<>=!\-])|"
    r"(?P<IDENT>[A-Za-z_][A-Za-z_0-9]*)|(?P<PUNCT>[\[\](){},.;])"
)

_KEYWORDS = (
    "IMPORT NUMBER LETTER SENTENCE LOGIC TRUE FALSE DO NEW DISPLAY DISPLAYNL INPUT "
    "IF ELSEIF ELSE LOOP TILL BREAK CONTINUE FUNCTION RETURN RETURNS SWITCH CASE DEFAULT "
    "AND OR NOT"
).split()
KEYWORD_FORMS = {form: canonical for canonical in _KEYWORDS
                 for form in (canonical, canonical.lower(), canonical.title())}
KEYWORD_FORMS.update({"DisplayNL": "DISPLAYNL", "Displaynl": "DISPLAYNL",
                      "ElseIf": "ELSEIF", "Returns": "RETURNS"})
OPEN_TO_CLOSE = {"(": ")", "[": "]", "{": "}"}
CLOSE_TO_OPEN = {v: k for k, v in OPEN_TO_CLOSE.items()}


def _scan(source: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    pos = 0
    while pos < len(source):
        match = TOKEN.match(source, pos)
        if match is None:
            raise ValueError(f"unrecognized GOCO token at character {pos}")
        pos = match.end()
        if match.lastgroup not in {"WS", "COMMENT"}:
            tokens.append((match.lastgroup, match.group()))
    return tokens


def canonical_tree(source: str) -> tuple:
    """Ordered, nested GOCO token tree with alpha-renamed variable uses."""
    raw = _scan(source)
    imported: set[str] = set()
    for i in range(len(raw) - 2):
        if (raw[i][0] == "IDENT" and KEYWORD_FORMS.get(raw[i][1]) == "IMPORT"
                and raw[i + 1][0] == "IDENT" and raw[i + 2] == ("PUNCT", ".")):
            imported.add(raw[i + 1][1])
    member_indices: set[int] = set()
    namespace_indices: set[int] = set()
    for i in range(len(raw) - 3):
        if (raw[i][0] == "IDENT" and raw[i][1] in imported
                and raw[i + 1] == ("PUNCT", ".") and raw[i + 2][0] == "IDENT"
                and raw[i + 3] == ("PUNCT", "(")):
            namespace_indices.add(i)
            member_indices.add(i + 2)
    names: dict[str, str] = {}
    flat: list[str] = []
    for i, (kind, value) in enumerate(raw):
        if kind == "IDENT":
            keyword = KEYWORD_FORMS.get(value)
            if keyword is not None:
                flat.append("KW:" + keyword)
            elif value in imported and (i in namespace_indices or
                    (i > 0 and raw[i - 1][0] == "IDENT" and
                     KEYWORD_FORMS.get(raw[i - 1][1]) == "IMPORT")):
                flat.append("LIB:" + value)
            elif i in member_indices:
                flat.append("API:" + value)
            else:
                flat.append(names.setdefault(value, f"VAR{len(names)}"))
        elif kind == "NUMERIC":
            flat.append("NUM")
        elif kind in {"STRING", "CHAR"}:
            flat.append(kind)
        else:
            flat.append(value)
    stack: list[list] = [[]]
    openings: list[str] = []
    for token in flat:
        if token in OPEN_TO_CLOSE:
            stack.append([])
            openings.append(token)
        elif token in CLOSE_TO_OPEN:
            if not openings or openings[-1] != CLOSE_TO_OPEN[token]:
                raise ValueError("unbalanced GOCO grouping")
            opening = openings.pop()
            children = tuple(stack.pop())
            stack[-1].append(("GROUP", opening, children))
        else:
            stack[-1].append(token)
    if openings:
        raise ValueError("unbalanced GOCO grouping")
    return tuple(stack[0])


def adjudicate_v2(candidate: str, consumed: str, coarse_equal: bool) -> str:
    if canonical_tree(candidate) == canonical_tree(consumed):
        return "PROHIBITED_STRUCTURAL_TEMPLATE_REUSE"
    if coarse_equal:
        return "COARSE_AST_EQUALITY_ONLY"
    return "STRUCTURALLY_DISTINCT"
