# Frozen CONF1 delegated-evidence and Coverage-v3 closure interfaces

**Status: FROZEN PROSPECTIVE PRE-ATTEMPT-004 METHODOLOGY; NOT IMPLEMENTED; CANDIDATE CONSTRUCTION UNAUTHORIZED; MODEL EXECUTION UNAUTHORIZED.**

Independent scientific review approved the exact proposal at commit `027427ed5567aa75e10e35a0b3ed342516094ce9`, with exact-byte SHA-256 `1c43f9bc4a1a93e20dec68a69963d123da909c7332647371a09612802f1bff0e`, Git blob `181cd74b0ba9ada1e8e2493504b6723699cd5c86`, and size 75,388 bytes. The accompanying `phase3c_conf1_delegated_evidence_interfaces_freeze.json` binds this frozen file, its upstream authorities, and the exact normative region beginning at `## 1. Authority, scope, and precedence`; that region is byte-for-byte unchanged from the approved proposal.

This freeze makes only the approved mechanical representation, enumeration, identity, and closure interfaces a normative prospective authority. It does not alter any scientific gate, task, case, seed, graph, treatment, budget, threshold, or authorization rule. It does not accept a candidate or authorize implementation, synthetic scientific validation, consumed-inventory contents, candidate construction, model execution, or sealed-holdout access. Attempt 004 remains prohibited, and the real consumed-inventory contents still require separate independent review and prospective freeze.

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

All new candidate manifests, expected-row indexes, producer-tool manifests, producer-execution-provenance artifacts, direct-evidence files, and E1--E6 reports use UTF-8 JSON. SHA-256 is computed over exact file bytes, and `size_bytes` is the exact byte length. No CRLF/LF normalization is applied. A file does not contain its own SHA-256. Frozen historical and methodology artifacts retain the hash policy already recorded by their own freeze manifests.

Every JSON artifact newly defined by this proposal has exact integer `schema_version: 1`. This includes the candidate input and evidence manifests, consumed-inventory manifest, producer-tool manifests, producer-execution-provenance artifacts, expected-row indexes, direct Coverage-v3 evidence, and all nine delegated report files. Any other value yields `UNSUPPORTED_SCHEMA_VERSION`. A future value requires a new prospective interface revision. An already-frozen authority retains its own schema version rather than being rewritten by this proposal.

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

### 2.1 Closed artifact-role vocabulary

`artifact_role` is exactly one of:

```text
FROZEN_AUTHORITY
FREEZE_MANIFEST
SLOT_LEDGER
CANDIDATE_TRAINING_INVENTORY
CANDIDATE_TRAINING_DATA
EVALUATION_INVENTORY
EVALUATION_DATA
SOURCE_REFERENCE
PROMPT
TARGET
CASE_SET
SCHEDULE
COVERAGE_CONTRACT_V3_INVENTORY
SOURCE_OCCURRENCE_INVENTORY
COMPILER_BINARY
COMPILER_PROVENANCE
COMPILER_WRAPPER
COMPILER_CONFIGURATION
TOKENIZER
CHAT_TEMPLATE
SCHEMA
STATIC_LOOKUP
PRODUCER_ENTRYPOINT
PRODUCER_DEPENDENCY
PRODUCER_CONFIGURATION
PRODUCER_TOOL_MANIFEST
PRODUCER_EXECUTION_PROVENANCE
RUNTIME_EXECUTABLE
RUNTIME_VERSION_CAPTURE
PACKAGE_ENVIRONMENT
CONSUMED_INVENTORY_MANIFEST
EXPECTED_ROW_INDEX
CANDIDATE_INPUT_MANIFEST
COVERAGE_V3_DIRECT_EVIDENCE
DELEGATED_EVIDENCE_REPORT
CANDIDATE_EVIDENCE_MANIFEST
COVERAGE_V3_CLOSURE_RESULT
CONSTRUCTION_PROVENANCE
DIAGNOSTIC_ARTIFACT
```

An artifact that cannot be assigned exactly one role is `UNRESOLVED`. New role strings require a prospective interface revision.

### 2.2 Exact `record_reference` schema

Every logical-record reference has exactly these fields; none may be omitted:

```json
{
  "artifact_id": "ID of a file-level artifact already bound by a manifest",
  "record_id": "stable unique record ID under that artifact's schema",
  "record_role": "one closed role below",
  "content_sha256_utf8": null,
  "content_size_bytes_utf8": null
}
```

`record_role` is exactly one of `TRAINING_EXAMPLE`, `EVALUATION_TASK`, `SOURCE`, `REFERENCE`, `PROMPT`, `TARGET`, `CASE_SET`, `CASE`, `CASE_INPUT`, `EXPECTED_OUTPUT`, `SCHEDULE_ENTRY`, `COVERAGE_CONTRACT`, `CONSUMED_RECORD`, `SERIALIZED_EXAMPLE`, or `DIAGNOSTIC`.

If the referenced logical value is a JSON string, including source, reference, prompt, target, case input, expected output, serialized example, or textual diagnostic, `content_sha256_utf8` is required as lowercase SHA-256 over the exact UTF-8 bytes of the string value without JSON quotes or escaping, and `content_size_bytes_utf8` is the length of those same bytes. If the referenced value is a structured JSON object, array, number, Boolean, or null, both content fields must be explicit JSON `null`; the containing artifact's exact-byte hash supplies its byte identity. A string reference with null content fields, a structured reference with non-null content fields, or omission of either field is malformed. A record reference never replaces file-level artifact closure.

## 3. Stable IDs and expected-row indexes

All candidate, program, task, slot, case, cell, and consumed-record IDs must be unique in their authoritative input inventory. Unknown or duplicate IDs fail before evidence execution.

For each report row set, a separate pre-run `expected_row_index` JSON artifact enumerates the complete ordered list of expected row IDs. These index artifacts are generated without making a scientific classification, are reviewed with the candidate inputs, and are bound by `candidate_input_manifest.json` before evidence producers run. Reports cannot choose, combine, omit, or shrink their own populations.

### 3.1 `expected_row_index` schema version 1

Every index has exactly these top-level fields:

```text
schema_version
phase
candidate_id
index_id
report_type
row_set_id
derivation_name
input_inventory_artifacts
ordered_row_ids
expected_count
ordered_row_id_digest
```

`schema_version` is integer `1`; `phase` is `PHASE_3C_CONF1`; `input_inventory_artifacts` is a nonempty ordered list of exact artifact references; and `ordered_row_ids` is an ordered array of unique nonempty UTF-8 strings. `expected_count` must equal `len(ordered_row_ids)`. `index_id` is unique within the candidate and `row_set_id` must be the exact closed ID assigned in section 7.1. The index artifact uses role `EXPECTED_ROW_INDEX` and is itself bound by exact SHA-256 and size in the candidate input manifest.

### 3.2 Ordered row-ID digest

For ordered row IDs `[r1, r2, ...]`, encode each row independently as the ASCII bytes `ROWSET|`, followed by the row ID's UTF-8 byte length as minimal unsigned decimal ASCII with no leading zero, followed by ASCII `:`, followed by the exact UTF-8 row-ID bytes. Concatenate the framed rows in order with no separator, terminator, or platform newline. For an empty sequence the concatenation is zero bytes. `ordered_row_id_digest` is the lowercase 64-character hexadecimal SHA-256 of those exact concatenated bytes.

The expected-row index stores this digest. Each report independently reconstructs it from row IDs in the report's array order. PASS requires exact digest equality as well as set equality, uniqueness, and count equality.

### 3.3 Shared row-ID framing and formulas

Define `RID(label, [c1, c2, ...])` as ASCII `label` followed, for each component in order, by ASCII `|`, the component's exact UTF-8 byte length as minimal unsigned decimal ASCII, ASCII `:`, and the exact UTF-8 component bytes. Components are never normalized. The fixed label and component arity are defined by the row set below, making the encoding unambiguous.

| Report / row set | Outcome-independent row-ID formula |
|---|---|
| Direct `v3_1_contract_rows` | `RID("V3.1", [program_id])` |
| Direct `v3_2_mapping_rows` | `RID("V3.2", [program_id])` |
| Direct `v3_3_equivalence_rows` | `RID("V3.3", [program_id])` |
| Direct `v3_5_activity_rows` | `RID("V3.5", [training_program_id, canonical_contract_key_id])` |
| Direct `input_domain_class_rows` | `RID("INPUT_DOMAIN_CLASS", [condition_id, domain_id, class_id])` |
| Direct `v3_4_coverage_rows` | `RID("V3.4", [evaluation_task_id, canonical_contract_key_id, required_condition_id])` |
| Direct `v3_6_symmetry_rows`, shared key | `RID("V3.6", ["SHARED_KEY", canonical_contract_key_id, condition_relation_id])` |
| Direct `v3_6_symmetry_rows`, treatment exception | `RID("V3.6", ["TREATMENT_EXCEPTION", canonical_relation_id, "COMPOSITION_ONLY"])` |
| Direct `v3_7_delegation_rows` | `RID("V3.7", ["E5_FULL_SIGNATURE"])` |
| E1 `program_rows` | `RID("E1", [program_type, program_id])` |
| E2 and both E4 `pair_rows` | `RID("PAIR", [candidate_program_id, consumed_id])` |
| E3 scaffold `paired_slot_rows` | `RID("E3SCAFFOLD", [slot_id])` |
| E3 token `example_rows` | `RID("E3TOKEN", [condition_id, example_id])` |
| E3 schedule `cell_rows` | `RID("E3CELL", [seed_id, condition_id])` |
| E3 schedule `exposure_rows` | `RID("E3EXPOSURE", [cell_row_id, epoch_id, exposure_ordinal])` |
| E3 schedule `optimizer_step_rows` | `RID("E3STEP", [cell_row_id, epoch_id, step_ordinal])` |
| E5 `primary_certificates` | `RID("E5PRIMARY", [primary_task_id])` |
| E5 `training_certificates` | `RID("E5TRAINING", [training_program_id])` |
| E5 `comparisons` | `RID("E5", [primary_task_id, training_program_id])` |
| E6 `task_rows` | `RID("E6TASK", [evaluation_task_id])` |
| E6 `pair_distinction_rows` | `RID("E6PAIR", [domain_id, lower_utf8_task_id, higher_utf8_task_id])` |

Canonical key IDs, condition IDs, domain IDs, epoch IDs, ordinals, and relation IDs are taken from bound pre-run contract, schedule, or inventory artifacts. For E6, task IDs are ordered by exact UTF-8 bytes. No expected row ID contains or depends on a V3.2 mapping, mapped occurrence, `PASS`, `FAIL`, `ACTIVE`, `INACTIVE`, collision, similarity, output value, or any other scientific result.

E2 and both E4 reports therefore use the same framed `pair_id`; E5 and E6 retain their previously proposed `E5` and `E6PAIR` semantics under this shared framing convention.

## 4. Non-self-referential candidate manifests

### 4.1 `candidate_input_manifest.json`

This manifest is created and frozen before any candidate-specific scientific evidence producer runs. It has `schema_version: 1` and does not contain E1--E6 report hashes or scientific outcomes. Its closed top-level fields are:

- `schema_version`, `phase`, `candidate_id`, `attempt_id`, `status`;
- `model_execution_authorized`, which must be actual JSON boolean `false`;
- `candidate_root` and `hash_policy`;
- `frozen_authorities`, each with identity, path, recorded hash policy, SHA-256, size, and its authority-declared Git blob or freeze identity, using explicit JSON `null` only when that authority declares neither;
- `slot_ledger` and `candidate_artifacts`;
- `coverage_contract_inventory` and `source_occurrence_inventory`;
- `schedule_manifest`;
- `compiler_identities`;
- `consumed_inventory_manifest`;
- `producer_tool_manifests`;
- `expected_row_indexes`; and
- `construction_provenance`.

`candidate_artifacts` binds every training example, target/reference, prompt, case, evaluation task/reference/case, serialization input, and configuration file required by a report. `coverage_contract_inventory` binds one prospective `CoverageContractV3` for each of the 120 training programs and 64 evaluation tasks using artifact role `COVERAGE_CONTRACT_V3_INVENTORY`. `source_occurrence_inventory`, with role `SOURCE_OCCURRENCE_INVENTORY`, assigns stable, outcome-independent occurrence IDs and source/graph locations to every syntactic source node and edge in the 120 training programs that is eligible under the frozen mapping grammar to appear as nested V3.5 occurrence evidence. It does not decide which occurrences V3.2 maps to a key and does not determine the V3.5 expected-row population. The manifest's own SHA-256 is recorded only by downstream reports and the later evidence manifest.

### 4.2 `candidate_evidence_manifest.json`

This manifest is created only after the direct Coverage-v3 evidence and every required delegated report exist. It has `schema_version: 1`; its closed fields are:

- `schema_version`, `phase`, `candidate_id`, `status`;
- `model_execution_authorized`, again actual JSON boolean `false`;
- an exact artifact reference to `candidate_input_manifest.json`;
- exact artifact references to `coverage_v3_direct_evidence.json` and all nine delegated report files;
- `producer_execution_provenances`, an ordered array of exact `PRODUCER_EXECUTION_PROVENANCE` artifact references covering every distinct execution that generated those ten reports;
- `report_execution_map`, an ordered array with exactly one closed entry per direct or delegated report, each containing only `report_artifact_id`, `report_type`, and `producer_execution_id`;
- `report_status_summary`;
- `overall_audit_state`, one of `ALL_REPORTS_PASS`, `BLOCKED`, or `UNRESOLVED`; and
- `failure_reasons`.

The nine delegated files are E1; E2; the three E3 reports; the two E4 reports; E5; and E6. Every one of those nine files and the direct Coverage-v3 file appears exactly once in `report_execution_map`. Its mapped execution ID and the execution-provenance hash and size in its report envelope must identify one exact artifact in `producer_execution_provenances`. Multiple reports may map to the same execution only when that artifact records the exact single invocation that produced all of them and its `report_types` equals those mapped report types. Unmapped reports, multiply mapped reports, unused provenance artifacts, and absent, stale, mismatched, failed, or unresolved provenance block PASS.

`ALL_REPORTS_PASS` is permitted only when every referenced report declares `PASS` and every mapped execution provenance declares `PASS`; it is not the final Coverage-v3 decision. The binder consumes both manifests, all reports, every execution-provenance artifact, and every transitively referenced read-set artifact, then emits a separate closure result. A later candidate freeze may bind that closure result; this proposal does not create such a freeze.

## 5. Producer-tool identity

Before evidence execution, each distinct report producer has a `producer_tool_manifest.json`, or a separately named manifest with the same schema version 1. One manifest may cover multiple reports only when the identical entrypoint, repository closure, non-code dependency closure, runtime/package closure, rules, and execution configuration produce all of them.

### 5.1 Repository code closure

Each producer-tool manifest contains:

- `repository_commit_sha`, the exact 40-hex Git commit used for execution;
- `repository_root_tree_id`, the exact root tree object of that commit;
- `producer_controlled_pathspecs`, the closed list of repository paths containing producer code and repository configuration under producer control;
- `producer_code_dirty_state`, which must equal `CLEAN_AGAINST_BOUND_COMMIT`;
- `entrypoint`, an artifact reference with role `PRODUCER_ENTRYPOINT`;
- `dependency_access_observer`, an exact `PRODUCER_DEPENDENCY` artifact reference plus its ordered invocation/configuration, identifying the frozen file-access tracer or hermetic boundary used for this producer;
- `explicit_uncommitted_dependencies`, an array of exact artifact references, empty when none; and
- `repository_state_inventory`, an exact diagnostic artifact produced before execution.

At execution, `git rev-parse HEAD` and `git rev-parse HEAD^{tree}` must equal the bound commit and root tree. All tracked files under `producer_controlled_pathspecs` must match that commit byte-for-byte. The state inventory enumerates every modified, staged, deleted, and untracked repository path. A repository-local code or configuration file outside the bound tracked tree may affect execution only when it appears in `explicit_uncommitted_dependencies` before evidence execution. Candidate-input paths are classified separately through `candidate_input_manifest.json`; they are not producer code dependencies. Any other dirty producer-controlled path is `DIRTY_PRODUCER_CODE` and makes tool identity `UNRESOLVED`.

Because the root tree binds every tracked repository file, imported tracked helpers cannot change without changing the bound tree. A producer execution additionally emits an exact `repository_local_read_set` diagnostic artifact from its bound `dependency_access_observer`. Every repository-local file read must classify as one of: bound tracked tree, explicit uncommitted dependency, explicit non-code dependency, or candidate input artifact. An unclassified read is `UNDECLARED_DEPENDENCY`. If the bound observer cannot produce this closed read set, producer identity is `UNRESOLVED`.

### 5.2 Explicit non-code dependency closure

The manifest separately contains ordered exact artifact-reference arrays for `schemas`, `prompts_and_templates`, `static_lookups`, `producer_configurations`, `compiler_wrapper_and_configuration`, and `tokenizer_and_chat_template_configuration`. Empty arrays are explicit. Each repository-local non-code file observed in the read set must appear in the applicable array or be a separately bound candidate input. This rule detects omission mechanically; a free-form assertion that a list is exhaustive cannot produce PASS.

### 5.3 Runtime and package closure

The manifest contains these runtime fields:

- `runtime_executable`, an exact artifact reference with path, exact-byte SHA-256, and size;
- `runtime_version_capture`, an exact artifact reference containing stdout and stderr from the frozen version command;
- parsed runtime name, vendor, version, and architecture, each required to match the captured bytes;
- the package-environment fields defined below, all present even when a mode requires an explicit JSON `null`;
- `execution_command`, represented as an ordered argument array rather than a shell string;
- exact working directory, environment-variable allowlist with values or bound secret identifiers, locale, encoding, timeouts, and resource/output limits; and
- `runtime_closure_status`, which must be `CLOSED`.

`package_environment_mode` is exactly `LOCK_OR_ENVIRONMENT_ARTIFACT` or `INSTALLED_PACKAGE_INVENTORY`. The manifest always contains exactly these six package-environment fields:

```text
package_environment_mode
lock_or_environment_artifact
lock_or_environment_selection
installed_package_inventory_artifact
installed_package_capture_command
installed_package_capture_identity
```

`lock_or_environment_selection`, when non-null, is a closed object containing exactly `method_id`, `ordered_arguments`, `runtime_executable_artifact_id`, `working_directory`, and `environment_inputs`; it mechanically identifies how the bound runtime is constructed or selected from the lock/environment artifact. `installed_package_capture_identity`, when non-null, is a closed object containing exactly `capture_tool_artifact`, `runtime_executable_artifact_id`, and `runtime_version_capture_artifact_id`. `capture_tool_artifact` is an exact reference with role `PRODUCER_DEPENDENCY` or `RUNTIME_EXECUTABLE`; the two runtime IDs must resolve to the exact bound runtime and version-capture artifacts. `installed_package_capture_command`, when non-null, is a nonempty ordered argument array.

For `LOCK_OR_ENVIRONMENT_ARTIFACT`:

- `lock_or_environment_artifact` is a non-null exact `PACKAGE_ENVIRONMENT` artifact reference with SHA-256 and size;
- `lock_or_environment_selection` is the non-null closed object above and must mechanically select or construct the runtime actually used;
- `installed_package_inventory_artifact` is exact JSON `null`;
- `installed_package_capture_command` is exact JSON `null`; and
- `installed_package_capture_identity` is exact JSON `null`.

If the lock/environment artifact and selection method do not adequately determine the environment used for execution, closure is `UNRESOLVED`.

For `INSTALLED_PACKAGE_INVENTORY`:

- `installed_package_inventory_artifact` is a non-null exact `PACKAGE_ENVIRONMENT` artifact reference to the deterministic complete installed-package inventory, with SHA-256 and size;
- `installed_package_capture_command` is the non-null ordered argument array used to capture it;
- `installed_package_capture_identity` is the non-null closed capture-tool/runtime identity above;
- `lock_or_environment_artifact` is either a non-null exact `PACKAGE_ENVIRONMENT` artifact reference when such an artifact governed the runtime or exact JSON `null`; and
- `lock_or_environment_selection` is the non-null closed selection object exactly when `lock_or_environment_artifact` is non-null, and otherwise is exact JSON `null`.

All six named fields are mandatory in both modes. Omission, a third mode, a non-null value where null is required, a null value where an exact artifact or object is required, or a lock artifact/selection nullity mismatch is malformed. No runtime executable, version capture, package-environment field, capture identity, or execution configuration is optional. If neither mode closes the actual runtime, the producer tool identity is `UNRESOLVED`. This mode choice changes reproducibility representation only and cannot change a scientific classification.

### 5.4 Tool-manifest fields and report binding

The complete manifest therefore contains `schema_version`, `producer_id`, `contract_ids`, `report_types`, all section 5.1--5.3 fields, `rule_authorities`, `output_schema_version` fixed to `1`, optional informational `dependency_enumeration_method`, and `unresolved_dependencies`. `unresolved_dependencies` must be an empty array for use. A producer report references the exact tool-manifest SHA-256 and size through the candidate input manifest. A single script hash never stands for repository, runtime, package, or configuration closure.

### 5.5 Post-execution producer provenance

Every distinct producer execution emits one `producer_execution_provenance.json` artifact with role `PRODUCER_EXECUTION_PROVENANCE`. One artifact may cover multiple reports only when the exact single supervised producer invocation generated all of them. The artifact has schema version 1 and exactly these top-level fields:

```text
schema_version
phase
candidate_id
producer_id
execution_id
report_types
candidate_input_manifest
producer_tool_manifest_sha256
producer_tool_manifest_size_bytes
bound_repository_commit_sha
bound_repository_root_tree_id
observed_repository_commit_sha
observed_repository_root_tree_id
actual_execution_arguments
actual_working_directory
actual_environment_configuration
execution_start
execution_end
process_exit_status
repository_state_inventory
repository_local_read_set
dependency_access_observer
runtime_executable
runtime_version_capture
package_environment_identity
compiler_identity_id
dependency_closure_result
failure_reasons
status
```

`schema_version` is integer `1`; `phase` is `PHASE_3C_CONF1`; `report_types` is a nonempty ordered list with no duplicates; and `candidate_input_manifest` is an exact file-level reference to the input manifest used by the execution. The producer-tool-manifest hash and size must match the exact manifest bound by that input manifest. Bound repository identities are copied from that tool manifest; observed identities are captured at execution and must equal them.

`actual_execution_arguments` is the exact ordered argument array; `actual_working_directory` is the exact resolved working directory; and `actual_environment_configuration` is the exact relevant allowlisted environment representation, including values or bound secret identifiers, observed for execution. These must equal the bound execution configuration. `execution_start` and `execution_end` are closed objects containing exactly `event_id` and `observed_at_utc`. Their event IDs are respectively `RID("EXECUTION_EVENT", [execution_id, "START"])` and `RID("EXECUTION_EVENT", [execution_id, "END"])`; each time value is either an RFC 3339 UTC string or explicit JSON `null`. Wall-clock values are provenance only and cannot affect any scientific or interface classification.

`process_exit_status` is a closed object containing exactly `kind`, `exit_code`, and `signal`. For `kind: "EXITED"`, `exit_code` is an integer and `signal` is null. For `kind: "SIGNALED"`, `exit_code` is null and `signal` is a nonempty string. For `kind: "UNRESOLVED"`, both are null and provenance status is `UNRESOLVED`. Other combinations are malformed.

`repository_state_inventory` and `repository_local_read_set` are exact artifact references with role `DIAGNOSTIC_ARTIFACT`, including exact SHA-256 and size. The binder reads and verifies both artifacts. `dependency_access_observer`, `runtime_executable`, and `runtime_version_capture` are exact artifact references and must equal the identities bound by the producer-tool manifest. `package_environment_identity` is a closed object containing exactly `package_environment_mode`, `lock_or_environment_artifact`, and `installed_package_inventory_artifact`; its values and explicit nulls must equal the producer-tool manifest's selected mode. `compiler_identity_id` follows the closed execution-level aggregation rule in section 6 across every report type covered by this execution.

`dependency_closure_result` is exactly `CLOSED`, `FAILED`, or `UNRESOLVED`; `failure_reasons` is an ordered array of interface reason records; and `status` is exactly `PASS`, `FAIL`, or `UNRESOLVED`. PASS requires zero process exit code, matching repository and execution identities, exact read-set and state-inventory closure, `dependency_closure_result: "CLOSED"`, an empty failure-reason list, and all runtime, package, observer, and applicable compiler identities closed. Every mismatch or unclassified repository-local read makes status `FAIL` or `UNRESOLVED` under its reason code.

The bound execution supervisor records the supervised producer subprocess's arguments, observations, read set, and exit status, then serializes execution provenance without any report hash. After those provenance bytes are fixed, the same supervisor invocation finalizes each report envelope with the provenance execution ID, hash, and size. The later evidence manifest binds both. Therefore the dependency order is input manifest and tool manifest → supervised execution/read set → execution provenance → report envelope → evidence manifest; no artifact hashes itself or a downstream artifact.

## 6. Candidate-level compiler identity

`candidate_input_manifest.json` contains one stable `compiler_identity_id` and this closed object:

- compiler JAR artifact reference, including exact JAR SHA-256 and size;
- compiler source/provenance-record artifact reference, including exact SHA-256 and size;
- the upstream compiler commit and source-tree identities recorded by that provenance;
- exact Java executable artifact reference, including the invoked path, exact-byte SHA-256, and size;
- exact `java -version` capture artifact containing stdout and stderr from the invoked executable;
- vendor, version, and architecture parsed from that captured output and required to match it;
- the compiler wrapper/tool artifact identity;
- exact ordered invocation arguments, wrapper/configuration references, working-directory policy, input encoding, output normalization, timeout, output-size limit, locale, and relevant environment configuration; and
- `identity_status`, which must be `CLOSED`.

The existing provenance record `research/manifests/goco_compiler_source.json` currently has exact-byte SHA-256 `67a15aefe1be747c630e887e6e030ae6dcf37ddd64e71b13b0fca7e41587725d` and size 1,289 bytes. It identifies upstream commit `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`. The deterministic JAR currently has SHA-256 `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb` and size 212,005 bytes. A future candidate must bind the then-invoked exact Java executable and its exact version capture in addition to the JAR, provenance, wrapper, and configuration. Failure to bind any component makes compiler identity `UNRESOLVED`; there is no portability or availability exception.

Every report contains `compiler_relevance`, with `status` exactly `REQUIRED` or `NOT_APPLICABLE`, and a closed `reason_code`:

| Report | Relevance rule |
|---|---|
| `coverage_v3_direct_evidence.json` | `REQUIRED`; reason `CONSUMES_PINNED_E1_COMPILER_VALIDATION`. |
| E1 | `REQUIRED`; reason `EXECUTES_PINNED_COMPILER`. |
| E2 | `REQUIRED`; reason `COMPILER_VALID_SOURCE_AND_GRAMMAR_AUTHORITY`. |
| E3 scaffold | `REQUIRED`; reason `PARSED_GOCO_AND_MECHANICAL_OUTPUT_DERIVATION`. |
| E3 token | `NOT_APPLICABLE`; reason `TOKENIZER_ONLY_NO_COMPILER_DEPENDENCY`, unless its implementation invokes compiler-backed parsing, in which case `REQUIRED`. |
| E3 schedule | `NOT_APPLICABLE`; reason `SCHEDULE_ONLY_NO_COMPILER_DEPENDENCY`. |
| E4 reports | `NOT_APPLICABLE`; reason `TEXTUAL_OVERLAP_WITHOUT_COMPILER_DEPENDENCY`, unless the actual producer invokes compiler parsing, in which case `REQUIRED`. |
| E5 | `NOT_APPLICABLE`; reason `CONSUMES_E1_VALIDATED_SOURCE_CONTRACT_MAPPING`, only when it consumes already bound mappings and does not invoke compiler parsing; otherwise `REQUIRED`. |
| E6 | `NOT_APPLICABLE`; reason `CONSUMES_E1_VALIDATED_REFERENCE_CASE_FACTS`, only when it does not compile or execute references; otherwise `REQUIRED`. |

When `REQUIRED`, `compiler_identity_id` must equal the input manifest's closed identity. When `NOT_APPLICABLE`, `compiler_identity_id` must be JSON `null`; omission is invalid.

For `coverage_v3_direct_evidence.json`, this rule is unconditional: `compiler_relevance.status` is `REQUIRED`, `compiler_relevance.reason_code` is `CONSUMES_PINNED_E1_COMPILER_VALIDATION`, and `compiler_identity_id` equals the candidate input manifest's closed compiler identity. Its mapped producer execution provenance carries the same non-null compiler identity ID. The report consumes the pinned E1-validated canonical source and case-output facts required before V3.5 activity; identity closure does not require the direct producer to invoke or rerun the compiler binary.

### 6.1 Execution-level compiler aggregation

For one `producer_execution_provenance.json`, let `R` be the exact nonempty report set obtained by joining its `execution_id` to `candidate_evidence_manifest.json.report_execution_map`. The binder requires that set to equal the provenance `report_types` and the applicable producer-tool manifest `report_types` for that exact invocation. It then validates every mapped report's individual `compiler_relevance` and `compiler_identity_id` rule before deriving the execution-level value.

The execution rule has exactly two states:

- if any report in `R` has `compiler_relevance.status: "REQUIRED"`, provenance `compiler_identity_id` is required non-null and must equal the candidate input manifest's closed compiler identity ID;
- if every report in `R` has `compiler_relevance.status: "NOT_APPLICABLE"`, provenance `compiler_identity_id` is required JSON `null`.

There is no third state. A missing, duplicate, malformed, internally inconsistent, or incomplete report-relevance declaration, a report/provenance compiler-ID mismatch, or a provenance value inconsistent with the derived execution state yields `EXECUTION_COMPILER_RELEVANCE_MISMATCH` and makes the execution `FAIL` or `UNRESOLVED` as appropriate.

An individual `NOT_APPLICABLE` report retains explicit JSON `null` in its own envelope even when another report from the same exact invocation is `REQUIRED` and causes the shared execution provenance to carry the candidate compiler identity. That non-null execution identity does not make the `NOT_APPLICABLE` report compiler-dependent. Mixed-relevance multi-report execution is permitted only when the existing producer-tool rule is also satisfied: the identical bound entrypoint, dependency closure, scientific rules, runtime/package closure, and execution configuration legitimately produce every mapped report type in that single invocation. The aggregation rule does not weaken that condition.

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
producer_execution_id
producer_execution_provenance_sha256
producer_execution_provenance_size_bytes
rule_authorities
compiler_relevance
compiler_identity_id
input_artifacts
row_sets
aggregate
failure_reasons
```

`schema_version` is exactly integer `1`. `phase` is `PHASE_3C_CONF1`. Status is exactly `PASS`, `FAIL`, or `UNRESOLVED`. `producer_execution_id` and the execution-provenance hash and size identify the exact schema-version-1 execution provenance later bound by the evidence manifest. They must match its internal execution ID, exact bytes, candidate ID, producer ID, producer-tool-manifest identity, and report type. A report cannot be `PASS` when that provenance is absent, stale, mismatched, `FAIL`, or `UNRESOLVED`. `rule_authorities` and `input_artifacts` are exact references to entries already bound by the input manifest, not free-form copies. `aggregate` contains only deterministic summaries derived from closed row sets. `failure_reasons` is an ordered list.

`row_sets` is an ordered array. Every entry has exactly these four fields:

```json
{
  "row_set_id": "closed ID from section 7.1",
  "expected_row_index": {
    "artifact_id": "bound EXPECTED_ROW_INDEX artifact ID",
    "index_id": "index_id inside that exact artifact",
    "sha256": "lowercase exact-byte SHA-256",
    "size_bytes": 1,
    "expected_count": 1
  },
  "observed_population": {
    "observed_row_count": 1,
    "unique_row_count": 1,
    "ordered_row_id_digest": "lowercase SHA-256 under section 3.2",
    "missing_ids": [],
    "duplicate_ids": [],
    "unexpected_ids": []
  },
  "rows": []
}
```

The `expected_row_index` and `observed_population` subobjects have exactly the fields shown. The expected-index reference must match the exact artifact bound by the candidate input manifest; `index_id` must equal the artifact contents; and `expected_count` must match the index contents. Every element of `rows` has one `row_id`. `observed_row_count` equals `len(rows)` and `unique_row_count` is the set cardinality of those exact IDs. The ordered digest is reconstructed from `rows` array order using section 3.2. `missing_ids` follows expected-index order; `duplicate_ids` follows first duplicate occurrence order with each duplicated ID listed once; `unexpected_ids` follows first observed occurrence order with each unexpected ID listed once. The three lists are computed, never producer-selected.

Each row set closes independently. Closure requires exact expected-index hash and size, matching report/candidate/row-set identity, exact count and ID set equality, zero duplicate or unexpected IDs, and ordered digest equality. A report can be `PASS` only if its required row-set ID inventory is exact, every required row set closes, all referenced artifacts and identities close, every blocking row is `PASS`, aggregate values reconcile with all row sets, and no `UNRESOLVED` item remains. An omitted, combined, renamed, or extra row set blocks PASS.

### 7.1 Closed row-set IDs by report

| Report | Required row-set IDs |
|---|---|
| `coverage_v3_direct_evidence.json` | `v3_1_contract_rows`, `v3_2_mapping_rows`, `v3_3_equivalence_rows`, `v3_5_activity_rows`, `input_domain_class_rows`, `v3_4_coverage_rows`, `v3_6_symmetry_rows`, `v3_7_delegation_rows` |
| E1 `reference_validation.json` | `program_rows` |
| E2 `ast_v2_overlap_audit.json` | `pair_rows` |
| E3 `scaffold_allowed_difference_audit.json` | `paired_slot_rows` |
| E3 `token_budget_audit.json` | `example_rows` |
| E3 `schedule_audit.json` | `cell_rows`, `exposure_rows`, `optimizer_step_rows` |
| E4 `consumed_similarity_pairs.json` | `pair_rows` |
| E4 `exact_overlap_audit.json` | `pair_rows` |
| E5 `full_signature_novelty_audit.json` | `primary_certificates`, `training_certificates`, `comparisons` |
| E6 `hidden_case_discrimination.json` | `task_rows`, `pair_distinction_rows` |

Although `v3_7_delegation_rows` has expected count one, it remains a plural row-set ID and uses the same closure mechanism.

## 8. Closed interface reason codes

The common interface vocabulary is:

- `MISSING_ROW`
- `DUPLICATE_ROW`
- `UNEXPECTED_ROW`
- `INPUT_ARTIFACT_HASH_MISMATCH`
- `INPUT_ARTIFACT_SIZE_MISMATCH`
- `CANDIDATE_INPUT_MANIFEST_MISMATCH`
- `PRODUCER_TOOL_IDENTITY_MISMATCH`
- `MISSING_PRODUCER_EXECUTION_PROVENANCE`
- `PRODUCER_EXECUTION_PROVENANCE_MISMATCH`
- `REPOSITORY_LOCAL_READ_SET_HASH_MISMATCH`
- `EXECUTION_DEPENDENCY_CLOSURE_FAILURE`
- `INVALID_PACKAGE_ENVIRONMENT_MODE`
- `PACKAGE_ENVIRONMENT_REQUIRED_FIELD_MISSING`
- `PACKAGE_ENVIRONMENT_NULL_RULE_VIOLATION`
- `RULE_IDENTITY_MISMATCH`
- `COMPILER_IDENTITY_MISMATCH`
- `COMPILER_RELEVANCE_INVALID`
- `EXECUTION_COMPILER_RELEVANCE_MISMATCH`
- `MALFORMED_REPORT`
- `UNSUPPORTED_SCHEMA_VERSION`
- `PRODUCER_ROW_FAIL`
- `PRODUCER_ROW_UNRESOLVED`
- `AGGREGATE_INCONSISTENCY`
- `EXPECTED_POPULATION_MISMATCH`
- `MODEL_AUTHORIZATION_NOT_FALSE`
- `FROZEN_AUTHORITY_MISMATCH`
- `REPOSITORY_COMMIT_MISMATCH`
- `REPOSITORY_TREE_MISMATCH`
- `DIRTY_PRODUCER_CODE`
- `UNDECLARED_DEPENDENCY`
- `DEPENDENCY_ACCESS_UNCLOSED`
- `RUNTIME_IDENTITY_MISMATCH`
- `PACKAGE_ENVIRONMENT_MISMATCH`

Each reason record contains `code`, `contract_id`, optional `row_id`, optional `artifact_id`, and `detail_reference`. Producers retain their closed contract-specific scientific reason codes in each affected row. The binder may add interface reasons but may not translate, erase, or replace scientific reasons.

## 9. Coverage-v3 direct evidence

`coverage_v3_direct_evidence.json` is the schema-version-1 output of the future Coverage-v3 contract, parser/mapping, equivalence, activity, and atomic-coverage engine. It uses the common envelope and independent `row_sets`, with `contract_id` `COVERAGE_V3_DIRECT`. It does not duplicate delegated scientific findings. Each row set below has its own separately bound expected-row index.

Its pre-enumerated row sets are:

- `v3_1_contract_rows`: one per 120 training and 64 evaluation contracts, total 184, binding contract provenance, required keys, source/case references, and case obligations;
- `v3_2_mapping_rows`: one per program/reference, total 184, binding the closed parse and complete contract/source node-and-edge mapping, plus any mechanically proved `REFERENCE_ONLY` constructs;
- `v3_3_equivalence_rows`: one per program/reference, total 184, with a complete nested list of every equivalence claim invoked for that record, its source locations, context, and closed V3.3 rule; an empty nested list is a resolved finding only when the complete V3.2 mapping requires no equivalence claim;
- `v3_5_activity_rows`: exactly one row for each `training_program_id × canonical_contract_key_id` over every potential task-essential behavioral or attribute key declared prospectively by each of the 120 training contracts. Its expected index is derived only from those bound contracts and their canonical keys, before V3.2 execution. A V3.2 mapping result cannot add, remove, split, or merge an expected row.
- `input_domain_class_rows`: exactly 14 condition/domain/class obligations: four numeric and three array classes in each of two conditions, with example, case, decoded-value/element, class, and decoder mapping; these rows remain distinct from V3.5 activity rows;
- `v3_4_coverage_rows`: one per evaluation-task-essential atomic key and required condition, with the sole pair-joint relation exception represented as a prospectively marked COMPOSITION-only relation; IDs are enumerated from the 64 evaluation contracts before execution;
- `v3_6_symmetry_rows`: one per required shared key/condition comparison plus one treatment-exception declaration and references to all 60 E3 scaffold rows; and
- `v3_7_delegation_rows`: exactly one row binding the complete E5 report and confirming that no weaker novelty result was reconstructed.

Each gate row has status `PASS`, `FAIL`, or `UNRESOLVED`, scientific reason codes, evidence record references, and source offsets or graph paths where V3 requires them. This direct report is bound by the evidence manifest and traversed by the final binder.

### 9.1 Closed V3.5 evidence variants

Every V3.5 row has these V3.5-specific fields in addition to the common row identity, status, and scientific-reason fields:

```text
training_program_id
canonical_contract_key_id
evidence_kind
behavioral_evidence
value_or_literal_attribute_evidence
output_attribute_evidence
```

`evidence_kind` is exactly `BEHAVIORAL`, `VALUE_OR_LITERAL_ATTRIBUTE`, or `OUTPUT_ATTRIBUTE`. It is derived prospectively from the key type in the bound frozen Coverage-v3 contract ontology: `SEMANTIC_PRIMITIVE`, `API_DECODER` including `INPUT_DOMAIN`, `ATOMIC_OPERATOR`, `GENERIC_CONSTRUCT` when it controls an update, and `ATOMIC_CONTROL_DATAFLOW` map to `BEHAVIORAL`; `VALUE_OR_LITERAL` keys map to `VALUE_OR_LITERAL_ATTRIBUTE`; and `OUTPUT_CATEGORY`, including prospectively required exact sentinels, maps to `OUTPUT_ATTRIBUTE`. A producer cannot choose or relabel the kind from mapping, activity, case, or PASS/FAIL outcomes.

All three evidence-object fields are mandatory. Within the one non-null object, every field listed for that variant is also mandatory; no field may be omitted. Their exact evidence-kind null matrix is:

| `evidence_kind` | `behavioral_evidence` | `value_or_literal_attribute_evidence` | `output_attribute_evidence` |
|---|---|---|---|
| `BEHAVIORAL` | required non-null | required JSON `null` | required JSON `null` |
| `VALUE_OR_LITERAL_ATTRIBUTE` | required JSON `null` | required non-null | required JSON `null` |
| `OUTPUT_ATTRIBUTE` | required JSON `null` | required JSON `null` | required non-null |

Omission, an unknown kind, more or fewer than one non-null evidence object, or a kind/object mismatch is malformed.

Finding and interface status remain separate. `ACTIVE`, `INACTIVE`, `COVERED`, and `NOT_COVERED` are resolved scientific findings and may have row `status: "PASS"` when their required evidence is complete and internally valid; `UNRESOLVED` requires row `status: "UNRESOLVED"`. An `INACTIVE` or `NOT_COVERED` row cannot serve as positive V3.4 coverage evidence, but does not alone preempt V3.4's condition-level decision about whether another training example supplies the required active/covered witness.

#### 9.1.1 `BEHAVIORAL`

`behavioral_evidence` has exactly `occurrence_evidence`, `connected_executed_paths`, `normal_run_output_events`, `intervention_ordering_rule_reference`, `ordered_intervention_attempts`, `selected_active_witness`, and `activity_finding`.

`occurrence_evidence` has exactly `source_occurrence_inventory_reference`, `mapping_cardinality`, `mapped_occurrence_count`, `mapped_occurrences`, and `joint_intervention_occurrence_ids`. `mapping_cardinality` is exactly `ZERO`, `ONE`, or `MULTIPLE` and reconciles with the count. `mapped_occurrences` is the complete list of every syntactic occurrence that V3.2 maps to the row's canonical key, ordered by the pre-bound source-occurrence inventory's frozen occurrence order. Each nested occurrence contains exactly `occurrence_id`, `source_location`, `graph_location`, `v3_2_mapping_reference`, and `affected_by_joint_intervention`. Occurrence IDs and locations resolve to the pre-bound `SOURCE_OCCURRENCE_INVENTORY`; mapping references resolve to the closed V3.2 row.

`connected_executed_paths`, `normal_run_output_events`, and `ordered_intervention_attempts` are required non-null ordered arrays, even when empty. The path and event entries bind the connected executed source-to-contract path, frozen case, displayed-accumulator reachability, and normal-run output event. Intervention attempts follow the frozen class-specific ordering and bind their case, intervention, normal output, counterfactual output, and whether the final output changed. `intervention_ordering_rule_reference` is always required non-null.

`joint_intervention_occurrence_ids` equals the complete ordered mapped-occurrence ID list, and every nested `affected_by_joint_intervention` is true. Every attempt therefore intervenes over all mapped instances of that capability in the example together. `selected_active_witness` is required non-null exactly when `activity_finding` is `ACTIVE`; it contains exactly `normal_event_witness_case_id`, `selected_intervention`, `normal_output`, and `counterfactual_output`, chosen under the frozen case/intervention order. It is required JSON `null` when `activity_finding` is `INACTIVE` or `UNRESOLVED`. Empty or incomplete evidence for those findings remains represented in the non-null arrays and must carry the frozen scientific reason codes. `activity_finding` is exactly `ACTIVE`, `INACTIVE`, or `UNRESOLVED`.

#### 9.1.2 `VALUE_OR_LITERAL_ATTRIBUTE`

No independent mutation, selected intervention, or attribute-specific counterfactual is performed. `value_or_literal_attribute_evidence` has exactly `canonical_attribute_key_id`, `attribute_subtype`, `attribute_parent_kind`, `exact_value_role`, `exact_required_lexeme`, `computed_integer`, `semantic_role`, `mapped_parent_behavioral_key_id`, `parent_v3_5_activity_row_reference`, `active_behavioral_parent_evidence`, `initial_accumulator_evidence`, and `coverage_finding`.

`attribute_parent_kind` is exactly `ACTIVE_BEHAVIORAL_PARENT` or `INITIAL_ACCUMULATOR`. It is derived prospectively from the frozen `CoverageContractV3` key attachment and semantic role. Mapping, parent activity, case results, and PASS/FAIL outcomes cannot select or change it. All parent fields are mandatory, with this exact null matrix:

| `attribute_parent_kind` | `mapped_parent_behavioral_key_id` | `parent_v3_5_activity_row_reference` | `active_behavioral_parent_evidence` | `initial_accumulator_evidence` |
|---|---|---|---|---|
| `ACTIVE_BEHAVIORAL_PARENT` | required non-null | required non-null | required non-null | required JSON `null` |
| `INITIAL_ACCUMULATOR` | required JSON `null` | required JSON `null` | required JSON `null` | required non-null |

Omission, an unknown parent kind, a kind/field mismatch, or switching to `INITIAL_ACCUMULATOR` because a declared behavioral parent is inactive or unresolved is malformed.

For `ACTIVE_BEHAVIORAL_PARENT`, `active_behavioral_parent_evidence` has exactly `source_location`, `graph_location`, `frozen_witness_case_id`, `parent_path_execution_evidence`, and `mapped_active_expression_reference`. For `coverage_finding: "COVERED"`, source/graph locations, witness case, and path-execution evidence are required non-null and must prove that the referenced parent V3.5 row is `ACTIVE` and that its mapped path executes on that case. `mapped_active_expression_reference` is required non-null for a covered `LITERAL_TOKEN` and required JSON `null` for `COMPUTED_VALUE`. For `NOT_COVERED` or `UNRESOLVED`, unavailable location, case, path, or literal-expression evidence is explicit JSON `null`, available evidence is retained, and scientific reasons identify each failed requirement.

For `INITIAL_ACCUMULATOR`, no behavioral parent is invented. `initial_accumulator_evidence` has exactly `initial_accumulator_contract_role_reference`, `mapped_source_initialization_reference`, `source_location`, `graph_location`, `initialization_value_role`, `frozen_witness_case_id`, `initialization_execution_evidence`, `displayed_accumulator_membership_evidence`, `mapped_initialization_expression_reference`, `computed_integer`, `semantic_role`, `exact_required_lexeme`, `coverage_finding`, `status`, and `scientific_reason_codes`. `initial_accumulator_contract_role_reference` and `initialization_value_role` are always required non-null because they are prospective contract facts. For `coverage_finding: "COVERED"`, the mapped initialization reference, locations, witness case, execution evidence, displayed-accumulator membership evidence, and mapped initialization expression are all required non-null and must prove that initialization executes on the frozen case and belongs to the mapped displayed-accumulator computation. For `NOT_COVERED` or `UNRESOLVED`, unavailable non-contract evidence fields are explicit JSON `null`, available evidence is retained, and the nested finding, status, and reasons exactly equal the enclosing attribute finding and row status/reasons.

The enclosing `coverage_finding` is exactly `COVERED`, `NOT_COVERED`, or `UNRESOLVED` and follows the resolved-finding/status rule above.

The subtype null rules are closed:

| `attribute_subtype` | `exact_value_role` | `computed_integer` | `semantic_role` | `exact_required_lexeme` |
|---|---|---|---|---|
| `COMPUTED_VALUE` | required non-null | required integer | required non-null | required JSON `null` |
| `LITERAL_TOKEN` | required JSON `null` | required JSON `null` | required JSON `null` | required non-null exact lexeme |

For `COMPUTED_VALUE`, the enclosing `computed_integer`, `semantic_role`, and `exact_value_role` retain the exact computed value/role requirement. For `LITERAL_TOKEN`, the enclosing `exact_required_lexeme` retains the exact syntax-essential lexeme requirement. Under `ACTIVE_BEHAVIORAL_PARENT`, those values must occur on the active mapped parent path or expression. Under `INITIAL_ACCUMULATOR`, the nested `computed_integer`, `semantic_role`, and `exact_required_lexeme` follow the same subtype null rules, equal their enclosing counterparts, and are evidenced by `mapped_initialization_expression_reference`, which is required non-null for `COVERED`. A failed parent path, initialization path, witness execution, displayed-accumulator membership, value/role, or lexeme requirement cannot yield `COVERED`. The row's `behavioral_evidence` remains explicit null for both parent kinds, and neither parent kind receives an intervention or independent counterfactual.

#### 9.1.3 `OUTPUT_ATTRIBUTE`

No intervention or active-parent mutation is performed. `output_attribute_evidence` has exactly `canonical_output_key_id`, `output_requirement_kind`, `output_category`, `exact_sentinel`, `evaluated_expected_output_cases`, `selected_output_witness`, and `coverage_finding`.

`output_requirement_kind` is exactly `CATEGORY` or `EXACT_SENTINEL`. For `CATEGORY`, `output_category` is required non-null and exactly one of `OUTPUT_ZERO`, `OUTPUT_POSITIVE`, `OUTPUT_NEGATIVE`, or `OUTPUT_MULTIDIGIT`, while `exact_sentinel` is required JSON `null`. For `EXACT_SENTINEL`, `output_category` is required JSON `null` and `exact_sentinel` is required non-null.

`evaluated_expected_output_cases` is a required non-null ordered array. Every entry contains exactly `frozen_case_id`, `expected_output_reference`, `expected_output_value`, and `mechanical_match`, where `mechanical_match` is `MATCH`, `NO_MATCH`, or `UNRESOLVED` under the frozen category or exact-sentinel definition. `selected_output_witness` is required non-null exactly when `coverage_finding` is `COVERED`; it contains exactly those same four fields, has `mechanical_match: "MATCH"`, and identifies an actual expected-output case satisfying the category or exact sentinel. It is required JSON `null` for `NOT_COVERED` or `UNRESOLVED`. `coverage_finding` is exactly `COVERED`, `NOT_COVERED`, or `UNRESOLVED` and follows the resolved-finding/status rule above. Both non-output evidence objects remain explicit null.

#### 9.1.4 Population and INPUT_DOMAIN preservation

The expected V3.5 row formula remains exactly `RID("V3.5", [training_program_id, canonical_contract_key_id])`. The expected population remains the Cartesian enumeration of each of the 120 prospective training contracts with its prospectively declared canonical task-essential keys. Behavioral and attribute rows are all retained. No V3.2 mapping, activity finding, attribute finding, or output case result can create or remove a row; a zero or invalid mapping resolves under frozen V3.2/V3.5 rules inside the still-present row.

`INPUT_DOMAIN:<domain/range>` remains an `API_DECODER` key and therefore has `evidence_kind: "BEHAVIORAL"`. It requires the connected decoder path, normal-run output event, capability-level joint intervention, and output-changing decoder counterfactual prescribed by frozen V3.5. Its separate 14 `input_domain_class_rows` obligations remain unchanged. The class witness and decoder-activity witness may use different frozen cases exactly as allowed by the frozen INPUT_DOMAIN amendment.

### 9.2 Frozen-V3.5 compatibility check

| Frozen V3.5 rule | Interface representation | Compatibility |
|---|---|---|
| Behavioral keys require a connected executed path, normal-run output event, and capability-level output-changing intervention over all mapped instances. | Non-null `behavioral_evidence` records complete mapped occurrences, connected paths, events, ordered joint attempts, and the selected active witness. | Exact representation; no strengthening or weakening. |
| `VALUE_OR_LITERAL` attached to a semantic predicate/operator inherits coverage from an active parent path and requires exact value/role or exact syntax-essential lexeme on an executing frozen case. | `ACTIVE_BEHAVIORAL_PARENT` binds the non-null parent key/row and executing path evidence; initial-accumulator evidence is null. | Exact representation; active-parent requirements are unchanged. |
| `VALUE_OR_LITERAL` may instead attach to the initial accumulator. | `INITIAL_ACCUMULATOR` requires null behavioral-parent IDs and binds the mapped initialization, execution, displayed-accumulator membership, and exact subtype evidence. | Exact representation without invented behavioral activity. |
| Neither value/literal parent kind receives a separate mutation. | Both parent variants live under attribute evidence while row `behavioral_evidence` is null and no counterfactual field exists. | Exact representation; no independent attribute mutation added. |
| `OUTPUT_CATEGORY` and exact sentinels require actual expected-output cases. | Non-null output evidence mechanically evaluates bound expected-output cases and selects an actual matching witness; behavioral and value/literal evidence are null. | Exact representation; no intervention or source-only evidence added. |
| `INPUT_DOMAIN` is behavioral `API_DECODER`; its V3.4 class checks are separate and conjunctive. | `INPUT_DOMAIN` is forced to `BEHAVIORAL`, while the existing 14 class rows remain separate and may use different frozen cases. | Exact representation; no strengthening or weakening. |

## 10. E1 — compiler/reference validation

Required file: `reference_validation.json`.

The report has only the `program_rows` row set and its separate expected index contains exactly 184 program rows: 60 ISOLATED training targets, 60 COMPOSITION training targets, and 64 evaluation references. Program IDs come from the candidate's frozen inventories. Row IDs use the section 3.3 E1 formula.

Each program row contains:

- `row_id`, `program_id`, `program_type`, condition or evaluation group;
- source/reference and case-set `record_reference` objects;
- exactly five expected case IDs, in frozen order;
- compile result, phase, and diagnostic artifact/reference;
- exactly five nested case outcomes with case ID, input reference, expected output, actual normalized output, execution phase, and status;
- compiler identity ID;
- row status and scientific reason codes.

The nested population is exactly 920 case outcomes. Each program row records its exact five expected case IDs from the input manifest; the binder requires the nested outcome IDs to equal that ordered list with no duplicates or extras. E1 `PASS` requires the closed `program_rows` set, exactly five unique expected cases per row, all 920 compile/semantic outcomes `PASS`, compiler closure, and source/case hash closure. The binder verifies these facts and the producer's statuses; it does not invoke or emulate the compiler.

## 11. E2 — AST-v2 structural overlap

Required file: `ast_v2_overlap_audit.json`.

The report has only the `pair_rows` row set. `consumed_inventory_manifest.json` prospectively enumerates the real permitted consumed population. If it has `N` records, the separate E2 pair index has `184 × N` rows, absent a separately frozen exclusion rule. No historical value of `N` is adopted here.

Each row contains shared `pair_id`, candidate program ID and source record reference, consumed ID and source/template record reference, legacy coarse-equality flag, canonical-tree identity/digest for both sides, exact frozen AST-v2 classification (`PROHIBITED_STRUCTURAL_TEMPLATE_REUSE`, `COARSE_AST_EQUALITY_ONLY`, or `STRUCTURALLY_DISTINCT`), adjudication status, and scientific reason codes. Prohibited reuse is `FAIL`; coarse-only and distinct are resolved results whose row status is `PASS`; parse, validity, or classification uncertainty is `UNRESOLVED`. Missing or unadjudicated pairs block.

## 12. E3 — matched scaffold, tokens, and schedule

### 12.1 `scaffold_allowed_difference_audit.json`

The report has only `paired_slot_rows`, with a separate expected index of exactly 60 rows, one for every frozen `training_paired_slots` ID. Each row binds the slot ID; ISOLATED and COMPOSITION program IDs; source, prompt, and case-set references; the five ordered paired case IDs and exact inputs; marked treatment-expression and treatment-description classifications; every protected-field comparison required by the paired-scaffold authority; mechanical expected-output derivations for both conditions on all five inputs; feature counts; row status; and scientific reasons.

Only the frozen treatment expression and treatment description may be `INTENDED_TREATMENT_DIFFERENCE`; only mechanically derived outputs and treatment serialization may be `UNAVOIDABLE_SEMANTIC_CONSEQUENCE`. Every other field is `MATCHED` or the row fails.

### 12.2 `token_budget_audit.json`

The report has only `example_rows`, with a separate expected index of exactly 120 model-facing example rows. Each row includes example ID, condition, exact prompt/input/target record references, tokenizer and chat-template identities, prompt/input token count, supervised target-token count, full serialized-token count, truncation status, applicable 320-token check, row status, and reasons.

The aggregate deterministically reports each condition's example and token totals, maximum sequence length, supervised-token relative difference, full-token relative difference, and the frozen 2%/5%/320 limits. All rows and aggregates must pass.

### 12.3 `schedule_audit.json`

The report has three independent row sets, each with its own expected index. The frozen design has five paired seeds and two conditions, hence 10 cell rows. Each cell has 60 examples over three epochs, hence 180 exposure rows and 24 optimizer-step rows. The full expected population is therefore:

- 10 `cell_rows`;
- 1,800 `exposure_rows` (180 per cell); and
- 240 `optimizer_step_rows` (24 per cell).

Exact IDs and ordering derive from the frozen schedule manifest bound in the candidate input manifest. Cell rows bind seed, condition, example inventory, epochs, microbatch, accumulation, exposures, and step totals. Exposure rows bind cell, epoch, within-epoch ordinal, example ID, and the step/accumulation group receiving that exposure. Optimizer-step rows bind cell, epoch, step ordinal, contributing exposure IDs, accumulation cardinality, and final partial-step handling prescribed by the schedule. The producer reconciles membership, duplicates, omissions, 180 exposures, 24 steps, and paired schedule rules without creating candidate-specific exceptions.

All three E3 reports must independently close and declare `PASS`.

## 13. E4 — consumed-suite overlap

Required files are `consumed_similarity_pairs.json` and `exact_overlap_audit.json`. Each has only `pair_rows` and its own exact expected-index artifact; the two indexes must contain the same ordered IDs and digest. Both reference the identical frozen consumed-inventory manifest. If that inventory has `N` records, each file has exactly `184 × N` pair rows and uses the same shared `pair_id`.

`consumed_similarity_pairs.json` contains candidate and consumed identities, every prespecified descriptive metric, normalized-code and coarse/structural fields where delegated to it, and deterministic nearest-neighbor summaries. Complete enumeration is required; descriptive status does not create a new scientific threshold.

`exact_overlap_audit.json` owns the blocking exact prompt, source/reference/target, normalized-source, and full-template decisions required by the frozen protocol. Each row records the applicable compared fields, exact flags, normalized/full-template result, final prohibited/allowed/unresolved classification, status, and scientific reasons.

The binder reconciles pair IDs across both files exactly. It does not recompute a textual-overlap decision or turn a descriptive similarity value into a veto.

## 14. E5 — full-signature novelty

Required file: `full_signature_novelty_audit.json`.

### 14.1 `primary_certificates`

The `primary_certificates` row set has its own expected index with exactly 32 rows, one per primary evaluation task. Rows contain task ID; task-contract reference; domain; role map and role count `k`; typed complete-graph identity; the complete ordered `2^k` contribution vector; aggregation/state recurrence; fixed initialization or fully represented initialization/state; source-to-contract completeness references; hidden/unrepresented-state checks; certificate status; and scientific reason codes. The field `k` here is role cardinality, distinct from any training accumulator offset.

### 14.2 `training_certificates`

The `training_certificates` row set has its own expected index with exactly 120 rows, one per training program, encoding the same completeness fields needed for comparison. They prevent 3,840 comparisons from silently using an uncertified aggregate training signature.

### 14.3 `comparisons`

The `comparisons` row set has its own expected index with exactly 32 primary tasks × 120 training programs = 3,840 rows under the current frozen design. Each row binds primary task ID, training program ID, both domains, role cardinalities, role-bijection enumeration/status, typed-graph comparison, graph-isomorphism result, complete semantic contribution/output-signature comparison, semantic-equality result, local-pair-motif diagnostic, final result (`COLLISION`, `NONMATCH`, or `UNRESOLVED`), row status, and reasons.

Graph isomorphism or complete semantic-signature equality independently yields `COLLISION` and row `FAIL`. A frozen V3.7 fewer-role motif comparison records a resolved `NONMATCH`, not missing or unresolved. Any incomplete certificate, unrepresented output-affecting state, undecidable role bijection, or unresolved graph/semantic comparison is `UNRESOLVED`. E5 `PASS` requires all 32 primary certificates, all 120 training certificates, all 3,840 comparison rows, and no collision or unresolved result. The binder verifies closure and status only; it does not rebuild signatures.

## 15. E6 — hidden-case discrimination

Required file: `hidden_case_discrimination.json` with two blocking row sets.

`task_rows` has its own expected index and contains exactly 64 rows, one per evaluation slot. Each binds task ID, contract and case-set references, exactly five nested case outcomes, and every prospectively declared task-essential behavior witness. The nested case population is exactly 320. Each task row records its exact five expected case IDs; nested outcome IDs must equal that ordered list with no duplicates or extras. Each witness identifies the behavior obligation, case IDs, source/contract path, observed behavior, status, and scientific reasons.

`pair_distinction_rows` has its own expected index and contains every unordered pair among the 16 primary slots separately within each domain: 120 numeric rows and 120 array rows, total 240. Each row contains domain, task A, task B, case/input witness references, the mechanically observed output or contribution difference, status, and reasons. Cross-domain pairs are not required by the frozen domain-specific 120/120 rule.

E6 `PASS` requires complete 64-task, 320-case, and 240-pair closure, all declared behavior obligations witnessed, and all required within-domain pairs distinguished. An aggregate `64/64` or `240/240` without the rows cannot pass.

## 16. Consumed-inventory boundary

`consumed_inventory_manifest.json` has exact integer `schema_version: 1` and closed fields `schema_version`, `status`, `inventory_id`, `authority`, `inclusion_rule`, `exclusion_rules`, `records`, `record_count`, `source_artifacts`, `hash_policy`, and `failure_reasons`.

Every record contains stable `consumed_id`, origin/suite, record type, source/template and prompt/target record references where applicable, exact file/content hashes and sizes, and the authority justifying inclusion. Duplicate semantic IDs or an unbound source artifact fail. The manifest must be independently reviewed and frozen before Attempt-004 construction. This proposal defines its format and completeness proof but does not choose its real contents and does not freeze the historical 420 records or 77,280 pair count. Later synthetic implementation tests may use a small manifest explicitly labeled `SYNTHETIC_FIXTURE_ONLY`.

## 17. Final binder and `ALL_GATES_PASS`

The final binder may emit `PASS` only when:

1. `candidate_input_manifest.json` closes and every frozen authority matches;
2. `model_execution_authorized` is actual boolean `false` in both candidate manifests;
3. every V3.1--V3.7 direct-evidence row population closes and every row passes;
4. all nine E1--E6 report files close against their exact expected indexes and declare `PASS`;
5. `candidate_evidence_manifest.json` binds the exact input manifest, direct report, all report hashes and sizes, every required producer-execution-provenance artifact, and exactly one execution mapping per report;
6. every mapped execution provenance passes and transitively closes its exact repository-state inventory and repository-local read-set hashes and sizes;
7. every compiler-relevance, producer-tool identity, runtime identity, and package-environment mode closes;
8. no row, report, provenance, manifest, or dependency is `UNRESOLVED`; and
9. aggregate summaries reconcile exactly with their rows.

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

1. An initial-accumulator value/literal row has null behavioral-parent IDs and non-null initialization evidence, so it does not require a fake behavioral parent.
2. An `ACTIVE_BEHAVIORAL_PARENT` row retains non-null parent key/row identity and the frozen active-parent, executing-path witness rule.
3. Neither attribute-parent kind receives an independent mutation or counterfactual, and row `behavioral_evidence` remains null.
4. Both parent kinds retain the exact `COMPUTED_VALUE` integer/semantic-role and `LITERAL_TOKEN` exact-lexeme requirements.
5. `attribute_parent_kind` derives prospectively from the frozen contract key/role and cannot change from observed activity or outcomes.
6. The approved V3.5 row identity and contract-key-derived expected population are unchanged.
7. An execution covering only `NOT_APPLICABLE` reports has a null provenance compiler identity.
8. An execution covering any `REQUIRED` report has the candidate compiler identity in provenance.
9. A `NOT_APPLICABLE` report can share an execution with `REQUIRED` reports while retaining null in its own envelope; this does not make it compiler-dependent.
10. The binder independently verifies report-level relevance/null rules and the deterministic execution-level aggregate.
11. These interface changes do not alter scientific PASS conditions, thresholds, populations, budgets, tasks, cases, seeds, graphs, treatment rules, Coverage-v3 gates, the 17-gate trace, consumed-inventory boundary, or authorization rules.

The earlier interface checks remain satisfied: every independent row set has a separate expected index and closure; schema version remains exactly 1; artifact and record-reference vocabularies remain closed; ordered row-ID digest encoding and every row-ID formula, including the approved two-component V3.5 formula, are unchanged by this repair; producer execution provenance and hash ordering remain acyclic; package-environment modes remain closed; compiler runtime identity remains mandatory; historical reports remain descriptive rather than authoritative; the real consumed population remains unfrozen and neither 420 nor 77,280 is adopted; E5 still requires 32 primary certificates, 120 training certificates, and 3,840 comparisons; E6 still requires 64 task rows, 320 nested cases, and 240 pair rows; and unknown, missing, duplicate, stale, mismatched, failed, or unresolved evidence blocks.

Remaining work is deliberately outside this proposal: independent review and freeze of this interface; independent review and freeze of the real consumed-inventory contents; implementation and preregistered scientific fixtures; prospective candidate construction; candidate-specific producer-tool manifests and expected indexes; candidate evidence production; and any separate authorization decision. None is implied by this document.
