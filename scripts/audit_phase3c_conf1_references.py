"""Validate CONF1 canonical programs on every frozen case; no model use."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from self_learning_ai.compiler import GocoCompiler, normalized_program_output  # noqa: E402

OUT = ROOT / "research/results/PHASE_3C_CONF1_PREFREEZE/reference_validation.json"
SETS = {
    "isolated": ROOT / "data/phase3c_conf1",
    "composition": ROOT / "data/phase3c_conf1",
    "evaluation": ROOT / "benchmark/phase3c_conf1",
}


def read(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    jar = ROOT / ".artifacts/compiler/goco-compiler-6a029b8-deterministic.jar"
    java = ROOT / ".tools/jdk-25.0.1+8/bin/java.exe"
    expected_hash = "42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb"
    if sha(jar) != expected_hash:
        raise ValueError("compiler hash mismatch")
    compiler = GocoCompiler(java, jar, timeout_seconds=3, output_limit_bytes=65536)
    report = {"status": "NON_MODEL_REFERENCE_VALIDATION", "compiler_sha256": expected_hash,
              "sets": {}, "all_pass": True}
    for name, folder in SETS.items():
        if name == "evaluation":
            rows = read(folder / "tasks.json")
            refs = read(folder / "references.json")
            cases = read(folder / "hidden_cases.json")
            key = "task_id"
        else:
            rows = read(folder / f"{name}_examples.json")
            refs = read(folder / f"{name}_references.json")
            cases = read(folder / f"{name}_cases.json")
            key = "example_id"
        assert len(rows) == len(refs) == len(cases)
        outcomes = []
        for row in rows:
            ident = row[key]
            per_case = []
            for c in cases[ident]:
                result = compiler.run(refs[ident], c["stdin"])
                actual = normalized_program_output(result.stdout)
                passed = result.phase == "success" and actual == c["expected_stdout"]
                per_case.append({"case_id": c["case_id"], "phase": result.phase,
                                 "actual": actual, "expected": c["expected_stdout"],
                                 "pass": passed, "stderr": result.stderr[:1000]})
            outcomes.append({"id": ident, "all_five_pass": all(x["pass"] for x in per_case),
                             "cases": per_case})
        summary = {"references": len(outcomes), "cases": sum(len(x["cases"]) for x in outcomes),
                   "passing_references": sum(x["all_five_pass"] for x in outcomes),
                   "passing_cases": sum(c["pass"] for x in outcomes for c in x["cases"]),
                   "outcomes": outcomes}
        report["sets"][name] = summary
        report["all_pass"] &= summary["passing_references"] == summary["references"]
        print(name, summary["passing_references"], "/", summary["references"], flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["all_pass"]:
        raise ValueError("STOP_PREFREEZE_DESIGN_FAILURE: canonical reference or semantic case failed")


if __name__ == "__main__":
    main()
