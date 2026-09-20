# Threats to validity

## Internal validity

- Base-model pretraining may already contain public GOCO material.
- Near-duplicate generators can leak structure across nominal splits.
- Documentation conditions may change prompt length or task framing in addition
  to supplying knowledge.
- Stochastic decoding and training can make single-seed gains misleading.
- Repeated evaluation can tune decisions to the promotion suite.
- Replay can receive more total optimization tokens or compute than naive
  training unless budgets are matched and separately reported.
- Compiler defects or nondeterminism can be mistaken for model errors.
- A pass on weak tests can label semantically wrong programs as correct.

## Construct validity

- Compilation is not semantic correctness; hidden tests remain primary.
- No-doc evaluation alone does not distinguish adaptation from memorization.
- Aggregate accuracy can hide severe worst-capability forgetting.
- Synthetic GOCO proficiency is not equivalent to general self-directed
  learning or broad intelligence.
- Adapter performance does not establish that knowledge resides in any
  interpretable internal representation.

## External validity

- Results from one small model, one custom language, one task order, and one GPU
  may not transfer to other models or domains.
- GOCO's low public exposure and interpreter behavior may make it easier or
  harder than established programming languages.
- Small benchmarks can exaggerate both gains and forgetting.

## Statistical conclusion validity

- Small task counts and correlated generated cases reduce effective sample size.
- pass@k estimates are sensitive to sampling policy and must not be compared to
  pass@1 without clear labeling.
- Thresholds selected after results invalidate promotion claims.
- Multiple replay ratios and capability slices create multiple-comparison risk.

## Reproducibility and implementation threats

- The inspected GOCO checkout is behind its remote; conclusions apply to the
  pinned local commit, not an unspecified latest version.
- GOCO requests Java 25.0.1, but Phase 0 found Java 21.0.12.1 installed.
- JavaCC is absent from `PATH`; generated parser sources may diverge from the
  grammar if provenance is not checked.
- Windows process timeout and `-Xmx` limits are not a complete sandbox.
- Hardware, driver, CUDA, quantization kernels, and package versions can alter
  training reproducibility.
- The Phase 1 documentation snapshot did not explicitly forbid a top-level
  `PROGRAM` wrapper; the model invented one in every documentation condition.
- The trusted snapshot incorrectly stated that recursion was supported. The
  pinned semantic validator rejects self-recursive calls. No frozen-evaluation
  task required recursion, but the error weakens the document's trusted status.
- Both Phase 1 conditions hit a parse-level floor, so the paired comparison is
  unable to distinguish semantic capability or retrieval benefit.
- GOCO's repeated-`INPUT` buffering behavior forced multi-value benchmark tasks
  to use delimiter parsing and the strings library, increasing task coupling.
- Phase 1R protocol candidates were additive and therefore differed in both
  information and prompt length; the contribution of the concise contract and
  examples cannot be isolated from length/order effects.
- Phase 1R's 24-task suite was used for engineering selection, not confirmatory
  inference, and is now consumed. Reusing it for further selection would
  increase adaptive overfitting.
- The largest identifier/literal-normalized development reference similarity
  was 0.952 for two conditional structures despite unique lineages and task
  labels; structural diversity is improved over ID-only checks but imperfect.
- The best Phase 1R candidate produced only three passing tasks. The paired
  interval is wide and all remaining failures were lexical or syntactic, so
  semantic capability outside those isolated successes remains largely
  unmeasured.
- Phase 1S deliberately matches scenarios across executable levels. This helps
  localize composition burden but induces dependence across levels and does not
  create 96 independent observations.
- Phase 1S compares FP16 1.5B inference with NF4 4-bit 3B inference because of
  the 6 GB hardware ceiling. Any difference conflates parameter scale with
  quantization and cannot be interpreted as a clean scaling law.
- Simple within-family tasks retain high structural similarity (maximum
  normalized reference similarity 0.963) despite unique lineages and
  signatures. Per-family cells contain only three items per level.
- Phase 1T's identifier/literal-normalized audit flags 23 reference pairs at or
  above 0.90, with maximum 0.976. Manual review confirms different semantic
  targets and signatures, but shared GOCO input/output boilerplate and related
  control-flow skeletons still induce correlation.
- The Phase 1T paired conditions differ substantially in context length as well
  as knowledge content. Any gain is attributable to the configuration change
  as a whole, not to an isolated documentation component.
- A single deterministic generation per task estimates exact pass@1 for the
  frozen protocol but not sampling robustness or uncertainty across prompts.

## Mitigations

Pin all inputs; separate task families and templates; freeze protocols before
results; use multiple pre-registered seeds where feasible; report per-slice and
worst-task metrics; preserve failures; strengthen hidden tests; seal the paper
holdout; audit compiler provenance; and explicitly distinguish exploratory from
confirmatory experiments.
