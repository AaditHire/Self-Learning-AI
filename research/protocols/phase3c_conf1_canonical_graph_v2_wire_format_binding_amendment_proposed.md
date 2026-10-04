# Phase 3C — CONF1: canonical graph-v2 wire-format binding amendment

Status: **PROSPECTIVE_GRAPH_V2_WIRE_FORMAT_BINDING_REPAIR; PROPOSED; UNFROZEN; NON_OPERATIVE**.

Prepared 2026-10-04, Asia/Calcutta. Starting repository: `e8a8d412762f4b85110efe688d059c53d9d26511`, branch `main`, clean. `docs/PROJECT_STATE.md` was read first. This document is a proposed interface binding, not a freeze, an implementation, a graph instance or scientific evidence. Independent review and an explicit prospective freeze are required before use. Stop after this proposal's single-file commit.

## 1. Purpose, authority and precedence

The accepted graph-v2 recipe determines the scientific construction but does not determine every nested JSON representation. This proposal closes those representations. G means the accepted Sections 1–31 of [the graph-v2 recipe](phase3c_conf1_canonical_contract_graph_recipe_proposed_v2.md), under [its exact freeze](phase3c_conf1_canonical_contract_graph_recipe_v2_freeze.json). A means the accepted atomic/activity/output amendment; D the original delegated interface; B1 the accepted delegated canonical binding; D2 the accepted direct-support amendment. These abbreviations identify existing authorities, not new ones.

G's seven categories, ten directed relations, operation profiles, topology, positive essentiality, selectors, key science, static multiplicity, direct prerequisites, state/phase facts, attachment meanings and output declarations control without alteration. The joint structural mathematics/topology freeze operates only as a pair. A controls the specified atomicity/activity/output points. D/B1/D2 continue to control their own identities, joins, evidence, stages and accounting. This proposal has no precedence over any scientific rule or over a B1/D2 container. It binds G's previously unspecified nested representation only, if subsequently accepted.

No historical/development representation, implementation, source generator, rejected attempt, fixture result or previous conversation selected these encodings. No scientific graph, key, contract, source, case, mapping, evidence, signature or population instance was generated. No compiler, model, RO, E1–E6 or scientific fixture was executed. The slot ledger was inspected only for existing field/type metadata and integrity; no selected specification was instantiated. Protected RO files were opaque identity checks, not semantic inputs. No sealed expected-label/holdout content was inspected.

This document does not define `Recipe_v2`, extraction, graph lowering, scientific owner derivation, output-image proof production, source mapping, interventions or E5 comparison. It defines the representation of supplied facts that those separately authorized processes must derive from G. A schema admitting a representation never authorizes emitting that fact.

The strongest demonstrated empirical claim remains Level B — parameterized behavioral acquisition. No new empirical result, candidate feasibility, Coverage PASS or learning claim follows from wire closure.

## 2. Independent authority verification

The starting HEAD, branch and tracked/index/untracked state matched the request. The three previously authorized foundation files were absent. Verification used independently recomputed working-file hashes, committed blobs, sizes, approved committed regions and explicitly declared normalization policies. No authority was edited or converted.

The final authority recheck passed **1,045 assertions**, with **zero failures**, across **11 controlling freeze manifests**, **48 bound files**, and **58 region declarations** including repeated bindings, descriptive regions and four flat predecessor-manifest declarations. Descriptive regions were integrity controls only. Six approved predecessor heading-to-EOF regions were reconstructed using their declared policies; heading matching used complete heading lines, not mentions in prose. The graph, atomic and structural accepted prefixes were checked separately from their excluded appendices. Approved proposal commits were checked where declared. The working ledger's CRLF bytes and its committed LF identity were preserved as separate identities. Excluding this sole new proposal, all 4,982 pre-existing files retained their starting sorted path/size/mtime-ns metadata fingerprint, SHA-256 `a222a77a41557c1a5157572288bdc4b35055fb45ace4577f264aa2d2001b39b5`.

| Authority | Exact working-file SHA-256 | Committed Git blob | Bytes |
|---|---|---|---:|
| G freeze | `274c3e39d9dada9939e87c67f72aa71e8a2514ad9a84d35327ac0f6b711c2a51` | `14976b41c8e5e8dba915147fd3a379e891daa7bb` | 47206 |
| G proposal | `067401333940664502bada12b41d591ef1f554680ba5c9062954b5280e3fd272` | `e01d56046711365e3369a7fad67591b1476c4d15` | 117756 |
| A freeze | `8a9bfe3c4ad3b687261f486189285156b4c1843e53bfbd20b0bc35c4f07d09e8` | `602b5593287c798e6da297917335795530530a33` | 47346 |
| B1 freeze | `0257f8eac42265265f9f88b53633e56c7f9b9c6918f53988675cdcb84bd6de7d` | `23d8b3370b26ceec6a076f1061778fa43dad7100` | 40647 |
| D2 freeze | `1afa76f58bdf35601488f390e17708a62ed156e2dd0c38e59d82f3fbd3879e26` | `46d3e0b4bfddbef96a8247e69ddef7b3ef4c126d` | 88427 |
| D freeze | `bd7a7fc6862ce049c1fdf363f763e1a3a17808132291b9064e3c6f26fb720948` | `32595c5c563fa262679f2bf93ae789f04cde7f72` | 5892 |
| Joint structural freeze | `73eb1c29de6b258de6f7b83867e11ee3f53f67b513f550a666ede550b4e00aa5` | `cb643d992bac60db6a3ef208f1e690f6783ac4f6` | 25696 |
| Coverage-v3 freeze | `8d8f8a37c808d84c740867174e219803712213e672687c42164500f2bca12291` | `28c0fb52fba083e72f87ebfc530fd88ddded5f92` | 3307 |
| Paired-scaffold freeze | `ff1a9610b10ff559ac1859361fb7a31668210ed33e97c2864e592981bd9cfea2` | `9a54e9b525b1795b10f94bf0d0250ae831e6db74` | 2093 |
| INPUT_DOMAIN freeze | `de4a353d58515b5c53210664ea1a642731ac6f1734f23afef4ae512fb8c2627a` | `774eb73150f66d2545ddf270cc2f051eddedc156` | 4201 |
| RO-interface-v2 freeze | `aa8cc827a5c171b388220b0382713982d7a981b6e73b071a2dd12c2cf50ed5ab` | `7aa3ca18fe4df6823278e3dbd82eaa6bebfc8e6b` | 9936 |
| RO-catalog freeze | `769eb09bf85440ac4baaaac90b074e282d87c9a9a5e2d0265aedc17f6c46f7ce` | `a5781769519f8432c795de0290aa3d15d3722c07` | 14086 |
| AST-v2 | `962960ed6d766b574d2f9812b8ade5b5faa824acfe84e85b520636e2d6667fd9` | `c1ffc66d6b8a98645711cd77b6ff49fde5841deb` | 4365 |
| CONF1 protocol | `11e40c821fa26e5a687cea8b8a9a0aa5a0b0c388eae31c99de9814ab2bd80920` | `7ec58f3b4d5fc5827e35e4fbf22712a300240cec` | 39663 |
| Slot ledger, exact CRLF bytes | `5fe76fbc02e9f65174327199c2004f7e51f19a7f3866ae15709744c5274415c2` | `133c9c7275bcedeaf2474e54e61bae47923508ad` | 47968 |
| Coverage-v2→v3 disposition | `fb8a385538ddebf95195f099b9ba933bde97d33faf86373a7611e532e8b637d2` | `511843b001f6827c2b46242155485eecc3e429d8` | 10364 |

Accepted exact-byte prefixes include G: 113400 bytes, SHA-256 `cb490e9a3a9a2d31b71aec1207f2e191a7b60d9538d81af23cec3d0d610ae2f5`; A: 56933 bytes, `1b72ff7fab98a870882a81797aea5d8a079e7cac74e520d02f373f4e31c794f8`; structural mathematics: 36321 bytes, `a0c99b79001c1a37163d1ff4b06d4518891dca8c12518dc4a3d276b3de5658ac`; structural topology: 44187 bytes, `19d9dfc8863e4b2668a6525294fbdb71b479dbf1211d39a95f544b28d30a185d`. B1 Sections 1–27 and D2 Sections 1–30 are their independently verified accepted prefixes under their controlling manifests. Retained proposal-stage annotations do not negate later acceptance.

## 3. Exhaustive audit before selecting bindings

Each registry entry below is exactly one auditable type or closed policy/fieldset projection. Separate projections avoid claiming that a record's closed outer field list also closed its nested types. `A` expands to **ALREADY_CLOSED_BY_FROZEN_G**; `W` expands to **WIRE_REPRESENTATION_UNDERDETERMINED**. An entry classified W has fixed consumed scientific meaning and missing wire detail. **SCIENTIFIC_MEANING_UNDERDETERMINED = 0**. Entries with consumed D/B1 enum meanings are W where G did not fix their graph encoding.

Every field is covered by the schemas below: an object's exact field sequence is exhaustive, every value resolves to a registry type, and every union variant is separately closed. Every field receives its enclosing registry classification unless explicitly identified by an A projection. This is a field audit as well as a type audit; no unclassified arbitrary JSON leaf remains. Empty lists and null are governed separately.

| Audit ID | Reachable type or closed projection | Class | Frozen meaning / proposed closure |
|---|---|---|---|
| A01 | Graph outer field sequence | A | G §5; unchanged 13 fields |
| A02 | SchemaVersion | A | Exact integer 2, G §5 |
| A03 | RecipeVersion | A | Exact string CONF1_CG_RECIPE_V2, G §5 |
| A04 | PopulationKind | A | G §2 four spellings |
| A05 | Family | A | G §2 two spellings |
| A06 | Condition | A | G §2 ISOLATED/COMPOSITION or evaluation null |
| A07 | Datatype | A | G §2 seven spellings; UNIT restrictions retained |
| A08 | Category | A | G §3 seven categories |
| A09 | NodeOperation profiles | A | G §3 exhaustive operation/type/class table |
| A10 | EdgeType | A | G §4 ordered ten labels |
| A11 | Producer reference kind | A | G §4 three labels |
| A12 | ContextKind | A | G §19 six labels |
| A13 | AttachmentKind | A | G §24 ordered thirteen labels |
| A14 | SelectorKind | A | NODE/EDGE, G §20 |
| A15 | ViewRole | A | INITIAL/PRE/POST/COMPLETED, G §§3/5/10 |
| A16 | StateRole | A | G §10 six stored roles; FINAL_RESULT not storage |
| A17 | StageOrdering | A | ORDERED/UNORDERED, G §10 |
| A18 | EvidenceKind | A | G §27 existing three kinds |
| A19 | RelationMarker | A | Null or CERTIFIED_LOCAL_PAIR_JOINT_RESULT, G §20 |
| A20 | KeyProjection field sequence | A | G §20 exact thirteen fields |
| A21 | Nine representation-ID formulas | A | G §5, original D RID framing |
| A22 | Serialization and digest scientific boundary | A | G §5; exact bytes distinct from E5 |
| W01 | Graph complete recursive type | W | §5 below |
| W02 | GraphAuthorityBinding | W | G §§1/2/5; §5 below |
| W03 | AuthorityEntry | W | Existing authority identities; §5 |
| W04 | AuthorityRegion | W | Existing extraction policies; §5 |
| W05 | SpecificationBinding | W | G §§2/5; §5 |
| W06 | LedgerRecordReference | W | Exact existing lookup/provenance, G §2; §5 |
| W07 | FrozenSlotSpecification | W | Six frozen fields, G §2; §5 |
| W08 | FrozenRecord union | W | Existing ledger group fieldsets; §5 |
| W09 | TrainingFrozenRecord | W | Existing training field/type metadata; §5 |
| W10 | PrimaryFrozenRecord | W | Existing primary field/type metadata; §5 |
| W11 | SanityFrozenRecord | W | Existing sanity field/type metadata; §5 |
| W12 | StructuralFrozenRecord | W | Existing structural field/type metadata; §5 |
| W13 | PredicateRoleMap | W | Frozen P/Q/R/S metadata; §5 |
| W14 | TaggedPath | W | G §5 tags/order fixed; §6 closes JSON |
| W15 | PathComponent union | W | LABEL/ORDINAL; §6 |
| W16 | NodeOrderingKey | W | G §§3/5; §6 |
| W17 | EdgeOrderingKey | W | G §§4/5; §6 |
| W18 | Non-field ordering projections | W | Frozen family order plus representation-only cross-array addressing; §6 |
| W19 | ClauseReference | W | Closed construction clauses, G §§2–24; §7 |
| W20 | SemanticRole | W | Frozen local role facts, no source spelling; §7 |
| W21 | PortReference | W | G §4 formal/result/definition ports; §7 |
| W22 | NODE | W | G §3 exact outer sequence and profiles; §8 |
| W23 | InputPort | W | G §3 port/datatype/producer_ref; §8 |
| W24 | ProducerReference / EDGE source_ref | W | G §§3/4; §9 closes one particular INITIAL/POST committed producer, separately from read reaching metadata |
| W25 | ActivitySite | W | G §§3/20/27, B1 §8; §8 |
| W26 | PredicateBinding | W | G §3 tuple wording; §8 |
| W27 | PredicateDefinitionReference | W | G §8 eight exact definitions; §8 |
| W28 | EDGE | W | G §4 exact outer sequence; §9 |
| W29 | STATE | W | G §10 exact outer sequence; §10 |
| W30 | StateView | W | G §10 exact six fields; §10 |
| W31 | ViewAddress | W | Embedded view identity, no new namespace; §10 |
| W32 | WriterIdentity | W | Exact reaching definitions, G §§3/9/10; §10 |
| W33 | PHASE | W | G §10 exact outer sequence; §10 |
| W34 | StageGroup | W | G §10 exact four fields; §10 |
| W35 | ContextualRecord | W | G §19; §11 |
| W36 | StaticBindingPayload | W | G §§3/9/19/21; §11 |
| W37 | DecodedPackagePayload | W | G §§3/7/19/21/24; §11 |
| W38 | ExpressionResultPayload | W | G §§3/15/19/21/24; §11 |
| W39 | InitialPostPayload | W | G §§3/10/19/21; §11 |
| W40 | CompletionPersistencePayload | W | G §§10/15/19/21; §11 closes all three completion cases and their derived Boolean/reference consistency |
| W41 | ProvenancePayload | W | G §§2/19/21/25; §11 |
| W42 | ConsumerReference | W | Actual consuming node/port/type, G §4; §11 |
| W43 | ATTACHMENT | W | G §24 outer fields retained; §12 |
| W44 | AttachmentValue union | W | All thirteen kinds and explicit null; §12 |
| W45 | ReferenceLayout | W | Ordered role-to-reference correspondence, G §24; §12 |
| W46 | TypedValue | W | Exact existing typed scalar/package meaning; §12 |
| W47 | DomainFact union | W | G §§6/7/16/24; §12 |
| W48 | StateIdentityFact | W | Exact storage role, G §§10/24; §12 |
| W49 | StateViewFact | W | G §§10/24; §12 |
| W50 | PhaseMembershipFact | W | G §§10/24; §12 |
| W51 | OperandFact | W | G §§4/24; §12 |
| W52 | AccumulatorFact | W | G §§10/24; §12 |
| W53 | InitializationFact | W | G §§10/16/24; §12 |
| W54 | OutputRelationFact | W | G §§15/17/24; §12 |
| W55 | ValueAssociationFact | W | G §§7/16/24; §12 |
| W56 | DefinitionAssociationFact | W | G §§3/10/24; §12 |
| W57 | OrderRelationFact | W | G §§10/14/15/24; §12 |
| W58 | CompletionFact | W | G §§10/15/24; §12 fixes the same derived persistence Boolean and cross-record agreement |
| W59 | REQUIREMENT | W | G §20 exact outer sequence; §13 |
| W60 | Selector | W | G §20 fourteen fields; §13 |
| W61 | LocalRoles | W | Local semantic roles only, G §20; §13 |
| W62 | PredicateIdentity | W | Frozen named definition, G §§8/20; §13 |
| W63 | ValueRequirement union | W | G §§16/20, D §9.1.2; §13 |
| W64 | ParentCapability | W | Prospective local parent meaning only; §13 |
| W65 | OutputRequirement union | W | G §§17/20, D §9.1.3; §13 |
| W66 | StateViewRole | W | Local typed view, G §20; §13 |
| W67 | InputDomainObligation | W | Frozen range/schema/classes; §13 |
| W68 | InputClassDeclaration | W | INPUT_DOMAIN normative class table; §13 |
| W69 | ScientificEvidenceClass | W | Existing behavioral/attribute class serialization; §13 |
| W70 | ObligationScope | W | G §20, existing B1 §6.2 labels; §13 |
| W71 | PREREQUISITE wrapper/address | W | G §§5/21 exact fields and CGPREREQ; §14 |
| W72 | CompleteFunction | W | G §28 eight fields retained; §15 |
| W73 | DomainDefinition | W | Frozen complete input/index domain; §15 |
| W74 | ContributionRecord | W | Exact per-state contribution terms; §15 |
| W75 | StateEquation | W | Exact writes/PRE/POST/guard dependencies; §15 |
| W76 | InitializationRecord | W | Actual initialization value/place; §15 |
| W77 | TraversalRecord | W | Exact bounds/step/stages/persistence; §15 |
| W78 | Expression union | W | Closed G §2 grammar; §15 |
| W79 | ConstantExpression | W | Exact integer/refinement, G §2; §15 |
| W80 | DomainValueExpression | W | G §§2/6/7; §15 |
| W81 | IndexValueExpression | W | Original current index, G §§2/6/7; §15 |
| W82 | StateViewExpression | W | G §§10/14/15/28; §15 |
| W83 | NamedPredicateExpression | W | Exact role/definition/runtime arguments, G §8; §15 |
| W84 | OperatorExpression | W | Exact eleven pure operators/arity, G §2; §15 |
| W85 | Canonical JSON lexical encoding | W | G byte rules plus uniquely selected escaping/reconstruction; §17 |
| W86 | Scalar/reference atom aliases and list constructors | W | Exact §4 domains, namespace unions, null and list distinctions; no arbitrary JSON leaf |
| W87 | Role/port/clause/profile enum aliases | W | Complete catalogs in §§5/7–15, including PrimitiveName, SlotRole, StageRole, Direction and SourceCorrespondenceRole |

Audit totals: **109 entries = 22 A + 87 W + 0 SCIENTIFIC_MEANING_UNDERDETERMINED**. **WIRE_REPRESENTATION_UNDERDETERMINED repaired = 87** under the revised bindings below. W24/W40/W58 close the two narrowly identified defects; their containing Graph/NODE/InputPort/EDGE/STATE/StateView/ContextualRecord/ATTACHMENT/AttachmentValue types inherit those corrected constraints without new fields or registry entries. Registry counts are schema/policy audit units, not emitted scientific records, capability counts or population enumeration. Union cases, field null matrices and fixed enum members are included explicitly in their registry entries.

## 4. Type notation and universal rejection rules

This is a specification, not executable code. `Object(a:T,b:U)` means exactly those JSON keys, emitted in that order. `T?` means T or an explicitly present JSON null under the stated condition. `List(T)` means a non-null JSON array; `SetList(T)` additionally forbids duplicate exact identities and uses the stated canonical order. A union accepts exactly one listed variant. No record has optional/extra fields. A missing fact is not an omitted key, empty proof or inferred default.

`String` means exact Unicode scalar-value text, encoded as UTF-8 without normalization. Unpaired surrogates are invalid. `Name` is a nonempty String. Names used as local scientific roles, ports, clauses, operations or enum values additionally satisfy the finite catalogs below; source spelling cannot create one. Provenance identifiers retain their exact bound authority values without trimming/case conversion. `Int` is an exact JSON integer, excluding bool, fractions/exponents, negative-zero spelling and coercion. `Nat` is Int ≥0; `Positive` is Int ≥1. `Bool` is JSON true/false only. `SHA256` is 64 lowercase hexadecimal characters; `Blob` is 40 lowercase hexadecimal characters. No arbitrary JSON, float, NaN, binary token or implementation object is a leaf type.

`NodeID`, `EdgeID`, `StateID`, `PhaseID`, `ContextID`, `AttachmentID`, `RequirementID`, `PrerequisiteID`, `KeyID` are exact existing RID strings in their respective CG namespaces, with V2 components and §16 formulas. `OccurrenceID` is NodeID/EdgeID/StateID/PhaseID/ContextID; `SupportedID` also admits AttachmentID. `RecordID` additionally admits RequirementID/PrerequisiteID, only in an identified-reference field whose frozen clause requires that record; it does not widen PREREQUISITE's SupportedID or grant transitive support. Requirement and prerequisite addresses are not substituted for selected occurrences. Every typed reference resolves uniquely within the bound same graph or specified exact authority. Strings merely resembling a namespace do not pass framing/formula validation.

Unknown keys/enums, duplicate keys, missing keys, wrong scalar types, foreign/stale/mixed-version references, duplicate IDs, inconsistent redundant values, invalid list order, unknown symbolic terms and unsupported scientific profiles reject. The object schemas admit no error/status/coverage/witness fields. Schema validation does not establish that supplied science SHOULD exist; eventual construction conformance must independently enforce G.

## 5. Graph, authorities and specification bindings

Graph is exactly `Object(schema_version:SchemaVersion, recipe_version:RecipeVersion, authority_binding:GraphAuthorityBinding, specification_binding:SpecificationBinding, nodes:List(NODE), edges:List(EDGE), states:List(STATE), phases:List(PHASE), contextual_records:List(ContextualRecord), attachments:List(ATTACHMENT), requirements:List(REQUIREMENT), prerequisites:List(PREREQUISITE), complete_function:CompleteFunction)`. No document digest, program ID, additional profile/version flag or wire-amendment field is added.

GraphAuthorityBinding is `Object(graph_recipe_version:RecipeVersion, authorities:List(AuthorityEntry))`. This is the graph's own nested object; it is not B1's separately registered `AuthorityBinding` and contains no BINDAUTH identifier. AuthorityEntry is `Object(authority_role:Name, path:Name, sha256_exact_bytes:SHA256, git_blob:Blob, size_bytes:Nat, normative_region:AuthorityRegion?)`. A non-null AuthorityRegion is `Object(extraction:Name, start_heading:Name?, start_byte_offset:Nat?, byte_count:Nat, sha256:SHA256)`. Extraction is exactly `EXACT_PREFIX`, `EXACT_HEADING_TO_EOF`, `CRLF_TO_LF_HEADING_TO_EOF`, `WHOLE_FILE`, or `CRLF_TO_LF_WHOLE_FILE`. EXACT_PREFIX requires heading null and offset 0; heading variants require exact heading/non-null and offset null; whole-file variants require heading null/offset 0. byte_count/hash describe the declared extracted bytes. CRLF conversion is performed only for a variant explicitly naming it. No algorithm dynamically selects a version or normalizes an authority outside its policy.

The authorities array is exactly this ordered role/path list; every whole-file identity equals the one fixed frozen-chain record independently verified in §2. The raw SHA, committed blob and raw byte size are mandatory even where the predecessor also uses normalized bytes. Whole-file identity and accepted-region identity remain separate. The subsequent region table is exhaustive: no caller chooses between null, prefix, whole-file or heading extraction. Freeze manifests and the descriptive disposition have normative_region null; this does not remove their whole-file integrity binding or give the disposition scientific authority.

| Order | authority_role | Fixed repository path / region |
|---:|---|---|
| 0 | GRAPH_FREEZE | phase3c_conf1_canonical_contract_graph_recipe_v2_freeze.json |
| 1 | GRAPH_RECIPE | phase3c_conf1_canonical_contract_graph_recipe_proposed_v2.md; G exact prefix |
| 2 | ATOMIC_FREEZE | phase3c_conf1_coverage_v3_atomic_activity_output_amendment_freeze.json |
| 3 | ATOMIC_AMENDMENT | phase3c_conf1_coverage_v3_atomic_activity_output_amendment_proposed.md; A exact prefix |
| 4 | DELEGATED_FREEZE | phase3c_conf1_delegated_evidence_interfaces_freeze.json |
| 5 | DELEGATED_INTERFACE | phase3c_conf1_delegated_evidence_interfaces_proposed.md; approved exact heading region |
| 6 | B1_FREEZE | phase3c_conf1_delegated_evidence_interfaces_binding_amendment_freeze.json |
| 7 | B1_BINDING | phase3c_conf1_delegated_evidence_interfaces_binding_amendment_proposed.md; accepted exact prefix |
| 8 | D2_FREEZE | phase3c_conf1_direct_support_accounting_amendment_v2_freeze.json |
| 9 | D2_BINDING | phase3c_conf1_direct_support_accounting_amendment_proposed_v2.md; accepted exact prefix |
| 10 | STRUCTURAL_PAIR_FREEZE | phase3c_conf1_structural_transfer_pair_freeze.json |
| 11 | STRUCTURAL_MATHEMATICS | phase3c_conf1_structural_transfer_semantics_amendment_proposed.md; accepted exact prefix |
| 12 | STRUCTURAL_TOPOLOGY | phase3c_conf1_structural_transfer_topology_amendment_proposed.md; accepted exact prefix |
| 13 | COVERAGE_FREEZE | phase3c_conf1_coverage_v3_freeze.json |
| 14 | COVERAGE_V3 | phase3c_conf1_coverage_v3_proposed.md; approved CRLF-to-LF heading region |
| 15 | PAIRED_FREEZE | phase3c_conf1_paired_scaffold_normalization_freeze.json |
| 16 | PAIRED_SCAFFOLD | phase3c_conf1_paired_scaffold_normalization_proposed.md; approved CRLF-to-LF heading region |
| 17 | INPUT_DOMAIN_FREEZE | phase3c_conf1_input_domain_case_classes_and_training_amendment_freeze.json |
| 18 | INPUT_DOMAIN | phase3c_conf1_input_domain_case_classes_and_training_amendment_proposed.md; approved CRLF-to-LF heading region |
| 19 | RO_INTERFACE_FREEZE | phase3c_conf1_reference_only_interface_clarification_v2_freeze.json |
| 20 | RO_INTERFACE | phase3c_conf1_reference_only_interface_clarification_proposed_v2.md; approved exact heading region |
| 21 | RO_CATALOG_FREEZE | phase3c_conf1_reference_only_catalog_freeze.json |
| 22 | RO_CATALOG | phase3c_conf1_reference_only_catalog_proposed.md; approved exact heading region |
| 23 | CONF1_PROTOCOL | phase3c_conf1_proposed_protocol.md; existing CRLF-to-LF whole-file binding |
| 24 | SLOT_LEDGER | phase3c_conf1_slots.json; exact working CRLF identity plus committed blob |
| 25 | COVERAGE_DISPOSITION | phase3c_conf1_coverage_v3_v2_disposition.md |
| 26 | AST_V2 | phase3c_conf1_ast_adjudication_v2.md |

All paths in this table have the fixed prefix `research/protocols/`. This exact list represents the already-frozen closure; inclusion creates no new precedence or scientific authority and authorizes no RO use. The prospective wire proposal/future freeze is bound externally as implementation authority if later approved, not inserted as a new graph field or substituted for G. Existing frozen manifests already transitively bind their protected files; those files are not new scientific authority entries.

| authority_role | Exact normative_region binding |
|---|---|
| GRAPH_FREEZE, ATOMIC_FREEZE, DELEGATED_FREEZE, B1_FREEZE, D2_FREEZE, STRUCTURAL_PAIR_FREEZE, COVERAGE_FREEZE, PAIRED_FREEZE, INPUT_DOMAIN_FREEZE, RO_INTERFACE_FREEZE, RO_CATALOG_FREEZE, COVERAGE_DISPOSITION | null |
| GRAPH_RECIPE | EXACT_PREFIX; heading null; offset 0; 113400 bytes; `cb490e9a3a9a2d31b71aec1207f2e191a7b60d9538d81af23cec3d0d610ae2f5` |
| ATOMIC_AMENDMENT | EXACT_PREFIX; heading null; offset 0; 56933 bytes; `1b72ff7fab98a870882a81797aea5d8a079e7cac74e520d02f373f4e31c794f8` |
| B1_BINDING | EXACT_PREFIX; heading null; offset 0; 119512 bytes; `cab925e51aac6beb6705439d5d0d02cc4414d143d39526089511c2a80f81b94b` |
| D2_BINDING | EXACT_PREFIX; heading null; offset 0; 102020 bytes; `d0b7d7975785c48ec62a7cdf9818655daac02231278319445d28fd139b99dbf5` |
| STRUCTURAL_MATHEMATICS | EXACT_PREFIX; heading null; offset 0; 36321 bytes; `a0c99b79001c1a37163d1ff4b06d4518891dca8c12518dc4a3d276b3de5658ac` |
| STRUCTURAL_TOPOLOGY | EXACT_PREFIX; heading null; offset 0; 44187 bytes; `19d9dfc8863e4b2668a6525294fbdb71b479dbf1211d39a95f544b28d30a185d` |
| DELEGATED_INTERFACE | EXACT_HEADING_TO_EOF; heading `## 1. Authority, scope, and precedence`; offset null; 74717 bytes; `26c642e17bb5218727c0cd09f370eaf1ac6c4de35006fa9801d701ece81cf16d` |
| COVERAGE_V3 | CRLF_TO_LF_HEADING_TO_EOF; heading `## Design record: why v2 is superseded`; offset null; 29178 bytes; `884a8ac3f859268e16dfa0d8f0d477211c7a273fca58666c7eba018265d8c15a` |
| PAIRED_SCAFFOLD | CRLF_TO_LF_HEADING_TO_EOF; heading `## Scope and source precedence`; offset null; 12217 bytes; `5aa404949a8cc580b9ca3ff4aff7325195e172a7cfa82c69317280597c73b25c` |
| INPUT_DOMAIN | CRLF_TO_LF_HEADING_TO_EOF; heading `## Authority and scope`; offset null; 14669 bytes; `b9dc3d6ca22778ab0b3e734270fb20a00b4d88e0602f24fe77b2112335df8167` |
| RO_INTERFACE | EXACT_HEADING_TO_EOF; heading `## 1. Authority, scope, and prospective effect`; offset null; 68141 bytes; `a2bf9185686171e566d4a0e35a9780eaab45eb99e1ffdfbd4dfa49dcf22d9a00` |
| RO_CATALOG | EXACT_HEADING_TO_EOF; heading `## 1. Prospective status, authority, and scope`; offset null; 51739 bytes; `25c04bb3b319314cce744d5c83a491dae97c1596c4e38a19d639bab3ca9a58d5` |
| CONF1_PROTOCOL | CRLF_TO_LF_WHOLE_FILE; heading null; offset 0; 39663 bytes; `11e40c821fa26e5a687cea8b8a9a0aa5a0b0c388eae31c99de9814ab2bd80920` |
| SLOT_LEDGER | CRLF_TO_LF_WHOLE_FILE; heading null; offset 0; 46284 bytes; `83436eecda3affe813b785e868e3f8936fa59afc35ded0eb6a54290edb41dc88` |
| AST_V2 | WHOLE_FILE; heading null; offset 0; 4365 bytes; `962960ed6d766b574d2f9812b8ade5b5faa824acfe84e85b520636e2d6667fd9` |

The six heading rows are precisely A.bound_authorities' approved_normative_region declarations. G/A/B1/D2 and both structural prefixes come from their exact controlling freeze entries. CONF1_PROTOCOL, SLOT_LEDGER and AST_V2 retain D.upstream_authorities' existing whole-file policies. Thus the table packages existing integrity/authority boundaries and makes none wider. Each heading must match one complete line in the policy-selected bytes; extraction starts at its first byte and ends at EOF, excluding the preceding LF. A prose mention is not a heading match.

SpecificationBinding is `Object(population_kind:PopulationKind, slot_identity:Name, family:Family, condition:Condition, frozen_record_reference:LedgerRecordReference)`. LedgerRecordReference is `Object(authority_role:"SLOT_LEDGER", group:Name, identity_field:Name, identity_value:Name)`. Its group is exactly `training_paired_slots`, `primary`, `primitive_sanity` or `structural_transfer`, matching population_kind. identity_field is `slot_id` for training and `task_id` otherwise; identity_value equals slot_identity. Resolve only the corresponding existing ledger array and exact identity field, never a recursive JSON search, array position guessed from an ID, or equivalent content. The reference is bound to the exact ledger identity in GraphAuthorityBinding; it uniquely binds the whole frozen record. Graph provenance therefore does not duplicate that record.

FrozenSlotSpecification is a distinct future builder input: `Object(authority_binding:GraphAuthorityBinding, population_kind:PopulationKind, slot_identity:Name, family:Family, frozen_record:FrozenRecord, condition:Condition)`, preserving G §2's six fields/order. G requires its entire selected existing ledger record, so this input alone carries the full record. A shape validator checks the appropriate complete fieldset; the future builder separately checks exact equality to the bound ledger and the specification binding. This proposal creates no record instance.

FrozenRecord is an externally discriminated union selected only by population_kind, with no new tag field. Its four exact field sequences/types are:

| Variant | Exact fields in order |
|---|---|
| TrainingFrozenRecord | slot_id:Name, family:Family, P:PrimitiveName, Q:PrimitiveName, unordered_pair:List(PrimitiveName)[2], variant:Nat, offset:Int, reverse:Bool |
| PrimaryFrozenRecord | task_id:Name, family:Family, group:Name, graph:G1/G2/G3/G4, rotation:Nat, block_id:Name, role_predicates:PredicateRoleMap, composition_signature:Name |
| SanityFrozenRecord | task_id:Name, family:Family, group:Name, primitive:PrimitiveName, variant:Nat, offset:Int |
| StructuralFrozenRecord | task_id:Name, family:Family, group:Name, structure:PREFIX/TWO_PASS, rotation:Nat, role_predicates:PredicateRoleMap |

PredicateRoleMap is exactly `Object(P:PrimitiveName,Q:PrimitiveName,R:PrimitiveName,S:PrimitiveName)`. PrimitiveName is the eight exact G §8 spellings. Family compatibility, group/variant/range/role-map/content equality remain the already-frozen ledger rules, not relaxed by these type descriptions. Unused R/S metadata remains metadata. Training conditions are ISOLATED or COMPOSITION; all evaluation conditions are null. `NONE` is only the RID component sentinel, never a graph JSON condition.

## 6. Occurrence paths, ordering keys and record order

PathComponent has exactly `Object(tag:"LABEL",value:String)` or `Object(tag:"ORDINAL",value:Nat)`, in tag/value order. Null values/tags, extra fields, raw untagged scalars, floats and Boolean ordinals reject. TaggedPath is a non-null ordered array of PathComponent. A scientific occurrence path is nonempty and retains G §5's clause/domain/traversal/stage/role/operand/use components; this proposal selects no new scientific labels or construction paths.

Compare components by `(0, exact UTF-8 bytes of value)` for LABEL and `(1, numeric value)` for ORDINAL. Compare arrays lexicographically; an exact proper prefix precedes the longer path. The comparison projection is not serialized as another path. Reject collisions among distinct occurrence identities where G requires distinct paths; do not manufacture a tie-break or normalize Unicode. Phase absence remains ordinal 0; traversal j remains j+1 in a scientific path. Record ordinals used below are representation indexes, not those path components or execution counters.

NodeOrderingKey is exactly `Object(occurrence_path:TaggedPath)`. It equals the node's occurrence_path byte-for-byte after canonical encoding. EdgeOrderingKey is exactly `Object(source_owner_ordinal:Nat,target_node_ordinal:Nat,edge_type_ordinal:Nat,destination_port_ordinal:Nat,repeated_use_ordinal:Nat)`. Edge type ordinal is its 0-based position in G's ten-label list; target_node_ordinal is its position in nodes[]. destination_port_ordinal is the position of the exact typed consuming input port in target.input_ports; every directed target use must resolve such a port. repeated_use_ordinal is the owning formal-use ordinal carried by its G path, not a count inferred from source. Source owner ordinal is defined below. Every field is recomputed and compared; no caller text/value selects ordering.

No ordering_key field is added to STATE, PHASE, context, ATTACHMENT, REQUIREMENT or PREREQUISITE. Their projections are recomputed from their existing content and identities. A future validator rejects unsorted arrays; it never sorts them silently. Typed object reconstruction in §17 does not reorder arrays.

| Collection / projection | Exact comparison and derivation |
|---|---|
| nodes | TaggedPath lexicographic order |
| phases | traversal_ordinal, ascending; uniqueness required |
| states | Owning traversal ordinal, then INDEX/INDICATOR/TOTAL/PRIOR_P_COUNT/P_COUNT/Q_COUNT order; INDICATOR ties use its frozen term path. No stored FINAL_RESULT is admitted. A persisted state retains its creation identity/order. |
| contextual_records | TaggedPath lexicographic order |
| PathOwnerOrder | Merge NODE/EDGE/STATE/PHASE/CONTEXT occurrence paths lexicographically. NODE/EDGE/context paths are explicit; STATE/PHASE paths are extracted from their exact RID final component. Require that redundant path and identity agree. Referenced contextual owners therefore enter the same path order as nodes, as G §5 requires. This temporary projection adds no record/field. |
| edges | G's five-component EdgeOrderingKey lexicographically; source owner is its owner_id's 0-based rank in PathOwnerOrder. The last ORDINAL in an edge path encodes its repeated formal use; only fixed LABEL qualifiers may follow it. This binds the location of G's existing repeated-use component without changing its value or generating a path. |
| attachments | Owner rank in PathOwnerOrder; thirteen-kind ordinal; port then semantic-role ordinal under §7. If that frozen leading projection ties, compare the exact canonical UTF-8 fragment of semantic_role/value/referenced_occurrence_ids from §16; it contains only the already-required facts. Identical IDs still reject. Scientific ordered reference sequences remain inside the record. |
| requirements | Selected-occurrence order, then profile ordinal 0/1. Selected-occurrence order is nodes[] followed by edges[], preserving each frozen array order. This closes cross-array addressing, not execution order. |
| prerequisites | Supported-record ordinal, then owning requirement ordinal. Supported order is nodes[], edges[], states[], phases[], contextual_records[], attachments[] in graph field order, preserving each collection's frozen order. A tie uses pairing_role catalog ordinal then pairing_position, retaining distinct formal pairings; duplicate supported/owner/role/position wrappers reject. |
| state.views | G view-role order INITIAL/PRE/POST/COMPLETED; phase ordinal (absent phase first); stage order below; lexicographic defining-writer node-ordinal list; ProducerReference comparison below, with null first. Distinct scientifically required facts remain distinct. |
| stage groups | G stage order entry, item.read, item.predicate, item.contribution, item.result_update, item.other_update, item.index_step, completion; final.expression/final.output only outside traversals |
| stage members | ORDERED retains the frozen scientific sequence; UNORDERED emits the already-qualified pure members in TaggedPath order. It never grants new reordering freedom. |

All derived ranks are Nat, 0-based. Membership lists order by the referenced family's frozen collection order unless G owns a scientific ordered sequence. Attachments' port/role ordinals use the exact catalogs below; no alphabetical sorting is substituted. A scientific ORDERED sequence can differ from representation record order and must be preserved independently. Phase order, strict PREFIX update precedence, TWO_PASS persistence, repeated uses, sharing and empty-body logical phases remain explicit facts.

RecordOrder is the concatenation nodes, edges, states, phases, contextual_records, attachments, requirements, prerequisites, preserving each collection order and using a prerequisite's derived CGPREREQ address. It closes mixed RecordID reference lists; it is not PathOwnerOrder and creates no execution order. PROVENANCE's identified_record_ids use RecordOrder, excluding REQUIREMENT, and identified_requirement_ids use requirements order. A generic membership SetList uses its exact referenced-family order, or RecordOrder for a mixed family. The explicit ContextualRecord owner rule remains PathOwnerOrder. The attachment/prerequisite final comparisons above apply only when G's entire leading projection ties; they package existing facts, preserve that leading projection and never break a scientific sequence or merge a formal pairing.

PortReference comparison is role-catalog ordinal, then ordinal with null before integers; an absent enclosing port precedes every present port. ProducerReference comparison is reference-kind ordinal NODE_OUTPUT_PORT/STATE_DEFINITION_PORT/ORDERED_PACKAGE, owner rank in PathOwnerOrder, PortReference comparison, G datatype ordinal, then lexicographic component-reference comparison with null before a list. Definition-reference lists use that comparison; writer lists use nodes order. ConsumerReference lists without their own scientific sequence use target node order then its formal input-port index, with datatype as a redundant checked fact. Tuple comparisons are lexicographic; a proper list prefix precedes the longer list. CompleteFunction contributions use phase/stage/state order; state equations use phase/stage/writer order; initializations use phase with absent phase first, stage, then writer order; traversals use traversal_ordinal. These rules sort supplied facts and do not derive additional facts or change temporal relationships.

Losslessness: tags retain both type and exact value; redundant keys retain no new semantic input; each projection uses existing content plus a fixed representation traversal of separate arrays. Changing the packaging of these projections changes bytes/representation IDs where applicable, but cannot change membership, directed topology, required scientific timing, selector facts, activity classes, evidence or populations. Sorting records cannot establish or erase execution order.

## 7. Closed role, clause and port representations

The following catalogs are wire names for the already-frozen local facts. They do not grant new roles, classify source or derive existence. Validation additionally checks the exact owning G clause/profile; a catalog member in the wrong clause rejects. Within a catalog, ordinal is its listed position. Catalog ordering resolves encoding/order only, not scientific priority.

SemanticRole is a String from this ordered catalog: `decoded_n`, `raw_array_text`, `numeric_field_text`, `decoded_field`, `ordered_decoded_domain`, `original_index`, `loop_bound`, `loop_step`, `index_initialization`, `predicate_argument`, `predicate_parameter`, `named_predicate_result`, `defining_operator_result`, `boolean_result`, `numeric_result`, `indexed_value`, `indicator`, `indicator_reset`, `indicator_set`, `index`, `count`, `result`, `initial`, `prior`, `current`, `post`, `completed`, `operand`, `contribution`, `committed_value`, `control_decision`, `initial_accumulator`, `final_integer`, `final_display`, `expression_result`, `fixed_value`, `literal_value`, `value_parent`, `output_property`, `domain_schema`, `decoder_separator_configuration`, `static_binding`, `phase_membership`, `ordered_stage`, `completion`, `persistence`, `provenance`, `joint_left`, `joint_right`, `FINAL_RESULT`.

The first ten roles encode G §§6–7's input/index/bound/step facts; predicate/operator roles encode §§3/8; indexed_value names §7's actual indexed element; indicator/read/write/state roles encode §§9–10; count/result/prior/completed facts encode §§10–15; value/output/configuration roles encode §§16–17/24; association/order/provenance roles encode §§19/21/24; joint_left/joint_right are G §20's exact key roles; FINAL_RESULT is §15's exact expression occurrence role. The six uppercase stored-state names belong only to StateRole, not alternative spellings in this catalog. Each label denotes its specified local fact, not an interchangeable synonym or normalization equating different roles. Source identifiers and task/condition/phase IDs never become role labels. Additional formal position is expressed by PortReference or occurrence attachments, not invented role text.

SlotRole is `P`, `Q`, `R`, `S`, `DESIGNATED` or null. DESIGNATED encodes G §13's single designated primitive and is not an additional predicate; it cannot appear in a four-role map. StateRole is exactly INDEX/INDICATOR/TOTAL/PRIOR_P_COUNT/P_COUNT/Q_COUNT. StageRole is entry/item.read/item.predicate/item.contribution/item.result_update/item.other_update/item.index_step/completion/final.expression/final.output. Domain selectors use Family; occurrence domain_role uses the corresponding SemanticRole, not a sampled domain value.

ClauseReference is `Object(section:Positive,rule:Name)`. Only these pairs are allowed: §3 with an actually emitted NodeOperation; §4 with an EdgeType; §6 D-N or D-N-LOOP; §7 D-A; §8 a PrimitiveName; §9 I-CONVERT; §10 U-SUM; §11 T-PAIR; §12 P-GRAPH; §13 S-PRIMITIVE; §14 ST-PREFIX; §15 ST-TWO; §16 COMPUTED_VALUE/DOMAIN_VALUE/FIELD_VALUE/LITERAL_TOKEN; §17 DISPLAY_INTEGER or an output-category operation; §19 a ContextKind; §20 NODE/EDGE/INPUT_DOMAIN/CERTIFIED_LOCAL_PAIR_JOINT_RESULT; §21 MANDATORY_PREREQUISITE_OF; §24 an AttachmentKind. A record's most specific scientifically owning clause is retained; the representation does not reassign an owner or allow an unrelated section. A clause reference resolves into the exact accepted G authority, not a mutable URL.

PortReference is `Object(role:Name,ordinal:Nat?)`. Role, in order, is `arg0`, `arg1`, `raw_text`, `field_j`, `package`, `original_index`, `decision`, `committed_value`, `contribution_application`, `prior_state`, `integer_result`, `stored_value`, `result`. ordinal is 0–3 only for a particular SPLIT field output; is the exact state.views position only for a STATE_DEFINITION_PORT; otherwise null. The enclosing reference/profile determines which rule applies. A TO_NUMBER consuming `field_j` has ordinal null: the exact field position is occurrence context, not reusable key identity. `arg0` and `arg1` remain distinct even for equal operands. Result ports and actual UNIT decision/committed outputs do not manufacture a UNIT payload. Null port, where permitted at an enclosing field, differs from a PortReference with ordinal null.

SourceCorrespondenceRole uses B1 §9's existing semantic-view labels: NAMED_PRIMITIVE_RESULT, DEFINING_OPERATOR_RESULT, STIPULATED_INDICATOR_RESULT, CONTROL_DECISION, COMMITTED_WRITE, CONTRIBUTION_APPLICATION, STATE_READ, DIRECTED_OPERAND_USE, CARRY_USE, PRIOR_USE, FINAL_VALUE_CONSUMPTION, DISPLAY_ARGUMENT, API_RESULT, INPUT_DOMAIN_MACRO, CERTIFIED_LOCAL_JOINT_RESULT, RUNTIME_CARRIER_ROLE, FIXED_ATTRIBUTE_ROLE, LITERAL_ATTRIBUTE_ROLE, OUTPUT_PROPERTY. This graph field binds the corresponding G §25 semantic association prospectively; it contains no source span, MappingView, finding or proof.

## 8. NODE and nested structures

NODE retains exactly G §3's sequence: `Object(node_id:NodeID,construction_clause:ClauseReference,occurrence_path:TaggedPath,category:Category,operation:NodeOperation,semantic_role:SemanticRole,domain_role:SemanticRole?,slot_role:SlotRole,state_id:StateID?,phase_id:PhaseID?,input_ports:List(InputPort),output_type:Datatype,activity_site:ActivitySite?,predicate_binding:PredicateBinding?,attachment_ids:SetList(AttachmentID),source_correspondence_role:SourceCorrespondenceRole,ordering_key:NodeOrderingKey,task_essential:true,selector_class:"ATOMIC_SELECTOR_REQUIRED")`.

InputPort is exactly `Object(port:PortReference,datatype:Datatype,producer_ref:ProducerReference)`. Its datatype excludes UNIT; it equals the actual consumed producer payload. Ports are unique in the node's exact formal-port order from G §4; empty input_ports is allowed only for a scientifically inputless profile such as INPUT. Missing references cannot be replaced by null or hidden constants. state_id/phase_id/domain_role/slot_role are null precisely when the owning frozen clause supplies no such occurrence fact. Identity, path, category, operation, output/activity types and all attachments must agree. All emitted nodes, including attributes, have task_essential true and atomic selector classification.

ActivitySite is exactly `Object(kind:Name,payload_type:Datatype,local_role:SemanticRole,port:PortReference?)`. Kind uses the existing B1 §8 labels BOOLEAN_RESULT/NUMERIC_RESULT/DECISION/COMMITTED_VALUE/DIRECTED_USE/CONTRIBUTION_APPLICATION/DISPLAY_ARGUMENT/API_RESULT/INPUT_DOMAIN_ROOT/CERTIFIED_LOCAL_JOINT_RESULT. payload_type excludes UNIT. port is null only for a non-port result/decision site; otherwise it identifies the exact local semantic port. No execution, witness, trace, case, finding or source identity appears. Attribute sites are null; every behavioral profile has its legitimate non-null site. UNIT-returning loop/IF/write/display nodes retain UNIT output_type with a BOOL/committed-numeric/contribution-numeric/display-INT site, respectively.

PredicateBinding is exactly `Object(slot_role:SlotRole,frozen_predicate_name:PrimitiveName,definition_reference:PredicateDefinitionReference)`, non-null only where a frozen bound predicate identity is applicable. Its slot_role is non-null. PredicateDefinitionReference is `Object(authority_role:"GRAPH_RECIPE",section:8,frozen_predicate_name:PrimitiveName)`. Resolve the exact row in G §8, which itself consumes the unchanged ledger definition. The duplicated name must match; no URL, arbitrary expression or implementation definition is accepted. PredicateBinding's tuple wording therefore selects an ordered object, not an ambiguous positional array.

G §3's operation/profile table is retained completely: SEMANTIC_PRIMITIVE has the eight BOOL predicates; GENERIC_CONSTRUCT has BOUNDED_LOOP/IF_CHOICE UNIT with BOOL decisions, INDEX_READ INT, INITIALIZE/non-accumulator ASSIGN UNIT with INT/INDICATOR_INT committed sites, accumulator ASSIGN UNIT with its numeric contribution site, DISPLAY_INTEGER UNIT/INT argument; API_DECODER has numeric INPUT INT or array INPUT TEXT, SPLIT TEXT4, TO_NUMBER INT; ATOMIC_OPERATOR has EQ/LT/LE/AND/OR BOOL, NEG/ADD/SUB/MUL/MOD INT with only frozen refinements, BOOL_TO_INT INDICATOR_INT; VALUE_OR_LITERAL has DOMAIN_VALUE/FIELD_VALUE INT, COMPUTED_VALUE INT/INDICATOR_INT, separately authorized LITERAL_TOKEN only; OUTPUT_CATEGORY has OUTPUT_ZERO/OUTPUT_POSITIVE/OUTPUT_NEGATIVE/OUTPUT_MULTIDIGIT/EXACT_SENTINEL INT-property profiles; ATOMIC_CONTROL_DATAFLOW has actual STATE_VIEW INT/INDICATOR_INT reads. No BINDING, EXPRESSION_RESULT, package assembly or unused INITIAL/POST read node is introduced. Current G authorizes no LITERAL_TOKEN or EXACT_SENTINEL occurrence merely because their enum spellings exist.

## 9. EDGE and shared producer-reference schema

ProducerReference is exactly `Object(kind:Name,owner_id:Name,port:PortReference,datatype:Datatype,component_refs:List(ProducerReference)?)`. This is the identical wire schema used by NODE.input_ports.producer_ref, EDGE.source_ref, context references and state value references. Its kind is one of G's three reference labels; datatype excludes UNIT. Recursive packages are forbidden, so component references terminate in scalar producer variants.

| kind | owner_id / port resolution | component_refs |
|---|---|---|
| NODE_OUTPUT_PORT | Exact NodeID; its result or genuine decision/committed-value output port. Attribute references preserve their supplied semantic value without inventing execution. | Explicit null |
| STATE_DEFINITION_PORT | Exact StateID; port.role is committed_value and port.ordinal is the canonical ordinal of that state's exact G-authorized INITIAL or POST definition view. That view has WriterIdentity SINGLE and identifies exactly one particular initializer/writer committed output. PRE/current/COMPLETED views and REACHING_SET resolution reject. A state identifier alone supplies no definition. | Explicit null |
| ORDERED_PACKAGE | Exact ContextID of ORDERED_DECODED_PACKAGE; package port, datatype INT4. | Exactly four scalar INT producer references in original field order, equal to that context's component_refs |

STATE_DEFINITION_PORT preserves G §4's PARTICULAR producer. Resolve owner_id to the exact STATE, port.ordinal to its INITIAL/POST view, and that view's SINGLE.writer_ids[0] to the exact existing initializer/writer NODE for the same state and placement. The selected view's value_ref must be NODE_OUTPUT_PORT for that writer's committed_value port with ordinal null and component_refs null; datatype equals the committed scalar type and the state's value_type, not the writer statement's UNIT output_type. This direct committed-port reference terminates resolution without a self-reference or indirection cycle. Its definition/port/state/phase/stage correspondence must be the one positively authorized by G. No caller may choose another view/writer, a runtime predecessor, several committed outputs, a summary or a union producer. The five-field outer schema and three reference kinds are unchanged.

Read definition metadata is separate. A PRE/current/consumed-COMPLETED StateView retains its exact SINGLE or REACHING_SET defining_writer_id and its value_ref identifies the actual STATE_VIEW read NODE's result port. The read's state/view/definition correspondence preserves all G-required initializer/reset/set/update writers and their control facts, including empty-body completion. Consumers reference the actual read result using NODE_OUTPUT_PORT; they do not reference its reaching set as a STATE_DEFINITION_PORT. The read's existing stored_value association remains subject to G §3's exact state/view/definition correspondence; this encoding neither chooses a member of its may-reaching set to fill a producer slot nor adds a definition-use edge. An actual STATE_DEFINITION_PORT in any input, edge or context is admitted only for G's independently supplied particular committed definition with mandatory INITIAL/POST metadata. Missing particular-definition correspondence rejects rather than inventing a producer. Legitimate read reaching metadata remains accessible through the existing STATE/view/context facts and B1 STATE/WHOLE, with no new namespace or set-valued value edge.

EDGE retains exactly `Object(edge_id:EdgeID,construction_clause:ClauseReference,occurrence_path:TaggedPath,edge_type:EdgeType,source_ref:ProducerReference,target_node_id:NodeID,target_port:PortReference,value_type:Datatype,source_role:SemanticRole,target_role:SemanticRole,state_id:StateID?,phase_id:PhaseID?,attachment_ids:SetList(AttachmentID),ordering_key:EdgeOrderingKey,task_essential:true,selector_class:"ATOMIC_SELECTOR_REQUIRED")`. Source payload, edge value_type and destination input datatype agree; UNIT rejects. Target is an actual consuming node/port, never a state/context wrapper. Nullable state/phase facts follow the owning clause, not source reachability.

EdgeType remains, in exact order: INPUT_TO_DECODER, VALUE_TO_PREDICATE, PREDICATE_TO_CONTROL, PREDICATE_TO_INDICATOR, VALUE_TO_OPERATOR, OPERATOR_TO_ACCUMULATOR, CONTROL_TO_UPDATE, LOOP_CARRY, PRIOR_STATE_TO_UPDATE, ACCUMULATOR_TO_OUTPUT. G §§4/27's exact directed-use roles/classes remain unchanged, including I4 package use, numeric prior/carry/output uses, and S versus B controlled-writer distinction. A CONTROL_TO_UPDATE payload can be BOOL while its S activity site is the guarded numeric contribution application; the two types are not coerced into equality. No definition/initialization/persistence/final-expression edge label is added.

## 10. State, view, phase and stage schemas

STATE is exactly `Object(state_id:StateID,semantic_role:StateRole,value_type:Datatype,initialization_attachment_id:AttachmentID,traversal_memberships:SetList(PhaseID),views:List(StateView),writer_node_ids:SetList(NodeID),carry_edge_ids:SetList(EdgeID),completed_consumer_ids:SetList(NodeID))`. value_type is INT or INDICATOR_INT under G's role. Initialization resolves the exact INITIALIZATION_VALUE attachment and its actual state/writer fact. Where G stipulates a per-item indicator reset as the first committed definition, that selected ASSIGN supplies the fact; the reference cannot create an additional INITIALIZE operation. Memberships, writers, carries and consumers use their respective canonical collection orders. Empty carries are valid only for scientifically non-carried local indicators; empty completed consumers only for unused completion. No empty list waives a required record.

StateView is exactly `Object(view_id:ViewAddress,role:ViewRole,phase_id:PhaseID?,stage_role:StageRole,defining_writer_id:WriterIdentity,value_ref:ProducerReference?)`. ViewAddress is `Object(state_id:StateID,view_ordinal:Nat)`: it equals the enclosing state and its position in views[]. G did not assign a CGVIEW namespace; a nested address closes view_id without adding one. It is not a scientific occurrence/RID or a new B1 addressable top-level record. B1 still selects STATE/WHOLE and reaches this nested fact. Duplicate ViewAddress values or mismatched enclosing state/position reject.

WriterIdentity is `Object(kind:Name,writer_ids:SetList(NodeID))`. Kind SINGLE requires one actual defining writer; REACHING_SET requires two or more exact may-reaching initializer/reset/set/update writers in node order. This closes the singularly named field's encoding of G's required reaching-definition identity without guessing one runtime writer. No new definition, execution, branch or read is created. G §§3/9/10 and B1's complete definition references require those facts already. INITIAL/POST require SINGLE for the particular committed definition; PRE/current/COMPLETED preserve the exact scientifically applicable reaching set, using SINGLE only when that set has one writer. Empty-body completion includes its reaching initializer. Runtime outcomes never select the list.

value_ref is the exact committed port for INITIAL/POST, the actual read result for PRE/current/consumed COMPLETED, or null only for unused completion with no value consumer. The defining writer and its state/phase/control placement remain explicit even then. Phase is null only for a fact genuinely outside traversal membership; stage_role remains entry/completion/final.expression/final.output as applicable, never an invented empty string.

PHASE is exactly `Object(phase_id:PhaseID,traversal_ordinal:Nat,domain_role:SemanticRole,direction:Name,index_state_id:StateID,entry_state_ids:SetList(StateID),body_stage_groups:List(StageGroup),completion_state_ids:SetList(StateID),persisted_state_ids:SetList(StateID))`. Direction is FORWARD or REVERSE, the wire spellings of G §§6–7's existing direction facts; reverse is admitted only in the already-frozen training clauses. Index/state membership and all phase identities agree with G's scientific construction. persisted_state_ids retains the completed P state in TWO_PASS without creating a new P write/carry.

StageGroup is exactly `Object(stage_role:StageRole,stage_occurrence_path:TaggedPath,ordering:StageOrdering,member_occurrence_ids:List(OccurrenceID))`. The existing actual member set/sequence is retained. Traversal groups admit only their G §10 stages; final expression/output remain outside traversals in their owning records/paths. ORDERED records the frozen temporal sequence; UNORDERED admits only G's already-qualified pure group and serializes it by path. No stage sequence is reconstructed from array sorting alone. Membership lists preserve distinct operations/uses even when keys are equal.

## 11. Six closed contextual payloads

ContextualRecord is exactly `Object(record_id:ContextID,construction_clause:ClauseReference,occurrence_path:TaggedPath,context_kind:ContextKind,owner_occurrence_ids:SetList(OccurrenceID),payload:Payload,task_essential:true,selector_class:"SUPPORT_ONLY_TASK_ESSENTIAL")`. Payload is selected solely by context_kind, with no second arbitrary tag. Owners are nonempty exact clause-owned occurrences in PathOwnerOrder; direct requirement owners remain separately represented by G prerequisite wrappers. These are not source-accounting dispositions. No category, selector, operation, edge, evidence_kind, mutation or finding field is accepted.

ConsumerReference is exactly `Object(node_id:NodeID,port:PortReference,datatype:Datatype)`, with non-UNIT datatype and an exact actual consuming port. Consumer lists retain a scientific sequence when one is required; otherwise target-node/port order. They do not imply an added edge.

Every payload field has a frozen clause provenance in this exhaustive table. All listed fields are mandatory and in the displayed order. Null and empty-list conditions are fixed below.

| context_kind / payload type | Fields, exact types and frozen meaning |
|---|---|
| STATIC_BINDING / StaticBindingPayload | `state_id:StateID?` (same storage identity when this is a storage binding, otherwise null for a pure non-storage name-to-role/definition association, G §§3/9/10/21); `binding_role:SemanticRole` (same bound local role, §§3/10/19); `phase_ids:SetList(PhaseID)` (existing lifetime/membership, §§9/10/21); `definition_refs:List(ProducerReference)` (exact definition associations, §§3/9/10/21). |
| ORDERED_DECODED_PACKAGE / DecodedPackagePayload | `datatype:"INT4"` (G §§3/7); `component_refs:List(ProducerReference)[4]` (four FIELD_VALUE producer refs in original positions, §§3/4/7); `conversion_refs:List(ProducerReference)[4]` (their exact TO_NUMBER parents, §§7/16/24). |
| EXPRESSION_RESULT_REFERENCE / ExpressionResultPayload | `producer_ref:ProducerReference` (one actual defining result port, G §§3/15/24); `consumer_refs:List(ConsumerReference)` (actual uses/final display association, §§3/15/21/24). |
| INITIAL_POST_DEFINITION / InitialPostPayload | `state_id:StateID` (G §§10/21); `view_role:INITIAL/POST` (committed definition, §§3/10); `writer_identity:WriterIdentity` (SINGLE, same particular actual defining writer, §§9/10); `phase_id:PhaseID?` (exact placement or outside-traversal null, §10); `stage_role:StageRole` (same temporal fact, §§10/21); `value_ref:ProducerReference` (that one committed definition port, §§3/10/24, resolving under §9). |
| COMPLETION_PERSISTENCE / CompletionPersistencePayload | `state_id:StateID` (G §§10/15/21); `completed_phase_id:PhaseID` (same completion, §§10/15); `persisted_phase_ids:SetList(PhaseID)` (exact G immutable interval or empty when absent, §§10/15/24); `completed_value_ref:ProducerReference?` (actual consumed completed-read result or unused-completion null, §§3/10/15); `consumer_refs:List(ConsumerReference)` (exact G consumption associations, §§10/15/21); `immutable:Bool` (true iff this exact record represents G's explicit immutable-persistence relation; otherwise false, §§10/15/24). |
| PROVENANCE / ProvenancePayload | `specification_binding:SpecificationBinding` (same frozen provenance, G §§2/5); `identified_record_ids:SetList(RecordID)` (exact non-requirement records identified, §§19/21); `identified_requirement_ids:SetList(RequirementID)` (exact owner/requirement identity, §21). RequirementID values occur only in the latter list; wrapper addresses do not become support premises. |

STATIC_BINDING adds no execution; definition_refs can be empty only for a genuinely uninitialized static declaration, not for an executed initializer relabeled as context. A non-storage definition association has nonempty exact producer references and state_id null; a storage binding identifies its existing state and its matching local index/indicator/count/result role. The phase list can be empty only when that association has no traversal lifetime. No source variable spelling is serialized. Package components are exactly four distinct original field positions and their corresponding conversions; no sorting/deduplication/assembly/read operation occurs. Expression-result contexts contain references, never executable expression trees or a new carrier. Their consumer list contains precisely the supplied G associations; it is nonempty for the required final-display association.

INITIAL_POST definitions retain their own schema only when the owning G clause actually supplies that association; the schema does not generate a duplicate wrapper for every state/view. The corresponding definition view and payload require the same SINGLE writer and particular committed port; read reaching sets cannot populate this definition-only payload.

Completion encoding first reconstructs the exact clause-authorized completion/consumption/persistence fact from G, then checks these exhaustive wire cases. immutable is a redundant presence/absence encoding of G's explicit immutable-persistence relation, never an input deciding that relation. False is not an independent scientific claim that the state is mutable. There is no third/unknown value, omitted flag or caller-selected Boolean.

| Existing G completion case | immutable | persisted_phase_ids | completed_value_ref | consumer_refs |
|---|---|---|---|---|
| Unused completion metadata, no value consumer and no immutable-persistence relation | false | Empty | Explicit null | Empty |
| Consumed completion without G's immutable-persistence relation, including completed TOTAL display consumption and non-persisted final operands under their owning clauses | false | Empty | Exact NODE_OUTPUT_PORT result of the corresponding actual completed STATE_VIEW read | Nonempty, exactly the G-required consuming ports/associations |
| TWO_PASS completed-P immutable persistence across the second traversal, G §§10/15 | true | Nonempty, exactly the second traversal's already-frozen persistence interval | Exact NODE_OUTPUT_PORT result of the same completed-P read, retaining its full reaching-definition metadata | Nonempty, exactly G's later completed-P consumption, including its final product operand |

Every case requires the exact existing state_id/completed_phase_id, the matching COMPLETED StateView and its reaching writers, and agreement with STATE.completed_consumer_ids and the corresponding PHASE/TraversalRecord persistence facts. A consumed reference equals that view's actual read-result value_ref and has the state's scalar datatype; consumer ports/types match the same G association. For unused completion the matching view has value_ref null, with its mandatory definition metadata retained. A consumed completion outside a later traversal does not acquire a persisted phase merely because it is consumed. The current frozen immutable relation is TWO_PASS completed P across phase 2; completion of another state, empty-body metadata or ordinary final consumption cannot borrow it. Missing/extra phases, references or consumers and mismatched state/phase/view/Boolean facts reject. These cases constrain only already-authorized records and do not manufacture a wrapper or attachment. PROVENANCE's copied specification equals the root binding; its two identified lists jointly identify at least one exact record/requirement and create no owner by themselves.

Canonical graph construction precedes actual source. These payloads bind the exact canonical association that later B1 ContextCorrespondence must pair with original source facts. They contain no fabricated source ID, source text, empty proof, raw-inventory outcome or placeholder mapping. Actual source identity remains in B1/R's exact independently parsed inventory and typed references; D2 must still establish the complete same-program source/context/owner join. Thus preserving canonical identity does not invent prior source evidence.

## 12. Attachments and thirteen value bindings

ATTACHMENT retains exactly `Object(attachment_id:AttachmentID,construction_clause:ClauseReference,owner_occurrence_id:OccurrenceID,kind:AttachmentKind,semantic_role:SemanticRole,port:PortReference?,value:AttachmentValue?,referenced_occurrence_ids:List(RecordID))`. Owner exists; port is null exactly when the fact is not port-specific. Referenced IDs remain separate from value payload and resolve to the exact G facts. They order by graph record-family/collection order, with requirements/prerequisites after supported records, unless the kind owns a scientific sequence such as original fields or temporal members. The owning G clause must positively authorize every reference and its role; the wider typed address union creates no new reference fact or support ownership. No scientific sequence is deduplicated merely because an ID repeats at two formal positions.

TypedValue is `Object(datatype:Datatype,value:PayloadScalar)`, with UNIT excluded. PayloadScalar is BOOL→Bool, INT→Int, INDICATOR_INT→integer 0/1, TEXT→String, TEXT4→exactly four Strings, INT4→exactly four Ints, matching existing B1 §8 lossless values. This representation is not execution/intervention data here.

ReferenceLayout is `List(Name)`, one entry per referenced_occurrence_ids position, zipped with that array. Allowed labels in order: STATE, PHASE, INITIALIZER, WRITER, READ, VALUE, PRODUCER, CONSUMER, PARENT, ATTRIBUTE, DISPLAY, DEFINITION, FIELD, CONVERSION, ORDER_MEMBER, COMPLETED_SOURCE, PERSISTED_PHASE. Each denotes only its G §24 reference role. The paired lists remain aligned when canonical reference order is applied; if equal referenced IDs occupy different reference roles, the layout-role ordinal breaks only that representation tie. A kind-owned scientific sequence always retains its formal positions instead. Repeated FIELD/ORDER_MEMBER labels retain positional meaning. A layout never introduces a reference or invents an owner. Exact IDs are not duplicated in arbitrary text or value objects.

The following is the complete AttachmentValue discriminated by the outer kind. Object sequences are exact. Additional `kind` tags are used only in DomainFact, where multiple already-frozen domain facts occur. This wire normal form uses the specified non-null value schema for every one of the thirteen current cases, including reference-only associations: their association object carries the already-required local role/reference layout, while an absent scalar uses its specified inner null. An outer null is not an alternative encoding of that same fact. G §24 requires explicit null when a port/value is absent, but identifies no separate current attachment profile with an expressly fixed absent outer value. No such profile is invented here; the schema's nullable slot is retained, with no authorized current outer-null case. Port null and all scientifically absent nested scalar/stage values remain explicit. Except for G's mandated literal separator, no arbitrary scalar/blob is accepted.

| AttachmentKind | Non-null value schema and scientific provenance |
|---|---|
| PREDICATE_ROLE | PredicateBinding; exact frozen role/name/definition, G §§8/24. No unused metadata predicate is materialized. |
| DOMAIN_ROLE | DomainFact: `Object(kind:"NUMERIC_DOMAIN",lower_bound:0,upper_bound:null)`; `Object(kind:"ARRAY_DOMAIN",field_count:4,element_type:"INT")`; `Object(kind:"FIELD_POSITION",ordinal:Nat)` restricted 0–3; `Object(kind:"ORIGINAL_INDEX",datatype:"INT")`; or InputDomainObligation. G §§6/7/16/24. The SPLIT configuration case is exactly the raw String `"\|"`, semantic_role decoder_separator_configuration, port null, as G §24 explicitly fixes. |
| STATE_IDENTITY | StateIdentityFact = `Object(state_role:StateRole,reference_roles:ReferenceLayout)`; same actual storage identities, G §§10/24. |
| PHASE_MEMBERSHIP | PhaseMembershipFact = `Object(stage_role:StageRole?,reference_roles:ReferenceLayout)`; stage null only for whole-phase membership, G §§10/24. |
| STATE_VIEW | StateViewFact = `Object(view_role:ViewRole,view_ordinal:Nat,stage_role:StageRole,reference_roles:ReferenceLayout)`; state reference plus view_ordinal resolves ViewAddress, G §§3/10/24. |
| OPERAND_ROLE | OperandFact = `Object(local_role:SemanticRole,reference_roles:ReferenceLayout)`; exact formal port/role already in outer port, G §§4/24. |
| ACCUMULATOR_ROLE | AccumulatorFact = `Object(local_role:SemanticRole,reference_roles:ReferenceLayout)`; prior versus contribution facts remain distinct, G §§10/24. |
| INITIALIZATION_VALUE | InitializationFact = `Object(value:TypedValue?,stage_role:StageRole,reference_roles:ReferenceLayout)`; exact constant initialization where applicable, G §§10/16/24. Input-dependent index initialization has value null, with exact initializer/value/state references instead of a guessed constant. This is the same InitializationFact nullable-value case, not another scientific initializer. |
| OUTPUT_RELATION | OutputRelationFact = `Object(local_role:SemanticRole,reference_roles:ReferenceLayout)`; completed state/expression and actual display, G §§15/17/24. |
| VALUE_ASSOCIATION | ValueAssociationFact = `Object(value:TypedValue?,local_role:SemanticRole,reference_roles:ReferenceLayout)`; scalar value null for a runtime carrier/package association, never a sampled value; exact fixed value when present, G §§7/16/24. |
| DEFINITION_ASSOCIATION | DefinitionAssociationFact = `Object(local_role:SemanticRole,reference_roles:ReferenceLayout)`; exact one defining expression/write relationship, G §§3/10/24. |
| ORDER_RELATION | OrderRelationFact = `Object(ordering:StageOrdering,stage_roles:List(StageRole),reference_roles:ReferenceLayout)`; sequence and qualified unordered group retain their scientific meaning, G §§10/14/15/24. |
| COMPLETION_PERSISTENCE | CompletionFact = `Object(view_role:"COMPLETED",immutable:Bool,reference_roles:ReferenceLayout)`; exact G-authorized completion/persistence association, G §§10/15/24. immutable is true iff that same canonical fact contains G's explicit immutable-persistence relation, otherwise false, under the exhaustive §11 rule. ReferenceLayout retains only that fact's existing references. |

INITIALIZATION_VALUE's typed constant can be INT or INDICATOR_INT only, with its exact writer/state/placement; an input-dependent value is bound by references and null scalar value, never supplied by an evaluated case. STATE_VIEW includes only the already-required view address, not a new read. ReferenceLayout labels and kind-specific role/type checks disambiguate all associations without promoting any to an atomic relation. An association object is a lossless packaging of mandatory facts, not a new fact supplied merely to avoid null. Known scalar/role facts cannot be dropped, and a value shape belonging to another attachment kind rejects. An independently found frozen profile expressly requiring outer null would need review against this table rather than silently selecting another representation.

CompletionFact uses §11's same derived Boolean in every admitted completion case: absence of G's explicit immutable-persistence relation requires false; TWO_PASS completed-P persistence requires true. False supplies no mutability proof. The attachment's existing owner/references/layout must resolve the precise clause-authorized completed state/view, phase and any interval/consumer; they cannot create or remove persistence. Wherever an attachment and context represent the same canonical completion fact, their Boolean, state/view/phase identity, interval and consumption references must agree with each other and the corresponding STATE/PHASE records. Equality is checked through those existing typed references, not inferred merely from a shared state name or raw reachability. Absence of a duplicate context does not leave the attachment flag free: it is still checked against G and the same state/phase/view facts. This synchronization adds no field/reference family and authorizes no new attachment case.

## 13. Requirements, selector subobjects and reusable keys

REQUIREMENT is exactly `Object(requirement_occurrence_id:RequirementID,canonical_contract_key_id:KeyID,selected_occurrence_id:NodeID|EdgeID,selector:Selector,required_multiplicity:Positive,multiplicity_position:Nat,attachment_ids:SetList(AttachmentID),evidence_kind:EvidenceKind,scientific_evidence_class:ScientificEvidenceClass,obligation_scope:ObligationScope)`. Current G §20 requires each independently emitted requirement's multiplicity exactly 1; the Positive shape is not permission to change it. multiplicity_position is the static position, independent of runtime counts. Selection kind and occurrence type agree; attachments are the complete required ordered set.

Selector is exactly `Object(kind:SelectorKind,category:Category,operation_or_edge_type:NodeOperation|EdgeType,domain:Family,input_types:List(Datatype),output_type:Datatype,local_roles:LocalRoles,predicate_identity:PredicateIdentity?,value_requirement:ValueRequirement?,output_requirement:OutputRequirement?,state_view_role:StateViewRole?,interface_obligation:InputDomainObligation?,activity_site:ActivitySite?,relation_marker:RelationMarker)`. Every nullable field is present. Base NODE input/output types follow G §20; EDGE has category ATOMIC_CONTROL_DATAFLOW, one payload input and the same payload output. UNIT is legitimate only for the appropriate NODE result, never EDGE payload.

| Nullable selector field | Non-null rule; otherwise explicit null |
|---|---|
| predicate_identity | The selector directly identifies a frozen named primitive identity. An unrelated neighboring operator/edge cannot inherit it. |
| value_requirement | Exactly VALUE_OR_LITERAL attribute profiles, with the matching computed/literal/runtime variant. |
| output_requirement | Exactly OUTPUT_CATEGORY attribute profiles, with the matching category/sentinel variant. |
| state_view_role | A selected actual state read or directed use whose local semantics consume that named state view. NODE STATE_VIEW uses its actual view; LOOP_CARRY uses its destination PRE (its source POST remains explicit in local_roles); PRIOR_STATE_TO_UPDATE uses source PRE; ACCUMULATOR_TO_OUTPUT uses source COMPLETED; a direct VALUE_TO_OPERATOR/state operand uses the exact source PRE/COMPLETED fact. No transitive neighborhood view is imported. |
| interface_obligation | Exactly the additional INPUT_DOMAIN NODE profile on INPUT. Base INPUT and every constituent retain null. |
| activity_site | Every BEHAVIORAL profile, with its exact accepted typed site; all value/literal/output attributes have null. |
| relation_marker | Exactly the certified additional local J profile. Base NODE/EDGE and INPUT_DOMAIN have null. |

LocalRoles is `List(SemanticRole)` in the local formal input/operand/result/association order required by the profile, retaining duplicates. It encodes no path, exact state/phase/field ID, task provenance or whole neighborhood. Per-use exact positions are attachments. PredicateIdentity is `Object(frozen_predicate_name:PrimitiveName,definition_reference:PredicateDefinitionReference)`; it retains the named primitive identity and exact definition but no occurrence/slot identifier. It is null only when the profile has no named primitive identity; a predicate's P/Q metadata role is not smuggled into reusable identity as a task topology field.

ParentCapability is `Object(parent_kind:Name,parent_key_projection:KeyProjection?,local_role:SemanticRole)`. parent_kind is ACTIVE_BEHAVIORAL_PARENT or INITIAL_ACCUMULATOR, retaining D §9.1.2/G §16's exact prospective distinction. For ACTIVE_BEHAVIORAL_PARENT, parent_key_projection is the exact already-required immediate behavioral parent's reusable projection, including its types, named primitive and local roles. An operation/category abbreviation is insufficient to preserve parent capability identity. Its value_requirement/output_requirement are null because this is a behavioral parent; consequently this nested type terminates without recursive attribute-parent chains. G §16 fixes which base behavioral parent applies, such as INPUT or the corresponding TO_NUMBER; an additional macro/J profile cannot be substituted. For INITIAL_ACCUMULATOR, parent_key_projection is null and local_role is initial_accumulator. This carries only the local prospective parent key meaning G §20/D §9.1.2 require; it adds no parent occurrence/phase, source, whole neighborhood or higher-order template. Actual parent identity is an occurrence attachment. No active finding selects the parent.

ValueRequirement is the closed union:

| kind | Exact variant fields/order |
|---|---|
| COMPUTED_VALUE | kind, datatype:INT/INDICATOR_INT, computed_integer:Int, local_role:SemanticRole, parent_capability:ParentCapability |
| LITERAL_TOKEN | kind, exact_lexeme:Name, parent_capability:ParentCapability |
| RUNTIME_VALUE_ROLE | kind, datatype:INT, local_role:decoded_n/decoded_field, parent_capability:ParentCapability |

All variants are Objects with those exact keys; INDICATOR_INT computed_integer is 0/1. LITERAL_TOKEN requires independent frozen authorization; current G emits none. Runtime variants contain no sampled integer, field ordinal, occurrence ID or evidence. Fixed numbers remain exact scientifically required values, not source literal spellings.

OutputRequirement is `Object(kind:"CATEGORY",output_category:OUTPUT_ZERO|OUTPUT_POSITIVE|OUTPUT_NEGATIVE|OUTPUT_MULTIDIGIT,exact_sentinel:null)` or `Object(kind:"EXACT_SENTINEL",output_category:null,exact_sentinel:Int)`. Current G authorizes no sentinel. Its family is already selector.domain. It contains no case, declaration proof, another contract's categories or complete function.

StateViewRole is `Object(storage_role:Name,view_role:ViewRole,value_type:INT|INDICATOR_INT)`. storage_role is index/indicator/count/result, G §20's local typed storage/use role; occurrence-specific TOTAL/PRIOR_P_COUNT/P_COUNT/Q_COUNT identities and phase placement remain attachments. The supplied scientific local role is retained; count is not a permission to confuse distinct count states. No PREFIX/TWO_PASS template name enters this reusable object.

InputDomainObligation is `Object(kind:"INPUT_DOMAIN",domain:Family,root_datatype:INT|TEXT,decoded_datatype:INT|INT4,field_count:Nat?,separator:String?,lower_bound:Int?,upper_bound:Int?,decoder_operations:List(NodeOperation),classes:List(InputClassDeclaration))`. Numeric has root/decoded INT, field_count/separator null, lower_bound 0, upper_bound null and decoder_operations [INPUT]. Array has root TEXT/decoded INT4, field_count 4, separator exactly pipe, lower/upper null and operations INPUT,SPLIT,TO_NUMBER,TO_NUMBER,TO_NUMBER,TO_NUMBER in original field order. This operation schema binds G's already-frozen complete interface macro, not actual node IDs or a new capability for each conversion. Actual four calls and fields remain independent occurrences.

InputClassDeclaration is `Object(class_id:Name,applicability:Name)`. Numeric classes in order are SIGN_ZERO REQUIRED, SIGN_POSITIVE REQUIRED, EMPTY_LOOP REQUIRED, LOWER_DOMAIN_BOUNDARY REQUIRED, SIGN_NEGATIVE NOT_APPLICABLE, UPPER_DOMAIN_BOUNDARY NOT_APPLICABLE. SIGN_NEGATIVE is the wire label for the frozen table's negative-sign row; UPPER_DOMAIN_BOUNDARY for its upper-boundary row. Array classes are NEGATIVE_PRESENT REQUIRED, ZERO_PRESENT REQUIRED, POSITIVE_PRESENT REQUIRED, EMPTY NOT_APPLICABLE, BOUNDARY NOT_APPLICABLE. The existing INPUT_DOMAIN authority fixes each membership predicate and applicability; these two formerly prose-only numeric row labels merely address those exact rows and add no class/witness. No case or sampled pool endpoint appears.

ScientificEvidenceClass is exactly a String: B/N/F/A/T4/I4/S/D/C/J for BEHAVIORAL, COMPUTED_VALUE/LITERAL_TOKEN/RUNTIME_VALUE_ROLE for VALUE_OR_LITERAL_ATTRIBUTE, CATEGORY/EXACT_SENTINEL for OUTPUT_ATTRIBUTE, using the existing G/D/B1 meanings. Current G emits no C/LITERAL_TOKEN/EXACT_SENTINEL profile. ObligationScope is exactly BOTH_CONDITIONS or COMPOSITION_ONLY_LOCAL_PAIR_JOINT, B1's existing serialization of G's rule; only the separately certified local J profile admits the latter.

For base operation/edge profiles relation_marker is null. INPUT_DOMAIN is only a separate NODE profile on INPUT with non-null interface_obligation; it creates no third selector kind. Its exact root/site/class remains separately resolved. The certified local J profile has the exact existing marker and actual AND/MUL selector/type/site. Only its reusable key projection applies G §20's canonical AND/two-BOOL-input/BOOL-result/joint_left-joint_right/Boolean-site representative. Base AND/MUL selectors/keys retain B/N, and no general Boolean/integer cast or count/PREFIX normalization is introduced.

KeyProjection is the exact Selector sequence excluding kind: category, operation_or_edge_type, domain, input_types, output_type, local_roles, predicate_identity, value_requirement, output_requirement, state_view_role, interface_obligation, activity_site, relation_marker. Its nested types are exactly those above, with explicit nulls and the sole frozen J projection exception. B, condition, population, slot/task/program/source IDs, occurrence paths/IDs/ordinals, multiplicity, exact state/phase/field identities and full neighborhoods are absent. Any activity-site PortReference in a reusable projection has ordinal null: a schema slot exists but carries no occurrence ordinal, and the exact original field/state-view position remains attached to the occurrence. Lossless nested encoding preserves equality of the scientific projection; it may determine different representation bytes from another encoding but does not change which abstract capability is equal.

## 14. Prerequisite wrapper and implicit CGPREREQ address

PREREQUISITE remains exactly `Object(prerequisite_record_id:SupportedID,prerequisite_record_kind:Name,owner_requirement_occurrence_id:RequirementID,construction_clause:ClauseReference,pairing_role:SemanticRole,pairing_position:Nat)`. Kind is CONTEXT/NODE/EDGE. NODE/EDGE selects that exact occurrence; CONTEXT selects a STATE/PHASE/ATTACHMENT/contextual record under its own existing namespace/schema. It never selects another wrapper to infer transitive ownership.

`prerequisite_record_id` is the SUPPORTED record's ID. It is not overwritten with the wrapper's own CGPREREQ address and no seventh key is added. The wrapper's exact representation address is the existing G §5 CGPREREQ formula, recomputed from its six fields and root provenance (§16). B1's PREREQUISITE ComponentRef.record_id selects this derived CGPREREQ value uniquely in prerequisites[]. ContextBinding.canonical_context_record_id can use that address when identifying the wrapper. This resolves the formerly ambiguous naming while preserving both supported-record identity and the frozen formula.

Every owner requirement and supported record must exist with matching kind. pairing_role and position retain the exact G §21 immediate constructive fact and local occurrence, not an ancestor/path discovered from source. Atomic prerequisites retain their independent requirements/evidence. Shared support has the actual separate direct wrappers, with no inherited owners and no fifth accounting bucket. The wrapper's address is immutable before use and is not a hash of final graph bytes.

## 15. Complete-function symbolic wire grammar

CompleteFunction retains exactly `Object(grammar_version:RecipeVersion,used_predicate_roles:List(PredicateBinding),domain_definition:DomainDefinition,contribution_term:List(ContributionRecord),state_equations:List(StateEquation),initialization:List(InitializationRecord),ordered_traversals:List(TraversalRecord),output_expression:Expression)`. The singular field name contribution_term carries the ordered already-required per-state/per-phase terms: this lossless list accommodates G's one total, PREFIX's two updates and TWO_PASS's separate count terms without a new aggregator tag or semantic branch.

used_predicate_roles contains exactly the actual referenced roles, in P/Q/R/S order (or the single DESIGNATED entry), each with the bound eight-predicate definition reference. G1 has three, structural terms P/Q only; unused rotation metadata is not a symbolic input. Predicate applications refer back to these bindings; identical role/definition references preserve sharing across distinct operand uses.

DomainDefinition is `Object(domain:Family,input_schema:InputDomainObligation,index_datatype:"INT",index_lower:Expression,index_upper:Expression)`. Numeric bounds encode 1 and decoded n; array bounds encode 0 and 3. input_schema retains the complete valid input domain, not a construction sampling pool. Reverse traversal changes its direction/initializer/decision/step record, not the domain or original index. No arithmetic/overflow/modulo convention is introduced; frozen language/reference semantics remains controlling.

### 15.1 Recursive expression variants

Expression is exactly one of the following ordered Objects. Every recursive child is an Expression. An expression is a symbolic representation of an already-required value/term, not a graph NODE. No expression variant grants permission for an additional computation.

| Variant | Exact fields/order and type |
|---|---|
| ConstantExpression | `kind:"CONSTANT",datatype:INT\|INDICATOR_INT,value:Int`; indicator value exactly 0/1 |
| DomainValueExpression | `kind:"DOMAIN_VALUE",role:decoded_n\|decoded_field\|indexed_value,field_ordinal:Nat?`; ordinal 0–3 only for an explicitly identified decoded field, null for decoded_n or the current indexed numeric value (indexed_value) |
| IndexValueExpression | `kind:"INDEX_VALUE",phase_id:PhaseID,role:"original_index"`; exact current original index, not iteration rank substituted for it |
| StateViewExpression | `kind:"STATE_VIEW",state_id:StateID,state_role:StateRole,view_role:ViewRole,phase_id:PhaseID?,stage_role:StageRole`; role/state/placement must match the graph's exact existing fact |
| NamedPredicateExpression | `kind:"NAMED_PREDICATE",slot_role:SlotRole,arguments:List(Expression)`; non-null bound role; arguments in exact G §8 runtime-dependency order, referring to the frozen definition |
| OperatorExpression | `kind:"OPERATOR",operation:Name,datatype:Datatype,operands:List(Expression)`; one of the exact pure operators below, fixed arity and types |

Pure operator signatures are exactly: NEG(INT)→INT; ADD/SUB/MUL/MOD(INT,INT)→INT; EQ/LT/LE(INT,INT)→BOOL; AND/OR(BOOL,BOOL)→BOOL; BOOL_TO_INT(BOOL)→INDICATOR_INT. The frozen INDICATOR_INT refinement is admissible as an integer operand while retaining its declared type; the permitted 0/1 result refinement is recorded only where G stipulates/proves it. There is no implicit BOOL↔INT coercion. No operator with UNIT/TEXT/package output is admitted in this pure term union. Package indexing/decoding remains the domain/graph obligation, not an invented symbolic arithmetic operator.

Operands retain arity, ordering, repeated occurrences and exact binary association. Allowed local pure commutative normalization remains only G/V3.3's frozen rule and original-position tie-break; serialization performs no algebraic normalization. A repeated predicate leaf identifies the same bound producer role, while the complete graph retains its distinct consumer edges/ports. Named predicates resolve the exact eight trees in G §8; their runtime argument counts/order are odd_index/residue_two: original index; divisor_index: decoded n then original index; first_half: original index then decoded n; negative_value/even_value/large_magnitude: current indexed value; value_exceeds_index: original index then current indexed value. Definition constants/repeated value*value operands remain in the bound exact tree, not an implementer-selected equivalent predicate.

No SUM/PREFIX/TWO_PASS macro, general function call, arbitrary AST/source fragment, hidden state, execution result, sampled output, Boolean vector, proof status or E5 result variant exists. G's sum/strict-prior/product laws are represented by the following exact equations, phases and output term. A required expression outside this closed grammar is a blocking authority/profile problem, not an extensible JSON node.

A current indexed DomainValueExpression is lexically bound to the enclosing ContributionRecord, StateEquation or TraversalRecord phase and its actual INDEX_READ; it cannot occur outside that context or resolve a value from another phase. Explicit IndexValueExpression.phase_id must agree with the same lexical phase. Direct decoded fields and decoded n bind the one frozen input domain rather than a sampled value.

### 15.2 Contributions, equations and initialization

ContributionRecord is `Object(state_id:StateID,phase_id:PhaseID,stage_role:StageRole,term:Expression)`. It names only the already-frozen applied contribution to that exact count/result state. Records follow traversal then G stage/state order. The contribution term's identity does not replace the arithmetic result, ASSIGN writer, prior relation or independent selector in the full graph.

StateEquation is `Object(state_id:StateID,phase_id:PhaseID,stage_role:StageRole,before_view:StateViewExpression?,after_view:StateViewExpression,guard:Expression?,expression:Expression,writer_node_id:NodeID)`. It encodes an existing ASSIGN/update and its exact POST identity/actual writer. before_view is non-null exactly for the actual prior/current-state dependency consumed by that update, such as count accumulation or index step; it is null for an overwrite such as indicator reset/set that consumes no previous value. A null dependency is not an unavailable proof and does not create a fictitious read. guard is null for an unconditional update and the exact existing Boolean IF/guard term when one controls that assignment; traversal membership supplies the bounded iteration, so no duplicate per-update loop execution is invented. Assignment to a local indicator is not given an inter-item carry. Records retain the frozen ordered stage and writer order; qualified pure evaluation does not reorder updates.

InitializationRecord is `Object(state_id:StateID,phase_id:PhaseID?,stage_role:StageRole,writer_node_id:NodeID,value:Expression)`. It records the actual INITIALIZE writer and exact value/placement: fixed total offset/zero, index initializer including decoded n for reverse numeric traversal, and Q initialization at second-phase entry as applicable. Null phase is only the existing outside-traversal initialization. Resets/sets are ASSIGN equations, not relabeled initializations. Lists preserve the actual scientific placement and state identity; no sampled initial value is allowed. An entry stage inside body_stage_groups denotes the already-required per-item entry work; an entry InitializationRecord denotes the actual outside-body/phase-entry writer. Their container, owning clause and existing membership distinguish them without another stage, phase or execution. A state initialization attachment referring to its first reset does not require an extra InitializationRecord or operation.

The complete_function lists represent every existing output-affecting state dependency and the supplied frozen control/index/indicator scaffold needed to establish completeness. They are redundant symbolic descriptions of the complete graph, not extra scientific operations or an alternative builder. Any mismatch in a state, writer, guard, value, phase or dependency rejects. No equation is generated simply because a schema variant exists.

### 15.3 Ordered traversal records and output

TraversalRecord is `Object(phase_id:PhaseID,traversal_ordinal:Nat,domain_role:SemanticRole,direction:FORWARD|REVERSE,index_state_id:StateID,initial_index:Expression,bound_condition:Expression,step_expression:Expression,body_stage_groups:List(StageGroup),completion_state_ids:SetList(StateID),persisted_state_ids:SetList(StateID))`. It is the same PHASE facts plus their exact frozen index/bound/step symbolic terms, with no extra phase. Phase, ordinal, state, domain, direction, groups/completion/persistence equal the corresponding graph record. Bound_condition is BOOL; initializer/step INT. Entry initialization remains in initialization[]; its expression equals initial_index. Each ordered traversal is complete over the same frozen domain.

For numeric forward, initializer 1, decision index≤n, step ADD(index,1); reverse training initializer n, decision 1≤index, step SUB(index,1). Array forward is 0, index≤3, ADD(index,1); reverse training is 3, 0≤index, SUB(index,1). These are G's existing terms, stated symbolically without instantiating an input, phase ID or program. n=0 retains the required logical phases/initializers/completions.

output_expression is the exact final integer Expression, never a DISPLAY execution or output witness. G training/primary/sanity retain completed TOTAL and exact offset/contribution law. PREFIX retains TOTAL and PRIOR_P_COUNT equations, strict PRIOR_P_COUNT PRE in Q's contribution, result update before P update, both carries, zero initialization and one traversal. TWO_PASS retains P-only first traversal, completed immutable P persistence, Q initialization at second entry, Q-only second traversal, and final MUL of the two COMPLETED states after both completions. FINAL_RESULT is the expression port role, not a stored state. A fused one-loop count product is not encoded as this topology even when its function agrees.

Losslessness follows by induction: each leaf retains its exact type/value/role or named state/definition address; each operator retains its operation, ordered full child list and result type; equations retain both state views, guard, writer and placement; traversals retain original bounds/step/order/completion/persistence; output retains the final dependency. Decoding reconstructs the same abstract symbolic structure with no missing dependency or new rewrite. E5 still requires its own completeness-certified semantic comparison, not structural JSON equality.

## 16. Exact representation identities, unchanged

V is exactly CONF1_CG_RECIPE_V2. B is exactly `8a9bfe3c4ad3b687261f486189285156b4c1843e53bfbd20b0bc35c4f07d09e8`. Provenance components are population_kind, slot_identity, family, condition-or-literal-NONE. Evaluation contributes the String `NONE`, never JSON null/empty/omitted framing. Training contributes ISOLATED or COMPOSITION. Port absence in CGATTACH likewise contributes literal NONE.

`RID(namespace, components)` is D §3.3's existing exact ASCII label followed, for every exact UTF-8 component, by `|` + minimal decimal UTF-8 byte length + `:` + those bytes. The existing controlling implementation is `self_learning_ai.conf1_v3.interfaces.rid`; this document implements no framing algorithm. RIDs are exact strings, not digests of themselves. Canonical fragments use §17's compact schema-ordered JSON without a final LF.

| Namespace | Exact ordered component list |
|---|---|
| CGNODE / CGEDGE / CGSTATE / CGPHASE / CGCONTEXT | V, B, population_kind, slot_identity, family, condition-or-NONE, canonical JSON TaggedPath |
| CGATTACH | V, B, same four provenance components, owner_occurrence_id, kind, port-or-NONE, canonical JSON `Object(semantic_role,value,referenced_occurrence_ids)` |
| CGREQ | V, B, same provenance, selected_occurrence_id, minimal decimal selector-profile ordinal |
| CGKEY | V, canonical JSON exact thirteen-field KeyProjection |
| CGPREREQ | V, B, same provenance, owner_requirement_occurrence_id, prerequisite_record_kind, prerequisite_record_id, pairing_role, minimal decimal pairing_position |

For a non-null CGATTACH port, its String component is canonical JSON of the bound PortReference, preserving the existing formula's port component without changing component count/order. If pairing_role is the bound SemanticRole String it is inserted verbatim; no alternative prerequisite formula is introduced. Profile ordinal is base 0, INPUT_DOMAIN additional INPUT profile 1, or certified local J additional result profile 1; no occurrence supports both additional profiles. Malformed integer/profile values reject, including bool. No new namespace is required. ViewAddress is a nested typed address and never consumes a tenth representation namespace.

CGKEY omits B and all program/task/condition/path/occurrence/multiplicity provenance, exactly as G requires. Authority binding remains outside the reusable key. Namespace, V/B/provenance, canonical path and all fragment fields are independently validated; mixed V1/V2 or mismatched authority values reject. No new ID or key instance is created by this document.

## 17. Canonical JSON, reconstruction and integrity digest

Canonical emitters reconstruct every object from its closed typed fields in the exact listed schema order. Caller dictionary insertion order cannot affect bytes. Unknown/missing/duplicate keys fail before reconstruction. Arrays must already have their prescribed order and are never auto-corrected. A parser can accept an unordered in-memory mapping as a supplied typed value; accepting a supposedly canonical serialized document additionally requires byte-for-byte equality to reconstructed canonical serialization, so wrong key order/whitespace/escape choices fail canonical-byte validation.

Strings use double quotes; escape quote and backslash as `\"` and `\\`; use `\b`, `\f`, `\n`, `\r`, `\t` for those five controls, and lowercase `\u00xx` for the other U+0000–U+001F controls. Backslashes in this sentence denote the literal JSON escape bytes, not a second escaping layer. All other Unicode scalar values are emitted literally in UTF-8, including non-ASCII and U+2028/U+2029. Do not escape solidus or ordinary Unicode alternatively. No BOM or normalization, trimming, case conversion or surrogate acceptance. These lexical choices select one lossless encoding; they do not equate different strings.

Object/array separators are comma/colon with no optional whitespace. Null is `null`; Booleans are `true`/`false`; exact integers use minimal signed decimal with no plus, leading zeros, decimal point, exponent or negative zero. No float coercion or binary-float rounding is permitted. All schema constants/enums retain their exact case/spelling.

An identity fragment is the complete compact UTF-8 JSON value with no terminating newline. A graph document is the complete compact Graph JSON followed by exactly one byte LF (`0a`), with no other document whitespace. Embedded string newlines use the specified escapes. SHA-256 graph integrity input is exactly that entire byte sequence including the single final LF, with no own digest field, byte normalization, external wrapper or omitted authority/provenance field. This digest is representation integrity only; it is neither a CG representation ID nor an E5 isomorphism/semantic-equality result.

## 18. Structural validation, compatibility and versioning

The eventual structural validator must close all nine RID families, occurrence/path uniqueness, binding versions/hashes, node/edge/category/profile types, exact producer/consumer family and port resolution, state/view/phase/definition identities, ordered package constituents, attachment owners/layouts, requirement selection/profile/CGKEY, prerequisite supported record/owner/address, all symbolic references and redundant projections. It must reject cross-graph/provenance references and conflicting copied facts. These checks validate supplied representation; they do not infer scientific existence or derive owners from a source graph.

| Consumer | Compatibility result and limits |
|---|---|
| B1 canonical inventory / ComponentRef | Graph has the same 13 fields and versions. NODE/EDGE/STATE/PHASE/CONTEXT/ATTACHMENT/REQUIREMENT arrays remain exactly addressable; PREREQUISITE selects its derived existing CGPREREQ address. ROOT AUTHORITY_BINDING/SPECIFICATION_BINDING/COMPLETE_FUNCTION exposes the exact objects above. No B1 field/container/RID/row formula changes. |
| B1 RequirementBinding / KeyBinding | All original CGREQ/CGKEY/selected IDs and actual selector types survive; profile/multiplicity/attachments remain independent. J's sole frozen projection is retained. Runtime attributes preserve exact type/role/parent, with no sampled integer or field-ordinal key. |
| B1 ContextBinding / ContextCorrespondence | Exact canonical state/phase/view/association facts and direct wrappers remain addressable. Nested ViewAddress is reached through STATE/WHOLE, not a new B1 registry family. Actual original source identity/proofs remain in the existing typed source references and same-program joins. Context gives no selector/activity credit. |
| B1 MappingView / MultiViewLink / all-mapped inventory | No source occurrence, semantic view, execution or intervention destination is selected by JSON encoding. Original extents/types/definitions, every mapped static/dynamic instance, independent selectors, repeats and source order remain required by B1. |
| D2 context/support / prior-reference closure | G §21 immediate owners and exact context/source/owner incidence remain available through B1 and CGPREREQ. This proposal creates no D2 proof object, registered target or prior evidence. D2's forbidden downstream/RO/activity/gate premises remain forbidden. Missing source facts still block support. |
| D2 accounting | Exactly four existing dispositions. No fifth bucket; no support credit for NODE/EDGE; atomic prerequisites retain own selectors/evidence. Serialization cannot move a live operation to support or RO. |
| E5 | Complete function/state/output dependencies and complete graph topology/sharing/multiplicity/timing remain. Document SHA/IDs are not graph isomorphism; task/provenance IDs are addresses resolved to semantic facts and are excluded/replaced under E5's existing role-bijection projection. No task ID becomes a semantic feature. |
| E5 equality/normalization/population | Graph-isomorphism OR certified complete semantic equality remains the collision rule; fixed offsets remain recorded and are normalized only by E5's existing novelty rule. No new AST equality shortcut, normalization, role bijection or undecidability waiver. Same 32 primary/120 training/3840 comparisons; sanity/structural outside that primary comparison population. |
| Scientific design | Same treatments, populations, endpoint, category/edge vocabulary, attachment meanings, output declaration algorithm, V3.4/V3.5/evidence obligations, no-padding/scaffold rules and Level B claim boundary. |

B1 SourceSite.port retains its existing string/null type and parsed semantic-port meaning. It is not replaced by this graph's PortReference object. A later binder compares the decoded graph port role and applicable exact field/view identity with the existing parsed port, definition references and occurrence attachments; it cannot compare unlike JSON objects as if they were scientific ports, drop an ordinal fact, or add a B1 field. Graph ActivitySite.kind uses the existing site labels, while actual source-site provenance and all-mapped destinations remain independently established under B1.

schema_version remains 2 and recipe_version/grammar_version remains CONF1_CG_RECIPE_V2. The amendment prospectively fixes previously unspecified nested bytes. Repository inspection found no operative foundation implementation or scientific graph artifact under this ambiguous wire representation. Historical/development objects are non-authoritative and cannot choose compatibility. Future use must bind the exact separately reviewed wire authority externally; a document cannot claim its bytes are accepted merely because its version equals 2. A discovered operative incompatible encoding would require explicit review, not a silent V3 or reinterpretation.

## 19. Exhaustive introduced-choice catalog and invariance proofs

For every row, encoding and decoding preserve the same abstract facts. The common invariance claim is: scientific existence, selector identity/projection, topology, E5 semantic projection, activity class, source-accounting disposition, evidence requirement, treatment and population are unchanged. Representation RID strings/digests can depend on the newly fixed bytes, as G already requires; semantic identity/equality cannot depend on choosing another lossless encoding. A choice that alters an abstract fact fails this proof and requires STOP, irrespective of this catalog label.

| Choice | Selected wire detail | Class | Specific losslessness/invariance argument |
|---|---|---|---|
| C01 | Closed schema notation, exact key rejection, scalar domains | REPRESENTATION_ONLY | No fact can be added/omitted/coerced by container syntax. |
| C02 | GraphAuthorityBinding/AuthorityEntry/AuthorityRegion | REPRESENTATION_ONLY | Addresses only fixed existing authorities and accepted regions; no precedence/version selection. |
| C03 | SpecificationBinding and exact ledger reference | REPRESENTATION_ONLY | Lossless lookup of the same frozen record; no copied or invented slot content. |
| C04 | FrozenSlotSpecification/FrozenRecord/role-map ordering | REPRESENTATION_ONLY | Same mandatory G input and existing complete record fields; no dispatch/content change. |
| C05 | Tagged path tag/value Objects and byte/numeric comparison | REPRESENTATION_ONLY | Preserves exact tag/value and frozen path grammar; determines one fragment encoding. |
| C06 | NODE/EDGE ordering_key Objects | REPRESENTATION_ONLY | Redundant recomputable frozen comparison projections, no caller scientific input. |
| C07 | Cross-array addressing and non-field collection projections | REPRESENTATION_ONLY | Total representation ordinals below existing within-family orders; no execution/timing rewrite. |
| C08 | Role/port/clause/reference catalogs | REPRESENTATION_ONLY | Exact addresses/spellings of already-fixed local facts; wrong clause/profile rejects. |
| C09 | NODE nested types and null matrix | REPRESENTATION_ONLY | Same actual profiles, ports, attribute/site distinction and source semantic associations. |
| C10 | Shared producer/source reference tagged union | REPRESENTATION_ONLY | STATE_DEFINITION_PORT selects one INITIAL/POST SINGLE writer's particular committed port; read REACHING_SET metadata remains separate. Same three kinds/five fields, no union producer, runtime choice, package operation or edge. |
| C11 | Predicate tuple→Object and exact definition reference | REPRESENTATION_ONLY | Same role/name/eight-definition identity; no new predicate or equivalence. |
| C12 | Embedded ViewAddress and WriterIdentity | REPRESENTATION_ONLY | Addresses existing view facts and retains every already-required reaching writer, no new namespace/read/runtime selection. |
| C13 | State/phase/stage membership/reference/list encodings | REPRESENTATION_ONLY | Same storage, carries, lifetime, temporal groups and qualified pure-order facts. |
| C14 | STATIC_BINDING payload | REPRESENTATION_ONLY | Same unexecuted declaration/definition/lifetime fact, no selected binding operation. |
| C15 | ORDERED_DECODED_PACKAGE payload | REPRESENTATION_ONLY | Same four original fields/conversions and package use, no assembly or reordered domain. |
| C16 | EXPRESSION_RESULT_REFERENCE payload | REPRESENTATION_ONLY | Same defining result and actual consumers, no extra expression/result carrier. |
| C17 | INITIAL_POST_DEFINITION payload | REPRESENTATION_ONLY | Same committed definition and state/phase/place, no atomic INITIAL/POST read. |
| C18 | COMPLETION_PERSISTENCE payload | REPRESENTATION_ONLY | Exhaustive unused/consumed-without-persistence/TWO_PASS-persistence cases derive one Boolean from G's explicit relation; false records its absence, not mutability. Same completion/interval/consumers, no boundary operation. |
| C19 | PROVENANCE payload | REPRESENTATION_ONLY | Same specification and identified records/requirements, no fabricated source/proof. |
| C20 | Thirteen attachment value cases / layouts / nulls | REPRESENTATION_ONLY | Preserves every scalar/role/reference association and scientifically ordered sequence; CompletionFact uses the same derived Boolean and exact cross-record completion identity/interval/consumer consistency. |
| C21 | LocalRoles/PredicateIdentity/ParentCapability/ValueRequirement | REPRESENTATION_ONLY | Same local reusable facts; exact parent/field/state/phase occurrence stays outside keys. |
| C22 | OutputRequirement/StateViewRole/InputDomainObligation/class rows | REPRESENTATION_ONLY | Same output property/local view/frozen input schema and class predicates, no witness or template addition. |
| C23 | ScientificEvidenceClass/ObligationScope labels | REPRESENTATION_ONLY | Existing G/D/B1 class/scope meaning only, no new evidence kind or treatment exception. |
| C24 | PREREQUISITE supported ID versus implicit wrapper address | REPRESENTATION_ONLY | Retains supported record, immediate owner and exact frozen CGPREREQ formula without another field. |
| C25 | CompleteFunction field value containers | REPRESENTATION_ONLY | Same used roles/domain/contribution/equations/init/traversals/output; each dependency independently recoverable. |
| C26 | Six recursive expression variants and signatures | REPRESENTATION_ONLY | Inductively preserves leaves/arity/ordered repeats/tree association and existing operator semantics. |
| C27 | StateEquation/Initialization/Traversal symbolic records | REPRESENTATION_ONLY | Same exact writer, guard, PRE/POST, offset, original bounds and scientific placement/persistence. |
| C28 | Canonical object reconstruction and exact string/integer escaping | REPRESENTATION_ONLY | One lossless byte encoding; no array sorting, coercion, normalization or algebraic rewrite. |
| C29 | Identity fragments/port fragment encoding/digest input | REPRESENTATION_ONLY | Same nine component lists, exact existing framing and one-final-LF graph integrity; no E5 shortcut. |
| C30 | External prospective binding with unchanged v2 versions | INTERFACE_METHODOLOGY_REFINEMENT | Narrows acceptance to the reviewed wire authority before use; no scientific requirement or operative prior artifact is changed. |

Choice totals: **30 = 29 REPRESENTATION_ONLY + 1 INTERFACE_METHODOLOGY_REFINEMENT + 0 SCIENTIFIC_CHANGE + 0 UNRESOLVED_SCIENTIFIC_CHOICE**. C30 is explicitly not mislabeled as encoding alone: it is an acceptance/provenance rule needed to prevent ambiguous version-2 bytes being treated as authoritative. It changes no scientific extraction, population or evidence test and revises no existing B1/D2 container.

## 20. Internal self-review and outcome

This is internal specification review, not independent approval, a freeze or an executed scientific validation. The field/type audit precedes the selections above. Closure is an induction over the closed registry and recursive Expression/ProducerReference unions, with packages prohibited from recursing. All other references terminate in exact existing record/authority registries. No arbitrary JSON/object, unspecified tuple, float, source-derived label or default null remains.

| Review item | Internal result / evidence |
|---|---|
| All 13 graph fields | §5 Graph exact sequence, no digest/new field |
| Authority/specification binding and builder-input distinction | §5 fixed existing authority closure, exact lookup versus complete future input record |
| Every nested record/field/type | §3 registry plus §§4–15 complete field/type tables; 109 audited units |
| Every tagged union | Paths, references, writer identity, domain/attachment values, selector requirements and expressions have exhaustive cases |
| Every contextual payload | §11 six exact schemas, every field cited to G, no hidden expression/operation |
| STATE_DEFINITION_PORT_IS_ALWAYS_PARTICULAR | §9 selects an INITIAL/POST view with SINGLE and one direct committed writer port; rejects sets, runtime selection and multi-output resolution. Read WriterIdentity metadata remains separate. |
| COMPLETION_IMMUTABLE_FLAG_TOTAL_AND_DERIVED | §§11–12 fix true iff G's explicit immutable-persistence relation exists, otherwise false; all three admitted cases fix interval/read/consumer fields. False is no mutability claim; matching CompletionFact/context/state/phase facts agree. |
| Every selector nested object | §13 exact local roles/predicate/value/output/view/interface/site/marker and explicit nulls |
| CompleteFunction recursive grammar | §15 exact six leaf/operator variants, eleven pure operators, arity/types/repeats/definitions retained |
| Equations/initialization/traversals/output | §15 complete supplied dependencies and actual writer/placement; strict PREFIX and TWO_PASS facts intact |
| ordering_key | §6 recomputable NODE/EDGE only, no added field for other families |
| Occurrence-path JSON | §6 tag/value, integer/bool distinction, UTF-8 comparison, collision rejection |
| Nullability / empty arrays | §§4–15 explicit rules; known fact cannot become null/empty proof |
| Scalar typing / integer versus Boolean | §4 exact integer tokens/types; no bool/int or float coercion |
| Object field order | Exact type sequences; §17 deterministic reconstruction and canonical-byte check |
| Array order / scientific timing | §6 validated supplied order; scientific ordered sequence never replaced by representation sorting |
| Nine representation-ID formulas | §16 exact D framing/V/B/NONE/profile/prerequisite components, no new namespace |
| Key projection | G's thirteen fields, explicit nullable objects, sole frozen J projection, no provenance/ordinal/multiplicity |
| Prerequisite address closure | §14 supported ID retained; implicit CGPREREQ address uniquely available to B1 |
| Graph digest | §17 entire exact compact document plus one LF, no own digest, no E5 result |
| B1 identities / typed joins | §18 existing ComponentRef/RequirementBinding/ContextBinding/MappingView registry intact |
| Runtime/all-mapped evidence | No parent switching, sampled runtime values or occurrence/instance omission introduced |
| D2 immediate owners / prior closure | No transitive owner, invented proof target or downstream activity/RO premise |
| Four buckets / atomicity | No fifth bucket or support-only NODE/EDGE; all own selectors/evidence intact |
| E5 | Existing graph-isomorphism OR certified semantic equality, complete dependencies/role sharing/fixed offsets, 3840 comparisons unchanged |
| Versioning | Schema/recipe/grammar v2 retained; future exact wire binding required externally |
| Population/treatment/endpoint/claim | Unchanged; no empirical evidence or candidate-readiness claim |
| Choice accounting | 29 representation + 1 interface refinement; zero scientific change/unresolved scientific choice |
| File/execution boundary | Exactly one prospective Markdown proposal; no implementation/freeze/scientific instances/RO/compiler/model/holdout work |

The following are normative specification rejection/acceptance checks, reviewed as document rules only; no graph instances or scientific fixtures are constructed or executed:

| Threat / supplied interpretation | Required result |
|---|---|
| STATE_DEFINITION_PORT resolves a REACHING_SET | REJECT; only an INITIAL/POST SINGLE definition view is admissible. |
| STATE_DEFINITION_PORT resolves more than one committed writer/output, or selects a runtime predecessor | REJECT; the exact state/view ordinal resolves one fixed committed port under §9. |
| PRE/current/COMPLETED StateView legitimately retains complete REACHING_SET metadata, with no set-valued producer reference | ACCEPT when all exact G read/definition/control facts are preserved; consumers still reference the actual read result. |
| Completion-only record carries caller-selected immutable=true | REJECT; no frozen immutable-persistence relation means false. |
| Completion-only record leaves immutable unconstrained, omitted, null or unknown | REJECT; the mandatory Boolean is uniquely derived. |
| Frozen TWO_PASS completed-P persistence carries immutable=false or omits its interval/consumer facts | REJECT; the exact G relation requires true and its complete references. |
| CompletionFact immutable differs from the corresponding completion/persistence context or state/phase fact | REJECT; §§11–12 require exact canonical-fact agreement. |
| False immutable is treated as an independent proof of mutability | REJECT; it encodes only absence of G's explicit immutable-persistence relation. |
| Consumed completion without immutable persistence is forced into an empty consumer/null read case or given a later persisted phase | REJECT; §11's consumed-without-persistence case retains the actual read/consumers with false and an empty interval. |

Self-review result: **ALL_GRAPH_V2_WIRE_TYPES_CLOSED**. **SCIENTIFIC_MEANING_UNDERDETERMINED = 0**. No scientific alternative was selected to make serialization convenient. A future independently identified semantic gap, incompatible operative v2 encoding or required E5/B1/D2 redesign remains a STOP; this internal review does not authorize silently repairing it.

Internal outcome: **GRAPH_V2_WIRE_FORMAT_BINDING_REVISED_WITHOUT_SCIENTIFIC_CHANGE**.

Proposal readiness status: **CANONICAL_GRAPH_V2_WIRE_FORMAT_BINDING_REVISED_READY_FOR_INDEPENDENT_REVIEW**. This means the two narrow wire repairs and their dependent documentation are ready for independent review, not frozen or implemented. Do not resume the foundation tranche, graph builder, RO, candidate construction or Attempt 004 in this task. Commit exactly this revised proposal and stop; do not modify any other repository file or create a freeze manifest.
