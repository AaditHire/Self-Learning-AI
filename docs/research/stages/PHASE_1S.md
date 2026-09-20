# Phase 1S — Syntax bottleneck diagnosis and backbone suitability

Date: 2026-09-20  
Start commit: `2879bbea5a5199eba3df1ead4fe9138916c17937`  
Preregistration commit: `2e14057ddd9ee622ef123dbc30c1099bf7d31782`  
Frozen config SHA-256: `5e7da9fe450cef1561bdeaa9f0642ec88d4e96429eac9c4bf44944b36df20c2a`

## 1. Preregistration

The benchmark, prompts, Candidate C context order, output normalization,
model revisions, decoding, scoring, smoke gate, and cases A–D were committed
before Phase 1S inference. No training, adapter, gradient, or weight update was
performed.

## 2. Diagnostic benchmark composition

The new diagnostic-only suite contains 96 items: eight semantic families,
four levels, and three items per family/level. Recognition has 24 choice items.
Local completion, structured modification, and full synthesis have 24 items
each, with four hidden cases per executable item (288 cases). All 72 reference
programs passed all cases. Phase 1/1R data remained consumed historical
evidence and the legacy final-paper holdout remained sealed.

## 3. Structural-diversity audit

There are zero exact duplicate prompts, 96 unique template lineages, and 96
unique structural signatures. Maximum prompt token-set Jaccard was 0.737 for
recognition, 0.851 for local completion, 0.733 for modification, and 0.619 for
full synthesis. Maximum identifier/literal-normalized reference sequence
similarity was 0.963 (ST1/ST3). Control-flow labels and family membership are
recorded per item. The three executable levels intentionally use matched
scenario lineages; unique labels are not treated as proof of independence.

## 4. 1.5B results by level

| Level | Choice / parse | Compile | Execute | Hidden pass |
|---|---:|---:|---:|---:|
| Recognition | 13/24 (54.2%) | — | — | — |
| Local completion | 2/24 (8.3%) | 1/24 | 1/24 | 0/24 (0%) |
| Structured modification | 4/24 (16.7%) | 4/24 | 4/24 | 4/24 (16.7%) |
| Full synthesis | 0/24 (0%) | 0/24 | 0/24 | 0/24 (0%) |

The non-monotonic modification result prevents a simple monotone “difficulty
gradient” interpretation. Nevertheless, recognition was only modest and local
completion was at floor, which activates case B rather than case A.

## 5. 1.5B results by semantic family

| Family | Recognition | Executable hidden pass |
|---|---:|---:|
| Arrays | 1/3 | 0/9 |
| Composition/algorithms | 1/3 | 0/9 |
| Conditionals | 1/3 | 1/9 |
| Expressions/variables | 2/3 | 1/9 |
| Functions | 2/3 | 0/9 |
| Input/output | 2/3 | 0/9 |
| Loops | 3/3 | 2/9 |
| Strings | 1/3 | 0/9 |

## 6. Failure-transition taxonomy

| Model | Wrong choice | Parse | Compile | Execute | Hidden pass |
|---|---:|---:|---:|---:|---:|
| 1.5B | 11/24 | 6/72 | 5/72 | 5/72 | 4/72 |
| 3B | 7/24 | 41/72 | 33/72 | 31/72 | 28/72 |

The 1.5B executable failures were lexical 8, syntax 58, semantic validation 1,
runtime 0, and hidden-test semantic 1; four succeeded. The 3B failures were
lexical 14, syntax 17, semantic validation 8, runtime 2, and hidden-test
semantic 3; 28 succeeded. Wrong-language outputs were zero for both. Thus the
larger model moved many failures past syntax into later semantic stages rather
than merely changing aggregate accuracy.

## 7. 3B hardware feasibility

The exact Qwen2.5-Coder-3B-Instruct revision
`488639f1ff808d1d3d0ba301aef8c11461451ec5` ran locally with bitsandbytes
0.50.2 NF4 4-bit, double quantization, and FP16 compute. Both model shards
matched their preregistered hashes. The smoke input was 2,046 tokens; it loaded
in 9.76 seconds, generated 11 tokens at 3.62 tokens/s, and peaked at
2,872,655,360 bytes allocated GPU memory. RSS was 833,384,448 bytes before and
1,890,095,104 bytes after; the smoke script did not continuously sample peak
RSS. Full-run peak measurements are below.

## 8. 3B diagnostic results

| Level | Choice / parse | Compile | Execute | Hidden pass |
|---|---:|---:|---:|---:|
| Recognition | 17/24 (70.8%) | — | — | — |
| Local completion | 11/24 (45.8%) | 8/24 | 8/24 | 7/24 (29.2%) |
| Structured modification | 17/24 (70.8%) | 16/24 | 16/24 | 14/24 (58.3%) |
| Full synthesis | 13/24 (54.2%) | 9/24 | 7/24 | 7/24 (29.2%) |

Full-synthesis passes spanned five families: composition/algorithms,
conditionals, expressions/variables, functions, and loops. The full run used
2,041–2,172 input tokens, peaked at 2,971,827,200 bytes allocated GPU memory
and 6,026,244,096 bytes process RSS, and generated 2,640 output tokens at 5.13
tokens/s over 514.62 generation seconds.

## 9. Direct model comparison

Relative to 1.5B, 3B improved recognition by 4/24 (+16.7 points), local hidden
pass by 7/24 (+29.2 points), modification by 10/24 (+41.7 points), and full
synthesis by 7/24 (+29.2 points). Across executable items it improved parse
from 6/72 to 41/72 and hidden pass from 4/72 to 28/72. This is a diagnostic
comparison, not a clean scaling law: model capacity and inference precision
differ simultaneously.

## 10. Location of failure

For 1.5B the dominant collapse is syntax assembly: 66/72 executable outputs
failed lexing or parsing, including every full-synthesis output. Recognition is
also only 54.2%, and local completion passed no tasks, so the evidence is not
consistent with intact GOCO knowledge blocked only by free-form composition.
For 3B, syntax assembly is substantially better, but failures persist at every
stage; input/output had zero executable passes. Capacity materially changes the
observed in-context behavior without eliminating semantic or composition
limits.

## 11. Threats to validity

The suite is diagnostic and not confirmatory. Matched scenarios induce
cross-level dependence; three items per family/level give coarse estimates;
some simple references remain structurally similar; Candidate C prompt length
may affect behavior; public GOCO exposure cannot be ruled out; and the 1.5B
FP16 versus 3B NF4 comparison conflates scale and quantization. A single greedy
run measures pass@1 under one exact environment, not stochastic robustness.

## 12. Protocol deviations

There were no scientific protocol deviations. The optional code-context
control was not preregistered and was not run. Transformers warned that
temperature/top-p/top-k values in model generation metadata were invalid for
greedy generation and ignored them; the runner explicitly used
`do_sample=false`, one beam, and no retry as frozen. The smoke script recorded
RSS before/after rather than a continuous peak; the full 3B runner did record
peak process RSS. Two pre-freeze instrument defects were corrected and retained
in EXP-0007 before preregistration.

## 13. Evidence supported

Phase 1S supports the bounded observations that the frozen 1.5B model is weak
even at recognition/local completion under Candidate C; its executable failure
is dominated by syntax assembly; and the frozen 3B comparator materially
improves recognition, parsing, semantic execution, and hidden-test pass rates.
The 3B model exceeded the engineering full-synthesis indicator (7/24 = 29.2%)
and passed five families.

## 14. Evidence not supported

The results do not establish parameterized learning, continual learning,
self-learning, autonomous learning, retention, forgetting prevention, causal
mechanisms, or a universal model-size threshold. They do not justify training
either backbone, replacing the primary backbone automatically, or claiming
that 3B has reliably learned GOCO.

## 15. Recommendation

Run a separately preregistered backbone-selection phase. It should test whether
the 3B result is robust on fresh diagnostic tasks and, if feasible, separate
capacity from quantization/precision effects. Keep all current Phase 1S tasks
consumed and keep the final-paper holdout sealed. Do not train until that phase
is independently reviewed and explicitly authorized.

## 16. Primary-backbone decision

**NO-GO for continuing with Qwen2.5-Coder-1.5B-Instruct as the primary
backbone.** Case B fires because recognition is poor/modest and local completion
is at floor. Case C also fires for the 3B comparator, requiring a separate
backbone-selection phase. Cases A and D do not fire. This is not authorization
to train or change the backbone.

## 17. Final Git commit

The exact final commit is recorded after all Phase 1S artifacts and integrity
checks are complete.

## 18. Suggested commit message

`research: complete Phase 1S backbone diagnostic`

## Reproduction commands

```powershell
$env:PYTHONPATH='src'
python scripts/validate_phase1s_diagnostic.py --tasks benchmark/phase1s/diagnostic_tasks.json --tests benchmark/phase1s/diagnostic_hidden_tests.json --references benchmark/phase1s/diagnostic_references.json --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output <new-validation-output>.json
python scripts/smoke_phase1s_3b.py --config research/protocols/phase1s_config.json --output <new-smoke-output>.json
python scripts/run_phase1s_evaluation.py --config research/protocols/phase1s_config.json --model-key qwen_1p5b --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output <new-1p5b-output>.json
python scripts/run_phase1s_evaluation.py --config research/protocols/phase1s_config.json --model-key qwen_3b --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output <new-3b-output>.json
```

Raw generations, normalized outputs, compiler outputs, hidden-case outcomes,
failure classifications, environment versions, and hardware measurements are
preserved in EXP-0008 through EXP-0010. Compact tables are under
`research/results/PHASE_1S/`.
