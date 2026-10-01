"""Read-only independent verification of SAVED region evidence, no constructor."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.conf1_v3.boolean_region_checker import check_serialized_mapping, extract_indicator_evidence
from self_learning_ai.conf1_v3.interfaces import ClosureError, canonical_json_bytes
OUT = ROOT / "research/implementation_notes/coverage_v3_boolean_total_mapping"

def read(name): return json.loads((OUT / name).read_bytes())

def run():
    mappings = read("total_mapping_certificates.json")["records"]
    checks = read("independent_checker_results.json")["records"]
    regions = read("equivalence_region_certificates.json")["records"]
    dags = read("proof_dependency_graphs.json")["records"]
    indicators = read("indicator_evidence.json")["records"]
    if not len(mappings) == len(checks) == len(regions) == len(dags) == len(indicators) == 6:
        raise RuntimeError("saved record inventory incomplete")
    for row, check, region, dag, indicator in zip(mappings, checks, regions, dags, indicators):
        cert = row["certificate"]; digest = hashlib.sha256(canonical_json_bytes(cert)).hexdigest()
        common = {k: row[k] for k in ("contract_form", "source_form", "mapping_sha256")}
        if any(record.get("mapping_sha256") != digest or any(record[k] != common[k] for k in common) for record in (row, check, region, dag, indicator)):
            raise RuntimeError("saved certificate/reference hash mismatch")
        rebuilt = {**common, **check_serialized_mapping(cert)}
        if canonical_json_bytes(rebuilt) != canonical_json_bytes(check): raise RuntimeError("saved independent result mismatch")
        if canonical_json_bytes(region["regions"]) != canonical_json_bytes(cert["regions"]) or canonical_json_bytes(dag["graph"]) != canonical_json_bytes(cert["proof_dependency_graph"]):
            raise RuntimeError("saved region/DAG reference mismatch")
        if canonical_json_bytes(indicator) != canonical_json_bytes({**common, **extract_indicator_evidence(cert)}): raise RuntimeError("saved indicator evidence mismatch")
    attacks = 0
    for row in read("adversarial_negative_results.json")["records"]:
        if row["kind"] != "SERIALIZED_EVIDENCE_MUTATION": continue
        attacks += 1
        try: check_serialized_mapping(row["mutation_evidence"])
        except ClosureError as exc:
            if str(exc) != row["reason"] or row["expected_reason"] not in str(exc): raise RuntimeError("saved mutation reason mismatch")
        else: raise RuntimeError("saved mutation accepted")
    print(json.dumps({"saved_total_certificates_verified": len(mappings), "saved_mutations_rejected": attacks, "constructor_invoked": False, "writes": 0}, indent=2))

if __name__ == "__main__": run()
