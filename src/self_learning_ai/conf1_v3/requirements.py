"""Prospective, source-independent requirement namespaces.

These records are NOT CoverageContractV3, an expected-row index, a V3.5
population, or activity evidence. Scientific derivation reads only frozen
metadata. Disposable projections cannot be cast into scientific contracts.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from .interfaces import ClosureError, SchemaError, canonical_json_bytes, rid
from .contracts import DOMAINS
from .goco import Parser
from .core_ir import infer_type, ungroup, OPERATORS

ROOT = Path(__file__).resolve().parents[3]
SCOPES = ("SCIENTIFIC_TRAINING", "SCIENTIFIC_EVALUATION", "DEVELOPMENT_ONLY")
AUTHORITY = "research/protocols/phase3c_conf1_slots.json"

def digest(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()

def frozen_metadata():
    freeze=(ROOT/"research/protocols/phase3c_conf1_delegated_evidence_interfaces_freeze.json").read_bytes()
    if hashlib.sha256(freeze).hexdigest()!="bd7a7fc6862ce049c1fdf363f763e1a3a17808132291b9064e3c6f26fb720948":
        raise ClosureError("FROZEN_REQUIREMENT_AUTHORITY_MANIFEST_CHANGED")
    for ref in json.loads(freeze)["upstream_authorities"].values():
        content=(ROOT/ref["path"]).read_bytes()
        if ref.get("hash_policy")=="SHA256_UTF8_CRLF_TO_LF" or "sha256_utf8_crlf_to_lf" in ref:
            content=content.replace(b"\r\n",b"\n"); expected=ref.get("sha256_utf8_crlf_to_lf",ref.get("sha256"))
        else: expected=ref.get("sha256_exact_bytes",ref.get("sha256"))
        if hashlib.sha256(content).hexdigest()!=expected: raise ClosureError("FROZEN_REQUIREMENT_NORMATIVE_AUTHORITY_CHANGED: "+ref["path"])
    raw = (ROOT / AUTHORITY).read_bytes().replace(b"\r\n", b"\n")
    if hashlib.sha256(raw).hexdigest() != "83436eecda3affe813b785e868e3f8936fa59afc35ded0eb6a54290edb41dc88":
        raise ClosureError("FROZEN_REQUIREMENT_LEDGER_CHANGED")
    coverage = (ROOT / "research/protocols/phase3c_conf1_coverage_v3_proposed.md").read_bytes().replace(b"\r\n", b"\n")
    if hashlib.sha256(coverage).hexdigest() != "a9fb8350c849ce62e2a673e3ca1f1d5a08f556b7f415687f1e2eabdf356030f3":
        raise ClosureError("FROZEN_REQUIREMENT_ONTOLOGY_CHANGED")
    return json.loads(raw)

def expression(text):
    parser = Parser(text); result = parser.expr()
    if parser.peek().kind != "EOF": raise SchemaError("requirement expression trailing tokens")
    return ungroup(result)

def unit(path, category, operation, operands, result, role, *, dependencies=(), value=None, operand_roles=None):
    return dict(path=path, category=category, operation=operation, operand_types=list(operands),
        operand_roles=list(operand_roles) if operand_roles is not None else [role+f"/operand/{i}" for i in range(len(operands))],
        result_type=result, result_role=role, semantic_role=role, dependencies=list(dependencies), value=value)

def expression_units(text, symbols, path):
    """Interpret the frozen semantic expression, never generated GOCO source."""
    out = []
    def visit(e, here):
        e = ungroup(e); typ = infer_type(e, symbols)
        if e.kind == "ID": return
        if e.kind == "NUMBER":
            out.append(unit(here, "VALUE_OR_LITERAL", "COMPUTED_VALUE", (), typ, here, value=int(e.value)))
            return
        if e.kind == "INDEX": op, category = "ARRAY_INDEX", "API_DECODER"
        elif e.kind == "BINARY": op, category = OPERATORS[e.value], "ATOMIC_OPERATOR"
        else: raise SchemaError("unlisted frozen requirement expression")
        ts = [infer_type(c, symbols) for c in e.children]
        binding_roles={"n":"INPUT_LIMIT","i":"DOMAIN_ITEM","values":"DOMAIN_SEQUENCE",**{r:r+"_PREDICATE" for r in "PQRS"}}
        rs=[binding_roles.get(ungroup(c).value,here+f"/operand/{i}") if ungroup(c).kind=="ID" else here+f"/operand/{i}" for i,c in enumerate(e.children)]
        out.append(unit(here, category, op, ts, typ, here,operand_roles=rs))
        for i,c in enumerate(e.children):
            child = here + f"/operand/{i}"; visit(c, child)
            out.append(unit(child + "/edge", "ATOMIC_CONTROL_DATAFLOW", "VALUE_TO_OPERATOR",
                (ts[i],), ts[i], child + "->" + here, dependencies=(child, here)))
    visit(expression(text), path)
    return out

def training_recipe(slot, condition, ledger):
    """Closed §6 scaffold + ledger expressions; no parser/IR inventory input."""
    if condition not in {"ISOLATED", "COMPOSITION"}: raise SchemaError("training condition required")
    expected_fields = {"slot_id","family","P","Q","unordered_pair","variant","offset","reverse"}
    if set(slot) != expected_fields: raise SchemaError("frozen training slot schema")
    domain = slot["family"]; definitions = {p["name"]:p["expression"] for p in ledger["predicate_definitions"][domain]}
    if sorted((slot["P"],slot["Q"])) != sorted(slot["unordered_pair"]): raise SchemaError("frozen unordered pair")
    if ledger["training_semantics"] != {"isolated":"per-item hitP+hitQ","composition":"per-item hitP*hitQ"}:
        raise SchemaError("frozen treatment grammar")
    symbols = {"i":"INTEGER", "n":"INTEGER", "values":"INTEGER_ARRAY"}
    raw_type = "INTEGER" if domain == "numeric_iteration" else "STRING"
    result = [unit("domain", "API_DECODER", "INPUT_DOMAIN:"+DOMAINS[domain], (), raw_type, "DOMAIN_DECODER"),
        unit("input", "API_DECODER", "INPUT", (), raw_type, "DOMAIN_INPUT"),
        unit("traversal", "GENERIC_CONSTRUCT", "BOUNDED_LOOP", ("BOOLEAN",), "BOOLEAN", "ITEM_TRAVERSAL"),
        unit("total/initial", "VALUE_OR_LITERAL", "COMPUTED_VALUE", (), "INTEGER", "INITIAL_ACCUMULATOR", value=slot["offset"])]
    # Orientation is semantic slot metadata, not inferred from source tokens.
    bound="i>=1" if domain=="numeric_iteration" and slot["reverse"] else "i<=n" if domain=="numeric_iteration" else "i>=0" if slot["reverse"] else "i<4"
    result += expression_units(bound,symbols,"traversal/bound")
    result.append(unit("traversal/step","GENERIC_CONSTRUCT","INDEX_STEP" if slot["reverse"] else "LOOP_INDEX_STEP",("INTEGER",),"INTEGER","ITEM_TRAVERSAL",value=-1 if slot["reverse"] else 1))
    if domain == "array_reduction":
        result += [unit("decoder/split", "API_DECODER", "strings.SPLIT", ("STRING","STRING"), "STRING_ARRAY", "FOUR_FIELDS"),
            unit("decoder/separator", "VALUE_OR_LITERAL", "LITERAL_TOKEN", (), "STRING", "FIELD_SEPARATOR", value='"|"')]
        for field in range(4):
            result.append(unit(f"decoder/field/{field}", "API_DECODER", "strings.TO_NUMBER", ("STRING",), "INTEGER", "DOMAIN_FIELD"))
    for role in ("P","Q"):
        pred = slot[role]; path = role+"/predicate"
        result.append(unit(path, "SEMANTIC_PRIMITIVE", pred, ("INTEGER","INTEGER"), "BOOLEAN", role+"_PREDICATE"))
        result += expression_units(definitions[pred], symbols, path+"/definition")
        result += [unit(role+"/control", "GENERIC_CONSTRUCT", "IF", ("BOOLEAN",), "BOOLEAN", role+"_CONTROL"),
            unit(role+"/indicator", "GENERIC_CONSTRUCT", "ASSIGN", ("INTEGER",), "INTEGER", role+"_INDICATOR",value={"declaration":0,"per_item_reset":0,"predicate_true_write":1,"current_iteration":True}),
            unit(role+"/predicate_to_control", "ATOMIC_CONTROL_DATAFLOW", "PREDICATE_TO_CONTROL", ("BOOLEAN",), "BOOLEAN", role+"_PREDICATE->CONTROL", dependencies=(path, role+"/control")),
            unit(role+"/predicate_to_indicator", "ATOMIC_CONTROL_DATAFLOW", "PREDICATE_TO_INDICATOR", ("BOOLEAN",), "BOOLEAN", role+"_PREDICATE->INDICATOR", dependencies=(path, role+"/indicator")),
            unit(role+"/indicator_to_treatment", "ATOMIC_CONTROL_DATAFLOW", "VALUE_TO_OPERATOR", ("INTEGER",), "INTEGER", role+"_INDICATOR->TREATMENT", dependencies=(role+"/indicator", "treatment")),
            unit(role+"/control_to_update", "ATOMIC_CONTROL_DATAFLOW", "CONTROL_TO_UPDATE", ("BOOLEAN",), "BOOLEAN", role+"_CONTROL->INDICATOR", dependencies=(role+"/control", role+"/indicator"))]
    op = "ADD" if condition == "ISOLATED" else "MUL"
    result.append(unit("treatment", "ATOMIC_OPERATOR", op, ("INTEGER","INTEGER"), "INTEGER", "INDEPENDENT_CONTRIBUTIONS" if op=="ADD" else "JOINT_INDICATOR_PRODUCT"))
    if condition == "COMPOSITION":
        # This is the explicitly authorized relation exception, NOT AND=MUL.
        result.append(unit("pair_joint", None, "LOCAL_PAIR_JOINT", ("BOOLEAN","BOOLEAN"), "BOOLEAN", "PAIR_JOINT", dependencies=("P/predicate", "Q/predicate", "treatment")))
    result += [unit("total/update", "GENERIC_CONSTRUCT", "ACCUMULATE", ("INTEGER",), "INTEGER", "DISPLAYED_ACCUMULATOR"),
        unit("treatment_to_total", "ATOMIC_CONTROL_DATAFLOW", "OPERATOR_TO_ACCUMULATOR", ("INTEGER",), "INTEGER", "CONTRIBUTION->DISPLAYED_ACCUMULATOR", dependencies=("treatment", "total/update")),
        unit("traversal_to_total", "ATOMIC_CONTROL_DATAFLOW", "CONTROL_TO_UPDATE", ("BOOLEAN",), "BOOLEAN", "TRAVERSAL->DISPLAYED_ACCUMULATOR", dependencies=("traversal", "total/update")),
        unit("total/prior", "ATOMIC_CONTROL_DATAFLOW", "PRIOR_STATE_TO_UPDATE", ("INTEGER",), "INTEGER", "DISPLAYED_ACCUMULATOR->UPDATE"),
        unit("total/carry", "ATOMIC_CONTROL_DATAFLOW", "LOOP_CARRY", ("INTEGER",), "INTEGER", "DISPLAYED_ACCUMULATOR->DISPLAYED_ACCUMULATOR"),
        unit("total/output", "ATOMIC_CONTROL_DATAFLOW", "ACCUMULATOR_TO_OUTPUT", ("INTEGER",), "INTEGER", "DISPLAYED_ACCUMULATOR->OUTPUT")]
    return result

def development_recipe(declaration, ledger):
    if set(declaration) != {"program_id","family","role_bindings","contributions"}: raise SchemaError("development declaration schema")
    family = declaration["family"]; catalog = {p["name"] for p in ledger["predicate_definitions"][family]}
    bindings = declaration["role_bindings"]
    if not isinstance(bindings,dict) or not set(bindings)<=set("PQRS") or not set(bindings.values())<=catalog:
        raise SchemaError("development predicate projection")
    result = []
    if not isinstance(declaration["contributions"],list) or not declaration["contributions"]: raise SchemaError("development contribution grammar")
    for i,c in enumerate(declaration["contributions"]):
        if set(c)!={"expression","mode"} or c["mode"] not in {"COUNT_TRUE","NUMERIC_UPDATE"}: raise SchemaError("development contribution schema")
        e = expression(c["expression"]); symbols={"n":"INTEGER","i":"INTEGER",**{r:"BOOLEAN" for r in bindings}}
        typ = infer_type(e,symbols)
        if typ != ("BOOLEAN" if c["mode"]=="COUNT_TRUE" else "INTEGER"): raise SchemaError("development contribution type")
        path=f"contribution/{i}"
        if c["mode"]=="COUNT_TRUE" and e.kind=="BINARY" and e.value in {"&&","||"} and all(ungroup(x).kind=="ID" and ungroup(x).value in bindings for x in e.children):
            op="LOCAL_PAIR_JOINT" if e.value=="&&" else "OR"
            result.append(unit(path,None if op=="LOCAL_PAIR_JOINT" else "ATOMIC_OPERATOR",op,("BOOLEAN","BOOLEAN"),"BOOLEAN",path,dependencies=tuple(bindings[ungroup(x).value] for x in e.children)))
        else:
            result += expression_units(c["expression"],symbols,path)
    return result

def requirement_record(scope, program_id, provenance, recipe_unit, family):
    capability = {k:v for k,v in recipe_unit.items() if k!="path"}
    kind = "VALUE_OR_LITERAL_ATTRIBUTE" if capability["category"]=="VALUE_OR_LITERAL" else "BEHAVIORAL"
    key = rid(scope+"_KEY", [family, DOMAINS[family], digest(capability)])
    req = rid(scope+"_REQUIREMENT", [program_id, key, recipe_unit["path"]])
    return dict(scope=scope, program_id=program_id, canonical_contract_key=key, requirement_id=req,
        capability=capability, requirement_class="LOCAL_PAIR_JOINT_RELATION_EXCEPTION" if capability["category"] is None else "ONTOLOGY_KEY",
        evidence_kind=kind, family=family, input_domain=DOMAINS[family],
        semantic_role=capability["semantic_role"], operand_types=capability["operand_types"], result_type=capability["result_type"],
        occurrence_requirements=[dict(occurrence_id=rid(scope+"_OCCURRENCE",[req,recipe_unit["path"]]), grammar_path=recipe_unit["path"])],
        multiplicity=1, provenance=provenance,
        derivation_reason="Required by declared semantic grammar before parsing/mapping; raw syntax, outputs and evidence outcomes are not inputs")

def _plan(scope, pid, provenance, recipe, family, declaration):
    rows=[requirement_record(scope,pid,provenance,u,family) for u in recipe]
    if scope=="SCIENTIFIC_TRAINING":
        grouped={}
        for row in rows:
            key=row["canonical_contract_key"]
            if key in grouped: grouped[key]["occurrence_requirements"]+=row["occurrence_requirements"]
            else:
                row["requirement_id"]=rid(scope+"_REQUIREMENT",[pid,key]); grouped[key]=row
        rows=list(grouped.values())
        for row in rows:
            row["multiplicity"]=len(row["occurrence_requirements"])
            row["occurrence_requirements"]=[dict(occurrence_id=rid(scope+"_OCCURRENCE",[row["requirement_id"],o["grammar_path"]]),grammar_path=o["grammar_path"]) for o in row["occurrence_requirements"]]
    return dict(schema_version=1, artifact_kind="PROSPECTIVE_REQUIREMENT_FOUNDATION_NOT_V35_POPULATION", scope=scope,
        program_id=pid, declaration=declaration, requirements=rows, requirements_sha256=digest(rows),
        scientific_expected_row_index_eligible=False, completion="FOUNDATION_ONLY_NOT_FULL_CONTRACT",
        deferred_obligations=[] if scope=="DEVELOPMENT_ONLY" else ["OUTPUT_CASE_OBLIGATIONS_UNRESOLVED","VALUE_LITERAL_ATTACHMENT_COMPLETE_UNRESOLVED","COMPLETE_TYPED_SOURCE_MAPPING_NOT_RUN"])

def derive_training_slot(slot_id, condition):
    ledger=frozen_metadata(); slots=[s for s in ledger["slots"]["training_paired_slots"] if s["slot_id"]==slot_id]
    if len(slots)!=1: raise SchemaError("unknown frozen training slot")
    slot=slots[0]; pid=slot_id.replace("CONF1-",f"CONF1-{condition}-",1)
    provenance=dict(authority_path=AUTHORITY, authority_sha256_lf="83436eecda3affe813b785e868e3f8936fa59afc35ded0eb6a54290edb41dc88", slot_id=slot_id,
        sections=["Coverage V3.1/V3.2/V3.6","CONF1 protocol §6"], frozen_slot=slot,
        frozen_training_semantics=ledger["training_semantics"], condition=condition)
    return _plan("SCIENTIFIC_TRAINING",pid,provenance,training_recipe(slot,condition,ledger),slot["family"],dict(slot_id=slot_id,condition=condition))

def derive_development(declaration):
    ledger=frozen_metadata(); provenance=dict(authority_path=AUTHORITY, slot_id=None,
        frozen_role_map_created=False, scientific_slot_binding=None,
        authority_sections=["Coverage V3.3 implementation projection only"], declaration_sha256=digest(declaration))
    return _plan("DEVELOPMENT_ONLY",declaration["program_id"],provenance,development_recipe(declaration,ledger),declaration["family"],declaration)

def evaluation_namespace(slot_id):
    ledger=frozen_metadata(); matches=[s for g in ("primary","primitive_sanity","structural_transfer") for s in ledger["slots"][g] if s["task_id"]==slot_id]
    if len(matches)!=1: raise SchemaError("unknown frozen evaluation slot")
    slot=matches[0]
    return dict(scope="SCIENTIFIC_EVALUATION", slot_id=slot_id, frozen_slot=slot, authority_path=AUTHORITY,
        namespace_id=rid("SCIENTIFIC_EVALUATION_NAMESPACE",[slot_id,digest(slot)]),
        requirement_derivation_status="NOT_ATTEMPTED", scientific_expected_row_index_eligible=False, training_requirement_transfer_authorized=False)

def assert_no_scope_transfer(before, after):
    if canonical_json_bytes(before)!=canonical_json_bytes(after): raise ClosureError("REQUIREMENT_SET_OR_SCOPE_CHANGED")

def require_scientific_index_eligibility(plan, scope="SCIENTIFIC_TRAINING"):
    if plan.get("scope")!=scope: raise ClosureError("CROSS_SCOPE_SCIENTIFIC_PROMOTION_FORBIDDEN")
    raise ClosureError("V3_5_POPULATION_UNRESOLVED: foundation records are not complete prospective contracts")
