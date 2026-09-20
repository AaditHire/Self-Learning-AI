# Phase 2A — Exploratory QLoRA parameter-acquisition feasibility pilot

Date: 2026-09-20 to 2026-09-21

Start commit: `00d819c1f38260f6750db70306150bd085422312`

Preregistration commit: `b5fe9b3b5e8d95d319ebc1e14bd14aa1df492f9b`

Frozen config SHA-256: `f8d4e94dddff4fbf6244c9d9d41585e69291325aefb386c26b2bcfa76b0075d2`

Decision: **EXPLORATORY PASS**. This is not a confirmatory result. Phase 1T
remains a failed gate and is not retroactively changed.

## 1. Preregistration commit

The complete data, overlap audit, smoke rule, one-run QLoRA configuration,
evaluation protocol, regression rule, and conjunctive success gate were frozen
at `b5fe9b3b5e8d95d319ebc1e14bd14aa1df492f9b` before any Phase 2A gradient.

## 2. Training dataset composition

The training-only pool contains 200 examples, exactly 25 in each of eight
families: expressions/variables, conditionals, loops, functions, arrays,
strings, input/output, and composition/algorithms. Each family contains five
generator structures with five variants. All 200 target programs passed all
600 hidden verification cases before freeze. The canonical training hash is
`bb87dce6086d362efbbfa279ad414e82dba9c8bd920ff01855b36eeac9cfdec3`.
Every example hash and verification provenance is in
`research/manifests/phase2a_data.json` and `research/results/EXP-0014/`.

The development-only suite contains 64 tasks, eight per family, and 320 hidden
cases. All 64 references passed before freeze. The 24-item regression suite is
non-GOCO. No Phase 1, 1R, 1S, or 1T task entered training, and the legacy sealed
holdout was not opened.

## 3. Train/evaluation structural-overlap audit

Before training, the audit found zero exact prompt reuse, zero generator-lineage
overlap, zero algorithm-label overlap, and zero prompt-token Jaccard flags at
the 0.75 threshold. Four earlier constructions were rejected and regenerated;
all attempts remain recorded. Identifier/literal/library-normalized code
comparison flagged 28/64 development tasks at 0.90 or above. Every flag was
manually reviewed before training and retained only where the semantic target,
algorithm, signature, hidden mapping, and lineage differed.

Eleven of 28 flagged tasks passed (39.29%), while seven of 36 unflagged tasks
passed (19.44%). Thus the effect is not attributable to exact, renamed,
constant-only, lineage, algorithm-label, or undisclosed copies, and successes
exist outside the flagged subset. However, coarse structural similarity is
enriched among passes and remains a major limitation rather than proof of broad
generalization. Full dispositions are in
`research/results/EXP-0014/structural_overlap_manual_review.md`.

## 4. QLoRA configuration

The immutable parent is `Qwen/Qwen2.5-Coder-3B-Instruct` at revision
`488639f1ff808d1d3d0ba301aef8c11461451ec5`. It was loaded in NF4 4-bit with
double quantization and FP16 compute. The PEFT adapter uses rank 16, alpha 32,
dropout 0.05, no bias, and targets `q_proj`, `k_proj`, `v_proj`, `o_proj`,
`gate_proj`, `up_proj`, and `down_proj`.

Training used three epochs, micro-batch one, gradient accumulation eight,
maximum length 320, gradient checkpointing, PagedAdamW8bit, learning rate
2e-4, five warmup steps, linear decay, max gradient norm 1.0, and seed
20260920. The final epoch was selected a priori; there was no development
evaluation during training and no hyperparameter search. The adapter remains
unmerged at `research/adapters/candidates/c0001-phase2a-qlora/`.

## 5. Hardware and training feasibility

The two-step smoke passed locally on the RTX 3060 Laptop GPU (6 GB). It used
3,531,969,536 peak allocated GPU bytes, 3,781,165,056 peak reserved bytes,
6,035,001,344 peak process RSS bytes, and 50.55 supervised tokens/s. These were
inside the frozen 5.5 GiB allocated-VRAM and 12 GiB RSS limits.

The full 75-step run completed in 697.74 seconds at 43.92 supervised tokens/s.
It peaked at 3,673,793,536 allocated GPU bytes, 4,102,029,312 reserved bytes,
and 6,030,819,328 process RSS bytes. The two exact base weight hashes were
identical before and after training. Only the versioned adapter was saved.

## 6. Training curve and instability

All losses and gradients were finite; there was no OOM or interrupted run.
Logged mean micro-loss was 2.23909 at step 1, 1.73676 at warmup step 5,
0.021692 at the end of epoch 1 (step 25), 0.015352 at the end of epoch 2
(step 50), and 0.002099 at the end of epoch 3 (step 75). The rapid near-zero
training loss and later 99% training pass rate are evidence of strong fitting,
not by themselves of generalization.

## 7. Frozen-base/no-doc results

Condition A scored 0/64 hidden pass (0%), with 0/64 parsing, compilation, and
execution success. Its taxonomy was 62 syntax, one lexical, and one
wrong-language failure.

## 8. Adapted/no-doc results

Condition B scored 18/64 hidden pass (28.125%), 56/64 parse (87.5%), 46/64
compile (71.875%), and 43/64 execute (67.188%). Documentation and retrieval
were absent, decoding was greedy pass@1, and there was no retry or repair.

## 9. Frozen-base-plus-docs reference

The optional Candidate C reference condition was not run. It was not required
by the protocol and was barred from checkpoint selection. The already consumed
Phase 1T Candidate C result remains 14/64 (21.875%) as historical context only.

## 10. Paired A/B comparison

The exact same 64 tasks produced 18 adapter-only passes and zero base-only
passes, for a +28.125 percentage-point paired risk difference. The 10,000-
resample paired bootstrap 95% interval is [+17.1875, +39.0625] points. Exact
two-sided McNemar p is `7.62939453125e-06`. These statistics describe this one
frozen development suite and do not make it confirmatory.

## 11. Semantic-family results

| Family | Base passes | Adapted passes | Adapted rate |
|---|---:|---:|---:|
| expressions/variables | 0/8 | 7/8 | 87.5% |
| conditionals | 0/8 | 4/8 | 50.0% |
| loops | 0/8 | 3/8 | 37.5% |
| arrays | 0/8 | 3/8 | 37.5% |
| composition/algorithms | 0/8 | 1/8 | 12.5% |
| functions | 0/8 | 0/8 | 0% |
| input/output | 0/8 | 0/8 | 0% |
| strings | 0/8 | 0/8 | 0% |

Successes span five families. Three families remain at zero hidden pass.

## 12. Training versus held-out gap

The adapter passed 198/200 training tasks (99.0%) but only 18/64 structurally
held-out tasks (28.125%), a 70.875-point train-minus-held-out gap. All 200
training outputs parsed, compiled, and executed; the two failures were hidden-
semantic failures in input/output. This large gap must be treated as potential
memorization plus narrow transfer, not evidence of broad GOCO generalization.

## 13. General-programming regression

The base scored 18/24 (75.0%) and the adapter 16/24 (66.67%). The adapter lost
three base-only tasks and gained one adapted-only task, for a net drop of two
tasks / 8.33 percentage points. This is inside the frozen severe-collapse
limits of at most four tasks and at most 20 points. It does not establish robust
retention or prevent unmeasured regressions.

## 14. Failure taxonomy

The adapted development arm produced 18 successes and 46 failures: 24 hidden-
test semantic, ten semantic-validation, six syntax, three runtime, two lexical,
and one structural-requirement failure. The dominant remaining problem is
therefore semantic correctness after the adapter largely removes the parent's
parse-level floor.

## 15. Failed runs and hyperparameter attempts

There were no failed smoke or full-training runs and no hyperparameter search.
Only the preregistered rank-16 configuration received Phase 2A gradients. Six
pre-freeze data-validation attempts, including construction and structural
rejections, are retained in `research/results/EXP-0014/` and were not hidden.

## 16. Protocol deviations

None. The optional base-plus-docs reference was omitted by design and is not a
deviation. A generated result field inherited the label `docs_pass_rate` from
the paired evaluator even though Condition B is adapter/no-docs; the condition
records and report use the correct meaning, and no computation changed.

## 17. Evidence supported

Under the frozen exploratory protocol, the result supports only: **QLoRA can
produce development-set evidence consistent with parameterized GOCO behavioral
acquisition in this setup.** The adapter materially improves compiler-backed
hidden pass@1 without documentation, on unseen prompts with separated lineage
and algorithms, while the parent weights remain unchanged.

## 18. Evidence not supported

This pilot does not establish continual learning, self-learning, autonomous
learning, robust retention, human-like understanding, general parameterized
acquisition, causal knowledge localization, or final-paper validity. It uses
one seed, one adapter configuration, synthetic trusted targets, one development
suite, and a small format-sensitive regression suite. Phase 1T remains a
failed gate at 14/64 against its required 25%.

## 19. Phase 2A success criteria

| Criterion | Result | Decision |
|---|---|---|
| Improvement at least +15 points | +28.125 points | PASS |
| Adapted hidden pass at least 20% | 28.125% | PASS |
| Successes in at least four families | five families | PASS |
| Not explained by structural duplication | zero exact/lineage/algorithm/prompt duplication; seven unflagged passes; disclosed coarse-code correlation | PASS with limitation |
| No severe general collapse | -2 tasks / -8.33 points | PASS |

The frozen conjunctive exploratory gate therefore **PASSES**.

## 20. Recommendation for later confirmation

Do not begin Phase 2B until independent review. A later preregistered
confirmatory acquisition experiment should use a newly generated untouched
suite, multiple training seeds, a stronger AST/semantic-distance split,
deduplicated generator families, a larger and less format-sensitive regression
battery, and prespecified uncertainty/gate rules. It should test whether the
effect survives when high coarse-code-similarity tasks are excluded or
stratified, and should retain a no-training control plus the immutable parent.

## 21. Exact final Git commit

The exact final commit is reported in the completion response after this record
is committed; a commit cannot contain its own hash.

## 22. Suggested commit message

`research: complete Phase 2A QLoRA feasibility pilot`

## Artifact index and reproduction

- Compact summary: `research/results/PHASE_2A/summary.json`
- Adapter lineage: `research/manifests/phase2a_adapter_c0001.json`
- Smoke: `research/results/EXP-0015/smoke.json`
- Training log: `research/results/EXP-0016/training.json`
- Primary raw generations and scoring: `research/results/EXP-0017/primary.json`
- Training-task raw generations and scoring:
  `research/results/EXP-0018/training_performance.json`
- Regression raw outputs: `research/results/EXP-0019/regression.json`

```powershell
$env:PYTHONPATH='src'
python scripts/train_phase2a_qlora.py --config research/protocols/phase2a_config.json --mode smoke --output research/results/EXP-0015/smoke.json
python scripts/train_phase2a_qlora.py --config research/protocols/phase2a_config.json --mode train --output research/results/EXP-0016/training.json --adapter-output research/adapters/candidates/c0001-phase2a-qlora
python scripts/run_phase2a_evaluation.py --config research/protocols/phase2a_config.json --plan primary --adapter research/adapters/candidates/c0001-phase2a-qlora --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output research/results/EXP-0017/primary.json
python scripts/run_phase2a_evaluation.py --config research/protocols/phase2a_config.json --plan training --adapter research/adapters/candidates/c0001-phase2a-qlora --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output research/results/EXP-0018/training_performance.json
python scripts/run_phase2a_evaluation.py --config research/protocols/phase2a_config.json --plan regression --adapter research/adapters/candidates/c0001-phase2a-qlora --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output research/results/EXP-0019/regression.json
python scripts/summarize_phase2a.py
```

Phase 2B was not started.
