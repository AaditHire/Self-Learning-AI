# Phase 2B — Multi-seed confirmatory parameter acquisition

Status: **COMPLETE — CONFIRMATORY PASS; GO FOR INDEPENDENT REVIEW**

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

## Experiment records

| Record | Purpose | Status |
|---|---|---|
| EXP-0020 | Data construction, verification, overlap audit | Complete / pre-training pass |
| EXP-0021 | Train seed 20260921 | Complete / pass |
| EXP-0022 | Train seed 20261007 | Complete / pass |
| EXP-0023 | Train seed 20261103 | Complete / pass |
| EXP-0024 | Confirmatory base/adapters/docs evaluation | Complete / confirmatory pass |
| EXP-0025 | Training-set performance and gaps | Complete / diagnostic |
| EXP-0026 | Non-GOCO regression | Complete / no severe collapse |

## Results

The frozen base/no-doc condition passed 0/128. The three adapted/no-doc seeds passed 65/128 (50.78%), 70/128 (54.69%), and 70/128 (54.69%), for a 53.39% mean and 50.78%–54.69% range. Every seed succeeded in all eight families. Frozen base plus Candidate C documentation passed 22/128 (17.19%) and remained descriptive only.

Training-set hidden pass was 200/200, 196/200, and 195/200, leaving held-out gaps of 49.22, 43.31, and 42.81 points. Non-GOCO regression was 47/64 for base and 40/64, 41/64, and 48/64 for the adapters; no drop exceeded the frozen 15-point severe-collapse boundary.

The paired task-cluster bootstrap mean improvement was 53.39 points with a 95% interval of 45.57–61.20 points. Medium/far tasks improved by 48.94 points on average, satisfying the alternative branch of the structural non-domination rule. Every conjunctive criterion passed. There were no post-preregistration protocol deviations or failed training/evaluation runs.

The complete tables, failure comparison, limitations, hashes, and decision are in `research/results/PHASE_2B/report.md`; the machine-readable analysis is `research/results/PHASE_2B/summary.json`.

## Reproduction commands

Commands used `scripts/train_phase2b_qlora.py`, `scripts/run_phase2b_evaluation.py`, and `scripts/analyze_phase2b.py` against `research/protocols/phase2b_config.json`. Exact output paths and the aggregate analysis command are recorded in `research/results/PHASE_2B/report.md`. Raw generations, compiler outputs, hidden tests, checkpoints, hardware records, and curves are preserved in EXP-0021 through EXP-0026.

## Boundary

Stop after Phase 2B reporting. Independent review is required before any continual-learning experiment.
