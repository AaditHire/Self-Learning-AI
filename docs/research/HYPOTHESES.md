# Hypotheses

All thresholds remain unset until their protocol is pre-registered. No result
may be used to retroactively choose its own success threshold.

## H-001 — Retrieval ceiling

On a frozen unseen GOCO benchmark, a frozen base model supplied with trusted
GOCO documentation will achieve a higher hidden-test pass@1 than the same base
model without documentation.

## H-002 — Persistent adaptation

After controlled adapter training, the adapted model without documentation will
outperform the frozen base model without documentation on unseen GOCO tasks.

## H-003 — Generalization beyond memorization

An adapted model's improvement will persist on structural and compositional
holdouts that do not share near-identical templates with training examples.

## H-004 — Sequential forgetting

Naive sequential LoRA will produce measurable degradation on at least one
previous GOCO capability after learning later capabilities.

## H-005 — Replay mitigation

At least one pre-registered replay ratio will reduce average or worst-task
forgetting relative to naive sequential LoRA while meeting the new-capability
learning threshold.

## H-006 — Stability gating

A pre-registered promotion gate will reject at least some candidate adapters
that improve the new capability but exceed an allowed old-capability or general
behavior regression.

## H-007 — Documentation dependence

As verified parameter learning accumulates, the marginal benefit of trusted
documentation at evaluation time will decrease for learned capabilities without
falling to zero for genuinely unlearned concepts.

## H-008 — Later self-directed learning (future)

Given calibrated evaluation signals, the system can identify capability gaps
better than a fixed or random curriculum and improve them using quarantined,
externally verified experience. This hypothesis is not authorized for current
implementation.

## H-009 — Syntax-capability localization

Under the fixed Candidate C context, frozen GOCO performance may be materially
better on recognition and local completion than on structured modification and
full synthesis, which would localize the primary limitation to composition
rather than basic syntax recognition. Phase 1S is diagnostic: any observed
pattern does not authorize parameter adaptation.

## H-010 — 3B documentation-assisted confirmation

On a fresh 64-task synthesis benchmark, the exact frozen 3B NF4 configuration
with Candidate C will achieve at least 25% hidden-test pass@1, improve by at
least 15 percentage points over its paired no-documentation condition, and pass
tasks in at least four semantic families. This is an engineering suitability
gate, not a causal parameter-count or universal scaling hypothesis.

**Result:** Not supported as a conjunctive hypothesis. Candidate C achieved
14/64 (21.875%) versus 0/64, a +21.875-point effect, and passed five families.
The absolute 25% criterion failed; therefore the preregistered gate failed.

## H-011 — Exploratory parameter-acquisition feasibility

On the frozen Phase 2A development suite, the fixed 3B QLoRA adapter without
GOCO documentation will improve hidden-test pass@1 by at least 15 points over
the frozen 3B base without documentation, reach at least 20%, pass at least four
families, avoid explanation by structural duplication, and avoid severe
general-regression collapse. This is exploratory and cannot establish the final
parameter-acquisition claim.
