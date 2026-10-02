"""Closed SCIENTIFIC_EVIDENCE selectors for the frozen nested V3.2 payload.

No recursive arbitrary-JSON search, role-only authorization, or earlier-report
read permission. This consumes already bound input/owning-row logical objects.
It is not a report loader or a scientific producer/provenance implementation.
"""
from copy import deepcopy
from .interfaces import rid, SchemaError, ClosureError, canonical_json_bytes

FIELDS = {
    "V32INVENTORY": set("schema_version record_id program_id source_reference coordinate_convention occurrences bindings presentation_associations eligible_v3_5_occurrence_ids".split()),
    "V32BINDING": set("record_id binding_id declaration_occurrence_id identifier datatype read_occurrence_ids write_occurrence_ids".split()),
    "V32OCCRECORD": set("record_id inventory_ordinal occurrence".split()),
    "V32GRAPH": set("schema_version record_id program_id source_inventory_reference node_ids edge_ids expression_children control_contexts".split()),
    "V32STATE": set("schema_version record_id program_id graph_reference definitions read_definitions dependency_edges output_ancestry decoder_ancestry analysis_status".split()),
    "V32PREMAP": set("schema_version record_id program_id prospective_contract_reference source_inventory_reference graph_reference state_reference required_occurrences direct_mapping_candidates authorized_equivalence_correspondences equivalence_internal_members still_unmatched_occurrence_ids context_status scientific_reason_codes".split()),
    "V32REQ": set("record_id requirement_occurrence_id canonical_contract_key_id prospective_contract_reference required_multiplicity attachment_references".split()),
    "V32ROREGION": {"schema_version", "record_id", "proof"},
    "V32ROCERT": set("schema_version record_id occurrence_reference region_reference reason_codes mechanical_disposition".split()),
    "V32ROSUPPORT": set("schema_version record_id proof_kind root_occurrence_id value".split()),
    "V32DEFINITION": set("record_id writer_occurrence_id binding_reference control_context".split()),
}
STAGES = {"V32INVENTORY": 0, "V32BINDING": 0, "V32OCCRECORD": 0,
          "V32GRAPH": 1, "V32DEFINITION": 2, "V32STATE": 3,
          "V32REQ": 4, "V32PREMAP": 5, "V32ROSUPPORT": 6, "V32ROREGION": 7, "V32ROCERT": 8}
REFERENCE_FIELDS = set("artifact_id record_id record_role content_sha256_utf8 content_size_bytes_utf8".split())
ROW_FIELDS = set("payload_schema_version row_id program_id prospective_contract_reference source_inventory_reference graph_reference state_reference pre_disposition_mapping_context_reference direct_required_mappings authorized_equivalence_required_mappings equivalence_internal_accounting reference_only_regions reference_only_certificates supporting_proofs evidence_records uncovered_occurrences duplicate_dispositions source_offsets graph_paths evidence_record_references status scientific_reason_codes".split())


def _schema(value, family, program):
    if not isinstance(value, dict) or set(value) != FIELDS[family]:
        raise SchemaError("V32_REPRESENTATION_MALFORMED: " + family)
    if "schema_version" in value and (type(value["schema_version"]) is not int or value["schema_version"] != 1):
        raise SchemaError("V32_REPRESENTATION_MALFORMED: VERSION")
    if "program_id" in value and value["program_id"] != program:
        raise ClosureError("V32_REFERENCE_UNCLOSED: PROGRAM")


class EvidenceResolver:
    """Selectors hardcoded to exact frozen container paths and producer stages.

    Independent replay still reconstructs source-derived contents and bindings;
    resolving a well-shaped record alone is never a proof of its semantics.
    The constructor consumes logical objects, not paths to earlier reports.
    """
    def __init__(self, inventory_artifact, rows, *, input_artifact_id, direct_artifact_id, candidate_id, bound_candidate_id):
        if candidate_id != bound_candidate_id:
            raise ClosureError("V32_REFERENCE_UNCLOSED: CANDIDATE_BINDING")
        if not isinstance(inventory_artifact, dict) or set(inventory_artifact) != {"schema_version", "candidate_id", "programs"}:
            raise SchemaError("V32_REPRESENTATION_MALFORMED: INVENTORY_ARTIFACT")
        if type(inventory_artifact["schema_version"]) is not int or inventory_artifact["schema_version"] != 1 or inventory_artifact["candidate_id"] != candidate_id:
            raise ClosureError("V32_REFERENCE_UNCLOSED: INVENTORY_BINDING")
        if not isinstance(inventory_artifact["programs"], list) or not isinstance(rows, list):
            raise SchemaError("V32_REPRESENTATION_MALFORMED: CONTAINER")
        self.input_artifact_id, self.direct_artifact_id = input_artifact_id, direct_artifact_id
        self._programs = deepcopy(inventory_artifact["programs"])
        self._rows = deepcopy(rows)
        self._records = []
        for program in self._programs:
            pid = program.get("program_id")
            self._add("V32INVENTORY", pid, None, "programs[]", program, rid("V32INVENTORY", [pid]))
            for binding in program["bindings"]:
                self._add("V32BINDING", pid, None, "programs[].bindings[]", binding,
                          rid("V32BINDING", [pid, binding["declaration_occurrence_id"]]))
                if binding["binding_id"] != binding["record_id"]:
                    raise SchemaError("V32_REPRESENTATION_MALFORMED: BINDING_ID")
            for occurrence in program["occurrences"]:
                self._add("V32OCCRECORD", pid, None, "programs[].occurrences[]", occurrence,
                          rid("V32OCCRECORD", [pid, occurrence["occurrence"]["occurrence_id"]]))
        for row in self._rows:
            if not isinstance(row, dict) or set(row) != ROW_FIELDS or type(row["payload_schema_version"]) is not int or row["payload_schema_version"] != 1:
                raise SchemaError("V32_REPRESENTATION_MALFORMED: ROW")
            pid, owner = row["program_id"], row["row_id"]
            if owner != rid("V3.2", [pid]):
                raise ClosureError("V32_REFERENCE_UNCLOSED: OWNER")
            records = row["evidence_records"]
            if not isinstance(records, dict) or set(records) != {"typed_graph", "state_control_analysis", "pre_disposition_mapping_context"}:
                raise SchemaError("V32_REPRESENTATION_MALFORMED: EVIDENCE_CONTAINER")
            for family, key in (("V32GRAPH", "typed_graph"), ("V32STATE", "state_control_analysis"), ("V32PREMAP", "pre_disposition_mapping_context")):
                value = records[key]
                if value is None:
                    if row["status"] == "PASS":
                        raise ClosureError("V32_REFERENCE_UNCLOSED: NULL_PASS_RECORD")
                    continue
                self._add(family, pid, owner, "evidence_records." + key, value, rid(family, [pid]))
                if family == "V32STATE":
                    for definition in value["definitions"]:
                        self._add("V32DEFINITION", pid, owner, "evidence_records.state_control_analysis.definitions[]", definition,
                                  rid("V32DEFINITION", [pid, definition["writer_occurrence_id"]]))
                elif family == "V32PREMAP":
                    for i, requirement in enumerate(value["required_occurrences"], 1):
                        self._add("V32REQ", pid, owner, "evidence_records.pre_disposition_mapping_context.required_occurrences[]", requirement,
                                  rid("V32REQ", [pid, str(i)]))
            for family, key in (("V32ROREGION", "reference_only_regions"), ("V32ROCERT", "reference_only_certificates"), ("V32ROSUPPORT", "supporting_proofs")):
                if not isinstance(row[key], list):
                    raise SchemaError("V32_REPRESENTATION_MALFORMED: PROOF_ARRAY")
                for value in row[key]:
                    if family == "V32ROREGION":
                        args = [pid, value["proof"]["ownership"]["owner_root_id"]]
                        if value["proof"]["program_id"] != pid:
                            raise ClosureError("V32_REFERENCE_UNCLOSED: REGION_PROGRAM")
                    elif family == "V32ROCERT":
                        # Exact inventory wrapper must select the occurrence.
                        oid = value["occurrence_reference"]["record_id"]
                        selected = [r["occurrence"]["occurrence_id"] for p in self._programs if p["program_id"] == pid
                                    for r in p["occurrences"] if r["record_id"] == oid]
                        if len(selected) != 1:
                            raise ClosureError("V32_REFERENCE_UNCLOSED: CERT_OCCURRENCE_SELECTOR")
                        args = [pid, selected[0]]
                    else:
                        args = [pid, value["proof_kind"], value["root_occurrence_id"]]
                    self._add(family, pid, owner, key + "[]", value, rid(family, args))
        identities = [r["value"]["record_id"] for r in self._records]
        if len(identities) != len(set(identities)):
            raise ClosureError("V32_REFERENCE_UNCLOSED: DUPLICATE_RECORD_ID")

    def _add(self, family, program, owner, path, value, expected_id):
        _schema(value, family, program)
        if value["record_id"] != expected_id:
            raise ClosureError("V32_REFERENCE_UNCLOSED: RID_FAMILY_OR_SELECTOR")
        self._records.append(dict(family=family, program=program, owner=owner, path=path,
                                  stage=STAGES[family], value=value))

    def resolve(self, reference, *, family, program_id, owning_row_id, consumer_stage, expected_path=None):
        if family not in FIELDS or not isinstance(reference, dict) or set(reference) != REFERENCE_FIELDS:
            raise SchemaError("V32_REFERENCE_UNCLOSED: REFERENCE_SCHEMA")
        if reference["record_role"] != "SCIENTIFIC_EVIDENCE" or reference["content_sha256_utf8"] is not None or reference["content_size_bytes_utf8"] is not None:
            raise ClosureError("V32_REFERENCE_UNCLOSED: RECORD_ROLE_OR_CONTENT_KIND")
        if type(consumer_stage) is not int or consumer_stage < 0:
            raise SchemaError("V32_REFERENCE_UNCLOSED: CONSUMER_STAGE")
        input_record = STAGES[family] == 0
        expected_artifact = self.input_artifact_id if input_record else self.direct_artifact_id
        if reference["artifact_id"] != expected_artifact:
            raise ClosureError("V32_REFERENCE_UNCLOSED: ARTIFACT_OR_PROVENANCE_BINDING")
        selected = [r for r in self._records if r["value"]["record_id"] == reference["record_id"]]
        if len(selected) != 1:
            raise ClosureError("V32_REFERENCE_UNCLOSED: SELECTOR_CARDINALITY")
        record = selected[0]
        if (record["family"] != family or record["program"] != program_id
                or (not input_record and record["owner"] != owning_row_id)
                or owning_row_id != rid("V3.2", [program_id])
                or record["stage"] >= consumer_stage
                or (expected_path is not None and record["path"] != expected_path)):
            raise ClosureError("V32_REFERENCE_UNCLOSED: TYPE_PROGRAM_OWNER_STAGE_OR_PATH")
        return deepcopy(record["value"])
