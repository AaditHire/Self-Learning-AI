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
    monkeypatch.setattr(stream, "stream_paths", lambda seed, method, lora_rank=16: (output, runtime))
    calls = []
    def fake_child(command, seed, stage, operation, lora_rank=16):
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


@pytest.mark.parametrize("rank,alpha", [(16, 32), (4, 8)])
def test_lora_rank_and_alpha(rank, alpha):
    from explore_sft import ROOT, lora_settings
    args = argument_parser().parse_args(["--data", "train.json"] +
                                       ([] if rank == 16 else ["--lora-rank", str(rank)]))
    assert args.lora_rank == rank
    settings = lora_settings(args.lora_rank)
    frozen = load_dev_pool(ROOT / "research/protocols/phase3a_config.json")["training"]["lora"]
    assert settings["r"] == rank and settings["lora_alpha"] == alpha
    assert settings["lora_dropout"] == frozen["dropout"]
    assert settings["bias"] == frozen["bias"] and settings["target_modules"] == frozen["target_modules"]


@pytest.mark.parametrize("method", ["naive", "opr"])
def test_rank_four_paths(method):
    seed = 20291016
    assert stream.argument_parser().parse_args(["--seed", str(seed)]).lora_rank == 16
    assert stream.stream_paths(seed, method, 4) == (
        stream.ROOT / f"research/explore/a2/r4/{method}/{seed}",
        stream.ROOT / f".runtime/explore/a2/r4/{method}/{seed}")
    assert stream.run_name("a1_stream", 16) == "a1_stream"
    assert stream.run_name("a1_stream", 4) == "a1_stream_r4"


def test_rank_four_no_g1(monkeypatch):
    import io
    import sys
    calls = []
    monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(io.BytesIO()))
    monkeypatch.setattr(sys, "stderr", io.TextIOWrapper(io.BytesIO()))
    monkeypatch.setattr(sys, "argv", ["stream", "--seed", "20291017", "--lora-rank", "4"])
    monkeypatch.setattr(stream, "stream", lambda seed, method, rank: calls.append((seed, method, rank)))
    monkeypatch.setattr(stream, "gate", lambda: pytest.fail("rank 4 must never call existing G1"))
    stream.main()
    assert calls == [(20291017, "naive", 4)]


@pytest.mark.parametrize("method", ["naive", "opr"])
def test_rank_four_stream_commands(monkeypatch, tmp_path, method):
    real_paths = stream.stream_paths
    output, runtime = tmp_path / "output", tmp_path / "runtime"
    monkeypatch.setattr(stream, "stream_paths", lambda seed, method, lora_rank=16: (output, runtime))
    calls, logs = [], []
    monkeypatch.setattr(stream, "append_run", logs.append)
    def fake_child(command, seed, stage, operation, lora_rank=16):
        assert lora_rank == 4
        calls.append((operation, command))
        if operation == "replay":
            assert command[command.index("--output") + 1] == output / f"replay_stage{stage}.json"
            assert command[-2:] == ["--run-name", "a2_opr_sample_r4"]
            stream.write_json(command[command.index("--output") + 1], dict(rows=[]))
            return
        if operation == "train":
            assert command[command.index("--run-name") + 1] == ("a1_train_r4" if method == "naive" else "a2_opr_train_r4")
            if stage == 1:
                assert command[-2:] == ["--lora-rank", 4] and "--fresh-lora" in command
            else:
                assert "--lora-rank" not in command
                assert command[-2:] == ["--init-adapter", runtime / f"stage{stage - 1}/adapter_final"]
            summary = {key: 0 for key in ("first_loss", "last_loss", "peak_gpu_allocated_bytes",
                                          "peak_gpu_reserved_bytes", "seconds", "training_seconds")}
        else:
            assert command[-2:] == ["--run-name", "a1_eval_r4"]
            summary = dict(stages={str(s): dict(pass_rate=1) for s in range(1, stage + 1)})
        stream.write_json(command[command.index("--summary") + 1], summary)
    monkeypatch.setattr(stream, "child", fake_child)
    stream.stream(20291016, method, 4)
    assert len(calls) == (8 if method == "naive" else 11)
    assert logs[-1]["run"] == ("a1_stream_r4" if method == "naive" else "a2_opr_stream_r4")
    assert real_paths(20291016, method, 16) == real_paths(20291016, method)


@pytest.mark.parametrize("retentions,invalid_stage4,verdict", [
    ([0.7, 0.7, 0.7], False, "PASS"),
    ([0.7, 0.7, 0.8], False, "FAIL"),
    ([0.7, 0.7, 0.7], True, "PASS"),
])
def test_rank_g2_formula_and_validity(monkeypatch, tmp_path, retentions, invalid_stage4, verdict):
    import explore_a2_probes as probes
    monkeypatch.setattr(probes, "ROOT", tmp_path)
    monkeypatch.setattr(stream, "ROOT", tmp_path)
    logs = []
    monkeypatch.setattr(probes, "append_run", logs.append)
    args = probes.argument_parser().parse_args(["--g2-rank", "4"])
    assert args.g2_rank == 4 and not args.g2
    for i, seed in enumerate(probes.SEEDS):
        naive = [[0.9, None, None, None], [0.2, 0.9, None, None],
                 [0.2, 0.3, 0.9, None], [0.2, 0.3, 0.4, 0.59 if invalid_stage4 and i == 1 else 0.9]]
        opr = [list(row) for row in naive]
        opr[3] = [retentions[i]] * 3 + [0.9]
        for method, matrix in (("naive", naive), ("opr", opr)):
            directory = stream.stream_paths(seed, method, 4)[0]
            stream.write_json(directory / "results.json", dict(accuracy_matrix=matrix,
                              acquisition={str(s + 1): matrix[s][s] for s in range(4)}))
        for stage in (2, 3, 4):
            stream.write_json(stream.stream_paths(seed, "opr", 4)[0] / f"replay_stage{stage}.json",
                              dict(earlier_stages={str(s): dict(prompts_drawn=6, verified=3)
                                                  for s in range(1, stage)}))
    summary = probes.gate_g2(args.g2_rank)
    assert summary["verdict"] == verdict
    assert summary["regime_valid_all"] is (not invalid_stage4)
    assert summary["lora_rank"] == 4 and summary["ceiling_is_proxy"]
    for i, seed in enumerate(probes.SEEDS):
        group = summary["seeds"][str(seed)]
        assert group["ceiling_proxy"] == pytest.approx(0.9)
        assert group["opr_final_retention"] == pytest.approx(retentions[i])
        assert group["gap_pp"] == pytest.approx(100 * (0.9 - retentions[i]))
        assert group["naive_final_retention"] == pytest.approx(0.3)
        assert group["regime_valid"] is (not (invalid_stage4 and i == 1))
        assert group["replay"]["2"]["1"]["verification_rate"] == 0.5
    assert load_dev_pool(tmp_path / "research/explore/a2/r4/g2_summary.json") == summary
    assert logs[-1]["run"] == "a2_g2_r4"
