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
- **Status:** TESTED ONCE; BOUNDED EXPLORATORY CLAIM SUPPORTED.
- **Supporting results:** EXP-0017: adapted/no-doc 18/64 (28.125%) versus
  frozen-base/no-doc 0/64, paired gain +28.125 points, bootstrap 95% interval
  [+17.1875, +39.0625], passes in five families. EXP-0018: training tasks
  198/200 (99.0%), exposing a 70.875-point train/held-out gap. EXP-0019: base
  regression 18/24 versus adapter 16/24, below the severe-collapse thresholds.
  Phase 1T remains failed and is not supporting evidence for adaptation.
- **Possible confounders:** synthetic-target memorization, family/template
  correlation, one seed/configuration, public GOCO exposure, quantization,
  exact-match regression sensitivity, and development-set selection.
- **Currently justified:** QLoRA can produce development-set evidence
  consistent with parameterized GOCO behavioral acquisition in this setup.
  This is a one-seed developmental result, not general acquisition evidence;
  the large train/held-out gap and coarse structural correlation require a
  later untouched confirmatory experiment.

## CLM-010

- **Proposed claim:** Across multiple independently trained QLoRA adapters,
  adaptation on verified GOCO examples reproducibly improves no-documentation
  performance on structurally held-out GOCO tasks relative to the frozen base,
  providing evidence of parameterized behavioral acquisition.
- **Evidence required:** The frozen Phase 2B 128-task comparison for all three
  preregistered seeds, task-cluster analysis, structural-distance criterion,
  per-seed family span, training/held-out gaps, and 64-task regression results.
- **Experiment:** EXP-0021 through EXP-0026; EXP-0020 establishes instrument
  integrity.
- **Status:** SUPPORTED WITH EXPLICIT SCOPE LIMITS.
- **Supporting results:** Frozen base/no-doc 0/128; three adapted/no-doc seeds
  65/128, 70/128, and 70/128; mean 53.39% and task-cluster bootstrap 95%
  interval 45.57–61.20 points. Every seed spans all eight families. Medium/far
  mean improvement is 48.94 points. Regression changes are -10.94, -9.38, and
  +1.56 points, with no severe collapse. EXP-0020 through EXP-0026 and
  `research/results/PHASE_2B/report.md` provide the full record.
- **Possible confounders:** synthetic-data regularity, residual shared grammar
  skeletons, public GOCO exposure, quantization/kernel nondeterminism, only
  three seeds, exact-response regression sensitivity, and a potentially large
  training/held-out gap.
- **Currently justified:** The proposed bounded multi-seed parameterized-
  acquisition claim is justified. Large 42.81–49.22 point train/held-out gaps,
  weak strings/composition results, residual grammar-skeleton similarity, and
  smaller regression drops constrain its scope. The result does not justify
  claims of understanding, self-learning, autonomous learning, continual
  learning, catastrophic-forgetting prevention, or general-purpose lifelong
  learning.

## CLM-011

- **Proposed claim:** Naive sequential QLoRA on distinct bounded GOCO
  capabilities acquires A then B but measurably forgets A on frozen EVAL_A.
- **Evidence required:** Three preregistered base→A→A→B trajectories, verified
  structurally audited EVAL_A/EVAL_B, before/after paired A outcomes, B
  acquisition, immutable adapter lineage, and non-GOCO regression.
- **Experiment:** EXP-0027 through EXP-0035; preregistered at
  `18c4c1065bf1e63bb0cdac91a33e01ec1c6a37e6`.
- **Status:** SUPPORTED FOR THE BOUNDED PHASE 3A DISTRIBUTIONS.
- **Supporting results:** Base EVAL_A 0/32; A adapters 29/32, 31/32, 30/32;
  after B-only continuation all 0/32. Mean absolute A forgetting 93.75
  points (task-cluster bootstrap 95% interval 85.42–100), relative retention
  0%; 90 pass→fail seed-task transitions. B rose from 0/32 pre-B in every seed
  to 19/32, 16/32, 8/32. Regression was 47/64 base, 48/64 after A, and
  49/64 after B in each seed. Full record:
  `research/results/PHASE_3A/report.md`.
- **Possible confounders:** All 32 EVAL_A tasks are normalized-code near
  neighbors of training targets; synthetic archetype/boilerplate correlation,
  one A→B order, one recipe/model, three seeds, and narrow regression.
- **Currently justified:** Severe, reproducible A-specific forgetting is
  observed under this exact naive sequential baseline. This does not show
  forgetting prevention, broad GOCO erasure, autonomous learning, or general
  lifelong learning. Replay or other interventions remain unauthorized pending
  independent review.

## CLM-012

- **Proposed claim:** A single fixed-budget 20% A-example replay schedule
  improves net post-B A performance over a fresh seed-matched zero-replay
  A→B control without destroying measured B acquisition.
- **Evidence required:** Three preregistered paired branches from each identical
  A parent; fresh structurally audited A/B task suites; 24-step parity;
  per-task A transitions; B acquisition; frozen non-GOCO regression.
- **Experiment:** EXP-0036 through EXP-0047; preregistered at
  `002395e5dc7916e827eeed3e4806417d27bb5419`.
- **Status:** NUMERICAL ENGINEERING GATE PASS; TASK-LEVEL PRESERVATION NOT
  SUPPORTED.
- **Supporting results:** Naive post-B A 0/32 in every seed; replay 15/32,
  16/32, 16/32, a 48.96-point mean advantage (descriptive paired task-cluster
  bootstrap 95% interval 31.25–65.625). Naive B 8/32 each; replay 9/32,
  8/32, 8/32. Non-GOCO base 47/64; replay 48/64, 47/64, 49/64.
- **Critical counter-evidence:** A-only checkpoints passed 8/32 per seed,
  but both naive **and replay** lost all 24 previously passed A seed-tasks.
  Replay's 47 A passes came entirely from formerly failed tasks. Thus the
  experiment does **not** show preservation of previously acquired A successes,
  even though the preregistered aggregate post-B A gate passed.
- **Possible confounders:** Synthetic correlated archetype variants, compact
  GOCO program boilerplate, 24/32 A train-code neighbors and 24/32 B train-code
  neighbors at the 0.85 threshold, initial A acquisition limited to one
  array-reduction archetype, zero B string-transform passes, one model/recipe/
  order and three seeds, and a narrow 64-item non-GOCO control.
- **Currently justified:** Replay improved *net* post-B A pass@1 in this
  bounded distribution with no measured B or general-control collapse. It
  does not establish task-level forgetting prevention, broad continual
  learning, optimal replay ratio, self-learning, or lifelong learning. Full
  record: `research/results/PHASE_3B/report.md`.
