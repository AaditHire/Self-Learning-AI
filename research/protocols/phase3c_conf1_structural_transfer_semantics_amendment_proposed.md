# CONF1 structural-transfer semantics amendment — prospective proposal

**Status: PROPOSED FOR INDEPENDENT SCIENTIFIC REVIEW; NOT FROZEN.**

Phase: **Phase 3C — CONF1**. Operational starting HEAD: `c6c8a32fdc09c0ea5193ddbf68ecee7ac388483b`, branch `main`, clean tracked worktree. Proposal date: 2026-10-02. This document is the sole proposed repository change. It creates no freeze manifest and authorizes no implementation, canonical graph recipe, candidate construction, scientific evidence production, model execution, or downstream experiment.

## 1. Scientific status and authority boundary

The original frozen authorities retained the structural-transfer families but failed to completely define and bind their mathematics. The authority-audit disposition supplied for this task is `STRUCTURAL_TRANSFER_SEMANTICS_PARTIALLY_RECOVERED_AUTHORITY_GAP`. Independent reading at the operational baseline confirms the relevant distinction: the slot ledger fixes structural labels and roles; the reviewed v2-to-v3 disposition retains aggregator names; neither supplies the complete strict-prior function and its slot binding specified below.

This is a **genuine prospective scientific specification repair**, before Attempt 004 and before any current CONF1 model result. The definitions are new, user-selected prospective choices for independent review. They are **not claimed to have been recovered from frozen authority**. In particular, choosing strict-prior PREFIX over inclusive-prefix, existence-only, or another interpretation is mathematically consequential. The amendment as a whole is not `REPRESENTATION_ONLY`.

No scientific result motivates these choices. No candidate result, model output, historical task-level success/failure, sealed holdout, or expected-label semantics is an input to this amendment. The original protocol's historical aggregate motivation does not select either new function. Historical implementation behavior is not normative authority. It may be compared only descriptively after the complete prospective text in sections 1–10 is fixed, and that comparison must not affect or revise the definitions.

If independently accepted and subsequently frozen, **this amendment** will own the missing structural-transfer mathematical definitions and bindings. Existing authorities continue to own all rules outside that narrow repair. This proposal does not become operative merely through creation or commit; independent review and an accepted prospective freeze remain prerequisites. Attempts 001–003 retain their historical status. The 17 RO development files tracked by starting commit `c6c8a32fdc09c0ea5193ddbf68ecee7ac388483b` remain **DEVELOPMENT_ONLY** and gain no scientific authority or readiness status.

### 1.1 Independently read evidence

The following evidence fixes the boundary, rather than supplying the new formulas:

| Repository authority | Relevant provision and conclusion |
|---|---|
| `phase3c_conf1_slots.json` | `slots.structural_transfer` contains 16 records: two structural labels × two domains × four rotations. Each has `task_id`, `family`, `group`, `structure`, `rotation`, and `role_predicates`; no complete initialization/recurrence/output definition. `training_semantics`, `graphs`, and `candidate_policy` independently fix the treatment, primary graphs, construction seed, case rules, and `no_semantically_dead_code: true`. |
| `phase3c_conf1_coverage_v3_v2_disposition.md` | Row 1.5 retains `sum_per_item`, `prefix_pair`, and `product_of_counts` under V3.2. Row 4.3 marks the old three aggregator counterfactual forms `REMOVED_AS_OVERREACH`; they do not supply a normative normal-execution law here. |
| `phase3c_conf1_coverage_v3_proposed.md` and freeze manifest | V3.1 prospective slot-derived contracts; V3.2 closed ontology and edges; V3.3 narrow equivalences; V3.4 both-condition coverage including exploratory transfer; V3.5 activity/interventions; V3.6 sole treatment exception; V3.7/E5 complete output/state signatures; V3.8 fail closed. |
| `phase3c_conf1_proposed_protocol.md` | §§1–4 question, treatment, counts, estimand and interpretation; §5 fixed G1–G4/rotations and prospective secondary specification; §§3/6/12 dead-code and paired-scaffold restrictions; §7 review, freeze and execution boundary. Structural Transfer is exploratory, with no threshold and no rescue or veto of the primary contrast. |
| `phase3c_conf1_paired_scaffold_normalization_proposed.md` and freeze manifest | Scope and closed comparison rule preserve the paired training source/prompt/case identities and the sole marked ADD-versus-MUL difference. They do not define structural-transfer mathematics. |
| `phase3c_conf1_input_domain_case_classes_and_training_amendment_proposed.md` and freeze manifest | Numeric input is nonnegative integer `n`, traversal positions `1..n`; arrays have exactly four signed integer fields in fixed input order. Sampling pools are not domain bounds. The existing sole numeric training-case override remains intact. |
| `phase3c_conf1_delegated_evidence_interfaces_proposed.md` and freeze manifest | §1 subordinates representations to scientific authorities and treats current scripts as descriptive; §§10/14/15 retain E1, E5 and E6 populations and ownership. Unrepresentable scientific facts are unresolved, never silently reinterpreted. |
| `phase3c_conf1_reference_only_catalog_proposed.md` §1.3 and its freeze manifest; frozen RO interface clarification v2 | Source accounting does not waive `no_semantically_dead_code`, admit a scientific source extra, or create a new scientific rule. Unused ledger metadata is distinguished below from executed source extras. |
| `phase3c_conf1_ast_adjudication_v2.md` | Source/template overlap remains a separate audit retaining source structure; this proposal adds no overlap normalization or deletion permission. |

The ten upstream identities in the delegated-interface freeze manifest were independently verified against their declared hash policy, exact size, and committed Git blob at the starting HEAD. In particular, the slot ledger's exact-byte SHA-256 is `5fe76fbc02e9f65174327199c2004f7e51f19a7f3866ae15709744c5274415c2`, size 47,968 bytes, Git blob `133c9c7275bcedeaf2474e54e61bae47923508ad`. These checks identify existing authorities; they do not freeze this proposal. No sealed holdout or expected-label file was read or hashed for this task.

## 2. Prospective slot bindings and role scope

For every already-frozen structural-transfer record, bind its existing label as follows:

| Frozen structural slot label | Proposed mathematical function |
|---|---|
| `prefix_running_pair(P,Q)` | `prefix_pair(P,Q)` as defined in §3 |
| `two_pass_product(P,Q)` | `product_of_counts(P,Q)` as defined in §4 |

`P` and `Q` are **exactly** that record's existing `role_predicates.P` and `role_predicates.Q`. No predicate is substituted, re-rotated, chosen from a case, or assigned from an implementation. All 16 task IDs, families, groups, structural labels and rotations remain unchanged. This supplies their missing mathematical binding; it creates no new slot or population.

`R` and `S`, where present, remain frozen role metadata. They are not arguments to either function and contribute no computation unless an independently applicable, already-frozen requirement demands their use. The authorities read for this proposal contain no such requirement for these structural-transfer records. Merely listing all four rotated roles is not a requirement to evaluate all four predicates.

Unused `R/S` **metadata is lawful**: the fixed role ledger can retain a complete rotation map while a slot's mathematical function depends on only `P/Q`. Metadata is not executed source and does not supply a capability witness. The frozen no-semantic-dead-code rule applies to generated source: it does not permit unused `R/S` predicate evaluations, assignments, branches, no-ops, or padding merely because those names appear in the ledger. Future generated source must not evaluate unused `R/S` predicates for that reason. A REFERENCE_ONLY certificate would not waive the independent scientific-source veto. A genuinely conflicting independent frozen requirement, if identified during review, must be resolved prospectively; no `R/S` term may be silently added to these functions.

## 3. PREFIX: normative mathematical specification

Let the deterministic ordered domain be `x_1, x_2, ..., x_m`. Define `P_i ∈ {0,1}` and `Q_i ∈ {0,1}` as the truth indicators of the frozen `P` and `Q` predicates at the corresponding item. Predicate definitions, input dependence, and original index semantics remain those of the slot ledger.

The selected function is:

```text
prefix_pair(P,Q) = Σ_{i=1..m} [ Q_i * (Σ_{j=1..i-1} P_j) ]
```

Equivalently, it counts ordered index pairs `(j,i)` with `j < i`, `P_j = 1`, and `Q_i = 1`. Both the ordered-pair definition and the following running-state definition are normative descriptions of **the same function**.

### 3.1 Domain order

- **numeric_iteration:** visit the frozen numeric domain in increasing iteration/index order, `1, 2, ..., n`; hence `m=n`. At `n=0` there are no items. In particular, the divisor predicate is never evaluated at numeric index zero.
- **array_reduction:** visit the four array elements in frozen input order, at original zero-based indices `0,1,2,3`; hence `m=4`. The mathematical ordinal `i=1..4` names position in the sequence; the ledger's index-dependent predicate still uses the original array index `i-1`. This notation does not change `value_exceeds_index` or introduce one-based array indexing.

There is no sorting, reverse traversal, alternative item order, or family-specific PREFIX variant. Frozen training-slot loop orientations remain independently unchanged; this section fixes the structural-transfer function's traversal.

### 3.2 Initialization and item semantics

Before the first item:

```text
prior_p_count = 0
result = 0
```

At ordered item `i`:

1. Evaluate `P_i`.
2. Evaluate `Q_i`.
3. Add `prior_p_count * Q_i` to `result`.
4. Then set `prior_p_count = prior_p_count + P_i`.

The semantic requirement is **strict-prior observation**. The contribution must use the P count from before the current item. Evaluation order of the pure `P/Q` predicates themselves may vary only if it preserves this mathematical function and every frozen source/graph requirement; this is not permission to change a protected scaffold, decoder, index, or evaluation dependency.

If both predicates hold on the current item, that item's P does **not** contribute to that item's Q contribution. It becomes available to later Q items. `P/Q` role reversal is not generally a PREFIX equivalence.

### 3.3 Output, empty domain, and equivalence

Return/display exactly `result` after all domain items have been processed, using the retained integer output schema. Do not display the prior P count, the last contribution, an existence flag, an added offset, or an intermediate state. For an empty domain, the result is `0`. The empty-domain rule applies to valid numeric `n=0`; it does not expand the four-element array input schema to admit empty arrays.

An induction establishes equivalence without inspecting cases or constructing outputs: immediately before item `i`, `prior_p_count = Σ_{j=1..i-1} P_j`. The contribution is therefore precisely the inner count multiplied by `Q_i`; adding the current `P_i` establishes the invariant for the next item. Summing these contributions gives the closed form, and each counted prior P contributes exactly once for each later Q. The ordered-pair and running-state definitions coincide for every admissible input sequence.

The following interpretations are excluded: inclusive/current-item prefix; existence-only prior-P detection; last-contribution-only output; and arbitrary nonzero initialization of either state. This is an explicit mathematical selection, not a representation normalization of those alternatives.

## 4. TWO_PASS: normative mathematical specification

Using the same deterministic task domain and frozen predicate truth indicators:

```text
countP = Σ_{i=1..m} P_i
countQ = Σ_{i=1..m} Q_i
product_of_counts(P,Q) = countP * countQ
```

Both counts range over the **complete same task domain**. Both initialize to zero. Each true occurrence contributes exactly one to its respective count. Return/display exactly the integer product of the **completed** P and Q counts. An empty domain gives two zero counts and result zero; this does not admit an empty array input.

An item satisfying both predicates contributes one to each count. There is no strict-prior restriction in this function: the product includes all combinations of a P occurrence and a Q occurrence, including a same-item combination where both hold. It is not `Σ_i(P_i*Q_i)`, the sum of the two counts, or a running product of partial counts.

A canonical source realization **may** complete one P-count pass, complete a second Q-count pass over the same domain, and then multiply the completed counts. The frozen label `two_pass_product` preserves the named structural-transfer intent. Independent reading of the ledger, protocol §§4–6, V3.2/V3.7, disposition row 1.5, paired/input-domain authorities, and subordinate delegated/RO interfaces found **no independent normative clause making exactly two literal source passes an additional scientific requirement**. The label alone is not used to invent one. This proposal defines the output function and its aggregate-state meaning; it neither freezes a source topology nor authorizes collapsing or choosing a canonical graph. Later reviewed canonical source/graph binding must record its topology and respect all independently frozen requirements. If review identifies an applicable stronger topology clause, cite and resolve it before binding rather than treating this paragraph as a waiver.

Multiplication of completed counts is commutative: swapping the final operands leaves the mathematical function unchanged. It does not change the slot's P/Q role assignments or license arbitrary source/graph rewriting. A later canonical graph ordering may be fixed representationally, subject to the closed V3.3 equivalences. No general program-equivalence rule is added here.

## 5. Family correspondence and prospective scientific rationale

The identical PREFIX law and identical TWO_PASS law apply to both `numeric_iteration` and `array_reduction`. Only domain traversal, concrete frozen predicate definitions, and frozen P/Q slot-role assignments differ. Numeric predicates remain `i%2==1`, `i%3==2`, `n%i==0`, and `2*i<=n`; array predicates remain `values[i]<0`, `values[i]%2==0`, `values[i]*values[i]>4`, and `values[i]>i`, with their existing role maps. There is no domain-specific aggregation variant.

**PREFIX rationale:** strict-prior ordered-pair counting is selected to test stateful structural transfer across items. It maintains prior predicate state, is sensitive to sequence order in general, and composes an earlier P occurrence with a later Q occurrence. Its dependence on cross-item state distinguishes it from ordinary per-item Boolean composition and from global multiplication of counts. Order sensitivity describes the law; it is not a claim that every concrete slot or every input must distinguish every permutation. This is an exploratory test of transferring covered ingredients into a different data-flow arrangement, not a new primary hypothesis or success threshold.

**TWO_PASS rationale:** the product of complete predicate counts selects a different structural composition: independently aggregate each primitive predicate, complete the global counts, and perform later arithmetic composition of those aggregate states. That target differs from accumulating local per-item joint contributions and from the ordered restriction in PREFIX. The distinction concerns the mathematics and required state relationships; literal canonical pass layout remains a subsequent representation decision within the frozen intent.

These rationales are prospective and independent of what a current builder does. Removed v2 §4.3 counterfactual mechanics are not normative authority for either definition. Historical compatibility, if present, cannot fill the original authority gap or turn this amendment into semantic recovery. No scientific pass, learned capability, domain realizability, case adequacy, or treatment effectiveness is asserted.

## 6. Preservation and blast radius

Each requested item receives exactly one classification. A follow-on binding is not performed by this proposal and does not authorize scientific execution.

| Item | Classification | Determination |
|---|---|---|
| CONF1 research question | `UNCHANGED` | Same end-to-end independent-versus-joint practice question and primary estimand; structural transfer remains exploratory. |
| ISOLATED treatment | `UNCHANGED` | Existing independent per-item `hitP+hitQ` training semantics remain intact. |
| COMPOSITION treatment | `UNCHANGED` | Existing per-item `hitP*hitQ` training semantics remain intact. |
| Sole ADD-vs-MUL training contrast | `UNCHANGED` | No additional asymmetric relation, example, scaffold, or intervention exception. |
| Training paired-slot schedule | `UNCHANGED` | Same 60 paired slots, roles, orientations, offsets, case pairing and exposure schedule. |
| Predicate definitions | `UNCHANGED` | Exact frozen predicates and index meanings; no added R/S computation. |
| Primary G1–G4 mathematics | `UNCHANGED` | Ledger graphs retained verbatim: G1 `(P&Q)|(P&R)` counted once; G2 `(P&Q)+(Q&R)+(R&S)`; G3 `(P&Q)+(P&R)+(P&S)`; G4 `((P|Q)&R)+(Q&S)`. |
| 32 primary slots | `UNCHANGED` | Same IDs, domains, blocks and role maps; no substituted or new primary task. |
| 16 primitive-sanity slots | `UNCHANGED` | Same IDs and single-primitive functions. |
| 16 structural-transfer slot identities | `UNCHANGED` | Same IDs, families, groups, labels and rotations; §§2–4 newly bind their previously incomplete mathematics without changing identity. |
| Role rotations | `UNCHANGED` | Existing left rotations and complete metadata maps retained; mathematical dependencies use the frozen P/Q entries. |
| Training/evaluation counts | `UNCHANGED` | 60 training programs per condition, 120 total; evaluation 32 primary + 16 sanity + 16 transfer = 64; five cases per program/task. Ten seed-condition cells, 180 exposures and 24 steps per cell remain unchanged. |
| Seven-category ontology | `UNCHANGED` | Exactly the existing seven V3.2 categories; no structural-family macro becomes a new category or atomic capability. |
| Frozen EDGE vocabulary | `UNCHANGED` | Existing ten typed edge labels retained; no new edge type is proposed. Actual source/key mappings are deferred. |
| V3.3 equivalences | `UNCHANGED` | Same closed equivalences; mathematical operand symmetry is not unrestricted code/graph equivalence. |
| INPUT_DOMAIN | `UNCHANGED` | Same nonnegative numeric schema and fixed four signed array fields, sign/empty/boundary classes, and existing one-slot training override. |
| Candidate seed | `UNCHANGED` | Construction seed `20290123` retained; no new sampling or candidate stream. Training/evaluation RNG and resampling schedules are also retained. |
| Case pools | `UNCHANGED` | Existing pools, case counts, exclusions, secondary-input reuse and prospective construction rules retained. New structural outputs must later derive from this amendment, not historical outputs; none are constructed here. |
| Overlap rules | `UNCHANGED` | Same exact/task-case, consumed-source/template and AST-v2 prohibitions and disclosed numeric-zero exception; no normalization or reuse waiver. |
| E1 compiler/reference semantics | `CLARIFIED_BY_THIS_AMENDMENT` | E1's correctness gate, compiler identity and populations do not change; the missing correct structural target functions are now specified prospectively. Later implementations and expected outputs need fresh validation, with no inherited PASS. |
| V3.4 both-condition requirement | `UNCHANGED` | Every task-essential atomic ingredient, including exploratory structural transfer, still needs active same-domain coverage in both conditions. Symmetric absence fails. |
| V3.5 intervention meaning | `UNCHANGED` | Same closed capability-level intervention table, normal-event rule, all-mapped-instance quantification and witness order. Unresolved realization/mapping issues remain blocked follow-on work under §7. |
| V3.6 treatment exception | `UNCHANGED` | Only the marked pair-joint training relation is asymmetric; all underlying operators, primitives, state edges, decoding and output abilities remain governed by both-condition coverage. |
| V3.8 fail-closed behavior | `UNCHANGED` | Missing, incompatible, unrepresentable, or failed bindings/evidence stop; no waiver, task replacement, or outcome-based adjustment. |
| E5 full-signature novelty | `REQUIRES_FOLLOW_ON_REPRESENTATIONAL_BINDING` | Complete structural function/state descriptions must be expressible faithfully as explained in §8. The scientific collision criterion and actual primary-versus-training comparison population are unchanged. No schema or signature is built here. |

**Blast-radius totals: 25 items = 23 `UNCHANGED`, 1 `CLARIFIED_BY_THIS_AMENDMENT`, 1 `REQUIRES_FOLLOW_ON_REPRESENTATIONAL_BINDING`, 0 `WOULD_CHANGE_EXISTING_SCIENTIFIC_DESIGN`.**

The repair changes the prospective mathematical specification of the exploratory structural tasks. Future prompts, reference implementations, complete contracts/state descriptions, derived expected outputs and hashes must agree with it after review/freeze; old artifacts cannot acquire correctness by inference or compatibility. That scientific specification effect is explicit even though identities, counts and primary design are preserved. The confirmatory +20-point rule, interval/heterogeneity procedure, primitive-sanity interpretation and own-training acquisition gate remain owned by the original protocol, unchanged.

No necessary change to the primary contrast, ontology, main confirmatory endpoint or population identity follows from these definitions. If faithful follow-on binding proves to require any such change, **stop and obtain broader CONF1 re-preregistration**; this proposal grants no advance permission for it. A failure to expose an existing task-essential ingredient in both conditions is a failure under existing rules, not an invitation to alter training or exempt the exploratory suite.

## 7. V3.5 compatibility and unresolved follow-on bindings

The newly defined functions use concepts already present in V3.2: input/domain values and decoding (`API_DECODER`), the frozen predicates (`SEMANTIC_PRIMITIVE`), Boolean indicators and typed arithmetic (`ATOMIC_OPERATOR`), iteration/conditional choice where used (`GENERIC_CONSTRUCT`), accumulator states and directed dataflow (`ATOMIC_CONTROL_DATAFLOW`), initialization values (`VALUE_OR_LITERAL`), and the actual integer output (`OUTPUT_CATEGORY`). This is a conceptual compatibility account, not a new capability inventory or a graph recipe. Atomic keys must later be derived and mapped under frozen V3.1/V3.2, never named manually here.

For **PREFIX**, the essential relationships include a prior P-count state carried between items, a current Q-dependent contribution that reads that prior state, accumulation of those contributions, a subsequent P-count update, and the final displayed total. Existing relevant edge concepts include `PRIOR_STATE_TO_UPDATE`, `LOOP_CARRY`, `OPERATOR_TO_ACCUMULATOR`, and `ACCUMULATOR_TO_OUTPUT`; predicate-to-indicator/control and control-to-update concepts apply where the reviewed source realization uses them. The exact instantiated one-edge roles and mappings remain unresolved until a reviewed recipe binds them. The whole cross-item P→Q recurrence must not be invented as one multi-edge atomic key.

For **TWO_PASS**, the essential relationships include separate P and Q aggregations initialized to zero, completion of both counts over the same domain, consumption of those states by typed multiplication, and the resulting final output. Existing relevant concepts include predicate-to-indicator/control, `CONTROL_TO_UPDATE`, `OPERATOR_TO_ACCUMULATOR`, `LOOP_CARRY`, `PRIOR_STATE_TO_UPDATE`, `VALUE_TO_OPERATOR`, and `ACCUMULATOR_TO_OUTPUT` as applicable to the eventual realization. No completed-count-product macro, two-pass category, or new atomic edge is added. Listing available concepts does not demand every listed edge in every legal representation.

Later activity evidence must retain V3.5 exactly: a source-to-contract path executes and reaches the output; a frozen normal case has a nonzero contribution or selects a nonzero update; one of the fixed interventions changes the correct final output on such a case. Boolean predicate/operator/branch decisions are forced false then true; numeric operators/directed value edges are replaced at their destination by 0 then 1; accumulator-update edges have all mapped contributions suppressed. Decoder interventions and attribute inheritance retain their own frozen meanings. For each canonical key in an example, all mapped instances are intervened on together; witness selection retains the lexicographically first qualifying case and first intervention in the frozen order. There is no special mutation of the final item, per-occurrence test, or product-to-sum substitution resurrected from v2 §4.3.

V3.5 activity is evidence about canonical **training** examples and their keys. It does not by itself validate a structural-transfer function, prove learning, or make a complete recurrence an atomic training requirement. E1 later validates normal source/reference correctness; E6 later checks evaluation-behavior witnesses. V3.4 separately requires the structural task's genuinely essential atomic ingredients to be active in each training condition. There is no exemption for transfer and no permission to add source-only practice or unused R/S evaluations.

At specification level, neither selected function requires changing the frozen intervention meanings. **Unresolved follow-on issue:** establish exact typed source/state/key mappings and demonstrate that the existing intervention engine can act on them faithfully, retaining strict-prior read/update phase and completed-count consumption. No engine behavior, active witness, both-condition population, or feasibility PASS is established here. If a required key cannot be typed/executed, or its normal-event/changing-intervention evidence cannot be obtained under the frozen rules, record unresolved/failure and stop under V3.8. If a faithful test would require different scientific intervention semantics, that remains an unresolved scientific issue needing separate prospective review; this document does not silently repair V3.5 or label such a change representational.

## 8. E5 compatibility and complete-function representation

The prospective contract for a structural slot must describe its complete output function, not merely its P/Q truth values on one item. For PREFIX that includes zero initialization, the ordered strict-prior P state, the Q-dependent contribution, the post-contribution P update, accumulated total and final output. For TWO_PASS it includes both zero-initialized complete-domain counts and the final product of completed states. Original index/input dependencies and frozen role sharing must remain explicit.

A future complete function/state representation must preserve enough information to distinguish **strict-prior PREFIX**, **inclusive/current-item PREFIX**, **global product-of-counts**, and **ordinary per-item composition**. A per-item Boolean vector alone cannot certify equality of these aggregate functions. Read-before-current-P-update versus read-after-update, domain sequencing, separate count states, count completion, initialization and final output relation cannot be erased by an aggregator name, five-case agreement, a category tag, or generic operator overlap. This specifies the facts the representation must carry, not new case outputs, signature artifacts, schema fields or graph topology.

V3.7/E5 still prohibits either complete typed-graph isomorphism under its narrow normalizations **or** equality of completeness-certified semantic contribution/output functions under consistent role bijection. Unrepresented output-affecting state or undecidable comparison remains `UNRESOLVED` and FAIL. The existing novelty-specific normalization of a fixed initial offset is unchanged; it does not permit a nonzero PREFIX initialization under this amendment. Local pair motifs remain descriptive, not freshness vetoes. No new general equivalence or threshold is introduced.

The authoritative E5 comparison population remains **32 primary certificates, 120 training certificates and 32×120 = 3,840 primary-versus-training comparisons** under delegated-interface §14. Structural Transfer remains exploratory. Requiring accurate function/state descriptions for its contracts under V3.1/V3.2 does **not** add 16 structural-transfer novelty certificates or comparisons to E5, or turn exploratory transfer into a new primary novelty veto. Existing independent source/case overlap obligations remain intact.

**Follow-on representational binding:** independently review how the accepted mathematics is carried by the closed contract grammar, complete-state signature descriptions and source mappings. No schema/interface file is changed now. If the existing representation cannot express these facts faithfully, it fails closed until a separately reviewed representational amendment resolves it. If representation would instead require changing the scientific collision criterion or population, stop for the appropriate broader scientific review. This proposal establishes no novelty PASS.

## 9. Canonical graph recipe and execution boundary

**The canonical contract-graph recipe remains blocked until this amendment is independently reviewed and, if accepted, frozen.** No recipe is drafted or resumed by this task. A future recipe must derive PREFIX/TWO_PASS topology and complete state semantics from this amendment, subject to the retained frozen authorities, rather than treating historical implementation as their source. Literal layouts, canonical operand ordering, typed source/contract mappings, key identities, activity realization and representation/schema closure remain subsequent reviewed work. This document supplies mathematical laws, not that recipe.

This task constructs no candidates, cases, expected outputs, graphs, coverage populations, DIRECT-support artifacts or REFERENCE_ONLY artifacts. It implements nothing and runs no scientific E1–E6 producers, models, or holdout work. `PROJECT_STATE` and every existing authority, freeze file, development draft and historical artifact remain unchanged. No sealed holdout or expected-label semantics is inspected. A later freeze, if approved, will require a separately authorized task; this proposal commit itself authorizes no downstream scientific execution.

## 10. Self-review: complete introduced-choice classification

The following catalog accounts for all introduced mathematical selections and the limited presentation/deferral choices. Repeated descriptions and their rationale do not introduce additional independent rules. Preservation of an already-frozen rule is not a newly introduced choice. `REPRESENTATION_ONLY` below applies only to notation and deferred encoding decisions, never to a slot binding or recurrence; it does not describe the amendment as a whole.

| Choice | Introduced selection | Classification |
|---|---|---|
| C01 | Bind `prefix_running_pair(P,Q)` to the specified `prefix_pair(P,Q)`. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C02 | Bind `two_pass_product(P,Q)` to the specified `product_of_counts(P,Q)`. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C03 | Use the exact frozen P/Q assignments as mathematical arguments; retain unused R/S as metadata, without adding computation. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C04 | Interpret P/Q occurrences as 0/1 truth indicators of the unchanged frozen predicates. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C05 | Fix structural numeric traversal to increasing `1..n`. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C06 | Fix structural array traversal to input order with original zero-based predicate indices. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C07 | Initialize PREFIX prior-P count and result to zero. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C08 | Select the strict-prior nested sum and its equivalent ordered-pair law. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C09 | Read prior P state for the Q contribution, then update it with current P; qualify P/Q evaluation-order freedom by function and frozen requirements. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C10 | Exclude same-item P from that item's Q contribution, while allowing it for later Q. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C11 | Output the completed PREFIX accumulated result exactly. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C12 | Define empty-domain PREFIX as zero without expanding array validity. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C13 | Exclude inclusive, existence-only, last-contribution and nonzero-initial-state PREFIX alternatives. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C14 | Define two independent complete same-domain counts, zero initialized, one per true occurrence. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C15 | Output the product of completed counts, including same-item combinations and empty-domain zero; exclude per-item product/sum/partial-count alternatives. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C16 | Recognize completed-count operand commutativity at the mathematical level without adding source equivalences or role changes. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C17 | Apply each law uniformly to both families, with only frozen domains, predicates and P/Q assignments differing. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C18 | Define aggregate-state mathematics without inventing an additional literal two-pass scientific requirement from the label. | `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR` |
| C19 | Use local mathematical ordinals/state names as descriptive notation; impose no new GOCO identifier or literal-token spelling requirement. | `REPRESENTATION_ONLY` |
| C20 | Defer canonical source/graph ordering and exact V3.5 typed source/state/key binding, retaining existing ontology and intervention meanings. No such binding is made here. | `REPRESENTATION_ONLY` |
| C21 | Defer faithful complete function/state encoding for contracts and signature descriptions, retaining E5's scientific criterion and primary comparison population. No schema is changed here. | `REPRESENTATION_ONLY` |

**Complete choice counts: 21 total = 18 `PROSPECTIVE_MATHEMATICAL_SPECIFICATION_REPAIR`, 3 `REPRESENTATION_ONLY`, 0 `TREATMENT_OR_ONTOLOGY_CHANGE`.**

Self-review findings: both functions have complete domain, predicate, initialization, aggregation/state, overlap and final-output meanings; the PREFIX closed form and recurrence agree; slot/family bindings are explicitly prospective; unchanged R/S metadata does not create dead source; mathematical count-product symmetry is separate from canonical topology; no new atomic category/key, source equivalence, training manipulation, primary endpoint or population is introduced; V3.5 and E5 retain their scientific meanings, with faithful implementation/representation still unresolved follow-on work. No coverage, activity, compiler, case, novelty, model or scientific PASS is asserted.

The single internal outcome is:

`STRUCTURAL_TRANSFER_AMENDMENT_PROPOSAL_COMPLETE_WITHOUT_PRIMARY_TREATMENT_OR_ONTOLOGY_CHANGE`

This outcome certifies completeness of the proposal for independent review, not approval, freeze, implementation readiness, scientific feasibility or execution permission. Any subsequent descriptive implementation comparison is outside these prospective selections and cannot revise them.

## 11. Subsequent read-only historical implementation comparison

Sections 1–10 were completely written and self-reviewed before implementation inspection. Their exact UTF-8/LF bytes were recorded as a 36,321-byte prefix with SHA-256 `a0c99b79001c1a37163d1ff4b06d4518891dca8c12518dc4a3d276b3de5658ac`. That prefix is retained unchanged when this descriptive appendix is added. The comparison did not select, revise or supply authority for any proposed definition. This prefix identity is an ordering/preservation record, not a freeze manifest or independent approval.

The current implementation was inspected as source text at operational HEAD `c6c8a32fdc09c0ea5193ddbf68ecee7ac388483b`. No module was imported, helper called, source generated, input evaluated, expected output constructed, compiler invoked, scientific test run, or implementation changed.

| Function | Separate descriptive compatibility result | Static evidence |
|---|---|---|
| PREFIX | **MATCHES the proposed mathematical behavior for the frozen structural slot labels.** | `scripts/build_phase3c_conf1_data.py` `structural_source` lines 132–137 initializes `seen=0` and `total=0`, adds `seen` on a Q item before incrementing it on a P item, and displays `total`. `structural_expected` lines 144–157 uses the same strict-prior recurrence and returns its completed total. Its Q-before-P predicate evaluation is compatible with §3's qualified evaluation-order freedom. Same-item overlap is excluded from its own Q contribution; zero items retain zero. |
| TWO_PASS | **MATCHES the proposed mathematical behavior for the frozen structural slot labels.** | The same builder's lines 138–141 initialize separate zero counts, complete a P pass and a Q pass, then display their product. Lines 149–150 compute the product of complete P/Q counts in the reference helper. This is the two-pass source realization permitted by §4, not evidence of an independently frozen literal-pass requirement. |

For both rows, lines 133–134 select only the frozen P/Q role entries for generated structural source, and lines 215–218 describe the same functions in prompts. `loop` lines 54–61 uses numeric `1..n` and array `0..3` forward traversal when called by `structural_source`. `scripts/design_phase3c_conf1.py` lines 48–59 supplies the same ordered items and original predicate indices to the reference helper. That helper constructs full primitive truth tuples internally and then selects P/Q; this does not add R/S dependence to either output function, and the generated structural GOCO source evaluates only P/Q. No candidate source or case artifact was generated to make this comparison.

Builder identity: committed Git blob `7f4ffd3d3efff00af610fdc2edcae0df50a83696`; inspected working-file exact SHA-256 `bfbd0f7d4b9b981e38097fca4e7e14f40107f530f9a315f6118ae0a8dc5cb124`, size 14,550 bytes. The working-file CRLF representation and committed text normalization are identified separately; neither is a scientific authority for these laws.

Additional descriptive cross-checks: the unmutated paths of legacy `scripts/phase3c_conf1_coverage_v2.py` lines 159–182 also use strict-prior PREFIX and the product of complete counts. Its optional historical mutation paths remain abandoned mechanics, not adopted interventions. Current `src/self_learning_ai/conf1_v3/contract_ir.py` lines 113–118 retains only P/Q as structural dependencies and describes the same zero-initialized PREFIX recurrence/order and count product; it obtains source templates from the historical builder. Current development `state_semantics.py` lines 171–190 requires a particular two-loop/pass-order layout and prior-state mapping for its declared development forms. Those implementation checks are descriptive layout constraints, not newly recovered scientific topology authority. No development form, atomic key, signature, mapping, RO file or readiness result is promoted by agreement.

These are bounded **static compatibility observations**, not execution results or proof that the broader implementation conforms to frozen methodology. Invalid-label handling, compiler legality, exact outputs on future cases, source/contract completeness, interventions, activity witnesses, both-condition coverage, canonical graph/schema binding and E1–E6 all remain unestablished by this comparison. No mathematical mismatch was found in the inspected normal structural builder paths; no implementation fix was made. Independent review of this prospective amendment and any accepted freeze still precede the blocked canonical graph recipe and all separately authorized downstream work.
