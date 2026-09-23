# Phase 3A preregistration — naive two-stage GOCO learning

Date: 2026-09-23. Starting commit: `1ded323e036cd93813ab165210e0c3dcf32616df`. This protocol and `phase3a_config.json` are frozen before Phase 3A gradients or model evaluation. Phase 1T remains a failed gate; Phase 2A exploratory and Phase 2B confirmatory acquisition evidence are unchanged.

## Question and capability choice

Can a 3B Qwen coder model acquire GOCO numeric capability A and then GOCO string capability B by naive sequential QLoRA, and how much A performance survives B training? A and B were chosen by semantic separation, not model outcomes. Both require standalone GOCO synthesis with typed variables, input and output, and compiler-executed hidden cases. A covers numeric iteration (loops, recurrence, conditional accumulation) and array reductions. B covers string transformations and delimited-field processing. Their distinct central data types and operations can interfere through one shared adapter, making them a useful first sequential baseline without building a forgetting remedy.

## Frozen data and separation

Each capability has 60 training examples, 30 per subskill, generated from four training archetypes with 15 parameterizations. Each frozen evaluation has 32 tasks, 16 per subskill, generated from four disjoint evaluation archetypes with eight parameterizations. Every item has five compiler-executed semantic cases. The complete data, validation and construction-attempt records, and manual structural review are frozen by SHA-256 in the JSON configuration. No Phase 2B evaluation task is reused. The final-paper holdout remains sealed. The 64-item Phase 2B non-GOCO exact-response regression suite is intentionally reused unchanged as a longitudinal control. All evaluation tasks are hidden from training, and no B-stage example contains an A training example.

The strengthened audit checks unique IDs, counts/balance, compiler correctness, exact prompt/algorithm/lineage/signature/semantic-operation overlaps, normalized-code nearest neighbors and ≥0.98 rejects, AST-proxy matches, and consumed-suite prompt/code reuse. Similarity flags below the rejection threshold are documented before training. Compact GOCO boilerplate means some code neighbors are near; this limits distant-generalization claims.

## Model and sequence

The immutable `Qwen/Qwen2.5-Coder-3B-Instruct` revision `488639f1ff808d1d3d0ba301aef8c11461451ec5` is loaded locally in NF4 4-bit quantization. Each preregistered seed independently initializes a new rank-16 LoRA adapter on the base and trains it for three epochs on A only. The exact saved A adapter is then loaded trainably from the same immutable base and trained for three epochs on B only, with a fresh optimizer and scheduler. No adapter is merged. Both base-weight shards and the A-parent adapter are hash-checked before/after B training.

The remaining QLoRA recipe is the Phase 2B recipe: alpha 32, dropout 0.05, no bias, q/k/v/o and gate/up/down projections, FP16 compute, gradient checkpointing, micro-batch 1, gradient accumulation 8, maximum sequence length 320, PagedAdamW8bit, learning rate 0.0002, linear schedule with five warmup steps, maximum gradient norm 1. Three epochs on 60 examples imply 24 optimizer steps per stage. Final epoch is selected a priori. Seeds: `20260923`, `20261011`, `20261117`. This gives three independent A→B trajectories while keeping the stage-specific workload substantially below Phase 2B's 75 steps per model.

## Evaluation and analysis

The primary no-documentation GOCO prompt is frozen from Phase 2B. Greedy pass@1 uses at most 512 new tokens, no retries or manual repair. Evaluate frozen base on EVAL_A and regression. For each seed, train A, then evaluate A on EVAL_A and EVAL_B and regression before B training. Next train B from the saved A adapter and evaluate A→B on EVAL_B, EVAL_A, and regression. No evaluation result may alter any training decision.

Primary absolute forgetting for each seed is A's EVAL_A pass@1 minus the same seed's A→B EVAL_A pass@1, in percentage points. Relative retention is A→B/A, undefined if A pass rate is zero. Report base→A acquisition, A→B B acquisition relative to pre-B A on EVAL_B, seedwise values and mean/range, subskill changes, and all four paired task transitions. A task bootstrap samples the same 32 paired EVAL_A tasks across all three seeds 10,000 times; seeds are repeated models, not 96 independent tasks. “Measurable forgetting” requires mean paired drop above zero and bootstrap 95% lower bound above zero, with nonzero A acquisition. Stronger “catastrophic” language requires large and systematic degradation and is not implied by any decline alone. Report regression separately to distinguish targeted forgetting from general degradation. No best-seed, checkpoint, prompt, dataset, or hyperparameter selection is permitted.

## Stop boundary

This phase measures a naive sequential baseline only. No replay, EWC, adapter isolation, STABLE, NoRA, gating, or other anti-forgetting method is authorized. The final report must include the 19 user-requested items and stop for independent review.
