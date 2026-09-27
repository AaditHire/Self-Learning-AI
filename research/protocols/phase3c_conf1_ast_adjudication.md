# CONF1 prospective structural-overlap adjudication, recovery v1

This rule is generic and applies to every candidate/history source pair in attempt 004. It was specified without using attempt-003 task acceptance or rejection outcomes. The historical coarse AST proxy remains an independently reported flag. It is not a prohibition by itself.

## Exact representation and comparison

`scripts/phase3c_conf1_structural_overlap.py` tokenizes a GOCO source without executing it. It rejects unrecognized tokens and unbalanced grouping. The enhanced signature preserves, in source order, all brackets, parentheses and braces; type declarations; input, import, loop, conditional and output statements; task-essential branch count and order; arithmetic, comparison, Boolean and assignment operators; API and library names; array indexing; repeated variable identity under deterministic alpha renaming; accumulator updates; aggregation and output-expression topology. Thus nesting, predicate location, and dataflow uses remain part of the signature. These are **SEMANTICALLY_STRUCTURAL** fields.

Whitespace, comments, identifier spellings, string contents and numeric magnitudes are **INCIDENTAL for template-overlap adjudication**. Numeric signs are operators and remain structural. The rule deliberately treats constant-only rewrites and prompt-only paraphrases as template reuse. Literal values and string delimiters are audited independently as task-essential capabilities; their normalization here does not waive coverage or semantic-case requirements.

For each pair, compute `COARSE_AST_EQUALITY` with the existing frozen coarse proxy and the enhanced signature with the code above. `PROHIBITED_STRUCTURAL_TEMPLATE_REUSE` means enhanced signatures are exactly equal, regardless of the coarse flag. `COARSE_AST_EQUALITY_ONLY` means coarse equality and unequal enhanced signatures. Otherwise the classification is `NO_STRUCTURAL_TEMPLATE_REUSE`. Exact prompt, exact source, normalized-source equality, and full-template matches remain separately reported and independently prohibited. No similarity score threshold can waive a prohibition or introduce a new one. No post-generation threshold or field change is permitted.

The exact signature is intentionally conservative about source order: a commutative operand reorder can produce a different signature. The consumed-suite audit still reports normalized-code similarity and full-template signatures; this rule makes no claim that unequal signatures prove semantic independence. Any uncertainty found after generation requires a STOP and another prospective design review, not a candidate-specific exception.

Synthetic fixtures and expected labels are frozen in `research/protocols/phase3c_conf1_ast_fixtures.json`. Run them before constructing attempt 004. All must pass, including the negative controls' coarse equality assertions, or `STOP_CONF1_AST_ADJUDICATION_FAILED`.
