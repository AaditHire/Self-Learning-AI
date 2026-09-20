# GOCO language reference — Phase 1R v1

This versioned reference describes the interpreter pinned at GOCO commit
`6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`. The grammar and executable
behavior, rather than the upstream README, are authoritative.

## Critical source-file contract

A GOCO file is a sequence of top-level statements executed in file order.
There is no package declaration, program declaration, class, or mandatory
entry function. Source begins directly with an `IMPORT`, declaration,
function declaration, or executable statement.

Never emit `package main`, `func main`, `PROGRAM`, `BEGIN`, `END`, `READLINE`,
`PRINT`, `STRING`, `INT`, or Go imports. Those constructs are not GOCO.

Return only source code. Markdown fences and explanations are presentation,
not language syntax. Ordinary statements end with a period (`.`). `IF`,
`SWITCH`, and `LOOP` blocks do not take a period after the closing brace.
Function declarations do end with `}.` or `} RETURNS TYPE.`.

## Types, variables, and assignment

The four scalar types are `NUMBER`, `SENTENCE`, `LETTER`, and `LOGIC`.
Boolean literals are `TRUE` and `FALSE`. Keywords are case-insensitive.

```text
NUMBER count = 3.
SENTENCE message = "hello".
LETTER initial = 'g'.
LOGIC ready = TRUE.
count += 2.
```

Numeric output uses floating-point form, such as `5.0`. Identifiers must not
reuse language keywords or built-in function names.

## Input and output

`INPUT(variable).` is a statement: it assigns one complete input line to an
already declared variable. It does not return a value and takes no prompt.
`DISPLAY(expression).` prints without a newline; `DISPLAYNL(expression).`
prints with a newline. Do not print input prompts or debugging text.

The pinned runtime is reliable for one `INPUT` per execution. When a task gives
multiple values, read one `SENTENCE`, split it, and convert the pieces.

Complete single-input file:

```text
NUMBER value.
INPUT(value).
DISPLAYNL(value * 2).
```

Complete delimited-input file:

```text
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
NUMBER left = strings.TO_NUMBER(parts[0]).
NUMBER right = strings.TO_NUMBER(parts[1]).
DISPLAYNL(left + right).
```

## Expressions

- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logic: `AND`, `OR`, `NOT`
- Assignment: `=`, `+=`, `-=`, `*=`, `/=`, `%=`
- Increment/decrement statements: `x++.`, `x--.`, `++x.`, `--x.`

Use `SENTENCE`, not `STRING`. For text equality and other string operations,
prefer the `strings` library rather than scalar comparison operators.

## Conditionals

The keyword is one word: `ELSEIF`, not `ELSE IF`.

```text
IF (score >= 90) {
    DISPLAYNL("high").
} ELSEIF (score >= 50) {
    DISPLAYNL("middle").
} ELSE {
    DISPLAYNL("low").
}
```

## Loops

```text
NUMBER total = 0.
LOOP (NUMBER i = 1 TILL i <= 4, i++) {
    total += i.
}
DISPLAYNL(total).
```

For-style syntax is `LOOP (NUMBER i = 0 TILL i < limit, i++) { ... }`.
Do-while syntax is `DO { ... } LOOP (condition).`. `BREAK.` and `CONTINUE.`
are valid inside loops.

## Functions

Parameters require types. A function declaration always has a final period
after the closing declaration. A returning function uses `RETURNS TYPE`.

```text
FUNCTION square(NUMBER x) {
    RETURN x * x.
} RETURNS NUMBER.

NUMBER inputValue.
INPUT(inputValue).
DISPLAYNL(square(inputValue)).
```

The pinned semantic validator registers a function only after validating its
body. Consequently, self-recursion and forward calls are rejected as undefined.
Do not use recursion. Declare a function before any later function or statement
that calls it.

## Arrays

Arrays use zero-based indexing and append `[]` to the element type.

```text
NUMBER[] values = [4, 2, 9].
values[1] = 7.
DISPLAYNL(values[0]).
```

`NEW NUMBER[5]` creates a sized array. Direct literals and indexing require no
import. `IMPORT arrays.` enables operations including `arrays.LENGTH`,
`PUSH`, `POP`, `REVERSE`, `SORT`, `JOIN`, `SUM`, `AVG`, `CONCAT`, `APPEND`,
`FIND`, `CONTAINS`, `COUNT`, `FILL`, and `SLICE`. The grammar also recognizes
the legacy standalone built-ins `LENGTH`, `GET`, `SET`, `PUSH`, and `POP`.

## String and math libraries

Use `IMPORT strings.` for `strings.LENGTH`, `UPPER`, `LOWER`, `REVERSE`,
`CONTAINS`, `REPLACE`, `SUB`, `CHARAT`, `COUNT`, `FIND`, `STARTSWITH`,
`ENDSWITH`, `EQUALS`, `SPLIT`, `CONCAT`, `REPEAT`, `TRIM`, `TO_NUMBER`, and
`TO_SENTENCE`. The pinned `strings.TRIM(text, chars)` takes two arguments: an
empty second argument trims ordinary surrounding whitespace; otherwise it
trims characters from the supplied set at both ends.

Use `IMPORT math.` for `ABS`, `POW`, `SQRT`, `MIN`, `MAX`, `FLOOR`, `CEIL`,
`ROUND`, `CLAMP`, `SIGN`, trigonometric functions, logarithms, and degree/radian
conversion. Constants are `math.PI` and `math.E`.

## Unsupported or unreliable constructs

- no `PROGRAM` wrapper, package, class, or `main` function requirement;
- no Go syntax, Go imports, `func`, `fmt`, or `strconv`;
- no `STRING` type or `READLINE` function;
- no expression-valued `INPUT` and no prompt argument to `INPUT`;
- no self-recursion or forward function calls under the pinned validator;
- no reliable sequence of multiple `INPUT` statements in one execution;
- no assumption that general scalar operators support `SENTENCE` or `LETTER`
  comparison—use the string library where applicable.
- avoid multiple simple assignments/increments adjacent in one loop body; the
  pinned parser has a known lookahead edge case. A for-style loop update is the
  reliable form when it fits the algorithm.
