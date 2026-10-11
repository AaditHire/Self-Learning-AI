"""A1 split and parser contract, without opening sealed data."""
import hashlib
import json
import random
import re
from collections import Counter

import pytest
import build_phase2b_data as builder
from explore_a1_build import OUT, SEED
from explore_sft import ADAPTER, ROOT, argument_parser
from self_learning_ai.explore.pools import load_dev_pool


def inputs():
    return (load_dev_pool(OUT / "stream_train.json"), load_dev_pool(OUT / "stream_dev.json"),
            json.loads((OUT / "manifest.json").read_bytes()))


def test_counts_and_k_splits():
    train, dev, manifest = inputs()
    assert len(train) == 288 and len(dev) == 96
    assert Counter(r["stage"] for r in train) == {s: 72 for s in range(1, 5)}
    assert Counter(r["stage"] for r in dev) == {s: 24 for s in range(1, 5)}
    assert manifest["counts"]["sealed"] == {str(s): 24 for s in range(1, 5)}
    assert len(manifest["stages"]) == 4
    assert all(len(s["templates"]) == 8 for s in manifest["stages"].values())
    assert manifest["max_training_tokens"] <= 320
    for template, split in manifest["k_splits"].items():
        ks = list(range(1, 16))
        random.Random(f"{SEED}-{template}").shuffle(ks)
        assert split == dict(train=ks[:9], dev=ks[9:12], sealed=ks[12:])
        assert len(set(sum(split.values(), []))) == 15
        assert [r["k"] for r in train if r["template"] == template] == split["train"]
        assert [r["k"] for r in dev if r["template"] == template] == split["dev"]


def test_ids_and_prompt_separation():
    train, dev, manifest = inputs()
    metadata = manifest["split_metadata"]
    all_ids = [r["model_id"] for records in metadata.values() for r in records]
    assert len(all_ids) == len(set(all_ids)) == 480
    assert all(re.fullmatch(r"EXPL-A1-\d{4}", value) for value in all_ids)
    for split, rows, key in (("train", train, "example_id"), ("dev", dev, "model_task_id")):
        assert [r[key] for r in rows] == [r["model_id"] for r in metadata[split]]
        assert [hashlib.sha256(r["prompt"].encode()).hexdigest() for r in rows] == [r["prompt_sha256"] for r in metadata[split]]
    sets = [{r["prompt_sha256"] for r in records} for records in metadata.values()]
    assert all(not sets[i] & sets[j] for i in range(3) for j in range(i + 1, 3))


def test_five_builder_cases():
    train, dev, _ = inputs()
    for row in train + dev:
        assert len(row["cases"]) == 5
        for index, case in enumerate(row["cases"], 1):
            assert case == builder.case(index, case["stdin"], case["expected_stdout"])
            assert case["stdin"].endswith("\n")


def test_sft_default_arguments_unchanged():
    args = argument_parser().parse_args(["--data", "train.json"])
    assert args.seed == 20291014
    assert args.run_name == "da_sft"
    assert args.init_adapter == ADAPTER and args.fresh_lora is False
    assert args.output_dir == ROOT / ".runtime/explore/da_sft"
    assert args.summary == ROOT / "research/explore/da/sft_summary.json"


def test_sft_initialization_exclusive():
    with pytest.raises(SystemExit) as error:
        argument_parser().parse_args(["--data", "train.json", "--fresh-lora", "--init-adapter", "adapter"])
    assert error.value.code == 2
    assert argument_parser().parse_args(["--data", "train.json", "--fresh-lora"]).fresh_lora
    assert not argument_parser().parse_args(["--data", "train.json", "--init-adapter", "adapter"]).fresh_lora
