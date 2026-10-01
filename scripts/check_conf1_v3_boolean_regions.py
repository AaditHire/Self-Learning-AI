"""Reproducible disposable region evidence; never population/scientific work."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "tests"), str(ROOT / "src")]
from check_bt902_preflight import preflight, emit


def run():
    preflight()
    import bt902_inputs as d
    from bt902_runtime import certificate
    from bt902_adversarial import negatives
    from self_learning_ai.conf1_v3.boolean_region_checker import check_serialized_mapping, extract_indicator_evidence
    from self_learning_ai.conf1_v3.boolean_mapping import frozen_boolean_catalog
    from self_learning_ai.conf1_v3.interfaces import canonical_json_bytes
    certs, regions, checks, dags, indicators = [], [], [], [], []
    for left, right, scope in d.PAIRS:
        cert = certificate(left, right, scope)
        if cert["finding"] != "COMPLETE": raise RuntimeError((left, right, cert.get("reason")))
        digest = hashlib.sha256(canonical_json_bytes(cert)).hexdigest()
        common = {"contract_form": left, "source_form": right, "mapping_sha256": digest}
        certs.append({**common, "certificate": cert})
        regions.append({**common, "regions": cert["regions"]})
        checks.append({**common, **check_serialized_mapping(json.loads(json.dumps(cert)))})
        dags.append({**common, "graph": cert["proof_dependency_graph"]})
        indicators.append({**common, **extract_indicator_evidence(cert)})
    negative = negatives()
    path = ROOT / "research/implementation_notes/coverage_v3_boolean_mapping/development_gate_evidence.json"
    baseline = json.loads(path.read_bytes()); gates = json.loads(path.read_bytes())
    blockers = [
        "This internal mapper supports only direct bounded-loop child singleton conditional +=1 / proven-01 product += regions with an identical outside declaration/reset/predicate scaffold; unmatched source-only indicator realization declarations/resets have no authorized region owner yet.",
        "Complete integration of the remaining V3.3 structural normalizations (pure commutative child sorting retaining duplicates, comparison duals/symmetric equality, computed-value-only constant folding) is not implemented by this region/scaffold mapper; their separate local recognizers do not establish totality here.",
        "Differing AND/MUL typed atomic keys and their distinct control/value edge requirements remain distinct. Region semantic correspondence is not automatic canonical-key/activity transport; no V3.5 activity or full-signature audit is performed.",
    ]
    targets = {"INDICATOR_EXTRACTION_COMPLETE", "V32_SEMANTIC_MAPPING_COMPLETE", "V33_REQUIRED_EQUIVALENCE_COMPLETE"}
    for gate in gates["gates"]:
        if gate["gate"] in targets:
            gate.update(status="UNRESOLVED", evidence_file="total_mapping_certificates.json", detail="Six total development correspondences independently verified; scoped successes do not close the full frozen obligations", remaining_evidence_obligations=blockers)
    assert all(a == b for a, b in zip(baseline["gates"], gates["gates"]) if a["gate"] not in targets)
    gates.update(starting_head=d.START, artifact_kind="INTERNAL_BOOLEAN_REGION_DEVELOPMENT_NOT_SCIENTIFIC_BINDER", baseline_gate_artifact_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        out_of_scope_gate_authority_path=path.relative_to(ROOT).as_posix(), status="STOPPED_COVERAGE_V3_BOOLEAN_TOTAL_MAPPING_ISSUE", all_semantic_gates_pass=False,
        authoritative_population_recount_performed=False, full_signature_audit_performed=False,
        scoped_total_correspondences=len(certs), independent_checker_results="independent_checker_results.json")
    # Actual executions are only these new sources/inputs. No scientific cases.
    from self_learning_ai.conf1_v3.core_ir import compile_program, execute
    from self_learning_ai.conf1_v3.coverage import PinnedCompilerOracle
    from test_conf1_v3_boolean_regions import expected
    oracle = PinnedCompilerOracle(ROOT / ".tools/jdk-25.0.1+8/bin/java.exe", ROOT / ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    normal = []
    for name in ("AND", "PRODUCT", "OR", "SUM", "REPEATED_AND", "REPEATED_PRODUCT", "ALPHA_PRODUCT", "ALPHA_SUM", "SAME_OUTPUT"):
        p = compile_program("BTOTAL902-" + name, d.SOURCES[name])
        for i, raw in enumerate(d.RAW):
            actual, compiler, reference = execute(p, raw).output, oracle.run(p.source, raw), expected(name, raw)
            if actual != compiler or actual != reference: raise RuntimeError("normal compiler/reference mismatch")
            normal.append({"program_id": p.program_id, "case_id": "BTOTAL902-CASE-" + str(i), "raw_input": raw, "actual_ir_output": actual, "actual_compiler_output": compiler, "reference_output": reference})
    known = {r["capability"] for name in ("ODD", "RESIDUE", "DIVISOR", "HALF", "ARRAY") for r in compile_program("BTOTAL902-" + name, d.SOURCES[name]).semantic_records}
    assert known == {"odd_index", "residue_two", "divisor_index", "first_half", "negative_value", "even_value", "large_magnitude", "value_exceeds_index"}
    artifacts = {"equivalence_region_certificates.json": {"records": regions, "catalog": frozen_boolean_catalog()},
        "total_mapping_certificates.json": {"records": certs}, "independent_checker_results.json": {"records": checks, "primitive_catalog": sorted(known)},
        "proof_dependency_graphs.json": {"records": dags}, "indicator_evidence.json": {"records": indicators},
        "adversarial_negative_results.json": {"records": negative, "new_normal_compiler_observations": normal}, "development_gate_evidence.json": gates}
    for name, value in artifacts.items(): emit(name, {"schema_version": 1, "starting_head": d.START, **value})
    print(json.dumps({"total_correspondences": len(certs), "negatives": len(negative), "new_compiler_observations": len(normal), "gates": {g["gate"]: g["status"] for g in gates["gates"]}, "status": gates["status"]}, indent=2))

if __name__ == "__main__": run()
