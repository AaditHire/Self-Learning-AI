# CONF1 specification-level coverage feasibility audit

Status: NON_NORMATIVE_SPECIFICATION_ANALYSIS; no authority; no freeze; no implementation; no candidate.

## 1. Authorities and verified identities

Repository: Self Learning AI. Starting branch: main. Starting HEAD and origin/main: 9887c38e3f37d1018022b2a2324df68b572986d0. Starting index, tracked worktree and untracked inventory were clean. This analysis is independent of prior conversation conclusions.

All paths in the table are under research/protocols/. SHA-256 means the exact working-file bytes; blob means the Git-filtered working content and identical committed blob. Every bound whole-file SHA/blob matched its controlling manifest. Ten separately bounded normative regions also matched their declared normalization/boundary policies. D2's root manifest has a committed Git identity, rather than an invented self-hash binding. The ledger's controlling SHA uses normalized LF bytes: 83436eecda3affe813b785e868e3f8936fa59afc35ded0eb6a54290edb41dc88 (46,284 bytes); its raw-byte hash below is supplemental, and its committed blob matches D's ledger binding.

| File | Verified raw SHA-256 | Verified Git blob | Raw bytes | Binding checked |
|---|---|---|---:|---|
| phase3c_conf1_canonical_contract_graph_recipe_proposed_v2.md | 067401333940664502bada12b41d591ef1f554680ba5c9062954b5280e3fd272 | e01d56046711365e3369a7fad67591b1476c4d15 | 117756 | canonical_contract_graph_recipe_v2_freeze.json.frozen_recipe |
| phase3c_conf1_coverage_v3_proposed.md | a9fb8350c849ce62e2a673e3ca1f1d5a08f556b7f415687f1e2eabdf356030f3 | 16210d9810d217461b77546c3568c3344c0c770b | 31128 | coverage_v3_atomic_activity_output_amendment_freeze.json.bound_authorities.coverage_v3 |
| phase3c_conf1_coverage_v3_atomic_activity_output_amendment_proposed.md | 8df78d2c96ccb9d6763999a6486202c1c6193bc3638b2c64421c386964cbaad6 | c2e3041297d0e65246943b928054e3d6cce8af9f | 61988 | canonical_contract_graph_recipe_v2_freeze.json.accepted_atomic_activity_output_amendment |
| phase3c_conf1_delegated_evidence_interfaces_proposed.md | 9c684eaf6b0099080ddf907630b0a2f8e176e3a882b67875d82f07bd82d64dc5 | 1b6d4d1a825bf9e9d288ca9c3815d1a8e7c78d1a | 76081 | coverage_v3_atomic_activity_output_amendment_freeze.json.bound_authorities.delegated_evidence_interfaces |
| phase3c_conf1_delegated_evidence_interfaces_binding_amendment_proposed.md | 2b045a0fb5a7dd22d54397700bab47b88b6857a1ce9b0e22e5f1f5c1ff94595c | 92edf8305f989f9dce55fa26f4f68ef5e661a3c6 | 120981 | delegated_evidence_interfaces_binding_amendment_freeze.json.frozen_amendment |
| phase3c_conf1_direct_support_accounting_amendment_proposed_v2.md | 1d2e5b5417a2ebadccc159e92a6c45737ae239666cf14b3b5d3962d250dd1e06 | dd9556076ec906eff7be0c35ae11f7c73fc8d944 | 106226 | direct_support_accounting_amendment_v2_freeze.json.frozen_amendment |
| phase3c_conf1_paired_scaffold_normalization_proposed.md | ef6063d39319d8b3bd3dbe6bdaa93b474217fa4c37d50ef43dfed5afc8da1fc0 | 475e9de4a0ef3bef23edac1e3631011a20790f5a | 14114 | coverage_v3_atomic_activity_output_amendment_freeze.json.bound_authorities.paired_scaffold_normalization |
| phase3c_conf1_input_domain_case_classes_and_training_amendment_proposed.md | bb59ad7cf4cb22c2492427a1fa5a78b0d81398ab16fb0a9cb8229d8c9489182e | 66467ef968e4963dd7a22568100a940871ad304c | 16901 | coverage_v3_atomic_activity_output_amendment_freeze.json.bound_authorities.input_domain_case_classes_and_training_amendment |
| phase3c_conf1_structural_transfer_semantics_amendment_proposed.md | 362c16faba42246344589fc7f46709b5b83e5bc829a13e1540b04392ddab2fba | eab80c50f3861438add2713689ee81fdbcdf38dd | 40956 | direct_support_accounting_amendment_v2_freeze.json.structural_pair_binding.frozen_amendments.mathematics |
| phase3c_conf1_structural_transfer_topology_amendment_proposed.md | 9a5e7e80502304e7281a924ef764f9a81b9edd0f9c65fc4a4e0007ad19a2aa2a | 4f624b93d33decf3dd4643067693546fed32499d | 49306 | direct_support_accounting_amendment_v2_freeze.json.structural_pair_binding.frozen_amendments.topology |
| phase3c_conf1_slots.json | 5fe76fbc02e9f65174327199c2004f7e51f19a7f3866ae15709744c5274415c2 | 133c9c7275bcedeaf2474e54e61bae47923508ad | 47968 | delegated_evidence_interfaces_freeze.json.upstream_authorities.semantic_slot_ledger |
| phase3c_conf1_canonical_contract_graph_recipe_v2_freeze.json | 274c3e39d9dada9939e87c67f72aa71e8a2514ad9a84d35327ac0f6b711c2a51 | 14976b41c8e5e8dba915147fd3a379e891daa7bb | 47206 | delegated_evidence_interfaces_binding_amendment_freeze.json.bound_authorities.canonical_graph_recipe_v2 |
| phase3c_conf1_coverage_v3_freeze.json | 8d8f8a37c808d84c740867174e219803712213e672687c42164500f2bca12291 | 28c0fb52fba083e72f87ebfc530fd88ddded5f92 | 3307 | coverage_v3_atomic_activity_output_amendment_freeze.json.bound_authorities.coverage_v3.controlling_freeze_manifest |
| phase3c_conf1_coverage_v3_atomic_activity_output_amendment_freeze.json | 8a9bfe3c4ad3b687261f486189285156b4c1843e53bfbd20b0bc35c4f07d09e8 | 602b5593287c798e6da297917335795530530a33 | 47346 | canonical_contract_graph_recipe_v2_freeze.json.bound_authorities.atomic_activity_output_repair |
| phase3c_conf1_delegated_evidence_interfaces_freeze.json | bd7a7fc6862ce049c1fdf363f763e1a3a17808132291b9064e3c6f26fb720948 | 32595c5c563fa262679f2bf93ae789f04cde7f72 | 5892 | coverage_v3_atomic_activity_output_amendment_freeze.json.bound_authorities.delegated_evidence_interfaces.controlling_freeze_manifest |
| phase3c_conf1_delegated_evidence_interfaces_binding_amendment_freeze.json | 0257f8eac42265265f9f88b53633e56c7f9b9c6918f53988675cdcb84bd6de7d | 23d8b3370b26ceec6a076f1061778fa43dad7100 | 40647 | direct_support_accounting_amendment_v2_freeze.json.bound_authorities.delegated_canonical_binding_b1 |
| phase3c_conf1_direct_support_accounting_amendment_v2_freeze.json | 1afa76f58bdf35601488f390e17708a62ed156e2dd0c38e59d82f3fbd3879e26 | 46d3e0b4bfddbef96a8247e69ddef7b3ef4c126d | 88427 | ROOT_MANIFEST_GIT_IDENTITY |
| phase3c_conf1_paired_scaffold_normalization_freeze.json | ff1a9610b10ff559ac1859361fb7a31668210ed33e97c2864e592981bd9cfea2 | 9a54e9b525b1795b10f94bf0d0250ae831e6db74 | 2093 | coverage_v3_atomic_activity_output_amendment_freeze.json.bound_authorities.paired_scaffold_normalization.controlling_freeze_manifest |
| phase3c_conf1_input_domain_case_classes_and_training_amendment_freeze.json | de4a353d58515b5c53210664ea1a642731ac6f1734f23afef4ae512fb8c2627a | 774eb73150f66d2545ddf270cc2f051eddedc156 | 4201 | coverage_v3_atomic_activity_output_amendment_freeze.json.bound_authorities.input_domain_case_classes_and_training_amendment.controlling_freeze_manifest |
| phase3c_conf1_structural_transfer_pair_freeze.json | 73eb1c29de6b258de6f7b83867e11ee3f53f67b513f550a666ede550b4e00aa5 | cb643d992bac60db6a3ef208f1e690f6783ac4f6 | 25696 | canonical_contract_graph_recipe_v2_freeze.json.bound_authorities.joint_structural_transfer_pair |

Normative-region checks: G prefix 113400 bytes, cb490e9a3a9a2d31b71aec1207f2e191a7b60d9538d81af23cec3d0d610ae2f5; A prefix 56933, 1b72ff7fab98a870882a81797aea5d8a079e7cac74e520d02f373f4e31c794f8; B1 prefix 119512, cab925e51aac6beb6705439d5d0d02cc4414d143d39526089511c2a80f81b94b; D2 prefix 102020, d0b7d7975785c48ec62a7cdf9818655daac02231278319445d28fd139b99dbf5; structural mathematics prefix 36321, a0c99b79001c1a37163d1ff4b06d4518891dca8c12518dc4a3d276b3de5658ac; structural topology prefix 44187, 19d9dfc8863e4b2668a6525294fbdb71b479dbf1211d39a95f544b28d30a185d. Heading-bounded normative checks: Coverage V3 (LF), 884a8ac3f859268e16dfa0d8f0d477211c7a273fca58666c7eba018265d8c15a; paired scaffold (LF), 5aa404949a8cc580b9ca3ff4aff7325195e172a7cfa82c69317280597c73b25c; input-domain amendment (LF), b9dc3d6ca22778ab0b3e734270fb20a00b4d88e0602f24fe77b2112335df8167; D, 26c642e17bb5218727c0cd09f370eaf1ac6c4de35006fa9801d701ece81cf16d.

Citation abbreviations: G = canonical graph recipe v2; A = atomic/activity/output amendment; D = delegated interfaces; B1 = delegated binding amendment; D2 = direct support accounting v2; Cov = Coverage V3. Section references identify the frozen scientific text, including its bounded normative regions. Freeze records and ledger metadata establish identities/populations; they are not evidence of successful scientific coverage. The unfrozen wire-format proposal supplies no scientific interpretation here.

## 2. Method and scope

This is a symbolic existence analysis of the profiles required by G §§3–17, §20 and §27. No canonical key IDs, selector instances, graph instances, contracts, programs, cases, candidate evidence, certificates or requirement rows were built. Ledger reads were limited to predicate_definitions, training_semantics, graphs and slot metadata. No sealed holdout, synthetic expected-label fixture, attempt hidden cases or model outcome files were consulted. Repository status documentation was not used as scientific outcome evidence. No tests, compiler, model or activity computation ran.

Population arithmetic from metadata: two conditions × 60 training slots = 120 specifications; primary = two domains × four graphs × four rotations = 32; sanity = two domains × four primitives × two offsets = 16; structural = two domains × two routes × four rotations = 16. Total = 184. For each domain, the training union contains all six primitive pairs, all five offsets 0,2,4,6,8 and both traversal directions. Comparisons below use the complete 30-slot union independently in each condition, never a same-slot-only restriction.

Numeric cyclic role order is odd_index, residue2_mod3, divisor_index, first_half. Array cyclic role order is negative_value, even_value, large_magnitude, value_exceeds_index. These are explanatory names for the ledger definitions. Each rotation shifts the P/Q/R/S assignment. G1 lowers P/Q/R only; G2/G3/G4 lower all four; structural routes lower P/Q only; sanity lowers its one named primitive. A missing role's metadata is not an emitted selector.

G §20 states:

> The key projection has exactly category, operation_or_edge_type, domain, input_types, output_type, local_roles, predicate_identity, value_requirement, output_requirement, state_view_role, interface_obligation, activity_site, relation_marker, in that field order and with explicit nulls.

And:

> The projection retains local semantic operand/result roles, named primitive identity, relevant value/output requirement and the local pre/post/completed distinction.

Tables use clause-based profile families, with each operation, formal use, exact value and local role retained. A row parameterized over named primitives or ports means separate profiles for those distinctions, not a merged key. Domain is retained in every comparison. NODE types are formal input lists and actual output; EDGE input_types is the singleton payload list and output_type the same payload. Attribute activity_site is null. All base relation_marker fields are null; only the certified J relation uses CERTIFIED_LOCAL_PAIR_JOINT_RESULT. Task IDs, condition IDs, field/phase ordinals, multiplicity and full neighborhoods cannot manufacture a missing capability.

Classification meanings:
- COVERED_BOTH: required declaration/profile exists in both same-domain training unions at this level; no V3.5 PASS is asserted.
- J_EXCEPTION_COMPOSITION_ONLY: only the certified local two-distinct-role joint-result relation can use the frozen exception.
- ISOLATED_ONLY / COMPOSITION_ONLY: exact profile known to exist only on the stated side.
- NEITHER: a mandatory operation/type/value/local-use distinction proves absence from both unions.
- UNDERDETERMINED_BY_FROZEN_TEXT: exact profile equality cannot be settled from the cited role/refinement clauses. Known one-sided absence is retained explicitly even when the other side is uncertain.

V3.5 activity, case witnesses, INPUT_DOMAIN case-class satisfaction and source mapping are outside this task. INPUT_DOMAIN is compared only as a declared domain/range/schema capability. Output categories are declaration-level existence only. These are necessary conditions, not sufficient evidence for V3.4/V3.6 compliance.

Cov V3.4:

> An essential capability present in neither condition is still FAIL, even though the absence is symmetric.

Cov V3.6:

> Both conditions must cover every evaluation-essential atomic key as in V3.4.

D §3.3 retains RID("V3.4", [evaluation_task_id, canonical_contract_key_id, required_condition_id]), shared V3.6 rows and the separate TREATMENT_EXCEPTION formula. No row count is inferred from symbolic families; the counts below are affected specifications, not unique keys, occurrences or evidence rows. B1's selector bindings and D2's direct accounting cannot supply a missing operation or broaden an equivalence.

## 3. Exhaustive clause-based atomic profile inventory

The following tables are compositional notation for specification text, not generated contracts. Each route row includes every member of its referenced families and the route-specific additions. Every actual NODE/EDGE is essential under G §§3–4. Repeated formal ports remain separate occurrences even if a reusable profile is equal.

### 3.1 Common domain and traversal families

| Family/domain | NODE profiles: operation, types/result, retained role | EDGE and attribute profiles | Clauses |
|---|---|---|---|
| DN: numeric input | API INPUT → INT (N); DOMAIN_VALUE → INT, decoded-n role with INPUT parent; separate INPUT_DOMAIN NODE profile on INPUT with numeric n≥0 interface | Runtime-value-role attribute retains INT/decoded-n/INPUT parent; each bound/predicate/operator use is separately listed below | G §§3,6,16,20,27 |
| DA: array decoding | API INPUT → TEXT (A); SPLIT(TEXT) → TEXT4 (T4); TO_NUMBER(TEXT) → INT (N), all four original positions; FIELD_VALUE → INT with TO_NUMBER parent; INPUT_DOMAIN profile with exact signed four-field schema | INPUT_TO_DECODER TEXT raw→SPLIT (A), TEXT field→TO_NUMBER (F); four runtime field attributes; pipe configuration "|" is attached to SPLIT, not a NODE/EDGE/independent C key | G §§3–4,7,16,20,27 |
| LA: array element | INDEX_READ(INT4,INT) → INT (N), original-index element role | VALUE_TO_OPERATOR payload INT4 (I4) at package port; payload INT (N) at original_index port; arity 4 and original positions 0–3 are required attached/fixed facts, not fictitious lookup edges | G §§4,7,16 |
| LN/LA forward traversal | BOUNDED_LOOP(BOOL) → UNIT with BOOL decision site (B); INITIALIZE → UNIT with committed INT original-index site (N); STATE_VIEW(INT) → INT, index PRE; LE(INT,INT) → BOOL (B); ADD(INT,INT) → INT for step; ASSIGN → UNIT with committed INT index-step site (N) | VALUE_TO_OPERATOR INT for bound and step ports; PREDICATE_TO_CONTROL BOOL bound→loop; PRIOR_STATE_TO_UPDATE INT where index-step prior port is the actual prior use; LOOP_CARRY INT index POST→PRE; CONTROL_TO_UPDATE BOOL (B) to actual index/body non-accumulator writers; fixed index/bound/step attributes with exact parents | G §§4,6–7,10,16 |
| Numeric forward specifics | Index initializer 1; LE(index,n); ADD(index,1) | COMPUTED_VALUE index-initial 1, step 1; n runtime bound. No fabricated numeric upper endpoint | G §6 |
| Array forward specifics | Index initializer 0; LE(index,3); ADD(index,1) | COMPUTED_VALUE index-initial 0, bound 3, step 1, domain arity/positions where independently required | G §§7,16 |
| Training reverse, numeric | Index initialized from runtime n; LE(1,index); SUB(index,1); same index read/write/carry families | Exact reversed comparison uses and SUB step; bound 1 and step 1 attributes; reverse init n is runtime, not a computed constant | G §6 |
| Training reverse, array | Index initialized 3; LE(0,index); SUB(index,1); same index families | Index-initial 3, bound 0, step 1; exact parents differ from accumulator initialization | G §7 |

The reverse-only profiles are extra training capabilities, not evaluation requirements. All evaluation traversals are forward; TWO repeats the same traversal. Comparison reversal is allowed only under Cov V3.3; the forward template itself is present in both unions.

### 3.2 Every predicate-definition family

For each used named primitive, emit its SEMANTIC_PRIMITIVE BOOL NODE (B), every internal operator below, every required fixed parameter COMPUTED_VALUE and every separate immediate-operator constant attribute. Each formal runtime/parameter use into the named primitive is VALUE_TO_PREDICATE INT (N). Each internal numeric operand use is VALUE_TO_OPERATOR INT (N), including duplicate ports. Comparison operators consume INT/INT and return BOOL; MOD/MUL consume INT/INT and return INT. Named primitive identity and local argument/value-parent roles are retained. No predicate has AND or OR internally.

| Domain/named primitive | Exact defining operator tree | Fixed parameter/operand facts | Cross-condition inventory |
|---|---|---|---|
| Numeric odd_index | EQ(MOD(index,2),1) | 2 and 1 with their exact primitive/operand parent roles | Both unions, because every primitive appears in several pairs |
| Numeric residue2_mod3 | EQ(MOD(index,3),2) | 3 and 2 with exact parents | Both |
| Numeric divisor_index | EQ(MOD(n,index),0) | 0 with exact parents; n and original index are distinct runtime arguments | Both |
| Numeric first_half | LE(MUL(2,index),n) | 2 with exact parents | Both; also supplies a numeric MUL ability, without count-state operands |
| Array negative_value | LT(value,0) | 0 with exact parents | Both |
| Array even_value | EQ(MOD(value,2),0) | 2 and 0 with exact parents | Both |
| Array large_magnitude | LT(4,MUL(value,value)) | 4 with exact parents; two separate uses of the same value | Both; also supplies a numeric MUL ability |
| Array value_exceeds_index | LT(index,value) | No fixed predicate constant | Both |

Source: G §8, with typing/ports in §§3–4, attributes in §16 and key projection in §20. These rows enumerate the named root, all arithmetic/comparison nodes, all named-formal and expression operand edges and their fixed/runtime attributes; a named predicate selector never substitutes for its internal operator selector.

### 3.3 Indicator and accumulation families

| Family | Complete emitted NODE profiles | Complete edges/attributes and retained distinctions | Clauses |
|---|---|---|---|
| IT: protected training indicators P/Q | Outer INITIALIZE committed INDICATOR_INT zero; per-item ASSIGN reset-0 and set-1 committed INDICATOR_INT; IF_CHOICE with BOOL decision; BOOL_TO_INT(BOOL)→INDICATOR_INT; current STATE_VIEW(INDICATOR_INT)→INDICATOR_INT | PREDICATE_TO_CONTROL BOOL to IF; PREDICATE_TO_INDICATOR BOOL to conversion; CONTROL_TO_UPDATE BOOL to set/reset where actual control exists; fixed init/reset/set 0/0/1, each exact writer parent; current reset/set reaching definitions. No indicator inter-item carry | G §§9–10,16 |
| IE: evaluation I(term) | Same closed reset-0/IF-set-1/conversion/current-read realization, for each required Boolean term; no protected training outer initialization added | Same labels and exact reset/set values; Boolean source may be a named predicate, conjunction or disjunction. Composite source local roles/identity require separate comparison in §4 | G §9 |
| U(state,k,t): accumulated INT count/result | INITIALIZE committed INT; COMPUTED_VALUE initial k with INITIAL_ACCUMULATOR parent; PRE STATE_VIEW(INT); ADD(prior,t) → INT unless an explicit refinement is stipulated; accumulator ASSIGN → UNIT with contribution site (S) | PRIOR_STATE_TO_UPDATE INT prior port; VALUE_TO_OPERATOR payload type of t at arithmetic contribution port (N); OPERATOR_TO_ACCUMULATOR payload type of t at contribution application (S); CONTROL_TO_UPDATE BOOL to accumulator writer (S); LOOP_CARRY INT POST→PRE. Initial k/state/writer/displayed-computation membership retained | G §§4,10,16 |
| UF: final accumulated state | COMPLETED STATE_VIEW(INT); DISPLAY_INTEGER with INT argument/UNIT output (D) | ACCUMULATOR_TO_OUTPUT INT (N); final integer property OUTPUT_CATEGORY attributes. Arithmetic-result commitment remains DEFINITION_ASSOCIATION context, not an eleventh edge | G §§3–4,10,17 |
| UX: completed count consumed by arithmetic | COMPLETED STATE_VIEW(INT) for each actually consumed count; consuming operator independently selected | VALUE_TO_OPERATOR INT with completed-count source/use; no cross-phase LOOP_CARRY/persistence edge | G §§4,10,15 |

U includes no unused completed read: PREFIX's prior-count completion is metadata only; training indicators have no unused completed read. INITIAL/POST are definition facts, not additional STATE_VIEW NODEs. Accumulator arithmetic ADD and accumulator contribution ASSIGN are distinct selectors. No BINDING, EXPRESSION_RESULT, package assembly, standalone pipe, NEG or syntax-essential LITERAL_TOKEN is emitted by these current routes. Exact sentinels and OUTPUT_NEGATIVE have no declarations in this universe.

### 3.4 Route/domain tables

A table row's predicate set ranges over the actual ledger rotations/pairs only. The table is exhaustive by union of §§3.1–3.3 and the explicitly listed contribution profiles. All ordinary arithmetic operands have VALUE_TO_OPERATOR edges of their actual payload; all Boolean binary operands have VALUE_TO_OPERATOR BOOL (B). Domain and named identities remain key content.

| Domain/route | Shared families and emitted contribution NODEs | Route-specific EDGE/attribute profiles |
|---|---|---|
| Numeric T-PAIR ISOLATED, 30 slots | DN + LN (forward/reverse) + each selected P/Q predicate + IT(P), IT(Q); ADD(INDICATOR_INT,INDICATOR_INT)→INT treatment; U(TOTAL,k,t), UF | Indicator-current→numeric operand uses; exact accumulator initial k∈{0,2,4,6,8}; predicate parameter families over all six pairs; treatment relation is independent addition, not J |
| Numeric T-PAIR COMPOSITION, 30 slots | Same; treatment MUL(INDICATOR_INT,INDICATOR_INT), proven 0/1 mathematical product, with actual result refinement only as frozen text stipulates; U, UF | Same incident typed operand roles as ISOLATED; separate certified two-role J profile; no exception for base MUL or downstream typed edges |
| Array T-PAIR ISOLATED, 30 slots | DA + LA (forward/reverse) + two selected predicates + IT(P/Q); ADD of indicators; U, UF | Same treatment/offset families; full raw/field decoder and package/index-use families |
| Array T-PAIR COMPOSITION, 30 slots | Same array families, treatment MUL of indicators; U, UF | Same incident operands; additional certified local J only |
| Numeric G1, four rotations | DN + LN forward; P/Q/R predicates; AND(P,Q), AND(P,R), OR of those BOOL results, all BOOL/BOOL→BOOL (B); IE on the OR result; U(TOTAL,0,indicator), UF | BOOL VALUE_TO_OPERATOR: primitive→AND and AND-result→OR; composite conversion/control; U contribution is INDICATOR_INT |
| Array G1, four rotations | DA + LA forward; same three-role Boolean/indicator/U/UF construction | Same Boolean and indicator edges; array decoding/index families |
| Numeric G2, four rotations | DN + LN forward; P/Q/R/S; AND(P,Q), AND(Q,R), AND(R,S); three IE; inner ADD(IND,IND), then outer ADD(inner-result,IND); U(TOTAL,0,sum), UF | BOOL primitive→AND operands; IND arithmetic operands; inner result→outer ADD; sum→U; separate local pair-J profiles where qualified |
| Array G2, four rotations | DA + LA forward; same G2 construction | Same distinct Boolean/arithmetic formal uses plus decoder/index families |
| Numeric G3, four rotations | DN + LN forward; P/Q/R/S; AND(P,Q), AND(P,R), AND(P,S); three IE; same binary-associated two ADDs as G2; U, UF | Separate repeated P Boolean operand uses retained; remaining G2-style edges |
| Array G3, four rotations | DA + LA forward; same G3 construction | Same, plus array families |
| Numeric G4, four rotations | DN + LN forward; all roles; OR(P,Q), AND(OR-result,R), AND(Q,S); two IE; ADD(IND,IND); U(TOTAL,0,sum), UF | BOOL primitive→OR/AND and OR-result→AND uses; IND/IND ADD ports; local J only for qualified two-distinct-role conjunction, not multi-role conjunction |
| Array G4, four rotations | DA + LA forward; same G4 construction | Same, plus array families |
| Numeric sanity, eight slots | DN + LN forward; one named predicate; IE; U(TOTAL,k,indicator), UF; k=0 or 3 | No AND/OR/treatment MUL; indicator→U arithmetic/write uses; INITIAL_ACCUMULATOR k=3 is distinct from predicate parameter 3 |
| Array sanity, eight slots | DA + LA forward; same single-predicate/indicator/U/UF | Same k=0/3 distinction plus decoder/index families |
| Numeric PREFIX, four rotations | DN + LN forward; P/Q predicates/IE; U(PRIOR_P_COUNT,0,I(P)); MUL(I(Q),PRIOR_P_COUNT.PRE), input IND/INT, output INT; U(TOTAL,0,product), UF(TOTAL) | Distinct PRE count→MUL VALUE_TO_OPERATOR INT; count writer's prior use stays PRIOR_STATE_TO_UPDATE; two distinct INT carries; count update after TOTAL update; no completed prior-count read |
| Array PREFIX, four rotations | DA + LA forward; same count/product/U/UF construction | Same PRE count consumption and two carries, plus decoder/index families |
| Numeric TWO, four rotations | DN + LN forward twice; P/IE/U(P_COUNT,0,I(P)) in first traversal; Q/IE/U(Q_COUNT,0,I(Q)) in second; two UX; final MUL(INT,INT)→INT; DISPLAY_INTEGER | Two COMPLETED-count VALUE_TO_OPERATOR INT ports; second-entry initialization and immutable P persistence are exact attachments; final-result→display association is context, no ACCUMULATOR_TO_OUTPUT on the product |
| Array TWO, four rotations | DA + LA forward twice; same two-count/final-product construction | Same completed-count consumption and entry attachments plus array families |

Here IND abbreviates INDICATOR_INT only. It is never normalized to BOOL in a base profile. The contribution expression is a quoted clause description, not an instantiated graph.

### 3.5 Declaration-level output profiles

G §17 requires own-target declarations before whole-condition comparison. Only OUTPUT_ZERO, OUTPUT_POSITIVE and OUTPUT_MULTIDIGIT can occur; all are OUTPUT_CATEGORY NODE attributes with INT property, null activity_site and property/domain-only keys. No sentinel is inferred from zero.

| Domain/route | Declared evaluation categories, or categories present somewhere in training union |
|---|---|
| Numeric training, each condition union | ZERO, POSITIVE, MULTIDIGIT; ZERO exists at offset 0; each numeric target is unbounded under G §17 |
| Numeric G1–G4, PREFIX, TWO | ZERO, POSITIVE, MULTIDIGIT |
| Numeric sanity offset 0 / offset 3 | ZERO, POSITIVE, MULTIDIGIT / POSITIVE, MULTIDIGIT |
| Array training, each condition union | ZERO, POSITIVE, MULTIDIGIT; offset-0 targets permit zero and offset-8 compatible pairs permit multidigit, independently for ADD and MUL |
| Array G1–G4 | ZERO, POSITIVE; G1≤4 and G4≤8. G2/G3 cannot have three indicator terms true at one index because that would require all four predicates, including mutually exclusive negative_value and value_exceeds_index; hence ≤8 |
| Array sanity offset 0 / offset 3 | ZERO, POSITIVE / POSITIVE; at most four hits plus offset, hence ≤7 |
| Array PREFIX | ZERO, POSITIVE; strict ordered-pair bound ≤6 |
| Array TWO | ZERO, POSITIVE in all rotations; MULTIDIGIT also in rotations pairing negative/even, even/large, large/exceeds. In exceeds/negative rotation the two counts sum to ≤4 and product ≤4 |

These are symbolic inequalities and truth-region existence statements, not concrete inputs, exhaustive truth-mask products or certificate instances. Compatible array predicate pairs have jointly nonempty integer/parity regions at every original index; this suffices for the stated maximum/count existence. The exceeds/negative pair has disjoint regions. Zero/positive membership follows from nonempty false/true regions with independent field domains. Training offsets 0 and 8 provide whole-condition category presence; no member inherits another's declarations or witnesses.

## 4. Cross-condition profile matrix

This matrix classifies all evaluation families enumerated above. Subfamilies with distinct type/local-parent/view roles inherit the listed classification only where the same owning clause fixes those roles. Where an arithmetic/indicator/count projection needs an unstated refinement or role mapping, the explicit underdetermined rows take precedence. No generic operator-token match is called exact coverage.

| Evaluation-essential profile family | ISOLATED union | COMPOSITION union | Classification and reason |
|---|---|---|---|
| Numeric INPUT, decoded-n carrier/attribute and declared INPUT_DOMAIN numeric interface | Same DN | Same DN | COVERED_BOTH; G §§6,16,20. Case classes excluded |
| Array INPUT/SPLIT/all TO_NUMBER/FIELD_VALUE and runtime attributes; declared INPUT_DOMAIN array interface | Same DA | Same DA | COVERED_BOTH; G §§7,16,20 |
| Array INPUT_TO_DECODER raw/field profiles, INDEX_READ and INT4/index operand-use profiles; arity/original-position facts and fixed pipe configuration | Same DA/LA | Same DA/LA | COVERED_BOTH. Pipe is an attachment, not an independent essential C profile |
| Forward loop/index INITIALIZE, STATE_VIEW, LE/ADD, committed step ASSIGN; bound/step/predicate argument/prior/index carry/control profiles and exact value-parent attributes | Same forward clauses | Same forward clauses | COVERED_BOTH; G §§4,6–7,10,16; reverse availability is additional |
| Every named primitive root, MOD/EQ/LT/LE and predicate-internal MUL; formal and internal numeric edges; exact parameter/runtime/fixed operand attributes | Every primitive present | Every primitive present | COVERED_BOTH for the same definition/typed local ports; G §8 |
| Single named-predicate IE reset/set, IF, BOOL_TO_INT, current read and Boolean control/conversion edges, reset/set parent values | Same §9 realization | Same §9 realization | COVERED_BOTH for clause-identical local predicate/indicator sites; no inference of activity |
| Composite-term IE site/role projection (IF, conversion, current read, reset/set and their directed control/value attributes) | No identical composite term | No identical composite term | UNDERDETERMINED_BY_FROZEN_TEXT where equality needs the exact composite-vs-primitive site/role binding; G §§9,20 retain roles but do not tabulate that mapping. No whole-expression equivalence is assumed |
| Base AND(BOOL,BOOL)→BOOL (B), all primary graphs | Absent | Absent | NEITHER; no training construction emits AND. J is separate |
| Base OR(BOOL,BOOL)→BOOL (B), G1/G4 | Absent | Absent | NEITHER; training lacks OR and the certified typed ADD-positive comparison/conversion pattern |
| Boolean VALUE_TO_OPERATOR operand uses: named predicate→AND/OR, AND-result→OR (G1), OR-result→AND (G4) | Absent | Absent | NEITHER; training predicate operands are numeric; conversion uses PREDICATE_TO_INDICATOR and IF uses PREDICATE_TO_CONTROL, not Boolean VALUE_TO_OPERATOR |
| Certified two-distinct-role local pair-joint relation in qualified primary conjunctions | No joint treatment | Certified indicator product relation | J_EXCEPTION_COMPOSITION_ONLY; only additional J key, not base AND or Boolean incident edges |
| G2/G3/G4 inner/direct ADD with two INDICATOR_INT operands | Typed ADD exists in treatment; exact evaluation local roles not fully mapped | No ADD with two indicator operands | UNDERDETERMINED_BY_FROZEN_TEXT as exact key: ISOLATED_ONLY if roles coincide, otherwise NEITHER. COMPOSITION-side absence is definite. G §§3,11–12,20 |
| G2/G3 outer ADD (inner sum, indicator), ordinarily INT/IND | No stipulated matching mixed-operand ADD | May depend on treatment-result refinement in TOTAL update | UNDERDETERMINED_BY_FROZEN_TEXT; G §3 says INT with proven refinement only where stipulated; §§10–12/20 do not fully fix refinement and local term/update role equality |
| G1/sanity direct U ADD(prior INT, indicator); PREFIX/TWO count-update ADD(prior INT, indicator) | Training TOTAL receives ADD-of-indicators, ordinarily INT; no stipulated INT/IND alternative | Training TOTAL receives indicator MUL, precise independent result/role projection unresolved | UNDERDETERMINED_BY_FROZEN_TEXT; ISOLATED typed mixed-ADD absence at stated INT result, COMPOSITION refinement/role equality unresolved. Not rescued by J |
| U contribution VALUE_TO_OPERATOR, OPERATOR_TO_ACCUMULATOR and contribution writer site, when t is IND or evaluation sum/product | Training t is treatment ADD result | Training t is treatment MUL result | UNDERDETERMINED_BY_FROZEN_TEXT for differing contribution types/roles; compare payload, application site and local source role independently. G §§3–4,9–12,20 |
| Clause-identical TOTAL INT initializer/PRE/carry/prior/accumulator-control/final completed read/output relation, excluding differing contribution-site rows above | Same TOTAL machinery | Same TOTAL machinery | COVERED_BOTH; U/UF G §10. Exact initial values classified separately |
| INITIAL_ACCUMULATOR exact 0 with TOTAL initialization parent | Offset-0 training exists | Offset-0 training exists | COVERED_BOTH |
| INITIAL_ACCUMULATOR exact 3 with TOTAL initialization parent, sanity variant 1 | Absent; offsets only 0,2,4,6,8 | Absent | NEITHER; parameter/bound/index-init 3 has a different parent/value role, G §16 |
| Structural count-state INITIALIZE, INITIAL_ACCUMULATOR 0, PRE/COMPLETED reads, writers/carries/prior/control projections against training TOTAL | Only TOTAL count/result machinery | Same | UNDERDETERMINED_BY_FROZEN_TEXT where count vs result storage/use roles need an exact mapping. G §§10,14–15,20 list distinctions but do not give a full reusable role projection for each such site |
| PREFIX PRE count→ordinary numeric contribution operand VALUE_TO_OPERATOR INT | Absent | Absent | NEITHER; index PRE role differs; TOTAL PRE into update is PRIOR_STATE_TO_UPDATE; training indicator operands are IND/current, not INT/prior-count |
| PREFIX independent MUL(IND,INT) and exact prior-count/product result roles | Predicate MUL is INT/INT, no stipulated exact match | Treatment MUL is IND/IND, predicate MUL INT/INT | NEITHER at mandatory input-type list; no conversion/coercion or J normalization of this base profile |
| TWO COMPLETED count→numeric operand VALUE_TO_OPERATOR INT, each completed port | Absent | Absent | NEITHER; training completed TOTAL goes to ACCUMULATOR_TO_OUTPUT, not arithmetic |
| TWO independent MUL(INT,INT) with count operands/final result local roles | INT/INT predicate MUL exists | INT/INT predicate MUL exists | UNDERDETERMINED_BY_FROZEN_TEXT for full role key; bare INT/INT MUL absence is refuted. G §§8,15,20 |
| TWO second-entry initialization considered solely as a new phase capability | Phase ordinal excluded | Phase ordinal excluded | COVERED_BOTH for generic phase-independent initialization capability; not a new key merely because phase is 1. Count-role/attribute equality remains in structural-count row |
| Final DISPLAY_INTEGER INT argument with newline/UNIT statement semantics | Present | Present | COVERED_BOTH; final-expression association is required context, not an invented output edge |
| Declared OUTPUT_ZERO/POSITIVE/MULTIDIGIT, separately by domain where evaluation-essential | Present in whole union | Present in whole union | COVERED_BOTH at declaration level only, G §17. No actual output witness asserted |

No evaluation-essential exact profile can safely be labeled COMPOSITION_ONLY from these clauses alone. Likewise the candidate ISOLATED_ONLY ADD comparison is deliberately not asserted as exact equality across differently described local sites. UNDERDETERMINED is a positive finding about the missing projection detail, not permission to pick a convenient serialization.

## 5. Adversarial adjudication of H-A through H-D

### H-A: independent AND absent from both training conditions

Attempted refutations: training predicates could hide AND; training MUL could be an AND-equivalent; J could satisfy the operator; symmetry could excuse absence. All fail under the frozen clauses. §8's eight predicate definitions contain only MOD/MUL/EQ/LT/LE. G §11 closes the training route to P/Q independent evaluations and one marked numeric treatment. G §9:

> AND and OR nodes in primary terms are independently B; MUL operator nodes independently N.

And:

> J cannot satisfy an independent AND/MUL selector.

A §5:

> Independent AND and MUL operator-node abilities still use B and N respectively and still require both-condition coverage where evaluation-essential.

G §20:

> No such normalization occurs for independent AND/MUL keys, which retain B/N, nor for multi-role conjunctions, general numeric products, PREFIX prior-count products or completed-count multiplication.

Outcome: H-A upheld. Base AND is NEITHER in all 32 primary specifications, 16 per domain. All four graphs contain it. This alone proves the final infeasibility verdict.

### H-B: OR absent from both training conditions

Attempted refutation: ISOLATED addition could supply the frozen OR-positive-indicator equivalence. Cov V3.3's exact limitation is:

> Boolean OR versus `indicator(add(a,b)>0)` is allowed only when both inputs are proven Boolean and the indicator/comparison is typed and source-mapped.

G §11 actually specifies:

> ISOLATED's treatment node is ADD of the two indicators. COMPOSITION's node is MUL of the SAME indicators at the SAME ports and construction path.

There is no comparison of that sum with zero followed by its certified indicator realization. Predicate-internal comparisons do not supply this missing local pattern. Cov V3.7:

> A two-role OR is an atomic Boolean operation but is not mislabeled as the COMPOSITION pair-joint motif.

Outcome: H-B upheld. OR is NEITHER in G1/G4: 16 specifications, eight per domain. The underlying Boolean operand edges also remain absent. No arbitrary algebraic OR replacement is licensed.

### H-C: indicator-input ADD in G2/G3/G4

Attempted refutations: COMPOSITION has other ADDs; commutativity/coercion could erase types; J could excuse ADD absence. Training COMPOSITION does have index ADD and TOTAL-update ADD. Their prior/index INT inputs do not give ADD(IND,IND). G §12 explicitly gives the three primary addition trees, while G §20 requires:

> For a base NODE selector, input_types is its exact formal input-port type list and output_type its actual semantic result;

G §11 states:

> ADD/MUL operator abilities and all their underlying primitive, decoder, value, control, dataflow and output requirements remain subject to the normal both-condition rule.

Outcome: definite COMPOSITION-side absence for two-indicator ADD in 24 primary specifications (G2/G3/G4, 12 per domain). Exact classification is UNDERDETERMINED_BY_FROZEN_TEXT: ISOLATED's treatment provides the same mandatory types, but §§11–12/20 do not fully tabulate equality of its local operand/result/activity roles with the evaluation inner/direct ADD. It would be ISOLATED_ONLY if those roles coincide, or NEITHER otherwise. No exception resolves either possibility. Outer and accumulator ADD refinements have the separate gaps in §4.

### H-D: structural transfer profiles

Attempted refutations: a training state read might cover any structural read; independent MUL tokens might cover structural products; later initialization could require a new phase capability.

G §14:

> The MUL's prior-count operand is a VALUE_TO_OPERATOR with PRE attachment; the prior operand of the P-count writer is PRIOR_STATE_TO_UPDATE.

G §15:

> After BOTH completions: MUL consumes the two completed count views at separate ports; its result output port, role FINAL_RESULT, supplies the final display.

G §4:

> For TWO_PASS the completed counts have VALUE_TO_OPERATOR edges into final MUL; the MUL result port has the required direct final-display association, not a fictitious accumulator-output edge.

Thus training TOTAL prior-update edges cannot stand in for PREFIX's count operand, and training completed-output edges cannot stand in for TWO's completed arithmetic operands. Index and indicator source roles/types are also distinct. PREFIX MUL(IND,INT) differs from training IND/IND treatment and INT/INT predicate MUL. These are definite NEITHER findings: eight PREFIX and eight TWO specifications, four per route/domain.

However, a blanket claim that TWO's INT/INT MUL type never occurs in training is refuted by G §8's first_half and large_magnitude predicate definitions. Their full final-count role equality is underdetermined, not established by the token/type alone.

A blanket new-key claim based on second-traversal entry is also refuted by G §20:

> Exact phase placement and state identity remain mandatory *occurrence attachments*, not a new multi-edge capability.

The initialization's exact count/result/value-parent role comparison is separately underdetermined; ordinal 1 itself is excluded from the reusable key. H-D is upheld for the explicit PRE/COMPLETED operand edges and PREFIX type profile, narrowed for TWO MUL and phase initialization. No structural exception exists.

## 6. Additional findings and limits

1. Independent Boolean VALUE_TO_OPERATOR profiles are NEITHER across all 32 primary specifications. A predicate-to-control or predicate-to-indicator edge has a different frozen operation label. A matched endpoint does not satisfy the edge. G §20: "An edge key names that one edge and its typed source/destination roles, not the full operations on both sides or a whole path."
2. Sanity offset 3 is a separate NEITHER attribute in eight specifications. G §16: "initial accumulated count/result/offset uses the distinct INITIAL_ACCUMULATOR evidence, with its exact mapped initialization writer, state and displayed-computation membership." The presence of an integer 3 in residue parameters, array bounds or reverse index initialization is insufficient because parent capability/local value role is retained.
3. Missing operator and missing incident edge obligations are independent; their affected tasks overlap and cannot be added as unique-task counts.
4. The exact arithmetic result refinement gap is G §3's "INT, with proven 0/1 refinement only where stipulated" together with §20's exact actual types/site. §§10–12 do not provide a complete type/role projection table for treatment result vs primary sum vs direct-indicator count update. No unfrozen wire table was imported to settle it.
5. Composite indicator and structural count role gaps arise from §20's retained local roles/site and count/result/prior/current/completed distinctions without a full clause-by-clause reusable projection. A whole-route mismatch is not itself a missing atomic key; exact local profiles must be compared. This is why these findings are explicitly underdetermined.
6. Output declarations and shared domain interfaces have no definite absence in the whole training unions at this level. This does not certify member-specific output cases, case-class overrides, source correspondence, activity or scientific rows. G §17: "Symbolic declaration is not coverage evidence."
7. The general evidence-class table is not a license to add an emitted profile. G §3: "General class-table availability is not permission to emit an operation/type absent from the scientific clauses." The absence of independent pipe C is a representation decision in G §7, not activity-based pruning performed by this audit.
8. No authority, wire proposal, ledger, witness population or candidate has been altered. No remedy, reinterpretation or recommendation is part of this document.

## 7. Every definite blocker and unresolved profile family: affected specifications

Counts are out of 64; per-domain counts are shown explicitly. Multiple rows can affect the same specification. Counts quantify presence of an obligation, not the number of unique canonical keys.

| Blocking or unresolved family | Primary (of 32) | Sanity (of 16) | Structural (of 16) | Domain breakdown and classification |
|---|---:|---:|---:|---|
| Independent AND B | 32 | 0 | 0 | Numeric 16, array 16; NEITHER |
| Independent OR B, G1/G4 | 16 | 0 | 0 | Numeric 8, array 8; NEITHER |
| BOOL VALUE_TO_OPERATOR named predicate→Boolean connective | 32 | 0 | 0 | Numeric 16, array 16; NEITHER |
| BOOL VALUE_TO_OPERATOR conjunction-result→OR, G1 | 8 | 0 | 0 | Numeric 4, array 4; NEITHER |
| BOOL VALUE_TO_OPERATOR OR-result→AND, G4 | 8 | 0 | 0 | Numeric 4, array 4; NEITHER |
| ADD(IND,IND), G2/G3/G4 | 24 | 0 | 0 | Numeric 12, array 12; COMPOSITION absent, exact full key UNDERDETERMINED |
| Outer mixed ADD, G2/G3 | 16 | 0 | 0 | Numeric 8, array 8; UNDERDETERMINED |
| Direct-indicator accumulator ADD, G1/sanity/count subupdates | 8 | 16 | 16 | Numeric 4+8+8, array 4+8+8; UNDERDETERMINED |
| Composite indicator realization/control/read/value-parent projection | 32 | 0 | 0 | Numeric 16, array 16; UNDERDETERMINED |
| Contribution operand/application/writer profiles depending on exact result refinement and local contribution role | 32 | 16 | 16 | Numeric 16+8+8, array 16+8+8; UNDERDETERMINED for differing profiles, not assertion all shared writer subprofiles are missing |
| Structural count INITIALIZE/zero-attribute/PRE/COMPLETED/writer/carry/prior/control local projection | 0 | 0 | 16 | Numeric 8, array 8; UNDERDETERMINED; exact late phase is attachment only |
| PREFIX PRE-count VALUE_TO_OPERATOR INT | 0 | 0 | 8 | Numeric 4, array 4; NEITHER |
| PREFIX independent MUL(IND,INT) | 0 | 0 | 8 | Numeric 4, array 4; NEITHER |
| TWO COMPLETED-count VALUE_TO_OPERATOR INT at both count ports | 0 | 0 | 8 | Numeric 4, array 4; NEITHER |
| TWO MUL(INT,INT) completed-count/final-result roles | 0 | 0 | 8 | Numeric 4, array 4; UNDERDETERMINED; bare type exists both |
| INITIAL_ACCUMULATOR exact 3, sanity offset-3 variant | 0 | 8 | 0 | Numeric 4, array 4; NEITHER |

Definite distinct-specification blocker union: primary 32/32, sanity 8/16, structural 16/16 = 56/64 (numeric 28/32, array 28/32). The remaining eight sanity offset-0 specifications have no definite blocker proven here but retain the indicated refinement/projection uncertainties. This is not a claim that those eight pass coverage. The unresolved rows also do not weaken any already definite absence.

## 8. Final verdict

FROZEN_STACK_COVERAGE_INFEASIBLE_AT_SPECIFICATION_LEVEL

The frozen training construction cannot emit independent AND required in every primary graph. V3.4/V3.6 demand both-condition coverage, and the sole local-J exception cannot satisfy that operator selector. This necessary-condition failure is decisive without resolving any projection ambiguity or examining activity/cases. OR, Boolean operand edges, structural count-consumption/type profiles and sanity initializer 3 provide additional failures. The analysis confers no authority, freeze, implementation approval or candidate status.

