from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


OUT = Path("benchmark/phase1s")


@dataclass(frozen=True)
class Scenario:
    family: str
    code: str
    structure: str
    control_flow: str
    prompt: str
    reference: str
    completion_token: str
    completion: str
    modification_source: str
    modification_instruction: str
    cases: list[tuple[str, str]]


def clean(text: str) -> str:
    return text.strip() + "\n"


scenarios = [
    Scenario("expressions_variables", "EV1", "affine_numeric_transform", "straight_line",
        "Read one NUMBER n and print 2*n - 7.",
        """NUMBER n.\nINPUT(n).\nDISPLAYNL(2 * n - 7).""", "2 * n - 7", "2 * n - 7",
        """NUMBER n.\nINPUT(n).\nDISPLAYNL(n + 7).""",
        "Modify the program so it prints 2*n - 7 instead of n + 7.",
        [("0\n", "-7.0"), ("5\n", "3.0"), ("-2\n", "-11.0"), ("3.5\n", "0.0")]),
    Scenario("expressions_variables", "EV2", "rectangle_area_from_delimited_input", "straight_line",
        "Read width|height on one line and print width*height.",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER width = strings.TO_NUMBER(parts[0]).\nNUMBER height = strings.TO_NUMBER(parts[1]).\nDISPLAYNL(width * height).""", "width * height", "width * height",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER width = strings.TO_NUMBER(parts[0]).\nNUMBER height = strings.TO_NUMBER(parts[1]).\nDISPLAYNL(2 * width + 2 * height).""",
        "Modify the program to print rectangle area instead of perimeter.",
        [("3|4\n", "12.0"), ("0|8\n", "0.0"), ("2.5|4\n", "10.0"), ("-2|3\n", "-6.0")]),
    Scenario("expressions_variables", "EV3", "temperature_offset", "straight_line",
        "Read one NUMBER representing Celsius and print Celsius + 273.15.",
        """NUMBER celsius.\nINPUT(celsius).\nNUMBER kelvin = celsius + 273.15.\nDISPLAYNL(kelvin).""", "celsius + 273.15", "celsius + 273.15",
        """NUMBER celsius.\nINPUT(celsius).\nNUMBER kelvin = celsius + 32.\nDISPLAYNL(kelvin).""",
        "Modify the conversion so it adds 273.15 rather than 32.",
        [("0\n", "273.15"), ("100\n", "373.15"), ("-273.15\n", "0.0"), ("20.5\n", "293.65")]),

    Scenario("conditionals", "CD1", "adult_threshold_classification", "if_else",
        "Read one NUMBER age. Print ADULT when age is at least 18, otherwise print MINOR.",
        """NUMBER age.\nINPUT(age).\nIF (age >= 18) {\n    DISPLAYNL("ADULT").\n} ELSE {\n    DISPLAYNL("MINOR").\n}""", "age >= 18", "age >= 18",
        """NUMBER age.\nINPUT(age).\nIF (age < 18) {\n    DISPLAYNL("ADULT").\n} ELSE {\n    DISPLAYNL("MINOR").\n}""",
        "Modify the condition so ADULT is printed exactly when age is at least 18.",
        [("17\n", "MINOR"), ("18\n", "ADULT"), ("40\n", "ADULT"), ("0\n", "MINOR")]),
    Scenario("conditionals", "CD2", "minimum_of_two", "if_else",
        "Read a|b on one line and print the smaller number. Ties print that value.",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER a = strings.TO_NUMBER(parts[0]).\nNUMBER b = strings.TO_NUMBER(parts[1]).\nIF (a <= b) {\n    DISPLAYNL(a).\n} ELSE {\n    DISPLAYNL(b).\n}""", "a <= b", "a <= b",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER a = strings.TO_NUMBER(parts[0]).\nNUMBER b = strings.TO_NUMBER(parts[1]).\nIF (a >= b) {\n    DISPLAYNL(a).\n} ELSE {\n    DISPLAYNL(b).\n}""",
        "Modify the program to print the smaller rather than the larger number.",
        [("2|9\n", "2.0"), ("9|2\n", "2.0"), ("5|5\n", "5.0"), ("-3|-8\n", "-8.0")]),
    Scenario("conditionals", "CD3", "three_way_divisibility_label", "if_elseif_else",
        "Read a whole NUMBER n. Print BOTH if divisible by 2 and 3, EVEN if only divisible by 2, otherwise OTHER.",
        """NUMBER n.\nINPUT(n).\nIF (n % 6 == 0) {\n    DISPLAYNL("BOTH").\n} ELSEIF (n % 2 == 0) {\n    DISPLAYNL("EVEN").\n} ELSE {\n    DISPLAYNL("OTHER").\n}""", "n % 6 == 0", "n % 6 == 0",
        """NUMBER n.\nINPUT(n).\nIF (n % 3 == 0) {\n    DISPLAYNL("BOTH").\n} ELSEIF (n % 2 == 0) {\n    DISPLAYNL("EVEN").\n} ELSE {\n    DISPLAYNL("OTHER").\n}""",
        "Modify the first branch so BOTH is printed only when n is divisible by both 2 and 3.",
        [("6\n", "BOTH"), ("12\n", "BOTH"), ("8\n", "EVEN"), ("9\n", "OTHER")]),

    Scenario("loops", "LP1", "sum_of_cubes_series", "for_loop_accumulator",
        "Read a nonnegative whole NUMBER n and print the sum of cubes from 1 through n.",
        """NUMBER n.\nINPUT(n).\nNUMBER total = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) {\n    total += i * i * i.\n}\nDISPLAYNL(total).""", "i * i * i", "i * i * i",
        """NUMBER n.\nINPUT(n).\nNUMBER total = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) {\n    total += i * i.\n}\nDISPLAYNL(total).""",
        "Modify the loop to sum cubes rather than squares.",
        [("0\n", "0.0"), ("1\n", "1.0"), ("3\n", "36.0"), ("5\n", "225.0")]),
    Scenario("loops", "LP2", "descending_sequence", "while_loop_output",
        "Read a nonnegative whole NUMBER n and print n down to 1, one number per line. Print nothing for zero.",
        """NUMBER n.\nINPUT(n).\nLOOP (n > 0) {\n    DISPLAYNL(n).\n    n--.\n}""", "n > 0", "n > 0",
        """NUMBER n.\nINPUT(n).\nLOOP (n > 0) {\n    DISPLAYNL(n).\n    n++.\n}""",
        "Modify the valid program so it counts downward and terminates rather than incrementing.",
        [("0\n", ""), ("1\n", "1.0"), ("3\n", "3.0\n2.0\n1.0"), ("5\n", "5.0\n4.0\n3.0\n2.0\n1.0")]),
    Scenario("loops", "LP3", "filtered_range_sum", "for_loop_with_branch",
        "Read a positive whole NUMBER n and print the sum of numbers from 1 through n that are divisible by 3.",
        """NUMBER n.\nINPUT(n).\nNUMBER total = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) {\n    IF (i % 3 == 0) {\n        total += i.\n    }\n}\nDISPLAYNL(total).""", "i % 3 == 0", "i % 3 == 0",
        """NUMBER n.\nINPUT(n).\nNUMBER total = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) {\n    IF (i % 2 == 0) {\n        total += i.\n    }\n}\nDISPLAYNL(total).""",
        "Modify the filter to sum multiples of 3 instead of even numbers.",
        [("1\n", "0.0"), ("3\n", "3.0"), ("10\n", "18.0"), ("12\n", "30.0")]),

    Scenario("functions", "FN1", "single_argument_scaling_function", "function_then_call",
        "Define a function named halfValue taking one NUMBER and returning value/2. Read one NUMBER and print the function result.",
        """FUNCTION halfValue(NUMBER value) {\n    RETURN value / 2.\n} RETURNS NUMBER.\nNUMBER inputValue.\nINPUT(inputValue).\nDISPLAYNL(halfValue(inputValue)).""", "value / 2", "value / 2",
        """FUNCTION halfValue(NUMBER value) {\n    RETURN value * 2.\n} RETURNS NUMBER.\nNUMBER inputValue.\nINPUT(inputValue).\nDISPLAYNL(halfValue(inputValue)).""",
        "Modify the function to return half the input rather than double it.",
        [("8\n", "4.0"), ("0\n", "0.0"), ("-5\n", "-2.5"), ("3\n", "1.5")]),
    Scenario("functions", "FN2", "branching_max_function", "function_with_if",
        "Define maxTwo(NUMBER a, NUMBER b) returning the greater value. Read a|b and print maxTwo(a,b).",
        """IMPORT strings.\nFUNCTION maxTwo(NUMBER a, NUMBER b) {\n    IF (a >= b) {\n        RETURN a.\n    }\n    RETURN b.\n} RETURNS NUMBER.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER a = strings.TO_NUMBER(parts[0]).\nNUMBER b = strings.TO_NUMBER(parts[1]).\nDISPLAYNL(maxTwo(a, b)).""", "a >= b", "a >= b",
        """IMPORT strings.\nFUNCTION maxTwo(NUMBER a, NUMBER b) {\n    IF (a <= b) {\n        RETURN a.\n    }\n    RETURN b.\n} RETURNS NUMBER.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER a = strings.TO_NUMBER(parts[0]).\nNUMBER b = strings.TO_NUMBER(parts[1]).\nDISPLAYNL(maxTwo(a, b)).""",
        "Modify maxTwo so it returns the greater rather than the smaller value.",
        [("2|9\n", "9.0"), ("9|2\n", "9.0"), ("5|5\n", "5.0"), ("-3|-8\n", "-3.0")]),
    Scenario("functions", "FN3", "affine_conversion_function", "function_arithmetic",
        "Define toFahrenheit(NUMBER c) returning c*9/5+32. Read one NUMBER and print the result.",
        """FUNCTION toFahrenheit(NUMBER c) {\n    RETURN c * 9 / 5 + 32.\n} RETURNS NUMBER.\nNUMBER celsius.\nINPUT(celsius).\nDISPLAYNL(toFahrenheit(celsius)).""", "c * 9 / 5 + 32", "c * 9 / 5 + 32",
        """FUNCTION toFahrenheit(NUMBER c) {\n    RETURN c + 32.\n} RETURNS NUMBER.\nNUMBER celsius.\nINPUT(celsius).\nDISPLAYNL(toFahrenheit(celsius)).""",
        "Modify the function to use the Fahrenheit formula c*9/5+32.",
        [("0\n", "32.0"), ("100\n", "212.0"), ("-40\n", "-40.0"), ("20\n", "68.0")]),

    Scenario("arrays", "AR1", "fixed_array_sum", "array_index_arithmetic",
        "Read a|b|c on one line, store the values in a NUMBER array, and print their sum.",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER[] values = [strings.TO_NUMBER(parts[0]), strings.TO_NUMBER(parts[1]), strings.TO_NUMBER(parts[2])].\nDISPLAYNL(values[0] + values[1] + values[2]).""", "values[0] + values[1] + values[2]", "values[0] + values[1] + values[2]",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER[] values = [strings.TO_NUMBER(parts[0]), strings.TO_NUMBER(parts[1]), strings.TO_NUMBER(parts[2])].\nDISPLAYNL(values[0] * values[1] * values[2]).""",
        "Modify the program to print the array sum rather than product.",
        [("1|2|3\n", "6.0"), ("0|-2|5\n", "3.0"), ("1.5|2.5|3\n", "7.0"), ("-1|-2|-3\n", "-6.0")]),
    Scenario("arrays", "AR2", "fixed_array_minimum_scan", "array_loop_branch",
        "Read four numbers separated by |, store them in a NUMBER array, and print the smallest.",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER[] values = [strings.TO_NUMBER(parts[0]), strings.TO_NUMBER(parts[1]), strings.TO_NUMBER(parts[2]), strings.TO_NUMBER(parts[3])].\nNUMBER smallest = values[0].\nLOOP (NUMBER i = 1 TILL i < 4, i++) {\n    IF (values[i] < smallest) {\n        smallest = values[i].\n    }\n}\nDISPLAYNL(smallest).""", "values[i] < smallest", "values[i] < smallest",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER[] values = [strings.TO_NUMBER(parts[0]), strings.TO_NUMBER(parts[1]), strings.TO_NUMBER(parts[2]), strings.TO_NUMBER(parts[3])].\nNUMBER smallest = values[0].\nLOOP (NUMBER i = 1 TILL i < 4, i++) {\n    IF (values[i] > smallest) {\n        smallest = values[i].\n    }\n}\nDISPLAYNL(smallest).""",
        "Modify the scan to print the smallest rather than greatest array value.",
        [("4|1|3|2\n", "1.0"), ("-1|-5|0|2\n", "-5.0"), ("7|7|7|7\n", "7.0"), ("2.5|2.1|9|3\n", "2.1")]),
    Scenario("arrays", "AR3", "array_reordered_indices", "array_multi_output",
        "Read a|b|c on one line, store them in a NUMBER array, and print c|a|b with no spaces.",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER[] values = [strings.TO_NUMBER(parts[0]), strings.TO_NUMBER(parts[1]), strings.TO_NUMBER(parts[2])].\nDISPLAY(values[2]).\nDISPLAY("|").\nDISPLAY(values[0]).\nDISPLAY("|").\nDISPLAYNL(values[1]).""", "values[2]", "values[2]",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER[] values = [strings.TO_NUMBER(parts[0]), strings.TO_NUMBER(parts[1]), strings.TO_NUMBER(parts[2])].\nDISPLAY(values[0]).\nDISPLAY("|").\nDISPLAY(values[1]).\nDISPLAY("|").\nDISPLAYNL(values[2]).""",
        "Modify the output order from a|b|c to c|a|b.",
        [("1|2|3\n", "3.0|1.0|2.0"), ("0|-1|5\n", "5.0|0.0|-1.0"), ("2.5|4|8\n", "8.0|2.5|4.0"), ("7|7|9\n", "9.0|7.0|7.0")]),

    Scenario("strings", "ST1", "lowercase_then_reverse", "nested_library_calls",
        "Read one SENTENCE, convert it to lowercase, reverse it, and print it.",
        """IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.REVERSE(strings.LOWER(text))).""", "strings.REVERSE(strings.LOWER(text))", "strings.REVERSE(strings.LOWER(text))",
        """IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.LOWER(text)).""",
        "Modify the program to reverse the lowercase text rather than only lowercase it.",
        [("AbC\n", "cba"), ("GOCO\n", "ocog"), ("A b\n", "b a"), ("x\n", "x")]),
    Scenario("strings", "ST2", "character_replacement", "library_replace",
        "Read one SENTENCE and replace every hyphen with an underscore, then print it.",
        """IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.REPLACE(text, "-", "_")).""", "strings.REPLACE(text, \"-\", \"_\")", "strings.REPLACE(text, \"-\", \"_\")",
        """IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.REPLACE(text, "-", "/")).""",
        "Modify the replacement so hyphens become underscores rather than slashes.",
        [("a-b-c\n", "a_b_c"), ("none\n", "none"), ("-x-\n", "_x_"), ("a--b\n", "a__b")]),
    Scenario("strings", "ST3", "trimmed_length", "nested_trim_length",
        "Read one SENTENCE, trim ordinary surrounding whitespace, and print the remaining length.",
        """IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.LENGTH(strings.TRIM(text, ""))).""", "strings.LENGTH(strings.TRIM(text, \"\"))", "strings.LENGTH(strings.TRIM(text, \"\"))",
        """IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.LENGTH(text)).""",
        "Modify the program so surrounding whitespace is trimmed before measuring length.",
        [("  abc  \n", "3.0"), ("x\n", "1.0"), (" two words \n", "9.0"), ("    \n", "0.0")]),

    Scenario("input_output", "IO1", "three_field_reformat", "split_multi_display",
        "Read first|middle|last and print last, first middle with exactly one space after the comma.",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nDISPLAY(parts[2]).\nDISPLAY(", ").\nDISPLAY(parts[0]).\nDISPLAY(" ").\nDISPLAYNL(parts[1]).""", "parts[2]", "parts[2]",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nDISPLAY(parts[0]).\nDISPLAY(" ").\nDISPLAY(parts[1]).\nDISPLAY(" ").\nDISPLAYNL(parts[2]).""",
        "Modify the output from first middle last to last, first middle.",
        [("Ada|L|Lovelace\n", "Lovelace, Ada L"), ("A|B|C\n", "C, A B"), ("one|two words|three\n", "three, one two words"), ("x||z\n", "z, x ")]),
    Scenario("input_output", "IO2", "labelled_numeric_echo", "split_display_format",
        "Read label|value and print [label]=value with no extra spaces.",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nDISPLAY("[").\nDISPLAY(parts[0]).\nDISPLAY("]=").\nDISPLAYNL(parts[1]).""", "\"]=\"", "\"]=\"",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nDISPLAY(parts[0]).\nDISPLAY(":").\nDISPLAYNL(parts[1]).""",
        "Modify the formatting from label:value to [label]=value.",
        [("x|3\n", "[x]=3.0"), ("score|0\n", "[score]=0.0"), ("temp|-2.5\n", "[temp]=-2.5"), ("A|12\n", "[A]=12.0")]),
    Scenario("input_output", "IO3", "field_duplication_format", "split_repeated_output",
        "Read word|count and print word-count-word with no spaces.",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nSENTENCE word = strings.TO_SENTENCE(parts[0]).\nSENTENCE countText = strings.TO_SENTENCE(parts[1]).\nDISPLAYNL(word + "-" + countText + "-" + word).""", "word + \"-\" + countText + \"-\" + word", "word + \"-\" + countText + \"-\" + word",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nSENTENCE word = strings.TO_SENTENCE(parts[0]).\nSENTENCE countText = strings.TO_SENTENCE(parts[1]).\nDISPLAYNL(word + "-" + countText + "-" + countText).""",
        "Modify the final field so the output is word-count-word rather than word-count-count.",
        [("go|2\n", "go-2.0-go"), ("x|0\n", "x-0.0-x"), ("hello|-1\n", "hello--1.0-hello"), ("A|3.5\n", "A-3.5-A")]),

    Scenario("composition_algorithms", "CP1", "power_by_repeated_multiplication", "for_loop_product",
        "Read base|exponent where exponent is a nonnegative whole number. Compute base raised to exponent using a loop and print it.",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER base = strings.TO_NUMBER(parts[0]).\nNUMBER exponent = strings.TO_NUMBER(parts[1]).\nNUMBER result = 1.\nLOOP (NUMBER i = 0 TILL i < exponent, i++) {\n    result *= base.\n}\nDISPLAYNL(result).""", "i < exponent", "i < exponent",
        """IMPORT strings.\nSENTENCE line.\nINPUT(line).\nSENTENCE[] parts = strings.SPLIT(line, "|").\nNUMBER base = strings.TO_NUMBER(parts[0]).\nNUMBER exponent = strings.TO_NUMBER(parts[1]).\nNUMBER result = 0.\nLOOP (NUMBER i = 0 TILL i < exponent, i++) {\n    result += base.\n}\nDISPLAYNL(result).""",
        "Modify the repeated-addition program into repeated multiplication for exponentiation, including the correct initial result.",
        [("2|0\n", "1.0"), ("2|3\n", "8.0"), ("-2|3\n", "-8.0"), ("3|4\n", "81.0")]),
    Scenario("composition_algorithms", "CP2", "proper_divisor_count", "for_loop_conditional_count",
        "Read a positive whole NUMBER n and print how many positive proper divisors it has (divisors less than n).",
        """NUMBER n.\nINPUT(n).\nNUMBER count = 0.\nLOOP (NUMBER candidate = 1 TILL candidate < n, candidate++) {\n    IF (n % candidate == 0) {\n        count++.\n    }\n}\nDISPLAYNL(count).""", "n % candidate == 0", "n % candidate == 0",
        """NUMBER n.\nINPUT(n).\nNUMBER count = 0.\nLOOP (NUMBER candidate = 1 TILL candidate < n, candidate++) {\n    IF (n % candidate != 0) {\n        count++.\n    }\n}\nDISPLAYNL(count).""",
        "Modify the program to count proper divisors rather than non-divisors.",
        [("1\n", "0.0"), ("2\n", "1.0"), ("6\n", "3.0"), ("12\n", "5.0")]),
    Scenario("composition_algorithms", "CP3", "perfect_square_classification", "math_then_branch",
        "Read a nonnegative whole NUMBER n. Print SQUARE if it is a perfect square, otherwise NOT SQUARE.",
        """IMPORT math.\nNUMBER n.\nINPUT(n).\nNUMBER root = math.FLOOR(math.SQRT(n)).\nIF (root * root == n) {\n    DISPLAYNL("SQUARE").\n} ELSE {\n    DISPLAYNL("NOT SQUARE").\n}""", "root * root == n", "root * root == n",
        """IMPORT math.\nNUMBER n.\nINPUT(n).\nNUMBER root = math.FLOOR(math.SQRT(n)).\nIF (root == n) {\n    DISPLAYNL("SQUARE").\n} ELSE {\n    DISPLAYNL("NOT SQUARE").\n}""",
        "Modify the condition to correctly recognize perfect squares.",
        [("0\n", "SQUARE"), ("1\n", "SQUARE"), ("16\n", "SQUARE"), ("15\n", "NOT SQUARE")]),
]


recognition = {
    "expressions_variables": [
        ("Which is a valid GOCO declaration? A: NUMBER total = 4. B: INT total = 4. C: NUMBER total = 4;", "A", "declaration_terminator_type"),
        ("Which is valid GOCO assignment syntax? A: value := 3. B: value = 3. C: value = 3;", "B", "assignment_operator_terminator"),
        ("Which uses the valid GOCO text type? A: STRING name. B: str name. C: SENTENCE name.", "C", "text_type"),
    ],
    "conditionals": [
        ("Which keyword is valid for an additional GOCO conditional branch? A: ELSE IF B: ELIF C: ELSEIF", "C", "elseif_keyword"),
        ("Which is a valid GOCO condition header? A: IF x > 2 { B: IF (x > 2) { C: if x > 2 then", "B", "if_parentheses"),
        ("Which valid GOCO block needs no period after its closing brace? A: IF (ready) { DISPLAYNL(1). } B: NUMBER x = 1 C: DISPLAYNL(1)", "A", "control_block_terminator"),
    ],
    "loops": [
        ("Which begins a valid GOCO while-style loop? A: WHILE (x < 3) { B: LOOP (x < 3) { C: FOR x < 3 {", "B", "while_loop_keyword"),
        ("Which is valid GOCO for-style syntax? A: FOR (i=0; i<3; i++) { B: LOOP (NUMBER i = 0 TILL i < 3, i++) { C: LOOP i FROM 0 TO 3 {", "B", "for_loop_header"),
        ("Which is the valid GOCO do-while ending? A: } WHILE (x < 3). B: } LOOP (x < 3). C: } LOOP x < 3", "B", "do_loop_ending"),
    ],
    "functions": [
        ("Which is a valid GOCO function header? A: func add(a NUMBER) { B: FUNCTION add(NUMBER a) { C: FUNCTION add(a) {", "B", "typed_function_parameter"),
        ("Which correctly ends a returning GOCO function declaration? A: } RETURNS NUMBER. B: } -> NUMBER C: } RETURNS NUMBER", "A", "function_final_period"),
        ("Which return statement is valid inside a GOCO function? A: return(x); B: RETURN x. C: RETURN: x.", "B", "return_statement"),
    ],
    "arrays": [
        ("Which is a valid GOCO number-array declaration? A: ARRAY<NUMBER> xs. B: NUMBER[] xs. C: NUMBER xs[].", "B", "array_type"),
        ("Which is valid zero-based GOCO array access? A: values[0] B: values(0) C: values{0}", "A", "array_index"),
        ("Which is a valid GOCO array literal? A: NUMBER[] xs = [1, 2, 3]. B: NUMBER[] xs = {1,2,3}. C: xs := [1,2,3];", "A", "array_literal"),
    ],
    "strings": [
        ("Which valid GOCO call uppercases text after importing strings? A: strings.UPPER(text) B: text.upper() C: UPPER strings text", "A", "string_library_call"),
        ("Which is the pinned GOCO trim call? A: strings.TRIM(text) B: strings.TRIM(text, \"\") C: text.TRIM()", "B", "trim_arity"),
        ("Which valid GOCO call splits line on |? A: strings.SPLIT(line, \"|\") B: line.split(\"|\") C: SPLIT line BY \"|\"", "A", "split_call"),
    ],
    "input_output": [
        ("Which is valid GOCO input usage? A: NUMBER x = INPUT(). B: INPUT(\"x\", x). C: NUMBER x. INPUT(x).", "C", "input_statement"),
        ("Which prints a value followed by a newline in GOCO? A: PRINTLN(x). B: DISPLAYNL(x). C: fmt.Println(x)", "B", "display_newline"),
        ("Which reads two values reliably under the pinned runtime? A: two INPUT statements B: one SENTENCE INPUT followed by strings.SPLIT C: READLINE twice", "B", "single_input_constraint"),
    ],
    "composition_algorithms": [
        ("Which is a valid complete GOCO top-level shape? A: PROGRAM main { DISPLAYNL(1). } B: package main; func main(){} C: DISPLAYNL(1).", "C", "bare_top_level"),
        ("Which identifier choice avoids a reserved/built-in name? A: NUMBER number. B: NUMBER totalValue. C: NUMBER length.", "B", "identifier_collision"),
        ("Which loop update belongs in a valid GOCO for-style header? A: i++ in LOOP (..., i++) B: i += 1; after FOR C: NEXT i", "A", "loop_update_composition"),
    ],
}


tasks: list[dict[str, object]] = []
hidden: dict[str, list[dict[str, str]]] = {}
references: dict[str, str] = {}

family_codes = {
    "expressions_variables": "EV", "conditionals": "CD", "loops": "LP",
    "functions": "FN", "arrays": "AR", "strings": "ST",
    "input_output": "IO", "composition_algorithms": "CP",
}

for family, questions in recognition.items():
    for index, (prompt, answer, signature) in enumerate(questions, 1):
        task_id = f"SYN-REC-{family_codes[family]}-{index:03d}"
        tasks.append({
            "task_id": task_id, "split": "phase1s_diagnostic", "level": "recognition",
            "family": family, "difficulty": "diagnostic", "prompt": prompt + " Reply with only A, B, or C.",
            "answer": answer, "template_lineage": f"phase1s-rec-{family_codes[family].lower()}-{signature}-v1",
            "structural_signature": signature, "control_flow": "recognition_choice",
            "constructs": [signature], "matched_scenario": None,
        })

for scenario in scenarios:
    reference = clean(scenario.reference)
    marker_index = scenario.reference.find(scenario.completion_token)
    if marker_index < 0:
        raise ValueError(f"Completion token missing for {scenario.code}")
    prefix = scenario.reference[:marker_index]
    suffix = scenario.reference[marker_index + len(scenario.completion_token):]
    case_rows = [
        {"case_id": chr(97 + index), "stdin": stdin, "expected_stdout": expected}
        for index, (stdin, expected) in enumerate(scenario.cases)
    ]
    common = {
        "split": "phase1s_diagnostic", "family": scenario.family,
        "difficulty": "diagnostic", "matched_scenario": scenario.code,
        "control_flow": scenario.control_flow,
        "constructs": [scenario.structure], "required_regex": [],
    }
    local_id = f"SYN-LOC-{scenario.code}-001"
    tasks.append(common | {
        "task_id": local_id, "level": "local_completion",
        "prompt": "Target behavior: " + scenario.prompt + "\nSupply only the missing GOCO fragment represented by <MISSING>. Do not return the full program.\n\n" + prefix + "<MISSING>" + suffix,
        "template_lineage": f"phase1s-loc-{scenario.code.lower()}-v1",
        "structural_signature": f"local::{scenario.structure}",
        "scaffold_prefix": prefix, "scaffold_suffix": suffix,
    })
    hidden[local_id] = case_rows
    references[local_id] = scenario.completion

    mod_id = f"SYN-MOD-{scenario.code}-001"
    tasks.append(common | {
        "task_id": mod_id, "level": "structured_modification",
        "prompt": scenario.modification_instruction + " Return the complete modified GOCO program.\n\nVALID STARTING PROGRAM:\n" + scenario.modification_source,
        "template_lineage": f"phase1s-mod-{scenario.code.lower()}-v1",
        "structural_signature": f"modification::{scenario.structure}",
    })
    hidden[mod_id] = case_rows
    references[mod_id] = reference

    full_id = f"SYN-FULL-{scenario.code}-001"
    tasks.append(common | {
        "task_id": full_id, "level": "full_synthesis", "prompt": scenario.prompt,
        "template_lineage": f"phase1s-full-{scenario.code.lower()}-v1",
        "structural_signature": f"full::{scenario.structure}",
    })
    hidden[full_id] = case_rows
    references[full_id] = reference


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / "diagnostic_tasks.json", tasks)
    write_json(OUT / "diagnostic_hidden_tests.json", hidden)
    write_json(OUT / "diagnostic_references.json", references)
    print(f"wrote {len(tasks)} diagnostic tasks: {len(hidden)} executable, {len(tasks)-len(hidden)} recognition")
