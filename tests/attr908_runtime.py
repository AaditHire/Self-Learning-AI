from functools import lru_cache
import attr908_inputs as d  # preflight BEFORE compiler/IR execution
from self_learning_ai.conf1_v3.projection_binding import bind_projection
from self_learning_ai.conf1_v3.state_evidence import construct_state_evidence
from self_learning_ai.conf1_v3.essentiality_evidence import construct_essentiality_evidence
from self_learning_ai.conf1_v3.attribute_evidence import construct_attribute_evidence
from self_learning_ai.conf1_v3.coverage import PinnedCompilerOracle
from self_learning_ai.conf1_v3.attribute_reference import digest_text

@lru_cache(maxsize=None)
def evidence(name):
    source=d.SOURCES[name];plan=d.PLANS[name]
    oracle=PinnedCompilerOracle(d.ROOT/".tools/jdk-25.0.1+8/bin/java.exe",d.ROOT/".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    compiler=dict(source_sha256=digest_text(source),oracle="PINNED_GOCO_COMPILER",
                  observations=[dict(raw_input=raw,output=oracle.run(source,raw)) for raw in d.RAW[name]])
    state=construct_state_evidence(plan,source,d.RAW[name]);mapping=bind_projection(plan,d.REFERENCE_SOURCES[name],source)
    essentiality=construct_essentiality_evidence(mapping,state,compiler)
    return construct_attribute_evidence(essentiality,d.OUTPUTS[name],d.LITERALS[name])
