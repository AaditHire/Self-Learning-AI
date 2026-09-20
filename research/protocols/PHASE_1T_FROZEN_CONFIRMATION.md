# Phase 1T frozen 3B backbone confirmation

Frozen before model inference on 2026-09-20.

## Purpose

Independently test whether the exact frozen Qwen2.5-Coder-3B-Instruct NF4
configuration provides a usable no-documentation and Candidate-C-assisted GOCO
baseline on 64 new full-program synthesis tasks. Phase 1T performs no training,
adapter creation, gradient computation, or weight update.

Phase 1S supports only this wording: under its fixed protocol, the 3B NF4
configuration materially outperformed the 1.5B FP16 configuration. It did not
isolate a causal parameter-count effect. Recognition, completion, modification,
and synthesis were distinct generation regimes, not a validated monotonic
difficulty ladder.

## Data governance and benchmark

All Phase 1, 1R, and 1S evaluation tasks are consumed. The legacy final-paper
holdout remains sealed. Phase 1T uses 64 new synthesis tasks, eight per semantic
family, with 329 hidden cases and at least five cases per task. All references
passed before freezing.

Every item records semantic family, algorithmic structure, control flow,
lineage, structural signature, and constructs. There are no duplicate prompts;
all 64 algorithmic labels, lineages, and signatures are unique. Prompt Jaccard
maxes at 0.65. The coarse normalized-code audit flags 23 pairs at >=0.90,
maximum 0.976. Every flagged pair was manually reviewed and retained only after
confirming distinct semantic targets, metadata signatures, and hidden-test
mappings. These tasks are not claimed to be statistically independent.

## Frozen conditions

- A / `NO_DOCS`: exact frozen 3B NF4 model, system/user prompts only.
- B / `CANDIDATE_C`: identical model and tasks with the exact ordered Phase 1R
  syntax contract, corrected reference, and canonical examples.

Condition order is A then B. Both use greedy single-beam generation, maximum
512 new tokens, one attempt, the Phase 1R v1 normalizer, no repair, the pinned
compiler, and complete hidden-case pass@1.

The technically straightforward secondary check runs the exact frozen 1.5B
revision under the same NF4/double-quant/FP16-compute configuration on Candidate
C only. It cannot change the 3B decision.

## Analysis and gate

Report parse, compile, execution, hidden pass, family results, and failure
taxonomy for each primary condition. Report paired risk difference, a 10,000-
sample paired-task bootstrap percentile 95% interval, docs-only wins,
baseline-only wins, and exact two-sided McNemar p as a secondary diagnostic.

The Phase 2 gate passes only if Candidate C simultaneously achieves:

1. hidden-test pass@1 >= 25%;
2. at least +15 percentage points over no docs; and
3. at least one passing task in four or more semantic families.

A major benchmark-integrity problem overrides numerical passage. Passing means
GO to a separately controlled Phase 2 parameter-acquisition experiment with 3B
as the operational backbone, but does not authorize training. Failure means
NO-GO for QLoRA and investigation before any prompt, model, or benchmark change.

The machine-readable config is `phase1t_config.json`, SHA-256
`4cf19e35b4b937eeba6a89cbf2340e49c83f147b37dddffbb9ebde0946e020d5`.
