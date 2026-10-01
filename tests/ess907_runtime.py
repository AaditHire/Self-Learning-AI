from functools import lru_cache
import ess907_inputs as d
from self_learning_ai.conf1_v3.projection_binding import bind_projection
from self_learning_ai.conf1_v3.state_evidence import construct_state_evidence
from self_learning_ai.conf1_v3.essentiality_evidence import construct_essentiality_evidence
from self_learning_ai.conf1_v3.coverage import PinnedCompilerOracle

@lru_cache(maxsize=None)
def compiler(name,alpha=False):
    from self_learning_ai.conf1_v3.projection_binding_verifier import digest_source
    source=d.ALPHA[name] if alpha else d.SOURCES[name]
    oracle=PinnedCompilerOracle(d.ROOT/".tools/jdk-25.0.1+8/bin/java.exe",d.ROOT/".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar")
    return dict(source_sha256=digest_source(source),oracle="PINNED_GOCO_COMPILER",
        observations=[dict(raw_input=raw,output=oracle.run(source,raw)) for raw in d.RAW[d.DECLARATIONS[name]["family"]]])

@lru_cache(maxsize=None)
def evidence(name,alpha=False):
    source=d.ALPHA[name] if alpha else d.SOURCES[name];plan=d.PLANS[name]
    state=construct_state_evidence(plan,source,d.RAW[d.DECLARATIONS[name]["family"]])
    mapping=bind_projection(plan,d.SOURCES[name],source)
    return construct_essentiality_evidence(mapping,state,compiler(name,alpha))
