# Phase 3B off-machine artifact preservation

Status: **verified remote backup and complete remote restore**. The existing
project GitHub repository is the versioned destination. Nine immutable final
Phase 3B adapter weights are stored through its established Git LFS endpoint;
39 raw training/evaluation JSON records are stored as ordinary Git objects.
The backup artifact commit is
`e8ee26f50fc71d941b8e84afa7eb470597136cbb` on `origin/main`.

The source of truth was the existing
`research/manifests/infrastructure_checkpoint_artifacts.json` for adapter
hashes/sizes and `research/results/PHASE_3B/provenance.json` for raw-record
hashes. `research/manifests/phase3b_artifact_preservation.json` lists all 48
original paths, backup paths, names/IDs, producing experiments, seeds,
lineage, sizes, SHA-256 values, and local copy checks. Its
`remote_restore_status` was recorded as pending at the backup commit; the
subsequent independent restore result is recorded in
`research/manifests/phase3b_remote_restore_verification.json`.

To verify remote recoverability, a fresh shallow clone was made from the
GitHub URL into a separate temporary directory with LFS smudge disabled.
The nine Phase 3B LFS objects were then downloaded selectively with
`git lfs pull`. Every restored backup file, local committed copy, and
untouched `.runtime/phase3b/` original was hashed and size-checked against
the preservation manifest. **48/48 passed; zero failed.** The restored
checkout resolved to the backup commit above. The temporary clone was left
intact after verification; no source artifact was moved or deleted.

The existing checkpoint commit
`1c1ee158bacfa6711ff9238a42801038d62bbafd` and backup commit were
pushed normally to `origin/main`; no force push or history rewrite occurred.
This closes the specifically identified local-only risk for the nine adapter
weights and 39 raw records. It does not claim an independent second provider,
offline copy, or backup of the local base-model/JDK caches.

No model gradients or scientific evaluations ran. Completed Phase 3B
scientific artifacts, frozen inputs, and local originals were not changed.
The sealed final-paper holdout was neither inspected nor evaluated.
