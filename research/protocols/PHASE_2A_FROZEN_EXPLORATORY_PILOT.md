# Phase 2A frozen exploratory QLoRA feasibility pilot

Start commit: `00d819c1f38260f6750db70306150bd085422312`

Frozen config SHA-256:
`f8d4e94dddff4fbf6244c9d9d41585e69291325aefb386c26b2bcfa76b0075d2`

## Status and scope

Phase 1T remains a failed gate. Phase 2A is separately authorized as a
developmental, exploratory feasibility pilot. It cannot retroactively change
Phase 1T and is not the confirmatory paper experiment.

The question is whether one fixed QLoRA adapter trained on verified GOCO
examples improves no-documentation hidden pass@1 on structurally held-out
development tasks relative to the same immutable frozen base.

## Frozen data

- Training: 200 examples, 25 per family, five generator structures per family,
  600 verification cases; 200/200 targets passed before freeze.
- Development: 64 tasks, eight per family, 320 hidden cases; 64/64 references
  passed before freeze.
- General regression: 24 non-GOCO exact-response programming/instruction tasks.
- Phase 1/1R/1S/1T tasks are excluded from training. The sealed holdout remains
  unopened.
- No exact prompt reuse, lineage overlap, algorithm-label overlap, or prompt
  similarity flag remains. Coarse normalized-code flags are manually reviewed
  and disclosed rather than treated as independent observations.

## Frozen training run

The immutable base is Qwen2.5-Coder-3B-Instruct revision
`488639f1ff808d1d3d0ba301aef8c11461451ec5`. It is loaded in NF4 with double
quantization and FP16 compute. The adapter is PEFT LoRA rank 16, alpha 32,
dropout 0.05, targeting attention projections and MLP projections. Training is
three epochs, micro-batch one, gradient accumulation eight, maximum length 320,
gradient checkpointing, PagedAdamW8bit, linear schedule, learning rate 2e-4,
five warmup steps, seed 20260920. The final epoch is selected a priori. There
is no development evaluation during training and no hyperparameter search.

Before the full run, EXP-0015 trains two examples per family for two optimizer
steps. It must finish with finite loss/gradients, no OOM, peak allocated GPU at
or below 5.5 GiB, and peak process RSS at or below 12 GiB. A failed smoke is
retained and stops this configuration. Any rank-8/length-256 fallback requires
a new preregistration before further gradients.

## Frozen evaluation

The primary comparison uses the exact same 64 development tasks:

- A: frozen base, no docs, no adapter.
- B: same base, candidate adapter active, no docs.

Decoding is greedy pass@1 with one beam, no retry, no repair, and at most 512
new tokens. Complete hidden-test success is primary; parse, compile, execution,
family, taxonomy, paired wins, a 10,000-resample paired bootstrap interval, and
exact McNemar are diagnostic. Candidate C is optional reference context only
and cannot select the checkpoint.

Training-task performance is reported separately. The 24-task regression suite
is evaluated on base and adapter with exact normalized responses. Severe
collapse means a drop greater than 0.20 or more than four tasks.

## Frozen success rule

All five criteria are required:

1. adapted/no-doc improves by at least 15 absolute percentage points;
2. adapted/no-doc reaches at least 20% hidden pass@1;
3. adapted successes span at least four families;
4. improvement is not explained by rejected or undisclosed structural copies;
5. the frozen regression suite does not suffer severe collapse.

These are exploratory engineering criteria. Passing supports only development-
set evidence consistent with parameterized GOCO behavioral acquisition in this
setup. It does not establish continual learning, self-learning, autonomous
learning, robust retention, human-like understanding, or general acquisition.

## Stop rule

Record all attempts and deviations. Do not begin Phase 2B. A later confirmatory
experiment requires an untouched suite and independent review.
