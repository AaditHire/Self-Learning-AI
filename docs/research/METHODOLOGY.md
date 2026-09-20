# Methodology

## Experimental unit

The experimental unit is a fully specified model condition evaluated on a
versioned, frozen suite. A condition binds an exact base-model revision, adapter
version (or none), prompt policy, documentation/retrieval policy, decoding
configuration, compiler snapshot, evaluation-suite version, and seed set.

## Controlled condition matrix

Every capability experiment should preserve these four interpretable cells:

| Condition | Parameter update | GOCO docs at evaluation |
|---|---:|---:|
| Frozen base, no docs | No | No |
| Frozen base + docs/RAG | No | Yes |
| Adapted, no docs | Yes | No |
| Adapted + docs/RAG | Yes | Yes |

All cells use the same frozen unseen tasks and semantic tests. Prompt budgets
and decoding settings must be fixed. The retrieval corpus and retrieval output
must be logged so document access is not confused with parameter learning.

## Data separation

Splits are assigned by semantic capability, structural template, and capability
combination—not by random examples. Each learned capability should include
basic, structural, compositional, and adversarial/near-valid holdouts. Maintain
three access tiers:

1. development tests, available during implementation;
2. frozen promotion tests, used for candidate decisions; and
3. final paper holdout, sealed until the method and configuration are frozen.

Deduplicate by normalized source, task specification, structural signature,
and generator/template lineage. Record any suspected pretraining contamination
as a threat rather than treating novelty as established.

## Objective evaluation

The primary correctness oracle is execution against hidden semantic tests.
Parsing or compiling alone is not success. Record parse, semantic-validation,
execution, hidden-test, exact-output, pass@1, and—only where pre-registered—
pass@k outcomes. Do not use BLEU or text similarity as the main correctness
metric.

Generalization slices must be reported separately. Aggregate scores must not
hide failure on a capability family.

## Continual-learning evaluation

After each sequential capability update, re-evaluate every earlier capability,
general coding, instruction following, and selected future-unlearned concepts.
Report new-capability learning, average forgetting, worst-task forgetting,
backward transfer, optional forward transfer, examples-to-threshold, GPU time
per accepted update, adapter size, and documentation dependence.

The first training comparison, after baseline infrastructure works, is naive
sequential LoRA versus replay LoRA. Candidate replay ratios are 0%, 10%, 20%,
and 40%; 20% is an engineering starting point, not a presumed optimum.

## Versioning and promotion

The base model is immutable. Candidate adapters branch from an accepted parent.
Each candidate record includes base model name and revision, parent adapter,
dataset manifest/hash, compiler hash, training configuration/hash, seed,
evaluation-suite version, results, and final accepted/rejected status.

Promotion thresholds must be frozen in a protocol before evaluation. A
candidate is accepted only if provenance and integrity checks pass, the new
skill reaches its threshold, and old-skill/general-behavior regressions remain
within their limits. Rejected and failed artifacts are retained.

## Reproducibility conventions

- Experiment IDs are sequential and immutable: `EXP-0001`, `EXP-0002`, ...
- `EXP-0000` is reserved for the non-training Phase 0 audit.
- Hash files with SHA-256; record Git commit and Git tree/blob IDs where source
  originated in Git.
- Canonical manifests use UTF-8 JSON with stable key ordering and no transient
  absolute paths in the hashed scientific payload.
- Record all random seeds. Use a pre-registered seed set for comparisons rather
  than choosing seeds after results.
- Store outputs beneath `research/results/<experiment-id>/`; tables and figures
  cite the immutable result manifest from which they were derived.
- Adapter names use `accepted/vNNN` and `candidates/cNNNN`; rejected candidates
  remain addressable and are marked rejected rather than deleted.
- Record package lockfiles, CUDA/driver/runtime versions, GPU identity, peak
  memory, wall time, and exact commands for every model experiment.
- Do not overwrite an experiment directory. Corrections receive a new
  experiment ID and cross-reference the superseded record.

## Verified-experience boundary

Model-proposed programs are untrusted candidates. Only experiences passing
provenance checks, quarantine, compiler execution, and hidden semantic tests
may enter a replay or training manifest. A model never certifies its own output.

Real user data is out of scope for early phases. Any later use requires consent,
privacy filtering, provenance, quarantine, deduplication, verification,
contribution limits, offline training, frozen evaluation, shadow deployment,
and explicit promotion.

## Phase 1 frozen baseline implementation

Phase 1 uses the official FP16 weights of
`Qwen/Qwen2.5-Coder-1.5B-Instruct` at commit
`2e1fd397ee46e1388853d2af2c993145b0f1098a`. Every parameter has
`requires_grad=False`, inference runs under `torch.inference_mode`, decoding is
greedy, and there is no retry. The two paired conditions differ only by the
complete trusted GOCO documentation snapshot appended to the system context.

Task-level pass@1 requires every hidden case plus any explicit structural
requirement to pass. Parse, semantic compile, execution, exact output, family,
difficulty, and first error phase are diagnostics. The paired effect is the
docs-minus-baseline task pass-rate difference. Phase 1 pre-registers a 10,000-
resample paired task bootstrap interval and two-sided exact McNemar comparison.
With zero discordant pairs and a complete floor in both conditions, these
statistics are descriptive and cannot establish equivalence.

The benchmark uses one physical input line per execution because the pinned
runtime's repeated `INPUT` implementation loses buffered later lines. Tasks
needing multiple values explicitly use a delimiter and the strings library.
This is a language/runtime constraint and a construct-validity limitation.

## Phase 1R diagnostic recovery methodology

Phase 1R separates engineering selection from confirmatory measurement. It uses
a new 24-task development-only suite to compare additive corrected-context
protocols. The consumed Phase 1 suite is not used for selection, and the legacy
sealed holdout is never loaded by Phase 1R tooling. Output normalization is
presentation-only and frozen before inference.

The development selection and progression rule is fixed in
`research/protocols/PHASE_1R_DEVELOPMENT_PROTOCOL_SELECTION.md`. Only a selected
documentation condition reaching at least 25% hidden pass@1, improving at least
15 points over its paired no-doc condition, and passing tasks in at least three
families permits construction of a new 48-task confirmatory suite. Development
scores are engineering evidence, not confirmatory claims.
