from __future__ import annotations

import re
from pathlib import Path

import pytest

from self_learning_ai.compiler import GocoCompiler, normalized_program_output


ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / ".tools" / "jdk-25.0.1+8" / "bin" / "java.exe"
JAR = ROOT / ".artifacts" / "compiler" / "goco-compiler-6a029b8-deterministic.jar"


@pytest.fixture(scope="module")
def compiler() -> GocoCompiler:
    if not JAVA.exists() or not JAR.exists():
        pytest.skip("Pinned local compiler toolchain has not been built")
    return GocoCompiler(JAVA, JAR)


def test_all_canonical_context_examples_execute(compiler: GocoCompiler) -> None:
    text = (ROOT / "prompts" / "phase1r_canonical_examples_v1.txt").read_text(encoding="utf-8")
    sources = re.findall(r"Example \d[^:]*:\n\n(.*?)(?=\n\nExample \d|\Z)", text, flags=re.DOTALL)
    cases = [("3\n", "9.0"), ("5|2\n", "5.0"), ("3\n", "6.0"), ("4\n", "8.0"), ("", "7.0")]
    assert len(sources) == len(cases) == 5
    for source, (stdin, expected) in zip(sources, cases, strict=True):
        result = compiler.run(source.strip(), stdin)
        assert result.phase == "success", result.stderr
        assert normalized_program_output(result.stdout) == expected
