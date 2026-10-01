"""Integrity, overlap, and captured pre-bridge raw atomic mismatch."""
from pathlib import Path
import importlib.util
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "src")]
import ct903_inputs as d
OUT = ROOT / "research/implementation_notes/coverage_v3_boolean_atomic_transport"
def emit(name, value, *, update_development=False):
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    OUT.mkdir(parents=True, exist_ok=True); path = OUT / name
    if path.exists():
        if path.read_bytes().replace(b"\r\n", b"\n") != raw:
            allowed = {"canonical_semantic_transport_records.json", "production_mapping_proof_results.json", "activity_semantic_key_derivations.json", "independent_transport_verifier_results.json", "proof_dependency_graphs.json", "negative_transport_results.json", "development_gate_evidence.json"}
            if not update_development or name not in allowed: raise RuntimeError("saved evidence differs: " + name)
            # Explicit refresh of only this pass's generated development results.
            path.write_bytes(raw)
    else:
        with path.open("xb") as f: f.write(raw)
def preflight():
    spec = importlib.util.spec_from_file_location("ct903_integrity", ROOT / "scripts/audit_conf1_v3_core_closure.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    v = m.verify_protected_inputs(); v["starting_head"] = d.START
    emit("protected_input_integrity.json", v); emit("disposable_overlap.json", d.overlap())
def reproduce():
    preflight()
    from ct903_runtime import contract, certificate
    from self_learning_ai.conf1_v3.boolean_region_checker import check_serialized_mapping
    from self_learning_ai.conf1_v3.coverage import reconcile_complete_mapping
    from self_learning_ai.conf1_v3.contract_ir import keys_from_ir
    from self_learning_ai.conf1_v3.core_ir import compile_program
    records = []
    for left, right, scope in d.PAIRS[:2]:
        c = contract(left); cert = certificate(left, right, scope)
        checked = check_serialized_mapping(cert)
        try: reconcile_complete_mapping(c, d.SOURCES[right])
        except Exception as exc: failure = {"type": type(exc).__name__, "reason": str(exc)}
        else: raise RuntimeError("strict raw mapper unexpectedly accepted")
        assert failure["reason"] == "INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE"
        source_keys, _ = keys_from_ir(compile_program(c.program_id, d.SOURCES[right]))
        records.append({"contract_form": left, "source_form": right, "region_certificate": cert, "independent_result": checked,
            "strict_mapping_failure": failure, "contract_raw_operator_keys": [k.to_dict() for k in c.canonical_keys if k.operation in {"AND", "OR"}],
            "source_raw_operator_keys": [k.to_dict() for k in source_keys if k.operation in {"MUL", "ADD", "GT"}], "raw_key_equality_claim": False})
    emit("reproduced_atomic_key_mismatch.json", {"starting_head": d.START, "records": records})
    print("Protected identities unchanged; zero overlap; two independently total regions / strict raw-key mismatch saved")
if __name__ == "__main__": reproduce()
