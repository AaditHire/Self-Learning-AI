"""Read-only SAVED generic-binding replay. No constructor/producer import."""
from pathlib import Path
from copy import deepcopy
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from audit_conf1_v3_core_closure import verify_protected_inputs
from self_learning_ai.conf1_v3.projection_binding_verifier import verify_projection_evidence,verify_projection_plan,equal
from self_learning_ai.conf1_v3.projection_grammar import require
from self_learning_ai.conf1_v3.core_ir import compile_program
from self_learning_ai.conf1_v3.typed_alignment import align
from self_learning_ai.conf1_v3.requirements import digest,frozen_metadata
from self_learning_ai.conf1_v3.interfaces import ClosureError,SchemaError
OUT=ROOT/"research/implementation_notes/coverage_v3_generic_source_binding"
START="654c1745ae4148a9d8a4200c818ffc288fb8bb36"


def read(name):
    value=json.loads((OUT/name).read_bytes())
    require(value.get("schema_version")==1 and value.get("artifact_kind")=="DEVELOPMENT_ONLY_GENERIC_BINDING_EVIDENCE" and
            value.get("starting_head")==START,"SAVED_DEVELOPMENT_ARTIFACT_HEADER_CHANGED")
    return value


def mutate(e,attack):
    result=deepcopy(e); target=result
    for p in attack["path"][:-1]: target=target[p]
    target[attack["path"][-1]]=deepcopy(attack["value"])
    return result


def run():
    integrity=verify_protected_inputs(); saved=read("protected_integrity.json")
    require(equal(integrity["authorities"],saved["authorities"]) and equal(integrity["normative_regions"],saved["normative_regions"]) and equal(integrity["preregistration"],saved["preregistration"]),"SAVED_PROTECTED_INTEGRITY_CHANGED")
    records=read("disposable_requirement_source_mappings.json")["records"]
    require(records and len({r["record_id"] for r in records})==len(records),"DUPLICATE_OR_MISSING_DEVELOPMENT_RECORD")
    results=[]; by_id={r["record_id"]:r for r in records}
    for r in records:
        require(digest(r["evidence"])==r["evidence_sha256"],"SAVED_EVIDENCE_HASH_CHANGED")
        check=verify_projection_evidence(r["evidence"])
        require(equal(check,r["verification"]),"SAVED_INDEPENDENT_RESULT_CHANGED")
        results.append(dict(record_id=r["record_id"],evidence_sha256=r["evidence_sha256"],verification=check))
    require(equal(results,read("independent_verifier_results.json")["records"]),"INDEPENDENT_RESULT_INVENTORY_CHANGED")
    require(equal(results,read("v32_readiness_evidence.json")["records"]),"V32_INVENTORY_CHANGED")
    require(equal([dict(record_id=r["record_id"],evidence=r["evidence"]["indicator_foundations"]) for r in records],read("indicator_readiness_evidence.json")["records"]),"INDICATOR_INVENTORY_CHANGED")
    require(equal([dict(record_id=r["record_id"],claims=r["evidence"]["claims"]) for r in records],read("v33_readiness_evidence.json")["records"]),"V33_INVENTORY_CHANGED")
    negatives=read("adversarial_mutation_results.json")["records"]
    # Saved readiness must include the actual adversarial obligations, not
    # merely pass whatever subset a caller chose to retain. These are test
    # obligation names, never dispatch keys in the source-binding adapter.
    required_source={"STALE","WRONG_ROLE","AMBIGUOUS","EXTRA_LIVE","REASSOCIATION","ARBITRARY_ALGEBRA",
        "DROPPED_DUPLICATE","LITERAL_REWRITE","INCOMPLETE_ALPHA","UNSUPPORTED_BOOLEAN_ARITHMETIC",
        "BAD_FOLD","WRONG_DIRECTION","WRONG_LOOP"}
    required_mutations={"DEVELOPMENT_TO_SCIENTIFIC","EVALUATION_NAMESPACE_FORGE","SLOT_INJECTION","MISSING_REQUIREMENT",
        "EXTRA_REQUIREMENT","DUPLICATE_SATISFACTION","MISSING_SATISFACTION","WRONG_P_Q","WRONG_LOOP_DIRECTION",
        "WRONG_LOOP_CONTEXT","STALE_INDICATOR","TYPE_MISMATCH","PORT_MISMATCH","PROVENANCE_PROMOTION",
        "INVENTED_REFERENCE_ONLY","BASE_PASS_FLAG","WRONG_EQUIVALENCE_RULE"}
    require(all(a["kind"] in {"SOURCE_REJECTION","SERIALIZED_MUTATION"} for a in negatives) and
            {a["name"] for a in negatives if a["kind"]=="SOURCE_REJECTION"}==required_source and
            {a["attack"]["name"] for a in negatives if a["kind"]=="SERIALIZED_MUTATION"}==required_mutations and
            len(negatives)==len(required_source)+len(required_mutations),"ADVERSARIAL_OBLIGATION_INVENTORY_INCOMPLETE")
    for attack in negatives:
        try:
            if attack["kind"]=="SERIALIZED_MUTATION": verify_projection_evidence(mutate(by_id[attack["base_record_id"]]["evidence"],attack["attack"]))
            else:
                # All saved source negatives fail the parser/total typed
                # accounting layer. Rebuild that fact without a constructor.
                c=compile_program(attack["declaration"]["program_id"],attack["reference_source"])
                p=compile_program(attack["declaration"]["program_id"],attack["source"])
                align(c,p)
        except (ClosureError,SchemaError) as exc:
            require(str(exc)==attack["reason"],"SAVED_ADVERSARY_REASON_CHANGED")
        else: raise ClosureError("SAVED_ADVERSARY_ACCEPTED")
    matrix=read("canonical_requirement_kind_coverage_matrix.json")["rows"]
    actual_kinds={digest(dict(capability=q["capability"],evidence_kind=q["evidence_kind"],family=q["family"])) for r in records for q in r["evidence"]["plan_before"]["requirements"]}
    require({row["development_kind_id"] for row in matrix}==actual_kinds and len(matrix)==len(actual_kinds),"KIND_MATRIX_INCOMPLETE_OR_DUPLICATED")
    for row in matrix:
        record=by_id[row["positive_record_id"]]; e=record["evidence"]
        index=row["negative_binding_index"]; req=e["plan_before"]["requirements"][index]; binding=e["bindings"][index]
        require(row["development_kind_id"]==digest(dict(capability=req["capability"],evidence_kind=req["evidence_kind"],family=req["family"])),"KIND_MATRIX_IDENTITY_CHANGED")
        require(row["capability"]==req["capability"] and row["development_requirement_id"]==req["requirement_id"] and
                row["requirement_class"]==req["requirement_class"] and row["semantic_role"]==req["capability"]["semantic_role"] and
                row["evidence_kind"]==req["evidence_kind"] and row["family"]==req["family"] and row["input_domain"]==req["input_domain"] and
                equal(row["grammatical_source_form"],req["occurrence_requirements"]) and row["mapping_path"]==binding["method"] and
                equal(row["independent_verifier_result"],record["verification"]),"KIND_MATRIX_NOT_BOUND_TO_VERIFIED_SOURCE")
        attacked=deepcopy(e); attacked["bindings"].pop(index)
        try: verify_projection_evidence(attacked)
        except ClosureError as exc: require(str(exc)==row["negative_verifier_reason"],"KIND_NEGATIVE_REASON_CHANGED")
        else: raise ClosureError("KIND_DELETION_ACCEPTED")
    rules={claim["catalog_rule"] for r in records for claim in r["evidence"]["claims"]}
    required_rules={"CONSISTENT_ALPHA_RENAMING","WHOLLY_INTEGER_CONSTANT_NEG_ADD_SUB_MUL_COMPUTED_KEY_ONLY", "PURE_COMMUTATIVE_CHILD_SORT",
                    "COMPARISON_DIRECTION","SYMMETRIC_EQUALITY","AND_VS_PROVEN_01_PRODUCT_LOCAL_ONLY","BOOLEAN_OR_VS_PROVEN_INDICATOR_SUM_POSITIVE"}
    require(required_rules<=rules,"V33_FAMILY_MISSING")
    forms={(r["evidence"]["plan_before"]["declaration"]["family"],r["evidence"]["plan_before"]["declaration"]["structure"],r["evidence"]["plan_before"]["declaration"]["reverse"]) for r in records}
    expected_forms={(f,s,b) for f in ("numeric_iteration","array_reduction") for s in ("PER_ITEM","PREFIX","TWO_PASS") for b in (False,True)}
    require(forms==expected_forms,"GRAMMAR_FORM_MISSING")
    predicates={q["capability"]["operation"] for r in records for q in r["evidence"]["plan_before"]["requirements"] if q["capability"]["category"]=="SEMANTIC_PRIMITIVE"}
    require(predicates=={p["name"] for ps in frozen_metadata()["predicate_definitions"].values() for p in ps},"PRIMITIVE_COVERAGE_MISSING")
    model=read("implementation_readiness_model.json")
    require(equal(model["implementation_readiness"],{k:"IMPLEMENTATION_READY" for k in ("INDICATOR","V32","V33")}) and
            equal(model["scientific_instance_closure"],{k:"DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION" for k in ("INDICATOR","V32","V33")}),"IMPLEMENTATION_SCIENTIFIC_LAYER_MIX")
    require(model["scientific_sources_constructed"]==model["scientific_satisfaction_claims"]==0 and not model["population_producer_invoked"] and not model["historical_8668_authoritative"],"UNAUTHORIZED_SCIENTIFIC_CLAIM")
    require(model["scope"]=="DEVELOPMENT_ONLY" and
            not any(model[k] for k in ("scientific_expected_index_created","scientific_gate_semantics_changed","old_global_gate_artifacts_changed")) and
            equal(model["grammar_forms"],[list(x) for x in sorted(forms)]) and model["primitive_identities"]==sorted(predicates) and
            model["frozen_equivalence_families"]==sorted(rules) and
            all(r["evidence"]["plan_before"]["edge_obligation_quantifier"]==model["edge_quantifier"] for r in records),"READINESS_MODEL_NOT_BOUND_TO_EVIDENCE")
    namespace=read("namespace_isolation.json"); guards=namespace["guards"]
    require(len(guards)==2 and {g["scope"] for g in guards}=={"SCIENTIFIC_TRAINING","SCIENTIFIC_EVALUATION"} and
            all(g["source_parsed"] is False for g in guards) and namespace["scientific_sources_constructed"]==namespace["scientific_requirements_satisfied"]==0 and
            namespace["scientific_instance_closure"]=="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION","NAMESPACE_INVENTORY_INCOMPLETE_OR_PROMOTED")
    for guard in guards:
        plan=deepcopy(records[0]["evidence"]["plan_before"]); plan["scope"]=guard["scope"]
        try: verify_projection_plan(plan)
        except ClosureError as exc: require(str(exc)==guard["reason"],"NAMESPACE_GUARD_CHANGED")
        else: raise ClosureError("SCIENTIFIC_PROMOTION_ACCEPTED")
    # Recompute string/hash overlap without importing a realization generator.
    def strings(v):
        if isinstance(v,str): yield v
        elif isinstance(v,list):
            for x in v: yield from strings(x)
        elif isinstance(v,dict):
            for k,x in v.items(): yield k; yield from strings(x)
    overlap=read("disposable_overlap.json"); old=set()
    require(overlap["expected_labels_parsed"] is False and
            overlap["exact_string_overlap"]==overlap["recorded_hash_overlap"]==overlap["recomputed_string_hash_overlap"]==0,"OVERLAP_STATUS_OR_BOUNDARY_CHANGED")
    paths=sorted((ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixtures").glob("*.json"))
    require(len(paths)==13,"PROTECTED_CORPUS_CHANGED")
    for path in (*paths,ROOT/"research/protocols/phase3c_conf1_v3_synthetic_fixture_manifest.json"): old.update(strings(json.loads(path.read_bytes())))
    import hashlib
    values={x["value"] for rows in overlap["inventory"].values() for x in rows}; hashes={hashlib.sha256(v.encode()).hexdigest() for v in values}
    require(not values&old and not hashes&old and not hashes&{hashlib.sha256(v.encode()).hexdigest() for v in old},"DISPOSABLE_OVERLAP_CHANGED")
    for rows in overlap["inventory"].values():
        require(all(hashlib.sha256(r["value"].encode()).hexdigest()==r["sha256_utf8"] for r in rows),"INVENTORY_STRING_HASH_CHANGED")
    admitted={e for r in records for e in (r["evidence"]["source"],r["evidence"]["reference_source"])}
    require(admitted<={r["value"] for r in overlap["inventory"]["sources"]},"UNPREFLIGHTED_DISPOSABLE_SOURCE")
    tests=read("verification_test_results.json")
    require(tests["focused"]["failures"]==tests["focused"]["errors"]==0 and tests["focused"]["pinned_disposable_cases"]==len({r["name"] for r in records}),"PINNED_DISPOSABLE_VALIDATION_INCOMPLETE")
    require(tests["scientific_fixture_execution"] is False and tests["population_test_deselected"] is True and
            tests["known_legacy_failures"]["tests"]==tests["known_legacy_failures"]["failures"]==3 and
            tests["known_legacy_failures"]["errors"]==0,"TEST_BOUNDARY_OR_LEGACY_RECORD_CHANGED")
    print(json.dumps(dict(development_mappings_verified=len(records),development_requirement_kinds_verified=len(matrix),adversaries_rejected=len(negatives),
                         implementation_readiness=model["implementation_readiness"],scientific_instance_closure=model["scientific_instance_closure"],
                         writes=0,constructor_invoked=False,population_producer_invoked=False),indent=2))


if __name__=="__main__": run()
