from self_learning_ai.benchmark import extract_source, extract_source_phase1r, paired_comparison


def test_extract_source_is_mechanical() -> None:
    assert extract_source("```goco\nDISPLAYNL(1).\n```") == "DISPLAYNL(1)."
    assert extract_source("DISPLAYNL(1).") == "DISPLAYNL(1)."


def test_phase1r_extracts_exactly_one_fenced_block() -> None:
    raw = "Explanation\n```goco\nNUMBER x = 1.\n```\nDone"
    assert extract_source_phase1r(raw) == "NUMBER x = 1."


def test_phase1r_does_not_choose_between_multiple_blocks() -> None:
    raw = "```goco\nNUMBER x = 1.\n```\n```goco\nDISPLAYNL(x).\n```"
    assert extract_source_phase1r(raw) == raw


def test_paired_comparison() -> None:
    baseline = [
        {"task_id": "a", "hidden_pass": False},
        {"task_id": "b", "hidden_pass": True},
    ]
    docs = [
        {"task_id": "a", "hidden_pass": True},
        {"task_id": "b", "hidden_pass": True},
    ]
    result = paired_comparison(baseline, docs, bootstrap_samples=100)
    assert result["paired_risk_difference"] == 0.5
    assert result["docs_only_passes"] == 1
