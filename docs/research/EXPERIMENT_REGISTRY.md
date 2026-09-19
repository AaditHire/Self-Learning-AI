# Experiment registry

Experiment IDs are immutable. Failed, rejected, and superseded experiments are
never deleted. Phase planning documents do not receive IDs until execution is
authorized and inputs are frozen.

| ID | Purpose | Date | Research commit | Model / revision | Adapter parent | Dataset hash | Compiler hash | Config hash | Seed | Hardware | Output | Summary | Status | Rejection reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EXP-0000 | Phase 0 repository/compiler audit and protocol foundation | 2026-09-19 | Working tree based on `1edb0f5c017302da9054dbb06c82b695612400fd` | None | None | None | GOCO commit `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`; compiler tree `f51973617cc3da8c78de88c668d8de6959575d6d` | Documentation-only; see Phase 0 Git diff | None | Windows 11; RTX 3060 Laptop 6 GB; Ryzen 7 6800HS; 16 GB RAM | `docs/research/stages/PHASE_00.md` | Read-only audit completed; no model run | COMPLETE / GO | N/A |

## Required fields for future entries

Before an experiment runs, assign its ID and freeze its purpose, exact commit,
model revision/hash, adapter parent, dataset manifest/hash, compiler hash,
configuration hash, seed or seed set, hardware record, and output path. After it
runs, append the result summary, status, and rejection reason without rewriting
the original protocol.
