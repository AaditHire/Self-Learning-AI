# EXP-0005 Phase 1R development construction failures

Before the Phase 1R development benchmark was frozen, its first validation had
6 failing reference tasks out of 24:

- `RDEV-LP-001` and `RDEV-CP-001` reproduced the pinned parser's failure on
  adjacent accumulator/update statements in a loop body. They were rewritten
  to use a for-style update.
- `RDEV-CP-002` used the Euclidean algorithm and reproduced the same parser
  edge on sequential state assignments. It was replaced by a structurally
  distinct prime-classification task.
- `RDEV-ST-001` revealed that `strings.TRIM` requires two arguments; the
  corrected reference now documents `TRIM(text, chars)`.
- `RDEV-IO-002` and `RDEV-IO-003` revealed that numeric-looking values returned
  by `strings.SPLIT` are displayed in numeric form (`10.0` rather than `10`).
  Expected outputs were corrected to the observed pinned-runtime semantics.

A second validation passed references but exposed excessive structural
similarity between a loop sum and a sum-of-squares composition task. The latter
was replaced by prime classification. The final pre-freeze validation passed
all 24 tasks and 97 hidden cases.

The failed machine-readable runs remain in the ignored local `.artifacts`
directory as `phase1r_development_validation_v1.json` through `v3.json`; this
tracked report preserves their scientific content without promoting mutable
construction artifacts to official experiment results.

