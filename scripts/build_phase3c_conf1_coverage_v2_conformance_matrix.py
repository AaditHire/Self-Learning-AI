"""Record clause-level coverage-v2 implementation/test trace after C postmortem."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE"
JSON_OUT = OUT / "coverage_v2_rule_conformance_matrix.json"
MD_OUT = OUT / "coverage_v2_rule_conformance_matrix.md"

rows = []


def add(ident, clause, functions, fixtures, properties, evidence, status):
    rows.append({"clause_id": ident, "specification_section": ident.split(".")[0],
                 "normative_clause": clause, "implementation_functions": functions,
                 "regression_fixtures": fixtures, "property_tests": properties,
                 "emitted_evidence_or_reason": evidence, "status": status})


add("1.1", "Closed required contract fields and unknown-key failure", ["_validate_schema"], ["A:equivalent_comparison_operands"], [], "CoverageError on schema mismatch", "UNTESTED")
add("1.2", "Contract derived by prospective builder from immutable slot grammar", [], [], [], "Attempt 004 builder and derivation absent", "UNIMPLEMENTED")
add("1.3", "Numeric and four-signed-value array input interpretation", ["parse_items", "evaluate"], ["A:task_essential_array_api_absent", "B:live_array_parser_chain"], [], "CONTRACT_CASE_MISMATCH", "UNTESTED")
add("1.4", "Typed expression grammar and closed operations", ["validate_expr"], ["A:boolean_or_operator_absent"], [], "Unknown op fails; operand/result type validation absent", "UNIMPLEMENTED")
add("1.5", "sum_per_item, prefix_pair, product_of_counts aggregators", ["evaluate", "_validate_schema"], ["A:prior_state_dataflow_absent"], [], "No positive product_of_counts or prefix_pair source-backed fixture", "UNTESTED")
add("1.6", "Five case contract/source/compiler exact agreement", ["extract", "evaluate"], ["A:equivalent_comparison_operands", "C_CONSUMED_REGRESSION:array_live_new_predicate"], ["required_input_api_removed"], "CONTRACT_CASE_MISMATCH; SOURCE_CASE_MISMATCH", "CONFORMANT")
add("1.7", "Same extraction for training/evaluation, no task-ID branches", ["extract", "audit_bundle"], ["A:local_pair_motifs_without_full_graph"], ["alpha_renaming_preserves_coverage"], "Shared extract function", "CONFORMANT")
add("2.1", "Closed ontology and explicit source-only classification", ["extract", "source_certificate"], ["B:unclassified_import", "C_CONSUMED_REGRESSION:unproved_extra_branch"], [], "Source statements default to TASK_ESSENTIAL without active-node link; expression operators not all inventoried", "UNIMPLEMENTED")
add("2.2", "Semantic predicate key and active same-domain training evidence", ["canonical_expr", "extract", "audit_bundle"], ["A:equivalent_comparison_operands"], ["alpha_renaming_preserves_coverage"], "SEMANTIC_PRIMITIVE rows and both-condition evidence", "CONFORMANT")
add("2.3", "Input, bounded loop, conditional choice, update, output, array index construct keys", ["extract", "source_certificate"], ["B:live_array_parser_chain"], [], "CONDITIONAL_CHOICE and ARRAY_INDEXING keys are not emitted", "UNIMPLEMENTED")
add("2.4", "Exact API role, connected decoder and distinct-input witness", ["source_certificate", "extract"], ["B:dead_array_conversion_disconnected", "B:live_array_parser_chain"], [], "Connection checked for fixed shape; distinct-input API witness not recorded", "UNIMPLEMENTED")
add("2.5", "Typed operators and sole pair-joint treatment exception", ["_typed_operator", "extract", "audit_bundle"], ["A:local_pair_motifs_without_full_graph", "A:boolean_or_operator_absent"], ["local_pair_motif_permitted"], "OPERATOR_CAPABILITY; LOCAL_PAIR_JOINT", "UNTESTED")
add("2.6", "Literal lexeme distinct from computed value and output category", ["_literal_token_witness", "walk_semantic", "extract"], ["A:literal_token_not_value", "C_CONSUMED_REGRESSION:literal_vs_computed_minus_two"], ["negative_output_capability_removed"], "LITERAL_TOKEN; COMPUTED_VALUE; OUTPUT_*", "CONFORMANT")
add("2.7", "Independent/dependent/nested branch relation is source-backed", ["extract", "_classify_extras"], ["A:dead_if_does_not_cover_independent_checks"], ["dead_if_not_independent_checks"], "Only predicate-count proxy; no ordered dependency graph", "UNIMPLEMENTED")
add("2.8", "Typed atomic dataflow edges retain paths/multiplicity", ["extract"], ["A:prior_state_dataflow_absent"], [], "Atomic keys emitted from aggregator witness, without each edge path/multiplicity", "UNIMPLEMENTED")
add("2.9", "Full vector plus typed graph/signature", ["_full_signature"], ["B:equal_inventory_distinct_typed_topology", "B:alpha_renamed_identical_graph", "C_CONSUMED_REGRESSION:multiplication_edge_rewire"], [], "typed_graph and contribution_vector serialized; duplicate equivalent predicate-role edge cases untested", "UNTESTED")
add("2.10", "Declared and observed output categories and exact sentinel cases", ["extract"], ["A:negative_output_capability_absent"], ["negative_output_capability_removed"], "OUTPUT_CATEGORY_UNWITNESSED; OUTPUT_EXACT", "UNTESTED")
add("3.1", "Consistent identifier alpha-renaming", ["canonical_expr", "_full_signature", "source_certificate"], ["B:alpha_renamed_identical_graph"], ["alpha_renaming_preserves_coverage"], "Same typed graph for tested alpha-renaming", "CONFORMANT")
add("3.2", "Pure integer constant-tree folding", ["const_value", "canonical_expr", "walk_semantic"], ["A:computed_negative_one_equivalence"], ["150 algebraic canonical checks"], "COMPUTED_VALUE equivalence", "CONFORMANT")
add("3.3", "Commutative pure child sorting with duplicate multiplicity", ["canonical_expr", "_full_signature"], ["A:commutative_pair_order"], ["150 algebraic canonical checks"], "Subtree sorting; duplicate structural relation not directly tested", "UNTESTED")
add("3.4", "Boolean and versus 0/1 indicator multiplication local-pair equivalence", ["_local_pair_motifs"], ["A:local_pair_motifs_without_full_graph"], [], "Full typed graph keeps distinct AND/MUL operators; equivalence absent", "UNIMPLEMENTED")
add("3.5", "Boolean or versus indicator(add(a,b)>0) equivalence", [], ["A:boolean_or_operator_absent"], [], "No canonical rewrite or equivalence test", "UNIMPLEMENTED")
add("3.6", "Comparison direction swap and symmetric equality", ["canonical_expr"], ["A:equivalent_comparison_operands"], ["150 algebraic canonical checks"], "Canonical GT/GE swap and EQ sort", "CONFORMANT")
add("3.7", "No other algebraic rewrite", ["canonical_expr"], ["B:equal_inventory_distinct_typed_topology"], [], "No explicit negative property set for forbidden rewrites", "UNTESTED")
add("3.8", "2^k truth vector, k<=4, role edges/shared predicates", ["_full_signature"], ["B:equal_inventory_distinct_typed_topology"], [], "No k<=4 enforcement; equal-definition distinct roles collapse in role_lookup", "UNIMPLEMENTED")
add("3.9", "Report local pair motifs without treating them as freshness failure", ["_local_pair_motifs", "audit_bundle"], ["A:local_pair_motifs_without_full_graph"], ["local_pair_motif_permitted"], "local_pair_motifs count and treatment relation", "CONFORMANT")
add("3.10", "Pair-joint sole exception, components covered in both conditions", ["extract", "audit_bundle"], ["A:local_pair_motifs_without_full_graph"], [], "No independent property proving all component requirements retained", "UNTESTED")
add("4.1", "Counterfactual table for every semantic node, lexicographic first witness", ["mutation", "activity", "walk_semantic"], ["C_CONSUMED_REGRESSION:numeric_loop_new_predicates"], [], "Activity failures recorded; complete mutation-table property suite absent", "UNTESTED")
add("4.2", "Each repeated predicate occurrence mutated separately", ["walk", "activity"], ["A:local_pair_motifs_without_full_graph"], [], "Occurrence paths exist; duplicate equal-predicate activity property absent", "UNTESTED")
add("4.3", "Three aggregator counterfactual forms", ["evaluate", "activity"], ["A:prior_state_dataflow_absent"], [], "No positive product_of_counts counterfactual property", "UNTESTED")
add("4.4", "Each control/dataflow key inherits exact source-backed edge witness/path", ["extract"], ["C_CONSUMED_REGRESSION:array_live_new_predicate"], [], "Atomic edges all inherit a single aggregator witness/path", "UNIMPLEMENTED")
add("4.5", "Pinned GOCO compilation and exact case agreement", ["compiler", "extract"], ["A:equivalent_comparison_operands"], ["required_input_api_removed"], "SOURCE_CASE_MISMATCH", "CONFORMANT")
add("4.6", "Parsed numeric input-loop bound/output dependency", ["parse", "_numeric_certificate"], ["B:numeric_loop_alpha_and_whitespace"], ["alpha_renaming_preserves_coverage"], "NUMERIC_LOOP_HEADER_INVALID; NUMERIC_ACCUMULATOR_DISCONNECTED", "UNTESTED")
add("4.7", "Parsed array input/SPLIT/conversions/index/predicate/output dependency", ["parse", "_array_certificate"], ["B:live_array_parser_chain", "B:dead_array_conversion_disconnected"], [], "ARRAY_DATAFLOW_DISCONNECTED", "UNTESTED")
add("4.8", "Inventory each GOCO token-tree occurrence with offset and classification", ["tokenize", "parse", "source_certificate", "_inventory_expression_tokens"], ["B:unclassified_import"], [], "Statement/API/index offsets only; no complete operator/expression occurrence inventory", "UNIMPLEMENTED")
add("4.9", "Source occurrence backs essential key only with matching active contract path", ["extract", "source_certificate"], ["C_CONSUMED_REGRESSION:array_live_new_predicate"], [], "Inventory defaults essential before activity; no per-source-node link", "UNIMPLEMENTED")
add("4.10", "Unmatched source requires valid proof or fail closed", ["_classify_extras", "parse"], ["B:unclassified_import", "C_CONSUMED_REGRESSION:unproved_extra_branch"], [], "Some extras fail; arbitrary recognized live statements not fully adjudicated", "UNIMPLEMENTED")
add("5.1", "Only active contract/domain/output requirements are TASK_ESSENTIAL", ["extract", "source_certificate"], ["C_CONSUMED_REGRESSION:array_live_new_predicate"], [], "Source inventory marks statements essential without individual activity proof", "UNIMPLEMENTED")
add("5.2", "Incidental names/grouping/formatting reference-only", ["canonical_expr", "source_certificate"], ["B:numeric_loop_alpha_and_whitespace"], ["alpha_renaming_preserves_coverage"], "Equivalent coverage classification", "UNTESTED")
add("5.3", "Nontrivial extra construct proof: rewrite, alternative reference, finite-domain or closed identity", ["_classify_extras"], ["A:unused_reference_declaration", "C_CONSUMED_REGRESSION:unproved_extra_branch"], [], "Alternative-reference and finite-domain proof forms absent; UNUSED_DECLARATION not explicit catalog proof", "UNIMPLEMENTED")
add("6.1", "Both-condition same-domain source-backed active coverage", ["audit_bundle"], ["A:task_essential_array_api_absent"], ["negative_output_capability_removed"], "UNCOVERED category/key with evidence lists", "CONFORMANT")
add("6.2", "Treatment exception does not waive atomic/operator/control/output capabilities", ["audit_bundle"], ["A:local_pair_motifs_without_full_graph"], [], "Per-row requirements retained but no dedicated all-component test", "UNTESTED")
add("6.3", "Primary full signature absent in both conditions even with other failures", ["_full_signature", "audit_bundle"], ["C_CONSUMED_REGRESSION:withheld_full_signature_reuse", "A:full_primary_signature_reused"], ["full_signature_inserted"], "PROHIBITED_FULL_SIGNATURE:composition", "CONFORMANT")
add("6.4", "Every independent violation emitted, no reason short-circuit", ["extract", "audit_bundle"], ["C_CONSUMED_REGRESSION:withheld_full_signature_reuse"], [], "One combined-violation regression only; general reason-order property absent", "UNTESTED")
add("6.5", "Report each requirement, condition evidence, category totals/reasons", ["extract", "audit_bundle"], ["A:equivalent_comparison_operands"], [], "requirements, evidence lists, category_counts, failures", "UNTESTED")
add("6.6", "No thresholds, manual waivers or post-candidate reclassification", ["audit_bundle"], ["A:local_pair_motifs_without_full_graph"], [], "No threshold branch; attempt 004 absent", "CONFORMANT")


def main():
    if JSON_OUT.exists() or MD_OUT.exists():
        raise FileExistsError("conformance matrix already exists")
    counts = Counter(row["status"] for row in rows)
    status = ("PASS" if counts["UNIMPLEMENTED"] == counts["UNTESTED"] ==
              counts["UNTRACED"] == 0 else "STOP_COVERAGE_V2_RULE_CONFORMANCE_INCOMPLETE")
    report = {"status": status, "normative_rule": "research/protocols/phase3c_conf1_coverage_v2.md",
              "clause_count": len(rows), "counts": dict(sorted(counts.items())), "rows": rows,
              "no_model_execution": True}
    JSON_OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Coverage-v2 rule-to-code conformance matrix", "",
             f"**Status:** `{status}`. {len(rows)} traced clauses; counts: {dict(sorted(counts.items()))}.", "",
             "Suite C is consumed regression evidence. No Suite D was constructed or run.", "",
             "| Clause | Rule | Implementation | Regression | Property | Evidence/reason | Status |",
             "|---|---|---|---|---|---|---|"]
    for row in rows:
        fields = [row["clause_id"], row["normative_clause"],
                  ", ".join(row["implementation_functions"]) or "NONE",
                  ", ".join(row["regression_fixtures"]) or "NONE",
                  ", ".join(row["property_tests"]) or "NONE",
                  row["emitted_evidence_or_reason"], row["status"]]
        lines.append("| " + " | ".join(str(x).replace("|", "\\|") for x in fields) + " |")
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "clause_count": len(rows),
                      "counts": dict(sorted(counts.items()))}, indent=2))


if __name__ == "__main__": main()
