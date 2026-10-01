"""Disposable normal/compiler-bound engines, shared by tests and diagnostics."""
from pathlib import Path
import sem900_development_inputs as dev

PREFLIGHT=dev.overlap()  # Before classifier imports.

from self_learning_ai.conf1_v3.contract_ir import graph_record,keys_from_ir
from self_learning_ai.conf1_v3.contracts import CoverageContractV3,DOMAINS
from self_learning_ai.conf1_v3.core_ir import compile_program
from self_learning_ai.conf1_v3.coverage import CoverageEngine,PinnedCompilerOracle,reconcile_complete_mapping
from self_learning_ai.conf1_v3.interfaces import PHASE,artifact_reference,ArtifactResolver,canonical_json_bytes,rid


def contract(source,program_id,outputs=()):
    p=compile_program(program_id,source);keys,occurrences=keys_from_ir(p,outputs)
    return CoverageContractV3(1,PHASE,rid("CONTRACT",[program_id]),program_id,program_id,
        "development","ISOLATED",p.domain,DOMAINS[p.domain],(),(),{"kind":"disposable_semantic_core"},
        graph_record(p),keys,("FIVE_DISPOSABLE_CASES",),tuple(p.roles.values()),{},source,occurrences,p)


def engine(folder:Path,name:str):
    outputs=("OUTPUT_ZERO","OUTPUT_POSITIVE","OUTPUT_MULTIDIGIT") if name=="TWO_PASS" else (
        "OUTPUT_NEGATIVE","OUTPUT_MULTIDIGIT","OUTPUT_EXACT_SENTINEL:-19") if name in {"INITIAL","INITIAL_FOLDED"} else (
        "OUTPUT_POSITIVE","OUTPUT_MULTIDIGIT","OUTPUT_EXACT_SENTINEL:37")
    program_id="SEMCORE-900-"+name;source=dev.SOURCES[name]
    c=contract(source,program_id,outputs)
    inputs=dev.ARRAY_RAW if name=="ARRAY" else dev.RAW
    cases={"schema_version":1,"program_id":program_id,"cases":[
        {"case_id":cid,"input":raw,"expected_output":str(dev.expected(name,raw))}
        for cid,raw in zip(dev.CASE_IDS,inputs)]}
    source_path=folder/"source.goco";source_path.write_bytes(source.encode())
    case_path=folder/"cases.json";case_path.write_bytes(canonical_json_bytes(cases))
    refs=[artifact_reference("SEMCORE-900-SOURCE-ARTIFACT","SOURCE_REFERENCE",source_path.name,source_path.read_bytes()),
          artifact_reference("SEMCORE-900-CASE-ARTIFACT","CASE_SET",case_path.name,case_path.read_bytes())]
    oracle=PinnedCompilerOracle(dev.ROOT/".tools/jdk-25.0.1+8/bin/java.exe",dev.ROOT/".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    return CoverageEngine(reconcile_complete_mapping(c,source),resolver=ArtifactResolver(folder,refs),
        source_artifact_id=refs[0]["artifact_id"],case_artifact_id=refs[1]["artifact_id"],oracle=oracle)
