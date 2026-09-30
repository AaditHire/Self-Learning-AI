"""Strict schema-version-1 interfaces frozen for CONF1 delegated evidence."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

PHASE = "PHASE_3C_CONF1"
SCHEMA_VERSION = 1
STATUSES = {"PASS", "FAIL", "UNRESOLVED"}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")

ARTIFACT_ROLES = {
    "FROZEN_AUTHORITY", "FREEZE_MANIFEST", "SLOT_LEDGER",
    "CANDIDATE_TRAINING_INVENTORY", "CANDIDATE_TRAINING_DATA",
    "EVALUATION_INVENTORY", "EVALUATION_DATA", "SOURCE_REFERENCE",
    "PROMPT", "TARGET", "CASE_SET", "SCHEDULE",
    "COVERAGE_CONTRACT_V3_INVENTORY", "SOURCE_OCCURRENCE_INVENTORY",
    "COMPILER_BINARY", "COMPILER_PROVENANCE", "COMPILER_WRAPPER",
    "COMPILER_CONFIGURATION", "TOKENIZER", "CHAT_TEMPLATE", "SCHEMA",
    "STATIC_LOOKUP", "PRODUCER_ENTRYPOINT", "PRODUCER_DEPENDENCY",
    "PRODUCER_CONFIGURATION", "PRODUCER_TOOL_MANIFEST",
    "PRODUCER_EXECUTION_PROVENANCE", "RUNTIME_EXECUTABLE",
    "RUNTIME_VERSION_CAPTURE", "PACKAGE_ENVIRONMENT",
    "CONSUMED_INVENTORY_MANIFEST", "EXPECTED_ROW_INDEX",
    "CANDIDATE_INPUT_MANIFEST", "COVERAGE_V3_DIRECT_EVIDENCE",
    "DELEGATED_EVIDENCE_REPORT", "CANDIDATE_EVIDENCE_MANIFEST",
    "COVERAGE_V3_CLOSURE_RESULT", "CONSTRUCTION_PROVENANCE",
    "DIAGNOSTIC_ARTIFACT",
}
RECORD_ROLES = {
    "TRAINING_EXAMPLE", "EVALUATION_TASK", "SOURCE", "REFERENCE", "PROMPT",
    "TARGET", "CASE_SET", "CASE", "CASE_INPUT", "EXPECTED_OUTPUT",
    "SCHEDULE_ENTRY", "COVERAGE_CONTRACT", "CONSUMED_RECORD",
    "SERIALIZED_EXAMPLE", "DIAGNOSTIC",
}
INTERFACE_REASON_CODES = {
    "MISSING_ROW", "DUPLICATE_ROW", "UNEXPECTED_ROW",
    "INPUT_ARTIFACT_HASH_MISMATCH", "INPUT_ARTIFACT_SIZE_MISMATCH",
    "CANDIDATE_INPUT_MANIFEST_MISMATCH", "PRODUCER_TOOL_IDENTITY_MISMATCH",
    "MISSING_PRODUCER_EXECUTION_PROVENANCE",
    "PRODUCER_EXECUTION_PROVENANCE_MISMATCH",
    "REPOSITORY_LOCAL_READ_SET_HASH_MISMATCH",
    "EXECUTION_DEPENDENCY_CLOSURE_FAILURE", "INVALID_PACKAGE_ENVIRONMENT_MODE",
    "PACKAGE_ENVIRONMENT_REQUIRED_FIELD_MISSING",
    "PACKAGE_ENVIRONMENT_NULL_RULE_VIOLATION", "RULE_IDENTITY_MISMATCH",
    "COMPILER_IDENTITY_MISMATCH", "COMPILER_RELEVANCE_INVALID",
    "EXECUTION_COMPILER_RELEVANCE_MISMATCH", "MALFORMED_REPORT",
    "UNSUPPORTED_SCHEMA_VERSION", "PRODUCER_ROW_FAIL",
    "PRODUCER_ROW_UNRESOLVED", "AGGREGATE_INCONSISTENCY",
    "EXPECTED_POPULATION_MISMATCH", "MODEL_AUTHORIZATION_NOT_FALSE",
    "FROZEN_AUTHORITY_MISMATCH", "REPOSITORY_COMMIT_MISMATCH",
    "REPOSITORY_TREE_MISMATCH", "DIRTY_PRODUCER_CODE", "UNDECLARED_DEPENDENCY",
    "DEPENDENCY_ACCESS_UNCLOSED", "RUNTIME_IDENTITY_MISMATCH",
    "PACKAGE_ENVIRONMENT_MISMATCH",
}

REPORT_ROW_SETS = {
    "COVERAGE_V3_DIRECT": (
        "v3_1_contract_rows", "v3_2_mapping_rows", "v3_3_equivalence_rows",
        "v3_5_activity_rows", "input_domain_class_rows", "v3_4_coverage_rows",
        "v3_6_symmetry_rows", "v3_7_delegation_rows",
    ),
    "E1_REFERENCE_VALIDATION": ("program_rows",),
    "E2_AST_V2": ("pair_rows",),
    "E3_SCAFFOLD": ("paired_slot_rows",),
    "E3_TOKEN_BUDGET": ("example_rows",),
    "E3_SCHEDULE": ("cell_rows", "exposure_rows", "optimizer_step_rows"),
    "E4_SIMILARITY_PAIRS": ("pair_rows",),
    "E4_EXACT_OVERLAP": ("pair_rows",),
    "E5_FULL_SIGNATURE": ("primary_certificates", "training_certificates", "comparisons"),
    "E6_HIDDEN_CASE_DISCRIMINATION": ("task_rows", "pair_distinction_rows"),
}

class SchemaError(ValueError):
    """Closed schema was malformed or used an unsupported state."""


class ClosureError(ValueError):
    """Identity, population, or transitive evidence closure failed."""


def _keys(value: Mapping[str, Any], required: Iterable[str], *, optional: Iterable[str] = ()) -> None:
    if not isinstance(value, dict):
        raise SchemaError("object required")
    required, optional = set(required), set(optional)
    actual = set(value)
    missing, extra = required - actual, actual - required - optional
    if missing or extra:
        raise SchemaError(f"closed fields mismatch missing={sorted(missing)} extra={sorted(extra)}")


def _string(value: Any, name: str, *, nonempty: bool = True) -> str:
    if not isinstance(value, str) or (nonempty and not value):
        raise SchemaError(f"{name} must be a{' nonempty' if nonempty else ''} string")
    return value


def _integer(value: Any, name: str, *, minimum: int | None = None) -> int:
    if type(value) is not int or (minimum is not None and value < minimum):
        raise SchemaError(f"{name} must be an integer" + (f" >= {minimum}" if minimum is not None else ""))
    return value


def _schema(value: Mapping[str, Any]) -> None:
    _integer(value.get("schema_version"), "schema_version")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise SchemaError("UNSUPPORTED_SCHEMA_VERSION")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_file_identity(path: Path) -> tuple[str, int]:
    data = path.read_bytes()
    return sha256_bytes(data), len(data)


def artifact_reference(artifact_id: str, artifact_role: str, path: str, data: bytes) -> dict[str, Any]:
    result = {
        "artifact_id": artifact_id,
        "artifact_role": artifact_role,
        "path": path,
        "sha256": sha256_bytes(data),
        "size_bytes": len(data),
        "hash_policy": "EXACT_BYTES_SHA256",
    }
    validate_artifact_reference(result)
    return result


def validate_artifact_reference(value: Mapping[str, Any]) -> None:
    _keys(value, {"artifact_id", "artifact_role", "path", "sha256", "size_bytes", "hash_policy"})
    _string(value["artifact_id"], "artifact_id")
    if value["artifact_role"] not in ARTIFACT_ROLES:
        raise SchemaError("unknown artifact_role")
    path = _string(value["path"], "path")
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts or "\\" in path or ":" in path or str(pure) != path:
        raise SchemaError("path must be repository-relative POSIX form")
    if not HEX64.fullmatch(_string(value["sha256"], "sha256")):
        raise SchemaError("invalid sha256")
    _integer(value["size_bytes"], "size_bytes", minimum=0)
    if value["hash_policy"] != "EXACT_BYTES_SHA256":
        raise SchemaError("new artifact hash policy must be EXACT_BYTES_SHA256")


def verify_artifact_reference(value: Mapping[str, Any], root: Path) -> None:
    validate_artifact_reference(value)
    path = (root / value["path"]).resolve()
    root_resolved = root.resolve()
    if root_resolved not in path.parents and path != root_resolved:
        raise ClosureError("artifact escapes root")
    if not path.is_file():
        raise ClosureError("artifact missing")
    digest, size = exact_file_identity(path)
    if digest != value["sha256"]:
        raise ClosureError("INPUT_ARTIFACT_HASH_MISMATCH")
    if size != value["size_bytes"]:
        raise ClosureError("INPUT_ARTIFACT_SIZE_MISMATCH")


def validate_record_reference(value: Mapping[str, Any], *, string_value: bool | None = None) -> None:
    _keys(value, {"artifact_id", "record_id", "record_role", "content_sha256_utf8", "content_size_bytes_utf8"})
    _string(value["artifact_id"], "artifact_id")
    _string(value["record_id"], "record_id")
    if value["record_role"] not in RECORD_ROLES:
        raise SchemaError("unknown record_role")
    digest, size = value["content_sha256_utf8"], value["content_size_bytes_utf8"]
    if (digest is None) != (size is None):
        raise SchemaError("record content hash and size nullity mismatch")
    if digest is not None:
        if not isinstance(digest, str) or not HEX64.fullmatch(digest):
            raise SchemaError("invalid record content hash")
        _integer(size, "content_size_bytes_utf8", minimum=0)
    if string_value is True and digest is None:
        raise SchemaError("string record requires UTF-8 identity")
    if string_value is False and digest is not None:
        raise SchemaError("structured record uses containing artifact identity")


def rid(label: str, components: Sequence[str]) -> str:
    raw = _string(label, "RID label").encode("ascii")
    chunks = [raw]
    for component in components:
        encoded = _string(component, "RID component", nonempty=False).encode("utf-8")
        chunks.extend((b"|", str(len(encoded)).encode("ascii"), b":", encoded))
    return b"".join(chunks).decode("utf-8")


def ordered_row_id_digest(row_ids: Sequence[str]) -> str:
    framed = bytearray()
    for row_id in row_ids:
        encoded = _string(row_id, "row_id").encode("utf-8")
        framed.extend(b"ROWSET|")
        framed.extend(str(len(encoded)).encode("ascii"))
        framed.extend(b":")
        framed.extend(encoded)
    return sha256_bytes(bytes(framed))


def expected_row_index(*, candidate_id: str, index_id: str, report_type: str,
                       row_set_id: str, derivation_name: str,
                       input_inventory_artifacts: Sequence[Mapping[str, Any]],
                       ordered_row_ids: Sequence[str]) -> dict[str, Any]:
    result = {
        "schema_version": 1, "phase": PHASE, "candidate_id": candidate_id,
        "index_id": index_id, "report_type": report_type, "row_set_id": row_set_id,
        "derivation_name": derivation_name,
        "input_inventory_artifacts": [dict(x) for x in input_inventory_artifacts],
        "ordered_row_ids": list(ordered_row_ids), "expected_count": len(ordered_row_ids),
        "ordered_row_id_digest": ordered_row_id_digest(ordered_row_ids),
    }
    validate_expected_row_index(result)
    return result


def validate_expected_row_index(value: Mapping[str, Any]) -> None:
    fields = {"schema_version", "phase", "candidate_id", "index_id", "report_type",
              "row_set_id", "derivation_name", "input_inventory_artifacts",
              "ordered_row_ids", "expected_count", "ordered_row_id_digest"}
    _keys(value, fields); _schema(value)
    if value["phase"] != PHASE:
        raise SchemaError("wrong phase")
    for name in ("candidate_id", "index_id", "report_type", "row_set_id", "derivation_name"):
        _string(value[name], name)
    if value["report_type"] not in REPORT_ROW_SETS or value["row_set_id"] not in REPORT_ROW_SETS[value["report_type"]]:
        raise SchemaError("unknown report/row set")
    refs = value["input_inventory_artifacts"]
    if not isinstance(refs, list) or not refs:
        raise SchemaError("input_inventory_artifacts must be nonempty")
    for ref in refs: validate_artifact_reference(ref)
    ids = value["ordered_row_ids"]
    if not isinstance(ids, list) or any(not isinstance(x, str) or not x for x in ids):
        raise SchemaError("ordered_row_ids invalid")
    if len(ids) != len(set(ids)):
        raise SchemaError("DUPLICATE_ROW")
    if _integer(value["expected_count"], "expected_count", minimum=0) != len(ids):
        raise ClosureError("EXPECTED_POPULATION_MISMATCH")
    if value["ordered_row_id_digest"] != ordered_row_id_digest(ids):
        raise ClosureError("EXPECTED_POPULATION_MISMATCH")


def reconcile_rows(index: Mapping[str, Any], rows: Sequence[Mapping[str, Any]]) -> None:
    validate_expected_row_index(index)
    actual = [row.get("row_id") for row in rows]
    if any(not isinstance(x, str) or not x for x in actual):
        raise SchemaError("row_id missing")
    if len(actual) != len(set(actual)):
        raise ClosureError("DUPLICATE_ROW")
    expected = index["ordered_row_ids"]
    missing, extra = set(expected) - set(actual), set(actual) - set(expected)
    if missing: raise ClosureError("MISSING_ROW")
    if extra: raise ClosureError("UNEXPECTED_ROW")
    if actual != expected or ordered_row_id_digest(actual) != index["ordered_row_id_digest"]:
        raise ClosureError("EXPECTED_POPULATION_MISMATCH")


def validate_package_environment(value: Mapping[str, Any]) -> None:
    fields = {"package_environment_mode", "lock_or_environment_artifact",
              "lock_or_environment_selection", "installed_package_inventory_artifact",
              "installed_package_capture_command", "installed_package_capture_identity"}
    _keys(value, fields)
    mode = value["package_environment_mode"]
    if mode not in {"LOCK_OR_ENVIRONMENT_ARTIFACT", "INSTALLED_PACKAGE_INVENTORY"}:
        raise SchemaError("INVALID_PACKAGE_ENVIRONMENT_MODE")
    selection_fields = {"method_id", "ordered_arguments", "runtime_executable_artifact_id",
                        "working_directory", "environment_inputs"}
    capture_fields = {"capture_tool_artifact", "runtime_executable_artifact_id",
                      "runtime_version_capture_artifact_id"}
    if mode == "LOCK_OR_ENVIRONMENT_ARTIFACT":
        if value["lock_or_environment_artifact"] is None or value["lock_or_environment_selection"] is None:
            raise SchemaError("PACKAGE_ENVIRONMENT_REQUIRED_FIELD_MISSING")
        validate_artifact_reference(value["lock_or_environment_artifact"])
        _keys(value["lock_or_environment_selection"], selection_fields)
        if any(value[x] is not None for x in ("installed_package_inventory_artifact",
                                               "installed_package_capture_command",
                                               "installed_package_capture_identity")):
            raise SchemaError("PACKAGE_ENVIRONMENT_NULL_RULE_VIOLATION")
    else:
        if value["installed_package_inventory_artifact"] is None or value["installed_package_capture_command"] is None or value["installed_package_capture_identity"] is None:
            raise SchemaError("PACKAGE_ENVIRONMENT_REQUIRED_FIELD_MISSING")
        validate_artifact_reference(value["installed_package_inventory_artifact"])
        _keys(value["installed_package_capture_identity"], capture_fields)
        if not isinstance(value["installed_package_capture_command"], list) or not value["installed_package_capture_command"]:
            raise SchemaError("installed package capture command invalid")
        if (value["lock_or_environment_artifact"] is None) != (value["lock_or_environment_selection"] is None):
            raise SchemaError("PACKAGE_ENVIRONMENT_NULL_RULE_VIOLATION")
        if value["lock_or_environment_artifact"] is not None:
            validate_artifact_reference(value["lock_or_environment_artifact"])
            _keys(value["lock_or_environment_selection"], selection_fields)


CANDIDATE_INPUT_FIELDS = {
    "schema_version", "phase", "candidate_id", "attempt_id", "status",
    "model_execution_authorized", "candidate_root", "hash_policy", "frozen_authorities",
    "slot_ledger", "candidate_artifacts", "coverage_contract_inventory",
    "source_occurrence_inventory", "schedule_manifest", "compiler_identities",
    "consumed_inventory_manifest", "producer_tool_manifests", "expected_row_indexes",
    "construction_provenance",
}

def validate_candidate_input_manifest(value: Mapping[str, Any]) -> None:
    _keys(value, CANDIDATE_INPUT_FIELDS); _schema(value)
    if value["phase"] != PHASE: raise SchemaError("wrong phase")
    if value["model_execution_authorized"] is not False:
        raise ClosureError("MODEL_AUTHORIZATION_NOT_FALSE")
    if value["hash_policy"] != "EXACT_BYTES_SHA256": raise SchemaError("wrong hash policy")
    for name in ("candidate_id", "attempt_id", "status", "candidate_root"):
        _string(value[name], name)
    for name in ("candidate_artifacts", "producer_tool_manifests", "expected_row_indexes"):
        if not isinstance(value[name], list): raise SchemaError(f"{name} must be a list")
        for ref in value[name]: validate_artifact_reference(ref)
    for name in ("slot_ledger", "coverage_contract_inventory", "source_occurrence_inventory",
                 "schedule_manifest", "consumed_inventory_manifest", "construction_provenance"):
        validate_artifact_reference(value[name])
    if not isinstance(value["frozen_authorities"], list) or not value["frozen_authorities"]:
        raise SchemaError("frozen authorities required")
    if not isinstance(value["compiler_identities"], list) or not value["compiler_identities"]:
        raise SchemaError("compiler identities required")


EVIDENCE_MANIFEST_FIELDS = {
    "schema_version", "phase", "candidate_id", "status", "model_execution_authorized",
    "candidate_input_manifest", "coverage_v3_direct_evidence", "delegated_reports",
    "producer_execution_provenances", "report_execution_map", "report_status_summary",
    "overall_audit_state", "failure_reasons",
}

def validate_candidate_evidence_manifest(value: Mapping[str, Any]) -> None:
    _keys(value, EVIDENCE_MANIFEST_FIELDS); _schema(value)
    if value["phase"] != PHASE: raise SchemaError("wrong phase")
    if value["model_execution_authorized"] is not False:
        raise ClosureError("MODEL_AUTHORIZATION_NOT_FALSE")
    validate_artifact_reference(value["candidate_input_manifest"])
    validate_artifact_reference(value["coverage_v3_direct_evidence"])
    if not isinstance(value["delegated_reports"], list) or len(value["delegated_reports"]) != 9:
        raise SchemaError("nine delegated reports required")
    for ref in value["delegated_reports"]: validate_artifact_reference(ref)
    if value["overall_audit_state"] not in {"ALL_REPORTS_PASS", "BLOCKED", "UNRESOLVED"}:
        raise SchemaError("invalid overall_audit_state")
    maps = value["report_execution_map"]
    if not isinstance(maps, list) or len(maps) != 10:
        raise SchemaError("exactly ten report execution mappings required")
    seen = set()
    for item in maps:
        _keys(item, {"report_artifact_id", "report_type", "producer_execution_id"})
        if item["report_artifact_id"] in seen: raise SchemaError("duplicate report mapping")
        seen.add(item["report_artifact_id"])


REPORT_ENVELOPE_FIELDS = {
    "schema_version", "phase", "candidate_id", "contract_id", "report_type", "status",
    "candidate_input_manifest_sha256", "candidate_input_manifest_size_bytes",
    "producer_tool_manifest_sha256", "producer_tool_manifest_size_bytes",
    "producer_execution_id", "producer_execution_provenance_sha256",
    "producer_execution_provenance_size_bytes", "rule_authorities", "compiler_relevance",
    "compiler_identity_id", "input_artifacts", "row_sets", "aggregate", "failure_reasons",
}

def validate_report_envelope(value: Mapping[str, Any], *, resolver: "ArtifactResolver | None" = None,
                             bound_indexes: Sequence[Mapping[str, Any]] = ()) -> None:
    _keys(value, REPORT_ENVELOPE_FIELDS); _schema(value)
    if value["phase"] != PHASE or value["status"] not in STATUSES:
        raise SchemaError("invalid report phase/status")
    report_type = _string(value["report_type"], "report_type")
    if report_type not in REPORT_ROW_SETS: raise SchemaError("unknown report_type")
    row_sets = value["row_sets"]
    if not isinstance(row_sets, list) or [r.get("row_set_id") if isinstance(r, dict) else None for r in row_sets] != list(REPORT_ROW_SETS[report_type]):
        raise SchemaError("row_sets do not match frozen report type/order")
    if resolver is None:
        raise ClosureError("expected-index resolver required")
    for row_set in row_sets:
        validate_row_set(row_set, resolver=resolver, bound_indexes=bound_indexes,
                         candidate_id=value["candidate_id"], report_type=report_type,
                         require_closed=value["status"] == "PASS")
    validate_reason_records(value["failure_reasons"])
    relevance = value["compiler_relevance"]
    _keys(relevance, {"status", "reason_code"})
    if relevance["status"] not in {"REQUIRED", "NOT_APPLICABLE"}:
        raise SchemaError("COMPILER_RELEVANCE_INVALID")
    if relevance["status"] == "REQUIRED" and not isinstance(value["compiler_identity_id"], str):
        raise SchemaError("COMPILER_RELEVANCE_INVALID")
    if relevance["status"] == "NOT_APPLICABLE" and value["compiler_identity_id"] is not None:
        raise SchemaError("COMPILER_RELEVANCE_INVALID")
    for name in ("candidate_input_manifest_sha256", "producer_tool_manifest_sha256",
                 "producer_execution_provenance_sha256"):
        if not HEX64.fullmatch(_string(value[name], name)): raise SchemaError(f"invalid {name}")
    for name in ("candidate_input_manifest_size_bytes", "producer_tool_manifest_size_bytes",
                 "producer_execution_provenance_size_bytes"):
        _integer(value[name], name, minimum=0)
    if report_type=="COVERAGE_V3_DIRECT" and value["status"]=="PASS":
        raise ClosureError("UNRESOLVED_REQUIREMENT: full direct-row variant/aggregate closure is not implemented")


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def validate_reason_records(reasons: Any) -> None:
    if not isinstance(reasons, list):
        raise SchemaError("reason records must be an array")
    for reason in reasons:
        _keys(reason, {"code", "contract_id", "detail_reference"}, optional={"row_id", "artifact_id"})
        if reason["code"] not in INTERFACE_REASON_CODES:
            raise SchemaError("unknown interface reason code")
        _string(reason["contract_id"], "contract_id")
        for name in ("row_id", "artifact_id"):
            if name in reason:
                _string(reason[name], name)
        validate_record_reference(reason["detail_reference"])


class ArtifactResolver:
    """Resolve only pre-bound exact-byte artifacts; never select an inventory."""

    def __init__(self, root: Path, artifacts: Sequence[Mapping[str, Any]]):
        self.root = root.resolve()
        self.artifacts: dict[str, dict[str, Any]] = {}
        for ref in artifacts:
            validate_artifact_reference(ref)
            if ref["artifact_id"] in self.artifacts:
                raise ClosureError("duplicate bound artifact ID")
            self.artifacts[ref["artifact_id"]] = dict(ref)

    def read(self, artifact_id: str, *, role: str | None = None) -> bytes:
        if artifact_id not in self.artifacts:
            raise ClosureError("unbound artifact")
        ref = self.artifacts[artifact_id]
        if role is not None and ref["artifact_role"] != role:
            raise ClosureError("artifact role mismatch")
        verify_artifact_reference(ref, self.root)
        return (self.root / ref["path"]).read_bytes()

    def json(self, artifact_id: str, *, role: str | None = None) -> Any:
        def unique_object(pairs):
            value = {}
            for key, item in pairs:
                if key in value:
                    raise ValueError("duplicate JSON field")
                value[key] = item
            return value
        try:
            return json.loads(self.read(artifact_id, role=role).decode("utf-8"),
                              object_pairs_hook=unique_object,
                              parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-JSON number")))
        except (ValueError, UnicodeError) as exc:
            raise SchemaError("invalid JSON artifact") from exc

    def verify_record_content(self, ref: Mapping[str, Any], content: str) -> None:
        validate_record_reference(ref, string_value=True)
        artifact = self.json(ref["artifact_id"])
        # This core resolver deliberately supports only the record selector it
        # can prove. Other producers need their own closed record adapters.
        if ref["record_role"] != "EXPECTED_OUTPUT" or not isinstance(artifact, dict) or not isinstance(artifact.get("cases"), list):
            raise ClosureError("unsupported record selector")
        matches = [row for row in artifact["cases"] if isinstance(row, dict) and row.get("case_id") == ref["record_id"]]
        if len(matches) != 1 or matches[0].get("expected_output") != content:
            raise ClosureError("record not present in bound artifact")
        encoded = content.encode("utf-8")
        if ref["content_sha256_utf8"] != sha256_bytes(encoded) or ref["content_size_bytes_utf8"] != len(encoded):
            raise ClosureError("record content identity mismatch")


def observed_population(expected_ids: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not isinstance(rows, list):
        raise SchemaError("rows must be an array")
    actual = []
    for row in rows:
        if not isinstance(row, dict):
            raise SchemaError("row object required")
        actual.append(_string(row.get("row_id"), "row_id"))
    seen: set[str] = set(); duplicates: list[str] = []; unexpected: list[str] = []
    expected = set(expected_ids)
    for row_id in actual:
        if row_id in seen and row_id not in duplicates:
            duplicates.append(row_id)
        if row_id not in expected and row_id not in unexpected:
            unexpected.append(row_id)
        seen.add(row_id)
    return {"observed_row_count": len(actual), "unique_row_count": len(seen),
            "ordered_row_id_digest": ordered_row_id_digest(actual),
            "missing_ids": [x for x in expected_ids if x not in seen],
            "duplicate_ids": duplicates, "unexpected_ids": unexpected}


def validate_row_set(value: Mapping[str, Any], *, resolver: ArtifactResolver,
                     bound_indexes: Sequence[Mapping[str, Any]], candidate_id: str,
                     report_type: str, require_closed: bool = True) -> None:
    _keys(value, {"row_set_id", "expected_row_index", "observed_population", "rows"})
    if report_type not in REPORT_ROW_SETS or value["row_set_id"] not in REPORT_ROW_SETS[report_type]:
        raise SchemaError("unknown row set")
    ref = value["expected_row_index"]
    _keys(ref, {"artifact_id", "index_id", "sha256", "size_bytes", "expected_count"})
    _integer(ref["size_bytes"], "size_bytes", minimum=0)
    _integer(ref["expected_count"], "expected_count", minimum=0)
    candidates = [a for a in bound_indexes if a.get("artifact_id") == ref["artifact_id"]]
    if len(candidates) != 1 or resolver.artifacts.get(ref["artifact_id"]) != candidates[0]:
        raise ClosureError("unbound or duplicate expected index")
    bound = candidates[0]
    if ref["sha256"] != bound["sha256"] or ref["size_bytes"] != bound["size_bytes"]:
        raise ClosureError("expected index identity mismatch")
    index = resolver.json(ref["artifact_id"], role="EXPECTED_ROW_INDEX")
    validate_expected_row_index(index)
    if (index["index_id"], index["candidate_id"], index["report_type"], index["row_set_id"], index["expected_count"]) != (
            ref["index_id"], candidate_id, report_type, value["row_set_id"], ref["expected_count"]):
        raise ClosureError("expected index identity/population mismatch")
    for artifact in index["input_inventory_artifacts"]:
        if resolver.artifacts.get(artifact["artifact_id"]) != artifact:
            raise ClosureError("unbound index input inventory")
        resolver.read(artifact["artifact_id"])
    population = value["observed_population"]
    _keys(population, {"observed_row_count", "unique_row_count", "ordered_row_id_digest",
                       "missing_ids", "duplicate_ids", "unexpected_ids"})
    for name in ("observed_row_count", "unique_row_count"):
        _integer(population[name], name, minimum=0)
    if population != observed_population(index["ordered_row_ids"], value["rows"]):
        raise ClosureError("AGGREGATE_INCONSISTENCY")
    if require_closed:
        reconcile_rows(index, value["rows"])
