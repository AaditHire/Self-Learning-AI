# Phase 1R — development-only elicitation protocol selection

Status: **FROZEN BEFORE PHASE 1R MODEL INFERENCE**

## Scope and prohibitions

This is diagnostic engineering on 24 newly authored development tasks. It is
not confirmatory evidence. The exact Qwen Phase 1 model remains frozen. No
training, gradient, optimizer, adapter, preference update, self-training, or
parameter change is permitted. The consumed Phase 1 evaluation and legacy
sealed holdout are prohibited inputs.

## Candidate conditions

All conditions use the same system prompt, user template, tasks, ordering,
normalization, compiler, deterministic decoding, and no retries.

- `DEV_NO_DOCS`: no GOCO knowledge context.
- `DEV_DOCS_A`: corrected comprehensive reference v1.
- `DEV_DOCS_B`: A plus a concise front-loaded syntax/source contract.
- `DEV_DOCS_C`: B plus five generic complete canonical examples.

Each step adds one recorded context component. No task-relevant retrieval is
tested in this iteration.

## Selection rule fixed before inference

Select the candidate with the highest task-level hidden-test pass@1. Break ties
by higher semantic compile rate, then higher parse rate, then fewer context
tokens in the fixed order A before B before C. Do not use the consumed Phase 1
evaluation for selection.

## Development gate fixed before inference

The selected documentation condition must achieve both:

1. hidden-test pass@1 at least 25%; and
2. at least 15 percentage points absolute improvement over `DEV_NO_DOCS`.

It must also pass at least one task in three or more semantic families; this is
the operational meaning of success spanning multiple families for this gate.
These are project engineering criteria, not universal scientific thresholds.

If the gate fails, stop Phase 1R without creating a new evaluation suite and
without training. If it passes, freeze the selected context unchanged, then
construct and freeze a new 48-task confirmatory suite before any confirmatory
inference.

## Decoding and scoring

- greedy decoding, one beam, at most 512 new tokens;
- at most 8192 input tokens;
- model EOS or token cap stopping;
- no retry or manual repair;
- output normalization v1 applied identically;
- three-second compiler timeout and 65,536 bytes per output stream;
- primary metric: all hidden cases and structural checks pass for a task;
- diagnostics: parse, semantic compile, execution, cases, family, difficulty,
  failure phase, tokens, time, and peak GPU allocation.

The development comparison is descriptive. A paired risk difference and
bootstrap interval are recorded but are not publication claims.

## Frozen model and instrument

- Qwen `Qwen2.5-Coder-1.5B-Instruct` revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`, FP16, unquantized,
  `requires_grad=False`, `torch.inference_mode`.
- Deterministic compiler JAR SHA-256
  `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`.
- Development benchmark and file hashes are recorded in
  `research/manifests/phase1r_development_benchmark.json`.
- Machine-readable frozen configuration:
  `research/protocols/phase1r_development_config.json`, SHA-256
  `c5391a6da514303bbf21b637fe89cf69f9476f1d9ab56d3204a406e9bf8ee21d`.
