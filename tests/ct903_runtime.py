"""New disposable complete contracts, not frozen-population construction."""
import ct903_inputs as d
PREFLIGHT = d.overlap()
from self_learning_ai.conf1_v3.contract_ir import graph_record, keys_from_ir
from self_learning_ai.conf1_v3.contracts import CoverageContractV3, DOMAINS
from self_learning_ai.conf1_v3.core_ir import compile_program
from self_learning_ai.conf1_v3.interfaces import PHASE, rid
from self_learning_ai.conf1_v3.boolean_regions import total_boolean_mapping
def contract(name):
    pid = "CTRANSPORT903-" + name
    p = compile_program(pid, d.SOURCES[name]); keys, occurrences = keys_from_ir(p, ())
    return CoverageContractV3(1, PHASE, rid("CONTRACT", [pid]), pid, pid, "development", "ISOLATED", p.domain, DOMAINS[p.domain], (), (), {"kind": "disposable_canonical_transport"}, graph_record(p), keys, ("FIVE_DISPOSABLE_CASES",), tuple(p.roles.values()), {}, p.source, occurrences, p)
def certificate(left, right, scope):
    return total_boolean_mapping(contract(left), d.SOURCES[right], scope=scope)

def engine(folder, left, right, scope):
    from self_learning_ai.conf1_v3.coverage import CoverageEngine, PinnedCompilerOracle, reconcile_complete_mapping
    from self_learning_ai.conf1_v3.interfaces import ArtifactResolver, artifact_reference, canonical_json_bytes
    c = contract(left); cert = certificate(left, right, scope)
    mapping = reconcile_complete_mapping(c, d.SOURCES[right], region_evidence=cert)
    source_path, cases_path = folder / "source.goco", folder / "cases.json"
    source_path.write_bytes(d.SOURCES[right].encode())
    cases = {"schema_version": 1, "program_id": c.program_id, "cases": [{"case_id": "CTRANSPORT903-CASE-" + str(i), "input": raw, "expected_output": d.expected(right, raw)} for i, raw in enumerate(d.RAW)]}
    cases_path.write_bytes(canonical_json_bytes(cases))
    refs = [artifact_reference("CTRANSPORT903-SOURCE-ARTIFACT", "SOURCE_REFERENCE", source_path.name, source_path.read_bytes()), artifact_reference("CTRANSPORT903-CASE-ARTIFACT", "CASE_SET", cases_path.name, cases_path.read_bytes())]
    oracle = PinnedCompilerOracle(d.ROOT / ".tools/jdk-25.0.1+8/bin/java.exe", d.ROOT / ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    return CoverageEngine(mapping, resolver=ArtifactResolver(folder, refs), source_artifact_id=refs[0]["artifact_id"], case_artifact_id=refs[1]["artifact_id"], oracle=oracle)
