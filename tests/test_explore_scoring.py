import errno
from types import SimpleNamespace

import pytest
from self_learning_ai.explore import scoring


class FakeCompiler:
    def __init__(self, sequence):
        self.sequence = iter(sequence)
        self.calls = 0

    def run(self, source, stdin):
        self.calls += 1
        value = next(self.sequence)
        if isinstance(value, Exception):
            raise value
        return value


@pytest.mark.parametrize("fault", [OSError(errno.EINVAL, "invalid"), SimpleNamespace(phase="system")])
def test_einval_or_system_two_reinvocations(monkeypatch, fault):
    monkeypatch.setattr(scoring.time, "sleep", lambda _: None)
    success = SimpleNamespace(phase="success")
    compiler = FakeCompiler([fault, fault, success])
    assert scoring.run_with_retries(compiler, "source", "input") is success
    assert compiler.calls == 3


def test_einval_exhausted(monkeypatch):
    monkeypatch.setattr(scoring.time, "sleep", lambda _: None)
    compiler = FakeCompiler([OSError(errno.EINVAL, "invalid")] * 3)
    with pytest.raises(OSError):
        scoring.run_with_retries(compiler, "source", "input")
    assert compiler.calls == 3


def test_other_oserror_never_retried():
    compiler = FakeCompiler([OSError(errno.EACCES, "denied")])
    with pytest.raises(OSError):
        scoring.run_with_retries(compiler, "source", "input")
    assert compiler.calls == 1


def test_score_partial_and_compile_failure(monkeypatch):
    results = [SimpleNamespace(phase="success", stdout="Enter value for n: 5\n"),
               SimpleNamespace(phase="success", stdout="7\n"),
               SimpleNamespace(phase="syntax", stdout="")]
    monkeypatch.setattr(scoring, "make_compiler", lambda: FakeCompiler(results))
    cases = [dict(stdin="1", expected_stdout=str(n)) for n in (5, 8, 0)]
    assert scoring.score_program("NUMBER n. INPUT(n). DISPLAYNL(n).", cases) == dict(
        compiled=False, cases_passed=1, cases_total=3, all_pass=False, phase="syntax")
