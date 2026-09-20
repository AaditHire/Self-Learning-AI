# GOCO execution threat model

## Scope

The adversarial input is model-generated GOCO source plus controlled stdin. The
protected assets are host availability, memory, disk, network, other processes,
repository contents, result integrity, and evaluator confidentiality.

## Capability audit

The pinned interpreter was searched for filesystem, process, network,
reflection, class loading, and Java interop surfaces. Its `java.io` use is
limited to reading the submitted source, stdin, and stdout/stderr. GOCO exposes
only computation, variables, control flow, functions, arrays, and fixed math,
string, and array libraries. It exposes no source-level file, process, network,
reflection, environment-variable, native, or arbitrary Java API.

Therefore generated GOCO cannot intentionally request host access through the
language as pinned. This conclusion must be re-audited for every compiler
revision; it is not a claim that the JVM or interpreter is vulnerability-free.

## Credible attacks

- infinite loops or extreme computation;
- unbounded output;
- excessive heap or metaspace use;
- blocking for unavailable stdin;
- malformed Unicode or parser stress;
- interpreter bugs that crash the JVM;
- future language changes that introduce host capabilities; and
- tampering with compiler/model/benchmark inputs before a run.

## Enforced controls

- Java is launched as an argument vector with `shell=False`.
- Each execution receives a new temporary working directory and source file.
- stdin is supplied once and then closed.
- stdout and stderr are captured separately and capped at 65,536 bytes each.
- Wall time defaults to three seconds; the process is killed on timeout or
  output overflow.
- JVM heap is capped at 256 MB and metaspace at 128 MB.
- Temporary directories are cleaned after process termination.
- The compiler, configuration, model, benchmark, and prompts are hash-checked.
- The final-paper split is rejected by the Phase 1 evaluation runner.

Because GOCO exposes no process-launch primitive, killing the single JVM is
sufficient for this pinned language revision; generated code cannot create a
child process through GOCO.

## Residual risks

The process runs under the current Windows user and is not contained by a VM,
AppContainer, or separate low-privilege account. A JVM or interpreter exploit
could escape the language-level capability boundary. The temporary directory
does not prevent the JVM itself from seeing other host paths. At the current
small experimental scale, the audited absence of host primitives plus resource
limits is accepted conditionally. Before adding host APIs, third-party native
libraries, user-supplied programs, or large-scale autonomous execution, require
OS-level isolation with filesystem and network denial.
