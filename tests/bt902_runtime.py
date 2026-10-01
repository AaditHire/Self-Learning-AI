"""Fresh development contracts, never scientific slot/population production."""
import bt902_inputs as d
PREFLIGHT = d.overlap()
from self_learning_ai.conf1_v3.contract_ir import graph_record, keys_from_ir
from self_learning_ai.conf1_v3.contracts import CoverageContractV3, DOMAINS
from self_learning_ai.conf1_v3.core_ir import compile_program
from self_learning_ai.conf1_v3.interfaces import PHASE, rid
from self_learning_ai.conf1_v3.boolean_regions import total_boolean_mapping

def contract(name):
    pid = "BTOTAL902-" + name
    p = compile_program(pid, d.SOURCES[name]); keys, occurrences = keys_from_ir(p, ())
    return CoverageContractV3(1, PHASE, rid("CONTRACT", [pid]), pid, pid, "development", "ISOLATED", p.domain, DOMAINS[p.domain], (), (), {"kind": "disposable_boolean_total"}, graph_record(p), keys, ("FIVE_DISPOSABLE_CASES",), tuple(p.roles.values()), {}, p.source, occurrences, p)

def certificate(left, right, scope):
    c = contract(left)
    return total_boolean_mapping(c, d.SOURCES[right], scope=scope)
