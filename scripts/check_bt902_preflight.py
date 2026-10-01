"""Integrity and pre-repair reproduction only; no population derivation."""
from pathlib import Path
import importlib.util
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "src")]
import bt902_inputs as d
OUT = ROOT / "research/implementation_notes/coverage_v3_boolean_total_mapping"

def emit(name, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    if path.exists():
        if path.read_bytes() != raw: raise RuntimeError("saved evidence changed: " + name)
    else:
        with path.open("xb") as f: f.write(raw)

def preflight():
    spec = importlib.util.spec_from_file_location("bt902_integrity", ROOT / "scripts/audit_conf1_v3_core_closure.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    v = m.verify_protected_inputs(); v["starting_head"] = d.START
    emit("protected_input_integrity.json", v)
    # Earlier inventories are retained; the final source uses grouped products
    # to disambiguate GOCO's dot/member syntax between consecutive updates.
    emit("disposable_overlap_final.json", d.overlap())

def reproduce():
    preflight()  # Must precede classifier imports.
    from self_learning_ai.conf1_v3.core_ir import compile_program
    from self_learning_ai.conf1_v3.boolean_mapping import _sites
    from self_learning_ai.conf1_v3.semantic_ir import source_flow_equivalence
    from self_learning_ai.conf1_v3.contract_ir import graph_record, keys_from_ir
    from self_learning_ai.conf1_v3.contracts import CoverageContractV3, DOMAINS
    from self_learning_ai.conf1_v3.interfaces import PHASE, rid
    from self_learning_ai.conf1_v3.coverage import reconcile_complete_mapping
    rows = []
    saved_path = OUT / "reproduced_failure.json"
    saved = json.loads(saved_path.read_bytes())["records"] if saved_path.exists() else None
    for left, right, scope in d.PAIRS[:2]:
        pid = "BTOTAL902-" + left
        original = next((r for r in saved if r["contract_form"] == left and r["source_form"] == right), None) if saved else None
        source_pair = (original["contract_source"], original["source"]) if original else (d.SOURCES[left], d.SOURCES[right])
        if original:
            initial = json.loads((OUT / "disposable_overlap.json").read_bytes())["inventory"]["sources"]
            if any(not any(r["value"] == text and r["sha256_utf8"] == hashlib.sha256(text.encode()).hexdigest() for r in initial) for text in source_pair):
                raise RuntimeError("original reproduction source not bound to initial overlap inventory")
        a, b = (compile_program(pid, text) for text in source_pair)
        keys, occurrences = keys_from_ir(a, ())
        c = CoverageContractV3(1, PHASE, rid("CONTRACT", [pid]), pid, pid, "development", "ISOLATED", a.domain, DOMAINS[a.domain], (), (), {"kind": "disposable_boolean_total"}, graph_record(a), keys, ("FIVE_DISPOSABLE_CASES",), tuple(a.roles.values()), {}, a.source, occurrences, a)
        proof = source_flow_equivalence(a, _sites(a, scope)[0], b, _sites(b, scope)[0], context=scope)
        assert proof["finding"] == "EQUIVALENT"
        try: reconcile_complete_mapping(c, b.source)
        except Exception as exc: failure = {"type": type(exc).__name__, "reason": str(exc)}
        else: raise RuntimeError("pre-repair unexpectedly complete")
        assert failure["reason"] == "INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE"
        rows.append({"contract_form": left, "source_form": right, "contract_source": a.source, "source": b.source, "local_proof": proof, "total_mapping_failure": failure})
    emit("reproduced_failure.json", {"starting_head": d.START, "records": rows})
    print("Integrity unchanged; zero overlap; two valid local proofs / INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE reproduced")

if __name__ == "__main__": reproduce()
