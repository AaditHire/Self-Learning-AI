"""C11 secondary definitions and compiler E1; no candidate selection or writes."""

from __future__ import annotations

from functools import partial

from self_learning_ai.conf1_r1.gates_primary import CompilerRunner, GateStop, p2_e1
from self_learning_ai.conf1_r1.training import _authorities, _builder


def _tasks(group):
    ledger, _, _ = _authorities()
    builder = _builder()  # Definitions only; never call the historical main().
    source_fn, expected_fn = ((builder.sanity_source, builder.sanity_expected)
                              if group == "primitive_sanity" else
                              (builder.structural_source, builder.structural_expected))
    slots = ledger["slots"][group]
    if len(slots) != 16 or len({slot["task_id"] for slot in slots}) != 16:
        raise GateStop("secondary ledger population mismatch", {"group": group})
    return [{"task_id": slot["task_id"], "family": slot["family"], "group": group,
             "prompt": builder.task_prompt(slot), "source": source_fn(slot),
             "expected_fn": partial(expected_fn, dict(slot))} for slot in slots]


def sanity_tasks():
    """Return all 16 frozen sanity slots using the C11 historical definitions."""
    return _tasks("primitive_sanity")


def structural_tasks():
    """Return all 16 frozen structural slots using the C11 historical definitions."""
    return _tasks("structural_transfer")


def secondary_cases(task, domain_inputs):
    """Reuse the caller's five selected primary inputs of this task's domain."""
    try:
        inputs = list(domain_inputs[task["family"]])
    except KeyError as exc:
        raise GateStop("secondary task domain inputs unavailable") from exc
    if len(inputs) != 5 or len(set(inputs)) != 5 or any(not isinstance(x, str) for x in inputs):
        raise GateStop("secondary cases require five distinct domain input strings")
    return [{"case_id": f"{task['task_id']}-C{i + 1}", "stdin": stdin,
             "expected_stdout": str(task["expected_fn"](stdin))}
            for i, stdin in enumerate(inputs)]


def secondary_e1(tasks, domain_inputs, runner=CompilerRunner):
    """Apply only E1; failed fixed references exhaust their secondary candidates.

    Kept/dropped records retain the task definitions. The sanity flag concerns
    the supplied population at this stage; P7 drops must also be accounted for
    by the caller before reporting the final secondary population.
    """
    tasks = list(tasks)
    if len({task["task_id"] for task in tasks}) != len(tasks):
        raise GateStop("duplicate secondary task ID")
    if any(task["group"] not in ("primitive_sanity", "structural_transfer") for task in tasks):
        raise GateStop("E1 secondary population contains a non-secondary task")
    result = p2_e1([(task["task_id"], task["source"],
                     [(case["stdin"], int(case["expected_stdout"]))
                      for case in secondary_cases(task, domain_inputs)]) for task in tasks], runner=runner)
    by_id = {row["id"]: row for row in result["items"]}
    kept, dropped = [], []
    for task in tasks:
        row = by_id[task["task_id"]]
        if row["status"] == "PASS":
            kept.append(task)
        else:
            dropped.append({"task": task, "task_id": task["task_id"], "reason": "E1_FAIL_CANDIDATES_EXHAUSTED",
                            "failures": row["failures"]})
    sanity_count = sum(task["group"] == "primitive_sanity" for task in kept)
    return {"status": "PASS", "e1_status": result["status"], "kept": kept, "dropped": dropped, "items": result["items"],
            "sanity_count": sanity_count, "SANITY_NOT_EVALUABLE": sanity_count < 12,
            "runner_calls": result["runner_calls"]}
