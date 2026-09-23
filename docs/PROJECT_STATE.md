# Project state

Last updated: 2026-09-23

Current phase: Phase 3A complete; naive sequential baseline shows measurable severe A forgetting; stopped for independent review
Phase decision: Phase 1T gate remains failed; Phase 2A remains exploratory;
Phase 2B independently confirms multi-seed parameterized GOCO behavioral acquisition.
Phase 3A was authorized solely to measure A-to-B sequential acquisition and A
forgetting. No replay or other anti-forgetting method was tested or authorized.

## Phase 3A recovery pointer

Starting commit: `1ded323e036cd93813ab165210e0c3dcf32616df`.
Preregistration: `research/protocols/phase3a_protocol.md` and
`research/protocols/phase3a_config.json` (SHA-256 `3fb940a6b9a65311904db13f2a834a2729f60826c12c250d966420aaa356a715`).
Preregistration Git commit: `18c4c1065bf1e63bb0cdac91a33e01ec1c6a37e6`.
Three frozen seeds: `20260923`, `20261011`, `20261117`. A is numeric
iteration/array reduction; B is string transformation/field processing.
Data: 60 training examples and 32 evaluation tasks per capability, five
semantic cases each. All 184 references/targets pass; see
`research/results/EXP-0027/data_validation.json` and manual review.
The sealed final-paper holdout remains unopened. All six training runs and all
required evaluations completed. EVAL_A: base 0/32, A 29/32, 31/32, 30/32,
and A→B 0/32 in every seed. EVAL_B: A-only 0/32 in every seed, A→B 19/32,
16/32, 8/32. Mean A forgetting 93.75 points (task-bootstrap 95% interval
85.42–100), relative retention 0%. Frozen non-GOCO regression: base 47/64,
all A checkpoints 48/64, all A→B checkpoints 49/64. Full report:
`research/results/PHASE_3A/report.md`; analysis:
`research/results/PHASE_3A/analysis.json`; independent verification:
`research/results/PHASE_3A/completion_verification.json`. STOP for
independent review.

## Repository boundaries

- Primary research repository (all new work goes here):
  `C:\Users\Admin\OneDrive\Documents\GitHub\Self Learning AI`
- Primary repository commit inspected at Phase 0 start:
  `1edb0f5c017302da9054dbb06c82b695612400fd`
- Main GOCO product repository (**STRICTLY READ ONLY**):
  `C:\Users\Admin\OneDrive\Documents\GitHub\GOCO`
- GOCO commit extracted and pinned for the research instrument:
  `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`
- GOCO remote: `https://github.com/Thryza-creators/GOCO.git`
- The mutable GOCO checkout had advanced to `57acfa52b3ce983572683e612c4cd8e4ba9b47a4`
  before Phase 1. Phase 1 did not use that working tree content: extraction came
  from the recorded `6a029b8` Git object. GOCO remained clean and unmodified.

Never write to the GOCO path for this research project. Future integration must
copy an explicitly pinned source tree into this repository and record its
provenance; it must not import from or execute against the mutable product
checkout.

## Research goal

Test whether a small language model can acquire verified GOCO capabilities in
sequence, retain them in adapter parameters without permanent documentation
access, and reject candidate updates that cause pre-registered unacceptable
forgetting. This project does not claim AGI, consciousness, self-awareness, or
unrestricted recursive self-improvement.

## Fixed constraints

- Hardware: Windows 11, RTX 3060 Laptop GPU (6 GB VRAM), Ryzen 7 6800HS,
  16 GB system RAM.
- Phase 1 primary model was `Qwen/Qwen2.5-Coder-1.5B-Instruct`. Phase 2A uses
  the exact frozen `Qwen/Qwen2.5-Coder-3B-Instruct` Phase 1S/1T revision under
  a separate exploratory authorization.
- Training path after baselines: 4-bit QLoRA, LoRA rank initially near 16,
  batch size 1, gradient accumulation, gradient checkpointing, conservative
  sequence lengths.
- No model training occurs in Phase 0 or Phase 1.
- Foundation-model weights remain immutable; adapters are versioned and never
  repeatedly merged into the base.
- Compiler plus hidden semantic tests, not the model, determine correctness.

## Phase 0 findings

GOCO's compiler is an interpreter implemented in Java around a JavaCC grammar.
The entry point is `parser.MyLanguageParser`. It accepts exactly one `.goco`
file, parses it to a `CoreNodes.ProgramNode`, validates it against a global
scope, and executes the AST only if semantic validation succeeds. Syntax,
lexical, semantic, and runtime failures terminate with exit code 1. Program
output uses stdout; diagnostics use stderr. `INPUT` reads stdin and emits a
prompt to stdout.

The production test manifest contains 88 cases: 45 expected successes and 43
expected failures. The current Python test harness regenerates test files and
the batch runner recompiles into `goco-compiler/bin`, so it was deliberately not
run inside the read-only repository.

The production repository already contains a useful Python subprocess adapter
in `goco-ai/src/goco_ai/compiler/goco.py`. It uses a temporary `.goco` file,
captures stdout/stderr, supplies stdin, applies a timeout, sets a 256 MB JVM
heap limit, and normalizes diagnostics. It is a design reference only; Phase 1
will implement a research-owned version against a pinned compiler snapshot.

## Compiler provenance selected for extraction

- GOCO commit: `6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e`
- `goco-compiler` Git tree: `f51973617cc3da8c78de88c668d8de6959575d6d`
- Java source Git tree: `415215892c7127df899d59b3bceb99dc8357484b`
- `tests/tests.json` Git blob: `7ad40be14848fa3d03ac02f36066e737000bc401`
- Full machine-readable record:
  `research/manifests/goco_compiler_source.json`

## Phase 1 frozen inputs

- Compiler runtime: Eclipse Temurin 25.0.1+8.
- Parser generator: JavaCC 7.0.13.
- Evaluated compiler JAR SHA-256: `c6f45759930438dd4ae7bfbff298e9c7242604582d29da04210f15377f2be879`.
- Canonical class-tree SHA-256: `68b3ab9e694d3917957a62577a10e658cd60f5103368a17c5c3ae77374c4fb2a`.
- Deterministically packaged reproduction JAR SHA-256:
  `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`.
- Model: `Qwen/Qwen2.5-Coder-1.5B-Instruct` revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- Model weights SHA-256: `c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`.
- Inference config SHA-256: `7a6ab3e3fcd335be8674a22dde74d137b7c04b5632eabea3229b7f9319fc7584`.
- Python 3.13.0, PyTorch 2.9.0+cu130, Transformers 4.57.1.

Java 21 and the pinned Java 25 runtime produced identical behavior across all 88
upstream conformance cases, but official results use Java 25.0.1 only.

## Phase 1 results

- Compiler conformance: 87/88 exact; one explained stale upstream expectation
  for the automatic `INPUT` prompt; no timeout, crash, or output-limit failure.
- Wrapper tests: 10/10 passed.
- Benchmark: 40 tasks, 8 semantic families, 40 unique template IDs; 8
  development, 24 frozen evaluation, and 8 sealed final-paper tasks.
- Condition A, frozen base/no docs: 0/24 parse and 0/24 hidden pass. Every output
  was a Go `package main` program.
- Condition B, frozen base/full trusted docs: 0/24 parse and 0/24 hidden pass.
  Every output invented an unsupported `PROGRAM` wrapper.
- Paired pass-rate difference: 0.000; paired bootstrap 95% interval [0, 0];
  exact McNemar p=1.0 with zero discordant pairs. This is a floor effect, not an
  equivalence finding.

The compiler exposes no GOCO filesystem, process, network, reflection, or Java
interop capabilities. Execution nevertheless remains bounded in a no-shell
subprocess with a temporary directory, controlled stdin, separate capped
streams, heap/metaspace caps, timeout, and cleanup.

## Phase 1R results

Phase 1R is a frozen-model diagnostic recovery phase starting from commit
`e88d49255abd7b9d1a4497d3d89dbdc4d3a8a5ae`. The consumed Phase 1 evaluation
is excluded from protocol selection. The eight final-paper tasks remain sealed
and are now classified as a legacy sealed holdout.

A new development-only suite contains 24 tasks, three in each of the eight
families, with 97 hidden cases. References passed all cases. No docs scored
0/24; corrected reference A scored 2/24; reference plus concise contract B
scored 2/24; contract, reference, and canonical examples C scored 3/24.

C was selected by the frozen rule but failed the conjunctive progression gate:
12.5% was below the required 25%, and its +12.5-point gain was below the
required +15 points. Its three successes did span three families. Therefore no
new confirmatory suite was created, no confirmatory A/B experiment ran, and
Phase 2 remains prohibited.

## Phase 1S preregistration

Phase 1S starts from commit
`2879bbea5a5199eba3df1ead4fe9138916c17937`. It introduces a new diagnostic-only
suite with 96 items: eight families, four capability levels, and three items
per family/level. The 72 executable items have 288 hidden cases; all references
passed before freezing. Phase 1/1R tasks remain consumed, and the legacy final-
paper holdout remains sealed.

Candidate C is fixed with no prompt search. The primary 1.5B revision remains
unchanged; a frozen 3B comparator is allowed only in 4-bit after a hardware
smoke gate. The frozen config SHA-256 is
`5e7da9fe450cef1561bdeaa9f0642ec88d4e96429eac9c4bf44944b36df20c2a`.
No Phase 1S inference result existed when this protocol was frozen.

## Phase 1S results

The exact preregistration commit is
`2e14057ddd9ee622ef123dbc30c1099bf7d31782`. The 1.5B model scored 13/24
recognition, 0/24 local completion, 4/24 structured modification, and 0/24 full
synthesis. Its executable funnel was 6/72 parse, 5/72 compile, 5/72 execute,
and 4/72 hidden pass; 66/72 executable outputs failed lexing or parsing.

The frozen 3B NF4 comparator passed its local smoke gate at 2.87 GB peak GPU
allocation. It scored 17/24 recognition, 7/24 local completion, 14/24
structured modification, and 7/24 full synthesis. Full-synthesis passes reached
29.2% across five families, satisfying preregistered case C. Case B also fires
for 1.5B. Therefore 1.5B is a NO-GO as the primary backbone, and the only
recommended next step is a separately preregistered backbone-selection phase.
No training or backbone change is authorized.

## Phase 1T preregistration

Phase 1T starts from commit
`56940731b14053677123521093615c73c24604c6`. It uses 64 completely new
full-synthesis tasks, eight in each semantic family, with 329 hidden cases and
at least five per task. All reference programs passed. Phase 1/1R/1S tasks are
consumed and the legacy final-paper holdout remains sealed.

The exact 3B NF4 configuration runs paired no-docs and fixed Candidate C
conditions. A secondary 1.5B NF4 Candidate C check is frozen but cannot alter
the 3B gate. The config SHA-256 is
`4cf19e35b4b937eeba6a89cbf2340e49c83f147b37dddffbb9ebde0946e020d5`.
No Phase 1T model inference existed at freeze time.

## Phase 1T results

The exact preregistration commit is
`dd3dd6f2ebcc303bc7ca6fcb1ca35bb2319fee26`. On the fresh 64-task suite, the
3B NF4 no-doc condition scored 0/64 hidden pass and Candidate C scored 14/64
(21.875%). The paired improvement was +21.875 points with a paired bootstrap
95% interval of [12.5, 32.8125] points; there were 14 docs-only wins and no
baseline-only wins. Candidate C passes spanned five families.

The 25% absolute-pass criterion failed, while the +15-point and four-family
criteria passed. No major benchmark-integrity issue was found. Because the gate
is conjunctive, Phase 1T is a **FAIL** and the recommendation is **NO-GO for
QLoRA or Phase 2 parameter adaptation**. The secondary matched-NF4 1.5B check
scored 4/64 (6.25%) across three families; it is diagnostic only and does not
alter the gate. No training or parameter update occurred.

## Phase 2A preregistration

Phase 2A starts from final Phase 1T commit
`00d819c1f38260f6750db70306150bd085422312`. Phase 1T remains a failed gate;
Phase 2A is a separately authorized developmental pilot and cannot change that
history.

The frozen pool has 200 verified training examples (25 per family; 600 hidden
verification cases), 64 structurally held-out development tasks (eight per
family; 320 hidden cases), and 24 non-GOCO regression tasks. All training
targets and development references passed. Phase 1/1R/1S/1T tasks are excluded
from training and the legacy final-paper holdout remains sealed.

The exact 3B base remains immutable. Candidate `c0001-phase2a-qlora` is an
unmerged rank-16 NF4 QLoRA adapter. A two-step smoke gate precedes the single
three-epoch training configuration. The frozen config SHA-256 is
`f8d4e94dddff4fbf6244c9d9d41585e69291325aefb386c26b2bcfa76b0075d2`.
No Phase 2A gradient step or model evaluation existed at freeze time.

## Phase 2A results

The exact preregistration commit is
`b5fe9b3b5e8d95d319ebc1e14bd14aa1df492f9b`. The local two-step smoke passed,
and the single fixed three-epoch run completed 75 optimizer steps without OOM
or non-finite values. Peak full-run GPU allocation was 3,673,793,536 bytes,
reserved GPU memory 4,102,029,312 bytes, and process RSS 6,030,819,328 bytes.
The immutable base shard hashes were unchanged; adapter weights remain
separate with SHA-256 `d23e22646bcdbc11281e3ed597487740ce9c50734bfc8caac4b628b30fdd5d43`.

On the frozen 64-task development suite, base/no-doc scored 0/64 and
adapter/no-doc 18/64 (28.125%), a +28.125-point paired gain with bootstrap 95%
interval [+17.1875, +39.0625]. Passes span five families. Training tasks scored
198/200 (99.0%), leaving a 70.875-point train/held-out gap that must be treated
as potential memorization and narrow transfer. Regression moved from 18/24 to
16/24, inside the frozen severe-collapse rule.

All five exploratory success criteria passed. This supports only development-
set evidence consistent with parameterized GOCO behavioral acquisition in this
setup. It does not establish continual learning, self-learning, general
acquisition, or robust retention. Phase 1T remains failed. The Phase 2A suites
are consumed, Phase 2B was not started, and independent review plus a new
untouched preregistration are required before any confirmatory work.

## Phase 2B preregistration

Phase 2B starts from exact commit
`06e5db763ad2af2adc51e9b4709916820b0883a6`. The exact preregistration commit is
`4589be9473283d46cff7920fc1a46208dfa911e1`. No Phase 2B gradient step or model
inference existed at freeze time.

The fresh pool has 200 verified training examples (25 per family; 600 hidden
cases), a new 128-task confirmatory suite (16 per family; 640 hidden cases), and
a 64-task non-GOCO regression suite. All training targets and confirmatory
references pass. Phase 2A training data and all prior consumed evaluation tasks
are excluded; the legacy sealed holdout remains unopened.

The final structural audit has zero exact train/evaluation prompt, algorithm,
lineage, structural-signature, or semantic-operation overlap; zero normalized-
code rejects at 0.98; zero prior-suite prompt flags at 0.70; and manual review
of every lower-threshold prompt, code, and AST-proxy flag. Frozen distance
buckets are 3 far, 44 medium, and 81 near.

Three independent rank-16 NF4 QLoRA adapters use the unchanged Phase 2A recipe
and seeds `20260921`, `20261007`, and `20261103`. Every seed is primary; best-
seed selection is prohibited. The success gate requires mean adapted pass@1 at
least 20%, mean gain at least 15 points, every seed gain at least 10 points,
every seed successes in four families, a frozen structural non-domination rule,
and no regression drop greater than 15 points. All three training runs must be
feasible. Candidate C on the immutable base is descriptive only.

At the Phase 2B stop boundary no sequential experiment was authorized; the
later explicit Phase 3A request separately authorized this naive baseline only.

## Phase 2B results

All three frozen QLoRA runs completed 75/75 optimizer steps with finite losses
and gradients, no OOM, separately saved adapters, and unchanged immutable base
shard hashes. Seeds `20260921`, `20261007`, and `20261103` reached final losses
0.000665, 0.002141, and 0.001394.

On the untouched 128-task confirmatory suite, frozen base/no-doc scored 0/128.
The three adapter/no-doc conditions scored 65/128 (50.78%), 70/128 (54.69%),
and 70/128 (54.69%): mean 53.39%, range 50.78%–54.69%. Every seed succeeded
in all eight families. The paired task-cluster bootstrap 95% interval for mean
improvement is 45.57–61.20 points. Medium/far tasks improved by 48.94 points on
average, so the preregistered structural non-domination rule passed. Frozen
base plus Candidate C documentation scored 22/128 (17.19%) and is descriptive
only.

Training performance was 200/200, 196/200, and 195/200, leaving large
train/held-out gaps of 49.22, 43.31, and 42.81 points. Regression was 47/64 for
base and 40/64, 41/64, and 48/64 for adapters; no seed crossed the greater-than-
15-point severe-collapse rule, though the first two had measurable drops.

All seven conjunctive confirmatory criteria passed. There were no post-freeze
protocol deviations and no failed training or evaluation runs. Phase 2B is a
confirmatory PASS and a GO for independent review of the bounded acquisition
claim. It does not authorize or establish continual learning, self-learning,
autonomous learning, human-like understanding, or general lifelong learning.

## Research records

- Phase 3A final report: `research/results/PHASE_3A/report.md`
- Phase 3A paired analysis: `research/results/PHASE_3A/analysis.json`
- Phase 3A frozen protocol and config: `research/protocols/phase3a_protocol.md`,
  `research/protocols/phase3a_config.json`

- Research question: `docs/research/RESEARCH_QUESTION.md`
- Hypotheses: `docs/research/HYPOTHESES.md`
- Methodology and reproducibility: `docs/research/METHODOLOGY.md`
- Claims ledger: `docs/research/CLAIMS_LEDGER.md`
- References: `docs/research/REFERENCES.md`
- Threats: `docs/research/THREATS_TO_VALIDITY.md`
- Experiment registry: `docs/research/EXPERIMENT_REGISTRY.md`
- Completed phase record: `docs/research/stages/PHASE_00.md`
- Completed Phase 1 record: `docs/research/stages/PHASE_01.md`
- Frozen Phase 1 protocol: `research/protocols/PHASE_01_FROZEN_BASELINE_RETRIEVAL_CEILING.md`
- Frozen Phase 1S protocol: `research/protocols/PHASE_1S_FROZEN_DIAGNOSTIC.md`
- Frozen Phase 1T protocol: `research/protocols/PHASE_1T_FROZEN_CONFIRMATION.md`
- Completed Phase 1S record: `docs/research/stages/PHASE_1S.md`
- Completed Phase 1T record: `docs/research/stages/PHASE_1T.md`
- Phase 2A record: `docs/research/stages/PHASE_2A.md`
- Frozen Phase 2B protocol: `research/protocols/PHASE_2B_FROZEN_CONFIRMATORY_EXPERIMENT.md`
- Phase 2B record: `docs/research/stages/PHASE_2B.md`
- Phase 1S compact summary: `research/results/PHASE_1S/summary.json`
- Phase 1T compact summary: `research/results/PHASE_1T/summary.json`
- Phase 2A compact summary: `research/results/PHASE_2A/summary.json`
- Phase 2B compact summary: `research/results/PHASE_2B/summary.json`
- Phase 2B final report: `research/results/PHASE_2B/report.md`
- Phase 2A adapter lineage: `research/manifests/phase2a_adapter_c0001.json`
- Raw evaluation: `research/results/EXP-0003-0004/phase1_evaluation.json`

## Resume instructions

Phase 3A is complete. Preserve Phase 1T as a failed gate, Phase 2A as an
exploratory pilot, and Phase 2B as bounded confirmatory acquisition evidence.
Do not tune against consumed suites, select a best seed, merge an adapter,
train on consumed tasks, or open the sealed holdout. Do not begin replay, EWC,
adapter isolation, STABLE, NoRA, gating, or any other anti-forgetting method.
The only next step is independent Phase 3A review. Any later experiment
requires explicit new authorization and a new preregistration.
