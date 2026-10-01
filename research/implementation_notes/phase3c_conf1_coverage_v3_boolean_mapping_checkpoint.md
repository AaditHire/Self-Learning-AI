# Coverage-v3 Boolean mapping boundary — partial, stopped checkpoint

Development implementation evidence only. This pass did **not** complete the
requested Boolean topology transport. Both frozen alternatives now have local
source-derived proofs across distinct spellings, but neither transformed
program has complete typed V3.2 correspondence. The three scoped gates remain
UNRESOLVED. No other semantic gate or later phase is advanced.

## Repository and commit boundary

Starting HEAD was independently verified as
`c13996834f3895c013b460f43cf2a0303c892360`, branch `main`, with empty
`git status --porcelain`. No applicable `AGENTS.md` was found. The latest core
checkpoint and actual saved gate artifact were read; they establish primitive
extraction PASS and the other seven gates UNRESOLVED.

One dedicated checkpoint commit:
`Separate CONF1 Boolean local proofs from complete mapping certificates`.
Final HEAD is the commit containing this report. Its concrete SHA and actual
post-commit worktree status are supplied in the final handoff and independently
recoverable using:

```powershell
git log -1 --format=%H -- research/implementation_notes/phase3c_conf1_coverage_v3_boolean_mapping_checkpoint.md
git status --porcelain
```

This avoids a self-referential commit hash in the committed report. The final
worktree must be clean and is checked after the commit. No branch, worktree,
sub-agent, external task, push or intermediate commit is created.

Exact changed-file inventory, 16 files:

- `src/self_learning_ai/conf1_v3/semantic_ir.py`
- `src/self_learning_ai/conf1_v3/boolean_mapping.py`
- `scripts/check_bm901_preflight.py`
- `scripts/check_conf1_v3_boolean_mapping.py`
- `tests/bm901_inputs.py`
- `tests/bm901_cases.py`
- `tests/test_conf1_v3_boolean_mapping.py`
- `research/implementation_notes/coverage_v3_boolean_mapping/frozen_boolean_rule_catalog.json`
- `research/implementation_notes/coverage_v3_boolean_mapping/v33_equivalence_certificates.json`
- `research/implementation_notes/coverage_v3_boolean_mapping/complete_v32_mapping_certificates.json`
- `research/implementation_notes/coverage_v3_boolean_mapping/indicator_extraction_evidence.json`
- `research/implementation_notes/coverage_v3_boolean_mapping/negative_case_results.json`
- `research/implementation_notes/coverage_v3_boolean_mapping/disposable_overlap.json`
- `research/implementation_notes/coverage_v3_boolean_mapping/development_gate_evidence.json`
- `research/implementation_notes/coverage_v3_boolean_mapping/protected_input_integrity.json`
- this report.

Core execution, state analysis, contract/key extraction, attribute/output
logic, the existing complete mapper, population guards, previous artifacts,
frozen protocols and historical preregistration files remain unchanged.
The only existing-file edit is local Boolean proof safety/availability in
`semantic_ir.py`; no state execution or essentiality intervention is changed.

## Integrity and pre-repair reproduction

Before mapping edits, all ten upstream authorities matched declared-policy
SHA-256 values, exact sizes, worktree Git clean-filter blobs and committed
Git blobs. Four normative regions matched their approved commits byte-for-byte
under the declared normalization policy. All 15 preregistration files matched
baseline blobs at `b44d1c73de1be47b541f76d67c88541a5d90f3fa`.
This pass separately snapshots exact working-byte hashes and checks them again
before execution and commit. The expected-label file is only generically
byte-hashed, never JSON-parsed, inspected or used as an oracle.

The delegated interface retains exact SHA-256
`9c684eaf6b0099080ddf907630b0a2f8e176e3a882b67875d82f07bd82d64dc5`,
size 76081, and blob `1b6d4d1a825bf9e9d288ca9c3815d1a8e7c78d1a`.
Its freeze manifest retains exact SHA-256
`bd7a7fc6862ce049c1fdf363f763e1a3a17808132291b9064e3c6f26fb720948`.
The Boolean catalog checks the frozen Coverage-v3 LF-normalized file SHA-256
`a9fb8350c849ce62e2a673e3ca1f1d5a08f556b7f415687f1e2eabdf356030f3`.
All detailed authority/approved-region/preregistration identities are retained
in the new integrity artifact. No protected identity changed unexpectedly.

Only the integrity function from the old population-checkpoint script is
imported. Neither its population producer nor any population derivation
function is invoked. The initial semantic-checkpoint preflight was called in
preflight-only mode; it performs integrity/overlap checks, not population
production or scientific execution.

After classifier-free overlap checking, new BMAP901 disposable AND/product
and OR/positive-sum programs reproduced both pre-repair failures:

- local cross-spelling proof: `local flow proof requires unchanged complete source topology`;
- total mapping: `INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE`.

The pre-edit reproduction command was
`python -B scripts/check_bm901_preflight.py`. It also independently recognized
all eight frozen primitive identities using new numeric and array sources.
That script reads the current implementation when rerun: after this repair,
its local proof result changes, while total mapping still rejects.

## Exact frozen catalog and its limits

The authority is frozen Coverage-v3 §V3.3, read together with V3.2's typed
node/edge and total source-mapping requirements. It supplies rule ID `V3.3`;
the descriptive AND/OR catalog labels used by the implementation are labels
for those existing clauses, not invented frozen authority IDs.

| Frozen alternative | Required foundation | Authorized scope |
|---|---|---|
| Boolean AND versus multiplication of two proven 0/1 indicators | Actual typed predicates, actual 0/1 writes/initialization, source-flow identity for each indicator | Local pair-joint key only; not atomic AND-to-MUL key substitution |
| Boolean OR versus `indicator(add(a,b)>0)` | Both inputs proven Boolean; numeric carriers need actual source-flow truth identity; comparison/indicator typed and source-mapped | The declared Boolean truth relation, not arbitrary arithmetic/control or full-graph substitution |

The frozen text expressly preserves complete graph multiplicity and excludes
complete-graph equality from these local rules without the full-signature
audit. There is no permission here for reassociation, distributivity, arbitrary
algebra, dropping predicates, range-only truth inference, or using output
agreement as mapping evidence.

The saved catalog separates frozen requirements from the implementation's
stricter safety restrictions: independently reconstructed source graphs,
complete injective type/role-compatible alpha mapping, matching parsed loop
contexts, exact operand bindings, source-recognized frozen predicates,
unconditional same-iteration reset, one predicate-controlled positive write,
read-after-definition order, exact reaching definitions, no stale/cross-loop
or circular identity, and retained duplicate occurrences. No new equivalence
rule or amendment is created.

## Repairs and remaining complete-mapping blocker

Local V3.3 proof no longer incorrectly requires two entire source syntax trees
to be identical. It can compare the frozen local alternatives across different
source spellings, while still independently reconstructing both graphs and
proving types, alpha roles, exact predicate inputs and matching loop context.
Every result continues to state that it is **not complete graph equivalence**.

Indicator foundations are tightened: a read must occur inside the same parsed
loop as its resetting definition. Circular-looking conditions that use the
indicator whose identity they are meant to establish are rejected. A numeric
range of [0,1] is deliberately insufficient; the circular test retains that
range and nevertheless fails because there is no independent frozen predicate
foundation. Existing state-analysis results are consumed, not altered.

The new complete Boolean certificate layer calls the actual complete V3.2
mapper as a separate obligation after local proofs. It serializes complete
source/contract node and edge inventories, source text/hash, control/loop
identities, bindings, state dependencies, predicate correspondence, source
locations, roles, typed ports, alpha mapping, local V3.3 proofs, canonical-key
occurrences and unmatched inventories. A supplied alpha bijection must agree
with the binding correspondence actually established by the total mapper.

The certificate verifier independently reconstructs the evidence. Duplicate,
missing or invented predicate mappings, changed ports/types and forged PASS
flags cannot establish completeness. Indicator evidence is derived only after
that verification, and records the actual predicate, source write/range proof,
current-iteration reaching definitions and complete-certificate hash.
Dependency order is explicit:

`parsed typed source → frozen predicate recognition → reaching definitions → local V3.3 preconditions → complete V3.2 correspondence → indicator evidence`.

This prevents indicator identity from being assumed to prove the same Boolean
equivalence that supposedly establishes it.

### Certificate results

| Contract/source forms | Local V3.3 | Complete V3.2 | Indicator evidence |
|---|---|---|---|
| AND / PRODUCT | EQUIVALENT | UNRESOLVED | Forbidden: no complete mapping |
| OR / SUM_POSITIVE | EQUIVALENT | UNRESOLVED | Forbidden: no complete mapping |
| PRODUCT / alpha-renamed PRODUCT | EQUIVALENT | COMPLETE | Derived from actual source reads and complete certificate |
| SUM_POSITIVE / alpha-renamed SUM_POSITIVE | EQUIVALENT | COMPLETE | Derived from actual source reads and complete certificate |
| Repeated AND / alpha-renamed repeated AND | Two local proofs | COMPLETE | No used numeric-indicator evidence asserted |

The three COMPLETE certificates have empty unmatched inventories and total,
injective physical node/edge correspondence. The repeated example maps all
six actual predicate occurrences separately.

The two transformed-program certificates remain UNRESOLVED with
`INCOMPATIBLE_COMPLETE_TYPED_STRUCTURE`. No partial correspondence is adopted,
so they retain the entire unaccepted inventories: AND/PRODUCT has 101 source
and 129 contract items; OR/SUM_POSITIVE has 109 source and 129 contract items.
These numbers are **not missing primitive counts or V3.5 row counts**.

The exact remaining implementation obligation is authorized topology lowering
and typed occurrence/key transport into a common semantic contract domain.
The current raw source-derived contracts retain different operator, control,
indicator-use, state-edge and multiplicity inventories. A local pair proof
does not supply correspondences for those extra/different items. In particular
Boolean AND and integer MUL are differently typed atomic operations; V3.3's
local-pair exception cannot silently equate their atomic capability keys.
OR truth equality likewise cannot erase unmatched predicate/control/state
connections. No cast, fabricated mapping, source-node deletion, output fallback
or arbitrary REFERENCE_ONLY waiver is introduced to bypass this blocker.

Thus the requested total alternative mapping algorithm remains incomplete.
This is an implementation limitation, **not** a claim that the frozen design
is impossible or contradictory. Neither full-signature auditing nor repair of
out-of-scope task-essentiality/attribute/state rules was attempted to force
closure.

## Disposable tests and independence

Classifier-free comparison precedes all new execution and is repeated at test
collection and evidence production. The final complete inventory has 35 IDs,
28 exact sources, 19 expressions and 10 raw input strings. Recursive raw strings
and recorded hashes in the 13 permitted historical fixture files plus their
manifest are compared with exact strings, recorded hashes and recomputed
string hashes. All three overlap counts are zero. Expected labels are not
parsed. Alpha variants are included before execution.

The machine artifact records 17 intended-reason negative results:

- incomplete alpha mapping;
- omitted Boolean/source predicate relation;
- unrelated extra Boolean term;
- compound predicate pretending to be atomic;
- ambiguous indicator definition;
- conditional instead of unconditional reset;
- read-before-current-write;
- changed state/update order;
- wrong operand type;
- matching normal outputs but invalid topology;
- source-only extra computation/binding;
- unlisted Boolean rewrite;
- circular indicator foundation despite 0/1 range;
- duplicate predicate mapping;
- missing contract predicate mapping;
- omitted source predicate mapping;
- cross-loop alternative.

All reject for the intended semantic reason. Only the wrong-operand-type case
fails during typed compilation, which is the correct frozen type outcome;
the others are not mere parser rejections. An additional test rejects a
type/role-compatible alpha permutation that disagrees with actual complete
binding correspondence. Forged completion flags and changed typed ports/types
also fail independent reconstruction.

Twenty-five actual new normal pinned-compiler runs agree with the IR and
independent elementary reference formulas. This includes the invalid-topology
program whose extra branch is unexercised on all five new inputs: its outputs
match AND, but complete mapping still rejects. No result-dependent waiver is
used.

## Machine artifacts and development gates

The seven requested artifacts are saved separately in
`research/implementation_notes/coverage_v3_boolean_mapping/`; the eighth is
protected-input integrity. Local proofs, total mapping certificates and
indicator evidence remain distinct records. V3.3 records link to the complete
mapping evidence by canonical JSON SHA-256. Every certificate retains original
source and full graph inventories for independent reconstruction.

Saved artifacts reproduce byte-for-byte in a subsequent full producer run
without writes. Scoped `--refresh` was used only for this pass's six generated
evidence files as their schema was completed; it cannot refresh protected-input
or overlap snapshots. Previous checkpoint artifacts remain unchanged.

The updated gate artifact binds the previous gate artifact by path and exact
SHA-256. The primitive gate and four out-of-scope unresolved gate records are
copied unchanged and checked for equality. Only the three permitted gate
records receive new evidence/blocker detail. Their statuses are derived from
the two transformed-program certificates, not manually asserted.

| Development gate | Final status |
|---|---|
| PRIMITIVE_EXTRACTION_COMPLETE | PASS, unchanged; all eight identities rechecked on new sources |
| INDICATOR_EXTRACTION_COMPLETE | UNRESOLVED: no complete certificates for both transformed forms |
| STATE_GRAPH_COMPLETE | UNRESOLVED, untouched |
| ESSENTIALITY_ENGINE_COMPLETE | UNRESOLVED, untouched |
| VALUE_LITERAL_ATTACHMENT_COMPLETE | UNRESOLVED, untouched |
| OUTPUT_ATTACHMENT_COMPLETE | UNRESOLVED, untouched |
| V32_SEMANTIC_MAPPING_COMPLETE | UNRESOLVED: transformed typed inventories not transported |
| V33_REQUIRED_EQUIVALENCE_COMPLETE | UNRESOLVED: local proofs do not complete required total mapping integration |

The frozen scientific 17-gate binder interface is unchanged. No production
contract probe or population producer runs in this pass.

## Commands and results

Python uses `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src`, `python -B`.
Pytest uses checked-unused unique temporary paths, `-p no:cacheprovider` and
`--tb=short`. No broad filesystem cleanup is performed.

```powershell
python -B scripts/check_bm901_preflight.py
python -B scripts/check_conf1_v3_boolean_mapping.py
python -B scripts/check_conf1_v3_boolean_mapping.py --refresh
python -B scripts/check_conf1_v3_boolean_mapping.py
python -B -m pytest tests/test_conf1_v3_boolean_mapping.py tests/test_conf1_v3_semantic_core.py tests/test_conf1_v3_unit.py -k 'not prospective_population_is_incomplete_not_authoritative' -p no:cacheprovider --tb=short --basetemp=$bm901FinalFocusedTemp
```

Final focused/core result: **93 passed, 1 deselected in 18.13s**: 33 new Boolean
tests plus 60 preceding semantic/core regressions. These include new primitive
catalog recognition and the prior primitive-extraction tests. The excluded
unit test invokes population derivation. No population-guard suite, population
producer or historical scientific fixture suite is executed.

Relevant repository regressions:

```powershell
python -B -m pytest tests/test_benchmark.py tests/test_compiler.py tests/test_phase1r_context.py tests/test_phase3c_execution_contract.py tests/test_phase3c_dev2r_evaluation.py --deselect=tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_real_manifest_remains_unauthorized --deselect=tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_versioned_manifest_portable_hashes --deselect=tests/test_phase3c_execution_contract.py::Phase3CContractTests::test_execution_manifest_and_model_support_hashes -p no:cacheprovider --tb=short --basetemp=$bm901RegressionTemp
```

Result: **36 passed, 3 deselected, 8 subtests passed in 3.74s**.

Known historical failures rerun separately:

```powershell
python -B -m pytest tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_real_manifest_remains_unauthorized tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_versioned_manifest_portable_hashes tests/test_phase3c_execution_contract.py::Phase3CContractTests::test_execution_manifest_and_model_support_hashes -p no:cacheprovider --tb=short --basetemp=$bm901KnownTemp
```

Result: **3 failed in 1.74s**, unchanged baseline reasons:
`RuntimeError not raised`, `True is not False`, and
`ValueError: Execution code changed: .gitattributes`, respectively. These
legacy issues are not repaired or hidden by the scoped regression command.

Final integrity-only preflight, generated-artifact reproduction and
`git diff --check` complete before the explicit-file checkpoint commit.
Post-commit HEAD/worktree and protected inputs are checked again in the handoff.

## Stop boundary

`V3_5_POPULATION_UNRESOLVED` remains unchanged. **No V3.5 recount occurred**,
including no new diagnostic recount. Historical `8668` remains non-authoritative
and is not evidence for this changed implementation.

No preregistered scientific fixture execution, expected-label parsing or
inspection, sealed-holdout access, model loading/training/inference/generation,
new/replacement preregistration, Attempt 004, E1–E6 execution or repair,
provenance work, binder work, or frozen gate relaxation occurred. No later
semantic gate or phase is begun. The checkpoint stops on the remaining total
Boolean occurrence/key-transport implementation deficiency.

STOPPED_COVERAGE_V3_BOOLEAN_MAPPING_CLOSURE_ISSUE
