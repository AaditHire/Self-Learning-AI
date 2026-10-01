"""Read-only saved transport/proof/activity-identity/mutation verification."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "src"))
from self_learning_ai.conf1_v3.transport_verifier import verify_canonical_transport, verify_mapping_proof_record
from self_learning_ai.conf1_v3.interfaces import ClosureError, canonical_json_bytes, rid
OUT = ROOT / "research/implementation_notes/coverage_v3_boolean_atomic_transport"
def read(name): return json.loads((OUT / name).read_bytes())
def apply_replacements(base, replacements):
    result = deepcopy(base)
    for op in replacements:
        if not op["path"]: result=op["value"]; continue
        target=result
        for part in op["path"][:-1]: target=target[part]
        target[op["path"][-1]]=op["value"]
    return result
def run():
    bundles=read("canonical_semantic_transport_records.json")["records"]
    proofs=read("production_mapping_proof_results.json")["records"]
    checks=read("independent_transport_verifier_results.json")["records"]
    activities=read("activity_semantic_key_derivations.json")["records"]
    dags=read("proof_dependency_graphs.json")["records"]
    if not len(bundles)==len(proofs)==len(checks)==len(activities)==len(dags)==6: raise RuntimeError("saved transport population incomplete")
    for b,p,c,a,d in zip(bundles,proofs,checks,activities,dags):
        bundle=b["bundle"]; digest=hashlib.sha256(canonical_json_bytes(bundle)).hexdigest()
        if any(r["bundle_sha256"]!=digest or r["pair"]!=b["pair"] for r in (b,p,c,a,d)): raise RuntimeError("saved transport reference mismatch")
        checked=verify_canonical_transport(bundle)
        if canonical_json_bytes(checked)!=canonical_json_bytes(c["transport_verification"]): raise RuntimeError("saved transport result mismatch")
        if canonical_json_bytes(verify_mapping_proof_record(bundle,p["mapping_proof"]))!=canonical_json_bytes(c["production_mapping_verification"]): raise RuntimeError("saved production proof mismatch")
        if canonical_json_bytes(d["graph"])!=canonical_json_bytes(bundle["proof_dependency_graph"]): raise RuntimeError("saved DAG mismatch")
        keys={t["semantic_key_id"] for t in bundle["transports"]}
        activity=a["activity"]
        if activity["source_sha256"]!=bundle["source_sha256"] or canonical_json_bytes(activity["verifier_result"])!=canonical_json_bytes(checked): raise RuntimeError("saved activity source/proof mismatch")
        if activity["caller_semantic_key_accepted"] is not False or activity["raw_graphs_modified"] is not False or activity["artifact_kind"]!="PROOF_DERIVED_SEMANTIC_ACTIVITY_NOT_POPULATION": raise RuntimeError("unauthorized saved activity identity")
        if len(activity["records"])!=len(keys): raise RuntimeError("duplicate saved activity identity")
        if {r["semantic_key_id"] for r in a["activity"]["records"]}!=keys: raise RuntimeError("unproved saved activity key")
        for row in a["activity"]["records"]:
            selected=[t for t in bundle["transports"] if t["semantic_key_id"]==row["semantic_key_id"]]
            if row["activity_identity"]!=rid("SEMANTIC_ACTIVITY",[bundle["contract"]["contract_id"],row["semantic_key_id"]]) or row["mapping_proof_sha256"]!=hashlib.sha256(canonical_json_bytes(p["mapping_proof"])).hexdigest(): raise RuntimeError("saved activity identity/hash mismatch")
            if canonical_json_bytes(row["semantic_definition"])!=canonical_json_bytes(selected[0]["semantic_definition"]) or row["canonical_semantic_key_ids"]!=[row["semantic_key_id"]]: raise RuntimeError("saved activity semantic definition mismatch")
            if row["obligation_ids"]!=[t["obligation_id"] for t in selected] or row["transport_references"]!=[t["transport_id"] for t in selected]: raise RuntimeError("saved activity proof references mismatch")
            destinations={t["activity_destination"]["occurrence_id"]:t["activity_destination"] for t in selected}
            raw_evidence=row["raw_source_activity_evidence"]
            if set(raw_evidence["raw_occurrences"])!=set(destinations) or len(raw_evidence["raw_occurrences"])!=len(destinations): raise RuntimeError("saved activity destination inventory mismatch")
            if {raw["occurrence_id"] for raw in raw_evidence["raw_destinations"]}!=set(destinations) or len(raw_evidence["raw_destinations"])!=len(destinations): raise RuntimeError("saved raw activity evidence incomplete")
            for raw in row["raw_source_activity_evidence"]["raw_destinations"]:
                dest=destinations[raw["occurrence_id"]]
                if (raw["operation"],raw["datatype"],raw["result_role"])!=(dest["raw_operation"],dest["raw_type"],dest["raw_role"]): raise RuntimeError("raw activity identity was rewritten")
    attacks=0
    for row in read("negative_transport_results.json")["records"]:
        if row["kind"]!="SERIALIZED_MUTATION": continue
        attacks+=1; attacked=apply_replacements(bundles[row["base_pair_index"]]["bundle"],row["replace_operations"])
        try: verify_canonical_transport(attacked)
        except ClosureError as exc:
            if str(exc)!=row["actual_reason"] or row["expected_reason"] not in str(exc): raise RuntimeError("saved transport mutation reason mismatch")
        else: raise RuntimeError("saved transport mutation accepted")
    print(json.dumps({"saved_transports_verified":6,"saved_mapping_proofs_verified":6,"saved_activity_identities_verified":6,"saved_mutations_rejected":attacks,"constructor_invoked":False,"writes":0},indent=2))
if __name__ == "__main__": run()
