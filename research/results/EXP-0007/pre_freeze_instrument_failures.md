# Phase 1S pre-freeze instrument corrections

These construction findings occurred before the Phase 1S protocol was frozen
and before any Phase 1S model inference. They are retained rather than erased.

1. The first generated local-completion prompts supplied a scaffold and blank
   but did not state the target behavior. The prompts were invalid as a
   capability diagnostic. The builder was corrected to include the target
   behavior for every local-completion task.
2. The first input/output reference pair for IO1 and IO3 had identical
   identifier/literal-normalized structure. IO3 was redesigned to use
   `strings.TO_SENTENCE` and one composed display expression. Its semantics and
   tests remained distinct.

After both corrections, all 96 task IDs, lineages, and structural signatures
were unique; exact duplicate prompts were zero; and all 72 executable reference
programs passed all 288 hidden cases. These corrections are instrument design,
not post-result tuning.
