"""Non-executing core-closure checkpoint producer, not a scientific validator.

Only frozen authority metadata, pure source templates, and raw historical
strings for overlap are read. Expected labels are NEVER parsed. No historical
case, compiler, model, candidate builder, or delegated producer is executed.
Generated JSON is diagnostic, never an EXPECTED_ROW_INDEX or candidate input.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STARTING_HEAD = "152673769d29b47c458b8fac0c153f8c4778fd02"
PREREG_BASE = "b44d1c73de1be47b541f76d67c88541a5d90f3fa"
OUT = ROOT / "research/implementation_notes/coverage_v3_core_closure"
PROTOCOLS = "research/protocols/"
INTERFACE = PROTOCOLS + "phase3c_conf1_delegated_evidence_interfaces_proposed.md"
COVERAGE = PROTOCOLS + "phase3c_conf1_coverage_v3_proposed.md"
LEDGER = PROTOCOLS + "phase3c_conf1_slots.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def require(condition: bool, description: str) -> None:
    if not condition:
        raise RuntimeError("STOP_FROZEN_IDENTITY_OR_CLOSURE_ISSUE: " + description)


def lf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def verify_protected_inputs() -> dict:
    """Exact hashes plus Git clean-filter blobs: do not conflate CRLF with edits."""
    freeze_path = PROTOCOLS + "phase3c_conf1_delegated_evidence_interfaces_freeze.json"
    data = (ROOT / freeze_path).read_bytes()
    require(sha(data) == "bd7a7fc6862ce049c1fdf363f763e1a3a17808132291b9064e3c6f26fb720948",
            "delegated interface freeze manifest")
    manifest = json.loads(data)
    authorities = []
    for name, authority in manifest["upstream_authorities"].items():
        path = authority["path"]
        data = (ROOT / path).read_bytes()
        policy = authority.get("hash_policy", "EXACT_BYTES_SHA256")
        expected = authority.get("sha256_exact_bytes", authority.get("sha256"))
        require(len(data) == authority["size_bytes"], name + " exact size")
        require(sha(lf(data) if policy == "SHA256_UTF8_CRLF_TO_LF" else data) == expected,
                name + " declared-policy hash")
        if "sha256_utf8_crlf_to_lf" in authority:
            require(sha(lf(data)) == authority["sha256_utf8_crlf_to_lf"], name + " LF hash")
        require(git("hash-object", "--", path).decode().strip() == authority["git_blob"],
                name + " worktree Git clean-filter blob")
        require(git("rev-parse", "HEAD:" + path).decode().strip() == authority["git_blob"],
                name + " committed Git blob")
        authorities.append({"name": name, **authority, "verification": "MATCH",
                            "actual_sha256_exact_bytes": sha(data)})
    regions = []
    for name, filename in (
        ("delegated", "phase3c_conf1_delegated_evidence_interfaces_freeze.json"),
        ("coverage", "phase3c_conf1_coverage_v3_freeze.json"),
        ("paired", "phase3c_conf1_paired_scaffold_normalization_freeze.json"),
        ("input", "phase3c_conf1_input_domain_case_classes_and_training_amendment_freeze.json"),
    ):
        m = json.loads((ROOT / PROTOCOLS / filename).read_bytes())
        exact = name == "delegated"
        path = (m["frozen_interface_path"] if exact else m["frozen_coverage_v3_path"]
                if name == "coverage" else m["frozen_amendment_path"])
        frozen = (ROOT / path).read_bytes()
        frozen = frozen if exact else lf(frozen)
        expected_sha = (m["frozen_interface_sha256_exact_bytes"] if exact else
                        m["frozen_coverage_v3_sha256_lf_normalized"] if name == "coverage" else
                        m["frozen_amendment_sha256_lf_normalized"])
        require(sha(frozen) == expected_sha, name + " frozen file")
        commit = m.get("approved_coverage_v3_commit", m.get("approved_proposal_commit"))
        approved_path = m.get("approved_coverage_v3_path", m.get("approved_proposal_path"))
        approved = git("show", commit + ":" + approved_path)
        approved = approved if exact else lf(approved)
        approved_sha = m.get("approved_coverage_v3_sha256_lf_normalized", m.get(
            "approved_proposal_sha256_exact_bytes" if exact else "approved_proposal_sha256_lf_normalized"))
        require(sha(approved) == approved_sha, name + " approved file")
        require(git("rev-parse", commit + ":" + approved_path).decode().strip() == m.get(
            "approved_coverage_v3_git_blob", m.get("approved_proposal_git_blob")), name + " approved blob")
        heading = b"\n" + m["normative_region_start_heading"].encode()
        frozen_tail = frozen[frozen.index(heading) + 1:]
        approved_tail = approved[approved.index(heading) + 1:]
        require(frozen_tail == approved_tail, name + " approved normative region equality")
        region_sha = m["frozen_normative_region_sha256_exact_bytes" if exact else
                       "frozen_normative_region_sha256_lf_normalized"]
        require(sha(frozen_tail) == region_sha, name + " normative hash")
        if "normative_region_byte_count" in m:
            require(len(frozen_tail) == m["normative_region_byte_count"], name + " normative size")
        if exact:
            require(len(frozen) == m["frozen_interface_size_bytes"], name + " size")
            require(git("hash-object", "--", path).decode().strip() == m["frozen_interface_git_blob"],
                    name + " frozen blob")
        regions.append({"name": name, "path": path, "approved_commit": commit,
                        "sha256": region_sha, "size_bytes": len(frozen_tail), "approved_byte_equal": True})
    paths = [ROOT / PROTOCOLS / "phase3c_conf1_v3_synthetic_fixture_manifest.json",
             ROOT / PROTOCOLS / "phase3c_conf1_v3_synthetic_expected_labels.json",
             *sorted((ROOT / PROTOCOLS / "phase3c_conf1_v3_synthetic_fixtures").glob("*.json"))]
    require(len(paths) == 15, "preregistration file population")
    prereg = []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        blob = git("rev-parse", PREREG_BASE + ":" + relative).decode().strip()
        require(git("hash-object", "--", relative).decode().strip() == blob, "preregistration " + relative)
        require(git("rev-parse", "HEAD:" + relative).decode().strip() == blob, "preregistration HEAD " + relative)
        # Generic byte-integrity only, including expected labels: no JSON load,
        # string extraction, label inspection, printing, or classifier access.
        raw = path.read_bytes()
        prereg.append({"path": relative, "baseline_git_blob": blob,
                       "sha256_exact_bytes": sha(raw), "size_bytes": len(raw), "verification": "UNCHANGED"})
    return {"schema_version": 1, "kind": "DEVELOPMENT_INTEGRITY_DIAGNOSTIC",
            "starting_head": STARTING_HEAD, "authorities": authorities, "normative_regions": regions,
            "interface_freeze_sha256_exact_bytes": sha((ROOT / freeze_path).read_bytes()),
            "preregistration": prereg, "expected_labels_parsed": False,
            "git_blob_policy": "Git clean filter, with exact working-file hashes independently bound"}


def authority(path: str, section: str, selector: str | None = None) -> dict:
    return {"path": path, "section": section, "selector": selector}


def derive_diagnostic(ledger: dict, contracts: list) -> tuple[dict, dict]:
    """Expose incompleteness; no mapping, activity, output, or case classification."""
    from self_learning_ai.conf1_v3.contracts import (
        ARRAY_CLASSES, NUMERIC_CLASSES, canonical_numeric_witness_slot, v35_expected_row_ids,
    )
    from self_learning_ai.conf1_v3.interfaces import SchemaError, ordered_row_id_digest, rid
    require(len(contracts) == len({c.program_id for c in contracts}) == 184, "contract population")
    training = [c for c in contracts if c.task_kind == "training"]
    require(len(training) == 120, "training population")
    rows = v35_expected_row_ids(contracts, diagnostic_incomplete=True)
    try:
        v35_expected_row_ids(contracts)
    except SchemaError as exc:
        refusal = str(exc)
    else:
        raise RuntimeError("STOP: incomplete core unexpectedly accepted as authoritative")
    missing = []
    records = []
    catalog = {key.key_id: key for contract in contracts for key in contract.canonical_keys}
    catalog_ids = {key_id: index for index, key_id in enumerate(sorted(catalog, key=lambda k: k.encode("utf-8")))}
    slots = {s.get("slot_id", s.get("task_id")): (group, index, s)
             for group, values in ledger["slots"].items() for index, s in enumerate(values)}
    for contract in sorted(contracts, key=lambda c: c.program_id.encode("utf-8")):
        group, index, slot = slots[contract.slot_id]
        slot_authority = authority(LEDGER, "slots", f"/slots/{group}/{index}")
        # The complete source IR currently contains NO primitive nodes or
        # predicate->indicator edges. Missing records below describe required
        # role obligations, not invented canonical keys or V3.5 row counts.
        if group == "training_paired_slots":
            roles = {r: slot[r] for r in ("P", "Q")}
        elif group == "primitive_sanity":
            roles = {"P": slot["primitive"]}
        elif group == "primary":
            graph_roles = set(ledger["graphs"][slot["graph"]]) & set("PQRS")
            roles = {r: p for r, p in slot["role_predicates"].items() if r in graph_roles}
        else:
            roles = {r: p for r, p in slot["role_predicates"].items() if r in {"P", "Q"}}
        primitive_items = [i for i in contract.ir.items if i.category == "SEMANTIC_PRIMITIVE"]
        indicator_edges = [i for i in contract.ir.items if i.operation == "PREDICATE_TO_INDICATOR"]
        require(not primitive_items and not indicator_edges,
                "audit must be revised for a changed primitive/indicator implementation")
        absent = []
        for role, predicate in roles.items():
            definition_index = next(i for i, p in enumerate(ledger["predicate_definitions"][contract.domain])
                                    if p["name"] == predicate)
            absent.append({"obligation_id": rid("UNRESOLVED_PRIMITIVE_ROLE", [contract.program_id, role, predicate]),
                           "role": role, "primitive": predicate,
                           "predicate_expression": ledger["predicate_definitions"][contract.domain][definition_index]["expression"],
                           "authority_trace": [slot_authority,
                               authority(LEDGER, "predicate_definitions", f"/predicate_definitions/{contract.domain}/{definition_index}"),
                               authority(COVERAGE, "V3.2"), authority(COVERAGE, "V3.4")],
                           "canonical_contract_key_id": None, "expected_v3_5_row_id": None,
                           "status": "UNRESOLVED", "reason": "No SEMANTIC_PRIMITIVE node/key is emitted"})
        predicate_locations = [asdict(i) for i in contract.ir.items
                               if i.kind == "NODE" and i.result_role == "PREDICATE_BOOLEAN"]
        provisional = []
        by_id = {i.occurrence_id: i for i in contract.ir.items}
        for key in sorted(contract.canonical_keys, key=lambda k: k.key_id.encode("utf-8")):
            provisional.append({"key_catalog_record": catalog_ids[key.key_id],
                                "occurrence_source_spans": [[oid, *by_id[oid].location]
                                    for oid in contract.key_occurrences[key.key_id]],
                                "diagnostic_row_identity": {"label": "V3.5", "program_id": contract.program_id,
                                    "key_catalog_record": catalog_ids[key.key_id]}
                                    if contract.task_kind == "training" else None,
                                "authoritative_expected_row_id": None})
        gaps = [{"code": gap, "contract_id": contract.contract_id, "program_id": contract.program_id,
                 "slot_authority": slot_authority, "status": "UNRESOLVED"} for gap in contract.core_gaps]
        missing.extend(gaps)
        records.append({"contract_id": contract.contract_id, "program_id": contract.program_id,
                        "slot_id": contract.slot_id, "condition": contract.condition, "domain": contract.domain,
                        "task_kind": contract.task_kind, "slot_authority": slot_authority,
                        "source_sha256_utf8": sha(contract.reference_source.encode()),
                        "aggregator": contract.aggregator, "required_primitive_roles": absent,
                        "current_predicate_nodes": predicate_locations,
                        "predicate_to_indicator_edge_count": len(indicator_edges),
                        "provisional_obligations": provisional, "core_gaps": gaps})
    class_rows = [rid("INPUT_DOMAIN_CLASS", [condition, domain, label])
                  for condition in ("ISOLATED", "COMPOSITION")
                  for domain, labels in (("numeric_iteration", NUMERIC_CLASSES), ("array_reduction", ARRAY_CLASSES))
                  for label in labels]
    class_rows.sort(key=lambda r: r.encode("utf-8"))
    summary = {"contract_count": len(contracts), "training_programs": len(training),
               "contracts_by_domain": dict(Counter(c.domain for c in contracts)),
               "contracts_by_aggregator_family": dict(Counter(c.aggregator["kind"] for c in contracts)),
               "contracts_by_task_kind": dict(Counter(c.task_kind for c in contracts)),
               "diagnostic_v3_5_rows": len(rows), "diagnostic_unique_v3_5_rows": len(set(rows)),
               "diagnostic_training_rows_by_kind": dict(Counter(k.evidence_kind for c in training for k in c.canonical_keys)),
               "diagnostic_training_rows_by_category": dict(Counter(k.category for c in training for k in c.canonical_keys)),
               "required_primitive_role_obligations_not_keys": sum(len(r["required_primitive_roles"]) for r in records),
               "current_semantic_primitive_nodes": 0, "current_predicate_to_indicator_edges": 0,
               "current_output_attribute_keys": sum(k.category == "OUTPUT_CATEGORY" for c in contracts for k in c.canonical_keys),
               "input_domain_class_rows": len(class_rows), "authoritative_v3_5_rows": None,
               "population_status": "V3_5_POPULATION_UNRESOLVED", "authoritative_refusal": refusal}
    derivation = {"schema_version": 1, "artifact_kind": "PARTIAL_CONTRACT_DERIVATION_DIAGNOSTIC",
                  "starting_head": STARTING_HEAD, "authoritative": False,
                  "contains_expected_row_index": False, "summary": summary, "contracts": records,
                  "provisional_key_catalog": [{"catalog_record": catalog_ids[key_id],
                      "canonical_key": catalog[key_id].to_dict()} for key_id in catalog_ids],
                  "provisional_obligation_semantics": {
                      "classification": "PROVISIONAL_NOT_CERTIFIED",
                      "authority_trace": [authority(COVERAGE, "V3.2; V3.5"), authority(INTERFACE, "3.3; 9.1")],
                      "slot_trace": "enclosing contract.slot_authority",
                      "occurrence_source_spans": "[occurrence_id, start_offset, end_offset]; graph reconstructible by the producer from the bound pure source template",
                      "diagnostic_row_identity": "RID(label,[program_id,canonical_key.key_id from key_catalog_record]); not an authoritative expected row",
                      "no_missing_obligation_has_a_fabricated_key_id": True},
                  "input_domain_classes": {"authority": authority(PROTOCOLS + "phase3c_conf1_input_domain_case_classes_and_training_amendment_proposed.md", "Frozen case classes"),
                      "ordered_diagnostic_row_ids": class_rows,
                      "canonical_numeric_witness_slot": canonical_numeric_witness_slot(ledger),
                      "activity_evaluated": False},
                  "partial_population_checks": {"duplicate_contracts": [], "duplicate_diagnostic_rows": [],
                      "ordered_row_id_digest": ordered_row_id_digest(rows), "order": "exact UTF-8 ascending",
                      "missing_required_ontology": "UNRESOLVED", "orphan_scientific_obligations": "UNRESOLVED",
                      "complete_row_population": False}}
    unresolved = {"schema_version": 1, "artifact_kind": "CORE_UNRESOLVED_OBLIGATION_DIAGNOSTIC",
                  "starting_head": STARTING_HEAD, "population_status": "V3_5_POPULATION_UNRESOLVED",
                  "authoritative_v3_5_rows": None, "contract_gaps": missing,
                  "gap_counts": dict(Counter(g["code"] for g in missing)),
                  "first_blocker": {"code": "SEMANTIC_PRIMITIVE_AND_PREDICATE_INDICATOR_EXTRACTION_INCOMPLETE",
                      "authority_trace": [authority(COVERAGE, "V3.2; V3.4"), authority(INTERFACE, "9.1")],
                      "evidence": "184 derived contracts emit zero semantic-primitive nodes and zero predicate-to-indicator edges; role obligations above are not canonical keys",
                      "effect": "Expected V3.5 keys cannot be complete before mapping/activity; no authoritative population is serialized"},
                  "additional_not_closed": [
                      {"scope": "V3.2", "detail": "Only complete identical/alpha/trivia trees map; general allowed-equivalence correspondence and a total/pure REFERENCE_ONLY catalog are missing", "implementation": "src/self_learning_ai/conf1_v3/coverage.py::reconcile_complete_mapping"},
                      {"scope": "V3.3", "detail": "LOCAL_PAIR_JOINT and BOOLEAN_OR contexts reject even potentially provable flow cases; frozen evidence serialization is incomplete", "implementation": "src/self_learning_ai/conf1_v3/goco.py::canonical_expression"},
                      {"scope": "V3.5/state", "detail": "Reachability uses all possible writers, not certified loop/prefix/two-pass reaching definitions; backward reachability is not task essentiality", "implementation": "src/self_learning_ai/conf1_v3/core_ir.py::compile_program"},
                      {"scope": "VALUE_OR_LITERAL", "detail": "Leaf constants, not maximal closed constant trees, are attached; syntax-essential literal declaration is not certified", "implementation": "src/self_learning_ai/conf1_v3/contract_ir.py::keys_from_ir"},
                      {"scope": "OUTPUT_ATTRIBUTE", "detail": "lower_contract sets outputs=(); category/sentinel declarations and their total derivation are not implemented", "implementation": "src/self_learning_ai/conf1_v3/contract_ir.py::lower_contract"},
                      {"scope": "V3.6", "detail": "Core paired source comparison exists but paired schedule comparison and full serialized evidence are not closed", "implementation": "src/self_learning_ai/conf1_v3/coverage.py::paired_symmetry"}],
                  "not_a_claim_of_authority_contradiction": True,
                  "delegated_phase_started": False, "status": "STOPPED_COVERAGE_V3_CORE_CLOSURE_ISSUE"}
    return derivation, unresolved


def build_artifacts() -> dict[str, dict]:
    integrity = verify_protected_inputs()
    sys.path.insert(0, str(ROOT / "tests"))
    import conf1_core_development_inputs as dev
    # Must precede importing or invoking any Coverage-v3 classifier/extractor.
    overlap = dev.assert_zero_historical_overlap()
    overlap.update(schema_version=1, artifact_kind="DISPOSABLE_INPUT_OVERLAP_DIAGNOSTIC",
                   starting_head=STARTING_HEAD, inventory=dev.disposable_inventory())
    sys.path.insert(0, str(ROOT / "src"))
    from self_learning_ai.conf1_v3.contracts import all_contracts
    ledger = json.loads((ROOT / LEDGER).read_bytes())
    derivation, unresolved = derive_diagnostic(ledger, all_contracts(ledger))
    return {"protected_input_integrity.json": integrity, "disposable_overlap.json": overlap,
            "partial_derivation.json": derivation, "unresolved_obligations.json": unresolved}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Reconstruct and compare artifacts without writing")
    mode.add_argument("--refresh", action="store_true", help="Regenerate only this pass's development diagnostics before its checkpoint commit")
    args = parser.parse_args()
    artifacts = build_artifacts()
    if not args.check:
        require(git("rev-parse", "HEAD").decode().strip() == STARTING_HEAD, "starting checkpoint HEAD")
        OUT.mkdir(parents=True, exist_ok=True)
    for filename, value in artifacts.items():
        raw = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        path = OUT / filename
        if args.check:
            require(path.read_bytes() == raw, filename + " deterministic artifact reproduction")
        elif args.refresh:
            require(path.exists(), "refresh target must be an existing producer artifact: " + filename)
            path.write_bytes(raw)
        else:
            # Immutable producer outputs, never silently replace an artifact.
            with path.open("xb") as stream:
                stream.write(raw)
    print(json.dumps({"status": "STOPPED_COVERAGE_V3_CORE_CLOSURE_ISSUE",
                      "population_status": "V3_5_POPULATION_UNRESOLVED",
                      "artifact_files": list(artifacts), "reproduced_without_writing": args.check,
                      "summary": artifacts["partial_derivation.json"]["summary"]}, indent=2))


if __name__ == "__main__":
    main()
