"""Pre-RO structural correspondence; surplus source never selects obligations.

The complete prospective development grammar is verified independently of the
source. Ordered-subsequence matching is an accounting proof view, NOT edited
source/AST/graph. All ambiguous/missing correspondences are fail closed.
No RO, activity, E1, output agreement, or producer final status is consulted.
"""
from dataclasses import dataclass
import json

from .core_ir import compile_program, ungroup, integer_constant
from .goco import Expr
from .interfaces import rid, canonical_json_bytes, ClosureError
from .projection_binding_verifier import verify_projection_plan, reference_sites, reconstruct_bindings, digest_source
from .projection_grammar import render_development
from .reference_only_inventory import ref
from .typed_alignment import align


@dataclass(frozen=True)
class PreDispositionMappingContextV1:
    payload: bytes

    def value(self):
        return json.loads(self.payload)


def match_required_structure(c, p):
    """Match full required AST/typed raw graph without classifying any surplus."""
    if c.domain != p.domain:
        raise ClosureError("V32_REQUIRED_MAPPING_INVALID: DOMAIN")
    solutions = []
    def expression(a, b, names, table):
        a, b = ungroup(a), ungroup(b)
        if a.kind != b.kind or len(a.children) != len(b.children):
            return None
        if a.kind == "ID":
            if a.value in c.symbols:
                if names.get(a.value) != b.value:
                    return None
            elif a.value != b.value:
                return None
        elif a.value != b.value:
            return None
        ao, bo = c.node_ids.get(id(a)), p.node_ids.get(id(b))
        if ao is not None:
            if bo is None or (ao in table and table[ao] != bo) or (bo in table.values() and table.get(ao) != bo):
                return None
            table[ao] = bo
            if ao in c.primitive_aliases:
                if bo not in p.primitive_aliases:
                    return None
                table[c.primitive_aliases[ao]] = p.primitive_aliases[bo]
        for left, right in zip(a.children, b.children):
            if expression(left, right, names, table) is None:
                return None
        return table
    def statement(a, b, names, table):
        if a.kind != b.kind or len(a.expressions) != len(b.expressions) or a.alternate or b.alternate:
            return []
        names, table = dict(names), dict(table)
        if a.kind == "DECLARE":
            at, an = a.value.split(":"); bt, bn = b.value.split(":")
            if at != bt or an in names and names[an] != bn or bn in names.values() and names.get(an) != bn:
                return []
            names[an] = bn
        elif a.value != b.value:
            return []
        if a.kind == "LOOP":
            if a.value == "FORWARD":
                if b.loop_index in names.values():
                    return []
                names[a.loop_index] = b.loop_index
            elif names.get(a.loop_index) != b.loop_index:
                return []
        ao, bo = c.node_ids.get(id(a)), p.node_ids.get(id(b))
        if ao is not None:
            if bo in table.values():
                return []
            table[ao] = bo
        if ao in c.index_nodes:
            if bo not in p.index_nodes:
                return []
            table.update(zip(c.index_nodes[ao], p.index_nodes[bo]))
        for left, right in zip(a.expressions, b.expressions):
            if expression(left, right, names, table) is None:
                return []
        return block(a.children, b.children, names, table)
    def block(required, source, names, table, start=0):
        if not required:
            return [(names, table)]
        results = []
        for i in range(start, len(source)):
            for new_names, new_table in statement(required[0], source[i], names, table):
                results.extend(block(required[1:], source, new_names, new_table, i + 1))
                if len(results) > 1:
                    return results[:2]
        return results
    solutions = block(c.statements, p.statements, {}, {})
    if len(solutions) != 1:
        raise ClosureError("V32_REQUIRED_MAPPING_INVALID: AMBIGUOUS_OR_MISSING_REQUIRED_STRUCTURE")
    names, table = solutions[0]
    if set(names) != set(c.symbols) or len(set(names.values())) != len(names) or any(c.symbols[a] != p.symbols[b] or c.roles[a] != p.roles[b] for a, b in names.items()):
        raise ClosureError("V32_REQUIRED_MAPPING_INVALID: BINDING_TYPE_ROLE")
    table[c.macro_id] = p.macro_id
    for a in (i for i in c.items if i.kind == "NODE"):
        if a.occurrence_id not in table:
            raise ClosureError("V32_REQUIRED_MAPPING_INVALID: INCOMPLETE_REQUIRED_NODE")
        b = p.item(table[a.occurrence_id])
        if a.semantic_identity() != b.semantic_identity():
            raise ClosureError("V32_REQUIRED_MAPPING_INVALID: TYPED_NODE")
    used = set()
    for a in (i for i in c.items if i.kind == "EDGE"):
        selected = [b for b in p.items if b.kind == "EDGE" and b.occurrence_id not in used
                    and b.semantic_identity() == a.semantic_identity()
                    and b.source == table[a.source] and b.target == table[a.target]
                    and (b.port == a.port or a.operation == "PRIOR_STATE_TO_UPDATE")]
        if len(selected) != 1:
            raise ClosureError("V32_REQUIRED_MAPPING_INVALID: TYPED_EDGE_OR_MULTIPLICITY")
        used.add(selected[0].occurrence_id)
        table[a.occurrence_id] = selected[0].occurrence_id
    return names, table


def prospective_structure(plan):
    """Verify unchanged grammar first; canonical scaffold is not candidate data."""
    verify_projection_plan(plan)
    source = render_development(plan["declaration"], "prospectiveRO")
    c = compile_program(plan["program_id"], source)
    reference_sites(plan, c)
    return c


def prior_bindings(plan, c):
    """Rebuild accepted prior head selectors AND complete typed dependencies.

    Only the independently rendered prior grammar is an input here. Candidate
    incident edges can never enlarge the required footprint after an RO result.
    No producer/evidence constructor is imported or called.
    """
    alignment = align(c, c)
    bindings, foundations = reconstruct_bindings(plan, c, c, dict(
        ordinary_correspondence=alignment["correspondence"], source_sha256=digest_source(c.source)))
    return bindings


def required_selector_audit(plan, c, bindings):
    """Dependency evidence is not a license to invent requirement selectors.

    The prior adapter's contract_occurrences are its resolved selectors. An
    incident dependency is separately retained structural evidence, not another
    satisfaction of that selector or its canonical key/multiplicity. This audit
    falsifies the draft footprint-as-membership shortcut without claiming that
    a different, fully bound occurrence-level contract cannot be implemented.
    """
    unsupported = []
    for requirement, binding in zip(plan["requirements"], bindings):
        for head in binding["contract_occurrences"]:
            for edge in binding["dependency_edges"]:
                if head not in {edge["source"], edge["target"]}:
                    continue
                if edge["occurrence_id"] != head:
                    unsupported.append(dict(requirement_id=requirement["requirement_id"],
                        canonical_contract_key_id=requirement["canonical_contract_key"],
                        selected_requirement_occurrence_id=head,
                        selected_kind=c.item(head).kind, selected_operation=c.item(head).operation,
                        proposed_dependency_occurrence_id=edge["occurrence_id"],
                        proposed_kind=edge["kind"], proposed_operation=edge["operation"],
                        dependency_is_not_selected_occurrence=True))
    return unsupported


def build_pre_context(plan, p, inventory, graph, state, contract_reference, *, direct_artifact_id):
    """Freeze complete prior memberships before RO, preserving key multiplicity.

    Required heads retain the accepted plan's exact IDs/keys/multiplicities.
    Their already-bound full typed dependency edges participate in complete
    structural correspondence, not as invented additional canonical keys.
    Only canonical prior edges, NEVER arbitrary candidate incident edges, enter
    these memberships. Head multiplicity is separately verified on selectors.
    """
    c = prospective_structure(plan)
    names, correspondence = match_required_structure(c, p)
    bindings = prior_bindings(plan, c)
    if len(bindings) != len(plan["requirements"]):
        raise ClosureError("V32_PRE_DISPOSITION_CONTEXT_INVALID: REQUIREMENT_COUNT")
    # Fail before a logical CLOSED context exists. The earlier draft incorrectly
    # treated every retained dependency as satisfying the head's selector. The
    # complete raw graph remains available, but that evidence alone cannot
    # supply the missing occurrence/key/multiplicity/attachment bridge.
    if required_selector_audit(plan, c, bindings):
        raise ClosureError("V32_PRE_DISPOSITION_CONTEXT_INVALID: DEPENDENCY_IS_NOT_REQUIRED_SELECTOR")
    requirements, memberships = [], {}
    for requirement, binding in zip(plan["requirements"], bindings):
        heads = binding["contract_occurrences"]
        if len(heads) != requirement["multiplicity"] or len(set(heads)) != len(heads):
            raise ClosureError("V32_PRE_DISPOSITION_CONTEXT_INVALID: MULTIPLICITY")
        for head in heads:
            ordinal = str(len(requirements) + 1)
            # Preserve the existing bound prospective graph's occurrence ID.
            # One entry per selected occurrence; group multiplicity is checked
            # above, not incorrectly repeated for every physical dependency.
            reqid = head
            requirements.append(dict(record_id=rid("V32REQ", [p.program_id, ordinal]),
                requirement_occurrence_id=reqid, canonical_contract_key_id=requirement["canonical_contract_key"],
                prospective_contract_reference=contract_reference, required_multiplicity=1,
                attachment_references=[contract_reference]))
            footprint = {head} | {edge["occurrence_id"] for edge in binding["dependency_edges"]
                                  if edge["source"] == head or edge["target"] == head}
            for oid in footprint:
                if oid not in correspondence:
                    raise ClosureError("V32_PRE_DISPOSITION_CONTEXT_INVALID: PRIOR_FOOTPRINT_UNBOUND")
                memberships.setdefault(correspondence[oid], []).append(reqid)
    if set(correspondence.values()) != set(memberships):
        raise ClosureError("V32_PRE_DISPOSITION_CONTEXT_INVALID: REQUIRED_GRAPH_FOOTPRINT_UNCLOSED")
    input_artifact = inventory["source_reference"]["artifact_id"]
    evidence = [contract_reference, ref(input_artifact, inventory["record_id"]),
                ref(direct_artifact_id, graph["record_id"]), ref(direct_artifact_id, state["record_id"])]
    required_order = {r["requirement_occurrence_id"]: i for i, r in enumerate(requirements)}
    mappings = [dict(source_occurrence_id=row["occurrence"]["occurrence_id"],
                     required_occurrence_ids=sorted(set(memberships[row["occurrence"]["occurrence_id"]]), key=required_order.get),
                     evidence_record_references=evidence)
                for row in inventory["occurrences"] if row["occurrence"]["occurrence_id"] in memberships]
    # These are typed structural correspondences under the independently
    # reconstructed binding bijection. Incidental alpha spelling changes are
    # already licensed; no constant/Boolean rewrite is invented by this adapter.
    context = dict(schema_version=1, record_id=rid("V32PREMAP", [p.program_id]), program_id=p.program_id,
        prospective_contract_reference=contract_reference, source_inventory_reference=ref(input_artifact, inventory["record_id"]),
        graph_reference=ref(direct_artifact_id, graph["record_id"]), state_reference=ref(direct_artifact_id, state["record_id"]),
        required_occurrences=requirements, direct_mapping_candidates=mappings,
        authorized_equivalence_correspondences=[], equivalence_internal_members=[],
        still_unmatched_occurrence_ids=[r["occurrence"]["occurrence_id"] for r in inventory["occurrences"]
                                      if r["occurrence"]["occurrence_id"] not in memberships],
        context_status="CLOSED", scientific_reason_codes=[])
    return PreDispositionMappingContextV1(canonical_json_bytes(context)), c, correspondence


def inspect_pre_context_inputs(plan, p, inventory, graph, state, contract_reference, *, direct_artifact_id):
    """Draft prerequisite diagnostic, NOT a constructor of a frozen context.

    Returning source alignment here does not grant ABSENT, CLOSED, a V32REQ
    membership, a valid accounting bucket, or an RO admission.
    """
    c = prospective_structure(plan)
    names, correspondence = match_required_structure(c, p)
    # The accepted projection plan is a *capability-kind witness*, not a complete
    # occurrence-level contract. Resolve its actual selectors, but do not invent
    # canonical keys/multiplicity/attachments for the separate raw-graph match.
    declared = set()
    sites, statements, _ = reference_sites(plan, c)
    for requirement in plan["requirements"]:
        for occurrence in requirement["occurrence_requirements"]:
            selector = occurrence["selector"]
            kind = selector["kind"]
            if kind == "EDGE_KIND":
                matches = [i for i in c.items if i.kind == "EDGE"
                           and i.operation == selector["operation"] and i.datatype == selector["datatype"]
                           and i.operand_roles == (selector["source_role"],) and i.result_role == selector["target_role"]]
                if not matches:
                    raise ClosureError("V32_REQUIRED_MAPPING_INVALID: REQUIRED_EDGE_KIND_MISSING")
                declared.add(matches[0].occurrence_id)
            elif kind == "DOMAIN":
                declared.add(c.macro_id)
            elif kind == "PRIMITIVE":
                declared.add(c.primitive_aliases[sites[selector["path"]]])
            elif kind == "INDEX_STATE":
                declared.add(c.index_nodes[sites[selector["path"]]][0 if selector["part"] == "initial" else 1])
            elif kind == "REGION":
                declared.add(sites[selector["path"] + "/e0"])
            else:
                declared.add(sites[selector["path"]])
    missing = [item.occurrence_id for item in c.items if item.occurrence_id not in declared]
    return dict(program=c, correspondence=correspondence, declared_selectors=declared,
                raw_structural_occurrences_without_declared_key_selector=missing,
                context_status="UNRESOLVED",
                scientific_reason_codes=["V32_PRE_DISPOSITION_CONTEXT_INVALID"])
