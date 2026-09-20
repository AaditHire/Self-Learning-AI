from __future__ import annotations

import os
from pathlib import Path

import pytest

from self_learning_ai.compiler import GocoCompiler, normalized_program_output


ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / ".tools" / "jdk-25.0.1+8" / "bin" / "java.exe"
JAR = ROOT / ".artifacts" / "compiler" / "goco-compiler-6a029b8.jar"


@pytest.fixture(scope="module")
def compiler() -> GocoCompiler:
    if not JAVA.exists() or not JAR.exists():
        pytest.skip("Pinned local compiler toolchain has not been built")
    return GocoCompiler(JAVA, JAR, timeout_seconds=1, output_limit_bytes=4096)


def test_success_and_utf8(compiler: GocoCompiler) -> None:
    result = compiler.run('DISPLAYNL("héllo").')
    assert result.phase == "success"
    assert result.stdout == "héllo" + os.linesep


@pytest.mark.parametrize(
    ("source", "phase"),
    [
        ('DISPLAYNL("unterminated).', "lexical"),
        ("DISPLAYNL(1)", "syntax"),
        ("DISPLAYNL(missing).", "semantic"),
        ("DISPLAYNL(1 / 0).", "runtime"),
    ],
)
def test_diagnostic_phase(compiler: GocoCompiler, source: str, phase: str) -> None:
    assert compiler.run(source).phase == phase


def test_controlled_stdin_and_prompt_normalization(compiler: GocoCompiler) -> None:
    source = "NUMBER x.\nINPUT(x).\nDISPLAYNL(x * 2)."
    result = compiler.run(source, "4\n")
    assert result.phase == "success"
    assert normalized_program_output(result.stdout) == "8.0"


def test_timeout_and_cleanup(compiler: GocoCompiler) -> None:
    result = compiler.run("LOOP (TRUE) {}")
    assert result.timed_out
    assert result.phase == "timeout"


def test_output_limit(compiler: GocoCompiler) -> None:
    source = 'LOOP (TRUE) { DISPLAY("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"). }'
    result = compiler.run(source)
    assert result.output_limited
    assert len(result.stdout.encode("utf-8")) <= compiler.output_limit_bytes
