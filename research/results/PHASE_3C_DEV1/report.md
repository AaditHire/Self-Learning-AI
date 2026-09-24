# Phase 3C-DEV1 development execution report

**Status:** complete exploratory development study; fresh DEV1 suite is `DEVELOPMENT_CONSUMED`. This is not confirmatory Phase 3C and is not a continual-learning result. Frozen design commit: `359a5eaa70bc8fcb468740b58b2d41ccc0ab5fb2`. No B training, replay, post-B retention, alternate ratio, or sealed final-paper holdout access occurred.

## Preflight and execution integrity

The clean execution checkout descended from the frozen design commit. All 28 design-manifest files matched local or LF-normalized SHA-256. The frozen reference validation, 4,320-pair structural audit, 60-ID per-condition schedules, three seeds, package versions, compiler hash, pinned model support/tokenizer files, and both immutable base-weight shard hashes passed pre-gradient checks. The GPU was an NVIDIA GeForce RTX 3060 Laptop GPU (6,144 MiB), driver 610.74; Python 3.13.0, torch 2.9.0+cu130, transformers 4.57.1, PEFT 0.17.1, bitsandbytes 0.50.2, accelerate 1.15.0, numpy 2.2.6, and safetensors 0.6.2 matched the design freeze. Full machine/JDK and hash details are in the archived `preflight.json`.

The pinned tokenizer remeasured one-epoch full-token exposures of **12,183 Dense** and **12,515 Diverse**. Diverse had **332 more full tokens (+2.7251%)**. Supervised target tokens were **4,809 Dense** and **5,015 Diverse**: **206 more (+4.2836%)**. Three-epoch totals were 36,549 versus 37,545 full tokens and 14,427 versus 15,045 supervised tokens. Maximum sequences were 232 and 260, below the frozen 320 limit. Both differences passed the prospective 10% stop rule. The Diverse condition's longer target-token exposure remains a measured confound; equal example/step budgets do not mean exactly equal FLOPs.

All six adapters started from the same pinned base revision and completed exactly 60 slots per epoch, 180 total, and 24 optimizer steps, using the fixed paired family-slot schedule and final-checkpoint rule. Step losses and gradient norms were finite, no NaN/Inf or OOM was recorded, and base-weight hashes were unchanged after every run. The scheduler rose from 0.00004 to the frozen 0.0002 peak and ended at zero. Final adapter SHA-256, every exposure ID, 24 step logs, runtime, and environment are in the six raw training records.

| Seed | Dense training seconds | Diverse training seconds | Dense final loss | Diverse final loss |
| --- | ---: | ---: | ---: | ---: |
| 20270925 | 172.2 | 265.7 | 0.00036 | 0.00054 |
| 20271013 | 265.1 | 328.7 | 0.00028 | 0.00238 |
| 20271119 | 354.0 | 374.1 | 0.00030 | 0.00094 |

These are observed final logged mean micro-loss values, not checkpoint-selection criteria. Runtime increased across execution order, so a per-condition time contrast is confounded by order and machine state.

## Frozen primary comparison and generalization gap

Every adapter passed **60/60 own-training tasks**, 30/30 numeric and 30/30 array, and reproduced **60/60 exact training targets**. Every training archetype was passed in every seed-condition. The fresh development task set was common to all six adapters and each task was scored once with greedy no-documentation generation, the pinned compiler, and all five semantic cases.

| Seed | Dense development | Diverse development | Diverse − Dense | Dense train→development gap | Diverse train→development gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| 20270925 | 6/36 | 12/36 | +6/36 (+16.67 pp) | 83.33 pp | 66.67 pp |
| 20271013 | 6/36 | 12/36 | +6/36 (+16.67 pp) | 83.33 pp | 66.67 pp |
| 20271119 | 6/36 | 12/36 | +6/36 (+16.67 pp) | 83.33 pp | 66.67 pp |

The frozen unweighted paired-seed mean is **+16.67 percentage points**. Its stratified task-cluster bootstrap 95% descriptive interval (10,000 draws, seed 20271221) is **5.56 to 27.78 points**. The frozen six-archetype block sensitivity interval is **0 to 50 points** and is unstable with six constructed blocks. These are conditional descriptive intervals, not a significance test or paper-level PASS gate. All three seeds show the same counts and the same passing archetypes; this is consistent within this fixed suite but does not establish robustness across new task structures.

## Subskills, structural distance, and archetypes

Counts below are **per seed**; all three seeds have the same archetype-level pass counts. Numeric and array development suites each have 18 tasks. Each distance group has 12 tasks. Every evaluation archetype has six tasks.

| Slice | Dense | Diverse | Diverse − Dense |
| --- | ---: | ---: | ---: |
| Numeric iteration | 0/18 | 6/18 | +6/18 |
| Array reduction | 6/18 | 6/18 | 0 |
| NEAR | 6/12 | 12/12 | +6/12 |
| COMPOSITIONAL | 0/12 | 0/12 | 0 |
| FAR | 0/12 | 0/12 | 0 |

The frozen subskill effects are +33.33 points numeric (task-cluster interval 11.11–55.56) and 0 array (0–0). The distance effects are +50 points NEAR (50–50) and 0 COMPOSITIONAL/FAR (0–0). Zero-width intervals here describe identical fixed task outcomes across seeds; they are not evidence of population certainty.

| Evaluation archetype | Distance | Dense passes | Diverse passes | Nearest Dense code similarity | Nearest Diverse code similarity |
| --- | --- | ---: | ---: | ---: | ---: |
| `fourth_square_step` | NEAR | 0/6 | 6/6 | 0.8918 | **0.9725** |
| `negative_tally_unrolled` | NEAR | 6/6 | 6/6 | 0.8232 | 0.8232 |
| `nontriple_divisor_mix` | COMPOSITIONAL | 0/6 | 0/6 | 0.8955 | 0.9123 |
| `range_neighbor_mix` | COMPOSITIONAL | 0/6 | 0/6 | 0.7989 | 0.8908 |
| `square_threshold_crossing` | FAR | 0/6 | 0/6 | 0.7911 | 0.8700 |
| `positive_run_length` | FAR | 0/6 | 0/6 | 0.9066 | 0.9066 |

The archived `analysis.json` contains each of the **36 task IDs**, its nearest Dense and Diverse training IDs and prompt/code/semantic-operation similarities, and each seed's paired outcome. The entire +6-task gain per seed is on the six `fourth_square_step` variants, whose nearest Diverse code similarity is the known **0.9725** maximum (versus 0.8918 for Dense). No high-similarity task was removed. This concentration, together with 0/24 COMPOSITIONAL/FAR in both conditions, limits the conclusion to a local NEAR transfer improvement. The similarity scores are coarse normalized-source proxies and can reflect shared GOCO scaffolding; they do not prove a causal mechanism.

## Failure analysis

The frozen failure taxonomy over each complete 36-task development run is:

| Seed | Condition | Success | Syntax | Compiler semantic | Hidden semantic |
| --- | --- | ---: | ---: | ---: | ---: |
| 20270925 | Dense | 6 | 22 | 2 | 6 |
| 20270925 | Diverse | 12 | 16 | 5 | 3 |
| 20271013 | Dense | 6 | 27 | 3 | 0 |
| 20271013 | Diverse | 12 | 7 | 6 | 11 |
| 20271119 | Dense | 6 | 18 | 6 | 6 |
| 20271119 | Diverse | 12 | 6 | 6 | 12 |

All 360 own-training seed-task outcomes passed, leaving no training-set failure category. On development failures, generations often retain familiar GOCO declarations, input parsing, loops, and array scaffolding, yet fail to realize unseen operations. Examples in the raw outputs include invalid multi-variable declaration or loop forms, attempted `BREAK`/`PRINTNL` constructs in `square_threshold_crossing`, and composed numeric programs rejected by the compiler or hidden cases. Array FAR generations frequently use familiar parsing scaffolding but fail the run-length semantics. The records support these as **observed behaviors only**. They do not localize an internal model mechanism, and the taxonomy's `semantic` class is a compiler phase distinct from `hidden_test_semantic` output mismatch.

## Interpretation and claims boundary

**Supported:** Under this matched 60-example, 24-step development budget, spreading examples across twelve rather than four training archetypes improved pass@1 on this fresh constructed suite by six tasks per seed. Both conditions fit their own training sets exactly. The improvement is confined to one NEAR numeric archetype with unusually high measured source similarity to the Diverse pool.

**Not supported:** broad structural transfer, COMPOSITIONAL or FAR generalization, general GOCO mastery, optimality of twelve archetypes, isolation of diversity from changed archetype frequency or token exposure, continual learning, replay success, forgetting prevention, or a repaired Phase 3C confirmatory acquisition result. The hand-built six-archetype suite, repeated parameter variants, three seeds, and 2.73%/4.28% token residuals limit inference. No new confirmatory suite was constructed. Phase 3C `EVAL_A` remained consumed and was not used for recipe selection; the sealed final-paper holdout was untouched.

## Deviations, preservation, and STOP

The first evaluation launcher attempt failed before model load or any generation because its script lacked the repository `src` import path. Commit `36e8e6a` added that path only; no scientific input, prompt, decoding, compiler, scorer, dataset, seed, schedule, or analysis rule changed, and no model evaluation was retried. All six training runs had already finished. This implementation correction is disclosed because it happened after gradients.

The six finalized adapters, six raw training records, twelve raw evaluation records, preflight provenance, analysis, and adapter support files were byte-verified into the established Git/Git LFS preservation paths. The separate preservation manifest records original/destination paths, sizes, SHA-256, seed/condition, and local copy verification. **Remote archival is complete only if a normal push and fresh-clone restore verify every copied artifact; consult the separate restore verification manifest for final status.** Local originals remain under `.runtime/phase3c_dev1/`.

The complete DEV1 development suite is now **consumed for future confirmatory use**. Do not use it or Phase 3C `EVAL_A` as untouched confirmatory evidence. A later recipe choice and any new confirmatory acquisition/retention suite require a separate prospective freeze and independent review. **STOP; no further development or continual-learning experiment is authorized by this result.**
