"""Overlap first, prospective plan second, disposable parsing/binding last."""
from functools import lru_cache
import gbind905_inputs as d
PREFLIGHT=d.overlap()
from self_learning_ai.conf1_v3.projection_grammar import derive_projection_plan
from self_learning_ai.conf1_v3.projection_binding import bind_projection

EQUIVALENCES=(("numeric_iteration-ADD","FOLDED"),("ADD_SORT","ADD_SWAP"),("MUL_SORT","MUL_SWAP"),
              ("AND_SORT","AND_SWAP"),("OR_SORT","OR_SWAP"),("GT","GT_REVERSED"),("GE","GE_REVERSED"),
              ("EQ","EQ_REVERSED"),("DUPLICATES","DUPLICATES_REVERSED"))
REGIONAL=tuple((f+"-"+a,f+"-"+b,scope) for f in d.PAIRS for a,b,scope in
               (("PAIR_AND","0-PER_ITEM-FWD","LOCAL_PAIR_JOINT"),("OR","SUM_POSITIVE","BOOLEAN_OR")))

@lru_cache(maxsize=None)
def mapped(name,variant=None,scope=None):
    plan=derive_projection_plan(d.DECLARATIONS[name])
    source=d.VARIANTS[variant] if variant in d.VARIANTS else d.SOURCES[variant or name]
    return bind_projection(plan,d.SOURCES[name],source,region_scope=scope)


def negative(name,attack):
    return bind_projection(derive_projection_plan(d.DECLARATIONS[name]),d.SOURCES[name],d.BAD[attack])


def mutations(e):
    """Serializable operations, replayable by the independent saved checker."""
    import copy
    result=[]
    def add(name,path,value): result.append(dict(name=name,path=path,value=value))
    add("DEVELOPMENT_TO_SCIENTIFIC",["plan_after","scope"],"SCIENTIFIC_TRAINING")
    add("EVALUATION_NAMESPACE_FORGE",["plan_after","scope"],"SCIENTIFIC_EVALUATION")
    add("SLOT_INJECTION",["source"],e["source"]+" // CONF1-TR-NU-01-V0")
    add("MISSING_REQUIREMENT",["plan_before","requirements"],e["plan_before"]["requirements"][:-1])
    add("EXTRA_REQUIREMENT",["plan_before","requirements"],e["plan_before"]["requirements"]+[e["plan_before"]["requirements"][0]])
    add("DUPLICATE_SATISFACTION",["bindings",1],e["bindings"][0])
    add("MISSING_SATISFACTION",["bindings"],e["bindings"][:-1])
    add("WRONG_P_Q",["indicator_foundations","source",0,"role"],"Q")
    add("WRONG_LOOP_DIRECTION",["plan_before","declaration","reverse"],True)
    add("WRONG_LOOP_CONTEXT",["indicator_foundations","source",0,"loop"],"WRONG_DISPOSABLE_LOOP")
    add("STALE_INDICATOR",["indicator_foundations","source",0,"current_iteration"],False)
    add("TYPE_MISMATCH",["bindings",0,"capability","result_type"],"BOOLEAN")
    add("PORT_MISMATCH",["bindings",0,"control_state_context",0,"port"],999)
    add("PROVENANCE_PROMOTION",["source_projection_provenance","scientific_requirement_satisfaction"],True)
    graph=copy.deepcopy(e["source_graph"])
    # A graph field cannot confer a reference-only classification.
    item=next(iter(graph["nodes"])) if isinstance(graph["nodes"],dict) else 0
    add("INVENTED_REFERENCE_ONLY",["source_graph","nodes",item,"proof"],"REFERENCE_ONLY_BY_CALLER")
    add("BASE_PASS_FLAG",["base_mapping","all_raw_atomic_keys_satisfied"],False)
    return result


def apply_mutation(e,attack):
    from copy import deepcopy
    out=deepcopy(e); target=out
    for p in attack["path"][:-1]: target=target[p]
    target[attack["path"][-1]]=deepcopy(attack["value"])
    return out
