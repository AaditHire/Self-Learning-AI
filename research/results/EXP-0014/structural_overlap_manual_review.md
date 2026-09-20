# Phase 2A pre-training structural-overlap review

Date: 2026-09-20

This review was completed before any Phase 2A gradient step. The validator
compared each development task with its nearest training example and with the
consumed Phase 1R/1S/1T suites. The sealed Phase 1 final-paper holdout was not
opened.

## Decision criteria

- Prompt-token Jaccard at or above 0.75 requires review.
- Identifier/literal/library-normalized reference similarity at or above 0.90
  requires review.
- Any exact prompt reuse, shared generator lineage, shared algorithm label, or
  task that differs only by constants/identifiers is rejected.
- Code similarity alone is not treated as independence: the prompt semantics,
  algorithm, control flow, signature, and hidden mappings were inspected.

## Aggregate result

- Exact development prompt reuse: 0.
- Train/development lineage overlap: 0.
- Train/development algorithm-label overlap: 0.
- Train/development prompt flags: 0.
- Development/consumed-suite prompt flags: 0.
- Train/development normalized-code flags: 28.
- Development/consumed-suite normalized-code flags: 23.
- Disposition: retain all final flags. They share mandatory GOCO boilerplate or
  coarse loop/function/library skeletons, but not the same semantic target,
  lineage, algorithm label, structural signature, or hidden mapping.

Four earlier development constructions were rejected and regenerated before
this decision because they reused consumed task semantics or formatting
skeletons too closely. Those rejected artifacts remain in the EXP-0014
pre-freeze validation history.

## Train/development code flags

| Development / nearest training | Similarity | Review disposition |
|---|---:|---|
| EV01 / EV-LIN-02 | 0.920 | Cubic-minus-constant versus affine mapping; distinct polynomial degree. |
| EV02 / EV-WEIGHT-01 | 0.970 | Midpoint division versus weighted sum. |
| EV03 / EV-WEIGHT-01 | 0.987 | Product-plus-operands versus weighted sum. |
| EV04 / EV-WEIGHT-01 | 0.980 | Squared-speed product/division versus weighted sum. |
| EV05 / EV-WEIGHT-01 | 0.977 | Unit conversion versus weighted sum. |
| EV06 / EV-ABS-01 | 0.956 | Square root versus absolute distance. |
| EV07 / EV-ABS-01 | 0.959 | Clamp versus absolute distance. |
| EV08 / EV-WEIGHT-01 | 0.971 | Square-sum remainder versus weighted sum. |
| LP01 / LP-ODDS-01 | 0.971 | Fourth-power sum versus odd-number identity. |
| LP02 / CP-FILTER-01 | 0.992 | Odd counter versus divisibility-filtered sum. |
| LP03 / CP-FILTER-01 | 0.939 | Union-of-divisors sum versus one-divisor sum. |
| LP04 / CP-FILTER-01 | 0.992 | Conditional product versus conditional sum. |
| LP05 / LP-ODDS-01 | 0.983 | Bilinear index sum versus odd-number sum. |
| LP06 / CP-FILTER-01 | 0.992 | Nonmultiple counter versus multiple sum. |
| LP07 / LP-SQUARES-01 | 0.909 | Power-of-two library accumulation versus square sum. |
| LP08 / LP-ODDS-01 | 0.992 | Symmetric pair products versus odd-number sum. |
| FN01 / FN-SQUAREPLUS-01 | 0.977 | Quadratic with linear term versus square plus constant. |
| FN05 / FN-DISTANCE-01 | 0.979 | Bounded clamp versus absolute distance. |
| ST02 / ST-REPEAT-01 | 0.984 | Whitespace trim versus repetition. |
| ST07 / ST-REPEAT-01 | 0.968 | Substring extraction versus repetition. |
| ST08 / ST-REPEAT-01 | 0.945 | Lowercase then repeat versus direct repetition. |
| IO02 / IO-TWOLINE-01 | 0.958 | Numeric field lengths versus raw field display. |
| IO03 / IO-SWAP-01 | 0.973 | Uppercase/trim transformation versus field reordering. |
| IO04 / IO-SWAP-01 | 0.946 | Reverse/length derivation versus field reordering. |
| IO06 / IO-BRACKET-01 | 0.902 | Uppercase labeled lines versus delimiter enclosure. |
| IO08 / IO-SLASH-01 | 0.920 | Numeric conversion/increment with unit versus raw formatting. |
| CP02 / CP-FILTER-01 | 0.996 | Proper-divisor sum versus bounded multiple sum. |
| CP08 / CP-FILTER-01 | 0.974 | Odd-square filtered sum versus multiple sum. |

## Consumed-suite code flags

The final development tasks flagged against consumed artifacts were:

`EV01/SYN-MOD-EV1-001`, `EV02/SYN-MOD-EV2-001`, `EV03/RDEV-EV-002`,
`EV04/SYN-MOD-EV2-001`, `EV05/SYN-MOD-EV2-001`, `EV06/RDEV-ST-002`,
`EV08/RDEV-EV-002`, `CD08/P1T-CD02`, `LP01/SYN-MOD-LP1-001`,
`LP02/SYN-MOD-LP3-001`, `LP03/SYN-MOD-LP3-001`,
`LP04/SYN-MOD-LP3-001`, `LP05/SYN-MOD-LP1-001`,
`LP06/SYN-MOD-LP3-001`, `LP08/SYN-MOD-LP1-001`,
`FN01/SYN-MOD-FN3-001`, `FN07/RDEV-FN-003`, `ST02/SYN-MOD-ST2-001`,
`ST04/RDEV-ST-001`, `ST07/SYN-MOD-ST2-001`, `ST08/RDEV-ST-001`,
`CP02/SYN-MOD-LP3-001`, and `CP08/SYN-MOD-LP3-001`.

Manual inspection found shared bare-program, split/convert, counted-loop,
function-call, or string-library forms after identifiers, literals, and library
names were deliberately erased. The requested operations and hidden mappings
are different. None is a renamed or constant-only copy of the consumed target.

## Limitation

The audit demonstrates explicit separation under the recorded checks; it does
not prove statistical independence. GOCO's small grammar, mandatory input
boilerplate, and coarse normalization make high syntactic similarity
unavoidable. Results must therefore be reported with the structural-distance
categories and a train/development gap rather than as unrestricted
generalization.
