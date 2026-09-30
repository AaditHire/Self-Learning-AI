"""Producer-tool, compiler and post-execution closure for schema version 1."""
from __future__ import annotations
from typing import Any, Mapping, Sequence
from .interfaces import (HEX40, ClosureError, SchemaError, _keys, _schema,
                         validate_artifact_reference, validate_package_environment, rid)

PRODUCER_FIELDS = {"schema_version","producer_id","contract_ids","report_types","repository_commit_sha","repository_root_tree_id","producer_controlled_pathspecs","producer_code_dirty_state","entrypoint","dependency_access_observer","explicit_uncommitted_dependencies","repository_state_inventory","schemas","prompts_and_templates","static_lookups","producer_configurations","compiler_wrapper_and_configuration","tokenizer_and_chat_template_configuration","runtime_executable","runtime_version_capture","runtime_name","runtime_vendor","runtime_version","runtime_architecture","package_environment_mode","lock_or_environment_artifact","lock_or_environment_selection","installed_package_inventory_artifact","installed_package_capture_command","installed_package_capture_identity","execution_command","working_directory","environment_allowlist","locale","encoding","timeouts","resource_output_limits","runtime_closure_status","rule_authorities","output_schema_version","dependency_enumeration_method","unresolved_dependencies"}

def validate_producer_tool_manifest(value: Mapping[str, Any]) -> None:
    _keys(value, PRODUCER_FIELDS); _schema(value)
    if not HEX40.fullmatch(str(value["repository_commit_sha"])) or not HEX40.fullmatch(str(value["repository_root_tree_id"])): raise SchemaError("invalid repository identity")
    if value["producer_code_dirty_state"] != "CLEAN_AGAINST_BOUND_COMMIT": raise ClosureError("DIRTY_PRODUCER_CODE")
    if value["runtime_closure_status"] != "CLOSED" or value["unresolved_dependencies"] != []: raise ClosureError("EXECUTION_DEPENDENCY_CLOSURE_FAILURE")
    if value["output_schema_version"] != 1: raise SchemaError("UNSUPPORTED_SCHEMA_VERSION")
    for name in ("contract_ids","report_types","producer_controlled_pathspecs","execution_command","rule_authorities"):
        if not isinstance(value[name], list) or (name in {"contract_ids","report_types","execution_command"} and not value[name]): raise SchemaError(f"{name} invalid")
    if len(value["report_types"]) != len(set(value["report_types"])): raise SchemaError("duplicate report type")
    for name in ("entrypoint","dependency_access_observer","repository_state_inventory","runtime_executable","runtime_version_capture"): validate_artifact_reference(value[name])
    for name in ("explicit_uncommitted_dependencies","schemas","prompts_and_templates","static_lookups","producer_configurations","compiler_wrapper_and_configuration","tokenizer_and_chat_template_configuration"):
        if not isinstance(value[name], list): raise SchemaError(f"{name} invalid")
        for ref in value[name]: validate_artifact_reference(ref)
    validate_package_environment({name: value[name] for name in ("package_environment_mode","lock_or_environment_artifact","lock_or_environment_selection","installed_package_inventory_artifact","installed_package_capture_command","installed_package_capture_identity")})

COMPILER_FIELDS = {"schema_version","phase","compiler_identity_id","compiler_binary","compiler_provenance","compiler_wrapper","compiler_configuration","runtime_executable","runtime_version_capture","source_commit_sha","closure_status","failure_reasons"}
def validate_compiler_identity(value: Mapping[str, Any]) -> None:
    _keys(value, COMPILER_FIELDS); _schema(value)
    for name in ("compiler_binary","compiler_provenance","compiler_wrapper","compiler_configuration","runtime_executable","runtime_version_capture"): validate_artifact_reference(value[name])
    if not HEX40.fullmatch(str(value["source_commit_sha"])): raise SchemaError("invalid compiler source commit")
    if value["closure_status"] != "CLOSED" or value["failure_reasons"] != []: raise ClosureError("COMPILER_IDENTITY_MISMATCH")

EXECUTION_FIELDS = {"schema_version","phase","candidate_id","producer_id","execution_id","report_types","candidate_input_manifest","producer_tool_manifest_sha256","producer_tool_manifest_size_bytes","bound_repository_commit_sha","bound_repository_root_tree_id","observed_repository_commit_sha","observed_repository_root_tree_id","actual_execution_arguments","actual_working_directory","actual_environment_configuration","execution_start","execution_end","process_exit_status","repository_state_inventory","repository_local_read_set","dependency_access_observer","runtime_executable","runtime_version_capture","package_environment_identity","compiler_identity_id","dependency_closure_result","failure_reasons","status"}

def aggregate_execution_compiler_id(reports: Sequence[Mapping[str, Any]], candidate_compiler_id: str) -> str | None:
    for report in reports:
        relevance = report["compiler_relevance"]
        if relevance["status"] == "REQUIRED":
            if report.get("compiler_identity_id") != candidate_compiler_id: raise ClosureError("COMPILER_RELEVANCE_INVALID")
        elif relevance["status"] == "NOT_APPLICABLE":
            if report.get("compiler_identity_id") is not None: raise ClosureError("COMPILER_RELEVANCE_INVALID")
        else: raise ClosureError("COMPILER_RELEVANCE_INVALID")
    return candidate_compiler_id if any(r["compiler_relevance"]["status"] == "REQUIRED" for r in reports) else None

def validate_execution_provenance(value: Mapping[str, Any], tool: Mapping[str, Any], reports: Sequence[Mapping[str, Any]], candidate_compiler_id: str) -> None:
    _keys(value, EXECUTION_FIELDS); _schema(value); validate_producer_tool_manifest(tool)
    if value["status"] not in {"PASS","FAIL","UNRESOLVED"}: raise SchemaError("invalid execution status")
    if value["report_types"] != tool["report_types"] or value["report_types"] != [r["report_type"] for r in reports]: raise ClosureError("PRODUCER_EXECUTION_PROVENANCE_MISMATCH")
    if value["bound_repository_commit_sha"] != tool["repository_commit_sha"] or value["observed_repository_commit_sha"] != tool["repository_commit_sha"]: raise ClosureError("REPOSITORY_COMMIT_MISMATCH")
    if value["bound_repository_root_tree_id"] != tool["repository_root_tree_id"] or value["observed_repository_root_tree_id"] != tool["repository_root_tree_id"]: raise ClosureError("REPOSITORY_TREE_MISMATCH")
    if value["actual_execution_arguments"] != tool["execution_command"] or value["actual_working_directory"] != tool["working_directory"]: raise ClosureError("PRODUCER_EXECUTION_PROVENANCE_MISMATCH")
    for point, label in (("execution_start","START"),("execution_end","END")):
        _keys(value[point], {"event_id","observed_at_utc"})
        if value[point]["event_id"] != rid("EXECUTION_EVENT", [value["execution_id"], label]): raise SchemaError("execution event ID mismatch")
    status=value["process_exit_status"]; _keys(status,{"kind","exit_code","signal"})
    valid=((status["kind"]=="EXITED" and isinstance(status["exit_code"],int) and status["signal"] is None) or (status["kind"]=="SIGNALED" and status["exit_code"] is None and isinstance(status["signal"],str) and bool(status["signal"])) or (status["kind"]=="UNRESOLVED" and status["exit_code"] is None and status["signal"] is None))
    if not valid: raise SchemaError("invalid process exit status")
    for name in ("candidate_input_manifest","repository_state_inventory","repository_local_read_set","dependency_access_observer","runtime_executable","runtime_version_capture"): validate_artifact_reference(value[name])
    if value["compiler_identity_id"] != aggregate_execution_compiler_id(reports,candidate_compiler_id): raise ClosureError("EXECUTION_COMPILER_RELEVANCE_MISMATCH")
    if value["dependency_closure_result"] not in {"CLOSED","FAILED","UNRESOLVED"}: raise SchemaError("invalid dependency closure")
    if value["status"]=="PASS" and (status!={"kind":"EXITED","exit_code":0,"signal":None} or value["dependency_closure_result"]!="CLOSED" or value["failure_reasons"]): raise ClosureError("EXECUTION_DEPENDENCY_CLOSURE_FAILURE")
