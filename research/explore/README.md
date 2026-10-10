# Exploration lane (EXPLORATORY)

- Exploration finds effects and failures quickly, using one dev pool per study
  and a sealed confirmation pool generated in the same call and hashed.
- Never evaluate the sealed pool during exploration, or use consumed CONF1/DEV
  suites. Sealed references are checked only during pool construction.
- Append every run, including failures, to `run_log.jsonl`.
- No freezes, amendments, coverage or AST machinery in exploration.
- Results are EXPLORATORY and never evidence for a claim; tasks may be sweeps.
- Confirmation follows exploration gates: one-page preregistration (hypothesis,
  metric, threshold, baselines, seeds, models, analysis, sealed-pool hash), then
  one frozen run. Report negative results.

Rules: `../../AGENTS.md`, Two-lane workflow (from 2026-10-10).
Run ledger: `run_log.jsonl`.
B0 dev pool: `b0/dev_pool.json`; manifest: `b0/pools_manifest.json`.
Sealed B0 pool: `b0/sealed/sealed_pool.json` (never load in exploration).

literature review: see project file phase_next/literature_review_2026-10.md (outside repo)
