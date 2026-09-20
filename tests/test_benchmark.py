from self_learning_ai.benchmark import extract_source, paired_comparison


def test_extract_source_is_mechanical() -> None:
    assert extract_source("```goco\nDISPLAYNL(1).\n```") == "DISPLAYNL(1)."
    assert extract_source("DISPLAYNL(1).") == "DISPLAYNL(1)."


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
