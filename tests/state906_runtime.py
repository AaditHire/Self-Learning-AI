from functools import lru_cache
from copy import deepcopy
import state906_inputs as d
from self_learning_ai.conf1_v3.state_evidence import construct_state_evidence

@lru_cache(maxsize=None)
def evidence(name,alpha=False):
    return construct_state_evidence(d.PLANS[name],d.ALPHA[name] if alpha else d.SOURCES[name],d.RAW[d.DECLARATIONS[name]["family"]])


def mutations(e):
    return [dict(name="MISSING_STATE_EDGE",path=["state_graph","required_state_edges"],value=e["state_graph"]["required_state_edges"][:-1]),
        dict(name="DUPLICATE_STATE_EDGE",path=["state_graph","matched_state_edges"],value=e["state_graph"]["matched_state_edges"]+[e["state_graph"]["matched_state_edges"][0]]),
        dict(name="FABRICATED_RECURRENCE_LABEL",path=["required_computation","recurrence_class"],value="TWO_PASS"),
        dict(name="STALE_RUNTIME_WRITER",path=["executions",0,"agreement","trace",0,"writer"],value="STALE_WRITER"),
        dict(name="WRONG_SOURCE_RUNTIME_MAP",path=["executions",0,"agreement","read_write_agreement",0,"actual_writer"],value="FOREIGN_WRITER"),
        dict(name="CONSTRUCTOR_READINESS_FORGE",path=["state_implementation_readiness"],value="SCIENTIFIC_PASS"),
        dict(name="SCIENTIFIC_TRAINING_PROMOTION",path=["scope"],value="SCIENTIFIC_TRAINING"),
        dict(name="SCIENTIFIC_EVALUATION_PROMOTION",path=["scope"],value="SCIENTIFIC_EVALUATION"),
        dict(name="SCIENTIFIC_SLOT_INJECTION",path=["source"],value=e["source"]+" // CONF1-TR-NU-01-V0"),
        dict(name="SCIENTIFIC_CLOSURE_FORGE",path=["scientific_instance_closure"],value="PASS")]


def mutate(e,attack):
    r=deepcopy(e);target=r
    for x in attack["path"][:-1]: target=target[x]
    target[attack["path"][-1]]=deepcopy(attack["value"])
    return r
