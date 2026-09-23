# Research infrastructure and reproducibility checkpoint

Date: 2026-09-23. Scope: metadata, storage, environment, path, and
documentation audit only. Scientific source of truth remains frozen/raw
artifacts, then preregistrations, then `PROJECT_STATE.md`, then phase reports.
This checkpoint does not authorize Phase 3C.

## 1. Verified repository state and commits

Starting HEAD and `origin/main` were both
`38a0de06c6329f9805cd211157fdaca7a01aa9eb`; the worktree was clean.
Git history had no scientific commit after the Phase 3B final commit. Phase
2B completed at `1ded323e036cd93813ab165210e0c3dcf32616df` with a
bounded confirmatory acquisition PASS. Phase 3A completed at
`000311f724155d0a643d99bff22c6cac848a15be` with severe forgetting in
the naive sequence. Phase 3B was preregistered at
`002395e5dc7916e827eeed3e4806417d27bb5419` and completed at the
starting HEAD. Its numerical gate PASS and 0/24 task-level A retention must
be reported together. All nine Phase 3B training runs and 30 evaluations
are complete. No undocumented later scientific run was found in Git or the
Phase 3B runtime inventory. Absence outside this checkout cannot be proven.

There is no conflict between the frozen Phase 3B protocol and compact result.
Two current-documentation problems were found: `PROJECT_STATE.md` ended with
stale Phase 3A resume instructions, and the stage index lacked Phase 3A/3B
entries. This checkpoint corrects those current pointers without changing
historical reports. The experiment registry retains its preregistered
"Pending" rows and separately appended completion rows by design.

## 2. Artifact inventory and preservation risk

| Class | Current location | Preservation status |
|---|---|---|
| Code, protocols, configs, data, benchmark suites, schedules, manifests, reports, compact outcomes/provenance | Git | Tracked; Phase 3B compact files under `research/results/PHASE_3B/` |
| Ten Phase 2A/2B/3A adapter binaries | Git LFS under `research/adapters/candidates/` | 1,198,015,280 local bytes total; existing history unchanged |
| Nine Phase 3B final adapter binaries | Ignored `.runtime/phase3b/adapters/` | 1,078,213,752 bytes; local-only and not known backed up |
| Phase 3B raw training and generation/evaluation records | Ignored `.runtime/phase3b/training/` and `evaluations/` | 39 provenance-hashed JSON files, 2,407,849 bytes; local-only |
| Other Phase 3B runtime files | Ignored `.runtime/phase3b/` | 134 files overall, 1,225,100,089 bytes including adapters; local-only |
| Pinned 3B base model shards | Ignored `.models/` | 6,171,927,000 bytes; revision and hashes frozen, local cache only in this audit |
| Deterministic GOCO compiler JAR | Ignored `.artifacts/compiler/` | 212,005 bytes; hash frozen and vendor source tracked in Git |
| Other external location or verified off-machine backup | None established | OneDrive path alone does not verify sync, versioning, or restore |

The machine-readable inventory at
`research/manifests/infrastructure_checkpoint_artifacts.json` gives each
Phase 3B and historical LFS adapter's identifier, path, SHA-256, byte size,
producing EXP ID, seed, and parent lineage. The frozen provenance contains hashes of all 39
raw JSON records. No artifact was moved, deleted, uploaded, or rewritten.
`.runtime/` is gitignored and outside LFS; `.git/lfs/tmp` had zero files at
this checkpoint. The immediate risk is loss of the local-only Phase 3B
adapters and raw records. `research/artifacts/README.md` defines a prospective
immutable versioned store layout and read-back verification. No remote store
was configured or migration attempted here.

## 3. Environment reproducibility

The Phase 3B raw training records report Windows 11 `10.0.26200`, Python
3.13.0, PyTorch `2.9.0+cu130`, Transformers 4.57.1, bitsandbytes 0.50.2,
PEFT 0.17.1, CUDA runtime 13.0, and RTX 3060 Laptop GPU. The current host
also reports NVIDIA driver 610.74, 6144 MiB VRAM, and local Eclipse Temurin
25.0.1+8 for the pinned compiler. Ambient `java` is Oracle Java 21.0.12.1,
so reproduction must select the local pinned JDK explicitly.

The current interpreter's 208-distribution exact-version snapshot is
`research/environment/phase3b_host_pip_freeze.txt`. Current critical pins
include Accelerate 1.15.0, tokenizers 0.22.1, pytest 9.1.1, NumPy 2.2.6,
SciPy 1.16.2, safetensors 0.6.2, and psutil 7.1.2. This is a checkpoint
snapshot, not proof that every transitive package had the same version during
Phase 3B. Exact wheel hashes, complete historical transitive versions,
driver binary, and independently stored JDK binaries were not recorded.
`pyproject.toml` pins the evaluation extra but does not list all training
dependencies; the host snapshot fills the version inventory without changing
the historical experiment or upgrading packages.

## 4. Path portability

A scoped search of executable Python and TOML found no `C:\\Users\\Admin`,
OneDrive, or Desktop absolute path used as an executable dependency. Phase
3B's frozen config uses repository-relative paths; its dispatcher also uses
relative paths and assumes invocation from the repository root. The
checkpoint inventory script anchors paths to its own repository location and
ran successfully. No frozen method script was edited, because its hash is a
preregistered input. The absolute paths in `PROJECT_STATE.md` identify the
then-current research and read-only GOCO checkouts; those in the Phase 0
stage record are historical provenance/commands, not current dependencies.
Future dispatchers should resolve paths from the script's repository root
or accept explicit configurable paths before preregistration.

## 5. Documentation and holdout policy

`PROJECT_STATE.md` now points to the completed Phase 3B STOP boundary. The
stage index and Phase 3A/3B stage pointers make commits, EXP IDs, protocols,
and reports discoverable. The result README now acknowledges Phase 3B's
runtime/compact publication split. Earlier stage reports were not rewritten.

The legacy sealed V1 split remains in the three original mixed-split Phase 1
benchmark containers. Their byte hashes match the frozen Phase 1 manifest,
and Git history shows no changes to those files since Phase 1 completion.
Phase 3B frozen provenance says `sealed_holdout_opened=false`. This audit did
not parse, inspect, execute, or evaluate V1; a historical access log does not
exist, so "never opened by anyone" cannot be independently proven. The
proposed V2 policy is in `docs/research/FINAL_HOLDOUT_V2_POLICY_PROPOSAL.md`:
preserve V1, construct V2 prospectively under a frozen method, make it larger
and structurally more diverse, forbid tuning against it, and reserve use for
an explicitly defined late paper-validation stage. No V2 tasks were created.

## 6. Immutability checks and remaining work

The read-only inventory tool verified SHA-256 for 24 frozen Phase 3B inputs,
39 provenance-listed raw records, nine runtime adapters, ten historical LFS
adapters, two base-weight shards,
the deterministic compiler JAR, and three V1 container files. The frozen
Phase 3B config matched SHA-256
`52cc6c8400e5675389a9ca151137a179442af6e6021859aa8572a819855e907f`.
Git diff inspection before commit must show no changes to completed datasets,
evaluation outputs, adapters, frozen configs, schedules, compiler, scoring,
Phase 3B analysis, or gates. The checkpoint changes only infrastructure and
current organizational documentation.

Unresolved: independent durable backup and restore verification for local-only
Phase 3B artifacts and local model/compiler binaries; complete historical
wheel-level environment reconstruction; historical holdout-access logging.
These require a separate preservation decision, not a scientific rerun.

**Execution declaration:** No model gradients were run. No scientific model
evaluation was run. No completed experimental artifact was altered. The
sealed holdout was not opened or evaluated; only byte hashes of its three
existing mixed-split container files were computed. Phase 3C was not begun.
