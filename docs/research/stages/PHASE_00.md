# Phase 0 — Repository Audit, GOCO Extraction Plan, Research Protocol Foundation

## Objective

Identify repository boundaries, audit the read-only GOCO compiler, design a
pinned integration path, and establish research-paper and reproducibility
records without training or downloading a model.

## Research question

Can this project define a reproducible, read-only integration boundary and a
scientifically falsifiable foundation before any baseline or adaptation run?

## Hypothesis

The GOCO CLI and test assets expose enough deterministic structure to support a
research-owned, pinned compiler oracle without modifying or depending directly
on the production repository.

## Why this experiment exists

Without fixed repository boundaries, compiler provenance, evaluation
definitions, and claims discipline, later model gains could be artifacts of
mutable code, data leakage, or post-hoc thresholds.

## Inputs

- Primary repository at
  `C:\Users\Admin\OneDrive\Documents\GitHub\Self Learning AI`.
- Read-only GOCO repository at
  `C:\Users\Admin\OneDrive\Documents\GitHub\GOCO`.
- User-supplied Phase 0 research brief.

## Exact model/revision

No model used. Planned primary model is
`Qwen/Qwen2.5-Coder-1.5B-Instruct`; exact revision is intentionally unresolved
until a model experiment protocol is frozen.

## Exact dataset/manifests

No research dataset used. The upstream compiler test manifest at pinned GOCO
commit contains 88 cases (45 expected successes, 43 expected failures). Its
SHA-256 is
`066938769b639163c0b05c5038d5637106a5bb8849ba06da8f7ac7a500f3ad5f`.
See `research/manifests/goco_compiler_source.json`.

## Compiler revision

GOCO commit `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`; compiler tree
`f51973617cc3da8c78de88c668d8de6959575d6d`; Java source tree
`415215892c7127df899d59b3bceb99dc8357484b`.

## Training configuration

None. Training was prohibited in Phase 0.

## Evaluation protocol

Read-only source inspection covered the compiler entry point, parser/semantic/
runtime boundary, IO behavior, error mapping, tests, existing wrapper, Git
provenance, and local toolchain. Documentation artifacts were validated for
required sections and JSON syntax. Repository states were compared before and
after changes.

## Frozen metrics decided BEFORE the experiment

Phase 0 acceptance was binary: repository paths identified; GOCO unchanged;
integration documented; required research files and Phase 1 draft present;
relevant checks pass; Git diff reviewed.

## Expected outcomes

A complete audit, an extraction decision, an explicit list of uncertainties,
and a recoverable research state that prevents premature training.

## Actual results

- Both repositories were identified unambiguously.
- GOCO remained clean and untouched.
- `parser.MyLanguageParser` was identified as the CLI entry point.
- Parsing produces an AST; semantic validation precedes in-process AST
  execution. stdout, stderr, stdin, exit status, and timeout can be captured by
  a research wrapper.
- The minimal coherent compiler snapshot is the full Java source subtree,
  because parser, AST validation, runtime behavior, and libraries are coupled.
- A pinned extraction and conformance plan was created.
- The paper-oriented documentation, ledgers, registry, directory conventions,
  and Phase 1 draft were created.
- No model, dataset generation, compiler build, or GPU workload ran.

## Failed experiments

None. The upstream test suite was not executed because its harness regenerates
test files and recompiles into the GOCO repository, violating the read-only
boundary.

## Deviations from protocol

None material. The Phase 0 audit found a local Java version mismatch and absent
JavaCC; both are documented rather than changed prematurely.

## Interpretation

The GOCO compiler is suitable as an objective oracle only after extraction,
toolchain pinning, conformance testing, and sandboxing. Its existing test suite
is valuable for compiler conformance but is not automatically a leakage-safe
model benchmark.

## Alternative explanations

The CLI may appear deterministic on inspected code while hiding static-state or
platform-specific behavior. The README's Java 25 requirement may be stricter
than necessary or may expose incompatibilities under Java 21. These questions
require tests in the copied research snapshot.

## Threats to validity

Source inspection does not prove runtime conformance. The local GOCO checkout is
two commits behind its remote, so findings apply only to the pinned commit.
Upstream docs and examples may conflict with actual grammar; executable tests
must arbitrate behavior.

## What this result DOES support

It supports proceeding to a controlled Phase 1 implementation of a pinned
compiler oracle and frozen baseline protocol.

## What this result DOES NOT support

It does not support any claim about model GOCO ability, retrieval benefit,
parameter learning, generalization, continual learning, forgetting, or
self-directed improvement.

## Figures/tables produced

No empirical figures or tables. The condition matrix appears in methodology as
a design artifact, not a result.

## Artifacts/hashes

- `docs/PROJECT_STATE.md`
- `docs/research/*.md`
- `docs/research/stages/PHASE_00.md`
- `research/manifests/goco_compiler_source.json`
- `research/protocols/PHASE_01_FROZEN_BASELINE_RETRIEVAL_CEILING.md`
- GOCO provenance hashes recorded above and in the manifest.

## Reproduction commands

From the primary repository:

```powershell
git status --short --branch
Get-Content -Raw research/manifests/goco_compiler_source.json | ConvertFrom-Json
git diff --check
```

Read-only GOCO verification:

```powershell
git -C "C:\Users\Admin\OneDrive\Documents\GitHub\GOCO" status --short --branch
git -C "C:\Users\Admin\OneDrive\Documents\GitHub\GOCO" rev-parse HEAD
git -C "C:\Users\Admin\OneDrive\Documents\GitHub\GOCO" rev-parse HEAD:goco-compiler
```

## Decision

GO — Phase 0 acceptance criteria are satisfied. Phase 1 remains draft-only and
requires explicit approval.

## Implications for the paper

The project now has a contemporaneous provenance trail, falsifiable claims
ledger, explicit construct boundaries, threat register, and negative-result
retention policy. No empirical paper claim is yet justified.
