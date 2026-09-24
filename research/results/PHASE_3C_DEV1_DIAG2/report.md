# Phase 3C-DEV1-DIAG2: post-hoc compositional transfer failure audit

**Status:** diagnostic of development-consumed DEV1 material. No new model invocation, training, development generation, compiler execution, or confirmatory evaluation occurred. This report describes saved outputs only. It does not define a new success gate or a DEV2 design.

## Sources and audit method

The diagnostic script reads the frozen Dense/Diverse training prompts and targets (60 examples each), 36 development prompts and reference programs, the frozen structural audit and nearest-training analysis, and all six saved development evaluation files (three seeds per condition). `operation_inventory.json` records SHA-256 for each consumed file. It checks task IDs, references, outcome counts, and the published failure totals before writing results. It never loads an adapter or scorer. The reference programs and prompts were read to curate semantic primitives; the existing labels were treated as a cross-check, not used alone. No reference or task was edited.

The machine-readable outputs are [operation_inventory.json](operation_inventory.json), [coverage_matrix.json](coverage_matrix.json), [failure_audit.json](failure_audit.json), and [failure_stages.json](failure_stages.json). The matrix has 36 task rows, each with Dense and Diverse coverage and three observed seed outcomes. The failure audit has **all 144** COMPOSITIONAL/FAR condition × seed × task records, including generated code, saved compiler/test statuses, first compiler stderr, required-versus-visible surface signatures, visible unexpected operations, and frozen nearest-reference similarity. These fields permit review of every individual failure without repeating generation or scoring.

## Training operation inventory

All numeric training examples read `n` and display a scalar. All array examples parse four pipe-separated numbers with `IMPORT strings`, `strings.SPLIT`, and `strings.TO_NUMBER`, store them in a four-element array, and display a scalar. Each archetype has five Diverse variants or fifteen Dense variants, differing principally in constants; see the inventory for representative prompts and exact reference source.

| Archetype | Conditions | Required operations and order | Control/data form |
|---|---|---|---|
| `fourth_square` | both | filter indices divisible by four, accumulate their squares | bounded scalar loop, IF |
| `nontriple_count` | both | filter indices not divisible by three, count, affine output | bounded scalar loop, IF |
| `negative_tally` | both | parse four values, filter negatives, count | indexed array loop, IF |
| `neighbor_products` | both | parse four values, sum adjacent products | indexed array loop |
| `alternating_weight` | Diverse | parity branch, position-weighted add/subtract | scalar loop, IF/ELSE |
| `divisor_tally` | Diverse | divisibility test, count | scalar loop, IF |
| `descending_odd` | Diverse | descend through indices, filter odd, affine accumulation | condition-controlled scalar loop |
| `quadratic_balance` | Diverse | accumulate square minus linear term | bounded scalar loop |
| `positive_position` | Diverse | filter positive values, weight by position, sum | indexed array loop, IF |
| `range_span` | Diverse | track minimum and maximum, subtract at output | indexed array loop, two IFs |
| `alternating_positions` | Diverse | branch on index parity, add/subtract values | indexed array loop, IF/ELSE |
| `even_square_total` | Diverse | filter even values, sum their squares | indexed array loop, IF |

Dense therefore covers seven curated primitive types; Diverse covers nineteen. These counts depend on the stated granularity and are descriptive. Neither training condition includes the full algorithm of any of the six evaluation archetypes. No reference uses absolute value or nested iteration; those labels were not invented. All array evaluation tasks use the same `strings` parsing API, so new library calls are not needed for those tasks.

## Development requirements and structural novelty

Each row below represents six task IDs (`-21` through `-26`). The full 36-row primitive-presence matrix records every required primitive individually. “Similarity” is the frozen nearest **evaluation-reference to training-reference normalized-code similarity**, not similarity of the saved model generation to a training example. A high score can coexist with a critical missing control operation.

| Development archetype (distance) | Required operation sequence and new structure | Dense / Diverse coverage | Frozen nearest code similarity, Dense / Diverse | Outcomes per condition across three seeds |
|---|---|---|---|---|
| `fourth_square_step` (NEAR) | reindex multiples of four, accumulate equivalent squares with step-index loop | all primitives in both; direct `fourth_square` semantic analogue; new loop form | 0.8918 / 0.9725 | 0/18 / 18/18 |
| `negative_tally_unrolled` (NEAR) | parse array, test/count each of four negatives separately | all in both; direct `negative_tally` analogue; loop unrolled | 0.8232 / 0.8232 | 18/18 / 18/18 |
| `nontriple_divisor_mix` (COMPOSITIONAL) | two independent tests in one loop; sum both counts | Dense lacks divisor test; Diverse has both tests separately, not their combination | 0.8955 / 0.9123 | 0/18 / 0/18 |
| `range_neighbor_mix` (COMPOSITIONAL) | sum adjacent products, track min/max in second loop, combine range once | Dense lacks extrema/range; Diverse has parts separately, not two-stage combination | 0.7989 / 0.8908 | 0/18 / 0/18 |
| `square_threshold_crossing` (FAR) | accumulate consecutive squares until **cumulative** threshold, output first crossing index | both have square accumulation; neither has accumulator-controlled termination or first-crossing task | 0.7911 / 0.8700 | 0/18 / 0/18 |
| `positive_run_length` (FAR) | positive filter, increment/reset run state, track longest segment | Dense lacks filter and state; Diverse has positive filter and max tracking separately, but lacks run increment/reset logic | 0.9066 / 0.9066 | 0/18 / 0/18 |

Thus Dense's compositional cases include **missing primitives**, while Diverse's compositional cases are **known primitives in unseen combinations**. FAR cases have essential missing state or termination operations under both conditions. The NEAR cases are **structural analogues** with a changed loop form. These are multi-label descriptions, not performance-derived distance reassignments. `positive_run_length` is a useful caution: its 0.9066 code similarity does not establish coverage of its run-state requirement.

## Audit of all 144 COMPOSITIONAL/FAR outcomes

The full per-outcome audit is in `failure_audit.json`; this table aggregates each eighteen-outcome archetype × condition cell. `semantic` is the saved compiler-semantic category; `hidden` means the generated program compiled and executed but failed hidden semantic cases. All 144 failed the saved hidden suite.

| Condition | Archetype | Syntax | Compiler semantic | Hidden semantic | Representative observed failure behavior |
|---|---|---:|---:|---:|---|
| Dense | `nontriple_divisor_mix` | 7 | 11 | 0 | Both tests often appear in text, but comma declarations cause syntax failures and repeated loop variable declarations cause scope errors. |
| Diverse | `nontriple_divisor_mix` | 6 | 12 | 0 | Both tests appear; comma declarations and repeated `i` declarations dominate. Some divisor loops use a square-root bound without correct paired-divisor accounting. |
| Dense | `range_neighbor_mix` | 18 | 0 | 0 | Array parsing and neighbor/extrema motifs appear, but comma declarations prevent execution. Some generations add the range in every neighbor iteration rather than once. |
| Diverse | `range_neighbor_mix` | 5 | 0 | 13 | Five comma-declaration syntax failures; executable outputs can add an unrequested whole-array sum or wraparound product and use positional differences instead of max−min. |
| Dense | `square_threshold_crossing` | 18 | 0 | 0 | Comma declarations recur; several generations request extra input inside a loop and use `BREAK`/other control tokens absent from the reference. |
| Diverse | `square_threshold_crossing` | 18 | 0 | 0 | Comma declarations dominate; visible candidate loops still have indexing/order or unrequested input/control differences. |
| Dense | `positive_run_length` | 6 | 0 | 12 | Several executable programs count current consecutive positives without a separate maximum, initialize/reset at one, or use adjacent-value relationships rather than positivity alone. |
| Diverse | `positive_run_length` | 0 | 5 | 13 | Many executable programs require equal/consecutive values or reset a run at one; some do not track the best run. Five saved compiler-semantic failures remain. |

The code records surface motifs separately from verified outcomes. For example, a `%3!=0` string is evidence that a test was generated, not that the resulting program implements the intended count. A missing regex signature can be a detector limitation. Comma declaration is a GOCO-form error, whereas wraparound multiplication or an extra array sum is a task-semantic deviation. “Visible training archetype motifs” identify recognizable source patterns in generated text; they do **not** establish that a model copied a training example or reveal internal representations. There is no generation-to-training copying claim. The frozen nearest similarity concerns references only.

## Failure-stage transition and NEAR contrast

The saved 108 outcomes per condition exactly reproduce the DEV1 totals: Dense **18 success, 67 syntax, 11 compiler semantic, 12 hidden semantic**; Diverse **36 success, 29 syntax, 17 compiler semantic, 26 hidden semantic**. Distribution:

| Distance / subskill (18 outcomes per cell) | Dense | Diverse |
|---|---|---|
| NEAR numeric | 18 syntax | 18 success |
| NEAR array | 18 success | 18 success |
| COMPOSITIONAL numeric | 7 syntax, 11 compiler semantic | 6 syntax, 12 compiler semantic |
| COMPOSITIONAL array | 18 syntax | 5 syntax, 13 hidden semantic |
| FAR numeric | 18 syntax | 18 syntax |
| FAR array | 6 syntax, 12 hidden semantic | 5 compiler semantic, 13 hidden semantic |

The successful Diverse NEAR numeric archetype requires the same multiple-of-four and square-sum operations as `fourth_square`, has a direct semantic analogue, and has frozen nearest code similarity 0.9725. Dense sees the same primitives and an analogue, but its nearest similarity is 0.8918 and its saved generations fail GOCO syntax. The other successful NEAR archetype is `negative_tally_unrolled`, solved by both conditions despite lower code similarity 0.8232. Thus similarity is descriptive, not a sufficiency rule. The failed COMPOSITIONAL archetypes in Diverse require known pieces in unseen order/combination; the FAR archetypes add missing control/state operations. Diverse shifts many array failures from syntax to executable hidden-semantic errors, especially the compositional array case. Numeric compositional failures remain mostly compiler errors and FAR numeric remains uniformly syntax. This is **consistent with** improved GOCO-form generation in parts of the distribution while semantic composition remains unsolved; it does not prove an internal mechanism or isolate a causal source.

## Candidate bottlenecks

| Candidate | Evidence for | Evidence against / limit |
|---|---|---|
| A. Primitive coverage | Dense lacks divisor/extrema/range in COMPOSITIONAL; both lack threshold-crossing and run-state parts in FAR. | Diverse contains all curated COMPOSITIONAL primitives but still solves 0/36 compositional seed-task outcomes. Primitive presence alone is insufficient. |
| B. Compositional practice | Diverse's individually trained nontriple/divisor and neighbor/extrema motifs are not reliably combined; executable array combinations fail hidden cases. | Many numeric mix outputs never compile, so semantic composition is not fully observed. No controlled composition-practice manipulation was run. |
| C. GOCO language/API robustness | 67 Dense and 29 Diverse syntax failures; comma declarations and loop-variable scope errors are visible even where relevant tests occur. | Array parsing API is shared with training; 26 Diverse failures execute yet are semantically wrong. Syntax is not the sole bottleneck. |
| D. Fixed-budget capacity | Six adapters fit training 60/60, but broad transfer is limited under the fixed recipe. | No budget variation was run. Perfect training fit and task structure do not identify an insufficient step/example budget as the cause. |
| E. Mixed | Missing FAR primitives, failed known-part composition, and GOCO-form errors coexist and vary by subskill. | This is a descriptive summary rather than a uniquely identified causal explanation. |

**Best supported development hypothesis: E, mixed bottlenecks.** A future **primitive-coverage-matched compositional-curriculum study**, with GOCO syntax outcomes measured separately, would help separate coverage from composition and language-form effects. This is only a study *type*; no DEV2 dataset, budget, rule, or experiment is specified here.

## Claims boundary and limitations

**What this diagnostic supports:** under the frozen DEV1 recipe, Dense and Diverse both failed all 24 COMPOSITIONAL/FAR task IDs across three seeds; Diverse's constituent-primitives coverage did not suffice on the two compositional archetypes; failure stage depends strongly on subskill/archetype; FAR requirements include operations absent from both training conditions; some generated outputs visibly combine known scaffolds yet fail at syntax, compiler semantics, or hidden behavior.

**What it does not support:** an internal neural mechanism, universal inability to compose programs, causally sufficient benefit from any proposed intervention, a budget-capacity explanation, broad GOCO/API competence, continual learning, replay effectiveness, or confirmatory performance claims. The 36 development tasks contain only six archetypes and six constant variants per archetype; seed-task pairs share task IDs and structures. The primitive taxonomy and token signatures are human-curated and fallible. Frozen code similarity is a reference-structure descriptor, not a measured causal distance or evidence that outputs copied training text. Hidden-case outcomes and compiler stages are reused exactly as saved; no fresh semantic adjudication was run.

**STOP:** DEV1 development remains consumed. Independent review is required before any future development-study design or execution.
