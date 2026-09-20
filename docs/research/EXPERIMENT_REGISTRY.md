# Experiment registry

Experiment IDs are immutable. Failed, rejected, and superseded experiments are
never deleted. Phase planning documents do not receive IDs until execution is
authorized and inputs are frozen.

| ID | Purpose | Date | Research commit | Model / revision | Adapter parent | Dataset hash | Compiler hash | Config hash | Seed | Hardware | Output | Summary | Status | Rejection reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EXP-0000 | Phase 0 repository/compiler audit and protocol foundation | 2026-09-19 | Working tree based on `1edb0f5c017302da9054dbb06c82b695612400fd` | None | None | None | GOCO commit `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`; compiler tree `f51973617cc3da8c78de88c668d8de6959575d6d` | Documentation-only; see Phase 0 Git diff | None | Windows 11; RTX 3060 Laptop 6 GB; Ryzen 7 6800HS; 16 GB RAM | `docs/research/stages/PHASE_00.md` | Read-only audit completed; no model run | COMPLETE / GO | N/A |
| EXP-0001 | Pinned compiler build and upstream conformance | 2026-09-20 | Working tree based on `0fabb29` | None | None | Upstream manifest SHA-256 `06693876…f3ad5f` | Runtime JAR SHA-256 `c6f45759…be879` | `phase1_toolchain.json` | None | Same host; Temurin 25.0.1+8 | `research/results/EXP-0001/conformance.json` | 87/88 exact; 44/45 expected-success and 43/43 expected-failure; one stale INPUT-prompt expectation | COMPLETE / CONDITIONAL PASS | One known upstream expectation mismatch |
| EXP-0002 | Build and validate separate LLM benchmark | 2026-09-20 | Working tree based on `0fabb29` | None | None | Tasks canonical SHA-256 `7d317c6b…be809`; tests `20fed5f1…9c7fd` | Runtime JAR SHA-256 `c6f45759…be879` | `phase1_benchmark.json` | None | Same host | `research/results/EXP-0002/benchmark_validation.json` | 40 tasks; 32 routine reference tasks passed; 8 final-paper tasks sealed after one construction validation | COMPLETE / PASS | N/A |
| EXP-0003 | Frozen base, no GOCO docs | 2026-09-20 | Working tree based on `0fabb29`; finalized by Phase 1 commit | Qwen commit `2e1fd397…f1098a` | None | Benchmark `7d317c6b…be809` | Runtime JAR `c6f45759…be879` | Inference config `7a6ab3e3…7584` | 20260920 (greedy) | RTX 3060 Laptop 6 GB; FP16 | `research/results/EXP-0003-0004/phase1_evaluation.json` | 0/24 pass; 0/24 parse; all outputs were Go `package main` programs | COMPLETE / NO-GO | Parse-level floor |
| EXP-0004 | Frozen base with complete trusted GOCO docs | 2026-09-20 | Working tree based on `0fabb29`; finalized by Phase 1 commit | Qwen commit `2e1fd397…f1098a` | None | Benchmark `7d317c6b…be809` | Runtime JAR `c6f45759…be879` | Inference config `7a6ab3e3…7584` | 20260920 (greedy) | RTX 3060 Laptop 6 GB; FP16 | `research/results/EXP-0003-0004/phase1_evaluation.json` | 0/24 pass; 0/24 parse; all outputs invented unsupported `PROGRAM` wrappers | COMPLETE / NO-GO | Parse-level floor; documentation protocol non-discriminating |

## Required fields for future entries

Before an experiment runs, assign its ID and freeze its purpose, exact commit,
model revision/hash, adapter parent, dataset manifest/hash, compiler hash,
configuration hash, seed or seed set, hardware record, and output path. After it
runs, append the result summary, status, and rejection reason without rewriting
the original protocol.
