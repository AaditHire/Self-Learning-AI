# Phase 2A — Exploratory QLoRA parameter-acquisition feasibility pilot

Date: 2026-09-20

Start commit: `00d819c1f38260f6750db70306150bd085422312`

Frozen config SHA-256: `f8d4e94dddff4fbf6244c9d9d41585e69291325aefb386c26b2bcfa76b0075d2`

## Preregistration status

The data, structural audit, model lineage, QLoRA configuration, smoke gate,
evaluation conditions, regression rule, and exploratory success criteria were
frozen before the first Phase 2A gradient step. The exact preregistration commit
is recorded after this pre-training state is committed.

Phase 1T remains a failed gate. This separately authorized exploratory pilot
cannot retroactively change that outcome and is not Phase 2B or a confirmatory
paper experiment.

## Frozen artifacts

- Data manifest: `research/manifests/phase2a_data.json`
- Model/lineage manifest: `research/manifests/phase2a_model.json`
- Machine config: `research/protocols/phase2a_config.json`
- Protocol: `research/protocols/PHASE_2A_FROZEN_EXPLORATORY_PILOT.md`
- Construction/verification: `research/results/EXP-0014/`

## Pending execution

EXP-0015 through EXP-0019 are pending. No Phase 2A training or model evaluation
existed at freeze time. Completion results, adapter hashes, curves, raw outputs,
decisions, deviations, and reproduction commands will be appended without
rewriting this pre-training record.
