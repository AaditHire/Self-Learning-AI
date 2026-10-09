# CONF1 implementation amendment C15

Project-head ruling and independent review: 2026-10-08. This amendment prepares
one reviewed continuation; it does not authorize model execution.

## Trigger and review

E1-R2 stopped while scoring frozen confirmatory index 128 (task 129/640):
seed 20280223, isolated, CONF1-NC-AR-G1-R0. Its raw generation was persisted;
its score was not. The reviewed incident is
`incidents/25dc8143d8ed456797a7c657ac7d9716.json`, byte SHA-256
`8563276e0f24ad726f9508e15ca449d759a6718748cf6f6cc9e0d7a4fa4d0db9`:

```json
{
  "error_type": "OSError",
  "evidence": {},
  "reason": "[Errno 22] Invalid argument",
  "stage": "confirmatory",
  "status": "STOP"
}
```

The project head completed the independent review required by protocol §7
(`review_E1_incident.md`). Aadit chose to continue under this prospective
amendment before any confirmatory score was viewed. Confirmatory scores,
compiler primary records and analysis remain sealed during implementation.

## Harness correction

`src/self_learning_ai/compiler.py` remains unchanged because its bytes are
hash-pinned by the frozen historical Phase 3C contract. On Windows, a pipe whose
child already exited can raise OSError EINVAL (CPython bpo-19612).

In `execution.compiler_score`, the CONF1 adapter treats an EINVAL raised by
compiler.run like a "system" result: it re-invokes the identical
compiler.run(source, stdin) with a fresh process at most two times, after sleeps
of 2 and 10 seconds. There are at most three attempts in total. Every other
OSError propagates immediately. Three consecutive EINVAL exceptions propagate
the final OSError, preserving the STOP incident content.

The first non-system result is returned; three system results return the last
result so the existing compiler-infrastructure GateStop fires. Timeout,
output_limit, lexical, syntax, semantic, runtime and success never trigger
re-invocation. If any re-invocation occurs, create-only
`<checkpoint_dir>/c15_system_retries.json` is written in finally through DEV2R
atomic_new_json, including before an exception propagates. EINVAL attempts
record case index, attempt number and einval true. Normal attempts record
case index, attempt number, einval false, is_system, exit_code, timed_out,
elapsed_ms and, for system attempts only, the first 200 stderr characters.
It records neither stdout nor expected values. The returned score-row schema
is unchanged.

## One reviewed continuation

`run_confirmatory_c15_continuation` verifies full candidate authorization and
hashes, the sole reviewed incident and its hash, absence of locks and temporary
files, the original STARTED marker, the re-verified acquisition PASS, and absence
of complete and continuation-started markers. It reconstructs all 640 entries
from the frozen cell and task order and verifies index 128 in code.

Every pre-index-128 artifact and raw/score hash must verify, and raw metadata
must match seed, condition, task ID and per-task RNG seed. Index 128 must have
only its started marker, raw record and original compiler directory containing
only generation.json. Later entries and stray confirmatory artifacts are
forbidden. The create-only `confirmatory_c15_continuation.started.json` binds
the amendment, reviewed incident/hash, index/task and persisted raw hash.

Task 128 is scored directly from its persisted raw text in a fresh
`.compiler-c15` checkpoint, with no generate call and no alteration of the old
compiler directory. Its score uses the same row-construction helper as _task.
Entries 129 through 639 use unchanged _task in frozen order, with the unchanged
generator and per-task RNG resets. All 640 rows are re-read and validated with
training records before writing the original complete-marker schema.

The evaluate entry point's `--c15-continue-confirmatory` flag loads the fixed
manifest-bound C15 incident record before any torch import and calls only the
continuation, using the original config, compiler and generator. Without the
flag its behavior is unchanged. Analysis accepts either no incident directory
or exactly the reviewed incident with its verified hash and matching C15 marker;
the record must itself match the manifest authority binding. Any additional or
unreviewed incident is refused. The inventory includes incident, marker and
retry-log JSON files.

## Equivalence, disclosure and further faults

For the 128 completed tasks, no compiler.run call raised EINVAL (it would have
crashed) or returned "system" (it would have raised GateStop). Therefore the
amended CONF1 adapter would have produced byte-identical score rows for them. Their results
are neither recomputed nor altered. The deterministic fixture test compares
all 640 rows and analysis against uninterrupted execution.

The final report must disclose that task 128's score comes from a fresh compiler
checkpoint (`.compiler-c15`), and the model for the rest of cell 3 is loaded at
entry 129 rather than entry 128. Generation remains greedy.

Any further fault causes STOP. Its incident makes analysis refuse. The run-once
marker prevents a second continuation; none is authorized. Re-freezing resets
model_execution_authorized to false; continuation authorization is pending.
