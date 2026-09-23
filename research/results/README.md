# Results

Each executed experiment receives `research/results/EXP-NNNN/`. Never overwrite
or delete failed/rejected results. Raw outputs, environment records, hashes, and
the result summary belong together.

For Phase 3B, the frozen protocol placed mutable raw generations and training
records in ignored `.runtime/phase3b/` and published compact immutable copies
and their source hashes in `research/results/PHASE_3B/`. The infrastructure
checkpoint inventories the local-only artifacts; it does not relocate them.
