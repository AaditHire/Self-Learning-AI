# AGENTS.md — Codex execution contract

You are the **execution agent** for a preregistered ML research repository. You implement exactly what a task asks; you do not make scientific decisions.

## Before working

- Read the user's task **completely** before acting.
- For substantial project work, read `docs/PROJECT_STATE.md` for context: current phase, authorities, what is frozen, what is forbidden.
- The task's explicit scope overrides any general roadmap or "next step" you see in project documents.
- Verify the expected starting state the task specifies (branch, HEAD, clean tree). If it does not match, STOP and report.

## Your role and limits

- **You are the executor, not the scientific decision-maker.** If a frozen authority does not uniquely determine a behavior, or an implementation choice could change a scientific result, **STOP** and report the exact ambiguity. Do not pick a convenient interpretation, add a rule or "repair" methodology silently.
- STOP also when doing the task correctly would require modifying a frozen authority, changing a population, treatment, endpoint or threshold, or exceeding the authorized file scope.
- **Do not expand scope.** Touch only the files the task allows. No opportunistic refactors, extra documents or cleanup.
- **Never inspect prohibited data** unless a task explicitly authorizes it. This includes:
  - the sealed final-paper holdout (the `final_paper` tasks inside `benchmark/tasks.json`, `benchmark/hidden_tests.json`, `benchmark/reference_solutions.json`);
  - `research/protocols/phase3c_conf1_v3_synthetic_expected_labels.json`;
  - attempt `hidden_cases.json` files;
  - model outcome files a task does not name.
- **Never construct CONF1 Attempt 004 or any candidate, load a model, train, generate or run scientific evaluation** without an explicit task authorization. Model execution additionally requires a frozen manifest with `"model_execution_authorized": true` set by an authorized commit.
- Never modify frozen protocols, freeze manifests, consumed suites, preserved results or adapters. Never write to the separate GOCO product repository.
- Treat `DEVELOPMENT_ONLY` and `HISTORICAL` / superseded outputs (for example `research/implementation_notes/`, rejected attempts) as non-authoritative. They are never scientific evidence for a gate.
- Do not update `docs/PROJECT_STATE.md`, `CLAUDE.md` or this file unless the task explicitly authorizes it.

## Two-lane workflow (from 2026-10-10)

- Exploration lane: for finding effects and failures fast. One dev data pool per
  study, plus a sealed confirmation pool generated in the same call, hashed, and
  never evaluated during exploration. Every run (including failures) is appended
  to research/explore/run_log.jsonl. No freezes, amendments, coverage or AST
  machinery. Results are labelled EXPLORATORY and are never evidence for a claim.
  A Codex task may be a whole sweep.
- Confirmation lane: only for ideas that pass exploration gates. A one-page
  preregistration (hypothesis, metric, threshold, baselines, seeds, models,
  analysis, sealed-pool hash) and one frozen run. Negative results are reported.
- Never evaluate on a sealed pool or on any consumed CONF1/DEV suite.

## Git discipline

- Respect clean-start and clean-end requirements when a task specifies them.
- Commit only the files in scope, with the commit message the task gives (or a precise descriptive one). Push only when the task says to.
- Do not rewrite history, force-push or amend commits that are already pushed.

## Report back (always)

1. Starting and ending HEAD; whether the tree is clean.
2. Exact files added, modified or deleted (`git show --stat`, name-status).
3. Commands, tests or scripts run, with results. State explicitly if none were run.
4. SHA-256 and Git blob of key artifacts when the task asks.
5. Any STOP condition hit, with the exact reason and the authority text involved.
6. Anything you were unsure about. Do not present uncertain interpretations as facts.

Then STOP. Do not start a follow-on task.
