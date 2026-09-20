# Pre-freeze benchmark construction failures

These failures occurred while building the benchmark, before its hashes and the
Phase 1 inference protocol were frozen. They are retained because failed
instrument-development attempts are research evidence.

The first validation found 19 failing reference tasks. Sixteen used multiple
`INPUT` statements. GOCO constructs a new buffered reader for each `INPUT`, so
the first reader may consume later lines and subsequent calls see EOF. One task
used recursion, which the semantic validator rejected as an undefined function.
Two tasks used identifiers that collide with case-insensitive language tokens or
unsupported string comparisons. The failed result file was mistakenly
overwritten during pre-freeze iteration; this is recorded as a Phase 1 protocol
deviation. The console summary was 21/40 reference tasks passing.

After changing multi-value tasks to one delimited line and replacing recursion,
a second all-split validation left three failures:

- `EVAL-ST-002`: unsupported direct `LETTER != LETTER` comparison;
- `EVAL-CP-001`: parser failure on sequential assignments in a loop body; and
- `FINAL-ST-001`: semantic `UNKNOWN` type for chained letter comparisons.

That full second failure record remains locally at
`.artifacts/benchmark_validation_all.json`. The final pre-freeze validation of
all 40 reference programs passed. Routine validation then sealed and skipped the
eight final-paper tasks.
