# Proposed CONF1 REFERENCE_ONLY delegated-interface amendment v2

Status: PROPOSAL FOR INDEPENDENT REVIEW ONLY. NOT APPROVED. NOT FROZEN.
Formal proposed status: `PROSPECTIVE_DELEGATED_INTERFACE_AMENDMENT`.
Representation revision: `RO-INTERFACE-PROPOSED-2`, authored 2026-10-02.
Starting HEAD: `a1f4725dd18aa5743a30336b315c274f415fc6a6`, branch `main`, clean.

## 1. Authority, scope, and prospective effect

This is a normative prospective delegated-interface amendment proposal, NOT an
explanatory note, implementation, scientific evidence, or freeze. The existing
`phase3c_conf1_reference_only_interface_clarification_proposed.md` (v1) remains
historical, unchanged, and unfrozen: exact-byte SHA-256
`e0a48b2ccd1eec31e3019982d199fc4b96c418a10e8b05558de2956ad70e3e9f`,
Git blob `3658ce02d473bc34c27f0f2144f4fb1c99136962`, 50,404 bytes.
This v2 supersedes v1 for prospective review only; neither version is frozen
authority. The semantic catalog
`phase3c_conf1_reference_only_catalog_proposed.md` is accepted in substance under
the supplied independent review but remains unchanged and unfrozen.

The final independent review returned
`REFERENCE_ONLY_INTERFACE_PROPOSAL_REVISION_REQUIRED`: it accepted the single
scientific record role, internal acyclic staging, complete 184-program inventory,
V3.2 payload/pre-context/Option B representation, and downstream veto direction.
V2 retains those choices and resolves only output-read permission, exact E1
prerequisites, formal amendment precedence, and explicit role-consumer closure.
No semantic admission rule is redesigned.

Both exact proposals must receive independent approval and the ordered compatible
freezes specified in §12 before implementation can be separately authorized.
Neither approval, a proposal commit, nor either partial freeze authorizes
implementation, fixtures, candidates, population work, E1--E6 production, models,
or sealed-holdout access. This document authorizes none of those activities.

The recorded boundary remains pre-Attempt-004: no Attempt-004 candidate exists;
no CONF1 model result selected these rules. Earlier rejected attempts remain
rejected. No source, case, population, scientific finding, or gate is produced here.

Controlling existing authorities, unchanged by this proposal:

| ID | Authority / exact identity | Relevant provisions |
| --- | --- | --- |
| D | `phase3c_conf1_delegated_evidence_interfaces_proposed.md`; exact-byte SHA-256 `9c684eaf6b0099080ddf907630b0a2f8e176e3a882b67875d82f07bd82d64dc5`, Git blob `1b6d4d1a825bf9e9d288ca9c3815d1a8e7c78d1a`, 76,081 bytes | §§1--4, 5.5--7, 8--9.1.4, 17 |
| DF | Its existing freeze manifest; exact-byte SHA-256 `bd7a7fc6862ce049c1fdf363f763e1a3a17808132291b9064e3c6f26fb720948` | Exact frozen bytes and upstream identities |
| V | Frozen Coverage-v3 methodology and its existing freeze | V3.1--V3.8, especially complete mapping, narrow equivalence, state completeness, and fail-closed rules |
| S | Accepted-but-unfrozen semantic catalog; exact-byte SHA-256 `7df2a31df6c995d0105e5547aa1d235c6046e9cf141f92321faf92cce3bac682`, Git blob `569ed951b121416b4c90240282d96231ce62c6e8`, 52,310 bytes | §§2--8, including occurrence ownership and cross-layer consistency |
| L | Frozen slot ledger; LF-policy SHA-256 `83436eecda3affe813b785e868e3f8936fa59afc35ded0eb6a54290edb41dc88`, Git blob `133c9c7275bcedeaf2474e54e61bae47923508ad` | Prospective roles, training/evaluation groups, `no_semantically_dead_code: true` |

D §9 requires complete mapping plus mechanically proved REFERENCE_ONLY
constructs; it does NOT already specify the row payload below. This v2 is proposed
against EXACTLY D and DF identified above, not a moving filename or historical
approved-proposal hash. Its operative effect exists only after approval/freeze.
The following table is the exhaustive normative override/supplement boundary:

| Base provision / representation | V2 prospective override or supplement | Exact precedence / unchanged boundary |
| --- | --- | --- |
| D §2.2 record-role vocabulary | Add exactly `SCIENTIFIC_EVIDENCE` with §2's mandatory type/selector checks | V2 controls only this addition; all old roles and the five reference fields remain unchanged |
| D §4.1 source occurrence inventory scope | Complete inventories across the existing 120 training + 32 primary + 16 primitive-sanity + 16 structural-transfer programs, as §3 specifies | V2 controls completeness/representation scope; no scientific population, slot, case selection, or expected-row-count change |
| D §9 V3.2 payload | §§2--6/10 specify the exact closed row, internal records, immutable pre-context, RO containers, deterministic ordering and four-bucket closure | V2 controls these previously unspecified payload details; D's 184 rows, row identities, wrappers/indexes, and frozen V meanings remain controlling |
| Canonical S §8 representation | §9's lossless inventory/shared-proof/per-occurrence adapter and §7's prior-structural/later-consistency staging, subject to §8's explicit per-program E1 gate | V2 controls encoding/logical staging ONLY; S and V control scientific admission, ownership, safety, equivalence, state, and mandatory veto meanings; no substantive semantic override |
| D §5.1 read classifications | NO override or addition; v1's proposed fifth class is not adopted | All four existing classes remain exhaustive and controlling; §8 uses only the existing shared-invocation route |
| D §§5/5.5/6 shared execution, compiler relevance and provenance | NO override; §8 specifies logical order within an invocation already satisfying D | No shared-session loophole, new execution map, report/provenance field, or weaker compiler rule |
| All other delegated-interface/scientific requirements | NO override | Every unlisted requirement remains unchanged and controlling |

For an approved/frozen compatible pair, v2 takes precedence over D ONLY in the
explicitly listed representational areas. For every other area D remains
controlling. S's approved/frozen scientific semantics and D's upstream frozen
scientific authorities are never displaced by this representation amendment.
V1 has no normative precedence. Any unlisted conflict or unrepresentable required
scientific finding blocks acceptance as FAIL/UNRESOLVED under the applicable
existing rule and requires prospective review, not an implementer-selected
interpretation, compatibility workaround, or relaxation. §12 fixes the exact
freeze relationship; no retroactive applicability is claimed.

Scientific semantics remain V's and S's. There are no new semantic classes,
admission paths, equivalences, state rules, thresholds, or execution waivers.
The exact rules remain `RO.PU.TOP_LEVEL_CONSTANT_DECL`,
`RO.CF.CONSTANT_COMPARISON_IF`, and supporting
`RO.SAFE.BOUNDED_INTEGER_CONSTANT_TREE`. State/activity interfaces here mean
V's frozen state-completeness requirements and D §9.1's evidence variants;
DEVELOPMENT essentiality/state files are not future scientific authorities.
All dead-code, scaffold, overlap, original-source E1, resource/budget, and full
E5 vetoes survive even when a V3.2 accounting disposition is valid.

## 2. Closed-schema conventions, roles, and identities

All fields listed for a new object are mandatory and exhaustive. Unknown fields,
duplicate JSON keys, wrong types/enums, missing fields, implicit nulls, unbound
references, unknown syntax, and unrepresentable occurrences block acceptance.
No arbitrary `data`, extension dictionary, or caller-selected proof schema is
permitted. Lists are ordered JSON arrays; IDs are nonempty exact UTF-8 strings.
An ID list has no duplicates unless explicitly representing invalid duplicate
claims. Integers exclude Booleans. Unknown scientific facts are not empty lists.

Reuse D's file-level artifact reference, logical `record_reference`, and
frozen-authority-reference policy WITHOUT changing their field sets. Structured
record references retain both explicit null content fields; source strings retain
their exact UTF-8 content digest and size. File hashes remain exact-byte SHA-256.

NEW minimal role extension: add exactly `SCIENTIFIC_EVIDENCE` to D §2.2's
`record_role` vocabulary. It denotes an addressable, schema-checked blocking
scientific representation/proof record, including the V3.2 row and its proof
subrecords, source-inventory/binding records, and referenced E1/V3.5 evidence
rows. This does not make every such record a PASS finding. Existing source and
contract references retain `SOURCE`/`REFERENCE` and `COVERAGE_CONTRACT`.
There is NO new `artifact_role`: inputs use `SOURCE_OCCURRENCE_INVENTORY`;
producer records live inside `COVERAGE_V3_DIRECT_EVIDENCE`; E1 references use
the existing `DELEGATED_EVIDENCE_REPORT` artifact role. `DIAGNOSTIC` is NOT used
to disguise blocking proof. This record-role addition requires approval of this
prospective interface revision; an old validator must reject it, not silently
accept it. No existing diagnostic role acquires a scientific admission function.

Normatively, `SCIENTIFIC_EVIDENCE` NEVER authorizes reference resolution by itself.
EVERY consuming field must additionally match the exact expected RID family,
object schema/record type, program identity, owning row, producer stage,
container/path and selector, plus the applicable input/output artifact binding,
compiler identity, and provenance closure. The registry below and each field's
schema define these constraints jointly; first-use logical values follow §8 and
final scientific consumption requires exact containing-file closure. A successful
role comparison cannot override any of these checks. Polymorphic support fields
must match the exact `proof_kind`/value-schema variant, not merely this role.

The consumer MUST reject V32STATE for V32GRAPH, V32GRAPH for V32PREMAP,
V32ROCERT for V32ROREGION, another program's same-family record, unrelated future
SCIENTIFIC_EVIDENCE, and DIAGNOSTIC relabeled as SCIENTIFIC_EVIDENCE. It MUST NOT
resolve by recursive arbitrary-JSON search, a coincident ID, a caller type tag,
or a later-stage fact. E1 references select the matching E1 producer program row;
V3.5 references are permitted only in the downstream consistency stage, never as
initial RO premises. This is one type-and-selector-checked role, not a catch-all.

Use D §3.3's exact RID framing. All ordinal components below are minimal decimal
strings starting at 1, not scientific results, runtime iterations, or hashes.

| Record | Exact record ID | Physical selector / container |
| --- | --- | --- |
| Complete inventory | `RID("V32INVENTORY", [program_id])` | Input occurrence artifact `programs[]`, matching `record_id` |
| Binding | `RID("V32BINDING", [program_id, declaration_occurrence_id])` | That program inventory's `bindings[]` |
| Raw semantic occurrence record | `RID("V32OCCRECORD", [program_id, occurrence_id])` | Inventory `occurrences[]`; preserves the separate original occurrence ID |
| Typed graph | `RID("V32GRAPH", [program_id])` | V3.2 row `evidence_records.typed_graph` |
| Static state/control analysis | `RID("V32STATE", [program_id])` | V3.2 row `evidence_records.state_control_analysis` |
| Pre-disposition context | `RID("V32PREMAP", [program_id])` | V3.2 row `evidence_records.pre_disposition_mapping_context` |
| Required occurrence record | `RID("V32REQ", [program_id, prospective_ordinal])` | Pre-context `required_occurrences[]`; separate requirement_occurrence_id preserves contract identity |
| Shared owner proof | `RID("V32ROREGION", [program_id, owner_root_id])` | V3.2 row `reference_only_regions[]` |
| Occurrence certificate | `RID("V32ROCERT", [program_id, occurrence_id])` | V3.2 row `reference_only_certificates[]` |
| Supporting proof | `RID("V32ROSUPPORT", [program_id, proof_kind, root_occurrence_id])` | V3.2 row `supporting_proofs[]` |
| State definition | `RID("V32DEFINITION", [program_id, writer_occurrence_id])` | State record `definitions[]` |
| Final V3.2 row | **Unchanged** `RID("V3.2", [program_id])` | D's existing `v3_2_mapping_rows.rows[]` |

Identity is `(containing artifact_id, record_id)` under the exact closed file
binding. Resolve only the specified containers, never recursively search arbitrary
JSON for a coincident string. Every record ID must select exactly one object;
zero/multiple matches fail. Cross-program borrowing fails. Referenced E1/V3.5
rows use D's unchanged row IDs and their existing row-set selectors. No record
contains its own hash or derives its ID from final serialized bytes. Referencing
one record repeatedly is not extra ownership or a new scientific row.

## 3. Complete pre-bound source inventory for all 184 programs

Prospectively broaden D §4.1's existing `source_occurrence_inventory` ARTIFACT
contents, not candidate counts or scientific row sets. It contains one consistent
complete inventory for 120 training programs, 32 primary evaluation references,
16 primitive-sanity references, and 16 structural-transfer references, in the
authoritative input inventories' fixed order. These are frozen design counts,
not an enumeration or recount performed by this proposal.

The artifact has exactly `schema_version`, `candidate_id`, `programs`.
`schema_version` is 1. Each program record has exactly `schema_version`,
`record_id`, `program_id`, `source_reference`, `coordinate_convention`,
`occurrences`, `bindings`, `presentation_associations`,
`eligible_v3_5_occurrence_ids`. `source_reference` is D's exact source-string
record reference. The artifact is bound in the existing input-manifest field.

Each `occurrences` entry has exactly `record_id`, `inventory_ordinal`,
`occurrence`. Its `occurrence` is EXACTLY S §8.2's closed occurrence object;
its binding references select the inventory's binding records. Each binding has
exactly `record_id`, `binding_id`, `declaration_occurrence_id`, `identifier`,
`datatype`, `read_occurrence_ids`, `write_occurrence_ids`. Binding/read/write
identity is static scope resolution, not reaching-state or activity evidence.
`binding_id` equals `record_id`; declaration/read/write IDs select semantic
NODE entries. Identifier/datatype are nonempty strings under the unchanged
scope/type grammar; read/write lists follow inventory order. All nested
`schema_version` fields in this artifact are integer 1.

`coordinate_convention` is exactly `source_unit`, `source_origin`, `graph_unit`:
`source_unit` is `UTF8_BYTE` or `UNICODE_CODE_POINT`, `source_origin` is 0,
`graph_unit` is `OCCURRENCE_ID`. `source_location` is exactly `start`, `end`
in the declared source unit; `raw_utf8_extent` is exactly `start`, `end` in bytes;
both are half-open nonnegative intervals into the original logical source string
(UTF-8 WITHOUT JSON quoting/escaping), not into its containing JSON serialization.
`graph_location` is its exact occurrence ID. Existing pre-bound locations and
IDs must not be changed; incompatible conventions require another reviewed
representation revision, not an implementation conversion. Node edge-endpoint
and port nullity, typed roles, and bindings follow S unchanged. For an EDGE,
`port` is the fixed parser's nonempty typed destination-port identity.

The uniform frozen/bound parser and type schema supply the allowed operations,
types, roles, edge identities, and syntax associations; this document adds none.
Unknown values cannot be legalized by adding them to a producer configuration.
The producer independently reparses source and checks inventory equality.

Inventory order is all semantic NODE records in source AST preorder, followed
by all semantic EDGE records sorted by `(source NODE ordinal, target NODE
ordinal, operation UTF-8 bytes, port UTF-8 bytes, raw_utf8_extent.start,
raw_utf8_extent.end)`. Identical-key parallel edges retain source traversal
discovery order as the final tie-breaker and remain separate occurrences.
`inventory_ordinal` is consecutive over that combined order. Existing assigned
occurrence IDs are retained, regardless of their spelling. For an unassigned
newly covered occurrence, its occurrence ID is
`RID("V32OCC", [program_id, kind, inventory_ordinal])`. New IDs cannot collide
within that program. The program-qualified record wrapper is distinct from the
occurrence ID, so existing locally scoped IDs are not silently renamed merely
to obtain report-wide record-reference uniqueness.

Each presentation association has exactly `source_location`, `raw_utf8_extent`,
`semantic_owner_ids`; association order is source-extent order, ties parser
preorder. These are existing permitted spelling/grouping associations, not a
fifth semantic disposition. The complete source parse, all semantic nodes/edges,
all repeated instances, and the presentation associations must reconcile.

`eligible_v3_5_occurrence_ids` is the outcome-independent projection already
required by D for training. It follows complete inventory order, retains EVERY
eligible training occurrence irrespective of future mapping or RO disposition,
and is empty for evaluation references. It cannot shrink to mapped occurrences.
This is representation only: it does not construct source, expose holdouts,
change the slot ledger, select different cases, change the V3.5 eligible
population, or alter any expected-row count.
The actual V3.5 `mapped_occurrences` list still derives from FINAL V3.2 mapping,
not this projection. No V3.5 expected row derives from either list.

This pre-bound input contains lexical/type/location information only: no required
correspondence decision, state feasibility, RO ownership, activity, or PASS.
Static inventory construction is outcome-independent input preparation; the
scientific producer reconstructs it after input freeze. Unparseable source cannot
be accepted into a candidate under the closed grammar. A malformed/stale input
still yields a rejecting report, never replacement input or silent omissions.

## 4. Exact closed V3.2 row payload

Exact path: `row_sets[row_set_id="v3_2_mapping_rows"].rows[]` in the existing
direct report. There are exactly 184 existing scientific rows, with the existing
single pre-run V3.2 expected index and unchanged `RID("V3.2", [program_id])`.
Certificates and support objects MUST NOT create, split, merge, or remove rows,
add another expected-row index, change any canonical scientific row ID, alter
V3.5 evidence kind/population, or change candidate cardinality.

Each row has EXACTLY these fields:

```text
payload_schema_version
row_id
program_id
prospective_contract_reference
source_inventory_reference
graph_reference
state_reference
pre_disposition_mapping_context_reference
direct_required_mappings
authorized_equivalence_required_mappings
equivalence_internal_accounting
reference_only_regions
reference_only_certificates
supporting_proofs
evidence_records
uncovered_occurrences
duplicate_dispositions
source_offsets
graph_paths
evidence_record_references
status
scientific_reason_codes
```

`payload_schema_version` is integer 1. `status` remains D's `PASS`, `FAIL`, or
`UNRESOLVED`. Contract/source inventory references select pre-bound inputs.
Graph/state/pre-context references select the matching row's `evidence_records`.
`evidence_records` has exactly `typed_graph`, `state_control_analysis`,
`pre_disposition_mapping_context`. Each is the corresponding object below.
An unavailable object AND its matching reference are explicit null only in a
non-PASS row; a malformed present object is not made valid by a FAIL status.
Contract/inventory references remain mandatory; unavailable inputs block binding.

`direct_required_mappings` entries have exactly `source_occurrence_id`,
`required_occurrence_ids`, `evidence_record_references`. Each equivalence mapping
entry has exactly those fields PLUS `equivalence_rule`,
`equivalence_internal_occurrence_ids`. Each internal-accounting entry has exactly
`source_occurrence_id`, `equivalence_mapping_source_occurrence_id`,
`evidence_record_references`. Arrays are ordered by source inventory ordinal;
required-ID arrays follow prospective required-occurrence order. A single source
occurrence satisfying several authorized required selectors has ONE accounting
entry with multiple required IDs, not multiple disposition entries. Required
multiplicity and full connected correspondence are still independently verified.

`equivalence_rule` is exactly one representation label for V3.3's already closed
rules: `ALPHA_RENAMING`, `INTEGER_CONSTANT_FOLD`, `PURE_COMMUTATIVE_ORDER`,
`COMPARISON_OPERAND_SWAP`, `BOOLEAN_AND_INDICATOR_PRODUCT_LOCAL_PAIR`,
`BOOLEAN_OR_INDICATOR_SUM_POSITIVE`. These labels cannot enlarge the scientific
rule: all original purity/type/role/indicator/local-pair/lexeme preconditions
remain mandatory. Direct/equivalent/internal memberships and all preconditions
are reconstructed from complete inputs/graph; a named rule is not proof.
Claims are also retained by the existing V3.3 row; no final V3.3/V3.2 PASS is a
premise for initial correspondence checking. Proof references may select graph,
state, input, or earlier support records, not downstream row acceptance.

`uncovered_occurrences` is the source-ordered list of semantic occurrence IDs
without a VALID bucket. `duplicate_dispositions` entries have exactly
`occurrence_id`, `claimed_buckets`, `claim_record_references`; they are ordered
by source ordinal. Bucket order is DIRECT, EQUIVALENT, INTERNAL, RO as named
in §10. Repeated claims within one bucket also constitute duplication.

`source_offsets` entries have exactly `occurrence_id`, `source_location`,
`raw_utf8_extent`, ordered by source ordinal. They cover all semantic occurrences.
`graph_paths` entries have exactly `origin_id`, `target_id`, `edge_ids`;
they are the deterministic witnesses required by mappings and S's influence
proofs, deduplicated in origin/target inventory order then exact edge-ID sequence
UTF-8 order. They cannot replace full graphs or reachability reconstruction.
`evidence_record_references` is the ordered unique union of prior input and proof
references actually needed by this row, in first schema-field traversal order;
it excludes the row itself, certificate dependents, and later activity rows.

## 5. Addressable graph, state, and pre-disposition records

### 5.1 Typed raw graph

Exactly `schema_version`, `record_id`, `program_id`,
`source_inventory_reference`, `node_ids`, `edge_ids`, `expression_children`,
`control_contexts`. Schema version is 1; IDs follow §2. Node/edge lists are the
complete raw semantic inventory partitions in inventory order, NOT pruned RO
views. Inventory occurrence objects supply all operation/type/role/endpoints.
Each `expression_children` entry is exactly `parent_occurrence_id`,
`ordered_child_occurrence_ids`; entry order is parent inventory order, children
original parse/evaluation order including grouping and repeated operands.
Each `control_contexts` entry has exactly `occurrence_id`, `ancestors`;
ancestors use S §8.3's exact control-context entry shape, outermost first.
Guard/body/loop placement is reconstructed from complete original parse and
source extents, not inferred from a claimed context. Missing nodes/edges,
wrong children/context, or disagreement with source/type grammar blocks.

### 5.2 Complete static state/control record

Exactly `schema_version`, `record_id`, `program_id`, `graph_reference`,
`definitions`, `read_definitions`, `dependency_edges`, `output_ancestry`,
`decoder_ancestry`, `analysis_status`. Version is 1; `analysis_status` is
`CLOSED` or `UNRESOLVED`, NEVER final V3.2/V3.5 PASS.

Each definition has exactly `record_id`, `writer_occurrence_id`,
`binding_reference`, `control_context`; each read entry has exactly
`read_occurrence_id`, `binding_reference`, `writer_references`.
Definitions/reads follow source order; writer references follow writer source
order and contain the complete may-reaching set. Control contexts use S's exact
entry schema. Each dependency edge has exactly `edge_id`, `source_occurrence_id`,
`target_occurrence_id`, `relation`; `relation` is `DATA`, `SEQUENTIAL`,
`CONTROL`, `MAY_REACHING`, `LOOP_CARRY`, `CROSS_PASS`, `OUTPUT`, or `DECODER`.
These are analysis relations, NOT new V3.2 ontology edge/category values.
`edge_id` is `RID("V32DEPENDENCY", [program_id, relation, source_occurrence_id,
target_occurrence_id])`; identical analysis relations are one edge, ordered by
source ordinal, target ordinal, then relation in the order just listed.
Output/decoder ancestry lists contain every relevant source occurrence in
inventory order. All joins, sequential effects, loop/cross-pass fixed points,
control dependencies and binding escape are recomputed, not asserted by CLOSED.
Data/state graphs may have cycles; the RECORD PROOF dependency graph may not.
No feasible pruning occurs in this raw state record. Only S's proved false-body
events may be excluded in a separate reconstructed feasible view during RO proof.

### 5.3 `PreDispositionMappingContextV1`

Exactly `schema_version`, `record_id`, `program_id`,
`prospective_contract_reference`, `source_inventory_reference`,
`graph_reference`, `state_reference`, `required_occurrences`,
`direct_mapping_candidates`, `authorized_equivalence_correspondences`,
`equivalence_internal_members`, `still_unmatched_occurrence_ids`,
`context_status`, `scientific_reason_codes`.

Version is 1. `context_status` is `CLOSED` or `UNRESOLVED`: CLOSED means all
pre-RO facts are established and consistently represented, not that unmatched
source is authorized or final source accounting passes. Every `required_occurrences`
entry has exactly `record_id`, `requirement_occurrence_id`, `canonical_contract_key_id`,
`prospective_contract_reference`, `required_multiplicity`, `attachment_references`.
The complete unchanged prospective contract supplies occurrence selectors,
operations/roles, multiplicity and attachments; record IDs select its existing
prospective order. `requirement_occurrence_id` preserves the contract's existing
occurrence ID; only if no such ID was defined, use outcome-independent
`RID("V32REQID", [program_id, prospective_ordinal])`. Direct/equivalent mappings'
`required_occurrence_ids` select these requirement IDs, not wrapper record IDs.
Wrapper IDs are separately program-qualified as §2 requires. No new requirement
is derived from candidate extras.
Multiplicity is a positive integer; available attachment references include all
value/literal, initial-accumulator, output, and state/control obligations.

The three mapping/member arrays use §4's direct/equivalent/internal entry schemas.
They retain every correspondence and internal member, including unresolved
claims with their available evidence, and cannot use outcome-filtered subsets.
`still_unmatched_occurrence_ids` is the independently reconstructed source-ordered
complement of valid required/equivalence memberships. Conflicting memberships
make context_status UNRESOLVED and block RO admission; they are not silently
removed to make an extra eligible. Required correspondence/multiplicity failure
also blocks eventual PASS even if all remaining extras have valid proofs.

The context is constructed and frozen IN MEMORY as an immutable producer record
before any RO certificate is evaluated; it is serialized unchanged inside the
eventual report. Its ID and reference do not depend on the final report's hash.
It contains NO final row status, RO dispositions, certificate references,
activity findings, or final V3.5/VALUE/OUTPUT references. It never references the
final V3.2 row. Final row mapping arrays must equal the valid pre-context arrays;
RO cannot rewrite them. A proof constructor cannot modify this context while
resolving extras. Scientific replay reconstructs it without the constructor.
Every reference in a present context selects a prior non-null input/graph/state
record; if a prerequisite cannot be represented, the context and its outer
reference are null in the non-PASS row. Its scientific reasons use §10's closed
V32 codes applicable to prior mapping/representation facts, not future RO or
activity findings. Required attachment references select prospective contract
facts only, never a later activity row or the context itself.

## 6. Option B: per-occurrence certificates plus shared owner proofs

Choose Option B to preserve S §§5.3/8's per-node/per-edge disposition records.
Exact certificate path: V3.2 row **`reference_only_certificates`**.
It is a zero-or-more ordered array, one logical record per attempted owned
semantic occurrence, strictly in complete source inventory order. A zero-length
array is valid only if no RO attempt/member exists and other accounting closes.

Each certificate has exactly `schema_version`, `record_id`,
`occurrence_reference`, `region_reference`, `reason_codes`,
`mechanical_disposition`. Version is 1; occurrence selects its exact inventory
wrapper, region selects its single owner proof. Reasons and mechanical enum are
EXACTLY S §8.4's catalog/order and `REFERENCE_ONLY`, `REJECTED`, `UNRESOLVED`.
No caller Boolean or inherited parent status establishes a disposition.
`mechanical_disposition: REFERENCE_ONLY` additionally requires the matching
immutable per-program E1 row PASS under §8. This conservative interface-stage
prerequisite does not add a semantic admission rule or replace any S premise.

Each `reference_only_regions` entry has exactly `schema_version`, `record_id`,
`proof`; its version is 1. `proof` has exactly:

```text
catalog_version
catalog_authority_reference
program_id
source_reference
source_inventory_reference
prospective_contract_reference
mapping_reference
graph_reference
state_reference
compiler_identity_id
disposition_class
proof_rule_id
ownership
prospective_lookup
influence
safety
constant_false_proof
pre_admission_cross_layer_checks
supporting_references
```

The matching source artifact reference is exact; the inventory additionally
binds its logical source-string identity. Header references equal the owning
row/input identities. `mapping_reference` selects the immutable §5.3 context,
NEVER final V3.2/V3.5. Compiler identity is D §6's closed identity, unchanged.
`ownership`, `prospective_lookup`, `influence` and S's non-reference scalar
fields/enums retain S §8's exact schemas and computations. Complete target/path
and fixed-point proofs remain mandatory for every member, not only the root.

Region order is owner-root inventory order. Each member has exactly one region
and one certificate; member arrays include all owned nodes AND edges and are
source-ordered. Independent reconstruction determines owners: PU owns exactly
S §4's declaration/constant/internal edges; CF uses S §5's outermost admitted
false IF and all its permitted members/boundary edges, never outside required
endpoints. Any required/equivalence member conflict invalidates the owner proof,
not just one omitted member. Nested IFs have their own supporting false proofs
but no second owner/disposition. Boundary-edge support is not permission to own
the outside endpoint. Unmatched noncatalog forms remain uncovered and FAIL.

Each `supporting_proofs` entry has exactly `schema_version`, `record_id`,
`proof_kind`, `root_occurrence_id`, `value`. Version is 1 and `proof_kind` is
exactly one of these closed variants:

| `proof_kind` | Exact `value` schema |
| --- | --- |
| `CONSTANT_TREE` | S §8.2 constant-tree proof: `rule_id`, `root_id`, `tree_reference`, `postorder_evaluations`, `exact_compiler_agreement` |
| `FALSE_GUARD_BODY` | S §8.3's complete `constant_false_proof` object and exact nested enums/context/null rules |
| `SOURCE_SUBINVENTORY` | Exactly `member_occurrence_ids`, complete inventory-ordered region/body membership reconstructed from parse |
| `TYPED_SUBTREE` | Exactly `root_occurrence_id`, `preorder_occurrence_ids`, complete original ordered subtree including raw grouping associations |

Constant `tree_reference` and guard tree references select `TYPED_SUBTREE`;
body inventory references select `SOURCE_SUBINVENTORY`; constant operand,
false-owner boundary, and nested guard/body references select their matching
CONSTANT_TREE/FALSE_GUARD_BODY records. No opaque proof bytes are accepted.
For SOURCE_SUBINVENTORY with an IF root, member IDs are exactly that IF's body
subtree semantic nodes/edges, excluding the owning IF and its guard; the complete
owner inventory instead resides in `ownership.member_occurrence_ids`. Other
subinventories use their exact parsed root subtree; no caller subset is allowed.
For safety, `constant_tree_proofs` stores ordered references to CONSTANT_TREE
records instead of duplicating their values. `constant_false_proof` stores a
FALSE_GUARD_BODY reference for CF and explicit null for PU. These two adaptations
are lossless dereferencing rules to S's exact values, not semantic changes.
Nested proofs reference proper descendants only; guard/body support cannot
reference its owner region/certificates. Supporting proof order is root inventory
order, then proof kinds in table order. Evaluate support topologically (inner
proofs before outer), independent of serialization order. Region proofs reference
support records, certificates reference regions; no reverse references occur.

All attempted members remain represented even when proof is rejected/unresolved.
An invalid member/region cannot supply the RO bucket. The verifier reconstructs
complete ownership and recomputes all member-specific premises; sharing a full
region analysis does not make a root's proof automatically true for every member.

## 7. Structural admission versus later consistency

`pre_admission_cross_layer_checks` has exactly `mapping_references`,
`state_references`, `required_inactive_or_unresolved_conflicts`,
`attachment_conflicts`, `result`. The first two arrays select complete prior
context/static state facts; the conflict arrays contain inventory-ordered
occurrence IDs. `result` is `CONSISTENT`, `CONFLICT`, or `UNRESOLVED`.
Required prospective/mapping membership always defeats RO, irrespective of
future activity, including required-but-INACTIVE/UNRESOLVED cases. All declared
behavioral-parent, value/literal, initial-state, output and state/control
attachments are checked structurally now. No future activity row is read now.
Required incomplete graph/state/lookup is UNRESOLVED, not CONSISTENT.

NEW staging clarification of S §8's `cross_layer_checks`: prior structural
facts are premises of initial V3.2 disposition; behavioral/VALUE/OUTPUT facts
are later mandatory consistency checks, never premises of that initial proof.
This does NOT waive S §2's disagreement veto. A source-only match, absent ACTIVE
witness, or DEVELOPMENT essentiality result supplies no admission evidence.

After final V3.2 accounting, the direct activity/attribute producer checks EVERY
prospective training key row against the complete immutable RO member inventory:

1. All mapped occurrences and joint-intervention members are the complete final
   required mappings; none can also be RO. A required inactive/unresolved row
   remains present and cannot be dropped or relabeled.
2. ACTIVE normal/intervention evidence cannot depend on an RO occurrence as its
   claimed mapped capability, active parent, or required path member. Any actual
   live influence contradicting an RO safety/influence claim also fails.
3. VALUE/LITERAL initialization/parent/expression and OUTPUT evidence cannot
   use RO as a required attachment/witness. Preserve all exact frozen null/kind
   rules. Mere occurrence in the full raw original-source execution is NOT itself
   a conflict: a PU declaration/CF guard can execute without supplying a required
   capability, and raw state graphs retain certified dead-body edges.

The producer retains all existing behavioral/attribute/output evidence. It uses
the affected existing V3.5 row's `status` and `scientific_reason_codes`, not a new
field/evidence kind/row, to reject a detected conflict. It records S's
`RO_ACTIVE_OR_REQUIRED_BEHAVIOR_CONFLICT` or
`RO_REQUIRED_MULTIPLICITY_OR_ATTACHMENT` as applicable. An unavailable necessary
check is UNRESOLVED with `RO_REQUIRED_EVIDENCE_OR_EXECUTION_GATE_UNRESOLVED`.
For INITIAL_ACCUMULATOR, nested status/reasons equal the enclosing row as D
requires. The common report failure record uses frozen `PRODUCER_ROW_FAIL` or
`PRODUCER_ROW_UNRESOLVED`, with `detail_reference` selecting that affected row.
Scientific reasons are never translated into weaker binder findings.

S's full `cross_layer_checks` is canonically reconstructed, not redundantly
serialized: combine the region's prior mapping/state/conflict facts with all
existing V3.5 rows for that program, ordered by the pre-bound V3.5 expected index;
partition references by the unchanged three evidence kinds and reconstruct
ACTIVE/required/attachment conflicts from their exact occurrence/path facts.
Missing expected rows or necessary facts makes the full result UNRESOLVED.
Zero relevant rows for evaluation is a structurally justified empty set, not a
synthetic inactive witness; evaluation's required mapping/attachments still apply.
No empty future array in the initial proof asserts that this later join has run.

The stored certificate's mechanical disposition is the stage-7 structural
accounting finding ONLY. It is not a final full-catalog/candidate acceptance
claim until this later join and ALL independent gates close. A later conflict
invalidates scientific use of the claim and fails the report/candidate; it does
not rewrite the prior context or V3.2, delete the certificate, promote the RO
occurrence, reclassify a required occurrence, shrink/expand mappings or joint
membership post hoc, regenerate a contract, or create a replacement candidate.
V3.2 accounting status may remain PASS as a stage finding while V3.5/report/candidate
fails. This is explicit
prospective proof staging, not backward compatibility with S's unsplit payload.

## 8. Shared-invocation E1 prerequisites, logical DAG, and file closure

### 8.1 Exact shared invocation, not a new upstream-output input

When a V3.2 RO proof requires E1 prerequisite facts, the prospectively authorized
scientific orchestration MUST perform the relevant per-program E1 validation
first within the SAME exact supervised invocation that produces E1 and the direct
Coverage-v3 report. "Session" means this one invocation, NOT separate executions
joined by a session label, cache, persisted result, or earlier report file.
The identical bound entrypoint, repository/non-code dependencies, scientific
rules, runtime/packages, observer, compiler identity and execution configuration
MUST legitimately produce both reports under D §§5/5.5/6.1. They share one
execution provenance only when D's exact report-tool/provenance/map-set equality
rules hold. If that architecture cannot be represented, STOP for prospective
review; this proposal supplies no fallback read permission.

All scientific data inputs are candidate-bound frozen inputs. E1 and V3.2 may
use the candidate source inventory as an input; the V3.2 producer's independent
reconstruction occurs in the following logical order. For each matching program:

```text
1. candidate-bound frozen inputs / pre-run input and tool manifests
  -> 2a. E1 original-source validation, compilation and exact five-case execution
  -> 2b. immutable matching E1 logical program row, with PASS prerequisite checked
  -> 2c. unchanged prospective contract
  -> 3. source parse + reconstruction of complete pre-bound inventory
  -> 4. complete typed raw graph
  -> 5. complete raw static state/control analysis
  -> 6. immutable PreDispositionMappingContextV1
  -> 7a. supporting constant/false-body proofs + owner proofs
  -> 7b. per-occurrence RO certificates
  -> 8. final V3.2 four-bucket accounting
  -> 9. V3.5 behavioral / VALUE / OUTPUT evidence + later consistency vetoes
  -> 10. finalized logical report rows / read set / execution provenance / envelopes
  -> 11. candidate evidence manifest and independent closure
```

This is logical dependency order, not permission to read unfinished reports as
input artifacts. No physical finalized E1 report is reread for RO/direct scientific
computation. Later binder consumption of finalized reports remains D's unchanged
closure operation, not a new scientific producer input route. E1 independently
uses original source/cases/compiler inputs, never V3.2 mappings/certificates or
V3.5 outcomes. V3.3 claim validation uses prior inputs/graph and can precede the
context; its final row retains claims without feeding final acceptance upstream.

### 8.2 Immutable matching E1 logical row and exact identity

Use the already-authorized E1 row schema in D §10, row set `program_rows`, and
row identity `RID("E1", [program_type, program_id])`. No additional E1 field,
row set, index, scientific population, output file or reference schema is added.

Before any dependent RO evaluation, the E1 producer deterministically assembles
its complete per-program logical row from the actual pinned-compiler validation
and five-case observations under the frozen E1 rules. Schema, case order, identity
and finding computation are deterministic; actual diagnostic/resource failures
are retained, never normalized away to manufacture PASS or promised away as
universally reproducible physical runtime behavior.

The orchestration fixes the following binding tuple in its private in-memory
invocation context; these are existing input/envelope/provenance identities,
NOT additional serialized E1-row fields:

- exact candidate ID and attempt ID from the exact pre-bound input manifest,
  including that manifest's artifact ID, exact SHA-256 and size;
- exact program type/program ID, condition or evaluation group, and existing E1 RID;
- exact canonical source/reference artifact and logical source record, including
  the source string's exact UTF-8 bytes, content SHA-256 and size;
- exact case-set identity and five frozen case IDs in their pre-bound order, with
  all containing-artifact hashes/sizes and logical input/expected-output content
  identities required by D; no omitted, extra, substituted or reordered case;
- the exact closed pinned compiler identity and applicable bound E1 execution,
  validation/resource/output-limit configuration, together with actual compile,
  phase, diagnostic, normalized-output, case-status and resource/validation facts;
- the current shared invocation's bound tool/configuration and logical execution
  identity; final provenance/file hashes close downstream, not as initial premises.

After E1 finishes the matching row, the orchestration validates its complete
schema and binding tuple, then registers one deep immutable typed-value snapshot
under the existing E1 row identity. Registration is one-time; the RO constructor
has read-only access and cannot replace the row, alter its arrays/references,
or mutate aliased objects. A row not completely established cannot be registered
as a PASS prerequisite. Logical finalization means all required row facts,
including case outcomes/status/reasons, are fixed BEFORE RO reads them; it does
not mean a final E1 report/envelope already exists.

Every diagnostic artifact/reference included in this row must have its exact
identity fixed before snapshot registration. Where it is a file reference, its
bytes must already be finalized before the hash/size is sealed into the row;
the E1 producer supplies the observation/value in memory without an RO/direct
reread of that generated file. No deferred field placeholder may later alter
the logical row. Final provenance/envelope fields belong to the containing
report, not to this immutable per-program row.

The eventual E1 report MUST serialize the exact same complete logical row content.
The supervisor compares each row against its preserved snapshot before finalizing
the report and again before allowing common closure. Comparison is exact recursive
typed-value equality: exhaustive object keys and values, arrays in order, exact
UTF-8 string values, integer values excluding Booleans, and explicit nulls/types.
Object member order/JSON whitespace are serialization only; altered logical values,
missing/extra fields, cases, references, phases, statuses or reasons are mismatches.
Referenced source/case bytes and eventual diagnostic artifacts must also close
under their exact identities. This supplies an acyclic deterministic content
identity without inventing a stored digest field, snapshot artifact, or new RID.

The content identity is the binding tuple PLUS the complete sealed logical value;
it does NOT include its own digest, the E1 report hash, the direct report hash,
or a future provenance/evidence-manifest hash. No self-hash or future file identity
is an initial RO premise. The sealed original value is retained until equality
and final closure checks finish; serialization cannot overwrite the comparator.
Mismatch is FAIL, blocks report/candidate acceptance, and cannot be repaired by
replacing the original snapshot, recomputing RO, or serializing a different E1 row.
Use existing malformed/hash/producer-row/execution failure mechanisms as applicable,
with scientific detail referencing the affected existing E1/V3.2 row; no new
common failure enum is introduced. The binder verifies final row identities,
statuses, source/case/compiler/provenance closure and producer findings; it does
not run a weaker E1 compiler or replace the producer's immutable-row enforcement.

### 8.3 Exact conservative E1 prerequisite

A certificate may receive `mechanical_disposition = REFERENCE_ONLY` ONLY if its
matching immutable E1 PROGRAM ROW is PASS for that exact source/program/type,
candidate/attempt, five frozen cases and pinned compiler/resource requirements.

This requires E1's original-source validation and successful compilation under
the frozen language/subset/binding/type/domain/placement restrictions; exactly
the five pre-bound case outcomes in their frozen order; successful canonical
execution and normalized expected-output agreement for all five; and all
applicable E1 validation, compiler-identity and execution/resource/output-limit
requirements. Every expected case/outcome and its reference identity must match.
A caller PASS label, compiler identity alone, static compilation alone, a subset
of successful cases, or local constant-proof success does not discharge this gate.

Missing/unavailable or unresolved necessary E1 facts block RO as UNRESOLVED.
Known FAIL, stale/mismatched source/case/compiler/attempt identity, forged PASS
or changed immutable content rejects RO as REJECTED/FAIL under the applicable
existing rules. Neither kind supplies a valid RO accounting bucket; retain
the original failed/unresolved evidence and applicable S reasons, including
`RO_REQUIRED_EVIDENCE_OR_EXECUTION_GATE_UNRESOLVED` for missing required gates.
A successful local RO proof cannot waive an E1 failure.

```text
matching per-program E1 PASS
    -> V3.2 structural RO admission
    -> V3.2 mapping closure
    -> V3.5 downstream evidence and consistency vetoes
```

GLOBAL final E1 report aggregate PASS is NOT an initial premise for each
certificate. Other programs' E1 results cannot substitute for the matching row.
Global E1 PASS, including the unchanged 184 rows/920 outcomes and all file,
compiler and execution closure, remains an independent final candidate-level
blocking requirement. Logical per-program PASS cannot assert that global gate
has already passed. Scientific acceptance still requires downstream common
artifact/provenance closure; provisional logical use is not final acceptance.

### 8.4 E1 authority and forbidden cycles

The RO constant-safety kernel remains subordinate to E1. It may prove local
totality, inert bounded constant evaluation, and constant-false guard safety
under S; it MUST NOT replace source compilation, canonical five-case execution,
expected outputs, compiler identity, resource validation, or E1's row PASS.
All S/V semantic preconditions and independent scaffold/overlap/budget/E5 gates
remain mandatory. Five-case agreement alone does not prove semantic inertness.

No E1 row depends on V3.2 or V3.5. There is no V3.2 -> E1 -> V3.2 cycle, no
V3.5 -> V3.2 admission dependency, and no final downstream PASS premise of RO.
All V3.2 graph/state/context/support/region/certificate/final mapping objects
remain internal deterministic records of the direct-report pipeline, not separate
scientific reports invented to obtain addressable references.

### 8.5 Logical handles and downstream file-hash closure

The input manifest is frozen BEFORE scientific evidence execution. Only source
inventory/contract INPUT artifacts are pre-bound there. E1 rows and direct
graph/state/pre-context/support/region/certificate records are producer OUTPUT
records, not retrospectively added input artifacts. "Immutable prior" means
values are fixed and checked before dependent computation, not that the containing
report exists as a pre-run file. Source/case/authority inputs retain exact binding.

During production, existing record IDs are symbolic handles for uniquely
registered immutable values and their designated eventual containing artifact.
E1 handles target only the matching existing E1 `program_rows` RID under the
designated E1 report artifact, never an arbitrary prior report. They become closed
`record_reference` objects for final scientific consumption when the evidence
manifest binds the reports. S's `safety.resource_gate_references` select this
matching E1 row for the prerequisite facts; compiler-semantics references retain
the exact bound authority. Any other necessary resource gate remains blocking
under S/D and cannot be manufactured or waived by this E1 reference.

The semantic catalog's "already-bound context" means identity-fixed prior logical
facts during computation AND exact containing-artifact closure before scientific
acceptance. No temporary output file, report self-hash or unbound handle is final
scientific evidence. Structured content references retain explicit null digest/
size fields, as D requires; logical comparison in §8.2 does not change that schema.

Intra-direct-report references use the direct report artifact ID. Neither report
embeds its own file-level artifact reference/hash. File hashes exist downstream.
Parent/container membership is serialization, not a proof premise. V3.5 references
the final V3.2 ROW ID as D §9.1.1 requires; V3.2 and its early records never
reference final V3.5 rows. Later consistency views are reconstructed downstream
and not stored as upstream references. Logical proof-reference cycles are forbidden.

D §5.5's exact file order remains input/tool manifests -> supervised read set ->
execution provenance WITHOUT report hashes -> finalized report envelopes ->
evidence manifest. The identical shared execution's exact report-type set must
match tool manifest, provenance and report_execution_map; E1 and direct envelopes
bind the same execution provenance only under D's original sharing conditions.
All approved/frozen supplemental schemas/rules are pre-bound through existing
tool-manifest/input-manifest/report authority mechanisms. No execution-map,
report-envelope, reference-object or provenance field is added. Compiler, runtime,
packages, all inputs and all referenced output records close before final PASS.

### 8.6 Exhaustive unchanged read classes; no substitute output permission

D §5.1's four existing classifications remain exhaustive: bound tracked tree,
explicit uncommitted dependency, explicit non-code dependency, or candidate input
artifact. This v2 proposes NO fifth read class and NO read-class override.
In-memory values within the exact shared invocation are not filesystem reads.

No generated scientific output may be disguised as a static lookup, non-code
dependency, producer code, or retroactive candidate input to evade this rule.
There is no permission to turn arbitrary prior scientific reports, E1--E6 outputs,
previous attempts, downstream results, model outputs, or holdouts into new
scientific inputs. Candidate inputs remain outcome-independent and prospectively
bound; no candidate-result-driven methodology/input change is authorized.
Unclassified reads remain UNDECLARED_DEPENDENCY and block closure under D.

D's existing E3, E5 and E6 scientific obligations remain controlling and unchanged;
this amendment grants them no additional output-read capability or execution-
sharing exception. If a proposed architecture for those obligations needs a
different physical read permission, it requires separate prospective review,
not inference from this E1/direct in-memory route. No extra report file, artifact
role, candidate-manifest field, or scientific execution is authorized here.

## 9. Nested versioning and canonical semantic embedding

The enclosing direct report, row-set wrapper, input/evidence manifests and
expected indexes retain D's artifact `schema_version: 1` and exact field sets.
This is lawful ONLY after this prospective amendment and the compatible semantic
catalog are approved/frozen and independently verified. It does NOT imply old
validators can consume the new role/payload. The exact frozen supplemental
authorities select the representation; absent/mismatched supplements make it
unauthorized, not a fallback to permissive old JSON.

`payload_schema_version: 1` is the independently closed V3.2 row revision.
Inventory, graph/state/context, support, shared-region, and certificate objects
have nested integer `schema_version: 1`. Their independent versioning is NEWLY
authorized prospectively by this clarification, not inferred from JSON nesting.
`catalog_version: RO-CATALOG-PROPOSED-1` identifies S's exact semantic authority,
not a schema version or permission to use an unfrozen catalog. Retain that exact
string only if its exact bytes are approved/frozen; a filename/string is not identity.

Semantic admission/domain/grammar changes require a NEW catalog version and
independent review. Future field-shape, RID-family, role-vocabulary, certificate-
structure, selector/order/ownership or staging changes require another prospective
reviewed interface amendment/version, including the affected nested version(s)
as appropriate; they cannot hide under the same authority identity. Common
reference, envelope, row identity/population or provenance changes likewise
require explicit prospective interface review. V2 proposes only §1's enumerated
record-role/inventory-scope/payload/representation amendments while retaining
outer version/shape and all read classes. Future version combinations must be
explicitly approved and bound; neither automatic cross-version adapters nor
unknown fields are allowed. No retrospective reinterpretation or old-validator
compatibility is claimed.

Let C be an occurrence certificate, R its selected shared region, and I its
selected inventory occurrence. The following is the complete S §8 embedding:

| Semantic-catalog field/fact | Canonical proposed location/adaptation |
| --- | --- |
| `schema_version` | `C.schema_version` and `R.schema_version`, both 1 |
| `catalog_version` | `R.proof.catalog_version` |
| `catalog_authority_reference` | `R.proof.catalog_authority_reference`, exact bound approved/frozen S |
| `program_id` | `R.proof.program_id`, equal owning row/input program |
| `source_reference` | `R.proof.source_reference`; logical source-string identity additionally in complete input inventory |
| `source_inventory_reference` | `R.proof.source_inventory_reference`, equal row field |
| `prospective_contract_reference` | `R.proof.prospective_contract_reference`, equal row field |
| `mapping_reference` | `R.proof.mapping_reference` -> `evidence_records.pre_disposition_mapping_context` |
| `graph_reference` | `R.proof.graph_reference` -> `evidence_records.typed_graph` |
| `state_reference` | `R.proof.state_reference` -> `evidence_records.state_control_analysis`, non-null for admission |
| `compiler_identity_id` | `R.proof.compiler_identity_id`, D §6 identity |
| `occurrence` | `C.occurrence_reference` -> `I.occurrence`, S's complete exact object |
| `disposition_class` | `R.proof.disposition_class`, unchanged two-class enum |
| `proof_rule_id` | `R.proof.proof_rule_id`, unchanged matching admission ID |
| `ownership` | `R.proof.ownership`, full owner/member/interior/boundary/context inventory; C must be a unique member |
| `prospective_lookup` | `R.proof.prospective_lookup`, complete lookup covering each owned member; no selector/multiplicity change |
| `influence` | `R.proof.influence`, complete raw/feasible analysis and per-member witnesses, S's exact boundary-proof schema |
| `safety` | `R.proof.safety`; dereference its constant-tree list entries to S's exact proof objects |
| `constant_false_proof` | Dereference `R.proof.constant_false_proof` to FALSE_GUARD_BODY.value; null for PU |
| `cross_layer_checks` | `R.proof.pre_admission_cross_layer_checks` PLUS mandatory downstream join of existing V3.5 behavioral/VALUE/OUTPUT rows under §7; no upstream activity reference |
| `supporting_references` | `R.proof.supporting_references`, exact typed support/record refs in deterministic first-use order |
| `reason_codes` | `C.reason_codes`, S §8.4 order; later conflict scientific codes retained in affected V3.5 rows |
| `mechanical_disposition` | `C.mechanical_disposition`, initial structural accounting finding; full scientific use additionally requires the §7 join and existing gates |

Flattening C/R/I is a deterministic replay view, not a new scientific row or
alternative source. All S facts remain reconstructible; no original S document
is edited here. Full-region facts are checked for EVERY member. This proposed
canonical adapter, including the staged cross-layer join, itself requires review.

## 10. Final V3.2 accounting and failure behavior

Mechanically reconstruct the complete semantic inventory and count VALID
disposition claims per occurrence. The only four final accounting buckets are:

1. `REQUIRED_DIRECT_MAPPING`;
2. `REQUIRED_VIA_AUTHORIZED_EQUIVALENCE`;
3. `AUTHORIZED_EQUIVALENCE_INTERNAL`;
4. `REFERENCE_ONLY`.

PASS requires exactly one valid bucket for EVERY semantic occurrence, all required
occurrences/multiplicities/attachments correspond correctly, all invoked existing
equivalences validate, every RO member/region certificate validates, and
`uncovered_occurrences = []`, `duplicate_dispositions = []`. Claims rejected or
unresolved do not contribute a valid bucket. Supporting references/incident
endpoints alone are not ownership. Unknown or unrepresentable occurrences FAIL.
Neither output agreement, E1 compiler PASS, nor later activity repairs accounting.

NEW closed V3.2 scientific reason additions, ordered as follows:

```text
V32_REPRESENTATION_MALFORMED
V32_REFERENCE_UNCLOSED
V32_REQUIRED_MAPPING_INVALID
V32_AUTHORIZED_EQUIVALENCE_INVALID
V32_PRE_DISPOSITION_CONTEXT_INVALID
V32_GRAPH_OR_STATE_MISSING
V32_RO_CERTIFICATE_INVALID
V32_RO_PROOF_UNRESOLVED
V32_UNCOVERED_OCCURRENCE
V32_DUPLICATE_DISPOSITION
V32_PROOF_DEPENDENCY_CYCLE
```

The row's `scientific_reason_codes` is the unique ordered union: this list first,
then applicable S §8.4 RO reasons in S order. Supporting certificates and other
producers retain their original scientific reasons, referenced rather than erased.
PASS has no failure codes; admitted RO codes may appear as resolved findings.
For UNKNOWN/invalid parse/type facts use V32_REPRESENTATION_MALFORMED and S's
RO_SOURCE_SUBSET_OR_TYPE_INVALID when an RO attempt exists.

| Condition | Required row/report disposition |
| --- | --- |
| Known invalid RO certificate, unsafe/noncatalog form, required-member conflict | V3.2 FAIL; V32_RO_CERTIFICATE_INVALID plus exact S reason; members remain uncovered |
| Incomplete necessary RO premise with no known violation | V3.2 UNRESOLVED; V32_RO_PROOF_UNRESOLVED plus exact S reason; cannot supply a bucket |
| Uncovered source / duplicate bucket or ownership | FAIL for known violation; corresponding V32 code plus RO_UNCOVERED_OR_DUPLICATE_DISPOSITION where relevant |
| Malformed pre-context or changed immutable facts | FAIL; V32_PRE_DISPOSITION_CONTEXT_INVALID (and malformed/reference codes as applicable) |
| Missing graph/state reference | UNRESOLVED if unavailable; FAIL if forged/mismatched; V32_GRAPH_OR_STATE_MISSING / V32_REFERENCE_UNCLOSED |
| Logical proof cycle / attempted self-hash | FAIL; V32_PROOF_DEPENDENCY_CYCLE; never manufacture a hash |
| Missing/stale/failed execution provenance | Frozen interface FAIL/UNRESOLVED reasons; no scientific PASS regardless of row findings |
| Later ACTIVE/attribute/output conflict | Existing affected V3.5 row FAIL and report/candidate FAIL under §7; no upstream remapping |

Known violations take precedence over incompleteness; preserve all applicable
reasons, locations and witnesses. D §8 common failure records retain exactly
`code`, `contract_id`, optional `row_id`, optional `artifact_id`, `detail_reference`.
No new common-interface reason enum is proposed: use existing MALFORMED_REPORT,
hash/population/provenance reasons, PRODUCER_ROW_FAIL and PRODUCER_ROW_UNRESOLVED
appropriately; their detail refs address the failed scientific row/subrecord.
Binder checks closure/validity, never substitutes weaker scientific production.

## 11. Compatibility self-audit and review decisions

| Base delegated-interface item | V2 treatment | Changed? | Reason |
| --- | --- | --- | --- |
| D §7 report envelope / outer schema 1 | Exact existing fields/report types/files | No | Supplemental authority selects nested payload; not old-validator compatibility |
| D §7 row-set wrapper | Exact existing wrapper and expected/observed closure | No | No extra row-set field |
| D §3 expected-row index/digest | Same framing, ordered IDs, count and one V3.2 index | No | Certificates/support are not new indexed scientific rows |
| D §3.3 row identities | Existing RID("V3.2", [program_id]) and existing E1/V3.5 RIDs | No | Program-qualified wrappers do not rename canonical scientific rows |
| Existing scientific populations | 184 V3.2/E1 programs and frozen V3.5/E1 outcome counts | No | No construction, derivation or result-selected population |
| D §2 artifact roles | Existing source-inventory/direct/delegated artifact roles | No | No new artifact role |
| D §2.2 record roles | Add exactly SCIENTIFIC_EVIDENCE | Yes, prospective override | Every consumer must also satisfy §2's type/selector/program/stage/binding checks |
| D §2 file artifact references | Exact existing fields/hash/size policies | No | No self-hash or alternate file identity |
| D §2.2 record references | Exact five fields and structured/string content rules | No | E1/direct handles close under eventual containing artifacts |
| D §5.1 read classes | Existing four alternatives remain exhaustive | No | V1's fifth class removed; no generic scientific-output input capability |
| D §4.1 source inventory scope | Complete raw inventories for 120+32+16+16 | Yes, prospective override | Representation scope only; eligible training projection and all existing IDs/locations retained |
| D §9 V3.2 payload | Exact closed row/internal schemas/context/Option B certificates/accounting | Yes, prospective supplement | Previously unspecified details and explicitly authorized lossless S adapter |
| S §8 canonical representation | Lossless shared support/per-occurrence adaptation plus staged consistency view | Yes, representation/staging only | No semantic admission, ownership or veto change |
| D §9.1 V3.5 rows | Existing final V3.2 row reference, full mapped list, joint membership, status/reasons | No shape/population change | Illegal RO use fails existing downstream row; no upstream remapping |
| D §9.1.2--9.1.4 evidence kinds/null rules | Exact existing kinds and required null/initial-state rules | No | No new evidence kind or attribute mutation |
| D §§2/5.5 provenance/hash order | Input/tool manifests -> read set -> provenance -> envelopes -> evidence manifest | No | Exact shared invocation; logical prerequisites are not future hash premises |
| D §4.1 input manifest timing | Frozen before scientific execution | No | No E1 outcome/report hash or direct output added retrospectively |
| D §10 E1 | Existing row schema/184 rows/920 outcomes/compiler/five-case/resource authority | No E1 schema or authority change; explicit RO-stage prerequisite | Matching immutable per-program PASS first in same invocation; global PASS remains final gate |
| D E3 | All existing scaffold/token/schedule obligations | No | No new scientific-output read permission or waived scaffold/budget veto |
| D E5/E6 | All existing source/mapping/reference facts, gates and compiler-relevance rules | No | No new physical read or execution-sharing permission inferred |
| D §4.2 evidence manifest closure | Existing direct + nine delegated reports, maps, hashes and provenance | No | Same full final closure; no partial scientific acceptance |
| All unlisted requirements | Remain controlling | No | §1's override boundary is exhaustive |

Independent review must explicitly decide:

1. Approve the one SCIENTIFIC_EVIDENCE role with mandatory field-specific typing,
   and supplemental-authority selection under outer schema version 1.
2. Confirm preservation of the accepted 184-program inventory, exact V3.2 payload,
   immutable pre-context, Option B adapter, four-bucket accounting and ordering.
3. Approve §8's exact same-invocation architecture and immutable E1-row equality
   enforcement, matching per-program PASS prerequisite, and unchanged read classes.
4. Confirm E1 remains independent/authoritative and global E1 PASS remains a final
   blocking gate; local constant proofs and logical row use grant no waiver.
5. Confirm the structural-admission/later-veto direction preserves all S semantics,
   with no V3.5-to-V3.2 premise and no post-hoc contract/mapping/certificate rewrite.
6. Approve §1's exhaustive precedence boundary and §12's ordered compatible freezes.

These are pending independent REVIEW decisions, not implementation choices or
empirical findings. No unspecified read architecture may be filled in permissively.
If an unrepresentable fact/incompatible stage is found, STOP for prospective
revision rather than implement a workaround. Scientific conformance/closure remains
`DEFERRED_UNTIL_CANDIDATE_CONSTRUCTION_AND_VALIDATION`.

## 12. Exact prospective freeze relationship and STOP boundary

Recommend ONLY the following sequence AFTER independent review:

1. Independently approve exact bytes of S (the unchanged semantic-catalog proposal)
   and this interface amendment v2. Approval must identify each exact hash/blob/
   size under its stated policy; filenames/version strings alone do not suffice.
2. Freeze interface amendment v2 against exact frozen D/DF identities in §1 and
   exact approved S PROPOSAL bytes. It may bind those existing approved bytes,
   never a not-yet-created semantic-catalog freeze hash or its own future hash.
3. Freeze S against the exact frozen Coverage-v3 authority/freeze, frozen base
   delegated interface D/DF, and newly frozen interface amendment v2 identity and
   freeze. That compatible combination has §1's explicit normative precedence.

The amendment freeze precedes the semantic-catalog freeze; this v2 does not offer
an alternative joint-freeze order. Avoid reciprocal self/future hash dependencies.
The approved S bytes bound at step 2 must be the catalog bytes frozen at step 3;
a byte/version change requires renewed review and compatible binding, never
automatic substitution. Exact identities of the completed pair must be
independently verified before implementation authorization can occur.

Neither partial freeze alone, both freezes by themselves, approval, nor this
proposal commit grants implementation permission. Separate explicit implementation
authorization may be given only after both compatible freezes exist and are
independently verified. No work may begin between incompatible partial freezes.

Only `phase3c_conf1_reference_only_interface_clarification_proposed_v2.md` may
be added and committed in this task, alone in one dedicated commit. Historical v1,
S, D/DF, all other frozen authorities, implementation, tests, evidence,
PROJECT_STATE and protected preregistration remain byte-identical.
No report file, freeze manifest, implementation evidence, fixture, test,
population derivation, E1--E6/V3.2/V3.5 producer, candidate, model or sealed-holdout
inspection/execution is authorized or performed by this specification task.
STOP after the dedicated v2 proposal commit and independent-review handoff.
