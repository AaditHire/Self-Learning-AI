"""Prospective CoverageContractV3 and frozen INPUT_DOMAIN construction rules."""

from __future__ import annotations

import hashlib
import itertools
import random
from dataclasses import dataclass, asdict
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

    def validate(self) -> None:
        if self.category not in CATEGORIES or self.evidence_kind not in KEY_KINDS:
            raise SchemaError("UNRESOLVED_REQUIREMENT")
        if self.domain not in DOMAINS:
            raise SchemaError("UNRESOLVED_REQUIREMENT")
        if self.required_condition not in CONDITIONS:
            raise SchemaError("UNRESOLVED_REQUIREMENT")
        if self.evidence_kind == "VALUE_OR_LITERAL_ATTRIBUTE":
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

    def validate(self) -> None:
        if self.schema_version != 1 or self.phase != PHASE:
            raise SchemaError("UNSUPPORTED_SCHEMA_VERSION")
        if self.condition not in CONDITIONS or self.domain not in DOMAINS:
            raise SchemaError("UNRESOLVED_REQUIREMENT")
        ids = [key.key_id for key in self.canonical_keys]
        if not ids or len(ids) != len(set(ids)):
            raise SchemaError("canonical key IDs must be nonempty and unique")
        for key in self.canonical_keys:
            key.validate()
            if key.domain != self.domain:
                raise SchemaError("key domain mismatch")

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
        }


def _key_id(category: str, domain: str, operation: str, roles: Sequence[str]) -> str:
    return rid("KEY", [category, domain, operation, *roles])


def _behavioral(category: str, domain: str, operation: str, roles: Sequence[str],
                required: str = "BOTH") -> ContractKey:
    return ContractKey(_key_id(category, domain, operation, roles), category, "BEHAVIORAL",
                       domain, operation, tuple(roles[:-1]), roles[-1], required)


def _predicate_ops(expression: str) -> tuple[str, ...]:
    found = []
    for token, name in (("%", "MOD"), ("*", "MUL"), ("<=", "LE"), (">=", "GE"),
                        ("==", "EQ"), ("<", "LT"), (">", "GT")):
        if token in expression and name not in found: found.append(name)
    return tuple(found)


def _domain_keys(domain: str) -> list[ContractKey]:
    roles = ("raw_input", "decoded_domain")
    keys = [_behavioral("API_DECODER", domain, f"INPUT_DOMAIN:{DOMAINS[domain]}", roles)]
    if domain == "array_reduction":
        for op in ("INPUT", "strings.SPLIT", "strings.TO_NUMBER", "ARRAY_INDEX"):
            keys.append(_behavioral("API_DECODER", domain, op, ("raw_input", "decoded_value")))
    else:
        keys.append(_behavioral("GENERIC_CONSTRUCT", domain, "BOUNDED_LOOP", ("decoded_n", "loop_control")))
    return keys


def _common_keys(domain: str, predicates: Iterable[tuple[str, str]]) -> list[ContractKey]:
    keys = _domain_keys(domain)
    for name, expression in predicates:
        parent = _behavioral("SEMANTIC_PRIMITIVE", domain, name, ("domain_item", "predicate_boolean"))
        keys.append(parent)
        keys.append(_behavioral("ATOMIC_CONTROL_DATAFLOW", domain, "PREDICATE_TO_INDICATOR",
                                (name, "indicator")))
        for op in _predicate_ops(expression):
            keys.append(_behavioral("ATOMIC_OPERATOR", domain, op, ("predicate_operand", "predicate_result")))
    for category, operation, roles in (
        ("GENERIC_CONSTRUCT", "CONDITIONAL_UPDATE", ("predicate", "update")),
        ("ATOMIC_CONTROL_DATAFLOW", "CONTROL_TO_UPDATE", ("control", "update")),
        ("ATOMIC_CONTROL_DATAFLOW", "OPERATOR_TO_ACCUMULATOR", ("contribution", "accumulator")),
        ("ATOMIC_CONTROL_DATAFLOW", "ACCUMULATOR_TO_OUTPUT", ("accumulator", "output")),
        ("GENERIC_CONSTRUCT", "FINAL_DISPLAY", ("accumulator", "output")),
    ):
        keys.append(_behavioral(category, domain, operation, roles))
    unique = {key.key_id: key for key in keys}
    return list(unique.values())


def _initial_attribute(domain: str, offset: int) -> ContractKey:
    op = f"COMPUTED_VALUE:{offset}:INITIAL_ACCUMULATOR"
    return ContractKey(_key_id("VALUE_OR_LITERAL", domain, op, ("initial_accumulator",)),
                       "VALUE_OR_LITERAL", "VALUE_OR_LITERAL_ATTRIBUTE", domain, op, (),
                       "initial_accumulator", "EVALUATION", "INITIAL_ACCUMULATOR", None,
                       offset, "INITIAL_ACCUMULATOR", None)


def _output_keys(domain: str) -> list[ContractKey]:
    return [ContractKey(_key_id("OUTPUT_CATEGORY", domain, name, ("displayed_output",)),
                        "OUTPUT_CATEGORY", "OUTPUT_ATTRIBUTE", domain, name, (),
                        "displayed_output", "EVALUATION")
            for name in ("OUTPUT_ZERO", "OUTPUT_POSITIVE")]


def _predicates_for_slot(ledger: Mapping[str, Any], slot: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    definitions = {x["name"]: x["expression"] for x in ledger["predicate_definitions"][slot["family"]]}
    names: list[str]
    if "role_predicates" in slot: names = list(slot["role_predicates"].values())
    elif "primitive" in slot: names = [slot["primitive"]]
    else: names = [slot["P"], slot["Q"]]
    return tuple((name, definitions[name]) for name in dict.fromkeys(names))


def contract_from_slot(ledger: Mapping[str, Any], slot: Mapping[str, Any], *,
                       condition: str = "EVALUATION") -> CoverageContractV3:
    condition = condition.upper()
    if condition not in CONDITIONS: raise SchemaError("unknown condition")
    domain = slot["family"]
    if domain not in DOMAINS: raise SchemaError("unknown domain")
    program_id = slot.get("task_id") or f"CONF1-{condition}-{slot['slot_id']}"
    slot_id = slot.get("slot_id") or slot["task_id"]
    predicates = _predicates_for_slot(ledger, slot)
    keys = _common_keys(domain, predicates)
    offset = int(slot.get("offset", 0))
    keys.append(_initial_attribute(domain, offset))
    keys.extend(_output_keys(domain))
    if "slot_id" in slot:
        treatment = "PAIR_INDEPENDENT_ADD" if condition == "ISOLATED" else "PAIR_JOINT_MUL"
        required = "COMPOSITION" if condition == "COMPOSITION" else "BOTH"
        keys.append(_behavioral("ATOMIC_OPERATOR", domain, treatment,
                                ("indicator_P", "indicator_Q", "contribution"), required))
        aggregator = {"kind": "sum_per_item", "treatment": treatment, "initial": offset}
        graph = {"family": "TRAINING_PAIR", "roles": ["P", "Q"], "relation": treatment}
        task_kind = "training"
        obligations = ("FIVE_CASES", "PAIRED_CASE_INPUT_IDENTITY")
        role_map = (("P", slot["P"]), ("Q", slot["Q"]))
    else:
        graph_name = slot.get("graph", slot.get("structure", "PRIMITIVE"))
        aggregator = {"kind": "sum_per_item", "graph": graph_name, "initial": offset}
        graph = {"family": graph_name, "roles": list(slot.get("role_predicates", {})),
                 "signature": slot.get("composition_signature")}
        task_kind = "primary" if slot.get("group") == "novel_composition" else "secondary"
        obligations = ("FIVE_CASES", "ZERO_OUTPUT", "POSITIVE_OUTPUT", "BEHAVIOR_EXERCISE")
        role_map = tuple(slot.get("role_predicates", {}).items())
    key_map = {key.key_id: key for key in keys}
    contract = CoverageContractV3(
        1, PHASE, rid("CONTRACT", [program_id]), program_id, slot_id, task_kind,
        condition, domain, DOMAINS[domain], predicates, role_map, aggregator, graph,
        tuple(key_map.values()), obligations,
        ("INPUT", "DECODER", "LOOP", "PREDICATES", "ACCUMULATOR", "DISPLAY"),
        {"role_count": len(role_map), "aggregation_state_complete": True,
         "fixed_initialization": offset, "hidden_state_allowed": False},
    )
    contract.validate()
    return contract


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


def v35_expected_row_ids(contracts: Sequence[CoverageContractV3]) -> list[str]:
    rows = []
    for contract in contracts:
        if contract.task_kind != "training": continue
        rows.extend(rid("V3.5", [contract.program_id, key.key_id]) for key in contract.canonical_keys)
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
