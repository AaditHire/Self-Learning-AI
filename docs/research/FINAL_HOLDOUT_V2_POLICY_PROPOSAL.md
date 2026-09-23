# Proposed future Final Holdout V2 policy

Status: proposal only. No V2 tasks, tests, references, or generators were
created by the infrastructure checkpoint. This document is not authorization
to construct or use V2.

1. Preserve the legacy Final Holdout V1 permanently, including its eight
   `final_paper` tasks and associated tests/references in the frozen Phase 1
   benchmark containers. Never replace, regenerate, or repurpose V1.
2. Construct V2 prospectively only after a separate approved protocol freezes
   the construction method, target capability coverage, structural-distance
   criteria, deduplication rules, sample size, scoring, access controls, and
   rejection rules. Preserve rejected construction attempts and audit records.
3. Make V2 larger and structurally more diverse than V1, with independent
   lineages and broader task families. Choose its size and composition before
   observing any V2 model result.
4. Seal V2 after construction and validation of references. No model,
   hyperparameter, prompt, adapter, replay ratio, gate, or stopping decision
   may be tuned against V2, including through selective reruns or error review.
5. Define an explicit late paper-validation stage and its one-time access
   procedure in advance. Use V2 only at that stage after all relevant model
   and analysis choices are frozen; record every access and outcome.

The current checkpoint hashes V1's three mixed-split container files as
bytes only. It does not parse or inspect their sealed tasks.
