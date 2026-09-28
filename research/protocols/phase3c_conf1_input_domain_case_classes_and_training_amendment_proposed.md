# Proposed CONF1 INPUT_DOMAIN case classes and numeric training-case amendment

**Status: PROSPECTIVE METHODOLOGY AMENDMENT PROPOSAL ONLY; NOT APPROVED, NOT FROZEN, NOT IMPLEMENTED; MODEL EXECUTION UNAUTHORIZED.** Independent review is required before this proposal can govern construction of Attempt 004 or a successor. It creates no candidate acceptance, fixture, or model authorization.

The missing `INPUT_DOMAIN` case-class definitions and the numeric training sampler's exclusion of `n=0` were identified during pre-candidate Coverage-v3 implementation review. Attempt 004 did not exist; no CONF1 model training, inference, or outcome informed this proposal. Attempts 001–003 and their data, audits, rejection records, and interpretations remain historical. Frozen Coverage v3, the slot ledger, the historical protocol, and the paired-scaffold methodology remain unchanged. This proposal would become an additional prospective authority only after separate approval and freeze, before candidate construction.

## Authority and scope

The frozen [Coverage v3](phase3c_conf1_coverage_v3_proposed.md) V3.4 requires active same-domain `INPUT_DOMAIN` coverage in both training conditions **and** the declared sign/empty/boundary case classes. V3.5 separately defines behavioral activity. The [slot ledger](phase3c_conf1_slots.json) fixes 60 paired training slots, their IDs, construction seed `20290123`, existing five-case rules, and the raw `n=0` boundary exception. The [historical protocol](phase3c_conf1_proposed_protocol.md) §§5–7 and 12 fixes the case, fairness, and budget obligations; the [paired-scaffold clarification](phase3c_conf1_paired_scaffold_normalization_proposed.md) requires identical case-input strings within a matched slot. This proposal supplies closed class meanings and one narrow **future override** of the ledger's numeric training-case rule. It does not alter any other V3 key, equivalence, activity intervention, threshold, or task.

Case-class membership is determined from a valid, decoded whole input under the frozen input schema, not from a source literal, expected output, predicate threshold, sampled-pool endpoint, or candidate-observed extremum. The same class definitions, membership tests, and evidence format apply to both conditions and every eligible task. An unknown domain type or an unproved validity/decoder mapping fails closed. `NOT_APPLICABLE` below is a fixed domain-class status, never a candidate-specific waiver. Every `REQUIRED` class needs a frozen case witness in **each** condition, with example ID, case ID, input, decoded value or elements, class label, and source/decoder mapping. One case may witness several classes. A malformed or out-of-domain input supplies no valid-domain evidence. No class, applicability status, or witness-slot rule may change after candidate construction.

## Numeric `INPUT_DOMAIN`: one nonnegative integer `n`

| Class | Membership on valid decoded input | Status and reason |
|---|---|---|
| `SIGN_ZERO` | `n == 0` | `REQUIRED` |
| `SIGN_POSITIVE` | `n > 0` | `REQUIRED` |
| `EMPTY_LOOP` | `n == 0` | `REQUIRED`: frozen numeric traversal covers positions `1..n`, hence zero body iterations |
| `LOWER_DOMAIN_BOUNDARY` | `n == 0` | `REQUIRED`: zero is the lower bound of nonnegative integers |
| Negative-sign class | `n < 0` | `NOT_APPLICABLE`: invalid input |
| Upper-domain boundary | — | `NOT_APPLICABLE`: no finite upper bound is declared for the valid input domain |

One `n=0` case may jointly witness `SIGN_ZERO`, `EMPTY_LOOP`, and `LOWER_DOMAIN_BOUNDARY`; a distinct `n>0` case witnesses `SIGN_POSITIVE`. Training and evaluation construction pools such as `1..60`, `0..60`, or `0..100` are sampling rules, not scientific domain boundaries. Neither `60` nor `100` becomes an upper-boundary witness merely by being a pool endpoint.

### Relation to frozen V3.5 activity

V3.4 asks for at least one source-backed **example** with an active domain key in each condition, then adds class coverage conjunctively. V3.5 defines a behavioral key's path, normal-run event, and changing intervention using at least one of **that example's five cases**; it does not require every class-witness case to produce a nonzero update. Accordingly, class presence and behavioral activity may be proved by different cases **in the same example**, while both obligations must pass. This is the existing example-level quantification, not a relaxation of activity.

For numeric `n=0`, `INPUT(n)` executes and its decoded value controls the loop bound, but the body performs no accumulator update. That case is **not** a V3.5 normal-run output-event witness. The example containing it must also contain a positive case whose connected, source-mapped decoder path reaches the displayed accumulator, has a normal-run nonzero contribution or selected nonzero update, and has a frozen V3.5 `INPUT` counterfactual (`all-zero` first, then `all-one`) that changes its correct final output on such a normal-event case. Both conditions must pass separately. Merely recording `0`, parsing a value, or inserting a disconnected decoder does not cover `INPUT_DOMAIN`. A future auditor must record the class-case IDs and the possibly distinct activity-case ID, normal output, intervention, and counterfactual output; failure of either side is FAIL.

## One-slot prospective numeric construction override

**Current frozen ledger rule:** for *every* numeric training slot, construct `random.Random(SHA256(construction_seed,slot_id,'train-numeric'))`, sample five distinct values from `1..60` excluding `12,13,14`, and sort ascending. The current builder implements this with `rng_for(slot_id, 'train-numeric')` and `r.sample(pool, 5)`.

**Proposed override, only if independently approved and frozen before construction:**

1. Take the frozen `training_paired_slots` records whose `family` is exactly `numeric_iteration`. Require nonempty records and unique `slot_id` values. Sort their exact UTF-8 `slot_id` byte strings in ascending lexicographic order; choose the first as the sole canonical numeric `INPUT_DOMAIN` witness slot. The present frozen ledger has 30 unique numeric IDs; this rule selects `CONF1-TR-NU-01-V0`. It depends only on the frozen ledger, not candidate cases, predicate firings, expected outputs, audit findings, Attempt-003 outcomes, or model outcomes. A missing/duplicate/changed ledger ID fails; do not substitute another slot.
2. For that slot only, construct the **same existing** `random.Random(SHA256(construction_seed,slot_id,'train-numeric'))` stream and eligible positive pool `1..60` excluding `12,13,14`. Call the existing deterministic sampling operation with sample size **four**, `r.sample(pool, 4)`, rather than five. Add the integer `0` once and sort the resulting five integers ascending under the existing convention. The builder's seed derivation is the SHA-256 digest of UTF-8 `f'{construction_seed}|{slot_id}|train-numeric'`, interpreted as a big-endian integer for `random.Random`; the prospective implementation must preserve that already-frozen derivation. This is a defined sample-size change, not a choice of which observed positive case to discard.
3. Both ISOLATED and COMPOSITION records for that matched slot use these identical five ordered input strings and ordered case IDs. Their expected outputs are calculated separately and mechanically from the unchanged respective treatment expressions. For `n=0`, both outputs equal the unchanged initial offset `k`. No sixth case is added.
4. Every other numeric training slot retains the frozen five-positive rule **without change**. Array training selection, all evaluation cases, and all slot definitions retain their existing rules.

There is no predicate-, output-, similarity-, or activity-based choice among the four sampled positives and no post-audit switch of the witness slot. If the resulting five cases fail V3.5 activity, required output categories, compiler/reference agreement, or another gate in either condition, the future candidate fails. Remedy would require a new prospective methodology review before a different candidate, never a silent replacement based on the failed candidate.

## Array `INPUT_DOMAIN`: exactly four signed integer fields

The valid schema is four pipe-separated fields decoded as signed integers, in fixed element order. For each sign witness record case ID, zero-based element index, and decoded integer value; record every class claimed by a case.

| Class | Membership on valid decoded input | Status |
|---|---|---|
| `NEGATIVE_PRESENT` | At least one of four elements `< 0` | `REQUIRED` |
| `ZERO_PRESENT` | At least one of four elements `== 0` | `REQUIRED` |
| `POSITIVE_PRESENT` | At least one of four elements `> 0` | `REQUIRED` |
| `EMPTY` | No valid member | `NOT_APPLICABLE`: every valid input has exactly four numeric fields |
| `BOUNDARY` | No finite numeric input-domain endpoint is declared | `NOT_APPLICABLE` |

One valid four-field case may satisfy several sign classes. Empty string, missing field, empty array, malformed split, and fewer than four fields are **invalid inputs**, not EMPTY witnesses. The `-16..16` construction pool, its endpoints, predicate thresholds, modulo values, and observed candidate extrema are not input-domain boundaries. A future positive/zero/negative sign case still needs connected, active array decoding under unchanged V3.5; case presence alone does not pass. The absence of a declared finite signed-integer bound is a schema fact, not discretion to mark a valid boundary case inapplicable after candidate inspection.

## Scientific effect and prospective evidence

This override changes the five case inputs and derived expected outputs for **one matched numeric training slot**, its case hashes/provenance, and later compiler/reference, coverage, own-training diagnostic, and possibly descriptive output-category evidence. All affected candidate artifacts must be generated and audited under the approved/frozen rule before any model use. The five cases are diagnostic semantic cases; this amendment adds no model-facing example. It does not pre-assert that the future candidate passes any audit.

It preserves 60 training examples per condition, 30 per subskill, five cases per example, 180 planned exposures, 24 planned optimizer steps, the paired predicate/role and prompt schedule, source scaffold and treatment relation (`hitP+hitQ` versus `hitP*hitQ`), primary evaluation inputs and tasks, withheld full higher-order graphs, model/tokenizer/adapter specification, five paired training seeds, task-local evaluation RNG, acquisition and scientific thresholds, and token/parity limits. The model-facing target source and prompt are unchanged by a case-input-only override; any later token or budget claim still needs its normal audit. No candidate, suite, or outcome is accepted by this proposal.

Raw `n=0` can recur in training and evaluation under the ledger's explicit boundary exception, with disclosure. Shared raw input is not automatically a shared task specification, predicate composition, prompt/source, or complete case. Future exact task/case, consumed prompt/source/template, AST-v2 structural, E5 full-signature, and E6 hidden-case discrimination audits remain independent blocking checks. This proposal pre-clears none of them and does not expose hidden evaluation cases to model-facing prompts or targets.

## Compatibility review

| Existing authority | Classification | Reason |
|---|---|---|
| Coverage V3.1 | Compatible | Closed classes are derived from the frozen domain schemas; no task-ID or candidate-content branch creates a capability. The one slot ID controls construction only, not coverage extraction. |
| Coverage V3.4 | Prospectively supplemented | Defines its previously undeclared sign/empty/boundary memberships and obtains a required numeric zero witness in both conditions; no required class is waived. |
| Coverage V3.5 | Compatible | Zero supplies class evidence, not a normal-run event; a positive case in the same example must independently establish active connected decoding and a changing counterfactual. |
| Coverage V3.6 and frozen paired fairness | Compatible | Identical ordered inputs/IDs in the matched pair; only the already marked treatment and mechanically derived outputs may differ. |
| Coverage input-domain and literal/output rules | Prospectively supplemented | Domain classes are decoder/case facts, never inferred from incidental literals or pool endpoints. Output categories remain separately case-witnessed. |
| E1 compiler/reference | Compatible | All revised cases and outputs require fresh pinned-compiler validation; no prior PASS is inherited. |
| E3 scaffold/budget | Compatible | Five-case paired equality and all source, prompt, example, schedule and token constraints remain mandatory. |
| E6 hidden-case discrimination | Compatible | Evaluation cases and their discrimination obligations are unchanged and must be independently reaudited. |
| Frozen slot ledger | Prospectively supplemented | Only its numeric training-case rule for the canonical slot receives the explicit future exception; the ledger file and all other slot rules remain unchanged. |
| Historical schedule and budgets | Compatible | No new example, case count, training seed, exposure slot, or optimizer step. |
| Freshness, exact/consumed overlap, AST-v2, E5 novelty | Compatible | Raw-zero reuse is disclosed and expressly permitted; all full-case, template and signature prohibitions remain blocking. |

No existing scientific requirement is waived. The sole intended rule change is the prospective construction exception above. If independent review finds a contradiction, construction must stop; this proposal cannot be treated as operative by interpretation alone.

## Closed threat examples

| Situation | Disposition |
|---|---|
| Canonical numeric slot has `0` and four positives from the specified `r.sample(pool, 4)` stream | Allowed **future construction** only after independent approval/freeze; activity and all other gates still apply. |
| A different numeric training slot is manually given `0` | Invalid construction. |
| Canonical witness slot is changed after a case, coverage, or similarity failure | Prohibited post-hoc change; candidate fails. |
| Valid `n=0` | Witnesses `SIGN_ZERO`, `EMPTY_LOOP`, and `LOWER_DOMAIN_BOUNDARY` together; not a V3.5 normal-event witness. |
| Positive case in the same example has connected, output-relevant decoder path and changing frozen INPUT intervention | May witness V3.5 activity, if proved separately in both conditions. |
| Numeric `n<0` | Invalid domain input; no negative-sign coverage. |
| Numeric `60` or `100` | `SIGN_POSITIVE`; not automatically an input-domain boundary. |
| Valid array `[-2,0,5,7]` | Witnesses all three array sign classes, with exact indices and values recorded. |
| Valid array `[0,0,0,0]` | `ZERO_PRESENT`, not EMPTY. |
| Malformed or short array | Invalid input, never EMPTY coverage. |
| Valid array containing `-16` or `+16` | Sign evidence only; not BOUNDARY evidence. |
| A required class is witnessed in only one training condition | FAIL. |
| A class value is present but the mapped decoder is dead or disconnected | `INPUT_DOMAIN` FAIL under V3.5. |
| One valid case witnesses multiple required classes | Allowed; each class and its evidence remain separately recorded. |

**Review boundary:** This is a proposal-only methodology commit. Do not implement the override, create fixtures or Attempt 004, reinterpret rejected attempts, train or infer, or authorize model execution from this file. Independent review must precede any prospective freeze and candidate construction.
