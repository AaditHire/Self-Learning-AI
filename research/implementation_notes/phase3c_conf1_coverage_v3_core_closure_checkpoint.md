# Coverage-v3 semantic/population closure — stopped checkpoint

Implementation diagnostic only. This is not a frozen authority, candidate,
expected-row index, scientific validation, delegated producer report, or
authorization. The full semantic repair was **not completed** in this pass.

## Repository boundary

Starting HEAD was independently verified as
`152673769d29b47c458b8fac0c153f8c4778fd02`, branch `main`, with an empty
`git status --porcelain`. The current request was the semantic/population-closure
attachment, not the unrelated experiment-evaluation prompt.

One dedicated checkpoint commit: `Guard CONF1 v3 population closure and record unresolved derivation`.
Final HEAD is the Git commit containing this report. Its exact concrete SHA is
reported in the accompanying final response and can be recovered without
self-reference using:

```powershell
git log -1 --format=%H -- research/implementation_notes/phase3c_conf1_coverage_v3_core_closure_checkpoint.md
```

Final worktree status is independently checked after committing and reported
in the handoff. No push is performed.

Exact changed-file inventory, nine files:

- `src/self_learning_ai/conf1_v3/contracts.py`
- `tests/conf1_core_development_inputs.py`
- `tests/test_conf1_v3_population_guard.py`
- `scripts/audit_conf1_v3_core_closure.py`
- `research/implementation_notes/coverage_v3_core_closure/protected_input_integrity.json`
- `research/implementation_notes/coverage_v3_core_closure/disposable_overlap.json`
- `research/implementation_notes/coverage_v3_core_closure/partial_derivation.json`
- `research/implementation_notes/coverage_v3_core_closure/unresolved_obligations.json`
- this report.

## Integrity verified before editing and again before commit

All ten upstream authorities match their frozen declared-policy SHA-256 values,
exact sizes, and committed Git blobs. The delegated interface matches exact
SHA-256 `9c684eaf6b0099080ddf907630b0a2f8e176e3a882b67875d82f07bd82d64dc5`,
size 76081, and blob `1b6d4d1a825bf9e9d288ca9c3815d1a8e7c78d1a`.
Its freeze manifest matches exact SHA-256
`bd7a7fc6862ce049c1fdf363f763e1a3a17808132291b9064e3c6f26fb720948`.

Approved normative tails were read from their actual approved commits and
compared byte-for-byte under each authority's declared policy:

| Authority | Normative bytes | SHA-256 |
|---|---:|---|
| Delegated interface, exact bytes | 74717 | `26c642e17bb5218727c0cd09f370eaf1ac6c4de35006fa9801d701ece81cf16d` |
| Coverage-v3, LF-normalized | 29178 | `884a8ac3f859268e16dfa0d8f0d477211c7a273fca58666c7eba018265d8c15a` |
| Paired scaffold, LF-normalized | 12217 | `5aa404949a8cc580b9ca3ff4aff7325195e172a7cfa82c69317280597c73b25c` |
| INPUT_DOMAIN amendment, LF-normalized | 14669 | `b9dc3d6ca22778ab0b3e734270fb20a00b4d88e0602f24fe77b2112335df8167` |

All 15 historical preregistration files remain unchanged against their baseline
Git blobs at `b44d1c73de1be47b541f76d67c88541a5d90f3fa`. Exact working-byte
SHA-256 and size are also recorded in `protected_input_integrity.json`; subsequent
`--check` reproduces those exact identities. Expected labels receive generic
byte-integrity checking only: their JSON/content is never inspected or parsed.

An initial unfiltered Git-blob comparison of the CRLF slot ledger failed.
Its frozen exact-byte SHA and LF SHA were already correct; the Git clean filter
produces the recorded committed blob. This was a verification-policy mismatch,
not an authority change. The producer checks both file-byte hashes and the
correct Git-filtered blob independently. No authority was changed.

## Fresh derivation and exact stop reason

Pure frozen source-template lowering, without candidate construction, case
selection, or execution, derives 184 partial contracts: 120 training programs,
32 primary tasks and 32 secondary tasks. There are 92 contracts per domain.
Aggregation families are 168 `sum_per_item`, 8 `prefix_running_pair`, and
8 `two_pass_product`.

The frozen ledger and Coverage-v3 V3.2/V3.4 require semantic predicate
capabilities. Independent structural inspection finds **zero
SEMANTIC_PRIMITIVE nodes/keys and zero PREDICATE_TO_INDICATOR edges** in all
184 current graphs. The derivation artifact traces 408 required predicate-role
obligations to exact ledger JSON selectors and the frozen rules. These are
role obligations, **not 408 distinct keys or missing V3.5 rows**: canonical
deduplication/typing has not been implemented. Their canonical key and expected
row ID fields are deliberately null.

For example, the first artifact contract is
`CONF1-COMPOSITION-TR-AR-01-V0`, from `/slots/training_paired_slots/30`.
Role P requires `negative_value`, from
`/predicate_definitions/array_reduction/0`, expression `values[i]<0`.
The source graph contains the typed LT predicate, but no semantic-primitive
node/key or predicate-to-indicator relation for that requirement. Recording
the incidental LT operator cannot substitute for the required primitive key.

This proves the **current implementation's** universe is incomplete. It does
not prove the frozen authorities contradictory or the repair impossible in
principle. No methodological amendment is proposed. This pass stops with an
implementation deficiency rather than inventing keys or calling diagnostics
authoritative. The absent ontology/state/output algorithms still need repair.

Fresh diagnostic V3.5 breakdown, unchanged in count after the guard repair:

| Diagnostic kind | Rows |
|---|---:|
| Behavioral | 7344 |
| VALUE_OR_LITERAL | 1324 |
| OUTPUT_ATTRIBUTE | 0 |
| Total diagnostic rows, unique | 8668 |

The 14 INPUT_DOMAIN class rows are a separate direct row set, not 14 additional
V3.5 activity rows. The behavioral decoder keys remain in the diagnostic
API_DECODER category. No other authoritative row class or total is asserted.
Neither historical 2360 nor diagnostic 8668 is adopted as an authoritative
count. No authoritative expected V3.5 population file is emitted.

`V3_5_POPULATION_UNRESOLVED`

## Scoped repair and remaining closure results

The reproduced population guard defect was that `v35_expected_row_ids([])`
returned `[]` in default mode. Default mode now requires the complete frozen
184-program contract inventory with its exact slot/kind/condition/domain
metadata. Missing/unexpected programs, duplicates, and relabeling frozen
contracts as development data cannot create a vacuous expected population.
The diagnostic flag must be an actual Boolean. Contract validation runs before
diagnostic row emission; duplicate keys, orphan occurrences, and missing key
occurrence inventories are rejected. Row identities are framed from contract
keys only and deterministically ordered by exact UTF-8 bytes, independent of
input contract order or observed findings. This ordering is an implementation
convention to be bound in a future reviewed index, not a new scientific gate.

All four previously reported contract gaps reproduce in every contract, with
736 per-contract gap records in `unresolved_obligations.json`:

- primitive/indicator extraction: incomplete as shown above;
- maximal constant-tree attachment: leaf-only extraction remains; exact
  syntax-essential literal obligations are not certified;
- output/case obligations: `lower_contract` still sets `outputs=()`; output
  category and exact-sentinel derivation are unfinished;
- task essentiality: backward reachability and all-writer state edges are not
  certified required-computation or prefix/two-pass reaching-definition proofs.

V3.2 is UNRESOLVED: identical/alpha/trivia mapping exists, but permitted
equivalence remapping and a closed total/pure REFERENCE_ONLY proof catalog do
not. V3.3 is UNRESOLVED: supported scalar cases remain tested; source-flow-proved
AND/product and OR/indicator alternatives and complete evidence serialization
remain unimplemented. V3.5 behavioral closure is UNRESOLVED: disposable
normal/compiler agreement and joint suppression still pass, but all-category,
essentiality and state closure are not established. VALUE_OR_LITERAL and
OUTPUT_ATTRIBUTE closure are UNRESOLVED for the reasons above.

INPUT_DOMAIN's 14 class identities and UTF-8-first canonical numeric slot
`CONF1-TR-NU-01-V0` are retained. Existing tests exercise separate class/activity
witnesses, actual four-field decoder connectivity, and exclude numeric zero
from normal behavioral events. No negative-numeric or finite-upper-bound class
was added. Full frozen inventory activity/class certification was not run.

V3.4 retains resolved-negative row status separately from aggregate absence;
its existing disposable regression passes. V3.6 source-scaffold success and
uncontrolled predicate-change rejection still pass, but schedule comparison
and full paired serialized evidence remain UNRESOLVED. No delegated producer,
provenance, binder, or direct-report PASS gate was relaxed or repaired.

## Artifacts and development independence

The four JSON files are implementation diagnostics with schema version 1,
not candidate-bound scientific artifacts. `partial_derivation.json` traces
frozen slot -> contract -> provisional key catalog -> source occurrence spans
-> framed diagnostic row identity. An independent test reconstructs all
diagnostic rows from that catalog and checks uniqueness and exact ordering.
Missing obligations have null canonical key/row identity, never fabricated IDs.
`unresolved_obligations.json` retains every contract gap plus the scope-specific
limitations. `protected_input_integrity.json` binds the protected authorities
and preregistration. `disposable_overlap.json` stores the complete test inventory
with exact UTF-8 string hashes and the comparison result.

Before test execution, 20 disposable IDs, 14 exact sources, 12 expressions,
and 10 distinct raw input strings were compared against all recursive raw
strings and recorded hashes in the 13 historical fixture files plus manifest.
Exact string overlap, recorded fixture-hash overlap, and freshly computed
historical-string hash overlap are all **zero**. Collection repeats the guard
before importing Coverage-v3 code. No expected-label oracle is used.

New tests use the distinct `DEV-CLOSURE-LEDGER-20260930-B` toy and independently
authored source initialized to 37. No new behavioral case execution was needed
for the population guard. Frozen contract tests lower pure source templates
only. Existing core toy regressions perform 25 normal pinned-compiler runs;
the normal oracle verifies the deterministic JAR hash before every invocation.
Unchanged legacy compiler tests execute their existing non-CONF1 examples.

## Commands and exact results

All Python commands use `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src`, `python -B`.
Pytest uses `-p no:cacheprovider --tb=short` and a newly allocated, checked-unused
temporary directory for `--basetemp`. No broad cleanup or deletion is performed.

```powershell
python -B scripts/audit_conf1_v3_core_closure.py
python -B tests/conf1_core_development_inputs.py
python -B -m pytest tests/test_conf1_v3_unit.py tests/test_conf1_v3_population_guard.py -p no:cacheprovider --tb=short --basetemp=$closureTemp
python -B scripts/audit_conf1_v3_core_closure.py --refresh
python -B scripts/audit_conf1_v3_core_closure.py --check
python -B -m pytest tests/test_conf1_v3_unit.py tests/test_conf1_v3_population_guard.py -p no:cacheprovider --tb=short --basetemp=$finalFocusedTemp
```

Initial focused run: **45 passed in 9.05s**. After adding machine-artifact
reconstruction checks, final focused run: **47 passed in 10.05s**, no skips.
`--refresh` only condensed this pass's generated diagnostics before commit;
`--check` then reproduced all four artifacts byte-for-byte without writing.

Relevant repository regression command:

```powershell
python -B -m pytest tests/test_benchmark.py tests/test_compiler.py tests/test_phase1r_context.py tests/test_phase3c_execution_contract.py tests/test_phase3c_dev2r_evaluation.py --deselect=tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_real_manifest_remains_unauthorized --deselect=tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_versioned_manifest_portable_hashes --deselect=tests/test_phase3c_execution_contract.py::Phase3CContractTests::test_execution_manifest_and_model_support_hashes -p no:cacheprovider --tb=short --basetemp=$regressionTemp
```

Result: **36 passed, 3 deselected, 8 subtests passed in 4.05s**.

Known failures were rerun separately, not suppressed or fixed:

```powershell
python -B -m pytest tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_real_manifest_remains_unauthorized tests/test_phase3c_dev2r_evaluation.py::RecoveryTests::test_versioned_manifest_portable_hashes tests/test_phase3c_execution_contract.py::Phase3CContractTests::test_execution_manifest_and_model_support_hashes -p no:cacheprovider --tb=short --basetemp=$knownFailureTemp
```

Result: **3 failed in 1.88s**, with the same checkpoint-known errors:
`RuntimeError not raised`, `True is not False`, and
`ValueError: Execution code changed: .gitattributes`, respectively.
These are not newly classified Coverage-v3 regressions. `git diff --check`
and deterministic artifact/protected-input verification are run before commit.

## No advancement

No historical/preregistered CONF1 scientific fixture was executed. Expected
labels were not parsed or inspected. No sealed holdout contents were accessed.
No model was loaded, trained, used for inference, or used to generate anything.
No candidate, Attempt 004, replacement preregistration, real consumed inventory,
E1–E6 execution/repair, provenance repair, or binder repair was begun.

STOPPED_COVERAGE_V3_CORE_CLOSURE_ISSUE
