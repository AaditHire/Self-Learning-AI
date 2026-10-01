# Proposed CONF1 REFERENCE_ONLY closed-catalog clarification

Status: PROPOSAL FOR INDEPENDENT REVIEW ONLY. NOT APPROVED. NOT FROZEN.
Specification version: `RO-CATALOG-PROPOSED-1`, authored 2026-10-01.

Starting repository HEAD: `24217d2bb69fd99a467a742f10336a74bcf9317e`,
branch `main`, clean worktree verified before drafting. This document is the
only permitted repository addition. It changes no implementation, test,
evidence, existing protocol, freeze manifest, implementation gate, or project
state. It is not a certificate or a report of executed threat tests.

## 1. Prospective status, authority, and scope

This clarification is authored before Attempt 004. Under the current recorded
research boundary, no active CONF1 candidate exists and no CONF1 model result
exists. Historical rejected Attempts 001–003 remain rejected; this proposal
neither reclassifies nor repairs them. No candidate or model outcome selected
these rules. The preceding DEVELOPMENT_ONLY, non-executing diagnostic of a
disconnected `1877 % 0` motivated the safety question; it did not supply an
admissibility rule or scientific finding.

Independent review must precede approval, and approval must precede a separate
prospective freeze binding the reviewed document. Only after that freeze and
separate implementation authorization may REFERENCE_ONLY implementation
resume. Drafting or committing this file does not authorize a freeze,
implementation, fixtures, candidates, population derivation, E1–E6 execution,
provenance/binder work, preregistration, model use, or sealed-holdout access.
Any subsequent catalog extension or change requires another prospective version
and independent review before use; no post-candidate waiver is allowed.

### 1.1 Authorities consulted and precedence

The following existing files and their current frozen identities remain
unchanged. Section references below identify the controlling constraints,
not a claim that this new catalog is already contained in those files.

| Reference | Existing authority and relevant sections |
| --- | --- |
| A1 | `phase3c_conf1_coverage_v3_proposed.md`: V3.1–V3.8; literal/computed/input/output rules; delegated E1/E3/E5; reference-only threat example and dead-code-gaming self-review. Bound by `phase3c_conf1_coverage_v3_freeze.json`. |
| A2 | `phase3c_conf1_coverage_v3_v2_disposition.md`: clauses 2.1, 3.1–3.7, 4.8–4.10, 5.1–5.3, 6.6. In particular 5.3 is `REMOVED_AS_OVERREACH`. |
| A3 | `phase3c_conf1_delegated_evidence_interfaces_proposed.md`: §§1–2, 4.1, 6–7, 9 including 9.1.1–9.1.4, 10, 11–12, 14. Bound by its existing freeze manifest. |
| A4 | `phase3c_conf1_proposed_protocol.md`: §§3, 5–8, 12. The training scaffold and dead-code/padding prohibitions remain controlling. |
| A5 | `phase3c_conf1_paired_scaffold_normalization_proposed.md`: scope/precedence, closed comparison rule, protected fields, output/parity, threat examples. Bound by its existing freeze manifest. |
| A6 | `phase3c_conf1_input_domain_case_classes_and_training_amendment_proposed.md`: authority/scope, numeric and array domain definitions, sampling-versus-domain distinction, V3.5 activity, sole prospective training-case override. Bound by its existing freeze manifest. |
| A7 | `phase3c_conf1_slots.json`: predicate definitions, relational/aggregation semantics, slot grammar and `candidate_policy`, especially `no_semantically_dead_code: true`. |
| A8 | `phase3c_conf1_ast_adjudication_v2.md`: complete source-order token tree; retained control/API/state structure; no dead-code removal or algebraic rewriting in overlap adjudication. |

Read-only integrity checks at the starting HEAD verified all ten upstream
authority files, all four approved normative regions, and all fifteen protected
preregistration files. Expected labels were read only as opaque integrity
bytes, never parsed. No sealed holdout was accessed. No scientific fixture was
parsed for this proposal or executed.

Execution semantics were inspected from the pinned compiler source, not the
sibling checkout's current HEAD: upstream commit
`6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`, Java source tree
`415215892c7127df899d59b3bceb99dc8357484b`, as bound by
`research/manifests/goco_compiler_source.json` and A3 §6. The deterministic JAR
identity remains SHA-256
`42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`.
Relevant pinned files are `parser/MyLanguageParser.jj`,
`ast/nodes/ExpressionNodes.java`, `DeclarationNodes.java`,
`ConditionalNodes.java`, `IONodes.java`, `ast/strings/StringsLibrary.java`,
`ast/arrays/ArrayAccessNodes.java`, and `utils/Debug.java` below
`goco-compiler/src/main/java/`. The existing local closed-parser/type
representation and compiler wrapper were inspected only to identify subset and
execution boundaries; their current behavior is not scientific authority.
The compiler, interpreter, fixtures, and models were not run.

### 1.2 Why clarification is necessary

A1 V3.2 names incidental spelling/grouping and a closed set of pure,
demonstrably unused or constant-false extras with mechanical proofs; it does
not enumerate that set, guard grammar, evaluation-safety obligations, or
certificate representation. A1's self-review expressly rejects contrived
branches outside the closed catalog. A2 5.3 removes broader
alternative-reference/finite-domain/general identity proof routes. A3 §9
requires complete mapping plus proved reference-only constructs, but supplies
no missing semantic catalog. Reachability flags or sampled output equality
cannot fill that authority gap.

This proposal makes a new, intentionally restrictive prospective choice within
the two named semantic classes. It is not a retroactive interpretation that
the exact choices below were previously frozen. If review finds these choices
incompatible with an existing gate, the proposal must change before approval;
implementation cannot resolve the conflict itself.

### 1.3 No additional top-level semantic class; no candidate permission

The only proposed REFERENCE_ONLY semantic classes are `PURE_UNUSED` and
`CONSTANT_FALSE`. A1/A2 independently name incidental identifier spelling,
formatting and ordinary expression grouping; these are existing presentation
normalizations under V3.3, not a third permission to ignore semantic nodes.
Their binding/parse associations remain recorded. No array length, delimiter,
API identity, literal obligation, or control structure is incidental merely
because its text can be normalized in another audit.

A reference-only disposition resolves only a V3.2 source-accounting question.
It does not make a candidate acceptable. In particular, A7's
`no_semantically_dead_code` and A4 §§3/6/12 dead-guard, unreachable-code,
no-op and padding prohibitions remain independent vetoes wherever applicable.
An extra that obtains a valid catalog certificate can still make a scientific
candidate FAIL under those rules, even when present symmetrically. No catalog
rule authorizes adding dead code to a scientific training target or evaluation
reference. Such an exception would require a different reviewed amendment;
none is proposed here.

## 2. Safety principle and mandatory preconditions

Ignoring an extra means excluding it from required-capability evidence only
after proving semantic inertness. It never means deleting it from the actual
source, target, raw AST, graph, overlap/scaffold/token audit, or source hash.
The hypothetical removal argument is an internal proof about execution
semantics, not a new rewritten source, alternative reference, equivalence
normalization, or compiler-agreement route.

All admission rules require:

1. The complete original source passes the frozen language/subset, binding,
   type, domain, statement-placement and schema restrictions. Unknown syntax,
   unsupported forms and compiler-invalid bodies fail even if unreachable.
2. The unchanged prospective contract and its required computation are
   independently reconstructed before dispositions. The proposed members
   satisfy no required canonical occurrence, required multiplicity,
   authorized-equivalence realization/internal obligation, required
   state/control/dataflow, value/literal attachment, initial-state evidence,
   ACTIVE behavioral parent, or output obligation. Incomplete lookup is
   UNRESOLVED, not absence.
3. Complete typed dataflow, sequential and may-reaching definitions, branch
   joins, loop-carry/cross-pass state, control dependencies, output ancestry,
   and domain-decoder dependencies are represented. Merely failing to find a
   direct display use is not proof.
4. The extra cannot alter required computation, live/required state, control,
   dataflow, decoder/API behavior, output sequence/value, language-level
   termination or language-level execution-error behavior. Its evaluation
   has no input/output, library, array-registry, or other observable side
   effect. Distinct unused local storage is permitted only by §4.
5. Existing independently verified mapping/state/activity/attribute evidence,
   where applicable, must agree. An ACTIVE occurrence cannot be reference-only.
   A required case-INACTIVE or essentiality-UNRESOLVED occurrence stays
   required. Lack of an ACTIVE witness does not prove non-requirement.
6. Full accounting and exact identities close under §§6–8. Output equality,
   a caller flag, five false cases, a nearest source span, another program,
   loop, pass, or occurrence cannot discharge a precondition.

The claim is preservation of the frozen semantic computation and its observable
language behavior, not identical wall-clock cost, target length, or compiler
internal bookkeeping. Physical timeout, output/resource limits, stack/heap
failure, unexpected diagnostics, or incomplete runtime/compiler semantics
cannot be waived as reference-only: retain the failure and FAIL/UNRESOLVED
under the existing execution/identity gates. Finite constant-tree reasoning
does not prove a resource-limited E1 run succeeds. The original unmodified
source still needs E1 and all budget/scaffold audits; no limit is relaxed and
no universal resource-success claim is made for an unbounded input domain.

## 3. Closed constant proof kernel

The following is the entire proposed constant grammar. It describes parsed
trees, not regex replacements. Parentheses may wrap an admitted expression
only as ordinary grouping with the same parsed children/order; raw grouping
and lexemes remain retained. No reassociation or arbitrary simplification is
performed.

```text
N ::= ASCII decimal token "0" | [1-9][0-9]{0,9}
C ::= N | GROUP(C) | NEG(C) | ADD(C,C) | SUB(C,C) | MUL(C,C)
G ::= GROUP(G) | CMP(C,C)
CMP ::= EQ | NE | LT | LE | GT | GE
```

Every `N` must denote an integer between 0 and 2147483647 inclusive.
Every intermediate `C` value, including operands and unary negation, must be
an exact integer in `[-2147483647, 2147483647]`. The checker evaluates every
node in original evaluation order and checks this bound at every node, not
only at the root. Leading-zero, signed-token, decimal, exponent, non-ASCII,
NaN/infinite and out-of-range spellings have no admission path in this
catalog; a negative value uses the admitted unary NEG tree. This restriction
is local to reference-only safety proofs, not a change to required literal or
computed-value coverage rules or the scientific input domain.

`RO.SAFE.BOUNDED_INTEGER_CONSTANT_TREE` is the sole supporting numeric proof
rule. Its proof retains the full tree, raw lexemes/locations, node types,
ordered child references, exact per-node integers, and per-node range checks.
No identifier, state read, input, call, array, indexing, modulo, division,
power, cast, assignment expression, Boolean coercion or other operation is
allowed. Even total nonconstant arithmetic and even constant nonzero modulo
are outside this deliberately small catalog.

The pinned compiler uses `Double.parseDouble` and binary64 arithmetic for
numeric operations; it does not implement arbitrary mathematical integers.
The selected bound makes each admitted operand/result exactly representable
and finite under that execution path. Numeric equality in the pinned
`BinaryOperationNode.execute` uses a 0.000001 tolerance. For distinct admitted
integers the difference has magnitude at least one, so this comparison agrees
with exact integer equality; no arbitrary real-number equality is inferred.
Each proof must bind the actual compiler identity and confirm this semantic
agreement, not silently use a different interpreter's integer arithmetic.
The pinned debug logging switch is disabled; a build/configuration that makes
extra declaration/evaluation logging observable cannot inherit this proof.

For `G`, type every comparison as two INTEGER operands and a BOOLEAN result,
evaluate both complete `C` operands safely, and apply exactly the named
comparison. The root must equal false. There are no Boolean connective or NOT
rules, no identifier substitution, no propagation from sampled state, no
algebraic identity, and no domain-contradiction solver. The pinned compiler
eagerly evaluates both Boolean operands; no false left operand may excuse an
unsafe right operand. A guard such as a false comparison combined with
`1877 % 0` has no proof path.

The three exact proof rule IDs in this proposal are:

| Rule ID | Function |
| --- | --- |
| `RO.SAFE.BOUNDED_INTEGER_CONSTANT_TREE` | Supporting typed constant-safety proof; cannot itself assign a disposition. |
| `RO.PU.TOP_LEVEL_CONSTANT_DECL` | Sole `PURE_UNUSED` admission rule, §4. |
| `RO.CF.CONSTANT_COMPARISON_IF` | Sole `CONSTANT_FALSE` admission rule, §5. |

These are finite grammar productions/rules, not a finite list of permitted
numeric values or example IDs. No catch-all harmlessness rule exists.

## 4. PURE_UNUSED: one fresh top-level constant declaration

The sole admitted root form is `NUMBER fresh = C.` as an initialized scalar
declaration at the program's outer statement-list level. Ordinary accepted
spacing/grouping is permitted. It is outside every IF/loop and creates one
new, unaliased, nonshadowing binding. Its initializer passes §3. It is not a
required initialization, accumulator, index, indicator, input/domain value,
decoder field, or displayed binding. Scope/type validation must succeed and
binding identity, not its chosen name, establishes freshness.

The full source must contain exactly this one writer/declaration of the
binding and no other read, target write, address/array use, or lexical/binding
dependency on it, including unreachable regions and later passes. Global
freshness includes all scopes; removal cannot enable a redeclaration, change
another identifier's binding, or resolve/hide a compile-time ambiguity.
Standalone assignment, default/uninitialized declaration, multiple writers,
compound update and assignment chains are excluded, even if a more general
analysis could prove them harmless. The declaration is the only unused
write allowed by this rule. A fresh local subsequently assigned a safe
constant still fails this v1 rule rather than receiving a discretionary
exception.

Own exactly the declaration's semantic node, its complete constant-expression
nodes, and internal expression/initializer edges. Preserve all raw syntax
associations. There must be no path from these members to required or live
computation, output, state, control, or decoder behavior in the complete
typed/control/state graph; no may-reaching read or ambiguous writer union may
depend on the binding. No external incident edge may be suppressed to obtain
this result. If such an edge exists and cannot be justified within the complete
inventory, admission fails.

Evaluation is a finite, input-independent, bounded exact-integer expression
and one unobserved fresh scalar store. It performs no observable input/output,
library/array allocation, state enumeration, control transfer or live write.
It cannot introduce a language-level divide/modulo-by-zero, conversion,
unbound-read, indexing, overflow/nonfinite, or type error. `1877 % 0` MUST FAIL
this rule even when structurally disconnected from the output; its executed
evaluation raises a pinned-compiler runtime error. No output-path proof can
repair it. Other partial or unsupported expressions fail similarly.

An unused assignment/declaration inside a required loop, an unused IF, an
unused loop, loop-carried/cross-pass local storage, an overwrite of required
state, and an ambiguous indicator scaffold are all excluded from PURE_UNUSED.
INPUT, SPLIT, TO_NUMBER, array indexing and all other API operations are
excluded, even if their values appear disconnected or all known inputs are
valid. INPUT consumes stdin/emits a prompt; SPLIT allocates/registers array
state; conversions/indexing can fail. No global API-purity assumption is made.

## 5. CONSTANT_FALSE: one statically false IF region

### 5.1 Guard and universal domain proof

The sole admitted region root is an IF with no ELSE/ELSEIF/alternate arm,
whose complete guard is `G` from §3 and statically evaluates to false.
Record the exact parsed guard and both typed constant trees; sampled
executions are not proof premises. The region may occur at top level or in
an already valid, independently mapped enclosing IF/loop, but never as a
replacement for a required branch, loop, update, or traversal obligation.

The proof quantifies over every admissible input and every state reaching
that exact occurrence under the prospectively bound frozen domain:
numeric `n` is a nonnegative integer with no declared finite upper bound;
array inputs are exactly four signed integer fields with no declared finite
numeric bound. Construction/sample-pool endpoints are not domain bounds.
Because `G` has no input/state reads and is safely constant, its false value
is invariant over both entire domains, forward/reverse traversals and all
passes. The certificate binds the actual domain and enclosing control/pass
context anyway; it cannot be borrowed across occurrences.

Literal Boolean `false` is distinguished from this rule: the upstream GOCO
compiler recognizes it, but this proposal does not add Boolean-literal forms
to the closed Coverage-v3 source subset or this guard grammar. `IF (false)`
has no admission path in catalog v1; it cannot be treated as an unbound ID
or silently converted to `0==1`. A future Boolean-literal extension requires
prospective review and an explicit closed-parser representation.

Exact constant-folded false comparisons are admitted. Frozen-domain
contradictions involving input, item index, values, indicators, or state are
not: even `n<0` on the declared numeric domain is outside this v1 grammar
and remains unresolved/unmatched unless required and mapped normally.
Input-dependent predicates false on all five cases but satisfiable elsewhere
are not constant-false proofs. This conservatively avoids hidden range,
overflow, conversion, or loop-context assumptions.

### 5.2 Closed body grammar and compiler validity

The complete body is a finite ordered list generated only by:

```text
Body ::= zero or more BodyStatement
BodyStatement ::= NUMBER fresh = C.
                | existing_number_binding = C.
                | existing_number_binding += C.
                | IF (G_false) { Body }
G_false ::= G from section 3, independently evaluated as false
```

All symbols/types/scopes and statement forms must already pass the original
closed source parser and pinned compiler's static validation. A body
declaration is globally fresh, with no outside read/write/binding dependency;
each assignment targets a declared scalar NUMBER binding. No body declaration
may supply a binding needed outside the region. Existing binding names and
their types/roles are retained exactly. All constants, including unreachable
RHS trees, pass §3. A static compiler error cannot be removed by unreachability.

No loop, input, import, API call, array/element access, array/string/Boolean
declaration, display, return, break/continue, alternate arm, general guard,
or other body form is admitted. A construct allowed elsewhere in the source
language can still be excluded from this body grammar. Unknown syntax ALWAYS
fails before classification. An unreachable display still violates the
catalog and any one-final-display source restriction; a false region cannot
hide an extra display or error-producing RHS.

An extra body write to an otherwise live/required accumulator can qualify only
as an unreachable EXTRA writer: the entire writer occurrence is prospectively
non-required and the static false guard proves it never executes. A required
writer placed in such a region remains required and cannot receive this
disposition. The guard/body are not allowed to erase an initialization or
change a required binding, type, loop header/step, branch selection, state
epoch, or subsequent live reaching definition.

The original complete raw graph may conservatively contain control or
may-reaching edges from unreachable writes to live reads. Those edges are
not deleted. For each such boundary edge the certificate must show the exact
owning false guard prevents the writer/update event, in the original control
context, on every admissible execution. A refined feasible-state view may
exclude ONLY those independently proved unreachable events. If any relevant
path can bypass the owner guard, if an outside operation executes as a
consequence of the region, or if feasible reaching definitions remain
ambiguous, the proof fails. General path pruning, algebraic cancellation,
five-case state unions and output equality are not permitted substitutes.

### 5.3 Complete graph, nested ownership, and safety

Keep the IF, guard, body, every repeated occurrence, all raw interior and
boundary typed/control/state edges, and all enclosing loop/pass locations.
The guard itself may execute; the body never does. Guard evaluation is total,
side-effect free and finite under §3. There is no ELSE arm or cleanup action.
The required feasible state/outputs remain unchanged. Existing enclosing
loop bounds/steps and control decisions remain mapped and unchanged.

Nested false regions are admitted only by the same body production and must
each have their own valid §3 false-guard proof. Assign each semantic member
to its outermost admitted false region, then emit one disposition certificate
per owned node/edge. Inner-region proofs are supporting references, not second
dispositions. Record the complete containment tree and member sets; no member
may be omitted or multiply owned. An enclosed declaration is not separately
PURE_UNUSED, even if it independently has no reads.

A region owns its IF/guard/body members, internal edges and justified incident
boundary edges for which the extra supplies an endpoint or unreachable
update event. It does NOT own outside required endpoints. An existing
enclosing-loop control edge remains recorded with both endpoints and can be
reference-only only for its extra destination/update relation, not for the
loop itself. Any edge already needed by a direct/equivalent required mapping
is ineligible. These restrictions prevent a wrong-loop/cross-pass certificate
from hiding a live dependency.

## 6. Occurrence identity, requirements, and V3.5 separation

Disposition is assigned to raw occurrence IDs, never to a capability key as a
whole. Identical arithmetic/type/role keys can have separately required and
non-required occurrences. Preserve all repetitions and raw locations. Alpha
renaming must preserve bindings, types, ownership, control/pass context and
semantic disposition, while retaining each realization's own source hash,
occurrence IDs and locations.

Use the unchanged prospective requirement occurrence selectors and complete
mapping obligations to establish non-requirement. A source-only key resemblance
does not add a requirement, and an unused same-key occurrence cannot satisfy
another required occurrence or multiplicity. Conversely, an occurrence
already mapped to a required canonical key remains in that mapping: the
catalog cannot shrink the complete joint-intervention occurrence list required
by A3 §9.1.1. Inconsistent claimed membership blocks, rather than retroactively
changing required occurrence selection.

Required-but-INACTIVE, required-but-essentiality-UNRESOLVED and uncertain
unmatched live structure have no reference-only admission path. If essentiality
evidence is relevant, verify its source/mapping/state identity and exact
occurrence membership before using it to reject a claim. Unsupported
interventions do not prove inertness; catalog proofs come from prospective
non-requirement plus complete static safety, not from absence of activity.

REFERENCE_ONLY contributes no training capability key, no ACTIVE evidence,
no V3.4 witness and no V3.5 behavioral, value/literal or output witness. Its
constants cannot supply exact lexemes, computed-value coverage, negative/zero
output categories or sentinels. Required initial-state or ACTIVE-parent
attachments and actual final output/display ancestry cannot simultaneously
be reference-only. There is no shared required/reference-only evidence role
in this proposal. Existing V3.5 evidence-kind/null rules and prospective row
identities remain unchanged; no row is created, deleted, merged or recounted.

## 7. Exhaustive V3.2 accounting

First reconstruct the full parsed source inventory, with all typed semantic
nodes/edges and raw syntax-to-semantic associations. Parser omissions,
unknown forms and an unrepresentable semantic occurrence are failures, not
normalization. Nonsemantic spelling/grouping records link to their semantic
owners under the existing presentation rules; they do not form an unexplained
fifth semantic bucket.

Every relevant semantic occurrence receives exactly one disposition:

1. `REQUIRED_DIRECT_MAPPING` — exact required source correspondence.
2. `REQUIRED_VIA_AUTHORIZED_EQUIVALENCE` — required realization with a verified
   existing V3.3 certificate and preserved interface.
3. `AUTHORIZED_EQUIVALENCE_INTERNAL` — explicitly inventoried internal source
   structure accounted for by that same authorized equivalence.
4. `REFERENCE_ONLY` — exactly §4 or §5, with this proposal's complete certificate
   once independently approved/frozen and implemented/verified later.

Preserve complete source, direct/equivalent mapped, equivalence-internal,
reference-only, uncovered and duplicate-disposition inventories. Acceptance
of this mapping accounting requires `uncovered = []` and
`duplicate_disposition = []`. This proposal permits no shared-disposition
exception. References to a node in supporting proofs or multiple required
edges are not additional dispositions; the node still has one owner/bucket.
Conflicting ownership or mapped-and-reference-only claims FAIL. Uncovered
source remains FAIL/UNRESOLVED, never an implicit ignored category.

The four labels describe source accounting, not four new scientific gate
categories. The existing seven-category V3 ontology and equivalence catalog
remain untouched. Output agreement cannot repair missing accounting.

## 8. Proposed deterministic certificate representation

This section is a specification of future nested V3.2 proof payloads, not a
new evidence artifact or current report. Each attempted reference-only
occurrence has one record. All listed fields are mandatory; unknown fields,
types, rule IDs, enums or implicit nulls fail. Explicit JSON null is allowed
only where specified. No `pass`, `harmless`, `unused`, `parent_active` or
caller-supplied Boolean establishes a proof.

### 8.1 Closed outer fields

| Field | Exact meaning/type |
| --- | --- |
| `schema_version` | Integer 1 for this nested payload; does not change enclosing report version. |
| `catalog_version` | String `RO-CATALOG-PROPOSED-1`; usable for acceptance only after the exact reviewed version has a separately bound approval/freeze. |
| `catalog_authority_reference` | Bound frozen-authority reference under the existing authority-reference policy; drafting this file alone cannot satisfy it. |
| `program_id` | Exact source program identity. |
| `source_reference` | Existing exact-byte artifact reference to the original complete source. |
| `source_inventory_reference` | Existing record reference to its complete raw occurrence inventory. |
| `prospective_contract_reference` | Existing record reference to the unchanged contract/required-computation inventory. |
| `mapping_reference` | Existing record reference to the complete V3.2 mapping context. |
| `graph_reference` | Existing record reference to the complete typed raw graph. |
| `state_reference` | Existing record reference to complete static reaching/control/state analysis. Required non-null. |
| `compiler_identity_id` | Exact closed pinned compiler/runtime/configuration identity under A3 §6. |
| `occurrence` | Closed object defined below. |
| `disposition_class` | Exactly `PURE_UNUSED` or `CONSTANT_FALSE`. |
| `proof_rule_id` | Exactly one of the two matching admission IDs in §3. |
| `ownership` | Closed object defined below. |
| `prospective_lookup` | Closed object defined below; recomputed, not caller-selected. |
| `influence` | Closed object defined below. |
| `safety` | Closed object defined below. |
| `constant_false_proof` | Exactly the §8.3 object for CONSTANT_FALSE; explicit null for PURE_UNUSED. |
| `cross_layer_checks` | Closed object defined below. |
| `supporting_references` | Ordered array of existing record references supporting all claimed facts; explicit empty array only when no further support is needed. |
| `reason_codes` | Ordered unique array from §8.4, not free-form proof assertions. |
| `mechanical_disposition` | Exactly `REFERENCE_ONLY`, `REJECTED`, or `UNRESOLVED`; independently recomputed. |

This proposal does not add an artifact-role enum, expected-row set or report
envelope field. The future producer embeds the payload in the complete
`v3_2_mapping_rows` proof context and uses existing artifact/record references.
The common A3 schema, hashes, provenance, row closure and status remain
mandatory. If that representation cannot express a needed scientific fact
without changing a closed interface, STOP for a prospectively reviewed
interface revision rather than inventing a new field/role in implementation.

References obey A3's acyclic hash/provenance ordering. In particular
`mapping_reference` denotes an immutable already-bound required-correspondence
context, not the enclosing final mapping row/report or this certificate's own
hash. Static graph/state and prospective memberships are reconstructed before
final disposition acceptance; the checker does not use a final mapping PASS
as a premise for proving that same mapping complete. Supporting/nested proofs
cannot form cycles. A missing prior context or an unavoidable cyclic reference
is UNRESOLVED and requires prospective representation review, not a fake hash.

### 8.2 Closed common objects

`occurrence` has exactly `occurrence_id`, `kind`, `source_location`,
`raw_utf8_extent`, `graph_location`, `operation`, `result_type`,
`operand_types`, `operand_roles`, `result_role`, `binding_references`,
`source_endpoint_id`, `target_endpoint_id`, and `port`.
`kind` is NODE or EDGE. Locations must exactly resolve to the pre-bound
inventory's declared coordinate convention. `raw_utf8_extent` is a half-open
byte interval into the exact source bytes, recorded additionally rather than
silently replacing any existing character-offset convention. Typed fields,
bindings and endpoints are reconstructed from the parser/type graph; NODE
edge endpoints/port are null, EDGE endpoints/port are non-null. Values for
constant nodes remain in the complete tree/graph proof, not an invented key.

`ownership` has exactly `owner_root_id`, `member_occurrence_ids`,
`interior_edge_ids`, `boundary_edge_ids`, `enclosing_control_ids`,
`loop_pass_context`, and `nested_region_proof_references`. Member lists follow
the complete inventory order and include the current occurrence exactly once.
Edges retain their own dispositions. Nested proof references do not assign
ownership again. PURE_UNUSED has empty control/pass/nested arrays.

`prospective_lookup` has exactly `requirements_digest`,
`required_occurrence_matches`, `required_multiplicity_matches`,
`equivalence_member_matches`, `required_state_control_dataflow_matches`,
`value_output_attachment_matches`, and `result`.
Match arrays contain existing requirement/evidence record references, in
prospective inventory order, and are recomputed against the entire contract
and mapping, not a producer-selected subset. `result` is ABSENT, REQUIRED,
or UNRESOLVED. ABSENT requires every match array empty and a complete lookup;
an unknown lookup cannot produce ABSENT.

`influence` has exactly `required_computation_targets`, `required_state_targets`,
`required_control_targets`, `required_decoder_targets`, `output_targets`,
`raw_dependency_paths`, `boundary_edge_proofs`, `feasible_dependency_paths`,
and `result`. Targets bind the complete required/live analysis, not an empty
caller list. Paths use ordered raw edge IDs. PURE_UNUSED requires no raw
path to any protected target. CONSTANT_FALSE retains raw paths and gives
each potentially relevant path an exact false-owner boundary proof; feasible
paths must be empty after ONLY the allowed §5 event exclusion. `result` is
NO_INFLUENCE, INFLUENCE, or UNRESOLVED, recomputed from that analysis.

The target arrays are ordered occurrence IDs derived from the whole protected
computation, not just the display's immediate predecessors. Both path arrays
are finite reachability-witness inventories: each entry has exactly `origin_id`,
`target_id`, and `edge_ids`, with the lexicographically first shortest raw-edge
path for each reachable member/target pair. Pair order follows source-inventory
order; an origin that is itself a target has the empty path. The checker
recomputes full least-fixed-point reachability, including cycles, and derives
these witnesses; listing selected paths cannot prove that other paths do not
exist. For an EDGE member, its event/destination participates in the dependency
check as well as both original endpoints. An incident required endpoint alone
does not make an unreachable extra edge executable (§5.3).

Each `boundary_edge_proofs` entry has exactly `edge_id`, `owner_region_root_id`,
`unreachable_event_id`, `event_control_ancestor_ids`,
`false_guard_proof_reference`, and `result`. `result` is BLOCKED_BY_FALSE_OWNER
or UNRESOLVED. The verifier must prove in the structured control graph that
EVERY route executing that event passes through the exact false owner; a single
blocked sample path is insufficient. The finite feasible-state view excludes
only validated body events and their incident execution-dependent relations,
retains all other edges/events, then recomputes the same complete reachability
and feasible reaching-definition fixed points. Raw graph edges are untouched.

`safety` has exactly `constant_tree_proofs`, `read_bindings`, `write_bindings`,
`api_or_io_occurrence_ids`, `partial_operation_ids`, `termination_basis`,
`language_error_basis`, `compiler_semantics_reference`, `resource_gate_references`,
and `result`. `constant_tree_proofs` is an ordered array of records containing
exactly `rule_id`, `root_id`, `tree_reference`, `postorder_evaluations`, and
`exact_compiler_agreement`. Each postorder evaluation has exactly `node_id`,
`operation`, `child_ids`, `integer_value`, `within_bound`; all values/flags
are recomputed under §3. Read/write lists resolve exact symbol and writer
identities; APIs/partial operations must be absent. `termination_basis` is
FINITE_CONSTANT_DECLARATION or SAFE_FALSE_GUARD_UNREACHABLE_BODY, matching
the class. `language_error_basis` is exactly BOUNDED_TOTAL_NO_IO_NO_PARTIAL_OPS.
`result` is SAFE, UNSAFE, or UNRESOLVED. Failed/missing resource execution
gates cannot be represented as successful reference-only waivers (§2).

Binding lists use existing symbol/writer record references. The compiler and
resource-gate references use the existing reference schemas. In the constant
proof, `exact_compiler_agreement` is exactly AGREES or UNRESOLVED, derived from
the bound semantics and every intermediate value, never caller assertion.

`cross_layer_checks` has exactly `mapping_references`, `state_references`,
`behavioral_references`, `value_references`, `output_references`,
`active_occurrence_conflicts`, `required_inactive_or_unresolved_conflicts`,
`attachment_conflicts`, and `result`. All are ordered arrays except `result`,
which is CONSISTENT, CONFLICT, or UNRESOLVED. The verifier selects all relevant
bound records, verifies their identities and facts, and derives conflict
lists itself. Accepted conflict lists are empty; unavailable necessary
evidence gives UNRESOLVED, not CONSISTENT. No essentiality rerun or redesign
is authorized by drafting this schema.

### 8.3 Closed CONSTANT_FALSE object

`constant_false_proof` has exactly `region_root_id`, `guard_occurrence_id`,
`guard_tree_reference`, `comparison_operation`, `operand_constant_proof_refs`,
`guard_type`, `guard_value`, `domain_authority_reference`, `domain_schema`,
`universal_basis`, `control_context`, `body_inventory_reference`,
`body_binding_escape_ids`, `outside_effect_ids`, and `nested_false_proof_refs`.

`comparison_operation` is one of EQ/NE/LT/LE/GT/GE; ordered operand references
point to the two complete §3 proofs. `guard_type` must be BOOLEAN and the
recomputed `guard_value` false. `domain_schema` is NONNEGATIVE_INTEGER or
FOUR_SIGNED_INTEGER_FIELDS, matching the unchanged contract and A6.
`universal_basis` is exactly INPUT_AND_STATE_INDEPENDENT_SAFE_CONSTANT_FALSE.
There is no sampled-case or domain-contradiction variant. `control_context`
resolves the exact ordered enclosing IF/loop and pass identities in the
original source. Binding escape and outside-effect arrays must be empty after
the complete binding/control analysis. The body and nested proofs resolve
the entire §5 grammar, not selected harmless statements.

`control_context` and each `loop_pass_context` entry have exactly
`control_occurrence_id`, `control_kind`, `parent_control_occurrence_id`,
`source_location`, and `pass_ordinal`. `control_kind` is IF or LOOP; a root's
parent is explicit null, an IF's pass ordinal is null, and a LOOP's positive
pass ordinal is its source-order traversal identity reconstructed from the
prospective computation, not a runtime iteration number. Nested-region arrays
contain existing record references to the corresponding guard/body proofs.

### 8.4 Deterministic outcomes, reasons, and independent checking

The closed reason-code catalog is:

```text
RO_ADMITTED_PURE_UNUSED
RO_ADMITTED_CONSTANT_FALSE
RO_SOURCE_SUBSET_OR_TYPE_INVALID
RO_IDENTITY_OR_CONTEXT_MISMATCH
RO_OUTSIDE_CLOSED_GRAMMAR
RO_REQUIRED_OR_EQUIVALENCE_MEMBER
RO_REQUIRED_MULTIPLICITY_OR_ATTACHMENT
RO_PROSPECTIVE_LOOKUP_UNRESOLVED
RO_STATE_CONTROL_OUTPUT_INFLUENCE
RO_PARTIAL_OR_NONEXACT_EVALUATION
RO_API_IO_OR_BINDING_ESCAPE
RO_GUARD_NOT_STATIC_FALSE
RO_NESTED_OR_BOUNDARY_PROOF_INVALID
RO_ACTIVE_OR_REQUIRED_BEHAVIOR_CONFLICT
RO_UNCOVERED_OR_DUPLICATE_DISPOSITION
RO_REQUIRED_EVIDENCE_OR_EXECUTION_GATE_UNRESOLVED
```

Order reasons by the order above; do not erase additional applicable reasons.
Exactly one matching admitted code and no failure code permits
`mechanical_disposition: REFERENCE_ONLY`. A known violation is REJECTED.
With no known violation but an incomplete required premise, use UNRESOLVED;
both block source-accounting acceptance. Successful per-occurrence disposition
does not imply overall candidate PASS (§1.3).

An independent read-only verifier must reconstruct the original full inventory,
prospective lookup, direct/equivalent/internal memberships, all dependency and
state/control paths, safe constant evaluations, body grammar, ownership,
cross-layer facts and final uncovered/duplicate lists. It must reject omitted
members, caller-forged classifications, wrong hashes/locations/loop/pass,
forged domain/constant proofs and repaired-but-false summary flags. Producer
final statuses are not proof inputs. Serialized replay must work without the
certificate constructor. Shared parser/type/compiler/state foundations must
be disclosed; constructor independence is not a claim of a second independent
GOCO implementation. This is a requirement for later separately authorized
implementation/testing, not evidence generated by this task.

## 9. Paper threat-test table

These are hypothetical specification checks only. None is an executable
fixture, candidate, expected-output record, or observed test result.
"Admitted" means a V3.2 disposition under this proposed catalog AFTER its
review/freeze and after all preconditions, never candidate acceptance. A7/A4
dead-code restrictions continue to veto scientific uses as applicable.

| Hypothetical case | Proposed disposition | Mechanical reason |
| --- | --- | --- |
| Fresh top-level scalar initialized to safe integer 1877, never read or written again | Admit `RO.PU.TOP_LEVEL_CONSTANT_DECL` | One fresh binding, no required obligation/influence, total bounded constant. |
| Same declaration with alpha-renamed identifier | Same rule, distinct raw certificate | Type/binding/ownership invariants persist; no location/hash borrowing. |
| Fresh top-level scalar initialized to `(13-8)*2`, never read | Admit same PU rule | Complete NEG/ADD/SUB/MUL constant kernel; every intermediate in bounds. |
| Fresh scalar initialized to total input-dependent arithmetic, never read | REJECT: `RO_OUTSIDE_CLOSED_GRAMMAR` | No identifier/range/totality-inference admission; harmlessness alone is insufficient. |
| Fresh scalar initialized to `1877 % 0`, never read | REJECT: `RO_PARTIAL_OR_NONEXACT_EVALUATION`, `RO_OUTSIDE_CLOSED_GRAMMAR` | Executed modulo-zero raises an error; output disconnection is irrelevant. |
| Constant expression leaves the bound then cancels back into range | REJECT: `RO_PARTIAL_OR_NONEXACT_EVALUATION` | Every intermediate, not just final value, must pass the bound. |
| Fresh top-level local later assigned another safe constant, never read | REJECT: `RO_OUTSIDE_CLOSED_GRAMMAR` | PU v1 allows one declaration writer only; no standalone/multi-writer route. |
| Unused declaration or assignment inside a required loop | REJECT PU: `RO_OUTSIDE_CLOSED_GRAMMAR` | Not a top-level one-time fresh declaration; no loop/cross-pass admission. |
| Executed unused write to a required accumulator, including `+=0` | REJECT: `RO_REQUIRED_OR_EQUIVALENCE_MEMBER` and/or `RO_STATE_CONTROL_OUTPUT_INFLUENCE` | Required/live state writers are not fresh unused bindings; equality/no-op is no proof route. |
| Writer consumed later or participating in reaching-definition ambiguity | REJECT/UNRESOLVED: `RO_STATE_CONTROL_OUTPUT_INFLUENCE` | Complete sequential/loop/pass state analysis cannot prove inertness. |
| Entire unused IF or loop with otherwise safe operations | REJECT PU: `RO_OUTSIDE_CLOSED_GRAMMAR` | Neither control form is in PU; only the exact false-IF CF rule exists. |
| Disconnected INPUT, SPLIT or TO_NUMBER call | REJECT: `RO_API_IO_OR_BINDING_ESCAPE` | Input/prompt, array registry and conversion-error effects are not pure-unused. |
| Disconnected array index possibly out of bounds | REJECT: `RO_OUTSIDE_CLOSED_GRAMMAR`, `RO_PARTIAL_OR_NONEXACT_EVALUATION` | Indexing has no PU/CF safety rule; disconnected errors remain observable. |
| Literal `IF (false)` | No admission: `RO_OUTSIDE_CLOSED_GRAMMAR`; source-subset error if unrepresented | Upstream Boolean literal is not added to this subset/catalog; do not rewrite it to a comparison. |
| `IF ((13-8)*2 == 11)` with an allowed constant body | Admit `RO.CF.CONSTANT_COMPARISON_IF` | Both operands exact/total, comparison universally false, complete body/context retained. |
| Predicate false on all five development cases but satisfiable elsewhere | REJECT: `RO_GUARD_NOT_STATIC_FALSE`, `RO_OUTSIDE_CLOSED_GRAMMAR` | Samples do not prove universal unreachability; guard reads input/state. |
| Frozen-domain-impossible `n<0` for nonnegative numeric input | REJECT RO: `RO_OUTSIDE_CLOSED_GRAMMAR` | Intentionally no domain-contradiction rule; unmatched structure continues to block. |
| False comparison containing modulo/division or API evaluation | REJECT: `RO_OUTSIDE_CLOSED_GRAMMAR`, plus applicable safety code | All guard operands must pass the closed total kernel; no unsafe constant-false shortcut. |
| False branch contains unknown GOCO syntax or a compiler-invalid binding | REJECT: `RO_SOURCE_SUBSET_OR_TYPE_INVALID` | Full static parse/type/validation precedes unreachability. |
| False branch contains an extra `total+=19` to a live accumulator | Admit CF only if wholly non-required | Exact false owner proves write never occurs; keep ghost raw state edges and prove each infeasible. |
| False branch contains a required accumulator writer | REJECT: `RO_REQUIRED_OR_EQUIVALENCE_MEMBER` | Static unreachability cannot erase a prospective required occurrence. |
| Nested false comparisons with bodies in §5.2 | Admit outer CF ownership with verified nested proofs | Each inner guard checked; each raw member gets one outermost owner. |
| Nested input-dependent IF under a false outer IF | REJECT: `RO_OUTSIDE_CLOSED_GRAMMAR` | Small body grammar excludes arbitrary nested guards even when outer body is unreachable. |
| Unreachable display, API, loop or error-producing RHS | REJECT: `RO_OUTSIDE_CLOSED_GRAMMAR` (and source error where applicable) | Body grammar and full source placement restrictions are not waived. |
| Required occurrence case-INACTIVE | REJECT RO: `RO_ACTIVE_OR_REQUIRED_BEHAVIOR_CONFLICT` | Remains required; a case-level activity result cannot change source obligations. |
| Required occurrence essentiality-UNRESOLVED | Same rejection; unresolved evidence retained | No activity-absence escape and no row removal. |
| Extra live arithmetic whose final output happens to match | REJECT/UNRESOLVED: `RO_STATE_CONTROL_OUTPUT_INFLUENCE` | Output agreement is not an admitted equivalence/safety proof. |
| One unused same-key occurrence plus another required occurrence | Separate dispositions; no multiplicity borrowing | Only independently eligible occurrence can be RO; required mapped/intervened list remains complete. |
| Caller RO flag, missing member, mapped-and-RO member, wrong loop or cross-pass certificate | REJECT identity/accounting/context codes | Reconstructed inventories/ownership reject flags, omissions, duplicates and borrowed proofs. |

## 10. Compatibility assessment

| Existing gate/authority | Assessment and unchanged obligation |
| --- | --- |
| V3.1 | Compatible if prospectively approved: requirements, occurrence selectors, evidence kinds and multiplicity remain derived from the unchanged slot contract. RO cannot add/remove requirements. |
| V3.2 | Prospectively supplemented: supplies the missing two-class closed grammar and safety/accounting proof, preserving full raw inventories and unknown-form failure. No existing parser acceptance is expanded by implication. |
| V3.3 / A2 5.3 | Compatible: no new equivalence, alternative reference, general algebra, finite-domain enumeration or source rewrite. Constant evaluation here proves an extra inert, not a new required-key equivalence. |
| V3.4 | Compatible: no training key/witness arises from RO; same-domain/type/role and both-condition coverage remain required. |
| V3.5 / A3 §9.1 | Compatible: required INACTIVE/UNRESOLVED rows remain required, ACTIVE conflicts reject RO, all mapped joint instances remain, attribute-parent and output-case evidence stay separate. |
| V3.8 | Compatible: incomplete lookup, uncertain safety, unmatched live structure, unknown forms, uncovered/duplicate members and unproved context fail closed. |
| Delegated interface | Proposed nested representation under existing V3.2 rows only. No artifact-role, envelope, expected-index, row-ID, population or closure change. Any representational conflict requires separate prospective review, not an implementation workaround. |
| Paired scaffold / V3.6 / E3 | Compatible only with the independent veto preserved: raw extras/counts remain visible, paired ASTs are not compared after RO deletion, and forbidden dead/padding/unreachable code still fails even symmetrically. |
| Slot ledger / CONF1 protocol | No change to `no_semantically_dead_code`, accepted-source/scaffold rules, predicates, graphs, sampling, schedules, seeds, budget or treatment. A V3.2 disposition is not permission to insert source extras. |
| INPUT_DOMAIN / A6 | Compatible: domains retain unbounded declared integer ranges and fixed four-field schema; sample pools are not proof bounds; decoder activity/class obligations are unchanged. |
| E1 | Compatible: E1 still owns validation of the original source and every frozen case with closed compiler identity. Neither constant proof nor reachability waives compile/runtime/resource failure or replaces expected-output validation. |
| E2/E4 / AST-v2 | Compatible: original complete source/token tree remains the compared object; no new dead-code-removal normalization or overlap exception. |
| E5 / V3.7 | Compatible only with complete source/state retained: exact inertness may explain non-required extras, but cannot prune raw graph topology or create a new novelty normalization. E5 still independently certifies complete behavior/state and checks graph and semantic collision. Unrepresentable state/safety remains UNRESOLVED. |

The compatibility entries are a reasoned specification assessment, not an
independent approval or executed validation. They confer no candidate or
scientific-instance closure and change no current implementation-readiness
status. In particular REFERENCE_ONLY implementation remains unresolved and
scientific closure remains
`DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION_AND_VALIDATION`.

## 11. Independent-review questions and final boundary

There is no unspecified alternative admission path in v1. Review should
explicitly accept or reject these conservative choices:

1. Restrict PURE_UNUSED to one initialized top-level fresh NUMBER declaration,
   excluding standalone writes, control constructs, loop-local/cross-pass
   storage, input-dependent expressions and all APIs/indexing.
2. Restrict CONSTANT_FALSE to exact bounded-integer comparisons and the
   explicit body grammar, excluding Boolean literals, domain contradictions,
   arbitrary nested guards and even known-but-unlisted unreachable operations.
3. Accept the bounded per-node exactness proof against the pinned binary64
   semantics, with no resource/execution-gate waiver or short-circuit assumption.
4. Accept unreachable extra live-binding writes only with complete raw-edge
   ownership and exact false-owner feasibility proofs, never a required writer.
5. Preserve A7/A4 dead-code prohibitions as independent candidate vetoes:
   the catalog can resolve a mapping question without permitting such extras
   in any scientific candidate governed by those prohibitions.
6. Confirm that the proposed closed nested certificate can be carried within
   A3's existing mapping-proof context. If not, require a separately reviewed
   prospective interface clarification before freeze/implementation.

These are review decisions, not implementer discretion or permission to
expand v1. No empirical claim is made that a future engine can produce these
proofs. Missing semantics/representation/proof support must STOP later work,
not turn an excluded form into an implicit accepted class.

Only this proposal is to be committed, alone, for a stable review identity.
Its exact commit/blob/byte-hash/size are reported in the handoff, outside this
file, avoiding self-referential identities. No freeze manifest is created.
No code, test, evidence artifact, frozen protocol/manifest, PROJECT_STATE,
implementation gate or protected preregistration is changed. No fixture or
scientific source is executed, no population test/producer or expected-row
enumeration/recount is performed, and historical 8668 remains non-authoritative.
No candidate, model, E1–E6 producer, experimental provenance/binder,
preregistration or sealed-holdout work occurs. STOP after this proposal commit
and handoff; independent review and prospective freeze must come next.
