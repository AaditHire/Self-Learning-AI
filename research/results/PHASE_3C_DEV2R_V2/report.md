# Phase 3C-DEV2R v2 execution: raw results and completion record

**Status:** `DEVELOPMENT_CONSUMED_DESCRIPTIVE_ONLY`. This is an A-only development comparison of frozen ISOLATED and COMPOSITION adapters. It is not a retention, continual-learning, self-learning, or final-paper result. No scientific GO/NO-GO is declared.

## Provenance and execution boundary

- Pre-authorization HEAD: `0aa261cf8effb700cbb7a4ee4fd21bf7d6fdc14c`.
- Authorization and execution commit: `53ac2ca264239d2c74c08aa47533cb6dacb3650c`. Its only diff changed `model_execution_authorized` from JSON boolean `false` to `true` in `research/protocols/phase3c_dev2r_v2_manifest.json`; `status` remained `FROZEN_PRE_EXECUTION`.
- Before model load, 43/43 manifest input hashes, including all v2 suite files, amendment, replacement map, original training sets, runner and evaluator, and all six byte-exact adapter hashes matched. No DEV2R attempt directory existed.
- Six development cells (48 tasks each) ran once. Five pending own-training diagnostics (60 tasks each) ran once. Historical 20270925/ISOLATED own-training was not rerun. Total new model generations: **588**.
- The user-authorized sequence ran the six development cells before the five own-training diagnostics. The original frozen DEV2R protocol describes the reverse order. This is the sole procedural order deviation identified; no task, case, seed, adapter, prompt, generation setting, evaluator, scorer, diagnostic definition, or analysis criterion changed. All cells completed without retry.
- No model-load/API exception, process crash, or incomplete attempt occurred. GOCO parse/compile/runtime/timeout outcomes are task scoring outcomes, tabulated below. Transformers reported that `temperature`, `top_p`, and `top_k` generation flags were invalid and might be ignored; the frozen runner used greedy decoding and was not changed.

## Raw development results

| Seed | Condition | Primitive Sanity /16 | Novel Composition /16 | Structural Transfer /16 | Total /48 |
|---|---|---:|---:|---:|---:|
| 20270925 | ISOLATED | 5/16 | 2/16 | 0/16 | 7/48 |
| 20270925 | COMPOSITION | 7/16 | 14/16 | 0/16 | 21/48 |
| 20271013 | ISOLATED | 4/16 | 4/16 | 0/16 | 8/48 |
| 20271013 | COMPOSITION | 14/16 | 14/16 | 0/16 | 28/48 |
| 20271119 | ISOLATED | 10/16 | 4/16 | 0/16 | 14/48 |
| 20271119 | COMPOSITION | 4/16 | 10/16 | 0/16 | 14/48 |

The original Primitive Sanity specifications all required `-1` for no match, but only **14/16** old frozen tasks exercised that negative output in their cases. The v2 sanity tasks are the prospectively versioned nonnegative-count replacements. Novel Composition and Structural Transfer tasks, references, and cases remained unchanged from v1.

## Paired COMPOSITION minus ISOLATED differences

| Seed | Primitive Sanity pp | Novel Composition pp | Structural Transfer pp | Total pp |
|---|---:|---:|---:|---:|
| 20270925 | +12.50 | +75.00 | +0.00 | +29.17 |
| 20271013 | +62.50 | +62.50 | +0.00 | +41.67 |
| 20271119 | -37.50 | +37.50 | +0.00 | +0.00 |

The frozen primary descriptive contrast is Novel Composition: ISOLATED `10/48` and COMPOSITION `38/48` paired seed-task instances; mean/pooled difference **+58.33 percentage points**. Its three seed differences are `+75.00`, `+62.50`, and `+37.50` points. The pooled transitions are 6 both pass, 6 both fail, 4 ISOLATED-only, and 32 COMPOSITION-only.

The preregistered two-way paired seed/archetype block bootstrap uses 10,000 draws, RNG seed 20270926, resampling paired seeds and whole archetype blocks within group and subskill while retaining all constant variants. Intervals are descriptive 2.5th–97.5th percentiles:

| Scope | Mean difference pp | Descriptive 95% interval pp |
|---|---:|---:|
| Primitive Sanity | +12.50 | [-37.50, +62.50] |
| Novel Composition | +58.33 | [+20.83, +83.33] |
| Structural Transfer | +0.00 | [+0.00, +0.00] |
| All 48 tasks | +23.61 | [+0.00, +43.75] |
| Numeric iteration | +37.50 | [+16.67, +58.33] |
| Array reduction | +9.72 | [-25.00, +36.11] |

These intervals do not supply a significance test or a population-generalization claim. The three seeds and correlated constant variants constrain interpretation.

## Task-level paired transitions

Each entry is `both pass / both fail / ISOLATED-only / COMPOSITION-only`. Full task-ID outcomes are in `task_transitions.json`.

| Seed | Primitive Sanity | Novel Composition | Structural Transfer | All 48 |
|---|---|---|---|---|
| 20270925 | 4 / 8 / 1 / 3 | 2 / 2 / 0 / 12 | 0 / 16 / 0 / 0 | 6 / 26 / 1 / 15 |
| 20271013 | 4 / 2 / 0 / 10 | 3 / 1 / 1 / 11 | 0 / 16 / 0 / 0 | 7 / 19 / 1 / 21 |
| 20271119 | 4 / 6 / 6 / 0 | 1 / 3 / 3 / 9 | 0 / 16 / 0 / 0 | 5 / 25 / 9 / 9 |
| Pooled | 12 / 16 / 7 / 13 | 6 / 6 / 4 / 32 | 0 / 48 / 0 / 0 | 18 / 70 / 11 / 45 |

## Frozen development breakdowns

| Seed | Condition | Numeric /24 | Array /24 | Parse /48 | Compile /48 | Execute /48 | Case 1–5 passes (each /48) |
|---|---|---:|---:|---:|---:|---:|---|
| 20270925 | ISOLATED | 5/24 | 2/24 | 44/48 | 42/48 | 31/48 | 18/9/9/9/8 |
| 20270925 | COMPOSITION | 13/24 | 8/24 | 45/48 | 39/48 | 32/48 | 31/25/23/22/23 |
| 20271013 | ISOLATED | 2/24 | 6/24 | 42/48 | 39/48 | 31/48 | 21/11/11/9/10 |
| 20271013 | COMPOSITION | 16/24 | 12/24 | 46/48 | 42/48 | 35/48 | 33/31/29/28/28 |
| 20271119 | ISOLATED | 6/24 | 8/24 | 47/48 | 45/48 | 37/48 | 28/17/19/16/17 |
| 20271119 | COMPOSITION | 11/24 | 3/24 | 39/48 | 34/48 | 27/48 | 19/14/14/14/14 |

All six cells had `structural_requirements_met=true` for 48/48 rows. Parse, compile, execution, semantic, and timeout failure counts by group/subskill, plus each archetype count and each task’s pass/fail against both frozen nearest-neighbor similarity measures, are in `analysis.json`. No new similarity metric or threshold was introduced.

## Own-training diagnostics

These are in-sample diagnostics and are separate from development performance. The historical first cell used the original DEV2 evaluator; the five new cells used the frozen DEV2R v2 evaluator.

| Seed | Condition | Evaluator | Semantic /60 | Exact target count/rate | Numeric semantic; exact /30 | Array semantic; exact /30 |
|---|---|---|---:|---:|---|---|
| 20270925 | ISOLATED | Historical DEV2 | 60/60 | 43/60 (71.67%) | 30/30; 28/30 | 30/30; 15/30 |
| 20270925 | COMPOSITION | DEV2R v2 | 60/60 | 45/60 (75.00%) | 30/30; 30/30 | 30/30; 15/30 |
| 20271013 | ISOLATED | DEV2R v2 | 60/60 | 45/60 (75.00%) | 30/30; 30/30 | 30/30; 15/30 |
| 20271013 | COMPOSITION | DEV2R v2 | 60/60 | 40/60 (66.67%) | 30/30; 25/30 | 30/30; 15/30 |
| 20271119 | ISOLATED | DEV2R v2 | 60/60 | 45/60 (75.00%) | 30/30; 30/30 | 30/30; 15/30 |
| 20271119 | COMPOSITION | DEV2R v2 | 60/60 | 51/60 (85.00%) | 30/30; 30/30 | 30/30; 21/30 |

Archetype-level semantic performance is 5/5 for every family × `pair1`…`pair6` row in every cell. The exact-target reproduction counts are:

| Family / archetype (each /5) | 20270925 I historical | 20270925 C | 20271013 I | 20271013 C | 20271119 I | 20271119 C |
|---|---:|---:|---:|---:|---:|---:|
| numeric_iteration:pair1 | 5 | 5 | 5 | 5 | 5 | 5 |
| numeric_iteration:pair2 | 5 | 5 | 5 | 5 | 5 | 5 |
| numeric_iteration:pair3 | 5 | 5 | 5 | 5 | 5 | 5 |
| numeric_iteration:pair4 | 3 | 5 | 5 | 0 | 5 | 5 |
| numeric_iteration:pair5 | 5 | 5 | 5 | 5 | 5 | 5 |
| numeric_iteration:pair6 | 5 | 5 | 5 | 5 | 5 | 5 |
| array_reduction:pair1 | 5 | 5 | 5 | 5 | 5 | 5 |
| array_reduction:pair2 | 0 | 0 | 0 | 0 | 0 | 0 |
| array_reduction:pair3 | 5 | 5 | 5 | 5 | 5 | 5 |
| array_reduction:pair4 | 0 | 0 | 0 | 0 | 0 | 5 |
| array_reduction:pair5 | 5 | 5 | 5 | 5 | 5 | 4 |
| array_reduction:pair6 | 0 | 0 | 0 | 0 | 0 | 2 |

## Persistence and provenance audit

- 11/11 expected aggregates, 588/588 raw-generation checkpoints, and 588/588 primary-score checkpoints exist. Each aggregate has the expected unique IDs (48 development or 60 own-training), and its raw generation and hidden-pass value match its primary checkpoint. Every primary contains five compiler-case outcomes. Each new own-training primary contains a boolean exact-target field.
- No attempted task lacks a primary checkpoint. No duplicate generation, retry, crash, partial attempt, or failed model/API/runtime call was observed. GOCO program failures and compiler timeouts are recorded as score outcomes in the raw files.
- The entire 1,187-file runtime evidence tree (5,695,339 bytes) was copied without transformation to `research/artifacts/phase3c-dev2r-v2/raw/evaluations/`. Every copied file matched its runtime source SHA-256 and size. The per-file inventory is `research/manifests/phase3c_dev2r_v2_execution_artifacts.json`.
- After execution, all 43 manifest input hashes and all six adapter-weight hashes still matched. The v2 suite hashes are tasks `9d33db75d40b2013bf45c8aa2c9f2d6d679854c107addb2cbc7eab9f18793d58`, references `0af18bc06a5c5785ca0faa5d396f5edc59ab0509d9e2c8a6310edfd7aba23d80`, and hidden cases `477982b11f6931d2da106958f8e00c0a0d535a32f613ee2585ce8acb729744e9` under the manifest’s LF-normalized text-hash policy.

The frozen adapter SHA-256 values, in manifest order, are:

- `20270925/isolated`: `b063db57ddf9a103b6777e14ef813847e7dff22fafadd38a8107a0e5d837f6b8`
- `20270925/composition`: `fd3a86800cff5c9b90b515b637e15a1b3fa96c372b4499d72a2ff3445cb246d9`
- `20271013/isolated`: `1be74ede1aff8a09caceb9e6011a8a996393ee2c9dd75a7f685ada22b24cf10e`
- `20271013/composition`: `cbe2c5efa295e73100ff5760e64fef0642bf00076b0acf6f2a2a14ab9f90d4b3`
- `20271119/isolated`: `a41fa70c5a59b9010763b37949209651683571213b333dbcf7dd0fea965852ed`
- `20271119/composition`: `e51cd29f262ba7c5332636a01b57e77e83a7de289e8e7b0667096c2277d24198`

The sealed final-paper holdout was not accessed. No gradients, adapter updates, B training, replay, DEV3 design, new threshold, new holdout, or poor-performing-seed rerun occurred. The original DEV2 development suite remains consumed from its earlier attempted use; DEV2R v2 is now development-consumed. Stop for independent scientific review.
