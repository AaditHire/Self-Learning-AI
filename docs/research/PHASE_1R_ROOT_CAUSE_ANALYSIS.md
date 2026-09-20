# Phase 1R root-cause analysis

## Evidence inspected

This analysis uses the immutable Phase 1 prompts, documentation, inference
configuration, all 48 consumed raw generations, compiler diagnostics, and the
pinned grammar/runtime. It does not inspect or run the legacy sealed holdout.

## Observed failure signatures

| Signature | No docs | Phase 1 docs |
|---|---:|---:|
| Markdown fenced output | 24/24 | 24/24 |
| Go `package main` | 24/24 | 0/24 |
| Unsupported `PROGRAM` wrapper | 0/24 | 24/24 |
| Unsupported `READLINE` | 0/24 | 6/24 |
| Unsupported `STRING` token | 18/24 | 17/24 |
| Some `INPUT(...)` form | 0/24 | 18/24 |
| Valid parse | 0/24 | 0/24 |

Average rendered input length increased from 124.3 tokens without docs to
1279.3 with docs. Average completion length decreased from 114.6 to 87.5
tokens. The documentation condition therefore changed behavior substantially,
despite equal executable performance.

## Findings

1. **Model prior is strongly implicated in the no-doc Go outputs.** The custom
   language name differs from the familiar language name only by two letters,
   and every no-doc generation used idiomatic Go scaffolding. This consistency
   is evidence of a strong Go prior, not proof of its internal cause.
2. **Program-structure ambiguity plausibly contributed to `PROGRAM`.** The
   Phase 1 reference described statements but gave no explicit full-file
   grammar, no complete top-level example clearly beginning at byte one, and no
   prohibition on `PROGRAM`. All documentation-assisted outputs invented the
   same wrapper family. The evidence supports association, not exclusive
   causation.
3. **The reference was factually incomplete and partly incorrect.** It falsely
   claimed recursion, did not say that `INPUT` is statement-only, did not warn
   against `STRING`/`READLINE`, and omitted runtime/parser limitations already
   observed during benchmark construction.
4. **Formatting instructions were ineffective.** Both conditions fenced every
   answer although the prompt requested source only. Phase 1 mechanically
   extracted the first fence, so fences did not themselves cause the syntax
   floor. Phase 1R nevertheless fixes a stricter one-block normalization rule
   before evaluation.
5. **Context length is not identified as a capacity failure.** Inputs were far
   below the 8192-token cap. The longer documentation could still affect
   attention or ordering, but the Phase 1 data cannot isolate that effect.
6. **Documentation ordering is a plausible but untested contributor.** Critical
   negative constraints were absent rather than merely late. Phase 1R compares
   a corrected reference with front-loaded contract variants on development
   data only.

## Causal limits

Phase 1 was not factorially designed to distinguish model prior, ambiguity,
document errors, context length, ordering, and examples. Phase 1R therefore
treats these as supported observations and plausible mechanisms, not isolated
causal estimates.

