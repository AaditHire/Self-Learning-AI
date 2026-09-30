"""Closed, non-model typed IR and bounded execution for Coverage-v3.

The graph retains occurrences, bindings, branch order and state. Execution never
uses Python eval/exec, edits source text, or accepts supplied activity flags.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Mapping

from .goco import Expr, Stmt, parse, _walk_expr, _walk_stmt
from .interfaces import SchemaError, rid

EDGES = frozenset({"INPUT_TO_DECODER", "VALUE_TO_PREDICATE", "PREDICATE_TO_CONTROL",
    "PREDICATE_TO_INDICATOR", "VALUE_TO_OPERATOR", "OPERATOR_TO_ACCUMULATOR",
    "CONTROL_TO_UPDATE", "LOOP_CARRY", "PRIOR_STATE_TO_UPDATE", "ACCUMULATOR_TO_OUTPUT"})
OPERATORS = {"+": "ADD", "-": "SUB", "*": "MUL", "%": "MOD", "==": "EQ",
             "!=": "NE", "<": "LT", "<=": "LE", ">": "GT", ">=": "GE",
             "&&": "AND", "||": "OR", "!": "NOT"}
TYPE_NAMES = {"NUMBER": "INTEGER", "SENTENCE": "STRING", "LOGIC": "BOOLEAN",
              "NUMBER[]": "INTEGER_ARRAY", "SENTENCE[]": "STRING_ARRAY"}


def ungroup(expr: Expr) -> Expr:
    while expr.kind == "GROUP":
        expr = expr.children[0]
    return expr


def integer_constant(expr: Expr) -> int | None:
    e = ungroup(expr)
    if e.kind == "NUMBER": return int(e.value)
    if e.kind == "UNARY" and e.value == "-":
        value = integer_constant(e.children[0]); return -value if value is not None else None
    if e.kind == "BINARY" and e.value in {"+", "-", "*"}:
        a, b = (integer_constant(c) for c in e.children)
        if a is not None and b is not None:
            return {"+": lambda: a+b, "-": lambda: a-b, "*": lambda: a*b}[e.value]()
    return None


def infer_type(expr: Expr, symbols: Mapping[str, str], imports: frozenset[str] = frozenset()) -> str:
    e = ungroup(expr)
    if e.kind == "NUMBER": return "INTEGER"
    if e.kind == "STRING":
        try: json.loads(e.value)
        except ValueError as exc: raise SchemaError("invalid string token") from exc
        return "STRING"
    if e.kind == "ID":
        if e.value not in symbols: raise SchemaError("unbound identifier")
        return symbols[e.value]
    if e.kind == "ARRAY":
        if len(e.children) != 4 or any(infer_type(c, symbols, imports) != "INTEGER" for c in e.children):
            raise SchemaError("only four-element numeric array construction is supported")
        return "INTEGER_ARRAY"
    if e.kind == "INDEX":
        a, b = (infer_type(c, symbols, imports) for c in e.children)
        if a not in {"INTEGER_ARRAY", "STRING_ARRAY"} or b != "INTEGER": raise SchemaError("index types")
        if a == "STRING_ARRAY" and integer_constant(e.children[1]) not in range(4): raise SchemaError("decoder field index")
        return "INTEGER" if a == "INTEGER_ARRAY" else "STRING"
    if e.kind == "CALL":
        callee = e.children[0]
        if callee.kind != "MEMBER" or callee.children[0].kind != "ID" or callee.children[0].value != "strings" or "strings" not in imports:
            raise SchemaError("UNSUPPORTED_GOCO_FORM call/import")
        types = [infer_type(c, symbols, imports) for c in e.children[1:]]
        if callee.value == "SPLIT" and types == ["STRING", "STRING"] and e.children[2].value == '"|"': return "STRING_ARRAY"
        if callee.value == "TO_NUMBER" and types == ["STRING"] and ungroup(e.children[1]).kind == "INDEX": return "INTEGER"
        raise SchemaError("UNSUPPORTED_GOCO_FORM call signature")
    if e.kind == "UNARY":
        typ = infer_type(e.children[0], symbols, imports)
        if (e.value, typ) == ("-", "INTEGER"): return "INTEGER"
        if (e.value, typ) == ("!", "BOOLEAN"): return "BOOLEAN"
        raise SchemaError("unary types")
    if e.kind == "BINARY":
        a, b = (infer_type(c, symbols, imports) for c in e.children)
        if e.value in {"+", "-", "*", "%"} and a == b == "INTEGER": return "INTEGER"
        if e.value in {"==", "!=", "<", "<=", ">", ">="} and a == b == "INTEGER": return "BOOLEAN"
        if e.value in {"&&", "||"} and a == b == "BOOLEAN": return "BOOLEAN"
        raise SchemaError("UNRESOLVED_REQUIREMENT expression type/operator")
    raise SchemaError("UNSUPPORTED_GOCO_FORM expression")


@dataclass(frozen=True)
class Item:
    occurrence_id: str
    kind: str
    operation: str
    category: str
    datatype: str
    operand_types: tuple[str, ...]
    operand_roles: tuple[str, ...]
    result_role: str
    location: tuple[int, int]
    source: str | None = None
    target: str | None = None
    port: int | None = None
    value: str | None = None
    parent: str | None = None
    essential: bool = True
    proof: str | None = None

    def semantic_identity(self) -> tuple:
        return (self.kind, self.operation, self.category, self.datatype,
                self.operand_types, self.operand_roles, self.result_role)


@dataclass
class Program:
    program_id: str
    source: str
    statements: tuple[Stmt, ...]
    symbols: dict[str, str]
    roles: dict[str, str]
    imports: frozenset[str]
    items: tuple[Item, ...]
    node_ids: dict[int, str]
    edge_ids: dict[tuple[str, int], str]
    domain: str
    output_id: str
    macro_id: str
    normalized_tree: tuple

    def item(self, occurrence_id: str) -> Item:
        for item in self.items:
            if item.occurrence_id == occurrence_id: return item
        raise SchemaError("unknown source occurrence")


def compile_program(program_id: str, source: str) -> Program:
    statements = parse(source); symbols: dict[str, str] = {}; imports: set[str] = set()
    indices: set[str] = set(); assignments: dict[str, list[Stmt]] = {}; declarations: dict[str, Stmt] = {}
    inputs: list[Stmt] = []; displays: list[Stmt] = []
    def validate(rows: tuple[Stmt, ...], in_loop: bool = False) -> None:
        for s in rows:
            if s.kind == "IMPORT":
                if in_loop or s.value in imports: raise SchemaError("duplicate/nested import")
                imports.add(s.value); continue
            if s.kind == "DECLARE":
                typ, name = s.value.split(":")
                if typ not in TYPE_NAMES or name in symbols or name in {"strings", "math", "true", "false"}: raise SchemaError("declaration binding/type")
                if s.expressions and infer_type(s.expressions[0], symbols, frozenset(imports)) != TYPE_NAMES[typ]: raise SchemaError("initializer type")
                symbols[name] = TYPE_NAMES[typ]; declarations[name] = s
            elif s.kind == "INPUT":
                if in_loop or s.expressions[0].kind != "ID" or infer_type(s.expressions[0], symbols, frozenset(imports)) not in {"INTEGER", "STRING"}: raise SchemaError("input binding")
                inputs.append(s)
            elif s.kind == "DISPLAYNL":
                if in_loop or infer_type(s.expressions[0], symbols, frozenset(imports)) != "INTEGER": raise SchemaError("output type/placement")
                displays.append(s)
            elif s.kind == "UPDATE":
                name = s.expressions[0].value
                if name not in symbols or symbols[name] != "INTEGER" or infer_type(s.expressions[1], symbols, frozenset(imports)) != "INTEGER": raise SchemaError("update type/binding")
                assignments.setdefault(name, []).append(s)
                if s.value == "-=" and name not in indices: raise SchemaError("only reverse-index decrement is frozen")
            elif s.kind == "IF":
                if infer_type(s.expressions[0], symbols, frozenset(imports)) != "BOOLEAN": raise SchemaError("condition type")
                validate(s.children, in_loop)
            elif s.kind == "LOOP":
                if in_loop or s.loop_index is None: raise SchemaError("nested/unbound loop")
                index = s.loop_index; indices.add(index)
                if s.value == "FORWARD":
                    if index in symbols: raise SchemaError("loop index shadowing")
                    if infer_type(s.expressions[0], symbols, frozenset(imports)) != "INTEGER": raise SchemaError("loop initial type")
                    symbols[index] = "INTEGER"
                elif index not in symbols: raise SchemaError("reverse index undeclared")
                cond = ungroup(s.expressions[-1])
                if infer_type(cond, symbols, frozenset(imports)) != "BOOLEAN" or cond.kind != "BINARY" or cond.children[0].value != index:
                    raise SchemaError("closed loop condition")
                if s.value == "FORWARD" and not ((integer_constant(s.expressions[0]) == 1 and cond.value == "<=" and cond.children[1].kind == "ID") or
                    (integer_constant(s.expressions[0]) == 0 and cond.value == "<" and integer_constant(cond.children[1]) == 4)):
                    raise SchemaError("closed forward bounds")
                if s.value == "REVERSE" and integer_constant(cond.children[1]) not in {0, 1}: raise SchemaError("closed reverse bounds")
                validate(s.children, True)
            else: raise SchemaError("UNSUPPORTED_GOCO_FORM statement")
    validate(statements)
    if len(inputs) != 1 or len(displays) != 1 or statements[-1] != displays[0]: raise SchemaError("one input and final display required")
    input_name = inputs[0].expressions[0].value
    domain = "numeric_iteration" if symbols[input_name] == "INTEGER" else "array_reduction"
    if (domain == "array_reduction") != ("strings" in imports): raise SchemaError("decoder import/domain mismatch")
    roles = {name: "LOCAL_VALUE" for name in symbols}
    roles[input_name] = "INPUT_LIMIT" if domain == "numeric_iteration" else "RAW_INPUT"
    for name in indices: roles[name] = "DOMAIN_ITEM" if domain == "numeric_iteration" else "ITEM_INDEX"
    for name, typ in symbols.items():
        if typ == "STRING_ARRAY": roles[name] = "SPLIT_FIELDS"
        elif typ == "INTEGER_ARRAY": roles[name] = "DOMAIN_SEQUENCE"
        elif name in assignments and name not in indices:
            roles[name] = "INDICATOR" if all(a.value == "=" and integer_constant(a.expressions[1]) in {0,1} for a in assignments[name]) else "ACCUMULATOR"
        elif name in declarations and declarations[name].expressions and ungroup(declarations[name].expressions[0]).kind == "CALL":
            roles[name] = "DECODED_FIELD"
    for e in _walk_expr(displays[0].expressions[0]):
        if e.kind == "ID": roles[e.value] = "DISPLAYED_ACCUMULATOR"
    nodes: list[Item] = []; edges: list[Item] = []; node_ids: dict[int,str] = {}; edge_ids: dict[tuple[str,int],str] = {}
    writers: dict[str,list[str]] = {}; reads: list[tuple[str,str]] = []
    def add(obj: Expr | Stmt, op: str, category: str, typ: str, operands: tuple[str,...], operand_roles: tuple[str,...], role: str, parent: str | None = None) -> str:
        oid = rid("OCC", [program_id, "NODE", str(obj.start), str(len(nodes))]); node_ids[id(obj)] = oid
        nodes.append(Item(oid,"NODE",op,category,typ,operands,operand_roles,role,(obj.start,obj.end),value=obj.value,parent=parent)); return oid
    def edge(src: str, dst: str, kind: str, port: int, typ: str, sr: str, dr: str) -> str:
        if kind not in EDGES: raise SchemaError("unknown graph edge")
        oid = rid("OCC", [program_id,"EDGE",str(len(edges))]); location = next(n.location for n in nodes if n.occurrence_id == dst)
        edges.append(Item(oid,"EDGE",kind,"ATOMIC_CONTROL_DATAFLOW",typ,(typ,),(sr,),dr,location,src,dst,port)); edge_ids[(dst,port)] = oid; return oid
    def expression(e: Expr, parent: str, role: str) -> str:
        if e.kind == "GROUP":
            oid = expression(e.children[0], parent, role); node_ids[id(e)] = oid; return oid
        typ = infer_type(e,symbols,frozenset(imports))
        args = e.children[1:] if e.kind == "CALL" else e.children
        if e.kind == "CALL": op, category = "strings."+e.children[0].value,"API_DECODER"
        elif e.kind == "BINARY": op, category = OPERATORS[e.value],"ATOMIC_OPERATOR"
        elif e.kind == "UNARY": op, category = ("NEG" if e.value == "-" else "NOT"),"ATOMIC_OPERATOR"
        elif e.kind in {"NUMBER","STRING"}: op, category = "CONSTANT","VALUE_OR_LITERAL"
        elif e.kind == "INDEX": op, category = "ARRAY_INDEX","API_DECODER"
        elif e.kind == "ARRAY": op, category = "FOUR_DOMAIN_VALUES","API_DECODER"
        elif e.kind == "ID": op, category, role = "READ","GENERIC_CONSTRUCT",roles[e.value]
        else: raise SchemaError("unknown typed node")
        ts = tuple(infer_type(c,symbols,frozenset(imports)) for c in args)
        rs = tuple(roles.get(c.value, f"{op}_OPERAND_{i}") if c.kind == "ID" else f"{op}_OPERAND_{i}" for i,c in enumerate(args))
        oid = add(e,op,category,typ,ts,rs,role,parent)
        if e.kind == "ID": reads.append((e.value,oid))
        for i,c in enumerate(args):
            cid = expression(c,oid,rs[i]); kind = "INPUT_TO_DECODER" if op.startswith("strings.") or op in {"ARRAY_INDEX","FOUR_DOMAIN_VALUES"} else "VALUE_TO_OPERATOR"
            edge(cid,oid,kind,i,ts[i],rs[i],role)
        return oid
    def statements_graph(rows: tuple[Stmt,...], controls: tuple[str,...] = (), loop_id: str | None = None) -> None:
        for s in rows:
            if s.kind == "IMPORT": continue
            if s.kind == "DECLARE":
                typ,name = s.value.split(":"); oid = add(s,"INITIALIZE","GENERIC_CONSTRUCT",symbols[name],(),(),roles[name]); writers.setdefault(name,[]).append(oid)
                if s.expressions:
                    cid=expression(s.expressions[0],oid,"INITIAL_"+roles[name]);edge(cid,oid,"VALUE_TO_OPERATOR",0,symbols[name],"INITIAL_"+roles[name],roles[name])
            elif s.kind == "INPUT":
                oid=add(s,"INPUT","API_DECODER",symbols[input_name],(),(),roles[input_name]); node_ids[id(s.expressions[0])]=oid;writers.setdefault(input_name,[]).append(oid)
            elif s.kind == "DISPLAYNL":
                oid=add(s,"FINAL_DISPLAY","GENERIC_CONSTRUCT","INTEGER",("INTEGER",),("DISPLAYED_ACCUMULATOR",),"OUTPUT")
                cid=expression(s.expressions[0],oid,"DISPLAYED_ACCUMULATOR");edge(cid,oid,"ACCUMULATOR_TO_OUTPUT",0,"INTEGER","DISPLAYED_ACCUMULATOR","OUTPUT")
            elif s.kind == "UPDATE":
                name=s.expressions[0].value;role=roles[name];oid=add(s,"ASSIGN" if s.value=="=" else "ACCUMULATE" if s.value=="+=" else "INDEX_STEP","GENERIC_CONSTRUCT","INTEGER",("INTEGER",),("CONTRIBUTION",),role)
                node_ids[id(s.expressions[0])]=oid;writers.setdefault(name,[]).append(oid)
                cid=expression(s.expressions[1],oid,"CONTRIBUTION");edge(cid,oid,"OPERATOR_TO_ACCUMULATOR",0,"INTEGER","CONTRIBUTION",role)
                for i,control in enumerate(controls):edge(control,oid,"CONTROL_TO_UPDATE",100+i,"BOOLEAN","CONTROL",role)
                if loop_id:edge(oid,oid,"LOOP_CARRY",200,"INTEGER",role,role)
            elif s.kind == "IF":
                oid=add(s,"IF","GENERIC_CONSTRUCT","BOOLEAN",("BOOLEAN",),("PREDICATE_BOOLEAN",),"CONTROL")
                cid=expression(s.expressions[0],oid,"PREDICATE_BOOLEAN");edge(cid,oid,"PREDICATE_TO_CONTROL",0,"BOOLEAN","PREDICATE_BOOLEAN","CONTROL")
                statements_graph(s.children,controls+(oid,),loop_id)
            elif s.kind == "LOOP":
                oid=add(s,"BOUNDED_LOOP","GENERIC_CONSTRUCT","BOOLEAN",("BOOLEAN",),("LOOP_BOUND",),"CONTROL")
                for i,e in enumerate(s.expressions):
                    cid=expression(e,oid,"LOOP_INITIAL" if i==0 and s.value=="FORWARD" else "LOOP_BOUND")
                    edge(cid,oid,"VALUE_TO_PREDICATE",i,infer_type(e,symbols,frozenset(imports)),"DOMAIN_VALUE","CONTROL")
                statements_graph(s.children,controls+(oid,),oid)
    statements_graph(statements)
    for name,read in reads:
        for writer in writers.get(name,[]):edge(writer,read,"PRIOR_STATE_TO_UPDATE",300+len(edges),symbols[name],roles[name],roles[name])
    input_id=node_ids[id(inputs[0])]; output_id=node_ids[id(displays[0])]
    macro_id=rid("OCC",[program_id,"DOMAIN_DECODER"])
    nodes.append(Item(macro_id,"NODE","INPUT_DOMAIN:"+("NONNEGATIVE_INTEGER" if domain=="numeric_iteration" else "FOUR_SIGNED_INTEGER_FIELDS"),"API_DECODER",symbols[input_name],(),(),"DOMAIN_DECODER",(inputs[0].start,inputs[0].end),target=input_id))
    edge(macro_id,input_id,"INPUT_TO_DECODER",400,symbols[input_name],"DOMAIN_DECODER",roles[input_name])
    # Backwards data/control reachability is a conservative mechanical proof of
    # non-observability. No case result selects essentiality or creates a key.
    reachable={output_id}; changed=True
    while changed:
        changed=False
        for e in edges:
            if e.target in reachable and e.source not in reachable:reachable.add(e.source);changed=True
    items=[]
    for item in (*nodes,*edges):
        essential=(item.occurrence_id in reachable) if item.kind=="NODE" else item.target in reachable and item.source in reachable
        proof=None if essential else "PURE_UNUSED_NO_TYPED_PATH_TO_OUTPUT"
        items.append(Item(**{**item.__dict__,"essential":essential,"proof":proof}))
    # Stable complete syntax/binding tree: graph mapping must also retain full
    # multiplicity, sequential state and traversal (not just reusable key sets).
    names={name:f"binding{index}" for index,name in enumerate(symbols)}
    def ex(e: Expr) -> tuple:
        e=ungroup(e)
        if e.kind=="ID":return ("ID",names.get(e.value,e.value),symbols.get(e.value))
        return (e.kind,e.value,*(ex(c) for c in e.children))
    def st(s: Stmt) -> tuple:
        value=s.value
        if s.kind=="DECLARE":typ,name=value.split(":");value=(typ,names[name])
        return (s.kind,value,names.get(s.loop_index) if s.loop_index else None,tuple(ex(e) for e in s.expressions),tuple(st(c) for c in s.children))
    return Program(program_id,source,statements,symbols,roles,frozenset(imports),tuple(items),node_ids,edge_ids,domain,output_id,macro_id,tuple(st(s) for s in statements))


@dataclass(frozen=True)
class Value:
    value: Any
    dependencies: frozenset[str] = frozenset()


@dataclass
class Execution:
    output: str
    output_dependencies: frozenset[str]
    evaluated: set[str]
    values: dict[str,list[Any]]
    events: list[dict[str,Any]]
    initialization: dict[str,Value]
    intervention_occurrences: tuple[str,...]


def execute(program: Program, raw_input: str, *, occurrences: tuple[str,...] = (), replacement: Any = None,
            max_steps: int = 100000) -> Execution:
    """Bounded typed-IR interpreter; destinations are altered jointly, never text."""
    if len(occurrences)!=len(set(occurrences)) or any(x not in {i.occurrence_id for i in program.items} for x in occurrences):raise SchemaError("intervention occurrence set")
    if type(max_steps) is not int or max_steps<1:raise SchemaError("step budget")
    selected=set(occurrences);env:dict[str,Value]={};evaluated:set[str]=set();values:dict[str,list[Any]]={};events=[];initialization={};output=None;steps=0
    last_writer: dict[str, str] = {}
    def tick() -> None:
        nonlocal steps
        steps+=1
        if steps>max_steps:raise SchemaError("IR_EXECUTION_BUDGET_EXCEEDED")
    def observe(oid:str,value:Any,deps:frozenset[str], *, replace: bool = True) -> Value:
        tick();evaluated.add(oid);values.setdefault(oid,[]).append(value)
        if replace and oid in selected:value=replacement
        return Value(value,deps|{oid})
    def operand(dst:str,port:int,value:Value) -> Value:
        oid=program.edge_ids.get((dst,port))
        return observe(oid,value.value,value.dependencies) if oid else value
    def expr(e:Expr) -> Value:
        e=ungroup(e);oid=program.node_ids[id(e)]
        if e.kind=="ID":
            v=env[e.value]
            writer=last_writer.get(e.value)
            matches=[item for item in program.items if item.kind=="EDGE" and item.operation=="PRIOR_STATE_TO_UPDATE" and item.source==writer and item.target==oid]
            if len(matches)>1:raise SchemaError("ambiguous runtime state edge")
            if matches:v=observe(matches[0].occurrence_id,v.value,v.dependencies)
            return observe(oid,v.value,v.dependencies)
        if e.kind=="NUMBER":return observe(oid,int(e.value),frozenset())
        if e.kind=="STRING":return observe(oid,json.loads(e.value),frozenset())
        args=e.children[1:] if e.kind=="CALL" else e.children
        vs=[operand(oid,i,expr(c)) for i,c in enumerate(args)];ds=frozenset().union(*(v.dependencies for v in vs));xs=[v.value for v in vs]
        if e.kind=="ARRAY":value=xs
        elif e.kind=="INDEX":
            if type(xs[1]) is not int or xs[1]<0 or xs[1]>=len(xs[0]):raise SchemaError("index out of bounds")
            value=xs[0][xs[1]]
        elif e.kind=="CALL":
            if e.children[0].value=="SPLIT":
                value=xs[0].split(xs[1])
                if len(value)!=4:raise SchemaError("invalid four-field decoder")
            else:
                if not isinstance(xs[0],str) or not xs[0].isascii() or not xs[0].lstrip("-").isdigit():raise SchemaError("invalid decoded integer")
                value=int(xs[0])
        elif e.kind=="UNARY":value=-xs[0] if e.value=="-" else not xs[0]
        elif e.kind=="BINARY":
            a,b=xs
            if e.value=="%":
                if b==0:raise SchemaError("remainder by zero")
                # Java/GOCO remainder truncates toward zero, not Python's floor.
                q=abs(a)//abs(b)*(1 if (a>=0)==(b>=0) else -1);value=a-q*b
            else:value={"+":lambda:a+b,"-":lambda:a-b,"*":lambda:a*b,"==":lambda:a==b,"!=":lambda:a!=b,
                "<":lambda:a<b,"<=":lambda:a<=b,">":lambda:a>b,">=":lambda:a>=b,"&&":lambda:bool(a and b),"||":lambda:bool(a or b)}[e.value]()
        else:raise SchemaError("unknown execution node")
        return observe(oid,value,ds)
    def rows(statements:tuple[Stmt,...], controls:frozenset[str]=frozenset()) -> None:
        nonlocal output
        for s in statements:
            tick()
            if s.kind=="IMPORT":continue
            oid=program.node_ids[id(s)]
            if s.kind=="DECLARE":
                typ,name=s.value.split(":");v=operand(oid,0,expr(s.expressions[0])) if s.expressions else Value(0 if typ=="NUMBER" else "")
                v=observe(oid,v.value,v.dependencies|controls);env[name]=v;initialization[oid]=v;last_writer[name]=oid
            elif s.kind=="INPUT":
                raw=replacement if program.macro_id in selected or oid in selected else raw_input
                if program.domain=="numeric_iteration":
                    if not isinstance(raw,str) or not raw.isascii() or not raw.isdigit():raise SchemaError("nonnegative integer input required")
                    value=int(raw)
                else:
                    if not isinstance(raw,str) or len(raw.split("|"))!=4 or any(not f or not f.isascii() or not f.lstrip("-").isdigit() for f in raw.split("|")):raise SchemaError("four signed integers required")
                    value=raw
                evaluated.update((program.macro_id,oid));values.setdefault(program.macro_id,[]).append(value);values.setdefault(oid,[]).append(value)
                decoded=Value(value,frozenset({program.macro_id,oid}))
                macro_edge=program.edge_ids[(oid,400)]
                decoded=observe(macro_edge,decoded.value,decoded.dependencies)
                env[s.expressions[0].value]=decoded;last_writer[s.expressions[0].value]=oid
            elif s.kind=="UPDATE":
                name=s.expressions[0].value;rhs=operand(oid,0,expr(s.expressions[1]));old=env[name];delta=rhs.value if s.value=="+=" else -rhs.value if s.value=="-=" else rhs.value-old.value
                carry=program.edge_ids.get((oid,200))
                active_controls=True;local_controls=controls
                for item in program.items:
                    if item.kind=="EDGE" and item.target==oid and item.operation=="CONTROL_TO_UPDATE":
                        control=observe(item.occurrence_id,True,local_controls|{item.source})
                        active_controls=active_controls and bool(control.value)
                        local_controls=local_controls|control.dependencies
                if not active_controls:continue
                if carry:
                    evaluated.add(carry);values.setdefault(carry,[]).append(old.value)
                if (oid in selected or carry in selected) and s.value=="+=":delta=0
                deps=rhs.dependencies|local_controls|(old.dependencies if s.value!="=" else frozenset())|(frozenset({carry}) if carry else frozenset())
                # An accumulator intervention suppresses its contribution; it
                # must never overwrite the previously accumulated state.
                v=observe(oid,old.value+delta,deps,replace=s.value!="+=");env[name]=v;last_writer[name]=oid
                events.append({"occurrence_id":oid,"delta":delta,"dependencies":v.dependencies,"register":name})
            elif s.kind=="IF":
                cond=operand(oid,0,expr(s.expressions[0]));cond=observe(oid,bool(cond.value),cond.dependencies|controls)
                if cond.value:rows(s.children,controls|cond.dependencies)
            elif s.kind=="LOOP":
                index=s.loop_index
                if s.value=="FORWARD":env[index]=operand(oid,0,expr(s.expressions[0]))
                while True:
                    cond=operand(oid,len(s.expressions)-1,expr(s.expressions[-1]));cond=observe(oid,bool(cond.value),cond.dependencies|controls)
                    if not cond.value:break
                    rows(s.children,controls|cond.dependencies)
                    if s.value=="FORWARD":env[index]=Value(env[index].value+1,env[index].dependencies)
            elif s.kind=="DISPLAYNL":
                v=operand(oid,0,expr(s.expressions[0]));output=observe(oid,v.value,v.dependencies|controls)
    try:rows(program.statements)
    except (TypeError,ValueError,KeyError,IndexError,ZeroDivisionError) as exc:raise SchemaError("IR_EXECUTION_UNRESOLVED") from exc
    if output is None or type(output.value) is not int:raise SchemaError("integer final output required")
    return Execution(str(output.value),output.dependencies,evaluated,values,events,initialization,occurrences)
