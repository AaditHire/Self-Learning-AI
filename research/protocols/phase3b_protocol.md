# Phase 3B preregistration: fixed-budget experience replay

Status: frozen before any Phase 3B gradients or model evaluations. Start from Phase 3A final commit `000311f724155d0a643d99bff22c6cac848a15be`.

## Question and scope

Can a single, fixed 20% replay of A examples during B training preserve more A capability than a fresh seed-matched naive A→B control without preventing B acquisition? This is one intervention, not a method search. Phase 3A results motivate but do not contribute evaluation observations to Phase 3B. No EWC, NoRA, adapter isolation, gating, STABLE, or other strategy is included. The final-paper holdout stays sealed.

## Frozen design

- Model: pinned `Qwen/Qwen2.5-Coder-3B-Instruct` revision and immutable local weights from the frozen config. GOCO compiler: pinned deterministic jar from earlier phases. The GOCO product checkout is read-only.
- Capabilities: A numeric iteration/array reduction; B string transformation/field processing. New Phase 3B datasets: 60 training examples and 32 held-out evaluation tasks per capability, with five compiler-verified semantic cases per item. The validation audit checks against consumed development/evaluation prompts and reference code. Shared language constructs and structurally close templates remain a documented limitation.
- Seeds: 20260924, 20261012, 20261118. For each seed, train A once from the same base with the same three-epoch QLoRA recipe as Phase 3A. Both B branches continue that **same** seed-matched A adapter, with separately reset optimizer and scheduler. No A-stage model or evaluation result is borrowed from Phase 3A.
- B budget: exactly 60 micro examples per epoch and 24 optimizer steps per branch. Naive B uses all 60 B IDs each epoch. Replay B replaces 12 B positions (six from each B subskill) with 12 A IDs (six from each A subskill) per epoch. Thus replay sees 48 B and 12 A examples, not 60 B plus extras. Thirty-six unique A IDs per seed appear across the three replay epochs. The deterministic per-seed positions and ID orders are in `phase3b_replay_schedule.json`. The two B branches share their B ordering; the replay branch only replaces selected slots. No replay ratio or example is selected by observed model performance.
- Training: 4-bit NF4 QLoRA, LoRA rank 16/alpha 32/dropout .05 on the seven frozen projection modules, three epochs, micro batch 1, gradient accumulation 8, max sequence length 320, PagedAdamW8bit learning rate 0.0002, linear scheduler with five warmup steps, final-epoch adapter only. No checkpoint or seed selection by evaluation score.
- Prompt/evaluation: identical frozen Phase 1T system/user templates, greedy one-pass decoding (`do_sample=false`, one beam), no documentation/search, no repair or retry. Primary score is task-level pass@1: all five hidden semantic cases must pass. Evaluate the base on fresh A and B and frozen 64-item non-GOCO regression; each A checkpoint on fresh A, B, and regression before B; each naive and replay B checkpoint on fresh A, B, and regression after B. No preliminary evaluation may alter any frozen setting.

## Decision rule, frozen before gradients

Use three-seed unweighted mean post-B EVAL_A pass rates. **PASS** requires all of:

1. Replay mean post-B A exceeds naive mean post-B A by **at least 20 percentage points** (primary endpoint).
2. Naive mean post-B B is strictly positive, and replay mean post-B B is **at least 75%** of it.
3. For every seed, replay's non-GOCO score is no more than **9 of 64 items** below either the same-seed naive score or the single frozen base score. This operationalizes “no severe regression” as a drop of less than 15 percentage points versus both comparators.

Any unmet requirement is **FAIL**. Report exact counts and differences even on failure; do not change the gate. Also report per-seed A immediately after A, per-seed B before B, A forgetting/retention under both branches, paired pass/fail transitions, and a task-cluster bootstrap 95% descriptive interval for the replay-minus-naive A difference (resample 32 task IDs, preserving the three seed observations within each sampled task; 10,000 draws, seed 20261220). The bootstrap interval is descriptive and does not override the gate. Seeds and tasks are not 96 independent replicates. If A acquisition is zero, retention-based interpretation is limited, but the gate is still computed.

## Storage and stopping

All checkpoints, adapters, in-progress generations, and mutable intermediate records live under gitignored `.runtime/phase3b/`, which is explicitly outside LFS. Publish only compact, immutable final records to `research/results/` once runs are complete. Local runtime adapters remain untracked; do not move them into Git/LFS unless a concrete preservation need is independently established. Do not run Git GC/prune or alter `.git` history. Verify source hashes, lineage, compute parity, complete task IDs, and compiler reference checks before publication. Report a final PASS/FAIL and **STOP** for independent review; do not start a second replay ratio or new anti-forgetting method.
