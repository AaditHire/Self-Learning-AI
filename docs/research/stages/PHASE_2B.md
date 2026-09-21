# Phase 2B — Multi-seed confirmatory parameter acquisition

Status: **PREREGISTERED; EXECUTION NOT YET STARTED**

Starting commit: `06e5db763ad2af2adc51e9b4709916820b0883a6`

Preregistration commit: `4589be9473283d46cff7920fc1a46208dfa911e1`

## Purpose

Phase 2B tests whether the exploratory Phase 2A no-documentation gain reproduces across three independently trained adapters on fresh training data and a new 128-task confirmatory benchmark with stronger structural separation.

Phase 1T remains failed. Phase 2B does not test sequential learning, replay, EWC, adapter isolation, STABLE, NoRA, autonomous curriculum selection, or any other continual-learning mechanism.

## Frozen design

- Immutable Qwen2.5-Coder-3B-Instruct revision `488639f1ff808d1d3d0ba301aef8c11461451ec5`.
- Exact Phase 2A QLoRA recipe.
- Fresh 200-example training corpus, balanced 25 per family.
- Fresh 128-task confirmatory suite, balanced 16 per family, five hidden cases per task.
- Frozen 64-task non-GOCO regression suite.
- Seeds: `20260921`, `20261007`, `20261103`.
- No best-seed selection; all results are primary.
- Descriptive frozen-base + Candidate C reference excluded from decisions.

The full rule is in `research/protocols/PHASE_2B_FROZEN_CONFIRMATORY_EXPERIMENT.md`; machine-readable settings are in `research/protocols/phase2b_config.json`.

## Pre-training data result

EXP-0020 verifies all 200 training targets over 600 cases and all 128 confirmatory references over 640 cases. There are zero execution failures, zero exact train/evaluation prompt/algorithm/lineage/structural-signature/semantic-operation overlaps, zero normalized-code rejects at 0.98, and zero prior-suite prompt flags at 0.70. The final distance buckets are 3 far, 44 medium, and 81 near. All lower-threshold train/evaluation and prior-suite code/AST flags were manually reviewed. The legacy sealed holdout was not opened.

## Planned records

| Record | Purpose | Status |
|---|---|---|
| EXP-0020 | Data construction, verification, overlap audit | Complete / pre-training pass |
| EXP-0021 | Train seed 20260921 | Not started |
| EXP-0022 | Train seed 20261007 | Not started |
| EXP-0023 | Train seed 20261103 | Not started |
| EXP-0024 | Confirmatory base/adapters/docs evaluation | Not started |
| EXP-0025 | Training-set performance and gaps | Not started |
| EXP-0026 | Non-GOCO regression | Not started |

## Results

To be populated after frozen execution. Required reporting includes every seed, mean/range, family results, train/evaluation gaps, failure taxonomies, paired task analysis, task-cluster bootstrap, structural-distance analysis, regression deltas, protocol deviations, and the conjunctive PASS/FAIL decision.

## Reproduction commands

Commands will use `scripts/train_phase2b_qlora.py`, `scripts/run_phase2b_evaluation.py`, and `scripts/analyze_phase2b.py` against the frozen configuration. Exact executed commands and output paths will be recorded here after execution.

## Boundary

Stop after Phase 2B reporting. Independent review is required before any continual-learning experiment.
