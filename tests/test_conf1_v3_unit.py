"""Disposable core development tests; NOT independent scientific validation."""
import hashlib
import json
from dataclasses import replace

import pytest

import conf1_core_development_inputs as dev

# This check runs before importing any classifier, constructing any contract or
# executing any case. It never opens the historical expected-label artifact.
OVERLAP_PROOF = dev.assert_zero_historical_overlap()

from self_learning_ai.conf1_v3.contract_ir import graph_record, keys_from_ir
from self_learning_ai.conf1_v3.contracts import (
    CoverageContractV3, DOMAINS, _predicate_ops, all_contracts,
    input_domain_classes, v35_expected_row_ids,
)
from self_learning_ai.conf1_v3.core_ir import compile_program, execute
from self_learning_ai.conf1_v3.coverage import (
    CoverageEngine, PinnedCompilerOracle, atomic_coverage, behavioral_activity,
    closed_equivalence, input_domain_obligations, paired_scaffold_structure,
    reconcile_complete_mapping,
)
from self_learning_ai.conf1_v3.goco import Parser, alpha_bijection, expressions_equivalent, parse
from self_learning_ai.conf1_v3.interfaces import (
    ArtifactResolver, ClosureError, PHASE, SchemaError, _integer, _schema,
    artifact_reference, canonical_json_bytes, expected_row_index,
    observed_population, ordered_row_id_digest, rid, validate_reason_records,
    validate_report_envelope, validate_row_set,
)


def toy_contract(source, program_id=dev.PROGRAM_IDS[0], outputs=()):
    program = compile_program(program_id, source)
    keys, occurrences = keys_from_ir(program, outputs)
    return CoverageContractV3(
        1, PHASE, rid("CONTRACT", [program_id]), program_id, program_id,
        "development", "ISOLATED", program.domain, DOMAINS[program.domain],
        (), (), {"kind": "development_only"}, graph_record(program), keys,
        ("FIVE_DISPOSABLE_CASES",), tuple(program.roles.values()), {},
        source, occurrences, program,
    )


def bind_bytes(folder, ident, role, name, data):
    (folder / name).write_bytes(data)
    return artifact_reference(ident, role, name, data)


def engine_for(folder, source, program_id, formula, outputs=(), raw_inputs=dev.RAW_INPUTS[:5]):
    contract = toy_contract(source, program_id, outputs)
    source_ref = bind_bytes(folder, "DEVCORE-SOURCE", "SOURCE_REFERENCE", "toy.goco", source.encode())
    cases = [{"case_id": cid, "input": raw, "expected_output": str(formula(int(raw) if contract.domain=="numeric_iteration" else [int(f) for f in raw.split("|")]))}
             for cid, raw in zip(dev.CASE_IDS, raw_inputs)]
    case_ref = bind_bytes(folder, "DEVCORE-CASES", "CASE_SET", "toy-cases.json",
                          canonical_json_bytes({"schema_version": 1, "program_id": program_id, "cases": cases}))
    oracle = PinnedCompilerOracle(dev.ROOT / ".tools/jdk-25.0.1+8/bin/java.exe",
                                  dev.ROOT / ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    return CoverageEngine(reconcile_complete_mapping(contract, source),
                          resolver=ArtifactResolver(folder, [source_ref, case_ref]),
                          source_artifact_id=source_ref["artifact_id"], case_artifact_id=case_ref["artifact_id"], oracle=oracle)


@pytest.fixture(scope="module")
def double_engine(tmp_path_factory):
    return engine_for(tmp_path_factory.mktemp("devcore-double"), dev.FORWARD,
                      dev.PROGRAM_IDS[0], lambda n: 17 + n * (n + 1), ("OUTPUT_MULTIDIGIT",))


@pytest.fixture(scope="module")
def pair_engine(tmp_path_factory):
    return engine_for(tmp_path_factory.mktemp("devcore-pair"), dev.PAIR_ADD,
                      dev.PROGRAM_IDS[1], lambda n: 17 + n // 5 + n // 7)


def test_preflight_proves_exact_nonoverlap():
    assert OVERLAP_PROOF["historical_files_compared"] == 13
    assert OVERLAP_PROOF["exact_string_overlap"] == OVERLAP_PROOF["recorded_fixture_hash_overlap"] == 0
    assert not OVERLAP_PROOF["expected_labels_loaded"]


@pytest.mark.parametrize("value", [True, False, 1.0, "1", None])
def test_strict_integer_schema(value):
    with pytest.raises(SchemaError):
        _integer(value, "schema_version")
    with pytest.raises(SchemaError):
        _schema({"schema_version": value})


def test_independently_framed_rid_digest():
    assert rid("DEVCORE", ["\u03bb", "ab"]) == "DEVCORE|2:\u03bb|2:ab"
    raw = b"ROWSET|15:DEVCORE-ROW-ONEROWSET|15:DEVCORE-ROW-TWO"
    assert ordered_row_id_digest(["DEVCORE-ROW-ONE", "DEVCORE-ROW-TWO"]) == hashlib.sha256(raw).hexdigest()


def test_row_population_and_index_binding(tmp_path):
    inventory = bind_bytes(tmp_path, "DEVCORE-INVENTORY", "DIAGNOSTIC_ARTIFACT", "inventory.json", b"{}")
    ids = ["DEVCORE-ROW-ONE", "DEVCORE-ROW-TWO"]
    index = expected_row_index(candidate_id="DEVCORE-CANDIDATE", index_id="DEVCORE-INDEX",
                               report_type="COVERAGE_V3_DIRECT", row_set_id="v3_1_contract_rows",
                               derivation_name="DISPOSABLE_DEVELOPMENT", input_inventory_artifacts=[inventory], ordered_row_ids=ids)
    ref = bind_bytes(tmp_path, "DEVCORE-INDEX-ARTIFACT", "EXPECTED_ROW_INDEX", "index.json", canonical_json_bytes(index))
    rows = [{"row_id": x} for x in ids]
    row_set = {"row_set_id": "v3_1_contract_rows", "expected_row_index": {"artifact_id": ref["artifact_id"],
               "index_id": index["index_id"], "sha256": ref["sha256"], "size_bytes": ref["size_bytes"], "expected_count": 2},
               "observed_population": observed_population(ids, rows), "rows": rows}
    resolver = ArtifactResolver(tmp_path, [inventory, ref])
    kwargs = dict(resolver=resolver, bound_indexes=[ref], candidate_id="DEVCORE-CANDIDATE", report_type="COVERAGE_V3_DIRECT")
    validate_row_set(row_set, **kwargs)
    bad = {**row_set, "extra": False}
    with pytest.raises(SchemaError): validate_row_set(bad, **kwargs)
    bad = {**row_set, "expected_row_index": {**row_set["expected_row_index"], "expected_count": True}}
    with pytest.raises(SchemaError): validate_row_set(bad, **kwargs)
    bad = {**row_set, "observed_population": {**row_set["observed_population"], "ordered_row_id_digest": "f" * 64}}
    with pytest.raises(ClosureError): validate_row_set(bad, **kwargs)
    negative = [{"row_id": x, "finding": "NOT_COVERED", "status": "PASS"} for x in ids]
    validate_row_set({**row_set, "rows": negative}, **kwargs)
    (tmp_path / "inventory.json").write_bytes(b"[]")
    with pytest.raises(ClosureError): validate_row_set(row_set, **kwargs)


def test_report_requires_array_before_evidence_resolution():
    from self_learning_ai.conf1_v3.interfaces import REPORT_ENVELOPE_FIELDS
    report = dict.fromkeys(REPORT_ENVELOPE_FIELDS)
    report.update(schema_version=1, phase=PHASE, report_type="COVERAGE_V3_DIRECT", status="PASS", row_sets={})
    with pytest.raises(SchemaError, match="row_sets"):
        validate_report_envelope(report)
    report["row_sets"] = []
    with pytest.raises(SchemaError, match="row_sets"):
        validate_report_envelope(report)


def test_reason_record_closure():
    reference = {"artifact_id": "DEVCORE-INVENTORY", "record_id": "DEVCORE-ROW-ONE", "record_role": "DIAGNOSTIC",
                 "content_sha256_utf8": None, "content_size_bytes_utf8": None}
    reason = {"code": "MISSING_ROW", "contract_id": "DEVCORE-CANDIDATE", "detail_reference": reference}
    validate_reason_records([reason])
    with pytest.raises(SchemaError): validate_reason_records([{**reason, "code": "UNFROZEN_DEVCORE_REASON"}])
    with pytest.raises(SchemaError): validate_reason_records([{**reason, "extra": 1}])


def test_duplicate_json_fields_rejected(tmp_path):
    ref = bind_bytes(tmp_path, "DEVCORE-INVENTORY", "DIAGNOSTIC_ARTIFACT", "duplicate.json", b'{"field":1,"field":2}')
    with pytest.raises(SchemaError): ArtifactResolver(tmp_path, [ref]).json(ref["artifact_id"])


def test_reverse_loop_typed_execution(tmp_path):
    engine=engine_for(tmp_path,dev.REVERSE,dev.PROGRAM_IDS[2],lambda n:17+n*(n+1)//2)
    program=engine.mapping.program
    result = engine.normals[dev.CASE_IDS[1]]
    assert result.output == str(17 + 6 * 7 // 2)
    assert any(item.operation == "PRIOR_STATE_TO_UPDATE" for item in program.items)
    assert any(program.item(oid).operation == "PRIOR_STATE_TO_UPDATE" for oid in result.evaluated)


@pytest.mark.parametrize("source", dev.UNKNOWN)
def test_unknown_import_loop_call_fail_closed(source):
    with pytest.raises(SchemaError): parse(source)


def test_exact_operator_recognition():
    assert _predicate_ops(dev.EXPRESSIONS[4]) == ("LE",)
    assert "LT" not in _predicate_ops(dev.EXPRESSIONS[4])


def test_alpha_is_a_typed_bijection():
    a = {"devLeft": "INTEGER", "devRight": "INTEGER"}
    b = {"otherLeft": "INTEGER", "otherRight": "INTEGER"}
    alpha_bijection(a, b, {"devLeft": "otherLeft", "devRight": "otherRight"})
    with pytest.raises(SchemaError): alpha_bijection(a, b, {"devLeft": "otherLeft", "devRight": "otherLeft"})
    with pytest.raises(SchemaError): alpha_bijection(a, b, {"devLeft": "otherLeft"})


def test_allowed_catalog_produces_typed_rule_proof():
    left = {"devLeft": "INTEGER", "devRight": "INTEGER"}
    right = {"otherLeft": "INTEGER", "otherRight": "INTEGER"}
    alpha = {"devLeft": "otherLeft", "devRight": "otherRight"}
    proof = closed_equivalence(Parser(dev.EXPRESSIONS[0]).expr(), Parser(dev.EXPRESSIONS[1]).expr(), alpha,
                               left_symbols=left, right_symbols=right)
    assert proof["finding"] == "EQUIVALENT"
    assert "V3.3.PURE_COMMUTATIVE_CHILD_SORT" in proof["rule_ids"]
    assert proof["typed_occurrences"]
    proof = closed_equivalence(Parser(dev.EXPRESSIONS[4]).expr(), Parser(dev.EXPRESSIONS[5]).expr(), alpha,
                               left_symbols=left, right_symbols=right)
    assert proof["finding"] == "EQUIVALENT"
    assert "V3.3.COMPARISON_DIRECTION" in proof["rule_ids"]
    assert expressions_equivalent(Parser(dev.EXPRESSIONS[6]).expr(), Parser(dev.EXPRESSIONS[7]).expr(),
                                  left_symbols={}, right_symbols={}, context="COMPUTED_VALUE")


def test_forbidden_catalog_and_unproved_indicators_fail_closed():
    symbols = {"devLeft": "INTEGER", "devRight": "INTEGER", "devThird": "INTEGER"}
    assert not expressions_equivalent(Parser(dev.EXPRESSIONS[2]).expr(), Parser(dev.EXPRESSIONS[3]).expr(),
                                      left_symbols=symbols, right_symbols=symbols)
    symbols.pop("devThird")
    assert not expressions_equivalent(Parser(dev.EXPRESSIONS[8]).expr(), Parser(dev.EXPRESSIONS[9]).expr(),
                                      left_symbols=symbols, right_symbols=symbols)
    proof = closed_equivalence(Parser(dev.EXPRESSIONS[10]).expr(), Parser(dev.EXPRESSIONS[10]).expr(),
                               left_symbols=symbols, right_symbols=symbols, context="LOCAL_PAIR_JOINT", indicators=frozenset(symbols))
    assert proof["finding"] == "UNRESOLVED"


def test_complete_mapping_alpha_trivia_and_literal_mismatch():
    contract = toy_contract(dev.FORWARD)
    proof = reconcile_complete_mapping(contract, dev.TRIVIA)
    assert len(proof.correspondence) == len(contract.ir.items)
    with pytest.raises(ClosureError): reconcile_complete_mapping(contract, dev.CHANGED_VALUE)
    contract.key_occurrences[next(iter(contract.key_occurrences))] = ()
    with pytest.raises(SchemaError): reconcile_complete_mapping(contract, dev.FORWARD)


def test_joint_suppression_preserves_initial_state_and_first_witness(double_engine):
    key = next(k for k in double_engine.mapping.contract.canonical_keys if k.operation == "ACCUMULATE")
    result = double_engine.behavioral(key.key_id)
    assert result["finding"] == "ACTIVE"
    assert len(result["occurrences"]) == 2
    assert result["witness"]["case_id"] == "DEVCORE-CASE-A"
    assert result["witness"]["intervention_order"] == 0
    assert result["witness"]["counterfactual_output"] == "17"
    assert all(tuple(a["occurrence_ids"]) == result["occurrences"] for a in result["attempts"])


def test_supplied_activity_flags_are_not_authoritative():
    with pytest.raises(SchemaError): behavioral_activity({"path_active": True, "normal_event_exists": True, "final_output_changed": True})


def test_active_parent_attribute_is_executed_on_active_case(pair_engine):
    key = next(k for k in pair_engine.mapping.contract.canonical_keys if k.computed_integer == 5 and k.attribute_parent_kind == "ACTIVE_BEHAVIORAL_PARENT")
    result = pair_engine.attribute(key.key_id)
    assert result["finding"] == "COVERED"
    assert result["witness"]["case_id"] == pair_engine.behavioral(key.parent_key_id)["witness"]["case_id"]


def test_initial_accumulator_has_no_invented_parent(double_engine):
    key = next(k for k in double_engine.mapping.contract.canonical_keys if k.attribute_parent_kind == "INITIAL_ACCUMULATOR")
    assert key.parent_key_id is None and key.computed_integer == 17
    assert double_engine.attribute(key.key_id)["finding"] == "COVERED"


def test_output_attribute_resolves_actual_bound_record(double_engine):
    key = next(k for k in double_engine.mapping.contract.canonical_keys if k.evidence_kind == "OUTPUT_ATTRIBUTE")
    assert double_engine.output_attribute(key.key_id)["finding"] == "COVERED"
    case = double_engine.cases[0]
    with pytest.raises(ClosureError):
        double_engine.resolver.verify_record_content({**case.expected_output_reference, "record_id": "DEVCORE-NONEXISTENT"}, case.expected_output)


def test_supplied_normal_cache_cannot_change_observed_outputs(double_engine):
    key = next(k for k in double_engine.mapping.contract.canonical_keys if k.operation == "ACCUMULATE")
    normal = double_engine.normals[dev.CASE_IDS[0]]
    original = normal.output
    try:
        normal.output = "DEVCORE-FORGED-OUTPUT"
        with pytest.raises(ClosureError, match="cache changed"):
            double_engine.behavioral(key.key_id)
    finally:
        normal.output = original


def test_zero_class_cannot_supply_normal_activity_event(double_engine):
    key = next(k for k in double_engine.mapping.contract.canonical_keys if k.operation.startswith("INPUT_DOMAIN:"))
    result = double_engine.behavioral(key.key_id)
    assert result["finding"] == "ACTIVE"
    assert "SIGN_ZERO" in input_domain_classes("numeric_iteration", dev.RAW_INPUTS[0])
    assert all(row["case_id"] != "DEVCORE-CASE-Z" for row in result["normal_events"])
    rows = input_domain_obligations([double_engine])
    assert len(rows) == 14
    assert any(row["status"] == "FAIL" for row in rows)
    assert all(witness["program_id"] == double_engine.mapping.program.program_id for row in rows for witness in row["witnesses"])


def test_four_field_decoder_all_conversions_connect_and_are_joint(tmp_path):
    engine=engine_for(tmp_path,dev.ARRAY_SOURCE,dev.PROGRAM_IDS[4],lambda fields:17+sum(fields),raw_inputs=dev.ARRAY_INPUTS)
    conversions=next(k for k in engine.mapping.contract.canonical_keys if k.operation=="strings.TO_NUMBER")
    activity=engine.behavioral(conversions.key_id)
    assert activity["finding"]=="ACTIVE" and len(activity["occurrences"])==4
    for normal in engine.normals.values():
        assert set(activity["occurrences"])<=normal.output_dependencies
    macro=next(k for k in engine.mapping.contract.canonical_keys if k.operation.startswith("INPUT_DOMAIN:"))
    assert engine.behavioral(macro.key_id)["finding"]=="ACTIVE"
    classes=input_domain_classes("array_reduction",dev.ARRAY_INPUTS[0])
    assert set(classes)=={"NEGATIVE_PRESENT","ZERO_PRESENT","POSITIVE_PRESENT"}


def test_resolved_negative_is_not_report_failure(tmp_path):
    engine = engine_for(tmp_path, dev.ZERO_EVENT, dev.PROGRAM_IDS[3], lambda n: 17)
    key = next(k for k in engine.mapping.contract.canonical_keys if k.operation == "ACCUMULATE")
    finding = engine.behavioral(key.key_id)
    assert finding["finding"] == "INACTIVE" and finding["status"] == "PASS"
    assert atomic_coverage([(key, "ISOLATED")], [engine])[0]["status"] == "FAIL"


def test_paired_scaffold_only_marked_treatment_may_change():
    a = compile_program(dev.PROGRAM_IDS[1], dev.PAIR_ADD)
    b = compile_program(dev.PROGRAM_IDS[1], dev.PAIR_MUL)
    assert paired_scaffold_structure(a, b)["finding"] == "MATCHED"
    with pytest.raises(ClosureError): paired_scaffold_structure(a, compile_program(dev.PROGRAM_IDS[1], dev.CHANGED_PAIR))


def test_prospective_population_is_incomplete_not_authoritative():
    ledger = json.loads((dev.ROOT / "research/protocols/phase3c_conf1_slots.json").read_text(encoding="utf-8"))
    contracts = all_contracts(ledger)
    assert len(contracts) == sum(len(group) * (2 if name == "training_paired_slots" else 1) for name, group in ledger["slots"].items()) == 184
    assert {c.aggregator["kind"] for c in contracts} == {"sum_per_item", "prefix_running_pair", "two_pass_product"}
    assert all(c.core_gaps for c in contracts)
    with pytest.raises(SchemaError): replace(contracts[0], core_gaps=()).validate()
    with pytest.raises(SchemaError): v35_expected_row_ids(contracts)
    rows = v35_expected_row_ids(contracts, diagnostic_incomplete=True)
    assert len(rows) == len(set(rows))
    with pytest.raises(ClosureError): reconcile_complete_mapping(contracts[0], contracts[0].reference_source)
