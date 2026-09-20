# Phase 1T pre-freeze construction record

This record predates preregistration and all Phase 1T model inference.

The first generated instrument contained five reference-test discrepancies:

- IO02, IO03, IO06, and IO07 expected the textual spelling of numeric-looking
  fields, while the pinned runtime's `strings.SPLIT` produced numeric values for
  those fields in the observed positions. Expected output was corrected to the
  actual supported runtime semantics; prompts and intended formatting were not
  changed in response to model output.
- CP04 compared `LETTER` values with scalar equality, which the semantic
  validator typed as unknown. It was replaced with five documented
  `strings.COUNT` reductions over lowercased text.
- ST05 and ST06 initially had identical identifier/literal-normalized token
  skeletons. ST06 gained an explicit valid-index bound and branch, preserving
  its character-selection semantics while making its control flow distinct.
- IO03 and IO07 later had identical normalized multi-display skeletons. IO07
  was changed to explicit `TO_SENTENCE` conversions and one concatenated
  display. Its invoice-format semantics remained unchanged.

After correction, all 64 references passed all 329 hidden cases. These are
instrument-construction corrections, not model-result tuning.
