# Coverage-v2 to proposed-v3 clause disposition

This is a prospective scientific disposition, not an amendment to frozen coverage v2. The v2 clause IDs and short descriptions are those in `coverage_v2_rule_conformance_matrix.json`. Each row has exactly one primary disposition. A retained *scientific invariant* may be expressed differently in v3; the rationale identifies any removed mechanics. Delegated controls must satisfy the hash-bound evidence contracts E1–E6 in `phase3c_conf1_coverage_v3_proposed.md` before a candidate can pass.

| V2 ID | V2 short description | Primary disposition | Scientific rationale |
|---|---|---|---|
| 1.1 | Closed required contract fields and unknown-key failure | `RETAINED_IN_V3_RULE_V3.1` | Missing/unknown claims could otherwise silently create coverage. |
| 1.2 | Contract derived by prospective builder from immutable slot grammar | `RETAINED_IN_V3_RULE_V3.1` | Prevents manually chosen task-essential claims after source/case inspection. |
| 1.3 | Numeric and four-signed-value array input interpretation | `RETAINED_IN_V3_RULE_V3.2` | The domain decoder and value types are needed for API/value coverage. |
| 1.4 | Typed expression grammar and closed operations | `RETAINED_IN_V3_RULE_V3.2` | Unknown or ill-typed operations must not be converted to known capability keys. |
| 1.5 | sum_per_item, prefix_pair, product_of_counts aggregators | `RETAINED_IN_V3_RULE_V3.2` | Aggregation changes the atomic edges and complete target signature. |
| 1.6 | Five case contract/source/compiler exact agreement | `DELEGATED_TO_E1_COMPILER_REFERENCE` | E1 owns normal source/case agreement; v3 binds the contract/source graph and consumes E1 by hash. A second compiler run is not a new fairness fact. |
| 1.7 | Same extraction for training/evaluation, no task-ID branches | `RETAINED_IN_V3_RULE_V3.3` | Distinct rules by condition or ID could manufacture symmetry. |
| 2.1 | Closed ontology and explicit source-only classification | `RETAINED_IN_V3_RULE_V3.2` | Unknown source/contract requirements fail closed. |
| 2.2 | Semantic predicate key and active same-domain training evidence | `RETAINED_IN_V3_RULE_V3.4` | Each evaluation predicate needs active evidence in both conditions. |
| 2.3 | Input, bounded loop, conditional choice, update, output, array index construct keys | `RETAINED_IN_V3_RULE_V3.2` | Generic constructs are atomic typed nodes/edges; exact higher-order branch layout is excluded. |
| 2.4 | Exact API role, connected decoder and distinct-input witness | `RETAINED_IN_V3_RULE_V3.5` | The connected domain decoder and capability-level output event block dead API tokens; a prescribed *pair of distinct inputs* is not independently required if the fixed counterfactual proves activity. |
| 2.5 | Typed operators and sole pair-joint treatment exception | `RETAINED_IN_V3_RULE_V3.6` | Atomic operators remain symmetric; only the declared pair relation differs. |
| 2.6 | Literal lexeme distinct from computed value and output category | `RETAINED_IN_V3_RULE_V3.5` | Exact syntax, value computation, input domain and observed output are separate keys. |
| 2.7 | Independent/dependent/nested branch relation is source-backed | `REMOVED_AS_OVERREACH` | Exact ordered multi-branch topology can be the withheld primary graph. V3.2 retains generic choice and atomic branch/dataflow edges; E5 prohibits full graph training. |
| 2.8 | Typed atomic dataflow edges retain paths/multiplicity | `RETAINED_IN_V3_RULE_V3.2` | One-edge typed abilities remain symmetric. Complete-path multiplicity is retained in E5's full graph, not demanded as an atomic training template. |
| 2.9 | Full vector plus typed graph/signature | `DELEGATED_TO_E5_FULL_SIGNATURE_NOVELTY` | One authoritative comparison owns the complete graph/vector and blocks leakage; coverage must not reconstruct a weaker version. |
| 2.10 | Declared and observed output categories and exact sentinel cases | `RETAINED_IN_V3_RULE_V3.5` | A required negative or exact output must be witnessed in both conditions. |
| 3.1 | Consistent identifier alpha-renaming | `RETAINED_IN_V3_RULE_V3.3` | Incidental names cannot decide fairness or novelty. |
| 3.2 | Pure integer constant-tree folding | `RETAINED_IN_V3_RULE_V3.3` | Exact computed-value equivalence is narrow and reproducible; it never supplies an exact literal lexeme. |
| 3.3 | Commutative pure child sorting with duplicate multiplicity | `RETAINED_IN_V3_RULE_V3.3` | Sorting avoids false novelty under operand swaps; duplicate relationships remain in E5. |
| 3.4 | Boolean and versus 0/1 indicator multiplication local-pair equivalence | `RETAINED_IN_V3_RULE_V3.3` | The bounded, type-proven local pair relation is equivalent; no untyped or full-graph rewrite is allowed. |
| 3.5 | Boolean or versus indicator(add(a,b)>0) equivalence | `RETAINED_IN_V3_RULE_V3.3` | Retained only when both inputs and result are proven Boolean/indicator; otherwise unresolved. |
| 3.6 | Comparison direction swap and symmetric equality | `RETAINED_IN_V3_RULE_V3.3` | Narrow semantic normalization prevents incidental syntax from blocking correct coverage. |
| 3.7 | No other algebraic rewrite | `RETAINED_IN_V3_RULE_V3.3` | Unsound additional rewrites could falsely cover a key or conceal a full target. |
| 3.8 | 2^k truth vector, k<=4, role edges/shared predicates | `DELEGATED_TO_E5_FULL_SIGNATURE_NOVELTY` | E5 must preserve role sharing, multiplicity and complete contribution semantics. |
| 3.9 | Report local pair motifs without treating them as freshness failure | `DIAGNOSTIC_ONLY` | D1 reports motif prevalence; E5 blocks only complete target reuse. Motif count is not an extra PASS threshold. |
| 3.10 | Pair-joint sole exception, components covered in both conditions | `RETAINED_IN_V3_RULE_V3.6` | Treatment cannot excuse a missing primitive/operator/API/output/atomic edge. |
| 4.1 | Counterfactual table for every semantic node, lexicographic first witness | `RETAINED_IN_V3_RULE_V3.5` | The *activity safeguard* remains, but the per-node intervention and first/final-item mechanics are replaced by frozen capability-level intervention with a normal output event. |
| 4.2 | Each repeated predicate occurrence mutated separately | `REMOVED_AS_OVERREACH` | Capability exposure needs one active instance in an example, not every repeated occurrence. E5 still retains repeated-use identity for full-graph novelty. |
| 4.3 | Three aggregator counterfactual forms | `REMOVED_AS_OVERREACH` | Suppressing a particular final item can miss an otherwise active aggregator. V3.5 tests the declared aggregation capability as a whole; E5 retains aggregator topology. |
| 4.4 | Each control/dataflow key inherits exact source-backed edge witness/path | `IMPLEMENTATION_DETAIL` | V3.5 requires source mapping, output event and recorded witness; a particular path serialization is not another scientific gate. |
| 4.5 | Pinned GOCO compilation and exact case agreement | `DELEGATED_TO_E1_COMPILER_REFERENCE` | The existing compiler/reference validation owns this fact and is consumed with matching hashes. |
| 4.6 | Parsed numeric input-loop bound/output dependency | `RETAINED_IN_V3_RULE_V3.2` | Numeric INPUT must connect to bounded task computation, not merely appear in source. |
| 4.7 | Parsed array input/SPLIT/conversions/index/predicate/output dependency | `RETAINED_IN_V3_RULE_V3.2` | A disconnected conversion cannot supply API/domain capability. |
| 4.8 | Inventory each GOCO token-tree occurrence with offset and classification | `IMPLEMENTATION_DETAIL` | A closed parsed source/contract mapping and fail-closed unmatched constructs are gating. Every token offset is evidence formatting; AST-v2 supplies reusable lexical machinery. |
| 4.9 | Source occurrence backs essential key only with matching active contract path | `RETAINED_IN_V3_RULE_V3.5` | A dead or unrelated source occurrence cannot supply coverage. |
| 4.10 | Unmatched source requires valid proof or fail closed | `RETAINED_IN_V3_RULE_V3.8` | Unproved extras cannot be silently treated as harmless. |
| 5.1 | Only active contract/domain/output requirements are TASK_ESSENTIAL | `RETAINED_IN_V3_RULE_V3.2` | Extra source syntax supplies no task-essential key or training evidence. |
| 5.2 | Incidental names/grouping/formatting reference-only | `RETAINED_IN_V3_RULE_V3.3` | Closed alpha/grouping normalization keeps incidental spelling out of capability matching. |
| 5.3 | Nontrivial extra construct proof: rewrite, alternative reference, finite-domain or closed identity | `REMOVED_AS_OVERREACH` | V3.2 permits only closed mechanical trivial proofs and otherwise fails. Arbitrary alternative-reference/finite-domain proof routes are unnecessary to accept a fair suite. |
| 6.1 | Both-condition same-domain source-backed active coverage | `RETAINED_IN_V3_RULE_V3.4` | This is the core atomic fairness comparison. |
| 6.2 | Treatment exception does not waive atomic/operator/control/output capabilities | `RETAINED_IN_V3_RULE_V3.6` | The one asymmetric relation cannot conceal another missing ingredient. |
| 6.3 | Primary full signature absent in both conditions even with other failures | `DELEGATED_TO_E5_FULL_SIGNATURE_NOVELTY` | E5 compares both training sets independently of their other failures and emits a prohibition reason. |
| 6.4 | Every independent violation emitted, no reason short-circuit | `DIAGNOSTIC_ONLY` | Complete reasons aid independent review, but their ordering is not a separate fairness threshold. V3.8 still fails on every detected violation. |
| 6.5 | Report each requirement, condition evidence, category totals/reasons | `DIAGNOSTIC_ONLY` | D3–D5 retain inspectable evidence; counts/order do not independently veto an otherwise verified comparison. Missing evidence needed for V3.4 is a V3.8 failure. |
| 6.6 | No thresholds, manual waivers or post-candidate reclassification | `RETAINED_IN_V3_RULE_V3.8` | Prevents outcome- or candidate-dependent relaxation. |

**Disposition check:** 46/46 v2 clauses have an explicit primary disposition. No existing rule, fixture or result is modified by this map.
