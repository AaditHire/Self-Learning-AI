# Phase 1 — Frozen Baseline + Documentation Ceiling

## Objective

Validate a pinned GOCO execution instrument, construct a separate semantic LLM
benchmark, and compare a frozen Qwen base model without GOCO documentation to
the identical model with trusted GOCO documentation in context. Perform no
parameter updates.

## Research question

What executable GOCO capability does the frozen model display, and how much
does a fixed trusted documentation context improve task-level hidden-test
pass@1 under the frozen protocol?

## Hypothesis

The documentation condition was expected to improve hidden-test pass@1,
especially on GOCO-specific syntax, while remaining below perfect accuracy.

## Why this experiment exists

Persistent parameter learning cannot be interpreted without first separating
base-model knowledge from in-context document access on the same unseen tasks.

## Inputs

- Research base commit: `0fabb29` (Phase 0).
- Pinned GOCO Git object: `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`.
- Eclipse Temurin 25.0.1+8 and JavaCC 7.0.13.
- Qwen snapshot and benchmark manifests listed below.
- Frozen inference configuration SHA-256:
  `7a6ab3e3fcd335be8674a22dde74d137b7c04b5632eabea3229b7f9319fc7584`.

## Exact model/revision

`Qwen/Qwen2.5-Coder-1.5B-Instruct` at
`2e1fd397ee46e1388853d2af2c993145b0f1098a`. Official safetensors SHA-256:
`c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`.
Inference used unquantized FP16. All parameters had gradients disabled and the
run used `torch.inference_mode`.

## Exact dataset/manifests

The benchmark contains 40 tasks across expressions/variables, conditionals,
loops, functions, arrays, strings, input/output, and compositional algorithms:
8 development, 24 frozen evaluation, and 8 final-paper. The official paired run
used only the 24 frozen-evaluation tasks, each with three hidden cases.

- Tasks canonical SHA-256: `7d317c6b…be809`.
- Hidden tests canonical SHA-256: `20fed5f1…9c7fd`.
- Reference solutions canonical SHA-256: `f2cc07b9…a74a`.
- Full record: `research/manifests/phase1_benchmark.json`.

## Compiler revision

GOCO commit `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`, compiler tree
`f51973617cc3da8c78de88c668d8de6959575d6d`, Java tree
`415215892c7127df899d59b3bceb99dc8357484b`. Produced runtime JAR SHA-256:
`c6f45759930438dd4ae7bfbff298e9c7242604582d29da04210f15377f2be879`.
The 95 class files have canonical tree SHA-256 `68b3ab9e…4fb2a`. A final
rebuild exposed timestamp-dependent JAR packaging; the deterministic
reproduction JAR is `42478b35…b2a2fb` and contains the identical class tree.

## Training configuration

None. No fine-tuning, LoRA, QLoRA, optimizer, backward pass, adapter, or
parameter update occurred.

## Evaluation protocol

Both conditions used the same model instance, tasks, order, user prompt,
compiler, hidden cases, greedy decoding, 512-new-token cap, no retry, and
mechanical source extraction. Condition B appended the complete trusted GOCO
reference to the unchanged system prompt. Task success required all three hidden
cases and declared structural constraints.

## Frozen metrics decided BEFORE the experiment

Primary: task-level hidden-test pass@1. Diagnostics: parse, semantic compile,
execution, exact output, error phase, family, and difficulty. The paired effect
was docs-minus-baseline risk difference with a 10,000-resample paired bootstrap
95% interval and a two-sided exact McNemar test.

## Expected outcomes

Condition B was expected to exceed Condition A. Nonzero parse and execution
rates were expected in at least the documentation condition.

## Actual results

Compiler conformance: 87/88 exact expected results; 44/45 expected-success and
43/43 expected-failure cases. There were no timeouts, output-limit
terminations, or crashes. The single mismatch was `tests/input_output.goco`:
the runtime emitted its automatic `Enter value for name:` prompt but the
upstream expected output omitted it. Java 21 and Java 25 produced identical
outcomes across all 88 cases.

Benchmark: 40 unique task and template IDs, no exact prompt duplicates, and all
40 reference solutions passed during construction. Routine tooling now skips
the sealed eight-task final-paper split. The largest cross-split prompt
token-set Jaccard similarity was 0.810 (`DEV-LP-001` versus `EVAL-LP-001`), even
though their algorithms/templates differ.

Condition A (`BASE_NO_DOCS`): 0/24 parse, compile, execute, or hidden-test pass.
All 24 generations were fenced Go programs beginning `package main`.

Condition B (`BASE_WITH_DOCS`): 0/24 parse, compile, execute, or hidden-test
pass. All 24 generations invented an unsupported top-level `PROGRAM <name>`
wrapper. Many adopted GOCO periods or keywords, but none formed a valid program.

Paired difference: 0.000 (0 percentage points), paired bootstrap 95% interval
[0.000, 0.000], zero discordant pairs, exact McNemar two-sided p=1.0. This is a
complete floor and is not an equivalence result.

## Failed experiments

Pre-freeze benchmark validation initially failed 19 reference tasks and later
three tasks, revealing repeated-input buffering, unsupported recursion,
identifier/token collisions, string comparison limits, and a loop parser edge
case. These are summarized in `EXP-0002/pre_freeze_failures.md`.

The frozen paired evaluation itself is a validly recorded negative result but a
failed measurement of the intended retrieval ceiling because neither condition
crossed the parse boundary.

## Deviations from protocol

- A pre-freeze development validation file was overwritten during benchmark
  iteration. Its 19-task failure summary was reconstructed from the retained
  console evidence; the later three-failure JSON remains in local artifacts.
- Transformers warned that sampling fields bundled in the model generation
  config were ignored. The run explicitly set deterministic `do_sample=false`;
  no sampling occurred.
- The evaluated JAR was packaged with the JDK `jar` tool, whose entry timestamps
  made its container hash non-reproducible. Class files were byte-identical
  across clean builds. A deterministic packager was added after inference, and
  rescoring equivalence was checked without regenerating model outputs.
- No official inference input or metric was changed after the inference config
  was frozen.

## Interpretation

The no-doc condition strongly preferred the familiar Go language despite being
asked for GOCO. The documentation changed the form of generations but did not
teach the model the absence of a program wrapper. Therefore Phase 1 provides no
evidence for H-001 and cannot estimate a useful documentation ceiling. The
result diagnoses a protocol/elicitation floor that must be repaired on
development tasks before any parameter-adaptation study is interpretable.

## Alternative explanations

The model may have latent GOCO-relevant capability that the prompt failed to
elicit. The language name may be confused with Go. The trusted reference did
not explicitly state that source begins directly with statements and that no
`PROGRAM` wrapper is allowed. A stronger few-shot or grammar-focused context
could change performance, but testing it on the same frozen suite now would be
post-hoc and requires a new protocol/experiment.

## Threats to validity

The paired sample has only 24 tasks; prompts are synthetic; multi-value tasks
depend on delimiter parsing due to a runtime input defect; the document
incorrectly claims recursion support; final-paper tasks were authored and
reference-validated by the researcher; and both conditions hit a floor. The
bootstrap [0,0] reflects observed uniformity, not certainty of no effect.

## What this result DOES support

- The pinned Java 25 compiler artifact is reproducibly buildable.
- It matches 87/88 upstream expectations with one explained stale expectation.
- The research wrapper enforces the specified subprocess boundaries and passes
  its tests.
- Under this exact prompt, the frozen base produced Go rather than valid GOCO.
- Under this exact documentation context, it consistently invented an invalid
  GOCO program wrapper and achieved no executable task success.

## What this result DOES NOT support

It does not support parameterized learning, continual learning, self-learning,
retention, forgetting prevention, autonomous learning, human-like
understanding, model equivalence between conditions, or a general claim that
trusted documentation cannot help.

## Figures/tables produced

`research/tables/phase1_results.csv` reports overall and per-family metrics.
No figure is warranted because every measured rate is zero.

## Artifacts/hashes

- Toolchain: `research/manifests/phase1_toolchain.json`.
- Benchmark: `research/manifests/phase1_benchmark.json`.
- Model: `research/manifests/phase1_model.json`.
- Raw paired result SHA-256:
  `282d2d3f4409ac2cb4374759de710cbe6d82ee0db0a97318c362e0e8b1f565a8`.
- Raw compiler conformance SHA-256:
  `391a1ab31e221bf10c78dfc8789335cad0306db39f000233a90fab7f934b07db`.

## Reproduction commands

```powershell
./scripts/build_compiler.ps1
$env:PYTHONPATH='src'
python -m pytest
python scripts/run_conformance.py --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --manifest vendor/goco/6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e/goco-compiler/tests/tests.json --output research/results/EXP-0001/conformance.reproduction.json
python scripts/validate_benchmark.py --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output research/results/EXP-0002/benchmark_validation.reproduction.json
python scripts/run_phase1_evaluation.py --config research/protocols/phase1_inference_config.json --model .models/Qwen2.5-Coder-1.5B-Instruct-2e1fd397 --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output research/results/<new-experiment-id>/phase1_evaluation.json
```

Reproduction must use a new output path; the original experiment is immutable.

## Decision

**NO-GO for Phase 2 / parameter adaptation.** The compiler and benchmark
infrastructure are usable, but the baseline/documentation experiment is
non-discriminating at a parse-level floor. A separately authorized Phase 1R
must repair and pre-register elicitation using development tasks, then evaluate
on a new frozen suite rather than tuning against these results.

## Implications for the paper

This is a negative pilot result and instrument-finding record. It should not be
presented as evidence about continual learning. It demonstrates why executable
validation and pre-training baselines are necessary: superficially GOCO-like
output in the documentation condition was still invalid on every task.
