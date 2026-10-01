"""One-shot DEVELOPMENT evidence producer, not a scientific/population producer."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"tests"),str(ROOT/"scripts")]
from audit_conf1_v3_core_closure import verify_protected_inputs
from self_learning_ai.conf1_v3.interfaces import ClosureError,SchemaError
from self_learning_ai.conf1_v3.requirements import digest
from self_learning_ai.conf1_v3.projection_binding_verifier import verify_projection_evidence,verify_projection_plan

OUT=ROOT/"research/implementation_notes/coverage_v3_generic_source_binding"
REQUIRED_RULES={"CONSISTENT_ALPHA_RENAMING","WHOLLY_INTEGER_CONSTANT_NEG_ADD_SUB_MUL_COMPUTED_KEY_ONLY",
    "PURE_COMMUTATIVE_CHILD_SORT","COMPARISON_DIRECTION","SYMMETRIC_EQUALITY",
    "AND_VS_PROVEN_01_PRODUCT_LOCAL_ONLY","BOOLEAN_OR_VS_PROVEN_INDICATOR_SUM_POSITIVE"}


def junit(path):
    root=ET.parse(path).getroot(); suites=list(root.iter("testsuite"))
    cases=list(root.iter("testcase"))
    return dict(tests=len(cases),failures=sum(int(s.attrib.get("failures",0)) for s in suites),
                errors=sum(int(s.attrib.get("errors",0)) for s in suites),
                skipped=sum(int(s.attrib.get("skipped",0)) for s in suites),
                failed_cases=[dict(name=c.attrib["classname"]+"::"+c.attrib["name"],message=c.find("failure").attrib.get("message","")) for c in cases if c.find("failure") is not None],
                pinned_disposable_cases=sum(c.attrib["name"].startswith("test_disposable_pinned_compiler") for c in cases))


def run():
    parser=argparse.ArgumentParser(); parser.add_argument("--focused-junit",required=True); parser.add_argument("--legacy-junit",required=True)
    args=parser.parse_args()
    import gbind905_inputs as d
    if subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()!=d.START: raise RuntimeError("starting HEAD changed")
    if OUT.exists(): raise RuntimeError("development evidence already exists; no refresh")
    integrity=verify_protected_inputs(); overlap=d.overlap()
    from gbind905_runtime import mapped,negative,mutations,apply_mutation,EQUIVALENCES,REGIONAL
    from test_conf1_v3_generic_binding import SOURCE_ATTACKS
    focused=junit(args.focused_junit); legacy=junit(args.legacy_junit)
    if focused["failures"] or focused["errors"] or focused["pinned_disposable_cases"]!=len(d.DECLARATIONS): raise RuntimeError("focused validation incomplete/failed")
    if legacy["tests"]!=3 or legacy["failures"]!=3 or legacy["errors"]: raise RuntimeError("known legacy boundary changed")
    records=[]
    def add(name,variant=None,scope=None):
        e=mapped(name,variant,scope); verified=verify_projection_evidence(e)
        records.append(dict(record_id="GBIND905-EVIDENCE-"+str(len(records)),name=name,variant=variant,regional_scope=scope,
                            evidence=e,evidence_sha256=digest(e),verification=verified))
    for name in d.DECLARATIONS: add(name)
    # Alpha is generic and checked in every domain/traversal/structure form.
    for name in d.DECLARATIONS: add(name,name+"-ALPHA")
    for name,variant in EQUIVALENCES: add(name,variant)
    for name,variant,scope in REGIONAL: add(name,variant,scope)
    negatives=[]
    for name,attack in SOURCE_ATTACKS:
        try: negative(name,attack)
        except (ClosureError,SchemaError) as exc:
            negatives.append(dict(kind="SOURCE_REJECTION",name=attack,declaration=d.DECLARATIONS[name],
                                  reference_source=d.SOURCES[name],source=d.BAD[attack],reason=str(exc)))
        else: raise RuntimeError("source adversary accepted: "+attack)
    base=next(r for r in records if r["name"]=="numeric_iteration-ADD" and r["variant"] is None)
    for attack in mutations(base["evidence"]):
        try: verify_projection_evidence(apply_mutation(base["evidence"],attack))
        except ClosureError as exc:
            negatives.append(dict(kind="SERIALIZED_MUTATION",base_record_id=base["record_id"],attack=attack,reason=str(exc)))
        else: raise RuntimeError("serialized adversary accepted")
    eq=next(r for r in records if r["variant"]=="ADD_SWAP")
    wrong=dict(name="WRONG_EQUIVALENCE_RULE",path=["claims",0,"catalog_rule"],value="ARBITRARY_ALGEBRA")
    try: verify_projection_evidence(apply_mutation(eq["evidence"],wrong))
    except ClosureError as exc: negatives.append(dict(kind="SERIALIZED_MUTATION",base_record_id=eq["record_id"],attack=wrong,reason=str(exc)))
    else: raise RuntimeError("wrong equivalence accepted")
    matrix={}
    for record in records:
        for index,(req,binding) in enumerate(zip(record["evidence"]["plan_before"]["requirements"],record["evidence"]["bindings"])):
            cap=req["capability"]; kind=digest(dict(capability=cap,evidence_kind=req["evidence_kind"],family=req["family"]))
            if kind in matrix: continue
            attack=dict(name="DELETE_KIND_BINDING",path=["bindings"],value=record["evidence"]["bindings"][:index]+record["evidence"]["bindings"][index+1:])
            try: verify_projection_evidence(apply_mutation(record["evidence"],attack))
            except ClosureError as exc: reason=str(exc)
            else: raise RuntimeError("requirement kind deletion accepted")
            matrix[kind]=dict(development_kind_id=kind,requirement_class=req["requirement_class"],capability=cap,
                semantic_role=cap["semantic_role"],evidence_kind=req["evidence_kind"],family=req["family"],input_domain=req["input_domain"],
                grammatical_source_form=req["occurrence_requirements"],mapping_path=binding["method"],positive_record_id=record["record_id"],
                development_requirement_id=req["requirement_id"],negative_example="DELETE_KIND_BINDING",negative_binding_index=index,
                negative_verifier_reason=reason,independent_verifier_result=record["verification"])
    rules={c["catalog_rule"] for r in records for c in r["evidence"]["claims"]}
    if not REQUIRED_RULES<=rules: raise RuntimeError("frozen equivalence family missing")
    from self_learning_ai.conf1_v3.requirements import frozen_metadata
    predicates={r["capability"]["operation"] for row in records for r in row["evidence"]["plan_before"]["requirements"] if r["capability"]["category"]=="SEMANTIC_PRIMITIVE"}
    expected_predicates={p["name"] for values in frozen_metadata()["predicate_definitions"].values() for p in values}
    if predicates!=expected_predicates: raise RuntimeError("primitive form coverage incomplete")
    forms={(r["evidence"]["plan_before"]["declaration"]["family"],r["evidence"]["plan_before"]["declaration"]["structure"],r["evidence"]["plan_before"]["declaration"]["reverse"]) for r in records}
    if forms!={(f,s,b) for f in d.PAIRS for s in ("PER_ITEM","PREFIX","TWO_PASS") for b in (False,True)}: raise RuntimeError("grammar traversal coverage missing")
    guards=[]
    for scope in ("SCIENTIFIC_TRAINING","SCIENTIFIC_EVALUATION"):
        forged=deepcopy(base["evidence"]["plan_before"]); forged["scope"]=scope
        try: verify_projection_plan(forged)
        except ClosureError as exc: guards.append(dict(scope=scope,reason=str(exc),source_parsed=False))
        else: raise RuntimeError("scientific namespace accepted")
    model=dict(scope="DEVELOPMENT_ONLY",implementation_readiness={k:"IMPLEMENTATION_READY" for k in ("INDICATOR","V32","V33")},
        scientific_instance_closure={k:"DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION" for k in ("INDICATOR","V32","V33")},
        scientific_sources_constructed=0,scientific_satisfaction_claims=0,scientific_expected_index_created=False,
        scientific_gate_semantics_changed=False,old_global_gate_artifacts_changed=False,population_producer_invoked=False,
        historical_8668_authoritative=False,grammar_forms=[list(x) for x in sorted(forms)],primitive_identities=sorted(predicates),
        frozen_equivalence_families=sorted(rules),matrix_quantifier="DEVELOPMENT REQUIREMENT KINDS, NOT SCIENTIFIC INSTANCES",
        edge_quantifier=base["evidence"]["plan_before"]["edge_obligation_quantifier"],
        other_core_gaps="state/essentiality/value/output/E5/V3.5/delegated/provenance/binder remain outside this pass")
    results=[dict(record_id=r["record_id"],evidence_sha256=r["evidence_sha256"],verification=r["verification"]) for r in records]
    files={"implementation_readiness_model.json":model,"canonical_requirement_kind_coverage_matrix.json":dict(rows=list(matrix.values())),
        "disposable_requirement_source_mappings.json":dict(records=records),
        "indicator_readiness_evidence.json":dict(records=[dict(record_id=r["record_id"],evidence=r["evidence"]["indicator_foundations"]) for r in records]),
        "v32_readiness_evidence.json":dict(records=results,typed_boundary_only_no_operator_alias=True),
        "v33_readiness_evidence.json":dict(records=[dict(record_id=r["record_id"],claims=r["evidence"]["claims"]) for r in records],rule_families=sorted(rules)),
        "independent_verifier_results.json":dict(records=results,constructor_pass_flag_trusted=False),
        "adversarial_mutation_results.json":dict(records=negatives),
        "namespace_isolation.json":dict(guards=guards,scientific_instance_closure="DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION",scientific_sources_constructed=0,scientific_requirements_satisfied=0),
        "disposable_overlap.json":overlap,"protected_integrity.json":{**integrity,"verifier_baseline_head":integrity["starting_head"],"starting_head":d.START},
        "verification_test_results.json":dict(focused=focused,known_legacy_failures=legacy,population_test_deselected=True,scientific_fixture_execution=False)}
    OUT.mkdir(parents=True)
    for name,value in files.items():
        value={"schema_version":1,"artifact_kind":"DEVELOPMENT_ONLY_GENERIC_BINDING_EVIDENCE","starting_head":d.START,**value}
        # The complete graphs are intentionally retained. Compact only this
        # large inventory; whitespace is not part of any evidence identity.
        encoded=json.dumps(value,sort_keys=True,separators=(",",":")) if name=="disposable_requirement_source_mappings.json" else json.dumps(value,sort_keys=True,indent=2)
        (OUT/name).write_text(encoded+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(dict(development_mapping_records=len(records),development_requirement_kinds=len(matrix),adversaries_rejected=len(negatives),
                         implementation_readiness=model["implementation_readiness"],scientific_instance_closure=model["scientific_instance_closure"]),indent=2))


if __name__=="__main__": run()
