"""Internal, closed Boolean contribution-region transport; not an E5 audit.

Physical graphs and atomic keys are retained. A region transports a local
truth/01 interface, never an atomic AND key to a MUL key. Whole correspondence
additionally requires an unchanged typed statement scaffold and exhaustive
ownership. Unsupported contexts fail closed rather than growing a region.
"""
from collections import Counter
from dataclasses import dataclass, asdict

from .boolean_mapping import frozen_boolean_catalog, _inventory
from .core_ir import compile_program, ungroup, integer_constant, infer_type
from .goco import _walk_stmt, alpha_bijection
from .interfaces import SchemaError, ClosureError, canonical_json_bytes
from .semantic_ir import source_flow_equivalence


def json_value(value):
    import json
    return json.loads(canonical_json_bytes(value))


@dataclass(frozen=True)
class EquivalenceRegionCertificate:
    region_id: str
    frozen_rule: dict
    scope: str
    contract: dict
    source: dict
    alpha_mapping: dict
    local_v33_proof: dict
    boundary_semantics: dict
    completeness_basis: str


def sites(program, scope):
    """Select only complete direct loop-child contribution statements."""
    found = []
    def visit(rows, path=(), loops=(), controls=()):
        for index, stmt in enumerate(rows):
            here = path + (index,)
            root = ungroup(stmt.expressions[0]) if stmt.kind == "IF" else ungroup(stmt.expressions[1]) if stmt.kind == "UPDATE" else None
            candidate = root and root.kind == "BINARY" and (
                scope == "LOCAL_PAIR_JOINT" and root.value in {"&&", "*"} or
                scope == "BOOLEAN_OR" and (root.value == "||" or root.value == ">" and ungroup(root.children[0]).value == "+"))
            if candidate: found.append((stmt, root, here, loops, controls))
            visit(stmt.children, here, loops + (here,) if stmt.kind == "LOOP" else loops,
                  controls + (here,) if stmt.kind == "IF" else controls)
    visit(program.statements)
    return found


def shape(program, site, scope):
    """Derive exact members from parsed syntax, not caller membership flags.

    IF(cond){a+=1} exposes indicator(cond) as its integer contribution;
    a+=p*q exposes the proven-01 product. The IF bridge is explicitly retained
    and checked, not treated as an equal Boolean/integer atomic operation.
    """
    stmt, root, path, loops, controls = site
    if len(loops) != 1 or controls or path[:-1] != loops[0]:
        raise ClosureError("INCOMPATIBLE_REGION_LOOP_CONTROL")
    if stmt.kind == "IF":
        if len(stmt.children) != 1: raise ClosureError("UNRELATED_REGION_COMPUTATION")
        update = stmt.children[0]
        if update.kind != "UPDATE" or update.value != "+=" or integer_constant(update.expressions[1]) != 1 or ungroup(update.expressions[1]).kind != "NUMBER":
            raise ClosureError("INCOMPATIBLE_REGION_DOWNSTREAM_CONSUMER")
        form = "CONDITIONAL_UNIT_CONTRIBUTION"
    elif stmt.kind == "UPDATE" and stmt.value == "+=" and scope == "LOCAL_PAIR_JOINT" and root.value == "*":
        update = stmt; form = "PROVEN_01_PRODUCT_CONTRIBUTION"
    else: raise ClosureError("UNLISTED_REGION_REALIZATION")
    target = update.expressions[0].value
    if program.roles[target] != "DISPLAYED_ACCUMULATOR": raise ClosureError("INCOMPATIBLE_REGION_STATE_BOUNDARY")
    nodes = {program.node_ids[id(n)] for n in _walk_stmt(stmt) if id(n) in program.node_ids}
    # Semantic primitive nodes are part of the replaced structure, not ignored.
    nodes |= {alias for original, alias in program.primitive_aliases.items() if original in nodes}
    internal, incoming, outgoing = [], [], []
    for edge in program.items:
        if edge.kind != "EDGE": continue
        a, b = edge.source in nodes, edge.target in nodes
        if a and b: internal.append(edge.occurrence_id)
        elif b: incoming.append(edge.occurrence_id)
        elif a: outgoing.append(edge.occurrence_id)
    ports = lambda ids: [asdict(program.item(oid)) for oid in ids]
    return {"statement_path": path, "loop_paths": loops, "control_paths": controls,
        "statement_location": [stmt.start, stmt.end], "expression_location": [root.start, root.end],
        "expression_node": program.node_ids[id(root)], "state_update_node": program.node_ids[id(update)],
        "target_binding": target, "target_role": program.roles[target], "realization": form,
        "operand_types": [infer_type(e, program.symbols, program.imports) for e in root.children],
        "expression_result_type": infer_type(root, program.symbols, program.imports),
        "semantic_result_type": "INTEGER_01_CONTRIBUTION", "nodes": sorted(nodes), "internal_edges": internal,
        "boundary_input_ports": ports(incoming), "boundary_output_ports": ports(outgoing),
        "owned_edges": [], "members": []}


def scaffold(program, region_shapes, names):
    selected = {tuple(r["statement_path"]): index for index, r in enumerate(region_shapes)}
    def expr(e):
        e = ungroup(e)
        return (e.kind, names.get(e.value, e.value), *(expr(c) for c in e.children))
    def rows(statements, path=()):
        result = []
        for index, s in enumerate(statements):
            here = path + (index,)
            if here in selected:
                r = region_shapes[selected[here]]
                result.append(("AUTHORIZED_LOCAL_REGION", selected[here], names[r["target_binding"]], r["loop_paths"], r["control_paths"]))
            else:
                value = s.value
                if s.kind == "DECLARE": typ, name = value.split(":"); value = (typ, names[name])
                result.append((s.kind, value, names.get(s.loop_index), tuple(expr(e) for e in s.expressions), rows(s.children, here)))
        return tuple(result)
    return rows(program.statements)


def assign_edges(program, shapes):
    owner = {oid: index for index, r in enumerate(shapes) for oid in r["nodes"]}
    if sum(len(r["nodes"]) for r in shapes) != len(owner): raise ClosureError("OVERLAPPING_REGION_NODES")
    for edge in program.items:
        if edge.kind == "EDGE" and (edge.source in owner or edge.target in owner):
            # A cross-region state edge has one owner (destination); both port
            # inventories can reference it without claiming it twice.
            index = owner[edge.target] if edge.target in owner else owner[edge.source]
            shapes[index]["owned_edges"].append(edge.occurrence_id)
    for r in shapes: r["members"] = r["nodes"] + r["owned_edges"]


def dependency_graph(region_ids):
    nodes = [{"id": n, "kind": "ROOT"} for n in ("parsed_typed_source", "frozen_metadata", "primitive_recognition", "reaching_definitions")]
    edges = [["parsed_typed_source", "primitive_recognition"], ["parsed_typed_source", "reaching_definitions"], ["frozen_metadata", "primitive_recognition"]]
    for rid in region_ids:
        nodes.append({"id": rid, "kind": "LOCAL_V33_REGION"})
        edges += [[n, rid] for n in ("parsed_typed_source", "frozen_metadata", "primitive_recognition", "reaching_definitions")]
    nodes += [{"id": "total_v32", "kind": "TOTAL_MAPPING"}, {"id": "indicator_evidence", "kind": "DERIVED_EVIDENCE"}]
    edges += [[r, "total_v32"] for r in region_ids] + [["parsed_typed_source", "total_v32"], ["total_v32", "indicator_evidence"]]
    return {"nodes": nodes, "edges": edges}


def coverage_partition(source, contract, pairs, regions):
    out = {}
    for side, program in (("source", source), ("contract", contract)):
        ordinary = [p[side] for p in pairs]
        regional = [oid for r in regions for oid in r[side]["members"]]
        counts = Counter(ordinary + regional)
        domain = {i.occurrence_id for i in program.items}
        out.update({side + "_ordinary_covered": sorted(ordinary), side + "_region_covered": sorted(regional),
            side + "_uncovered": sorted(domain - set(counts)), side + "_duplicate_coverage": sorted(oid for oid, count in counts.items() if count != 1)})
    return out


def total_boolean_mapping(contract, source, *, scope, alpha_map=None):
    """Construct evidence; acceptance is separately checked from serialized data."""
    if contract.task_kind != "development" or contract.core_gaps:
        raise ClosureError("UNRESOLVED_REQUIREMENT: internal region mapper requires a complete development contract")
    catalog = frozen_boolean_catalog(); contract.validate()
    c, p = contract.ir, compile_program(contract.program_id, source)
    names = alpha_map if alpha_map is not None else dict(zip(c.symbols, p.symbols))
    result = {"schema_version": 1, "artifact_kind": "INTERNAL_BOOLEAN_REGION_TOTAL_MAPPING", "scope": scope,
        "source_inventory": _inventory(p), "contract_inventory": _inventory(c), "alpha_mapping": names,
        "regions": [], "ordinary_correspondence": [], "local_v33_proofs": [],
        "complete_graph_equivalence_claim": False, "atomic_key_transport_claim": False,
        "indicator_evidence_permitted": False}
    try:
        if scope not in {"LOCAL_PAIR_JOINT", "BOOLEAN_OR"}: raise ClosureError("UNLISTED_BOOLEAN_SCOPE")
        alpha_bijection(c.symbols, p.symbols, names)
        if any(c.roles[a] != p.roles[b] for a, b in names.items()): raise ClosureError("ALPHA_ROLE_MISMATCH")
        left, right = sites(c, scope), sites(p, scope)
        # Keep local proofs even when an extra unrelated statement defeats V3.2.
        for a, b in zip(left, right):
            result["local_v33_proofs"].append(source_flow_equivalence(c, a[1], p, b[1], context=scope, alpha_map=names))
        if not left or len(left) != len(right): raise ClosureError("BOOLEAN_REGION_INVENTORY_INCOMPLETE")
        cs, ps = [], []
        rule = next(r for r in catalog["rules"] if r["scope"] == scope)
        for index, (a, b, proof) in enumerate(zip(left, right, result["local_v33_proofs"])):
            if proof["finding"] != "EQUIVALENT": raise ClosureError("LOCAL_BOOLEAN_PRECONDITION: " + proof["reason"])
            ca, sa = shape(c, a, scope), shape(p, b, scope)
            if ca["statement_path"] != sa["statement_path"] or names[ca["target_binding"]] != sa["target_binding"]:
                raise ClosureError("INCOMPATIBLE_REGION_BOUNDARY")
            cs.append(ca); ps.append(sa)
            relation = "AND" if scope == "LOCAL_PAIR_JOINT" else "OR"
            truth = [{"operands": [x, y], "contribution": int(x and y) if relation == "AND" else int(x or y)} for x in (False, True) for y in (False, True)]
            result["regions"].append(asdict(EquivalenceRegionCertificate(
                "region_" + str(index), rule, scope, ca, sa, names, proof,
                {"incoming_predicate_identity": proof["normalized_local_relation"], "truth_01_table": truth,
                 "state_transition": "prior_accumulator + contribution01", "no_other_writes": True,
                 "integer01_if_bridge": "exact singleton +=1 under condition; false leaves value unchanged",
                 "atomic_keys_remain_distinct": True},
                "exact parsed contribution statement plus its semantic primitive occurrences; all incident edges recorded")))
        assign_edges(c, cs); assign_edges(p, ps)
        # asdict copies nested members; replace with the completed ownership.
        for r, ca, sa in zip(result["regions"], cs, ps): r.update(contract=ca, source=sa)
        cn = {name: "binding" + str(i) for i, name in enumerate(c.symbols)}
        pn = {names[name]: value for name, value in cn.items()}
        if scaffold(c, cs, cn) != scaffold(p, ps, pn): raise ClosureError("INCOMPATIBLE_ORDINARY_STATEMENT_SCAFFOLD")
        excluded_c = {o for r in cs for o in r["members"]}; excluded_p = {o for r in ps for o in r["members"]}
        ca = [i for i in c.items if i.kind == "NODE" and i.occurrence_id not in excluded_c]
        sa = [i for i in p.items if i.kind == "NODE" and i.occurrence_id not in excluded_p]
        if len(ca) != len(sa): raise ClosureError("ORDINARY_NODE_INVENTORY_INCOMPLETE")
        table = {}
        def node_value(item, rename):
            if item.operation == "INITIALIZE":
                typ, binding = item.value.split(":")
                return typ, rename[binding]
            return rename.get(item.value, item.value)
        for a, b in zip(ca, sa):
            if a.semantic_identity() != b.semantic_identity() or node_value(a, cn) != node_value(b, pn): raise ClosureError("ORDINARY_NODE_TYPE_ROLE_VALUE_MISMATCH")
            table[a.occurrence_id] = b.occurrence_id
        def edge_key(e, rename):
            return (rename.get(e.source, e.source), rename.get(e.target, e.target), e.port, e.semantic_identity())
        available = {}
        for b in p.items:
            if b.kind == "EDGE" and b.occurrence_id not in excluded_p: available.setdefault(edge_key(b, {}), []).append(b.occurrence_id)
        for a in c.items:
            if a.kind == "EDGE" and a.occurrence_id not in excluded_c:
                key = edge_key(a, table)
                if not available.get(key): raise ClosureError("ORDINARY_EDGE_PORT_STATE_MISMATCH")
                table[a.occurrence_id] = available[key].pop(0)
        if any(available.values()): raise ClosureError("SOURCE_ORDINARY_EDGE_UNCOVERED")
        result["ordinary_correspondence"] = [{"contract": a, "source": b} for a, b in table.items()]
        result["partition"] = coverage_partition(p, c, result["ordinary_correspondence"], result["regions"])
        if any(result["partition"][side + suffix] for side in ("source", "contract") for suffix in ("_uncovered", "_duplicate_coverage")): raise ClosureError("TOTAL_COVERAGE_INCOMPLETE")
        result.update(finding="COMPLETE", proof_dependency_graph=dependency_graph([r["region_id"] for r in result["regions"]]))
        from .boolean_region_checker import check_serialized_mapping
        check_serialized_mapping(json_value(result))
        result["indicator_evidence_permitted"] = True
    except (SchemaError, ClosureError) as exc:
        result.update(finding="UNRESOLVED", reason=str(exc), indicator_evidence_permitted=False)
        result["partition"] = coverage_partition(p, c, result["ordinary_correspondence"], result["regions"])
    return json_value(result)
