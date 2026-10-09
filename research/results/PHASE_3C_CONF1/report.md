# Phase 3C-CONF1 report: prospective composition-transfer confirmation

**Label: `NOT_CONFIRMED_UNDER_CONF1`.** On 32 fresh Novel Composition tasks across five paired seeds, COMPOSITION practice beat ISOLATED practice by **+5.0 percentage points** (95% percentile interval −5.0 to +20.0). Both preregistered numerical criteria failed: ΣE = 8 against a required 32 (the +20 pp target), and the interval's lower bound is not above zero. This label does not show a zero effect. It shows that the large DEV2R development effect (+58.3 pp) did not reproduce at the preregistered magnitude on a fresh, matched, frozen design.

## 1. What was tested

Protocol: `research/protocols/phase3c_conf1_proposed_protocol.md` (R1 and its frozen amendments).

- **Conditions.** Two fresh rank-16 QLoRA adapters on pinned Qwen2.5-Coder-3B-Instruct, trained on the same eight GOCO predicates:
  - ISOLATED: independent predicate practice;
  - COMPOSITION: pairwise joint-predicate practice.
  Each condition had 60 new examples, and the conditions were matched on scaffold, exposures and budget (24 optimizer steps per cell).
- **Primary estimand.** The mean over seeds 20280117, 20280223, 20280329, 20280411 and 20280507 of the paired per-task COMPOSITION − ISOLATED pass@1 rate on 32 Novel Composition tasks. Generation was one greedy pass; a task passes only if it compiles and gets all five hidden cases right.
- **Confirmatory rule.** Support required a point estimate of at least +20 pp (ΣE ≥ 32) AND a 95% bootstrap lower bound strictly above 0. That bootstrap used 10,000 replicates, seed 20290119, resampling seeds and blocks within each domain.
- **Execution.** Frozen candidate Attempt 004.
  - First authorization commit: `4c1d0b6`.
  - Run E1-R2 trained all 10 cells, then stopped at confirmatory task index 128. The cause was a Windows EINVAL in the scorer's pipe write, an infrastructure fault rather than a model outcome.
  - Amendment C15 (`611cdc2`, `8eb836c`, `b3b30b9`) added a bounded fresh-process re-invocation in the CONF1 scorer adapter and a one-time reviewed continuation.
  - Continuation authorization: `7a2e022`.
  - The continuation scored task 128 from its persisted raw generation, then generated and scored tasks 129–639 in frozen order. No re-invocation was ever needed, and the 128 earlier scores were not recomputed.
  - No confirmatory score was viewed before the frozen analyzer ran.
  - Execution record: `research/results/PHASE_3C_CONF1/execution/` (commit `a1ec61c`).

## 2. Results

**Acquisition passed in all 10 cells**: nine scored 60/60, and COMPOSITION seed 20280329 scored 56/60. On own-training semantics, ISOLATED scored 300/300 and COMPOSITION 296/300.

**Primary (Novel Composition, 32 tasks × 5 seeds).** Pooled passes were ISOLATED 7/160 and COMPOSITION 15/160.

| Seed | ISOLATED /32 | COMPOSITION /32 | Diff (pp) | Array (pp) | Numeric (pp) |
|---|---:|---:|---:|---:|---:|
| 20280117 | 0 | 4 | +12.5 | +25.0 | 0 |
| 20280223 | 2 | 4 | +6.25 | +12.5 | 0 |
| 20280329 | 1 | 1 | 0 | 0 | 0 |
| 20280411 | 3 | 4 | +3.125 | +18.75 | −12.5 |
| 20280507 | 1 | 2 | +3.125 | +12.5 | −6.25 |
| **Mean** | | | **+5.0** | **+13.75** | **−3.75** |

Block mean differences (pp):

| Block | Mean |
|---|---:|
| Array G1 | 0 |
| Array G2 | **+55** |
| Array G3P | 0 |
| Array G4 | 0 |
| Numeric G1 | 0 |
| Numeric G2 | −15 |
| Numeric G3 | 0 |
| Numeric G4 | 0 |

Predeclared qualifications, which do not affect the label:

| Qualification | Result |
|---|---|
| Every seed nonnegative | true |
| At least four seeds positive | true |
| Both domains positive | **false** |
| At least six of eight blocks positive | **false** |

Paired discordance over the 160 seed-tasks: 13 COMPOSITION-only passes, 5 ISOLATED-only, 2 both, and 140 neither.

**Sanity (16 primitive tasks): `NONCATASTROPHIC`.** ISOLATED passed 0/80 and COMPOSITION 1/80, a mean difference of +1.25 pp.

**Structural Transfer (exploratory, 16 tasks).** Both conditions scored 0/80, with zero difference in every seed and block.

**Descriptive.**
- Tasks containing OR scored 0/40 in both conditions and both domains.
- On OR-free tasks:
  - array: ISOLATED 4/40, COMPOSITION 15/40 (+27.5 pp);
  - numeric: ISOLATED 3/40, COMPOSITION 0/40 (−7.5 pp).
- Exact-target reproduction of own training was ISOLATED 149/300 and COMPOSITION 140/300.
- Primary-task failures were mostly compile failures and output mismatches, with almost no execution failures.

## 3. Interpretation (project head)

1. **The confirmatory claim fails.** CONF1 does not support "composition practice improves novel-composition generation by at least 20 pp" under this design. Nothing in this run licenses a broader composition or continual-learning claim.
2. **The development effect shrank by more than an order of magnitude.** DEV2R gave +58.3 pp (10/48 vs 38/48) on its own topology. CONF1, on a fresh topology with a new scaffold and fully matched budgets, gives +5.0 pp. The most likely reading (INFERENCE) is that much of the DEV2R gain was specific to that suite's topology or template, not a general benefit of joint practice.
3. **Both conditions are near the floor on novel structure.** Training was learned almost perfectly (296–300/300 semantic), yet novel compositions passed 4–9% of the time, and structural transfer stayed at 0%. The model reproduces trained archetypes but rarely builds unseen combinations of the same predicates. This floor limits how large any measurable effect could be and is itself the main substantive finding.
4. **The small positive signal is concentrated in one place.**
   - Array G2 alone nets +11 paired outcomes, more than the overall net of +8; Numeric G2 nets −3. OR-free array tasks show +27.5 pp.
   - Numeric tasks lean slightly negative, and OR structures are never solved.
   - These are post-hoc, single-block descriptions. They are hypotheses for exploration, not findings.
5. **Process outcome.** The prospective machinery worked: freeze, hash binding, a run-once fault STOP, a reviewed amendment, and a continuation with blind analysis. The one infrastructure fault was caught, amended and resumed without viewing outcomes. The C15 equivalence test showed the amended adapter reproduces the 128 pre-fault rows exactly.

## 4. Limitations

- One model, one recipe and one GOCO domain.
- Five seeds and 32 primary tasks. Seed-task observations are correlated.
- The +20 pp target was chosen prospectively but is coarse for floor-level rates.
- CUDA nondeterminism.
- Prompt semantics and target loss geometry differ by construction between conditions.
- The run was resumed under amendment C15. The resume was reviewed and outcome-blind, but it is still a deviation from an uninterrupted single pass.

## 5. Claims ledger entry (CLM-013)

- **Justified:** under the frozen CONF1 design, the observed COMPOSITION − ISOLATED Novel Composition difference was +5.0 pp, with a 95% interval of −5.0 to +20.0. The preregistered confirmatory label is `NOT_CONFIRMED_UNDER_CONF1`. Both conditions learned their training sets but rarely solved novel compositions (7/160 and 15/160), and neither solved Structural Transfer (0/80).
- **Not justified:**
  - that composition practice has no effect;
  - that it has a ≥20 pp effect;
  - any claim about the DEV2R effect's generality, continual learning, retention or self-learning.
