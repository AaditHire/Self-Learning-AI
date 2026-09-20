# Project state

Last updated: 2026-09-20

Current phase: Phase 1 complete; no parameter adaptation authorized
Phase decision: NO-GO for Phase 2

## Repository boundaries

- Primary research repository (all new work goes here):
  `C:\Users\Admin\OneDrive\Documents\GitHub\Self Learning AI`
- Primary repository commit inspected at Phase 0 start:
  `1edb0f5c017302da9054dbb06c82b695612400fd`
- Main GOCO product repository (**STRICTLY READ ONLY**):
  `C:\Users\Admin\OneDrive\Documents\GitHub\GOCO`
- GOCO commit extracted and pinned for the research instrument:
  `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`
- GOCO remote: `https://github.com/Thryza-creators/GOCO.git`
- The mutable GOCO checkout had advanced to `57acfa52b3ce983572683e612c4cd8e4ba9b47a4`
  before Phase 1. Phase 1 did not use that working tree content: extraction came
  from the recorded `6a029b8` Git object. GOCO remained clean and unmodified.

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

## Phase 1 frozen inputs

- Compiler runtime: Eclipse Temurin 25.0.1+8.
- Parser generator: JavaCC 7.0.13.
- Evaluated compiler JAR SHA-256: `c6f45759930438dd4ae7bfbff298e9c7242604582d29da04210f15377f2be879`.
- Canonical class-tree SHA-256: `68b3ab9e694d3917957a62577a10e658cd60f5103368a17c5c3ae77374c4fb2a`.
- Deterministically packaged reproduction JAR SHA-256:
  `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`.
- Model: `Qwen/Qwen2.5-Coder-1.5B-Instruct` revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- Model weights SHA-256: `c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`.
- Inference config SHA-256: `7a6ab3e3fcd335be8674a22dde74d137b7c04b5632eabea3229b7f9319fc7584`.
- Python 3.13.0, PyTorch 2.9.0+cu130, Transformers 4.57.1.

Java 21 and the pinned Java 25 runtime produced identical behavior across all 88
upstream conformance cases, but official results use Java 25.0.1 only.

## Phase 1 results

- Compiler conformance: 87/88 exact; one explained stale upstream expectation
  for the automatic `INPUT` prompt; no timeout, crash, or output-limit failure.
- Wrapper tests: 10/10 passed.
- Benchmark: 40 tasks, 8 semantic families, 40 unique template IDs; 8
  development, 24 frozen evaluation, and 8 sealed final-paper tasks.
- Condition A, frozen base/no docs: 0/24 parse and 0/24 hidden pass. Every output
  was a Go `package main` program.
- Condition B, frozen base/full trusted docs: 0/24 parse and 0/24 hidden pass.
  Every output invented an unsupported `PROGRAM` wrapper.
- Paired pass-rate difference: 0.000; paired bootstrap 95% interval [0, 0];
  exact McNemar p=1.0 with zero discordant pairs. This is a floor effect, not an
  equivalence finding.

The compiler exposes no GOCO filesystem, process, network, reflection, or Java
interop capabilities. Execution nevertheless remains bounded in a no-shell
subprocess with a temporary directory, controlled stdin, separate capped
streams, heap/metaspace caps, timeout, and cleanup.

## Research records

- Research question: `docs/research/RESEARCH_QUESTION.md`
- Hypotheses: `docs/research/HYPOTHESES.md`
- Methodology and reproducibility: `docs/research/METHODOLOGY.md`
- Claims ledger: `docs/research/CLAIMS_LEDGER.md`
- References: `docs/research/REFERENCES.md`
- Threats: `docs/research/THREATS_TO_VALIDITY.md`
- Experiment registry: `docs/research/EXPERIMENT_REGISTRY.md`
- Completed phase record: `docs/research/stages/PHASE_00.md`
- Completed Phase 1 record: `docs/research/stages/PHASE_01.md`
- Frozen Phase 1 protocol: `research/protocols/PHASE_01_FROZEN_BASELINE_RETRIEVAL_CEILING.md`
- Raw evaluation: `research/results/EXP-0003-0004/phase1_evaluation.json`

## Resume instructions

Do not start QLoRA, LoRA, Phase 2, or any parameter update. Phase 1's NO-GO must
be independently reviewed. If authorized, the next work should be **Phase 1R —
Elicitation Protocol Repair and Fresh Frozen Baseline Replication**: use only
development tasks to make the documentation/prompt produce valid GOCO, correct
the trusted reference (including its false recursion statement), pre-register a
new protocol, and evaluate on a newly created frozen suite. Do not tune against
the completed 24-task Phase 1 evaluation or open the final-paper suite.
