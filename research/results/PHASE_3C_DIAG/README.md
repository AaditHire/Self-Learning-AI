# Phase 3C-DIAG: post-STOP A-acquisition failure diagnosis

**Status: exploratory, post-hoc diagnostic.** The confirmatory Phase 3C result remains exactly `STOP_before_B_no_tuning` at commit `12e2b2b80502ab962ca32c8c5c92cbdb9afc42ad`. No threshold, seed, dataset, prompt, adapter, or frozen scientific output was changed. No training, gradients, B stage, replay, or new continual-learning intervention occurred.

**Phase 3C EVAL_A status: `CONSUMED_FOR_CONFIRMATORY_USE`.** Its 32 tasks were used for the original confirmatory STOP and are now inspected diagnostically. They cannot later be presented as untouched confirmatory evidence for an acquisition recipe selected after this diagnosis. A future confirmatory retention experiment needs fresh untouched evaluation material and independent review. The sealed final-paper holdout was neither opened nor evaluated.

## Primary result: training versus held-out A

Each existing A adapter was evaluated once on the **same 60 frozen A training prompts** using no documentation, the original chat template, greedy decoding, the pinned compiler, and all five frozen training hidden cases per task. This is a **POST-HOC DIAGNOSTIC training-set evaluation**, not a new confirmatory test. The task-level [records](training_20260925.json), [second seed](training_20261013.json), and [third seed](training_20261119.json), with the [descriptive analysis](analysis.json), contain every generation and case result.

| Seed | A training | Held-out EVAL_A (existing) | Training − held-out gap | Training numeric | Held-out numeric | Training array | Held-out array | Exact training-target reproductions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20260925 | 60/60 | 0/32 | 100.000 pp | 30/30 | 0/16 | 30/30 | 0/16 | 60/60 |
| 20261013 | 60/60 | 7/32 | 78.125 pp | 30/30 | 7/16 | 30/30 | 0/16 | 60/60 |
| 20261119 | 60/60 | 7/32 | 78.125 pp | 30/30 | 7/16 | 30/30 | 0/16 | 60/60 |

All four training archetypes scored **15/15 in every seed**: `odd_linear_bonus`, `even_count_shift`, `count_above_shift`, and `positive_square_sum`. On the four distinct held-out archetypes, `triangular_milestones` scored **0/8, 7/8, 7/8** by seed. `alternating_accumulator`, `negative_position_weight`, and `outer_inner_gap` each scored **0/8 in every seed**. The 60 training targets were all reproduced as exact output strings; training failures in the evaluator's syntax, lexical, runtime, semantic, and hidden-test categories were **zero**. No diagnostic generation hit the 512-token output cap; the largest training generation was 115 tokens. These large descriptive gaps compare different archetypes and are not a new PASS/FAIL rule or an estimate of a causal generalization effect.

## Existing-run integrity and optimization record

The [analysis](analysis.json) preserves the complete original **24-step loss, gradient-norm, and learning-rate log for each seed**, plus epoch summaries. All three A runs completed three 60-example epochs, 24 optimizer steps, and 14,535 supervised tokens, with 29,933,568 trainable adapter parameters and no parent adapter. The final step-24 checkpoint was used without score-based selection. Logged losses, gradient norms, and learning rates were finite; the training code checks nonfinite losses/gradients, and no NaN/Inf/OOM abort was recorded. Gradients ran during the completed confirmatory A training, **not** during this diagnosis. Loss reduction by itself would not show correct program synthesis; the post-hoc executable training scores supply the narrower evidence of in-sample fitting.

| Seed | Epoch | First → last step mean micro-loss | Epoch mean step loss | Recorded gradient-norm range | First → last logged learning rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| 20260925 | 1 | 1.7645 → 0.4824 | 1.2698 | 0.7342–1.6996 | 0.000040 → 0.000168 |
| 20260925 | 2 | 0.3426 → 0.0043 | 0.1116 | 0.0667–1.9739 | 0.000158 → 0.000084 |
| 20260925 | 3 | 0.0050 → 0.0012 | 0.0021 | 0.0527–0.2924 | 0.000074 → 0 |
| 20261013 | 1 | 1.6647 → 0.5380 | 1.2874 | 0.5644–1.6264 | 0.000040 → 0.000168 |
| 20261013 | 2 | 0.2948 → 0.0132 | 0.1039 | 0.1325–1.3110 | 0.000158 → 0.000084 |
| 20261013 | 3 | 0.0087 → 0.0004 | 0.0024 | 0.0077–0.6232 | 0.000074 → 0 |
| 20261119 | 1 | 1.7907 → 0.5009 | 1.2865 | 0.4784–1.5985 | 0.000040 → 0.000168 |
| 20261119 | 2 | 0.3935 → 0.0040 | 0.1068 | 0.0592–1.4737 | 0.000158 → 0.000084 |
| 20261119 | 3 | 0.0032 → 0.0004 | 0.0011 | 0.0120–0.2089 | 0.000074 → 0 |

The original training records and diagnostic inference both hash-verified the A adapter files. Each adapter's base-weight hashes were equal before and after training and during diagnosis. Adapter SHA-256 values were `30dfe2a087103866fc2b7b8e6d5651b691594c6cc5be4a2eaa517cdfc12e0617` (20260925), `692823f4aaf95b59a987031dde6f7baa11d8a0b2b2572649e98af8a0d8af883a` (20261013), and `4ed80bd9d3ad37166e211cfa57fbfc57f4226d1cd1e57200962268c4ead176c3` (20261119). The immutable base is Qwen/Qwen2.5-Coder-3B-Instruct revision `488639f1ff808d1d3d0ba301aef8c11461451ec5`.

The frozen scheduler used five warmup optimizer steps to reach learning rate 0.0002, followed by linear decay to zero at step 24. The diagnostic scoring used the same pinned Java/JAR compiler invocation, 3-second per-case timeout, 65,536-byte stream cap, no repair attempt, and no documentation context as the original A evaluation.

## Seven successful held-out tasks

The existing task-level results verify that seeds `20261013` and `20261119` passed exactly `P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-02` through `-08`; seed `20260925` passed none. The two successful seeds produced identical generated programs for all eight members of this archetype. They correctly maintained a running sum, added it when the loop index was divisible by three, and used the prompt's initial-answer constant for variants 02–08. Variant 01 failed because the generated program initialized its running total to 1 rather than 0. Thus seven PASS IDs are seven parameterized cases of one structural pattern, not seven independent transfer structures.

```text
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-02
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-03
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-04
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-05
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-06
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-07
P3C-A-EVAL-NU-TRIANGULAR_MILESTONES-08
```

The [structural comparison](structural_audit.json) uses the already frozen similarity machinery and includes each evaluation prompt, normalized reference, nearest training prompt/target, AST proxy, semantic-operation tags, and nearest generated-code training target. For `triangular_milestones`, nearest training-prompt Jaccard is **0.345–0.379**, and normalized reference-code similarity to the nearest `even_count_shift` training target is **0.8947**. The nearest training prompt is usually `odd_linear_bonus`. No exact train AST proxy or semantic-operation tag overlaps. The apparently high code similarity includes common GOCO input/loop/output syntax; `alternating_accumulator` is even more code-similar to training (**0.9119**) yet scored 0/8. These observations are consistent with limited compositional transfer for one numeric pattern, but do **not** establish why it occurred.

## Array-reduction failure and failure taxonomy

All **90/90** array training seed-tasks passed and exactly reproduced their targets; all **48/48** held-out array seed-tasks failed. The existing held-out array outcomes comprise **26 compiler-semantic** failures and **22 hidden-test-semantic** failures, with no output reaching the 512-token cap (held-out A maxima: 119, 119, and 116 tokens by seed). All 24 `outer_inner_gap` attempts called bare `ABS`, which the compiler rejected as undefined; the valid frozen reference calls `math.ABS` after `IMPORT math.`. Two `negative_position_weight` attempts used `Math.ABS` without importing math. The other 22 negative-position attempts compiled and ran but used negative values directly instead of their magnitudes, passing only some cases. The generated programs reused the array input/parsing and loop scaffolding visible in training targets, then failed the new absolute-value or weighted-magnitude operations. These are representative observed output patterns, not proof of a particular learned internal mechanism.

The original [Phase 3C failure taxonomy](../PHASE_3C/stop_failure_taxonomy.json) records outcomes by seed, capability, subskill, and archetype. Its A totals are:

| Seed | Syntax | Lexical | Compiler semantic | Runtime | Hidden-test semantic | Success |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 20260925 | 10 | 3 | 10 | 0 | 9 | 0 |
| 20261013 | 8 | 0 | 9 | 0 | 8 | 7 |
| 20261119 | 8 | 0 | 8 | 0 | 9 | 7 |

By subskill, array reduction has **0 syntax/lexical/runtime failures**: it fails at compiler semantics or executable hidden semantics. Numeric iteration has all 26 syntax failures, the three lexical failures, four hidden-test-semantic failures, one compiler-semantic failure, and all 14 successes. The [descriptive analysis](analysis.json) and [structural comparison](structural_audit.json) provide the per-archetype counts and task IDs. Error categories identify observed failure stages; they do not by themselves establish a causal source.

## Deterministic pipeline and data audit

The [read-only audit](pipeline_audit.json) rechecked the frozen A path without model generation or compiler execution. It found 60 unique nonempty A training targets, 32 unique A evaluation IDs, no ID collision, correct subskill/archetype labels, five cases per task, and the pre-model reference validation's **300/300 A training and 160/160 A evaluation** case passes. The training and inference user text and prompt token IDs match exactly. Assistant target labels are a contiguous supervised suffix; all prompt tokens are masked. The longest complete training sequence is **237/320 tokens**, so no frozen training item was truncated. It independently recomputed the archived EVAL_A case pass flags, failure categories, prompt token counts, and summaries. The pinned compiler SHA-256 remains `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`.

**No concrete implementation, data, or scoring defect was found in these checks.** This is bounded evidence: it cannot prove the absence of every defect or validate behavior beyond the five cases per task. The observed invalid `ABS` calls are generated model outputs, while the frozen references passed compiler execution and their cases. No frozen artifact was repaired or rerun.

## Baseline context, classification, and limits

The preregistered, already executed base/no-docs Phase 3C EVAL_A score was **0/32**. Already observed pre-B B scores after A training were **8/32, 0/32, 0/32**; these are descriptive baselines and **not B acquisition**. No new base evaluation ran.

**Primary diagnostic category: GENERALIZATION FAILURE.** Supporting evidence is 60/60 exact in-sample target reproduction for every adapter, versus 0/32, 7/32, and 7/32 on distinct held-out A archetypes; array training is 90/90 across seeds while held-out array is 0/48. Evidence limiting this conclusion is that exact training-prompt success can reflect memorization of four parameterized templates, rather than robust learning of an entire training distribution. The few held-out numeric passes show some transfer and prevent a claim of zero generalization.

**Secondary descriptive pattern: MIXED / SUBSKILL-SPECIFIC.** Two seeds transferred one numeric archetype, while no seed transferred either held-out array archetype or the other numeric archetype. Against a strong subskill-specific causal claim, seed `20260925` transferred no archetype, the seven numeric successes per seed are correlated variants of one template, and the train/eval structures differ by design. The evidence does **not** support OPTIMIZATION / UNDER-ACQUISITION of the observed training examples or IMPLEMENTATION / DATA DEFECT as the leading diagnosis, while neither broad possibility can be excluded outside the audited scope.

Alternative explanations include narrow training-template coverage, a model that reproduces targets but lacks the needed composition of unseen operations, the particular hidden cases/scoring regime, and correlation among task variants. The structural similarity scores are proxies and do not locate a mechanism; the suite is hand-constructed with only four evaluation archetypes, three fixed seeds, and five cases per task. These observations are exploratory and carry no new inferential gate.

## What the diagnostic supports

The frozen A recipe fit the 60 seen training prompts exactly under the same no-documentation compiler-scored regime but transferred poorly to the structurally distinct held-out A suite. The hard acquisition STOP remains scientifically appropriate. A **development-only acquisition/generalization study** using separate development evaluation material is the justified type of next work; it would examine structural coverage and transfer before any independently reviewed fresh confirmatory retention protocol.

## What it does not support

It does not rescue or reinterpret Phase 3C, establish a causal mechanism, prove the model could not learn broader A with a different approved recipe, or measure replay retention or B plasticity. No hyperparameter or data recipe was selected from this consumed EVAL_A suite. Any later confirmatory claim requires fresh untouched evaluation tasks. No Phase 3D protocol or new continual-learning intervention was designed or executed here. **STOP for independent review.**
