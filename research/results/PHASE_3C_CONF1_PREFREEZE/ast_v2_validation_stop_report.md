# CONF1 AST v2 recovery STOP: coverage method not ready

**Status:** `STOP_COVERAGE_METHOD_NOT_READY`. This is synthetic adjudicator-development evidence, not a CONF1 candidate or scientific result. Attempt 004 was not constructed. No model was loaded, trained, or used for inference; the sealed final-paper holdout was not accessed.

## Preserved boundary and root cause

V1 implementation, rule, fixtures, expected labels, and attempt-003 evidence remain unchanged. The frozen v1 fixture suite is designated `ADJUDICATOR_DEVELOPMENT_REGRESSION_FIXTURES_V1` in `ast_v2_root_cause.md`. Its failed spacing/case control was semantically superficial: both programs parsed and gave the same outputs for n=0..4. V1's regex swallowed `n.input` into an API token at a statement boundary, causing unequal enhanced tuples while the coarse proxy remained equal. Diagnosis commit: `0d689292da9389dd7191342469c3b2e2bf2f854d`.

## V2 rule and validation

Normative rule commit: `912e2c4f6fdc87904e5271bc8ed2f42bc9eacc89`. The rule SHA-256 is `962960ed6d766b574d2f9812b8ade5b5faa824acfe84e85b520636e2d6667fd9`. V2 implementation SHA-256 is `e437aa49e34092e0eae0682342782874382730dd463bdfb19efaf92511b753c7`.

All 8 unchanged v1 fixtures passed under v2: 4 prohibited reuse, 3 coarse-only, and 1 structurally distinct (the old negative label is mapped to the v2 spelling only in the regression harness).

Fresh validation labels were frozen **before** their first v2 run in commit `2ae8d8a343b9f7c7e363160d25a21f5eea188051`; fixture file SHA-256 `18f8b30693ca0b55bb2b5add1a8bcd14e8a87bce9666f7faeef25279c3309339`. All 22 fresh fixture programs compiled and executed with the pinned GOCO compiler. One subsequent v2 validation run passed 11/11:

| Expected \ Observed | Prohibited reuse | Coarse only | Structurally distinct |
|---|---:|---:|---:|
| Prohibited reuse | 6 | 0 | 0 |
| Coarse only | 0 | 3 | 0 |
| Structurally distinct | 0 | 0 | 2 |

The generic deterministic metamorphic test generated 50 synthetic base programs. All 250 incidental transformations retained v2 identity, and all 200 task-structural transformations changed v2 identity. These tests are synthetic; they do not establish that every GOCO program is captured by the limited token-tree representation.

## Coverage-method review

The frozen coverage method SHA-256 is `670dd6837e8e12752e5143c71ffdea9a2366658f04df7cd678ea428d48ea8fd3`. It explicitly names semantic primitives, GOCO constructs, APIs, literal roles, output values, control flow, operators, dataflow/aggregation, and `TASK_ESSENTIAL` versus `REFERENCE_ONLY`. It is **not yet machine-implementable without discretionary decisions**:

1. It supplies no finite, slot-specific capability schema or extraction algorithm for all 120 training and 64 evaluation rows. The requirement to inventory every reference token cannot be reproduced deterministically from the prose alone.
2. “Semantically active,” “cases exercise the path,” and “behaviorally equivalent derivation” have no frozen operational tests. Two auditors can disagree on whether a source occurrence covers a required capability.
3. Literal roles and output categories are not completely enumerated. “Multi-digit where required” gives no rule for deciding when a task requires it or which frozen case must witness it.
4. The boundary between an atomic dataflow capability and a withheld structural signature is stated conceptually but not as an exact graph or edge representation. Prefix running pairs and products of counts could be classified differently by independent implementations.
5. A `REFERENCE_ONLY` classification requires a semantically equivalent covered alternative, but the allowed equivalence rules and machine-checkable witness format are unspecified.

No attempt-004 data was consulted or generated to make these findings. The method was not modified. Its completeness cannot be asserted, so the success boundary for a final validated v2 evidence commit was not met. The v2 rule, implementation and fixture-freeze commits are preserved for independent review, but **do not authorize** attempt 004 construction.
