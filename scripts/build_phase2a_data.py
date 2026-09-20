from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Callable


FAMILIES = (
    "expressions_variables",
    "conditionals",
    "loops",
    "functions",
    "arrays",
    "strings",
    "input_output",
    "composition_algorithms",
)


def number(value: float) -> str:
    if math.isclose(value, round(value), abs_tol=1e-12):
        return f"{float(round(value)):.1f}"
    return repr(float(value))


def case(index: int, stdin: str, expected: str | float) -> dict[str, str]:
    return {
        "case_id": f"case-{index}",
        "stdin": stdin if stdin.endswith("\n") else stdin + "\n",
        "expected_stdout": number(expected) if isinstance(expected, (int, float)) else expected,
    }


def split_numbers(names: list[str]) -> str:
    declarations = "\n".join(
        f"NUMBER {name} = strings.TO_NUMBER(parts[{index}])." for index, name in enumerate(names)
    )
    return (
        "IMPORT strings.\n"
        "SENTENCE line.\n"
        "INPUT(line).\n"
        "SENTENCE[] parts = strings.SPLIT(line, \"|\").\n"
        f"{declarations}\n"
    )


def split_sentences(names: list[str]) -> str:
    declarations = "\n".join(
        f"SENTENCE {name} = parts[{index}]." for index, name in enumerate(names)
    )
    return (
        "IMPORT strings.\n"
        "SENTENCE line.\n"
        "INPUT(line).\n"
        "SENTENCE[] parts = strings.SPLIT(line, \"|\").\n"
        f"{declarations}\n"
    )


def concat(*parts: str) -> str:
    """Build binary strings.CONCAT calls; the pinned library accepts arity two."""
    if len(parts) < 2:
        raise ValueError(parts)
    expression = f"strings.CONCAT({parts[0]}, {parts[1]})"
    for part in parts[2:]:
        expression = f"strings.CONCAT({expression}, {part})"
    return expression


def task_record(
    task_id: str,
    split: str,
    family: str,
    prompt: str,
    algorithm: str,
    flow: str,
    lineage: str,
    signature: str,
    required: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "split": split,
        "level": "full_synthesis",
        "family": family,
        "difficulty": "phase2a_pilot",
        "prompt": prompt,
        "algorithmic_structure": algorithm,
        "control_flow": flow,
        "template_lineage": lineage,
        "structural_signature": signature,
        "required_regex": required or [],
    }


def add(
    tasks: list[dict[str, Any]],
    refs: dict[str, str],
    tests: dict[str, list[dict[str, str]]],
    *,
    task_id: str,
    split: str,
    family: str,
    prompt: str,
    source: str,
    cases: list[dict[str, str]],
    algorithm: str,
    flow: str,
    lineage: str,
    signature: str,
    required: list[str] | None = None,
) -> None:
    tasks.append(task_record(task_id, split, family, prompt, algorithm, flow, lineage, signature, required))
    refs[task_id] = source.strip()
    tests[task_id] = cases


def build_training() -> tuple[list[dict[str, Any]], dict[str, str], dict[str, list[dict[str, str]]]]:
    tasks: list[dict[str, Any]] = []
    refs: dict[str, str] = {}
    tests: dict[str, list[dict[str, str]]] = {}

    # Expressions/variables: five structures, five independently parameterized examples each.
    for variant, (multiplier, offset) in enumerate([(2, 3), (3, -2), (4, 1), (-2, 5), (5, -4)], 1):
        tid = f"P2A-TR-EV-LIN-{variant:02d}"
        src = f"NUMBER x.\nINPUT(x).\nDISPLAYNL({multiplier} * x + ({offset}))."
        vals = [-3, 0, 4]
        add(tasks, refs, tests, task_id=tid, split="phase2a_train", family=FAMILIES[0],
            prompt=f"Read one NUMBER x and print {multiplier}*x + ({offset}).", source=src,
            cases=[case(i+1, str(x), multiplier*x+offset) for i, x in enumerate(vals)],
            algorithm=f"affine_map_m{multiplier}_b{offset}", flow="straight_line",
            lineage=f"p2a-tr-ev-affine-{variant}", signature="input>affine>display")
    for variant, constant in enumerate([2, 5, -3, 7, 11], 1):
        tid = f"P2A-TR-EV-QUAD-{variant:02d}"
        src = f"NUMBER x.\nINPUT(x).\nNUMBER square = x * x.\nDISPLAYNL(square + ({constant}))."
        vals = [-2, 0, 3]
        add(tasks, refs, tests, task_id=tid, split="phase2a_train", family=FAMILIES[0],
            prompt=f"Read x, square it, add {constant}, and print the result.", source=src,
            cases=[case(i+1, str(x), x*x+constant) for i, x in enumerate(vals)],
            algorithm=f"square_plus_{constant}", flow="straight_line_intermediate",
            lineage=f"p2a-tr-ev-square-{variant}", signature="input>square>offset>display")
    for variant, (a, b) in enumerate([(2, 1), (3, -1), (-1, 4), (5, 2), (1, -3)], 1):
        tid = f"P2A-TR-EV-WEIGHT-{variant:02d}"
        src = split_numbers(["left", "right"]) + f"DISPLAYNL({a} * left + ({b}) * right)."
        vals = [(1, 2), (-2, 5), (4, -1)]
        add(tasks, refs, tests, task_id=tid, split="phase2a_train", family=FAMILIES[0],
            prompt=f"Read left|right and print {a}*left + ({b})*right.", source=src,
            cases=[case(i+1, f"{x}|{y}", a*x+b*y) for i, (x, y) in enumerate(vals)],
            algorithm=f"weighted_pair_{a}_{b}", flow="split_convert_straight_line",
            lineage=f"p2a-tr-ev-weighted-{variant}", signature="split2>convert2>weighted_sum>display")
    for variant, percent in enumerate([10, 15, 25, 30, 40], 1):
        tid = f"P2A-TR-EV-DISC-{variant:02d}"
        factor = (100-percent)/100
        src = split_numbers(["price", "quantity"]) + f"NUMBER gross = price * quantity.\nDISPLAYNL(gross * {factor})."
        vals = [(10, 2), (5, 0), (8, 3)]
        add(tasks, refs, tests, task_id=tid, split="phase2a_train", family=FAMILIES[0],
            prompt=f"Read price|quantity and print the product after a {percent} percent discount.", source=src,
            cases=[case(i+1, f"{x}|{y}", x*y*factor) for i, (x, y) in enumerate(vals)],
            algorithm=f"discount_pipeline_{percent}", flow="split_convert_two_stage",
            lineage=f"p2a-tr-ev-discount-{variant}", signature="split2>product>scale>display")
    for variant, shift in enumerate([1, 2, 4, 6, 9], 1):
        tid = f"P2A-TR-EV-ABS-{variant:02d}"
        src = f"IMPORT math.\nNUMBER x.\nINPUT(x).\nDISPLAYNL(math.ABS(x - {shift}))."
        vals = [-2, shift, shift+5]
        add(tasks, refs, tests, task_id=tid, split="phase2a_train", family=FAMILIES[0],
            prompt=f"Read x and print the absolute distance from {shift}.", source=src,
            cases=[case(i+1, str(x), abs(x-shift)) for i, x in enumerate(vals)],
            algorithm=f"absolute_distance_{shift}", flow="library_straight_line",
            lineage=f"p2a-tr-ev-abs-{variant}", signature="import_math>input>subtract>abs>display")

    # Conditionals.
    for variant, pivot in enumerate([-3, 0, 2, 5, 10], 1):
        tid = f"P2A-TR-CD-SIGN-{variant:02d}"
        src = f"NUMBER x.\nINPUT(x).\nIF (x > {pivot}) {{\n DISPLAYNL(\"ABOVE\").\n}} ELSEIF (x == {pivot}) {{\n DISPLAYNL(\"EQUAL\").\n}} ELSE {{\n DISPLAYNL(\"BELOW\").\n}}"
        vals = [pivot-2, pivot, pivot+3]
        add(tasks, refs, tests, task_id=tid, split="phase2a_train", family=FAMILIES[1],
            prompt=f"Read x and print ABOVE, EQUAL, or BELOW compared with {pivot}.", source=src,
            cases=[case(i+1, str(x), "ABOVE" if x>pivot else "EQUAL" if x==pivot else "BELOW") for i,x in enumerate(vals)],
            algorithm=f"three_way_pivot_{pivot}", flow="if_elseif_else",
            lineage=f"p2a-tr-cd-pivot-{variant}", signature="input>three_way_branch>display")
    for variant, divisor in enumerate([2, 3, 4, 5, 7], 1):
        tid = f"P2A-TR-CD-DIV-{variant:02d}"
        src = f"NUMBER n.\nINPUT(n).\nIF (n % {divisor} == 0) {{\n DISPLAYNL(\"YES\").\n}} ELSE {{\n DISPLAYNL(\"NO\").\n}}"
        vals = [divisor, divisor+1, divisor*3]
        add(tasks, refs, tests, task_id=tid, split="phase2a_train", family=FAMILIES[1],
            prompt=f"Read n and print YES if divisible by {divisor}, otherwise NO.", source=src,
            cases=[case(i+1, str(x), "YES" if x%divisor==0 else "NO") for i,x in enumerate(vals)],
            algorithm=f"divisibility_test_{divisor}", flow="if_else_modulo",
            lineage=f"p2a-tr-cd-div-{variant}", signature="input>modulo_branch>display")
    for variant, threshold in enumerate([0, 10, 25, 50, 100], 1):
        tid = f"P2A-TR-CD-THR-{variant:02d}"
        src = f"NUMBER value.\nINPUT(value).\nIF (value >= {threshold}) {{\n DISPLAYNL(\"PASS\").\n}} ELSE {{\n DISPLAYNL(\"FAIL\").\n}}"
        vals = [threshold-1, threshold, threshold+8]
        add(tasks, refs, tests, task_id=tid, split="phase2a_train", family=FAMILIES[1],
            prompt=f"Read value and print PASS if it is at least {threshold}, else FAIL.", source=src,
            cases=[case(i+1, str(x), "PASS" if x>=threshold else "FAIL") for i,x in enumerate(vals)],
            algorithm=f"threshold_gate_{threshold}", flow="if_else_comparison",
            lineage=f"p2a-tr-cd-threshold-{variant}", signature="input>threshold_branch>display")
    for variant, label in enumerate(["LARGER", "WINNER", "HIGH", "MAX", "TOP"], 1):
        tid = f"P2A-TR-CD-MAX-{variant:02d}"
        src = split_numbers(["a", "b"]) + f"IF (a >= b) {{\n DISPLAYNL(\"{label}:A\").\n}} ELSE {{\n DISPLAYNL(\"{label}:B\").\n}}"
        vals = [(1,2),(5,5),(9,-1)]
        add(tasks, refs, tests, task_id=tid, split="phase2a_train", family=FAMILIES[1],
            prompt=f"Read a|b and print {label}:A when a>=b, otherwise {label}:B.", source=src,
            cases=[case(i+1,f"{a}|{b}",f"{label}:A" if a>=b else f"{label}:B") for i,(a,b) in enumerate(vals)],
            algorithm=f"pair_selector_{label.lower()}", flow="split_then_if_else",
            lineage=f"p2a-tr-cd-max-{variant}", signature="split2>compare>literal_display")
    for variant, (low, high) in enumerate([(0,10),(5,15),(-5,5),(20,30),(50,80)], 1):
        tid = f"P2A-TR-CD-RANGE-{variant:02d}"
        src = f"NUMBER x.\nINPUT(x).\nIF (x >= {low} AND x <= {high}) {{\n DISPLAYNL(\"IN\").\n}} ELSE {{\n DISPLAYNL(\"OUT\").\n}}"
        vals = [low-1,(low+high)/2,high+1]
        add(tasks, refs, tests, task_id=tid, split="phase2a_train", family=FAMILIES[1],
            prompt=f"Read x and print IN when {low} <= x <= {high}, otherwise OUT.", source=src,
            cases=[case(i+1,str(x),"IN" if low<=x<=high else "OUT") for i,x in enumerate(vals)],
            algorithm=f"closed_interval_{low}_{high}", flow="compound_condition_if_else",
            lineage=f"p2a-tr-cd-range-{variant}", signature="input>and_range_branch>display")

    # Loops.
    loop_specs = [
        ("sum", "NUMBER total = 0.", "total += i.", lambda n: n*(n+1)/2, "sum_1_to_n"),
        ("factorial", "NUMBER total = 1.", "total *= i.", lambda n: math.prod(range(1,n+1)), "factorial_product"),
        ("squares", "NUMBER total = 0.", "total += i * i.", lambda n: sum(i*i for i in range(1,n+1)), "square_sum"),
        ("odds", "NUMBER total = 0.", "total += 2 * i - 1.", lambda n: n*n, "first_n_odd_sum"),
        ("triangular", "NUMBER total = 0.", "total += i + 2.", lambda n: sum(i+2 for i in range(1,n+1)), "shifted_progression"),
    ]
    for archetype, init, body, solver, algorithm in loop_specs:
        for variant, extra in enumerate([0,1,2,3,4],1):
            tid=f"P2A-TR-LP-{archetype.upper()}-{variant:02d}"
            upper=f"n + {extra}" if extra else "n"
            src=f"NUMBER n.\nINPUT(n).\n{init}\nLOOP (NUMBER i = 1 TILL i <= {upper}, i++) {{\n {body}\n}}\nDISPLAYNL(total)."
            vals=[0,2,5]
            add(tasks,refs,tests,task_id=tid,split="phase2a_train",family=FAMILIES[2],
                prompt=f"Read nonnegative n and use a loop to compute {algorithm.replace('_',' ')} through n+{extra}.",source=src,
                cases=[case(i+1,str(n),solver(n+extra)) for i,n in enumerate(vals)],algorithm=f"{algorithm}_offset_{extra}",
                flow="counted_loop_accumulator",lineage=f"p2a-tr-lp-{archetype}-{variant}",signature=f"input>loop>{archetype}_accumulator>display",required=[r"LOOP\s*\("])

    # Functions.
    fn_specs: list[tuple[str, str, Callable[[float, int], float]]] = [
        ("scale", "RETURN x * K.", lambda x,k:x*k),
        ("shift", "RETURN x + K.", lambda x,k:x+k),
        ("squareplus", "RETURN x * x + K.", lambda x,k:x*x+k),
        ("distance", "IMPORT math.", lambda x,k:abs(x-k)),
        ("halveplus", "RETURN x / 2 + K.", lambda x,k:x/2+k),
    ]
    for name, template, solver in fn_specs:
        for variant,k in enumerate([1,2,3,4,5],1):
            tid=f"P2A-TR-FN-{name.upper()}-{variant:02d}"
            if name=="distance":
                src=f"IMPORT math.\nFUNCTION transform(NUMBER x) {{\n RETURN math.ABS(x - {k}).\n}} RETURNS NUMBER.\nNUMBER value.\nINPUT(value).\nDISPLAYNL(transform(value))."
            else:
                body=template.replace("K",str(k))
                src=f"FUNCTION transform(NUMBER x) {{\n {body}\n}} RETURNS NUMBER.\nNUMBER value.\nINPUT(value).\nDISPLAYNL(transform(value))."
            vals=[-2,0,6]
            add(tasks,refs,tests,task_id=tid,split="phase2a_train",family=FAMILIES[3],
                prompt=f"Define a returning function for the {name} transformation with constant {k}; read one number and print the function result.",source=src,
                cases=[case(i+1,str(x),solver(x,k)) for i,x in enumerate(vals)],algorithm=f"function_{name}_{k}",
                flow="function_then_call",lineage=f"p2a-tr-fn-{name}-{variant}",signature=f"function>{name}>input>call>display",required=[r"FUNCTION\s+"])

    # Arrays: fixed-width delimited input with different reductions.
    array_archetypes = ["sum3", "product3", "max3", "min3", "positive4"]
    for archetype in array_archetypes:
        for variant, bias in enumerate([0,1,2,3,4],1):
            tid=f"P2A-TR-AR-{archetype.upper()}-{variant:02d}"
            width=4 if archetype=="positive4" else 3
            names=[f"v{i}" for i in range(width)]
            prefix=split_numbers(names)
            arr=f"NUMBER[] values = [{', '.join(names)}].\n"
            if archetype=="sum3":
                body=f"DISPLAYNL(arrays.SUM(values) + {bias})."; solver=lambda xs,b=bias:sum(xs)+b
            elif archetype=="product3":
                body=f"NUMBER result = values[0] * values[1] * values[2].\nDISPLAYNL(result + {bias})."; solver=lambda xs,b=bias:math.prod(xs)+b
            elif archetype=="max3":
                body=f"IMPORT math.\nNUMBER result = math.MAX(values[0], math.MAX(values[1], values[2])).\nDISPLAYNL(result + {bias})."; solver=lambda xs,b=bias:max(xs)+b
            elif archetype=="min3":
                body=f"IMPORT math.\nNUMBER result = math.MIN(values[0], math.MIN(values[1], values[2])).\nDISPLAYNL(result - {bias})."; solver=lambda xs,b=bias:min(xs)-b
            else:
                body="NUMBER count = 0.\nLOOP (NUMBER i = 0 TILL i < 4, i++) {\n IF (values[i] > 0) {\n  count += 1.\n }\n}\n"+f"DISPLAYNL(count + {bias})."; solver=lambda xs,b=bias:sum(x>0 for x in xs)+b
            src=prefix+"IMPORT arrays.\n"+arr+body
            samples=[[1,2,3],[-2,0,5],[4,-1,2]] if width==3 else [[1,-2,3,0],[-1,-2,-3,-4],[2,4,6,8]]
            add(tasks,refs,tests,task_id=tid,split="phase2a_train",family=FAMILIES[4],
                prompt=f"Read {width} pipe-delimited numbers, place them in an array, compute {archetype} with adjustment {bias}, and print the result.",source=src,
                cases=[case(i+1,"|".join(map(str,xs)),solver(xs)) for i,xs in enumerate(samples)],algorithm=f"array_{archetype}_adjust_{bias}",
                flow="split_array_reduction",lineage=f"p2a-tr-ar-{archetype}-{variant}",signature=f"split{width}>array>{archetype}>display",required=[r"NUMBER\[\]"])

    # Strings.
    string_specs = [
        ("upper", lambda k:f"DISPLAYNL(strings.UPPER(text)).", lambda s,k:s.upper()),
        ("lower", lambda k:f"DISPLAYNL(strings.LOWER(text)).", lambda s,k:s.lower()),
        ("reverse", lambda k:f"DISPLAYNL(strings.REVERSE(text)).", lambda s,k:s[::-1]),
        ("lengthplus", lambda k:f"DISPLAYNL(strings.LENGTH(text) + {k}).", lambda s,k:len(s)+k),
        ("repeat", lambda k:f"DISPLAYNL(strings.REPEAT(text, {k})).", lambda s,k:s*k),
    ]
    for name,body_fn,solver in string_specs:
        for variant,k in enumerate([1,2,3,4,5],1):
            repeat_k=(k%3)+1 if name=="repeat" else k
            tid=f"P2A-TR-ST-{name.upper()}-{variant:02d}"
            src=f"IMPORT strings.\nSENTENCE text.\nINPUT(text).\n{body_fn(repeat_k)}"
            vals=["GoCo","alpha beta","XyZ"]
            add(tasks,refs,tests,task_id=tid,split="phase2a_train",family=FAMILIES[5],
                prompt=f"Read one sentence and apply strings.{name} with parameter {repeat_k}; print only the result.",source=src,
                cases=[case(i+1,s,solver(s,repeat_k)) for i,s in enumerate(vals)],algorithm=f"string_{name}_{repeat_k}_variant_{variant}",
                flow="string_library_straight_line",lineage=f"p2a-tr-st-{name}-{variant}",signature=f"import>input>strings_{name}>display")

    # Input/output formatting.
    io_specs=[
        ("swap", lambda a,b,k:f"{b}:{a}:{k}"),
        ("bracket", lambda a,b,k:f"[{a}]<{b}>#{k}"),
        ("arrow", lambda a,b,k:f"{a}->{b}->{k}"),
        ("slash", lambda a,b,k:f"{k}/{a}/{b}"),
        ("twoline", lambda a,b,k:f"{a}-{k}\n{b}"),
    ]
    for name,solver in io_specs:
        for variant,k in enumerate([1,2,3,4,5],1):
            tid=f"P2A-TR-IO-{name.upper()}-{variant:02d}"
            prefix=split_sentences(["first","second"])
            if name=="swap": body=f'DISPLAYNL({concat("second", "\":\"", "first", f"\":{k}\"")}).'
            elif name=="bracket": body=f'DISPLAYNL({concat("\"[\"", "first", "\"]<\"", "second", f"\">#{k}\"")}).'
            elif name=="arrow": body=f'DISPLAYNL({concat("first", "\"->\"", "second", f"\"->{k}\"")}).'
            elif name=="slash": body=f'DISPLAYNL({concat(f"\"{k}/\"", "first", "\"/\"", "second")}).'
            else: body=f'DISPLAYNL({concat("first", f"\"-{k}\"")}).\nDISPLAYNL(second).'
            src=prefix+body
            vals=[("A","B"),("red","blue"),("hello world","ok")]
            add(tasks,refs,tests,task_id=tid,split="phase2a_train",family=FAMILIES[6],
                prompt=f"Read first|second and emit the {name} format with fixed marker {k} exactly.",source=src,
                cases=[case(i+1,f"{a}|{b}",solver(a,b,k)) for i,(a,b) in enumerate(vals)],algorithm=f"format_{name}_{k}",
                flow="split_fields_format",lineage=f"p2a-tr-io-{name}-{variant}",signature=f"split2>format_{name}>display")

    # Composition/algorithms.
    for variant, divisor in enumerate([2,3,4,5,6],1):
        tid=f"P2A-TR-CP-FILTER-{variant:02d}"
        src=f"NUMBER n.\nINPUT(n).\nNUMBER total = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) {{\n IF (i % {divisor} == 0) {{\n  total += i.\n }}\n}}\nDISPLAYNL(total)."
        vals=[0,divisor,divisor*4]
        add(tasks,refs,tests,task_id=tid,split="phase2a_train",family=FAMILIES[7],prompt=f"Read n and sum integers from 1 through n divisible by {divisor}.",source=src,
            cases=[case(i+1,str(n),sum(x for x in range(1,n+1) if x%divisor==0)) for i,n in enumerate(vals)],algorithm=f"filtered_sum_divisor_{divisor}",flow="loop_with_filter",
            lineage=f"p2a-tr-cp-filter-{variant}",signature="input>loop>modulo_if>accumulate>display",required=[r"LOOP\s*\(",r"IF\s*\("])
    for variant, k in enumerate([2,3,4,5,6],1):
        tid=f"P2A-TR-CP-POWER-{variant:02d}"
        src=split_numbers(["base","exponent"])+"NUMBER result = 1.\nLOOP (NUMBER i = 0 TILL i < exponent, i++) {\n result *= base.\n}\n"+f"IF (result % {k} == 0) {{\n DISPLAYNL(\"MULTIPLE\").\n}} ELSE {{\n DISPLAYNL(\"OTHER\").\n}}"
        vals=[(2,3),(3,2),(5,0)]
        add(tasks,refs,tests,task_id=tid,split="phase2a_train",family=FAMILIES[7],prompt=f"Read base|exponent, compute the power by a loop, and classify divisibility by {k}.",source=src,
            cases=[case(i+1,f"{a}|{b}","MULTIPLE" if (a**b)%k==0 else "OTHER") for i,(a,b) in enumerate(vals)],algorithm=f"iterative_power_then_mod_{k}",flow="split_loop_then_branch",
            lineage=f"p2a-tr-cp-power-{variant}",signature="split2>power_loop>modulo_branch>display")
    for variant, limit in enumerate([3,4,5,6,7],1):
        tid=f"P2A-TR-CP-DIVCOUNT-{variant:02d}"
        src=f"NUMBER n.\nINPUT(n).\nNUMBER count = 0.\nLOOP (NUMBER i = 1 TILL i <= {limit}, i++) {{\n IF (n % i == 0) {{\n  count += 1.\n }}\n}}\nDISPLAYNL(count)."
        vals=[1,12,25]
        add(tasks,refs,tests,task_id=tid,split="phase2a_train",family=FAMILIES[7],prompt=f"Read n and count how many integers from 1 through {limit} divide it.",source=src,
            cases=[case(i+1,str(n),sum(n%x==0 for x in range(1,limit+1))) for i,n in enumerate(vals)],algorithm=f"bounded_divisor_count_{limit}",flow="fixed_loop_conditional_count",
            lineage=f"p2a-tr-cp-divcount-{variant}",signature="input>bounded_loop>divisor_if>count>display")
    for variant, threshold in enumerate([5,10,15,20,25],1):
        tid=f"P2A-TR-CP-SUMCLASS-{variant:02d}"
        src=split_numbers(["a","b","c"])+f"NUMBER total = a + b + c.\nIF (total >= {threshold}) {{\n DISPLAYNL(\"HIGH\").\n}} ELSE {{\n DISPLAYNL(\"LOW\").\n}}"
        vals=[(1,2,3),(10,10,10),(-2,1,0)]
        add(tasks,refs,tests,task_id=tid,split="phase2a_train",family=FAMILIES[7],prompt=f"Read a|b|c, sum them, and print HIGH if the sum is at least {threshold}, otherwise LOW.",source=src,
            cases=[case(i+1,f"{a}|{b}|{c}","HIGH" if a+b+c>=threshold else "LOW") for i,(a,b,c) in enumerate(vals)],algorithm=f"aggregate_then_threshold_{threshold}",flow="split_aggregate_branch",
            lineage=f"p2a-tr-cp-sumclass-{variant}",signature="split3>aggregate>threshold_branch>display")
    for variant, token in enumerate(["a","e","i","o","u"],1):
        tid=f"P2A-TR-CP-TEXTCOUNT-{variant:02d}"
        src=f"IMPORT strings.\nSENTENCE text.\nINPUT(text).\nNUMBER count = strings.COUNT(strings.LOWER(text), \"{token}\").\nIF (count > 1) {{\n DISPLAYNL(\"MANY\").\n}} ELSE {{\n DISPLAYNL(\"FEW\").\n}}"
        vals=["alphabet","sky",token*3]
        add(tasks,refs,tests,task_id=tid,split="phase2a_train",family=FAMILIES[7],prompt=f"Read text, count letter {token} ignoring case, and print MANY if count>1 else FEW.",source=src,
            cases=[case(i+1,s,"MANY" if s.lower().count(token)>1 else "FEW") for i,s in enumerate(vals)],algorithm=f"normalized_text_count_branch_{token}",flow="library_transform_then_branch",
            lineage=f"p2a-tr-cp-textcount-{variant}",signature="input>lower>count>branch>display")

    return tasks, refs, tests


def build_eval() -> tuple[list[dict[str, Any]], dict[str, str], dict[str, list[dict[str, str]]]]:
    tasks: list[dict[str, Any]]=[]; refs: dict[str,str]={}; tests: dict[str,list[dict[str,str]]]={}
    def emit(code:str,family:str,prompt:str,source:str,values:list[tuple[str,str|float]],algorithm:str,flow:str,signature:str,required:list[str]|None=None)->None:
        index=sum(t["family"]==family for t in tasks)+1
        tid=f"P2A-DEV-{code}{index:02d}"
        add(tasks,refs,tests,task_id=tid,split="phase2a_development",family=family,prompt=prompt,source=source,
            cases=[case(i+1,stdin,expected) for i,(stdin,expected) in enumerate(values)],algorithm=algorithm,flow=flow,
            lineage=f"p2a-dev-{code.lower()}-{index:02d}-{algorithm}",signature=signature,required=required)

    ev=FAMILIES[0]
    emit("EV",ev,"Read x and print x*x*x - 2.","NUMBER x.\nINPUT(x).\nDISPLAYNL(x * x * x - 2).",[("0",-2),("1",-1),("-2",-10),("3",25),("4",62)],"cubic_minus_constant","straight_line","input>cube>subtract>display")
    emit("EV",ev,"Read a|b and print their arithmetic midpoint.",split_numbers(["a","b"])+"DISPLAYNL((a + b) / 2).",[("0|2",1),("-2|4",1),("5|5",5),("1|2",1.5),("-7|-3",-5)],"pair_midpoint","split_convert","split2>sum>divide>display")
    emit("EV",ev,"Read a|b and print a*b + a + b.",split_numbers(["a","b"])+"DISPLAYNL(a * b + a + b).",[("1|2",5),("0|5",5),("2.5|3",13),("-1|4",-1),("10|10",120)],"pair_product_plus_sum","split_convert","split2>product_plus_operands>display")
    emit("EV",ev,"Read mass|speed and print mass*speed*speed/2.",split_numbers(["mass","speed"])+"DISPLAYNL(mass * speed * speed / 2).",[("2|3",9),("1|0",0),("4|2",8),("0.5|4",4),("3|-2",6)],"kinetic_proxy","split_convert","split2>square_product>divide>display")
    emit("EV",ev,"Read minutes|seconds and print total seconds.",split_numbers(["minutes","seconds"])+"DISPLAYNL(minutes * 60 + seconds).",[("0|0",0),("1|30",90),("2|5",125),("10|59",659),("-1|30",-30)],"time_to_seconds","split_convert","split2>unit_scale>add>display")
    emit("EV",ev,"Read x and print its square root using math.SQRT.","IMPORT math.\nNUMBER x.\nINPUT(x).\nDISPLAYNL(math.SQRT(x)).",[("0",0),("1",1),("4",2),("9",3),("2",math.sqrt(2))],"square_root","library_straight_line","import_math>input>sqrt>display")
    emit("EV",ev,"Read x and clamp it to the interval 2 through 8 using math.CLAMP.","IMPORT math.\nNUMBER x.\nINPUT(x).\nDISPLAYNL(math.CLAMP(x, 2, 8)).",[("-1",2),("2",2),("5",5),("8",8),("12",8)],"numeric_clamp","library_straight_line","import_math>input>clamp>display")
    emit("EV",ev,"Read a|b and print (a*a + b*b) % 7.",split_numbers(["a","b"])+"DISPLAYNL((a * a + b * b) % 7).",[("1|2",5),("0|0",0),("3|4",4),("7|1",1),("-2|5",1)],"squared_pair_remainder","split_convert","split2>squares>sum>modulo>display")

    cd=FAMILIES[1]
    emit("CD",cd,"Read a|b|c and print the middle value when the three values are ordered.",split_numbers(["a","b","c"])+"IF ((a >= b AND a <= c) OR (a <= b AND a >= c)) { DISPLAYNL(a). } ELSEIF ((b >= a AND b <= c) OR (b <= a AND b >= c)) { DISPLAYNL(b). } ELSE { DISPLAYNL(c). }",[("1|2|3",2),("3|1|2",2),("2|3|1",2),("5|5|9",5),("-1|-3|-2",-2)],"median_of_three","compound_if_chain","split3>median_conditions>numeric_display")
    emit("CD",cd,"Read a|b and print ZERO if either is zero, SAME if they have the same sign, otherwise MIXED.",split_numbers(["a","b"])+"IF (a == 0 OR b == 0) { DISPLAYNL(\"ZERO\"). } ELSEIF ((a > 0 AND b > 0) OR (a < 0 AND b < 0)) { DISPLAYNL(\"SAME\"). } ELSE { DISPLAYNL(\"MIXED\"). }",[("0|2","ZERO"),("-1|0","ZERO"),("2|3","SAME"),("-2|-5","SAME"),("-2|4","MIXED")],"pair_sign_relation","compound_if_chain","split2>zero_guard>sign_relation>display")
    emit("CD",cd,"Read n and print POSITIVE EVEN, POSITIVE ODD, or NONPOSITIVE.","NUMBER n.\nINPUT(n).\nIF (n > 0) {\n IF (n % 2 == 0) {\n  DISPLAYNL(\"POSITIVE EVEN\").\n } ELSE {\n  DISPLAYNL(\"POSITIVE ODD\").\n }\n} ELSE {\n DISPLAYNL(\"NONPOSITIVE\").\n}",[("-2","NONPOSITIVE"),("0","NONPOSITIVE"),("1","POSITIVE ODD"),("2","POSITIVE EVEN"),("9","POSITIVE ODD")],"nested_sign_parity","nested_if","input>sign_if>parity_if>display")
    emit("CD",cd,"Read n and print BOTH if divisible by 3 and 5, THREE if only 3, FIVE if only 5, else NEITHER.","NUMBER n.\nINPUT(n).\nIF (n % 3 == 0 AND n % 5 == 0) {\n DISPLAYNL(\"BOTH\").\n} ELSEIF (n % 3 == 0) {\n DISPLAYNL(\"THREE\").\n} ELSEIF (n % 5 == 0) {\n DISPLAYNL(\"FIVE\").\n} ELSE {\n DISPLAYNL(\"NEITHER\").\n}",[("15","BOTH"),("9","THREE"),("10","FIVE"),("7","NEITHER"),("0","BOTH")],"fizzbuzz_classification","compound_if_chain","input>compound_modulo_chain>display")
    emit("CD",cd,"Read a|b and print SUM when a+b is greater than a*b, PRODUCT when a*b is greater, otherwise TIE.",split_numbers(["a","b"])+"NUMBER sum = a + b.\nNUMBER product = a * b.\nIF (sum > product) { DISPLAYNL(\"SUM\"). } ELSEIF (product > sum) { DISPLAYNL(\"PRODUCT\"). } ELSE { DISPLAYNL(\"TIE\"). }",[("1|2","SUM"),("2|2","TIE"),("3|3","PRODUCT"),("0|5","SUM"),("-2|-3","PRODUCT")],"sum_product_comparison","derive_then_chain","split2>derive_sum_product>compare>display")
    emit("CD",cd,"Read n and print EVEN-SMALL, EVEN-LARGE, ODD-SMALL, or ODD-LARGE using parity and the boundary 20.","NUMBER n.\nINPUT(n).\nIF (n % 2 == 0) { IF (n < 20) { DISPLAYNL(\"EVEN-SMALL\"). } ELSE { DISPLAYNL(\"EVEN-LARGE\"). } } ELSE { IF (n < 20) { DISPLAYNL(\"ODD-SMALL\"). } ELSE { DISPLAYNL(\"ODD-LARGE\"). } }",[("2","EVEN-SMALL"),("20","EVEN-LARGE"),("7","ODD-SMALL"),("21","ODD-LARGE"),("-3","ODD-SMALL")],"nested_parity_magnitude","nested_if","input>parity_branch>magnitude_branch>display")
    emit("CD",cd,"Read a|b and print A when abs(a)>abs(b), B when abs(b)>abs(a), else TIE.",split_numbers(["a","b"])+"IMPORT math.\nNUMBER aa = math.ABS(a).\nNUMBER bb = math.ABS(b).\nIF (aa > bb) {\n DISPLAYNL(\"A\").\n} ELSEIF (bb > aa) {\n DISPLAYNL(\"B\").\n} ELSE {\n DISPLAYNL(\"TIE\").\n}",[("-5|3","A"),("2|-7","B"),("-4|4","TIE"),("0|0","TIE"),("1|2","B")],"absolute_magnitude_compare","library_then_chain","split2>abs2>three_way_branch>display")
    emit("CD",cd,"Read n and print SIX when divisible by 6, TWO when divisible only by 2, THREE when divisible only by 3, otherwise OTHER.","NUMBER n.\nINPUT(n).\nIF (n % 6 == 0) { DISPLAYNL(\"SIX\"). } ELSEIF (n % 2 == 0) { DISPLAYNL(\"TWO\"). } ELSEIF (n % 3 == 0) { DISPLAYNL(\"THREE\"). } ELSE { DISPLAYNL(\"OTHER\"). }",[("12","SIX"),("8","TWO"),("9","THREE"),("7","OTHER"),("0","SIX")],"divisibility_precedence","four_way_modulo_chain","input>ordered_divisibility>display")

    lp=FAMILIES[2]
    loop_eval=[
        ("sum_fourth_powers","NUMBER total = 0.","total += i * i * i * i.",lambda n:sum(i**4 for i in range(1,n+1))),
        ("count_odd","NUMBER total = 0.","IF (i % 2 != 0) { total += 1. }",lambda n:sum(i%2 for i in range(1,n+1))),
        ("sum_four_or_seven","NUMBER total = 0.","IF (i % 4 == 0 OR i % 7 == 0) { total += i. }",lambda n:sum(i for i in range(1,n+1) if i%4==0 or i%7==0)),
        ("product_evens","NUMBER total = 1.","IF (i % 2 == 0) { total *= i. }",lambda n:math.prod([i for i in range(1,n+1) if i%2==0]) if n>=2 else 1),
        ("weighted_index_sum","NUMBER total = 0.","total += i * (i + 1).",lambda n:sum(i*(i+1) for i in range(1,n+1))),
        ("count_nonmultiples_five","NUMBER total = 0.","IF (i % 5 != 0) { total += 1. }",lambda n:sum(i%5!=0 for i in range(1,n+1))),
        ("powers_two_sum","NUMBER total = 0.\nNUMBER power = 1.","total += power.\n power *= 2.",lambda n:sum(2**i for i in range(n))),
        ("symmetric_pair_sum","NUMBER total = 0.","total += i * (n - i).",lambda n:sum(i*(n-i) for i in range(1,n+1))),
    ]
    for name,init,body,solver in loop_eval:
        source=f"NUMBER n.\nINPUT(n).\n{init}\nLOOP (NUMBER i = 1 TILL i <= n, i++) {{\n {body}\n}}\nDISPLAYNL(total)." if name!="powers_two_sum" else "IMPORT math.\nNUMBER n.\nINPUT(n).\nNUMBER total = 0.\nLOOP (NUMBER i = 0 TILL i < n, i++) {\n total += math.POW(2, i).\n}\nDISPLAYNL(total)."
        emit("LP",lp,f"Read nonnegative n and compute {name.replace('_',' ')} with a loop.",source,[(str(n),solver(n)) for n in [0,1,2,5,7]],name,"counted_loop","input>loop>"+name+">display",[r"LOOP\s*\("])

    fn=FAMILIES[3]
    fn_eval=[
        ("quadratic_offset_function","RETURN x * x - x + 3.",lambda xs:xs[0]**2-xs[0]+3,1),
        ("average_three","RETURN (a + b + c) / 3.",lambda xs:sum(xs)/3,3),
        ("triangle_area","RETURN base * height / 2.",lambda xs:xs[0]*xs[1]/2,2),
        ("percentage_of","RETURN amount * rate / 100.",lambda xs:xs[0]*xs[1]/100,2),
        ("clamp_zero_ten","IMPORT math.",lambda xs:max(0,min(10,xs[0])),1),
        ("minimum_three","IMPORT math.",lambda xs:min(xs),3),
        ("positive_square_else_negate","branch",lambda xs:xs[0]**2 if xs[0]>=0 else -xs[0],1),
        ("weighted_pair_function","RETURN 2 * a - 3 * b.",lambda xs:2*xs[0]-3*xs[1],2),
    ]
    for name,body,solver,arity in fn_eval:
        if name=="triangle_area": names=["base","height"]
        elif name=="percentage_of": names=["amount","rate"]
        else: names=["x"] if arity==1 else ["a","b"] if arity==2 else ["a","b","c"]
        prefix=split_numbers(names) if arity>1 else f"NUMBER {names[0]}.\nINPUT({names[0]}).\n"
        params=", ".join(f"NUMBER {x}" for x in names)
        if name=="clamp_zero_ten": fbody="RETURN math.CLAMP(x, 0, 10)."
        elif name=="minimum_three": fbody="RETURN math.MIN(a, math.MIN(b, c))."
        elif body=="branch": fbody="IF (x >= 0) { RETURN x * x. } ELSE { RETURN -x. }"
        else: fbody=body
        imports="IMPORT math.\n" if name in {"clamp_zero_ten","minimum_three"} else ""
        source=imports+f"FUNCTION compute({params}) {{\n {fbody}\n}} RETURNS NUMBER.\n"+prefix+f"DISPLAYNL(compute({', '.join(names)}))."
        sample_values=[[0],[2],[-3],[5],[1.5]] if arity==1 else [[1,2],[0,0],[-2,4],[5,-1],[3,3]] if arity==2 else [[1,2,3],[0,0,0],[-2,4,1],[5,-1,2],[3,3,3]]
        emit("FN",fn,f"Define a function implementing {name.replace('_',' ')}, read {'|'.join(names)}, and print its result.",source,[("|".join(map(str,xs)),solver(xs)) for xs in sample_values],name,"function_then_call","function>"+name+">input>call>display",[r"FUNCTION\s+"])

    ar=FAMILIES[4]
    array_eval=[
        ("range_four",4,lambda xs:max(xs)-min(xs),"IMPORT math.\nNUMBER result = math.MAX(values[0], math.MAX(values[1], math.MAX(values[2], values[3]))) - math.MIN(values[0], math.MIN(values[1], math.MIN(values[2], values[3]))).\nDISPLAYNL(result)."),
        ("average_four",4,lambda xs:sum(xs)/4,"IMPORT arrays.\nDISPLAYNL(arrays.AVG(values))."),
        ("count_even_five",5,lambda xs:sum(x%2==0 for x in xs),"NUMBER count = 0.\nLOOP (NUMBER i = 0 TILL i < 5, i++) { IF (values[i] % 2 == 0) { count += 1. } }\nDISPLAYNL(count)."),
        ("weighted_dot_three",3,lambda xs:xs[0]+2*xs[1]+3*xs[2],"DISPLAYNL(values[0] + 2 * values[1] + 3 * values[2])."),
        ("endpoint_sum_five",5,lambda xs:xs[0]+xs[-1],"DISPLAYNL(values[0] + values[4])."),
        ("middle_product_four",4,lambda xs:xs[1]*xs[2],"DISPLAYNL(values[1] * values[2])."),
        ("negative_count_five",5,lambda xs:sum(x<0 for x in xs),"NUMBER count = 0.\nLOOP (NUMBER i = 0 TILL i < 5, i++) { IF (values[i] < 0) { count += 1. } }\nDISPLAYNL(count)."),
        ("alternating_sum_four",4,lambda xs:xs[0]-xs[1]+xs[2]-xs[3],"DISPLAYNL(values[0] - values[1] + values[2] - values[3])."),
    ]
    for name,width,solver,body in array_eval:
        names=[f"v{i}" for i in range(width)]; source=split_numbers(names)+f"NUMBER[] values = [{', '.join(names)}].\n"+body
        samples=[list(range(1,width+1)),[0]*width,[-i for i in range(width)],[(i%3)-1 for i in range(width)],[5,2,9,1,4][:width]]
        emit("AR",ar,f"Read {width} pipe-delimited numbers into an array and compute {name.replace('_',' ')}.",source,[("|".join(map(str,xs)),solver(xs)) for xs in samples],name,"split_array_operation","split>array>"+name+">display",[r"NUMBER\[\]"])

    st=FAMILIES[5]
    string_eval=[
        ("dual_replace","DISPLAYNL(strings.REPLACE(strings.REPLACE(text, \"a\", \"@\"), \"e\", \"3\")).",lambda s:s.replace("a","@").replace("e","3")),
        ("trim_spaces","DISPLAYNL(strings.TRIM(text, \"\")).",lambda s:s.strip()),
        ("contains_go","IF (strings.CONTAINS(strings.LOWER(text), \"go\")) { DISPLAYNL(\"YES\"). } ELSE { DISPLAYNL(\"NO\"). }",lambda s:"YES" if "go" in s.lower() else "NO"),
        ("count_a","DISPLAYNL(strings.COUNT(strings.LOWER(text), \"a\")).",lambda s:s.lower().count("a")),
        ("starts_pre","IF (strings.STARTSWITH(strings.LOWER(text), \"pre\")) { DISPLAYNL(\"YES\"). } ELSE { DISPLAYNL(\"NO\"). }",lambda s:"YES" if s.lower().startswith("pre") else "NO"),
        ("ends_ing","IF (strings.ENDSWITH(strings.LOWER(text), \"ing\")) { DISPLAYNL(\"YES\"). } ELSE { DISPLAYNL(\"NO\"). }",lambda s:"YES" if s.lower().endswith("ing") else "NO"),
        ("first_three","DISPLAYNL(strings.SUB(text, 0, 2)).",lambda s:s[:3]),
        ("double_lower","DISPLAYNL(strings.REPEAT(strings.LOWER(text), 2)).",lambda s:s.lower()*2),
    ]
    strvals=["GoCo", "prefix", "running", "A banana", " xyz "]
    for name,body,solver in string_eval:
        source="IMPORT strings.\nSENTENCE text.\nINPUT(text).\n"+body
        emit("ST",st,f"Read one sentence and perform {name.replace('_',' ')} exactly.",source,[(s,solver(s)) for s in strvals],name,"string_transform","import>input>"+name+">display")

    io=FAMILIES[6]
    io_eval=[
        ("numeric_double_label",lambda a,b:f"{a}={float(b)*2:.1f}",f'NUMBER value = strings.TO_NUMBER(second).\nDISPLAYNL({concat("first", "\"=\"", "strings.TO_SENTENCE(value * 2)")}).'),
        ("field_lengths",lambda a,b:f"{float(len(a)):.1f}\n{float(len(b)):.1f}",'DISPLAYNL(strings.LENGTH(first)).\nDISPLAYNL(strings.LENGTH(second)).'),
        ("upper_status_trim_title",lambda a,b:f"{b.upper()}:{a.strip()}",f'DISPLAYNL({concat("strings.UPPER(second)", "\":\"", "strings.TRIM(first, \"\")")}).'),
        ("reverse_and_length",lambda a,b:f"{a[::-1]}:{float(len(b)):.1f}",f'DISPLAYNL({concat("strings.REVERSE(first)", "\":\"", "strings.TO_SENTENCE(strings.LENGTH(second))")}).'),
        ("length_suffix",lambda a,b:f"{a}:{b}:{float(len(a)+len(b)):.1f}",f'NUMBER total = strings.LENGTH(first) + strings.LENGTH(second).\nDISPLAYNL({concat("first", "\":\"", "second", "\":\"", "strings.TO_SENTENCE(total)")}).'),
        ("upper_labels",lambda a,b:f"A={a.upper()}\nB={b.upper()}",'DISPLAYNL(strings.CONCAT("A=", strings.UPPER(first))).\nDISPLAYNL(strings.CONCAT("B=", strings.UPPER(second))).'),
        ("repeat_by_count",lambda a,b:a*int(b), 'NUMBER count = strings.TO_NUMBER(second).\nDISPLAYNL(strings.REPEAT(first, count)).'),
        ("increment_with_unit",lambda a,b:f"{float(a)+1:.1f} {b}",f'NUMBER value = strings.TO_NUMBER(first).\nDISPLAYNL({concat("strings.TO_SENTENCE(value + 1)", "\" \"", "second")}).'),
    ]
    io_values={
        "numeric_double_label":[("A","2"),("mass","3.5"),("zero","0"),("neg","-2"),("x","10")],
        "field_lengths":[("A","B"),("red","blue"),("hello","world"),("x",""),("two words","ok")],
        "upper_status_trim_title":[("  task  ","ok"),("build","pending"),(" x ","done"),("alpha beta","hold"),("z","go")],
        "reverse_and_length":[("abc","xy"),("GoCo","language"),("x",""),("two words","ok"),("123","abcd")],
        "length_suffix":[("A","B"),("red","blue"),("hello","world"),("x",""),("two words","ok")],
        "upper_labels":[("A","B"),("red","blue"),("hello","world"),("x",""),("two words","ok")],
        "repeat_by_count":[("a","3"),("Go","2"),("x","1"),("z","0"),("ab","4")],
        "increment_with_unit":[("1","kg"),("0","m"),("-2","C"),("3.5","s"),("10","items")],
    }
    for name,solver,body in io_eval:
        source=split_sentences(["first","second"])+body
        emit("IO",io,f"Read first|second and perform {name.replace('_',' ')} exactly.",source,[(f"{a}|{b}",solver(a,b)) for a,b in io_values[name]],name,"split_transform_output","split2>"+name+">display")

    cp=FAMILIES[7]
    cp_specs=[
        ("quadratic_sequence_classification","NUMBER total = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) { total += i * i + i. }\nIF (total % 3 == 0) { DISPLAYNL(\"THREE\"). } ELSE { DISPLAYNL(\"OTHER\"). }",lambda n:"THREE" if sum(i*i+i for i in range(1,n+1))%3==0 else "OTHER"),
        ("proper_divisor_sum","NUMBER total = 0.\nLOOP (NUMBER i = 1 TILL i < n, i++) { IF (n % i == 0) { total += i. } }\nDISPLAYNL(total).",lambda n:sum(i for i in range(1,n) if n%i==0)),
        ("count_xor_divisibility","NUMBER count = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) { IF ((i % 2 == 0 AND i % 3 != 0) OR (i % 2 != 0 AND i % 3 == 0)) { count += 1. } }\nDISPLAYNL(count).",lambda n:sum((i%2==0)^(i%3==0) for i in range(1,n+1))),
        ("sum_then_parity","NUMBER total = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) { total += i. }\nIF (total % 2 == 0) { DISPLAYNL(\"EVEN\"). } ELSE { DISPLAYNL(\"ODD\"). }",lambda n:"EVEN" if (n*(n+1)//2)%2==0 else "ODD"),
        ("factorial_threshold","NUMBER total = 1.\nLOOP (NUMBER i = 1 TILL i <= n, i++) { total *= i. }\nIF (total >= 100) { DISPLAYNL(\"LARGE\"). } ELSE { DISPLAYNL(\"SMALL\"). }",lambda n:"LARGE" if math.prod(range(1,n+1))>=100 else "SMALL"),
        ("square_sum_threshold","NUMBER total = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) { total += i * i. }\nIF (total > 50) { DISPLAYNL(\"OVER\"). } ELSE { DISPLAYNL(\"UNDER\"). }",lambda n:"OVER" if sum(i*i for i in range(1,n+1))>50 else "UNDER"),
        ("divisor_parity","NUMBER count = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) { IF (n % i == 0) { count += 1. } }\nIF (count % 2 == 0) { DISPLAYNL(\"EVEN COUNT\"). } ELSE { DISPLAYNL(\"ODD COUNT\"). }",lambda n:"EVEN COUNT" if sum(n%i==0 for i in range(1,n+1))%2==0 else "ODD COUNT"),
        ("filtered_square_sum","NUMBER total = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) { IF (i % 2 != 0) { total += i * i. } }\nDISPLAYNL(total).",lambda n:sum(i*i for i in range(1,n+1) if i%2)),
    ]
    for name,body,solver in cp_specs:
        source="NUMBER n.\nINPUT(n).\n"+body
        emit("CP",cp,f"Read positive n and compute {name.replace('_',' ')} using loops and conditionals.",source,[(str(n),solver(n)) for n in [1,2,4,6,10]],name,"loop_and_branch","input>loop>"+name+">display",[r"LOOP\s*\("])
    return tasks,refs,tests


def build_regression() -> list[dict[str, Any]]:
    rows=[]
    items=[
        ("trace_python_add","What does this Python expression print: 3 + 4 * 2? Reply with only the number.","11"),
        ("trace_python_slice","What does Python 'abcdef'[1:4] evaluate to? Reply with only the text.","bcd"),
        ("trace_python_len","What does len([10, 20, 30, 40]) return? Reply with only the number.","4"),
        ("trace_python_bool","In Python, what does bool([]) evaluate to? Reply TRUE or FALSE only.","FALSE"),
        ("trace_js_mod","What is 17 % 5 in JavaScript? Reply with only the number.","2"),
        ("trace_loop_sum","A loop adds integers 1 through 5 inclusive. Reply with only the final sum.","15"),
        ("trace_zero_index","For array [8, 6, 4], what value is at zero-based index 1? Reply with only the number.","6"),
        ("trace_precedence","Evaluate (2 + 3) * 4. Reply with only the number.","20"),
        ("instruction_upper","Convert 'quiet river' to uppercase. Reply with only the result.","QUIET RIVER"),
        ("instruction_reverse","Reverse the characters in 'stressed'. Reply with only the result.","desserts"),
        ("instruction_sort","Sort 9, 2, 5 ascending. Reply as comma-separated numbers with no spaces.","2,5,9"),
        ("instruction_count","How many letters are in 'compiler'? Reply with only the number.","8"),
        ("instruction_first","Return the first word of 'small reliable system'. Reply with only that word.","small"),
        ("instruction_last","Return the last word of 'tests protect behavior'. Reply with only that word.","behavior"),
        ("instruction_replace","Replace every '-' in 'a-b-c' with ':'. Reply with only the result.","a:b:c"),
        ("instruction_concat","Concatenate 'data' and 'set' with an underscore. Reply with only the result.","data_set"),
        ("concept_stack","Which data structure is LIFO? Reply with one lowercase word.","stack"),
        ("concept_queue","Which data structure is FIFO? Reply with one lowercase word.","queue"),
        ("concept_binary","How many possible values does one bit have? Reply with only the number.","2"),
        ("concept_http","Which HTTP method is conventionally used to retrieve a resource? Reply with the uppercase method only.","GET"),
        ("concept_sql","Which SQL keyword filters rows? Reply with the uppercase keyword only.","WHERE"),
        ("concept_git","Which Git command records staged changes as a new revision? Reply with the command's subcommand only.","commit"),
        ("concept_complexity","What is the typical lookup complexity of a hash table, using Big-O notation? Reply with only the notation.","O(1)"),
        ("concept_json","Which two JSON literals represent boolean values? Reply exactly: true,false","true,false"),
    ]
    for index,(lineage,prompt,expected) in enumerate(items,1):
        rows.append({"task_id":f"P2A-REG-{index:02d}","split":"phase2a_general_regression","category":lineage.split("_",1)[0],"template_lineage":f"p2a-reg-{lineage}","prompt":prompt,"expected":expected})
    return rows


def write_new(path: Path, value: Any) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path("."))
    args=parser.parse_args()
    train,train_refs,train_tests=build_training()
    dev,dev_refs,dev_tests=build_eval()
    if len(train)!=200 or len(dev)!=64:
        raise AssertionError((len(train),len(dev)))
    training_examples=[]
    for task in train:
        training_examples.append({
            "example_id":task["task_id"],"split":"phase2a_train","family":task["family"],
            "prompt":task["prompt"],"target":train_refs[task["task_id"]],
            "algorithmic_structure":task["algorithmic_structure"],"control_flow":task["control_flow"],
            "template_lineage":task["template_lineage"],"structural_signature":task["structural_signature"],
        })
    root=args.root
    write_new(root/"data/phase2a/training_examples.json",training_examples)
    write_new(root/"data/phase2a/training_hidden_tests.json",train_tests)
    write_new(root/"benchmark/phase2a/development_tasks.json",dev)
    write_new(root/"benchmark/phase2a/development_references.json",dev_refs)
    write_new(root/"benchmark/phase2a/development_hidden_tests.json",dev_tests)
    write_new(root/"benchmark/phase2a/general_regression.json",build_regression())
    print(json.dumps({"training_examples":len(train),"development_tasks":len(dev),"general_regression":24},indent=2))


if __name__=="__main__":
    main()
