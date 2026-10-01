"""Pure serialized-data readiness/matrix projections; no evidence constructors."""
from .requirements import digest
from .essentiality_semantics import SCIENTIFIC
from .projection_grammar import require
from .essentiality_audit import dependency_notes


def inventories(records):
    value_kinds={};output_kinds={};active=[];initial=[];maximal=[];categories=[];sentinels=[];expected=[]
    for r in records:
        a=r["evidence"];d=a["essentiality"]["state"]["plan"]["declaration"]
        for i,row in enumerate(a["values"]):
            q=row["requirement"];k=q["key"];w=row["witness"]
            ops=sorted({x["operation"] for x in w["attachment"]["interior"] if x["operation"]!="CONSTANT"}) if w else []
            kind=dict(evidence_kind=q["evidence_kind"],domain=k["domain"],parent_kind=k["attribute_parent_kind"],type=k["result_type"],
                      subtype="LITERAL_TOKEN" if k["exact_required_lexeme"] is not None else "COMPUTED_VALUE",role=k["result_role"],constant_operations=ops)
            kid=digest(kind);matrix=value_kinds.setdefault(kid,dict(kind_id=kid,kind=kind,requirement_id=q["requirement_id"],grammar_forms=[],
               binding_rule="EXACT_PROSPECTIVE_MAXIMAL_UNIT_AND_VERIFIED_ACTIVE_PARENT_OR_INITIAL_STATE; NO_NEAREST_TEXT",positive_witness=None,unresolved_witnesses=[]))
            form=[d["family"],d["structure"],d["treatment"],d["reverse"]]
            if form not in matrix["grammar_forms"]:matrix["grammar_forms"].append(form)
            index=dict(record_id=r["record_id"],value_index=i,requirement_id=q["requirement_id"],record_sha256=digest(row),status=row["status"],reason=row["reason"])
            if w:
                if matrix["positive_witness"] is None:matrix["positive_witness"]=index
                entry={**index,"canonical_key":k,"attachment":w["attachment"],"case_id":w["case_id"],"source_sha256":w["source_sha256"],
                       "parent_witness":w["active_parent"],"initial_state":w["initial_state"],"full_execution_record":"value_output_evidence_records.jsonl.gz"}
                (active if w["active_parent"] else initial).append(entry)
                if w["attachment"]["maximal_constant"]:maximal.append(entry)
            else:matrix["unresolved_witnesses"].append(index)
        expected.extend(a["prospective_output"]["expected_records"])
        for i,row in enumerate(a["outputs"]):
            req=row["requirement"];kind=dict(evidence_kind="OUTPUT_ATTRIBUTE",operation=req["operation"],domain=d["family"])
            kid=digest(kind);idx=dict(record_id=r["record_id"],output_index=i,requirement_id=req["requirement_id"],record_sha256=digest(row),status=row["status"])
            output_kinds.setdefault(kid,dict(kind_id=kid,kind=kind,requirement_id=req["requirement_id"],grammar_forms=[[d["family"],d["structure"],d["treatment"]]],
                binding_rule="PROSPECTIVE_FROZEN_REQUIREMENT_AND_SOURCE_CASE_BOUND_DECLARATION_EXPECTED_RECORD_PLUS_ACTUAL_FINAL_EXECUTION_STATE_ANCESTRY",
                positive_witness=idx if row["status"]=="COVERED" else None))
            (categories if req["output_requirement_kind"]=="CATEGORY" else sentinels).append(dict(**idx,requirement=req,cases=row["cases"],first_matching_case=row["first_matching_case"]))
    values=list(value_kinds.values());outputs=list(output_kinds.values())
    require(all(r["positive_witness"] for r in values+outputs),"ATTRIBUTE_KIND_POSITIVE_WITNESS_MISSING")
    for row in values:
        row["negative_witness"]=dict(**row["positive_witness"],mutation="ALTER_ATTACHMENT_TYPE",intended_reason="VALUE_TYPE_MISMATCH")
        row["independent_verification"]="VERIFIED"
    for row in outputs:
        row["negative_witness"]=dict(**row["positive_witness"],mutation="ALTER_FINAL_DISPLAY_NODE",intended_reason="OUTPUT_FINAL_DISPLAY_OR_STATE_DEPENDENCY_MISMATCH")
        row["independent_verification"]="VERIFIED"
    return dict(value_kind_matrix=values,output_kind_matrix=outputs,active_parent_records=active,initial_state_records=initial,
                maximal_constant_records=maximal,output_category_records=categories,exact_sentinel_records=sentinels,development_expected_records=expected)


def kind_attack(e,row):
    from copy import deepcopy
    result=deepcopy(e);negative=row["negative_witness"]
    if "value_index" in negative:result["values"][negative["value_index"]]["witness"]["attachment"]["type"]="BOOLEAN"
    else:result["outputs"][negative["output_index"]]["cases"][0]["final_display"]["occurrence_id"]="UNRELATED_NODE"
    return result


def models(records,inv,old_gates):
    common=dict(scope="DEVELOPMENT_ONLY",scientific_instance_closure=SCIENTIFIC,scientific_satisfaction_claims=0,
                scientific_expected_row_index_eligible=False,constructor_status_trusted=False,
                independence="Read-only serialized verification; shared parser/runtime/state/attachment/reference kernels. Full essentiality status replay independent of constructor.",
                frozen_gate_semantics_changed=False)
    value=dict(**common,implementation_readiness="VALUE_LITERAL_IMPLEMENTATION_READY",scientific_layer="VALUE_LITERAL_SCIENTIFIC_INSTANCE_CLOSURE",
               readiness_layer="VALUE_LITERAL_IMPLEMENTATION_READINESS",old_global_gate=old_gates["VALUE_LITERAL_ATTACHMENT_COMPLETE"],
               requirement_kinds=len(inv["value_kind_matrix"]),records=len(records),inactive_unbound_remain_unresolved=True,
               maximal_operations=["NEG","ADD","SUB","MUL"],exact_numeric_lexeme_is_prospective_grammar_syntax_obligation=True)
    output=dict(**common,implementation_readiness="OUTPUT_ATTRIBUTE_IMPLEMENTATION_READY",scientific_layer="OUTPUT_ATTRIBUTE_SCIENTIFIC_INSTANCE_CLOSURE",
                readiness_layer="OUTPUT_ATTRIBUTE_IMPLEMENTATION_READINESS",old_global_gate=old_gates["OUTPUT_ATTACHMENT_COMPLETE"],
                requirement_kinds=len(inv["output_kind_matrix"]),records=len(records),categories=["OUTPUT_ZERO","OUTPUT_POSITIVE","OUTPUT_NEGATIVE","OUTPUT_MULTIDIGIT"],
                exact_sentinel="CANONICAL_INTEGER_TEXT_EXACT_MATCH; ZERO_POSITIVE_NEGATIVE",expected_record_oracle="INDEPENDENT_DECLARATION_REFERENCE_CHECKED_AGAINST_PINNED_COMPILER",
                behavioral_outputs_are_not_expected_records=True)
    return value,output


def reference_dependency():
    return dict(**dependency_notes()["reference_only"],remaining_before_comprehensive_ready=[
        "Complete prospective catalog/admission proof for pure-unused and constant-false extras",
        "Complete typed accounting of every unmatched live/dead construct against that closed catalog",
        "Independent serialized disposition verifier and negative tests for each admitted form",
        "Required inactive/unresolved behaviors must remain unresolved, never REFERENCE_ONLY escapes"],
        current_pass="Existing PURE_UNUSED_NO_TYPED_PATH_TO_OUTPUT only; no comprehensive repair",scientific_closure=SCIENTIFIC)
