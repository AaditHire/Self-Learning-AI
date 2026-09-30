"""Prospective CoverageContractV3 and frozen INPUT_DOMAIN construction rules."""

from __future__ import annotations

import hashlib
import itertools
import random
from dataclasses import dataclass, asdict, field
from typing import Any, Iterable, Mapping, Sequence

from .interfaces import PHASE, SchemaError, rid

CATEGORIES = {
    "SEMANTIC_PRIMITIVE", "GENERIC_CONSTRUCT", "API_DECODER", "ATOMIC_OPERATOR",
    "VALUE_OR_LITERAL", "OUTPUT_CATEGORY", "ATOMIC_CONTROL_DATAFLOW",
}
KEY_KINDS = {"BEHAVIORAL", "VALUE_OR_LITERAL_ATTRIBUTE", "OUTPUT_ATTRIBUTE"}
PARENT_KINDS = {"ACTIVE_BEHAVIORAL_PARENT", "INITIAL_ACCUMULATOR"}
CONDITIONS = {"ISOLATED", "COMPOSITION", "EVALUATION", "BOTH"}
DOMAINS = {
    "numeric_iteration": "NONNEGATIVE_INTEGER",
    "array_reduction": "FOUR_SIGNED_INTEGER_FIELDS",
}
EDGES = {
    "INPUT_TO_DECODER", "VALUE_TO_PREDICATE", "PREDICATE_TO_CONTROL",
    "PREDICATE_TO_INDICATOR", "VALUE_TO_OPERATOR", "OPERATOR_TO_ACCUMULATOR",
    "CONTROL_TO_UPDATE", "LOOP_CARRY", "PRIOR_STATE_TO_UPDATE",
    "ACCUMULATOR_TO_OUTPUT",
}

@dataclass(frozen=True)
class ContractKey:
    key_id: str
    category: str
    evidence_kind: str
    domain: str
    operation: str
    operand_roles: tuple[str, ...]
    result_role: str
    required_condition: str
    attribute_parent_kind: str | None = None
    parent_key_id: str | None = None
    computed_integer: int | None = None
    semantic_role: str | None = None
    exact_required_lexeme: str | None = None
    operand_types: tuple[str, ...] = ()
    result_type: str = "INTEGER"

    def validate(self) -> None:
        if self.category not in CATEGORIES or self.evidence_kind not in KEY_KINDS:
            raise SchemaError("UNRESOLVED_REQUIREMENT")
        expected = "VALUE_OR_LITERAL_ATTRIBUTE" if self.category == "VALUE_OR_LITERAL" else "OUTPUT_ATTRIBUTE" if self.category == "OUTPUT_CATEGORY" else "BEHAVIORAL"
        if self.evidence_kind != expected or self.result_type not in {"INTEGER","BOOLEAN","STRING","INTEGER_ARRAY","STRING_ARRAY"}:
            raise SchemaError("key ontology/type mismatch")
        if self.domain not in DOMAINS:
            raise SchemaError("UNRESOLVED_REQUIREMENT")
        if self.required_condition not in CONDITIONS:
            raise SchemaError("UNRESOLVED_REQUIREMENT")
        if self.evidence_kind == "VALUE_OR_LITERAL_ATTRIBUTE":
            if self.exact_required_lexeme is None and (type(self.computed_integer) is not int or not self.semantic_role):
                raise SchemaError("computed integer/role required")
            if self.exact_required_lexeme is not None and (self.computed_integer is not None or self.semantic_role is not None):
                raise SchemaError("literal subtype null matrix")
            if self.attribute_parent_kind not in PARENT_KINDS:
                raise SchemaError("attribute parent kind missing")
            if self.attribute_parent_kind == "ACTIVE_BEHAVIORAL_PARENT" and not self.parent_key_id:
                raise SchemaError("active attribute parent missing")
            if self.attribute_parent_kind == "INITIAL_ACCUMULATOR" and self.parent_key_id is not None:
                raise SchemaError("initial accumulator cannot invent behavioral parent")
        elif self.attribute_parent_kind is not None or self.parent_key_id is not None:
            raise SchemaError("non-attribute key has attribute parent")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        value = asdict(self)
        value["operand_roles"] = list(self.operand_roles)
        return value


@dataclass(frozen=True)
class CoverageContractV3:
    schema_version: int
    phase: str
    contract_id: str
    program_id: str
    slot_id: str
    task_kind: str
    condition: str
    domain: str
    input_domain: str
    predicate_definitions: tuple[tuple[str, str], ...]
    role_map: tuple[tuple[str, str], ...]
    aggregator: Mapping[str, Any]
    complete_expression_graph: Mapping[str, Any]
    canonical_keys: tuple[ContractKey, ...]
    case_obligations: tuple[str, ...]
    source_roles: tuple[str, ...]
    e5_role_state: Mapping[str, Any]
    reference_source: str = ""
    key_occurrences: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    ir: Any = field(default=None, repr=False, compare=False)
    core_gaps: tuple[str, ...] = ()

    def validate(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1 or self.phase != PHASE:
            raise SchemaError("UNSUPPORTED_SCHEMA_VERSION")
        if self.condition not in CONDITIONS or self.domain not in DOMAINS:
            raise SchemaError("UNRESOLVED_REQUIREMENT")
        if self.task_kind not in {"training","primary","secondary","development"}:
            raise SchemaError("unknown contract kind")
        if self.task_kind!="development" and not self.core_gaps:
            raise SchemaError("UNRESOLVED_REQUIREMENT: frozen contract completion is not implemented")
        ids = [key.key_id for key in self.canonical_keys]
        if not ids or len(ids) != len(set(ids)):
            raise SchemaError("canonical key IDs must be nonempty and unique")
        for key in self.canonical_keys:
            key.validate()
            if key.domain != self.domain:
                raise SchemaError("key domain mismatch")
        if self.ir is None or self.ir.program_id != self.program_id or self.ir.source != self.reference_source:
            raise SchemaError("complete prospective IR required")
        if set(self.key_occurrences) != set(ids): raise SchemaError("key occurrence inventory incomplete")
        item_ids = {i.occurrence_id for i in self.ir.items}
        if any(not occurrences or not set(occurrences) <= item_ids for occurrences in self.key_occurrences.values()):
            raise SchemaError("unknown prospective key occurrence")
        from .contract_ir import graph_record, keys_from_ir
        from .core_ir import compile_program
        rebuilt=compile_program(self.program_id,self.reference_source)
        if graph_record(rebuilt)!=dict(self.complete_expression_graph) or graph_record(self.ir)!=graph_record(rebuilt):
            raise SchemaError("prospective graph not derivable from bound source")
        outputs=tuple(k.operation for k in self.canonical_keys if k.category=="OUTPUT_CATEGORY")
        keys,occurrences=keys_from_ir(rebuilt,outputs)
        if keys!=self.canonical_keys or occurrences!=dict(self.key_occurrences):
            raise SchemaError("key inventory not derivable from prospective graph")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version, "phase": self.phase,
            "contract_id": self.contract_id, "program_id": self.program_id,
            "slot_id": self.slot_id, "task_kind": self.task_kind,
            "condition": self.condition, "domain": self.domain,
            "input_domain": self.input_domain,
            "predicate_definitions": [{"name": n, "expression": e} for n, e in self.predicate_definitions],
            "role_map": dict(self.role_map), "aggregator": dict(self.aggregator),
            "complete_expression_graph": dict(self.complete_expression_graph),
            "canonical_keys": [key.to_dict() for key in self.canonical_keys],
            "case_obligations": list(self.case_obligations),
            "source_roles": list(self.source_roles), "e5_role_state": dict(self.e5_role_state),
            "key_occurrences": {key:list(ids) for key,ids in self.key_occurrences.items()},
            "core_gaps": list(self.core_gaps),
        }


def _predicate_ops(expression: str) -> tuple[str, ...]:
    from .core_ir import OPERATORS
    from .goco import Parser, _walk_expr
    parser = Parser(expression); root = parser.expr()
    if parser.peek().kind != "EOF": raise SchemaError("predicate trailing token")
    return tuple(dict.fromkeys(OPERATORS[e.value] for e in _walk_expr(root) if e.kind == "BINARY"))


def contract_from_slot(ledger: Mapping[str, Any], slot: Mapping[str, Any], *,
                       condition: str = "EVALUATION") -> CoverageContractV3:
    from .contract_ir import lower_contract
    return lower_contract(ledger, slot, condition=condition)


def all_contracts(ledger: Mapping[str, Any]) -> list[CoverageContractV3]:
    result = []
    for slot in ledger["slots"]["training_paired_slots"]:
        result.extend((contract_from_slot(ledger, slot, condition="ISOLATED"),
                       contract_from_slot(ledger, slot, condition="COMPOSITION")))
    for group in ("primary", "primitive_sanity", "structural_transfer"):
        result.extend(contract_from_slot(ledger, slot) for slot in ledger["slots"][group])
    if len(result) != 184 or len({x.program_id for x in result}) != 184:
        raise SchemaError("frozen contract population must be 184")
    return result


def v35_expected_row_ids(contracts: Sequence[CoverageContractV3], *, diagnostic_incomplete: bool = False) -> list[str]:
    # A vacuous/partial inventory is not the prospective population required by
    # interface sections 4.1 and 9.1. Diagnostic IDs are never an expected index.
    if type(diagnostic_incomplete) is not bool:
        raise SchemaError("diagnostic_incomplete must be an actual boolean")
    program_ids = [contract.program_id for contract in contracts]
    if len(program_ids) != len(set(program_ids)):
        raise SchemaError("duplicate contract program in prospective population")
    if not diagnostic_incomplete:
        from .contract_ir import _builder
        ledger = _builder().LEDGER
        expected_programs = {
            slot["slot_id"].replace("CONF1-", f"CONF1-{condition}-", 1):
                (slot["slot_id"], "training", condition, slot["family"])
            for slot in ledger["slots"]["training_paired_slots"]
            for condition in ("ISOLATED", "COMPOSITION")
        }
        expected_programs.update({slot["task_id"]:
            (slot["task_id"], "primary" if group == "primary" else "secondary", "EVALUATION", slot["family"])
            for group in ("primary", "primitive_sanity", "structural_transfer") for slot in ledger["slots"][group]})
        if set(program_ids) != set(expected_programs):
            raise SchemaError("V3_5_POPULATION_UNRESOLVED: missing or unexpected frozen contracts")
        if any((c.slot_id, c.task_kind, c.condition, c.domain) != expected_programs[c.program_id]
               for c in contracts):
            raise SchemaError("V3_5_POPULATION_UNRESOLVED: frozen contract inventory metadata mismatch")
    if not diagnostic_incomplete and any(contract.core_gaps for contract in contracts):
        raise SchemaError("V3_5_POPULATION_UNRESOLVED: incomplete prospective key ontology")
    rows = []
    for contract in contracts:
        contract.validate()
        if contract.task_kind != "training": continue
        rows.extend(rid("V3.5", [contract.program_id, key.key_id]) for key in contract.canonical_keys)
    if len(rows) != len(set(rows)):
        raise SchemaError("duplicate logical V3.5 row")
    # Ordering is a reproducible implementation convention, not a new gate.
    # The frozen interface binds this exact order in the pre-run row index.
    rows.sort(key=lambda value: value.encode("utf-8"))
    return rows


def canonical_numeric_witness_slot(ledger: Mapping[str, Any]) -> str:
    ids = [slot["slot_id"] for slot in ledger["slots"]["training_paired_slots"]
           if slot["family"] == "numeric_iteration"]
    if not ids or len(ids) != len(set(ids)):
        raise SchemaError("numeric slot population missing or duplicated")
    selected = sorted(ids, key=lambda x: x.encode("utf-8"))[0]
    if selected != "CONF1-TR-NU-01-V0":
        raise SchemaError("frozen canonical numeric witness slot changed")
    return selected


def _rng(seed: int, slot_id: str, tag: str) -> random.Random:
    digest = hashlib.sha256(f"{seed}|{slot_id}|{tag}".encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest, "big"))


def numeric_training_inputs(ledger: Mapping[str, Any], slot_id: str) -> tuple[str, ...]:
    canonical = canonical_numeric_witness_slot(ledger)
    valid_ids = {slot["slot_id"] for slot in ledger["slots"]["training_paired_slots"]
                 if slot["family"] == "numeric_iteration"}
    if slot_id not in valid_ids: raise SchemaError("unknown numeric slot")
    pool = [value for value in range(1, 61) if value not in {12, 13, 14}]
    count = 4 if slot_id == canonical else 5
    values = _rng(int(ledger["construction_seed"]), slot_id, "train-numeric").sample(pool, count)
    if slot_id == canonical: values.append(0)
    result = tuple(str(value) for value in sorted(values))
    if len(result) != 5 or len(set(result)) != 5:
        raise SchemaError("numeric case construction must yield five unique cases")
    return result


NUMERIC_CLASSES = ("SIGN_ZERO", "SIGN_POSITIVE", "EMPTY_LOOP", "LOWER_DOMAIN_BOUNDARY")
ARRAY_CLASSES = ("NEGATIVE_PRESENT", "ZERO_PRESENT", "POSITIVE_PRESENT")

def input_domain_classes(domain: str, raw: str) -> dict[str, list[dict[str, Any]]]:
    if domain == "numeric_iteration":
        if not re_full_int(raw) or int(raw) < 0: raise SchemaError("invalid numeric domain input")
        value = int(raw); labels = []
        if value == 0: labels = ["SIGN_ZERO", "EMPTY_LOOP", "LOWER_DOMAIN_BOUNDARY"]
        else: labels = ["SIGN_POSITIVE"]
        return {label: [{"value": value}] for label in labels}
    if domain == "array_reduction":
        fields = raw.split("|")
        if len(fields) != 4 or any(not re_signed_int(x) for x in fields):
            raise SchemaError("invalid array domain input")
        values = [int(x) for x in fields]; result: dict[str, list[dict[str, Any]]] = {}
        for label, test in (("NEGATIVE_PRESENT", lambda x: x < 0),
                            ("ZERO_PRESENT", lambda x: x == 0),
                            ("POSITIVE_PRESENT", lambda x: x > 0)):
            hits = [{"index": i, "value": value} for i, value in enumerate(values) if test(value)]
            if hits: result[label] = hits
        return result
    raise SchemaError("unknown domain")


def re_full_int(value: str) -> bool:
    return bool(value) and value.isascii() and value.isdigit()

def re_signed_int(value: str) -> bool:
    return bool(value) and value.isascii() and (value.isdigit() or (value.startswith("-") and value[1:].isdigit()))


def contribution_vector(expression, roles: Sequence[str]) -> tuple[int, ...]:
    if len(roles) > 4: raise SchemaError("role cardinality exceeds four")
    return tuple(int(expression(dict(zip(roles, bits)))) for bits in itertools.product((False, True), repeat=len(roles)))
