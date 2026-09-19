# Project state

Last updated: 2026-09-19  
Current phase: Phase 0 complete; Phase 1 is drafted but not authorized  
Phase decision: GO

## Repository boundaries

- Primary research repository (all new work goes here):
  `C:\Users\Admin\OneDrive\Documents\GitHub\Self Learning AI`
- Primary repository commit inspected at Phase 0 start:
  `1edb0f5c017302da9054dbb06c82b695612400fd`
- Main GOCO product repository (**STRICTLY READ ONLY**):
  `C:\Users\Admin\OneDrive\Documents\GitHub\GOCO`
- GOCO commit inspected and pinned for planning:
  `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`
- GOCO remote: `https://github.com/Thryza-creators/GOCO.git`
- GOCO status at both start and end of Phase 0: clean, branch `main`, two
  commits behind `origin/main`. It was not pulled, built, generated into, or
  modified.

Never write to the GOCO path for this research project. Future integration must
copy an explicitly pinned source tree into this repository and record its
provenance; it must not import from or execute against the mutable product
checkout.

## Research goal

Test whether a small language model can acquire verified GOCO capabilities in
sequence, retain them in adapter parameters without permanent documentation
access, and reject candidate updates that cause pre-registered unacceptable
forgetting. This project does not claim AGI, consciousness, self-awareness, or
unrestricted recursive self-improvement.

## Fixed constraints

- Hardware: Windows 11, RTX 3060 Laptop GPU (6 GB VRAM), Ryzen 7 6800HS,
  16 GB system RAM.
- Primary model: `Qwen/Qwen2.5-Coder-1.5B-Instruct`, immutable exact revision
  to be resolved and frozen before the first model experiment.
- Training path after baselines: 4-bit QLoRA, LoRA rank initially near 16,
  batch size 1, gradient accumulation, gradient checkpointing, conservative
  sequence lengths.
- No model training occurs in Phase 0 or Phase 1.
- Foundation-model weights remain immutable; adapters are versioned and never
  repeatedly merged into the base.
- Compiler plus hidden semantic tests, not the model, determine correctness.

## Phase 0 findings

GOCO's compiler is an interpreter implemented in Java around a JavaCC grammar.
The entry point is `parser.MyLanguageParser`. It accepts exactly one `.goco`
file, parses it to a `CoreNodes.ProgramNode`, validates it against a global
scope, and executes the AST only if semantic validation succeeds. Syntax,
lexical, semantic, and runtime failures terminate with exit code 1. Program
output uses stdout; diagnostics use stderr. `INPUT` reads stdin and emits a
prompt to stdout.

The production test manifest contains 88 cases: 45 expected successes and 43
expected failures. The current Python test harness regenerates test files and
the batch runner recompiles into `goco-compiler/bin`, so it was deliberately not
run inside the read-only repository.

The production repository already contains a useful Python subprocess adapter
in `goco-ai/src/goco_ai/compiler/goco.py`. It uses a temporary `.goco` file,
captures stdout/stderr, supplies stdin, applies a timeout, sets a 256 MB JVM
heap limit, and normalizes diagnostics. It is a design reference only; Phase 1
will implement a research-owned version against a pinned compiler snapshot.

## Compiler provenance selected for extraction

- GOCO commit: `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`
- `goco-compiler` Git tree: `f51973617cc3da8c78de88c668d8de6959575d6d`
- Java source Git tree: `415215892c7127df899d59b3bceb99dc8357484b`
- `tests/tests.json` Git blob: `7ad40be14848fa3d03ac02f36066e737000bc401`
- Full machine-readable record:
  `research/manifests/goco_compiler_source.json`

## Environment audit

- Installed Java/Javac: 21.0.12.1 LTS.
- GOCO compiler README requests Java 25.0.1 only.
- `javacc` is not available on `PATH`.
- Python: 3.13.0.

Phase 1 must resolve and record the Java-version mismatch before promoting a
compiler snapshot. The checked-in generated parser makes JavaCC unnecessary for
an initial compile, but future grammar regeneration must pin JavaCC explicitly.

## Architecture decision

Phase 1 should extract the minimal complete compiler source subtree from the
pinned commit into a research-owned vendor location. Preserve license and
provenance. Compile it into a content-addressed build artifact inside this repo,
then invoke `parser.MyLanguageParser` through a no-shell subprocess wrapper with
temporary files, UTF-8, stdin capture, separate stdout/stderr, time and memory
limits, and normalized result fields. Do not couple to the GOCO checkout.

Compiler execution must occur in a stronger sandbox before untrusted/generated
programs are used at scale. A JVM timeout and heap cap alone do not constitute a
security boundary.

## Research records

- Research question: `docs/research/RESEARCH_QUESTION.md`
- Hypotheses: `docs/research/HYPOTHESES.md`
- Methodology and reproducibility: `docs/research/METHODOLOGY.md`
- Claims ledger: `docs/research/CLAIMS_LEDGER.md`
- References: `docs/research/REFERENCES.md`
- Threats: `docs/research/THREATS_TO_VALIDITY.md`
- Experiment registry: `docs/research/EXPERIMENT_REGISTRY.md`
- Completed phase record: `docs/research/stages/PHASE_00.md`
- Draft next protocol: `research/protocols/PHASE_01_FROZEN_BASELINE_RETRIEVAL_CEILING.md`

## Resume instructions

Do not start Phase 1 without explicit user approval. On approval, first verify
both repository states, resolve the pinned Java runtime strategy, and turn the
draft Phase 1 protocol into a frozen protocol before generating benchmark data
or invoking a model.
