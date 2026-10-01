"""Prospective DEVELOPMENT_ONLY grammar; no scientific slot materializer.

Requirements are declared from a typed grammatical tree BEFORE a realization
is parsed. Paths address grammatical sites, never parser occurrence IDs.
This is implementation evidence, not task essentiality or a population.
"""
import re
from collections import OrderedDict
from .interfaces import ClosureError, rid
from .requirements import frozen_metadata, digest, expression
from .core_ir import infer_type, ungroup, OPERATORS, TYPE_NAMES
from .contracts import DOMAINS
from .semantic_ir import predicate_signature, frozen_predicates


def require(ok, reason):
    if not ok:
        raise ClosureError(reason)


def development_identity(value):
    # Also rejects a scientific slot injected in a comment/string/provenance.
    require(not re.search(r"CONF1-(?:TR|ISOLATED|COMPOSITION|NC|PS|ST)(?:-|\b)", str(value)),
            "SCIENTIFIC_IDENTITY_IN_DEVELOPMENT_PROJECTION")


def validate_declaration(d):
    require(set(d) == {"program_id", "family", "role_bindings", "structure",
                      "treatment", "reverse", "offset", "repeat", "expression", "unused"},
            "PROJECTION_DECLARATION_SCHEMA")
    development_identity(d)
    require(isinstance(d["program_id"], str) and d["program_id"], "PROJECTION_PROGRAM_ID")
    ledger = frozen_metadata()
    require(d["family"] in ledger["predicate_definitions"], "PROJECTION_DOMAIN")
    names = {p["name"] for p in ledger["predicate_definitions"][d["family"]]}
    require(set(d["role_bindings"]) == {"P", "Q"} and
            set(d["role_bindings"].values()) <= names, "PROJECTION_PREDICATE_ROLES")
    require(d["structure"] in {"PER_ITEM", "PREFIX", "TWO_PASS"}, "PROJECTION_STRUCTURE")
    require(d["treatment"] in {"ADD", "PRODUCT", "PAIR_AND", "OR", "SUM_POSITIVE", "EXPRESSION"},
            "PROJECTION_TREATMENT")
    require(type(d["reverse"]) is bool and type(d["unused"]) is bool, "PROJECTION_BOOLEAN_FIELDS")
    # Deliberately outside every frozen training offset. Not a scientific rule.
    require(type(d["offset"]) is int and d["offset"] >= 1000, "DISPOSABLE_OFFSET_REQUIRED")
    require(type(d["repeat"]) is int and d["repeat"] in {1, 2}, "PROJECTION_REPETITION")
    require((isinstance(d["expression"], str) and d["expression"]) if d["treatment"] == "EXPRESSION"
            else d["expression"] is None, "PROJECTION_EXPRESSION")


def grammar(d):
    """A declarative statement/expression tree, not a source/parser inventory."""
    validate_declaration(d)
    array = d["family"] == "array_reduction"
    definitions = {p["name"]: p["expression"] for p in frozen_metadata()["predicate_definitions"][d["family"]]}
    def st(kind, value="", expressions=(), children=(), index=None, region=False):
        return dict(kind=kind, value=value, expressions=list(expressions), children=list(children),
                    index=index, region=region)
    def decl(name, value=None, typ="NUMBER"):
        return st("DECLARE", typ+":"+name, () if value is None else (str(value),))
    def update(name, value, op="+="):
        return st("UPDATE", op, (name, str(value)))
    def check(role, index):
        text = re.sub(r"\bi\b", index, definitions[d["role_bindings"][role]])
        return st("IF", expressions=(text,), children=(update("hit"+role, 1, "="),))
    def loop(index, body):
        if d["reverse"]:
            initial = "3" if array else "n"
            return [decl(index, initial), st("LOOP", "REVERSE", (index+(">=0" if array else ">=1"),),
                    [*body, update(index, 1, "-=")], index)]
        return [st("LOOP", "FORWARD", ("0" if array else "1", index+("<4" if array else "<=n")), body, index)]
    rows = ([st("IMPORT", "strings"), decl("raw", typ="SENTENCE"), st("INPUT", expressions=("raw",)),
             decl("fields", 'strings.SPLIT(raw,"|")', "SENTENCE[]"),
             *[decl("field"+str(i), "strings.TO_NUMBER(fields["+str(i)+"])") for i in range(4)],
             decl("values", "[field0,field1,field2,field3]", "NUMBER[]")]
            if array else [decl("n"), st("INPUT", expressions=("n",))])
    rows += [decl("total", d["offset"]), decl("hitP", 0), decl("hitQ", 0)]
    if d["unused"]:
        rows += [decl("unused", 1877)]
    def checks(index):
        return [update("hitP", 0, "="), update("hitQ", 0, "="), check("P", index), check("Q", index)]
    if d["structure"] == "PER_ITEM":
        body = checks("i")
        for _ in range(d["repeat"]):
            if d["treatment"] in {"PAIR_AND", "OR", "SUM_POSITIVE"}:
                a, b = definitions[d["role_bindings"]["P"]], definitions[d["role_bindings"]["Q"]]
                test = "("+a+")"+("&&" if d["treatment"] == "PAIR_AND" else "||")+"("+b+")"
                if d["treatment"] == "SUM_POSITIVE": test = "hitP+hitQ>0"
                body += [st("IF", expressions=(test,), children=(update("total", 1),), region=True)]
            else:
                term = "hitP+hitQ" if d["treatment"] == "ADD" else "hitP*hitQ" if d["treatment"] == "PRODUCT" else d["expression"]
                if d["treatment"] == "EXPRESSION" and infer_type(expression(term), {"n":"INTEGER","i":"INTEGER","values":"INTEGER_ARRAY"}) == "BOOLEAN":
                    body += [st("IF", expressions=(term,), children=(update("total",1),))]
                else:
                    body += [update("total", term)]
        rows += loop("i", body)
    elif d["structure"] == "PREFIX":
        rows += [decl("seen", 0)]
        rows += loop("i", [*checks("i"), st("IF", expressions=("hitQ==1",), children=(update("total", "seen"),)),
                           st("IF", expressions=("hitP==1",), children=(update("seen", 1),))])
    else:
        rows += [decl("left", 0), decl("right", 0)]
        for index, role, target in (("i", "P", "left"), ("j", "Q", "right")):
            rows += loop(index, [*checks(index), update(target, "hit"+role)])
        rows += [update("total", "left*right")]
    rows += [st("DISPLAYNL", expressions=("total",))]
    symbols = OrderedDict()
    def symbols_in(block):
        for s in block:
            if s["kind"] == "DECLARE":
                typ, name = s["value"].split(":"); symbols[name] = TYPE_NAMES[typ]
            if s["kind"] == "LOOP" and s["value"] == "FORWARD": symbols[s["index"]] = "INTEGER"
            symbols_in(s["children"])
    symbols_in(rows)
    roles = {n: "LOCAL_VALUE" for n in symbols}
    roles.update({"raw": "RAW_INPUT", "n": "INPUT_LIMIT", "fields": "SPLIT_FIELDS",
                  "values": "DOMAIN_SEQUENCE", "total": "DISPLAYED_ACCUMULATOR", "hitP": "INDICATOR",
                  "hitQ": "INDICATOR", "seen": "ACCUMULATOR", "left": "ACCUMULATOR", "right": "ACCUMULATOR"})
    for n in symbols:
        if n in {"i", "j"}: roles[n] = "ITEM_INDEX" if array else "DOMAIN_ITEM"
        if n.startswith("field") and n != "fields": roles[n] = "DECODED_FIELD"
    return rows, symbols, {n: roles[n] for n in symbols}


def render_development(d, prefix):
    rows, symbols, _ = grammar(d)
    require(bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", prefix)), "PROJECTION_PREFIX")
    development_identity(prefix)
    def ex(text):
        return re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\b", lambda m: prefix+m[0] if m[0] in symbols else m[0], text)
    def block(rows):
        out = []
        for s in rows:
            k, v, es = s["kind"], s["value"], s["expressions"]
            if k == "IMPORT": out.append("IMPORT strings.")
            elif k == "DECLARE":
                typ, name = v.split(":"); out.append(typ+" "+ex(name)+("="+ex(es[0]) if es else "")+".")
            elif k in {"INPUT", "DISPLAYNL"}: out.append(k+"("+ex(es[0])+").")
            elif k == "UPDATE": out.append(ex(es[0])+v+(ex(es[1]) if v=="-=" else "("+ex(es[1])+")")+".")
            elif k == "IF": out.append("IF ("+ex(es[0])+") { "+block(s["children"])+" }")
            else:
                header = ("NUMBER "+ex(s["index"])+"="+ex(es[0])+" TILL "+ex(es[1])+", "+ex(s["index"])+"++") if v == "FORWARD" else ex(es[0])
                out.append("LOOP ("+header+") { "+block(s["children"])+" }")
        return " ".join(out)
    return block(rows)


def recipe(d):
    rows, symbols, roles = grammar(d); units = []
    imports = frozenset({"strings"}) if d["family"] == "array_reduction" else frozenset()
    catalog = frozen_predicates(d["family"])
    def node(path, op, category, typ, operands=(), role="", value=None, selector=None, operand_roles=(), result_role=None):
        units.append(dict(path=path, capability=dict(category=category, operation=op, operand_types=list(operands),
                     operand_roles=list(operand_roles),result_type=typ,result_role=result_role or role,semantic_role=role, value=value), selector=selector or dict(kind="NODE", path=path)))
    def expr(e, path, role):
        e = ungroup(e); typ = infer_type(e, symbols, imports)
        if e.kind == "CALL": op, cat, args = "strings."+e.children[0].value, "API_DECODER", e.children[1:]
        else:
            args = e.children
            op, cat = ((OPERATORS[e.value], "ATOMIC_OPERATOR") if e.kind == "BINARY" else
                       ("NEG" if e.value == "-" else "NOT", "ATOMIC_OPERATOR") if e.kind == "UNARY" else
                       ("COMPUTED_VALUE" if e.kind == "NUMBER" else "LITERAL_TOKEN", "VALUE_OR_LITERAL") if e.kind in {"NUMBER", "STRING"} else
                       ("ARRAY_INDEX", "API_DECODER") if e.kind == "INDEX" else
                       ("FOUR_DOMAIN_VALUES", "API_DECODER") if e.kind == "ARRAY" else ("READ", "GENERIC_CONSTRUCT"))
        if e.kind == "ID": role = roles[e.value]
        value = int(e.value) if e.kind == "NUMBER" else e.value if e.kind == "STRING" else None
        raw_op="CONSTANT" if cat=="VALUE_OR_LITERAL" else op
        operand_roles=[roles.get(c.value,raw_op+"_OPERAND_"+str(i)) if c.kind=="ID" else raw_op+"_OPERAND_"+str(i) for i,c in enumerate(args)]
        node(path, op, cat, typ, [infer_type(c, symbols, imports) for c in args], role, value,operand_roles=operand_roles)
        primitive = catalog.get(predicate_signature(e, symbols, roles))
        if primitive:
            node(path+"/primitive", primitive, "SEMANTIC_PRIMITIVE", "BOOLEAN", [infer_type(c,symbols,imports) for c in args], "PREDICATE_BOOLEAN",
                 selector=dict(kind="PRIMITIVE", path=path),operand_roles=operand_roles)
        for i, child in enumerate(args): expr(child, path+"/a"+str(i), roles.get(child.value, op+"_OPERAND_"+str(i)) if child.kind == "ID" else op+"_OPERAND_"+str(i))
    def visit(block, prefix=""):
        for i, s in enumerate(block):
            path = prefix+"/s"+str(i); k=s["kind"]
            if k == "IMPORT": continue
            if k == "DECLARE" and s["value"].endswith(":unused"): continue
            if s["region"]:
                op="LOCAL_PAIR_JOINT" if d["treatment"] == "PAIR_AND" else "OR"
                node(path+"/relation", op, None if op=="LOCAL_PAIR_JOINT" else "ATOMIC_OPERATOR", "BOOLEAN", ("BOOLEAN","BOOLEAN"), "PAIR_RELATION",
                     value=list(d["role_bindings"].values()), selector=dict(kind="REGION", path=path),operand_roles=("P_PREDICATE","Q_PREDICATE"))
                continue
            op = {"DECLARE":"INITIALIZE","INPUT":"INPUT","DISPLAYNL":"FINAL_DISPLAY","IF":"IF","LOOP":"BOUNDED_LOOP"}.get(k,
                  "ASSIGN" if s["value"]=="=" else "ACCUMULATE" if s["value"]=="+=" else "INDEX_STEP")
            role = roles[s["value"].split(":")[1]] if k=="DECLARE" else roles[s["expressions"][0]] if k in {"UPDATE","INPUT"} else "OUTPUT" if k=="DISPLAYNL" else "CONTROL"
            typ = symbols[s["value"].split(":")[1]] if k=="DECLARE" else symbols[s["expressions"][0]] if k=="INPUT" else "BOOLEAN" if k in {"IF","LOOP"} else "INTEGER"
            operands = () if k in {"DECLARE","INPUT"} else ("BOOLEAN",) if k in {"IF","LOOP"} else ("INTEGER",)
            ors=() if not operands else ("PREDICATE_BOOLEAN",) if k=="IF" else ("LOOP_BOUND",) if k=="LOOP" else ("DISPLAYED_ACCUMULATOR",) if k=="DISPLAYNL" else ("CONTRIBUTION",)
            node(path, op, "API_DECODER" if k=="INPUT" else "GENERIC_CONSTRUCT", typ, operands, role,operand_roles=ors)
            for j, text in enumerate(s["expressions"]):
                if k=="INPUT" or k=="UPDATE" and j==0: continue
                er = "INITIAL_"+role if k=="DECLARE" else "CONTRIBUTION" if k=="UPDATE" else "PREDICATE_BOOLEAN" if k=="IF" else "DISPLAYED_ACCUMULATOR" if k=="DISPLAYNL" else "LOOP_INITIAL" if j==0 and s["value"]=="FORWARD" else "LOOP_BOUND"
                expr(expression(text), path+"/e"+str(j), er)
            if k=="LOOP" and s["value"]=="FORWARD":
                for part, op2 in (("initial","LOOP_INDEX_INITIALIZE"),("step","LOOP_INDEX_STEP")):
                    node(path+"/"+part, op2, "GENERIC_CONSTRUCT", "INTEGER", role=roles[s["index"]], selector=dict(kind="INDEX_STATE",path=path,part=part))
            visit(s["children"], path+"/body")
    visit(rows)
    node("domain", "INPUT_DOMAIN:"+("FOUR_SIGNED_INTEGER_FIELDS" if imports else "NONNEGATIVE_INTEGER"), "API_DECODER", "STRING" if imports else "INTEGER", role="DOMAIN_DECODER", selector=dict(kind="DOMAIN"))
    # Atomic edge TYPES are prospective obligations, not scientific instances.
    # Each is a typed one-edge witness. Complete multiplicity stays in the graph.
    edge_roles = {
        "INPUT_TO_DECODER": ("STRING" if imports else "INTEGER", "DOMAIN_DECODER", "RAW_INPUT" if imports else "INPUT_LIMIT"),
        "VALUE_TO_PREDICATE": ("BOOLEAN", "PREDICATE_BOOLEAN", "PREDICATE_BOOLEAN"),
        "PREDICATE_TO_CONTROL": ("BOOLEAN", "PREDICATE_BOOLEAN", "CONTROL"),
        "PREDICATE_TO_INDICATOR": ("BOOLEAN", "PREDICATE_BOOLEAN", "INDICATOR"),
        "VALUE_TO_OPERATOR": ("INTEGER", "INITIAL_DISPLAYED_ACCUMULATOR", "DISPLAYED_ACCUMULATOR"),
        "OPERATOR_TO_ACCUMULATOR": ("INTEGER", "CONTRIBUTION", "INDICATOR"),
        "CONTROL_TO_UPDATE": ("BOOLEAN", "CONTROL", "INDICATOR"),
        "LOOP_CARRY": ("INTEGER", "DISPLAYED_ACCUMULATOR" if d["structure"] != "TWO_PASS" else "ACCUMULATOR", "DISPLAYED_ACCUMULATOR" if d["structure"] != "TWO_PASS" else "ACCUMULATOR"),
        "PRIOR_STATE_TO_UPDATE": ("INTEGER", "DISPLAYED_ACCUMULATOR", "DISPLAYED_ACCUMULATOR"),
        "ACCUMULATOR_TO_OUTPUT": ("INTEGER", "DISPLAYED_ACCUMULATOR", "OUTPUT")}
    for op, (typ, source_role, target_role) in edge_roles.items():
        selector=dict(kind="EDGE_KIND", operation=op, datatype=typ, source_role=source_role, target_role=target_role)
        node("edge_kind/"+op, op, "ATOMIC_CONTROL_DATAFLOW", typ, (typ,), source_role+"->"+target_role, selector=selector,operand_roles=(source_role,),result_role=target_role)
    return units


def derive_projection_plan(d):
    units=recipe(d); groups=OrderedDict()
    for u in units: groups.setdefault(digest(u["capability"]), []).append(u)
    requirements=[]
    for cap_id, members in groups.items():
        cap=members[0]["capability"]; key=rid("DEVELOPMENT_ONLY_KIND",[d["family"],cap_id])
        req=rid("DEVELOPMENT_ONLY_BINDING_REQUIREMENT",[d["program_id"],key])
        requirements.append(dict(requirement_id=req,canonical_contract_key=key,capability=cap,
            requirement_class="LOCAL_PAIR_JOINT_RELATION_EXCEPTION" if cap["category"] is None else "ONTOLOGY_KEY",
            scope="DEVELOPMENT_ONLY",evidence_kind="VALUE_OR_LITERAL_ATTRIBUTE" if cap["category"]=="VALUE_OR_LITERAL" else "BEHAVIORAL",
            family=d["family"],input_domain=DOMAINS[d["family"]],multiplicity=len(members),occurrence_requirements=[dict(grammar_path=u["path"],selector=u["selector"]) for u in members]))
    return dict(schema_version=1,artifact_kind="DEVELOPMENT_ONLY_PROSPECTIVE_GRAMMAR_PLAN",scope="DEVELOPMENT_ONLY",
                program_id=d["program_id"],declaration=d,requirements=requirements,requirements_sha256=digest(requirements),
                scientific_expected_row_index_eligible=False,scientific_slot_binding=None,
                provenance=dict(declaration_sha256=digest(d),authority="Coverage V3.2/V3.3 closed grammatical forms; development projection only",
                                frozen_slot_role_map_created=False),
                edge_obligation_quantifier="ONE_TYPED_EDGE_PER_KIND; full graph multiplicity is separately retained")
