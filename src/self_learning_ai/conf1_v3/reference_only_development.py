"""Predetermined disposable RO fixture plan, not a scientific materializer.

All selected positive numeric atoms come from the previously serialized seed
schedule. Required decoder/indicator/loop terminals are the unchanged frozen
generic grammar, not newly selected isolated RO constant witnesses.
"""
from .reference_only_overlap import witness_schedule, digest, FIELD, SCOPE
from .projection_grammar import derive_projection_plan, render_development
from .requirements import frozen_metadata
from .attribute_reference import reference_output


def fixture_plan():
    scheduled = witness_schedule()
    v = {r["label"]: r["literal"] for r in scheduled["non_boundary"]}
    numeric = [v[f"CASE_{i}_NUMERIC"] for i in range(5)]
    arrays = ["|".join(("-" if j % 2 else "") + v[f"CASE_{i}_ARRAY_{j}"] for j in range(4)) for i in range(5)]
    definitions = frozen_metadata()["predicate_definitions"]
    fixtures = []
    for family, structure, group in (
        ("numeric_iteration", "PER_ITEM", "TRAINING"),
        ("array_reduction", "PER_ITEM", "PRIMARY_EVALUATION"),
        ("numeric_iteration", "PREFIX", "PRIMITIVE_SANITY"),
        ("numeric_iteration", "TWO_PASS", "STRUCTURAL_TRANSFER"),
    ):
        pid = f"DEVELOPMENT_ONLY_RO_{family.upper()}_{structure}_{group}"
        decl = dict(program_id=pid, family=family,
                    role_bindings=dict(P=definitions[family][0]["name"], Q=definitions[family][1]["name"]),
                    structure=structure, treatment="EXPRESSION", reverse=False,
                    offset=int(v["ARRAY_OFFSET"] if family == "array_reduction" else v["INITIAL_OFFSET"]),
                    repeat=1, expression="values[i]" if family == "array_reduction" else "i", unused=False)
        prospective = derive_projection_plan(decl)
        base = render_development(decl, "ro")
        inputs = arrays if family == "array_reduction" else numeric
        expected = [str(reference_output(decl, raw)) for raw in inputs]
        a, b, c = v["ATOM_A"], v["ATOM_B"], v["ATOM_C"]
        safe = f"(({a}+{b})*{c}-{a})"
        guard = f"({v['FALSE_GUARD_LEFT']}>{v['FALSE_GUARD_RIGHT']})"
        body = f"NUMBER roBody={v['BODY_CONSTANT']}."
        nested = f"IF ({guard}) {{ NUMBER roNested={v['NESTED_BODY']}. }}"
        declarations = {
            "BASE": "",
            "PURE_UNUSED": f"NUMBER roUnused={v['PU_CONSTANT']}.",
            "ALPHA_UNUSED": f"NUMBER roUnusedAlias={v['PU_CONSTANT']}.",
            "NESTED_CONSTANT": f"NUMBER roUnused={safe}.",
            "SAME_KEY_UNUSED": f"NUMBER roUnused={decl['offset']}.",
            "PURE_UNUSED_ZERO": "NUMBER roUnused=0.",
            "PURE_UNUSED_MAX": "NUMBER roUnused=2147483647.",
            "PURE_UNUSED_OVERFLOW": "NUMBER roUnused=2147483648.",
            "CONSTANT_FALSE": f"IF ({guard}) {{ {body} }}",
            "NESTED_FALSE": f"IF ({guard}) {{ {body} {nested} }}",
            "FALSE_REQUIRED_ACCUMULATOR_EXTRA": f"IF ({guard}) {{ rototal+={v['EXTRA_WRITE']}. }}",
            "UNSAFE_MODULO_ZERO": f"NUMBER roUnused={v['PU_CONSTANT']}%0.",
            "UNSUPPORTED_MODULO": f"NUMBER roUnused={v['PU_CONSTANT']}%{v['UNSUPPORTED_MODULUS']}.",
            "OUT_OF_BOUND_INTERMEDIATE": f"NUMBER roUnused=(2147483647+{a})-{a}.",
            "EXTRA_WRITE": f"NUMBER roUnused={v['PU_CONSTANT']}. roUnused={v['EXTRA_WRITE']}.",
            "FRESH_LATER_READ": f"NUMBER roUnused={v['PU_CONSTANT']}. NUMBER roBorrow=roUnused.",
            "UNMATCHED_LIVE_EQUIVALENT": f"rototal+=({v['LIVE_UNMATCHED']}-{v['LIVE_UNMATCHED']}).",
            "DISPLAY_ANCESTRY": f"NUMBER roUnused={v['PU_CONSTANT']}. rototal+=roUnused.",
            "UNSUPPORTED_BOOLEAN_GUARD": f"IF (false) {{ {body} }}",
            "UNSAFE_GUARD": f"IF ({v['ATOM_A']}%0>{v['ATOM_B']}) {{ {body} }}",
            "INPUT_DEPENDENT_GUARD": f"IF ({'rofield0' if family == 'array_reduction' else 'ron'}>{v['COMPARISON_OTHER']}) {{ {body} }}",
            "FORBIDDEN_BODY_ARRAY": f"IF ({guard}) {{ NUMBER[] roBodyArray=[{a},{b},{c},{v['ATOM_D']}]. }}",
            "FORBIDDEN_BODY_DISPLAY": f"IF ({guard}) {{ DISPLAYNL({a}). }}",
            "UNKNOWN_BODY": f"IF ({guard}) {{ roUnknown({a}). }}",
            "FORBIDDEN_BODY_INPUT": f"IF ({guard}) {{ INPUT({'rofield0' if family == 'array_reduction' else 'ron'}). }}",
            "BODY_BINDING_ESCAPE": f"IF ({guard}) {{ {body} }} NUMBER roEscaped=roBody.",
        }
        if family == "numeric_iteration":
            declarations["INPUT_DEPENDENT_INITIALIZER"] = "NUMBER roUnused=ron."
            declarations["FORBIDDEN_BODY_LOOP"] = f"IF ({guard}) {{ LOOP (NUMBER roForbiddenCursor=1 TILL roForbiddenCursor<=ron, roForbiddenCursor++) {{ NUMBER roLoopLocal={a}. }} }}"
        else:
            declarations["DECODER_INITIALIZER"] = "NUMBER roUnused=strings.TO_NUMBER(rofields[0])."
            declarations["ARRAY_INDEX_INITIALIZER"] = "NUMBER roUnused=rovalues[0]."
        for case, extra in declarations.items():
            source = base.replace("DISPLAYNL(rototal).", extra + " DISPLAYNL(rototal).") if extra else base
            fixtures.append(dict(scope=SCOPE, development_case_id=pid + "_" + case, program_id=pid,
                                 program_group=group, variant=case, source=source, reference_source=base,
                                 prospective=prospective, raw_inputs=inputs, expected_outputs=expected,
                                 semantic_constant_witness=safe, comparison_witness=guard))
        # This adversary is placed within a real loop, not mislabeled top-level.
        source = base.replace("{ ", "{ NUMBER roLoopLocal=" + v["PU_CONSTANT"] + ". ", 1)
        fixtures.append(dict(scope=SCOPE, development_case_id=pid + "_LOOP_LOCAL", program_id=pid,
                             program_group=group, variant="LOOP_LOCAL", source=source, reference_source=base,
                             prospective=prospective, raw_inputs=inputs, expected_outputs=expected,
                             semantic_constant_witness=safe, comparison_witness=guard))
    return fixtures


def executable_overlap_inventory(fixtures):
    rows = []
    for fixture in fixtures:
        case = fixture["development_case_id"]
        values = [("development_case_id", case), ("program_id", fixture["program_id"]),
                  ("sources", fixture["source"]), ("reference_sources", fixture["reference_source"]),
                  ("expressions", fixture["semantic_constant_witness"]),
                  ("expressions", fixture["comparison_witness"])]
        values += [("raw_inputs", v) for v in fixture["raw_inputs"]]
        values += [("expected_outputs", v) for v in fixture["expected_outputs"]]
        for i, (field, value) in enumerate(values):
            rows.append(dict(scope=SCOPE, implementation_test="REFERENCE_ONLY", field=field,
                             path=f"fixtures/{case}/{field}/{i}", value=value, sha256_utf8=digest(value),
                             boundary_rule=None, development_case_id=case))
    return rows
