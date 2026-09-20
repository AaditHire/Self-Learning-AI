"""GOCO benchmark loading, scoring, and paired analysis."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import binomtest

from .compiler import GocoCompiler, normalized_program_output


@dataclass(frozen=True, slots=True)
class ScoreSummary:
    task_id: str
    family: str
    difficulty: str
    parse_success: bool
    compile_success: bool
    execution_success: bool
    hidden_pass: bool
    cases_passed: int
    cases_total: int
    error_phase: str | None
    structural_requirements_met: bool
    case_results: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "family": self.family,
            "difficulty": self.difficulty,
            "parse_success": self.parse_success,
            "compile_success": self.compile_success,
            "execution_success": self.execution_success,
            "hidden_pass": self.hidden_pass,
            "cases_passed": self.cases_passed,
            "cases_total": self.cases_total,
            "error_phase": self.error_phase,
            "structural_requirements_met": self.structural_requirements_met,
            "case_results": self.case_results,
        }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def extract_source(raw_generation: str) -> str:
    """Frozen mechanical extraction: first fenced block, otherwise all text."""

    text = raw_generation.strip()
    if "```" not in text:
        return text
    first = text.find("```")
    start = text.find("\n", first)
    if start < 0:
        return text
    end = text.find("```", start + 1)
    if end < 0:
        return text[start + 1 :].strip()
    return text[start + 1 : end].strip()


def extract_source_phase1r(raw_generation: str) -> str:
    """Phase 1R v1 normalization: extract only one complete fenced block."""

    text = raw_generation.strip()
    if text.count("```") != 2:
        return text
    first = text.find("```")
    content_start = text.find("\n", first + 3)
    closing = text.find("```", first + 3)
    if content_start < 0 or closing < content_start:
        return text
    return text[content_start + 1 : closing].strip()


def score_source(
    compiler: GocoCompiler,
    task: dict[str, Any],
    cases: list[dict[str, str]],
    source: str,
) -> ScoreSummary:
    case_results: list[dict[str, Any]] = []
    phases: list[str] = []
    structural_requirements_met = all(
        re.search(pattern, source, flags=re.IGNORECASE | re.MULTILINE) is not None
        for pattern in task.get("required_regex", [])
    )
    for case in cases:
        result = compiler.run(source, case["stdin"])
        actual = normalized_program_output(result.stdout)
        expected = case["expected_stdout"].replace("\r\n", "\n").strip()
        passed = result.phase == "success" and actual == expected
        phases.append(result.phase)
        case_results.append(
            {
                "case_id": case["case_id"],
                "phase": result.phase,
                "exit_code": result.exit_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "normalized_stdout": actual,
                "expected_stdout": expected,
                "elapsed_ms": result.elapsed_ms,
                "passed": passed,
            }
        )
    parse_success = all(p not in {"system", "lexical", "syntax"} for p in phases)
    compile_success = all(p not in {"system", "lexical", "syntax", "semantic"} for p in phases)
    execution_success = all(p == "success" for p in phases)
    passed_count = sum(bool(item["passed"]) for item in case_results)
    first_error = next((p for p in phases if p != "success"), None)
    if first_error is None and not structural_requirements_met:
        first_error = "structural_requirement"
    return ScoreSummary(
        task_id=task["task_id"],
        family=task["family"],
        difficulty=task["difficulty"],
        parse_success=parse_success,
        compile_success=compile_success,
        execution_success=execution_success,
        hidden_pass=passed_count == len(cases) and structural_requirements_met,
        cases_passed=passed_count,
        cases_total=len(cases),
        error_phase=first_error,
        structural_requirements_met=structural_requirements_met,
        case_results=case_results,
    )


def paired_comparison(
    baseline: list[dict[str, Any]],
    docs: list[dict[str, Any]],
    *,
    bootstrap_seed: int = 20260920,
    bootstrap_samples: int = 10_000,
) -> dict[str, Any]:
    a = {item["task_id"]: int(item["hidden_pass"]) for item in baseline}
    b = {item["task_id"]: int(item["hidden_pass"]) for item in docs}
    if a.keys() != b.keys():
        raise ValueError("Paired conditions do not contain identical task IDs")
    task_ids = sorted(a)
    av = np.array([a[item] for item in task_ids], dtype=float)
    bv = np.array([b[item] for item in task_ids], dtype=float)
    docs_only = int(np.sum((av == 0) & (bv == 1)))
    baseline_only = int(np.sum((av == 1) & (bv == 0)))
    discordant = docs_only + baseline_only
    p_value = 1.0 if discordant == 0 else float(
        binomtest(min(docs_only, baseline_only), discordant, 0.5).pvalue
    )
    rng = np.random.default_rng(bootstrap_seed)
    indices = rng.integers(0, len(task_ids), size=(bootstrap_samples, len(task_ids)))
    deltas = (bv[indices] - av[indices]).mean(axis=1)
    return {
        "n_tasks": len(task_ids),
        "baseline_pass_rate": float(av.mean()),
        "docs_pass_rate": float(bv.mean()),
        "paired_risk_difference": float((bv - av).mean()),
        "paired_bootstrap_95pct_ci": [
            float(np.quantile(deltas, 0.025)),
            float(np.quantile(deltas, 0.975)),
        ],
        "docs_only_passes": docs_only,
        "baseline_only_passes": baseline_only,
        "mcnemar_exact_two_sided_p": p_value,
        "bootstrap_seed": bootstrap_seed,
        "bootstrap_samples": bootstrap_samples,
    }
