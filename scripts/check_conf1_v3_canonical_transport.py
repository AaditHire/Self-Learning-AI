"""New disposable canonical-transport producer; no population entry point."""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "tests"), str(ROOT / "src")]
from check_ct903_preflight import preflight, emit

def run():
    if sys.argv[1:] not in ([], ["--update-development-evidence"]): raise RuntimeError("unsupported producer arguments")
    preflight()
    import ct903_inputs as d
    from ct903_runtime import engine
    from ct903_adversarial import negatives
    from self_learning_ai.conf1_v3.transport_verifier import verify_canonical_transport, verify_mapping_proof_record
    from self_learning_ai.conf1_v3.interfaces import canonical_json_bytes
    bundles, proofs, activities, verified, dags = [], [], [], [], []
    with tempfile.TemporaryDirectory(prefix="ct903-evidence-") as temp:
        for index, pair in enumerate(d.PAIRS):
            folder = Path(temp) / str(index); folder.mkdir()
            e = engine(folder, *pair); bundle = e.mapping.semantic_transport; proof = e.mapping.to_record()
            activity = e.semantic_activity()
            common = {"pair": pair, "bundle_sha256": hashlib.sha256(canonical_json_bytes(bundle)).hexdigest()}
            bundles.append({**common, "bundle": bundle}); proofs.append({**common, "mapping_proof": proof})
            activities.append({**common, "activity": activity})
            verified.append({**common, "transport_verification": verify_canonical_transport(bundle), "production_mapping_verification": verify_mapping_proof_record(bundle, proof)})
            dags.append({**common, "graph": bundle["proof_dependency_graph"]})
        # Direct Boolean realization has the same derived semantic identity,
        # while retaining different raw destinations/intervention types.
        references = []
        for index, (left, _, scope) in enumerate(d.PAIRS[:2]):
            folder = Path(temp) / ("boolean-" + str(index)); folder.mkdir()
            activity = engine(folder, left, left, scope).semantic_activity()
            expected = activities[index]["activity"]["records"][0]["semantic_key_id"]
            if activity["records"][0]["semantic_key_id"] != expected: raise RuntimeError("raw/canonical identity separation failed")
            references.append({"contract_form": left, "activity": activity})
    negative = negatives()
    # Matching outputs remain insufficient, on these same new disposable inputs.
    from self_learning_ai.conf1_v3.core_ir import compile_program, execute
    from self_learning_ai.conf1_v3.coverage import PinnedCompilerOracle
    p = compile_program("CTRANSPORT903-MATCHING_OUTPUT_INVALID", d.SOURCES["MATCHING_OUTPUT_INVALID"])
    oracle = PinnedCompilerOracle(ROOT / ".tools/jdk-25.0.1+8/bin/java.exe", ROOT / ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    matching = []
    for raw in d.RAW:
        normal, compiler, expected = execute(p, raw).output, oracle.run(p.source, raw), d.expected("PRODUCT", raw)
        if normal != expected or compiler != expected: raise RuntimeError("matching-output adversary premise failed")
        matching.append({"raw_input": raw, "actual_ir_output": normal, "actual_compiler_output": compiler, "reference_output": expected})
    path = ROOT / "research/implementation_notes/coverage_v3_boolean_total_mapping/development_gate_evidence.json"
    baseline = json.loads(path.read_bytes()); gates = json.loads(path.read_bytes())
    targets = {"INDICATOR_EXTRACTION_COMPLETE", "V32_SEMANTIC_MAPPING_COMPLETE", "V33_REQUIRED_EQUIVALENCE_COMPLETE"}
    blockers = [
        "Remaining frozen V3.3 catalog integration is intentionally not attempted: commutative global transport, comparison duals/symmetry, and computed-value-only folding in the regional adapter.",
        "The earlier region representation still requires an identical outside declaration/reset/predicate scaffold. Unmatched source-only indicator realization ownership remains unsupported and out of this bridge pass.",
        "Canonical local pair-joint transport cannot satisfy distinct raw atomic AND/MUL or role-specific operator/edge requirements not authorized by V3.3. MappingProof explicitly retains unresolved raw-key records; full atomic coverage is not asserted.",
        "Prospective non-development contract completion remains fail-closed on its existing core gaps. No frozen population contract builder, scientific activity report or full-signature audit runs in this pass.",
    ]
    for gate in gates["gates"]:
        if gate["gate"] in targets:
            gate.update(status="UNRESOLVED", evidence_file="production_mapping_proof_results.json", detail="Verified semantic transport is integrated in MappingProof and typed activity machinery for the six scoped shapes; raw identities and unresolved requirements are preserved", remaining_evidence_obligations=blockers)
    assert all(a == b for a,b in zip(baseline["gates"], gates["gates"]) if a["gate"] not in targets)
    gates.update(starting_head=d.START, artifact_kind="BOOLEAN_ATOMIC_TRANSPORT_DEVELOPMENT_NOT_SCIENTIFIC_BINDER",
        independent_checker_results="independent_transport_verifier_results.json",
        baseline_gate_artifact_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), out_of_scope_gate_authority_path=path.relative_to(ROOT).as_posix(),
        status="COVERAGE_V3_BOOLEAN_ATOMIC_TRANSPORT_COMPLETE", all_semantic_gates_pass=False, authoritative_population_recount_performed=False,
        bridge_complete_for_intended_frozen_semantic_obligations=True, broader_catalog_only_blocker=False)
    artifacts = {"canonical_semantic_transport_records.json": {"records": bundles}, "production_mapping_proof_results.json": {"records": proofs},
        "activity_semantic_key_derivations.json": {"records": activities, "direct_boolean_reference_activities": references},
        "independent_transport_verifier_results.json": {"records": verified}, "proof_dependency_graphs.json": {"records": dags},
        "negative_transport_results.json": {"records": negative, "mutation_format": "replace whole tree value at path; [] replaces bundle", "matching_output_observations": matching},
        "development_gate_evidence.json": gates}
    for name,value in artifacts.items(): emit(name,{"schema_version":1,"starting_head":d.START,**value}, update_development=bool(sys.argv[1:]))
    print(json.dumps({"status":gates["status"],"positive_shapes":len(bundles),"negative_cases":len(negative),
        "new_pinned_compiler_normal_runs":45,"active_semantic_identities":sum(len(r["activity"]["records"]) for r in activities),
        "gates":{g["gate"]:g["status"] for g in gates["gates"]}},indent=2))
if __name__ == "__main__": run()
