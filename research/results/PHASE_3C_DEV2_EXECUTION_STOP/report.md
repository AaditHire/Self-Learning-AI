# Phase 3C-DEV2 execution STOP after evaluator defect

**Status:** `STOP_EVALUATION_CODE_DEFECT_NO_RETRY`. The frozen A-only training contract ran to completion for all six cells. The development comparison did **not** complete. No DEV2 primary effect or Primitive Sanity, Novel Composition, or Structural Transfer result is available. No B training, replay, retention testing, or sealed final-paper holdout access occurred.

## Pre-gradient contract

Preflight was recorded at `.runtime/phase3c_dev2/preflight.json` and preserved in the partial artifact manifest. It verified the frozen design commit `886cf3c69c2babb3f735776ab7b28ce36b2de62d`, clean tree, 20 normalized design-file hashes, compiler, two immutable backbone weights, tokenizer/support files, package contract, three seeds, paired 60-ID/180-slot/24-step schedules, all 168 passing references and 840 semantic cases. All eight primitive containing-example frequencies and reference occurrence counts matched between conditions, as did eight audited GOCO syntax/API construct counts. All essential primitives for the 32 central development tasks were represented in both conditions.

The critical novelty assertion passed for **16/16** Novel Composition IDs. Each frozen signature and reference body contains two ordered predicate intersections using four covered primitives. The ISOLATED and COMPOSITION training references contain one nested pair plus a simple count, and no training ID has the same full two-intersection signature. This is stronger than exact prompt/reference non-overlap; it remains a bounded semantic-signature check rather than proof of independent problem distributions.

Per epoch, ISOLATED used **14,235 full tokens** and COMPOSITION **14,620**: COMPOSITION had **385 more, +2.7046%** relative to ISOLATED. Supervised target tokens were **6,630 in each**. Every sequence fit the 320-token limit. The residual 2.70% full-token imbalance was frozen and not corrected. All 60 ISOLATED training examples contain the redundant nested P-within-P guard; zero COMPOSITION examples contain that redundant guard. Prompt semantics, target relation and run-time difficulty necessarily differ despite matched audited primitive/API counts. These remain interpretation limits.

## Six completed training runs

All runs used the pinned Qwen2.5-Coder-3B-Instruct revision and QLoRA recipe, three epochs, 180 slots, 24 optimizer steps, final checkpoint rule and unchanged base weights. Each saved record includes per-step loss, gradient norm, learning rate, elapsed time, token counts, environment, adapter SHA-256, and before/after base hashes. All six report `nan_inf_oom=false`; no rescue run, seed replacement, extra epoch or hyperparameter change occurred.

| Seed | Condition | Steps | Full / supervised tokens | Training time (s) | First → final logged mean micro-loss | Maximum logged gradient norm | Adapter SHA-256 |
|---|---|---:|---:|---:|---:|---:|---|
| 20270925 | ISOLATED | 24 | 42,705 / 19,890 | 218.4 | 1.5280 → 0.0025 | 1.2719 | `b063db57ddf9a103b6777e14ef813847e7dff22fafadd38a8107a0e5d837f6b8` |
| 20270925 | COMPOSITION | 24 | 43,860 / 19,890 | 325.6 | 1.4839 → 0.0031 | 1.3967 | `fd3a86800cff5c9b90b515b637e15a1b3fa96c372b4499d72a2ff3445cb246d9` |
| 20271013 | ISOLATED | 24 | 42,705 / 19,890 | 348.7 | 1.4952 → 0.0037 | 1.3331 | `1be74ede1aff8a09caceb9e6011a8a996393ee2c9dd75a7f685ada22b24cf10e` |
| 20271013 | COMPOSITION | 24 | 43,860 / 19,890 | 346.2 | 1.4512 → 0.0058 | 1.1884 | `cbe2c5efa295e73100ff5760e64fef0642bf00076b0acf6f2a2a14ab9f90d4b3` |
| 20271119 | ISOLATED | 24 | 42,705 / 19,890 | 360.4 | 1.5552 → 0.0019 | 1.1921 | `a41fa70c5a59b9010763b37949209651683571213b333dbcf7dd0fea965852ed` |
| 20271119 | COMPOSITION | 24 | 43,860 / 19,890 | 404.8 | 1.5021 → 0.0035 | 1.2497 | `e51cd29f262ba7c5332636a01b57e77e83a7de289e8e7b0667096c2277d24198` |

## Evaluation performed and failure

The first own-training evaluation, seed `20270925` ISOLATED, completed its frozen 60-ID pass: **60/60** hidden-semantic pass@1, **30/30** numeric, **30/30** array, all twelve training archetypes **5/5**, and **43/60** exact target reproductions. All 60 outcomes were saved with generated source and five case results each. This is one seed-condition's in-sample fit only; the other five own-training cells were not evaluated.

The first shared development evaluation then attempted task `P3CDEV2-EVAL-NU-SANITY1-31` for the same adapter. Greedy generation and five GOCO compiler-case executions occurred, but `score_source` raised `KeyError: 'difficulty'` while constructing the score summary. The committed evaluator passed the frozen DEV2 task row directly to the scorer; the row has no `difficulty` field. The scorer requires `task["difficulty"]`. The generated text and case results were **not persisted**, and no development output or checkpoint file was written. The evaluation process stopped immediately; no other development task or adapter was evaluated.

The frozen protocol calls for one pass without retry or repair. Repeating that generated task after fixing the evaluator would violate that execution boundary. The error is recorded in `.runtime/phase3c_dev2/incident.json` and the available records are preserved. The DEV2 development suite is treated as **development-consumed from this attempted use**. Independent review must decide any future path; this run does not silently resume or replace the missing observation.

## Unavailable outcomes and interpretation

Primitive Sanity `/16`, Novel Composition `/16`, Structural Transfer `/16`, paired seed differences, bootstrap intervals, development subskills/archetypes, failure-stage distributions, and development nearest-neighbor/pass relationships are **unavailable**. The pre-gradient structural-neighbor table remains frozen and valid as design metadata, but there are no saved development outcomes with which to compare it. No development winner, primary effect, significance or paper-level PASS is reported.

**What this result supports:** the frozen pre-gradient contract passed; all six adapters completed their specified training; one ISOLATED seed fit its own 60 training examples under the frozen scorer. **What it does not support:** any claim that COMPOSITION improves novel-combination transfer, comparable Primitive Sanity acquisition, structural transfer, broad GOCO mastery, continual learning, replay, forgetting prevention, or confirmatory scientific success. Low final training losses do not substitute for the missing five own-training evaluations or any development evaluation.

The available adapters and records are inventoried in `research/manifests/phase3c_dev2_partial_artifact_preservation.json`. They were pushed to the configured GitHub/Git LFS remote in artifact commit `9eadaa00ad350593bd799bad7d7b9e178d250ff7`. A separate fresh clone restored **all 70 available artifacts**, including six adapter weights; every restored size and SHA-256 matched the manifest, local copy, and unchanged original. JSON files parsed and restored adapter safetensors headers/keys opened. The complete verification is `research/manifests/phase3c_dev2_partial_remote_restore_verification.json`. Archival of **available** artifacts is complete; the unsaved first development generation/case result and unrun evaluation cells do not exist to preserve. **STOP for independent scientific review.**
