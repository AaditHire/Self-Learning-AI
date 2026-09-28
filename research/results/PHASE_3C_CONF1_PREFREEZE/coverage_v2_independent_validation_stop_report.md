# CONF1 coverage-v2 independent validation STOP

**Status:** `STOP_COVERAGE_V2_INDEPENDENT_VALIDATION_FAILED`

This is an implementation-method validation result, not a CONF1 scientific result. Attempt 004 was not constructed. No real model was loaded, trained, or queried; the sealed final-paper holdout was not accessed.

## Prospective sequence

1. Four-gap rule-to-code trace committed at `7eb0e92e3a09c224527ab93aeb8bee2b118136ff` before repair.
2. Six Suite-B expected labels frozen at `19aca2c9feed989f4a0489ee794d2a9141d0f377` before repair.
3. Auditor repair committed at `edf7a2978d339a65d3c14be20f2e85bf02005bea`.
4. Frozen Suite A passed 12/12; Suite B passed 6/6. The prior 150 algebraic and 7 bundle property checks passed. See `coverage_v2_repaired_regressions.json` and `coverage_v2_repaired_prior_properties.json`.
5. Eleven independent Suite-C labels frozen at `7a162159435109f2dd8c7688b990bcb13325cc9d` before its one repaired-auditor run.
6. Suite C passed 5/11 expectations. See `coverage_v2_suite_c_validation.json` for the complete expected-versus-observed matrix and reason codes.

## Suite C failure

All five expected-PASS fixtures were observed FAIL. Their frozen cases did not witness several required predicate constants or, for the pairwise COMPOSITION rows, the aggregator's final-item contribution. This invalidated training rows, removed them as coverage evidence, and produced cascading uncovered requirements. The expected-FAIL full-signature fixture was observed FAIL, but lacked its required `PROHIBITED_FULL_SIGNATURE` reason because its training signature was invalid; it therefore also mismatched its frozen expectation. The other three expected-FAIL fixtures and both signature-pair fixtures matched.

The validation result cannot be repaired by changing Suite-C labels, cases, implementation, thresholds, or equivalence rules after this run. Expanded properties and the complete rule-to-code conformance matrix were not run or claimed. The implementation is not approved for attempt 004.

## Frozen-boundary checks

- Normative rule SHA-256: `9b2bc3bbeec5d8036dce7e66b3f4f6582256e52881eedf9a3ff7c380c215af3b` (unchanged).
- Original Suite-A fixture SHA-256: `40cccc16844fb81ccb5d178c5665cb7e24dbb1d119dc97b7efad40bddcb507ae` (unchanged).
- Suite-B fixture SHA-256: `0a283e3e2805bacd89ced401c837654d4e4d089caac4ffa9089bce24b3fbf7cd`.
- Suite-C fixture SHA-256: `c2bc2cb55d42f8d82fedc03e409cdbf1d916a941f2c482cc1699c0792bea3c2f`.
- No attempt-004 artifact was found in the CONF1 prefreeze results location.

**Required next boundary:** independent review of the failed validation and a new prospective repair/validation instruction before further implementation work. Do not construct attempt 004 from this state.
