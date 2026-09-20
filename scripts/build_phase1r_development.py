from __future__ import annotations

import json
from pathlib import Path


OUT = Path("benchmark/phase1r")
tasks: list[dict[str, object]] = []
tests: dict[str, list[dict[str, str]]] = {}
references: dict[str, str] = {}


def add(
    task_id: str,
    family: str,
    difficulty: str,
    structure: str,
    lineage: str,
    prompt: str,
    source: str,
    cases: list[tuple[str, str]],
    *,
    constructs: list[str],
    input_shape: str,
    required_regex: list[str] | None = None,
) -> None:
    tasks.append(
        {
            "task_id": task_id,
            "split": "phase1r_development",
            "family": family,
            "difficulty": difficulty,
            "structure": structure,
            "template_lineage": lineage,
            "constructs": constructs,
            "input_shape": input_shape,
            "prompt": prompt,
            "required_regex": required_regex or [],
        }
    )
    tests[task_id] = [
        {"case_id": chr(97 + index), "stdin": stdin, "expected_stdout": expected}
        for index, (stdin, expected) in enumerate(cases)
    ]
    references[task_id] = source.strip() + "\n"


add(
    "RDEV-EV-001", "expressions_variables", "basic", "affine_expression",
    "phase1r-dev-affine-v1",
    "Read one NUMBER n. Print 3*n + 2 as a number.",
    """
NUMBER n.
INPUT(n).
NUMBER result = 3 * n + 2.
DISPLAYNL(result).
""",
    [("0\n", "2.0"), ("5\n", "17.0"), ("-4\n", "-10.0"), ("2.5\n", "9.5")],
    constructs=["NUMBER", "INPUT", "arithmetic"], input_shape="one_number",
)
add(
    "RDEV-EV-002", "expressions_variables", "basic", "difference_of_squares",
    "phase1r-dev-two-number-algebra-v1",
    "Read one SENTENCE containing two numbers x|y. Print (x-y)*(x+y).",
    """
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
NUMBER x = strings.TO_NUMBER(parts[0]).
NUMBER y = strings.TO_NUMBER(parts[1]).
DISPLAYNL((x - y) * (x + y)).
""",
    [("5|2\n", "21.0"), ("3|3\n", "0.0"), ("-2|4\n", "-12.0"), ("1.5|0.5\n", "2.0")],
    constructs=["SPLIT", "TO_NUMBER", "arithmetic"], input_shape="two_numbers_pipe",
)
add(
    "RDEV-EV-003", "expressions_variables", "basic", "weighted_total",
    "phase1r-dev-three-number-algebra-v1",
    "Read one SENTENCE containing price|quantity|discount. Print price*quantity-discount.",
    """
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
NUMBER price = strings.TO_NUMBER(parts[0]).
NUMBER quantity = strings.TO_NUMBER(parts[1]).
NUMBER discount = strings.TO_NUMBER(parts[2]).
DISPLAYNL(price * quantity - discount).
""",
    [("10|3|5\n", "25.0"), ("2.5|4|1\n", "9.0"), ("0|8|0\n", "0.0"), ("7|1|10\n", "-3.0")],
    constructs=["SPLIT", "variables", "arithmetic"], input_shape="three_numbers_pipe",
)

add(
    "RDEV-CD-001", "conditionals", "basic", "three_way_sign",
    "phase1r-dev-sign-branch-v1",
    "Read one NUMBER. Print NEGATIVE, ZERO, or POSITIVE.",
    """
NUMBER value.
INPUT(value).
IF (value < 0) {
    DISPLAYNL("NEGATIVE").
} ELSEIF (value == 0) {
    DISPLAYNL("ZERO").
} ELSE {
    DISPLAYNL("POSITIVE").
}
""",
    [("-9\n", "NEGATIVE"), ("0\n", "ZERO"), ("2.5\n", "POSITIVE"), ("-0.5\n", "NEGATIVE")],
    constructs=["IF", "ELSEIF", "ELSE"], input_shape="one_number",
)
add(
    "RDEV-CD-002", "conditionals", "intermediate", "maximum_of_three",
    "phase1r-dev-max-three-v1",
    "Read one SENTENCE containing a|b|c. Print the greatest number. Ties may print the tied value.",
    """
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
NUMBER a = strings.TO_NUMBER(parts[0]).
NUMBER b = strings.TO_NUMBER(parts[1]).
NUMBER c = strings.TO_NUMBER(parts[2]).
NUMBER greatest = a.
IF (b > greatest) {
    greatest = b.
}
IF (c > greatest) {
    greatest = c.
}
DISPLAYNL(greatest).
""",
    [("1|9|3\n", "9.0"), ("7|2|7\n", "7.0"), ("-1|-8|-3\n", "-1.0"), ("2.5|2.7|2.6\n", "2.7")],
    constructs=["IF", "assignment", "SPLIT"], input_shape="three_numbers_pipe",
)
add(
    "RDEV-CD-003", "conditionals", "intermediate", "tiered_fee",
    "phase1r-dev-threshold-fee-v1",
    "Read one NUMBER amount. Print 0 when amount is at least 100, 5 when it is at least 50 but below 100, otherwise print 10.",
    """
NUMBER amount.
INPUT(amount).
IF (amount >= 100) {
    DISPLAYNL(0).
} ELSEIF (amount >= 50) {
    DISPLAYNL(5).
} ELSE {
    DISPLAYNL(10).
}
""",
    [("100\n", "0.0"), ("99.9\n", "5.0"), ("50\n", "5.0"), ("0\n", "10.0")],
    constructs=["IF", "ELSEIF", "boundary"], input_shape="one_number",
)

add(
    "RDEV-LP-001", "loops", "basic", "iterated_sequence_output",
    "phase1r-dev-square-sequence-v1",
    "Read a nonnegative whole NUMBER n. For each whole number from 1 through n, print its square on a separate line. For n=0 print nothing.",
    """
NUMBER n.
INPUT(n).
LOOP (NUMBER i = 1 TILL i <= n, i++) {
    DISPLAYNL(i * i).
}
""",
    [("0\n", ""), ("1\n", "1.0"), ("3\n", "1.0\n4.0\n9.0"), ("5\n", "1.0\n4.0\n9.0\n16.0\n25.0")],
    constructs=["LOOP", "iterated_output", "arithmetic"], input_shape="one_nonnegative_integer",
    required_regex=[r"\bLOOP\b"],
)
add(
    "RDEV-LP-002", "loops", "intermediate", "filtered_count",
    "phase1r-dev-divisible-count-v1",
    "Read one SENTENCE containing positive whole numbers n|k. Print how many numbers from 1 through n are divisible by k.",
    """
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
NUMBER n = strings.TO_NUMBER(parts[0]).
NUMBER k = strings.TO_NUMBER(parts[1]).
NUMBER count = 0.
NUMBER i = 1.
LOOP (i <= n) {
    IF (i % k == 0) {
        count++.
    }
    i++.
}
DISPLAYNL(count).
""",
    [("10|2\n", "5.0"), ("10|3\n", "3.0"), ("4|9\n", "0.0"), ("12|4\n", "3.0")],
    constructs=["LOOP", "IF", "modulo"], input_shape="two_positive_integers_pipe",
    required_regex=[r"\bLOOP\b"],
)
add(
    "RDEV-LP-003", "loops", "intermediate", "digit_reduction",
    "phase1r-dev-digit-sum-v1",
    "Read a nonnegative whole NUMBER n. Print the sum of its decimal digits. For n=0 print 0.",
    """
IMPORT math.
NUMBER n.
INPUT(n).
NUMBER total = 0.
LOOP (n > 0) {
    total += n % 10.
    n = math.FLOOR(n / 10).
}
DISPLAYNL(total).
""",
    [("0\n", "0.0"), ("7\n", "7.0"), ("1234\n", "10.0"), ("90909\n", "27.0")],
    constructs=["LOOP", "modulo", "math.FLOOR"], input_shape="one_nonnegative_integer",
    required_regex=[r"\bLOOP\b"],
)

add(
    "RDEV-FN-001", "functions", "basic", "single_numeric_function",
    "phase1r-dev-cube-function-v1",
    "Define and use a function named cube that accepts one NUMBER and returns its cube. Read one NUMBER and print cube(input).",
    """
FUNCTION cube(NUMBER value) {
    RETURN value * value * value.
} RETURNS NUMBER.
NUMBER inputValue.
INPUT(inputValue).
DISPLAYNL(cube(inputValue)).
""",
    [("0\n", "0.0"), ("2\n", "8.0"), ("-3\n", "-27.0"), ("1.5\n", "3.375")],
    constructs=["FUNCTION", "RETURN", "call"], input_shape="one_number",
    required_regex=[r"\bFUNCTION\s+cube\b"],
)
add(
    "RDEV-FN-002", "functions", "intermediate", "two_argument_function",
    "phase1r-dev-distance-function-v1",
    "Define and use a function named distance that accepts two NUMBER values and returns their absolute difference. Read x|y on one line and print the result.",
    """
IMPORT strings.
IMPORT math.
FUNCTION distance(NUMBER x, NUMBER y) {
    RETURN math.ABS(x - y).
} RETURNS NUMBER.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
NUMBER x = strings.TO_NUMBER(parts[0]).
NUMBER y = strings.TO_NUMBER(parts[1]).
DISPLAYNL(distance(x, y)).
""",
    [("8|3\n", "5.0"), ("3|8\n", "5.0"), ("-2|-9\n", "7.0"), ("1.5|1.5\n", "0.0")],
    constructs=["FUNCTION", "math.ABS", "SPLIT"], input_shape="two_numbers_pipe",
    required_regex=[r"\bFUNCTION\s+distance\b"],
)
add(
    "RDEV-FN-003", "functions", "intermediate", "function_with_branch",
    "phase1r-dev-cap-function-v1",
    "Define and use a function named capAtTen that returns 10 when its NUMBER argument is above 10 and otherwise returns the argument. Read one NUMBER and print the function result.",
    """
FUNCTION capAtTen(NUMBER value) {
    IF (value > 10) {
        RETURN 10.
    }
    RETURN value.
} RETURNS NUMBER.
NUMBER value.
INPUT(value).
DISPLAYNL(capAtTen(value)).
""",
    [("4\n", "4.0"), ("10\n", "10.0"), ("11\n", "10.0"), ("-3\n", "-3.0")],
    constructs=["FUNCTION", "IF", "RETURN"], input_shape="one_number",
    required_regex=[r"\bFUNCTION\s+capAtTen\b"],
)

add(
    "RDEV-AR-001", "arrays", "intermediate", "array_scan_maximum",
    "phase1r-dev-array-max-four-v1",
    "Read four numbers a|b|c|d on one line, place them in a NUMBER array, and print the greatest element.",
    """
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
NUMBER a = strings.TO_NUMBER(parts[0]).
NUMBER b = strings.TO_NUMBER(parts[1]).
NUMBER c = strings.TO_NUMBER(parts[2]).
NUMBER d = strings.TO_NUMBER(parts[3]).
NUMBER[] values = [a, b, c, d].
NUMBER greatest = values[0].
NUMBER i = 1.
LOOP (i < 4) {
    IF (values[i] > greatest) {
        greatest = values[i].
    }
    i++.
}
DISPLAYNL(greatest).
""",
    [("1|4|2|3\n", "4.0"), ("-1|-8|-2|-3\n", "-1.0"), ("5|5|5|5\n", "5.0"), ("2.2|9.1|0|8\n", "9.1")],
    constructs=["array_literal", "indexing", "LOOP"], input_shape="four_numbers_pipe",
    required_regex=[r"NUMBER\s*\[\s*\]"],
)
add(
    "RDEV-AR-002", "arrays", "basic", "array_reordered_output",
    "phase1r-dev-array-reverse-four-v1",
    "Read four numbers a|b|c|d on one line, store them in a NUMBER array, and print them in reverse order separated by | with no extra spaces.",
    """
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
NUMBER[] values = [strings.TO_NUMBER(parts[0]), strings.TO_NUMBER(parts[1]), strings.TO_NUMBER(parts[2]), strings.TO_NUMBER(parts[3])].
DISPLAY(values[3]).
DISPLAY("|").
DISPLAY(values[2]).
DISPLAY("|").
DISPLAY(values[1]).
DISPLAY("|").
DISPLAYNL(values[0]).
""",
    [("1|2|3|4\n", "4.0|3.0|2.0|1.0"), ("0|-1|5|2.5\n", "2.5|5.0|-1.0|0.0"), ("9|9|8|7\n", "7.0|8.0|9.0|9.0"), ("-2|-3|-4|-5\n", "-5.0|-4.0|-3.0|-2.0")],
    constructs=["array_literal", "indexing", "DISPLAY"], input_shape="four_numbers_pipe",
    required_regex=[r"NUMBER\s*\[\s*\]"],
)
add(
    "RDEV-AR-003", "arrays", "intermediate", "array_filtered_count",
    "phase1r-dev-array-threshold-count-v1",
    "Read five numbers a|b|c|d|threshold. Store a,b,c,d in a NUMBER array and print how many are strictly greater than threshold.",
    """
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
NUMBER[] values = [strings.TO_NUMBER(parts[0]), strings.TO_NUMBER(parts[1]), strings.TO_NUMBER(parts[2]), strings.TO_NUMBER(parts[3])].
NUMBER threshold = strings.TO_NUMBER(parts[4]).
NUMBER count = 0.
NUMBER i = 0.
LOOP (i < 4) {
    IF (values[i] > threshold) {
        count++.
    }
    i++.
}
DISPLAYNL(count).
""",
    [("1|2|3|4|2\n", "2.0"), ("5|5|5|5|5\n", "0.0"), ("-1|0|1|2|-2\n", "4.0"), ("2.5|3.5|1.5|4.5|3\n", "2.0")],
    constructs=["array_literal", "LOOP", "IF"], input_shape="five_numbers_pipe",
    required_regex=[r"NUMBER\s*\[\s*\]"],
)

add(
    "RDEV-ST-001", "strings", "basic", "trim_and_uppercase",
    "phase1r-dev-string-normalize-v1",
    "Read one SENTENCE. Trim leading and trailing whitespace, convert it to uppercase, and print it.",
    """
IMPORT strings.
SENTENCE text.
INPUT(text).
DISPLAYNL(strings.UPPER(strings.TRIM(text, ""))).
""",
    [("  hello  \n", "HELLO"), ("GoCo\n", "GOCO"), ("  two words\n", "TWO WORDS"), ("x\n", "X")],
    constructs=["strings.TRIM", "strings.UPPER"], input_shape="one_sentence",
)
add(
    "RDEV-ST-002", "strings", "basic", "string_reverse",
    "phase1r-dev-string-reverse-v1",
    "Read one SENTENCE and print its characters in reverse order using the strings library.",
    """
IMPORT strings.
SENTENCE text.
INPUT(text).
DISPLAYNL(strings.REVERSE(text)).
""",
    [("abc\n", "cba"), ("racecar\n", "racecar"), ("a b\n", "b a"), ("GOCO\n", "OCOG")],
    constructs=["strings.REVERSE"], input_shape="one_sentence",
)
add(
    "RDEV-ST-003", "strings", "intermediate", "substring_count",
    "phase1r-dev-substring-count-v1",
    "Read one SENTENCE containing text|fragment. Print the number of non-overlapping occurrences of fragment in text.",
    """
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
DISPLAYNL(strings.COUNT(parts[0], parts[1])).
""",
    [("banana|an\n", "2.0"), ("aaaa|aa\n", "2.0"), ("hello|z\n", "0.0"), ("abcabcabc|abc\n", "3.0")],
    constructs=["strings.SPLIT", "strings.COUNT"], input_shape="two_sentences_pipe",
)

add(
    "RDEV-IO-001", "input_output", "basic", "field_reordering",
    "phase1r-dev-io-swap-fields-v1",
    "Read one SENTENCE containing first|second. Print second|first with no extra spaces.",
    """
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
DISPLAY(parts[1]).
DISPLAY("|").
DISPLAYNL(parts[0]).
""",
    [("red|blue\n", "blue|red"), ("a|b\n", "b|a"), ("first words|last\n", "last|first words"), ("x|x\n", "x|x")],
    constructs=["INPUT", "DISPLAY", "DISPLAYNL"], input_shape="two_sentences_pipe",
)
add(
    "RDEV-IO-002", "input_output", "basic", "formatted_record",
    "phase1r-dev-io-record-v1",
    "Read one SENTENCE containing name|score. Print NAME=score where NAME is uppercase and there are no extra spaces.",
    """
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
DISPLAY(strings.UPPER(parts[0])).
DISPLAY("=").
DISPLAYNL(parts[1]).
""",
    [("ada|10\n", "ADA=10.0"), ("Lin|0\n", "LIN=0.0"), ("two words|7.5\n", "TWO WORDS=7.5"), ("x|-2\n", "X=-2.0")],
    constructs=["INPUT", "strings.UPPER", "multi_display"], input_shape="two_fields_pipe",
)
add(
    "RDEV-IO-003", "input_output", "intermediate", "numeric_and_text_output",
    "phase1r-dev-io-repeat-label-v1",
    "Read one SENTENCE containing label|number. Print label:number:number with no extra spaces.",
    """
IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] parts = strings.SPLIT(line, "|").
DISPLAY(parts[0]).
DISPLAY(":").
DISPLAY(parts[1]).
DISPLAY(":").
DISPLAYNL(parts[1]).
""",
    [("id|3\n", "id:3.0:3.0"), ("x|0\n", "x:0.0:0.0"), ("long label|-4.5\n", "long label:-4.5:-4.5"), ("A|12\n", "A:12.0:12.0")],
    constructs=["INPUT", "ordered_output"], input_shape="two_fields_pipe",
)

add(
    "RDEV-CP-001", "composition_algorithms", "intermediate", "iterative_factorial",
    "phase1r-dev-factorial-v1",
    "Read a whole NUMBER n from 0 through 10. Compute n factorial iteratively and print it.",
    """
NUMBER n.
INPUT(n).
NUMBER result = 1.
LOOP (NUMBER i = 2 TILL i <= n, i++) {
    result *= i.
}
DISPLAYNL(result).
""",
    [("0\n", "1.0"), ("1\n", "1.0"), ("5\n", "120.0"), ("8\n", "40320.0")],
    constructs=["LOOP", "multiplicative_accumulator"], input_shape="one_bounded_integer",
)
add(
    "RDEV-CP-002", "composition_algorithms", "advanced", "divisor_search_classification",
    "phase1r-dev-prime-classification-v1",
    "Read a whole NUMBER n. Print PRIME if n is prime; otherwise print NOT PRIME. Values below 2 are not prime.",
    """
NUMBER n.
INPUT(n).
LOGIC prime = TRUE.
IF (n < 2) {
    prime = FALSE.
}
LOOP (NUMBER divisor = 2 TILL divisor < n, divisor++) {
    IF (n % divisor == 0) {
        prime = FALSE.
    }
}
IF (prime) {
    DISPLAYNL("PRIME").
} ELSE {
    DISPLAYNL("NOT PRIME").
}
""",
    [("0\n", "NOT PRIME"), ("1\n", "NOT PRIME"), ("2\n", "PRIME"), ("9\n", "NOT PRIME"), ("17\n", "PRIME")],
    constructs=["LOOP", "modulo", "LOGIC", "classification"], input_shape="one_integer",
)
add(
    "RDEV-CP-003", "composition_algorithms", "advanced", "digit_classification",
    "phase1r-dev-digit-sum-parity-v1",
    "Read a nonnegative whole NUMBER. Sum its decimal digits, then print EVEN if that sum is even and ODD otherwise.",
    """
IMPORT math.
NUMBER value.
INPUT(value).
NUMBER total = 0.
LOOP (value > 0) {
    total += value % 10.
    value = math.FLOOR(value / 10).
}
IF (total % 2 == 0) {
    DISPLAYNL("EVEN").
} ELSE {
    DISPLAYNL("ODD").
}
""",
    [("0\n", "EVEN"), ("7\n", "ODD"), ("123\n", "EVEN"), ("9992\n", "ODD")],
    constructs=["LOOP", "digit_reduction", "IF"], input_shape="one_nonnegative_integer",
)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / "development_tasks.json", tasks)
    write_json(OUT / "development_hidden_tests.json", tests)
    write_json(OUT / "development_reference_solutions.json", references)
    print(f"wrote {len(tasks)} Phase 1R development tasks")
