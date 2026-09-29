# CONF1 delegated-evidence and Coverage-v3 closure interfaces

**Status: PROPOSED PROSPECTIVE METHODOLOGY FOR INDEPENDENT REVIEW; NOT FROZEN; NOT IMPLEMENTED; NO CANDIDATE OR MODEL EXECUTION AUTHORIZED.**

This proposal closes only the mechanical representation, enumeration, identity, and closure interfaces required by the frozen CONF1 Coverage-v3 methodology. It does not alter any scientific gate, task, case, seed, graph, treatment, budget, threshold, or authorization rule. It does not accept a candidate. Attempt 004 remains prohibited until this interface and a real consumed-inventory manifest have received separate independent review and prospective freezes.

## 1. Authority, scope, and precedence

The scientific meanings remain owned by the existing authorities:

1. `phase3c_conf1_coverage_v3_proposed.md` and its freeze manifest;
2. `phase3c_conf1_paired_scaffold_normalization_proposed.md` and its freeze manifest;
3. `phase3c_conf1_input_domain_case_classes_and_training_amendment_proposed.md` and its freeze manifest;
4. `phase3c_conf1_slots.json`;
5. `phase3c_conf1_proposed_protocol.md`;
6. `phase3c_conf1_coverage_v3_v2_disposition.md`; and
7. `phase3c_conf1_ast_adjudication_v2.md`.

This document is subordinate to those scientific authorities. If an interface field cannot represent a required scientific finding without changing its meaning, the report is `UNRESOLVED` and the candidate fails. A later interface revision requires prospective review; it cannot reinterpret a candidate result.

Historical Attempt-001 through Attempt-003 reports and current scripts are descriptive format evidence only. Their field names, counts, omissions, and aggregate conventions do not become normative through this proposal.

Scientific finding production is owned by the authoritative E1--E6 producers and by the Coverage-v3 direct-evidence producer. Evidence closure is owned by the Coverage-v3 binder. The binder verifies identity, schema, population, uniqueness, status, and hash closure. It never substitutes a weaker scientific calculation for a producer finding.

The repository identities verified before drafting this proposal are:

| Authority | Recorded/current SHA-256 | Git blob |
|---|---|---|
| Frozen Coverage v3 | `a9fb8350c849ce62e2a673e3ca1f1d5a08f556b7f415687f1e2eabdf356030f3` | `16210d9810d217461b77546c3568c3344c0c770b` |
| Coverage-v3 freeze manifest | `8d8f8a37c808d84c740867174e219803712213e672687c42164500f2bca12291` | `28c0fb52fba083e72f87ebfc530fd88ddded5f92` |
| Frozen paired-scaffold authority | `ef6063d39319d8b3bd3dbe6bdaa93b474217fa4c37d50ef43dfed5afc8da1fc0` | `475e9de4a0ef3bef23edac1e3631011a20790f5a` |
| Paired-scaffold freeze manifest | `ff1a9610b10ff559ac1859361fb7a31668210ed33e97c2864e592981bd9cfea2` | `9a54e9b525b1795b10f94bf0d0250ae831e6db74` |
| Frozen INPUT_DOMAIN amendment | `bb59ad7cf4cb22c2492427a1fa5a78b0d81398ab16fb0a9cb8229d8c9489182e` | `66467ef968e4963dd7a22568100a940871ad304c` |
| INPUT_DOMAIN freeze manifest | `de4a353d58515b5c53210664ea1a642731ac6f1734f23afef4ae512fb8c2627a` | `774eb73150f66d2545ddf270cc2f051eddedc156` |
| Frozen semantic slot ledger | `83436eecda3affe813b785e868e3f8936fa59afc35ded0eb6a54290edb41dc88` | `133c9c7275bcedeaf2474e54e61bae47923508ad` |
| Historical CONF1 protocol | `11e40c821fa26e5a687cea8b8a9a0aa5a0b0c388eae31c99de9814ab2bd80920` | `7ec58f3b4d5fc5827e35e4fbf22712a300240cec` |
| Frozen v2-to-v3 disposition | `fb8a385538ddebf95195f099b9ba933bde97d33faf86373a7611e532e8b637d2` | `511843b001f6827c2b46242155485eecc3e429d8` |
| AST-v2 authority, exact bytes | `962960ed6d766b574d2f9812b8ade5b5faa824acfe84e85b520636e2d6667fd9` | `c1ffc66d6b8a98645711cd77b6ff49fde5841deb` |

All table SHA-256 values except AST-v2 use their recorded LF-normalized text policy. AST-v2 is listed with an exact-byte SHA-256 because it has no accompanying freeze manifest that declares the same text-normalization policy.

## 2. Exact-byte hash policy and shared references

All new candidate manifests, expected-row indexes, producer-tool manifests, direct-evidence files, and E1--E6 reports use UTF-8 JSON. SHA-256 is computed over exact file bytes, and `size_bytes` is the exact byte length. No CRLF/LF normalization is applied. A file does not contain its own SHA-256. Frozen historical and methodology artifacts retain the hash policy already recorded by their own freeze manifests.

Every file-level reference uses this closed object:

```json
{
  "artifact_id": "stable unique ID within the candidate",
  "artifact_role": "closed role from the manifest schema",
  "path": "repository-relative path",
  "sha256": "64 lowercase hexadecimal characters",
  "size_bytes": 1,
  "hash_policy": "EXACT_BYTES_SHA256"
}
```

`size_bytes` is a nonnegative integer; zero is allowed only where the artifact schema expressly permits an empty file. Paths are descriptive locations, never identity. The binder resolves each path inside the declared candidate root, reads exact bytes, and requires hash and size equality.

When a row refers to one logical record inside a bound JSON artifact, it uses a `record_reference` containing `artifact_id`, the artifact schema's stable `record_id`, and, for source/prompt/target or case strings, `content_sha256_utf8` and `content_size_bytes_utf8` over the exact UTF-8 payload. This does not replace the containing artifact's file-level closure.

## 3. Stable IDs and expected-row indexes

All candidate, program, task, slot, case, cell, and consumed-record IDs must be unique in their authoritative input inventory. Unknown or duplicate IDs fail before evidence execution.

For each report or row set, a pre-run `expected_row_index` JSON artifact enumerates the complete ordered list of expected row IDs, the derivation name, the exact input-inventory artifact IDs used, and the expected count. These index artifacts are generated without making a scientific classification, are reviewed with the candidate inputs, and are bound by `candidate_input_manifest.json` before evidence producers run. Reports cannot choose or shrink their own populations.

For a cross-product pair, the stable shared pair ID is constructed from the exact candidate-program ID and consumed-record ID using unambiguous UTF-8 byte-length framing:

```text
PAIR|<candidate_utf8_byte_length>:<candidate_id>|<consumed_utf8_byte_length>:<consumed_id>
```

E2 and both E4 reports use this same `pair_id`. E5 uses an analogous `E5|<primary-length>:<primary-id>|<training-length>:<training-id>` ID. E6 unordered primary pairs place the two task IDs in ascending UTF-8 byte order and use the same length framing prefixed by `E6PAIR|<domain>|`.

## 4. Non-self-referential candidate manifests

### 4.1 `candidate_input_manifest.json`

This manifest is created and frozen before any candidate-specific scientific evidence producer runs. It does not contain E1--E6 report hashes or scientific outcomes. Its closed top-level fields are:

- `schema_version`, `phase`, `candidate_id`, `attempt_id`, `status`;
- `model_execution_authorized`, which must be actual JSON boolean `false`;
- `candidate_root` and `hash_policy`;
- `frozen_authorities`, each with identity, path, recorded hash policy, SHA-256, size, and Git blob or freeze identity where available;
- `slot_ledger` and `candidate_artifacts`;
- `coverage_contract_inventory`;
- `schedule_manifest`;
- `compiler_identities`;
- `consumed_inventory_manifest`;
- `producer_tool_manifests`;
- `expected_row_indexes`; and
- `construction_provenance`.

`candidate_artifacts` binds every training example, target/reference, prompt, case, evaluation task/reference/case, serialization input, and configuration file required by a report. `coverage_contract_inventory` binds one prospective `CoverageContractV3` for each of the 120 training programs and 64 evaluation tasks. The manifest's own SHA-256 is recorded only by downstream reports and the later evidence manifest.

### 4.2 `candidate_evidence_manifest.json`

This manifest is created only after the direct Coverage-v3 evidence and every required delegated report exist. Its closed fields are:

- `schema_version`, `phase`, `candidate_id`, `status`;
- `model_execution_authorized`, again actual JSON boolean `false`;
- an exact artifact reference to `candidate_input_manifest.json`;
- exact artifact references to `coverage_v3_direct_evidence.json` and all nine delegated report files;
- `report_status_summary`;
- `overall_audit_state`, one of `ALL_REPORTS_PASS`, `BLOCKED`, or `UNRESOLVED`; and
- `failure_reasons`.

The nine delegated files are E1; E2; the three E3 reports; the two E4 reports; E5; and E6. `ALL_REPORTS_PASS` is permitted only when every referenced report declares `PASS`; it is not the final Coverage-v3 decision. The binder consumes both manifests and all referenced bytes and emits a separate closure result, avoiding a self-reference. A later candidate freeze may bind that closure result; this proposal does not create such a freeze.

## 5. Producer-tool identity

Before evidence execution, each distinct report producer has a `producer_tool_manifest.json`, or a separately named manifest with the same closed schema. One manifest may cover multiple reports only when the identical entrypoint, dependency closure, rules, and execution configuration produce all of them.

Required fields are:

- `schema_version`, `producer_id`, `contract_ids`, `report_types`;
- `entrypoint`, as an exact artifact reference;
- `repository_dependency_closure`, an exhaustive list of exact artifact references for every repository-local source, imported helper, schema, configuration, prompt/template, and static data file that can affect the result;
- `rule_authorities`, exact references to all controlling frozen scientific rules;
- `external_runtime`, including executable/package name, version, immutable distribution or environment identity where available, and provenance source;
- `execution_configuration`, containing all flags, environment settings, timeouts, limits, locale/encoding, and command template that can affect output;
- `output_schema_version`; and
- `dependency_enumeration_method` and `unresolved_dependencies`.

Any unresolved dependency makes the tool manifest unusable. A producer report references the exact tool-manifest SHA-256 and size through the candidate input manifest. A single script hash never stands for unlisted imports or configuration.

## 6. Candidate-level compiler identity

`candidate_input_manifest.json` contains one stable `compiler_identity_id` and this closed object:

- compiler JAR artifact reference, including exact JAR SHA-256 and size;
- compiler source/provenance-record artifact reference, including exact SHA-256 and size;
- the upstream compiler commit and source-tree identities recorded by that provenance;
- Java executable/distribution identity, vendor, version, architecture, and an executable or immutable distribution hash where available;
- the compiler wrapper/tool artifact identity;
- exact command template, working-directory policy, input encoding, output normalization, timeout, output-size limit, locale, and relevant environment configuration; and
- `identity_status`, which must be `CLOSED`.

The existing provenance record `research/manifests/goco_compiler_source.json` currently has exact-byte SHA-256 `67a15aefe1be747c630e887e6e030ae6dcf37ddd64e71b13b0fca7e41587725d` and size 1,289 bytes. It identifies upstream commit `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`. The deterministic JAR currently has SHA-256 `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb` and size 212,005 bytes. A future candidate must bind the then-present exact files and runtime; this proposal does not silently freeze an unrecorded Java executable or invocation.

Every report contains `compiler_relevance`, with `status` exactly `REQUIRED` or `NOT_APPLICABLE`, and a closed `reason_code`:

| Report | Relevance rule |
|---|---|
| E1 | `REQUIRED`; reason `EXECUTES_PINNED_COMPILER`. |
| E2 | `REQUIRED`; reason `COMPILER_VALID_SOURCE_AND_GRAMMAR_AUTHORITY`. |
| E3 scaffold | `REQUIRED`; reason `PARSED_GOCO_AND_MECHANICAL_OUTPUT_DERIVATION`. |
| E3 token | `NOT_APPLICABLE`; reason `TOKENIZER_ONLY_NO_COMPILER_DEPENDENCY`, unless its implementation invokes compiler-backed parsing, in which case `REQUIRED`. |
| E3 schedule | `NOT_APPLICABLE`; reason `SCHEDULE_ONLY_NO_COMPILER_DEPENDENCY`. |
| E4 reports | `NOT_APPLICABLE`; reason `TEXTUAL_OVERLAP_WITHOUT_COMPILER_DEPENDENCY`, unless the actual producer invokes compiler parsing, in which case `REQUIRED`. |
| E5 | `NOT_APPLICABLE`; reason `CONSUMES_E1_VALIDATED_SOURCE_CONTRACT_MAPPING`, only when it consumes already bound mappings and does not invoke compiler parsing; otherwise `REQUIRED`. |
| E6 | `NOT_APPLICABLE`; reason `CONSUMES_E1_VALIDATED_REFERENCE_CASE_FACTS`, only when it does not compile or execute references; otherwise `REQUIRED`. |

When `REQUIRED`, `compiler_identity_id` must equal the input manifest's closed identity. When `NOT_APPLICABLE`, `compiler_identity_id` must be JSON `null`; omission is invalid.

## 7. Common evidence-report envelope

Every E1--E6 report uses these exact top-level fields:

```text
schema_version
phase
candidate_id
contract_id
report_type
status
candidate_input_manifest_sha256
candidate_input_manifest_size_bytes
producer_tool_manifest_sha256
producer_tool_manifest_size_bytes
rule_authorities
compiler_relevance
compiler_identity_id
input_artifacts
expected_row_population
observed_row_population
rows
aggregate
failure_reasons
```

`schema_version` is a supported positive integer. `phase` is `PHASE_3C_CONF1`. Status is exactly `PASS`, `FAIL`, or `UNRESOLVED`. `rule_authorities` and `input_artifacts` are exact references to entries already bound by the input manifest, not free-form copies. `expected_row_population` references the pre-run index artifact and records its count and SHA-256. `observed_row_population` records count, unique count, ordered row-ID digest, missing IDs, duplicate IDs, and unexpected IDs. `rows` contains the contract-specific row sets below. `aggregate` contains only deterministic summaries derived from rows. `failure_reasons` is an ordered list.

A report can be `PASS` only if all referenced artifacts, rule identities, producer-tool identities, and relevant compiler identity close; expected and observed row IDs are exactly equal; there are no duplicates; every blocking row is `PASS`; aggregate values reconcile with rows; and no `UNRESOLVED` item remains.

## 8. Closed interface reason codes

The common interface vocabulary is:

- `MISSING_ROW`
- `DUPLICATE_ROW`
- `UNEXPECTED_ROW`
- `INPUT_ARTIFACT_HASH_MISMATCH`
- `INPUT_ARTIFACT_SIZE_MISMATCH`
- `CANDIDATE_INPUT_MANIFEST_MISMATCH`
- `PRODUCER_TOOL_IDENTITY_MISMATCH`
- `RULE_IDENTITY_MISMATCH`
- `COMPILER_IDENTITY_MISMATCH`
- `COMPILER_RELEVANCE_INVALID`
- `MALFORMED_REPORT`
- `UNSUPPORTED_SCHEMA_VERSION`
- `PRODUCER_ROW_FAIL`
- `PRODUCER_ROW_UNRESOLVED`
- `AGGREGATE_INCONSISTENCY`
- `EXPECTED_POPULATION_MISMATCH`
- `MODEL_AUTHORIZATION_NOT_FALSE`
- `FROZEN_AUTHORITY_MISMATCH`

Each reason record contains `code`, `contract_id`, optional `row_id`, optional `artifact_id`, and `detail_reference`. Producers retain their closed contract-specific scientific reason codes in each affected row. The binder may add interface reasons but may not translate, erase, or replace scientific reasons.

## 9. Coverage-v3 direct evidence

`coverage_v3_direct_evidence.json` is the versioned output of the future Coverage-v3 contract, parser/mapping, equivalence, activity, and atomic-coverage engine. It uses the same identity and population fields as the common envelope, with `contract_id` `COVERAGE_V3_DIRECT`. It does not duplicate delegated scientific findings.

Its pre-enumerated row sets are:

- `v3_1_contract_rows`: one per 120 training and 64 evaluation contracts, total 184, binding contract provenance, required keys, source/case references, and case obligations;
- `v3_2_mapping_rows`: one per program/reference, total 184, binding the closed parse and complete contract/source node-and-edge mapping, plus any mechanically proved `REFERENCE_ONLY` constructs;
- `v3_3_equivalence_rows`: one per program/reference, total 184, with a complete nested list of every equivalence claim invoked for that record, its source locations, context, and closed V3.3 rule; an empty nested list is a resolved finding only when the complete V3.2 mapping requires no equivalence claim;
- `v3_5_activity_rows`: one per potential task-essential behavioral or attribute-key occurrence declared by each of the 120 training contracts, enumerated before execution from contracts and frozen expected-output facts, with mapped paths, normal-event case, ordered intervention, normal and counterfactual outputs, and a resolved finding `ACTIVE` or `INACTIVE`, or `UNRESOLVED`; `INACTIVE` is not itself an interface failure because V3.4, rather than every individual occurrence, decides whether each required key has at least one active witness;
- `input_domain_class_rows`: exactly 14 condition/domain/class obligations: four numeric and three array classes in each of two conditions, with example, case, decoded-value/element, class, and decoder mapping; these rows remain distinct from V3.5 activity rows;
- `v3_4_coverage_rows`: one per evaluation-task-essential atomic key and required condition, with the sole pair-joint relation exception represented as a prospectively marked COMPOSITION-only relation; IDs are enumerated from the 64 evaluation contracts before execution;
- `v3_6_symmetry_rows`: one per required shared key/condition comparison plus one treatment-exception declaration and references to all 60 E3 scaffold rows; and
- `v3_7_delegation_row`: exactly one row binding the complete E5 report and confirming that no weaker novelty result was reconstructed.

Each gate row has status `PASS`, `FAIL`, or `UNRESOLVED`, scientific reason codes, evidence record references, and source offsets or graph paths where V3 requires them. This direct report is bound by the evidence manifest and traversed by the final binder.

## 10. E1 — compiler/reference validation

Required file: `reference_validation.json`.

The expected index contains exactly 184 program rows: 60 ISOLATED training targets, 60 COMPOSITION training targets, and 64 evaluation references. Program IDs come from the candidate's frozen inventories. Row ID is `E1|<program_type>|<program_id>`.

Each program row contains:

- `row_id`, `program_id`, `program_type`, condition or evaluation group;
- source/reference and case-set `record_reference` objects;
- exactly five expected case IDs, in frozen order;
- compile result, phase, and diagnostic artifact/reference;
- exactly five nested case outcomes with case ID, input reference, expected output, actual normalized output, execution phase, and status;
- compiler identity ID;
- row status and scientific reason codes.

The nested population is exactly 920 case outcomes. E1 `PASS` requires all 184 rows, exactly five unique expected cases per row, all 920 compile/semantic outcomes `PASS`, compiler closure, and source/case hash closure. The binder verifies these facts and the producer's statuses; it does not invoke or emulate the compiler.

## 11. E2 — AST-v2 structural overlap

Required file: `ast_v2_overlap_audit.json`.

`consumed_inventory_manifest.json` prospectively enumerates the real permitted consumed population. If it has `N` records, the E2 expected population is `184 × N`, absent a separately frozen exclusion rule. No historical value of `N` is adopted here.

Each row contains shared `pair_id`, candidate program ID and source record reference, consumed ID and source/template record reference, legacy coarse-equality flag, canonical-tree identity/digest for both sides, exact frozen AST-v2 classification (`PROHIBITED_STRUCTURAL_TEMPLATE_REUSE`, `COARSE_AST_EQUALITY_ONLY`, or `STRUCTURALLY_DISTINCT`), adjudication status, and scientific reason codes. Prohibited reuse is `FAIL`; coarse-only and distinct are resolved results whose row status is `PASS`; parse, validity, or classification uncertainty is `UNRESOLVED`. Missing or unadjudicated pairs block.

## 12. E3 — matched scaffold, tokens, and schedule

### 12.1 `scaffold_allowed_difference_audit.json`

The expected population is exactly 60 paired-slot rows, one for every frozen `training_paired_slots` ID. Each row binds the slot ID; ISOLATED and COMPOSITION program IDs; source, prompt, and case-set references; the five ordered paired case IDs and exact inputs; marked treatment-expression and treatment-description classifications; every protected-field comparison required by the paired-scaffold authority; mechanical expected-output derivations for both conditions on all five inputs; feature counts; row status; and scientific reasons.

Only the frozen treatment expression and treatment description may be `INTENDED_TREATMENT_DIFFERENCE`; only mechanically derived outputs and treatment serialization may be `UNAVOIDABLE_SEMANTIC_CONSEQUENCE`. Every other field is `MATCHED` or the row fails.

### 12.2 `token_budget_audit.json`

The expected population is exactly 120 model-facing example rows. Each row includes example ID, condition, exact prompt/input/target record references, tokenizer and chat-template identities, prompt/input token count, supervised target-token count, full serialized-token count, truncation status, applicable 320-token check, row status, and reasons.

The aggregate deterministically reports each condition's example and token totals, maximum sequence length, supervised-token relative difference, full-token relative difference, and the frozen 2%/5%/320 limits. All rows and aggregates must pass.

### 12.3 `schedule_audit.json`

The frozen design has five paired seeds and two conditions, hence 10 cell rows. Each cell has 60 examples over three epochs, hence 180 exposure rows and 24 optimizer-step rows. The full expected population is therefore:

- 10 `cell_rows`;
- 1,800 `exposure_rows` (180 per cell); and
- 240 `optimizer_step_rows` (24 per cell).

Exact IDs and ordering derive from the frozen schedule manifest bound in the candidate input manifest. Cell rows bind seed, condition, example inventory, epochs, microbatch, accumulation, exposures, and step totals. Exposure rows bind cell, epoch, within-epoch ordinal, example ID, and the step/accumulation group receiving that exposure. Optimizer-step rows bind cell, epoch, step ordinal, contributing exposure IDs, accumulation cardinality, and final partial-step handling prescribed by the schedule. The producer reconciles membership, duplicates, omissions, 180 exposures, 24 steps, and paired schedule rules without creating candidate-specific exceptions.

All three E3 reports must independently close and declare `PASS`.

## 13. E4 — consumed-suite overlap

Required files are `consumed_similarity_pairs.json` and `exact_overlap_audit.json`. Both reference the identical frozen consumed-inventory manifest and identical expected pair index. If that inventory has `N` records, each file has exactly `184 × N` pair rows and uses the same shared `pair_id`.

`consumed_similarity_pairs.json` contains candidate and consumed identities, every prespecified descriptive metric, normalized-code and coarse/structural fields where delegated to it, and deterministic nearest-neighbor summaries. Complete enumeration is required; descriptive status does not create a new scientific threshold.

`exact_overlap_audit.json` owns the blocking exact prompt, source/reference/target, normalized-source, and full-template decisions required by the frozen protocol. Each row records the applicable compared fields, exact flags, normalized/full-template result, final prohibited/allowed/unresolved classification, status, and scientific reasons.

The binder reconciles pair IDs across both files exactly. It does not recompute a textual-overlap decision or turn a descriptive similarity value into a veto.

## 14. E5 — full-signature novelty

Required file: `full_signature_novelty_audit.json`.

### 14.1 `primary_certificates`

Exactly 32 rows, one per primary evaluation task, contain task ID; task-contract reference; domain; role map and role count `k`; typed complete-graph identity; the complete ordered `2^k` contribution vector; aggregation/state recurrence; fixed initialization or fully represented initialization/state; source-to-contract completeness references; hidden/unrepresented-state checks; certificate status; and scientific reason codes. The field `k` here is role cardinality, distinct from any training accumulator offset.

### 14.2 `training_certificates`

Exactly 120 rows, one per training program, encode the same completeness fields needed for comparison. They prevent 3,840 comparisons from silently using an uncertified aggregate training signature.

### 14.3 `comparisons`

Exactly 32 primary tasks × 120 training programs = 3,840 rows under the current frozen design. Each row binds primary task ID, training program ID, both domains, role cardinalities, role-bijection enumeration/status, typed-graph comparison, graph-isomorphism result, complete semantic contribution/output-signature comparison, semantic-equality result, local-pair-motif diagnostic, final result (`COLLISION`, `NONMATCH`, or `UNRESOLVED`), row status, and reasons.

Graph isomorphism or complete semantic-signature equality independently yields `COLLISION` and row `FAIL`. A frozen V3.7 fewer-role motif comparison records a resolved `NONMATCH`, not missing or unresolved. Any incomplete certificate, unrepresented output-affecting state, undecidable role bijection, or unresolved graph/semantic comparison is `UNRESOLVED`. E5 `PASS` requires all 32 primary certificates, all 120 training certificates, all 3,840 comparison rows, and no collision or unresolved result. The binder verifies closure and status only; it does not rebuild signatures.

## 15. E6 — hidden-case discrimination

Required file: `hidden_case_discrimination.json` with two blocking row sets.

`task_rows` contains exactly 64 rows, one per evaluation slot. Each binds task ID, contract and case-set references, exactly five nested case outcomes, and every prospectively declared task-essential behavior witness. The nested case population is exactly 320. Each witness identifies the behavior obligation, case IDs, source/contract path, observed behavior, status, and scientific reasons.

`pair_distinction_rows` contains every unordered pair among the 16 primary slots separately within each domain: 120 numeric rows and 120 array rows, total 240. Each row contains domain, task A, task B, case/input witness references, the mechanically observed output or contribution difference, status, and reasons. Cross-domain pairs are not required by the frozen domain-specific 120/120 rule.

E6 `PASS` requires complete 64-task, 320-case, and 240-pair closure, all declared behavior obligations witnessed, and all required within-domain pairs distinguished. An aggregate `64/64` or `240/240` without the rows cannot pass.

## 16. Consumed-inventory boundary

`consumed_inventory_manifest.json` has closed fields `schema_version`, `status`, `inventory_id`, `authority`, `inclusion_rule`, `exclusion_rules`, `records`, `record_count`, `source_artifacts`, `hash_policy`, and `failure_reasons`.

Every record contains stable `consumed_id`, origin/suite, record type, source/template and prompt/target record references where applicable, exact file/content hashes and sizes, and the authority justifying inclusion. Duplicate semantic IDs or an unbound source artifact fail. The manifest must be independently reviewed and frozen before Attempt-004 construction. This proposal defines its format and completeness proof but does not choose its real contents and does not freeze the historical 420 records or 77,280 pair count. Later synthetic implementation tests may use a small manifest explicitly labeled `SYNTHETIC_FIXTURE_ONLY`.

## 17. Final binder and `ALL_GATES_PASS`

The final binder may emit `PASS` only when:

1. `candidate_input_manifest.json` closes and every frozen authority matches;
2. `model_execution_authorized` is actual boolean `false` in both candidate manifests;
3. every V3.1--V3.7 direct-evidence row population closes and every row passes;
4. all nine E1--E6 report files close against their exact expected indexes and declare `PASS`;
5. `candidate_evidence_manifest.json` binds the exact input manifest, direct report, and all report hashes and sizes;
6. every compiler-relevance and producer-tool identity closes;
7. no row, report, manifest, or dependency is `UNRESOLVED`; and
8. aggregate summaries reconcile exactly with their rows.

A later separate protocol action is required to authorize model execution. Evidence PASS cannot change authorization.

A future synthetic fixture labeled `ALL_GATES_PASS` qualifies only if execution emits an ordered trace with these exact gate records, all marked `executed: true`, all `PASS`, and each containing its input/output evidence references and verified row counts:

1. `V3.1_CONTRACTS`
2. `V3.2_TYPED_SOURCE_MAPPING`
3. `V3.3_CLOSED_EQUIVALENCE`
4. `E1_REFERENCE_VALIDATION`
5. `V3.5_ACTIVITY`
6. `V3.4_ATOMIC_COVERAGE`
7. `V3.4_INPUT_DOMAIN_CLASSES`
8. `V3.6_TREATMENT_SYMMETRY`
9. `E3_SCAFFOLD`
10. `E3_TOKEN_BUDGET`
11. `E3_SCHEDULE`
12. `V3.7_E5_FULL_SIGNATURE`
13. `E2_AST_V2`
14. `E4_SIMILARITY_PAIRS`
15. `E4_EXACT_OVERLAP`
16. `E6_HIDDEN_CASE_DISCRIMINATION`
17. `V3.8_FINAL_CLOSURE`

The validator rejects a trace with a missing, duplicated, reordered, skipped, mocked-away, or aggregate-only gate. Synthetic reports may contain synthetic scientific inputs, but they must be schema-complete and traverse the same closure and decision paths. No fixture is created by this proposal.

## 18. Compatibility review

| Authority | Classification | Finding |
|---|---|---|
| Coverage V3.1 | Prospectively supplemented | Adds exact contract/input identities, expected indexes, and a direct-evidence row format; does not alter contract derivation or case obligations. |
| Coverage V3.8 | Prospectively supplemented | Makes missing/stale/unresolved evidence mechanically detectable and preserves fail-closed behavior. |
| E1 | Prospectively supplemented | Fixes row and nested-case closure while preserving compiler/semantic PASS ownership. |
| E2 and AST-v2 | Prospectively supplemented | Represents every frozen AST-v2 pair classification; no structural rule or label changes. |
| E3 and paired-scaffold authority | Prospectively supplemented | Represents every protected comparison, token row, and schedule row; allowed differences and limits are unchanged. |
| E4 | Prospectively supplemented | Makes the consumed population explicit and shared; exact/template prohibitions and descriptive metrics remain unchanged. |
| E5 / V3.7 | Prospectively supplemented | Requires certificates and all comparisons; graph or semantic collision rules are unchanged. |
| E6 | Prospectively supplemented | Requires task/case and within-domain pair rows; behavior and distinction requirements are unchanged. |
| Historical CONF1 manifest requirements | Compatible | Two-stage manifests provide the required hashes, sizes, identities, audit bindings, and false authorization without circular hashes. |
| INPUT_DOMAIN amendment | Prospectively supplemented | Adds the 14 condition/domain/class rows and keeps class presence separate from V3.5 decoder activity. |

No conflict was identified. If independent review finds that a field changes a scientific PASS condition, this proposal must stop rather than be implemented.

## 19. Prospective self-review and remaining boundaries

This proposal satisfies the following interface checks:

1. Scientific PASS conditions, thresholds, budgets, tasks, cases, seeds, graphs, and treatment rules are unchanged.
2. Historical reports remain descriptive and are not promoted to authority.
3. The real consumed population remains unfrozen; neither 420 nor 77,280 is adopted.
4. Expected populations are fixed counts where existing authority fixes inventories and are exact cross-products of independently frozen indexes otherwise.
5. Every report has row-level closure and duplicate/missing/unexpected-row handling.
6. Compiler relevance is explicit for every report.
7. Producer identity covers dependencies, rules, runtime, and execution configuration rather than one script hash.
8. Input and evidence manifests do not hash themselves or create report cycles.
9. E5 requires 32 primary and 120 training certificates plus 3,840 comparisons; an aggregate novelty flag cannot pass.
10. E6 requires 64 task rows, 320 nested cases, and 240 pair rows; aggregate counts cannot pass.
11. A full-path synthetic PASS must contain all 17 executed gate records.
12. Unknown, missing, duplicate, stale, mismatched, failed, or unresolved evidence blocks.

Remaining work is deliberately outside this proposal: independent review and freeze of this interface; independent review and freeze of the real consumed-inventory contents; implementation and preregistered scientific fixtures; prospective candidate construction; candidate-specific producer-tool manifests and expected indexes; candidate evidence production; and any separate authorization decision. None is implied by this document.
