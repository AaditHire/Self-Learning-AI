"""Prospective declaration first; disposable raw contract second; mapping last."""
import creq904_inputs as d
PREFLIGHT=d.overlap()
from self_learning_ai.conf1_v3.requirements import derive_development
from self_learning_ai.conf1_v3.contracts import CoverageContractV3, DOMAINS
from self_learning_ai.conf1_v3.contract_ir import graph_record, keys_from_ir
from self_learning_ai.conf1_v3.core_ir import compile_program
from self_learning_ai.conf1_v3.interfaces import PHASE, rid
from self_learning_ai.conf1_v3.coverage import reconcile_complete_mapping
from self_learning_ai.conf1_v3.boolean_regions import total_boolean_mapping

def plan(name): return derive_development(d.declaration(name))
def contract(name):
    # Requirement projection exists before the raw parser is invoked.
    prospective=plan(name); p=compile_program(prospective["program_id"],d.SOURCES[name]); keys,occ=keys_from_ir(p,())
    return CoverageContractV3(1,PHASE,rid("CONTRACT",[p.program_id]),p.program_id,p.program_id,"development","ISOLATED",p.domain,DOMAINS[p.domain],(),(),{"kind":"development_projection_not_frozen_training"},graph_record(p),keys,("NO_SCIENTIFIC_CASES",),tuple(p.roles.values()),{},p.source,occ,p)
def mapped(left,right,scope=None):
    prospective=plan(left); c=contract(left)
    cert=total_boolean_mapping(c,d.SOURCES[right],scope=scope) if scope else None
    return reconcile_complete_mapping(c,d.SOURCES[right],requirement_plan=prospective,region_evidence=cert)
