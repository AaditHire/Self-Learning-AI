# Claims ledger

Claims below are limited to the exact evidence and scope stated. No training or
continual-learning claim is currently justified.

## CLM-001

- **Proposed claim:** Trusted GOCO documentation improves frozen-model
  performance on unseen GOCO tasks.
- **Evidence required:** Frozen base + docs/RAG versus frozen base/no docs on the
  same untouched suite with fixed decoding and prompt budgets.
- **Experiment:** EXP-0003 (`BASE_NO_DOCS`) and EXP-0004
  (`BASE_WITH_DOCS`).
- **Status:** TESTED ONCE; NOT SUPPORTED UNDER THE FROZEN PHASE 1 PROTOCOL.
- **Supporting results:** `research/results/EXP-0003-0004/phase1_evaluation.json`
  and `summary.json`. Both conditions passed 0/24 tasks.
- **Possible confounders:** prompt-length effects, retrieval leakage, benchmark
  contamination, decoding variance.
- **Phase 1R development evidence:** EXP-0006 tested three corrected fixed-
  context candidates on a new engineering-only suite. The best candidate
  passed 3/24 tasks versus 0/24 without docs, but failed the preregistered 25%
  assisted-pass and 15-point-improvement gate. No confirmatory suite or A/B run
  followed.
- **Currently justified:** No confirmatory claim. Phase 1R supports only the
  narrower engineering observation that corrected context elicited three
  executable development successes and eliminated the universal `PROGRAM`
  wrapper; it does not establish a reliable retrieval ceiling or general
  documentation benefit.

## CLM-002

- **Proposed claim:** Parameter adaptation improves unseen GOCO performance
  without access to documentation.
- **Evidence required:** Adapted/no docs versus frozen base/no docs on semantic,
  structural, and compositional holdouts.
- **Experiment:** Future first adaptation phase.
- **Status:** NOT YET TESTED.
- **Supporting results:** None.
- **Possible confounders:** train/test template overlap, base pretraining
  exposure, prompt drift, cherry-picked seeds.
- **Currently justified:** No.

## CLM-003

- **Proposed claim:** The observed gain reflects generalization rather than
  memorization.
- **Evidence required:** Gains on lineage-separated structural and
  compositional holdouts plus deduplication audit.
- **Experiment:** Future adaptation and generalization phase.
- **Status:** NOT YET TESTED.
- **Supporting results:** None.
- **Possible confounders:** hidden generator overlap and undocumented GOCO
  material in pretraining.
- **Currently justified:** No.

## CLM-004

- **Proposed claim:** Replay reduces catastrophic forgetting during sequential
  GOCO capability learning.
- **Evidence required:** Pre-registered naive sequential LoRA versus multiple
  replay ratios across identical task order, seeds, compute, and evaluations.
- **Experiment:** Future continual-learning baseline phase.
- **Status:** NOT YET TESTED.
- **Supporting results:** None.
- **Possible confounders:** extra tokens/compute, replay sample quality, task
  order, unequal convergence.
- **Currently justified:** No.

## CLM-005

- **Proposed claim:** A stability gate prevents promotion of updates with
  unacceptable forgetting.
- **Evidence required:** Frozen thresholds, independently evaluated candidates,
  retained rejection records, and counterfactual outcomes without gating.
- **Experiment:** Future promotion-gate phase.
- **Status:** NOT YET TESTED.
- **Supporting results:** None.
- **Possible confounders:** thresholds tuned after observation, repeated access
  to promotion tests, gate overfitting.
- **Currently justified:** No.

## CLM-006

- **Proposed claim:** The system can objectively identify its own missing GOCO
  capabilities.
- **Evidence required:** Pre-registered gap-detection labels and precision,
  recall, calibration, and curriculum-utility comparisons against baselines.
- **Experiment:** Future self-directed-learning phase; not authorized.
- **Status:** OUT OF CURRENT SCOPE / NOT YET TESTED.
- **Supporting results:** None.
- **Possible confounders:** evaluator leakage, self-scoring bias, benchmark
  familiarity, selective abstention.
- **Currently justified:** No.

## CLM-007

- **Proposed claim:** Frozen-model GOCO failure can be localized to a specific
  capability level, and a larger frozen backbone may change the synthesis
  ceiling.
- **Evidence required:** The preregistered balanced Phase 1S diagnostic under
  identical Candidate C elicitation, with exact model revisions and per-level,
  per-family compiler-backed scoring.
- **Experiment:** EXP-0009 and conditional EXP-0010.
- **Status:** TESTED ONCE; BOUNDED DIAGNOSTIC CLAIM SUPPORTED.
- **Supporting results:** EXP-0009: 1.5B recognition 13/24 and executable hidden
  pass 4/72, with 66/72 lexical/syntax failures. EXP-0010: 3B recognition 17/24
  and executable hidden pass 28/72; full synthesis 7/24 across five families.
- **Possible confounders:** matched-scenario dependence, quantization mismatch,
  model-scale architectural differences, prompt length, and small family cells.
- **Currently justified:** Under the fixed Phase 1S protocol, the
  Qwen2.5-Coder-3B NF4 configuration materially outperformed the
  Qwen2.5-Coder-1.5B FP16 configuration. The result does not isolate a causal
  parameter-count effect; precision, parameter count, and generation regime are
  confounded, and it does not authorize training.

## CLM-008

- **Proposed claim:** The exact frozen 3B NF4 configuration supplies a
  reproducible documentation-assisted GOCO baseline suitable for a separately
  controlled parameter-acquisition experiment.
- **Evidence required:** Fresh paired Phase 1T no-docs/Candidate-C results that
  pass all three preregistered criteria without a major integrity failure.
- **Experiment:** EXP-0012; EXP-0013 is secondary context only.
- **Status:** TESTED ONCE; CONJUNCTIVE GATE FAILED.
- **Supporting results:** EXP-0012: 3B no docs 0/64; Candidate C 14/64
  (21.875%); paired difference +21.875 points, bootstrap 95% interval
  [+12.5, +32.8125] points; 14 docs-only and zero baseline-only wins; passes
  in five families. EXP-0013: matched-NF4 1.5B Candidate C 4/64 (secondary).
- **Possible confounders:** fixed-context length, public GOCO exposure,
  structural correlation, one greedy run, quantization kernels, and benchmark
  representativeness.
- **Currently justified:** The frozen 3B no-doc and Candidate-C baselines are
  reproducible for Phase 1T, and Candidate C materially improves this exact
  configuration. Operational-backbone suitability is not supported because
  21.875% misses the preregistered 25% criterion. Phase 1T did not authorize
  Phase 2; the later Phase 2A pilot is a separate exploratory authorization.

## CLM-009

- **Proposed claim:** QLoRA can produce development-set evidence consistent
  with parameterized GOCO behavioral acquisition in this setup.
- **Evidence required:** Frozen Phase 2A base/no-doc versus adapter/no-doc on
  lineage-separated tasks, verified targets, training/held-out gap, paired
  outcomes, and non-GOCO regression.
- **Experiment:** EXP-0015 through EXP-0019.
- **Status:** PREREGISTERED EXPLORATORY PILOT; NOT YET TESTED.
- **Supporting results:** None at freeze time. Phase 1T remains failed and is
  not supporting evidence for parameter adaptation.
- **Possible confounders:** synthetic-target memorization, family/template
  correlation, one seed/configuration, public GOCO exposure, quantization,
  exact-match regression sensitivity, and development-set selection.
- **Currently justified:** No parameter-acquisition claim. Even a Phase 2A
  pass requires a later untouched confirmatory experiment.
