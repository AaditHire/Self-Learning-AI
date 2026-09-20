# Phase 1S frozen syntax-capability diagnostic

Frozen: 2026-09-20, before any Phase 1S model inference.

## Purpose and boundary

Phase 1S localizes the frozen model's GOCO failure across four levels:
recognition, local completion, structured modification, and full synthesis. It
does not train, adapt, merge, or write any model weight. Phase 1 and Phase 1R
tasks are consumed historical evidence. The legacy eight-task final-paper
holdout remains sealed and is not loaded by any Phase 1S script.

## Instrument

The diagnostic has 96 new items: eight semantic families, four levels, and
three items per family/level. Recognition has 24 exact-choice items. The 72
executable items each have four hidden cases (288 total). Local completion,
structured modification, and full synthesis intentionally share scenario
families so the required composition burden changes while semantics remain
comparable. This matching creates dependence and is reported rather than
treated as 96 independent observations.

All reference programs must pass before freezing. Exact duplicate prompts,
lineages, structural signatures, prompt token-set similarity, normalized
reference similarity, family balance, and level balance are recorded in the
benchmark manifest. Pre-freeze instrument failures are retained under
`research/results/EXP-0007/`.

## Frozen elicitation and scoring

Candidate C is the only allowed knowledge condition. Its context is the exact
ordered concatenation of the concise syntax contract, corrected language
reference, and canonical examples used by Phase 1R. There is no prompt search.
Output normalization is the already frozen Phase 1R rule. Decoding is greedy,
single-beam, pass@1, with no retry or manual repair.

Recognition is exact normalized A/B/C. Local completion inserts only the
normalized fragment into the frozen scaffold. Modification and synthesis score
the normalized complete program. Executable success requires compilation,
execution, all four hidden cases, and structural requirements. Results are
reported overall and by level, family, level-by-family, and failure class.

## Models and hardware gate

The primary is the exact Phase 1/1R Qwen2.5-Coder-1.5B revision in FP16. The
comparator is the exact Qwen2.5-Coder-3B-Instruct revision in bitsandbytes NF4
4-bit with double quantization and FP16 compute. Every parameter is frozen and
all generation runs under inference mode.

Before the comparator suite, the 3B model must load and generate at least one
token without CUDA OOM and without exceeding physical VRAM. Failure is retained
and causes the 3B suite to be skipped, not reconfigured. The 1.5B suite still
runs. No remote inference API and no 7B-or-larger model may be substituted.

## Pre-registered decisions

- A: strong 1.5B recognition/local completion followed by collapse on
  modification/synthesis indicates a composition bottleneck. Do not train.
- B: poor 1.5B recognition/local completion means the 1.5B backbone is
  unsuitable. No-go.
- C: 3B full-synthesis hidden pass@1 of at least 25%, spanning at least four
  families, recommends a separate backbone-selection phase. It does not
  authorize training.
- D: if both backbones are poor, re-examine the task, context, and tooling
  setup. No-go for QLoRA.

“Strong” and “poor” in A/B are localization descriptions rather than promotion
thresholds; raw level-wise counts are decisive evidence. Rule C is the sole
quantitative advancement trigger. Any ambiguous pattern defaults to no
training and a documented diagnostic interpretation.

The machine-readable authority is `phase1s_config.json`, SHA-256
`5e7da9fe450cef1561bdeaa9f0642ec88d4e96429eac9c4bf44944b36df20c2a`.
