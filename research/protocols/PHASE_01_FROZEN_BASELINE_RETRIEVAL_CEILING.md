# Phase 1 protocol — Frozen Baseline + Documentation Ceiling

Status: **FROZEN BEFORE INFERENCE — 2026-09-20T11:55:48+05:30**
Execution authorized by the user. Machine-readable configuration SHA-256:
`7a6ab3e3fcd335be8674a22dde74d137b7c04b5632eabea3229b7f9319fc7584`.

## Objective

Create a pinned GOCO execution oracle and frozen, unseen evaluation suite, then
compare an immutable base model with no GOCO documentation against the same
model with trusted GOCO documentation available. No parameter training occurs.

## Research question

How much GOCO capability does the frozen base model exhibit without documents,
and what performance ceiling is provided by controlled access to trusted GOCO
documentation on the same unseen tasks?

## Hypothesis

The docs condition will improve hidden-test pass@1 over no docs, especially on
GOCO-specific syntax, while neither condition will achieve perfect semantic
correctness.

## Why this experiment exists

It measures base-model knowledge and the controlled documentation ceiling before
parameter adaptation. Without this baseline, later no-doc adapter performance
cannot be interpreted as persistent learning.

## Inputs

Inputs are the pinned compiler snapshot, the 24-task frozen evaluation split,
the trusted documentation snapshot, the immutable base-model snapshot, fixed
prompt files, and `research/protocols/phase1_inference_config.json`.

## Exact model/revision

`Qwen/Qwen2.5-Coder-1.5B-Instruct` at Hub commit
`2e1fd397ee46e1388853d2af2c993145b0f1098a`. The safetensors SHA-256 is
`c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`.
Inference uses unquantized FP16 on CUDA with all gradients disabled.

## Exact dataset/manifests

The benchmark contains 8 development, 24 frozen-evaluation, and 8 sealed
final-paper tasks across eight families. Exact hashes are in
`research/manifests/phase1_benchmark.json`. The documentation SHA-256 is
`e9fca4fc1cea7737923e7429a3c7d46370f1c11bd794e55680813a7536cdc5c4`.

## Compiler revision

Planned source is GOCO commit
`6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`, compiler Git tree
`f51973617cc3da8c78de88c668d8de6959575d6d`. The Temurin 25.0.1 runtime JAR
SHA-256 is
`c6f45759930438dd4ae7bfbff298e9c7242604582d29da04210f15377f2be879`.

## Training configuration

None. Phase 1 performs inference only and must not update model parameters.

## Evaluation protocol

Run both conditions on the same task IDs and pre-registered seed schedule. Store
raw generations without manual repair, execute each in the pinned sandboxed
compiler, and score only through frozen hidden semantic tests. Log prompt,
retrieved context, token counts, raw streams, diagnostic class, runtime, and
test outcomes for every attempt.

## Prerequisites to freeze

- extracted compiler snapshot passes conformance at a recorded Java version;
- wrapper and isolation tests pass;
- exact `Qwen/Qwen2.5-Coder-1.5B-Instruct` revision/hash is recorded;
- benchmark families, generators, and hidden tests are reviewed and frozen;
- contamination/deduplication audit is recorded;
- prompts, trusted-doc corpus, retrieval policy, decoding, seeds, and thresholds
  are fixed before inference;
- final paper holdout remains sealed and is not used in Phase 1.

## Conditions

1. `BASE_NO_DOCS`: frozen base, no GOCO docs, no retrieval, no updates.
2. `BASE_WITH_DOCS`: identical frozen base and decoding, trusted GOCO docs
   supplied under a frozen retrieval/context policy, no updates.

The full four-cell matrix is not claimed until adapted conditions exist. Phase 1
establishes only the first two cells.

## Proposed benchmark design

Derive actual capability families from the pinned GOCO grammar and semantics.
Candidate families for review are declarations/arithmetic/output, branching,
loops, functions, arrays, and libraries. Hold out entire semantic/structural
families rather than randomly splitting generated siblings. Include basic,
structural, compositional, adversarial/near-valid, and invalid-program cases.

Each task must have a public prompt/specification and hidden executable tests.
The model must never see hidden tests. A compile-only pass is insufficient.

## Frozen metrics decided BEFORE the experiment

- primary: hidden semantic-test pass@1;
- secondary: parse success, semantic-validation success, execution success,
  exact-output accuracy where applicable;
- slice metrics: basic, structural, compositional, adversarial, invalid-program;
- paired difference and uncertainty interval between conditions;
- inference time, prompt tokens, completion tokens, and compiler failure class.

Primary inference is greedy (`do_sample=false`, one beam), with at most 8,192
input tokens and 512 new tokens, EOS stopping, and no retry. The paired effect
is the docs-minus-baseline task pass-rate difference. Its 95% interval uses
10,000 paired task bootstrap resamples with seed 20260920. A two-sided exact
McNemar test is reported on discordant pairs and interpreted cautiously.

## Expected outcomes

The docs condition is expected to outperform no docs on GOCO-specific syntax
and semantics, while failures in both conditions should reveal benchmark and
prompt weaknesses before any training begins.

## Actual results

NOT RUN. This section must be completed without rewriting the frozen protocol.

## Failed experiments

NOT RUN. Preserve all failures here and in the experiment registry.

## Deviations from protocol

NOT RUN. Any deviation must be timestamped and justified before interpreting
results.

## Interpretation

Pending. A docs-condition improvement would establish a retrieval/context
ceiling, not parameter learning. Strong no-doc performance would indicate base
knowledge or possible pretraining exposure and must be investigated.

## Alternative explanations

Potential alternatives include prompt-length effects, benchmark leakage,
pretraining exposure, retrieval of solution-like material, decoding variance,
and weaknesses in hidden semantic tests.

## Threats to validity

Primary risks are task-family leakage, unsealed tests, unequal context budgets,
compiler/runtime defects, small correlated samples, and repeated tuning against
the frozen suite. See `docs/research/THREATS_TO_VALIDITY.md`.

## What this result DOES support

If executed successfully, it can support claims about measured frozen-base GOCO
performance and the incremental benefit of controlled trusted documentation on
this benchmark and model revision.

## What this result DOES NOT support

It cannot support parameter learning, continual learning, retention,
catastrophic-forgetting mitigation, autonomous gap detection, or broad
self-improvement claims.

## Figures/tables produced

Planned: a paired condition table, capability-slice table, and failure-category
plot. Exact filenames are assigned only when experiment IDs are frozen.

## Artifacts/hashes

Pending model, compiler-build, dataset, docs-corpus, prompt, configuration,
generation, and result manifests.

## Reproduction commands

TODO after Phase 1 implementation. Commands must use only pinned inputs and
write to new immutable experiment directories.

## Integrity controls

- randomize or blind condition evaluation order where practical;
- use identical task IDs and seed schedule in both conditions;
- log the exact documents/chunks included for every docs-condition sample;
- prevent docs from containing benchmark solutions or generator templates;
- hash prompts, outputs, docs corpus, compiler, tests, and configurations;
- prohibit manual repair of model outputs before scoring;
- quarantine development tasks from promotion tasks.

## Expected artifacts

- pinned compiler source/build manifest and conformance report;
- research-owned compiler wrapper with tests;
- benchmark taxonomy, dataset cards, generators, and split manifests;
- sealed hidden-test package or access-controlled equivalent;
- trusted documentation corpus manifest;
- model and inference configuration manifests;
- raw generations and compiler/test traces;
- paired results table and Phase 1 research record.

## Decision

GO only if the compiler oracle is reproducible, hidden tests discriminate
semantic correctness, both conditions complete under identical controls, and no
material leakage is found. Otherwise record a conditional GO or NO-GO and do
not proceed to adapter training.

## Implications for the paper

Phase 1 should provide the indispensable base-knowledge and documentation-ceiling
comparison. It is a prerequisite for, not evidence of, persistent parameter
adaptation.
