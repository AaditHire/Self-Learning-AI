# GOCO language reference — Phase 1 trusted snapshot

This reference describes the pinned GOCO compiler at commit
`6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`. It contains language syntax and
generic examples, not benchmark solutions.

## Program structure

GOCO is case-insensitive for language keywords. Ordinary statements end with a
period (`.`). Control blocks do not take a trailing period unless shown below.
Comments use `//` or `/* ... */`.

Primitive types are `NUMBER`, `SENTENCE`, `LETTER`, and `LOGIC`. Logic literals
are `TRUE` and `FALSE`. Numbers are represented and displayed as floating-point
values, so an integer-valued result commonly prints as `3.0`.

```text
NUMBER count = 3.
SENTENCE message = "hello".
LETTER initial = 'g'.
LOGIC ready = TRUE.
```

Declare without an initializer when input will assign the value:

```text
NUMBER value.
INPUT(value).
```

`INPUT(variable).` reads one complete input line and converts it to the declared
type. The interpreter emits an input prompt; evaluation removes that fixed
interpreter prompt. Programs should not print their own input prompts.

`DISPLAY(expression).` prints without a newline. `DISPLAYNL(expression).`
prints with a newline.

## Operators

- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logic: `AND`, `OR`, `NOT`
- Assignment: `=`, `+=`, `-=`, `*=`, `/=`, `%=`
- Increment/decrement: `x++.`, `x--.`, `++x.`, `--x.`

`+` concatenates a sentence with another value.

## Conditionals

```text
IF (score >= 90) {
    DISPLAYNL("high").
} ELSEIF (score >= 50) {
    DISPLAYNL("middle").
} ELSE {
    DISPLAYNL("low").
}
```

Switch syntax is:

```text
SWITCH (choice) {
    CASE (1) { DISPLAYNL("one"). }
    DEFAULT { DISPLAYNL("other"). }
}
```

## Loops

While-style loop:

```text
LOOP (condition) {
    // statements
}
```

For-style loop uses `TILL` and a comma before the update:

```text
LOOP (NUMBER i = 0 TILL i < limit, i++) {
    DISPLAYNL(i).
}
```

Do-while syntax is `DO { ... } LOOP (condition).`. `BREAK.` and `CONTINUE.` are
available inside loops.

## Functions

A function declaration ends with a period after its closing declaration.

```text
FUNCTION add(NUMBER a, NUMBER b) {
    RETURN a + b.
} RETURNS NUMBER.

DISPLAYNL(add(2, 3)).
```

A void function omits `RETURNS type` but still ends `}.`. Parameters may have
defaults, with all defaulted parameters after required parameters. Functions
may call other functions or themselves recursively.

## Arrays

Append `[]` to a type. Arrays use zero-based indexing.

```text
NUMBER[] values = [4, 2, 9].
DISPLAYNL(values[0]).
values[1] = 7.
NUMBER[] emptySized = NEW NUMBER[5].
```

Multidimensional arrays append more brackets, for example `NUMBER[][]`.

The optional arrays library is enabled with `IMPORT arrays.` and provides
`arrays.LENGTH`, `PUSH`, `POP`, `REVERSE`, `SORT`, `JOIN`, `SUM`, `AVG`,
`CONCAT`, `APPEND`, `FIND`, `CONTAINS`, `COUNT`, `FILL`, and `SLICE` as shown by
their names. Direct indexing and array literals do not require the import.

## String library

Use `IMPORT strings.`. Supported operations include:

- `strings.LENGTH(text)`
- `strings.UPPER(text)` and `strings.LOWER(text)`
- `strings.REVERSE(text)`
- `strings.CONTAINS(text, fragment)`
- `strings.REPLACE(text, old, replacement)`
- `strings.SUB(text, start, end)`
- `strings.CHARAT(text, index)`
- `strings.COUNT(text, fragment)` (non-overlapping occurrences)
- `strings.FIND(text, fragment)`
- `strings.STARTSWITH`, `strings.ENDSWITH`, `strings.EQUALS`
- `strings.SPLIT`, `strings.CONCAT`, `strings.REPEAT`, and `strings.TRIM`
- `strings.TO_NUMBER` and `strings.TO_SENTENCE`

## Math library

Use `IMPORT math.`. Constants are `math.PI` and `math.E`. Operations include
`ABS`, `POW`, `SQRT`, `MIN`, `MAX`, `FLOOR`, `CEIL`, `ROUND`, `CLAMP`, `SIGN`,
trigonometric functions, logarithms, and degree/radian conversion.

```text
IMPORT math.
NUMBER whole = math.FLOOR(7 / 2).
DISPLAYNL(whole).
```

## Output contract for benchmark tasks

Return a complete GOCO program only. Do not use Markdown fences or explanatory
text. Read inputs in the order specified. Print only requested values or labels;
do not print additional prompts, labels, or debugging text.
