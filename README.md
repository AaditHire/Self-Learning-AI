# Self Learning AI

Research infrastructure for controlled continual-learning experiments in the
GOCO programming language.

The production GOCO repository is an upstream, read-only source. This repository
owns all experiment code, pinned compiler snapshots, datasets, protocols, and
results. Start with [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md).

## Research status

- **Purpose:** test whether a small language model (Qwen2.5-Coder-3B with QLoRA
  adapters) can acquire verified programming-language capabilities, retain
  them across sequential updates, and avoid harmful forgetting.
- **Strongest demonstrated result:** parameterized behavioral acquisition. In
  the confirmatory Phase 2B, adapters raised held-out GOCO pass@1 from 0% to
  roughly 51–55% without documentation in the prompt. Continual learning and
  retention have **not** been demonstrated.
- **Current phase:** Phase 3C-CONF1, a preregistered test of whether
  compositional training practice improves novel-composition program
  generation. Its methodology is being re-baselined; no CONF1 model
  execution has occurred.

[`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md) is the authoritative,
current description of project status. The
[stage index](docs/research/stages/README.md) and
[infrastructure checkpoint](docs/research/RESEARCH_INFRASTRUCTURE_CHECKPOINT.md)
locate historical phases and preservation records.
