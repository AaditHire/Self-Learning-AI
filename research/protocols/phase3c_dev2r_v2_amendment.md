# Prospective Phase 3C-DEV2R amendment and v2 refreeze

**Status:** proposed and frozen before any DEV2R model inference. Execution authorization remains false. This document supplements, and does not rewrite, the original [DEV2R protocol](phase3c_dev2r_protocol.md) at design commit `cdff638153df13c5da2d77b4eda908385c1a6423`. The pre-execution construct STOP was recorded at `c5d26366345cb228c3bafb7c64d51ec58d39ca95`; Structural Transfer essentiality evidence at `1815279f0f8acf4266aab58b1cf2215edf55efe4`. The Git commit containing this amendment and v2 manifest is the prospective amendment commit; its exact SHA is reported with the final review package. No history is rewritten.

## Fairness rule

**Original ambiguity:** the mechanical source audit treated each construct in a canonical reference as if the task required that construct. This marked Structural Transfer 0/16 because its references used `-1` as an absent-anchor sentinel.

**Amended definition:** a development task is coverage-valid only if every semantic primitive, GOCO API/library/language construct, and literal or value capability **essential to satisfying the frozen task specification and semantic cases** is represented in both original DEV2 training conditions. A construct appearing only in one valid implementation is not automatically task-essential. An independent solution using only covered constructs that passes every frozen semantic case is diagnostic evidence of nonessentiality; reasoning about the task specification is also required. These diagnostic solutions are not canonical references, training data, model outputs, or changes to hidden cases.

This definition was approved prospectively before any DEV2R model inference. It does not retroactively erase the 0/16 reference-construct result or imply that the model can implement a diagnostic alternative.

## Primitive Sanity decision and versioned replacement

The [original sanity essentiality audit](../results/PHASE_3C_DEV2R_AMENDMENT/primitive_sanity_original_essentiality.json) finds **0/16 task-essential coverage**. Every original sanity prompt requires a `-1` output when no match exists; 14 frozen cases exercise that output. Neither DEV2 training condition has a negative target output or a negative literal in its target reference programs. The literal spelling might be avoidable, but the negative output requirement is not. Both conditions cover the eight intended predicates and input/output APIs.

Before model use, exactly the 16 affected sanity tasks are replaced in `benchmark/phase3c_dev2r_v2/`. Each new task counts matches of the **same single semantic primitive** and prints a nonnegative count plus fixed offset 1 or 2. The old five frozen input strings and case IDs for each task are retained; expected outputs are recomputed for the new specification and frozen in a new versioned test file. There are still eight numeric and eight array sanity tasks, two correlated variants per primitive. No adapter generation or outcome was consulted. The [mapping](../results/PHASE_3C_DEV2R_AMENDMENT/replacement_map.json) records every old ID, reason, new ID, and unchanged input identity. The original v1 suite remains intact and historically frozen.

The amendment changes the secondary sanity construct from first/last index retrieval to counting. Counting is closer to the training targets and may be easier; the sanity result must be interpreted as a bounded check of primitive acquisition under this new specification. The two offsets per primitive are correlated variants, not independent archetypes. The primary Novel Composition question, its tasks and analysis, and all 16 Structural Transfer tasks remain exactly as frozen in v1. The overall suite still has 48 tasks with five cases each.

## Final pre-inference scientific gates

The v2 audit verifies **16/16 Primitive Sanity task-essential coverage** in both conditions, **16/16 Novel Composition primitive coverage and signature absence** in both conditions, and **16/16 Structural Transfer primitive and task-essential construct coverage** in both conditions. Reference-only gaps remain separately documented. All 48 canonical references pass all 240 pinned-compiler semantic cases, including all 80 new sanity cases. The 16 replacements have zero exact prompt/reference reuse against original DEV2 training, earlier A evaluation suites, the consumed original DEV2 development suite, and DEV2R v1. All 1,920 replacement-to-training pairs, including lower similarity scores, and nearest neighbors are frozen. Similarity does not prove distributional independence.

## Execution infrastructure, still unauthorized

The prospective runner uses `phase3c_dev2r_v2_manifest.json` and requires the actual boolean value `true` before heavy model imports, adapter load, generation, or compiler evaluation. Missing, null, false, numeric, string, or malformed authorization values fail closed. The real manifest remains `model_execution_authorized: false`. Its non-model authorization-check path must refuse execution at this freeze.

For each of the five remaining own-training cells, the prospective evaluator uses the frozen first-fence extraction and compares the normalized generated source directly with the frozen target string, matching the historical diagnostic rule. It checkpoints this exact-target boolean together with primary score and case results before optional reporting. The aggregate reports overall pass/60, numeric/30, array/30, each training archetype, exact target reproduction/60, and failure taxonomy. Historical 20270925/ISOLATED 60/60 is not rerun. A pre-existing run directory blocks regeneration; no resume of an attempted task is authorized by this amendment.

The original DEV2 development suite remains consumed. The versioned DEV2R suite remains untouched by models and will become development-consumed after eventual authorized use. No B training, replay, retention test, paper-level PASS threshold, or sealed final-paper holdout access is authorized. Independent review must explicitly approve a future execution authorization commit; this amendment does not do so.

The v2 manifest hashes text after CRLF-to-LF normalization so Windows and fresh Git checkouts agree; compiler and adapter hashes remain byte-exact. Both original and versioned suite hashes are recorded under this explicit policy. The original design manifest and historical artifacts are retained without rewriting their recorded hashes.
