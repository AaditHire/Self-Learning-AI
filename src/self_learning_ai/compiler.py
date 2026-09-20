"""Bounded subprocess interface to the pinned GOCO interpreter."""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CompilerResult:
    phase: str
    exit_code: int | None
    stdout: str
    stderr: str
    elapsed_ms: int
    timed_out: bool
    output_limited: bool
    executed: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class _CappedReader(threading.Thread):
    def __init__(self, stream: object, limit: int, stop: threading.Event) -> None:
        super().__init__(daemon=True)
        self.stream = stream
        self.limit = limit
        self.stop = stop
        self.data = bytearray()
        self.exceeded = False

    def run(self) -> None:
        while True:
            chunk = self.stream.read(4096)  # type: ignore[attr-defined]
            if not chunk:
                return
            remaining = self.limit - len(self.data)
            if remaining > 0:
                self.data.extend(chunk[:remaining])
            if len(chunk) > remaining:
                self.exceeded = True
                self.stop.set()
                return


class GocoCompiler:
    """Execute one GOCO source file with explicit resource boundaries.

    The process is isolated in a fresh temporary working directory and is never
    invoked through a shell. The pinned GOCO language exposes no process,
    network, reflection, arbitrary filesystem, or Java-interop primitives.
    """

    def __init__(
        self,
        java_executable: Path,
        compiler_jar: Path,
        *,
        timeout_seconds: float = 3.0,
        heap_megabytes: int = 256,
        output_limit_bytes: int = 65_536,
    ) -> None:
        self.java_executable = java_executable.resolve()
        self.compiler_jar = compiler_jar.resolve()
        self.timeout_seconds = timeout_seconds
        self.heap_megabytes = heap_megabytes
        self.output_limit_bytes = output_limit_bytes
        if not self.java_executable.is_file():
            raise FileNotFoundError(self.java_executable)
        if not self.compiler_jar.is_file():
            raise FileNotFoundError(self.compiler_jar)

    def run(self, source: str, stdin: str = "") -> CompilerResult:
        started = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="goco-research-") as raw_dir:
            working_dir = Path(raw_dir)
            source_path = working_dir / "submission.goco"
            source_path.write_text(source, encoding="utf-8")
            command = [
                str(self.java_executable),
                "-Dfile.encoding=UTF-8",
                "-Dstdout.encoding=UTF-8",
                "-Dstderr.encoding=UTF-8",
                f"-Xmx{self.heap_megabytes}m",
                "-XX:MaxMetaspaceSize=128m",
                "-cp",
                str(self.compiler_jar),
                "parser.MyLanguageParser",
                str(source_path),
            ]
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(
                subprocess, "CREATE_NEW_PROCESS_GROUP", 0
            )
            process = subprocess.Popen(  # noqa: S603
                command,
                cwd=working_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                creationflags=flags,
            )
            assert process.stdin and process.stdout and process.stderr
            stop = threading.Event()
            stdout_reader = _CappedReader(process.stdout, self.output_limit_bytes, stop)
            stderr_reader = _CappedReader(process.stderr, self.output_limit_bytes, stop)
            stdout_reader.start()
            stderr_reader.start()
            try:
                process.stdin.write(stdin.encode("utf-8"))
                process.stdin.close()
            except BrokenPipeError:
                pass

            timed_out = False
            deadline = time.monotonic() + self.timeout_seconds
            while process.poll() is None:
                if stop.wait(0.01):
                    process.kill()
                    break
                if time.monotonic() >= deadline:
                    timed_out = True
                    process.kill()
                    break
            process.wait()
            stdout_reader.join(timeout=1)
            stderr_reader.join(timeout=1)

        stdout = bytes(stdout_reader.data).decode("utf-8", errors="replace")
        stderr = bytes(stderr_reader.data).decode("utf-8", errors="replace")
        output_limited = stdout_reader.exceeded or stderr_reader.exceeded
        phase = self._phase(process.returncode, stdout, stderr, timed_out, output_limited)
        return CompilerResult(
            phase=phase,
            exit_code=process.returncode,
            stdout=stdout,
            stderr=stderr,
            elapsed_ms=round((time.perf_counter() - started) * 1000),
            timed_out=timed_out,
            output_limited=output_limited,
            executed=phase in {"success", "runtime"},
        )

    @staticmethod
    def _phase(
        exit_code: int,
        stdout: str,
        stderr: str,
        timed_out: bool,
        output_limited: bool,
    ) -> str:
        if timed_out:
            return "timeout"
        if output_limited:
            return "output_limit"
        text = f"{stdout}\n{stderr}".casefold()
        if exit_code == 0:
            return "success"
        if "lexical error:" in text:
            return "lexical"
        if "syntax error:" in text:
            return "syntax"
        if "semantic errors:" in text:
            return "semantic"
        if "runtime error:" in text:
            return "runtime"
        return "system"


_INPUT_PROMPT = re.compile(r"Enter value for [A-Za-z_][A-Za-z0-9_]*(?:\[\d+\])?: ")


def normalized_program_output(text: str) -> str:
    """Remove deterministic interpreter input prompts and normalize newlines."""

    without_prompts = _INPUT_PROMPT.sub("", text)
    return without_prompts.replace("\r\n", "\n").replace("\r", "\n").strip()
