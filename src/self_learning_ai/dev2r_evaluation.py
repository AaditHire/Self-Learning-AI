"""Prospective DEV2R schema and crash-recoverable per-task scoring."""
from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Callable

from .benchmark import extract_source_phase1r, score_source


def validate_task(task: dict[str, Any], cases: list[dict[str, str]]) -> dict[str, Any]:
    required = ("task_id", "family", "prompt", "development_group", "archetype",
                "semantic_primitives", "composition_signature")
    if not isinstance(task, dict) or any(not task.get(key) for key in required):
        raise ValueError(f"DEV2R task missing required field: {[k for k in required if not task.get(k)]}")
    if not isinstance(task.get("required_regex", []), list) or any(
            not isinstance(x, str) for x in task.get("required_regex", [])):
        raise ValueError("required_regex must be a list of strings")
    if not isinstance(cases, list) or len(cases) != 5 or any(
            not all(isinstance(case.get(k), str) for k in ("case_id", "stdin", "expected_stdout"))
            for case in cases):
        raise ValueError("DEV2R requires five well-formed semantic cases")
    if len({case["case_id"] for case in cases}) != 5:
        raise ValueError("Duplicate semantic case ID")
    for pattern in task.get("required_regex", []):
        try: re.compile(pattern)
        except re.error as exc: raise ValueError(f"Invalid required_regex: {pattern}") from exc
    return {**task, "difficulty": task.get("difficulty") or "phase3c_dev2r_development"}


def atomic_new_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): raise FileExistsError(path)
    temp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        with temp.open("x", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
        if path.exists(): raise FileExistsError(path)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def evaluate_task(*, compiler: Any, task: dict[str, Any], cases: list[dict[str, str]],
                  raw_generation: str, generation_metadata: dict[str, Any],
                  adapter_identity: dict[str, Any], checkpoint_dir: Path,
                  reporter: Callable[[dict[str, Any]], Any] | None = None) -> dict[str, Any]:
    scored_task = validate_task(task, cases)
    if not isinstance(raw_generation, str) or not isinstance(generation_metadata, dict) or not adapter_identity:
        raise ValueError("Malformed generation or adapter identity")
    tid = task["task_id"]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", tid): raise ValueError("Unsafe task ID")
    stem = checkpoint_dir / tid
    generation = {"status": "GENERATION_DURABLE", "task_id": tid, "task_metadata": task,
                  "adapter_identity": adapter_identity, "raw_generation": raw_generation,
                  "generation_metadata": generation_metadata}
    atomic_new_json(stem.with_suffix(".generation.json"), generation)
    normalized = extract_source_phase1r(raw_generation)
    score = score_source(compiler, scored_task, cases, normalized).as_dict()
    primary = {**generation, "status": "PRIMARY_SCORE_DURABLE", "normalized_output": normalized,
               "score": score}
    atomic_new_json(stem.with_suffix(".primary.json"), primary)
    if reporter is not None: reporter(primary)
    return primary
