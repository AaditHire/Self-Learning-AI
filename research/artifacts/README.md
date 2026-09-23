# Durable artifact storage plan

The checkpoint inventory is `research/manifests/infrastructure_checkpoint_artifacts.json`.
Git retains protocols, code, configs, manifests, reports, hashes, compact
task outcomes, and provenance. Historical Phase 2A/2B/3A adapter binaries
already tracked by Git LFS remain there; this checkpoint does not migrate
or rewrite them. Phase 3B's nine adapter binaries and 39 raw runtime records
remain under ignored `.runtime/phase3b/` and need a second durable copy.

For future preservation, use an immutable versioned artifact store outside
ordinary Git history. An object key should include phase, experiment ID,
seed, condition, and SHA-256. Before upload, record relative local path,
object URI or version ID, SHA-256, byte size, producing experiment, seed,
base revision, and parent adapter hash in a Git-tracked manifest. Verify the
uploaded bytes by reading back their hash, retain the local original, and
test recovery to a separate directory. Never reuse an object key for changed
bytes. Protect the store with independent backup and access controls.

Git LFS is a possible versioned mechanism for future final adapters, but
putting mutable checkpoints or repeated overwrites under LFS recreates the
previous `.git/lfs/tmp` growth risk. An external versioned object store is
preferable for large raw generations and checkpoints. No remote artifact
store, independent backup, or verified off-machine copy was established by
this checkpoint. OneDrive location alone is not evidence of completed sync.
