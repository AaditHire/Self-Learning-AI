# Research question

## Primary question

Can a small language model acquire objectively verified programming-language
capabilities sequentially, retain those capabilities in trainable adapter
parameters without continued access to teaching documentation, and reject
candidate parameter updates that cause pre-registered unacceptable forgetting?

## Operational definitions

- **Base-model knowledge:** performance of the immutable base model without
  GOCO documentation or parameter updates.
- **In-context/document access:** performance produced while trusted GOCO
  material is present in the prompt.
- **Retrieval/external memory:** performance produced by selecting trusted
  GOCO material from an external corpus at inference time.
- **Persistent parameter adaptation:** improvement retained by a versioned
  adapter and measured with GOCO documentation absent.
- **Memorization:** success limited to training instances or near-duplicate
  structural templates.
- **Generalization:** success on frozen, unseen semantic families, structures,
  or compositions that are separated from training data.
- **Continual learning:** sequential acquisition accompanied by measurement of
  every previously learned capability and general behavior after each update.
- **Self-directed learning:** later-stage selection of learning targets based on
  objectively calibrated capability gaps; this is outside the initial phases.

## Scope boundaries

Initial work concerns bounded, offline adapter updates under an external
compiler-and-test oracle. It does not study live updates from user messages,
unrestricted autonomy, consciousness, or recursive self-improvement.

## Evidence standard

Removing documentation is necessary but insufficient evidence of learning.
The key causal comparison is frozen base/no docs versus adapted/no docs on the
same unseen, integrity-protected executable benchmark, with near-duplicate
templates excluded across splits.
