# Phase 1R — Retrieval and Elicitation Protocol Repair

## Objective

Determine whether corrected, explicitly structured GOCO knowledge can break the
Phase 1 parse-level floor for the same completely frozen Qwen model, using only
new development data for protocol engineering. Proceed to a new confirmatory
suite only if a pre-registered development gate passes.

## Research question

Can an accurate, controlled GOCO context protocol elicit nontrivial executable
GOCO from frozen `Qwen2.5-Coder-1.5B-Instruct` strongly enough to justify a new
confirmatory baseline experiment?

## Hypothesis

A corrected reference with explicit source-file constraints and complete
examples would improve hidden-test pass@1 by at least 15 percentage points over
no documentation and reach at least 25% on development tasks.

## Why this experiment exists

Phase 1 changed model behavior but left both conditions at zero. The original
reference falsely claimed recursion and did not prohibit the invented
`PROGRAM` wrapper. A protocol floor had to be repaired before parameter
adaptation could be interpretable.

## Inputs

- Research start commit: `e88d49255abd7b9d1a4497d3d89dbdc4d3a8a5ae`.
- Pre-inference protocol commit: `0d1b6ab`.
- Development config SHA-256:
  `c5391a6da514303bbf21b637fe89cf69f9476f1d9ab56d3204a406e9bf8ee21d`.
- Corrected reference SHA-256:
  `aa0e7f75804d05f24a8e8f9a70ef25b6ca7caa5b87c9bb2d4bec9833f072bc8d`.
- Output-normalization protocol SHA-256:
  `3b3ed11956f00341944849b57a9af6cbe74c9dc7670bcfc7e477c0798e6311e4`.
- Development suite: 24 tasks and 97 hidden cases, three tasks per family.
- Pinned deterministic compiler JAR:
  `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`.

The consumed Phase 1 evaluation was used only for root-cause diagnosis, never
candidate selection. The eight legacy final-paper tasks remained sealed and
were not inspected, evaluated, modified, or loaded by Phase 1R tooling.

## Exact model/revision

`Qwen/Qwen2.5-Coder-1.5B-Instruct` revision
`2e1fd397ee46e1388853d2af2c993145b0f1098a`; official FP16 weights SHA-256
`c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`.
The model was unquantized, all parameters had `requires_grad=False`, and all
generation ran under `torch.inference_mode`.

## Training configuration

None. No LoRA, QLoRA, fine-tuning, adapter, optimizer, backward pass, preference
optimization, self-training, or weight update occurred.

## Root-cause findings

Every consumed no-doc Phase 1 output was fenced Go with `package main`; every
documentation output used an unsupported `PROGRAM` wrapper. The Phase 1
reference omitted the bare-statement top-level grammar, complete file examples,
and explicit prohibitions against common Go/custom-language constructs. It also
contained a false recursion claim. These observations implicate model prior and
underspecified/inaccurate context as plausible contributors, but the Phase 1
design cannot isolate a single cause. Full analysis is in
`docs/research/PHASE_1R_ROOT_CAUSE_ANALYSIS.md`.

## Documentation corrections

Phase 1's snapshot was preserved unchanged. Versioned v1 states that a file is
a bare statement sequence and explicitly prohibits `PROGRAM`, Go scaffolding,
`STRING`, `READLINE`, expression-valued `INPUT`, recursion, forward calls, and
multiple `INPUT` statements. It documents function terminators, `ELSEIF`,
`strings.TRIM` arity, delimiter input, and the loop parser edge. Corrections and
implementation evidence are enumerated in
`docs/research/PHASE_1R_DOCUMENTATION_CORRECTIONS.md`.

## Output normalization

Version 1 trims outer whitespace and extracts a code block only when exactly
one complete Markdown fence pair exists. It performs no syntax or semantic
repair, translation, wrapper removal, statement insertion, or multi-block
selection. It was applied identically to all conditions.

## Development benchmark and diversity

The new engineering-only suite has 24 unique task IDs, structures, and template
lineages, balanced 3-per-family, with 97 hidden cases. All reference solutions
passed. There were no exact prompt duplicates. Maximum prompt token Jaccard was
0.692; maximum identifier/literal-normalized reference sequence similarity was
0.952 between two conditional templates. The latter is a disclosed residual
within-family structural similarity and limits diversity claims.

## Candidate protocols and development results

| Condition | Added knowledge | Parse/compile/execute/pass | Passing families |
|---|---|---:|---:|
| `DEV_NO_DOCS` | none | 0/24 | 0 |
| `DEV_DOCS_A` | corrected reference | 2/24 (8.3%) | 2 |
| `DEV_DOCS_B` | A + front-loaded syntax contract | 2/24 (8.3%) | 2 |
| `DEV_DOCS_C` | B + five complete canonical examples | 3/24 (12.5%) | 3 |

Candidate A passed `RDEV-CD-003` and `RDEV-FN-001`. B passed the same two. C
passed `RDEV-EV-001`, `RDEV-CD-003`, and `RDEV-CP-001`. Under the frozen
selection rule, C was selected because it had the highest primary metric.

## Development gate

**FAILED.** Candidate C reached 12.5%, below the required 25%, and improved by
12.5 points over baseline, below the required 15 points. It did satisfy the
third criterion by passing tasks in three families. Because all criteria were
conjunctive, Phase 1R stopped here.

## New evaluation benchmark composition

Not created. The frozen protocol prohibited creating a new confirmatory suite
after a failed development gate.

## Confirmatory Condition A and B results

Not run. There is no confirmatory A/B result, paired confirmatory comparison,
or confirmatory family table. Development candidates must not be relabeled as
confirmatory evidence.

## Development paired comparison and uncertainty

For selected C versus no docs: paired risk difference `+0.125`; 10,000-task
bootstrap 95% percentile interval `[0.000, 0.2917]`; docs-only wins 3;
baseline-only wins 0; exact two-sided McNemar `p=0.25`. These are exploratory
development diagnostics and do not rescue the failed engineering gate.

## Family-level development results

Candidate C passed 1/3 expressions/variables, 1/3 conditionals, and 1/3
composition/algorithm tasks. It passed 0/3 arrays, functions, input/output,
loops, and strings. A and B each passed 1/3 conditionals and 1/3 functions.
Baseline passed 0/3 in every family.

## Failure taxonomy

- Baseline: 24 syntax failures; all 24 began with Go `package main`.
- A: 12 lexical, 10 syntax, 2 successes.
- B: 7 lexical, 15 syntax, 2 successes.
- C: 9 lexical, 12 syntax, 3 successes.
- Corrected context eliminated `PROGRAM` completely in all 72 assisted
  generations and eliminated Go `package main` completely.
- Remaining failures included semicolon leakage, expression-valued `INPUT`,
  pipe-delimited variables passed directly to `INPUT`, reserved identifiers
  such as `number`, `sentence`, and `length`, invented `FOR`, missing function
  declaration periods/braces, and invalid library-call syntax.
- No failed assisted task crossed parse/compile and then failed hidden output;
  failures remained lexical or syntactic.

## Failed experiments

Development benchmark construction initially had six failing references and a
later excessive-similarity finding. Both are retained in EXP-0005. The three
assisted candidates all failed the development progression gate; none was
discarded or rerun.

## Deviations from protocol

- Transformers warned that bundled `temperature`, `top_p`, and `top_k` fields
  were ignored. The runner explicitly used deterministic `do_sample=false`;
  no sampling occurred.
- No inference input, candidate, gate, selection rule, normalization behavior,
  or score was changed after preregistration.
- Task-relevant retrieval was not tested; investigation was intentionally
  bounded to the three preregistered additive fixed-context candidates.

## Interpretation

Accurate context repaired the universal `PROGRAM` failure and elicited three
fully executable, hidden-test-correct programs. Thus frozen in-context GOCO use
is possible for this model, but too sparse and fragile to establish a usable
retrieval-assisted baseline. The result is an engineering improvement over the
Phase 1 floor, not a successful retrieval-ceiling measurement.

## Alternative explanations

The model may require task-specific retrieval, more targeted examples, a
different prompt architecture, or a larger model. Conversely, the synthetic
development suite and examples may overstate transfer. Because candidate C
changes context length as well as content and examples, its small gain cannot
be attributed specifically to any one component.

## Threats to validity

The suite is small and expressly used for engineering; candidate contexts are
additive and differ in length; normalized code similarity remains high for one
within-family pair; all failures except successes stop before semantic testing;
and repeated use of this suite would overfit future protocol work. The
development suite is now consumed for Phase 1R selection and cannot become an
unseen confirmatory benchmark.

## What this result DOES support

- The corrected context eliminates the Phase 1 `PROGRAM` failure signature.
- A frozen model can produce some executable, semantically correct GOCO when
  given the tested trusted context.
- Candidate C achieved the best tested development score, 3/24 across three
  families, under a frozen selection rule.
- The pre-registered development progression gate was not met.

## What this result DOES NOT support

It does not establish a confirmatory retrieval ceiling, robust GOCO capability,
parameter learning, continual learning, self-learning, autonomous learning,
retention, catastrophic-forgetting prevention, human-like understanding, or a
reason to begin parameter adaptation.

## Figures/tables produced

`research/tables/phase1r_development_results.csv` contains the development
condition table. No confirmatory figure or table exists because confirmatory
evaluation was correctly not started.

## Artifacts/hashes

- Raw EXP-0006 result SHA-256:
  `fe12dc4f15fef7382952651f20fc4d5aae3f3cd5caf606006f182ce1b7977dcd`.
- Frozen config SHA-256:
  `c5391a6da514303bbf21b637fe89cf69f9476f1d9ab56d3204a406e9bf8ee21d`.
- Benchmark and context hashes are recorded in their manifests/config.

## Reproduction commands

```powershell
$env:PYTHONPATH='src'
python scripts/build_phase1r_development.py
python scripts/validate_phase1r_benchmark.py --tasks benchmark/phase1r/development_tasks.json --tests benchmark/phase1r/development_hidden_tests.json --references benchmark/phase1r/development_reference_solutions.json --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output <new-validation-path>.json
python scripts/run_phase1r_evaluation.py --config research/protocols/phase1r_development_config.json --model .models/Qwen2.5-Coder-1.5B-Instruct-2e1fd397 --java .tools/jdk-25.0.1+8/bin/java.exe --jar .artifacts/compiler/goco-compiler-6a029b8-deterministic.jar --output <new-result-path>.json
```

Never overwrite EXP-0006. The development suite is consumed and reproduction
is for verification, not further protocol selection.

## Decision

**NO-GO for Phase 2.** Phase 1R failed the preregistered development gate. No
new confirmatory benchmark was created, no confirmatory A/B run occurred, and
no parameter adaptation is authorized.

## Implications for the paper

This is a retained diagnostic negative result. It demonstrates that accurate
documentation can change failure modes and produce isolated executable
successes, while also showing why a pre-registered engineering gate prevents
premature training after a weak development improvement.
