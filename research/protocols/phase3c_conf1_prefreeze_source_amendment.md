# CONF1 prefreeze source-template correction

**Status:** prospective non-model construction amendment; no model or adapter has been loaded. The design-baseline proposal and semantic slot ledger remain unchanged. This correction does not change a task specification, predicate, input case, expected output, seed, budget, graph, or decision rule.

The first generated candidate (`attempt_001`) failed GOCO syntax because compound assignment of a two-term treatment expression requires parentheses. Both conditions were corrected symmetrically to `total+=(hitP+hitQ).` and `total+=(hitP*hitQ).` The rejected candidate is preserved.

The second candidate (`attempt_002`) passed 60/60 ISOLATED, 60/60 COMPOSITION, and 64/64 evaluation reference programs, all five cases each. The consumed-suite audit then found that all 16 Primitive Sanity references exactly matched the old DEV2 sanity template after the already approved normalized-code transformation (identifier and numeric-literal normalization). This violates the prospective full-template exclusion, so attempt 002 is rejected despite semantic correctness. Its source, cases, rejection ledger, and compiler validation are preserved.

**Prespecified next candidate:** keep the 16 single-primitive sanity specifications and five cases unchanged, but use a meaningful indicator scaffold for their canonical references: declare `NUMBER hit=0`, reset it on every item, set it to one inside the one primitive `IF`, then add `hit` to the tally. The indicator is read by the tally and is not a dead or redundant guard. Apply this source change to both subskills and both sanity variants. The semantic reference-output oracle remains unchanged. Re-run compiler, exact/template, AST-proxy, and all other prefreeze audits. If this candidate still matches a prohibited consumed template or fails any gate, STOP; do not select another source form by model outcomes.

No historical task-level model outcome or adapter output was consulted. The only feedback used was pinned-compiler syntax and input/reference-template comparison, both permitted pre-model audits.
