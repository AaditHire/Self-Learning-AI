# GOCO compiler extraction and integration plan

## Decision

Use a pinned, research-owned source snapshot of the minimal complete
`goco-compiler` implementation. Do not depend on the mutable production checkout
and do not copy `goco-ai`, the website, or IDE.

## Observed compiler boundary

`parser.MyLanguageParser.main` is the supported CLI boundary. It:

1. requires one `.goco` filename;
2. constructs a JavaCC parser from a file stream;
3. produces a `CoreNodes.ProgramNode` AST;
4. runs semantic validation with a global `CoreNodes.Scope`;
5. executes the AST when validation has no errors; and
6. maps file, syntax, lexical, semantic, and runtime failures to stderr and a
   non-zero process exit.

This is an interpreter rather than a code generator. Parser, semantic checker,
runtime, and standard libraries share Java classes and static state, so taking
only the parser class would be incomplete. The minimal coherent source snapshot
is therefore `goco-compiler/src/main/java/**`, plus the license, grammar,
compiler README, and a separately curated set of provenance-marked tests.

## Proposed research layout (Phase 1)

```text
vendor/goco/<commit>/
  LICENSE
  README.upstream.md
  PROVENANCE.json
  src/main/java/...
  tests/upstream_manifest.json
src/.../compiler/
  adapter
  result schema
  sandbox/process runner
tests/compiler/
  smoke and diagnostic conformance tests
```

The exact Python package layout is intentionally deferred until Phase 1 chooses
the smallest testable project scaffold.

## Extraction procedure

1. Reconfirm that the GOCO checkout is clean and at the pinned commit.
2. Use `git archive` or `git show <commit>:<path>` to extract from the Git object,
   not an uncommitted working tree.
3. Copy only the scoped files into this research repository.
4. Preserve `goco-compiler/LICENSE` and upstream notices.
5. Record source commit, Git tree IDs, per-file SHA-256 hashes, extraction
   command, timestamp, and any exclusions in `PROVENANCE.json`.
6. Verify the extracted tree against the manifest before compiling.
7. Compile into a content-addressed build directory; do not commit opaque class
   files as the only reproducible compiler source.

## Wrapper contract

Input fields should include source text, stdin, and timeout. Output fields should
include phase (`system`, `lexical`, `syntax`, `semantic`, `runtime`, `success`),
exit code, stdout, stderr, elapsed time, timeout flag, executed flag, compiler
hash, and structured diagnostics. Preserve raw streams in result artifacts.

Invoke Java without a command shell. Write source to a fresh temporary
directory, enforce UTF-8, set a conservative heap cap, supply stdin, capture
stdout/stderr separately, and kill the process tree on timeout. Treat input
prompts as stdout, not diagnostics.

## Sandboxing

Generated programs are untrusted. The existing interpreter offers no adequate
security boundary. Before large-scale generation, choose and test a Windows-
compatible isolation strategy with CPU, wall-time, memory, process, filesystem,
and network limits. Until then, only audited fixtures may be executed.

## Conformance gate

Before the snapshot becomes the research oracle:

- resolve the documented Java 25.0.1 requirement;
- compile twice from clean extracted sources and compare manifests;
- run the 88 upstream manifest cases in the copied workspace, never GOCO;
- add wrapper tests for success, syntax, lexical, semantic, runtime, stdin,
  timeout, Unicode, and process cleanup;
- investigate every mismatch rather than updating expected outputs casually;
- freeze the resulting compiler artifact/hash for the evaluation suite.

## Deferred choices

- whether Java 25.0.1 is strictly necessary or merely the upstream development
  version;
- the precise sandbox technology on Windows;
- whether grammar regeneration is needed in Phase 1 (prefer not); and
- which upstream tests may seed development tests without contaminating frozen
  benchmark tasks.
