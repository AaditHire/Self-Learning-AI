"""Synthetic regression and fault-injection tests; no model execution."""
from __future__ import annotations

import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from self_learning_ai.benchmark import score_source
from self_learning_ai.dev2r_evaluation import (
    evaluate_task, reject_existing_attempt, require_authorization,
    summarize_own_training, validate_task,
)


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

    def test_authorization_truth_table_is_strict_boolean(self):
        base = {"status": "FROZEN_PRE_EXECUTION"}
        for value in (False, None, "false", 0, 1, [], {}, "true"):
            with self.subTest(value=value), self.assertRaisesRegex(RuntimeError, "not explicitly authorized"):
                require_authorization({**base, "model_execution_authorized": value})
        with self.assertRaisesRegex(RuntimeError, "not explicitly authorized"):
            require_authorization(base)
        with self.assertRaisesRegex(RuntimeError, "not explicitly authorized"):
            require_authorization({"status": "wrong", "model_execution_authorized": True})
        require_authorization({**base, "model_execution_authorized": True})

    def test_authorization_blocks_model_adapter_generation_and_compiler_spies(self):
        calls = {name: 0 for name in ("model_load", "adapter_load", "generate", "compiler")}
        def downstream():
            for name in calls: calls[name] += 1
        for invalid in (False, None, "false", 0):
            with self.assertRaises(RuntimeError):
                require_authorization({"status": "FROZEN_PRE_EXECUTION",
                                       "model_execution_authorized": invalid})
                downstream()
        self.assertEqual(calls, {name: 0 for name in calls})
        require_authorization({"status": "FROZEN_PRE_EXECUTION",
                               "model_execution_authorized": True})
        downstream()
        self.assertEqual(calls, {name: 1 for name in calls})

    def test_real_manifest_remains_unauthorized(self):
        manifest = json.loads((Path(__file__).resolve().parents[1] /
            "research/protocols/phase3c_dev2r_v2_manifest.json").read_text())
        with self.assertRaisesRegex(RuntimeError, "not explicitly authorized"):
            require_authorization(manifest)

    def test_exact_target_reproduction_precedes_optional_reporting(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            def broken(_): raise RuntimeError("report failed")
            with self.assertRaisesRegex(RuntimeError, "report failed"):
                evaluate_task(compiler=Compiler(), task=self.task, cases=self.cases,
                    raw_generation="```goco\nDISPLAYNL(1).\n```", generation_metadata={},
                    adapter_identity={"seed": 1}, checkpoint_dir=folder,
                    target_source="DISPLAYNL(1).", reporter=broken)
            primary = json.loads((folder / "SYNTHETIC-01.primary.json").read_text())
            self.assertTrue(primary["exact_target_reproduction"])
            self.assertEqual(primary["score"]["cases_passed"], 5)
            self.assertEqual(len(primary["score"]["case_results"]), 5)

    def test_own_training_summary_and_duplicate_attempt_guard(self):
        rows = [{"task_id": f"synthetic-{i}",
                 "family": "numeric_iteration" if i < 30 else "array_reduction",
                 "archetype": "a" if i % 2 else "b", "hidden_pass": i % 3 != 0,
                 "exact_target_reproduction": i % 4 == 0,
                 "failure_category": "success" if i % 3 != 0 else "hidden_test_semantic"}
                for i in range(60)]
        summary = summarize_own_training(rows)
        self.assertEqual(summary["overall"]["total"], 60)
        self.assertEqual(summary["overall"]["passed"], 40)
        self.assertEqual(summary["overall"]["exact_target_reproduction"], 15)
        self.assertEqual(summary["by_family"]["numeric_iteration"]["total"], 30)
        self.assertEqual(summary["by_family"]["array_reduction"]["total"], 30)
        self.assertEqual(set(summary["by_archetype"]), {"a", "b"})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "attempt"
            reject_existing_attempt(root)
            root.mkdir()
            (root / "valid.primary.json").write_text("{}")
            with self.assertRaises(FileExistsError): reject_existing_attempt(root)

    def test_versioned_suite_schema_and_frozen_scientific_gates(self):
        root = Path(__file__).resolve().parents[1]
        folder = root / "benchmark/phase3c_dev2r_v2"
        tasks = json.loads((folder / "a_development_eval_tasks.json").read_text())
        refs = json.loads((folder / "a_development_eval_references.json").read_text())
        cases = json.loads((folder / "a_development_eval_hidden_tests.json").read_text())
        audit = json.loads((root / "research/results/PHASE_3C_DEV2R_AMENDMENT/v2_pre_execution_audit.json").read_text())
        self.assertEqual(len(tasks), 48)
        self.assertEqual(set(refs), set(cases))
        self.assertEqual(set(refs), {task["task_id"] for task in tasks})
        self.assertEqual(audit["final_gate"], {
            "primitive_sanity_task_essential": "16/16",
            "novel_composition_primitive": "16/16",
            "novel_composition_signature_absence": "16/16",
            "structural_transfer_primitive_and_task_essential": "16/16"})
        for task in tasks:
            validate_task(task, cases[task["task_id"]])
        sanity = [task for task in tasks if task["development_group"] == "primitive_sanity"]
        self.assertEqual(len(sanity), 16)
        self.assertTrue(all("-1" not in task["prompt"] for task in sanity))
        self.assertTrue(all("=-1." not in refs[task["task_id"]] for task in sanity))

    def test_versioned_manifest_portable_hashes(self):
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / "research/protocols/phase3c_dev2r_v2_manifest.json").read_text())
        self.assertIs(manifest["model_execution_authorized"], False)
        self.assertEqual(len(manifest["input_sha256"]), 43)
        for relative, expected in manifest["input_sha256"].items():
            path = root / relative
            payload = path.read_bytes()
            if path.suffix.lower() in {".json", ".md", ".py", ".txt", ".jinja"}:
                payload = payload.replace(b"\r\n", b"\n")
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected, relative)


if __name__ == "__main__": unittest.main()
