# Phase 1T — 3B backbone confirmation

Date: 2026-09-20

Start commit: `56940731b14053677123521093615c73c24604c6`

Preregistration commit: `dd3dd6f2ebcc303bc7ca6fcb1ca35bb2319fee26`

Frozen config SHA-256: `4cf19e35b4b937eeba6a89cbf2340e49c83f147b37dddffbb9ebde0946e020d5`

## 1. Preregistration commit

The benchmark, similarity review, exact model revisions and weights, NF4
configuration, prompts, fixed Candidate C context, normalization, decoding,
scoring, uncertainty procedure, secondary check, and conjunctive gate were
committed before inference. No parameter update was performed.

## 2. Benchmark composition and structural diversity

The fresh suite has 64 full-program synthesis tasks: eight tasks in each of
eight semantic families and 329 hidden cases, with at least five cases per
task. All 64 references passed every case. It has no duplicate prompts, 64
unique algorithmic labels, 60 control-flow labels, 64 template lineages, and
64 structural signatures. Maximum prompt-token Jaccard is 0.650. Maximum
identifier/literal-normalized reference similarity is 0.976.

The 23 reference pairs at or above 0.90 were manually reviewed before
inference. Each differs in semantic target, algorithmic label, structural
signature, and hidden mapping, but shared language boilerplate and some
control-flow skeletons induce correlation. Only LP01/LP02 form a flagged pair
in which both members passed under Candidate C (2 of 14 passes); the result is
not dominated by the flagged pairs. No major integrity problem was found, but
the tasks are not claimed to be statistically independent.

## 3. Condition A — 3B no docs

The exact frozen Qwen2.5-Coder-3B-Instruct revision produced 0/64 parseable,
0/64 compilable, 0/64 executable, and 0/64 hidden-passing programs. All eight
families were at zero. Failures were lexical 3 and syntax 61.

## 4. Condition B — 3B plus Candidate C

Candidate C produced 35/64 parseable (54.7%), 26/64 compilable (40.6%), 15/64
executable (23.4%), and 14/64 hidden-passing programs (21.875%). Thus the
documentation-assisted condition materially changed GOCO generation, but did
not reach the preregistered 25% operational threshold.

## 5. Paired comparison and uncertainty

The paired Candidate-C minus no-doc risk difference is +14/64 = +21.875
percentage points. The preregistered 10,000-resample paired task bootstrap 95%
interval is [+12.5, +32.8125] points. There were 14 docs-only wins and zero
baseline-only wins. Two-sided exact McNemar p = 0.000122; the effect size and
interval, not the p-value, are primary.

## 6. Family-level results

| Family | No docs | Candidate C |
|---|---:|---:|
| Arrays | 0/8 | 0/8 |
| Composition/algorithms | 0/8 | 3/8 |
| Conditionals | 0/8 | 4/8 |
| Expressions/variables | 0/8 | 1/8 |
| Functions | 0/8 | 3/8 |
| Input/output | 0/8 | 0/8 |
| Loops | 0/8 | 3/8 |
| Strings | 0/8 | 0/8 |

Candidate C passed tasks in five families. Arrays, input/output, and strings
remained at floor.

## 7. Failure taxonomy

| Condition | Lexical | Syntax | Semantic | Runtime | Hidden semantic | Success |
|---|---:|---:|---:|---:|---:|---:|
| 3B no docs | 3 | 61 | 0 | 0 | 0 | 0 |
| 3B Candidate C | 21 | 8 | 9 | 11 | 1 | 14 |
| 1.5B NF4 Candidate C | 34 | 25 | 0 | 1 | 0 | 4 |

Candidate C moved 3B failures substantially beyond parsing, but later semantic
and runtime failures still prevented the required task-level success rate.

## 8. Optional matched-NF4 1.5B result

The preregistered diagnostic-only 1.5B NF4 run produced 5/64 parseable, 5/64
compilable, 4/64 executable, and 4/64 hidden-passing programs (6.25%). Passes
spanned expressions/variables, conditionals, and loops. All four were a subset
of the 3B passes. Under matched NF4 configuration, 3B exceeded 1.5B by 10/64
(15.625 points), supporting a configuration-specific backbone difference. This
does not isolate causal parameter count and cannot alter the primary gate.

## 9. Protocol deviations

There were no scientific protocol deviations. Transformers warned that
temperature, top-p, and top-k values present in generation metadata were
ignored for greedy generation; the runner explicitly used `do_sample=false`,
one beam, and no retry as frozen. Checkpoint files were retained in addition to
the final raw result files. The legacy sealed holdout was not opened.

## 10. Evidence supported

Phase 1T establishes reproducible frozen 3B no-doc and Candidate-C baselines
for this suite. Candidate C caused a sizeable paired improvement, produced 14
docs-only wins, and expanded successes across five families. The matched-NF4
secondary result also shows that the exact 3B configuration outperformed the
exact 1.5B configuration under the fixed protocol.

## 11. Evidence not supported

The phase does not establish parameterized learning, continual learning,
self-learning, retention, forgetting prevention, autonomous improvement, a
causal model-size effect, or a universal scaling threshold. It also does not
show that recognition, completion, modification, and synthesis form a
monotonic difficulty ladder.

## 12. Phase 2 gate

**FAIL.** Candidate C passed 21.875%, below the required 25%. The +21.875-point
improvement criterion passed, the five-family criterion passed, and no major
benchmark-integrity issue was found, but the gate is conjunctive.

## 13. Recommendation

**NO-GO for QLoRA and Phase 2 parameter adaptation.** The Phase 1S 3B
full-synthesis rate (7/24 = 29.2%) did not replicate above the 25% threshold on
the independent 64-task suite. Analyze the failure pattern before changing
models, prompts, or benchmarks. Any new attempt requires a new preregistration;
do not train automatically.

## 14. Final Git commit

The exact final commit is the commit containing this completed Phase 1T record
and is reported in the completion handoff.

## 15. Suggested commit message

`research: complete Phase 1T backbone confirmation`

## Reproduction commands

```powershell
$env:PYTHONPATH='src'
python scripts/validate_phase1t_benchmark.py --tasks benchmark/phase1t/confirmation_tasks.json --tests benchmark/phase1t/confirmation_hidden_tests.json --references benchmark/phase1t/confirmation_references.json --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output <new-validation-output>.json
python scripts/run_phase1t_evaluation.py --config research/protocols/phase1t_config.json --model-key qwen_3b --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output <new-3b-output>.json
python scripts/run_phase1t_evaluation.py --config research/protocols/phase1t_config.json --model-key qwen_1p5b_nf4 --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output <new-1p5b-output>.json
```

Raw generations, normalized outputs, compiler/test results, case outcomes,
failure classifications, environment versions, timing, and peak resource
measurements are preserved in EXP-0012 and EXP-0013. Compact results are in
`research/results/PHASE_1T/summary.json`.
