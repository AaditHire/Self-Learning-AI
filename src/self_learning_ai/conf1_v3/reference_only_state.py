"""Frozen raw state-record adapter and separate feasible-state reconstruction.

The raw adapter uses the accepted independent epoch/fixed-point state kernel.
Feasible reconstruction traverses the original AST and excludes only specified
body events; callers must independently prove that exclusion under the catalog.
It never edits source, original AST/IR items, raw state, or inventory.
"""
from .goco import _walk_expr
from .interfaces import rid, SchemaError
from .reference_only_inventory import ref
from .state_semantics import analyze_state

RELATIONS = ("DATA", "SEQUENTIAL", "CONTROL", "MAY_REACHING", "LOOP_CARRY", "CROSS_PASS", "OUTPUT", "DECODER")


def _relations(p, graph, diagnostic):
    relations = set()
    def add(a, b, relation):
        relations.add((a, b, relation))
    for e in p.items:
        if e.kind != "EDGE" or e.operation == "PRIOR_STATE_TO_UPDATE":
            continue
        relation = ("CONTROL" if e.operation == "CONTROL_TO_UPDATE" else
                    "LOOP_CARRY" if e.operation == "LOOP_CARRY" else
                    "OUTPUT" if e.operation == "ACCUMULATOR_TO_OUTPUT" else
                    "DECODER" if e.operation == "INPUT_TO_DECODER" else "DATA")
        add(e.source, e.target, relation)
        # EDGE occurrences are executable operand/state/control observations in
        # the accepted runtime. Retain their event participation as raw analysis
        # relations, without adding ontology nodes/edges or changing identities.
        add(e.source, e.occurrence_id, relation)
        add(e.occurrence_id, e.target, relation)
    for context in graph["control_contexts"]:
        for ancestor in context["ancestors"]:
            add(ancestor["control_occurrence_id"], context["occurrence_id"], "CONTROL")
    for e in diagnostic["required_state_edges"]:
        add(e["writer"], e["reader"], "MAY_REACHING")
        if e["relation"] == "PRIOR_STATE":
            add(e["writer"], e["reader"], "LOOP_CARRY")
        elif e["relation"] == "PRESERVED_PASS_STATE":
            add(e["writer"], e["reader"], "CROSS_PASS")
    for kill in diagnostic["sequential_kills"]:
        for previous in kill["killed"]:
            add(previous["writer"], kill["writer"], "SEQUENTIAL")
    return relations


def ancestry(p, inventory, relations, targets):
    """Finite least-fixed-point ancestry with every semantic occurrence retained."""
    reached = set(targets)
    while True:
        new = {a for a, b, _ in relations if b in reached} - reached
        if not new:
            break
        reached.update(new)
    for item in p.items:
        if item.kind == "EDGE" and item.source in reached and item.target in reached:
            reached.add(item.occurrence_id)
    return [r["occurrence"]["occurrence_id"] for r in inventory["occurrences"] if r["occurrence"]["occurrence_id"] in reached]


def state_record(p, inventory, graph, *, direct_artifact_id):
    diagnostic = analyze_state(p)
    artifact = inventory["source_reference"]["artifact_id"]
    ordinal = {r["occurrence"]["occurrence_id"]: r["inventory_ordinal"] for r in inventory["occurrences"]}
    contexts = {r["occurrence_id"]: r["ancestors"] for r in graph["control_contexts"]}
    bindings = {r["identifier"]: r for r in inventory["bindings"]}
    def binding(name):
        return ref(artifact, bindings[name]["record_id"])
    definitions = [dict(record_id=rid("V32DEFINITION", [p.program_id, w["writer"]]),
                        writer_occurrence_id=w["writer"], binding_reference=binding(w["binding"]),
                        control_context=contexts[w["writer"]])
                   for w in sorted(diagnostic["writes"], key=lambda w: ordinal[w["writer"]])]
    definition_ids = {d["writer_occurrence_id"]: d["record_id"] for d in definitions}
    reads = []
    for read in sorted(diagnostic["reads"], key=lambda r: ordinal[r["reader"]]):
        writers = {e["writer"] for e in diagnostic["required_state_edges"] if e["reader"] == read["reader"]}
        reads.append(dict(read_occurrence_id=read["reader"], binding_reference=binding(read["binding"]),
                          writer_references=[ref(direct_artifact_id, definition_ids[w]) for w in sorted(writers, key=ordinal.get)]))
    relations = _relations(p, graph, diagnostic)
    dependency_edges = [dict(edge_id=rid("V32DEPENDENCY", [p.program_id, relation, a, b]),
                             source_occurrence_id=a, target_occurrence_id=b, relation=relation)
                        for a, b, relation in sorted(relations, key=lambda r: (ordinal[r[0]], ordinal[r[1]], RELATIONS.index(r[2])))]
    decoders = [i.occurrence_id for i in p.items if i.kind == "NODE" and i.category == "API_DECODER"]
    state = dict(schema_version=1, record_id=rid("V32STATE", [p.program_id]), program_id=p.program_id,
                 graph_reference=ref(direct_artifact_id, graph["record_id"]), definitions=definitions, read_definitions=reads,
                 dependency_edges=dependency_edges, output_ancestry=ancestry(p, inventory, relations, [p.output_id]),
                 decoder_ancestry=ancestry(p, inventory, relations, decoders), analysis_status="CLOSED")
    return state, diagnostic


def feasible_reaching(p, diagnostic, excluded):
    """Recompute structured kill/union/loop fixed points after event exclusions.

    Exclusions are a separate proof view, not deletions from raw records. This
    helper alone grants no exclusion permission and creates no RO certificate.
    Epochs and all surviving joins/backedges are recomputed, never just filtered.
    """
    writers = {r["writer"]: r for r in diagnostic["writes"]}
    reached = {r["reader"]: set() for r in diagnostic["reads"] if r["reader"] not in excluded}
    killed = set()
    fixed_points = []
    def join(a, b):
        return {n: set(a.get(n, ())) | set(b.get(n, ())) for n in set(a) | set(b)}
    def expression(e, env):
        for node in _walk_expr(e):
            oid = p.node_ids.get(id(node))
            if node.kind == "ID" and node.value in p.symbols and oid in reached:
                reached[oid].update(env.get(node.value, ()))
    def transfer(rows, incoming, loop=None):
        env = {n: set(values) for n, values in incoming.items()}
        for s in rows:
            if s.kind == "IMPORT":
                continue
            oid = p.node_ids[id(s)]
            if oid in excluded:
                continue
            if s.kind == "LOOP":
                pre = {n: set(values) for n, values in env.items()}
                if s.value == "FORWARD":
                    expression(s.expressions[0], pre)
                    pre[s.loop_index] = {(p.index_nodes[oid][0], "BEFORE_LOOP")}
                header = pre
                for iteration in range(2 * len(writers) + 2):
                    expression(s.expressions[-1], header)
                    after = transfer(s.children, header, oid)
                    if s.value == "FORWARD":
                        step = p.index_nodes[oid][1]
                        reached[step].update(after.get(s.loop_index, ()))
                        after[s.loop_index] = {(step, "CURRENT_ITERATION")}
                    back = {n: {(w, "PREVIOUS_ITERATION" if writers[w]["loop"] == oid and epoch == "CURRENT_ITERATION" else epoch)
                                for w, epoch in values} for n, values in after.items()}
                    newer = join(pre, back)
                    if newer == header:
                        break
                    header = newer
                else:
                    raise SchemaError("RO_FEASIBLE_STATE_FIXED_POINT_UNRESOLVED")
                fixed_points.append(dict(loop=oid, iterations=iteration + 1,
                                         header={n: sorted(v) for n, v in header.items()}))
                env = {n: {(w, "PASS_FINAL" if writers[w]["loop"] == oid else epoch) for w, epoch in values}
                       for n, values in header.items()}
            elif s.kind == "IF":
                expression(s.expressions[0], env)
                env = join(env, transfer(s.children, env, loop))
            else:
                roots = s.expressions[1:] if s.kind == "UPDATE" else () if s.kind == "INPUT" else s.expressions
                for root in roots:
                    expression(root, env)
                if oid in writers:
                    name = writers[oid]["binding"]
                    if oid in reached:
                        reached[oid].update(env.get(name, ()))
                    killed.update((w, oid) for w, epoch in env.get(name, ()))
                    env[name] = {(oid, "CURRENT_ITERATION" if loop else "INITIAL_OR_SEQUENTIAL")}
        return env
    transfer(p.statements, {})
    if any(not values for values in reached.values()):
        raise SchemaError("RO_FEASIBLE_STATE_READ_UNRESOLVED")
    relations = {(w, reader, "MAY_REACHING") for reader, values in reached.items() for w, epoch in values}
    for reader, values in reached.items():
        read = next(r for r in diagnostic["reads"] if r["reader"] == reader)
        for w, epoch in values:
            if epoch == "PREVIOUS_ITERATION" and writers[w]["loop"] == read["loop"]:
                relations.add((w, reader, "LOOP_CARRY"))
            elif epoch == "PASS_FINAL":
                relations.add((w, reader, "CROSS_PASS"))
    relations.update((a, b, "SEQUENTIAL") for a, b in killed)
    return reached, relations, fixed_points
