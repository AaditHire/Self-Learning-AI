# Claims ledger

No claim below is currently justified by experimental evidence.

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
- **Currently justified:** No. The all-syntax-error floor makes the comparison
  non-discriminating; it does not justify a claim that documentation is
  generally ineffective.

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
