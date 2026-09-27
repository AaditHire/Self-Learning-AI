# CONF1 prefreeze construction STOP

**Status:** `STOP_CONF1_PREFREEZE_FAILED`. This is a non-model construction and audit record, **not** a CONF1 result or frozen candidate. No CONF1 authorization manifest, adapter, model load, generation, inference, gradient, or training run exists. The sealed final-paper holdout was not accessed.

## Provenance and attempts

- Reviewed proposal verified before construction and committed alone at design-baseline commit `ebe5b1d90b1d44dce8551e29de3ebb8a807cfaa3`.
- Semantic ledger, deterministic candidate policy, all four Boolean contribution signatures and all 240 domain witness pairs committed at `602e311bc1b6027ff21b683e48513f5dda1be9f6`. Ledger SHA-256: `5fe76fbc02e9f65174327199c2004f7e51f19a7f3866ae15709744c5274415c2`; graph audit SHA-256: `4faff2b17fd7e29480e791e6095923306306c37463e64a8a6e94eb5e2954a329`.
- `attempt_001` was rejected on pinned-GOCO syntax for unparenthesized compound assignment. Both conditions were corrected symmetrically; original files and rejection record were retained.
- `attempt_002` passed all 184 canonical references and 920 semantic cases but was rejected because all 16 Primitive Sanity references matched a consumed DEV2 normalized full template. A prospective source-template correction was committed at `3ed3c746039541a3f2546bee99add096bb45865e` before the next candidate. Original files, compiler results, and rejection record were retained.
- `attempt_003` used the corrected meaningful-indicator sanity reference. Its training/evaluation data, cases, scripts, complete 4,092-entry candidate rejection ledger, compiler results, all 77,280 consumed-input similarity pairs, token audit, and rejection reason are retained in `attempt_003/`. The active `data/phase3c_conf1/` and `benchmark/phase3c_conf1/` paths were moved into that rejected-attempt record; there is **no frozen active candidate**.

## Completed non-model checks on attempt 003

| Check | Evidence |
|---|---|
| Counts | 60 examples per condition, 30 per subskill; 32 Novel Composition, 16 Primitive Sanity, 16 Structural Transfer tasks; five cases each (600 training and 320 evaluation cases). |
| Abstract graphs | Four canonical contribution signatures distinct under all 24 predicate renamings; numeric/array are two domain realizations of four graphs, not eight algebraic graphs. |
| Domain witnesses | Numeric 120/120 and array 120/120 slot pairs, each with a retained whole-input witness and contribution difference. |
| Selected five-case discrimination | Numeric 120/120 and array 120/120 primary slot pairs distinguishable by their actual five selected cases; per-task zero/positive, boundary and realizable multiplicity checks passed in the preliminary case matrix. |
| Training source scaffold | 60/60 paired sources exactly match after replacing only `total+=(hitP+hitQ).` versus `total+=(hitP*hitQ).`; each uses one evaluation of each predicate, two meaningful IFs, one loop and one display. No uncontrolled source difference was found. |
| Primitive exposure | Eight primitives occur in exactly 15 examples per condition; pair/role schedule matches; 180 exposures and 24 planned optimizer steps per cell. These are design counts, not executed steps. |
| Full graph and local motifs | 32/32 primary full graph signatures absent from both pair-only training conditions in the preliminary signature audit; 32/32 primary references use a local pair multiplication motif. This supports a bounded local-motif transfer interpretation, not representation-independent reasoning. |
| Compiler/reference | Pinned compiler SHA-256 `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`; 60/60 ISOLATED, 60/60 COMPOSITION, 64/64 evaluation references and 920/920 cases passed. |
| Tokens | Pinned tokenizer only, no model load: ISOLATED 15,346 full/7,531 supervised tokens, max sequence 295; COMPOSITION 15,466 full/7,531 supervised, max 297. Full difference 0.78196%, supervised 0%, within the proposed 5%/2% limits and 320-token maximum. |
| Consumed-suite exact/template overlap | Across 77,280 input/reference comparisons with DEV1/DEV2/DEV2R, zero exact prompts, sources or normalized full-template matches. Maximum normalized-code similarity 0.9796437659. All pairs and nearest neighbors retained. No historical model outcome or sealed holdout was read. |

**Blocking finding:** the approved coarse AST proxy reports **174 exact equalities**, all on Primitive Sanity: 64 against DEV2 evaluation, 60 against DEV1 dense training, and 50 against DEV1 diverse training. A meaningful indicator assignment in the new reference is absent from the old count template, and the approved normalized-code comparison has zero exact matches. Nevertheless the reviewed proposal requires an overcoarse-proxy false-positive adjudication rule frozen **before data review**. No such rule was frozen. We cannot create one after seeing these flags to waive them. The consumed-suite similarity gate therefore remains unresolved and the candidate cannot be frozen.

The per-task task-essential matrix in `attempt_003/data_audit.json` is also **preliminary**: it lists primitives and APIs but does not independently establish every literal/output-value/control-flow capability in both conditions. Its `coverage_valid: 64` field must **not** be treated as a complete fairness gate. The full runner, acquisition gate, analyzer, task-local RNG, boolean authorization, persistence and fault-injection implementations/tests were not completed after this STOP. No candidate config, paired schedule, or frozen manifest was created. In particular, there is no CONF1 `model_execution_authorized` field to change; CONF1 model execution remains unauthorized.

## Preservation and next boundary

`stop_evidence_inventory.json` contains byte-exact SHA-256 and size for the design, ledger, graph audit, compiler/tokenizer inputs, scripts, all three retained attempts, and their audits. Key attempt-003 hashes: tasks `080747ac6df58cb9758605771e6224b26a983f2c11891519fa6e1879561f4d23`; references `0a45cd89cd2f1fcd03582dfc2f38da6e3b86d44517bda9ff1e7bd7831a12f0c8`; hidden cases `c78f4bc17357642834026d9d2dd6f2a025b8f5eca2834716019b0ce1e3e41d7c`; ISOLATED examples `04c814f7c84e019c8ff0eff1a109d29c7a0349058bd4169389e53a4e5363cb97`; COMPOSITION examples `6e1cf8ea3fda8c445bf123d35e7d96429e42749de48fa5d483eacb0dfd57a91e`.

No model use or candidate freeze may follow from this report. Independent review is needed to decide whether and how the missing proxy-adjudication rule and incomplete task-essential audit can be addressed prospectively. No scientific CONF1 effect is reported.
