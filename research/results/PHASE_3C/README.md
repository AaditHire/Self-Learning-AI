# Phase 3C frozen execution: acquisition STOP

**Decision: `STOP_before_B_no_tuning`.** The preregistered A eligibility gate failed in all three seeds. No naive or replay B branch was trained or evaluated. This is a completed, preregistered STOP outcome, not a test of the retention hypotheses.

## Raw outcomes and fixed gate

The frozen A eligibility rule requires **each** seed to pass at least 24/32 A tasks overall, 10/16 in each A subskill, and 2/8 in each of four A evaluation archetypes. The runner wrote the [mechanical gate](../../artifacts/phase3c/raw/pre_b_acquisition_gate.json) before any B-stage work.

| Seed | A overall | Numeric iteration | Array reduction | Triangular milestones | Alternating accumulator | Negative position weight | Outer inner gap | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 20260925 | 0/32 | 0/16 | 0/16 | 0/8 | 0/8 | 0/8 | 0/8 | FAIL |
| 20261013 | 7/32 | 7/16 | 0/16 | 7/8 | 0/8 | 0/8 | 0/8 | FAIL |
| 20261119 | 7/32 | 7/16 | 0/16 | 7/8 | 0/8 | 0/8 | 0/8 | FAIL |

The base scored 0/32 on A (0/16 in each subskill). The table above reports the three post-A checkpoints used by the eligibility gate.

Seed `20260925` had no pre-B A PASS IDs. Seeds `20261013` and `20261119` each passed the same seven IDs:

```text
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-02
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-03
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-04
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-05
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-06
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-07
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-08
```

The frozen pre-B B baseline was also run once per seed; it is not B-stage training.

| Condition | B overall | String transform | Field processing | Replace upper prefix | Reverse lower suffix | Combined field length | Select reversed field |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Base | 0/32 | 0/16 | 0/16 | 0/8 | 0/8 | 0/8 | 0/8 |
| Post-A 20260925 | 8/32 | 8/16 | 0/16 | 8/8 | 0/8 | 0/8 | 0/8 |
| Post-A 20261013 | 0/32 | 0/16 | 0/16 | 0/8 | 0/8 | 0/8 | 0/8 |
| Post-A 20261119 | 0/32 | 0/16 | 0/16 | 0/8 | 0/8 | 0/8 | 0/8 |

Non-GOCO scores were base **47/64**, post-A **49/64**, **49/64**, and **48/64** in seed order. No post-A seed dropped more than the frozen severe-collapse boundary of 9/64 relative to base. This is only the post-A portion of H4; the complete H4 comparison requires both B branches and is **undefined** here. The limited suite does not establish general capability preservation.

## Frozen hypothesis and decision status

| Component | Status | Reason |
| --- | --- | --- |
| A eligibility | FAIL | Every seed misses overall, both-subskill, and at least three archetype floors. |
| H1 acquired-task retention | Not evaluated | No B branches; seed 20260925 also has zero acquired A tasks. |
| H2 aggregate post-B A | Not evaluated | No post-B A records. |
| Naive B acquisition floor | Not evaluated | No naive B branch. |
| H3 broad B plasticity | Not evaluated | No B branches. |
| H4 non-GOCO regression | Incomplete | Base and post-A only; no post-B comparisons. |
| Joint Phase 3C | **STOP** | Frozen acquisition gate bars entry to B. |

No PASS→PASS, PASS→FAIL, FAIL→PASS, or FAIL→FAIL post-B transition exists. Retention, forgetting, replay-minus-naive effect sizes, B net gains, 10,000-draw clustered bootstrap intervals, and four-archetype post-B sensitivity analysis are **undefined**. They were not imputed or replaced with a post hoc statistic. Descriptive pre-B counts and failure categories are in the raw records and [failure taxonomy](stop_failure_taxonomy.json).

## Execution and provenance

Execution began from clean pre-execution commit `3c2e2b8ddd12a611fd639bbc32660163f4742a77`, following design commit `a2fb247d090d3d2b00e7fcc4a4f71325723b7086`. The frozen preflight verified 26 design files, 17 execution files, seven tokenizer/model-support files, both base-weight shards, compiler, schedules, package contract, and empty Phase 3C runtime. The actual [environment capture](../../artifacts/phase3c/raw/environment.json) records Windows 11, Python 3.13.0, CUDA 13.0, NVIDIA RTX 3060 Laptop GPU 6 GB, driver 610.74, Temurin JDK 25.0.1, and the package versions. The base was immutable Qwen/Qwen2.5-Coder-3B-Instruct revision `488639f1ff808d1d3d0ba301aef8c11461451ec5`; its two weight hashes match before and after each A run. The compiler SHA-256 was `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`.

Each seed trained its final A adapter once for the frozen three epochs and 24 optimizer steps; gradients ran for these three A runs only. Adapter SHA-256 values were:

| Seed | Adapter SHA-256 |
| --- | --- |
| 20260925 | `30dfe2a087103866fc2b7b8e6d5651b691594c6cc5be4a2eaa517cdfc12e0617` |
| 20261013 | `692823f4aaf95b59a987031dde6f7baa11d8a0b2b2572649e98af8a0d8af883a` |
| 20261119 | `4ed80bd9d3ad37166e211cfa57fbfc57f4226d1cd1e57200962268c4ead176c3` |

The [frozen protocol](../../protocols/phase3c_protocol.md) has SHA-256 `4ca4838522981354ffd6a81bc8cc99a684661ec8e36f2a7ec5e2b990a380b58a`; the [config](../../protocols/phase3c_config.json) has SHA-256 `3d9b1d05d55a5fdfe69a25a4a376b3174f7323e86a5a3a936442d5499b4fe679`; the [schedule](../../protocols/phase3c_replay_schedule.json) has SHA-256 `08e216002c8c8dccdb8d6dd16666dd5bc4a1b82bd5217b3cdf8cc93ec1500e12`. The finalized [artifact manifest](../../artifacts/phase3c/raw/artifact_manifest.json) records 47 produced files and four frozen design inputs; the [preservation manifest](../../manifests/phase3c_artifact_preservation.json) lists 48 runtime files copied for archival, including the artifact manifest itself, three adapter weights, and 12 raw evaluation records.

## Failure taxonomy and interpretation

The [taxonomy audit](stop_failure_taxonomy.json) gives evaluator categories by condition, seed, capability, subskill, and archetype. Its overall counts are:

| Condition | Capability | Success | Syntax | Lexical | Semantic | Runtime | Hidden-test semantic |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Base | A | 0 | 32 | 0 | 0 | 0 | 0 |
| Base | B | 0 | 31 | 1 | 0 | 0 | 0 |
| Post-A 20260925 | A | 0 | 10 | 3 | 10 | 0 | 9 |
| Post-A 20260925 | B | 8 | 5 | 0 | 11 | 8 | 0 |
| Post-A 20261013 | A | 7 | 8 | 0 | 9 | 0 | 8 |
| Post-A 20261013 | B | 0 | 24 | 0 | 8 | 0 | 0 |
| Post-A 20261119 | A | 7 | 8 | 0 | 8 | 0 | 9 |
| Post-A 20261119 | B | 0 | 5 | 0 | 19 | 8 | 0 |

For A, all 14 successes across the last two seeds occur in one eight-task numeric archetype; array reduction has zero successes in every seed. Failure labels describe where observed attempts failed; they do not localize a causal training mechanism. The pre-B B successes in seed `20260925` also occupy one archetype. The result therefore does not demonstrate broad acquisition of either capability.

The data [structural audit](../EXP-0048/structural_overlap_manual_review.md) froze separate training/evaluation archetypes, exact prompt/reference exclusion, lower-threshold similarity diagnostics, and manual review before this execution. Those checks cannot prove independence from all historical or unseen prompts. The hand-constructed suite has only four archetypes per capability and 32 evaluation IDs; the repeated seven PASS IDs emphasize the narrowness of the observed generalization. No similarity threshold or dataset item was changed after the model results.

## Preservation and deviations

The established project GitHub remote stores the three A adapter weights through Git LFS and 45 other runtime files as ordinary Git objects at preservation commit `79ce19cd283a4b4d7aeb3e2052992a6e07db2289`. The normal push to `origin/main` succeeded. A separate fresh shallow clone of that commit retrieved all three LFS weights; the [restore verification](../../manifests/phase3c_remote_restore_verification.json) compared SHA-256 and size for every restored file, committed copy, and untouched `.runtime/phase3c/` original against the preservation manifest: **48/48 PASS, zero failures**. The local originals were not moved or modified. This establishes recoverability from that remote commit, not an independent second provider or a backup of local base-model/JDK caches.

No frozen scientific input or completed Phase 3A/3B artifact was modified. The final-paper sealed holdout was neither opened nor evaluated. No rerun, seed replacement, training change, rescue run, Phase 3D work, or alternate intervention occurred. The runner's nonzero exit was the designed `STOP_before_B_no_tuning` outcome, not a runtime crash.

## What the result supports

Under the frozen Phase 3C setup, the fixed A recipe failed its preregistered meaningful-acquisition standard in all three seeds. The hard gate successfully prevented an uninterpretable B-stage retention comparison. The archived pre-B records permit independent review of this STOP result.

## What the result does not support

It provides no estimate of replay's exact acquired-task retention, aggregate post-B A advantage, broad B plasticity, or complete non-GOCO regression behavior. It does not establish general GOCO mastery, optimal replay ratio, general replay superiority, catastrophic-forgetting prevention, lifelong learning, autonomous learning, or Level D/E/F behavior. The principal unresolved scientific risk is that this fixed A-training recipe does not acquire A broadly on the structurally distinct evaluation suite; resolving that would require a separately reviewed future protocol, not a change to this frozen run.
