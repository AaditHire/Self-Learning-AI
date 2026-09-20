from __future__ import annotations

import argparse
import json
from pathlib import Path

from self_learning_ai.compiler import GocoCompiler


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--jar", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    compiler = GocoCompiler(args.java, args.jar, timeout_seconds=5)
    tests = json.loads(args.manifest.read_text(encoding="utf-8"))
    results = []
    for test in tests:
        result = compiler.run(test["code"], test.get("stdin") or "")
        actual = normalize(result.stdout + result.stderr)
        expected = normalize(test["output"])
        passed = result.exit_code == test["output_code"] and actual == expected
        results.append(
            {
                "path": test["path"],
                "expected_exit_code": test["output_code"],
                "actual_exit_code": result.exit_code,
                "expected_output": expected,
                "actual_output": actual,
                "phase": result.phase,
                "elapsed_ms": result.elapsed_ms,
                "timed_out": result.timed_out,
                "output_limited": result.output_limited,
                "passed": passed,
            }
        )
    success = [r for r, t in zip(results, tests, strict=True) if t["output_code"] == 0]
    failure = [r for r, t in zip(results, tests, strict=True) if t["output_code"] != 0]
    summary = {
        "total": len(results),
        "passed": sum(r["passed"] for r in results),
        "mismatches": sum(not r["passed"] for r in results),
        "expected_success_passed": sum(r["passed"] for r in success),
        "expected_success_total": len(success),
        "expected_failure_passed": sum(r["passed"] for r in failure),
        "expected_failure_total": len(failure),
        "timeouts": sum(r["timed_out"] for r in results),
        "output_limit_terminations": sum(r["output_limited"] for r in results),
        "system_crashes": sum(r["phase"] == "system" for r in results),
    }
    payload = {"summary": summary, "results": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    raise SystemExit(0 if summary["mismatches"] == 0 else 1)


if __name__ == "__main__":
    main()
