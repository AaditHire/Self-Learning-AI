"""Synthetic regression and fault-injection tests; no model execution."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from self_learning_ai.benchmark import score_source
from self_learning_ai.dev2r_evaluation import evaluate_task, validate_task


class Result:
    phase = "success"
    exit_code = 0
    stdout = "1\n"
    stderr = ""
    elapsed_ms = 1


class Compiler:
    def __init__(self): self.calls = 0
    def run(self, source, stdin):
        self.calls += 1
        return Result()


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.task = {"task_id": "SYNTHETIC-01", "family": "synthetic", "prompt": "Print 1",
                     "development_group": "primitive_sanity", "archetype": "synthetic",
                     "semantic_primitives": ["synthetic"], "composition_signature": "synthetic",
                     "required_regex": []}
        self.cases = [{"case_id": f"case-{i}", "stdin": "x\n", "expected_stdout": "1"}
                      for i in range(1, 6)]

    def test_reproduces_original_metadata_failure(self):
        compiler = Compiler()
        with self.assertRaisesRegex(KeyError, "difficulty"):
            score_source(compiler, self.task, self.cases, "DISPLAYNL(1).")
        self.assertEqual(compiler.calls, 5)

    def test_repair_scores_preserves_original_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            row = evaluate_task(compiler=Compiler(), task=self.task, cases=self.cases,
                raw_generation="DISPLAYNL(1).", generation_metadata={"tokens": 4},
                adapter_identity={"seed": 1, "condition": "synthetic", "sha256": "fake"},
                checkpoint_dir=Path(directory))
            self.assertEqual(row["score"]["cases_passed"], 5)
            self.assertTrue(row["score"]["hidden_pass"])
            self.assertEqual(row["task_metadata"], self.task)
            self.assertEqual(row["score"]["difficulty"], "phase3c_dev2r_development")
            self.assertEqual(row["score"]["task_id"], self.task["task_id"])
            self.assertTrue((Path(directory) / "SYNTHETIC-01.primary.json").exists())

    def test_reporting_failure_keeps_primary_and_raw(self):
        def broken_reporter(_): raise RuntimeError("optional report failed")
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            with self.assertRaisesRegex(RuntimeError, "optional report"):
                evaluate_task(compiler=Compiler(), task=self.task, cases=self.cases,
                    raw_generation="DISPLAYNL(1).", generation_metadata={"tokens": 4},
                    adapter_identity={"seed": 1}, checkpoint_dir=folder,
                    reporter=broken_reporter)
            raw = json.loads((folder / "SYNTHETIC-01.generation.json").read_text())
            primary = json.loads((folder / "SYNTHETIC-01.primary.json").read_text())
            self.assertEqual(raw["raw_generation"], "DISPLAYNL(1).")
            self.assertEqual(primary["score"]["cases_total"], 5)
            self.assertEqual(len(primary["score"]["case_results"]), 5)
            with self.assertRaises(FileExistsError):
                evaluate_task(compiler=Compiler(), task=self.task, cases=self.cases,
                    raw_generation="changed", generation_metadata={}, adapter_identity={"seed": 1},
                    checkpoint_dir=folder)

    def test_bad_schema_fails_before_compiler_or_write(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for malformed in ({**self.task, "prompt": ""}, {**self.task, "required_regex": ["["]}):
                with self.assertRaises(ValueError):
                    evaluate_task(compiler=Compiler(), task=malformed, cases=self.cases,
                        raw_generation="x", generation_metadata={}, adapter_identity={"seed": 1},
                        checkpoint_dir=folder)
            self.assertFalse(list(folder.iterdir()))
            with self.assertRaises(ValueError): validate_task(self.task, self.cases[:4])

    def test_wrong_semantic_answer_is_a_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            cases = [dict(case, expected_stdout="2") for case in self.cases]
            row = evaluate_task(compiler=Compiler(), task=self.task, cases=cases,
                raw_generation="DISPLAYNL(1).", generation_metadata={}, adapter_identity={"seed": 1},
                checkpoint_dir=Path(directory))
            self.assertFalse(row["score"]["hidden_pass"])
            self.assertEqual(row["score"]["cases_passed"], 0)
            self.assertTrue(row["score"]["execution_success"])

    def test_scoring_failure_still_keeps_generation(self):
        class BrokenCompiler:
            def run(self, source, stdin): raise RuntimeError("compiler unavailable")
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            with self.assertRaisesRegex(RuntimeError, "compiler unavailable"):
                evaluate_task(compiler=BrokenCompiler(), task=self.task, cases=self.cases,
                    raw_generation="DISPLAYNL(1).", generation_metadata={"tokens": 3},
                    adapter_identity={"seed": 1}, checkpoint_dir=folder)
            self.assertEqual(json.loads((folder / "SYNTHETIC-01.generation.json").read_text())
                             ["raw_generation"], "DISPLAYNL(1).")
            self.assertFalse((folder / "SYNTHETIC-01.primary.json").exists())


if __name__ == "__main__": unittest.main()
