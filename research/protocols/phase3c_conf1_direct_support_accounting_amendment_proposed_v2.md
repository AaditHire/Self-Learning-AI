# Phase 3C CONF1 — DIRECT-support accounting v2 proposal

Status: **PROSPECTIVE_DIRECT_ACCOUNTING_SEMANTIC_AND_INTERFACE_REPAIR**.
Lifecycle: **PROPOSED / UNFROZEN / NON-OPERATIVE**.
Prospective profile: **CONF1_DIRECT_SUPPORT_ACCOUNTING_2**, abbreviated D2.
Required binding profile: **CONF1_DELEGATED_CANONICAL_BINDING_1**, abbreviated B1.
Authoring baseline: 839b8e6855e2b7b9a6a10c62c3000b120d5dcce8, main, clean.
Date: 2026-10-03, Asia/Calcutta.

This document proposes a SOURCE_ACCOUNTING_SEMANTIC_REPAIR and the minimum corresponding interface changes. It prospectively supplements the scientific meaning of REQUIRED_DIRECT_MAPPING; it is not merely representation-only and does not claim that the predecessor catalog already authorized this meaning. Nothing in this proposal is operative. Independent review, a separately authorized prospective freeze binding exact bytes and compatibility, and separately authorized implementation remain necessary. This task authorizes only this document and its single-file commit. REFERENCE_ONLY remains DEVELOPMENT_ONLY_PAUSED. Attempt 004 is nonexistent and unauthorized.

## 1. Authorities, exact bindings and prospective precedence

Symbols: V = frozen Coverage-v3; D = original frozen delegated interface; R = frozen REFERENCE_ONLY interface clarification v2; S = frozen closed REFERENCE_ONLY catalog; A = frozen atomic/activity/output repair; G = frozen canonical graph recipe v2; B1 = frozen delegated canonical-binding amendment. Their manifest-bound scientific and interface regions, rather than historical proposal annotations or descriptive appendices, control.

The following identities were independently checked against working bytes and HEAD blobs. The table supplies no authority to the historical DIRECT v1, whose status remains UNFROZEN and NON-OPERATIVE.

| File under `research/protocols/` | Exact-byte SHA-256 | Git blob | Bytes |
|---|---|---|---:|
| phase3c_conf1_delegated_evidence_interfaces_binding_amendment_freeze.json | 0257f8eac42265265f9f88b53633e56c7f9b9c6918f53988675cdcb84bd6de7d | 23d8b3370b26ceec6a076f1061778fa43dad7100 | 40647 |
| phase3c_conf1_direct_support_accounting_amendment_proposed.md | 9325a0cb67f64a529d4df784ab77d9211d569ac19718b9c036c409f427cc472c | 1f14af54db8480ff76b4f27a446acc03fd8acb1c | 41367 |
| phase3c_conf1_delegated_evidence_interfaces_binding_amendment_proposed.md | 2b045a0fb5a7dd22d54397700bab47b88b6857a1ce9b0e22e5f1f5c1ff94595c | 92edf8305f989f9dce55fa26f4f68ef5e661a3c6 | 120981 |
| phase3c_conf1_canonical_contract_graph_recipe_v2_freeze.json | 274c3e39d9dada9939e87c67f72aa71e8a2514ad9a84d35327ac0f6b711c2a51 | 14976b41c8e5e8dba915147fd3a379e891daa7bb | 47206 |
| phase3c_conf1_coverage_v3_atomic_activity_output_amendment_freeze.json | 8a9bfe3c4ad3b687261f486189285156b4c1843e53bfbd20b0bc35c4f07d09e8 | 602b5593287c798e6da297917335795530530a33 | 47346 |
| phase3c_conf1_delegated_evidence_interfaces_freeze.json | bd7a7fc6862ce049c1fdf363f763e1a3a17808132291b9064e3c6f26fb720948 | 32595c5c563fa262679f2bf93ae789f04cde7f72 | 5892 |
| phase3c_conf1_reference_only_interface_clarification_v2_freeze.json | aa8cc827a5c171b388220b0382713982d7a981b6e73b071a2dd12c2cf50ed5ab | 7aa3ca18fe4df6823278e3dbd82eaa6bebfc8e6b | 9936 |
| phase3c_conf1_reference_only_catalog_freeze.json | 769eb09bf85440ac4baaaac90b074e282d87c9a9a5e2d0265aedc17f6c46f7ce | a5781769519f8432c795de0290aa3d15d3722c07 | 14086 |
| phase3c_conf1_structural_transfer_pair_freeze.json | 73eb1c29de6b258de6f7b83867e11ee3f53f67b513f550a666ede550b4e00aa5 | cb643d992bac60db6a3ef208f1e690f6783ac4f6 | 25696 |
| phase3c_conf1_canonical_contract_graph_recipe_proposed_v2.md | 067401333940664502bada12b41d591ef1f554680ba5c9062954b5280e3fd272 | e01d56046711365e3369a7fad67591b1476c4d15 | 117756 |
| phase3c_conf1_coverage_v3_atomic_activity_output_amendment_proposed.md | 8df78d2c96ccb9d6763999a6486202c1c6193bc3638b2c64421c386964cbaad6 | c2e3041297d0e65246943b928054e3d6cce8af9f | 61988 |
| phase3c_conf1_delegated_evidence_interfaces_proposed.md | 9c684eaf6b0099080ddf907630b0a2f8e176e3a882b67875d82f07bd82d64dc5 | 1b6d4d1a825bf9e9d288ca9c3815d1a8e7c78d1a | 76081 |
| phase3c_conf1_coverage_v3_proposed.md | a9fb8350c849ce62e2a673e3ca1f1d5a08f556b7f415687f1e2eabdf356030f3 | 16210d9810d217461b77546c3568c3344c0c770b | 31128 |
| phase3c_conf1_coverage_v3_freeze.json | 8d8f8a37c808d84c740867174e219803712213e672687c42164500f2bca12291 | 28c0fb52fba083e72f87ebfc530fd88ddded5f92 | 3307 |
| phase3c_conf1_paired_scaffold_normalization_proposed.md | ef6063d39319d8b3bd3dbe6bdaa93b474217fa4c37d50ef43dfed5afc8da1fc0 | 475e9de4a0ef3bef23edac1e3631011a20790f5a | 14114 |
| phase3c_conf1_paired_scaffold_normalization_freeze.json | ff1a9610b10ff559ac1859361fb7a31668210ed33e97c2864e592981bd9cfea2 | 9a54e9b525b1795b10f94bf0d0250ae831e6db74 | 2093 |
| phase3c_conf1_input_domain_case_classes_and_training_amendment_proposed.md | bb59ad7cf4cb22c2492427a1fa5a78b0d81398ab16fb0a9cb8229d8c9489182e | 66467ef968e4963dd7a22568100a940871ad304c | 16901 |
| phase3c_conf1_input_domain_case_classes_and_training_amendment_freeze.json | de4a353d58515b5c53210664ea1a642731ac6f1734f23afef4ae512fb8c2627a | 774eb73150f66d2545ddf270cc2f051eddedc156 | 4201 |
| phase3c_conf1_reference_only_interface_clarification_proposed_v2.md | 7a8b69e208bb0a5406cbce0515c4ff95e37aa2d3d8d8e493cda6df5783a2cf25 | e6e12aedf658698a5dd1975894b6e4e7299bd171 | 68503 |
| phase3c_conf1_reference_only_catalog_proposed.md | 7df2a31df6c995d0105e5547aa1d235c6046e9cf141f92321faf92cce3bac682 | 569ed951b121416b4c90240282d96231ce62c6e8 | 52310 |
| phase3c_conf1_slots.json | 5fe76fbc02e9f65174327199c2004f7e51f19a7f3866ae15709744c5274415c2 | 133c9c7275bcedeaf2474e54e61bae47923508ad | 47968 |
| phase3c_conf1_coverage_v3_v2_disposition.md | fb8a385538ddebf95195f099b9ba933bde97d33faf86373a7611e532e8b637d2 | 511843b001f6827c2b46242155485eecc3e429d8 | 10364 |
| phase3c_conf1_ast_adjudication_v2.md | 962960ed6d766b574d2f9812b8ade5b5faa824acfe84e85b520636e2d6667fd9 | c1ffc66d6b8a98645711cd77b6ff49fde5841deb | 4365 |
| phase3c_conf1_proposed_protocol.md | 11e40c821fa26e5a687cea8b8a9a0aa5a0b0c388eae31c99de9814ab2bd80920 | 7ec58f3b4d5fc5827e35e4fbf22712a300240cec | 39663 |
| phase3c_conf1_structural_transfer_semantics_amendment_proposed.md | 362c16faba42246344589fc7f46709b5b83e5bc829a13e1540b04392ddab2fba | eab80c50f3861438add2713689ee81fdbcdf38dd | 40956 |
| phase3c_conf1_structural_transfer_topology_amendment_proposed.md | 9a5e7e80502304e7281a924ef764f9a81b9edd0f9c65fc4a4e0007ad19a2aa2a | 4f624b93d33decf3dd4643067693546fed32499d | 49306 |

Accepted B1: first 119512 exact bytes from offset 0, SHA-256 cab925e51aac6beb6705439d5d0d02cc4414d143d39526089511c2a80f81b94b, Sections 1–27. One LF follows; Section 28 at offset 119513 is descriptive only. Accepted G: first 113400 exact bytes, SHA-256 cb490e9a3a9a2d31b71aec1207f2e191a7b60d9538d81af23cec3d0d610ae2f5, Sections 1–31. Its one LF and Section 32 are outside scientific authority. Accepted A: first 56933 exact bytes, SHA-256 1b72ff7fab98a870882a81797aea5d8a079e7cac74e520d02f373f4e31c794f8. The jointly frozen structural pair operates ONLY AS A PAIR: mathematics first 36321 bytes, SHA-256 a0c99b79001c1a37163d1ff4b06d4518891dca8c12518dc4a3d276b3de5658ac; topology first 44187 bytes, SHA-256 19d9dfc8863e4b2668a6525294fbdb71b479dbf1211d39a95f544b28d30a185d. Their descriptive Section 11 appendices are not premises.

The six predecessor normative regions start at the first byte of the named heading immediately following LF and extend through EOF, excluding that preceding LF. Convert CRLF to LF only for the first three records below; use exact bytes for the last three.

| Authority | Region start heading | Region bytes | Region SHA-256 | Approved commit |
|---|---|---:|---|---|
| V | ## Design record: why v2 is superseded | 29178 | 884a8ac3f859268e16dfa0d8f0d477211c7a273fca58666c7eba018265d8c15a | e641cce3a7fd127b87d0d0ccb22edfe74e411cf0 |
| Paired normalization | ## Scope and source precedence | 12217 | 5aa404949a8cc580b9ca3ff4aff7325195e172a7cfa82c69317280597c73b25c | 4a5f947843d0fb49bb7a8ccf62c8411ce37b5b94 |
| INPUT_DOMAIN | ## Authority and scope | 14669 | b9dc3d6ca22778ab0b3e734270fb20a00b4d88e0602f24fe77b2112335df8167 | e662fae4596c4a5f25cd262e479933ba59ed38fc |
| D | ## 1. Authority, scope, and precedence | 74717 | 26c642e17bb5218727c0cd09f370eaf1ac6c4de35006fa9801d701ece81cf16d | 027427ed5567aa75e10e35a0b3ed342516094ce9 |
| R | ## 1. Authority, scope, and prospective effect | 68141 | a2bf9185686171e566d4a0e35a9780eaab45eb99e1ffdfbd4dfa49dcf22d9a00 | 9f23a3cfb0862cfdfaad0332f1260ab00dadae2f |
| S | ## 1. Prospective status, authority, and scope | 51739 | 25c04bb3b319314cce744d5c83a491dae97c1596c4e38a19d639bab3ca9a58d5 | e56533364c38bf5c96b5c521081b3c368449c952 |

The ledger has declared raw-byte SHA-256 5fe76fbc02e9f65174327199c2004f7e51f19a7f3866ae15709744c5274415c2 and CRLF-to-LF SHA-256 83436eecda3affe813b785e868e3f8936fa59afc35ded0eb6a54290edb41dc88. Working bytes match the former; committed LF bytes and the declared normalized policy match the latter. Preserve both policies. No conversion is authorized by D2.

The exact transitive chain is B1.bound_authorities -> G/A/D/R/S/joint freeze; A.bound_authorities -> V, paired normalization, INPUT_DOMAIN and their controlling manifests/regions; D.freeze.upstream_authorities -> CONF1 protocol, slot ledger/design, v2→v3 disposition, AST-v2 and the remaining upstream identities. S.bound_authorities and R's three predecessor bindings remain subordinate and exact. Repeated references must agree; no moving-path replacement or historical fallback is permitted.

If later independently accepted and frozen, D2 has precedence ONLY for this exhaustive list:

| Predecessor provision | D2 prospective supplement | Unchanged boundary |
|---|---|---|
| S §7 item 1, REQUIRED_DIRECT_MAPPING — exact required source correspondence; R §4/§10 selector-direct representation | Add mandatory canonical-context source accounting as the second DIRECT proof basis | S §§2–6, PURE_UNUSED/CONSTANT_FALSE, safety, influence and no-dead-code veto unchanged |
| R §4 plus B1 §3's additive V3.2 field | V3.2 payload version 2, one added direct_required_support array | Same row, existing selector/equivalence/internal arrays, all other row sets/indexes |
| R §5.3 | PREMAP version 2, one added direct_support_candidates array and amended residual membership | Complete immutable pre-RO facts, no outcomes/final dispositions |
| R §§8.5/9 and B1 §§3/4/23 | Explicit D2 container discriminator, narrowly staged correspondence leaves, typed reference/consumer closure described below | Existing logical-handle/file-hash policy, B1 field bodies, provenance and behavioral evidence |
| R §10 | Closed D2 reason additions and context completeness in accounting | Existing failure precedence, four buckets and all independent scientific checks |
| All other authority | No override | G construction, selectors, ontology, treatments, keys, evidence, populations, E5 and endpoint |

Predecessor bytes, including S/R/B1/G, remain unchanged. D2 does not freeze, refreeze or amend a file in place. B1's freeze explicitly did not establish a DIRECT-v2 accounting rule; this proposal supplies that separate prospective repair.

## 2. Exactly four buckets; exactly two DIRECT bases

The complete final disposition enum remains:

| Final bucket | Valid ownership |
|---|---|
| REQUIRED_DIRECT_MAPPING | Union of valid SELECTOR_SATISFIER entries and valid MANDATORY_CONTEXT_SUPPORT entries |
| REQUIRED_VIA_AUTHORIZED_EQUIVALENCE | Existing verified required realization under one frozen V3.3 rule |
| AUTHORIZED_EQUIVALENCE_INTERNAL | Existing completely inventoried internal structure of that verified equivalence |
| REFERENCE_ONLY | Existing S admission and R certificates, with every independent veto |

The two mutually exclusive proof bases inside DIRECT are exactly SELECTOR_SATISFIER and MANDATORY_CONTEXT_SUPPORT. The existing direct_required_mappings array denotes the former; the new direct_required_support array denotes the latter. SUPPORT, DIRECT_SUPPORT and CONTEXT are not final buckets. SUPPORT_ONLY_TASK_ESSENTIAL remains G/B1 classification metadata.

Ownership is assigned to original raw semantic occurrence IDs, not keys, extents, owners, canonical context IDs or proof references. One source occurrence receives one valid final claim. Distinct occurrences remain distinct even with equal owner, key, text or extent. Repeated references are not claims.

## 3. Atomicity is preserved without exceptions

G §§3/4/18–21 establish that every emitted task-essential typed NODE and EDGE is ATOMIC_SELECTOR_REQUIRED. Each has its own exact RequirementBinding, selector, multiplicity and attachments; the additional INPUT_DOMAIN and certified local-J profiles keep their separate requirements. There are zero support-only canonical NODEs or EDGEs.

A CGPREREQ with prerequisite_record_kind NODE or EDGE records an additional constructive association; it never demotes that occurrence. If a raw source occurrence realizes an atomic canonical NODE/EDGE, its selector/direct-or-equivalence accounting remains independently required. Support cannot repair a missing selector, missing constituent, type mismatch, missing directed port, attachment or multiplicity. A dependency edge never inherits its head NODE's requirement.

D2 distinguishes the canonical record being supported from the raw source record's parser kind. R's semantic source inventory still consists of NODE/EDGE occurrences. A raw NODE/EDGE can supply a genuine static contextual association only if the uniform frozen parser and exact G context establish that association without a separately required canonical operation. This is not authorization for a new raw operation or edge type. Unknown source forms fail closed; an executed read, write, conversion, package assembly or operand operation cannot be hidden as metadata.

## 4. Positive eligibility chain and accepted context forms

The only positive construction chain is:

ProgramBinding -> ContextBinding -> contextual_component_reference -> exact immediate owner_requirement_references -> complete CGPREREQ associations -> pre-RO ContextCorrespondence -> exact original source facts.

This is a typed chain of already-constructed frozen G/B1 facts, not an inferred necessity metric. Start from the complete pre-run ProgramBinding.contexts array. Reconstruct its equality to G; then independently pair its records with source. Source extras cannot create a context, owner or prerequisite.

G's closed contextual_records context_kind values are STATIC_BINDING, ORDERED_DECODED_PACKAGE, EXPRESSION_RESULT_REFERENCE, INITIAL_POST_DEFINITION, COMPLETION_PERSISTENCE and PROVENANCE. Mandatory states, phases, scientific order metadata, exact attachments and prerequisite wrappers retain their own G schemas. Fixed SPLIT "|" configuration is its exact DOMAIN_ROLE attachment; it does not create a C requirement. Context exists only where the actual G clause constructs it.

| Constructed mandatory context | Exact immediate owner/association to verify |
|---|---|
| Static binding/lifetime/definition | Actual same-state initializer, writer, read, reset, set, carry or prior requirement identified by G |
| Original ordered decoded package | Actual package VALUE_TO_OPERATOR and consuming INDEX_READ requirements, four original decoded producers in scientific order |
| Expression-result/final-output association | Defining result requirement and actual consuming display requirement, exact output port |
| INITIAL/POST definition | Exact committed definition and same storage/state/phase identity; not an extra STATE_VIEW read |
| Completion/persistence | Actual completed-P read/final operand and directly specified phase-boundary/member requirements |
| Phase/stage/order | Actual member requirements identified by that exact scientific ordering |
| INPUT_DOMAIN configuration/connectivity | Actual INPUT_DOMAIN root requirement and its complete connectivity association |
| SPLIT separator | Actual SPLIT requirement, exact separator configuration |
| Value/output/initialization attachments | Own attribute owner and exact prospectively fixed parent, initializer or display counterpart |
| Provenance/prerequisite wrappers | Exact record/requirement identified; each wrapper's immediate owner and pairing role/position |

These are consumed G §21 associations, not a D2 graph-building table. No output reachability, arbitrary dependency, liveness alone, producer flag, activity, outcome, compilation, symmetry, presence in both conditions, later RO failure or subjective necessity judgment establishes eligibility.

## 5. SELECTOR_SATISFIER stays scientifically unchanged

An existing valid direct entry exactly satisfies one or more canonical selectors. It retains complete required_occurrence_ids, exact types, roles, directed attachments, static multiplicity and original source correspondence. Multiple compatible views may share one genuine raw occurrence in one entry only under existing G/B1 correspondence rules. Every requirement still has its independent MappingView and obligation.

D2 neither changes the existing three-field direct entry nor gives it additional scientific credit. A failed, unresolved, missing or only partially satisfied selector cannot be discarded so that its source becomes context-only. If exact source/selector incidence is unresolved, support ownership is unresolved and RO remains blocked. Mere same-key resemblance is not selector incidence.

## 6. Conjunctive MANDATORY_CONTEXT_SUPPORT predicate

For a raw occurrence o, VALID support requires ALL twelve conditions:

1. o is exactly one original semantic occurrence in the complete, independently reparsed pre-bound inventory, retaining wrapper, ordinal, coordinates, extents, endpoints, port, types and binding identity.
2. At least one valid immutable pre-RO ContextCorrespondence explicitly identifies o as an actual source fact of that context.
3. Every claimed correspondence resolves to its exact pre-run ContextBinding, with the same program and exact containing-artifact binding.
4. That ContextBinding resolves to accepted mandatory non-NODE/non-EDGE G content. Its complete ProgramBinding/G population is checked.
5. Exact role, state, phase, field, port, configuration, definition, lifetime, expression association and scientific order agree wherever specified. Unspecified facts cannot be invented.
6. The complete nonempty immediate owner set and every relevant CGPREREQ agree with G, including construction_clause, prerequisite_record_kind/id, owner_requirement_occurrence_id, pairing_role and pairing_position.
7. o does not independently realize a required selector for which the existing selector basis controls. Selector incidence/ownership cannot be erased.
8. o is not legitimately owned by REQUIRED_VIA_AUTHORIZED_EQUIVALENCE or AUTHORIZED_EQUIVALENCE_INTERNAL.
9. Complete verified equivalence/internal inventories show that o lies outside their controlled transformed structure. No migration or new equivalence is allowed.
10. Support and owner realizations are established before RO, independently of V3.5, output/activity, final RO or candidate findings.
11. Frozen slot, exact G construction, source grammar, no-padding and paired-scaffold constraints permit its presence; source-driven or paired redundant additions fail.
12. The complete source/context relation and independent owner realization are mechanically reconstructable from permitted prior facts, with no proof cycle.

A known violation is INVALID; an incomplete necessary premise without a known violation is UNRESOLVED. Neither supplies a valid bucket. Interface validity alone does not establish this scientific predicate.

## 7. Exact source-fact incidence; no dependency-footprint expansion

B1 ContextCorrespondence has exactly record_id, context_binding_reference, source_fact_references, owner_requirement_references, validation. Its Ref[] source_fact_references supplies source/configuration/binding/order/state facts; it is not itself a disposition array.

For D2, every raw semantic occurrence claimed to directly realize a context must appear as its explicit matching-program Ref(V32OCCRECORD) in source_fact_references. This minimal reference-use refinement exposes existing identity without adding a B1 field or a raw occurrence. Independently verify that this occurrence supplies the clause's actual contextual fact, rather than merely proving a neighboring operation. Other permitted references supply the precise binding, configuration, expression order, definition or state premises.

Referencing a whole V32GRAPH, V32STATE, V32BINDING or V32DEFINITION does not automatically support all its nodes, reads, writers, dependency edges or ancestors. A binding's declaration/read/write lists and a definition's writer are checked for their stated roles; only explicitly identified raw fact occurrences receive possible ownership. No recursive traversal of proof dependencies creates support membership. A Ref to original source-string content may establish an exact configuration/spelling fact under B1's existing source reference rules, but creates no semantic occurrence ID.

A contextual fact that is metadata only, with no separately inventoried semantic occurrence, still requires complete valid ContextCorrespondence and canonical completeness. It creates no DirectRequiredSupportEntry. Presentation associations remain nonsemantic and receive no fifth bucket. Conversely, if a semantic occurrence supplies a context fact, omitting its explicit raw reference makes correspondence incomplete; the consumer cannot guess ownership from an extent or from a text explanation.

Missing facts are unavailable, not empty successful proofs. A source extra without an existing ContextBinding is unavailable for support even if live or useful. A context without exact source realization blocks readiness. These rules expose existing source identity and prevent padding; they do not introduce a necessity test.

## 8. Selector and equivalence precedence

First independently reconstruct all existing selector/direct, authorized-equivalence and internal correspondences under frozen R/G/B1 rules, preserving unresolved claims. No D2 rule changes conflicts between selector-direct and equivalence ownership: inconsistent double ownership still fails under R.

A valid selector-direct occurrence that also realizes context remains solely SELECTOR_SATISFIER. Its ContextCorrespondence remains mandatory and independently validated, but does not create a support claim. A verified equivalence-required or equivalence-internal occurrence retains that existing bucket even when it supplies exact context. Context support cannot pull any transformed member out of the invoked equivalence.

Only a contextual raw occurrence outside existing selector/equivalence ownership can use MANDATORY_CONTEXT_SUPPORT. Invalid/uncertain equivalence ownership cannot be silently treated as absent: preserve its claims, invalidate or mark the context unresolved, and block RO as required. No new equivalence rule, algebraic rewrite or special mixed-bucket permission is supplied.

## 9. Independent owner anchoring, including all-equivalence owners

A context's owner relationship is canonical and immediate. Its required atomic owners exist in the pre-run G contract and have their own BINDREQ/V32REQ records. Each has an independently reconstructed MappingView. Support neither creates that requirement nor supplies its selector.

For VALID support every immediate owner MappingView must be MATCHED, interface-valid, CLOSED and complete for its frozen multiplicity and attachments. NO_CORRESPONDENCE is a resolved missing owner realization and invalidates support; UNRESOLVED or missing prior mapping leaves support unresolved. Retain available facts and all reasons. Global canonical completeness independently blocks PASS for every missing owner/atomic requirement. MATCHED is established from original source, typed correspondence and attachments; it does not require a final bucket decision for its contextual prerequisites. Thus the owner cannot depend on the support claim that it anchors.

An owner's mapping_method can be DIRECT or AUTHORIZED_EQUIVALENCE. The all-equivalence case is determined by frozen authority: G §21 attaches context to an owner_requirement_occurrence_id, not to a source disposition; G §25 expressly allows the closed V3.3 correspondences with preserved roles/interfaces; R §4 permits those required mappings; B1 §9 MappingView/SourceMappingInstance expressly represents both methods. Therefore a complete lawful equivalence-realized owner anchors its context just as a lawful direct-realized owner does, provided the exact contextual identity/attachment is preserved. Requiring an additional DIRECT source owner would contradict those accepted owner realizations.

This does not make an equivalence's transformed/internal member support-owned. If the contextual source fact is already equivalence-controlled, §8 retains that bucket and no support entry is created. If the separate contextual occurrence is outside those complete memberships, it may pass the same twelve-condition predicate with those equivalence-realized owners. An equivalence that fails to preserve the required contextual fact cannot anchor it. There is no treatment-dependent exception or new equivalence precondition. Unknown case facts remain UNRESOLVED; the methodology introduces no unresolved scientific choice.

## 10. Shared facts and complete contextual realization

One original raw occurrence may source-back several compatible mandatory ContextBindings only if each exact B1 correspondence independently proves its role. Its support entry retains the complete ordered set of relevant ContextCorrespondence references and receives one DIRECT disposition.

Several distinct raw occurrences may jointly realize one context if its actual frozen role requires those distinct source facts; each otherwise-unowned valid occurrence gets its own entry, and the context correspondence retains the complete ordered facts. Extra repetitions do not become necessary because they share an owner. A required single fact cannot be padded with redundant copies. Equal extents, names or keys do not prove identity.

The context set and source facts are complete even where selector/equivalence precedence eliminates the need for support entries. Context completeness and source bucket completeness are different obligations and neither substitutes for the other.

## 11. Zero atomic, evidence or E5 credit; no activity criterion

Each support entry contributes zero selector satisfaction, atomic multiplicity, CGREQ, CGKEY, V3.5 expected row, V3.4 coverage, ACTIVE/COVERED finding, VALUE_OR_LITERAL evidence, OUTPUT evidence and E5 capability identity. It has no key, selector, evidence_kind, multiplicity, required_occurrence_ids or activity payload field. It cannot inherit any scientific property from an immediate owner.

A static configuration, definition/order/lifetime fact or a context associated with a branch executing zero times on a case can be mandatory. Support has no activity test, changing-output trial or dynamic-count threshold. Frozen canonical construction establishes necessity; actual future V3.5 findings remain independent. Five support facts cannot repair one missing required NODE/EDGE.

## 12. Exact conformity and prospective padding veto

Validate the complete G contract against Recipe_v2(FrozenSlotSpecification), using only frozen authorities/ledger/condition inputs. Verify complete B1 contexts, owners and prerequisites against that exact graph. Then validate the exact source realization and every independent source/scaffold restriction.

Reject redundant context prospectively added to both treatments, predeclared unnecessary support nodes/edges, candidate-specific graph additions, source-driven graph additions, unauthorized condition-specific context, output-reachable noncanonical extras and structures invented to close accounting. Paired presence never establishes necessity. Exact clause-owned conformity excludes additions without inventing a global graph-size minimization requirement.

Preserve actual required scaffold initialization, reads, writes, carries, conversions and ordered uses even if a future case overwrites or never visits them. No context claim waives protocol no-dead-code rules, AST-v2/template controls, E3 protected literal/source comparison, token parity or budgets. No filler is admitted to balance treatments.

## 13. Exact profile and version compatibility

The only new DIRECT profile is the exact string CONF1_DIRECT_SUPPORT_ACCOUNTING_2. It requires B1=CONF1_DELEGATED_CANONICAL_BINDING_1, G schema_version=2/recipe_version=CONF1_CG_RECIPE_V2, and the exact frozen authorities in §1. Profile spelling alone is not authorization.

| Object/container | D2 version/field change | Preserved |
|---|---|---|
| candidate_input_manifest, D §4.1 + B1 §3 | Append mandatory direct_accounting_version=D2 | schema_version=1, all predecessor/B1 fields |
| Coverage-v3 direct-report envelope | Append mandatory direct_accounting_version=D2 | schema_version=1, binding_version=B1, eight row sets and binding_records |
| candidate_evidence_manifest, D §4.2 + B1 §3 | Append mandatory direct_accounting_version=D2 | schema_version=1, ten-report execution map |
| Producer-tool manifest, D §5.4 + B1 §3 | Append mandatory output_direct_accounting_version; D2 iff report_types includes COVERAGE_V3_DIRECT, otherwise explicit null | output_schema_version=1 and output_binding_version's B1/null rule |
| Existing V3.2 payload only | payload_schema_version=2; append direct_required_support | Existing canonical_obligation_binding_reference, unchanged row ID/index |
| PreDispositionMappingContext only | schema_version=2; append direct_support_candidates | Existing V32PREMAP ID, graph/state/requirement/member fields |
| DirectRequiredSupportEntry | New closed nested value selected by D2 and containing schema version 2 | No RID family, row, index, artifact role or independent schema discriminator |
| G canonical graph/contract content | No change | schema_version=2 and exact frozen bytes/recipe |
| Raw inventory; typed graph; static state | No change | nested schema_version=1 |
| R V32ROSUPPORT; RO shared-region/certificate | No field change; V32ROSUPPORT remains downstream of sealed PREMAP and required MultiViewLink checks | schema_version=1, exact frozen proof variants/catalog; no D2 field or production-stage change |
| B1 input, canonical binding records and evidence variant bodies | No field change | B1, existing nested versions/types and StatusState |
| Other seven direct row sets; nine delegated report envelopes; expected indexes; compiler identity; execution provenance | No change | Already-frozen versions/field sets |

The four profile markers are the minimal analogue of B1's existing markers: the input selects methodology before execution, the producer declares the supported output profile, the report identifies its closed payload, and the final manifest/binder closes the same declared profile. They must agree. No new profile field is needed in an unchanged canonical-binding inventory, raw graph/state, authority component, expected index or RO certificate. Its exact containing input/report profile and the consumer's schema-version check select interpretation. A producer emitting no direct report uses explicit null in the tool field; it cannot claim D2 behavior for another report.

For D2 all 184 V3.2 rows use payload version 2 even with an empty support array. A present PREMAP uses version 2. Unknown, absent, mixed or contradictory D2/B1/version combinations fail interface closure before scientific use. No automatic migration, permissive schema union or fallback to version 1 is allowed. Old validators must reject D2 and its unknown fields/version, never ignore support. Historical profile-absent/schema-1 objects remain valid only within their original frozen scope and cannot establish D2 readiness.

This is a prospectively reviewed interface methodology refinement under R §9. It does not silently reuse schema version 1 for a changed nested object. B1's canonical/evidence meanings and bodies remain frozen; only the named enclosing fields and narrowly described pre-RO timing/reference-use rules receive D2 precedence.

## 14. Closed conventions, identities, ordering and reference closure

All listed D2 fields are mandatory and exhaustive. Reject duplicate JSON keys, unknown/missing fields, wrong types/enums, implicit nulls/defaults, invalid integer/Boolean coercion, duplicate ordered-set references, ambiguous selectors and unbound/cross-program references even in a FAIL record. Ordered arrays are non-null. Empty arrays are allowed only under their specified population rule; an unavailable proof is not a successful empty proof.

Reuse exact D/R/B1 references. FileRef has exactly artifact_id, artifact_role, path, sha256, size_bytes, hash_policy. Ref has exactly artifact_id, record_id, record_role, content_sha256_utf8, content_size_bytes_utf8. Structured references retain both content fields explicit null; source-string refs retain exact unescaped UTF-8 digest/size. No role is added: SCIENTIFIC_EVIDENCE remains subject to exact RID-family, object type, container, owning program/row, stage and containing-artifact/provenance checks. SOURCE/REFERENCE/COVERAGE_CONTRACT retain their meanings. DIAGNOSTIC cannot be relabeled into proof.

Reuse D's exact length-framed RID; all original IDs, raw inventory coordinates/ordinals/extents and G IDs remain unchanged. The existing scientific row is RID("V3.2",[program_id]); PREMAP is RID("V32PREMAP",[program_id]); a source wrapper is RID("V32OCCRECORD",[program_id,occurrence_id]). BINDCONTEXTMAP is RID("BINDCONTEXTMAP",[program_id,context_binding_id]); BINDREQ and BINDMAP are their unchanged B1 IDs. No support-entry ID or new scientific row family is introduced. Nested support values are selected only in the named array of the owning row/PREMAP by unique source_occurrence_id; they are not standalone reference targets.

Use predecessor field order, append only the listed new fields at the end of amended containers, and retain exact predecessor types/optional permissions. New support/validation fields use the table order below. Serialization is lossless UTF-8 without BOM, LF, one final LF, compact JSON comma/colon separators for new objects, explicit null where permitted, minimal decimal integers, exact Unicode without normalization. Arrays preserve scientific order. Do not rewrite externally bound artifacts to this convention.

Support entries order by raw inventory ordinal. Context references order by the owning ProgramBinding.contexts order. Owner MappingViews order by G requirement order, deduplicating the complete union across contexts. Prior evidence refs order by first field traversal: source wrapper; same-program graph; state; then each context's available source-fact refs in B1 order; then each owner's actually needed prior correspondence proofs in owner/source-instance order. Deduplicate exact reference identity only; do not collapse scientifically distinct facts. Referenced binding/configuration/order evidence must itself preserve its original scientific order.

No record embeds its own digest or final report hash. Immutable logical handles fix exact value, type and designated eventual artifact before first proof use; containing-file closure follows R §8.5 and D §5.5. Parent/container membership is serialization, not a proof premise. Resolve only declared registries/containers, never recursive arbitrary JSON or coincident IDs.

## 15. V3.2 payload version 2: complete field set

The exact field set, in serialization order, is R §4's field set with B1's existing addition, then the single D2 array:

~~~text
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
canonical_obligation_binding_reference
direct_required_support
~~~

payload_schema_version is integer 2. All fields besides direct_required_support retain R/B1's exact types, container selectors, null rules and scientific meanings, except scientific_reason_codes has the explicitly enumerated D2 additions in §22. Status remains PASS/FAIL/UNRESOLVED. The same pre-bound BINDROW obligation binds the row. evidence_records still has exactly typed_graph, state_control_analysis, pre_disposition_mapping_context. A genuinely unavailable object and its matching reference are explicit null only in a non-PASS row; a malformed present object is a rejecting structure.

Existing direct entries remain exactly source_occurrence_id, required_occurrence_ids, evidence_record_references, with nonempty complete requirement IDs in G order. Authorized-equivalence entries remain exactly those three fields plus equivalence_rule and equivalence_internal_occurrence_ids. Internal entries remain exactly source_occurrence_id, equivalence_mapping_source_occurrence_id, evidence_record_references. The six closed equivalence labels remain ALPHA_RENAMING, INTEGER_CONSTANT_FOLD, PURE_COMMUTATIVE_ORDER, COMPARISON_OPERAND_SWAP, BOOLEAN_AND_INDICATOR_PRODUCT_LOCAL_PAIR and BOOLEAN_OR_INDICATOR_SUM_POSITIVE, with every frozen precondition.

direct_required_support is an ordered array of the closed entry in §16. It contains exactly the VALID support candidates of the immutable PREMAP v2, serialized unchanged. An empty array is legal only if no valid support candidate exists; it says nothing about whether contexts are complete. Invalid/unresolved candidates remain in PREMAP and reasons, never contribute a bucket, and cannot disappear to improve readiness.

R's complete source_offsets, graph_paths, evidence_record_references, uncovered and duplicate schemas/order remain. Extend the row's existing unique prior-evidence union only with the actual D2 context/owner/source proof references; never include the row itself or future dependents. No scientific row set, expected-row index or population changes.

## 16. Complete closed DirectRequiredSupportEntry

The same closed entry represents a prospective candidate and, if VALID, the final support DIRECT claim. Every field is mandatory; no field permits null.

| Field, in order | Exact type | Validation/meaning |
|---|---|---|
| source_occurrence_id | nonempty string | Exact original occurrence ID in this program's complete raw semantic inventory, not wrapper/CGREQ/key |
| proof_basis | MANDATORY_CONTEXT_SUPPORT | Literal second DIRECT basis, never a bucket |
| context_correspondence_references | Ref(BINDCONTEXTMAP)[] | Nonempty; complete ordered context incidence set from §7/§18; exact same-program registered context_correspondences |
| owner_mapping_view_references | Ref(BINDMAP)[] | Complete ordered unique union of immediate-owner views derived by the join below; nonempty for VALID; unavailable missing views may leave an incomplete/empty list only with blocking validation |
| prior_evidence_references | Ref[] | Nonempty typed prior evidence set under §14/§20, always including the exact raw source wrapper; complete actual graph/state/source/configuration/binding/definition/equivalence premises |
| support_status | VALID / INVALID / UNRESOLVED | Independently reconstructed twelve-condition result; no ACTIVE/PASS disposition finding |
| validation | DirectSupportValidation | Exact four-field object below; format/resolution and scientific reasons are separate |

The exact associated ContextBindings, canonical components, immediate BINDREQ/CGREQ owners and CGPREREQ facts are bound by deterministic dereference, rather than redundant copied scientific fields:

For every context reference, resolve its sole ContextCorrespondence -> context_binding_reference -> sole ContextBinding -> contextual_component_reference and prerequisite_references. Its owner_requirement_references must equal the ContextBinding's complete owner list. Each owner Ref(BINDREQ) resolves to the same ProgramBinding and canonical G requirement; each CGPREREQ owner_requirement_occurrence_id must equal the exact dereferenced CGREQ, with matching prerequisite record, kind, construction, role and position. Reconstruct the complete relevant direct wrapper set independently from G. Then the support entry's owner_mapping_view_references must equal exactly the deduplicated union of the BINDMAP records for those owners.

This join binds all associated ContextBinding/requirement/prerequisite facts without introducing fake requirement/key/selector IDs or duplicating their scientific fields. Missing, foreign, transitive, invented or incomplete owners fail or remain unresolved as §22 determines. A known nonexistent required owner/view is INVALID; an independently required view not yet available is UNRESOLVED and blocks readiness. Unavailable references cannot be forged; preserve available refs and the missing-premise reason.

Every prior_evidence_reference must select an already-prior fact under its existing frozen role, type, selector, program and stage: this program's original source/string records, complete source inventory, exact V32OCCRECORD and source binding/configuration/order facts; its V32GRAPH/V32STATE/V32DEFINITION/V32REQ; or an exact frozen authorized-equivalence proof/certificate leaf already permitted before PREMAP and final V3.2 acceptance. That last permission retains the existing proof schema and reference/selector policy; it does not create an equivalence-proof object or admit a later V3.3 finding. The exact B1 ProgramBinding, RequirementBinding and ContextBinding are consumed through the closed join above; ContextCorrespondence and MappingView are separately typed refs in the entry's named fields. Applicable source-site/mapping leaves are the existing prior values reached through those registered mappings, not newly addressable records. This is the complete D2 pre-RO evidence universe; no new proof object, RID family or scientific rule is introduced to replace an RO proof.

V32ROSUPPORT belongs to the frozen downstream RO supporting-proof stage and MUST NOT be an input, directly or through another proof record, to ContextCorrespondence, MappingView used for D2 support admission, DirectRequiredSupportEntry, direct_support_candidates, PREMAP-v2 support membership or still_unmatched derivation. This prohibits every V32ROSUPPORT variant: TYPED_SUBTREE, CONSTANT_TREE, FALSE_GUARD_BODY and SOURCE_SUBINVENTORY. No V32ROSUPPORT, V32ROREGION or V32ROCERT may establish D2 support membership. B1's general proof-reference permission for R supporting records does not override this narrower D2 stage restriction.

No E1 success, final V3.2/V3.3 finding, V32PREMAP root as its own premise, final RO certificate/region/disposition, BINDALL, execution/event/trial evidence, V3.5, output evidence, ProgramOutputCheck, model outcome or gate result is a support premise. If a necessary support fact cannot be established from the legitimate already-prior universe, the claim remains UNRESOLVED; do not speculate, create a replacement proof object or move RO supporting-proof production upstream.

Static information that may later also occur in an RO supporting proof is independently reconstructed for D2 from original source/parse/typed graph/static-state facts: exact subtree membership from the original parse and V32GRAPH; binding/state/order from inventory and V32STATE/V32DEFINITION; fixed literal/configuration facts from original source; and applicable frozen equivalence validity from its proper prior proof leaves. A static false-body/control fact may be an original source-control premise, never an RO-admission conclusion. Later serialization of similar information inside V32ROSUPPORT does not make that downstream record a D2 premise or permit copying its conclusion backward.

No fields named required_occurrence_ids, canonical_contract_key_id, evidence_kind, required_multiplicity, selector or activity are permitted in this entry. Owner refs identify independent obligations; they do not satisfy them.

## 17. DirectSupportValidation: separate layers and closed states

DirectSupportValidation has exactly the following fields. It is a D2 nested validation object, not a modified B1 StatusState.

| Field | Closed type | Rule |
|---|---|---|
| interface_status | PASS / FAIL / UNRESOLVED | Schema/type/reference result only |
| resolution_status | CLOSED / MISSING / AMBIGUOUS / UNRESOLVED | Resolution of necessary support/owner facts |
| interface_reason_codes | D2 interface-code array from §22 | Ordered unique; no BIND scientific translation |
| scientific_reason_codes | D2 scientific-code array from §22 | Ordered unique applicable support reasons |

VALID requires interface_status=PASS, resolution_status=CLOSED, both code arrays empty, all twelve scientific conditions established and complete exact owners. Resolved INVALID can be interface-valid PASS/CLOSED with scientific failure codes; it has no valid bucket. UNRESOLVED has at least one applicable unresolved code and a non-CLOSED resolution. A known scientific violation plus missing facts is INVALID with all scientific reasons retained and unresolved premises still blocking readiness. A format/reference failure yields interface FAIL with an applicable interface failure code and support INVALID; preserve any independent unavailable facts. Interface FAIL prevails over interface UNRESOLVED; known scientific INVALID prevails over scientific UNRESOLVED. These are separate precedence rules, not a scientific PASS inferred from format PASS.

Interface PASS requires empty interface codes and CLOSED resolution. Interface UNRESOLVED requires a non-CLOSED resolution and D2_SUPPORT_REFERENCE_UNRESOLVED; scientific known violations, if any, still make support INVALID. CLOSED must never be asserted with missing premises. A present malformed entry cannot be legalized by writing INVALID. Its malformed structure causes report/binder rejection; retain failure detail under existing D common records.

B1 ContextCorrespondence/MappingView/MultiViewLink validations keep the frozen StatusState and BIND reasons, unmodified. Their existing scientific reasons remain attached to those records. D2-specific findings belong in the support validation and PREMAP/V3.2 reasons; they are not inserted into B1's closed code vocabulary.

## 18. Complete PreDispositionMappingContextV2

The exact field set, in predecessor order plus one appended array, is:

~~~text
schema_version
record_id
program_id
prospective_contract_reference
source_inventory_reference
graph_reference
state_reference
required_occurrences
direct_mapping_candidates
authorized_equivalence_correspondences
equivalence_internal_members
still_unmatched_occurrence_ids
context_status
scientific_reason_codes
direct_support_candidates
~~~

schema_version is integer 2. V32PREMAP identity and all existing schemas remain R §5.3, including each required_occurrences entry's exact fields record_id, requirement_occurrence_id, canonical_contract_key_id, prospective_contract_reference, required_multiplicity, attachment_references. With G, the requirement ID is the existing CGREQ, never a fallback invented for context.

The original three mapping/member arrays retain all existing claims and available proof, including unresolved claims; they are not outcome-filtered. graph/state/contract/source refs retain their existing roles. direct_support_candidates uses §16's exact schema, ordered by source ordinal. context_status remains CLOSED/UNRESOLVED. CLOSED means all necessary pre-RO memberships, exact mandatory-context realizations and ownership/conflict premises are established consistently, not that residual extras or final accounting pass. Independently retain every atomic requirement's mapping finding: a resolved selector failure still prevents eventual PASS under R, and an unresolved membership or required owner/context premise blocks RO. CLOSED does not relabel a missing atomic selector as satisfied. Known invalidity makes context non-CLOSED and eventual row FAIL; incomplete premises without known invalidity make it UNRESOLVED. Retain all applicable existing and D2 scientific codes.

Compute complete context incidence by independently reconciling every pre-run ContextBinding, its one B1 ContextCorrespondence and every exact source_fact_reference (§7). For an otherwise unowned raw occurrence with available explicit context incidence, include one candidate, retaining the complete ordered incidence set and complete available independent owner facts. This includes INVALID/UNRESOLVED attempted candidates, not only positive ones. Established selector/equivalence-owned facts create no support candidate but retain mandatory context correspondence. Uncertain selector/equivalence ownership with available context incidence creates an UNRESOLVED candidate unless a known violation makes it INVALID; it cannot obtain a valid support claim by assuming absence.

A malformed or extra submitted support claim, claim outside reconstructed incidence, duplicate candidate or invented source ID is rejected rather than silently dropped. Missing ContextCorrespondence/source facts do not permit a guessed source ID or a fabricated candidate. Their complete mandatory ContextBinding/ContextCorrespondence population and global reasons independently block context closure even when no candidate can yet be named. Missing prior records use the predecessor explicit-null/non-PASS rule where the object cannot be represented. No empty support array asserts that such obligations were satisfied.

The PREMAP contains no V32ROSUPPORT premise, final RO disposition/certificate, final V3.2 PASS, V3.5 activity/attribute/output result, ProgramOutputCheck, model outcome or candidate acceptance. D2 support candidates and residual membership are fixed in immutable PREMAP before any V32ROSUPPORT production, RO region proof or RO certificate evaluation; PREMAP is serialized unchanged. Final selector/equivalence/internal arrays equal the valid pre-context claims; final direct_required_support equals its VALID support entries exactly. Negative/unresolved claims are preserved in PREMAP and cannot be edited after RO or output.

## 19. Deterministic residual and final accounting

Let I be the complete source-ordered semantic inventory. Independently reconstruct D_s = valid selector-direct membership, E = valid required-equivalence membership, E_i = valid equivalence-internal membership, and D_c = valid mandatory-context support membership. The last is determined solely by §§4–18.

still_unmatched_occurrence_ids is exactly I minus the union of D_s, E, E_i and D_c, retaining original source order. No V32ROSUPPORT, V32ROREGION, V32ROCERT or final RO fact enters this computation. Membership and residual are sealed before RO supporting proofs are constructed or replayed. Invalid/unresolved claims are not positive membership. Conflicts, unresolved ownership/correspondence or missing mandatory context make PREMAP non-CLOSED and block RO admission; listing a residual does not make it eligible. A known mandatory contextual incidence that failed support cannot be diverted to RO to escape its obligation.

Only the CLOSED residual is eligible for S/R consideration. S's independent prospective non-requirement lookup still protects every required state/control/dataflow, attachment, initial state, decoder and output fact. A mandatory context is protected even if its source is not in a support array due to precedence or a failed/unavailable proof. No RO constructor may create, revise or remove support.

Final DIRECT membership is D_s union D_c, one bucket. These sets are disjoint; each array has one entry per owned source occurrence. A selector-owned contextual fact belongs solely to the selector array. A deliberately submitted second support entry is a duplicate/conflict, not ancillary correspondence. The existing duplicate_dispositions shape remains occurrence_id, claimed_buckets, claim_record_references. Both direct arrays project to REQUIRED_DIRECT_MAPPING; repeated same-bucket claims remain duplicates. Use the original typed Ref(V32PREMAP) for support-candidate claim provenance in duplicate records, since support entries have no RID; the occurrence_id and reconstructed unique array selector identify its claim. Do not mint a reference family.

PASS requires uncovered_occurrences=[] and duplicate_dispositions=[], exactly one valid final bucket per semantic occurrence, complete required selector/equivalence multiplicity/attachments, complete mandatory contexts, all equivalences/internals valid and every RO member/region proof and independent veto satisfied. The support-array union supplies no extra scientific gate/row.

Known invalid accounting/conflicts yield FAIL even if other premises are unresolved; preserve all reasons and unresolved readiness blocks. Unavailable necessary facts without a known violation yield UNRESOLVED, never a positive bucket. Output agreement, E1, activity or final acceptance cannot repair missing accounting.

## 20. Acyclic pre-RO staging and narrow B1/R reference precedence

D2 refines R §5.3's early context construction and B1 §23's lifecycle steps 2–3 only as necessary to assemble immutable support candidates. It changes no scientific meanings or B1 object field sets.

1. Validate frozen inputs and complete G/B1 canonical bindings. Fix the raw inventory and parsed graph/static-state records independently.
2. Fix each V32REQ leaf and the available selector/equivalence/internal correspondence facts under R. These leaves are eventually contained in PREMAP but do not depend logically on the PREMAP root or final row.
3. Independently fix MappingViews from those leaves and prior graph/state/source/equivalence proof, without V32ROSUPPORT. Establish the compatible same-occurrence view facts needed for sharing. Fix every ContextCorrespondence from canonical contexts and exact prior source facts, likewise without V32ROSUPPORT. Validate their full scientific identity.
4. Reconstruct support incidence, complete immediate-owner mapping union and every candidate finding. Seal PREMAP v2 exactly once with the original claims, support candidates, reasons and residual.
5. Build/validate each required B1 MultiViewLink against the sealed PREMAP and prior compatible MappingViews, before RO admission. Its mandatory pre_context_mapping_reference remains the exact unchanged V32PREMAP Ref. Reconcile the complete link population and all memberships.
6. Only with complete valid pre-RO closure and the already-sealed D2 residual, construct/evaluate the existing downstream RO supporting proofs, V32ROSUPPORT, under R's unchanged schemas and topological proof order. No D2 field is added and no RO proof production stage is moved upstream.
7. Construct/evaluate the existing RO regions and certificates from those downstream supporting proofs and the sealed context, retaining all frozen S/R safety, admission and resource prerequisites. No RO proof may change D2 support membership or the residual.
8. Close final V3.2 accounting. Downstream BINDALL/V3.5/output/evidence/coverage follow unchanged scientific dependencies and final file closure.

Steps describe future proof dependencies, not execution performed or authorized by this proposal. A missing/invalid MultiViewLink after sealing blocks RO/final readiness and is retained in its B1 record and final reasons; it does not rewrite PREMAP or its support membership. An impossible/incompatible alias is already a known correspondence violation at step 3. The later link cross-check cannot retroactively manufacture support.

In D2, MappingView/ContextCorrespondence used upstream of support may refer to prior V32REQ/graph/state/source/binding/definition and applicable prior equivalence proof leaves, but must not use V32ROSUPPORT, V32ROREGION, V32ROCERT, the current whole V32PREMAP root, final V3.2/V3.3 findings or a MultiViewLink containing that PREMAP reference as a premise. This is an explicit narrowing of B1's otherwise broad V32PREMAP/R-supporting-record proof-reference permission at these fields, preserving the frozen downstream RO stage. pre_context_required_reference still selects its already-fixed V32REQ leaf; its physical parent array is not a logical proof dependency.

MultiViewLink is consumed where applicable as the required post-seal pre-RO consistency check. Its prior MappingViews/source proof establish actual compatibility; the link itself is not an upstream admission premise of the support entry. The normative logical dependency order is prior frozen inputs/source/graph/state/equivalence leaves -> RequirementBinding / MappingView / ContextBinding / ContextCorrespondence -> D2 support candidate reconstruction -> immutable PREMAP v2 -> required post-seal B1 MultiViewLink consistency checks -> RO supporting proofs (V32ROSUPPORT) -> RO regions/certificates -> final V3.2 accounting -> downstream V3.5/output/etc. Pre-run RequirementBinding/ContextBinding records remain canonical inputs; this logical order does not postpone their construction.

No D2 support, PREMAP-membership or residual constructor may depend on an RO supporting proof; no RO proof may feed backward into D2 membership. There is no PREMAP -> MappingView -> support -> PREMAP cycle and no PREMAP/support dependency on V32ROSUPPORT. Independent RO replay reconstructs and compares D2 support membership and the residual from the same legitimate pre-RO facts before constructing/replaying any RO supporting proof. It cannot use a just-created RO proof to revise sealed PREMAP. No temporary file, own hash, mutation after first use or fake negative evidence is required.

Static source dataflow may contain cycles; the record-proof DAG may not. A later activity/output/gate result may consume final mapping but never feeds an upstream support/context decision. The same logical values close into exact report files and evidence manifest under R §8.5/D §5.5.

## 21. Bidirectional completeness and multi-view closure

All three conjunctions are mandatory:

A. Every G atomic requirement retains complete independent selector/direct-or-authorized-equivalence correspondence, exact multiplicity and attachments.
B. Every pre-run mandatory ContextBinding retains complete exact source realization in its one ContextCorrespondence, including metadata facts and contexts supplied by already-accounted selector/equivalence occurrences.
C. Every raw semantic source occurrence has exactly one lawful final bucket.

A complete source inventory with missing canonical context is FAIL/UNRESOLVED. A complete graph with unaccounted source is FAIL/UNRESOLVED under known-violation/incompleteness precedence. Neither direction substitutes for another. Proof-reference presence alone is not completeness.

Frozen B1 sharing permits one genuine raw occurrence to satisfy several compatible selector views in one selector entry. The same occurrence may also source-back compatible contexts without a second owner. Context references never add required_occurrence_ids. Distinct conversions, writers, phases, operand ports, states and occurrences remain distinct; exact actual computation, definition, order and attachment proof are required. MultiViewLink population and replay remain B1's complete selector-view population; shared context facts alone do not mint an extra selector link, source entry or execution.

D2 leaves BINDALL and V3.5 joint-intervention mapping derived from valid selector/equivalence correspondences for the key. It must not include context-support-only entries as key destinations. It retains all required views, actual instances and zero-execution sites under B1's existing science.

## 22. Minimal reason vocabulary and deterministic status aggregation

D2 introduces these interface reasons in the stated serialization order. They belong only to DirectSupportValidation; existing D common failure records keep their original code/contract_id/optional row_id/optional artifact_id/detail_reference shape.

| Interface code | Exact condition | Interface result |
|---|---|---|
| D2_SUPPORT_RECORD_MALFORMED | Unknown/missing field, type/enum/null/order/duplicate-key/closed-schema violation | FAIL |
| D2_SUPPORT_REFERENCE_UNCLOSED | Wrong RID family/type/container/program/stage, foreign/forged/ambiguous selector, stale or mismatched exact artifact | FAIL |
| D2_SUPPORT_REFERENCE_UNRESOLVED | Necessary expected prior fact/reference genuinely unavailable, without a known reference violation | UNRESOLVED |

Unknown/mixed container profile or nested versions use existing MALFORMED_REPORT/authority/hash/provenance failure handling; they are not new scientific reasons. B1 binding errors retain their exact BIND interface codes. Interface failure never proves scientific necessity, inactivity or absence.

D2 scientific reasons, in this exact order, are:

| Scientific code | Deterministic support/context finding |
|---|---|
| V32_D2_CONTEXT_UNBOUND | Claimed context cannot resolve to the exact prospective ContextBinding; known absence/foreign claim INVALID, unavailable necessary reference UNRESOLVED |
| V32_D2_CONTEXT_NONCANONICAL | Known context outside exact G construction, canonical NODE/EDGE demoted, extra source-driven or padded context; INVALID |
| V32_D2_CONTEXT_SOURCE_MISMATCH | Resolved wrong source fact, role/state/phase/field/port/configuration/definition/order/grammar association; INVALID |
| V32_D2_OWNER_RELATION_INVALID | Known missing/invented/transitive/incomplete immediate-owner/CGPREREQ relation or NO_CORRESPONDENCE owner; INVALID |
| V32_D2_SELECTOR_SUPPORT_CONFLICT | Known selector incidence/ownership submitted as support, or a second direct-array claim; INVALID |
| V32_D2_EQUIVALENCE_SUPPORT_CONFLICT | Verified required/internal equivalence member submitted as support or transformed structure migrated; INVALID |
| V32_D2_CONTEXT_REALIZATION_INCOMPLETE | Known omitted mandatory context/fact/reference/owner set; INVALID. Genuinely unavailable required facts additionally retain PROOF_UNRESOLVED |
| V32_D2_SUPPORT_PROOF_UNRESOLVED | Necessary source/context/selector-equivalence absence/owner proof missing or ambiguous without a known violation; UNRESOLVED |

Scientific malformed/support reference rejection additionally retains existing V32_REPRESENTATION_MALFORMED/V32_REFERENCE_UNCLOSED as applicable in PREMAP/row. A V32ROSUPPORT/RO-region/certificate reference used to establish D2 membership is a known stage violation: D2_SUPPORT_REFERENCE_UNCLOSED yields interface FAIL/support INVALID; retain V32_REFERENCE_UNCLOSED and V32_PROOF_DEPENDENCY_CYCLE where a cycle is attempted or present. A necessary fact unavailable from legitimate prior inputs uses existing D2_SUPPORT_REFERENCE_UNRESOLVED where applicable and V32_D2_SUPPORT_PROOF_UNRESOLVED, leaving support UNRESOLVED without moving proof production upstream. No new reason code or scientific meaning is introduced by this staging correction. Missing owners caused by unavailable MappingViews use PROOF_UNRESOLVED rather than asserting a nonexistent canonical owner. A known context exists but demonstrably absent source fact is a resolved INVALID mismatch/incompleteness; missing analysis is UNRESOLVED. These distinguish scientific absence from lack of proof.

DirectSupportValidation.scientific_reason_codes uses only the eight D2 codes above. Original equivalence/mapping/B1 reasons stay in their original records and are retained in the owning PREMAP/row where applicable, rather than copied into this closed D2 field. PREMAP and V3.2 scientific_reason_codes preserve R §10's ordered eleven V32 codes first, then its existing S §8.4 reasons in S order, then these eight D2 additions. Each is an ordered unique union; never discovery/thread order. R/S/B1 reason vocabularies are not modified internally.

Known violations take precedence over incompleteness. Preserve every applicable reason, location, proof witness and unresolved premise. A schema-valid but scientifically invalid support object can have interface PASS while V3.2 is FAIL. A purely unresolved necessary claim supplies no valid bucket and leaves V3.2 UNRESOLVED unless another known violation requires FAIL. PASS requires all closure checks and no failure/unresolved reasons; existing resolved RO-admission findings may remain under R's unchanged rule. Independent E1/provenance/report/binder failures still block readiness irrespective of row findings.

## 23. Complete producer, replay, adapter and binder contract

Every consumer that previously treated DIRECT membership as selector-only must select the exact D2 profile and preserve the distinct bases inside the same bucket.

| Consumer | Required D2 change | Reject/block condition |
|---|---|---|
| V3.2 producer | Independently reparse raw source, validate exact G/B1, produce complete selector/EQ/internal leaves, contexts, support candidates, sealed PREMAP and final valid support array | No source-driven graph/context; no final/outcome premise; no partial inventory |
| Pre-disposition consumer | Validate closed PREMAP v2, all mandatory contexts/owners and the four pre-RO memberships before reconstructing residual | Unknown/mixed version; missing context; support conflict/unresolved ownership blocks RO |
| RO eligibility constructor | Receive already-sealed v2 residual and valid support membership, plus complete protected G/B1 context facts; only then may existing V32ROSUPPORT and unchanged S proof machinery run | Cannot ignore support, reclassify failed mandatory context, consume RO support as a D2 premise or rewrite PREMAP |
| Independent RO replay | First reconstruct support candidates/findings/membership and residual from the same legitimate pre-RO inputs and compare exact PREMAP; only afterward construct/replay V32ROSUPPORT and unchanged RO rules | Producer/replay disagreement, omitted support or backward use of a newly created RO proof invalidates closure |
| R §9 C/R/I flattening adapter | Keep unchanged S field embedding; mapping_reference resolves version-2 PREMAP under D2, including all support/context facts when checking prospective lookup and protected requirements; keep RO supporting records downstream | No flattened view that erases support, substitutes final status, uses selector-only residual or presents V32ROSUPPORT as an upstream D2 proof |
| General mapping/replay export adapter | Preserve both direct arrays and exact references; DIRECT population is their disjoint union, while required-ID/key projection uses only existing selector/EQ mappings | Cannot drop support, rename it RO or invent required IDs for it |
| Final delegated binder | Check identical input/tool/report/evidence profile, exact frozen authority, closed schemas, hashes/provenance, complete prior membership and final-array equality | Old validator must reject; no permissive unknown-field handling or binder-generated scientific support |
| Expected-row closure | Consume the same eight direct row sets, same 184 V3.2 rows and existing expected index/BINDROW references | No support row/index/CGREQ/CGKEY/V3.5 row; existing population errors remain |
| B1 canonical-reference consumer | Exact ProgramBinding -> ContextBinding/component/owner/prerequisite and BINDMAP/BINDCONTEXTMAP reconciliation, with D2's explicit pre-RO reference staging | Cross-program borrowing, arbitrary ancestor, missing wrappers/views, cycle or incomplete mandatory context |
| B1 multi-view consumer | Original compatible-view science, mandatory full links after PREMAP seal and before RO; match same raw ID and selector obligations | Equal extent/key insufficient; incomplete/invalid link blocks, never rewrites sealed support |
| BINDALL/V3.5 consumer | Original selector/EQ key realization and complete actual intervention destination rules | Support-only occurrence cannot enter keyed mapped_occurrences through owner inheritance |
| V3.4/V3.6/E5/downstream reports | Consume unchanged scientific inputs/formulas/populations; retain complete source/graph/context facts | No support-derived key, activity, output, symmetry exception, signature omission or novelty feature |

The R semantic embedding remains exact: shared RO region proof.mapping_reference still selects V32PREMAP; its schema is unchanged because Ref's shape is unchanged. prospective_lookup's existing required_state_control_dataflow_matches and value_output_attachment_matches retain complete frozen protected-context facts; the DIRECT union/complement is reconstructed from the referenced D2 PREMAP, not a new catalog field. A support candidate cannot be accepted or deleted by RO prospective lookup. RO support/certificate variants retain schema 1 because no field changed.

Adapters are deterministic views of the same closed records, not substitute scientific sources or new execution authority. Every export must carry its existing containing artifact/profile association; schema-1 tools cannot be used as a partial D2 adapter. Flatten/replay/export adapters must not present any RO supporting record as an upstream D2 proof, including through a reconstructed view or alias. Replay uses pre-RO membership exactly, not V32ROSUPPORT, final V3.2 PASS, the final support array alone, an RO finding or activity.

D2 is future consumer methodology only. No producer, validator, replay adapter, binder or schema has been implemented or executed by this proposal task.

## 24. B1 preservation and source-accounting dependency boundary

B1 remains the sole canonical identity/context interface authority. Consume its exact ProgramBinding, RequirementBinding, ContextBinding, ContextCorrespondence, MappingView, MultiViewLink, original source identity and closed references. D2's complete differences are the four enclosing profile markers, one V3.2 array/payload version, one PREMAP array/version, local support validation/reasons and §20's narrowly necessary staging/reference-use precedence.

B1 evidence schemas, behavioral classes/typed payloads, actual execution/event/path/trial records, runtime value-parent evidence, output declarations, ProgramOutputCheck and V3.5 variant bodies/formulas are unchanged. No D2 code is added to StatusState's BIND vocabulary. No additional canonical-binding artifact, source inventory, graph, state, case, execution, declaration, expected index or scientific record population is authorized.

Support proofs use only exact frozen G/B1 input and permitted prior raw/graph/static-state/source/context/owner/authorized-equivalence facts. MultiViewLink contributes its post-seal pre-RO cross-check where B1 requires it. V32ROSUPPORT of every variant, V32ROREGION, V32ROCERT, V3.5, behavioral/output evidence, ProgramOutputCheck, final RO dispositions, model outcomes and candidate gates are forbidden support premises. Static information also needed by later RO proofs is reconstructed independently from legitimate earlier facts, never borrowed from downstream supporting records. Compiler success and resource-gate success never prove support; existing later S/E1 resource prerequisites remain unchanged for RO.

## 25. REFERENCE_ONLY is scientifically unchanged and remains paused

S's PURE_UNUSED and CONSTANT_FALSE admission classes, closed constant/false-guard proof kernels, grammar, whole-program bindings, state/control/dataflow/decoder/output influence protection, complete owner-region membership, live-influence vetoes and later cross-layer consistency checks remain unchanged. D2 only changes which original source occurrences are already lawfully accounted for as required context before RO eligibility.

D2 makes no live mandatory occurrence RO-admissible, broadens neither admission class and weakens neither dead-code/no-padding nor treatment-symmetry rules. A difficult or unavailable context proof is not prospective non-requirement. R certificates continue to cover only a CLOSED residual, never required/support/equivalence-owned members. No RO implementation is resumed and no historical development fixture is rerun.

The 17 protected RO development drafts are opaque integrity controls with their existing DEVELOPMENT_ONLY/STOP status. Their prior counts, overlap diagnostics, test outputs and scripts are not scientific support premises, not canonical context construction authority and not evidence of closure.

## 26. Treatment, ontology, rows, population and endpoint preservation

| Frozen item | D2 result |
|---|---|
| Research question | Unchanged CONF1 acquisition/presentation contrast; no learning-process redesign |
| Conditions | ISOLATED and COMPOSITION unchanged |
| Manipulated source contrast | Sole marked ADD/MUL contrast and existing local pair-joint exception unchanged |
| Paired scaffold | Protected source/literals/roles/loop/order/cases/prompt/schedule/token/budget controls unchanged; no added filler |
| Training population | 120 programs, 60 per condition; no instances constructed/recounted here |
| Evaluation population | 64 references: 32 primary, 16 primitive sanity, 16 structural transfer; no holdout/label inspection |
| Canonical graph | Exact G Recipe_v2 and full state/phase/context representation unchanged |
| Categories | SEMANTIC_PRIMITIVE, GENERIC_CONSTRUCT, API_DECODER, ATOMIC_OPERATOR, VALUE_OR_LITERAL, OUTPUT_CATEGORY, ATOMIC_CONTROL_DATAFLOW |
| Edge labels | INPUT_TO_DECODER, VALUE_TO_PREDICATE, PREDICATE_TO_CONTROL, PREDICATE_TO_INDICATOR, VALUE_TO_OPERATOR, OPERATOR_TO_ACCUMULATOR, CONTROL_TO_UPDATE, LOOP_CARRY, PRIOR_STATE_TO_UPDATE, ACCUMULATOR_TO_OUTPUT |
| V3.2 scientific rows | Same 184 rows and same RID/index, source accounting supplemented prospectively only |
| V3.3 | Exact six-rule catalog and certificates unchanged |
| V3.4 | Every evaluation-essential atomic key needs existing same-domain active exposure in both conditions; support gives zero witness |
| Supplemented V3.5 | Same training-program × own-canonical-key rows, three evidence kinds, all-instance joint intervention, typed trials/parents/output obligations; support has no activity row |
| V3.6 | Existing treatment scope and sole certified local-pair exception unchanged |
| E5 | Same full graph-isomorphism or complete certified semantic collision under consistent role bijection, fixed-offset novelty and completeness rules |
| E5 comparisons | 32 × 120 = 3840 primary-versus-training comparisons; no structural/sanity additions |
| Endpoint/E1–E6 | Original feasibility/audit/primary contrast and reporting boundaries unchanged |

Context support creates no E5 capability node, key or signature feature beyond the already-frozen complete G context representation. It does not prune original source, AST, raw graph, unused members or state/phase/order facts from E2/E4/E5. Document/hash equality is not the E5 graph/function test. No signature, comparison, row or certificate instance is constructed here. The strongest demonstrated empirical claim remains Level B — parameterized behavioral acquisition; this proposal supplies zero empirical evidence or candidate feasibility claim.

## 27. Historical non-reinterpretation and authorization

Historical DIRECT v1 remains UNFROZEN/NON-OPERATIVE with the exact identity in §1. It supplies design history only. Its graph-element support idea and connected-direct-anchor language do not override newly accepted G atomicity or B1 contexts. Do not amend or freeze v1.

Attempts 001–003 and their rejection remain unchanged. DEVELOPMENT_ONLY diagnostics and old uncovered edges are not reclassified as supported, rescued or scientifically accepted. No rerun, retrospective admission or revised count is authorized.

Attempt 004 remains nonexistent/unauthorized within the repository observation boundary. No candidate, graph, contract, requirement, key, scientific row, case, evidence, signature, population instance or output is created. No V3.4/V3.5, E1–E6, compiler validation, model training/inference or scientific producer/replay execution occurs. No sealed holdout or expected-label semantics is read or hashed. Read-only identity verification and text/schema self-review of this proposal are the only checks described by this task.

## 28. Paper-only threat adjudication

ACCEPT below means the described accounting relation is permitted subject to every stated condition, not that a candidate passes. REJECT is a known violation and yields INVALID/FAIL or interface rejection. UNRESOLVED is unavailable necessary proof with no known violation and blocks readiness/RO. These are normative paper cases, not constructed fixtures.

| # | Threat/case | Deterministic result and rule |
|---|---|---|
| T01 | Dependency EDGE inherits head NODE requirement | REJECT: separate canonical EDGE selector/port/multiplicity required; §3 |
| T02 | Atomic canonical NODE/EDGE missing own selector, labeled support | REJECT: zero support-only atoms; no repair by context |
| T03 | Arbitrary incident edge with a required endpoint | REJECT as support: incident identity is not frozen ContextBinding incidence; its independent selector/extra accounting remains |
| T04 | Output-reachable source extra | REJECT as support absent exact mandatory context; reachability supplies no positive eligibility |
| T05 | Redundant context added to both treatments | REJECT: exact G conformity/no-padding veto, paired presence insufficient |
| T06 | Candidate-specific or source-driven context | REJECT: cannot construct context from source extras |
| T07 | One occurrence submitted as selector-owned and support-owned | REJECT duplicate/conflict; selector ownership retained, ancillary valid context still recorded |
| T08 | Support occurrence already equivalence-required/internal-owned | REJECT support claim; preserve existing verified equivalence ownership |
| T09 | One genuine raw occurrence supplies several valid compatible contexts | ACCEPT one DIRECT support entry with complete ordered context refs and independent owners; no raw duplication |
| T10 | Several raw occurrences supply one context | ACCEPT only the complete distinct facts actually required by that canonical role; redundant extras REJECT, incomplete proof UNRESOLVED |
| T11 | Wrong phase/state/field/port/definition/order/configuration | REJECT on established mismatch; unavailable necessary comparison UNRESOLVED |
| T12 | Context has a known missing/invented canonical owner | REJECT; owner cannot be manufactured by support |
| T13 | Transitive/output ancestor substituted for immediate owner | REJECT; exact complete G direct owner/CGPREREQ relation required |
| T14 | Context exists but exact source fact demonstrably absent | REJECT incomplete realization; unavailable source analysis UNRESOLVED |
| T15 | Source fact exists with no canonical ContextBinding | REJECT support; no source-driven context creation |
| T16 | Valid mandatory static/zero-execution context | ACCEPT if all static/context/owner facts validate; no activity requirement |
| T17 | Support assigned V3.4/V3.5 ACTIVE/COVERED/attribute/output credit | REJECT; zero evidence/key/destination credit |
| T18 | Support inherits owner's key/multiplicity/selector IDs | REJECT malformed or scientific ownership; no such fields/credit |
| T19 | Mandatory context diverted to RO because support is difficult | REJECT admission; mandatory lookup protected; unresolved proof blocks RO |
| T20 | Final RO certificate used to create support | REJECT proof stage/cycle; immutable pre-RO membership required |
| T21 | Activity/output/model/gate success selects support | REJECT forbidden premise, regardless of observed result |
| T22 | Extra source structure present symmetrically | REJECT support absent exact canonical incidence and no-padding permission |
| T23 | Unknown/mixed DIRECT or B1 profile | REJECT interface; no fallback/partial interpretation |
| T24 | Old validator silently ignores support array | REJECT consumer compatibility; old validator must reject D2 |
| T25 | Replay/flatten consumer omits support or uses selector-only residual | REJECT closure; exact producer/replay pre-RO membership required |
| T26 | Duplicate DIRECT/equivalence/RO disposition, including within DIRECT | REJECT; one claim per raw occurrence and uncovered/duplicate checks |
| T27 | All immediate owners legitimately equivalence-realized | ACCEPT support for a separate otherwise-unowned exact contextual source fact when all frozen role/interface facts preserved; §§8–9 |
| T28 | Owner MappingView NO_CORRESPONDENCE | REJECT support; independent missing selector remains FAIL |
| T29 | Owner MappingView unavailable/UNRESOLVED with no known violation | UNRESOLVED; cannot assert support VALID, canonical PASS or RO eligibility |
| T30 | MappingView -> current PREMAP -> support -> MappingView cycle | REJECT; use sealed prior leaves and post-seal MultiViewLink cross-check |
| T31 | Whole graph/state/binding reference used to own all dependency members | REJECT; explicit actual raw fact incidence and exact role required |
| T32 | Equal extents collapse distinct conversions/writers/phases/ports | REJECT; actual source/semantic identity controls |
| T33 | Selector/EQ-owned source also supplies complete context | ACCEPT its original bucket plus mandatory ancillary ContextCorrespondence; no support entry |
| T34 | Complete source buckets but missing mandatory context | REJECT if known omitted/absent; otherwise UNRESOLVED, never PASS |
| T35 | Complete canonical correspondence but unaccounted raw semantic extra | REJECT known uncovered source; no implied support or ignored bucket |
| T36 | Context source fact is metadata with no additional semantic occurrence | ACCEPT complete exact ContextCorrespondence with no support entry; no fabricated source record |
| T37 | Raw source NODE/EDGE supplies permitted static association | ACCEPT only when exact parser/G context confirms no separately required canonical operation is being demoted; unknown syntax or executed extra REJECT |
| T38 | PREMAP edited after RO or outcome, support final array differs | REJECT immutable context/consumer equality violation |
| T39 | Missing mandatory MultiViewLink after PREMAP seal | UNRESOLVED if genuinely unavailable; REJECT known omission/mismatch; block RO/final without rewriting PREMAP |
| T40 | Unknown source grammar legalized by a support label | REJECT original parse/type restriction; support cannot introduce syntax/operations |
| T41 | RO supporting proof used to establish D2 support membership | REJECT stage violation/cycle: no V32ROSUPPORT variant may be a direct or indirect D2 membership/residual premise |
| T42 | CONSTANT_TREE/FALSE_GUARD_BODY information needed by both D2 and later RO | ACCEPT only when D2 independently reconstructs the underlying static fact from permitted earlier source/parse/graph/state/equivalence inputs; the later V32ROSUPPORT record is not a D2 premise |
| T43 | D2 support remains unprovable without a future RO supporting proof | UNRESOLVED: retain missing-premise reasons; do not speculate, invent a replacement proof object or move RO proof production upstream |
| T44 | RO replay uses its just-created V32ROSUPPORT to change sealed PREMAP membership | REJECT immutable pre-RO membership and stage violation; replay must reconstruct D2 first and may never feed an RO proof backward |

## 29. Exhaustive introduced-choice catalog

This table catalogs the introduced semantic/serialization/interface decisions. Consumed G/B1/V/D/R/S scientific meanings are not additional choices. Derivations such as the all-equivalence owner case apply those frozen meanings; they do not supply a new equivalence rule. No other discretionary scientific switch, necessity test, selector policy or implementation default is authorized.

The complete classification enum is SOURCE_ACCOUNTING_SEMANTIC_REPAIR, INTERFACE_REPRESENTATION, INTERFACE_METHODOLOGY_REFINEMENT, TREATMENT_OR_ONTOLOGY_CHANGE, UNRESOLVED_SCIENTIFIC_CHOICE, CONFLICT_WITH_FROZEN_AUTHORITY.

| Choice | Introduced decision and exhaustive scope | Classification |
|---|---|---|
| C01 | Prospectively broaden S §7/R §10 DIRECT meaning with mandatory-context ownership while preserving four buckets | SOURCE_ACCOUNTING_SEMANTIC_REPAIR |
| C02 | Close the new basis with the twelve-condition predicate and three-way canonical/source/owner completeness; no atomic credit or padding waiver | SOURCE_ACCOUNTING_SEMANTIC_REPAIR |
| C03 | New support-basis eligibility exclusion for existing selector/equivalence owners, preserving ancillary contexts and rejecting double ownership | SOURCE_ACCOUNTING_SEMANTIC_REPAIR |
| C04 | Exact D2 profile name, B1 requirement and compatible nested-version matrix | INTERFACE_METHODOLOGY_REFINEMENT |
| C05 | Four mandatory profile markers on input/tool/direct/evidence containers and old/mixed-validator rejection | INTERFACE_METHODOLOGY_REFINEMENT |
| C06 | Same V3.2 row, appended direct_required_support, payload version 2 | INTERFACE_REPRESENTATION |
| C07 | Same PREMAP identity, appended direct_support_candidates, schema version 2 | INTERFACE_REPRESENTATION |
| C08 | Seven-field DirectRequiredSupportEntry with literal basis, context/owner/prior refs and separate finding/validation | INTERFACE_REPRESENTATION |
| C09 | Bind ContextBinding/CGREQ/CGPREREQ by exact dereference join instead of redundant copied scientific fields | INTERFACE_REPRESENTATION |
| C10 | Unique nested source-ID selector without new support RID/index/row family | INTERFACE_REPRESENTATION |
| C11 | Explicit V32OCCRECORD references for semantic context incidence; no whole-proof dependency expansion | INTERFACE_METHODOLOGY_REFINEMENT |
| C12 | Complete source-ordered support candidate population retaining invalid/unresolved claims and global missing-context checks | INTERFACE_METHODOLOGY_REFINEMENT |
| C13 | Four-field DirectSupportValidation, exact status/null/known-failure precedence, frozen B1 StatusState unchanged | INTERFACE_REPRESENTATION |
| C14 | Three closed local D2 interface reasons, mapped to existing common failure envelopes | INTERFACE_REPRESENTATION |
| C15 | Eight local D2 scientific reasons and deterministic R/S/D2 ordered unions | INTERFACE_REPRESENTATION |
| C16 | Exact support/context/owner/evidence ordering and lossless amended-container serialization | INTERFACE_REPRESENTATION |
| C17 | Explicit legitimate prior-leaf staging, narrowed upstream PREMAP/RO-support proof-reference permission and post-seal MultiViewLink cross-check; D2 membership is completed before any V32ROSUPPORT production, which remains downstream RO machinery | INTERFACE_METHODOLOGY_REFINEMENT |
| C18 | Immutable producer/replay support equality and pre-RO residual consumer semantics; replay reconstructs D2 support and sealed residual first, before constructing/replaying V32ROSUPPORT, with no backward membership change | INTERFACE_METHODOLOGY_REFINEMENT |
| C19 | Complete flatten/export/binder/B1/expected-row compatibility obligations, unchanged Ref/RO schema bodies/stages; adapters cannot present downstream V32ROSUPPORT as an upstream D2 proof | INTERFACE_METHODOLOGY_REFINEMENT |
| C20 | Project both direct arrays to one duplicate bucket, use existing PREMAP provenance ref for nested support claims | INTERFACE_REPRESENTATION |

Counts: SOURCE_ACCOUNTING_SEMANTIC_REPAIR=3; INTERFACE_REPRESENTATION=10; INTERFACE_METHODOLOGY_REFINEMENT=7; TREATMENT_OR_ONTOLOGY_CHANGE=0; UNRESOLVED_SCIENTIFIC_CHOICE=0; CONFLICT_WITH_FROZEN_AUTHORITY=0; total=20.

Positive SOURCE_ACCOUNTING_SEMANTIC_REPAIR is intentional and necessary. Any consequential scientific case not determined by §1 authority and this exact proposed supplement must stop for independent review; it cannot become an implementation choice. A discovered unresolved all-equivalence anchoring rule would require DIRECT_SUPPORT_V2_ADDITIONAL_SCIENTIFIC_GAP rather than a complete proposal. The derivation in §9 resolves that case from frozen owner/correspondence authority.

## 30. Internal self-review and proposal-only STOP boundary

The following is author self-review of a methodology document, not independent review, freeze, scientific evidence or a candidate PASS.

| Required review item | Result and evidence |
|---|---|
| Exactly four final buckets | PASS: §2 exact enum; DIRECT union remains one bucket |
| Exactly two mutually exclusive DIRECT bases | PASS: §§2/8/19; existing selector array plus one support array |
| No fifth SUPPORT bucket | PASS: classifications/basis labels distinguished from dispositions |
| Every emitted atomic NODE/EDGE selector-required | PASS: §3 consumes G atomicity; no support-only canonical atoms |
| Eligibility only from frozen ContextBinding | PASS: §§4/6 exact pre-run chain, no source-driven additions |
| Exact pre-RO source/context correspondence | PASS: §§7/16/18/20, explicit original occurrence incidence |
| Deterministic selector/equivalence precedence | PASS: §8; frozen double-ownership failures retained |
| Zero atomic/key/activity/output credit | PASS: §§11/16/21/26, no inheritance or keyed intervention site |
| No padding loophole | PASS: §12 exact construction plus independent source/scaffold veto |
| No activity-derived support | PASS: static predicate and allowed proof types; zero execution permitted |
| No RO-derived support | PASS: §§19/20/25; immutable prior membership |
| NO_PRE_RO_DEPENDENCY_ON_V32ROSUPPORT | PASS: §§16/18–20/23 prohibit V32ROSUPPORT in DirectRequiredSupportEntry, PREMAP support candidates, upstream ContextCorrespondence/MappingView and residual derivation; membership is fixed before its creation, RO cannot alter it, and any legitimately needed equivalent static information is independently reconstructed from earlier authoritative facts |
| Pre-context/replay/version closure | PASS: §§13–23, complete closed field sets, exact replay, DAG staging |
| Scientific rows/populations unchanged | PASS: same 184 V3.2 rows, 120/64 and indexes; §§15/26 |
| B1 evidence unchanged outside narrow DIRECT additions | PASS: §§1/13/20/24 exhaustive precedence, no evidence-body edits |
| RO admission science unchanged | PASS: §25, same two classes/proofs/vetoes |
| E5 unchanged | PASS: §26, same complete signature/collision rules and 3840 comparisons |
| No historical reinterpretation | PASS: §27, v1/history/development counts unchanged |
| Zero candidate/scientific execution | PASS: document-only scope, no scientific instances or runtime checks |

Additional closure checks: all-equivalence owners follow frozen §9 correspondence, each context retains the exact immediate owner set, every actual owner remains independently MATCHED or blocks support, missing context cannot hide behind an empty array, shared occurrences receive one owner, all 44 paper threat cases have deterministic rules, and the 20-choice catalog has zero prohibited classifications. The narrow staging revision preserves the twelve-condition scientific predicate, four buckets, two bases, all-equivalence-owner result, schemas/profile/identities/populations and every independent science/veto rule; it removes the downstream RO-support reference permission without introducing a new proof object or reason code.

Internal outcome: **DIRECT_SUPPORT_ACCOUNTING_V2_REVISED_WITHOUT_NEW_SCIENTIFIC_CHOICE**.

This outcome means only that the prospective document is complete for independent review. It supplies no implementation readiness, future scientific feasibility, source correspondence instance or result. Future accepted authority must bind exact D2 bytes and its predecessors before use; authorization remains a separate boundary.

**END OF PROSPECTIVE NORMATIVE PROPOSAL. STOP after this proposal and its single-file commit. Do not freeze, implement, resume RO, construct scientific instances or create Attempt 004.**

## 31. Descriptive creation and v1→v2 disposition — DESCRIPTIVE_NON_NORMATIVE

This section supplies no scientific/interface authority. The repository was independently read at the starting HEAD. Read-only hash/blob/size/region checks matched the bound upstreams and protected files; the 17 RO drafts were checked opaquely without reading their scientific contents or running their scripts. Metadata-only repository inventory excludes .git and this authorized new proposal. No sealed holdout or expected-label content was read/hashed. The fresh baseline verified 44 distinct files through 260 declared identity/region checks; six predecessor regions and the B1/G/A accepted prefixes also matched their approved committed bytes. Both structural scientific prefixes matched their joint freeze. The ledger's committed LF bytes matched its normalized identity. All checked active CONF1/Attempt-004 paths were absent. These are repository-integrity findings only.

v1's two-role DIRECT concept and four buckets are retained descriptively. Its ordinary graph-element support eligibility is replaced by exact G/B1 mandatory non-NODE/non-EDGE context incidence. Its possible support-edge interpretation is rejected by accepted atomicity. Its connected-direct-only owner intuition is replaced by exact immediate canonical owners and independent lawful direct-or-authorized-equivalence realizations. Its speculative graph necessity gap is closed by accepted G construction and B1 ContextBinding/ContextCorrespondence identities; no diagnostic result supplies this authority.

v1 remains unchanged with SHA-256 9325a0cb67f64a529d4df784ab77d9211d569ac19718b9c036c409f427cc472c, Git blob 1f14af54db8480ff76b4f27a446acc03fd8acb1c and 41367 bytes. It remains UNFROZEN, NON-OPERATIVE. This proposal adds no freeze manifest. Current repository absence checks cover data/phase3c_conf1, benchmark/phase3c_conf1, research/results/PHASE_3C_CONF1, .runtime/phase3c_conf1, research/adapters/phase3c_conf1 and research/results/PHASE_3C_CONF1_PREFREEZE/attempt_004; they establish no claim about external/private activity.

Narrow staging revision provenance: independently read at HEAD 454ec05f7a14b713c799fbd85c239fcc9ec0cbe5 on clean main. Before editing, this D2 file matched SHA-256 dd8c6a891e809a3a4c39e5812d1f7343f4300c3a9a335ff91c88ad478d09bd7a, Git blob 47b455794d21aa27ea480736632fa88e7ee33567 and 87556 bytes. The independently reported PRE_RO_PROOF_DEPENDENCY_CYCLE is repaired only by removing downstream V32ROSUPPORT premises and mechanically updating dependency/consumer/threat/choice/self-review text. Scientific architecture, historical creation provenance and all frozen files remain unchanged; D2 remains PROPOSED, UNFROZEN and NON-OPERATIVE. No scientific execution or RO resumption is authorized or performed.

The final commit containing this revised file is reported separately to avoid self-reference. Post-write and post-commit integrity checks must confirm this exact single modified file, unchanged predecessor/protected bytes, unchanged repository file metadata outside that file, the single staged/committed path, clean main, zero scientific execution and Attempt 004 still unauthorized.
