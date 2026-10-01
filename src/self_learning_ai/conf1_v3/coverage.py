"""Mechanically derived core findings; no caller-supplied scientific flags.

Producer provenance, delegated reports and final authorization are deliberately
outside this module. Unsupported core forms remain fail closed.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence
import hashlib

from .interfaces import ArtifactResolver, ClosureError, SchemaError, _keys, _schema, rid, validate_record_reference, canonical_json_bytes
from .core_ir import Program, Execution, compile_program, execute
from .contracts import CoverageContractV3, ContractKey, input_domain_classes
from .goco import Expr, expressions_equivalent, alpha_bijection


@dataclass(frozen=True)
class MappingProof:
    contract:CoverageContractV3
    program:Program
    correspondence:tuple[tuple[str,str],...]
    key_occurrences:Mapping[str,tuple[str,...]]
    source_sha256:str
    equivalence_proofs:tuple[Mapping[str,Any],...]=()
    semantic_transport:Mapping[str,Any]|None=None
    raw_key_resolution:tuple[Mapping[str,Any],...]=()

    def to_record(self) -> dict[str,Any]:
        """Expose direct/region satisfaction without hiding unresolved raw keys."""
        from .interfaces import canonical_json_bytes
        regional=self.semantic_transport is not None
        return {"contract_id":self.contract.contract_id,"program_id":self.program.program_id,
            "source_sha256":self.source_sha256,"ordinary_correspondence":self.correspondence,
            "key_occurrences":dict(self.key_occurrences),"equivalence_proofs":self.equivalence_proofs,
            "semantic_transport_sha256":hashlib.sha256(canonical_json_bytes(self.semantic_transport)).hexdigest() if regional else None,
            "obligation_satisfaction":{"direct":self.semantic_transport["ordinary_obligations"],"regional":self.semantic_transport["transports"]} if regional else {"direct":self.correspondence,"regional":[]},
            "raw_key_resolution":self.raw_key_resolution,
            "mapping_status":"TOTAL_CORRESPONDENCE_WITH_VERIFIED_SEMANTIC_TRANSPORT" if regional else "STRICT_TYPED_MAPPING",
            "all_raw_atomic_keys_satisfied":all(r["method"]!="UNRESOLVED_DISTINCT_RAW_REQUIREMENT" for r in self.raw_key_resolution),
            "raw_graph_equality_claim":False if regional else None}

    def validate(self) -> None:
        from .contract_ir import graph_record
        rebuilt=reconcile_complete_mapping(self.contract,self.program.source,
            transport_evidence=self.semantic_transport)
        if canonical_json_bytes(rebuilt.to_record())!=canonical_json_bytes(self.to_record()):
            raise ClosureError("MAPPING_PROOF_RECONSTRUCTION_MISMATCH")
        if graph_record(rebuilt.program)!=graph_record(self.program):raise ClosureError("bound typed IR changed")


def reconcile_complete_mapping(contract:CoverageContractV3,source:str,*,region_evidence:Mapping[str,Any]|None=None,
                               transport_evidence:Mapping[str,Any]|None=None) -> MappingProof:
    """No ID-set substitute: exact complete typed/binding/tree correspondence."""
    contract.validate();program=compile_program(contract.program_id,source);expected=contract.ir
    if contract.core_gaps:raise ClosureError("UNRESOLVED_REQUIREMENT: incomplete prospective contract")
    if region_evidence is not None or transport_evidence is not None:
        from .canonical_transport import build_canonical_transport,digest
        from .transport_verifier import verify_canonical_transport
        if region_evidence is None:
            region_evidence=transport_evidence.get("total_mapping_certificate")
        if region_evidence is None:raise ClosureError("MISSING_REGION_CERTIFICATE")
        bundle=transport_evidence if transport_evidence is not None else build_canonical_transport(contract,source,region_evidence)
        verify_canonical_transport(bundle)
        if digest(bundle["contract"])!=digest(contract.to_dict()):raise ClosureError("TRANSPORT_WRONG_BOUND_CONTRACT")
        if digest(region_evidence)!=digest(bundle["total_mapping_certificate"]):raise ClosureError("TRANSPORT_CERTIFICATE_HASH_MISMATCH")
        if bundle["source_sha256"]!=hashlib.sha256(source.encode()).hexdigest():raise ClosureError("TRANSPORT_WRONG_BOUND_SOURCE")
        table={r["contract"]:r["source"] for r in region_evidence["ordinary_correspondence"]}
        occurrences={};resolution=[]
        region_by_root={r["contract"]["expression_node"]:r for r in region_evidence["regions"]}
        transport_by_region={t["region_id"]:t for t in bundle["transports"]}
        for key in contract.canonical_keys:
            required=contract.key_occurrences[key.key_id]
            refs=[]
            if all(o in table for o in required):
                method="DIRECT_TYPED_CORRESPONDENCE";actual=tuple(table[o] for o in required)
            elif key.evidence_kind=="BEHAVIORAL" and key.operation=="OR" and all(o in region_by_root and region_by_root[o]["scope"]=="BOOLEAN_OR" for o in required):
                # V3.3 explicitly authorizes typed Boolean OR truth transport.
                # No analogous atomic AND->MUL authorization exists.
                method="VERIFIED_REGIONAL_SEMANTIC_TRANSPORT"
                actual=tuple(region_by_root[o]["source"]["expression_node"] for o in required)
                refs=[transport_by_region[region_by_root[o]["region_id"]]["transport_id"] for o in required]
                if any(program.item(o).datatype!="BOOLEAN" for o in actual):raise ClosureError("TRANSPORT_BOUNDARY_TYPE_MISMATCH")
            else:
                method="UNRESOLVED_DISTINCT_RAW_REQUIREMENT";actual=()
            if actual:occurrences[key.key_id]=actual
            resolution.append({"key_id":key.key_id,"operation":key.operation,"method":method,
                "contract_occurrences":required,"source_occurrences":actual,"transport_references":refs})
        return MappingProof(contract,program,tuple(table.items()),occurrences,hashlib.sha256(source.encode()).hexdigest(),
            tuple(bundle["transports"]),bundle,tuple(resolution))
    from .semantic_ir import computed_mapping_view
    expected_tree,expected_items,expected_hidden=computed_mapping_view(expected)
    source_tree,source_items,source_hidden=computed_mapping_view(program)
    if program.domain!=contract.domain or source_tree!=expected_tree:
        raise ClosureError("INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE")
    names=dict(zip(expected.symbols,program.symbols))
    alpha_bijection(expected.symbols,program.symbols,names)
    if len(source_items)!=len(expected_items):raise ClosureError("INCOMPLETE_SOURCE_MAPPING")
    pairs=[]
    def identity(item,p):
        spec=p.attribute_specs.get(item.occurrence_id)
        if spec and spec["parent_ontology_supported"] and item.essential:
            return ("COMPUTED_VALUE",spec["computed_integer"],spec["semantic_role"],spec["attribute_parent_kind"],item.datatype)
        return item.semantic_identity()
    equivalences=[]
    for a,b in zip(expected_items,source_items):
        if identity(a,expected)!=identity(b,program) or a.essential!=b.essential or a.proof!=b.proof:
            raise ClosureError("INCOMPATIBLE_TYPED_NODE_OR_EDGE")
        pairs.append((a.occurrence_id,b.occurrence_id))
        if a.occurrence_id in expected_hidden or b.occurrence_id in source_hidden:
            equivalences.append({"frozen_rule_id":"V3.3","catalog_rule":"WHOLLY_INTEGER_CONSTANT_NEG_ADD_SUB_MUL_COMPUTED_KEY_ONLY",
                "source_locations":[a.location,b.location],"result_type":"INTEGER",
                "computed_integer":expected.attribute_specs[a.occurrence_id]["computed_integer"],
                "semantic_role":expected.attribute_specs[a.occurrence_id]["semantic_role"],
                "contract_accounted_occurrences":expected_hidden.get(a.occurrence_id,()),
                "source_accounted_occurrences":source_hidden.get(b.occurrence_id,()),
                "affected_occurrence_mapping":[a.occurrence_id,b.occurrence_id],
                "preconditions":"maximal source-mapped pure integer constant tree; neg/add/sub/mul only; same exact value and role; no literal-token obligation"})
    table=dict(pairs)
    for a,b in zip(expected_items,source_items):
        if a.kind=="EDGE" and (table[a.source]!=b.source or table[a.target]!=b.target or a.port!=b.port):
            raise ClosureError("INCOMPATIBLE_DIRECTED_BINDING")
        if not a.essential and a.proof!="PURE_UNUSED_NO_TYPED_PATH_TO_OUTPUT":raise ClosureError("UNPROVED_REFERENCE_ONLY")
    return MappingProof(contract,program,tuple(pairs),{k:tuple(table[x] for x in ids) for k,ids in contract.key_occurrences.items()},hashlib.sha256(source.encode("utf-8")).hexdigest(),tuple(equivalences))


def closed_equivalence(left:Expr,right:Expr,alpha_map:Mapping[str,str]|None=None,**typed_context:Any) -> dict[str,Any]:
    try:
        equal=expressions_equivalent(left,right,alpha_map,**typed_context)
    except SchemaError:
        return {"finding":"UNRESOLVED","source_locations":[(left.start,left.end),(right.start,right.end)],"rule_ids":[],"precondition_proof":None}
    if not equal:return {"finding":"UNRESOLVED","source_locations":[(left.start,left.end),(right.start,right.end)],"rule_ids":[],"precondition_proof":None}
    from .goco import _walk_expr, COMMUTATIVE
    from .core_ir import infer_type,integer_constant
    rules=["V3.3.CONSISTENT_ALPHA_RENAMING"]
    operands=[]
    for side,root,symbols in (("left",left,typed_context["left_symbols"]),("right",right,typed_context["right_symbols"])):
        for node in _walk_expr(root):
            if node.kind=="GROUP":continue
            operands.append({"side":side,"source_location":(node.start,node.end),"operand_types":[infer_type(c,symbols) for c in node.children],"result_type":infer_type(node,symbols)})
            if node.kind=="BINARY" and node.value in {">",">="}:rules.append("V3.3.COMPARISON_DIRECTION")
            if node.kind=="BINARY" and node.value in COMMUTATIVE:rules.append("V3.3.SYMMETRIC_EQUALITY" if node.value=="==" else "V3.3.PURE_COMMUTATIVE_CHILD_SORT")
        if typed_context.get("context")=="COMPUTED_VALUE" and integer_constant(root) is not None:rules.append("V3.3.COMPUTED_INTEGER_NEG_ADD_SUB_MUL")
    return {"finding":"EQUIVALENT","source_locations":[(left.start,left.end),(right.start,right.end)],
        "rule_ids":list(dict.fromkeys(rules)),"typed_occurrences":operands,"precondition_proof":{"left_types":dict(typed_context["left_symbols"]),
        "right_types":dict(typed_context["right_symbols"]),"context":typed_context.get("context","ATOMIC"),"alpha_bijection":dict(alpha_map or {k:k for k in typed_context["left_symbols"]}),
        "purity_and_totality":"closed scalar tree; no calls/indexing; remainder divisor proved constant nonzero wherever sorted","duplicates_retained":True}}


def _integer_output(raw:str) -> str:
    try:value=Decimal(raw.strip())
    except InvalidOperation as exc:raise SchemaError("non-integer reference output") from exc
    if not value.is_finite() or value!=value.to_integral_value():raise SchemaError("non-integer reference output")
    return str(int(value))


class PinnedCompilerOracle:
    """Use the existing non-model compiler adapter for normal-run agreement.

    This is not an E1 report producer or a substitute for execution provenance.
    It checks the pinned compiler binary before every actual normal invocation.
    """
    def __init__(self,java:Path,jar:Path):self.java,self.jar=java,jar
    def run(self,source:str,raw_input:str) -> str:
        from self_learning_ai.compiler import GocoCompiler,normalized_program_output
        if hashlib.sha256(self.jar.read_bytes()).hexdigest()!="42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb":raise ClosureError("COMPILER_IDENTITY_MISMATCH")
        result=GocoCompiler(self.java,self.jar).run(source,raw_input+"\n")
        if result.phase!="success":raise ClosureError("NORMAL_COMPILER_EXECUTION_FAILED")
        return _integer_output(normalized_program_output(result.stdout))


@dataclass(frozen=True)
class FrozenCase:
    case_id:str
    raw_input:str
    expected_output:str
    expected_output_reference:Mapping[str,Any]


def resolve_cases(resolver:ArtifactResolver,artifact_id:str,program_id:str) -> tuple[FrozenCase,...]:
    artifact=resolver.json(artifact_id,role="CASE_SET")
    _keys(artifact,{"schema_version","program_id","cases"});_schema(artifact)
    if artifact["program_id"]!=program_id or not isinstance(artifact["cases"],list) or len(artifact["cases"])!=5:raise ClosureError("five bound program cases required")
    cases=[];ids=set()
    for row in artifact["cases"]:
        _keys(row,{"case_id","input","expected_output"})
        if not isinstance(row["case_id"],str) or not row["case_id"] or row["case_id"] in ids:raise SchemaError("case ID missing/duplicate")
        if not isinstance(row["input"],str) or not isinstance(row["expected_output"],str):raise SchemaError("case string required")
        ids.add(row["case_id"]);content=row["expected_output"].encode("utf-8")
        reference={"artifact_id":artifact_id,"record_id":row["case_id"],"record_role":"EXPECTED_OUTPUT","content_sha256_utf8":hashlib.sha256(content).hexdigest(),"content_size_bytes_utf8":len(content)}
        cases.append(FrozenCase(row["case_id"],row["input"],row["expected_output"],reference))
    return tuple(cases)


class CoverageEngine:
    def __init__(self,mapping:MappingProof,*,resolver:ArtifactResolver,source_artifact_id:str,case_artifact_id:str,oracle:PinnedCompilerOracle):
        if type(oracle) is not PinnedCompilerOracle:raise SchemaError("actual pinned compiler oracle required")
        mapping.validate()
        raw=resolver.read(source_artifact_id,role="SOURCE_REFERENCE")
        if raw!=mapping.program.source.encode("utf-8"):raise ClosureError("source artifact identity mismatch")
        self.mapping,self.resolver,self.oracle=mapping,resolver,oracle
        self.case_artifact_id=case_artifact_id;self.source_artifact_id=source_artifact_id
        self.cases=resolve_cases(resolver,case_artifact_id,mapping.program.program_id)
        self.normals={};self.findings={};self.compiler_outputs={}
        for case in self.cases:
            input_domain_classes(mapping.program.domain,case.raw_input)
            normal=execute(mapping.program,case.raw_input)
            expected=_integer_output(case.expected_output)
            compiler_output=oracle.run(mapping.program.source,case.raw_input)
            if normal.output!=expected or compiler_output!=expected:raise ClosureError("NORMAL_REFERENCE_IR_COMPILER_DISAGREEMENT")
            self.compiler_outputs[case.case_id]=compiler_output
            self.normals[case.case_id]=normal

    def _check_bound_inputs(self) -> None:
        from .contract_ir import graph_record
        source=self.resolver.read(self.source_artifact_id,role="SOURCE_REFERENCE").decode("utf-8")
        current_mapping=reconcile_complete_mapping(self.mapping.contract,source,transport_evidence=self.mapping.semantic_transport)
        if canonical_json_bytes(current_mapping.to_record())!=canonical_json_bytes(self.mapping.to_record()):
            raise ClosureError("bound source/mapping changed")
        if graph_record(current_mapping.program)!=graph_record(self.mapping.program):
            raise ClosureError("bound typed IR changed")
        current=resolve_cases(self.resolver,self.case_artifact_id,self.mapping.program.program_id)
        if current!=self.cases:raise ClosureError("bound case set changed")
        if any(execute(current_mapping.program,case.raw_input)!=self.normals.get(case.case_id) for case in current):
            raise ClosureError("normal execution cache changed")
        if any(self.compiler_outputs.get(case.case_id)!=self.normals[case.case_id].output for case in current):
            raise ClosureError("normal compiler observation cache changed")

    def _key(self,key_id:str) -> ContractKey:
        for key in self.mapping.contract.canonical_keys:
            if key.key_id==key_id:
                if key_id not in self.mapping.key_occurrences:raise ClosureError("UNSATISFIED_DISTINCT_RAW_KEY: "+key.operation)
                return key
        raise ClosureError("undeclared canonical key")

    def behavioral(self,key_id:str) -> dict[str,Any]:
        self._check_bound_inputs();key=self._key(key_id)
        if key.evidence_kind!="BEHAVIORAL":raise SchemaError("behavioral key required")
        resolution=next((r for r in self.mapping.raw_key_resolution if r["key_id"]==key_id),None)
        if resolution and resolution["method"]=="VERIFIED_REGIONAL_SEMANTIC_TRANSPORT":
            from .canonical_activity import activity_for_raw_or_key
            return activity_for_raw_or_key(self,key_id,resolution)
        occurrences=self.mapping.key_occurrences[key_id];program=self.mapping.program
        items=[program.item(x) for x in occurrences]
        if any(item.operation=="BOUNDED_LOOP" for item in items):
            return {"key_id":key_id,"finding":"UNRESOLVED","status":"UNRESOLVED","occurrences":occurrences,"attempts":[],"witness":None,
                    "reason":"force-true removes the sole exit from the parsed bounded loop; this closed subset has no break/return; no terminating counterfactual output exists"}
        if key.operation=="INPUT" or key.operation.startswith("INPUT_DOMAIN:"):
            values=("0","1") if program.domain=="numeric_iteration" else ("0|0|0|0","1|1|1|1")
        elif key.operation=="strings.SPLIT":values=(["0"]*4,["1"]*4)
        elif key.operation=="ACCUMULATE" or key.operation in {"OPERATOR_TO_ACCUMULATOR","LOOP_CARRY"} and key.result_role in {"ACCUMULATOR","DISPLAYED_ACCUMULATOR"}:values=(0,)
        elif key.result_type=="BOOLEAN":values=(False,True)
        elif key.result_type=="INTEGER":values=(0,1)
        else:return {"row_id":rid("V3.5",[program.program_id,key_id]),"key_id":key_id,"finding":"UNRESOLVED","status":"UNRESOLVED","occurrences":occurrences,"attempts":[],"witness":None}
        attempts=[];events=[];witness=None
        for case in sorted(self.cases,key=lambda c:c.case_id.encode("utf-8")):
            normal=self.normals[case.case_id]
            eligible=[event for event in normal.events if event["delta"]!=0 and set(occurrences)&event["dependencies"] and event["occurrence_id"] in normal.output_dependencies]
            if program.domain=="numeric_iteration" and int(case.raw_input)==0 and key.category=="API_DECODER":eligible=[]
            if not eligible:continue
            events.append({"case_id":case.case_id,"events":eligible,"normal_output":normal.output})
            for order,value in enumerate(values):
                try:counterfactual=execute(program,case.raw_input,occurrences=occurrences,replacement=value)
                except SchemaError:
                    result={"finding":"UNRESOLVED","status":"UNRESOLVED","occurrences":occurrences,"attempts":attempts,"witness":None};self.findings[key_id]=result;return result
                attempt={"case_id":case.case_id,"intervention_order":order,"replacement":value,"occurrence_ids":occurrences,"normal_output":normal.output,"counterfactual_output":counterfactual.output,"changed":normal.output!=counterfactual.output}
                attempts.append(attempt)
                if witness is None and attempt["changed"]:witness=attempt
        result={"row_id":rid("V3.5",[program.program_id,key_id]),"key_id":key_id,"finding":"ACTIVE" if witness else "INACTIVE","status":"PASS","occurrences":occurrences,"normal_events":events,"attempts":attempts,"witness":witness}
        self.findings[key_id]=result;return result

    def semantic_activity(self) -> dict[str,Any]:
        """No caller-selected canonical key; derive all identities from proof."""
        self._check_bound_inputs()
        from .canonical_activity import semantic_activity
        return semantic_activity(self)

    def attribute(self,key_id:str) -> dict[str,Any]:
        self._check_bound_inputs();key=self._key(key_id)
        if key.evidence_kind!="VALUE_OR_LITERAL_ATTRIBUTE":raise SchemaError("value/literal key required")
        parent=self.behavioral(key.parent_key_id) if key.attribute_parent_kind=="ACTIVE_BEHAVIORAL_PARENT" else None
        if parent is not None and parent["finding"]!="ACTIVE":return {"key_id":key_id,"finding":"UNRESOLVED" if parent["finding"]=="UNRESOLVED" else "NOT_COVERED","status":"UNRESOLVED" if parent["finding"]=="UNRESOLVED" else "PASS","witness":None}
        for case in sorted(self.cases,key=lambda c:c.case_id.encode("utf-8")):
            normal=self.normals[case.case_id]
            if parent is not None and case.case_id!=parent["witness"]["case_id"]:continue
            for oid in self.mapping.key_occurrences[key_id]:
                item=self.mapping.program.item(oid)
                if oid not in normal.evaluated:continue
                if key.attribute_parent_kind=="INITIAL_ACCUMULATOR":
                    initialization=normal.initialization.get(item.parent)
                    if initialization is None or item.parent not in normal.output_dependencies:continue
                elif item.parent not in self.mapping.key_occurrences[key.parent_key_id] or item.parent not in normal.output_dependencies:continue
                role_matches=(item.result_role in {"INITIAL_ACCUMULATOR","INITIAL_DISPLAYED_ACCUMULATOR"}) if key.attribute_parent_kind=="INITIAL_ACCUMULATOR" else item.result_role==key.semantic_role
                exact=(item.value==key.exact_required_lexeme) if key.exact_required_lexeme is not None else key.computed_integer in normal.values.get(oid,[]) and role_matches
                if exact:
                    from .goco import Stmt, _walk_stmt
                    initialization=normal.initialization.get(item.parent) if key.attribute_parent_kind=="INITIAL_ACCUMULATOR" else None
                    initial_binding=next((s.value.split(":")[1] for top in self.mapping.program.statements for s in _walk_stmt(top)
                        if isinstance(s,Stmt) and s.kind=="DECLARE" and self.mapping.program.node_ids[id(s)]==item.parent),None) if initialization else None
                    return {"key_id":key_id,"finding":"COVERED","status":"PASS","witness":{
                        "case_id":case.case_id,"occurrence_id":oid,"source_location":item.location,"parent_kind":key.attribute_parent_kind,
                        "parent_occurrence_id":item.parent,"parent_key_id":key.parent_key_id,"semantic_role":key.semantic_role,
                        "result_type":item.datatype,"computed_integer":key.computed_integer,"exact_required_lexeme":key.exact_required_lexeme,
                        "executed_values":normal.values.get(oid,[]),"normal_output":normal.output,
                        "expected_output_reference":case.expected_output_reference,
                        "initialization_value":initialization.value if initialization else None,
                        "initialization_dependencies":sorted(initialization.dependencies) if initialization else [],
                        "initial_accumulator_binding":initial_binding,
                        "downstream_state_read_occurrences":[read for read,proof in self.mapping.program.state_analysis.get("read_definitions",{}).items() if item.parent in proof],
                        "output_dependencies":sorted(normal.output_dependencies),"active_parent_witness":parent["witness"] if parent else None}}
        return {"key_id":key_id,"finding":"NOT_COVERED","status":"PASS","witness":None}

    def output_attribute(self,key_id:str) -> dict[str,Any]:
        self._check_bound_inputs();key=self._key(key_id)
        if key.evidence_kind!="OUTPUT_ATTRIBUTE":raise SchemaError("output key required")
        from .contract_ir import output_requirement
        requirement=output_requirement(key.operation)
        program=self.mapping.program
        if self.mapping.key_occurrences[key_id]!=(program.output_id,):raise ClosureError("output obligation is not attached to the final output node")
        rows=[];witness=None
        for case in sorted(self.cases,key=lambda c:c.case_id.encode("utf-8")):
            validate_record_reference(case.expected_output_reference,string_value=True)
            self.resolver.verify_record_content(case.expected_output_reference,case.expected_output)
            normal=self.normals[case.case_id]
            if program.output_id not in normal.evaluated or program.output_id not in normal.output_dependencies:raise ClosureError("expected output has no executed mapped output connection")
            v=int(_integer_output(case.expected_output))
            match=(str(v)==requirement["exact_sentinel"]) if requirement["output_requirement_kind"]=="EXACT_SENTINEL" else {"OUTPUT_ZERO":v==0,"OUTPUT_POSITIVE":v>0,"OUTPUT_NEGATIVE":v<0,"OUTPUT_MULTIDIGIT":abs(v)>=10}.get(key.operation)
            if match is None:raise SchemaError("unknown output category")
            row={"frozen_case_id":case.case_id,"expected_output_reference":case.expected_output_reference,"expected_output_value":case.expected_output,"mechanical_match":"MATCH" if match else "NO_MATCH"};rows.append(row)
            if match and witness is None:witness=row
        return {"key_id":key_id,**requirement,"finding":"COVERED" if witness else "NOT_COVERED","status":"PASS","cases":rows,"witness":witness,
                "output_attachment":{"occurrence_id":program.output_id,"source_location":program.item(program.output_id).location,"result_type":"INTEGER"}}


def behavioral_activity(*args:Any,**kwargs:Any):
    raise SchemaError("caller-supplied activity evidence is not authoritative; use CoverageEngine.behavioral")


def value_or_literal_coverage(*args:Any,**kwargs:Any):
    raise SchemaError("resolve attributes through CoverageEngine.attribute")


def output_attribute_coverage(*args:Any,**kwargs:Any):
    raise SchemaError("resolve bound cases through CoverageEngine.output_attribute")


def atomic_coverage(required:Sequence[tuple[ContractKey,str]],engines:Sequence[CoverageEngine]) -> list[dict[str,Any]]:
    rows=[]
    for key,condition in required:
        if condition not in {"ISOLATED","COMPOSITION"}:raise SchemaError("expanded condition required")
        witnesses=[];unresolved=False
        for engine in engines:
            if engine.mapping.contract.condition!=condition or engine.mapping.contract.domain!=key.domain:continue
            if key.key_id not in engine.mapping.key_occurrences:continue
            result=engine.behavioral(key.key_id) if key.evidence_kind=="BEHAVIORAL" else engine.attribute(key.key_id) if key.evidence_kind=="VALUE_OR_LITERAL_ATTRIBUTE" else engine.output_attribute(key.key_id)
            unresolved=unresolved or result["finding"]=="UNRESOLVED"
            if result["finding"] in {"ACTIVE","COVERED"}:witnesses.append(result)
        rows.append({"key_id":key.key_id,"condition":condition,"status":"PASS" if witnesses else "UNRESOLVED" if unresolved else "FAIL","witnesses":witnesses})
    return rows


def input_domain_obligations(engines:Sequence[CoverageEngine]) -> list[dict[str,Any]]:
    required={(condition,domain,label) for condition in ("ISOLATED","COMPOSITION") for domain,labels in (("numeric_iteration",("SIGN_ZERO","SIGN_POSITIVE","EMPTY_LOOP","LOWER_DOMAIN_BOUNDARY")),("array_reduction",("NEGATIVE_PRESENT","ZERO_PRESENT","POSITIVE_PRESENT"))) for label in labels}
    witnesses={r:[] for r in required}
    for engine in engines:
        domain=engine.mapping.program.domain;condition=engine.mapping.contract.condition
        key=next((k for k in engine.mapping.contract.canonical_keys if k.operation.startswith("INPUT_DOMAIN:")),None)
        if key is None:raise ClosureError("domain decoder key absent")
        activity=engine.behavioral(key.key_id)
        if activity["finding"]!="ACTIVE":continue
        for case in engine.cases:
            for label,decoded in input_domain_classes(domain,case.raw_input).items():
                identity=(condition,domain,label)
                if identity not in witnesses:raise SchemaError("unknown class/condition")
                witnesses[identity].append({"program_id":engine.mapping.program.program_id,"case_id":case.case_id,"raw_input":case.raw_input,"decoded":decoded,"activity_witness":activity["witness"]})
    return [{"row_id":rid("INPUT_DOMAIN_CLASS",list(identity)),"status":"PASS" if witnesses[identity] else "FAIL","witnesses":witnesses[identity]} for identity in sorted(required)]


def paired_scaffold_structure(left:Program,right:Program) -> dict[str,Any]:
    """Replace one structurally proved pair treatment, preserving all else."""
    from .core_ir import ungroup, integer_constant
    from .goco import _walk_stmt
    alpha_bijection(left.symbols,right.symbols,dict(zip(left.symbols,right.symbols)))
    def scaffold(program,operator):
        candidates=[]
        for top in program.statements:
            for stmt in _walk_stmt(top):
                if not hasattr(stmt,"expressions") or stmt.kind!="UPDATE" or stmt.value!="+=":continue
                if program.roles[stmt.expressions[0].value]!="DISPLAYED_ACCUMULATOR":continue
                expr=ungroup(stmt.expressions[1])
                if expr.kind!="BINARY" or expr.value!=operator or any(ungroup(c).kind!="ID" for c in expr.children):continue
                bindings=[ungroup(c).value for c in expr.children]
                if len(set(bindings))!=2 or any(program.roles[n]!="INDICATOR" for n in bindings):continue
                for name in bindings:
                    declaration=next(s for s in program.statements if s.kind=="DECLARE" and s.value.split(":")[1]==name)
                    if not declaration.expressions or integer_constant(declaration.expressions[0]) not in {0,1}:raise ClosureError("indicator initialization not proved")
                candidates.append((stmt,expr))
        if len(candidates)!=1:raise ClosureError("exactly one marked pair treatment required")
        stmt,expr=candidates[0]
        names={name:f"binding{index}" for index,name in enumerate(program.symbols)}
        target=("BINARY",operator,*(('ID',names[ungroup(c).value],"INTEGER") for c in expr.children))
        replaced=0
        def rewrite(value):
            nonlocal replaced
            if value==target:replaced+=1;return ("TREATMENT_EXPRESSION",*target[2:])
            return tuple(rewrite(v) if isinstance(v,tuple) else v for v in value)
        tree=rewrite(program.normalized_tree)
        if replaced!=1:raise ClosureError("treatment substitution not unique")
        return tree,expr
    a,expr_a=scaffold(left,"+");b,expr_b=scaffold(right,"*")
    if a!=b:raise ClosureError("INVALID_UNCONTROLLED_DIFFERENCE")
    return {"finding":"MATCHED","treatment_locations":[(expr_a.start,expr_a.end),(expr_b.start,expr_b.end)],
        "alpha_bijection":dict(zip(left.symbols,right.symbols)),"matched_complete_scaffold":a}


def paired_symmetry(left:CoverageEngine,right:CoverageEngine,*,left_prompt_artifact_id:str,right_prompt_artifact_id:str) -> dict[str,Any]:
    """Core source/prompt/case check, not an E3 budget/schedule producer."""
    from .contract_ir import _builder
    left._check_bound_inputs();right._check_bound_inputs()
    a,b=left.mapping.contract,right.mapping.contract
    if (a.condition,b.condition)!=("ISOLATED","COMPOSITION") or a.slot_id!=b.slot_id or a.task_kind!=b.task_kind or a.task_kind!="training":raise ClosureError("exact paired training slot required")
    if (a.domain,a.role_map,a.predicate_definitions,a.input_domain)!=(b.domain,b.role_map,b.predicate_definitions,b.input_domain):raise ClosureError("protected contract fields changed")
    source_proof=paired_scaffold_structure(left.mapping.program,right.mapping.program)
    builder=_builder();slots=[s for s in builder.LEDGER["slots"]["training_paired_slots"] if s["slot_id"]==a.slot_id]
    if len(slots)!=1:raise ClosureError("unknown paired slot")
    slot=slots[0];p,q=slot["P"],slot["Q"]
    clauses=(f"independently tally {builder.DESCRIPTIONS[p]} and {builder.DESCRIPTIONS[q]}",f"tally items satisfying both {builder.DESCRIPTIONS[p]} and {builder.DESCRIPTIONS[q]}")
    prompts=(left.resolver.read(left_prompt_artifact_id,role="PROMPT").decode("utf-8"),right.resolver.read(right_prompt_artifact_id,role="PROMPT").decode("utf-8"))
    for prompt,clause in zip(prompts,clauses):
        expected=builder.prompt_prefix(slot["family"])+f"For each item, {clause}; begin at {slot['offset']} and print the total."
        if prompt!=expected:raise ClosureError("INVALID_UNCONTROLLED_DIFFERENCE prompt")
    if prompts[0].replace(clauses[0],"<TREATMENT_DESCRIPTION>",1)!=prompts[1].replace(clauses[1],"<TREATMENT_DESCRIPTION>",1):raise ClosureError("prompt scaffold mismatch")
    if [(c.case_id,c.raw_input) for c in left.cases]!=[(c.case_id,c.raw_input) for c in right.cases]:raise ClosureError("paired case/order mismatch")
    return {"finding":"MATCHED","source_proof":source_proof,"prompt_scaffold":"MATCHED","case_inputs":"MATCHED",
        "output_consequences":[{"case_id":x.case_id,"isolated_output":left.normals[x.case_id].output,"composition_output":right.normals[y.case_id].output,
            "classification":"MATCHED" if x.expected_output==y.expected_output else "UNAVOIDABLE_SEMANTIC_CONSEQUENCE"} for x,y in zip(left.cases,right.cases)]}
