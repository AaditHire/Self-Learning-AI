# Phase 3C-CONF1: proposed prospective composition-transfer confirmation

**Status: DESIGN PROPOSAL FOR INDEPENDENT REVIEW.** No dataset, implementation, manifest, or execution is frozen by this document. `model_execution_authorized` is not set here. No model use, gradients, training, or sealed final-paper holdout access is authorized. The completed DEV2R v2 suite is development-consumed. Approval of this design alone would not authorize execution; a later reviewed freeze must contain actual data, tests, code, hashes, and an explicit authorization decision.

## 1. Plain-English question and boundary

Train two fresh adapters from the same immutable base on the same eight semantic predicates. Give one condition independent predicate-count practice (`ISOLATED`) and the other pairwise joint-predicate practice (`COMPOSITION`). Match the inventory, exposures, implementation affordances, training budget, and evaluation procedure. Test both on a **new** set of tasks combining the known predicates in structures present in neither training condition. The outcome is the difference in all-cases-passing program generation, paired by seed and task. This asks about this particular practice manipulation and this particular GOCO domain; it does not test retention or continual learning.

The designers have seen the DEV2R v2 aggregate report: Novel Composition was 10/48 paired seed-task successes for ISOLATED and 38/48 for COMPOSITION (a +58.33 percentage-point development difference), with all three seed differences positive; Structural Transfer was 0/16 for every condition and seed; the versioned Primitive Sanity results varied by seed. The designers have seen the DEV2R protocol and amendment, including its union-of-two-intersections primary topology, first/last-anchor secondary topology, and sanity replacement. No individual DEV2R generation, per-task pass/fail transition, or task-level failure analysis is used to choose this design. The aggregate effect motivates a fresh test, **not** the minimum effect below. DEV2, DEV1, and DEV2R suites are permanently unavailable for model selection or tuning. Similarity checks may inspect their inputs and references through a mechanical audit but may not condition construction on their model outcomes. The sealed final-paper holdout is excluded even from the overlap audit.

`docs/PROJECT_STATE.md` was last updated before DEV2R completion. At design time, Git HEAD was `6c225547a396bc43fd7e8c1bd1b469c38d554ce0` with a clean worktree. The DEV2R v2 completion report and its frozen inputs, rather than that stale state file, establish the immediate research boundary.

## 2. Estimand and hypotheses

The primary estimand is the unweighted mean, over five predetermined paired training seeds, of the paired task-level COMPOSITION minus ISOLATED pass@1 rate on the **32** fixed Novel Composition tasks. Each program gets one greedy generation and passes only if it compiles, executes, and matches all five frozen semantic cases. The same task IDs and cases are used for both conditions. Task variants and repeated seed evaluations are correlated; neither 160 seed-task observations nor individual cases are treated as independent replicates.

- **Scientific hypothesis H1:** under the frozen matched-budget CONF1 design, COMPOSITION has higher Novel Composition pass@1 than ISOLATED; the estimand is positive. The scientific null is a nonpositive estimand. This hypothesis is distinct from the decision checklist below.
- **Confirmatory decision:** a separately preregistered rule determines whether the completed experiment receives the label `CONFIRMATORY_SUPPORT_UNDER_CONF1` or `NOT_CONFIRMED_UNDER_CONF1`. The latter does not prove a zero composition effect.
- Secondary question: does COMPOSITION suffer a severe loss on fresh single-primitive tasks? Structural Transfer is exploratory and cannot rescue or veto the primary contrast.

## 3. Conditions and fixed design

Use the eight original *semantic* primitive definitions only as an inventory: four numeric-iteration predicates (odd index, residue two modulo three, divisor of input, first-half index) and four array-reduction predicates (negative value, even value, squared magnitude above four, value above its index). These are domain definitions, not a license to copy DEV2/DEV2R examples, wording, targets, input cases, or reference templates. Each training condition has **60 newly authored examples**, 30 per subskill. In each subskill, every unordered pair of the four predicates occupies five examples; predicate role/orientation is counterbalanced so each predicate is task-essential in exactly 15 examples per condition, with equal first/second-role counts to the extent the 30-example pairing permits. All example IDs, input instances, task wording, reference programs, and target strings are new. The paired condition examples have matched input schema, predicate pair, constant/value range, prompt wrapper, and schedule slot. The semantic difference is the requested independent use versus joint use of the pair.

Use the new indicator-and-accumulator scaffold specified in section 6 and audited in section 12, not DEV2's redundant nested-`P` guard program or the DEV2R union template. Before data freeze, publish its compiled GOCO instantiation and a source/AST overlap report against DEV2/DEV2R training and evaluation. A template is unacceptable if it is a literal or alpha-renamed clone of a consumed template. Both conditions must have an identical scaffold after replacing the requested predicate relation with `<TREATMENT_EXPRESSION>`. No semantically dead guard, repeated predicate check, no-op arithmetic, unreachable branch, or padding is permitted. If the proposed scaffold fails GOCO validation, overlap, coverage, or the token audit, STOP and redesign both conditions **before** the suite is frozen; do not waive a difference after seeing results. Prompt semantics and target loss geometry still differ because they encode the treatment; report that residual limitation.

Use the pinned Qwen2.5-Coder-3B-Instruct revision `488639f1ff808d1d3d0ba301aef8c11461451ec5` and immutable base weight hashes from the DEV2 contract, with fresh rank-16 NF4 QLoRA adapters (alpha 32, dropout 0.05, the same seven target modules), PagedAdamW8bit, learning rate 0.0002, no weight decay, betas 0.9/0.999, epsilon 1e-8, max grad norm 1.0, linear schedule, five warmup steps, gradient checkpointing, max sequence length 320, microbatch 1, accumulation 8, three epochs, 180 exposure slots and **24 optimizer steps per cell**. Select the final epoch in advance. Use the same pinned tokenizer, system/user templates, first-fence extraction, deterministic GOCO compiler/scorer, 3-second case timeout, one greedy generation (`do_sample=false`, `num_beams=1`, 512 new-token cap), and no repair/retry. Freeze exact versions and hashes later. No DEV2 adapter is reused.

Paired seed schedule: `20280117`, `20280223`, `20280329`, `20280411`, `20280507`. A repository text search at proposal time found none of these seed integers in `research`, `data`, `benchmark`, `scripts`, or `docs`; the prefreeze audit must repeat this against all relevant seed records. Five pairs increase robustness over the three DEV2R pairs and permit reporting seed heterogeneity, but are not a formal power calculation. Every seed is primary; no winner selection, substitution, or seed-based stopping. For a pair, initialize each condition from the identical immutable base with fresh adapters and the same seed policy. Freeze every epoch's matched example order before training. Record all RNG seeds and determinism settings, package versions, and hardware; train cells in frozen seed order, ISOLATED then COMPOSITION. CUDA nondeterminism remains a limitation and is not corrected by choosing a favorable rerun.

## 4. Endpoints and exact interpretation rules

**Primary:** the 32-task Novel Composition suite has four predeclared structural slots per subskill and four semantically distinct tasks per slot (eight blocks of four). The blocks, not individual constant rewrites, are the structural units. Each task has five hidden cases. Report seed-by-condition counts `/32`, each seed difference, the unweighted mean difference in percentage points, both subskill differences, each block's raw count, and paired discordance (both, neither, COMPOSITION-only, ISOLATED-only).

The core primary label `CONFIRMATORY_SUPPORT_UNDER_CONF1` requires complete valid outcomes for all ten cells, a point estimate of the mean paired difference **at least +20 percentage points**, and a two-sided 95% percentile interval with lower bound **strictly above zero** under the frozen resampling procedure below. If either numerical criterion fails, report `NOT_CONFIRMED_UNDER_CONF1` and all raw results. This means **evidence of a positive effect whose observed magnitude meets the prospectively chosen +20 pp target**. It does not establish that the underlying effect is at least +20 pp. A 20-point target corresponds to about six or seven additional successes per 32-task seed on average, large enough to matter on this fixed program-generation workload while smaller gains remain scientifically reportable. This domain-based target is proposed for independent review; it is not derived by scaling the DEV2R estimate. No second primary suite, changed threshold, or result-dependent analysis is allowed. The interval is a design-sensitive uncertainty summary, not a population-generalization guarantee.

Seed, subskill, and block consistency are **predeclared robustness/heterogeneity qualifications**, not parts of the scientific hypothesis and not vetoes on the core label. Report whether every seed difference is nonnegative, at least four of five are positive, both subskill mean differences are positive, and at least six of eight block mean differences are positive. Report each raw difference even if these checks fail. If core support holds but a qualification fails, the exact interpretation is `CONFIRMATORY_SUPPORT_UNDER_CONF1_WITH_HETEROGENEITY`; identify the failing dimensions and restrict any broad or uniformity claim. This separation avoids converting one noisy seed or block into a hidden second primary endpoint, while leaving possible concentration visible and prospectively classified. If the acquisition gate prevents evaluation, use its separate indeterminate label rather than either primary label.

For the interval, use exactly 10,000 bootstrap replicates with RNG seed `20290119`. In each replicate, resample the five **paired seed IDs** with replacement; independently resample four whole **structural blocks** with replacement within numeric and four within array; retain all four tasks in each sampled block and both conditions for every selected seed; compute the equally weighted paired mean. Use the 2.5th and 97.5th empirical percentiles, with a fixed, documented quantile interpolation rule in the frozen analyzer. No task-level or case-level independent resampling and no changed clustering after results.

**Primitive Sanity secondary:** 16 fresh single-primitive count tasks, two per predicate, with new wording and cases. All required output values, literals, language constructs, and APIs must be present in both training conditions. Report each seed's paired rate and the mean difference. Prospectively label a **noncatastrophic sanity result** only if the mean COMPOSITION minus ISOLATED difference is at least −10 percentage points and no seed difference is below −25 points. This is a separate qualification on the interpretation of primary support, not an exclusion gate, significance test, or way to relabel an unconfirmed primary. If it fails, state that the primary effect, even if it meets its rule, coexists with a serious simpler-task regression. Report absolute sanity rates to expose a common floor.

**Structural Transfer secondary/exploratory:** 16 fresh tasks, balanced across subskills and at least four prespecified structure blocks, exercising covered primitives in a different data-flow arrangement. Their design must be specified before model use without reference to which old tasks failed. Report rates, paired differences, block and subskill results, and failure stages. The DEV2R 0/16 floor makes this an exploratory boundary, with no success threshold and no role in the primary claim. Do not tune these tasks to produce a positive result.

**Own-training diagnostics:** each adapter is evaluated once on its own 60 fresh training prompts before any confirmatory task generation. Report semantic all-five-case pass `/60` and exact normalized target-string reproduction `/60` separately, by seed, condition, subskill, and training archetype. Exact reproduction is descriptive and never substituted for semantic correctness. **Acquisition gate:** test all ten cells before deciding; each must have at least 54/60 semantic passes (90%). If any misses, stop before confirmatory evaluation, retain every diagnostic record, and report `INDETERMINATE_INSUFFICIENT_ACQUISITION`; do not exclude an individual seed, change a checkpoint, add steps, or rerun. Ninety percent allows up to six training-task misses per cell while rejecting a clearly unacquired training treatment; it is a proposed feasibility cutoff for independent review, not tuned to CONF1 outcomes. Exact-target rate does not gate. The primary estimand is the **end-to-end effect of training presentation under equal budgets**, not an effect conditioned on identical in-sample scores. Report the raw paired own-training semantic and exact-target differences alongside any CONF1 result so unequal training fit remains visible. This all-cell feasibility gate can still make results indeterminate and is a design limitation.

## 5. Prospective dataset construction and audit

Before building any examples, freeze a semantic design ledger listing the eight predicates, both training-condition relational definitions, the eight primary block signatures, sixteen sanity slots, and sixteen structural-transfer slots. The original candidate graphs failed an array-domain feasibility audit (section 10), so the **revised proposed graphs** are: (G1) count `(P∧Q)∨(P∧R)` once per item; (G2) add counts of `P∧Q`, `Q∧R`, and `R∧S`; (G3) add counts of `P∧Q`, `P∧R`, and `P∧S`; (G4) add count of `(P∨Q)∧R` and count of `Q∧S`. Count terms are separate: an item can contribute more than once. Within each subskill, map `P,Q,R,S` to the four predicates in the fixed order listed in section 3, then rotate the order left by 0, 1, 2, or 3 positions. This defines eight subskill blocks and 32 candidate tasks. Sections 10–11 document the non-model Boolean and domain checks: all four revised graphs are nonisomorphic by contribution function, all 16 slots per subskill are behaviorally pairwise distinguishable by feasible inputs, and rotations change named predicate assignment while remaining the **same** abstract graph under renaming. Numeric and array versions are distinct domain blocks, not eight distinct algebras. The DEV2R disjoint-pair union, DEV2 disjoint-pair sum, and first/last-anchor counting remain prohibited as primary blocks. All graphs remain subject to later exact task-essential coverage, novelty, compiler, and hidden-case audits; no final prompts, references, or cases exist yet. If any graph collapses to a consumed template or lacks both-condition coverage, STOP for independent redesign before training rather than substitute a favorable task after model use.

Generate candidate programs and cases deterministically from a new builder and a frozen construction seed, with a separate construction attempt ledger that records every rejected candidate and reason. No DEV2R outcome file or adapter output is a builder input. A human reviewer checks each task specification for the **task-essential** primitives, language/API constructs, literal and output capabilities; incidental syntax in one reference is reported separately. A distinct reference implementation where useful may demonstrate nonessentiality but is never training data, a canonical target, or a changed test. For each task, construct five cases from new input instances, including positive, zero/empty, overlap, and boundary behavior where applicable. A case matrix must show that each task-essential branch and capability is actually exercised; otherwise STOP or redesign before freeze. Evaluate every canonical training target and evaluation reference on all frozen cases with the pinned compiler **before any model use**. Reference validation is instrument checking, not model inference.

The pre-model audit must show, for each condition separately: every primary and secondary task-essential primitive represented; every task-essential GOCO construct/API represented; every required literal and output-value capability represented; no construct or capability available in only one condition; every primary full composition signature absent from both training sets. Compute exact prompt, target/reference, and normalized-source matches; the already used AST-proxy and normalized-code similarity against both fresh training conditions, DEV2/DEV2R training/evaluation, and other consumed A suites; retain *all pairs*, nearest neighbors, and manual disposition of high-similarity and lower-threshold flags. Equality of a coarse AST proxy is a STOP unless independently shown to be an overcoarse false positive under a rule frozen before data review. Any exact prompt/reference/target or full template match with a consumed suite is a STOP. Do not invent a new similarity metric or threshold after observing model results. Similarity proxies cannot prove independence; publish nearest examples and structural rationale without disclosing hidden cases to model-facing prompts. A reviewer who knows aggregate DEV2R results may inspect input-only overlap but may not inspect task-level DEV2R outcomes during construction. The sealed final-paper holdout is never read, hashed, or compared.

Freshness means newly sampled input cases and newly authored prompts and references, not merely different IDs or constants. Keep evaluation cases hidden from prompts and training. Check no exact input-case reuse against new training where it would leak the answer, and preserve a case-generation provenance ledger. Freeze cases and expected outputs with the tasks. Once a suite or any part of it is exposed to a model, it is consumed, including an interrupted attempt.

## 6. Matched-budget audit

### Proposed abstract training scaffold

The input schema is one nonnegative `n` for numeric iteration or four pipe-separated signed numbers for array reduction, parsed into the same four-element array in both conditions. Output is one nonnegative integer followed by a newline. For each matched predicate pair `(P,Q)` and offset `k`, both programs declare `NUMBER total=k`, `NUMBER hitP=0`, and `NUMBER hitQ=0` after the identical input/API scaffold; traverse the same indices with the same frozen forward/reverse loop; reset both indicators to zero on each item; evaluate `P` once in the first `IF` and set `hitP=1` if true; evaluate `Q` once in the second `IF` and set `hitQ=1` if true; add the treatment expression to `total`; and finish with the same `DISPLAYNL(total)`. Abstract GOCO-like form (subject to pinned-compiler validation before freeze):

```text
<IDENTICAL INPUT DECLARATIONS, INPUT AND ARRAY PARSE>
NUMBER total=k. NUMBER hitP=0. NUMBER hitQ=0.
<IDENTICAL INDEX LOOP> {
  hitP=0. hitQ=0.
  IF (<PREDICATE P>) { hitP=1. }
  IF (<PREDICATE Q>) { hitQ=1. }
  total+=<TREATMENT_EXPRESSION>.
}
DISPLAYNL(total).
```

`ISOLATED` uses `<TREATMENT_EXPRESSION> = hitP+hitQ`, independently counting each predicate. `COMPOSITION` uses `<TREATMENT_EXPRESSION> = hitP*hitQ`, counting their conjunction. This indicator scaffold evaluates each predicate once per item in both conditions, with two meaningful branches and no redundant guard. Addition versus multiplication inside the expression is the treatment encoding; outside that expression the abstract syntax must be identical after normalizing IDs, predicate spellings, input values, and `k`. The paired prompts share one wrapper and differ only in a marked `<TREATMENT_DESCRIPTION>` requesting separate counts versus overlap count. This remains a paired-predicate **independent-count** baseline, not single-predicate training; it tests the stipulated presentation contrast. Multiplication and addition already occur in the eight-predicate language inventory, but their counts in this expression differ intentionally. The later audit must confirm each task-essential output range, operator, and GOCO syntax is usable in **both** conditions. An artificial extra expression or code path to equalize raw token counts is forbidden.

The pre-gradient contract is exact equality of 60 examples, 30 per subskill, primitive containing-example counts, task-essential predicate occurrence counts, pair/role schedule, 180 exposure slots, 24 optimizer steps, epochs, batch/accumulation, prompt wrappers, model/tokenizer/adapter/hyperparameters, and audited GOCO construct/API counts except the intended structural relation. A signed table must state both condition totals and each difference. Use the pinned tokenizer on the exact chat serialization: supervised target-token totals must differ by **no more than 2%**, and full-token totals by no more than **5%**, calculated relative to ISOLATED; every sequence must fit 320 tokens without truncation. These stricter prospective limits improve on DEV2's allowed 10%; they are set now, not from confirmatory outcomes. If targets cannot satisfy them without distorting the treatment, STOP before gradients and obtain independent review of a new design. Do not pad with arbitrary target text merely to hit parity. Record actual tokens, steps, optimizer exposures, memory, and wall time afterward; a matched token count cannot guarantee matched optimization difficulty.

## 7. Freeze, execution order, persistence, and STOP

**Design/freeze order:** (1) independent review of this proposal; (2) freeze semantic slot ledger and generation rules; (3) build new training and evaluation artifacts and rejected-candidate ledger without model use; (4) compiler reference/case validation; (5) coverage, signature, overlap, template, seed, schedule, and token audits; (6) implement and test the runner/analyzer using synthetic fixtures only; (7) freeze the complete manifest and source tree in a prospective commit; (8) independent pre-execution review and separate explicit model authorization. No post-freeze task or threshold change is routine maintenance; any change requires a versioned pre-inference amendment, fresh audit, and independent approval. After any confirmatory model attempt, no replacement suite is used to repair the same result.

**If separately authorized later:** verify all hashes and the actual JSON boolean authorization before heavy model import. Train ten cells in listed seed order, ISOLATED then COMPOSITION, to the frozen final checkpoint. Run all ten own-training diagnostics in that same order and apply the 90% acquisition gate. Only if it passes, run the confirmatory suite in the same cell order; within each cell use a frozen task order that interleaves the three groups in a predeclared schedule, then analyze once. For each task, derive a task-specific deterministic generation RNG seed from a cryptographic hash of `(global evaluation seed, paired training seed, task ID)` and use the **same** seed for both conditions. Reset Python, NumPy, CPU Torch, and CUDA RNG immediately before every task; freeze deterministic settings and greedy decoding. A shuffled-order synthetic invariance test must show identical generation input/RNG state per task. If task-local RNG isolation cannot be verified on the pinned stack, freeze one exact task order, state that order can affect outputs, and require renewed review **before** inference. Do not change order after results. No task is retried or regenerated.

For each prospective model task, atomically write and fsync a raw generation checkpoint before scoring; then atomically write and fsync a primary semantic-score checkpoint (including all five case outcomes and own-training exact-target boolean where applicable) before optional classification or aggregation. Existing task checkpoints block another model call. A crash or scoring fault leaves available evidence, creates an incident, and stops the entire experiment pending independent review; no silent resume or duplicate call. Verify output cardinality and hashes before analysis.

**STOP before model use** on a missing/changed hash, nonboolean authorization, seed reuse, reference/case failure, incomplete capability exercise, unmatched primitive/construct/API/literal/output coverage, signature leak, exact/template reuse, unaudited high similarity, token or schedule mismatch, missing test, or any sealed-holdout access. **STOP during execution** on OOM, nonfinite gradients/loss, incorrect exposure/step count, model/evaluator/compiler failure, attempted retry, missing checkpoint, or unexpected RNG/order behavior; preserve the failure record. An ordinary generated GOCO program that fails to compile or hidden cases is a scored failure, not an infrastructure STOP. No B training, replay, retention study, or paper-level claim is part of CONF1.

## 8. Planned artifacts, paths, manifest, and tests

All paths below are **proposed and currently uncreated**, except this document. Do not edit `data/phase3c_dev2/`, `benchmark/phase3c_dev2r*/`, their protocols, manifests, results, or adapters.

| Purpose | Proposed repository path |
|---|---|
| Semantic slot ledger and construction rules | `research/protocols/phase3c_conf1_slots.json` |
| Frozen protocol/config/schedule/manifest | `research/protocols/phase3c_conf1_protocol.md`, `phase3c_conf1_config.json`, `phase3c_conf1_schedule.json`, `phase3c_conf1_manifest.json` |
| Fresh training examples/references/cases | `data/phase3c_conf1/{isolated,composition}_{examples,references,cases}.json` |
| Fresh evaluation tasks/references/hidden cases | `benchmark/phase3c_conf1/{tasks,references,hidden_cases}.json` |
| New builder, audit, runner, analyzer, tests | `scripts/{build,audit,train,evaluate,analyze}_phase3c_conf1.py`, `tests/test_phase3c_conf1_*.py` |
| Prefreeze audit/rejections and later report | `research/results/PHASE_3C_CONF1_PREFREEZE/`, `research/results/PHASE_3C_CONF1/` |
| Mutable execution records, ignored from source tree | `.runtime/phase3c_conf1/` |

The later manifest must include a schema version and status, `model_execution_authorized: false` at freeze, parent design/freeze commit IDs, explicit hash policy (byte-exact for binaries/adapters; LF-normalized only for declared text files), SHA-256 and size for every protocol, slot ledger, builder, data/reference/case file, schedule, prompt, tokenizer, model shard, compiler binary, runner, evaluator, analyzer, and tests, plus package/Java/hardware identities. It must record task/case counts, eight block IDs/signatures, five paired seeds, total exposures/steps/tokens per condition, audit output hashes, expected result IDs, generation config, checkpoint paths, and the exact analysis thresholds/resampling seed. The freeze report must include a no-inference/no-gradient prefreeze audit. After execution, a separate immutable output inventory hashes each adapter, raw generation, primary score, diagnostic, aggregate, and incident artifact; it must not rewrite the frozen input manifest.

Proposed **synthetic/non-model** tests: builder determinism and freshness; reference/case semantic validation; all condition coverage and essentiality matrices; absent signatures; prompt/reference/normalized-code/AST-proxy/template overlap; token/step/schedule parity; seed uniqueness; authorization type checks (`true` only); one-pass/no-retry and duplicate-call guard; fault injection after generation and before primary score; atomic persistence/resume refusal; task-order RNG invariance; own-training gate ordering and failure STOP; exact-target versus semantic-score separation; analyzer known-answer paired differences, clustered resampling, quantile rule, incomplete-cell refusal, and all conjunctive interpretation branches. Tests use fakes and fixtures, no model load or generation.

## 9. Risks and independent self-review

| Risk checked | Proposed control and remaining limitation |
|---|---|
| Development leakage / template reuse | Outcome-blind construction, input-only mechanical comparison, explicit exclusion of DEV2R union and consumed templates, no sealed holdout access. Shared primitive vocabulary and GOCO scaffolding remain unavoidable. |
| Condition asymmetry / weak baseline | Exact predicate, role, construct, schedule, example, token, and training-budget audits; review of full target scaffolds. Independent versus joint semantics necessarily changes targets and can change optimization difficulty; an artificial isolated template would invalidate the intended contrast and must be rejected before freeze. |
| Missing task-essential capabilities | Per-task requirements checked against **both** training sets and exercised cases; incidental reference constructs distinguished. A frozen five-case test still samples only limited behavior. |
| Post-hoc freedom | Fixed 32 primary slots, five seeds, thresholds, clustered interval, gate, STOP logic, and no substitutions after model use. Concrete operator graphs and tasks do not yet exist, so independent review of the later freeze is indispensable. |
| Seed dependence / correlation | Five paired fresh seeds, all displayed, two-way seed/block resampling, and prospectively labeled seed/subskill/block heterogeneity. Five seeds/eight blocks remain a small convenience sample; interval precision and generality are limited. |
| Structural-transfer floor | Fresh secondary tasks defined prospectively, no rescue of old failures, no structural-transfer claim from the primary result. |
| Confirmation versus development | DEV2R used only as aggregate motivation; a wholly fresh training/evaluation run and new scaffolds are required. The designers' knowledge of the aggregate effect and task family remains a source of human design bias, even without individual outcomes. |

## 10. Non-model semantic audit of the original candidate graphs

The original proposal's graphs were O1=`P∧Q∧R`, O2=`P∧(Q∨R)`, O3=`(P∧Q)+(Q∧R)+(R∧P)`, and O4=`(P∧Q∧R)+(P∧Q∧S)`, where `+` adds per-item contributions and Boolean terms yield 0 or 1. The exhaustive Boolean truth/contribution table is:

| PQRS | O1 | O2 | O3 | O4 |
|---|---:|---:|---:|---:|
| 0000 | 0 | 0 | 0 | 0 |
| 0001 | 0 | 0 | 0 | 0 |
| 0010 | 0 | 0 | 0 | 0 |
| 0011 | 0 | 0 | 0 | 0 |
| 0100 | 0 | 0 | 0 | 0 |
| 0101 | 0 | 0 | 0 | 0 |
| 0110 | 0 | 0 | 1 | 0 |
| 0111 | 0 | 0 | 1 | 0 |
| 1000 | 0 | 0 | 0 | 0 |
| 1001 | 0 | 0 | 0 | 0 |
| 1010 | 0 | 1 | 1 | 0 |
| 1011 | 0 | 1 | 1 | 0 |
| 1100 | 0 | 1 | 1 | 0 |
| 1101 | 0 | 1 | 1 | 1 |
| 1110 | 1 | 1 | 3 | 1 |
| 1111 | 1 | 1 | 3 | 2 |

These four functions are pairwise distinct even after any of the 24 predicate permutations: their multisets of 16 contribution values differ. AND and OR commutativity is included in that permutation check. O1/O2/O3 omit S; O4 depends on all four variables. O3's contribution of three and O4's contribution of two at `1111` are not collapsed to a Boolean pass. Rotations of a given graph are **isomorphic under predicate renaming**, so they are role assignments, not four new algebras.

The abstract result does **not** carry into all actual array tasks. Array predicates in order are A=`x<0`, B=`x` even, C=`x²>4`, D=`x>i` with `i∈{0,1,2,3}`. A and D cannot coexist. Enumeration of `i=0..3` and `x=-30..30` yields the complete eleven attainable truth patterns `0000,0001,0010,0011,0100,0101,0111,1000,1010,1100,1110`; values outside that interval repeat one of these patterns because only sign, parity, magnitude threshold, and `x>i` matter. The original 16 array slots have six exact functional collisions on this complete pattern set: `O1R0=O4R0`, `O1R1=O4R2`, `O1R2=O1R3=O4R3`, and `O2R2=O3R2`. For example, two triple conjunction rotations require both A and D and are identically zero. These equalities hold for every four-element input array, not merely the enumerated witnesses. Numeric predicates realize all 16 Boolean patterns by `n≤11`, and an enumeration through `n=2000` found a whole-input count witness for every pair of its 16 old slots. **Disposition:** the old candidate set is infeasible as a 32-task primary suite; it is replaced at design stage, before any dataset or model use, by the revised graphs in section 5.

## 11. Revised graph and domain-realizability feasibility

The revised graphs' per-item contributions for `PQRS=0000..1111` are shown below. Their contribution-value multisets remain different under all 24 predicate permutations, including AND/OR commutativity; G2/G3 count multiplicity, while G1 is Boolean and G4 can count twice. G1 uses P,Q,R and omits S; G2/G3/G4 use all four. Rotations remain algebraically isomorphic within a graph but assign different **named** primitives.

| PQRS | G1 | G2 | G3 | G4 |
|---|---:|---:|---:|---:|
| 0000 | 0 | 0 | 0 | 0 |
| 0001 | 0 | 0 | 0 | 0 |
| 0010 | 0 | 0 | 0 | 0 |
| 0011 | 0 | 1 | 0 | 0 |
| 0100 | 0 | 0 | 0 | 0 |
| 0101 | 0 | 0 | 0 | 1 |
| 0110 | 0 | 1 | 0 | 1 |
| 0111 | 0 | 2 | 0 | 2 |
| 1000 | 0 | 0 | 0 | 0 |
| 1001 | 0 | 0 | 1 | 0 |
| 1010 | 1 | 0 | 1 | 1 |
| 1011 | 1 | 1 | 2 | 1 |
| 1100 | 1 | 1 | 1 | 0 |
| 1101 | 1 | 1 | 2 | 1 |
| 1110 | 1 | 2 | 2 | 1 |
| 1111 | 1 | 3 | 3 | 2 |

The following table supplies a **feasibility witness, not a final hidden case**, for every proposed slot against its next rotation (`R3` against `R0`). A numeric witness is a whole input `n`; `i` gives one item at which the per-item contributions differ and `pattern` is that item's original-order truth vector. An array witness sets only index `i` to `x` and the other three entries to zero; its pattern is for that index. The two counts before/after the slash are the whole-input outputs of the two slots, before any shared offset. A future hidden-case matrix must include a fresh input with the same discriminating **property** for each adjacent rotation, plus cases separating every other pair and exercising all task-essential branches; these witness inputs are not copied into the final suite.

| Slot vs next | Numeric witness `n,i,pattern` | Numeric counts | Array witness `i,x,pattern` | Array counts |
|---|---|---:|---|---:|
| G1R0/R1 | 1,1,1010 | 1/0 | 0,-15,1010 | 1/0 |
| G1R1/R2 | 1,1,1010 | 0/1 | 0,-15,1010 | 0/1 |
| G1R2/R3 | 1,1,1010 | 1/0 | 0,-15,1010 | 1/0 |
| G1R3/R0 | 1,1,1010 | 0/1 | 0,-15,1010 | 0/1 |
| G2R0/R1 | 2,1,1011 | 2/3 | 0,-14,1110 | 2/1 |
| G2R1/R2 | 2,2,0110 | 3/2 | 0,-2,1100 | 0/1 |
| G2R2/R3 | 3,1,1011 | 2/1 | 0,-14,1110 | 1/2 |
| G2R3/R0 | 4,2,0111 | 2/3 | 0,3,0011 | 0/1 |
| G3R0/R1 | 1,1,1010 | 1/0 | 0,-15,1010 | 1/0 |
| G3R1/R2 | 1,1,1010 | 0/1 | 0,-15,1010 | 0/1 |
| G3R2/R3 | 1,1,1010 | 1/0 | 0,-15,1010 | 1/0 |
| G3R3/R0 | 1,1,1010 | 0/1 | 0,-15,1010 | 0/1 |
| G4R0/R1 | 3,1,1011 | 2/3 | 0,3,0011 | 0/1 |
| G4R1/R2 | 2,1,1011 | 2/1 | 0,3,0011 | 1/0 |
| G4R2/R3 | 5,5,1110 | 3/4 | 0,-14,1110 | 1/2 |
| G4R3/R0 | 2,2,0110 | 1/2 | 0,-14,1110 | 2/1 |

The deterministic non-model enumeration compared **all 120 unordered pairs** of the 16 revised slots separately within each domain. Numeric inputs `n=0..100` distinguish 120/120 pairs by total output; array inputs with one varied entry `i=0..3`, `x=-15..15`, and other entries zero distinguish 120/120. This is an existence check with explicit witnesses, not a final-case validation or a proof of equal task difficulty. The numeric and array copies of each graph share one abstract topology, so the design has **four** algebraic graph families across **eight** domain/subskill blocks. The later audit must verify that the actual hidden cases exercise these distinctions and that every required primitive/output capability is present in both training conditions.

## 12. Allowed-difference audit for the proposed training scaffold

After abstracting the intended expression to `<TREATMENT_EXPRESSION>` and the prompt clause to `<TREATMENT_DESCRIPTION>`, the two condition scaffolds must compare as follows. `MATCHED` is a zero-difference requirement; the other two allowed labels must be confined to the marked treatment slot or its unavoidable outputs. Any additional difference is `INVALID_UNCONTROLLED_DIFFERENCE` and stops the freeze.

| Feature | ISOLATED / COMPOSITION contract | Classification |
|---|---|---|
| Input/API and domain | Same `INPUT`, same nonnegative numeric or four signed pipe-separated array schema, `strings.SPLIT`/`strings.TO_NUMBER`/indexing in array, same case-input pairing | MATCHED |
| Output schema | One `DISPLAYNL` integer and newline from `total`; expected values may differ because semantics differ | MATCHED structure; UNAVOIDABLE_SEMANTIC_CONSEQUENCE values |
| Declarations and literals | Same input declarations, `total`, `hitP`, `hitQ`, same `k`, zero resets and one assignments | MATCHED |
| Loop | Same single traversal, bounds, direction, index and increment for a paired slot | MATCHED |
| Predicate evaluations | Exactly one `P` in first indicator `IF`, one `Q` in second; same spellings, order and locations | MATCHED |
| Branch/control flow | Exactly two independent meaningful `IF` statements; no nested or redundant guards | MATCHED |
| Accumulators/display | One `total`, two resettable indicators, one `total+=...`, one final display | MATCHED |
| Arithmetic outside treatment | Same parsing/index math, initial offset, assignments, increment and predicate-internal operators | MATCHED |
| Treatment expression | `hitP+hitQ` versus `hitP*hitQ` | INTENDED_TREATMENT_DIFFERENCE |
| Prompt treatment clause | Separately count two predicates versus count their overlap; same wrapper and pair roles | INTENDED_TREATMENT_DIFFERENCE |
| Result and target tokens | Different contribution values and exact target tokens follow from the treatment; still subject to the 2%/5% budget audit | UNAVOIDABLE_SEMANTIC_CONSEQUENCE |
| Any dead guard, duplicate check, extra loop, no-op, unreachable code, filler tokens, API change, or unmatched branch | Forbidden | INVALID_UNCONTROLLED_DIFFERENCE |

This is an abstract contract, **not** a claim that the GOCO source has already been compiled or that token/construct parity has passed. The later machine audit must parse both generated targets, replace only the marked treatment subtree, normalize identifiers and literals according to a frozen rule, and require the remaining ASTs and audited feature counts to match exactly. It must verify that the two arithmetic operators and all output capabilities are covered by both full training sets, without treating incidental spelling in one reference as task-essential.

**Revised self-review disposition:** no new model outcome was inspected or generated. The old graphs failed the array-domain check, and the revised four graphs have explicit Boolean and input-domain witnesses. The indicator scaffold gives a nonartificial matched abstract design, but GOCO compilation, exact training/evaluation data, coverage, token parity, consumed-template overlap, and five-case matrices remain unverified. These are prefreeze STOP conditions. Independent reviewers should still challenge the proposed +20-point target, the 90% acquisition feasibility gate, the novel-topology claim, and any residual prompt/optimization difference before a separate freeze or execution decision.
