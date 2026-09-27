# CONF1 structural-overlap adjudication v2: normative rule

Version 2 is a generic, source-pair rule. It does not use fixture names, candidate IDs, attempt numbers, historical outcome data, or similarity thresholds. It supersedes v1 for **future** prospective audits; v1 and its failed result remain unchanged. No attempt 004 is part of this rule-development task.

## Input validity and structural representation

Inputs are GOCO programs valid under the pinned compiler. The v2 scanner follows the GOCO grammar's token boundaries: a statement-ending `.` is always a `DOT` token, even without following whitespace. In particular, `n.input(n)` tokenizes as `ID(n), DOT, INPUT_CMD(input), ...`, because `input` is a recognized keyword. A dotted library call is recognized only from the sequence `imported-namespace, DOT, member-name, LPAREN`; the namespace must have appeared in an `IMPORT` statement in the same program. GOCO built-in object method names after `DOT` are retained. Unrecognized characters or unbalanced grouping cause an audit error, never a similarity decision.

The canonical representation is a source-order token tree with nested `()`, `[]`, and `{}` groups. Statement terminators and top-level statement order remain explicit. Identifiers are alpha-renamed by first occurrence with repeated identity retained throughout the program. GOCO keyword spellings are mapped to one canonical keyword only for the exact case variants accepted by the pinned grammar. Library names and API/member names keep their exact spelling and case. Numeric literal magnitudes and string/character literal contents become typed placeholders. Unary sign, Boolean/arithmetic/comparison/assignment operators, delimiters, type names, and array indexing remain explicit. The compiler's parser is the authority for source validity; the token tree is the adjudication representation, not a replacement compiler AST.

### INCIDENTAL_NORMALIZED_AWAY

- Whitespace, line breaks, indentation, and GOCO comments.
- Exact grammar-accepted keyword casing, including lower-case spellings in the failed v1 fixture.
- Consistent renaming of user variables and other user-defined identifiers. Repeated-identifier relationships remain.
- Numeric magnitudes and string/character contents **for this template-reuse comparison**. Their task-essential roles remain subject to the separate coverage and semantic audits.

### TASK_STRUCTURAL_RETAINED

- Source-order sequence of statements. No statement reordering is normalized: even apparently independent statements can differ through input, mutation, errors, or future use. The adjudicator may therefore leave some equivalent rewrites structurally distinct rather than silently assuming commutativity.
- Nested control-flow and loop grouping, including loop headers, iterator updates, branch count/order and predicate placement.
- Boolean/composition and arithmetic operators, grouping, array indexing, assignments, accumulator update operators and repeated variable-use identities.
- Imported library identity, API/member call identity, call arity/argument order, and output command and expression structure.
- Task-essential branch relationships and aggregation/dataflow topology as expressed by ordered operations and variable-use links.

No semantic algebraic rewriting is performed. In particular, operand swaps, reassociation, dead-code removal, assignment desugaring, and branch reorderings remain structural differences unless a later independent design review freezes a separate generic rule before candidate construction. This rule is exact equality, not a graded similarity threshold.

## Exact labels

For a candidate/consumed pair, compute both the unchanged legacy coarse AST proxy and the v2 canonical token tree.

1. If v2 canonical trees are equal, label `PROHIBITED_STRUCTURAL_TEMPLATE_REUSE`, regardless of coarse equality.
2. Otherwise, if the coarse proxies are equal, label `COARSE_AST_EQUALITY_ONLY`.
3. Otherwise, label `STRUCTURALLY_DISTINCT`.

Exact prompt/source and normalized-source/full-template matches remain separate prohibitions and must be reported independently. V1's frozen fixture label `NO_STRUCTURAL_TEMPLATE_REUSE` is a legacy spelling for v2's `STRUCTURALLY_DISTINCT` **only in the regression harness**; the v1 fixture file is not changed. No fixture-specific production exception is permitted.
