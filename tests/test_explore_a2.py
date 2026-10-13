"""A2 contracts; no model execution and no sealed data access."""
from collections import Counter

import pytest

import explore_a1_stream as stream
import explore_opr_sample as opr
from explore_a2_probes import cue_example, forced_prefix, forgotten_set, templates, DATA
from explore_sft import argument_parser
from self_learning_ai.explore.pools import load_dev_pool


@pytest.mark.parametrize("stage,counts", [(2, {1: 18}), (3, {1: 9, 2: 9}), (4, {1: 6, 2: 6, 3: 6})])
def test_opr_prompt_split(stage, counts):
    train = load_dev_pool(DATA / "stream_train.json")
    chosen = opr.draw_prompts(train, 20291016, stage)
    assert chosen == opr.draw_prompts(train, 20291016, stage)
    assert Counter(r["stage"] for r in chosen) == counts
    assert len({r["example_id"] for r in chosen}) == 18
    assert all(r in train and r["stage"] < stage for r in chosen)


def test_verification_first_pass(monkeypatch):
    scores = [dict(all_pass=False, cases_passed=4), dict(all_pass=True, cases_passed=5),
              dict(all_pass=True, cases_passed=5), dict(all_pass=False, cases_passed=0)]
    iterator = iter(scores)
    monkeypatch.setattr(opr, "score_program", lambda raw, cases: next(iterator))
    row = dict(example_id="train", prompt="p", stage=1, target="old", cases=[{}] * 5)
    replay, actual, first = opr.verify(row, ["wrong", "```goco\nFIRST\n```", "SECOND", "wrong"])
    assert first == 1 and replay["target"] == "FIRST"
    assert replay["example_id"] == "train" and actual == scores
    monkeypatch.setattr(opr, "score_program", lambda raw, cases: dict(all_pass=False, cases_passed=4))
    assert opr.verify(row, ["wrong"] * 4)[0] is None


@pytest.mark.parametrize("stage", [1, 2, 3])
def test_forced_prefix(stage):
    row = next(r for r in load_dev_pool(DATA / "stream_dev.json") if r["stage"] == stage)
    prefix = forced_prefix(row)
    assert prefix.endswith("\n") and "INPUT(" in prefix
    assert "LOOP" not in prefix and "DISPLAYNL" not in prefix
    lines = prefix.splitlines()
    input_index = next(i for i, line in enumerate(lines) if "INPUT(" in line)
    assert all(any(t in line for t in ("strings.SPLIT", "strings.TO_NUMBER", "= parts["))
               for line in lines[input_index + 1:])
    if stage == 3:
        assert "strings.SPLIT" in prefix and "strings.TO_NUMBER" in prefix


def test_cue_actual_manifest_order():
    train = load_dev_pool(DATA / "stream_train.json")
    for current, following in [("count_letter", "string_length_class"),
                               ("string_length_class", "contains_label"), ("contains_label", "upper_reverse")]:
        example = cue_example(dict(stage=2, template=current), train, templates())
        assert example["template"] == following
        assert example["k"] == min(r["k"] for r in train if r["stage"] == 2 and r["template"] == following)


def test_forgotten_set():
    dev = [dict(model_task_id=str(i), stage=s) for i, s in enumerate([1, 2, 3, 4, 1])]
    own = {str(i): dict(score=dict(all_pass=p)) for i, p in enumerate([True, False, True, True, True])}
    final = {str(i): dict(score=dict(all_pass=p)) for i, p in enumerate([False, False, False, False, True])}
    assert forgotten_set(dev, own, final) == [dev[0], dev[2]]


def test_naive_paths_and_arguments(monkeypatch, tmp_path):
    assert stream.stream_paths(20291018) == (DATA / "20291018", stream.ROOT / ".runtime/explore/a1/20291018")
    assert stream.argument_parser().parse_args(["--seed", "20291018"]).method == "naive"
    output, runtime = tmp_path / "output", tmp_path / "runtime"
    monkeypatch.setattr(stream, "stream_paths", lambda seed, method: (output, runtime))
    calls = []
    def fake_child(command, seed, stage, operation):
        calls.append(command)
        path = command[command.index("--summary") + 1]
        if operation == "train":
            summary = {key: 0 for key in ("first_loss", "last_loss", "peak_gpu_allocated_bytes",
                                          "peak_gpu_reserved_bytes", "seconds", "training_seconds")}
        else:
            summary = dict(stages={str(s): dict(pass_rate=1) for s in range(1, stage + 1)})
        stream.write_json(path, summary)
    monkeypatch.setattr(stream, "child", fake_child)
    monkeypatch.setattr(stream, "append_run", lambda record: None)
    stream.stream(20291018, "naive")
    assert len(calls) == 8
    for stage in range(1, 5):
        command = calls[2 * (stage - 1)]
        expected = [stream.ROOT / "scripts/explore_sft.py", "--seed", 20291018,
                    "--data", output / f"train_rows_stage{stage}.json", "--output-dir", runtime / f"stage{stage}",
                    "--summary", output / f"train_stage{stage}.json", "--run-name", "a1_train"]
        expected += (["--fresh-lora"] if stage == 1 else ["--init-adapter", runtime / f"stage{stage - 1}/adapter_final"])
        assert command == expected
        assert calls[2 * (stage - 1) + 1] == [stream.ROOT / "scripts/explore_stream_eval.py", "--adapter",
            runtime / f"stage{stage}/adapter_final", "--rows", DATA / "stream_dev.json", "--stages",
            ",".join(map(str, range(1, stage + 1))), "--out-dir", runtime / f"eval_after_s{stage}",
            "--summary", output / f"eval_after_s{stage}.json"]


def test_sft_defaults():
    args = argument_parser().parse_args(["--data", "train.json"])
    assert args.epochs == 3 and args.warmup_steps == 5
    custom = argument_parser().parse_args(["--data", "train.json", "--epochs", "1", "--warmup-steps", "0"])
    assert custom.epochs == 1 and custom.warmup_steps == 0
