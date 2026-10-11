"""P2 atom format, offset separation and neutral model IDs."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from explore_da_build import OUT, WORDINGS, held_out_examples, render, training_examples
from explore_b0_sample_check import sample_prompts
from self_learning_ai.conf1_r1.training import _builder
from self_learning_ai.explore.pools import enumerate_candidates, load_dev_pool, probes, signature, split_candidates


def rows():
    return json.loads((OUT / "train.json").read_bytes())


def test_training_formats_and_counts():
    training = rows()
    assert Counter(r["category"] for r in training) == {"atom_single": 160, "atom_isolated": 240}
    assert set(r["wording"] for r in training) == {"W1", "W2", "W3", "W4"}
    builder = _builder()
    counts = Counter()
    for row in training:
        slot = row["slot"]
        assert 20 <= slot["offset"] <= 39
        assert "{" not in row["prompt"] and "}" not in row["prompt"]
        assert row["prompt"] == render(row["category"], slot, int(row["wording"][1]))
        definition = slot["primitive"] if row["category"] == "atom_single" else tuple(sorted((slot["P"], slot["Q"])))
        counts[row["category"], row["family"], definition, row["wording"]] += 1
        source = (builder.sanity_source(slot) if row["category"] == "atom_single" else builder.train_source("isolated", slot))
        assert row["target"] == source
        if row["category"] == "atom_single":
            assert row["group"] == "primitive_sanity"
        assert len(row["cases"]) == 5
        assert len({c["stdin"] for c in row["cases"]}) == 5
        values = []
        for case in row["cases"]:
            value = (builder.sanity_expected(slot, case["stdin"]) if row["category"] == "atom_single" else
                     builder.train_expected("isolated", slot, case["stdin"]))
            values.append(value)
            assert case["expected_stdout"] == f"{value}.0"
            assert case["stdin"].endswith("\n")
        assert len(set(values)) > 1
    assert len(counts) == 80
    assert set(counts.values()) == {5}
    assert training == training_examples()


def test_no_dev_or_sealed_signature_with_same_offset():
    survivors, _, _ = enumerate_candidates()
    dev, sealed_metadata, _ = split_candidates(survivors)
    # Deterministic metadata only; the sealed pool file is never opened.
    occupied = {(r["slot"].get("offset"), tuple(r["signature"])) for r in dev + sealed_metadata}
    inputs = probes()
    for row in rows():
        assert (row["slot"]["offset"], signature(row["category"], row["slot"], inputs)) not in occupied


def test_opaque_ids_and_w5_eval_only():
    training = rows()
    identifiers = [row["example_id"] for row in training]
    assert len(set(identifiers)) == 400
    assert all(re.fullmatch(r"EXPL-DA-\d{4}", ident) for ident in identifiers)
    evaluation = json.loads((OUT / "eval_w5.json").read_bytes())
    assert evaluation == held_out_examples()
    originals = [r for r in sample_prompts(load_dev_pool()) if r["category"] in WORDINGS]
    assert Counter(r["category"] for r in evaluation) == {"atom_single_w5": 16, "atom_isolated_w5": 16}
    for extra, original in zip(evaluation, originals):
        assert extra["task_id"] == original["task_id"]
        assert extra["model_task_id"] == original["model_task_id"]
        assert extra["cases"] == original["cases"]
        assert extra["wording"] == "W5"
        assert re.fullmatch(r"EXPL-B0-\d{4}", extra["model_task_id"])
        assert "{" not in extra["prompt"] and "}" not in extra["prompt"]
