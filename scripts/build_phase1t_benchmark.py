from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


OUT = Path("benchmark/phase1t")


@dataclass(frozen=True)
class Task:
    family: str
    code: str
    prompt: str
    source: str
    cases: list[tuple[str, str]]
    algorithm: str
    control_flow: str
    ast_signature: str
    constructs: list[str]
    required_regex: list[str]


def t(family: str, code: str, prompt: str, source: str,
      cases: list[tuple[str, str]], algorithm: str, control_flow: str,
      ast_signature: str, constructs: list[str], required_regex: list[str] | None = None) -> Task:
    return Task(family, code, prompt, source.strip() + "\n", cases, algorithm,
                control_flow, ast_signature, constructs, required_regex or [])


tasks = [
    # Expressions and variables: distinct arithmetic/data-flow shapes.
    t("expressions_variables", "EV01", "Read a|b and print 3*a - 2*b.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] fields = strings.SPLIT(line, "|").
NUMBER a = strings.TO_NUMBER(fields[0]).
NUMBER b = strings.TO_NUMBER(fields[1]).
NUMBER weighted = 3 * a - 2 * b.
DISPLAYNL(weighted).''',
      [("0|0\n","0.0"),("4|5\n","2.0"),("-2|3\n","-12.0"),("1.5|2\n","0.5"),("10|-1\n","32.0")],
      "weighted_linear_combination", "straight_line", "import>split>convert2>affine>display", ["split","arithmetic"]),
    t("expressions_variables", "EV02", "Read price|quantity and print their product after applying a 20 percent discount.",
      '''IMPORT strings.
SENTENCE orderLine.
INPUT(orderLine).
SENTENCE[] fields = strings.SPLIT(orderLine, "|").
NUMBER price = strings.TO_NUMBER(fields[0]).
NUMBER quantity = strings.TO_NUMBER(fields[1]).
NUMBER subtotal = price * quantity.
NUMBER discounted = subtotal * 0.8.
DISPLAYNL(discounted).''',
      [("10|2\n","16.0"),("0|5\n","0.0"),("2.5|4\n","8.0"),("100|1\n","80.0"),("3|3\n","7.2")],
      "two_stage_discount", "straight_line", "import>split>convert2>multiply>scale>display", ["intermediate_values","arithmetic"]),
    t("expressions_variables", "EV03", "Read hours|minutes and print the total number of minutes.",
      '''IMPORT strings.
SENTENCE clockText.
INPUT(clockText).
SENTENCE[] pieces = strings.SPLIT(clockText, "|").
NUMBER hours = strings.TO_NUMBER(pieces[0]).
NUMBER minutes = strings.TO_NUMBER(pieces[1]).
minutes += hours * 60.
DISPLAYNL(minutes).''',
      [("0|0\n","0.0"),("1|30\n","90.0"),("2|5\n","125.0"),("10|59\n","659.0"),("0|45\n","45.0")],
      "unit_conversion_accumulation", "straight_line_compound_assignment", "import>split>convert2>compound_add>display", ["compound_assignment","conversion"]),
    t("expressions_variables", "EV04", "Read one NUMBER x and print x*x + 2*x + 1.",
      '''NUMBER x.
INPUT(x).
NUMBER square = x * x.
NUMBER linear = 2 * x.
DISPLAYNL(square + linear + 1).''',
      [("0\n","1.0"),("1\n","4.0"),("-1\n","0.0"),("3\n","16.0"),("2.5\n","12.25")],
      "quadratic_polynomial", "straight_line", "input_number>two_intermediates>sum_expression>display", ["numeric_input","polynomial"]),
    t("expressions_variables", "EV05", "Read radius|height and print cylinder volume using math.PI * radius * radius * height.",
      '''IMPORT strings.
IMPORT math.
SENTENCE dimensions.
INPUT(dimensions).
SENTENCE[] pieces = strings.SPLIT(dimensions, "|").
NUMBER radius = strings.TO_NUMBER(pieces[0]).
NUMBER height = strings.TO_NUMBER(pieces[1]).
DISPLAYNL(math.PI * radius * radius * height).''',
      [("0|5\n","0.0"),("1|1\n","3.141592653589793"),("2|3\n","37.69911184307752"),("1|2\n","6.283185307179586"),("0.5|4\n","3.141592653589793")],
      "cylinder_volume", "straight_line_library_constant", "import2>split>convert2>pi_product>display", ["math_constant","multi_factor"]),
    t("expressions_variables", "EV06", "Read one NUMBER x and print its distance from 10 using math.ABS.",
      '''IMPORT math.
NUMBER x.
INPUT(x).
NUMBER offset = x - 10.
DISPLAYNL(math.ABS(offset)).''',
      [("10\n","0.0"),("14\n","4.0"),("3\n","7.0"),("-2\n","12.0"),("10.5\n","0.5")],
      "absolute_distance", "straight_line_library_call", "import_math>input>subtract>abs>display", ["math_abs","intermediate"]),
    t("expressions_variables", "EV07", "Read a|b|c and print their arithmetic mean.",
      '''IMPORT strings.
SENTENCE triple.
INPUT(triple).
SENTENCE[] cells = strings.SPLIT(triple, "|").
NUMBER sum = strings.TO_NUMBER(cells[0]) + strings.TO_NUMBER(cells[1]) + strings.TO_NUMBER(cells[2]).
DISPLAYNL(sum / 3).''',
      [("1|2|3\n","2.0"),("0|0|0\n","0.0"),("-3|0|3\n","0.0"),("1.5|2.5|5\n","3.0"),("10|20|30\n","20.0")],
      "three_value_mean", "straight_line_nested_conversion", "import>split>three_inline_converts>divide>display", ["nested_calls","division"]),
    t("expressions_variables", "EV08", "Read value|lower|upper and print value clamped to the inclusive bounds using math.CLAMP.",
      '''IMPORT strings.
IMPORT math.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER value = strings.TO_NUMBER(p[0]).
NUMBER lower = strings.TO_NUMBER(p[1]).
NUMBER upper = strings.TO_NUMBER(p[2]).
DISPLAYNL(math.CLAMP(value, lower, upper)).''',
      [("5|0|10\n","5.0"),("-2|0|10\n","0.0"),("12|0|10\n","10.0"),("3|3|9\n","3.0"),("8|-5|7\n","7.0")],
      "bounded_clamp", "straight_line_ternary_library", "import2>split>convert3>clamp>display", ["math_clamp","three_inputs"]),

    # Conditionals: binary, multiway, compound and nested decisions.
    t("conditionals", "CD01", "Read one NUMBER and print NEGATIVE, ZERO, or POSITIVE.",
      '''NUMBER value.
INPUT(value).
IF (value < 0) {
    DISPLAYNL("NEGATIVE").
} ELSEIF (value == 0) {
    DISPLAYNL("ZERO").
} ELSE {
    DISPLAYNL("POSITIVE").
}''',
      [("-3\n","NEGATIVE"),("0\n","ZERO"),("4\n","POSITIVE"),("-0.5\n","NEGATIVE"),("2.5\n","POSITIVE")],
      "sign_classification", "if_elseif_else", "input>if_lt>elseif_eq>else>display_labels", ["three_way_branch"]),
    t("conditionals", "CD02", "Read one NUMBER score and print A for score >= 90, B for >= 75, C for >= 60, otherwise F.",
      '''NUMBER score.
INPUT(score).
IF (score >= 90) {
    DISPLAYNL("A").
} ELSEIF (score >= 75) {
    DISPLAYNL("B").
} ELSEIF (score >= 60) {
    DISPLAYNL("C").
} ELSE {
    DISPLAYNL("F").
}''',
      [("95\n","A"),("90\n","A"),("80\n","B"),("60\n","C"),("59\n","F"),("74\n","C")],
      "ordered_grade_thresholds", "if_two_elseif_else", "input>descending_threshold_chain4>display", ["multiway_branch","boundary_order"]),
    t("conditionals", "CD03", "Read a|b|c as side lengths. Print VALID if all are positive and each pair sums to more than the third; otherwise INVALID.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER a = strings.TO_NUMBER(p[0]).
NUMBER b = strings.TO_NUMBER(p[1]).
NUMBER c = strings.TO_NUMBER(p[2]).
IF (a > 0 AND b > 0 AND c > 0 AND a + b > c AND a + c > b AND b + c > a) {
    DISPLAYNL("VALID").
} ELSE {
    DISPLAYNL("INVALID").
}''',
      [("3|4|5\n","VALID"),("1|1|2\n","INVALID"),("-1|2|2\n","INVALID"),("2|2|3\n","VALID"),("10|1|1\n","INVALID")],
      "triangle_validity", "compound_if_else", "split3>six_conjunct_condition>binary_label", ["logic_and","triangle_inequality"]),
    t("conditionals", "CD04", "Read a whole NUMBER year and print LEAP when divisible by 400 or divisible by 4 but not 100; otherwise COMMON.",
      '''NUMBER year.
INPUT(year).
LOGIC leap = year % 400 == 0 OR (year % 4 == 0 AND year % 100 != 0).
IF (leap) {
    DISPLAYNL("LEAP").
} ELSE {
    DISPLAYNL("COMMON").
}''',
      [("2000\n","LEAP"),("1900\n","COMMON"),("2024\n","LEAP"),("2023\n","COMMON"),("2400\n","LEAP"),("2100\n","COMMON")],
      "gregorian_leap_rule", "logic_assignment_then_if", "input>boolean_or_nested_and>if_logic>display", ["logic_variable","modulo"]),
    t("conditionals", "CD05", "Read a|b|c and print the middle value (the median).",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER a = strings.TO_NUMBER(p[0]).
NUMBER b = strings.TO_NUMBER(p[1]).
NUMBER c = strings.TO_NUMBER(p[2]).
IF ((a >= b AND a <= c) OR (a >= c AND a <= b)) {
    DISPLAYNL(a).
} ELSEIF ((b >= a AND b <= c) OR (b >= c AND b <= a)) {
    DISPLAYNL(b).
} ELSE {
    DISPLAYNL(c).
}''',
      [("1|2|3\n","2.0"),("3|1|2\n","2.0"),("2|3|1\n","2.0"),("5|5|2\n","5.0"),("-1|-3|-2\n","-2.0")],
      "median_of_three", "compound_if_elseif_else", "split3>range_membership_a>range_membership_b>else", ["logic_or","ordered_selection"]),
    t("conditionals", "CD06", "Read one whole NUMBER n. Print POSITIVE EVEN, POSITIVE ODD, or NONPOSITIVE.",
      '''NUMBER n.
INPUT(n).
IF (n <= 0) {
    DISPLAYNL("NONPOSITIVE").
} ELSE {
    IF (n % 2 == 0) {
        DISPLAYNL("POSITIVE EVEN").
    } ELSE {
        DISPLAYNL("POSITIVE ODD").
    }
}''',
      [("-2\n","NONPOSITIVE"),("0\n","NONPOSITIVE"),("2\n","POSITIVE EVEN"),("7\n","POSITIVE ODD"),("12\n","POSITIVE EVEN")],
      "positive_parity", "nested_if_else", "input>outer_nonpositive>inner_parity>labels", ["nested_branch","modulo"]),
    t("conditionals", "CD07", "Read one NUMBER temperature and print COLD below 10, MILD from 10 through 25 inclusive, and HOT above 25.",
      '''NUMBER temperature.
INPUT(temperature).
IF (temperature < 10) {
    DISPLAYNL("COLD").
} ELSEIF (temperature <= 25) {
    DISPLAYNL("MILD").
} ELSE {
    DISPLAYNL("HOT").
}''',
      [("9\n","COLD"),("10\n","MILD"),("25\n","MILD"),("26\n","HOT"),("-5\n","COLD")],
      "bounded_temperature_band", "if_elseif_else", "input>lower_cut>upper_cut>display3", ["interval_classification"]),
    t("conditionals", "CD08", "Read x|y. Print AXIS if either is zero, Q1 if both are positive, Q3 if both are negative, otherwise MIXED.",
      '''IMPORT strings.
SENTENCE coordinates.
INPUT(coordinates).
SENTENCE[] p = strings.SPLIT(coordinates, "|").
NUMBER x = strings.TO_NUMBER(p[0]).
NUMBER y = strings.TO_NUMBER(p[1]).
IF (x == 0 OR y == 0) {
    DISPLAYNL("AXIS").
} ELSEIF (x > 0 AND y > 0) {
    DISPLAYNL("Q1").
} ELSEIF (x < 0 AND y < 0) {
    DISPLAYNL("Q3").
} ELSE {
    DISPLAYNL("MIXED").
}''',
      [("0|2\n","AXIS"),("3|4\n","Q1"),("-2|-8\n","Q3"),("-1|5\n","MIXED"),("7|-3\n","MIXED"),("2|0\n","AXIS")],
      "coordinate_region", "if_two_elseif_else", "split2>axis_or>q1_and>q3_and>else", ["logic_composition","four_way_branch"]),

    # Loops: accumulators, filters, counters and nested iteration.
    t("loops", "LP01", "Read a nonnegative whole NUMBER n and print n factorial using a loop.",
      '''NUMBER n.
INPUT(n).
NUMBER product = 1.
LOOP (NUMBER factor = 2 TILL factor <= n, factor++) {
    product *= factor.
}
DISPLAYNL(product).''',
      [("0\n","1.0"),("1\n","1.0"),("2\n","2.0"),("5\n","120.0"),("7\n","5040.0")],
      "iterative_factorial", "for_loop_product", "input>init_one>for_from2>multiply>display", ["loop","product_accumulator"]),
    t("loops", "LP02", "Read a nonnegative whole NUMBER n and print the sum of odd squares from 1 through n.",
      '''NUMBER n.
INPUT(n).
NUMBER total = 0.
LOOP (NUMBER i = 1 TILL i <= n, i += 2) {
    total += i * i.
}
DISPLAYNL(total).''',
      [("0\n","0.0"),("1\n","1.0"),("2\n","1.0"),("5\n","35.0"),("7\n","84.0")],
      "odd_square_series", "for_loop_step_two", "input>init_zero>for_odd_step2>square_sum>display", ["loop","nonunit_step"]),
    t("loops", "LP03", "Read limit|divisor and print how many whole numbers from 1 through limit are divisible by divisor.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER limit = strings.TO_NUMBER(p[0]).
NUMBER divisor = strings.TO_NUMBER(p[1]).
NUMBER count = 0.
LOOP (NUMBER candidate = 1 TILL candidate <= limit, candidate++) {
    IF (candidate % divisor == 0) {
        count++.
    }
}
DISPLAYNL(count).''',
      [("10|2\n","5.0"),("10|3\n","3.0"),("5|7\n","0.0"),("1|1\n","1.0"),("20|5\n","4.0")],
      "divisibility_count", "for_loop_conditional_counter", "split2>counter>for>mod_if>increment>display", ["loop","conditional_count"]),
    t("loops", "LP04", "Read a positive whole NUMBER n and print the first five multiples of n, one per line.",
      '''NUMBER n.
INPUT(n).
LOOP (NUMBER multiplier = 1 TILL multiplier <= 5, multiplier++) {
    DISPLAYNL(n * multiplier).
}''',
      [("1\n","1.0\n2.0\n3.0\n4.0\n5.0"),("2\n","2.0\n4.0\n6.0\n8.0\n10.0"),("3\n","3.0\n6.0\n9.0\n12.0\n15.0"),("5\n","5.0\n10.0\n15.0\n20.0\n25.0"),("10\n","10.0\n20.0\n30.0\n40.0\n50.0")],
      "fixed_multiplication_table", "for_loop_direct_output", "input>fixed_bound_for>product_display_each", ["loop","multi_line_output"]),
    t("loops", "LP05", "Read a positive whole NUMBER n and print its decimal digit count.",
      '''IMPORT math.
NUMBER n.
INPUT(n).
NUMBER digits = 0.
LOOP (n >= 1) {
    digits++.
    n = math.FLOOR(n / 10).
}
DISPLAYNL(digits).''',
      [("1\n","1.0"),("9\n","1.0"),("10\n","2.0"),("999\n","3.0"),("10000\n","5.0")],
      "decimal_digit_count", "while_loop_destructive_division", "import_math>input>while_ge1>increment>floor_divide>display", ["while_loop","floor"]),
    t("loops", "LP06", "Read a nonnegative whole NUMBER n and print every even number from 0 through n, one per line.",
      '''NUMBER n.
INPUT(n).
LOOP (NUMBER evenValue = 0 TILL evenValue <= n, evenValue += 2) {
    DISPLAYNL(evenValue).
}''',
      [("0\n","0.0"),("1\n","0.0"),("2\n","0.0\n2.0"),("5\n","0.0\n2.0\n4.0"),("8\n","0.0\n2.0\n4.0\n6.0\n8.0")],
      "even_sequence", "for_loop_step_two_output", "input>for_zero_step2>display_each", ["loop","sequence_output"]),
    t("loops", "LP07", "Read rows|columns and print rows lines, each containing columns asterisks. Use loops.",
      '''IMPORT strings.
SENTENCE dimensions.
INPUT(dimensions).
SENTENCE[] p = strings.SPLIT(dimensions, "|").
NUMBER rows = strings.TO_NUMBER(p[0]).
NUMBER columns = strings.TO_NUMBER(p[1]).
LOOP (NUMBER row = 0 TILL row < rows, row++) {
    LOOP (NUMBER column = 0 TILL column < columns, column++) {
        DISPLAY("*").
    }
    DISPLAYNL("").
}''',
      [("1|1\n","*"),("2|3\n","***\n***"),("3|2\n","**\n**\n**"),("1|4\n","****"),("4|1\n","*\n*\n*\n*")],
      "rectangle_pattern", "nested_for_loops", "split2>outer_rows>inner_columns>display_star>newline", ["nested_loops","pattern_output"], ["LOOP[\\s\\S]*LOOP"]),
    t("loops", "LP08", "Read a positive whole NUMBER n and print the sum 1 - 2 + 3 - 4 and so on through n.",
      '''NUMBER n.
INPUT(n).
NUMBER total = 0.
LOOP (NUMBER i = 1 TILL i <= n, i++) {
    IF (i % 2 == 0) {
        total -= i.
    } ELSE {
        total += i.
    }
}
DISPLAYNL(total).''',
      [("1\n","1.0"),("2\n","-1.0"),("3\n","2.0"),("4\n","-2.0"),("7\n","4.0"),("8\n","-4.0")],
      "alternating_sum", "for_loop_if_else_accumulator", "input>for>parity_branch>plus_minus_accumulate>display", ["loop","branching_accumulator"]),

    # Functions: different signatures, return types and internal control flow.
    t("functions", "FN01", "Define cube(NUMBER x) returning x*x*x. Read one NUMBER and print cube(input).",
      '''FUNCTION cube(NUMBER x) {
    RETURN x * x * x.
} RETURNS NUMBER.
NUMBER inputValue.
INPUT(inputValue).
DISPLAYNL(cube(inputValue)).''',
      [("0\n","0.0"),("2\n","8.0"),("-3\n","-27.0"),("1.5\n","3.375"),("10\n","1000.0")],
      "cube_function", "pure_function_then_call", "function1>return_product3>input>call>display", ["function","numeric_return"]),
    t("functions", "FN02", "Define clampValue(NUMBER value, NUMBER low, NUMBER high) using IF statements, returning the bounded value. Read value|low|high and print the result.",
      '''IMPORT strings.
FUNCTION clampValue(NUMBER value, NUMBER low, NUMBER high) {
    IF (value < low) {
        RETURN low.
    }
    IF (value > high) {
        RETURN high.
    }
    RETURN value.
} RETURNS NUMBER.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
DISPLAYNL(clampValue(strings.TO_NUMBER(p[0]), strings.TO_NUMBER(p[1]), strings.TO_NUMBER(p[2]))).''',
      [("5|0|10\n","5.0"),("-1|0|10\n","0.0"),("20|0|10\n","10.0"),("3|3|8\n","3.0"),("7|-2|6\n","6.0")],
      "manual_clamp_function", "function_early_returns", "import>function3>if_return>if_return>return>split>nested_call", ["function","early_return"]),
    t("functions", "FN03", "Define isMultiple(NUMBER value, NUMBER divisor) returning LOGIC. Read value|divisor and print YES when true, otherwise NO.",
      '''IMPORT strings.
FUNCTION isMultiple(NUMBER value, NUMBER divisor) {
    RETURN value % divisor == 0.
} RETURNS LOGIC.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
LOGIC answer = isMultiple(strings.TO_NUMBER(p[0]), strings.TO_NUMBER(p[1])).
IF (answer) {
    DISPLAYNL("YES").
} ELSE {
    DISPLAYNL("NO").
}''',
      [("10|2\n","YES"),("10|3\n","NO"),("0|5\n","YES"),("-9|3\n","YES"),("7|7\n","YES")],
      "divisibility_predicate", "logic_function_then_branch", "import>function2_logic>split>call_assign>if_else", ["function","logic_return"]),
    t("functions", "FN04", "Define absoluteDifference(NUMBER a, NUMBER b) without math.ABS, returning the nonnegative difference. Read a|b and print it.",
      '''IMPORT strings.
FUNCTION absoluteDifference(NUMBER a, NUMBER b) {
    IF (a >= b) {
        RETURN a - b.
    }
    RETURN b - a.
} RETURNS NUMBER.
SENTENCE pairText.
INPUT(pairText).
SENTENCE[] p = strings.SPLIT(pairText, "|").
NUMBER left = strings.TO_NUMBER(p[0]).
NUMBER right = strings.TO_NUMBER(p[1]).
DISPLAYNL(absoluteDifference(left, right)).''',
      [("5|2\n","3.0"),("2|5\n","3.0"),("-3|-8\n","5.0"),("4|4\n","0.0"),("1.5|4\n","2.5")],
      "absolute_difference_function", "function_branch_return", "import>function2>if_return>fallback_return>split>convert>call", ["function","branching_return"]),
    t("functions", "FN05", "Define triangleSum(NUMBER n) that uses a loop and returns the sum from 1 through n. Read n and print the result.",
      '''FUNCTION triangleSum(NUMBER n) {
    NUMBER total = 0.
    LOOP (NUMBER i = 1 TILL i <= n, i++) {
        total += i.
    }
    RETURN total.
} RETURNS NUMBER.
NUMBER n.
INPUT(n).
DISPLAYNL(triangleSum(n)).''',
      [("0\n","0.0"),("1\n","1.0"),("3\n","6.0"),("10\n","55.0"),("20\n","210.0")],
      "summation_function", "function_with_for_loop", "function>local_accumulator>for>return>input>call", ["function","loop_inside"]),
    t("functions", "FN06", "Define minTwo(NUMBER a, NUMBER b), then define minThree(NUMBER a, NUMBER b, NUMBER c) using minTwo. Read a|b|c and print minThree.",
      '''IMPORT strings.
FUNCTION minTwo(NUMBER a, NUMBER b) {
    IF (a < b) {
        RETURN a.
    }
    RETURN b.
} RETURNS NUMBER.
FUNCTION minThree(NUMBER a, NUMBER b, NUMBER c) {
    RETURN minTwo(minTwo(a, b), c).
} RETURNS NUMBER.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
DISPLAYNL(minThree(strings.TO_NUMBER(p[0]), strings.TO_NUMBER(p[1]), strings.TO_NUMBER(p[2]))).''',
      [("1|2|3\n","1.0"),("3|1|2\n","1.0"),("2|3|1\n","1.0"),("5|5|7\n","5.0"),("-1|-9|0\n","-9.0")],
      "composed_minimum_functions", "ordered_function_composition", "import>function2_branch>function3_nested_calls>split>call", ["two_functions","nested_call"]),
    t("functions", "FN07", "Define parityLabel(NUMBER n) returning SENTENCE EVEN or ODD. Read a whole number and print the returned label.",
      '''FUNCTION parityLabel(NUMBER n) {
    IF (n % 2 == 0) {
        RETURN "EVEN".
    }
    RETURN "ODD".
} RETURNS SENTENCE.
NUMBER value.
INPUT(value).
SENTENCE label = parityLabel(value).
DISPLAYNL(label).''',
      [("0\n","EVEN"),("1\n","ODD"),("2\n","EVEN"),("-3\n","ODD"),("100\n","EVEN")],
      "parity_label_function", "sentence_function_branch", "function_number_to_sentence>if_return>return>input>call_assign>display", ["function","sentence_return"]),
    t("functions", "FN08", "Define applyRate(NUMBER amount, NUMBER percent) returning amount + amount*percent/100. Read amount|percent and print it.",
      '''IMPORT strings.
FUNCTION applyRate(NUMBER amount, NUMBER percent) {
    NUMBER change = amount * percent / 100.
    RETURN amount + change.
} RETURNS NUMBER.
SENTENCE values.
INPUT(values).
SENTENCE[] p = strings.SPLIT(values, "|").
NUMBER amount = strings.TO_NUMBER(p[0]).
NUMBER percent = strings.TO_NUMBER(p[1]).
DISPLAYNL(applyRate(amount, percent)).''',
      [("100|10\n","110.0"),("50|20\n","60.0"),("80|-25\n","60.0"),("0|50\n","0.0"),("40|12.5\n","45.0")],
      "percentage_adjustment_function", "function_local_then_return", "import>function2>local_calc>return>split>convert2>call", ["function","local_variable"]),

    # Arrays: literals, scans, indexed transforms and library reductions.
    t("arrays", "AR01", "Read four numbers separated by |, store them in a NUMBER array, and print their product.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER[] values = [strings.TO_NUMBER(p[0]), strings.TO_NUMBER(p[1]), strings.TO_NUMBER(p[2]), strings.TO_NUMBER(p[3])].
NUMBER product = 1.
LOOP (NUMBER i = 0 TILL i < 4, i++) {
    product *= values[i].
}
DISPLAYNL(product).''',
      [("1|2|3|4\n","24.0"),("0|2|3|4\n","0.0"),("-1|2|-3|4\n","24.0"),("0.5|2|3|4\n","12.0"),("5|1|1|2\n","10.0")],
      "array_product", "array_for_reduction", "split4>array_literal>product_init>indexed_for_multiply>display", ["array","loop_reduction"]),
    t("arrays", "AR02", "Read five numbers separated by |, store them in a NUMBER array, and print their average using arrays.SUM.",
      '''IMPORT strings.
IMPORT arrays.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER[] values = [strings.TO_NUMBER(p[0]), strings.TO_NUMBER(p[1]), strings.TO_NUMBER(p[2]), strings.TO_NUMBER(p[3]), strings.TO_NUMBER(p[4])].
DISPLAYNL(arrays.SUM(values) / 5).''',
      [("1|2|3|4|5\n","3.0"),("0|0|0|0|0\n","0.0"),("-2|-1|0|1|2\n","0.0"),("5|5|5|5|5\n","5.0"),("1.5|2.5|3.5|4.5|5.5\n","3.5")],
      "array_library_average", "array_library_reduction", "import_strings_arrays>split5>array_literal>sum_divide>display", ["array","arrays_sum"]),
    t("arrays", "AR03", "Read five numbers separated by |, store them in an array, and print how many are positive.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER[] values = [strings.TO_NUMBER(p[0]), strings.TO_NUMBER(p[1]), strings.TO_NUMBER(p[2]), strings.TO_NUMBER(p[3]), strings.TO_NUMBER(p[4])].
NUMBER positiveCount = 0.
LOOP (NUMBER index = 0 TILL index < 5, index++) {
    IF (values[index] > 0) {
        positiveCount++.
    }
}
DISPLAYNL(positiveCount).''',
      [("1|2|3|4|5\n","5.0"),("0|0|0|0|0\n","0.0"),("-1|2|-3|4|0\n","2.0"),("-1|-2|-3|-4|-5\n","0.0"),("1|0|0|0|-1\n","1.0")],
      "positive_array_count", "array_loop_conditional_counter", "split5>array>count>indexed_for>positive_if>increment>display", ["array","conditional_count"]),
    t("arrays", "AR04", "Read target|a|b|c|d. Store a,b,c,d in an array and print how many equal target.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER target = strings.TO_NUMBER(p[0]).
NUMBER[] values = [strings.TO_NUMBER(p[1]), strings.TO_NUMBER(p[2]), strings.TO_NUMBER(p[3]), strings.TO_NUMBER(p[4])].
NUMBER matches = 0.
LOOP (NUMBER i = 0 TILL i < 4, i++) {
    IF (values[i] == target) {
        matches++.
    }
}
DISPLAYNL(matches).''',
      [("2|1|2|2|3\n","2.0"),("0|0|0|0|0\n","4.0"),("5|1|2|3|4\n","0.0"),("-1|-1|2|-1|4\n","2.0"),("3.5|3.5|0|3.5|3.5\n","3.0")],
      "target_frequency", "array_loop_equality_counter", "split5>target_plus_array>count>indexed_for>equality_if>display", ["array","target_scan"]),
    t("arrays", "AR05", "Read a|b|c|d, store the values in an array, and print d|c|b|a with no spaces.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER[] values = [strings.TO_NUMBER(p[0]), strings.TO_NUMBER(p[1]), strings.TO_NUMBER(p[2]), strings.TO_NUMBER(p[3])].
DISPLAY(values[3]).
DISPLAY("|").
DISPLAY(values[2]).
DISPLAY("|").
DISPLAY(values[1]).
DISPLAY("|").
DISPLAYNL(values[0]).''',
      [("1|2|3|4\n","4.0|3.0|2.0|1.0"),("0|-1|5|8\n","8.0|5.0|-1.0|0.0"),("2.5|3.5|4.5|5.5\n","5.5|4.5|3.5|2.5"),("7|7|8|8\n","8.0|8.0|7.0|7.0"),("-4|-3|-2|-1\n","-1.0|-2.0|-3.0|-4.0")],
      "fixed_array_reverse_output", "indexed_multi_output", "split4>array_literal>reverse_index_display_sequence", ["array","formatting"]),
    t("arrays", "AR06", "Read a|b|c|x|y|z. Store the first and last three numbers in two arrays and print their dot product.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER[] left = [strings.TO_NUMBER(p[0]), strings.TO_NUMBER(p[1]), strings.TO_NUMBER(p[2])].
NUMBER[] right = [strings.TO_NUMBER(p[3]), strings.TO_NUMBER(p[4]), strings.TO_NUMBER(p[5])].
NUMBER dot = 0.
LOOP (NUMBER i = 0 TILL i < 3, i++) {
    dot += left[i] * right[i].
}
DISPLAYNL(dot).''',
      [("1|2|3|4|5|6\n","32.0"),("0|0|0|1|2|3\n","0.0"),("1|0|0|5|9|9\n","5.0"),("-1|2|-3|4|-5|6\n","-32.0"),("0.5|1|2|2|3|4\n","12.0")],
      "vector_dot_product", "parallel_array_for_reduction", "split6>two_arrays>dot_init>parallel_index_multiply_sum>display", ["two_arrays","loop_reduction"]),
    t("arrays", "AR07", "Read four numbers separated by |, store them in an array, and print maximum minus minimum.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER[] values = [strings.TO_NUMBER(p[0]), strings.TO_NUMBER(p[1]), strings.TO_NUMBER(p[2]), strings.TO_NUMBER(p[3])].
NUMBER minimum = values[0].
NUMBER maximum = values[0].
LOOP (NUMBER i = 1 TILL i < 4, i++) {
    IF (values[i] < minimum) {
        minimum = values[i].
    }
    IF (values[i] > maximum) {
        maximum = values[i].
    }
}
DISPLAYNL(maximum - minimum).''',
      [("1|2|3|4\n","3.0"),("5|5|5|5\n","0.0"),("-2|4|-8|1\n","12.0"),("0|10|3|7\n","10.0"),("1.5|2.5|0.5|4.5\n","4.0")],
      "array_range", "array_loop_dual_branch", "split4>array>minmax_init>indexed_for>two_if_updates>difference", ["array","dual_extrema"]),
    t("arrays", "AR08", "Read a|b|c|d, store them in an array, and print b|c|d|a (a left rotation).",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER[] values = [strings.TO_NUMBER(p[0]), strings.TO_NUMBER(p[1]), strings.TO_NUMBER(p[2]), strings.TO_NUMBER(p[3])].
NUMBER first = values[0].
LOOP (NUMBER i = 0 TILL i < 3, i++) {
    values[i] = values[i + 1].
}
values[3] = first.
DISPLAY(values[0]).
DISPLAY("|").
DISPLAY(values[1]).
DISPLAY("|").
DISPLAY(values[2]).
DISPLAY("|").
DISPLAYNL(values[3]).''',
      [("1|2|3|4\n","2.0|3.0|4.0|1.0"),("0|-1|5|8\n","-1.0|5.0|8.0|0.0"),("2.5|3.5|4.5|5.5\n","3.5|4.5|5.5|2.5"),("7|7|8|8\n","7.0|8.0|8.0|7.0"),("-4|-3|-2|-1\n","-3.0|-2.0|-1.0|-4.0")],
      "in_place_left_rotation", "array_shift_loop_then_output", "split4>array>save_first>shift_for>restore_last>display4", ["array_mutation","index_shift"]),

    # Strings: library calls, predicates, transformations and indexed scans.
    t("strings", "ST01", "Read one SENTENCE, reverse it, convert the result to uppercase, and print it.",
      '''IMPORT strings.
SENTENCE text.
INPUT(text).
SENTENCE reversed = strings.REVERSE(text).
DISPLAYNL(strings.UPPER(reversed)).''',
      [("Abc\n","CBA"),("GOCO\n","OCOG"),("a b\n","B A"),("x\n","X"),("123a\n","A321")],
      "reverse_then_upper", "sequential_string_transform", "import>input_sentence>reverse_assign>upper_display", ["strings_reverse","strings_upper"]),
    t("strings", "ST02", "Read text|needle and print how many times needle occurs in text using strings.COUNT.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
DISPLAYNL(strings.COUNT(p[0], p[1])).''',
      [("banana|a\n","3.0"),("hello|l\n","2.0"),("abc|z\n","0.0"),("aaaa|aa\n","2.0"),("GOCO|O\n","2.0")],
      "substring_count", "direct_string_library_reduction", "import>split2>count_call>display", ["strings_count","split"]),
    t("strings", "ST03", "Read prefix|text|suffix. Print BOTH when text starts with prefix and ends with suffix, otherwise NO.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
LOGIC starts = strings.STARTSWITH(p[1], p[0]).
LOGIC ends = strings.ENDSWITH(p[1], p[2]).
IF (starts AND ends) {
    DISPLAYNL("BOTH").
} ELSE {
    DISPLAYNL("NO").
}''',
      [("a|abc|c\n","BOTH"),("ab|abc|bc\n","BOTH"),("x|abc|c\n","NO"),("a|abc|x\n","NO"),("same|same|same\n","BOTH")],
      "prefix_suffix_predicate", "two_library_predicates_then_if", "import>split3>startswith_assign>endswith_assign>and_if", ["string_predicates","logic"]),
    t("strings", "ST04", "Read one SENTENCE, replace every ordinary space with a hyphen, and print it.",
      '''IMPORT strings.
SENTENCE text.
INPUT(text).
SENTENCE changed = strings.REPLACE(text, " ", "-").
DISPLAYNL(changed).''',
      [("a b c\n","a-b-c"),("none\n","none"),(" two words\n","-two-words"),("a  b\n","a--b"),("x y\n","x-y")],
      "space_to_hyphen", "string_replace_assignment", "import>input>replace_assign>display", ["strings_replace"]),
    t("strings", "ST05", "Read text|times and print text repeated times using strings.REPEAT.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER times = strings.TO_NUMBER(p[1]).
DISPLAYNL(strings.REPEAT(p[0], times)).''',
      [("x|1\n","x"),("ab|3\n","ababab"),("z|0\n",""),("go|2\n","gogo"),("-|4\n","----")],
      "string_repetition", "split_convert_library_call", "import>split2>convert_count>repeat>display", ["strings_repeat","numeric_argument"]),
    t("strings", "ST06", "Read text|index and print the character at the zero-based index using strings.CHARAT.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER index = strings.TO_NUMBER(p[1]).
NUMBER lastIndex = strings.LENGTH(p[0]) - 1.
IF (index <= lastIndex) {
    DISPLAYNL(strings.CHARAT(p[0], index)).
}''',
      [("abc|0\n","a"),("abc|2\n","c"),("hello|1\n","e"),("GOCO|3\n","O"),("a b|1\n"," ")],
      "indexed_character", "bounded_index_branch", "import>split2>convert_index>length_minus_one>if_bound>charat_display", ["strings_charat","indexing","branch"]),
    t("strings", "ST07", "Read text|needle and print FOUND if text contains needle, otherwise MISSING.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
IF (strings.CONTAINS(p[0], p[1])) {
    DISPLAYNL("FOUND").
} ELSE {
    DISPLAYNL("MISSING").
}''',
      [("banana|nan\n","FOUND"),("hello|x\n","MISSING"),("GOCO|GO\n","FOUND"),("abc|abc\n","FOUND"),("abc|A\n","MISSING")],
      "substring_membership", "library_predicate_if_else", "import>split2>contains_condition>display2", ["strings_contains","branch"]),
    t("strings", "ST08", "Read one SENTENCE, trim ordinary surrounding whitespace, convert it to uppercase, and print it.",
      '''IMPORT strings.
SENTENCE text.
INPUT(text).
SENTENCE trimmed = strings.TRIM(text, "").
SENTENCE upper = strings.UPPER(trimmed).
DISPLAYNL(upper).''',
      [("  abc  \n","ABC"),("x\n","X"),(" two words \n","TWO WORDS"),("    \n",""),(" a B c \n","A B C")],
      "trim_then_upper", "two_stage_string_transform", "import>input>trim_assign>upper_assign>display", ["strings_trim","strings_upper"]),

    # Input/output: exact formatting contracts with distinct field arrangements.
    t("input_output", "IO01", "Read city|country and print country: city with exactly one space after the colon.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
DISPLAY(p[1]).
DISPLAY(": ").
DISPLAYNL(p[0]).''',
      [("Paris|France\n","France: Paris"),("Tokyo|Japan\n","Japan: Tokyo"),("X|Y\n","Y: X"),("New York|USA\n","USA: New York"),("a|b c\n","b c: a")],
      "city_country_reformat", "split_three_display", "import>split2>display_field1>literal>field0_newline", ["formatting","field_reorder"]),
    t("input_output", "IO02", "Read key|value and print <key>(value) with no spaces.",
      '''IMPORT strings.
SENTENCE record.
INPUT(record).
SENTENCE[] p = strings.SPLIT(record, "|").
DISPLAY("<").
DISPLAY(p[0]).
DISPLAY(">(").
DISPLAY(p[1]).
DISPLAYNL(")").''',
      [("x|3\n","<x>(3.0)"),("name|Ada\n","<name>(Ada)"),("A|B C\n","<A>(B C)"),("empty|\n","<empty>()"),("k|-2.5\n","<k>(-2.5)")],
      "angle_parenthesis_format", "split_five_display", "import>split2>literal_field_literal_field_literal", ["formatting","delimiters"]),
    t("input_output", "IO03", "Read first|last|id and print id - last, first with spaces around the hyphen and one space after the comma.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
DISPLAY(p[2]).
DISPLAY(" - ").
DISPLAY(p[1]).
DISPLAY(", ").
DISPLAYNL(p[0]).''',
      [("Ada|Lovelace|42\n","42.0 - Lovelace, Ada"),("A|B|C\n","C - B, A"),("first name|last name|7\n","7.0 - last name, first name"),("x|y|0\n","0.0 - y, x"),("One|Two|ID\n","ID - Two, One")],
      "identifier_name_format", "split_reordered_five_display", "import>split3>field2>literal>field1>literal>field0", ["formatting","three_fields"]),
    t("input_output", "IO04", "Read label|a|b and print label=a+b=result, where result is numeric and there are no spaces.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER a = strings.TO_NUMBER(p[1]).
NUMBER b = strings.TO_NUMBER(p[2]).
DISPLAY(p[0]).
DISPLAY("=").
DISPLAY(a).
DISPLAY("+").
DISPLAY(b).
DISPLAY("=").
DISPLAYNL(a + b).''',
      [("sum|2|3\n","sum=2.0+3.0=5.0"),("x|0|0\n","x=0.0+0.0=0.0"),("n|-2|5\n","n=-2.0+5.0=3.0"),("v|1.5|2.5\n","v=1.5+2.5=4.0"),("A|10|-1\n","A=10.0+-1.0=9.0")],
      "labelled_equation", "split_convert_interleaved_output", "import>split3>convert2>field_literal_number_literal_number_literal_sum", ["formatting","numeric_output"]),
    t("input_output", "IO05", "Read word|number and print number lines, each containing word.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER repetitions = strings.TO_NUMBER(p[1]).
LOOP (NUMBER i = 0 TILL i < repetitions, i++) {
    DISPLAYNL(p[0]).
}''',
      [("x|1\n","x"),("go|3\n","go\ngo\ngo"),("none|0\n",""),("two words|2\n","two words\ntwo words"),("A|4\n","A\nA\nA\nA")],
      "repeated_line_output", "split_for_display", "import>split2>convert_count>for>field_display_each", ["loop","multi_line_output"]),
    t("input_output", "IO06", "Read left|middle|right and print (left)[middle]{right} with no spaces.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
DISPLAY("(").
DISPLAY(p[0]).
DISPLAY(")[").
DISPLAY(p[1]).
DISPLAY("]{").
DISPLAY(p[2]).
DISPLAYNL("}").''',
      [("a|b|c\n","(a)[b]{c}"),("1|2|3\n","(1.0)[2.0]{3.0}"),("x y|z|q r\n","(x y)[z]{q r}"),("||\n","()[]{}"),("A|B C|D\n","(A)[B C]{D}")],
      "multi_bracket_format", "split_seven_display", "import>split3>three_bracket_pairs_interleaved", ["formatting","nested_delimiters"]),
    t("input_output", "IO07", "Read item|count|price and print countx item @ price exactly, with one space before and after @.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
SENTENCE countText = strings.TO_SENTENCE(p[1]).
SENTENCE priceText = strings.TO_SENTENCE(p[2]).
DISPLAYNL(countText + "x " + p[0] + " @ " + priceText).''',
      [("apple|3|2.50\n","3.0x apple @ 2.5"),("book|1|10\n","1.0x book @ 10.0"),("red pen|2|1.5\n","2.0x red pen @ 1.5"),("x|0|0\n","0.0x x @ 0.0"),("A|12|-3\n","12.0x A @ -3.0")],
      "invoice_line_format", "split_convert_concat_display", "import>split3>to_sentence_count>to_sentence_price>concatenate_all>display", ["formatting","string_concatenation"]),
    t("input_output", "IO08", "Read title|status. Print [status] on the first line and title on the second line.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
DISPLAY("[").
DISPLAY(p[1]).
DISPLAYNL("]").
DISPLAYNL(p[0]).''',
      [("Build|OK\n","[OK]\nBuild"),("Task one|PENDING\n","[PENDING]\nTask one"),("X|Y\n","[Y]\nX"),("empty|\n","[]\nempty"),("Hello world|DONE\n","[DONE]\nHello world")],
      "two_line_status_format", "split_bracket_line_then_field_line", "import>split2>bracketed_field1_newline>field0_newline", ["formatting","two_line_output"]),

    # Composition/algorithms: multiple interacting constructs.
    t("composition_algorithms", "CP01", "Read a positive whole NUMBER n and print PRIME if it is prime, otherwise COMPOSITE. Treat 1 as COMPOSITE.",
      '''NUMBER n.
INPUT(n).
LOGIC prime = n > 1.
LOOP (NUMBER divisor = 2 TILL divisor * divisor <= n, divisor++) {
    IF (n % divisor == 0) {
        prime = FALSE.
    }
}
IF (prime) {
    DISPLAYNL("PRIME").
} ELSE {
    DISPLAYNL("COMPOSITE").
}''',
      [("1\n","COMPOSITE"),("2\n","PRIME"),("3\n","PRIME"),("4\n","COMPOSITE"),("17\n","PRIME"),("25\n","COMPOSITE")],
      "trial_division_prime", "loop_flag_then_branch", "input>prime_flag>sqrt_bound_for>divisor_if_set_false>final_if", ["loop","logic_flag","branch"]),
    t("composition_algorithms", "CP02", "Read a positive whole NUMBER n and print the sum of its decimal digits.",
      '''IMPORT math.
NUMBER n.
INPUT(n).
NUMBER sum = 0.
LOOP (n > 0) {
    sum += n % 10.
    n = math.FLOOR(n / 10).
}
DISPLAYNL(sum).''',
      [("1\n","1.0"),("9\n","9.0"),("10\n","1.0"),("12345\n","15.0"),("9008\n","17.0")],
      "decimal_digit_sum", "while_modulo_accumulator", "import_math>input>sum_init>while>mod_add>floor_divide>display", ["while_loop","digit_processing"]),
    t("composition_algorithms", "CP03", "Read one SENTENCE and print PALINDROME if it equals its reverse ignoring case, otherwise DIFFERENT.",
      '''IMPORT strings.
SENTENCE text.
INPUT(text).
SENTENCE lowered = strings.LOWER(text).
SENTENCE reversed = strings.REVERSE(lowered).
IF (strings.EQUALS(lowered, reversed)) {
    DISPLAYNL("PALINDROME").
} ELSE {
    DISPLAYNL("DIFFERENT").
}''',
      [("Level\n","PALINDROME"),("abc\n","DIFFERENT"),("A\n","PALINDROME"),("RaceCar\n","PALINDROME"),("abca\n","DIFFERENT")],
      "casefold_palindrome", "string_transform_compare_branch", "import>input>lower>reverse>equals_if>labels", ["string_pipeline","branch"]),
    t("composition_algorithms", "CP04", "Read one SENTENCE and print the number of vowels a,e,i,o,u, ignoring case.",
      '''IMPORT strings.
SENTENCE text.
INPUT(text).
SENTENCE lowered = strings.LOWER(text).
NUMBER vowels = strings.COUNT(lowered, "a").
vowels += strings.COUNT(lowered, "e").
vowels += strings.COUNT(lowered, "i").
vowels += strings.COUNT(lowered, "o").
vowels += strings.COUNT(lowered, "u").
DISPLAYNL(vowels).''',
      [("hello\n","2.0"),("AEIOU\n","5.0"),("rhythm\n","0.0"),("GOCO language\n","6.0"),("a b c e\n","2.0")],
      "vowel_count_reductions", "multiple_string_reductions", "import>input>lower>five_count_accumulations>display", ["strings_count","compound_assignment"]),
    t("composition_algorithms", "CP05", "Read a positive whole NUMBER n. Sum its positive proper divisors. Print PERFECT if the sum equals n, ABUNDANT if greater, otherwise DEFICIENT.",
      '''NUMBER n.
INPUT(n).
NUMBER divisorSum = 0.
LOOP (NUMBER d = 1 TILL d < n, d++) {
    IF (n % d == 0) {
        divisorSum += d.
    }
}
IF (divisorSum == n) {
    DISPLAYNL("PERFECT").
} ELSEIF (divisorSum > n) {
    DISPLAYNL("ABUNDANT").
} ELSE {
    DISPLAYNL("DEFICIENT").
}''',
      [("1\n","DEFICIENT"),("6\n","PERFECT"),("12\n","ABUNDANT"),("28\n","PERFECT"),("8\n","DEFICIENT"),("18\n","ABUNDANT")],
      "divisor_sum_classification", "loop_reduction_then_three_way_branch", "input>divisor_sum>for>mod_if>accumulate>compare_chain3", ["loop","classification"]),
    t("composition_algorithms", "CP06", "Read a positive whole NUMBER n and print POWER OF TWO if repeated division by 2 reaches 1 with no odd intermediate value; otherwise OTHER.",
      '''IMPORT math.
NUMBER n.
INPUT(n).
LOGIC power = TRUE.
LOOP (n > 1) {
    IF (n % 2 != 0) {
        power = FALSE.
    }
    n = math.FLOOR(n / 2).
}
IF (power) {
    DISPLAYNL("POWER OF TWO").
} ELSE {
    DISPLAYNL("OTHER").
}''',
      [("1\n","POWER OF TWO"),("2\n","POWER OF TWO"),("8\n","POWER OF TWO"),("12\n","OTHER"),("31\n","OTHER"),("64\n","POWER OF TWO")],
      "power_of_two_reduction", "while_flag_destructive_division", "import_math>input>flag>while>odd_if_false>floor_half>final_branch", ["while_loop","logic_flag"]),
    t("composition_algorithms", "CP07", "Read base|exponent for a nonnegative whole exponent. Compute the power by repeated multiplication, then print EVEN if the result is even, otherwise ODD.",
      '''IMPORT strings.
SENTENCE line.
INPUT(line).
SENTENCE[] p = strings.SPLIT(line, "|").
NUMBER base = strings.TO_NUMBER(p[0]).
NUMBER exponent = strings.TO_NUMBER(p[1]).
NUMBER result = 1.
LOOP (NUMBER i = 0 TILL i < exponent, i++) {
    result *= base.
}
IF (result % 2 == 0) {
    DISPLAYNL("EVEN").
} ELSE {
    DISPLAYNL("ODD").
}''',
      [("2|0\n","ODD"),("2|3\n","EVEN"),("3|2\n","ODD"),("4|1\n","EVEN"),("-3|3\n","ODD"),("10|2\n","EVEN")],
      "power_parity", "loop_product_then_branch", "split2>power_init>for_multiply>parity_if", ["loop","postcondition_branch"]),
    t("composition_algorithms", "CP08", "Read a positive whole NUMBER n and print how many numbers from 1 through n are divisible by 2 or 5 but not both.",
      '''NUMBER n.
INPUT(n).
NUMBER count = 0.
LOOP (NUMBER i = 1 TILL i <= n, i++) {
    LOGIC byTwo = i % 2 == 0.
    LOGIC byFive = i % 5 == 0.
    IF ((byTwo OR byFive) AND NOT (byTwo AND byFive)) {
        count++.
    }
}
DISPLAYNL(count).''',
      [("1\n","0.0"),("2\n","1.0"),("5\n","3.0"),("10\n","5.0"),("20\n","10.0"),("25\n","13.0")],
      "exclusive_divisibility_count", "for_local_flags_xor_counter", "input>count>for>two_logic_locals>xor_expression_if>increment>display", ["loop","boolean_composition"]),
]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(tasks) != 64:
        raise ValueError(f"Expected 64 tasks, found {len(tasks)}")
    rows = []
    hidden: dict[str, list[dict[str, str]]] = {}
    references: dict[str, str] = {}
    for item in tasks:
        task_id = f"P1T-{item.code}"
        rows.append({
            "task_id": task_id,
            "split": "phase1t_confirmation",
            "level": "full_synthesis",
            "family": item.family,
            "difficulty": "confirmation",
            "prompt": item.prompt,
            "algorithmic_structure": item.algorithm,
            "control_flow": item.control_flow,
            "template_lineage": f"phase1t-{item.code.lower()}-{item.algorithm}-v1",
            "structural_signature": item.ast_signature,
            "constructs": item.constructs,
            "required_regex": item.required_regex,
        })
        hidden[task_id] = [
            {"case_id": f"case-{index + 1}", "stdin": stdin, "expected_stdout": expected}
            for index, (stdin, expected) in enumerate(item.cases)
        ]
        references[task_id] = item.source
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / "confirmation_tasks.json", rows)
    write_json(OUT / "confirmation_hidden_tests.json", hidden)
    write_json(OUT / "confirmation_references.json", references)
    print(f"wrote {len(rows)} tasks and {sum(map(len, hidden.values()))} hidden cases")
