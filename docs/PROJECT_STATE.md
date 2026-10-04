# Project state — Self-Learning AI

Last verified repository HEAD: `841f5ca4a7b829fb87b7667315de89f0af2cacc2` (the commit before this handoff; the handoff commit adds only this file, `CLAUDE.md`, `AGENTS.md` and a README status line)
Last substantive state review: 2026-10-05 (Opus takeover review plus the specification-level coverage feasibility audit)
Current project-head model: Claude Sonnet (Opus as escalation)
Current execution agent: Codex
Current phase: **Phase 3C-CONF1 — methodology reopened; coverage re-baseline required. No implementation, candidate construction or model execution is authorized.**

This file is the single source of truth for current project state. It summarizes and points; the files it names are the authorities. If this file conflicts with a frozen artifact, the artifact wins and this file must be corrected.

---

## A. Project objective

**Overall goal.** Test whether a small language model can acquire objectively verified programming-language capabilities sequentially, retain them in adapter parameters without documentation in the prompt, and reject updates that cause preregistered unacceptable forgetting. The domain is GOCO, a small private language whose pinned compiler plus hidden test cases (not the model) decide correctness. Model: `Qwen/Qwen2.5-Coder-3B-Instruct` (pinned revision), 4-bit NF4 QLoRA rank-16 adapters, immutable base weights, one RTX 3060 6 GB laptop GPU. Research question: `docs/research/RESEARCH_QUESTION.md`; hypotheses: `docs/research/HYPOTHESES.md`; claims: `docs/research/CLAIMS_LEDGER.md`.

**Strongest demonstrated claim: `Level B — parameterized behavioral acquisition`.** Phase 2B (confirmatory, three seeds) showed that QLoRA adapters, with no documentation at inference, raise hidden-test pass@1 on a fresh 128-task GOCO suite from 0% (base) to 50.8–54.7%, in all eight task families. Large train/held-out gaps (≈43–49 points) limit this to narrow behavioral acquisition.

**Not demonstrated:** continual learning; retention of previously acquired tasks across sequential updates; effective forgetting mitigation at the task level; broad or compositional generalization; self-directed learning; autonomous or self-modifying improvement; persistent knowledge in any general sense. Do not describe the project's results with those terms.

**Why CONF1 exists.** The continual-learning programme stalled at a prerequisite: in the original Phase 3C the adapters could not even acquire the compositional "A" capability (acquisition gate failed in every seed), so retention could not be tested. Development studies (DEV1/DEV2/DEV2R) then suggested that *how* training examples are presented matters: practising pairs of predicates jointly ("composition") produced much better performance on new multi-predicate tasks than practising them independently. CONF1 is the preregistered, fresh-data confirmation of that curriculum effect. It is an acquisition/curriculum question; it does **not** test retention and cannot by itself raise the claim level above B.

## B. Key empirical history

| Phase | What was tested | Key result | Consequence |
|---|---|---|---|
| 1 / 1R / 1S / 1T | Base model knowledge of GOCO, with/without documentation | Base no-docs ≈0%; 1.5B unusable; 3B with documentation 14/64 (21.9%) — conjunctive 25% gate **failed** | 3B chosen as backbone; documentation alone insufficient |
| 2A | Exploratory QLoRA pilot | 0/64 → 18/64 dev; 99% train | Promising but possibly memorization |
| **2B** | Confirmatory multi-seed acquisition | 0/128 → 65, 70, 70/128; all 8 families; all 7 criteria **PASS** | **Level B claim** |
| 3A | Naive sequential A→B | A 29–31/32 then 0/32 after B; mean forgetting 93.75 pts | Catastrophic forgetting baseline |
| 3B | Fixed 20% replay vs naive | Gate PASS numerically (post-B A 15–16/32 vs 0/32), but **0/24** previously passed A tasks stayed passed | Net score gain, **not** preservation |
| 3C (confirmatory) | New A/B with acquisition gate | A scored 0, 7, 7/32 (gate needed 24/32) | `STOP_before_B_no_tuning`; EVAL_A consumed |
| 3C-DEV1 | Dense vs diverse training | 6/36 vs 12/36, entirely one near archetype; 0 on compositional/far | No broad structural gain |
| 3C-DEV2 | ISOLATED vs COMPOSITION (first try) | Execution stopped on an evaluator schema bug after one task | Suite consumed; plumbing risk demonstrated |
| 3C-DEV2R v2 | ISOLATED vs COMPOSITION (development) | Novel Composition 10/48 vs 38/48 (+58.3 pp, all 3 seeds positive); Structural Transfer 0/16 everywhere; Primitive Sanity seed differences −37.5 to +62.5 pp | Motivates CONF1; development-consumed |
| CONF1 Attempts 001–003 | Pre-freeze candidate construction (no model use) | 001: GOCO syntax error; 002: sanity references matched a consumed template; 003: 174 unadjudicated coarse-AST flags and incomplete task-essential coverage audit | All rejected, permanently non-confirmatory |
| CONF1 methodology (since 003) | Coverage-v2 (abandoned) → Coverage-v3 and ~10 frozen amendments | See §E | Methodology became very large (§H) |
| CONF1 feasibility audit (2026-10-05) | Can the frozen coverage rules pass on the frozen task population? | **No** — definite blockers in 56/64 evaluation specifications | **Current blocker (§D)** |

Reports: `research/results/PHASE_2B/report.md`, `PHASE_3A/report.md`, `PHASE_3B/report.md`, `PHASE_3C/README.md`, `PHASE_3C_DEV1/report.md`, `PHASE_3C_DEV2_EXECUTION_STOP/report.md`, `PHASE_3C_DEV2R_V2/report.md`, `PHASE_3C_CONF1_PREFREEZE/STOP_report.md`. Full registry: `docs/research/EXPERIMENT_REGISTRY.md`.

All earlier evaluation suites (Phase 1–3C, DEV1, DEV2, DEV2R) are **consumed**: never reuse them for tuning, selection or confirmation.

## C. Current CONF1 research question

**Plain English.** Two fresh adapters are trained from the same base on the same eight predicates with the same budget. One practises counting two predicates *independently*; the other practises counting their *overlap*. Is the second better at writing new programs that combine three or four of those predicates?

**Technical form** (`research/protocols/phase3c_conf1_proposed_protocol.md`; slot ledger `research/protocols/phase3c_conf1_slots.json`):

- **Predicates (8).** Numeric iteration: odd index, index ≡ 2 mod 3, index divides n, first-half index. Array reduction (four `|`-separated signed integers): negative, even, value² > 4, value > index.
- **Training population.** 60 paired slots × 2 conditions = 120 programs (30 per domain; all six predicate pairs × five offsets {0,2,4,6,8}; both loop directions). Paired programs are byte-identical except the marked treatment expression:
  - `ISOLATED`: `total+=(hitP+hitQ).`
  - `COMPOSITION`: `total+=(hitP*hitQ).`
  - Prompts differ only in a marked treatment clause. Attempt 003 achieved 60/60 exact scaffold matches and a 0.78% full-token difference (supervised tokens equal).
- **Evaluation population.** 64 specifications: 32 primary Novel Composition (graphs G1–G4 × 4 rotations × 2 domains; G1=(P∧Q)∨(P∧R), G2=(P∧Q)+(Q∧R)+(R∧S), G3=(P∧Q)+(P∧R)+(P∧S), G4=((P∨Q)∧R)+(Q∧S)); 16 Primitive Sanity (single predicate, offsets 0 or 3); 16 Structural Transfer (PREFIX ordered-pair count and TWO_PASS product of counts). Five hidden cases each. Universe = 120 + 64 = 184 specifications.
- **Training recipe.** Fresh rank-16 NF4 QLoRA per cell, 180 exposures, 24 optimizer steps, max length 320, fixed final epoch.
- **Seeds.** Five paired seeds: 20280117, 20280223, 20280329, 20280411, 20280507. All primary; no selection or substitution.
- **Acquisition gate.** Every one of the 10 cells must score ≥ 54/60 semantic passes on its own training prompts, or the result is `INDETERMINATE_INSUFFICIENT_ACQUISITION`.
- **Primary endpoint.** Mean over seeds of the paired COMPOSITION − ISOLATED pass@1 on the 32 primary tasks (one greedy generation; pass = compile + all 5 cases). `CONFIRMATORY_SUPPORT_UNDER_CONF1` requires a point estimate ≥ +20 pp **and** a 95% two-way bootstrap interval (10,000 replicates, RNG seed 20290119, resampling seeds and whole graph blocks within domain) with lower bound > 0. Otherwise `NOT_CONFIRMED_UNDER_CONF1`. Heterogeneity and sanity qualifications are reported, not vetoes.
- **Claim limitation.** Even a positive result supports only: *pairwise conjunctive practice beats pairwise additive practice for generating multi-conjunction counting programs in GOCO under this budget*. The primary tasks reuse COMPOSITION's local `hitX*hitY` idiom, so this is bounded local-motif transfer, not general compositional reasoning. Four algebraic graphs, one DSL, one model.

**Status of this design: REOPENED.** The protocol's estimand, thresholds and gate were reviewed and are hash-bound by later freezes, but no executable CONF1 config/manifest exists, and the coverage methodology that gates candidate acceptance is internally infeasible (§D).

## D. Current scientific blocker

**Finding** (VERIFIED_FROM_ARTIFACT: `research/results/PHASE_3C_CONF1_PREFREEZE/specification_coverage_feasibility_audit.md`, commit `841f5ca`; independently confirmed against the frozen text by the Opus review). Verdict: **`FROZEN_STACK_COVERAGE_INFEASIBLE_AT_SPECIFICATION_LEVEL`**.

The frozen fairness rule (Coverage-v3 V3.4/V3.6) requires every evaluation-essential atomic capability to be present and active in **both** training conditions; the only exception is the COMPOSITION-only local pair-joint relation ("J"). Symmetric absence is explicitly FAIL. The frozen canonical graph recipe v2 (G) defines those capabilities at a fine typed granularity. Applying G to the frozen training and evaluation constructions gives:

| Blocker | Affected specifications | Status |
|---|---|---|
| Independent AND operator required by every primary graph; no training program (either condition) or predicate emits AND; J explicitly cannot satisfy it (G §9, §20; atomic amendment §5) | 32/32 primary | **Proven** (NEITHER) |
| OR required by G1/G4; absent from both conditions; the frozen OR≡`indicator(add>0)` equivalence is not realized in training | 16 primary | **Proven** |
| Boolean operand edges into AND/OR | 32 primary | **Proven** |
| PREFIX: prior-count state read into a MUL operand; MUL(indicator, int) | 8 structural | **Proven** |
| TWO_PASS: completed-count reads into a MUL operand | 8 structural | **Proven** |
| Sanity offset-3 accumulator initial value (training offsets are 0,2,4,6,8) | 8 sanity | **Proven** |
| ADD of two indicators (G2/G3/G4) absent from COMPOSITION; ISOLATED equality underdetermined | 24 primary | COMPOSITION absence proven; full key underdetermined |
| Mixed/accumulator ADD refinements, composite indicator roles, structural count roles | various | UNDERDETERMINED by frozen text |

Definite-blocker union: **56/64** evaluation specifications (all 32 primary, all 16 structural, 8 sanity). The audit assessed only key-profile existence; activity, case witnesses and source mapping were not assessed, so the remaining 8 are not shown to pass.

**Why this matters scientifically.** The conflict is not a serialization detail. The evaluation tasks need *both* treatment operators (multiplying indicators for conjunction, adding indicator terms) plus Boolean OR, which neither condition trains. Under the frozen rules, conjunction is simultaneously "the treatment" (J, COMPOSITION-only) and "an ordinary capability both conditions must have" (independent AND). Very fine typing (e.g., an exact offset value) also turns trivially novel details into coverage failures. Any implementation that "passes" this gate would have to reinterpret frozen rules, which would be an implementation-dependent scientific choice.

**Consequences (accepted by the project head):**

- Implementation of graph-v2/B1/D2/wire/RO/E5 machinery is **stopped**; building it would only produce a deterministic coverage FAIL.
- The wire-format proposal is **not to be frozen** (its two narrow repairs were reviewed as correct, but they serialize a design that cannot pass).
- **Attempt 004 remains nonexistent and unauthorized.** No candidate construction, model loading, training or evaluation.
- A **consolidated CONF1 methodology re-baseline** is required before any further implementation. It must decide, prospectively and before any new candidate is generated: (1) the exact treatment construct (is conjunction the treatment?); (2) how OR in G1/G4 is handled; (3) the granularity of coverage keys (operator vs typed role vs exact values); (4) whether Structural Transfer and the sanity offset-3 variant block or are descriptive; (5) which of the existing coverage/accounting layers are retained, simplified or superseded. These are Opus-escalation decisions (§M) requiring user authorization.

## E. What is frozen vs proposed vs historical

All under `research/protocols/` unless noted. "Frozen" means a freeze manifest binds exact bytes; it does **not** mean implemented or feasible. Hashes live in the freeze manifests.

| Item | File(s) | Role | Status |
|---|---|---|---|
| CONF1 design protocol (estimand, thresholds, gate, bootstrap, scaffold) | `phase3c_conf1_proposed_protocol.md` | Scientific design | Reviewed; hash-bound by later freezes; titled "design proposal"; no executable config/manifest. **Reopened** for coverage semantics |
| Semantic slot ledger | `phase3c_conf1_slots.json` | 184-specification population | FROZEN |
| AST adjudication v2 | `phase3c_conf1_ast_adjudication_v2.md` | Consumed-template overlap rule (E2) | FROZEN |
| Coverage-v3 | `phase3c_conf1_coverage_v3_proposed.md` + `_freeze.json` (+ `phase3c_conf1_coverage_v3_v2_disposition.md`) | Fairness gate V3.1–V3.8, E1–E6 | FROZEN, **shown infeasible with G** |
| Atomic/activity/output amendment | `phase3c_conf1_coverage_v3_atomic_activity_output_amendment_proposed.md` + `_freeze.json` | Activity/output evidence classes | FROZEN |
| Paired-scaffold normalization | `phase3c_conf1_paired_scaffold_normalization_proposed.md` + `_freeze.json` | Treatment-symmetry check (E3) | FROZEN; sound and simple |
| INPUT_DOMAIN case classes | `phase3c_conf1_input_domain_case_classes_and_training_amendment_proposed.md` + `_freeze.json` | Input-domain coverage | FROZEN |
| Structural-transfer pair (PREFIX/TWO_PASS) | `phase3c_conf1_structural_transfer_{semantics,topology}_amendment_proposed.md`, `phase3c_conf1_structural_transfer_pair_freeze.json` | Exploratory endpoint definition | FROZEN |
| REFERENCE_ONLY catalog + interface v2 | `phase3c_conf1_reference_only_catalog_proposed.md`, `phase3c_conf1_reference_only_interface_clarification_proposed_v2.md` + freezes | Proof that extra source constructs are inert | FROZEN; RO implementation paused |
| Canonical graph recipe v2 ("G") | `phase3c_conf1_canonical_contract_graph_recipe_proposed_v2.md` + `_v2_freeze.json` | Typed canonical graph defining coverage keys | FROZEN, **source of the infeasibility** |
| Delegated evidence interfaces + B1 binding | `phase3c_conf1_delegated_evidence_interfaces_proposed.md`, `phase3c_conf1_delegated_evidence_interfaces_binding_amendment_proposed.md` + freezes | Report schemas, row formulas | FROZEN |
| D2 direct-support accounting | `phase3c_conf1_direct_support_accounting_amendment_proposed_v2.md` + `_v2_freeze.json` | Four-bucket source accounting | FROZEN |
| Graph-v2 wire-format binding | `phase3c_conf1_canonical_graph_v2_wire_format_binding_amendment_proposed.md` | Serialization of G | **PROPOSED / UNFROZEN**, revised at `9887c38`; do not freeze pending re-baseline |
| Specification coverage feasibility audit | `research/results/PHASE_3C_CONF1_PREFREEZE/specification_coverage_feasibility_audit.md` | Evidence for §D | NON-NORMATIVE ANALYSIS (accepted as correct) |
| Development readiness evidence | `research/implementation_notes/` (~325 MB) | Development-only tranches (Boolean mapping, state, essentiality, value/output, RO) | DEVELOPMENT_ONLY; predates G/B1/D2; never scientific evidence |
| Coverage-v2 (`phase3c_conf1_coverage_v2*`), AST v1 (`phase3c_conf1_ast_adjudication.md`), and superseded v1 proposals (`phase3c_conf1_canonical_contract_graph_recipe_proposed.md`, `phase3c_conf1_direct_support_accounting_amendment_proposed.md`, `phase3c_conf1_reference_only_interface_clarification_proposed.md`) | `research/protocols/` | Earlier methodology | HISTORICAL / SUPERSEDED |
| Attempts 001–003 | `research/results/PHASE_3C_CONF1_PREFREEZE/attempt_00{1,2,3}/` | Rejected candidates | HISTORICAL; never confirmatory; never select Attempt 004 content from their outcomes |
| CONF1 config, schedule, manifest, authorization field | — | Required before execution | MISSING |

## F. Current implementation state

VERIFIED_FROM_REPOSITORY at `841f5ca`. Code status, not protocol status.

**`src/self_learning_ai/conf1_v3/` (~7,200 lines, last changed 2026-10-02, before G/B1/D2 were frozen):**

| Component (modules) | What it does | Classification |
|---|---|---|
| `goco.py`, `core_ir.py` | Parser and typed IR/bounded executor for the builder-generated GOCO subset | Partially reusable (useful for any simpler auditor) |
| `contracts.py`, `contract_ir.py`, `requirements.py`, `requirement_mapping.py`, `requirement_verifier.py` | Pre-G Coverage-v3 contracts and requirement namespaces | STALE (pre-G key ontology) |
| `boolean_mapping.py`, `boolean_regions.py`, `boolean_region_checker.py`, `canonical_transport.py`, `transport_verifier.py`, `typed_alignment.py`, `canonical_activity.py`, `semantic_ir.py` | Boolean-region equivalence proofs and transport to semantic keys | STALE; maps `&&` to the J relation, which G-v2 contradicts |
| `state_*`, `essentiality_*`, `attribute_*`, `projection_*` | Development-only readiness kernels and verifiers | DEVELOPMENT_ONLY; stale |
| `reference_only_*` | RO inventory/kernel/context/resolution | DEVELOPMENT_ONLY; paused |
| `coverage.py`, `delegated.py`, `interfaces.py`, `provenance.py`, `binder.py` | Coverage findings, E1–E6 helpers, schema-v1 interfaces, 17-gate binder | STALE relative to B1/D2; binder concept reusable |

**Missing entirely:** graph-v2 builder, B1 producers, D2 accounting, wire serializer, E5 producer, CONF1 orchestration, and all CONF1 execution code (training runner, evaluator, scorer, acquisition gate, task-local RNG, atomic persistence/no-retry guard, analyzer with the frozen bootstrap). **No graph-v2/B1/D2 identifiers appear anywhere in `src/`, `scripts/` or `tests/`.**

**Reusable from earlier phases:** `scripts/build_phase3c_conf1_data.py` (produced Attempts 001–003; will need changes after re-baseline), `scripts/phase3c_conf1_structural_overlap_v2.py`, `scripts/audit_phase3c_conf1_references.py` and `scripts/audit_phase3c_conf1_tokens.py` (E1/E2/E4/E3-token style audits), and the DEV2/DEV2R runners (`scripts/train_phase3c_dev2.py`, `scripts/evaluate_phase3c_dev2r.py`, `scripts/analyze_phase3c_dev2r_v2.py`), which executed 588 generations cleanly and are the natural template for CONF1 execution code.

## G. Scientific principles (non-negotiable)

1. **Prospective decisions.** Every rule, threshold, population and analysis is frozen before the candidate or model results it governs. Non-model construction diagnostics may motivate a prospective change; model outcomes may never.
2. **No sealed or prohibited data.** Never open the legacy final-paper holdout (the 8 `final_paper` tasks inside `benchmark/tasks.json`, `benchmark/hidden_tests.json`, `benchmark/reference_solutions.json`). Do not read `research/protocols/phase3c_conf1_v3_synthetic_expected_labels.json` or attempt `hidden_cases.json` files unless a task explicitly authorizes it. Never tune on consumed suites.
3. **Treatment symmetry.** The only intended difference between conditions is the marked treatment expression and prompt clause; everything else is matched and audited.
4. **Preserve negative results.** STOPs, failures and rejections are recorded, never rerun or overwritten to get a better answer. One pass, no retries, all seeds primary.
5. **Claim conservatism.** Level B until preregistered evidence supports more. State limitations with every result.
6. **Fail closed on consequential ambiguity.** If authority does not uniquely determine a scientific behavior, STOP and surface it; never resolve it inside implementation.
7. **Separate the stages:** methodology/authority → implementation → candidate construction → candidate audit/freeze → execution authorization → execution → analysis. Passing one stage never authorizes the next.
8. **Model execution requires an explicit, separate user authorization** recorded as a JSON boolean in a frozen manifest.

## H. Simplification policy

The takeover review concluded that the coverage machinery became disproportionate: about 1.9 MB of CONF1 protocol text, a 17-gate binder and ~325 MB of development evidence for 184 ten-line programs generated from about six templates, and it did not surface the first-order infeasibility in §D. Complexity is now the main threat to internal validity and to explaining the paper.

**Essential for validity (keep):**

- Fresh, newly generated data; hidden cases; pinned compiler reference validation (E1).
- Exact paired-scaffold equality, token budget and schedule parity (E3).
- A coverage check that both conditions have the non-treatment ingredients evaluation needs, with **one explicit, prospectively declared treatment exception**.
- Full-graph novelty (E5): the complete primary function must not appear in training. For this design it reduces to a role-count argument plus exact truth tables.
- Hidden-case discrimination (E6); consumed-suite overlap reporting (E2/E4).
- Acquisition gate, five seeds, frozen estimand/threshold/bootstrap, one-pass execution, atomic persistence, boolean authorization.

**Historical complexity that may be replaced (recommended by the Opus review; NOT yet decided):** the occurrence-level typed canonical graph (G-v2), the wire format, B1 binding, D2 four-bucket source accounting, the REFERENCE_ONLY catalog/interface, and the counterfactual intervention engine (V3.5). A plausible replacement is a template-level coverage argument plus mechanical per-instance conformance to template and simple statement-level mutation liveness. Consumed-suite similarity gates could become descriptive (CONF1 adapters never train on consumed suites, so these protect only against designer bias), and Structural Transfer could become non-blocking and descriptive.

Until the re-baseline is frozen, the frozen documents in §E remain the operative authorities. Do not declare them obsolete, and do not implement either the old stack or a replacement.

## I. Dependency roadmap to Attempt 004

| # | Step | Completion condition | Unlocks |
|---|---|---|---|
| 1 | **Re-baseline decision brief** (options plus recommendation for the five decisions in §D) | User decides each point | Step 2 |
| 2 | **Consolidated re-baseline amendment** drafted (one document), independently reviewed and frozen prospectively; must include an on-paper feasibility check that the frozen populations can pass it | Freeze manifest committed | Implementation |
| 3 | **Implementation**: builder update, compact coverage/E-gate auditors, CONF1 runner/evaluator/analyzer adapted from DEV2R | Code matches frozen spec; reviewed diffs | Validation |
| 4 | **Synthetic/unit validation**: known-bad fixtures per gate, analyzer known-answer tests, fault injection, RNG-order invariance | All pass; no model | Dry run |
| 5 | **Static conformance + end-to-end dry run** with a fake model | Independent code-vs-spec review passes | Candidate construction |
| 6 | **Attempt 004 construction** (fresh construction seed) and all audits | All gates PASS, or STOP and record | Freeze |
| 7 | **Candidate freeze**: hashed manifest, `model_execution_authorized: false` | Committed | Authorization review |
| 8 | **Pre-execution authorization**: independent review; a single-diff commit flips the boolean | User authorizes | Execution |
| 9 | **Execution**: 10 cells, acquisition gate, primary/secondary evaluation, one pass | Raw outputs persisted | Analysis |
| 10 | **Analysis and reporting**: frozen analyzer, report, claims ledger and this file updated | Committed | Next research decision |

## J. Current next action

**Exactly one:** prepare the **CONF1 re-baseline decision brief**: for each of the five decisions in §D, state the options, the scientific trade-offs (construct validity, symmetry, feasibility, explainability) and a recommendation, and confirm feasibility on paper against the frozen 184-specification population.

- **Agent:** project head escalated to **Opus** (it changes treatment and coverage semantics, §M). Delivered to the user in conversation; it is written into the repository only after the user decides, via a later single Codex document task.
- **Type:** READ-ONLY analysis / DOCUMENT.
- **Still forbidden:** freezing the wire proposal; implementing graph-v2/B1/D2/RO/E5 or any replacement; modifying frozen authorities; constructing Attempt 004 or any candidate; model loading, training, inference or evaluation; reading prohibited data.

Update this section after every major milestone.

## K. Agent workflow

- **Claude Sonnet**: project brain and reviewer. Reads this file and relevant authorities, reviews results, decides the next action and writes Codex prompts.
- **Codex**: execution agent. Edits files, implements, tests and reports exactly what it did. Not a scientific decision-maker.
- **User**: authorization boundary for methodology changes, freezes and any model execution.
- **Opus**: escalation for consequential methodology and statistics decisions (§M).

Loop:
1. Sonnet reads `docs/PROJECT_STATE.md` and the authorities relevant to the current step.
2. Sonnet reviews the previous result.
3. Sonnet decides exactly one next action (or escalates).
4. Sonnet gives one complete Codex prompt: expected repository state, scope, allowed files, allowed execution, STOP conditions, validation, then stop.
5. Codex executes and reports.
6. The user returns the result.
7. Sonnet inspects the actual diff or artifact, not just Codex's summary.
8. This file is updated only when the state materially changes (see below).

## L. Verification language

Use these labels when provenance matters:

- `VERIFIED_FROM_REPOSITORY`: checked directly in code, Git history or tracked files at a stated commit.
- `VERIFIED_FROM_ARTIFACT`: checked by reading a specific committed artifact (report, manifest, audit).
- `REPORTED_BY_CODEX`: stated in a Codex report and not yet independently checked.
- `INFERENCE`: reasoning from verified facts; not itself verified.

## M. Escalate to Opus when

Escalate when a decision could change any of: the research question; the treatment or its definition; the training or evaluation populations; the primary endpoint; preregistered statistics, thresholds or gates; coverage semantics or key granularity; leakage or holdout policy; the claim level; or the interpretation of a consequential positive or negative result. Routine implementation review, test review and documentation stay with Sonnet.

## State update protocol

Update this file when: methodology authority changes; an audit changes the blocker; an implementation tranche is accepted; a candidate is frozen or rejected; model execution occurs; or scientific interpretation changes. Do not update it for trivial refactors. The updating reviewer must inspect the actual committed artifact or diff first, update the HEAD, date and next action at the top, remove statements that are no longer true rather than appending, and keep this file short: point to authorities rather than copying them.

## Repository boundaries and fixed facts

- Research repository: this repository, `https://github.com/AaditHire/Self-Learning-AI`. All research work happens here.
- GOCO product repository (`C:\Users\Admin\OneDrive\Documents\GitHub\GOCO`) is **strictly read-only**. The research instrument is a pinned compiler snapshot (GOCO commit `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`, JAR SHA-256 `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`). Provenance: `research/manifests/goco_compiler_source.json`.
- Base model weights are immutable; adapters are versioned and never merged. Mutable runtime state lives in gitignored `.runtime/`.
- Hardware: Windows 11, RTX 3060 Laptop 6 GB, 16 GB RAM.
- Methodology and reproducibility background: `docs/research/METHODOLOGY.md`, `docs/research/THREATS_TO_VALIDITY.md`, stage records in `docs/research/stages/`.
