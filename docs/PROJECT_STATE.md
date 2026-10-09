# Project state — Self-Learning AI

Last verified repository HEAD: `c4aa4bdcc9586821ae2286e3f5f18efaa71d1374`
Last substantive state review: 2026-10-08
Current project-head model: Claude Opus 5.5 (designated by the user 2026-10-05; previous project head: Claude Sonnet)
Current execution agent: Codex
Current phase: **R1 + R2 frozen; implementation accepted; Attempt 004 constructed (2da5b85) and frozen (c4aa4bdcc9586821ae2286e3f5f18efaa71d1374); model execution NOT authorized; step 8 (project-head readiness review, then the user's one-line authorization) next**

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
| CONF1 feasibility audit (2026-10-05) | Can the frozen coverage rules pass on the frozen task population? | **No** — definite blockers in 56/64 evaluation specifications | **Resolved historical blocker (§D)** |

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
- **Evaluation population.** 64 specifications: 32 primary Novel Composition (graphs G1–G4 × 4 rotations × 2 domains; G1=(P∧Q)∨(P∧R), G2=(P∧Q)+(Q∧R)+(R∧S), G3=(P∧Q)+(P∧R)+(P∧S), G4=((P∨Q)∧R)+(Q∧S)); 16 Primitive Sanity (single predicate, offsets 0 or 3); 16 Structural Transfer (PREFIX ordered-pair count and TWO_PASS product of counts). Five hidden cases each. Universe = 120 + 64 = 184 specifications. R1 (frozen) replaces array G3 with G3P=(P∧Q)+(P∧R) and repairs the array role maps; the primary count stays 32.
- **Training recipe.** Fresh rank-16 NF4 QLoRA per cell, 180 exposures, 24 optimizer steps, max length 320, fixed final epoch.
- **Seeds.** Five paired seeds: 20280117, 20280223, 20280329, 20280411, 20280507. All primary; no selection or substitution.
- **Acquisition gate.** Every one of the 10 cells must score ≥ 54/60 semantic passes on its own training prompts, or the result is `INDETERMINATE_INSUFFICIENT_ACQUISITION`.
- **Primary endpoint.** Mean over seeds of the paired COMPOSITION − ISOLATED pass@1 on the 32 primary tasks (one greedy generation; pass = compile + all 5 cases). `CONFIRMATORY_SUPPORT_UNDER_CONF1` requires a point estimate ≥ +20 pp **and** a 95% two-way bootstrap interval (10,000 replicates, RNG seed 20290119, resampling seeds and whole graph blocks within domain) with lower bound > 0. Otherwise `NOT_CONFIRMED_UNDER_CONF1`. Heterogeneity and sanity qualifications are reported, not vetoes.
- **Claim limitation (R1 §2).** Even a positive result supports only: pair-joint indicator-product practice transfers, relative to independent additive practice, to new multi-role multi-term counting programs built from that idiom, in GOCO, under this budget, with one base model (Level B). ISOLATED has no conjunction exposure, so a positive result partly reflects availability of the joint idiom. It does not support general compositional ability, structural transfer, retention or continual learning.

**Status of this design: R1 + R2 FROZEN; Attempt 004 FROZEN.** Its manifest binds `research/protocols/phase3c_conf1_config_proposed.json` and the execution inputs. The candidate manifest remains `model_execution_authorized: false`; step 8 is next. Freeze evidence: `research/results/PHASE_3C_CONF1_PREFREEZE/attempt_004_freeze/freeze_report.json`.

## D. Resolved blocker (historical)

The accepted audit verdict was **`FROZEN_STACK_COVERAGE_INFEASIBLE_AT_SPECIFICATION_LEVEL`** (`research/results/PHASE_3C_CONF1_PREFREEZE/specification_coverage_feasibility_audit.md`, commit `841f5ca`), with a definite-blocker union of **56/64** evaluation specifications.
`research/results/PHASE_3C_CONF1_PREFREEZE/r1_specification_feasibility.json` also recorded 8 of 16 array primary slots as degenerate; array G3 admitted only 2 distinct non-degenerate functions.
R1 (freeze `622b8cd`) repaired the array population; R1 and R2 (freeze `e0e48de`) replaced the coverage machinery and resolved the blocker.
Current blocker: none scientific. Remaining pre-execution work is the project-head readiness review and the user's one-line authorization (§I).

## E. What is frozen vs proposed vs historical

All under `research/protocols/` unless noted. "Frozen" means a freeze manifest binds exact bytes; it does **not** mean implemented or feasible. Hashes live in the freeze manifests.

| Item | File(s) | Role | Status |
|---|---|---|---|
| CONF1 re-baseline R1 | `phase3c_conf1_rebaseline_r1_proposed.md` + `phase3c_conf1_rebaseline_r1_freeze.json` | Current methodology authority (treatment, catalog, gates, array population repair) | FROZEN |
| CONF1 amendment R2 | `phase3c_conf1_rebaseline_r2_proposed.md` + `phase3c_conf1_rebaseline_r2_freeze.json` | Domain-equivalent mutant list, requirement-directed training-case selection, K7 descriptive | FROZEN |
| R1 implementation clarifications C1–C6 | `phase3c_conf1_r1_implementation_clarifications.md` | Construction seed, compiler gate oracle, killed mutant, P4 scope, array and numeric primary cases | PROJECT-HEAD CLARIFICATIONS (commit 6192040) |
| R2 implementation clarifications C7–C9 | `phase3c_conf1_r2_implementation_clarifications.md` | C7 Statement kinds and K-row liveness; C8 P3 implementation; C9 Condition-neutral model-facing identifiers | PROJECT-HEAD CLARIFICATIONS (commit ad29adb) |
| Implementation clarifications C10–C11 | `phase3c_conf1_implementation_clarifications_c10_c11.md` | C10 P7/E4 overlap; C11 secondary tasks | PROJECT-HEAD CLARIFICATIONS (commit 410e7f2) |
| Implementation clarifications C12–C14 | `phase3c_conf1_implementation_clarifications_c12_c14.md` | C12 training schedule; C13 evaluation order/RNG/scoring; C14 analysis and bootstrap | PROJECT-HEAD CLARIFICATIONS (commit 9002fd7) |
| CONF1 execution config | `phase3c_conf1_config_proposed.json` | Execution config (hyperparameters copied from DEV2, CONF1 seeds, C12-C14 references) | File retains PROPOSED_NOT_FROZEN; exact bytes bound in frozen Attempt 004 (c4aa4bd) |
| CONF1 design protocol (estimand, thresholds, gate, bootstrap, scaffold) | `phase3c_conf1_proposed_protocol.md` | Scientific design | RETAINED; amended by R1 |
| Semantic slot ledger | `phase3c_conf1_slots.json` | 184-specification population | RETAINED; amended by R1 |
| AST adjudication v2 | `phase3c_conf1_ast_adjudication_v2.md` | Consumed-template overlap rule (E2) | DEMOTED to descriptive |
| Coverage-v3 | `phase3c_conf1_coverage_v3_proposed.md` + `_freeze.json` (+ `phase3c_conf1_coverage_v3_v2_disposition.md`) | Fairness gate V3.1–V3.8, E1–E6 | SUPERSEDED by R1 (freeze manifest still binds bytes) |
| Atomic/activity/output amendment | `phase3c_conf1_coverage_v3_atomic_activity_output_amendment_proposed.md` + `_freeze.json` | Activity/output evidence classes | SUPERSEDED/HISTORICAL |
| Paired-scaffold normalization | `phase3c_conf1_paired_scaffold_normalization_proposed.md` + `_freeze.json` | Treatment-symmetry check (E3) | RETAINED |
| INPUT_DOMAIN case classes | `phase3c_conf1_input_domain_case_classes_and_training_amendment_proposed.md` + `_freeze.json` | Input-domain coverage | RETAINED |
| Structural-transfer pair (PREFIX/TWO_PASS) | `phase3c_conf1_structural_transfer_{semantics,topology}_amendment_proposed.md`, `phase3c_conf1_structural_transfer_pair_freeze.json` | Exploratory endpoint definition | semantic definitions retained as exploratory; coverage clauses superseded |
| REFERENCE_ONLY catalog + interface v2 | `phase3c_conf1_reference_only_catalog_proposed.md`, `phase3c_conf1_reference_only_interface_clarification_proposed_v2.md` + freezes | Proof that extra source constructs are inert | SUPERSEDED by R1 (freeze manifest still binds bytes) |
| Canonical graph recipe v2 ("G") | `phase3c_conf1_canonical_contract_graph_recipe_proposed_v2.md` + `_v2_freeze.json` | Typed canonical graph defining coverage keys | SUPERSEDED by R1 (freeze manifest still binds bytes) |
| Delegated evidence interfaces + B1 binding | `phase3c_conf1_delegated_evidence_interfaces_proposed.md`, `phase3c_conf1_delegated_evidence_interfaces_binding_amendment_proposed.md` + freezes | Report schemas, row formulas | SUPERSEDED by R1 (freeze manifest still binds bytes) |
| D2 direct-support accounting | `phase3c_conf1_direct_support_accounting_amendment_proposed_v2.md` + `_v2_freeze.json` | Four-bucket source accounting | SUPERSEDED by R1 (freeze manifest still binds bytes) |
| Graph-v2 wire-format binding | `phase3c_conf1_canonical_graph_v2_wire_format_binding_amendment_proposed.md` | Serialization of G | REJECTED; never frozen |
| Specification coverage feasibility audit | `research/results/PHASE_3C_CONF1_PREFREEZE/specification_coverage_feasibility_audit.md` | Evidence for §D | NON-NORMATIVE ANALYSIS (accepted as correct) |
| Development readiness evidence | `research/implementation_notes/` (~325 MB) | Development-only tranches (Boolean mapping, state, essentiality, value/output, RO) | DEVELOPMENT_ONLY; predates G/B1/D2; never scientific evidence |
| Coverage-v2 (`phase3c_conf1_coverage_v2*`), AST v1 (`phase3c_conf1_ast_adjudication.md`), and superseded v1 proposals (`phase3c_conf1_canonical_contract_graph_recipe_proposed.md`, `phase3c_conf1_direct_support_accounting_amendment_proposed.md`, `phase3c_conf1_reference_only_interface_clarification_proposed.md`) | `research/protocols/` | Earlier methodology | HISTORICAL / SUPERSEDED |
| Attempts 001–003 | `research/results/PHASE_3C_CONF1_PREFREEZE/attempt_00{1,2,3}/` | Rejected candidates | HISTORICAL; never confirmatory; never select Attempt 004 content from their outcomes |
| Frozen candidate manifest with `model_execution_authorized` | `research/results/PHASE_3C_CONF1_PREFREEZE/attempt_004/candidate_manifest.json` | Frozen inputs and required execution authorization | CANDIDATE_FROZEN (c4aa4bd); boolean false |

## F. Current implementation state

VERIFIED_FROM_REPOSITORY at `c4aa4bdcc9586821ae2286e3f5f18efaa71d1374`. Code status, not protocol status.

Modules under `src/self_learning_ai/conf1_r1/` unless a full path is shown.

| Modules / scripts | Tranche | Accepted commit | Role |
|---|---|---|---|
| `primary.py`, `interp.py` | I1 | `36b9298` | Verified primary slots and canonical references; statement deletion and fail-closed subset interpreter |
| `gates_primary.py` | I2 | `6192040` | R1 primary gates and deterministic selection; pinned compiler supplies gate verdicts |
| `training.py` | I3 | `ad29adb` | R1+R2 training gates: P3, P4, R2-B case selector, P5 |
| `overlap.py`, `secondary.py` | I4a | `410e7f2` | C10 P7/E4 overlap and read-only consumed inventory; C11 secondary definitions and compiler E1 |
| `candidate.py` | I4b | `2670093` | Candidate builder, R2-A-aware P6 and synthetic dry run; construction requires explicit authorization |
| `schedule.py`, `analysis.py` | I5a | `9002fd7` | C12/C13 schedule and orders; C14 analyzer; analysis acquisition path corrected in I5b (`034ff88`) |
| `execution.py`; `scripts/train_phase3c_conf1.py`, `scripts/evaluate_phase3c_conf1.py`, `scripts/analyze_phase3c_conf1.py` | I5b | `034ff88` | Authorization check, create-only checkpoints and one-pass orchestration; GPU paths exercised only in the consumed-DEV2 smoke run |

H1-H5 closed in step 4 (`a456e9f`): 254 tests passed in the plugin-free counted run. Real GPU paths ran once in a non-scientific consumed-DEV2 smoke run (`097b74b`). The freeze writer is `scripts/freeze_phase3c_conf1_candidate.py` (`c4aa4bd`). V1-V5 and the prefreeze no-model audit passed; see `research/results/PHASE_3C_CONF1_PREFREEZE/attempt_004_freeze/freeze_report.json`.
`src/self_learning_ai/conf1_v3/` is non-authoritative pre-R1 code, not used by `conf1_r1`.
DEV2/DEV2R runners are reused by reference: `scripts/train_phase2a_qlora.py` (`TokenDataset`), `src/self_learning_ai/dev2r_evaluation.py` (`evaluate_task`), `src/self_learning_ai/benchmark.py` (`extract_source`).

## G. Scientific principles (non-negotiable)

1. **Prospective decisions.** Every rule, threshold, population and analysis is frozen before the candidate or model results it governs. Non-model construction diagnostics may motivate a prospective change; model outcomes may never.
2. **No sealed or prohibited data.** Never open the legacy final-paper holdout (the 8 `final_paper` tasks inside `benchmark/tasks.json`, `benchmark/hidden_tests.json`, `benchmark/reference_solutions.json`). Do not read `research/protocols/phase3c_conf1_v3_synthetic_expected_labels.json` or attempt `hidden_cases.json` files unless a task explicitly authorizes it. Never tune on consumed suites.
3. **Treatment symmetry.** The only intended difference between conditions is the marked treatment expression and prompt clause; everything else is matched and audited.
4. **Preserve negative results.** STOPs, failures and rejections are recorded, never rerun or overwritten to get a better answer. One pass, no retries, all seeds primary.
5. **Claim conservatism.** Level B until preregistered evidence supports more. State limitations with every result.
6. **Fail closed on consequential ambiguity.** If authority does not uniquely determine a scientific behavior, STOP and surface it; never resolve it inside implementation.
7. **Separate the stages:** methodology/authority → implementation → candidate construction → candidate audit/freeze → execution authorization → execution → analysis. Passing one stage never authorizes the next.
8. Model execution requires a frozen manifest with an authorized boolean, set only after project-head readiness review and the user's one-line confirmation.

## H. Simplification policy

The takeover review concluded that the coverage machinery became disproportionate: about 1.9 MB of CONF1 protocol text, a 17-gate binder and ~325 MB of development evidence for 184 ten-line programs generated from about six templates, and it did not surface the first-order infeasibility in §D. Complexity is now the main threat to internal validity and to explaining the paper.

**Essential for validity (keep):**

- Fresh, newly generated data; hidden cases; pinned compiler reference validation (E1).
- Exact paired-scaffold equality, token budget and schedule parity (E3).
- A coverage check that both conditions have the non-treatment ingredients evaluation needs, with **one explicit, prospectively declared treatment exception**.
- Full-graph novelty (E5): the complete primary function must not appear in training. For this design it reduces to a role-count argument plus exact truth tables.
- Hidden-case discrimination (E6); consumed-suite overlap reporting (E2/E4).
- Acquisition gate, five seeds, frozen estimand/threshold/bootstrap, one-pass execution, atomic persistence, boolean authorization.

Adopted and frozen in R1 (§§4-6, §9).

R1 is the operative methodology authority together with the documents R1 §9 marks RETAINED. Superseded documents are not to be implemented.

## I. Dependency roadmap to Attempt 004

| # | Step | Completion condition | Unlocks |
|---|---|---|---|
| 1 | **DONE — Re-baseline decisions** | Project-head decisions recorded in the committed R1 proposal | Step 2 |
| 2 | **DONE — R1 frozen (commit 622b8cd)** | Freeze manifest committed | Implementation |
| 3 | **DONE — implementation I1-I5b** (36b9298, 6192040, ad29adb, 410e7f2, 2670093, 9002fd7, 034ff88) | Code matches frozen spec; reviewed diffs | Validation |
| 4 | **DONE — synthetic validation and hardening H1-H5** (`a456e9f`) | 254 tests passed, plugin-free; no model | Conformance review |
| 5 | **DONE — static conformance review CONFORMS; infrastructure smoke** (`097b74b`) | Review accepted; one non-scientific real-model cell on consumed DEV2 | Candidate construction |
| 6 | **DONE — Attempt 004 construction** (`2da5b85`; seed 20290123) | All 18 candidate gates PASS | Freeze |
| 7 | **DONE — candidate freeze** (`c4aa4bdcc9586821ae2286e3f5f18efaa71d1374`) | Hashed manifest; `model_execution_authorized: false` | Authorization review |
| 8 | **DONE — C15 implemented, re-frozen and continuation authorized** (`611cdc2`, `8eb836c`, `7a2e022`). Open test-hygiene items, all pre-existing: the schedule_analysis audit hook breaks single-process suite runs; F1/F2 (DEV2R v2 manifest tests); F3/F4 (Coverage-v3 population_guard); F5 (`.gitattributes` is pinned by the Phase 3C execution manifest). | Completed | Execution |
| 9 | **DONE — execution**: continuation executed once, exit 0; runtime 7,578 files; execution record `a1ec61c` | Raw outputs persisted | Analysis |
| 10 | **DONE — analysis and reporting**: label `NOT_CONFIRMED_UNDER_CONF1`; report `research/results/PHASE_3C_CONF1/report.md`; CLM-013 | Completed | Next research decision |

## J. Current next action

- **Next action:** next research decision after CONF1 (project head plan), in a new phase.
- **Agent:** the project head proposes the plan; the user decides.
- **Type:** PLANNING.
- **Still forbidden:** any further use of CONF1 confirmatory data for model selection or tuning; edits to frozen CONF1 artifacts; the sealed final-paper holdout.
- **Preserve:** .runtime/phase3c_conf1 (git-ignored) holds the raw outputs hashed by execution/output_inventory.json. Do not delete it.

## K. Agent workflow

- **Project head** (designated by the user; currently Claude Opus 5.5): scientific decision-maker and reviewer under §M. Reads authorities, reviews results, decides the next action and writes Codex prompts. The user may re-designate the project head; the change must be recorded here and in CLAUDE.md.
- **Codex**: execution agent. Executes the exact authorized scope and reports; stops on ambiguity and never chooses a scientific rule.
- **User**: exceptional decisions in §M and the final model-execution one-line confirmation after project-head readiness review.
- **Second opinion**: an independent second opinion (for example from another Claude model) is optional and used only when the project head judges a consequential issue needs it.

Loop:
1. The project head reads `docs/PROJECT_STATE.md` and the authorities relevant to the current step.
2. The project head reviews the previous result.
3. The project head decides exactly one next action; an independent second opinion is optional under §M.
4. The project head gives one complete Codex prompt: expected repository state, scope, allowed files, allowed execution, STOP conditions, validation, then stop.
5. Codex executes and reports.
6. The user returns the result.
7. The project head inspects the actual diff or artifact, not just Codex's summary, and reports with VERDICT, the per-dimension tracker and a progress bar for the current phase.
8. This file is updated only when the state materially changes (see below).

## L. Verification language

Use these labels when provenance matters:

- `VERIFIED_FROM_REPOSITORY`: checked directly in code, Git history or tracked files at a stated commit.
- `VERIFIED_FROM_ARTIFACT`: checked by reading a specific committed artifact (report, manifest, audit).
- `REPORTED_BY_CODEX`: stated in a Codex report and not yet independently checked.
- `INFERENCE`: reasoning from verified facts; not itself verified.

## M. Decision authority

The designated project head (currently Claude Opus 5.5) decides scientific and methodology questions (treatment, coverage, gates, population repairs and analysis) within the research objective and Level B claim boundary. Decisions stay prospective, preserve negative results, avoid prohibited data and outcome-dependent changes, and fail closed on genuine ambiguity. Codex stops on ambiguity and reports it.

Ask the user only for: (1) a fundamental research-objective change; (2) a genuine value or preference choice that cannot be settled scientifically; (3) major external cost or irreversible consequences, including final confirmatory model-execution authorization after project-head readiness review, presented as a one-line confirmation because it consumes the suite; (4) a choice Claude cannot defensibly determine from the evidence. An independent second opinion (for example from another Claude model) is optional and used only when the project head judges a consequential issue needs it.

## State update protocol

Update this file when: methodology authority changes; an audit changes the blocker; an implementation tranche is accepted; a candidate is frozen or rejected; model execution occurs; or scientific interpretation changes. Do not update it for trivial refactors. The updating reviewer must inspect the actual committed artifact or diff first, update the HEAD, date and next action at the top, remove statements that are no longer true rather than appending, and keep this file short: point to authorities rather than copying them.

## Repository boundaries and fixed facts

- Research repository: this repository, `https://github.com/AaditHire/Self-Learning-AI`. All research work happens here.
- GOCO product repository (`C:\Users\Admin\OneDrive\Documents\GitHub\GOCO`) is **strictly read-only**. The research instrument is a pinned compiler snapshot (GOCO commit `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`, JAR SHA-256 `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`). Provenance: `research/manifests/goco_compiler_source.json`.
- Base model weights are immutable; adapters are versioned and never merged. Mutable runtime state lives in gitignored `.runtime/`.
- Hardware: Windows 11, RTX 3060 Laptop 6 GB, 16 GB RAM.
- Methodology and reproducibility background: `docs/research/METHODOLOGY.md`, `docs/research/THREATS_TO_VALIDITY.md`, stage records in `docs/research/stages/`.
