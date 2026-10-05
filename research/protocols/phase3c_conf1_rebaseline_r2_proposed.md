# CONF1 re-baseline R2 — mutation-liveness and training-case amendment

## §1 Status

Prospective amendment to the frozen R1 (`phase3c_conf1_rebaseline_r1_proposed.md`, LF-normalized SHA-256 `4e0ca5c576746ab51fce3414085fd698003a37f745dcb2004cdf8d8c14b3af31`) and to the frozen training-case rules of the slot ledger (`phase3c_conf1_slots.json`) and the input-domain amendment. Authored by the project head (Claude Opus 5.5) on 2026-10-05; binding when a freeze manifest binds this file. No CONF1 model outcome exists, Attempt 004 does not exist, and the construction seed has not been used for any R1 draw. The only evidence is non-model: the I2 synthetic P6 dry run (commit `6192040a7c275a10f369461600070bd56d885130`) and the R2 liveness-feasibility audit (commit `a58ceb1a1017064a15560bb4ed51c9eca44e7d18`, §7). No population, treatment, prompt, model-facing target, estimand, threshold, seed, budget or label changes.

## §2 Defects in R1 as frozen

D1 Domain-equivalent mutants. R1 P4(iii) and P6(b) require every single-statement-deletion mutant to be killed. Seventeen non-exempt programs contain a deletion mutant that produces the reference output on every valid input, so these gates can never pass: primary `CONF1-NC-AR-G1-R3` mutant 14 (`hitOr=0.`); training `CONF1-TR-NU-03-V0`, `-V2`, `-V4` and `CONF1-TR-NU-13-V1`, `-V3` mutant 7 (`hitP=0.`), and `CONF1-TR-NU-23-V0`, `-V2`, `-V4` mutant 8 (`hitQ=0.`), each in both conditions (16 programs). Mutant indices follow the accepted I1 enumeration (`conf1_r1.interp.enumerate_mutants`).

D2 Random training cases. Under the frozen random five-case rule with 12 synthetic seeds, P4(iii) failed for 7-14 programs per seed and P4(iv) for up to 2 (audit E2). Attempt 004 would fail with near certainty.

D3 K7. Under requirement-satisfying training cases, array ISOLATED training outputs never include ZERO while array primary outputs do (audit E4: 5 of 5 seeds), so K7 fails for a reason unrelated to the treatment contrast.

## §3 Decision R2-A: domain-equivalent mutants

A mutant is DOMAIN_EQUIVALENT when it produces the same outcome as its reference on every valid input. Proofs for the D1 list over the full valid domain:

- `CONF1-NC-AR-G1-R3` (P = value_exceeds_index, Q = even_value, R = large_magnitude): without the per-item reset, hitOr at item i equals the OR over items 0..i of (Q or R). The contribution hitP*hitOr can change only at an item where P is true and Q and R are false, i.e. an odd value with square at most 4 that exceeds its index: value 1 at index 0. Index 0 is the first item of the forward traversal, so no earlier item can have set hitOr.
- The 16 training programs traverse i = n down to 1, and the deleted reset belongs to first_half (2*i<=n), which is false for i > n/2 and true for i <= n/2. Under this traversal the predicate never becomes false after being true, so the un-reset indicator always equals the current predicate value.

Rule: P4(iii) and P6(b) apply to every single-statement-deletion mutant except (a) the 17 D1 pairs and (b) the unchanged R1 exemption for the COMPOSITION members of DOMAIN_DISJOINT_PAIR slots. Any other unkilled mutant is FAIL. Before applying these gates, the candidate builder recomputes the exhaustive equivalence enumeration of the R2 audit (method E1) on the constructed programs and must obtain exactly the D1 list and the DOMAIN_DISJOINT list recorded in the audit; any difference is STOP. A domain-equivalent mutant is a correct program, so a model program that omits one of these resets is correct.

## §4 Decision R2-B: requirement-directed training-case selection

This replaces the ledger's `training_numeric_cases` and `training_array_cases` rules and step 2 of the input-domain amendment's one-slot override. Steps 1, 3 and 4 of that override (canonical slot `CONF1-TR-NU-01-V0`; identical ordered inputs and case IDs for both members of a matched slot; no sixth case) and all case-class requirements are retained.

For each matched training slot, one ordered list of five inputs serves both members:

1. Candidate stream from the frozen per-slot generator `random.Random(int.from_bytes(sha256(f"{construction_seed}|{slot_id}|{tag}".encode("utf-8")).digest(), "big"))`, with `construction_seed` 20290123 (clarification C1) and tag `train-numeric` or `train-array`. Numeric: the order `r.sample(pool, len(pool))` over pool = 1..60 excluding 12, 13, 14. Array: successive `|`-joined tuples of four `r.randint(-16, 16)` draws; a tuple equal to an earlier accepted tuple or to one of the five selected array evaluation inputs (clarification C5, selected before training cases) is skipped and logged; the stream is the first 256 accepted tuples.
2. Requirements over both members: (iii) every deletion mutant of each member, other than those excluded by §3, killed by at least one chosen case (clarification C3); (iv) each of the slot's two predicates true on at least one item and false on at least one item across the chosen cases, and for the COMPOSITION member at least one item with both true; (v) the two members' outputs differ on at least one chosen case. For DOMAIN_DISJOINT_PAIR slots the COMPOSITION-member parts of (iii)-(v) are exempt as in R1.
3. For the canonical slot, case 1 is n = 0. The remaining cases are chosen one at a time from the unchosen stream, each maximizing the cumulative number of satisfied requirements; ties go to the earliest stream position. Case IDs follow selection order.
4. If any requirement is unmet after five cases: STOP. There is no fallback stream and no post-hoc change.
5. The `conf1_r1` interpreter may rank candidates; every verdict on the chosen cases is re-established with the pinned compiler (clarification C2), and any disagreement is STOP.

Rationale: training cases are diagnostic and never model-facing. They serve E1, P4 and acquisition-gate scoring. One fixed, seed-determined algorithm makes these diagnostics complete in both conditions without discretion and without changing any model-facing text. Audit E3: 0 unmet requirements on 5 of 5 synthetic seeds. Consequence to disclose: acquisition-gate scoring uses requirement-directed cases, identically in both conditions.

## §5 Decision R2-C: K7 becomes descriptive

K7 OUTPUT_CLASS is removed from the coverage catalog and from P4(ii). Output classes (ZERO, POSITIVE, MULTIDIGIT) of training and primary expected outputs are reported descriptively per domain and condition. Rationale: training cases and their expected outputs are never shown to the model, so their output class cannot affect what either condition learns; and no program statement differs by output magnitude, consistent with R1 decision C, which treats input values, offsets and constants as parameters rather than coverage units. The audit evidence (D3) prompted this review; the rationale does not depend on it.

## §6 Unchanged

Everything else in R1 and in the authorities R1 §9 retains, including the populations (60 paired training slots, 32 primary tasks), paired scaffold, prompts and targets, primary case procedure (clarifications C5 and C6), P1-P3, P4(i), P4(ii) for K1-K6 and the treatment rows, P5-P7, acquisition gate, seeds, budget, estimand, thresholds, bootstrap, labels, claim boundary, and the absence of model_execution_authorized.

## §7 Evidence

| Path | SHA-256 (raw bytes) | Commit |
|---|---|---|
| `scripts/audit_phase3c_conf1_r2_liveness_feasibility.py` | `2de6cb5cd17c60e878cf630c550c54c3fcfa3a599d8e99569f43cd359f73a254` | `a58ceb1a1017064a15560bb4ed51c9eca44e7d18` |
| `research/results/PHASE_3C_CONF1_PREFREEZE/r2_liveness_feasibility.json` | `69dd9efb7de72f5bddb1effdad5aee468ca0e425499087356bdc69d5d2a733f7` | `a58ceb1a1017064a15560bb4ed51c9eca44e7d18` |
| `research/results/PHASE_3C_CONF1_PREFREEZE/r2_liveness_feasibility.md` | `ed431011af56d5161b65af2263ca222fbcb9902cf6d48f10f5fe61a7924bc52a` | `a58ceb1a1017064a15560bb4ed51c9eca44e7d18` |
| `src/self_learning_ai/conf1_r1/gates_primary.py` | `51fc7de533e789550218b063f437f93eeac16ff0e98c5700e86400deba13335b` | `6192040a7c275a10f369461600070bd56d885130` |
| `research/protocols/phase3c_conf1_r1_implementation_clarifications.md` | `9fbe75fa2caf6a27ecbac943bec6a99f69c87a604669d533b73cc83e3bfcd328` | `6192040a7c275a10f369461600070bd56d885130` |

## §8 Reporting disclosures

The paper's methods section states: the D1 equivalent-mutant list and its proofs; that training cases are selected by the R2-B rule and that acquisition-gate scoring uses them in both conditions; that K7 is descriptive; and that D1-D3 were found before any candidate construction or model use.
