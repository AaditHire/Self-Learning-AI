# Phase 2B final confirmatory report

Date completed: 2026-09-23  
Starting commit: `06e5db763ad2af2adc51e9b4709916820b0883a6`  
Preregistration commit: `4589be9473283d46cff7920fc1a46208dfa911e1`  
Preregistration-record follow-up: `a319694c2fba658986eaa9ac716b46e0f8d1c4b8`  
Frozen configuration SHA-256: `9cfeceb97cef6967d820308990cc7bcf544928490cb950b3a08c3acfc8df8638`

## Decision

Phase 2B **PASS**es every conjunctive preregistered criterion. The project recommendation is **GO for independent review of the Phase 2B acquisition result**. This is not authorization to begin continual-learning experiments; the project stops here pending that review.

The strongest supported conclusion is:

> Across multiple independently trained QLoRA adapters, adaptation on verified GOCO examples reproducibly improved no-documentation performance on structurally held-out GOCO tasks relative to the frozen base model, providing evidence of parameterized behavioral acquisition.

This result does not establish human-like understanding, self-learning, autonomous learning, continual learning, catastrophic-forgetting prevention, or general-purpose lifelong learning.

## Frozen data and separation

- Training: 200 fresh verified examples, 25 in each of eight semantic families, with 600 hidden cases. All 200 targets passed all verification cases.
- Confirmatory benchmark: 128 fresh tasks, 16 per family, exactly five hidden cases per task (640 total). All 128 references passed all cases.
- Regression: 64 frozen non-GOCO exact-response tasks.
- No Phase 2A training example or Phase 1/1R/1S/1T/2A evaluation task was reused. The legacy sealed holdout remained unopened.
- Exact train/evaluation overlaps: prompt 0, algorithm 0, generator lineage 0, structural signature 0, and semantic-operation combination 0.
- Similarity audit: 4 prompt flags at 0.70, 81 normalized-code flags at 0.85, 0 code rejects at 0.98, and 25 exact AST-proxy flags. All suspicious pairs were manually reviewed before training.
- Frozen structural-distance buckets: 3 far, 44 medium, and 81 near.
- Prior consumed suites: 0 prompt flags at 0.70, 84 code flags at 0.90, and 0 pairs at 0.98.

Canonical data hashes are recorded in `research/manifests/phase2b_data.json`; the complete review is in `research/results/EXP-0020/structural_overlap_manual_review.md`.

## Frozen model and training recipe

Immutable base: `Qwen/Qwen2.5-Coder-3B-Instruct` revision `488639f1ff808d1d3d0ba301aef8c11461451ec5`.

The unchanged Phase 2A recipe used NF4 4-bit quantization, double quantization, FP16 compute, LoRA rank 16, alpha 32, dropout 0.05, no bias, and targets `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, and `down_proj`. Training used 3 epochs, micro-batch 1, gradient accumulation 8, maximum length 320, gradient checkpointing, PagedAdamW8bit, learning rate 0.0002, weight decay 0, Adam betas 0.9/0.999, epsilon 1e-8, maximum gradient norm 1, a linear schedule, and 5 warmup steps. The final epoch was selected a priori; there was no early stopping, prompt search, hyperparameter search, checkpoint selection, or best-seed selection.

Preregistered seeds: `20260921`, `20261007`, and `20261103`.

## Training feasibility and lineage

| Seed | Steps | First loss | Last loss | Time (s) | Supervised tok/s | Peak GPU bytes | Peak RSS bytes | Adapter weight SHA-256 |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 20260921 | 75/75 | 2.089602 | 0.000665 | 903.422 | 38.902 | 3,480,380,928 | 6,028,582,912 | `1968cb0d503c502dbe31a1f53a3c70528c7dd5d478e5e50062d2e212e76e03ee` |
| 20261007 | 75/75 | 2.343363 | 0.002141 | 819.214 | 42.901 | 3,480,667,648 | 6,021,156,864 | `ac3f5f1ed1162874d9bacf9a0ebffebb1d44a930be6daf77801f2760cab86010` |
| 20261103 | 75/75 | 2.201381 | 0.001394 | 964.396 | 36.442 | 3,480,380,928 | 6,023,499,776 | `502a6ce0176f8e6371a7fddb0b8e3b32ee5af7673008a48b1f63277c7f2384f7` |

All losses and recorded gradients were finite, all expected optimizer steps completed without OOM, all adapters were saved separately, and the before/after hashes of both immutable base-weight shards matched in every run.

## Primary results

| Condition | Hidden pass | Parse | Compile | Execute | Absolute gain vs base |
|---|---:|---:|---:|---:|---:|
| Frozen base / no docs | 0/128 (0.00%) | 0/128 (0.00%) | 0/128 (0.00%) | 0/128 (0.00%) | — |
| Adapter seed 20260921 / no docs | 65/128 (50.78%) | 116/128 (90.63%) | 102/128 (79.69%) | 95/128 (74.22%) | +50.78 pp |
| Adapter seed 20261007 / no docs | 70/128 (54.69%) | 116/128 (90.63%) | 102/128 (79.69%) | 99/128 (77.34%) | +54.69 pp |
| Adapter seed 20261103 / no docs | 70/128 (54.69%) | 115/128 (89.84%) | 104/128 (81.25%) | 101/128 (78.91%) | +54.69 pp |
| Frozen base + Candidate C docs, descriptive | 22/128 (17.19%) | 55/128 (42.97%) | 46/128 (35.94%) | 33/128 (25.78%) | descriptive only |

Across adapted seeds, mean hidden-test pass@1 was **53.39%**, range **50.78%–54.69%**. Mean parse, compile, and execution rates were 90.36%, 80.21%, and 76.82%. The mean absolute improvement over frozen base/no-docs was 53.39 points.

All 65/70/70 adapter successes were adapted-only paired successes because the frozen base passed no task. Every seed succeeded in all eight semantic families.

## Family-level hidden-test pass@1

| Family | Seed 20260921 | Seed 20261007 | Seed 20261103 | Mean | Range |
|---|---:|---:|---:|---:|---:|
| Arrays | 12/16 (75.00%) | 12/16 (75.00%) | 12/16 (75.00%) | 75.00% | 75.00%–75.00% |
| Composition/algorithms | 3/16 (18.75%) | 3/16 (18.75%) | 2/16 (12.50%) | 16.67% | 12.50%–18.75% |
| Conditionals | 11/16 (68.75%) | 12/16 (75.00%) | 12/16 (75.00%) | 72.92% | 68.75%–75.00% |
| Expressions/variables | 11/16 (68.75%) | 13/16 (81.25%) | 13/16 (81.25%) | 77.08% | 68.75%–81.25% |
| Functions | 11/16 (68.75%) | 10/16 (62.50%) | 10/16 (62.50%) | 64.58% | 62.50%–68.75% |
| Input/output | 4/16 (25.00%) | 6/16 (37.50%) | 7/16 (43.75%) | 35.42% | 25.00%–43.75% |
| Loops | 11/16 (68.75%) | 12/16 (75.00%) | 12/16 (75.00%) | 72.92% | 68.75%–75.00% |
| Strings | 2/16 (12.50%) | 2/16 (12.50%) | 2/16 (12.50%) | 12.50% | 12.50%–12.50% |

The effect is broad in family coverage but uneven in depth. Strings and composition/algorithms are the clearest remaining generalization bottlenecks.

## Training versus held-out performance

| Seed | Training hidden pass | Held-out hidden pass | Absolute gap |
|---:|---:|---:|---:|
| 20260921 | 200/200 (100.00%) | 65/128 (50.78%) | 49.22 pp |
| 20261007 | 196/200 (98.00%) | 70/128 (54.69%) | 43.31 pp |
| 20261103 | 195/200 (97.50%) | 70/128 (54.69%) | 42.81 pp |

The mean training rate was 98.50%, the mean held-out rate was 53.39%, and the mean gap was 45.11 points. This is smaller than Phase 2A's 70.88-point gap (99.00% versus 28.13%) but remains large. It materially constrains the breadth of any generalization claim.

## Failure analysis

| Outcome | Seed 20260921 | Seed 20261007 | Seed 20261103 | All Phase 2B seeds | Phase 2A adapter |
|---|---:|---:|---:|---:|---:|
| Wrong language | 0 | 0 | 0 | 0/384 | 0/64 |
| Lexical failure | 1 | 1 | 1 | 3/384 | 2/64 |
| Syntax failure | 11 | 11 | 12 | 34/384 | 6/64 |
| Semantic validation failure | 14 | 14 | 11 | 39/384 | 10/64 |
| Structural-requirement failure | 1 | 0 | 0 | 1/384 | 1/64 |
| Runtime failure | 7 | 3 | 3 | 13/384 | 3/64 |
| Hidden-test semantic failure | 29 | 29 | 31 | 89/384 | 24/64 |
| Success | 65 | 70 | 70 | 205/384 | 18/64 |

The frozen Phase 2B base failed lexically on 5 tasks and syntactically on 123; the adapted models instead parsed about 90% of tasks. Thus QLoRA reproducibly taught the GOCO surface form and much of its executable structure. Among adapted failures, hidden-test semantics was the largest single category (89), confirming that semantic transfer—not language identification—is now the main bottleneck. Compared with Phase 2A, success rose from 28.13% to a 53.39% mean while parse success remained comparably high (87.50% in Phase 2A versus 90.36% mean here).

## Structural-distance and statistical analysis

The preregistered task-cluster bootstrap resampled 128 paired task clusters and treated the three seeds as repeated trained models within each task; it did not treat 384 seed-task observations as independent. With 10,000 samples and bootstrap seed `20261201`, the observed mean improvement was 53.39 points and the 95% interval was **45.57 to 61.20 points**.

There were 47 medium/far tasks. Across all seeds, 69 of 205 successful seed-task instances (33.66%) were on medium/far tasks, below the first branch of the non-domination rule. However, mean improvement on medium/far tasks was **48.94 points**, far above the alternative 10-point threshold. The preregistered structural non-domination criterion therefore passed.

## Non-GOCO regression

| Condition | Correct | Accuracy | Change from base | Severe drop (>15 pp) |
|---|---:|---:|---:|---|
| Frozen base | 47/64 | 73.44% | — | — |
| Adapter seed 20260921 | 40/64 | 62.50% | -10.94 pp | No |
| Adapter seed 20261007 | 41/64 | 64.06% | -9.38 pp | No |
| Adapter seed 20261103 | 48/64 | 75.00% | +1.56 pp | No |

No seed crossed the severe-collapse limit, but the first two seeds show real smaller regressions that must not be described as zero degradation. The 64 exact-response items are a narrow proxy, not a comprehensive general-capability evaluation.

## Conjunctive success rule

| Criterion | Result |
|---|---|
| Mean adapted pass@1 at least 20% | Pass: 53.39% |
| Mean gain at least 15 points | Pass: +53.39 points |
| Every seed gains at least 10 points | Pass: +50.78, +54.69, +54.69 |
| Every seed succeeds in at least four families | Pass: 8/8 for every seed |
| Not dominated by structural near-duplicates | Pass: medium/far mean gain +48.94 points |
| No regression drop greater than 15 points | Pass: worst drop 10.94 points |
| All three training runs feasible | Pass: 75/75 finite steps each, no OOM |

Overall confirmatory decision: **PASS**.

## Protocol deviations and failed runs

There were **no protocol deviations** after preregistration: no prompt, data, seed, recipe, checkpoint, or success-rule change; no retry; no manual generation repair; no adapter merge; and no best-seed selection. The Transformers notice that sampling-only flags were ignored is consistent with the frozen `do_sample=false`, `num_beams=1` greedy protocol and did not change decoding.

No training or evaluation run failed. Pre-freeze data-construction attempts 01–09 remain preserved under EXP-0020, as required; they occurred before gradients and are not hidden confirmatory failures.

## Evidence boundaries

Supported: reproducible, multi-seed parameterized acquisition of a narrow verified GOCO behavior distribution, including substantial improvement on structurally medium/far held-out tasks.

Not supported: broad GOCO mastery; robust string or algorithmic composition generalization; absence of memorization; zero general-capability regression; causal claims about architecture scale; human-like understanding; autonomous/self-directed learning; continual learning; catastrophic-forgetting prevention; or general-purpose lifelong learning.

Important residual threats are only three seeds, one base model and recipe, synthetic templated supervision, residual shared grammar skeletons (81/128 near tasks under the deliberately coarse code metric), deterministic pass@1 only, exact-response regression sensitivity, one hardware/software stack, and the large remaining training/held-out gap.

## Reproduction

Training used `scripts/train_phase2b_qlora.py` once for each preregistered seed and its frozen adapter output. Evaluation used `scripts/run_phase2b_evaluation.py` with plans `primary`, `training`, and `regression`; Java `.tools/jdk-25.0.1+8/bin/java.exe`; compiler `.artifacts/compiler/goco-compiler-6a029b8-deterministic.jar`; and the paths recorded in EXP-0021 through EXP-0026. Aggregate analysis used:

```text
python scripts/analyze_phase2b.py --config research/protocols/phase2b_config.json --base-primary research/results/EXP-0024/base_no_docs.json --docs-primary research/results/EXP-0024/base_docs.json --adapter-primary research/results/EXP-0024/adapter_seed_20260921.json research/results/EXP-0024/adapter_seed_20261007.json research/results/EXP-0024/adapter_seed_20261103.json --training-run research/results/EXP-0021/training.json research/results/EXP-0022/training.json research/results/EXP-0023/training.json --training-eval research/results/EXP-0025/seed_20260921.json research/results/EXP-0025/seed_20261007.json research/results/EXP-0025/seed_20261103.json --base-regression research/results/EXP-0026/base.json --adapter-regression research/results/EXP-0026/seed_20260921.json research/results/EXP-0026/seed_20261007.json research/results/EXP-0026/seed_20261103.json --output research/results/PHASE_2B/summary.json
```

Raw generations, compiler outputs, hidden-test results, checkpoints, hardware measurements, and training curves are retained in EXP-0021 through EXP-0026.

Final repository verification used `PYTHONPATH=src python -m pytest -q` (13 tests passed) and explicit byte-compilation of all six Phase 2B scripts. A preliminary bare `python -m pytest -q` could not collect tests because this src-layout repository does not install itself into the active environment; rerunning with the required import path passed and did not affect any experiment artifact.

## Stop boundary

Phase 2B is complete. Do not begin a continual-learning phase without independent review and explicit new authorization.
