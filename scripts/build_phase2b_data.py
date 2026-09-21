from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any, Callable


FAMILIES = (
    "expressions_variables", "conditionals", "loops", "functions",
    "arrays", "strings", "input_output", "composition_algorithms",
)


def number(value: float | int) -> str:
    value = float(value)
    return f"{round(value):.1f}" if math.isclose(value, round(value), abs_tol=1e-10) else repr(value)


def case(index: int, stdin: str, expected: str | float | int) -> dict[str, str]:
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
        "IMPORT strings.\nSENTENCE line.\nINPUT(line).\n"
        "SENTENCE[] parts = strings.SPLIT(line, \"|\").\n" + declarations + "\n"
    )


def split_sentences(names: list[str]) -> str:
    declarations = "\n".join(f"SENTENCE {name} = parts[{i}]." for i, name in enumerate(names))
    return (
        "IMPORT strings.\nSENTENCE line.\nINPUT(line).\n"
        "SENTENCE[] parts = strings.SPLIT(line, \"|\").\n" + declarations + "\n"
    )


def concat(*parts: str) -> str:
    if len(parts) < 2:
        raise ValueError(parts)
    result = f"strings.CONCAT({parts[0]}, {parts[1]})"
    for part in parts[2:]:
        result = f"strings.CONCAT({result}, {part})"
    return result


def ast_proxy(source: str) -> str:
    tokens = re.findall(
        r"\b(?:IMPORT|INPUT|DISPLAYNL|IF|ELSEIF|ELSE|LOOP|FUNCTION|RETURN|RETURNS|AND|OR|NOT)\b|"
        r"\b(?:strings|arrays|math)\.[A-Z_]+|(?:\+=|-=|\*=|/=|==|!=|>=|<=|[%+*/-])",
        source.upper(),
    )
    return ">".join(tokens)


def add(
    tasks: list[dict[str, Any]], refs: dict[str, str], tests: dict[str, list[dict[str, str]]],
    *, task_id: str, split: str, family: str, prompt: str, source: str,
    cases: list[dict[str, str]], algorithm: str, flow: str, lineage: str,
    signature: str, semantic_ops: list[str], required: list[str] | None = None,
) -> None:
    source = source.strip()
    tasks.append({
        "task_id": task_id, "split": split, "level": "full_synthesis", "family": family,
        "difficulty": "phase2b_confirmatory", "prompt": prompt,
        "algorithmic_structure": algorithm, "control_flow": flow,
        "template_lineage": lineage, "structural_signature": signature,
        "ast_proxy_signature": ast_proxy(source), "semantic_operations": semantic_ops,
        "required_regex": required or [],
    })
    refs[task_id] = source
    tests[task_id] = cases


def build_training() -> tuple[list[dict[str, Any]], dict[str, str], dict[str, list[dict[str, str]]]]:
    tasks: list[dict[str, Any]] = []
    refs: dict[str, str] = {}
    tests: dict[str, list[dict[str, str]]] = {}
    split = "phase2b_train"

    # Expressions/variables: five fresh semantic structures, five parameterizations each.
    ev_specs: list[tuple[str, Callable[[int], tuple[str, str, list[tuple[str, float]], list[str], str]]]] = [
        ("quotient_shift", lambda k: (
            f"Read x and print x divided by {k + 1}, then add {k}.",
            f"NUMBER x.\nINPUT(x).\nNUMBER q = x / {k + 1}.\nDISPLAYNL(q + {k}).",
            [(str(x), x / (k + 1) + k) for x in (-6, 0, 10)], ["division", "offset"], "input>divide>offset>display")),
        ("difference_of_squares", lambda k: (
            f"Read a|b and print (a-b)*(a+b) plus {k}.",
            split_numbers(["a", "b"]) + f"NUMBER left = a - b.\nNUMBER right = a + b.\nDISPLAYNL(left * right + {k}).",
            [(f"{a}|{b}", (a-b)*(a+b)+k) for a,b in ((1,2),(-3,4),(8,-1))],
            ["pair_split", "difference_of_squares"], "split2>two_intermediates>multiply>offset>display")),
        ("ceiling_scale", lambda k: (
            f"Read x and print ceil(x/{k + 2}) plus {k}.",
            f"IMPORT math.\nNUMBER x.\nINPUT(x).\nDISPLAYNL(math.CEIL(x / {k + 2}) + {k}).",
            [(str(x), math.ceil(x/(k+2))+k) for x in (-5, 0, 13)], ["ceil", "division"],
            "import_math>input>divide>ceil>offset>display")),
        ("triple_product_adjust", lambda k: (
            f"Read a|b|c and print a*b-c plus {k}.",
            split_numbers(["a", "b", "c"]) + f"NUMBER product = a * b.\nDISPLAYNL(product - c + {k}).",
            [(f"{a}|{b}|{c}", a*b-c+k) for a,b,c in ((1,2,3),(-2,5,1),(4,-1,-3))],
            ["triple_split", "product", "subtraction"], "split3>product>subtract>offset>display")),
        ("remainder_scale", lambda k: (
            f"Read integer-like n and print (n modulo {k + 2}) times {k + 1}.",
            f"NUMBER n.\nINPUT(n).\nNUMBER remainder = n % {k + 2}.\nDISPLAYNL(remainder * {k + 1}).",
            [(str(n), (n%(k+2))*(k+1)) for n in (0, k+3, 4*k+11)],
            ["modulo", "scale"], "input>modulo>scale>display")),
    ]
    for archetype, factory in ev_specs:
        for k in range(1, 6):
            prompt, source, values, ops, sig = factory(k)
            tid = f"P2B-TR-EV-{archetype.upper()}-{k:02d}"
            add(tasks, refs, tests, task_id=tid, split=split, family=FAMILIES[0], prompt=prompt,
                source=source, cases=[case(i+1,*v) for i,v in enumerate(values)],
                algorithm=f"{archetype}_{k}", flow="straight_line_expression",
                lineage=f"p2b-tr-ev-{archetype}-{k}", signature=sig, semantic_ops=ops)

    # Conditionals.
    for k in range(1, 6):
        specs = [
            ("smaller_with_tie", f"Read a|b. Print TIE if equal; otherwise print the smaller number plus {k}.",
             split_numbers(["a","b"]) + f'IF (a == b) {{ DISPLAYNL("TIE"). }} ELSEIF (a < b) {{ DISPLAYNL(a + {k}). }} ELSE {{ DISPLAYNL(b + {k}). }}',
             [("2|2","TIE"),("1|4",1+k),("8|-2",-2+k)], ["pair_compare","three_way_branch"], "split2>equality>less_than>numeric_display"),
            ("parity_sign", f"Read n. Print NEG when negative, EVEN{k} when nonnegative even, otherwise ODD{k}.",
             f'NUMBER n.\nINPUT(n).\nIF (n < 0) {{ DISPLAYNL("NEG"). }} ELSEIF (n % 2 == 0) {{ DISPLAYNL("EVEN{k}"). }} ELSE {{ DISPLAYNL("ODD{k}"). }}',
             [("-3","NEG"),("4",f"EVEN{k}"),("5",f"ODD{k}")], ["sign","parity","three_way_branch"], "input>negative_branch>modulo_branch>display"),
            ("outside_interval", f"Read x. Print OUT when x is below {-k} or above {2*k+3}; otherwise print IN.",
             f'NUMBER x.\nINPUT(x).\nIF (x < {-k} OR x > {2*k+3}) {{ DISPLAYNL("OUT"). }} ELSE {{ DISPLAYNL("IN"). }}',
             [(str(-k-1),"OUT"),("0","IN"),(str(2*k+4),"OUT")], ["or_condition","open_exterior"], "input>or_exterior_branch>display"),
            ("either_divisor", f"Read n. Print MATCH if divisible by {k+1} or {k+3}, else MISS.",
             f'NUMBER n.\nINPUT(n).\nIF (n % {k+1} == 0 OR n % {k+3} == 0) {{ DISPLAYNL("MATCH"). }} ELSE {{ DISPLAYNL("MISS"). }}',
             [(str(k+1),"MATCH"),(str(k+2),"MISS"),(str((k+3)*2),"MATCH")], ["dual_divisibility","or_condition"], "input>dual_modulo_or>display"),
            ("absolute_band", f"Read x. Print NEAR if abs(x) <= {k+2}, otherwise FAR.",
             f'IMPORT math.\nNUMBER x.\nINPUT(x).\nIF (math.ABS(x) <= {k+2}) {{ DISPLAYNL("NEAR"). }} ELSE {{ DISPLAYNL("FAR"). }}',
             [("0","NEAR"),(str(k+2),"NEAR"),(str(-k-5),"FAR")], ["absolute_value","threshold"], "import_math>input>abs_threshold_branch>display"),
        ]
        for name,prompt,source,values,ops,sig in specs:
            tid=f"P2B-TR-CD-{name.upper()}-{k:02d}"
            add(tasks,refs,tests,task_id=tid,split=split,family=FAMILIES[1],prompt=prompt,source=source,
                cases=[case(i+1,*v) for i,v in enumerate(values)],algorithm=f"{name}_{k}",flow="conditional",
                lineage=f"p2b-tr-cd-{name}-{k}",signature=sig,semantic_ops=ops,required=[r"IF\s*\("])

    # Loops.
    for k in range(1,6):
        loop_specs = [
            ("linear_term_sum", f"Read nonnegative n and sum 3*i+{k} for i=1..n.",
             f"NUMBER n.\nINPUT(n).\nNUMBER total = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) {{ total += 3 * i + {k}. }}\nDISPLAYNL(total).",
             lambda n,k=k: sum(3*i+k for i in range(1,n+1)), ["counted_loop","affine_accumulation"], "input>loop>affine_sum>display"),
            ("nonmultiple_count", f"Read nonnegative n and count values 1..n not divisible by {k+2}.",
             f"NUMBER n.\nINPUT(n).\nNUMBER count = 0.\nLOOP (NUMBER i = 1 TILL i <= n, i++) {{ IF (i % {k+2} != 0) {{ count += 1. }} }}\nDISPLAYNL(count).",
             lambda n,k=k: sum(i%(k+2)!=0 for i in range(1,n+1)), ["loop_filter","nondivisibility","count"], "input>loop>modulo_if>count>display"),
            ("shifted_product", f"Read nonnegative n and multiply i+{k} for i=1..n.",
             f"NUMBER n.\nINPUT(n).\nNUMBER product = 1.\nLOOP (NUMBER i = 1 TILL i <= n, i++) {{ product *= i + {k}. }}\nDISPLAYNL(product).",
             lambda n,k=k: math.prod((i+k for i in range(1,n+1)),start=1), ["counted_loop","product"], "input>loop>shifted_product>display"),
            ("even_minus_odd", f"Read nonnegative n; add evens and subtract odds from 1 through n, then add {k}.",
             f"NUMBER n.\nINPUT(n).\nNUMBER total = {k}.\nLOOP (NUMBER i = 1 TILL i <= n, i++) {{ IF (i % 2 == 0) {{ total += i. }} ELSE {{ total -= i. }} }}\nDISPLAYNL(total).",
             lambda n,k=k: k+sum(i if i%2==0 else -i for i in range(1,n+1)), ["loop_branch","alternating_accumulation"], "input>loop>parity_if>add_subtract>display"),
            ("cubic_offset_sum", f"Read nonnegative n, sum the cubes from 1 through n, then add {k}.",
             f"NUMBER n.\nINPUT(n).\nNUMBER total = {k}.\nLOOP (NUMBER i = 1 TILL i <= n, i++) {{ total += i * i * i. }}\nDISPLAYNL(total).",
             lambda n,k=k: k+sum(i**3 for i in range(1,n+1)), ["cubic_sum","offset_accumulation"], "input>loop>cube_accumulate>offset>display"),
        ]
        for name,prompt,source,solver,ops,sig in loop_specs:
            tid=f"P2B-TR-LP-{name.upper()}-{k:02d}"; ns=[0,2,5]
            add(tasks,refs,tests,task_id=tid,split=split,family=FAMILIES[2],prompt=prompt,source=source,
                cases=[case(i+1,str(n),solver(n)) for i,n in enumerate(ns)],algorithm=f"{name}_{k}",flow="counted_loop",
                lineage=f"p2b-tr-lp-{name}-{k}",signature=sig,semantic_ops=ops,required=[r"LOOP\s*\("])

    # Functions.
    for k in range(1,6):
        fn_specs = [
            ("weighted_pair", f"Define a two-number function returning a+{k}*b. Read a|b and print it.",
             f"FUNCTION combine(NUMBER a, NUMBER b) {{ RETURN a + {k} * b. }} RETURNS NUMBER.\n"+split_numbers(["a","b"])+"DISPLAYNL(combine(a,b)).",
             lambda a,b,k=k:a+k*b, ["two_argument_function","weighted_sum"], "function2>split2>call>display"),
            ("composed_functions", f"Define inc and scale functions; print scale(inc(x)) using constants {k} and {k+1}.",
             f"FUNCTION inc(NUMBER x) {{ RETURN x + {k}. }} RETURNS NUMBER.\nFUNCTION scale(NUMBER x) {{ RETURN x * {k+1}. }} RETURNS NUMBER.\nNUMBER x.\nINPUT(x).\nDISPLAYNL(scale(inc(x))).",
             lambda x,k=k:(x+k)*(k+1), ["function_composition","nested_call"], "function>function>input>nested_call>display"),
            ("conditional_function", f"Define a function returning x when nonnegative and -x+{k} otherwise; read x and print it.",
             f"FUNCTION adjust(NUMBER x) {{ IF (x >= 0) {{ RETURN x. }} ELSE {{ RETURN 0 - x + {k}. }} }} RETURNS NUMBER.\nNUMBER x.\nINPUT(x).\nDISPLAYNL(adjust(x)).",
             lambda x,k=k:x if x>=0 else -x+k, ["function_branch","return"], "function_if_returns>input>call>display"),
            ("squared_distance", f"Define a two-number function returning (a-b)^2 plus {k}; read a|b and print it.",
             f"FUNCTION distance2(NUMBER a, NUMBER b) {{ NUMBER d = a - b. RETURN d * d + {k}. }} RETURNS NUMBER.\n"+split_numbers(["a","b"])+"DISPLAYNL(distance2(a,b)).",
             lambda a,b,k=k:(a-b)**2+k, ["two_argument_function","squared_distance"], "function2>local>split2>call>display"),
            ("clamp_function", f"Define a function clamping x to [{-k},{2*k}], then read x and print it.",
             f"FUNCTION clamp(NUMBER x) {{ IF (x < {-k}) {{ RETURN {-k}. }} ELSEIF (x > {2*k}) {{ RETURN {2*k}. }} ELSE {{ RETURN x. }} }} RETURNS NUMBER.\nNUMBER x.\nINPUT(x).\nDISPLAYNL(clamp(x)).",
             lambda x,k=k:max(-k,min(2*k,x)), ["function_three_way_branch","clamp"], "function_three_return>input>call>display"),
        ]
        for name,prompt,source,solver,ops,sig in fn_specs:
            tid=f"P2B-TR-FN-{name.upper()}-{k:02d}"
            if name in {"weighted_pair","squared_distance"}:
                vals=[(1,2),(-3,4),(8,-1)]; pairs=[(f"{a}|{b}",solver(a,b)) for a,b in vals]
            else:
                vals=[-4,0,7]; pairs=[(str(x),solver(x)) for x in vals]
            add(tasks,refs,tests,task_id=tid,split=split,family=FAMILIES[3],prompt=prompt,source=source,
                cases=[case(i+1,*v) for i,v in enumerate(pairs)],algorithm=f"{name}_{k}",flow="function_definition_call",
                lineage=f"p2b-tr-fn-{name}-{k}",signature=sig,semantic_ops=ops,required=[r"FUNCTION\s+"])

    # Arrays.
    for k in range(1,6):
        array_specs = [
            ("weighted_four", f"Read four pipe-delimited numbers into an array and print v0+2*v1+3*v2+{k}*v3.",
             split_numbers(["a","b","c","d"])+f"NUMBER[] values = [a,b,c,d].\nDISPLAYNL(values[0] + 2 * values[1] + 3 * values[2] + {k} * values[3]).",
             lambda xs,k=k:xs[0]+2*xs[1]+3*xs[2]+k*xs[3], ["array_literal","weighted_indexing"], "split4>array>weighted_indices>display",4),
            ("count_even_five", f"Read five numbers into an array, count even entries, then add {k}.",
             split_numbers(["a","b","c","d","e"])+f"NUMBER[] values=[a,b,c,d,e].\nNUMBER count={k}.\nLOOP (NUMBER i=0 TILL i<5, i++) {{ IF (values[i] % 2 == 0) {{ count += 1. }} }}\nDISPLAYNL(count).",
             lambda xs,k=k:k+sum(x%2==0 for x in xs), ["array_loop","parity_count"], "split5>array>loop>modulo_if>count>display",5),
            ("absolute_sum_three", f"Read three numbers into an array and print the sum of absolute values plus {k}.",
             split_numbers(["a","b","c"])+f"IMPORT math.\nNUMBER[] values=[a,b,c].\nNUMBER total={k}.\nLOOP (NUMBER i=0 TILL i<3, i++) {{ total += math.ABS(values[i]). }}\nDISPLAYNL(total).",
             lambda xs,k=k:k+sum(abs(x) for x in xs), ["array_loop","absolute_sum"], "split3>array>loop>abs_sum>display",3),
            ("range_three", f"Read three numbers into an array and print max-min plus {k}.",
             split_numbers(["a","b","c"])+f"IMPORT math.\nNUMBER[] values=[a,b,c].\nNUMBER hi=math.MAX(values[0],math.MAX(values[1],values[2])).\nNUMBER lo=math.MIN(values[0],math.MIN(values[1],values[2])).\nDISPLAYNL(hi-lo+{k}).",
             lambda xs,k=k:max(xs)-min(xs)+k, ["array_index","nested_minmax","range"], "split3>array>nested_minmax>subtract>display",3),
            ("dot_three", f"Read six numbers as two arrays of three and print their dot product plus {k}.",
             split_numbers(["a","b","c","d","e","f"])+f"NUMBER[] left=[a,b,c].\nNUMBER[] right=[d,e,f].\nDISPLAYNL(left[0]*right[0]+left[1]*right[1]+left[2]*right[2]+{k}).",
             lambda xs,k=k:sum(xs[i]*xs[i+3] for i in range(3))+k, ["two_arrays","dot_product"], "split6>two_arrays>dot_product>display",6),
        ]
        for name,prompt,source,solver,ops,sig,width in array_specs:
            samples={3:[[1,2,3],[-2,0,5],[4,-1,2]],4:[[1,2,3,4],[-2,0,5,1],[4,-1,2,-3]],5:[[1,2,3,4,5],[-2,0,5,1,-4],[4,-1,2,-3,8]],6:[[1,2,3,4,5,6],[-2,0,5,1,-4,2],[4,-1,2,-3,8,1]]}[width]
            tid=f"P2B-TR-AR-{name.upper()}-{k:02d}"
            add(tasks,refs,tests,task_id=tid,split=split,family=FAMILIES[4],prompt=prompt,source=source,
                cases=[case(i+1,"|".join(map(str,xs)),solver(xs)) for i,xs in enumerate(samples)],algorithm=f"{name}_{k}",flow="array_processing",
                lineage=f"p2b-tr-ar-{name}-{k}",signature=sig,semantic_ops=ops,required=[r"NUMBER\[\]"])

    # Strings.
    for k in range(1,6):
        char = ["a","e","i","o","u"][k-1]
        string_specs = [
            ("replace_vowel", f"Read text and replace every '{char}' with '#'.", f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.REPLACE(text,"{char}","#")).', lambda s,c=char:s.replace(c,"#"), ["replace"], "input>replace>display"),
            ("count_letter", f"Read text and print how many times '{char}' occurs, plus {k}.", f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.COUNT(text,"{char}")+{k}).', lambda s,c=char,k=k:s.count(c)+k, ["substring_count","offset"], "input>count>offset>display"),
            ("char_at", f"Read text of length at least 6 and print the character at zero-based index {k}.", f"IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.CHARAT(text,{k})).", lambda s,k=k:s[k], ["character_index"], "input>charat>display"),
            ("trim_marker", f"Read text and trim '{k}' characters from both ends.", f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nDISPLAYNL(strings.TRIM(text,"{k}")).', lambda s,k=k:s.strip(str(k)), ["trim_character_set"], "input>trim>display"),
            ("contains_label", f"Read text and print HAS{k} if it contains '{char}{char}', otherwise NO{k}.", f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nIF (strings.CONTAINS(text,"{char}{char}")) {{ DISPLAYNL("HAS{k}"). }} ELSE {{ DISPLAYNL("NO{k}"). }}', lambda s,c=char,k=k:f"HAS{k}" if c+c in s else f"NO{k}", ["contains","branch"], "input>contains_if>display"),
        ]
        for name,prompt,source,solver,ops,sig in string_specs:
            vals=["seaside", "bananas", "uvwxyzABC"]
            tid=f"P2B-TR-ST-{name.upper()}-{k:02d}"
            add(tasks,refs,tests,task_id=tid,split=split,family=FAMILIES[5],prompt=prompt,source=source,
                cases=[case(i+1,s,solver(s)) for i,s in enumerate(vals)],algorithm=f"{name}_{k}",flow="string_operation",
                lineage=f"p2b-tr-st-{name}-{k}",signature=sig,semantic_ops=ops)

    # Input/output formatting.
    for k in range(1,6):
        formats = [
            ("tagged_pair", f"Read first|second and print <{k}:first>[second].", f'DISPLAYNL({concat(f"\"<{k}:\"","first","\">[\"","second","\"]\"")}).', lambda a,b,k=k:f"<{k}:{a}>[{b}]", ["field_format"], "split2>tagged_concat>display"),
            ("two_labeled_lines", f"Read first|second and print X{k}=first then Y{k}=second on separate lines.", f'DISPLAYNL(strings.CONCAT("X{k}=",first)).\nDISPLAYNL(strings.CONCAT("Y{k}=",second)).', lambda a,b,k=k:f"X{k}={a}\nY{k}={b}", ["two_line_format"], "split2>two_labeled_displays"),
            ("case_pair", f"Read first|second and print uppercase first, a slash, then lowercase second and marker {k}.", f'DISPLAYNL({concat("strings.UPPER(first)","\"/\"","strings.LOWER(second)",f"\"/{k}\"")}).', lambda a,b,k=k:f"{a.upper()}/{b.lower()}/{k}", ["case_transform","format"], "split2>upper_lower>concat>display"),
            ("reversed_fields", f"Read first|second and print reverse(second)|reverse(first)|{k}.", f'DISPLAYNL({concat("strings.REVERSE(second)","\"|\"","strings.REVERSE(first)",f"\"|{k}\"")}).', lambda a,b,k=k:f"{b[::-1]}|{a[::-1]}|{k}", ["field_reverse","format"], "split2>reverse_both>concat>display"),
            ("length_product", f"Read first|second and print the product of their lengths plus {k}.", f'DISPLAYNL(strings.LENGTH(first)*strings.LENGTH(second)+{k}).', lambda a,b,k=k:len(a)*len(b)+k, ["field_lengths","product"], "split2>length_product>display"),
        ]
        for name,prompt,body,solver,ops,sig in formats:
            source=split_sentences(["first","second"])+body; vals=[("A","B"),("Red","BLUE"),("hello world","ok")]
            tid=f"P2B-TR-IO-{name.upper()}-{k:02d}"
            add(tasks,refs,tests,task_id=tid,split=split,family=FAMILIES[6],prompt=prompt,source=source,
                cases=[case(i+1,f"{a}|{b}",solver(a,b)) for i,(a,b) in enumerate(vals)],algorithm=f"{name}_{k}",flow="input_output_format",
                lineage=f"p2b-tr-io-{name}-{k}",signature=sig,semantic_ops=ops)

    # Composition/algorithms.
    for k in range(1,6):
        comp_specs = [
            ("include_exclude_sum", f"Read n; sum values 1..n divisible by {k+1} but not by {k+2}.", f"NUMBER n.\nINPUT(n).\nNUMBER total=0.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ IF (i%{k+1}==0 AND i%{k+2}!=0) {{ total+=i. }} }}\nDISPLAYNL(total).", lambda n,k=k:sum(i for i in range(1,n+1) if i%(k+1)==0 and i%(k+2)!=0), ["loop_filter","dual_modulo","sum"], "input>loop>and_modulo_if>sum>display"),
            ("factorial_class", f"Read n, compute n!, and print BIG{k} if it exceeds {20*k}, else SMALL{k}.", f'NUMBER n.\nINPUT(n).\nNUMBER product=1.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ product*=i. }}\nIF (product>{20*k}) {{ DISPLAYNL("BIG{k}"). }} ELSE {{ DISPLAYNL("SMALL{k}"). }}', lambda n,k=k:f"BIG{k}" if math.prod(range(1,n+1))>20*k else f"SMALL{k}", ["factorial","threshold_branch"], "input>product_loop>threshold_if>display"),
            ("array_positive_sum", f"Read four numbers into an array; sum positive values and add {k}.", split_numbers(["a","b","c","d"])+f"NUMBER[] values=[a,b,c,d].\nNUMBER total={k}.\nLOOP (NUMBER i=0 TILL i<4, i++) {{ IF (values[i]>0) {{ total+=values[i]. }} }}\nDISPLAYNL(total).", lambda xs,k=k:k+sum(x for x in xs if x>0), ["array_loop","positive_filter","sum"], "split4>array>loop>positive_if>sum>display"),
            ("string_length_class", f"Read text; lowercase it and print LONG{k} if length is at least {k+4}, else the lowercase text.", f'IMPORT strings.\nSENTENCE text.\nINPUT(text).\nSENTENCE low=strings.LOWER(text).\nIF (strings.LENGTH(low)>={k+4}) {{ DISPLAYNL("LONG{k}"). }} ELSE {{ DISPLAYNL(low). }}', lambda s,k=k:f"LONG{k}" if len(s)>=k+4 else s.lower(), ["lowercase","length_branch"], "input>lower>length_if>display"),
            ("function_loop_sum", f"Define a function returning x*x+{k}; read n and sum the function over 1..n.", f"FUNCTION term(NUMBER x) {{ RETURN x*x+{k}. }} RETURNS NUMBER.\nNUMBER n.\nINPUT(n).\nNUMBER total=0.\nLOOP (NUMBER i=1 TILL i<=n, i++) {{ total+=term(i). }}\nDISPLAYNL(total).", lambda n,k=k:sum(i*i+k for i in range(1,n+1)), ["function","loop","sum"], "function>input>loop>call_accumulate>display"),
        ]
        for name,prompt,source,solver,ops,sig in comp_specs:
            tid=f"P2B-TR-CP-{name.upper()}-{k:02d}"
            if name=="array_positive_sum":
                vals=[[1,-2,3,0],[-1,-2,-3,-4],[2,4,6,8]]; pairs=[("|".join(map(str,x)),solver(x)) for x in vals]
            elif name=="string_length_class":
                vals=["GoCo","alpha beta","XyZ"]; pairs=[(x,solver(x)) for x in vals]
            else:
                vals=[0,3,7]; pairs=[(str(x),solver(x)) for x in vals]
            add(tasks,refs,tests,task_id=tid,split=split,family=FAMILIES[7],prompt=prompt,source=source,
                cases=[case(i+1,*v) for i,v in enumerate(pairs)],algorithm=f"{name}_{k}",flow="composed_algorithm",
                lineage=f"p2b-tr-cp-{name}-{k}",signature=sig,semantic_ops=ops)

    return tasks, refs, tests


def build_evaluation() -> tuple[list[dict[str, Any]], dict[str, str], dict[str, list[dict[str, str]]]]:
    tasks: list[dict[str, Any]]=[]; refs: dict[str,str]={}; tests: dict[str,list[dict[str,str]]]={}
    split="phase2b_confirmatory_eval"; counters={f:0 for f in FAMILIES}

    def emit(prefix:str,family:str,prompt:str,source:str,values:list[tuple[str,Any]],algorithm:str,flow:str,signature:str,ops:list[str],required:list[str]|None=None)->None:
        counters[family]+=1; index=counters[family]; tid=f"P2B-EVAL-{prefix}{index:02d}"
        add(tasks,refs,tests,task_id=tid,split=split,family=family,prompt=prompt,source=source,
            cases=[case(i+1,*value) for i,value in enumerate(values)],algorithm=f"confirm_{algorithm}",flow=flow,
            lineage=f"p2b-eval-{prefix.lower()}-{index}-{algorithm}",signature=signature,semantic_ops=ops,required=required)

    ev=FAMILIES[0]
    ev_specs=[
        ("cubic_minus","Read x and print x cubed minus 7.","NUMBER x.\nINPUT(x).\nDISPLAYNL(x*x*x-7).",lambda x:x**3-7),
        ("weighted_gap","Given two pipe-delimited numbers, emit three times the first minus twice the second plus seven.",split_numbers(["a","b"])+"DISPLAYNL(3*a-2*b+7).",lambda a,b:3*a-2*b+7),
        ("shifted_cross_product","Given p|q, emit (p+2)*(q-3).",split_numbers(["p","q"])+"DISPLAYNL((p+2)*(q-3)).",lambda a,b:(a+2)*(b-3)),
        ("mass_speed_polynomial","Accept mass|speed and emit mass squared plus three times speed.",split_numbers(["mass","speed"])+"NUMBER energy=mass*mass+3*speed.\nDISPLAYNL(energy).",lambda a,b:a*a+3*b),
        ("hours_minutes","Read hours|minutes and print total minutes plus one.",split_numbers(["h","m"])+"DISPLAYNL(h*60+m+1).",lambda a,b:a*60+b+1),
        ("sqrt_shift","Read x and print sqrt(abs(x))+3.","IMPORT math.\nNUMBER x.\nINPUT(x).\nDISPLAYNL(math.SQRT(math.ABS(x))+3).",lambda x:math.sqrt(abs(x))+3),
        ("clamped_expression","Read x and print min(10,max(-2,x)).","IMPORT math.\nNUMBER x.\nINPUT(x).\nDISPLAYNL(math.MIN(10,math.MAX(-2,x))).",lambda x:min(10,max(-2,x))),
        ("affine_remainder","For integers a|b, emit the remainder of 3*a+2*b upon division by 11.",split_numbers(["a","b"])+"NUMBER combined=3*a+2*b.\nDISPLAYNL(combined%11).",lambda a,b:(3*a+2*b)-math.trunc((3*a+2*b)/11)*11),
        ("fahrenheit_celsius","Read Fahrenheit and print Celsius using (f-32)*5/9.","NUMBER f.\nINPUT(f).\nDISPLAYNL((f-32)*5/9).",lambda x:(x-32)*5/9),
        ("trapezoid_area","Read base1|base2|height and print trapezoid area.",split_numbers(["a","b","h"])+"DISPLAYNL((a+b)*h/2).",lambda a,b,c:(a+b)*c/2),
        ("mean_four","Read four values and print their arithmetic mean.",split_numbers(["a","b","c","d"])+"DISPLAYNL((a+b+c+d)/4).",lambda a,b,c,d:(a+b+c+d)/4),
        ("squared_origin_distance","Read x|y and print x*x+y*y.",split_numbers(["x","y"])+"DISPLAYNL(x*x+y*y).",lambda a,b:a*a+b*b),
        ("quotient_remainder_combo","Read integer-like n|d with nonzero d and print n/d+n%d.",split_numbers(["n","d"])+"DISPLAYNL(n/d+n%d).",lambda a,b:a/b+(a-math.trunc(a/b)*b)),
        ("percentage_of","Accept value|percent; compute the corresponding percentage amount and emit it.",split_numbers(["v","p"])+"NUMBER scaled=v*p.\nDISPLAYNL(scaled/100).",lambda a,b:a*b/100),
        ("hypotenuse","Read x|y and print sqrt(x*x+y*y).","IMPORT math.\n"+split_numbers(["x","y"])+"DISPLAYNL(math.SQRT(x*x+y*y)).",lambda a,b:math.sqrt(a*a+b*b)),
        ("quartic_polynomial","For scalar x, emit the square of (x squared minus one).","NUMBER x.\nINPUT(x).\nNUMBER square=x*x.\nDISPLAYNL(square*square-2*square+1).",lambda x:x**4-2*x*x+1),
    ]
    for name,prompt,source,solver in ev_specs:
        arity=solver.__code__.co_argcount
        samples={1:[(-3,), (0,), (5,), (9,), (16,)],2:[(1,2),(-3,4),(8,-1),(0,5),(12,3)],3:[(1,2,3),(4,6,2),(-2,5,4),(0,3,7),(10,-2,5)],4:[(1,2,3,4),(-2,0,5,1),(4,-1,2,-3),(0,0,0,0),(10,20,30,40)]}[arity]
        values=[("|".join(map(str,xs)) if arity>1 else str(xs[0]),solver(*xs)) for xs in samples]
        emit("EV",ev,prompt,source,values,name,"expression_pipeline",f"eval_ev>{name}",[name])

    cd=FAMILIES[1]
    cd_specs=[
        ("three_number_max","Read a|b|c and print the largest.",split_numbers(["a","b","c"])+"NUMBER best=a.\nIF (b>best) { best=b. }\nIF (c>best) { best=c. }\nDISPLAYNL(best).",lambda a,b,c:max(a,b,c)),
        ("grade_band","Read score and print A for >=80, B for >=60, otherwise C.",'NUMBER x.\nINPUT(x).\nIF (x>=80) { DISPLAYNL("A"). } ELSEIF (x>=60) { DISPLAYNL("B"). } ELSE { DISPLAYNL("C"). }',lambda x:"A" if x>=80 else "B" if x>=60 else "C"),
        ("leap_proxy","Read year and print LEAP if divisible by 4 but not 100, or divisible by 400; else COMMON.",'NUMBER y.\nINPUT(y).\nIF ((y%4==0 AND y%100!=0) OR y%400==0) { DISPLAYNL("LEAP"). } ELSE { DISPLAYNL("COMMON"). }',lambda y:"LEAP" if (y%4==0 and y%100!=0) or y%400==0 else "COMMON"),
        ("triangle_validity","Read a|b|c and print VALID if all positive and each pair sum exceeds the third.",split_numbers(["a","b","c"])+ 'IF (a>0 AND b>0 AND c>0 AND a+b>c AND a+c>b AND b+c>a) { DISPLAYNL("VALID"). } ELSE { DISPLAYNL("INVALID"). }',lambda a,b,c:"VALID" if a>0 and b>0 and c>0 and a+b>c and a+c>b and b+c>a else "INVALID"),
        ("quadrant_axis","Read x|y and print ORIGIN, AXIS, Q1, Q2, Q3, or Q4.",split_numbers(["x","y"])+ 'IF (x==0 AND y==0) { DISPLAYNL("ORIGIN"). } ELSEIF (x==0 OR y==0) { DISPLAYNL("AXIS"). } ELSEIF (x>0 AND y>0) { DISPLAYNL("Q1"). } ELSEIF (x<0 AND y>0) { DISPLAYNL("Q2"). } ELSEIF (x<0 AND y<0) { DISPLAYNL("Q3"). } ELSE { DISPLAYNL("Q4"). }',lambda x,y:"ORIGIN" if x==0 and y==0 else "AXIS" if x==0 or y==0 else "Q1" if x>0 and y>0 else "Q2" if x<0 and y>0 else "Q3" if x<0 and y<0 else "Q4"),
        ("majority_sign","Given a|b|c, print POS when at least two are positive, NEG when at least two are negative, otherwise MIX.",split_numbers(["a","b","c"])+"NUMBER positives=0.\nNUMBER negatives=0.\nIF (a>0) { positives+=1. } ELSEIF (a<0) { negatives+=1. }\nIF (b>0) { positives+=1. } ELSEIF (b<0) { negatives+=1. }\nIF (c>0) { positives+=1. } ELSEIF (c<0) { negatives+=1. }\nIF (positives>=2) { DISPLAYNL(\"POS\"). } ELSEIF (negatives>=2) { DISPLAYNL(\"NEG\"). } ELSE { DISPLAYNL(\"MIX\"). }",lambda a,b,c:"POS" if sum(x>0 for x in (a,b,c))>=2 else "NEG" if sum(x<0 for x in (a,b,c))>=2 else "MIX"),
        ("signed_parity_class","Classify one number as NEGATIVE, ZERO, POSITIVE_EVEN, or POSITIVE_ODD.",'NUMBER t.\nINPUT(t).\nIF (t<0) { DISPLAYNL("NEGATIVE"). } ELSEIF (t==0) { DISPLAYNL("ZERO"). } ELSEIF (t%2==0) { DISPLAYNL("POSITIVE_EVEN"). } ELSE { DISPLAYNL("POSITIVE_ODD"). }',lambda x:"NEGATIVE" if x<0 else "ZERO" if x==0 else "POSITIVE_EVEN" if x%2==0 else "POSITIVE_ODD"),
        ("exclusive_range","Read x and print EDGE at 5 or 15, INSIDE strictly between, otherwise OUTSIDE.",'NUMBER x.\nINPUT(x).\nIF (x==5 OR x==15) { DISPLAYNL("EDGE"). } ELSEIF (x>5 AND x<15) { DISPLAYNL("INSIDE"). } ELSE { DISPLAYNL("OUTSIDE"). }',lambda x:"EDGE" if x in (5,15) else "INSIDE" if 5<x<15 else "OUTSIDE"),
        ("multiple_class","Read n and print BOTH if divisible by 2 and 3, TWO, THREE, or NEITHER.",'NUMBER n.\nINPUT(n).\nIF (n%6==0) { DISPLAYNL("BOTH"). } ELSEIF (n%2==0) { DISPLAYNL("TWO"). } ELSEIF (n%3==0) { DISPLAYNL("THREE"). } ELSE { DISPLAYNL("NEITHER"). }',lambda n:"BOTH" if n%6==0 else "TWO" if n%2==0 else "THREE" if n%3==0 else "NEITHER"),
        ("closest_to_zero","Read a|b and print the value closer to zero; print TIE if equally distant.","IMPORT math.\n"+split_numbers(["a","b"])+ 'IF (math.ABS(a)==math.ABS(b)) { DISPLAYNL("TIE"). } ELSEIF (math.ABS(a)<math.ABS(b)) { DISPLAYNL(a). } ELSE { DISPLAYNL(b). }',lambda a,b:"TIE" if abs(a)==abs(b) else a if abs(a)<abs(b) else b),
        ("shipping_band","Read weight and print FREE for <=0, LIGHT for <=5, MEDIUM for <=20, HEAVY otherwise.",'NUMBER w.\nINPUT(w).\nIF (w<=0) { DISPLAYNL("FREE"). } ELSEIF (w<=5) { DISPLAYNL("LIGHT"). } ELSEIF (w<=20) { DISPLAYNL("MEDIUM"). } ELSE { DISPLAYNL("HEAVY"). }',lambda w:"FREE" if w<=0 else "LIGHT" if w<=5 else "MEDIUM" if w<=20 else "HEAVY"),
        ("odd_in_window","Read n and print YES only when n is odd and between 10 and 30 inclusive.",'NUMBER n.\nINPUT(n).\nIF (n>=10 AND n<=30 AND n%2!=0) { DISPLAYNL("YES"). } ELSE { DISPLAYNL("NO"). }',lambda n:"YES" if 10<=n<=30 and n%2 else "NO"),
        ("pair_same_sign","Read a|b and print SAME if both positive or both negative, otherwise DIFFERENT.",split_numbers(["a","b"])+ 'IF ((a>0 AND b>0) OR (a<0 AND b<0)) { DISPLAYNL("SAME"). } ELSE { DISPLAYNL("DIFFERENT"). }',lambda a,b:"SAME" if (a>0 and b>0) or (a<0 and b<0) else "DIFFERENT"),
        ("rounded_compare","Read a|b and print A if floor(a)>ceil(b), otherwise B.","IMPORT math.\n"+split_numbers(["a","b"])+ 'IF (math.FLOOR(a)>math.CEIL(b)) { DISPLAYNL("A"). } ELSE { DISPLAYNL("B"). }',lambda a,b:"A" if math.floor(a)>math.ceil(b) else "B"),
        ("bounded_divisible","Read n and print ACCEPT if 1<=n<=100 and divisible by 7; else REJECT.",'NUMBER n.\nINPUT(n).\nIF (n>=1 AND n<=100 AND n%7==0) { DISPLAYNL("ACCEPT"). } ELSE { DISPLAYNL("REJECT"). }',lambda n:"ACCEPT" if 1<=n<=100 and n%7==0 else "REJECT"),
        ("three_equality","Read a|b|c and print ALL, TWO, or NONE for equality patterns.",split_numbers(["a","b","c"])+ 'IF (a==b AND b==c) { DISPLAYNL("ALL"). } ELSEIF (a==b OR a==c OR b==c) { DISPLAYNL("TWO"). } ELSE { DISPLAYNL("NONE"). }',lambda a,b,c:"ALL" if a==b==c else "TWO" if a==b or a==c or b==c else "NONE"),
    ]
    for name,prompt,source,solver in cd_specs:
        arity=prompt.count("|")+1 if "|" in prompt else 1
        samples={1:[(-5,), (0,), (7,), (15,), (100,)],2:[(0,0),(1,-1),(-3,-2),(4,9),(8,8)],3:[(1,2,3),(3,3,3),(5,5,2),(3,4,5),(1,2,8)]}[arity]
        emit("CD",cd,prompt,source,[("|".join(map(str,x)) if arity>1 else str(x[0]),solver(*x)) for x in samples],name,"branching",f"eval_cd>{name}",[name],[r"IF\s*\("])

    lp=FAMILIES[2]
    loop_specs=[
        ("fourth_power_sum","sum i^4 for i=1..n","total+=i*i*i*i.",lambda n:sum(i**4 for i in range(1,n+1))),
        ("odd_counter","count odd values from 1..n","IF (i%2!=0) { total+=1. }",lambda n:sum(i%2 for i in range(1,n+1))),
        ("union_divisor_sum","sum values divisible by 3 or 5","IF (i%3==0 OR i%5==0) { total+=i. }",lambda n:sum(i for i in range(1,n+1) if i%3==0 or i%5==0)),
        ("conditional_product","multiply values from 1..n not divisible by 3","IF (i%3!=0) { total*=i. }",lambda n:math.prod((i for i in range(1,n+1) if i%3!=0),start=1)),
        ("bilinear_index_sum","sum i*(i+1) for i=1..n","total+=i*(i+1).",lambda n:sum(i*(i+1) for i in range(1,n+1))),
        ("multiple_counter","count multiples of 4 through n","IF (i%4==0) { total+=1. }",lambda n:sum(i%4==0 for i in range(1,n+1))),
        ("power_two_sum","sum powers 2^i for i=0..n","total+=math.POW(2,i).",lambda n:sum(2**i for i in range(0,n+1))),
        ("symmetric_products","sum i*(n-i) for i=0..n","total+=i*(n-i).",lambda n:sum(i*(n-i) for i in range(0,n+1))),
        ("descending_sum","sum n down to 1 using n-i","total+=n-i.",lambda n:sum(n-i for i in range(0,n))),
        ("square_even_sum","sum squares of even values through n","IF (i%2==0) { total+=i*i. }",lambda n:sum(i*i for i in range(1,n+1) if i%2==0)),
        ("alternating_square","add odd squares and subtract even squares","IF (i%2==0) { total-=i*i. } ELSE { total+=i*i. }",lambda n:sum(i*i if i%2 else -i*i for i in range(1,n+1))),
        ("divisor_count","count positive divisors of n","IF (n%i==0) { total+=1. }",lambda n:sum(n%i==0 for i in range(1,n+1))),
        ("proper_divisor_sum","sum positive divisors below n","IF (n%i==0 AND i<n) { total+=i. }",lambda n:sum(i for i in range(1,n) if n%i==0)),
        ("cumulative_triangles","sum i*(i+1)/2 through n","total+=i*(i+1)/2.",lambda n:sum(i*(i+1)/2 for i in range(1,n+1))),
        ("residue_two_sum","sum values congruent to 2 modulo 5","IF (i%5==2) { total+=i. }",lambda n:sum(i for i in range(1,n+1) if i%5==2)),
        ("rising_cubic_sum","sum i*(i+1)*(i+2) through n","total+=i*(i+1)*(i+2).",lambda n:sum(i*(i+1)*(i+2) for i in range(1,n+1))),
    ]
    for name,description,body,solver in loop_specs:
        if name=="power_two_sum": source="IMPORT math.\nNUMBER n.\nINPUT(n).\nNUMBER total=0.\nLOOP (NUMBER i=0 TILL i<=n, i++) { "+body+" }\nDISPLAYNL(total)."
        elif name=="conditional_product": source="NUMBER n.\nINPUT(n).\nNUMBER total=1.\nLOOP (NUMBER i=1 TILL i<=n, i++) { "+body+" }\nDISPLAYNL(total)."
        elif name=="descending_sum": source="NUMBER n.\nINPUT(n).\nNUMBER total=0.\nLOOP (NUMBER i=0 TILL i<n, i++) { "+body+" }\nDISPLAYNL(total)."
        else: source="NUMBER n.\nINPUT(n).\nNUMBER total=0.\nLOOP (NUMBER i=1 TILL i<=n, i++) { "+body+" }\nDISPLAYNL(total)."
        ns=[1,2,4,6,10]; emit("LP",lp,f"Read positive n and {description}.",source,[(str(n),solver(n)) for n in ns],name,"counted_loop",f"eval_lp>{name}",[name],[r"LOOP\s*\("])

    fn=FAMILIES[3]
    fn_specs=[
        ("quadratic_offset","function f(x)=x*x+2*x+3","FUNCTION f(NUMBER x) { RETURN x*x+2*x+3. } RETURNS NUMBER.",lambda x:x*x+2*x+3),
        ("average_three","three-argument average function","FUNCTION f(NUMBER a, NUMBER b, NUMBER c) { RETURN (a+b+c)/3. } RETURNS NUMBER.",lambda a,b,c:(a+b+c)/3),
        ("triangle_area","two-argument triangle area function","FUNCTION f(NUMBER b, NUMBER h) { RETURN b*h/2. } RETURNS NUMBER.",lambda a,b:a*b/2),
        ("min_three","three-argument minimum function","IMPORT math.\nFUNCTION f(NUMBER a, NUMBER b, NUMBER c) { RETURN math.MIN(a,math.MIN(b,c)). } RETURNS NUMBER.",lambda a,b,c:min(a,b,c)),
        ("bounded_shift","function that clamps x+3 into [0,10]","FUNCTION f(NUMBER x) { NUMBER y=x+3. IF (y<0) { RETURN 0. } ELSEIF (y>10) { RETURN 10. } ELSE { RETURN y. } } RETURNS NUMBER.",lambda x:max(0,min(10,x+3))),
        ("absolute_pair_sum","two-argument sum of absolute values","IMPORT math.\nFUNCTION f(NUMBER a, NUMBER b) { RETURN math.ABS(a)+math.ABS(b). } RETURNS NUMBER.",lambda a,b:abs(a)+abs(b)),
        ("neighbor_product","function returning (x-1)*x*(x+1)","FUNCTION f(NUMBER x) { RETURN x*x*x-x. } RETURNS NUMBER.",lambda x:x*x*x-x),
        ("parity_value","function returning 1 for even and 0 for odd","FUNCTION f(NUMBER x) { IF (x%2==0) { RETURN 1. } ELSE { RETURN 0. } } RETURNS NUMBER.",lambda x:1 if x%2==0 else 0),
        ("two_stage_offset","functions g(x)=2*x and f(x)=g(x)+5","FUNCTION g(NUMBER x) { RETURN 2*x. } RETURNS NUMBER.\nFUNCTION f(NUMBER x) { RETURN g(x)+5. } RETURNS NUMBER.",lambda x:2*x+5),
        ("rectangle_perimeter","two-argument perimeter function","FUNCTION f(NUMBER a, NUMBER b) { RETURN 2*(a+b). } RETURNS NUMBER.",lambda a,b:2*(a+b)),
        ("safe_difference","function returning larger minus smaller","FUNCTION f(NUMBER a, NUMBER b) { IF (a>=b) { RETURN a-b. } ELSE { RETURN b-a. } } RETURNS NUMBER.",lambda a,b:abs(a-b)),
        ("weighted_three","three-argument weighted function a+2b+3c","FUNCTION f(NUMBER a, NUMBER b, NUMBER c) { RETURN a+2*b+3*c. } RETURNS NUMBER.",lambda a,b,c:a+2*b+3*c),
        ("square_then_half","compose square and half functions","FUNCTION square(NUMBER x) { RETURN x*x. } RETURNS NUMBER.\nFUNCTION half(NUMBER x) { RETURN x/2. } RETURNS NUMBER.",lambda x:x*x/2),
        ("threshold_return","function returning 10 above 5 and -10 otherwise","FUNCTION f(NUMBER x) { IF (x>5) { RETURN 10. } ELSE { RETURN 0-10. } } RETURNS NUMBER.",lambda x:10 if x>5 else -10),
        ("remainder_function","two-argument function returning a modulo b","FUNCTION f(NUMBER a, NUMBER b) { RETURN a%b. } RETURNS NUMBER.",lambda a,b:a-math.trunc(a/b)*b),
        ("distance_origin","two-argument Euclidean distance function","IMPORT math.\nFUNCTION f(NUMBER x, NUMBER y) { RETURN math.SQRT(x*x+y*y). } RETURNS NUMBER.",lambda a,b:math.sqrt(a*a+b*b)),
    ]
    for name,description,defs,solver in fn_specs:
        arity=solver.__code__.co_argcount
        prefix=split_numbers(["a","b","c"][:arity]) if arity>1 else "NUMBER a.\nINPUT(a).\n"
        call="f(a,b,c)" if arity==3 else "f(a,b)" if arity==2 else "half(square(a))" if name=="square_then_half" else "f(a)"
        source=defs+"\n"+prefix+f"DISPLAYNL({call})."
        samples={1:[(-3,), (0,), (2,), (6,), (10,)],2:[(1,2),(-3,4),(8,-1),(0,5),(12,3)],3:[(1,2,3),(4,6,2),(-2,5,4),(0,3,7),(10,-2,5)]}[arity]
        emit("FN",fn,f"Define the requested {description}; read {'|'.join(['a','b','c'][:arity])} and print the function result.",source,[("|".join(map(str,x)) if arity>1 else str(x[0]),solver(*x)) for x in samples],name,"function_call",f"eval_fn>{name}",[name],[r"FUNCTION\s+"])

    ar=FAMILIES[4]
    array_specs=[
        ("sum_five","sum five entries",5,lambda xs:sum(xs),"NUMBER result=arrays.SUM(values)."),
        ("product_four","product of four entries",4,lambda xs:math.prod(xs),"NUMBER result=values[0]*values[1]*values[2]*values[3]."),
        ("maximum_five","maximum of five entries",5,lambda xs:max(xs),"NUMBER result=values[0].\nLOOP (NUMBER i=1 TILL i<5, i++) { IF (values[i]>result) { result=values[i]. } }"),
        ("minimum_four","minimum of four entries",4,lambda xs:min(xs),"NUMBER result=values[0].\nLOOP (NUMBER i=1 TILL i<4, i++) { IF (values[i]<result) { result=values[i]. } }"),
        ("negative_count","count negative entries",5,lambda xs:sum(x<0 for x in xs),"NUMBER result=0.\nLOOP (NUMBER i=0 TILL i<5, i++) { IF (values[i]<0) { result+=1. } }"),
        ("odd_sum","sum odd entries",5,lambda xs:sum(x for x in xs if x%2),"NUMBER result=0.\nLOOP (NUMBER i=0 TILL i<5, i++) { IF (values[i]%2!=0) { result+=values[i]. } }"),
        ("first_last_difference","first minus last entry",4,lambda xs:xs[0]-xs[-1],"NUMBER result=values[0]-values[3]."),
        ("adjacent_difference_sum","sum absolute adjacent differences",4,lambda xs:sum(abs(xs[i]-xs[i-1]) for i in range(1,4)),"IMPORT math.\nNUMBER result=0.\nLOOP (NUMBER i=1 TILL i<4, i++) { result+=math.ABS(values[i]-values[i-1]). }"),
        ("above_average_count","count entries above their average",4,lambda xs:sum(x>sum(xs)/4 for x in xs),"NUMBER avg=arrays.SUM(values)/4.\nNUMBER result=0.\nLOOP (NUMBER i=0 TILL i<4, i++) { IF (values[i]>avg) { result+=1. } }"),
        ("alternating_sum","v0-v1+v2-v3+v4",5,lambda xs:xs[0]-xs[1]+xs[2]-xs[3]+xs[4],"NUMBER result=values[0]-values[1]+values[2]-values[3]+values[4]."),
        ("square_sum","sum squares of four entries",4,lambda xs:sum(x*x for x in xs),"NUMBER result=0.\nLOOP (NUMBER i=0 TILL i<4, i++) { result+=values[i]*values[i]. }"),
        ("zero_count","count zero entries",5,lambda xs:sum(x==0 for x in xs),"NUMBER result=0.\nLOOP (NUMBER i=0 TILL i<5, i++) { IF (values[i]==0) { result+=1. } }"),
        ("range_five","maximum minus minimum",5,lambda xs:max(xs)-min(xs),"NUMBER hi=values[0]. NUMBER lo=values[0].\nLOOP (NUMBER i=1 TILL i<5, i++) { IF (values[i]>hi) { hi=values[i]. } IF (values[i]<lo) { lo=values[i]. } }\nNUMBER result=hi-lo."),
        ("pair_products","v0*v1+v2*v3",4,lambda xs:xs[0]*xs[1]+xs[2]*xs[3],"NUMBER result=values[0]*values[1]+values[2]*values[3]."),
        ("bounded_sum","sum entries between -2 and 5 inclusive",5,lambda xs:sum(x for x in xs if -2<=x<=5),"NUMBER result=0.\nLOOP (NUMBER i=0 TILL i<5, i++) { IF (values[i]>=-2 AND values[i]<=5) { result+=values[i]. } }"),
        ("weighted_positions","sum (i+1)*values[i] for four entries",4,lambda xs:sum((i+1)*x for i,x in enumerate(xs)),"NUMBER result=0.\nLOOP (NUMBER i=0 TILL i<4, i++) { result+=(i+1)*values[i]. }"),
    ]
    for name,description,width,solver,body in array_specs:
        names=[chr(97+i) for i in range(width)]; source=split_numbers(names)+"IMPORT arrays.\nNUMBER[] values=["+",".join(names)+"].\n"+body+"\nDISPLAYNL(result)."
        samples=[[1,2,3,4,5],[-2,1,5,1,-4],[4,-1,2,-3,8],[0,0,0,0,0],[10,2,-5,7,1]]
        values=[xs[:width] for xs in samples]
        emit("AR",ar,f"Read {width} pipe-delimited numbers into an array and {description}; print the result.",source,[("|".join(map(str,x)),solver(x)) for x in values],name,"array_algorithm",f"eval_ar>{name}",[name],[r"NUMBER\[\]"])

    st=FAMILIES[5]
    str_specs=[
        ("labeled_upper_reverse","uppercase, reverse, and prefix R=",'SENTENCE transformed=strings.REVERSE(strings.UPPER(text)).\nDISPLAYNL(strings.CONCAT("R=",transformed)).',lambda s:"R="+s.upper()[::-1]),
        ("lower_length","lowercase text followed by its length separated by colon",f'DISPLAYNL({concat("strings.LOWER(text)","\":\"","strings.TO_SENTENCE(strings.LENGTH(text))")}).',lambda s:f"{s.lower()}:{float(len(s)):.1f}"),
        ("dual_replace","replace a with @ and e with 3",'DISPLAYNL(strings.REPLACE(strings.REPLACE(text,"a","@"),"e","3")).',lambda s:s.replace("a","@").replace("e","3")),
        ("first_last_chars","print first and last characters separated by dash",f'DISPLAYNL({concat("strings.CHARAT(text,0)","\"-\"","strings.CHARAT(text,strings.LENGTH(text)-1)")}).',lambda s:f"{s[0]}-{s[-1]}"),
        ("count_go","print how many lowercase go substrings occur",'SENTENCE normalized=strings.LOWER(text).\nDISPLAYNL(strings.COUNT(normalized,"go")).',lambda s:s.lower().count("go")),
        ("labeled_trim_reverse","trim spaces, reverse, and prefix T=",'SENTENCE cleaned=strings.TRIM(text," ").\nDISPLAYNL(strings.CONCAT("T=",strings.REVERSE(cleaned))).',lambda s:"T="+s.strip(" ")[::-1]),
        ("starts_pre","print YES if lowercase text starts with pre",'SENTENCE normalized=strings.LOWER(text).\nIF (strings.STARTSWITH(normalized,"pre")) { DISPLAYNL("YES"). } ELSE { DISPLAYNL("NO"). }',lambda s:"YES" if s.lower().startswith("pre") else "NO"),
        ("ends_ing","print YES if lowercase text ends with ing",'SENTENCE normalized=strings.LOWER(text).\nIF (strings.ENDSWITH(normalized,"ing")) { DISPLAYNL("YES"). } ELSE { DISPLAYNL("NO"). }',lambda s:"YES" if s.lower().endswith("ing") else "NO"),
        ("count_a_e","print count(a)+count(e)",'DISPLAYNL(strings.COUNT(strings.LOWER(text),"a")+strings.COUNT(strings.LOWER(text),"e")).',lambda s:s.lower().count("a")+s.lower().count("e")),
        ("labeled_repeat_reverse","reverse text, repeat twice, and prefix D=",'SENTENCE doubled=strings.REPEAT(strings.REVERSE(text),2).\nDISPLAYNL(strings.CONCAT("D=",doubled)).',lambda s:"D="+s[::-1]*2),
        ("middle_char","print character at floor(length/2)",'DISPLAYNL(strings.CHARAT(text,math.FLOOR(strings.LENGTH(text)/2))).',lambda s:s[math.floor(len(s)/2)],True),
        ("replace_spaces","replace spaces with underscores",'SENTENCE changed=strings.REPLACE(text," ","_"). DISPLAYNL(strings.CONCAT("",changed)).',lambda s:s.replace(" ","_")),
        ("length_band","print SHORT below 5, MEDIUM through 10, LONG otherwise",'NUMBER n=strings.LENGTH(text). IF (n<5) { DISPLAYNL("SHORT"). } ELSEIF (n<=10) { DISPLAYNL("MEDIUM"). } ELSE { DISPLAYNL("LONG"). }',lambda s:"SHORT" if len(s)<5 else "MEDIUM" if len(s)<=10 else "LONG"),
        ("palindrome","print PAL if text equals its reverse",'IF (strings.EQUALS(text,strings.REVERSE(text))) { DISPLAYNL("PAL"). } ELSE { DISPLAYNL("NO"). }',lambda s:"PAL" if s==s[::-1] else "NO"),
        ("first_third_last","print first, third, and last characters separated by colons",f'DISPLAYNL({concat("strings.CHARAT(text,0)","\":\"","strings.CHARAT(text,2)","\":\"","strings.CHARAT(text,strings.LENGTH(text)-1)")}).',lambda s:f"{s[0]}:{s[2]}:{s[-1]}",False),
        ("case_swap_proxy","uppercase lowercase text, otherwise lowercase mixed text",'IF (strings.EQUALS(text,strings.LOWER(text))) { DISPLAYNL(strings.UPPER(text)). } ELSE { DISPLAYNL(strings.LOWER(text)). }',lambda s:s.upper() if s==s.lower() else s.lower()),
    ]
    vals=["GoCode","alpha beta","PREview","testing","level"]
    for spec in str_specs:
        name,description,body,solver,*flags=spec
        imports="IMPORT strings.\n"+("IMPORT math.\n" if flags and flags[0] else "")
        source=imports+"SENTENCE text.\nINPUT(text).\n"+body
        emit("ST",st,f"Read one sentence and {description}; print only the result.",source,[(v,solver(v)) for v in vals],name,"string_algorithm",f"eval_st>{name}",[name])

    io=FAMILIES[6]
    io_specs=[
        ("numeric_triple_tag",lambda a,b:f"{a}#{float(b)*3:.1f}",lambda: f'DISPLAYNL({concat("first","\"#\"","strings.TO_SENTENCE(strings.TO_NUMBER(second)*3)")}).'),
        ("length_difference",lambda a,b:float(len(a)-len(b)),lambda:'NUMBER leftLength=strings.LENGTH(first).\nNUMBER rightLength=strings.LENGTH(second).\nNUMBER difference=leftLength-rightLength.\nDISPLAYNL(difference).'),
        ("lower_upper_tilde",lambda a,b:f"PAIR={a.lower()}~{b.upper()}",lambda:f'DISPLAYNL({concat("\"PAIR=\"","strings.LOWER(first)","\"~\"","strings.UPPER(second)")}).'),
        ("double_reverse",lambda a,b:f"REV={b[::-1]}::{a[::-1]}",lambda:f'DISPLAYNL({concat("\"REV=\"","strings.REVERSE(second)","\"::\"","strings.REVERSE(first)")}).'),
        ("length_square_sum",lambda a,b:float(len(a)*len(a)+len(b)*len(b)),lambda:'NUMBER total=strings.LENGTH(first)*strings.LENGTH(first)+strings.LENGTH(second)*strings.LENGTH(second).\nDISPLAYNL(total).'),
        ("lower_labels",lambda a,b:f"left:{a.lower()}\nright:{b.lower()}",lambda:'SENTENCE leftValue=strings.CONCAT("left:",strings.LOWER(first)).\nSENTENCE rightValue=strings.CONCAT("right:",strings.LOWER(second)).\nDISPLAYNL(leftValue).\nDISPLAYNL(rightValue).'),
        ("repeat_plus_one",lambda a,b:"R="+a*(int(b)+1),lambda:'NUMBER count=strings.TO_NUMBER(second)+1.\nSENTENCE repeated=strings.REPEAT(first,count).\nDISPLAYNL(strings.CONCAT("R=",repeated)).'),
        ("decrement_with_unit",lambda a,b:f"{float(a)-1:.1f}:{b}",lambda:f'DISPLAYNL({concat("strings.TO_SENTENCE(strings.TO_NUMBER(first)-1)","\":\"","second")}).'),
        ("braced_fields",lambda a,b:f"{{{a}}}({b})",lambda:'SENTENCE left=strings.CONCAT("{",first).\nSENTENCE middle=strings.CONCAT(left,"}(").\nSENTENCE right=strings.CONCAT(middle,second).\nDISPLAYNL(strings.CONCAT(right,")")).'),
        ("lower_pipe_upper",lambda a,b:f"MIX={a.lower()}|{b.upper()}",lambda:f'DISPLAYNL({concat("\"MIX=\"","strings.LOWER(first)","\"|\"","strings.UPPER(second)")}).'),
        ("reverse_order_lines",lambda a,b:f"{b}\n{a}",lambda:'DISPLAYNL(second).\nDISPLAYNL(first).'),
        ("combined_length_label",lambda a,b:f"LEN={float(len(a)+len(b)):.1f}",lambda:f'DISPLAYNL({concat("\"LEN=\"","strings.TO_SENTENCE(strings.LENGTH(first)+strings.LENGTH(second))")}).'),
        ("first_chars",lambda a,b:f"{a[0]}{b[0]}",lambda:f'DISPLAYNL({concat("strings.CHARAT(first,0)","strings.CHARAT(second,0)")}).'),
        ("last_chars",lambda a,b:f"{a[-1]}:{b[-1]}",lambda:f'DISPLAYNL({concat("strings.CHARAT(first,strings.LENGTH(first)-1)","\":\"","strings.CHARAT(second,strings.LENGTH(second)-1)")}).'),
        ("numeric_sum_label",lambda a,b:f"SUM={float(a)+float(b):.1f}",lambda:f'DISPLAYNL({concat("\"SUM=\"","strings.TO_SENTENCE(strings.TO_NUMBER(first)+strings.TO_NUMBER(second))")}).'),
        ("repeat_separator",lambda a,b:f"{a}::{b}::{a}",lambda:f'DISPLAYNL({concat("first","\"::\"","second","\"::\"","first")}).'),
    ]
    values=[("A","B"),("mass","unit"),("zero","nil"),("hello","world"),("two words","ok")]
    for name,solver,bodyfn in io_specs:
        filtered=values
        if name=="repeat_plus_one": filtered=[("a","3"),("Go","2"),("x","1"),("z","0"),("ab","4")]
        if name=="numeric_sum_label": filtered=[("2","3"),("1","4"),("0","2"),("5","1"),("3","2")]
        if name=="numeric_triple_tag": filtered=[("A","2"),("mass","3.5"),("zero","0"),("neg","-2"),("x","10")]
        if name=="decrement_with_unit": filtered=[("1","kg"),("0","m"),("-2","C"),("3.5","s"),("10","items")]
        if name in {"first_chars","last_chars"}: filtered=[("A","B"),("red","blue"),("hello","world"),("x","z"),("two words","ok")]
        io_prompts={
            "numeric_triple_tag":"Accept a text tag followed by a numeric field, separated by |; emit tag#(three times the number).",
            "length_difference":"Given left|right text fields, emit length(left)-length(right).",
            "lower_upper_tilde":"Transform left|right into PAIR=lower(left)~upper(right).",
            "double_reverse":"For left|right, emit REV= followed by reversed right, ::, then reversed left.",
            "length_square_sum":"Given two text fields separated by |, emit the sum of their squared lengths.",
            "lower_labels":"Parse left|right and emit two lines labeled left: and right: after lowercasing each value.",
            "repeat_plus_one":"Treat the second field as a count; prefix R= and repeat the first field count+1 times.",
            "decrement_with_unit":"Parse number|unit, subtract one from the number, and emit result:unit.",
            "braced_fields":"Render left|right as {left}(right).",
            "lower_pipe_upper":"Emit MIX=lower(left)|upper(right) for two pipe-delimited text fields.",
            "reverse_order_lines":"For first|second, emit second on line one and first on line two.",
            "combined_length_label":"Emit LEN= followed by the combined length of two pipe-delimited fields.",
            "first_chars":"Emit the first character from each of two nonempty fields with no separator.",
            "last_chars":"Emit last(left):last(right) for two nonempty pipe-delimited fields.",
            "numeric_sum_label":"Parse two numeric fields and emit SUM= followed by their sum.",
            "repeat_separator":"Render left|right as left::right::left.",
        }
        source=split_sentences(["first","second"])+bodyfn()
        emit("IO",io,io_prompts[name],source,[(f"{a}|{b}",solver(a,b)) for a,b in filtered],name,"formatted_io",f"eval_io>{name}",[name])

    cp=FAMILIES[7]
    cp_specs=[
        ("proper_divisor_class", "sum proper divisors and print PERFECT if the sum equals n", "NUMBER total=0. LOOP (NUMBER i=1 TILL i<n, i++) { IF (n%i==0) { total+=i. } } IF (total==n) { DISPLAYNL(\"PERFECT\"). } ELSE { DISPLAYNL(\"OTHER\"). }", lambda n:"PERFECT" if sum(i for i in range(1,n) if n%i==0)==n else "OTHER"),
        ("prime_proxy", "count divisors and print PRIME when count is two", "NUMBER count=0. LOOP (NUMBER i=1 TILL i<=n, i++) { IF (n%i==0) { count+=1. } } IF (count==2) { DISPLAYNL(\"PRIME\"). } ELSE { DISPLAYNL(\"OTHER\"). }", lambda n:"PRIME" if sum(n%i==0 for i in range(1,n+1))==2 else "OTHER"),
        ("square_sum_parity", "sum squares through n then print EVEN or ODD", "NUMBER total=0. LOOP (NUMBER i=1 TILL i<=n, i++) { total+=i*i. } IF (total%2==0) { DISPLAYNL(\"EVEN\"). } ELSE { DISPLAYNL(\"ODD\"). }", lambda n:"EVEN" if sum(i*i for i in range(1,n+1))%2==0 else "ODD"),
        ("filtered_square_sum", "sum squares divisible by 3", "NUMBER total=0. LOOP (NUMBER i=1 TILL i<=n, i++) { IF (i%3==0) { total+=i*i. } } DISPLAYNL(total).", lambda n:sum(i*i for i in range(1,n+1) if i%3==0)),
        ("divisor_parity", "count divisors and print EVENCOUNT or ODDCOUNT", "NUMBER count=0. LOOP (NUMBER i=1 TILL i<=n, i++) { IF (n%i==0) { count+=1. } } IF (count%2==0) { DISPLAYNL(\"EVENCOUNT\"). } ELSE { DISPLAYNL(\"ODDCOUNT\"). }", lambda n:"EVENCOUNT" if sum(n%i==0 for i in range(1,n+1))%2==0 else "ODDCOUNT"),
        ("triangular_threshold", "compute n*(n+1)/2 and print OVER if above 20", "NUMBER total=n*(n+1)/2. IF (total>20) { DISPLAYNL(\"OVER\"). } ELSE { DISPLAYNL(\"UNDER\"). }", lambda n:"OVER" if n*(n+1)/2>20 else "UNDER"),
        ("odd_cube_sum", "sum cubes of odd values through n", "NUMBER total=0. LOOP (NUMBER i=1 TILL i<=n, i++) { IF (i%2!=0) { total+=i*i*i. } } DISPLAYNL(total).", lambda n:sum(i**3 for i in range(1,n+1) if i%2)),
        ("multiple_difference", "sum multiples of 2 minus multiples of 3", "NUMBER total=0. LOOP (NUMBER i=1 TILL i<=n, i++) { IF (i%2==0) { total+=i. } IF (i%3==0) { total-=i. } } DISPLAYNL(total).", lambda n:sum((i if i%2==0 else 0)-(i if i%3==0 else 0) for i in range(1,n+1))),
        ("even_product_class", "multiply positive even values through n and print LARGE when at least 1000", "NUMBER product=1. LOOP (NUMBER i=1 TILL i<=n, i++) { IF (i%2==0) { product*=i. } } IF (product>=1000) { DISPLAYNL(\"LARGE\"). } ELSE { DISPLAYNL(\"SMALL\"). }", lambda n:"LARGE" if math.prod(range(2,n+1,2))>=1000 else "SMALL"),
        ("sum_function_class", "use a square-plus-one function in a loop, then classify total modulo 3", "FUNCTION term(NUMBER x) { RETURN x*x+1. } RETURNS NUMBER. NUMBER total=0. LOOP (NUMBER i=1 TILL i<=n, i++) { total+=term(i). } IF (total%3==0) { DISPLAYNL(\"THREE\"). } ELSE { DISPLAYNL(\"OTHER\"). }", lambda n:"THREE" if sum(i*i+1 for i in range(1,n+1))%3==0 else "OTHER"),
        ("polynomial_sum_parity", "sum i*(i+2) through n and print its parity", "NUMBER total=0. LOOP (NUMBER i=1 TILL i<=n, i++) { total+=i*(i+2). } IF (total%2==0) { DISPLAYNL(\"EVEN\"). } ELSE { DISPLAYNL(\"ODD\"). }", lambda n:"EVEN" if sum(i*(i+2) for i in range(1,n+1))%2==0 else "ODD"),
        ("alternating_threshold", "alternately add and subtract 1..n then compare with zero", "NUMBER total=0. LOOP (NUMBER i=1 TILL i<=n, i++) { IF (i%2==0) { total-=i. } ELSE { total+=i. } } IF (total>=0) { DISPLAYNL(\"NONNEG\"). } ELSE { DISPLAYNL(\"NEG\"). }", lambda n:"NONNEG" if sum(i if i%2 else -i for i in range(1,n+1))>=0 else "NEG"),
        ("count_two_or_five", "count values divisible by exactly one of 2 and 5", "NUMBER count=0. LOOP (NUMBER i=1 TILL i<=n, i++) { IF ((i%2==0 AND i%5!=0) OR (i%2!=0 AND i%5==0)) { count+=1. } } DISPLAYNL(count).", lambda n:sum((i%2==0)^(i%5==0) for i in range(1,n+1))),
        ("remainder_accumulation", "sum 12 modulo i for i=1..n", "NUMBER total=0. LOOP (NUMBER i=1 TILL i<=n, i++) { total+=12%i. } DISPLAYNL(total).", lambda n:sum(12%i for i in range(1,n+1))),
        ("nested_small_products", "sum i*j for 1<=j<=i<=n", "NUMBER total=0. LOOP (NUMBER i=1 TILL i<=n, i++) { LOOP (NUMBER j=1 TILL j<=i, j++) { total+=i*j. } } DISPLAYNL(total).", lambda n:sum(i*j for i in range(1,n+1) for j in range(1,i+1))),
        ("range_prime_count", "count primes from 2 through n using nested divisor counts", "NUMBER primes=0. LOOP (NUMBER x=2 TILL x<=n, x++) { NUMBER divisors=0. LOOP (NUMBER i=1 TILL i<=x, i++) { IF (x%i==0) { divisors+=1. } } IF (divisors==2) { primes+=1. } } DISPLAYNL(primes).", lambda n:sum(sum(x%i==0 for i in range(1,x+1))==2 for x in range(2,n+1))),
    ]
    for name,description,body,solver in cp_specs:
        source="NUMBER n.\nINPUT(n).\n"+body; ns=[1,2,4,6,10]
        required=[] if name=="triangular_threshold" else [r"LOOP\s*\("]
        emit("CP",cp,f"Read positive n, {description}, and print the requested result.",source,[(str(n),solver(n)) for n in ns],name,"composed_algorithm",f"eval_cp>{name}",[name],required)

    if counters != {family:16 for family in FAMILIES}:
        raise AssertionError(counters)
    return tasks,refs,tests


def build_regression() -> list[dict[str, Any]]:
    items: list[tuple[str,str,str]]=[]
    trace=[
        ("python_arithmetic","What does Python print for 7 + 3 * 4? Reply only with the number.","19"),
        ("python_slice","What does Python 'abcdefgh'[2:6] evaluate to? Reply only with the text.","cdef"),
        ("python_negative_index","For Python list [2,4,6], what is items[-1]? Reply only with the number.","6"),
        ("python_floor_div","What is 17 // 5 in Python? Reply only with the number.","3"),
        ("python_bool","What does bool([0]) evaluate to in Python? Reply TRUE or FALSE only.","TRUE"),
        ("js_strict_equal","In JavaScript, does 3 === '3' evaluate true? Reply TRUE or FALSE only.","FALSE"),
        ("loop_sum","A loop sums integers 2 through 6 inclusive. Reply only with the total.","20"),
        ("loop_product","A loop multiplies integers 1 through 4 inclusive. Reply only with the product.","24"),
        ("precedence","Evaluate 10 - 2 * 3. Reply only with the number.","4"),
        ("parentheses","Evaluate (10 - 2) * 3. Reply only with the number.","24"),
        ("array_index","For zero-based array [9,7,5,3], what is index 2? Reply only with the number.","5"),
        ("string_len","What is the length of 'adapter'? Reply only with the number.","7"),
        ("modulo","What is 29 modulo 6? Reply only with the number.","5"),
        ("binary","Convert binary 1010 to decimal. Reply only with the number.","10"),
        ("boolean_and","Evaluate TRUE AND FALSE. Reply TRUE or FALSE only.","FALSE"),
        ("min","What is min(8,-2,5)? Reply only with the number.","-2"),
        ("max","What is max(8,-2,5)? Reply only with the number.","8"),
        ("power","What is 3 squared? Reply only with the number.","9"),
        ("list_count","How many elements are in [1,1,2,3,5]? Reply only with the number.","5"),
        ("range_count","How many integers are in 4 through 9 inclusive? Reply only with the number.","6"),
        ("dict_lookup","Given mapping a:2,b:5, what is the value for b? Reply only with the number.","5"),
        ("string_concat","Concatenate 'micro' and 'service' without a separator. Reply only with the result.","microservice"),
    ]
    instruction=[
        ("upper","Convert 'stable system' to uppercase. Reply only with the result.","STABLE SYSTEM"),
        ("lower","Convert 'Mixed CASE' to lowercase. Reply only with the result.","mixed case"),
        ("reverse","Reverse characters in 'drawer'. Reply only with the result.","reward"),
        ("sort","Sort 8,1,6,3 ascending. Reply as comma-separated numbers without spaces.","1,3,6,8"),
        ("replace","Replace every slash in 'a/b/c' with a dash. Reply only with the result.","a-b-c"),
        ("first_word","Return the first word of 'careful tests matter'. Reply only with that word.","careful"),
        ("last_word","Return the last word of 'models need evidence'. Reply only with that word.","evidence"),
        ("count_letters","How many letters are in 'validation'? Reply only with the number.","10"),
        ("dedupe","Remove repeated adjacent characters from 'bookkeeper'. Reply only with the result.","bokeper"),
        ("join","Join red,green,blue with vertical bars. Reply only with the result.","red|green|blue"),
        ("prefix","Return the first three characters of 'compiler'. Reply only with the result.","com"),
        ("suffix","Return the last four characters of 'learning'. Reply only with the result.","ning"),
        ("title","Capitalize the first letter of 'reliable'. Reply only with the result.","Reliable"),
        ("count_words","How many words are in 'small models learn patterns'? Reply only with the number.","4"),
        ("remove_spaces","Remove spaces from 'a b c d'. Reply only with the result.","abcd"),
        ("repeat","Repeat 'go' three times with no separator. Reply only with the result.","gogogo"),
        ("numeric_order","Order -1,5,0 ascending. Reply exactly as -1,0,5","-1,0,5"),
        ("extract_digits","Return only the digits from 'a1b2c3'. Reply only with the result.","123"),
        ("swap_case","Swap case in 'AbC'. Reply only with the result.","aBc"),
        ("colon_join","Join key and value with a colon. Reply exactly key:value","key:value"),
        ("boolean_format","Write the lowercase JSON boolean for false. Reply only with the token.","false"),
    ]
    concept=[
        ("lifo","Which data structure is LIFO? Reply with one lowercase word.","stack"),
        ("fifo","Which data structure is FIFO? Reply with one lowercase word.","queue"),
        ("http_get","Which HTTP method retrieves a resource? Reply with the uppercase method.","GET"),
        ("http_create","Which HTTP method conventionally creates a resource? Reply with the uppercase method.","POST"),
        ("sql_filter","Which SQL keyword filters rows? Reply with the uppercase keyword.","WHERE"),
        ("sql_sort","Which SQL clause sorts query results? Reply exactly ORDER BY","ORDER BY"),
        ("git_commit","Which Git subcommand records staged changes? Reply only with the subcommand.","commit"),
        ("git_branch","Which Git subcommand lists branches? Reply only with the subcommand.","branch"),
        ("hash_lookup","Typical average hash-table lookup complexity? Reply only with Big-O notation.","O(1)"),
        ("binary_search","Binary-search time complexity? Reply only with Big-O notation.","O(log n)"),
        ("json_null","Which JSON literal represents no value? Reply only with the literal.","null"),
        ("json_array","Which characters delimit a JSON array? Reply exactly []","[]"),
        ("bit_values","How many possible values does one bit have? Reply only with the number.","2"),
        ("byte_bits","How many bits are in a conventional byte? Reply only with the number.","8"),
        ("recursion_base","What kind of case stops recursion? Reply with two lowercase words.","base case"),
        ("immutable","Which Python built-in sequence is immutable: list or tuple? Reply one lowercase word.","tuple"),
        ("set_unique","Which common collection stores unique elements: list or set? Reply one lowercase word.","set"),
        ("tcp","Which transport protocol is connection-oriented: TCP or UDP? Reply uppercase.","TCP"),
        ("boolean_values","List JSON boolean literals exactly as true,false","true,false"),
        ("merge_sort","Typical merge-sort time complexity? Reply only with Big-O notation.","O(n log n)"),
        ("primary_key","What database key uniquely identifies a row? Reply with two lowercase words.","primary key"),
    ]
    for category, rows in (("trace",trace),("instruction",instruction),("concept",concept)):
        for lineage,prompt,expected in rows: items.append((category+"_"+lineage,prompt,expected))
    if len(items)!=64: raise AssertionError(len(items))
    return [{"task_id":f"P2B-REG-{i:03d}","split":"phase2b_general_regression","category":lineage.split("_",1)[0],"template_lineage":f"p2b-reg-{lineage}","prompt":prompt,"expected":expected} for i,(lineage,prompt,expected) in enumerate(items,1)]


def write_new(path: Path, value: Any) -> None:
    if path.exists(): raise FileExistsError(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--root",type=Path,default=Path(".")); args=parser.parse_args()
    train,train_refs,train_tests=build_training(); evaluation,eval_refs,eval_tests=build_evaluation()
    if len(train)!=200 or len(evaluation)!=128: raise AssertionError((len(train),len(evaluation)))
    examples=[]
    for task in train:
        examples.append({
            "example_id":task["task_id"],"split":"phase2b_train","family":task["family"],"prompt":task["prompt"],
            "target":train_refs[task["task_id"]],"algorithmic_structure":task["algorithmic_structure"],
            "control_flow":task["control_flow"],"template_lineage":task["template_lineage"],
            "structural_signature":task["structural_signature"],"ast_proxy_signature":task["ast_proxy_signature"],
            "semantic_operations":task["semantic_operations"],
        })
    root=args.root
    write_new(root/"data/phase2b/training_examples.json",examples)
    write_new(root/"data/phase2b/training_hidden_tests.json",train_tests)
    write_new(root/"benchmark/phase2b/confirmatory_tasks.json",evaluation)
    write_new(root/"benchmark/phase2b/confirmatory_references.json",eval_refs)
    write_new(root/"benchmark/phase2b/confirmatory_hidden_tests.json",eval_tests)
    write_new(root/"benchmark/phase2b/general_regression.json",build_regression())
    print(json.dumps({"training_examples":len(train),"confirmatory_tasks":len(evaluation),"general_regression":64},indent=2))


if __name__=="__main__": main()
