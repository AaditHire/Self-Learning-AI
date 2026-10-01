"""Independent consumer of serialized Boolean region mapping evidence.

Does not call total_boolean_mapping, shape, assign_edges, coverage_partition,
scaffold or dependency_graph. Parsing, primitive recognition and the trusted
local V3.3 source-flow lemma are foundations, not constructor decisions.
"""
from collections import Counter
from dataclasses import asdict
from .core_ir import compile_program, ungroup, integer_constant, infer_type
from .goco import _walk_stmt, alpha_bijection
from .interfaces import ClosureError, canonical_json_bytes
from .boolean_mapping import frozen_boolean_catalog, _inventory
from .semantic_ir import source_flow_equivalence


def require(ok, reason):
    if not ok: raise ClosureError(reason)


def equal(a, b):
    return canonical_json_bytes(a) == canonical_json_bytes(b)


def _side(program, row, scope):
    """Independently discover selected statement and exact physical region."""
    found = []
    paths = {}
    def visit(rows, path=(), loops=(), controls=()):
        for index, s in enumerate(rows):
            here = path + (index,); paths[here] = (s, loops, controls)
            if [s.start, s.end] == row["statement_location"]: found.append((s, here, loops, controls))
            visit(s.children, here, loops + (here,) if s.kind == "LOOP" else loops, controls + (here,) if s.kind == "IF" else controls)
    visit(program.statements)
    require(len(found) == 1, "REGION_STATEMENT_NOT_FOUND")
    s, path, loops, controls = found[0]
    require(len(loops) == 1 and not controls and path[:-1] == loops[0], "REGION_LOOP_CONTROL_MISMATCH")
    require(equal(path, row["statement_path"]) and equal(loops, row["loop_paths"]) and equal(controls, row["control_paths"]), "REGION_CONTEXT_MUTATION")
    if s.kind == "IF":
        require(len(s.children) == 1, "REGION_HIDES_EXTRA_COMPUTATION")
        update = s.children[0]; e = ungroup(s.expressions[0])
        require(update.kind == "UPDATE" and update.value == "+=" and ungroup(update.expressions[1]).kind == "NUMBER" and integer_constant(update.expressions[1]) == 1, "REGION_DOWNSTREAM_NOT_UNIT_UPDATE")
        form = "CONDITIONAL_UNIT_CONTRIBUTION"
        require(e.kind == "BINARY" and (e.value == "&&" if scope == "LOCAL_PAIR_JOINT" else e.value == "||" or e.value == ">" and ungroup(e.children[0]).value == "+"), "UNAUTHORIZED_REGION_EXPRESSION")
    else:
        require(s.kind == "UPDATE" and s.value == "+=" and scope == "LOCAL_PAIR_JOINT", "UNAUTHORIZED_REGION_STATEMENT")
        update = s; e = ungroup(s.expressions[1]); form = "PROVEN_01_PRODUCT_CONTRIBUTION"
        require(e.kind == "BINARY" and e.value == "*", "UNAUTHORIZED_PRODUCT_REALIZATION")
    target = update.expressions[0].value
    require(program.roles[target] == "DISPLAYED_ACCUMULATOR" and target == row["target_binding"], "REGION_STATE_BOUNDARY_MISMATCH")
    require(row["target_role"] == program.roles[target] and row["realization"] == form, "REGION_ROLE_REALIZATION_MUTATION")
    require(row["semantic_result_type"] == "INTEGER_01_CONTRIBUTION" and row["expression_result_type"] == infer_type(e, program.symbols, program.imports), "REGION_RESULT_TYPE_MUTATION")
    require(equal(row["operand_types"], [infer_type(x, program.symbols, program.imports) for x in e.children]), "REGION_OPERAND_TYPE_MUTATION")
    require(row["expression_node"] == program.node_ids[id(e)] and row["state_update_node"] == program.node_ids[id(update)] and row["expression_location"] == [e.start, e.end], "REGION_LOCATION_MUTATION")
    nodes = {program.node_ids[id(n)] for n in _walk_stmt(s) if id(n) in program.node_ids}
    nodes.update(alias for original, alias in program.primitive_aliases.items() if original in nodes)
    require(len(row["nodes"]) == len(set(row["nodes"])) and set(row["nodes"]) == nodes, "REGION_NODE_COMPLETENESS")
    internal, incoming, outgoing = [], [], []
    for edge in program.items:
        if edge.kind != "EDGE": continue
        a, b = edge.source in nodes, edge.target in nodes
        if a and b: internal.append(edge.occurrence_id)
        elif b: incoming.append(asdict(edge))
        elif a: outgoing.append(asdict(edge))
    require(equal(row["internal_edges"], internal), "REGION_INTERNAL_EDGE_COMPLETENESS")
    require(equal(row["boundary_input_ports"], incoming), "REGION_INPUT_BOUNDARY_PORT_MISMATCH")
    require(equal(row["boundary_output_ports"], outgoing), "REGION_OUTPUT_BOUNDARY_PORT_MISMATCH")
    return s, e, path, target


def check_serialized_mapping(cert):
    require(cert.get("finding") == "COMPLETE", "COMPLETE_MAPPING_REQUIRED")
    require(not cert.get("complete_graph_equivalence_claim") and not cert.get("atomic_key_transport_claim"), "UNAUTHORIZED_FULL_GRAPH_OR_ATOMIC_KEY_CLAIM")
    scope = cert["scope"]
    require(scope in {"LOCAL_PAIR_JOINT", "BOOLEAN_OR"}, "UNLISTED_SCOPE")
    programs = {}
    for side in ("source", "contract"):
        inv = cert[side + "_inventory"]
        p = compile_program(inv["program_id"], inv["source"])
        require(equal(inv, _inventory(p)), "SERIALIZED_GRAPH_SOURCE_MISMATCH")
        programs[side] = p
    c, p = programs["contract"], programs["source"]
    require(c.program_id == p.program_id and c.domain == p.domain, "PROGRAM_DOMAIN_MISMATCH")
    names = cert["alpha_mapping"]; alpha_bijection(c.symbols, p.symbols, names)
    require(all(c.roles[a] == p.roles[b] and c.symbols[a] == p.symbols[b] for a, b in names.items()), "ALPHA_TYPE_ROLE_MISMATCH")
    regions = cert["regions"]
    ids = [r["region_id"] for r in regions]
    require(ids and len(ids) == len(set(ids)), "DUPLICATE_OR_MISSING_REGION_ID")
    for side in ("source", "contract"):
        locations = [tuple(r[side]["statement_path"]) for r in regions]
        require(len(locations) == len(set(locations)), "OVERLAPPING_REGION_CANDIDATES")
        claimed = [o for r in regions for o in r[side]["nodes"]]
        require(len(claimed) == len(set(claimed)), "OVERLAPPING_REGION_NODES")
    rule = next(r for r in frozen_boolean_catalog()["rules"] if r["scope"] == scope)
    selected = {"source": {}, "contract": {}}
    for r in regions:
        require(r["scope"] == scope and equal(r["frozen_rule"], rule) and equal(r["alpha_mapping"], names), "FROZEN_REGION_AUTHORITY_MISMATCH")
        cs, ce, cp, ct = _side(c, r["contract"], scope)
        ss, se, sp, st = _side(p, r["source"], scope)
        require(cp == sp and names[ct] == st, "REGION_INTERFACE_CONTEXT_TARGET_MISMATCH")
        proof = source_flow_equivalence(c, ce, p, se, context=scope, alpha_map=names)
        require(proof["finding"] == "EQUIVALENT" and equal(proof, r["local_v33_proof"]), "LOCAL_V33_SOURCE_FLOW_MISMATCH")
        table = [{"operands": [a, b], "contribution": int(a and b) if scope == "LOCAL_PAIR_JOINT" else int(a or b)} for a in (False, True) for b in (False, True)]
        expected = {"incoming_predicate_identity": proof["normalized_local_relation"], "truth_01_table": table,
            "state_transition": "prior_accumulator + contribution01", "no_other_writes": True,
            "integer01_if_bridge": "exact singleton +=1 under condition; false leaves value unchanged", "atomic_keys_remain_distinct": True}
        require(equal(r["boundary_semantics"], expected), "REGION_SEMANTIC_BOUNDARY_MUTATION")
        require(r["completeness_basis"] == "exact parsed contribution statement plus its semantic primitive occurrences; all incident edges recorded", "REGION_COMPLETENESS_BASIS_MUTATION")
        for side, path in (("contract", cp), ("source", sp)):
            require(path not in selected[side], "OVERLAPPING_REGION_CANDIDATES")
            selected[side][path] = r
    require(equal(cert["local_v33_proofs"], [r["local_v33_proof"] for r in regions]), "LOCAL_PROOF_REFERENCE_INCOMPLETE")
    # Recompute coverage from actual claims, not the saved partition/PASS flag.
    partition = {}
    coverage_errors = []
    pairs = cert["ordinary_correspondence"]
    for side, program in programs.items():
        node_owners = {}
        for r in regions:
            for oid in r[side]["nodes"]:
                require(oid not in node_owners, "OVERLAPPING_REGION_NODES")
                node_owners[oid] = r["region_id"]
        expected_edges = {rid: [] for rid in ids}
        for edge in program.items:
            if edge.kind == "EDGE" and (edge.source in node_owners or edge.target in node_owners):
                owner = node_owners.get(edge.target, node_owners.get(edge.source))
                expected_edges[owner].append(edge.occurrence_id)
        for r in regions:
            require(equal(r[side]["owned_edges"], expected_edges[r["region_id"]]), "REGION_EDGE_OWNERSHIP_INCOMPLETE")
            require(equal(r[side]["members"], r[side]["nodes"] + expected_edges[r["region_id"]]), "REGION_MEMBER_CLAIM_MUTATION")
        ordinary = [x[side] for x in pairs]; regional = [oid for r in regions for oid in r[side]["members"]]
        count = Counter(ordinary + regional); domain = {i.occurrence_id for i in program.items}
        require(set(count) <= domain, "INVENTED_COVERAGE_OCCURRENCE")
        missing = sorted(domain - set(count)); duplicate = sorted(o for o, n in count.items() if n != 1)
        if duplicate: coverage_errors.append(side.upper() + "_DUPLICATE_COVERAGE")
        if missing: coverage_errors.append(side.upper() + "_UNCOVERED")
        partition.update({side + "_ordinary_covered": sorted(ordinary), side + "_region_covered": sorted(regional), side + "_uncovered": missing, side + "_duplicate_coverage": duplicate})
    require(not coverage_errors, "; ".join(coverage_errors))
    require(equal(partition, cert["partition"]), "SAVED_PARTITION_MISMATCH")
    table = {x["contract"]: x["source"] for x in pairs}
    cn = {n: "binding" + str(i) for i, n in enumerate(c.symbols)}
    pn = {names[n]: v for n, v in cn.items()}
    def normalize(program, side, rename):
        def ex(e):
            e = ungroup(e)
            return (e.kind, rename.get(e.value, e.value), *(ex(ch) for ch in e.children))
        def walk(rows, path=()):
            out = []
            for i, s in enumerate(rows):
                here = path + (i,)
                if here in selected[side]:
                    r = selected[side][here]; z = r[side]
                    out.append(("REGION", r["region_id"], rename[z["target_binding"]], z["loop_paths"], z["control_paths"]))
                else:
                    value = s.value
                    if s.kind == "DECLARE": typ, name = value.split(":"); value = (typ, rename[name])
                    out.append((s.kind, value, rename.get(s.loop_index), tuple(ex(e) for e in s.expressions), walk(s.children, here)))
            return tuple(out)
        return walk(program.statements)
    require(equal(normalize(c, "contract", cn), normalize(p, "source", pn)), "ORDINARY_SCAFFOLD_STATE_OUTPUT_MISMATCH")
    for a, b in table.items():
        ca, sa = c.item(a), p.item(b)
        require(ca.semantic_identity() == sa.semantic_identity(), "ORDINARY_TYPE_ROLE_MISMATCH")
        if ca.kind == "NODE":
            cv = (ca.value.split(":")[0], cn[ca.value.split(":")[1]]) if ca.operation == "INITIALIZE" else cn.get(ca.value, ca.value)
            sv = (sa.value.split(":")[0], pn[sa.value.split(":")[1]]) if sa.operation == "INITIALIZE" else pn.get(sa.value, sa.value)
            require(cv == sv, "ORDINARY_BINDING_VALUE_MISMATCH")
            require((table.get(ca.parent) == sa.parent) if ca.parent in table else ca.parent == sa.parent, "ORDINARY_PARENT_MISMATCH")
            if ca.target: require(table.get(ca.target) == sa.target, "ORDINARY_MACRO_TARGET_MISMATCH")
        else:
            require(table.get(ca.source) == sa.source and table.get(ca.target) == sa.target and ca.port == sa.port, "ORDINARY_EDGE_PORT_ENDPOINT_MISMATCH")
    # Dependency nodes/edges are validated, including exact roots and each
    # region reference, independently of the constructor's graph builder.
    dag = cert["proof_dependency_graph"]
    node_ids = [n["id"] for n in dag["nodes"]]
    roots = {"parsed_typed_source", "frozen_metadata", "primitive_recognition", "reaching_definitions"}
    require(len(node_ids) == len(set(node_ids)) and set(node_ids) == roots | set(ids) | {"total_v32", "indicator_evidence"}, "DAG_NODE_OR_REGION_REFERENCE_MISMATCH")
    edges = [tuple(x) for x in dag["edges"]]
    require(len(edges) == len(set(edges)) and all(a in node_ids and b in node_ids for a, b in edges), "DAG_EDGE_REFERENCE_MISMATCH")
    successors = {n: [] for n in node_ids}; incoming = Counter(b for a, b in edges)
    for a, b in edges: successors[a].append(b)
    ready = [n for n in node_ids if not incoming[n]]; visited = []
    while ready:
        n = ready.pop(); visited.append(n)
        for b in successors[n]:
            incoming[b] -= 1
            if incoming[b] == 0: ready.append(b)
    require(len(visited) == len(node_ids), "CYCLIC_PROOF_DEPENDENCY")
    expected = {( "parsed_typed_source", "primitive_recognition"), ("parsed_typed_source", "reaching_definitions"), ("frozen_metadata", "primitive_recognition"), ("parsed_typed_source", "total_v32"), ("total_v32", "indicator_evidence")}
    expected |= {(root, rid) for root in roots for rid in ids} | {(rid, "total_v32") for rid in ids}
    require(set(edges) == expected, "DAG_REQUIRED_FOUNDATION_MISSING")
    kinds = {n["id"]: n["kind"] for n in dag["nodes"]}
    require(all(kinds[r] == "ROOT" for r in roots) and all(kinds[r] == "LOCAL_V33_REGION" for r in ids) and kinds["total_v32"] == "TOTAL_MAPPING" and kinds["indicator_evidence"] == "DERIVED_EVIDENCE", "DAG_KIND_MUTATION")
    return {"finding": "VERIFIED_TOTAL", "partition": partition, "region_ids": ids, "dependency_order": visited,
        "boundary_verification": "reconstructed exact typed ports, closed truth/01 kernels, identical outside syntax/state/output scaffold",
        "constructor_invoked": False}


def extract_indicator_evidence(cert):
    check = check_serialized_mapping(cert)
    program = compile_program(cert["source_inventory"]["program_id"], cert["source_inventory"]["source"])
    records = []
    seen = set()
    for r in cert["regions"]:
        for flow in r["local_v33_proof"]["preconditions_and_flow_proofs"]:
            proof = program.indicator_proofs.get(flow["range_proof"]["binding"])
            if proof is None or not equal(proof, flow["range_proof"]): continue  # contract-side evidence separately bound
            read = flow["indicator_read"]
            require(read in r["source"]["nodes"], "INDICATOR_READ_OUTSIDE_REGION")
            require(equal(program.state_analysis["read_definitions"][read], flow["current_iteration_reaching_definitions"]), "INDICATOR_REACHING_MISMATCH")
            if read in seen: continue
            seen.add(read)
            records.append({"region_id": r["region_id"], "source_indicator_read": read, "range_and_write_proof": proof,
                "reaching_definitions": flow["current_iteration_reaching_definitions"], "predicate": proof["predicate_definitions"][0]["predicate_occurrence"]})
    require(records, "NO_SOURCE_INDICATOR_EVIDENCE")
    return {"finding": "DERIVED_AFTER_VERIFIED_TOTAL", "records": records, "dependency_order": check["dependency_order"]}
