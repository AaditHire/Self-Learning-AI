"""Lossless frozen source inventory adapter; no disposition or outcome input.

Existing IDs/UTF8 offsets are retained. Numeric parser destination ports are
retained exactly (including zero); their decimal UTF8 spelling is used ONLY as
the deterministic sorting key, never substituted for the bound identity.
Ordinary GROUP/INPUT-LHS/UPDATE-LHS aliases stay presentation associations.
"""
from .core_ir import compile_program
from .goco import Expr, Stmt, _walk_expr, _walk_stmt, lex
from .interfaces import rid, canonical_json_bytes, SchemaError


def ref(artifact_id, record_id, role="SCIENTIFIC_EVIDENCE", content=None):
    from hashlib import sha256
    raw = content.encode("utf-8") if content is not None else None
    return dict(artifact_id=artifact_id, record_id=record_id, record_role=role,
                content_sha256_utf8=sha256(raw).hexdigest() if raw is not None else None,
                content_size_bytes_utf8=len(raw) if raw is not None else None)


def interval(start, end):
    return dict(start=start, end=end)


def source_inventory(program_id, source, source_reference, *, training):
    if type(training) is not bool:
        raise SchemaError("RO_INVENTORY_TRAINING_TYPE")
    p = compile_program(program_id, source)
    nodes, seen, contexts, associations, expression_children = [], set(), {}, [], {}
    loop_ordinal = {p.node_ids[id(s)]: i + 1 for i, s in enumerate(
        s for top in p.statements for s in _walk_stmt(top) if isinstance(s, Stmt) and s.kind == "LOOP")}
    def node(oid, ancestors):
        if oid is not None and oid not in seen:
            seen.add(oid); nodes.append(oid); contexts[oid] = list(ancestors)
    def expression(e, ancestors):
        oid = p.node_ids.get(id(e))
        node(oid, ancestors)
        if e.kind in {"GROUP", "ID"} and oid is not None:
            associations.append(dict(source_location=interval(e.start, e.end), raw_utf8_extent=interval(e.start, e.end), semantic_owner_ids=[oid]))
        if e.kind == "GROUP":
            expression(e.children[0], ancestors)
            return
        children = e.children[1:] if e.kind == "CALL" else e.children
        if oid is not None:
            expression_children[oid] = [p.node_ids[id(c)] for c in children if id(c) in p.node_ids]
            if oid in p.primitive_aliases:
                alias = p.primitive_aliases[oid]
                node(alias, ancestors)
                expression_children[alias] = expression_children[oid][:]
        for c in children:
            expression(c, ancestors)
    def block(rows, ancestors=()):
        for s in rows:
            if s.kind == "IMPORT":
                continue
            oid = p.node_ids[id(s)]; node(oid, ancestors)
            child_context = ancestors
            if s.kind in {"IF", "LOOP"}:
                child_context = (*ancestors, dict(control_occurrence_id=oid, control_kind=s.kind,
                    parent_control_occurrence_id=ancestors[-1]["control_occurrence_id"] if ancestors else None,
                    source_location=interval(s.start, s.end), pass_ordinal=loop_ordinal.get(oid)))
            if s.kind == "INPUT":
                node(p.macro_id, ancestors)
            if oid in p.index_nodes:
                node(p.index_nodes[oid][0], child_context)
            roots = s.expressions[1:] if s.kind == "UPDATE" else () if s.kind == "INPUT" else s.expressions
            expression_children[oid] = [p.node_ids[id(e)] for e in roots]
            for e in roots:
                expression(e, ancestors)
            # The aliased binding lexeme remains represented, not a self-child.
            if s.kind in {"INPUT", "UPDATE"}:
                e = s.expressions[0]
                associations.append(dict(source_location=interval(e.start, e.end), raw_utf8_extent=interval(e.start, e.end), semantic_owner_ids=[oid]))
            block(s.children, child_context)
            if oid in p.index_nodes:
                node(p.index_nodes[oid][1], child_context)
    block(p.statements)
    original_nodes = {i.occurrence_id for i in p.items if i.kind == "NODE"}
    if seen != original_nodes:
        raise SchemaError("RO_UNPLACED_SEMANTIC_NODE")
    order = {oid: i for i, oid in enumerate(nodes)}
    edges = [i for i in p.items if i.kind == "EDGE"]
    edges.sort(key=lambda e: (order[e.source], order[e.target], e.operation.encode("utf-8"),
                             str(e.port).encode("utf-8"), *e.location))
    combined = [p.item(oid) for oid in nodes] + edges
    ordinal = {item.occurrence_id: i for i, item in enumerate(combined, 1)}
    binding_meta, occurrence_bindings = {}, {}
    def bind(oid, name, action):
        binding_meta[name][action].add(oid)
        occurrence_bindings.setdefault(oid, set()).add(name)
    def bindings(rows):
        for s in rows:
            if s.kind == "IMPORT":
                continue
            oid = p.node_ids[id(s)]
            if s.kind == "DECLARE":
                name = s.value.split(":")[1]
                binding_meta[name] = dict(declaration=oid, reads=set(), writes=set())
                bind(oid, name, "writes")
                # Declaration identifier spelling is also a presentation fact.
                token = next(t for t in lex(p.source) if s.start <= t.start < s.end and t.kind == "ID" and t.text == name)
                associations.append(dict(source_location=interval(token.start, token.end), raw_utf8_extent=interval(token.start, token.end), semantic_owner_ids=[oid]))
            if s.kind == "LOOP" and s.value == "FORWARD":
                initial, step = p.index_nodes[oid]
                binding_meta[s.loop_index] = dict(declaration=initial, reads=set(), writes=set())
                bind(initial, s.loop_index, "writes"); bind(step, s.loop_index, "writes"); bind(step, s.loop_index, "reads")
            if s.kind in {"UPDATE", "INPUT"}:
                name = s.expressions[0].value
                bind(oid, name, "writes")
                if s.kind == "UPDATE" and s.value != "=":
                    bind(oid, name, "reads")
            roots = s.expressions[1:] if s.kind == "UPDATE" else () if s.kind == "INPUT" else s.expressions
            for root in roots:
                for e in _walk_expr(root):
                    if e.kind == "ID" and e.value in p.symbols and id(e) in p.node_ids:
                        bind(p.node_ids[id(e)], e.value, "reads")
            bindings(s.children)
    bindings(p.statements)
    artifact = source_reference["artifact_id"]
    binding_rows, refs = [], {}
    for name, meta in binding_meta.items():
        bid = rid("V32BINDING", [program_id, meta["declaration"]])
        refs[name] = ref(artifact, bid)
        binding_rows.append(dict(record_id=bid, binding_id=bid, declaration_occurrence_id=meta["declaration"],
                                 identifier=name, datatype=p.symbols[name],
                                 read_occurrence_ids=sorted(meta["reads"], key=ordinal.get),
                                 write_occurrence_ids=sorted(meta["writes"], key=ordinal.get)))
    binding_rows.sort(key=lambda r: ordinal[r["declaration_occurrence_id"]])
    binding_order = {r["identifier"]: i for i, r in enumerate(binding_rows)}
    occurrences = []
    for i, item in enumerate(combined, 1):
        names = occurrence_bindings.get(item.occurrence_id, set())
        if item.kind == "EDGE":
            names = occurrence_bindings.get(item.source, set()) | occurrence_bindings.get(item.target, set())
            contexts[item.occurrence_id] = list(contexts[item.target])
        occurrence = dict(occurrence_id=item.occurrence_id, kind=item.kind,
            source_location=interval(*item.location), raw_utf8_extent=interval(*item.location),
            graph_location=item.occurrence_id, operation=item.operation, result_type=item.datatype,
            operand_types=list(item.operand_types), operand_roles=list(item.operand_roles), result_role=item.result_role,
            binding_references=[refs[n] for n in sorted(names, key=binding_order.get)],
            source_endpoint_id=item.source if item.kind == "EDGE" else None,
            target_endpoint_id=item.target if item.kind == "EDGE" else None,
            port=item.port if item.kind == "EDGE" else None)
        occurrences.append(dict(record_id=rid("V32OCCRECORD", [program_id, item.occurrence_id]), inventory_ordinal=i, occurrence=occurrence))
    associations.sort(key=lambda a: (a["raw_utf8_extent"]["start"], a["raw_utf8_extent"]["end"]))
    inventory = dict(schema_version=1, record_id=rid("V32INVENTORY", [program_id]), program_id=program_id,
                     source_reference=source_reference,
                     coordinate_convention=dict(source_unit="UTF8_BYTE", source_origin=0, graph_unit="OCCURRENCE_ID"),
                     occurrences=occurrences, bindings=binding_rows, presentation_associations=associations,
                     eligible_v3_5_occurrence_ids=[item.occurrence_id for item in combined] if training else [])
    graph = dict(schema_version=1, record_id=rid("V32GRAPH", [program_id]), program_id=program_id,
                 source_inventory_reference=ref(artifact, inventory["record_id"]), node_ids=nodes,
                 edge_ids=[item.occurrence_id for item in edges],
                 expression_children=[dict(parent_occurrence_id=oid, ordered_child_occurrence_ids=expression_children[oid])
                                      for oid in nodes if oid in expression_children],
                 control_contexts=[dict(occurrence_id=item.occurrence_id, ancestors=contexts[item.occurrence_id]) for item in combined])
    return p, inventory, graph
