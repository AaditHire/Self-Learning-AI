# Phase 1R documentation corrections

The Phase 1 snapshot at `docs/goco_language_reference.md` is immutable
historical evidence. Phase 1R creates
`docs/goco_language_reference_phase1r_v1.md` instead of rewriting it.

| Phase 1 issue | Phase 1R correction | Pinned implementation evidence |
|---|---|---|
| It did not define the complete top-level file shape. | A file is a bare sequence of statements; explicitly prohibit `PROGRAM`, packages, classes, and mandatory `main`. | `MyLanguageParser.jj::Program` parses `Statement()* EOF`. |
| It said functions may call themselves recursively. | Self-recursion and forward calls are unsupported by semantic validation. | `FunctionDeclarationNode.validate` validates the body before registering the function; `FunctionCallNode.validate` rejects missing table entries. |
| It did not state that `INPUT` is statement-only. | Declare the target first and use `INPUT(variable).`; prohibit expression-valued `INPUT` and prompt arguments. | `InputStatement` accepts exactly one identifier or indexed array target. |
| It did not contrast `SENTENCE` with the model's likely `STRING` prior. | Explicitly prohibit `STRING` and identify `SENTENCE` as the text type. | Grammar token and declaration productions accept `SENTENCE_TYPE`, not `STRING`. |
| It showed fragments but no unmistakable complete source file. | Add complete single-input, delimited-input, loop, and function examples with top-level execution. | Complete canonical examples were compiler-validated during Phase 1R instrument preparation; illustrative fragments were checked against grammar productions. |
| It did not warn against `READLINE`, Go imports, `func`, `fmt`, or `strconv`. | Explicitly prohibit these common generated constructs. | No corresponding grammar productions or runtime APIs exist. |
| It did not emphasize `ELSEIF` versus `ELSE IF`. | State that `ELSEIF` is one keyword. | Grammar consumes one `ELSEIF` token. |
| It broadly listed comparison operators without type caveats. | Warn that text/letter comparisons are not generally reliable; prefer string-library operations. | Phase 1 benchmark construction exposed rejected `LETTER` and text comparison cases. |
| It did not disclose repeated-input buffering behavior. | Recommend exactly one `INPUT`, with delimited parsing for multiple values. | Phase 1 pre-freeze validation produced 16 failures from repeated `INPUT`. |
| It listed `strings.TRIM` without its unusual arity. | Document `strings.TRIM(text, chars)` and the empty-character-set whitespace behavior. | `StringsLibrary.PARAM_COUNTS` requires two arguments and `doTrim` treats an empty second value as ordinary trim. |
| It did not expose the consecutive loop-update parser edge case. | Recommend for-style updates where applicable and avoid adjacent simple loop-body assignments/increments. | Phase 1 and Phase 1R pre-freeze reference validation reproduced the parser failure. |

These corrections describe the pinned implementation only and do not assert
features of later GOCO revisions.
