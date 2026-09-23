# Phase 3C structural-overlap review before model execution

The accepted construction passed pinned-compiler execution for **920/920** semantic cases: 300 A training, 160 A evaluation, 300 B training, and 160 B evaluation. No exact Phase 3C prompt collision, consumed prior prompt reuse, exact train/evaluation reference overlap, or exact train/evaluation structural-metadata overlap was found. No normalized-reference similarity reached the preregistered `0.98` rejection threshold against consumed prior material or the new opposite split. The compact `construction_attempts.json` records the earlier rejected matches: attempt 1 had 38 prior-code matches, attempt 2 had 8 prior-code matches, attempt 3 had 8 new train/evaluation code matches, and attempt 4 had 8 prior-code matches. Every attempt passed all reference semantic cases. All revisions were based only on compiler and structural diagnostics, before any model run. The final accepted data and audit are frozen by `phase3c_config.json`.

| Evaluation suite | Train-prompt Jaccard >=0.70 | Train-code similarity >=0.85 | Prior-prompt Jaccard >=0.70 | Prior-code similarity >=0.90 | Exact train AST proxy | Train-code distance buckets |
|---|---:|---:|---:|---:|---:|---|
| A, 32 tasks | 0 | 24 | 0 | 32 | 0 | 24 near, 8 far |
| B, 32 tasks | 0 | 32 | 8 | 32 | 24 | 32 near |

The largest A train-prompt similarity is **0.6000**, train-code **0.9515**, prior-prompt **0.6800**, and prior-code **0.9784**. The largest B values are **0.6000**, **0.9697**, **0.7692**, and **0.9677**, respectively. These lower-threshold values are part of the frozen interpretation, even though the `0.98` hard-rejection test passes.

| Evaluation archetype (8 IDs each) | Max train-code similarity | Max consumed-prior-code similarity | Max prior-prompt Jaccard | Exact train AST-proxy matches |
|---|---:|---:|---:|---:|
| A `alternating_accumulator` | 0.9119 | 0.9784 | 0.4583 | 0 |
| A `negative_position_weight` | 0.9515 | 0.9202 | 0.4800 | 0 |
| A `outer_inner_gap` | 0.6832 | 0.9173 | 0.6800 | 0 |
| A `triangular_milestones` | 0.8947 | 0.9586 | 0.3636 | 0 |
| B `combined_field_length` | 0.8831 | 0.9574 | 0.3810 | 0 |
| B `replace_upper_prefix` | 0.9697 | 0.9576 | 0.7692 | 8 |
| B `reverse_lower_suffix` | 0.9419 | 0.9677 | 0.4667 | 8 |
| B `select_reversed_field` | 0.9095 | 0.9136 | 0.3478 | 8 |

**Manual interpretation:** the new evaluation prompts and target programs are not literal duplicates of training or previously consumed evaluation items. The A triangular milestone task uses a running partial sum at every third step, whereas its closest new training structures use different operations and the nearest consumed reference remains at 0.9586. The A alternating accumulator is only 0.0216 below the hard prior-code threshold, so any result on that archetype deserves cautious interpretation. B replacement/prefix and reverse/lower tasks use the same compact GOCO string primitives as training and prior tasks; all eight `replace_upper_prefix` prompts have notable prior-prompt overlap, and three B archetypes share a coarse AST-proxy signature with training. These are **near-family tests**, not evidence of broad transfer to unrelated programming tasks. The fourth B archetype is structurally farther by the AST proxy but still code-similar. The exact per-task nearest IDs, similarities, flags, distance buckets, and reference case results are in `data_validation.json`.

The comparisons cover explicitly consumed development/evaluation full-synthesis materials from Phase 1R through 3B, including Phase 3A/3B evaluation prompts. The sealed final-paper holdout was neither opened nor compared. Similarity metrics and a coarse AST proxy cannot prove semantic novelty or independence, and the 8 IDs in each archetype are parameterized relatives. Statistical analysis therefore retains archetype correlation and limits generalization claims.
