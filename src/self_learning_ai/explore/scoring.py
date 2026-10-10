"""Minimal compiler reward for EXPLORATORY programs."""
from __future__ import annotations

import errno
import json
import time
from pathlib import Path

from self_learning_ai.benchmark import extract_source
from self_learning_ai.compiler import GocoCompiler, normalized_program_output

ROOT = Path(__file__).resolve().parents[3]


def make_compiler():
    cfg = json.loads((ROOT / "research/protocols/phase3c_conf1_config_proposed.json").read_bytes())
    return GocoCompiler(ROOT / cfg["compiler"]["java"], ROOT / cfg["compiler"]["path"],
                        timeout_seconds=cfg["evaluation"]["compiler_timeout_seconds"],
                        output_limit_bytes=cfg["evaluation"]["output_limit_bytes_per_stream"])


def run_with_retries(compiler, source, stdin):
    """CONF1 EINVAL/system policy: at most two re-invocations."""
    for number in range(1, 4):
        if number > 1:
            time.sleep(2 if number == 2 else 10)
        try:
            result = compiler.run(source, stdin)
        except OSError as exc:
            if exc.errno != errno.EINVAL or number == 3:
                raise
            continue
        if result.phase != "system":
            return result
    return result


def score_program(raw_generation, cases) -> dict:
    compiler = make_compiler()
    source = extract_source(raw_generation)
    passed, compiled, phase = 0, bool(cases), "success"
    for case in cases:
        result = run_with_retries(compiler, source, case["stdin"])
        compiled = compiled and result.phase in {"success", "runtime", "timeout", "output_limit"}
        if result.phase != "success":
            phase = result.phase
        passed += int(result.phase == "success" and
                      normalized_program_output(result.stdout) == case["expected_stdout"].strip())
    return dict(compiled=compiled, cases_passed=passed, cases_total=len(cases),
                all_pass=bool(cases) and passed == len(cases), phase=phase)
