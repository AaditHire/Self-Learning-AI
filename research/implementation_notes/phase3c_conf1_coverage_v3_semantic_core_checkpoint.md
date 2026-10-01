# Coverage-v3 core semantic repair — partial, stopped checkpoint

Checkpoint date: 2026-10-01, Asia/Calcutta.

This is development implementation evidence, not a frozen authority, scientific
validation, candidate acceptance, expected-row index, or authorization. The
requested full semantic closure has **not** been completed. One development
gate passes; seven remain UNRESOLVED. No V3.5 population derivation or recount
was performed, including no new diagnostic recount. Historical `8668` remains
non-authoritative and is not evidence for the changed implementation.

`V3_5_POPULATION_UNRESOLVED`

## Repository boundary and commits

Starting HEAD was independently verified as
`41468f4c831159b5658f14efd87c3ee9407922e8`, branch `main`. The initial
`git status --porcelain` was empty. No applicable `AGENTS.md` was found.
The current core-engine-repair attachment, not earlier superseded requests,
defines this pass. No worktree, branch, sub-agent, push, or external task was
created.

One dedicated checkpoint commit:
`Repair CONF1 v3 semantic foundations and record remaining closure gates`.
Ending HEAD is the commit containing this report. Its exact concrete SHA and
actual post-commit worktree status are reported in the final handoff. The SHA
is recoverable without attempting an impossible self-hash in this file:

```powershell
git log -1 --format=%H -- research/implementation_notes/phase3c_conf1_coverage_v3_semantic_core_checkpoint.md
git status --porcelain
```

The required final worktree state is clean; it is checked independently after
the commit, not inferred from staging. There are no intermediate commits in
this pass.

Exact changed-file inventory, 15 files:

- `src/self_learning_ai/conf1_v3/core_ir.py`
- `src/self_learning_ai/conf1_v3/semantic_ir.py`
- `src/self_learning_ai/conf1_v3/contract_ir.py`
- `src/self_learning_ai/conf1_v3/coverage.py`
- `scripts/check_conf1_v3_semantic_core.py`
- `tests/sem900_development_inputs.py`
- `tests/sem900_runtime.py`
- `tests/test_conf1_v3_semantic_core.py`
- `research/implementation_notes/coverage_v3_semantic_core/protected_input_integrity.json`
- `research/implementation_notes/coverage_v3_semantic_core/disposable_overlap.json`
- `research/implementation_notes/coverage_v3_semantic_core/primitive_indicator_extraction.json`
- `research/implementation_notes/coverage_v3_semantic_core/state_essentiality_traces.json`
- `research/implementation_notes/coverage_v3_semantic_core/attribute_output_attachments.json`
- `research/implementation_notes/coverage_v3_semantic_core/semantic_gate_evidence.json`
- this report.

The preceding checkpoint report, its four diagnostic artifacts, its producer,
the population guard, all frozen protocols, preregistration and project-state
documents remain unchanged.

## Preflight and protected identities

Before editing, the ten upstream frozen authorities were checked against their
declared-policy SHA-256, exact byte sizes, worktree Git clean-filter blobs and
committed Git blobs. Four approved normative regions were independently
compared with their actual approved commits. All match. The same integrity
checks are repeated by the new producer before any disposable execution and
again before commit.

The delegated interface retains exact SHA-256
`9c684eaf6b0099080ddf907630b0a2f8e176e3a882b67875d82f07bd82d64dc5`,
size 76081 and Git blob `1b6d4d1a825bf9e9d288ca9c3815d1a8e7c78d1a`.
Its freeze manifest retains exact SHA-256
`bd7a7fc6862ce049c1fdf363f763e1a3a17808132291b9064e3c6f26fb720948`.

| Approved normative region | Bytes | SHA-256 |
|---|---:|---|
| Delegated interface, exact | 74717 | `26c642e17bb5218727c0cd09f370eaf1ac6c4de35006fa9801d701ece81cf16d` |
| Coverage-v3, LF-normalized | 29178 | `884a8ac3f859268e16dfa0d8f0d477211c7a273fca58666c7eba018265d8c15a` |
| Paired scaffold, LF-normalized | 12217 | `5aa404949a8cc580b9ca3ff4aff7325195e172a7cfa82c69317280597c73b25c` |
| INPUT_DOMAIN amendment, LF-normalized | 14669 | `b9dc3d6ca22778ab0b3e734270fb20a00b4d88e0602f24fe77b2112335df8167` |

The predicate recognizer additionally verifies the frozen slot ledger's
LF-normalized SHA-256
`83436eecda3affe813b785e868e3f8936fa59afc35ded0eb6a54290edb41dc88`
before reading its eight predicate definitions. It does not select ontology
from test results, IDs, condition or expected labels.

All 15 historical preregistration files match baseline Git blobs at
`b44d1c73de1be47b541f76d67c88541a5d90f3fa`. Their exact working-byte hashes
and sizes are separately bound in this pass's integrity snapshot and remain
byte-identical on subsequent checks. Expected-label files receive only generic
byte-integrity hashing: their contents are not inspected or JSON-parsed.
No sealed holdout is read.

Only `verify_protected_inputs()` is reused from the previous checkpoint's
producer. Its population audit and historical diagnostic regeneration are
not invoked: its old zero-primitive assertions describe the previous engine,
not this checkpoint.

## Reproduced boundary and implemented repairs

The pre-repair defects were missing semantic primitive/indicator relations,
all-writer state overapproximation, leaf-only computed-value attachment,
unsupported exact output sentinels and absent source-flow Boolean proofs.
Investigation and execution used disposable examples, not preregistered
scientific cases. Negative intervention tests also reproduced loss of the
execution-budget error identity; the original SchemaError is now preserved.

### Primitive and indicator extraction

Parsed, typed expression trees are compared with the frozen ledger catalog.
All eight identities are recognized: `odd_index`, `residue_two`,
`divisor_index`, `first_half`, `negative_value`, `even_value`,
`large_magnitude`, and `value_exceeds_index`. Source operators remain distinct;
in particular `values[i]<=0` does not become the frozen `<0` primitive.
The development artifact contains 31 individually identified primitive
occurrences across 16 executed disposable programs, with identity, authority,
source span, AST node, semantic occurrence, typed operand/result ports,
control context, incident state/data relations and output reachability.
Repeated occurrences are retained and jointly intervened upon.

Semantic input edges now affect the actual comparison value under typed
intervention, rather than merely adding dependency tags. The focused test
forces an odd-predicate input edge to zero and observes the changed output.

Indicator range is derived from explicit initialization and every syntactic
write. Predicate-to-indicator relations are source-mapped. Accepted local-flow
proofs additionally require a same-iteration unconditional reset, one
conditional positive definition, read-after-write order and exact reaching
definitions. Range alone is not truth equivalence. Ambiguous definitions,
caller indicator sets, incomplete alpha maps and cross-loop contexts reject.
Complete Boolean-alternative source mapping is still absent; the indicator
completion gate therefore remains UNRESOLVED.

### State graph and essentiality

All-writer edges are replaced by structured reaching definitions: sequential
definition kill, conditional union and a finite loop-header fixed point.
Forward index initialization and steps have explicit typed identities.
Assignments do not incorrectly inherit overwritten state. Runtime reads and
accumulator updates must resolve their actual last writer to an exact static
state edge; missing/ambiguous edges fail closed. Reverse domain traversal
remains supported, with an exact terminal decrement and immutable input bound.

Normal/compiler/reference agreement is established for 80 new disposable
cases covering sum-per-item, prefix prior-state, two-pass product, reverse
iteration, repeated checks/updates, computed initial values, arrays and Boolean
flow examples. Prefix Q reads the earlier P count, not a later current-item
write. Both two-pass registers reach the displayed product. Its final product
event is specifically derived from the parsed displayed product; generic
nonzero offset output is not used to make zero-delta updates eligible.

Saved behavioral evidence has 64 findings: 48 ACTIVE and 16 UNRESOLVED. Each
attempt binds the same case, complete mapped occurrence set, typed neutral,
actual normal output and actual counterfactual output. Eighteen stateful
witnesses are re-executed and serialize actual counterfactual state traces
and final-output dependencies. Compiler output observations are retained and
checked against independently recomputed normal IR outputs. Mutation of the
runtime primitive mapping cannot establish activity.

This is not all-class essentiality closure. The artifact explicitly inventories
656 untested behavioral key obligations in these toys. Force-true bounded-loop
intervention removes the sole exit in this closed subset, which has no
break/return; it is UNRESOLVED, not a fabricated terminating output. The
all-writer repair and case traces do not supply a complete frozen-family
required-computation/recurrence certificate or a closed total/pure
REFERENCE_ONLY catalog. These missing implementation proofs block closure;
they do not establish a contradiction in the frozen authorities.

### VALUE_OR_LITERAL and OUTPUT_ATTRIBUTE

Maximal wholly integer-constant `neg/add/sub/mul` trees are attachment units.
For example `-(13+8)` attaches computed value -21 to the exact accumulator
initialization; 13 and 8 do not become separate required-value keys. Initial
evidence records source span, value, type, role, exact state binding,
initialization dependencies, execution and output dependencies, with no
fabricated behavioral parent. The threshold `3*5+2` attaches 17 to its exact
active comparison occurrence and the same-case parent intervention witness.
No nearest-text attachment or invented exact literal spelling is used.

There are 71 unsupported parent specifications in the toy inventory. They
remain explicit and block the development gate. Complete syntax-essential
literal obligations and all source parent roles are not certified. They are
not silently treated as covered.

Output findings read actual hash/selector-bound disposable expected-output
records, check normal/compiler agreement, require execution of the exact final
output node and derive ZERO/POSITIVE/NEGATIVE/MULTIDIGIT or canonical exact
integer sentinel matches mechanically. Category declarations are toy contract
requirements, not caller match flags. Exact sentinels -19 and 37 have actual
record witnesses. Noncanonical sentinel spellings fail schema validation.
Prospective frozen output declarations remain unimplemented; no historical
expected labels are consulted to fill them.

### V3.2 mapping and V3.3 equivalence

Identical/alpha mapping retains complete type, role, directed endpoint and
port checks. Computed-value mapping accounts for maximal constant interiors
using a serialized V3.3 proof, while retaining the original full graphs.
It does not erase general algebra, unrelated source-only trees, state/order,
literal spelling obligations or Boolean topology. Alpha maps are complete
and injective; local-flow proofs also check role compatibility.

Source-proved AND versus 0/1 product and OR versus positive indicator-sum
alternatives now serialize frozen rule/catalog IDs, locations, operand/result
types, alpha mapping, current-iteration flow preconditions and affected local
occurrences. Inputs must each resolve to one source-mapped frozen predicate;
compound/unlisted predicates cannot be relabeled as atomic pair inputs.
Only unchanged complete source topology and matching loop contexts are
supported here. These proofs explicitly say they are not complete graph
equivalence. They are not integrated into total source-to-contract mapping
for programs written with alternative Boolean topology. V3.2 and V3.3 remain
UNRESOLVED rather than falling back to output agreement.

## Evidence-derived development gates

These are local development gates only. The frozen scientific 17-gate binder
interface is unchanged. Status is derived from typed extracted records,
mapping certificates, unsupported-attachment inventory, actual intervention
findings, untested obligations and one pure frozen metadata contract probe.

| Development gate | Status | Evidence / remaining obligation |
|---|---|---|
| PRIMITIVE_EXTRACTION_COMPLETE | PASS | All eight catalog identities; required metadata, typed ports and mapped occurrences are checked in extraction evidence. This is catalog-recognition closure, not scientific closure. |
| INDICATOR_EXTRACTION_COMPLETE | UNRESOLVED | Range/current-iteration evidence exists; complete source mapping for Boolean alternatives does not. |
| STATE_GRAPH_COMPLETE | UNRESOLVED | Actual-writer traces and fixed points exist; frozen required-computation/recurrence certification remains incomplete. |
| ESSENTIALITY_ENGINE_COMPLETE | UNRESOLVED | Untested class obligations and nonterminating force-true loop interventions remain. |
| VALUE_LITERAL_ATTACHMENT_COMPLETE | UNRESOLVED | 71 unsupported toy parent specifications and incomplete prospective maximal/literal obligation derivation. |
| OUTPUT_ATTACHMENT_COMPLETE | UNRESOLVED | Actual toy output attachment works; frozen prospective output declarations remain absent. |
| V32_SEMANTIC_MAPPING_COMPLETE | UNRESOLVED | No complete-source mapping certificates for accepted local Boolean alternatives. |
| V33_REQUIRED_EQUIVALENCE_COMPLETE | UNRESOLVED | Local proofs exist, but required complete mapping integration is unfinished. |

The pure metadata probe `CONF1-ISOLATED-TR-NU-01-V0` derives only a contract
from a frozen source template. It selects/executes no cases and derives no
population. Its remaining core gaps are
`COMPUTED_CONSTANT_SUBTREE_ATTACHMENT_INCOMPLETE`,
`OUTPUT_CASE_OBLIGATIONS_UNRESOLVED` and
`TASK_ESSENTIALITY_PROOF_INCOMPLETE`. Removing the old primitive gap from this
probe is not a certificate for the other gaps or for every frozen contract.

## Disposable independence and machine artifacts

Before execution, the classifier-free preflight compares the entire declared
new inventory: 26 IDs, 19 exact sources, 16 expressions and 11 raw input
strings. Comparison covers all recursive raw strings and recorded hashes in
the 13 historical preregistered fixture files plus their manifest. Exact
string overlap, recorded-hash overlap and recomputed historical-string-hash
overlap are all zero. Expected-label files are not parsed. Module collection
repeats the overlap guard before importing the classifier/executor.

The six JSON artifacts are development-only evidence. The five requested
artifacts record extraction, actual state/intervention traces, exact
attribute/output attachments, gate evidence and overlap; the sixth records
protected-input integrity. Extraction embeds exact UTF-8 disposable source
and case artifacts with their bound references/hashes, so the temporary
directory is not needed to reconstruct the evidence. Independent saved-artifact
tests recheck these hashes, compiler/IR/reference output equality, joint
occurrence sets, actual changed-output relations and fail-closed gate status.

No authoritative population file or new row count is emitted. The historical
four-artifact population checkpoint is deliberately not regenerated.

## Tests and reproducibility

Python commands use `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src`, `python -B`.
Pytest runs use `-p no:cacheprovider --tb=short` and a checked-unused unique
temporary directory for `--basetemp`. No broad cleanup is performed. Each
complete new-toy test/producer run performs 80 normal pinned-compiler calls;
the oracle verifies the deterministic compiler JAR identity before execution.
Existing core regressions additionally run their non-preregistered toys.

```powershell
python -B scripts/check_conf1_v3_semantic_core.py --preflight-only
python -B scripts/check_conf1_v3_semantic_core.py --refresh-development-evidence
python -B scripts/check_conf1_v3_semantic_core.py
python -B -m pytest tests/test_conf1_v3_semantic_core.py tests/test_conf1_v3_unit.py -k 'not prospective_population_is_incomplete_not_authoritative' -p no:cacheprovider --tb=short --basetemp=$semanticPortTemp
```

Final focused result: **60 passed, 1 deselected in 13.81s**: 30 new semantic
tests and 30 existing core regressions. Coverage includes all minimum requested
topics, actual semantic input-edge suppression, runtime-map mutation resistance,
cross-loop rejection and independent saved-artifact checks. The sole excluded
unit test derives a population. The population-guard module and previous full
diagnostic producer are not run, because they would revisit the old diagnostic
population before semantic closure.

An intermediate byte-reproduction check failed because loop fixed-point
dictionaries inherited process-dependent key order. This was not waived:
the four generated evidence files now use sorted JSON object keys and sorted
set serialization. This pass's generated evidence was refreshed, then full
normal/compiler/intervention production reproduced all six saved artifacts
byte-for-byte without writes. Protected-input and overlap snapshots cannot be
refreshed by the scoped refresh option. Multiple subsequent full reproductions
passed, including after the semantic input-edge repair.

Relevant regression command:

```powershell
python -B -m pytest tests/test_benchmark.py tests/test_compiler.py tests/test_phase1r_context.py tests/test_phase3c_execution_contract.py tests/test_phase3c_dev2r_evaluation.py --deselect=tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_real_manifest_remains_unauthorized --deselect=tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_versioned_manifest_portable_hashes --deselect=tests/test_phase3c_execution_contract.py::Phase3CContractTests::test_execution_manifest_and_model_support_hashes -p no:cacheprovider --tb=short --basetemp=$semanticCommitRegressionTemp
```

Final result: **36 passed, 3 deselected, 8 subtests passed in 7.89s**. No full-repository
scientific-fixture suite was run.

Known historical failures were rerun separately and not repaired:

```powershell
python -B -m pytest tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_real_manifest_remains_unauthorized tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_versioned_manifest_portable_hashes tests/test_phase3c_execution_contract.py::Phase3CContractTests::test_execution_manifest_and_model_support_hashes -p no:cacheprovider --tb=short --basetemp=$semanticKnownTemp
```

Result: **3 failed in 5.79s**, with the same recorded baseline errors:

- `test_real_manifest_remains_unauthorized`: `RuntimeError not raised`.
- `test_versioned_manifest_portable_hashes`: `True is not False`.
- `test_execution_manifest_and_model_support_hashes`:
  `ValueError: Execution code changed: .gitattributes`.

The unchanged `.gitattributes` mismatch is a legacy failure, not a change made
by this repair. Final protected-input preflight and `git diff --check` are
required before the scoped checkpoint commit.

## Stop boundary

No preregistered CONF1 scientific fixture was executed. No historical expected
label was parsed or inspected. No sealed-holdout access, model loading,
training, inference or generation occurred. No candidate, Attempt 004,
replacement preregistration, E1–E6 execution/repair, provenance repair, binder
repair or scientific gate relaxation was begun. The frozen 17-gate interface
and all historical protected inputs remain unchanged.

This stops on remaining implementation/proof deficiencies, not a claim that
the frozen design is impossible. The safe boundary is preserved: no semantic
closure declaration, no V3.5 certification/recount, and no next-stage work.

STOPPED_COVERAGE_V3_CORE_SEMANTIC_CLOSURE_ISSUE
