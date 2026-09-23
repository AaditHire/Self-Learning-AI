# Phase 3A final report — two-stage naive sequential GOCO learning

Completed 2026-09-23. Starting commit: `1ded323e036cd93813ab165210e0c3dcf32616df`. Preregistration commit: `18c4c1065bf1e63bb0cdac91a33e01ec1c6a37e6`; hash-record follow-up: `84d6696be80e520b6ca3f1a03d1a073f604dabb6`. Frozen configuration SHA-256: `3fb940a6b9a65311904db13f2a834a2729f60826c12c250d966420aaa356a715`.

## Decision and interpretation

This experiment establishes a bounded naive sequential QLoRA baseline with **measurable, severe A forgetting**. A was acquired at 29/32, 31/32, and 30/32, but after B-only continuation every seed scored 0/32 on the identical EVAL_A suite. Mean absolute forgetting is **93.75 percentage points** (range 90.625–96.875), relative retention is **0%** in each seed, and the preregistered task-cluster bootstrap 95% interval for mean forgetting is **85.42–100 points**. The preregistered measurable-forgetting rule passes. All 90 A successes across the three trajectories became failures; the six remaining seed-task instances failed before and after B. B was acquired from a 0/32 pre-B floor to 19/32, 16/32, and 8/32. Non-GOCO regression stayed near its base score (47/64 base, 48/64 after A, 49/64 after B in every seed), arguing against broad exact-response collapse on this limited control.

This is nearly complete forgetting **on the narrow EVAL_A distribution**, not proof that all previously learned GOCO or general programming knowledge was erased. No prevention or recovery method was tested. The result does not establish autonomous learning, self-learning, lifelong learning, or successful continual learning.

## 1–5. Capabilities, preregistration, data, recipe, and seeds

Capability A is numeric iteration and array reduction: counted loops, filtered accumulations/recurrences, and numeric array computations. Capability B is string transformation and delimited-field processing: case conversion, reversal, replacement, splitting, joining, and string predicates. Both use GOCO typed declarations, `INPUT`, and `DISPLAYNL`, while their main data types and semantic operations differ. The choice was made before any Phase 3A model result.

Each capability has 60 fresh training examples (30 per subskill; four archetypes × 15 variants) and a separate frozen 32-task evaluation (16 per subskill; four different archetypes × eight variants). Every item has five compiler-executed semantic cases: 920/920 cases across 184 targets/references passed. The pinned compiler SHA-256 is `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`. The Phase 2B 64-task non-GOCO regression suite was reused unchanged as the longitudinal control. The sealed final-paper holdout was not opened.

The structural audit found zero exact train/evaluation prompt, algorithmic-structure, lineage, structural-signature, or semantic-operation-combination overlap within A or B; zero prompt-neighbor flags at 0.70; zero normalized-code train/evaluation rejects at 0.98; zero exact reuse of consumed evaluation prompts; and zero consumed-reference code flags at 0.98. Lower-threshold flags remain: A has 32/32 near normalized-code neighbors and eight AST-proxy matches; B has 16 near, 16 medium, and 24 AST-proxy matches. Prior consumed-reference neighbors at 0.90 number eight for A and 24 for B. They were manually reviewed before training. Compact GOCO boilerplate and synthetic archetype variants leave substantial effective-task correlation; this limits generalization claims. The complete audit and two retained construction attempts are in `research/results/EXP-0027/`.

The base is immutable `Qwen/Qwen2.5-Coder-3B-Instruct` revision `488639f1ff808d1d3d0ba301aef8c11461451ec5`. Three independent seeds (`20260923`, `20261011`, `20261117`) each followed base → A LoRA adapter → A→B LoRA adapter. B used only the 60 B examples and continued the same seed-matched A LoRA weights, with a fresh optimizer and scheduler; zero A examples were replayed. Adapters were never merged. Both base-weight shard hashes remained unchanged, and each A-parent hash was unchanged by B training. All six runs completed 24/24 steps with finite losses and gradients; no OOM occurred.

The frozen recipe used NF4 4-bit double quantization, FP16 compute, rank-16 LoRA with alpha 32/dropout 0.05/no bias on q/k/v/o and gate/up/down projections, three epochs, micro-batch 1, gradient accumulation 8, maximum length 320, gradient checkpointing, PagedAdamW8bit, learning rate 0.0002, linear schedule with five warmup steps, and maximum gradient norm 1. The final epoch was selected a priori; there was no checkpoint, prompt, seed, or hyperparameter search. Training took 186/229/260 seconds for A and 179/223/225 seconds for B by seed. Detailed lineage and adapter SHA-256 values are in EXP-0028–EXP-0033.

## 6–11. Acquisition, forgetting, and retention

All scores are no-documentation greedy task-level hidden-test pass@1. Base EVAL_A was 0/32 (all syntax failures). EVAL_B before B training was measured on the A adapter; there was no B success in any seed.

| Seed | Base→EVAL_A | A→EVAL_A before B | A→EVAL_B before B | A→B→EVAL_B | A→B→EVAL_A | Absolute A forgetting | Relative A retention |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 20260923 | 0/32 | 29/32 (90.625%) | 0/32 | 19/32 (59.375%) | 0/32 | 90.625 pp | 0% |
| 20261011 | 0/32 | 31/32 (96.875%) | 0/32 | 16/32 (50.000%) | 0/32 | 96.875 pp | 0% |
| 20261117 | 0/32 | 30/32 (93.750%) | 0/32 | 8/32 (25.000%) | 0/32 | 93.750 pp | 0% |
| Mean | 0% | 93.750% | 0% | 44.792% | 0% | 93.750 pp | 0% |

EVAL_A subskill passes before→after B were numeric iteration 13→0, 15→0, 14→0 of 16; array reduction 16→0 in all seeds. Thus both A subskills lost all measured passes. EVAL_B after B was string transformation 11/16, 8/16, 0/16, and field processing 8/16 in every seed. B acquisition is heterogeneous and not complete.

Paired EVAL_A transitions were: seed `20260923` 29 pass→fail and three fail→fail; seed `20261011` 31 pass→fail and one fail→fail; seed `20261117` 30 pass→fail and two fail→fail. There were zero pass→pass and zero fail→pass transitions. Of the 32 distinct tasks, 29 were passed before B in all three seeds and failed after B in all three; two were passed before B in some seeds and failed after; one was never passed. These are 32 task clusters observed under three independently trained models, not 96 independent tasks.

The task-cluster bootstrap resampled those 32 paired tasks 10,000 times, carrying each task's three seed outcomes together. Its 95% interval for mean absolute forgetting is 85.42–100 points. A acquisition was nonzero in every seed, the mean drop is positive, and the interval excludes zero, satisfying the frozen measurable-forgetting rule. “Severe” is warranted for this bounded distribution because the drop is large and systematic; any unqualified claim about catastrophic forgetting across all GOCO capabilities would overreach.

## 12–14. Regression, failures, and deviations

| Condition | Base | After A, each seed | After A→B, each seed |
|---|---:|---:|---:|
| Frozen non-GOCO exact-response accuracy | 47/64 (73.44%) | 48/64 (75.00%) | 49/64 (76.56%) |

The small regression score increases by one item at each stage. This control does not prove preservation of general capability; it only shows no measured collapse on these 64 format-sensitive items. It separates the dramatic EVAL_A loss from a generalized inability to answer this particular non-GOCO suite.

Before B, A adapters generated valid, executable GOCO for all 96 seed-task EVAL_A instances; six failed hidden semantics. After B, EVAL_A had 46 syntax, 29 semantic-validation, 12 runtime, eight hidden-test-semantic, and one lexical failure across the 96 seed-task instances. Several numeric-task generations visibly used B-style `strings.SPLIT`/`strings.COUNT` scaffolds, consistent with interference in the shared adapter; this is a qualitative observation, not a mechanistic localization. EVAL_B after B had 43 successes, 27 hidden-test-semantic failures, 15 semantic-validation failures, six lexical failures, and five syntax failures across seed-task instances. The raw per-task generations and compiler case records are retained in EXP-0034.

There were **no post-freeze methodological deviations**: no data, prompt, model, seed, training recipe, scoring rule, or checkpoint selection changed. A post-freeze dispatch wrapper (`scripts/run_phase3a_remaining.py`) only invoked the already frozen train/evaluation scripts in the specified order for seeds two and three; it did not alter any hashed input or model method. Two data-construction audit attempts are retained from before the preregistration commit; both were resolved before gradients. All specified conditions completed once, with no model-evaluation retry or manual repair.

## 15–18. Evidence, limits, decision, and next baseline recommendation

Supported: reproducible bounded A acquisition from an immutable base; B acquisition from the A checkpoint; quantitative, task-paired severe A forgetting after B-only QLoRA; and a naive sequential-learning baseline with explicit adapter lineage. The loss is not explained by measured broad degradation on the frozen non-GOCO control.

Not supported: broad continual-learning ability, any forgetting prevention, replay or EWC success, autonomous/self-directed learning, lifelong learning, or retention outside the evaluated A distribution. The data are synthetic and heavily archetype-structured, with A EVAL_A entirely in the normalized-code “near” bucket. Three seeds, one training recipe, one capability order (A then B), and one fixed small model/hardware stack limit external validity. No B→A order reversal or multi-stage durability test was performed. The baseline is not a causal comparison among anti-forgetting methods.

**Measurable forgetting exists** under the frozen rule. For independent review, the recommended *first future* anti-forgetting comparator is a minimal, fixed-budget A-example replay baseline against this exact naive sequence, because it directly tests whether occasional A supervision can reduce the observed interference with few new components. Pre-register the replay fraction, schedule, seeds, acceptance criteria, and a fresh non-consumed evaluation before running it. This is a recommendation only; **no replay or other intervention begins in Phase 3A**.

## 19. Finalization

An independent completion verifier checked all 23 frozen input hashes, both base-weight shards, six training records, 20 evaluation conditions, adapter-parent hashes, and paired counts; all passed (`completion_verification.json`). The repository's 13 tests and Python syntax checks pass. The final Git commit is recorded in the completion message. The project stops after this report for independent Phase 3A review.
