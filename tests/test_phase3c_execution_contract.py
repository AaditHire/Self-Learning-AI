"""Synthetic contract tests only. No model import, inference, or gradients."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import phase3c_contract as c


class Phase3CContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = c.load_frozen(check_base=False)
        cls.items = c.load_items(cls.cfg)

    def test_frozen_schedule_and_training_only_replay(self):
        from audit_phase3c_train_eval_separation import audit
        self.assertEqual(audit()["status"], "PASS_pre_model_train_eval_separation")
        summary = c.validate_schedule(self.cfg, self.items)
        self.assertEqual(summary["slots_per_branch_seed"], 180)
        self.assertEqual(summary["optimizer_steps_per_branch_seed"], 24)
        self.assertEqual(summary["replay_slots_per_branch_seed"], 36)
        self.assertEqual(summary["evaluation_ids_in_schedule"], 0)
        a_ids = {x["example_id"] for x in self.items["a_train"]}
        for epochs in self.items["schedule"]["by_seed"].values():
            self.assertEqual(len({x for epoch in epochs for x in epoch["replayed_a_example_ids"]}), 36)
            self.assertTrue(all(set(epoch["replayed_a_example_ids"]) <= a_ids for epoch in epochs))

    def test_schedule_rejects_evaluation_item_and_extra_compute(self):
        corrupted = copy.deepcopy(self.items)
        epoch = corrupted["schedule"]["by_seed"][str(self.cfg["seeds"][0])][0]
        position = epoch["replaced_b_positions_zero_based"][0]
        epoch["replay_example_ids"][position] = self.items["a_eval"][0]["task_id"]
        with self.assertRaises(ValueError):
            c.validate_schedule(self.cfg, corrupted)
        corrupted = copy.deepcopy(self.items)
        corrupted["schedule"]["micro_batches_per_epoch"] = 61
        with self.assertRaises(ValueError):
            c.validate_schedule(self.cfg, corrupted)

    def test_every_seed_acquisition_gate_and_stop(self):
        tasks = self.items["a_eval"]
        outcomes = {seed: {x["task_id"]: True for x in tasks} for seed in self.cfg["seeds"]}
        self.assertTrue(c.a_eligibility(self.cfg, tasks, outcomes)["all_eligible"])
        seed = self.cfg["seeds"][1]
        for row in tasks[:9]:
            outcomes[seed][row["task_id"]] = False
        gate = c.a_eligibility(self.cfg, tasks, outcomes)
        self.assertFalse(gate["all_eligible"])
        self.assertEqual(gate["action"], "STOP_before_B_no_tuning")
        self.assertEqual(c.joint_decision(gate, None, None, None), "STOP_acquisition_ineligible")
        with self.assertRaises(ValueError):
            c.a_eligibility(self.cfg, tasks, {self.cfg["seeds"][0]: outcomes[self.cfg["seeds"][0]]})

    def test_retention_transitions_and_macro_seed_aggregation(self):
        tasks = self.items["a_eval"]
        by_archetype = {name: [x["task_id"] for x in tasks if x["archetype"] == name]
                        for name in sorted({x["archetype"] for x in tasks})}
        counts = (6, 7, 8)  # 24, 28, 32 acquired IDs; intentionally unequal denominators.
        pre, naive, replay = {}, {}, {}
        for seed, count in zip(self.cfg["seeds"], counts):
            acquired = {tid for ids in by_archetype.values() for tid in ids[:count]}
            pre[seed] = {x["task_id"]: x["task_id"] in acquired for x in tasks}
            naive[seed] = {x["task_id"]: False for x in tasks}
            passed_after = set(list(sorted(acquired))[:12]) if count == 6 else acquired if count == 7 else set()
            replay[seed] = {x["task_id"]: x["task_id"] in passed_after for x in tasks}
        self.assertTrue(c.a_eligibility(self.cfg, tasks, pre)["all_eligible"])
        effect = c.a_endpoints(self.cfg, tasks, pre, naive, replay)
        self.assertAlmostEqual(effect["mean_retention_difference_pp"], 50.0)
        pooled = 100 * (12 + 28) / (24 + 28 + 32)
        self.assertNotAlmostEqual(effect["mean_retention_difference_pp"], pooled)
        first = effect["by_seed"][self.cfg["seeds"][0]]["replay"]
        self.assertEqual((first["PASS_PASS"], first["PASS_FAIL"], first["FAIL_PASS"], first["FAIL_FAIL"]), (12, 12, 0, 8))
        self.assertFalse(effect["h1_pass"])  # Third seed fails the per-seed 50% floor.

    def test_b_gate_requires_both_subskills_and_all_archetypes(self):
        tasks = self.items["b_eval"]
        ids = [x["task_id"] for x in tasks]
        before = {seed: {tid: False for tid in ids} for seed in self.cfg["seeds"]}
        per_arch = {name: [x["task_id"] for x in tasks if x["archetype"] == name]
                    for name in sorted({x["archetype"] for x in tasks})}
        successes = {tid for group in per_arch.values() for tid in group[:3]}
        naive = {seed: {tid: tid in successes for tid in ids} for seed in self.cfg["seeds"]}
        replay = copy.deepcopy(naive)
        self.assertTrue(c.b_gate(self.cfg, tasks, before, naive, replay)["h3_pass"])
        broken = copy.deepcopy(naive)
        string_ids = {x["task_id"] for x in tasks if x["family"] == "string_transform"}
        for seed in broken:
            for tid in string_ids:
                broken[seed][tid] = False
        result = c.b_gate(self.cfg, tasks, before, broken, replay)
        self.assertFalse(result["naive_broad_eligible"])
        self.assertFalse(result["broad_plasticity_claim_allowed"])
        below_fraction = copy.deepcopy(naive)
        keep = set(sorted(successes)[:8])
        for seed in below_fraction:
            below_fraction[seed] = {tid: tid in keep for tid in ids}
        self.assertFalse(c.b_gate(self.cfg, tasks, before, naive, below_fraction)["h3_pass"])

    def test_non_goco_strictly_more_than_nine_drop(self):
        ids = [f"R{i:02d}" for i in range(64)]
        base = {tid: True for tid in ids}
        nine_down = {tid: i >= 9 for i, tid in enumerate(ids)}
        ten_down = {tid: i >= 10 for i, tid in enumerate(ids)}
        post_a = {seed: dict(nine_down) for seed in self.cfg["seeds"]}
        naive = copy.deepcopy(post_a)
        replay = copy.deepcopy(post_a)
        self.assertTrue(c.regression_gate(self.cfg, base, post_a, naive, replay)["h4_pass"])
        replay[self.cfg["seeds"][0]] = ten_down
        self.assertFalse(c.regression_gate(self.cfg, base, post_a, naive, replay)["h4_pass"])

    def test_frozen_config_hash_rejection_and_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_cfg = root / "changed_config.json"
            fake_cfg.write_text(json.dumps({"seeds": []}), encoding="utf-8")
            with patch.object(c, "CONFIG", fake_cfg):
                with self.assertRaises(ValueError):
                    c.load_frozen(check_base=False)
            one, two, output = root / "adapter.safetensors", root / "record.json", root / "manifest.json"
            one.write_bytes(b"synthetic adapter fixture")
            two.write_text('{"synthetic": true}\n', encoding="utf-8")
            manifest = c.write_manifest([one, two], output, {"parent": "synthetic-base"},
                                        {str(one): {"seed": 1, "condition": "A"}})
            self.assertEqual(len(manifest["artifacts"]), 2)
            self.assertEqual(manifest["artifacts"][0]["sha256"], c.sha256(one))
            self.assertEqual(manifest["artifacts"][0]["condition"], "A")
            with self.assertRaises(FileExistsError):
                c.write_manifest([one], output, {})

    def test_pre_b_record_lineage_and_automatic_stop(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cfg = copy.deepcopy(self.cfg)
            cfg["runtime_root"] = "runtime"
            tasks = self.items["a_eval"]
            for seed in cfg["seeds"]:
                evaluation = root / "runtime" / "evaluations" / str(seed) / "A_a.json"
                training = root / "runtime" / "training" / str(seed) / "A.json"
                evaluation.parent.mkdir(parents=True)
                training.parent.mkdir(parents=True)
                hashes = {"adapter_model.safetensors": f"synthetic-{seed}"}
                training.write_text(json.dumps({"adapter": {"file_hashes": hashes}}), encoding="utf-8")
                evaluation.write_text(json.dumps({"phase": "3C", "suite": "A", "condition": "A",
                    "seed": seed, "config_sha256": c.sha256(c.CONFIG), "adapter_file_hashes": hashes,
                    "records": [{"task_id": x["task_id"], "hidden_pass": True} for x in tasks]}), encoding="utf-8")
            with patch.object(c, "ROOT", root):
                self.assertTrue(c.pre_b_gate_from_records(cfg, self.items)["all_eligible"])
                seed = cfg["seeds"][0]
                evaluation = root / "runtime" / "evaluations" / str(seed) / "A_a.json"
                record = json.loads(evaluation.read_text())
                record["adapter_file_hashes"] = {"adapter_model.safetensors": "wrong-parent"}
                evaluation.write_text(json.dumps(record), encoding="utf-8")
                with self.assertRaises(ValueError):
                    c.pre_b_gate_from_records(cfg, self.items)
                record["adapter_file_hashes"] = {"adapter_model.safetensors": f"synthetic-{seed}"}
                record["records"][:9] = [{"task_id": x["task_id"], "hidden_pass": False} for x in tasks[:9]]
                evaluation.write_text(json.dumps(record), encoding="utf-8")
                self.assertEqual(c.pre_b_gate_from_records(cfg, self.items)["action"], "STOP_before_B_no_tuning")

    def test_bootstrap_keeps_task_ids_clustered(self):
        from analyze_phase3c import bootstrap_a
        cfg = copy.deepcopy(self.cfg)
        cfg["bootstrap"]["task_cluster_draws"] = 40
        tasks = self.items["a_eval"]
        ids = [x["task_id"] for x in tasks]
        pre = {seed: {tid: True for tid in ids} for seed in cfg["seeds"]}
        naive = {seed: {tid: False for tid in ids} for seed in cfg["seeds"]}
        replay = {seed: {tid: True for tid in ids} for seed in cfg["seeds"]}
        result = bootstrap_a(cfg, tasks, pre, naive, replay)
        self.assertEqual(result["retention_difference_pp"]["valid_draws"], 40)
        self.assertEqual(result["retention_difference_pp"]["lower_2p5"], 100)
        self.assertEqual(result["aggregate_a_difference_pp"]["upper_97p5"], 100)

    def test_aggregate_a_ten_point_boundary(self):
        tasks = self.items["a_eval"]
        ids = [x["task_id"] for x in tasks]
        pre = {seed: {tid: True for tid in ids} for seed in self.cfg["seeds"]}
        naive = {seed: {tid: False for tid in ids} for seed in self.cfg["seeds"]}
        replay = {seed: {tid: tid in ids[:3] for tid in ids} for seed in self.cfg["seeds"]}
        self.assertFalse(c.a_endpoints(self.cfg, tasks, pre, naive, replay)["h2_pass"])
        replay = {seed: {tid: tid in ids[:4] for tid in ids} for seed in self.cfg["seeds"]}
        self.assertTrue(c.a_endpoints(self.cfg, tasks, pre, naive, replay)["h2_pass"])

    def test_executor_requires_explicit_future_execute_flag(self):
        result = subprocess.run([sys.executable, str(c.ROOT / "scripts/run_phase3c.py")],
                                cwd=c.ROOT, capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("disabled without --execute", result.stderr + result.stdout)

    def test_execution_manifest_and_model_support_hashes(self):
        manifest = c.verify_execution_files()
        self.assertEqual(manifest["frozen_design_commit"], c.FROZEN_HEAD)
        self.assertIn("scripts/train_phase3c_qlora.py", manifest["code_git_text_sha256"])
        self.assertEqual(len(manifest["model_support_file_sha256"]), 7)
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / "execution_manifest.json"
            bad = copy.deepcopy(manifest)
            bad["frozen_design_commit"] = "wrong"
            fake.write_text(json.dumps(bad), encoding="utf-8")
            with patch.object(c, "EXECUTION_MANIFEST", fake):
                with self.assertRaises(ValueError):
                    c.verify_execution_files()

    def test_critical_package_versions_are_pinned(self):
        self.assertEqual(c.assert_critical_packages(self.cfg), self.cfg["environment_at_design_freeze"]["packages"])
        altered = copy.deepcopy(self.cfg)
        altered["environment_at_design_freeze"]["packages"]["torch"] = "0.0.0-synthetic"
        with self.assertRaises(ValueError):
            c.assert_critical_packages(altered)


if __name__ == "__main__":
    unittest.main()
