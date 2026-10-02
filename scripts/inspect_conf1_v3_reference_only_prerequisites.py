"""Read-only DEVELOPMENT_ONLY prerequisite diagnostic, not an RO verifier.

Only disposable generic sources are parsed. No compiler, models, candidate,
population, expected labels, scientific reports, or artifact writes.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from self_learning_ai.conf1_v3.contract_ir import keys_from_ir
from self_learning_ai.conf1_v3.projection_binding import bind_projection
from self_learning_ai.conf1_v3.projection_grammar import derive_projection_plan, render_development
from self_learning_ai.conf1_v3.reference_only_context import inspect_pre_context_inputs, build_pre_context, prior_bindings, required_selector_audit
from self_learning_ai.conf1_v3.interfaces import ClosureError
from self_learning_ai.conf1_v3.reference_only_development import fixture_plan, executable_overlap_inventory
from self_learning_ai.conf1_v3.reference_only_inventory import source_inventory, ref
from self_learning_ai.conf1_v3.reference_only_overlap import (canonical, load_schedule, load_raw_corpus, compare, require_clear)
from self_learning_ai.conf1_v3.reference_only_state import state_record


def inspect_inputs():
    saved = load_schedule(ROOT / "research/implementation_notes/coverage_v3_reference_only_implementation/predetermined_witness_schedule.json")
    base = [f for f in fixture_plan() if f["variant"] == "BASE"]
    # A second positive treatment checks that the issue is not simply unused
    # indicator scaffolding in EXPRESSION. Values/seed are never changed.
    extras = []
    for f in base:
        declaration = dict(f["prospective"]["declaration"], treatment="ADD", expression=None)
        from self_learning_ai.conf1_v3.attribute_reference import reference_output
        source = render_development(declaration, "ro")
        extras.append(dict(f, variant="BASE_ADD", development_case_id=f["development_case_id"] + "_ADD",
                           source=source, reference_source=source, prospective=derive_projection_plan(declaration),
                           expected_outputs=[str(reference_output(declaration, raw)) for raw in f["raw_inputs"]]))
    fixtures = [*base, *extras]
    # Independently compute the entire additional source/input/expected inventory
    # before this comparison. No source is parsed until strict overlap passes.
    inventory = executable_overlap_inventory(fixtures)
    inventory_hash = sha256(canonical(inventory)).hexdigest()
    corpus, _ = load_raw_corpus(ROOT)
    overlap = compare(inventory, saved, corpus)
    require_clear(overlap)
    records = []
    for f in fixtures:
        p, source_inv, graph = source_inventory(f["program_id"], f["source"],
            ref("DEVELOPMENT_ONLY_INPUT", f["development_case_id"], "SOURCE", f["source"]),
            training=f["program_group"] == "TRAINING")
        state, state_diagnostic = state_record(p, source_inv, graph, direct_artifact_id="DEVELOPMENT_ONLY_DIRECT")
        inspected = inspect_pre_context_inputs(f["prospective"], p, source_inv, graph, state,
            ref("DEVELOPMENT_ONLY_CONTRACT", "DEVELOPMENT_ONLY_CONTRACT_RECORD", "COVERAGE_CONTRACT"),
            direct_artifact_id="DEVELOPMENT_ONLY_DIRECT")
        c = inspected["program"]
        keys, keyed_occurrences = keys_from_ir(c, ())
        keyed = {oid for values in keyed_occurrences.values() for oid in values}
        declared = inspected["declared_selectors"]
        all_ids = {i.occurrence_id for i in c.items}
        missing_both = [i for i in c.items if i.occurrence_id not in keyed | declared]
        # Readiness of the existing kind-witness adapter is not invalidated or
        # upgraded; reconstruct its accepted generic result independently.
        bind_projection(f["prospective"], f["reference_source"], f["source"])
        prior = prior_bindings(f["prospective"], c)
        footprint = {oid for b in prior for oid in b["contract_occurrences"]}
        footprint.update(e["occurrence_id"] for b in prior for e in b["dependency_edges"])
        unsupported = required_selector_audit(f["prospective"], c, prior)
        try:
            build_pre_context(f["prospective"], p, source_inv, graph, state,
                ref("DEVELOPMENT_ONLY_CONTRACT", "DEVELOPMENT_ONLY_CONTRACT_RECORD", "COVERAGE_CONTRACT"),
                direct_artifact_id="DEVELOPMENT_ONLY_DIRECT")
        except ClosureError as error:
            rejected_context_reason = str(error)
        else:
            raise AssertionError("Draft dependency-as-selector shortcut unexpectedly accepted")
        def example(item):
            return dict(occurrence_id=item.occurrence_id, kind=item.kind, operation=item.operation,
                        operand_roles=list(item.operand_roles), result_role=item.result_role,
                        source_endpoint_id=item.source, target_endpoint_id=item.target,
                        parser_legacy_essential=item.essential, parser_legacy_proof=item.proof)
        records.append(dict(development_case_id=f["development_case_id"], program_id=f["program_id"],
            family=f["prospective"]["declaration"]["family"], structure=f["prospective"]["declaration"]["structure"],
            treatment=f["prospective"]["declaration"]["treatment"],
            edge_obligation_quantifier=f["prospective"]["edge_obligation_quantifier"],
            accepted_generic_binding_replayed=True, complete_raw_occurrences=len(c.items),
            declared_selector_occurrences=len(declared), canonical_key_member_occurrences=len(keyed),
            raw_without_declared_selector_count=len(all_ids - declared),
            raw_without_canonical_key_membership_count=len(all_ids - keyed),
            declared_but_not_canonical_key_member_count=len(declared - keyed),
            raw_without_either_selector_or_key_count=len(missing_both),
            raw_without_either_selector_or_key_examples=[example(i) for i in missing_both[:3]],
            raw_without_either_selector_or_key_sha256_utf8=sha256(canonical([example(i) for i in missing_both])).hexdigest(),
            full_mismatch_sets_sha256_utf8=sha256(canonical(dict(
                without_selector=sorted(all_ids - declared), without_key=sorted(all_ids - keyed),
                declared_without_key=sorted(declared - keyed)))).hexdigest(),
            prior_head_and_dependency_footprint_count=len(footprint),
            prior_head_and_dependency_footprint_complete=footprint == all_ids,
            context_constructed=False, prospective_contract_changed=False,
            unsupported_dependency_as_selector_claim_count=len(unsupported),
            unsupported_dependency_as_selector_examples=unsupported[:3],
            unsupported_dependency_as_selector_claims_sha256_utf8=sha256(canonical(unsupported)).hexdigest(),
            rejected_context_reason=rejected_context_reason,
            context_status="UNRESOLVED", scientific_reason_codes=["V32_PRE_DISPOSITION_CONTEXT_INVALID"],
            structural_match_is_not_canonical_key_attachment_proof=True,
            draft_inventory_occurrences=len(source_inv["occurrences"]), raw_state_definitions=len(state["definitions"]),
            raw_state_dependency_edges=len(state["dependency_edges"])))
    return dict(schema_version=1, scope="DEVELOPMENT_ONLY",
        artifact_kind="DEVELOPMENT_ONLY_RO_PRE_CONTEXT_PREREQUISITE_DIAGNOSTIC",
        status="STOPPED_COVERAGE_V3_REFERENCE_ONLY_IMPLEMENTATION_ISSUE",
        witness_schedule_sha256_utf8=saved.sha256_utf8, additional_fixture_inventory_sha256_utf8=inventory_hash,
        additional_overlap=overlap, records=records,
        limitation="The prior adapter retains a complete typed dependency footprint, so direct selector/key list gaps alone were not a blocker. However, assigning each dependency edge to its incident head requirement creates unlicensed required-selector satisfactions (including EDGE INPUT_TO_DECODER assigned to NODE INPUT). No CLOSED pre-context is produced by that shortcut. A faithful occurrence/key/multiplicity/attachment bridge still requires establishment against the complete unchanged prospective contract; this diagnostic does not prove that no such bridge can be implemented. No new requirement or equivalence rule was invented.",
        independent_ro_verifier=False, constructors_used=["accepted DEVELOPMENT_ONLY bind_projection for prior-readiness replay"],
        scientific_instance_closure="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION_AND_VALIDATION",
        prohibited_work_invoked=False, expected_labels_parsed=False, writes=0)


if __name__ == "__main__":
    print(json.dumps(inspect_inputs(), sort_keys=True, separators=(",", ":")))
    raise SystemExit(2)
