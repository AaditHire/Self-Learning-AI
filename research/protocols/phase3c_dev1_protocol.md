# Phase 3C-DEV1: structural diversity generalization development study

**Status:** frozen proposal for independent review, before DEV1 gradients or model evaluation. This is exploratory development, not a new Phase 3C confirmatory attempt or a continual-learning experiment. The historical Phase 3C `EVAL_A` is consumed for confirmatory use and its scores did not select these data or this recipe. The final-paper holdout remains sealed.

## Question and intervention

At fixed 60-example A training sets and the same 24-step QLoRA recipe, does a 12-archetype structurally diverse distribution transfer better to 36 fresh development A tasks than a 4-archetype template-dense distribution? The **only intended intervention** is training structural diversity. Both conditions have 30 numeric-iteration and 30 array-reduction examples, the same backbone, prompt format, adaptation, optimizer, seed set, epochs, slot count, and evaluation procedure. Parameterized examples in the four shared archetypes deliberately occur in both conditions; this is a controlled shared core, not 120 independent task structures.

Phase 3C-DIAG found 60/60 in-sample task passes and exact target reproduction for each existing A adapter, but weak fresh structural transfer, especially for arrays. That motivates this development comparison; no Phase 3C `EVAL_A` item or outcome is used as a DEV1 optimization target.

## Frozen materials

`scripts/build_phase3c_dev1_data.py` deterministically constructs the following GOCO material, with unique condition-specific IDs and five frozen semantic cases per ID. All outputs are committed as JSON before training.

| Split | Numeric iteration | Array reduction | Total |
| --- | --- | --- | ---: |
| Template-dense training | `fourth_square`, `nontriple_count`; 15 each | `negative_tally`, `neighbor_products`; 15 each | 60 |
| Structure-diverse training | The same two plus `alternating_weight`, `divisor_tally`, `descending_odd`, `quadratic_balance`; 5 each | The same two plus `positive_position`, `range_span`, `alternating_positions`, `even_square_total`; 5 each | 60 |
| Fresh development evaluation | `fourth_square_step` (NEAR), `nontriple_divisor_mix` (COMPOSITIONAL), `square_threshold_crossing` (FAR); 6 each | `negative_tally_unrolled` (NEAR), `range_neighbor_mix` (COMPOSITIONAL), `positive_run_length` (FAR); 6 each | 36 |

All tasks remain within A: numeric iteration over bounded indices or reduction over a fixed four-number array. The diverse distribution broadens branch, traversal, arithmetic, neighbor, extremum, position, and alternation structures while preserving the same input/output style. Numeric tasks read one nonnegative integer; array tasks read four pipe-delimited numbers; all print one number. Dense has two archetypes per subskill with 15 offset variants each. Diverse has six archetypes per subskill with five variants each. Offset variants do not count as distinct structures.

NEAR means core semantic operations shared with a training archetype but changed reference control or expression structure. COMPOSITIONAL means training operations recombined in an unseen task. FAR means a new operation/control composition inside the same A domain. These six archetypes and assignments were specified by construction, before any DEV1 model output; similarity scores do not reassign groups. Each group has 12 tasks, six per subskill. The six examples per evaluation archetype vary constants, not structure. Evaluation IDs and cases never appear in either training schedule. The future evaluator must use these cases only for scoring, never for recipe changes during a run.

## Reference and structural audits

`scripts/validate_phase3c_dev1_data.py` compiles and executes all **156** references over all **780** semantic cases: 60 dense, 60 diverse, 36 evaluation, five cases each. Frozen result: 780/780 pass. It also checks zero exact development train/evaluation prompt or reference overlap and zero exact prompt/reference reuse against Phase 3A, 3B, and consumed Phase 3C A evaluation suites. This bounded historical check does not inspect the final-paper holdout. Any failed case or exact forbidden reuse before training is a **STOP**.

`scripts/audit_phase3c_dev1_structure.py` records every 36×60×2 = **4,320** train/evaluation pair, prompt token-set Jaccard, identifier/number/string-normalized source `SequenceMatcher` similarity, exact coarse AST proxy equality, declared semantic-operation Jaccard, and per-task nearest neighbors. It publishes full pair records, histograms below 0.98, and distance-group summaries. There are zero exact prompt/reference/AST-proxy pairs. Maximum normalized code similarity is 0.9066 for dense and **0.9725** for diverse; 30 diverse pairs reach 0.95 but none reach 0.98. The 0.9725 match is `fourth_square_step` to `quadratic_balance`; it reflects similar GOCO scaffolding and is an interpretive risk, even though their declared semantic operations differ. Similarity proxies are not proof of semantic independence. No similarity result was used to move evaluation tasks or change the archetype count.

## Matched training contract and frozen schedule

Use the immutable `Qwen/Qwen2.5-Coder-3B-Instruct` revision `488639f1ff808d1d3d0ba301aef8c11461451ec5`, the two base-weight hashes in `phase3c_config.json`, adapter-only NF4 QLoRA, and the unchanged Phase 3C A recipe: 4-bit NF4/double quantization/float16; rank 16, alpha 32, dropout 0.05, no bias, target modules `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj`; micro batch 1, accumulation 8, max length 320, gradient checkpointing; PagedAdamW8bit, learning rate 0.0002, weight decay 0, betas (0.9,0.999), epsilon 1e-8, max gradient norm 1; linear scheduler, five warmup optimizer steps; exactly three epochs, final checkpoint selected without evaluation. Start each condition and seed from the same immutable base weights with a fresh, same-policy optimizer and scheduler. Never merge or alter base weights.

The three fixed paired seeds are **20270925, 20271013, 20271119**. `phase3c_dev1_schedule.json` fixes 60 slots per epoch and the exact example ID at every slot, for 180 exposure slots and 24 optimizer steps per seed-condition. At each corresponding slot the two conditions have the same A subskill; every ID appears once per epoch. For both conditions use identical training device and package environment, prompt template, tokenizer, checkpoint rule, greedy evaluation decoding, pinned GOCO compiler and semantic scorer. No score-driven checkpoint choice, resampling, seed replacement, hyperparameter change, or additional training is allowed inside DEV1.

The pinned tokenizer audit (`token_budget_audit.json`) confirms no sequence exceeds 320 tokens (dense max 232, diverse max 260). One epoch is 12,183 versus 12,515 full tokens, a **2.73%** difference relative to dense; supervised target tokens are 4,809 versus 5,015, a **4.28%** difference. Before gradients, if a reproducible rerun finds either full-token or supervised-token exposure differs by **more than 10%** relative to dense, **STOP for independent redesign**. The frozen data pass this gate. Equal examples and steps do not imply exactly equal FLOPs; report actual token counts, wall time, and compute in the eventual run. The fixed condition difference in target lengths remains a confound.

## Evaluation and descriptive analysis plan

After authorized training, run exactly one greedy pass per final adapter on its own 60 training IDs and the common 36-task fresh development suite. Use the frozen Phase 3C system/user templates, no docs, `do_sample=false`, one beam, max input 8192, max new 512, no retry or repair, the pinned deterministic GOCO compiler, 3-second compile/run timeout, 65,536-byte stream limit, and five frozen hidden semantic cases. A PASS requires compilation and all five cases. Record raw output and compiler/scorer failure class (syntax, lexical, compiler, runtime, hidden-semantic), exact reference-target reproduction, and per-task pass. Do not score the sealed holdout. Do not use consumed Phase 3C `EVAL_A` as an optimization target or decide a winner from it.

Primary **descriptive** effect: for each paired seed, diverse minus dense fresh development pass@1 over 36 tasks, in percentage points; report the unweighted three-seed mean and all three seed effects. Also report each condition's training pass@1, train-to-development gap, exact target reproduction, A subskill (18 IDs each), NEAR/COMPOSITIONAL/FAR (12 each), all six archetypes (six each), and error categories. Report both absolute pass counts and rates. This is not the old 24/32 Phase 3C acquisition gate and has no paper-level PASS threshold.

All three seeds see the same 36 evaluation task IDs. Treat task ID as a repeated cluster across conditions/seeds, and report descriptive paired uncertainty from 10,000 task-cluster bootstrap resamples (seed **20271221**), preserving all six condition/seed observations for each sampled ID. For overall and subskill effects, resample task IDs within subskill to retain 18/18 balance; for distance-group effects, resample within the six subskill×distance cells to retain 6 each. Report percentile 2.5/97.5 intervals. Also resample six whole evaluation archetype blocks, preserving all tasks and observations in each, as a correlation sensitivity; label this unstable with six blocks. Show archetype-specific results individually. Seeds are three fixed repeats, not independent task observations or a population of architectures. Bootstrap intervals are descriptive, not a significance or PASS gate. Do not infer broad A generalization from this constructed suite.

If both conditions fit training and diverse transfers better, structural diversity is promising for further development. If both fit but fail fresh tasks, training diversity alone is insufficient. If dense fits and diverse does not, the fixed recipe may not learn the broader distribution. If a gain is only NEAR, transfer remains limited. Large seed variation leaves stability unresolved. No interpretation may be upgraded to confirmatory evidence.

## Execution, archival, and firewall

The design-stage order is: build JSON → validate every reference/case and exact historical separation → structural and tokenizer audits → paired schedule and hashes → independent review → only then separately authorized model execution. The future implementation must assert manifest hashes, compiler/model/tokenizer hashes, 60 IDs per condition, no evaluation IDs in the schedule, exact slot order, 24 optimizer steps, and final-checkpoint rule before exposing GPUs. It must save raw per-ID outputs and training logs, check unchanged base hashes after training, and archive finalized adapters and essential records using the established off-machine/versioned GitHub + Git LFS preservation workflow with a verified fresh-clone restore. An unavailable or failed remote restore is an archival **STOP**, not a completed preservation claim. The main GOCO repository remains read-only.

For independent implementation review, the future runner interface is one `--seed` from the frozen list and one `--condition dense|diverse`, plus the manifest path; it loads the specified 60 rows in the exact per-epoch schedule, refuses existing output paths, logs every exposure ID/step and token count, and emits only the final adapter and raw training record. A separate evaluator takes an adapter path, frozen `training|development` suite ID, and seed; it writes one raw record per task with prompt, generated source, compiler trace, five case outcomes, exact target-match flag where applicable, and failure class. A deterministic analyzer accepts only the complete six-cell record set, recomputes all rates and bootstrap results from task IDs, and never makes a paper-level PASS decision. These execution scripts are **not** part of this design commit; implementation and execution require separate review. The current `build`, `validate`, `audit`, and `freeze` scripts perform data and reference work only.

DEV1 evaluation is development-consumed once executed. Neither it nor consumed Phase 3C `EVAL_A` may serve as untouched confirmatory evidence. After exploratory selection and a separately frozen new recipe, a **new** confirmatory acquisition/retention suite must be constructed prospectively; it is outside DEV1. No B training, replay, A retention after B, alternate replay ratio, EWC, or other continual-learning intervention is part of this study.

## Explicit decision and stop logic

1. **STOP before gradients** on any reference semantic failure, exact forbidden prompt/reference reuse, missing or changed manifest hash, changed base/compiler/tokenizer/prompt, schedule imbalance, ID leakage, token length above 320, or token-exposure difference above 10% under the rule above.
2. After independent review and separate execution authorization, execute each of six seed-condition cells exactly once at the frozen recipe. An incomplete cell or protocol deviation is reported, not silently replaced.
3. Score training and fresh development suites once with the frozen evaluator. Report the descriptive effects and failure classes regardless of direction. There is **no DEV1 scientific PASS gate** and no post hoc threshold for selecting a publishable result.
4. Mark the suite development-consumed after execution. **STOP for independent analysis** before any new confirmatory design or B-stage work.

## Unresolved scientific risks

- Hand-built archetypes and repeated parameter variants limit external validity; six evaluation archetypes are few and correlated.
- The diverse condition changes the frequency of four shared structures as well as adding eight new structures, so distribution weight and coverage are intertwined.
- Higher code similarity for some diverse/evaluation pairs (up to 0.9725) may make the diverse condition locally closer to parts of the evaluation suite; the complete pair audit is required for interpretation.
- Fixed example/step budgets leave a small measured token and FLOP difference, and target length may alter optimization.
- Five semantic cases per task do not prove full semantic correctness.
- Three seeds and one backbone/compiler/prompt style yield limited precision; seed and archetype sensitivity must be shown.
- Training pass and exact target reproduction can coexist with poor transfer; no development result rescues the failed Phase 3C confirmatory acquisition gate.
- An eventual winning DEV1 recipe remains exploratory until tested on a prospectively constructed untouched suite.

No DEV1 model gradients or model evaluations are authorized by this frozen design. **STOP for independent scientific review.**
