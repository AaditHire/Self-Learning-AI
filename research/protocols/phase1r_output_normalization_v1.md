# Phase 1R output normalization v1

This presentation-only protocol is fixed before Phase 1R model evaluation and
is applied identically to every condition.

1. Remove leading and trailing whitespace from the decoded response.
2. If the response contains exactly one Markdown fenced code block, extract
   only the text inside that block, discarding an optional fence language tag
   and explanatory text outside the fence.
3. Otherwise use the complete trimmed response unchanged.

The normalizer never repairs syntax, translates languages, inserts or removes
statements, removes a `PROGRAM` wrapper, changes identifiers, or otherwise
modifies program semantics. Multiple fenced blocks are not combined or chosen
between: the complete response remains unchanged and is expected to fail if it
is not valid GOCO.

