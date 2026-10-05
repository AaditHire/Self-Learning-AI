# CONF1 re-baseline R1 — proposed amendment

## §1 Status

PROPOSED PROSPECTIVE AMENDMENT FOR PROJECT-HEAD REVIEW. Not frozen; confers no authority until a freeze manifest binds it. model_execution_authorized is not set. No CONF1 model outcome exists. The only evidence motivating R1 is non-model specification analysis: the specification coverage feasibility audit (commit 841f5ca) and the R1 specification feasibility audit committed with this amendment. DEV2R aggregate results are not used to set any R1 rule, threshold or population. Until R1 is frozen, the frozen documents listed in PROJECT_STATE §E remain the operative authorities, although they are known to be coverage-infeasible.

## §2 Construct and claim

ISOLATED trains, for a predicate pair (P,Q), a per-item contribution equal to the sum of two independently set indicators (hitP+hitQ). COMPOSITION trains the product of the same two indicators (hitP*hitQ), a joint pair count. Everything else is common and matched: the eight predicates, input decoders, indicator reset and set, total accumulation, initial offset, display, token and schedule budget, prompt wrapper. Paired programs are byte-identical outside the marked treatment expression and prompt clause. The evaluation preserves novelty at the level of arrangement: 3-4 predicate roles instead of 2, 2-3 accumulated terms instead of 1, a role shared across terms, OR built by two IF-set statements writing one indicator, a product with a composite indicator, and repeated predicate evaluation. A positive result supports only: pair-joint indicator-product practice transfers, relative to independent additive practice, to new multi-role multi-term counting programs built from that idiom, in GOCO, under this budget, with one base model (Level B). It does not support general compositional ability, any claim that joint practice beats conjunction-exposed independent practice (ISOLATED has no conjunction exposure, so a positive result partly reflects availability of the joint idiom), structural transfer, retention or continual learning.

## §3 Adopted decisions

A. T-JOINT (the product of two indicator variables inside the accumulated expression) is the one treatment-specific capability, COMPOSITION only. T-SUM (the sum of two indicator variables) is its ISOLATED counterpart. They are the only permitted asymmetric capabilities. No common conjunction exposure is added to either condition.

B. OR is not a capability. Canonical evaluation references realize OR as two IF-set statements writing the same indicator after one per-item reset. No Boolean operator (&&, ||, !), nested-IF conjunction or MUL other than a product of exactly two indicator variables appears in any canonical primary reference. No OR exposure is added to training. OR-containing graphs are G1 and G4.

C. Coverage unit: the catalog in §4. Offsets, predicate constants, input values, traversal direction beyond forward existence, spelling, rotation and slot identity are parameters and not coverage units. An evaluation statement kind absent from the catalog is a FAIL (fail closed).

D. Primitive Sanity is a secondary non-blocking qualifier (protocol §4 rule retained unchanged; the offset-3 variant is retained as a parameter). Structural Transfer (PREFIX, TWO_PASS) is exploratory descriptive: it has no coverage requirement and cannot invalidate or rescue the primary comparison.

E. Methodology machinery follows §9.

F. Primary array population is repaired per §7.

## §4 Capability catalog

Common rows (each must be live in both conditions' training unions, per domain):

| Common capability |
|---|
| K1 DECODE: numeric single nonnegative integer n; array four signed pipe-separated integers (split, to-number, indexed). |
| K2 FORWARD_TRAVERSAL: forward bounded index traversal over the domain's index range (numeric 1..n, array 0..3). |
| K3 PRED[p]: one row per domain predicate (4 per domain). |
| K4 INDICATOR_SET: per-item reset of an indicator to 0, then an IF whose true branch sets it to 1. |
| K5 ACCUMULATE: "total += <expression>" on an accumulator initialised to a nonnegative integer constant. In training the expression is the treatment expression (T-SUM or T-JOINT); in evaluation references it is as §5 states. |
| K6 DISPLAY: DISPLAYNL of the accumulator. |
| K7 OUTPUT_CLASS: ZERO = 0, POSITIVE = 1..9, MULTIDIGIT >= 10. Every output class of an evaluation task's expected outputs must also be present among that condition's training expected outputs in the same domain. |

Treatment rows: T-JOINT (COMPOSITION only; required by every primary canonical reference); T-SUM (ISOLATED only; required by no canonical evaluation reference).

Arrangement features (audited for novelty, not coverage rows): 3-4 indicator variables in one loop body; 2-3 accumulate statements per item; one indicator written by two IF-set statements (OR); product with a composite indicator; a predicate evaluated more than once; a role shared across terms.

| K3 row | Domain | Predicate |
|---|---|---|
| K3 PRED[odd_index] | numeric_iteration | odd_index |
| K3 PRED[residue_two] | numeric_iteration | residue_two |
| K3 PRED[divisor_index] | numeric_iteration | divisor_index |
| K3 PRED[first_half] | numeric_iteration | first_half |
| K3 PRED[negative_value] | array_reduction | negative_value |
| K3 PRED[even_value] | array_reduction | even_value |
| K3 PRED[large_magnitude] | array_reduction | large_magnitude |
| K3 PRED[value_exceeds_index] | array_reduction | value_exceeds_index |

## §5 Canonical-form rules

R-CF1 and R-CF2 apply to canonical PRIMARY EVALUATION references only. R-CF3 applies to training programs and primary canonical references. Training programs are governed by the frozen paired scaffold (protocol §6 and the retained paired-scaffold normalization): ISOLATED accumulates "total+=(hitP+hitQ)." (T-SUM) and COMPOSITION accumulates "total+=(hitP*hitQ)." (T-JOINT); R-CF1 does not apply to them.

R-CF1 One "total +=" statement per additive term; each term is a single indicator variable or a product of exactly two indicator variables.

R-CF2 OR per decision B. G1 canonical: composite indicator over Q,R (two IF-sets after one reset) multiplied by the P indicator. G4 canonical: composite indicator over P,Q multiplied by the R indicator, plus the product of the Q and S indicators.

R-CF3 No declared indicator that is never read; no statement kind outside §4.

R-CF4 Solvers (models) may emit any compile-valid program; coverage obligations are defined only on canonical references.

## §6 Gates

Primary-blocking gates (all must PASS before candidate acceptance; unresolved = FAIL; no post-candidate waiver):

P1 Ledger non-degeneracy (domain-aware). Evaluated on the slot functions of §7 and the frozen numeric slots using the definitions of the R1 feasibility audit (feasible patterns, live terms, influential roles, pair functions, consumed-template functions, QR_FEASIBLE for G1/G3P). Every primary slot must be non-degenerate and all 16 slots in a domain pairwise-distinct as per-item functions.

P2 E1: every training target and every primary reference compiles under the pinned compiler and matches all frozen cases.

P3 E3: paired-scaffold normalization (frozen), protocol §6/§12 budget parity: 60 programs per condition, 180 exposures, 24 optimizer steps, supervised-token difference <= 2%, full-token difference <= 5% relative to ISOLATED, no truncation at 320.

P4 Catalog and liveness: (i) conformance: every training program equals the frozen paired scaffold (E3) and parses into statement kinds of §4; every primary canonical reference parses into statement kinds of §4 and obeys §5 R-CF1-R-CF3; (ii) catalog inclusion: every K row required by an evaluation task is live in each condition's same-domain training union; forward traversal (K2) occurs in each union; (iii) deletion liveness: deleting any single executable statement of an example yields a mutant that fails to compile, times out, or produces different output on at least one of the example's five cases (such a mutant counts as killed; every mutant must be killed); (iv) witness: in each example, each predicate present is true on >=1 item and false on >=1 item across its cases, and each COMPOSITION example has >=1 item with both indicators 1; (v) treatment discrimination: paired ISOLATED/COMPOSITION canonical outputs differ on >=1 case. Exemption: the COMPOSITION members of slots flagged DOMAIN_DISJOINT_PAIR (§7) are exempt from (iii)-(v); their ISOLATED members are not; the exemption is recorded in a diagnostic report. Any other asymmetric capability beyond T-JOINT/T-SUM is FAIL.

P5 Function-level novelty (E5 simplified): all training and primary programs are instances of the template output = k + sum over items of c(pattern); the fixed offset k is recorded and normalized away. Each primary per-item function (domain-restricted) must differ from every training per-item function (P+Q and P*Q of every training pair) and from every consumed-template function, and must depend on >= 3 roles with >= 2 live terms.

P6 E6 hidden-case discrimination: the five cases of each primary task (a) separate that task from every other primary task of the same domain, (b) kill every single-statement-deletion mutant of its own canonical reference (killed as defined in P4(iii)), (c) cover the input-domain case classes retained in §9. Array primary case selection: the frozen 4096-tuple pool and ordering are retained; the greedy objective is (R1 clarification, superseding the frozen greedy objective for array primary cases) to maximize the number of satisfied (a)+(b) requirements, ties broken by lowest pool index; all requirements must be satisfied or STOP. Numeric primary cases remain the frozen five (0, 70, 12, 13, 14) and must satisfy (a)-(c) or STOP.

P7 E4: exact prompt, normalized-source and (stdin, expected-output) overlap against training and consumed suites follows the frozen candidate_policy: any match -> next deterministic candidate, else STOP.

Execution-time gate unchanged: acquisition gate (every one of 10 cells >= 54/60 semantic passes on its own training prompts, else INDETERMINATE_INSUFFICIENT_ACQUISITION).

Secondary rules (non-blocking): Sanity and Structural tasks face only E1 and E4-exact. A failing candidate -> next deterministic candidate; if candidates are exhausted the slot is dropped and recorded. If fewer than 12 of the 16 sanity tasks remain, the sanity qualifier is reported SANITY_NOT_EVALUABLE. Structural has no minimum. No secondary result or gate may block or alter the primary evaluation or label.

## §7 Primary ledger delta

Numeric primary slots are unchanged. Training slots are unchanged; the five array training slots CONF1-TR-AR-03-V0..V4 (pair {negative_value, value_exceeds_index}) are flagged DOMAIN_DISJOINT_PAIR (their COMPOSITION contribution is provably identically zero). Array primary role maps are replaced by the following table (role letters follow the ledger; "-" = role unused). Array G3 is replaced by G3P with contribution (P&Q)+(P&R). New IDs for G3P slots: CONF1-NC-AR-G3P-R0..R3, block_id array_reduction:G3P, composition_signature array_reduction:G3P:R0..R3. All other array primary IDs and block_ids are unchanged; the abbreviations are neg=negative_value, even=even_value, large=large_magnitude, exc=value_exceeds_index:

G1: R0 P=neg Q=even R=large S=-; R1 P=even Q=neg R=large S=-; R2 P=large Q=even R=exc S=-; R3 P=exc Q=even R=large S=-.

G2: R0 P=neg Q=even R=large S=exc; R1 P=neg Q=even R=exc S=large; R2 P=even Q=neg R=large S=exc; R3 P=large Q=neg R=even S=exc.

G3P: R0 P=neg Q=even R=large S=-; R1 P=even Q=large R=exc S=-; R2 P=large Q=neg R=even S=-; R3 P=exc Q=even R=large S=-.

G4: R0 P=neg Q=even R=large S=exc; R1 P=even Q=large R=neg S=exc; R2 P=large Q=even R=neg S=exc; R3 P=exc Q=even R=large S=neg.

| Graph | Rotation | P | Q | R | S |
|---|---|---|---|---|---|
| G1 | R0 | neg | even | large | - |
| G1 | R1 | even | neg | large | - |
| G1 | R2 | large | even | exc | - |
| G1 | R3 | exc | even | large | - |
| G2 | R0 | neg | even | large | exc |
| G2 | R1 | neg | even | exc | large |
| G2 | R2 | even | neg | large | exc |
| G2 | R3 | large | neg | even | exc |
| G3P | R0 | neg | even | large | - |
| G3P | R1 | even | large | exc | - |
| G3P | R2 | large | neg | even | - |
| G3P | R3 | exc | even | large | - |
| G4 | R0 | neg | even | large | exc |
| G4 | R1 | even | large | neg | exc |
| G4 | R2 | large | even | neg | exc |
| G4 | R3 | exc | even | large | neg |

```json
[
  {
    "task_id": "CONF1-NC-AR-G1-R0",
    "family": "array_reduction",
    "graph": "G1",
    "rotation": 0,
    "block_id": "array_reduction:G1",
    "role_predicates": {
      "P": "negative_value",
      "Q": "even_value",
      "R": "large_magnitude",
      "S": null
    },
    "composition_signature": "array_reduction:G1:R0"
  },
  {
    "task_id": "CONF1-NC-AR-G1-R1",
    "family": "array_reduction",
    "graph": "G1",
    "rotation": 1,
    "block_id": "array_reduction:G1",
    "role_predicates": {
      "P": "even_value",
      "Q": "negative_value",
      "R": "large_magnitude",
      "S": null
    },
    "composition_signature": "array_reduction:G1:R1"
  },
  {
    "task_id": "CONF1-NC-AR-G1-R2",
    "family": "array_reduction",
    "graph": "G1",
    "rotation": 2,
    "block_id": "array_reduction:G1",
    "role_predicates": {
      "P": "large_magnitude",
      "Q": "even_value",
      "R": "value_exceeds_index",
      "S": null
    },
    "composition_signature": "array_reduction:G1:R2"
  },
  {
    "task_id": "CONF1-NC-AR-G1-R3",
    "family": "array_reduction",
    "graph": "G1",
    "rotation": 3,
    "block_id": "array_reduction:G1",
    "role_predicates": {
      "P": "value_exceeds_index",
      "Q": "even_value",
      "R": "large_magnitude",
      "S": null
    },
    "composition_signature": "array_reduction:G1:R3"
  },
  {
    "task_id": "CONF1-NC-AR-G2-R0",
    "family": "array_reduction",
    "graph": "G2",
    "rotation": 0,
    "block_id": "array_reduction:G2",
    "role_predicates": {
      "P": "negative_value",
      "Q": "even_value",
      "R": "large_magnitude",
      "S": "value_exceeds_index"
    },
    "composition_signature": "array_reduction:G2:R0"
  },
  {
    "task_id": "CONF1-NC-AR-G2-R1",
    "family": "array_reduction",
    "graph": "G2",
    "rotation": 1,
    "block_id": "array_reduction:G2",
    "role_predicates": {
      "P": "negative_value",
      "Q": "even_value",
      "R": "value_exceeds_index",
      "S": "large_magnitude"
    },
    "composition_signature": "array_reduction:G2:R1"
  },
  {
    "task_id": "CONF1-NC-AR-G2-R2",
    "family": "array_reduction",
    "graph": "G2",
    "rotation": 2,
    "block_id": "array_reduction:G2",
    "role_predicates": {
      "P": "even_value",
      "Q": "negative_value",
      "R": "large_magnitude",
      "S": "value_exceeds_index"
    },
    "composition_signature": "array_reduction:G2:R2"
  },
  {
    "task_id": "CONF1-NC-AR-G2-R3",
    "family": "array_reduction",
    "graph": "G2",
    "rotation": 3,
    "block_id": "array_reduction:G2",
    "role_predicates": {
      "P": "large_magnitude",
      "Q": "negative_value",
      "R": "even_value",
      "S": "value_exceeds_index"
    },
    "composition_signature": "array_reduction:G2:R3"
  },
  {
    "task_id": "CONF1-NC-AR-G3P-R0",
    "family": "array_reduction",
    "graph": "G3P",
    "rotation": 0,
    "block_id": "array_reduction:G3P",
    "role_predicates": {
      "P": "negative_value",
      "Q": "even_value",
      "R": "large_magnitude",
      "S": null
    },
    "composition_signature": "array_reduction:G3P:R0"
  },
  {
    "task_id": "CONF1-NC-AR-G3P-R1",
    "family": "array_reduction",
    "graph": "G3P",
    "rotation": 1,
    "block_id": "array_reduction:G3P",
    "role_predicates": {
      "P": "even_value",
      "Q": "large_magnitude",
      "R": "value_exceeds_index",
      "S": null
    },
    "composition_signature": "array_reduction:G3P:R1"
  },
  {
    "task_id": "CONF1-NC-AR-G3P-R2",
    "family": "array_reduction",
    "graph": "G3P",
    "rotation": 2,
    "block_id": "array_reduction:G3P",
    "role_predicates": {
      "P": "large_magnitude",
      "Q": "negative_value",
      "R": "even_value",
      "S": null
    },
    "composition_signature": "array_reduction:G3P:R2"
  },
  {
    "task_id": "CONF1-NC-AR-G3P-R3",
    "family": "array_reduction",
    "graph": "G3P",
    "rotation": 3,
    "block_id": "array_reduction:G3P",
    "role_predicates": {
      "P": "value_exceeds_index",
      "Q": "even_value",
      "R": "large_magnitude",
      "S": null
    },
    "composition_signature": "array_reduction:G3P:R3"
  },
  {
    "task_id": "CONF1-NC-AR-G4-R0",
    "family": "array_reduction",
    "graph": "G4",
    "rotation": 0,
    "block_id": "array_reduction:G4",
    "role_predicates": {
      "P": "negative_value",
      "Q": "even_value",
      "R": "large_magnitude",
      "S": "value_exceeds_index"
    },
    "composition_signature": "array_reduction:G4:R0"
  },
  {
    "task_id": "CONF1-NC-AR-G4-R1",
    "family": "array_reduction",
    "graph": "G4",
    "rotation": 1,
    "block_id": "array_reduction:G4",
    "role_predicates": {
      "P": "even_value",
      "Q": "large_magnitude",
      "R": "negative_value",
      "S": "value_exceeds_index"
    },
    "composition_signature": "array_reduction:G4:R1"
  },
  {
    "task_id": "CONF1-NC-AR-G4-R2",
    "family": "array_reduction",
    "graph": "G4",
    "rotation": 2,
    "block_id": "array_reduction:G4",
    "role_predicates": {
      "P": "large_magnitude",
      "Q": "even_value",
      "R": "negative_value",
      "S": "value_exceeds_index"
    },
    "composition_signature": "array_reduction:G4:R2"
  },
  {
    "task_id": "CONF1-NC-AR-G4-R3",
    "family": "array_reduction",
    "graph": "G4",
    "rotation": 3,
    "block_id": "array_reduction:G4",
    "role_predicates": {
      "P": "value_exceeds_index",
      "Q": "even_value",
      "R": "large_magnitude",
      "S": "negative_value"
    },
    "composition_signature": "array_reduction:G4:R3"
  }
]
```

The primary count remains 32; the estimand, blocks (4 per domain, 4 tasks each) and bootstrap structure are unchanged.

The reason is recorded in the [R1 specification feasibility audit results](../results/PHASE_3C_CONF1_PREFREEZE/r1_specification_feasibility.json): 8 of 16 frozen array primary slots are degenerate (dead terms in G1R3, G2R1, G2R2, G2R3, G3R0, G3R3; G1R3 equals a pair function; G2R2 and G4R2 equal consumed-template functions; G1R2 has Q and R mutually exclusive so the OR is vacuous), and array G3 (star) admits only 2 non-degenerate slots. Numeric G3 (star) is retained because it is non-degenerate there.

## §8 Interpretation and reporting additions

Primary labels, estimand and thresholds are unchanged. Additional DESCRIPTIVE reporting, not decision-bearing: primary pass rate and paired difference for OR-containing blocks (G1,G4) versus OR-free blocks (G2, G3, G3P), by domain. If OR-containing blocks floor in both conditions, the limitation is stated; no label changes. Sanity qualification (mean difference >= -10 pp and no seed below -25 pp) is a qualifier only. Structural Transfer: rates and failure stages only; no threshold; no claim.

## §9 Supersession table

| File (under research/protocols/) | SHA-256 (raw bytes) | Git blob | Disposition |
|---|---|---|---|
| `phase3c_conf1_proposed_protocol.md` | `11e40c821fa26e5a687cea8b8a9a0aa5a0b0c388eae31c99de9814ab2bd80920` | `7ec58f3b4d5fc5827e35e4fbf22712a300240cec` | RETAINED; amended only by R1 §§3-8. |
| `phase3c_conf1_slots.json` | `5fe76fbc02e9f65174327199c2004f7e51f19a7f3866ae15709744c5274415c2` | `133c9c7275bcedeaf2474e54e61bae47923508ad` | RETAINED except §7 delta (R1 carries the delta; the file is not edited). |
| `phase3c_conf1_ast_adjudication_v2.md` | `962960ed6d766b574d2f9812b8ade5b5faa824acfe84e85b520636e2d6667fd9` | `c1ffc66d6b8a98645711cd77b6ff49fde5841deb` | DEMOTED to descriptive report (E2). |
| `phase3c_conf1_coverage_v3_proposed.md` | `a9fb8350c849ce62e2a673e3ca1f1d5a08f556b7f415687f1e2eabdf356030f3` | `16210d9810d217461b77546c3568c3344c0c770b` | SUPERSEDED for confirmatory purposes; retained concepts: prospective contract derived from the ledger, both-condition coverage with one declared treatment exception, fail closed, no post-candidate waiver. |
| `phase3c_conf1_coverage_v3_freeze.json` | `8d8f8a37c808d84c740867174e219803712213e672687c42164500f2bca12291` | `28c0fb52fba083e72f87ebfc530fd88ddded5f92` | SUPERSEDED for confirmatory purposes; retained concepts: prospective contract derived from the ledger, both-condition coverage with one declared treatment exception, fail closed, no post-candidate waiver. |
| `phase3c_conf1_coverage_v3_v2_disposition.md` | `fb8a385538ddebf95195f099b9ba933bde97d33faf86373a7611e532e8b637d2` | `511843b001f6827c2b46242155485eecc3e429d8` | SUPERSEDED for confirmatory purposes; retained concepts: prospective contract derived from the ledger, both-condition coverage with one declared treatment exception, fail closed, no post-candidate waiver. |
| `phase3c_conf1_coverage_v3_atomic_activity_output_amendment_proposed.md` | `8df78d2c96ccb9d6763999a6486202c1c6193bc3638b2c64421c386964cbaad6` | `c2e3041297d0e65246943b928054e3d6cce8af9f` | SUPERSEDED/HISTORICAL. |
| `phase3c_conf1_coverage_v3_atomic_activity_output_amendment_freeze.json` | `8a9bfe3c4ad3b687261f486189285156b4c1843e53bfbd20b0bc35c4f07d09e8` | `602b5593287c798e6da297917335795530530a33` | SUPERSEDED/HISTORICAL. |
| `phase3c_conf1_paired_scaffold_normalization_proposed.md` | `ef6063d39319d8b3bd3dbe6bdaa93b474217fa4c37d50ef43dfed5afc8da1fc0` | `475e9de4a0ef3bef23edac1e3631011a20790f5a` | RETAINED unchanged (E3). |
| `phase3c_conf1_paired_scaffold_normalization_freeze.json` | `ff1a9610b10ff559ac1859361fb7a31668210ed33e97c2864e592981bd9cfea2` | `9a54e9b525b1795b10f94bf0d0250ae831e6db74` | RETAINED unchanged (E3). |
| `phase3c_conf1_input_domain_case_classes_and_training_amendment_proposed.md` | `bb59ad7cf4cb22c2492427a1fa5a78b0d81398ab16fb0a9cb8229d8c9489182e` | `66467ef968e4963dd7a22568100a940871ad304c` | RETAINED for its case-class requirements. |
| `phase3c_conf1_input_domain_case_classes_and_training_amendment_freeze.json` | `de4a353d58515b5c53210664ea1a642731ac6f1734f23afef4ae512fb8c2627a` | `774eb73150f66d2545ddf270cc2f051eddedc156` | RETAINED for its case-class requirements. |
| `phase3c_conf1_structural_transfer_semantics_amendment_proposed.md` | `362c16faba42246344589fc7f46709b5b83e5bc829a13e1540b04392ddab2fba` | `eab80c50f3861438add2713689ee81fdbcdf38dd` | semantic task definitions RETAINED as descriptive exploratory definitions; all coverage/topology-key/graph-key clauses SUPERSEDED. |
| `phase3c_conf1_structural_transfer_topology_amendment_proposed.md` | `9a5e7e80502304e7281a924ef764f9a81b9edd0f9c65fc4a4e0007ad19a2aa2a` | `4f624b93d33decf3dd4643067693546fed32499d` | semantic task definitions RETAINED as descriptive exploratory definitions; all coverage/topology-key/graph-key clauses SUPERSEDED. |
| `phase3c_conf1_structural_transfer_pair_freeze.json` | `73eb1c29de6b258de6f7b83867e11ee3f53f67b513f550a666ede550b4e00aa5` | `cb643d992bac60db6a3ef208f1e690f6783ac4f6` | semantic task definitions RETAINED as descriptive exploratory definitions; all coverage/topology-key/graph-key clauses SUPERSEDED. |
| `phase3c_conf1_reference_only_catalog_proposed.md` | `7df2a31df6c995d0105e5547aa1d235c6046e9cf141f92321faf92cce3bac682` | `569ed951b121416b4c90240282d96231ce62c6e8` | SUPERSEDED (REMOVE_FROM_CONFIRMATORY_GATE). |
| `phase3c_conf1_reference_only_catalog_freeze.json` | `769eb09bf85440ac4baaaac90b074e282d87c9a9a5e2d0265aedc17f6c46f7ce` | `a5781769519f8432c795de0290aa3d15d3722c07` | SUPERSEDED (REMOVE_FROM_CONFIRMATORY_GATE). |
| `phase3c_conf1_reference_only_interface_clarification_proposed_v2.md` | `7a8b69e208bb0a5406cbce0515c4ff95e37aa2d3d8d8e493cda6df5783a2cf25` | `e6e12aedf658698a5dd1975894b6e4e7299bd171` | SUPERSEDED (REMOVE_FROM_CONFIRMATORY_GATE). |
| `phase3c_conf1_reference_only_interface_clarification_v2_freeze.json` | `aa8cc827a5c171b388220b0382713982d7a981b6e73b071a2dd12c2cf50ed5ab` | `7aa3ca18fe4df6823278e3dbd82eaa6bebfc8e6b` | SUPERSEDED (REMOVE_FROM_CONFIRMATORY_GATE). |
| `phase3c_conf1_canonical_contract_graph_recipe_proposed_v2.md` | `067401333940664502bada12b41d591ef1f554680ba5c9062954b5280e3fd272` | `e01d56046711365e3369a7fad67591b1476c4d15` | SUPERSEDED (replaced by §4-§6). |
| `phase3c_conf1_canonical_contract_graph_recipe_v2_freeze.json` | `274c3e39d9dada9939e87c67f72aa71e8a2514ad9a84d35327ac0f6b711c2a51` | `14976b41c8e5e8dba915147fd3a379e891daa7bb` | SUPERSEDED (replaced by §4-§6). |
| `phase3c_conf1_delegated_evidence_interfaces_proposed.md` | `9c684eaf6b0099080ddf907630b0a2f8e176e3a882b67875d82f07bd82d64dc5` | `1b6d4d1a825bf9e9d288ca9c3815d1a8e7c78d1a` | SUPERSEDED/HISTORICAL; evidence reports are plain hashed JSON. |
| `phase3c_conf1_delegated_evidence_interfaces_freeze.json` | `bd7a7fc6862ce049c1fdf363f763e1a3a17808132291b9064e3c6f26fb720948` | `32595c5c563fa262679f2bf93ae789f04cde7f72` | SUPERSEDED/HISTORICAL; evidence reports are plain hashed JSON. |
| `phase3c_conf1_delegated_evidence_interfaces_binding_amendment_proposed.md` | `2b045a0fb5a7dd22d54397700bab47b88b6857a1ce9b0e22e5f1f5c1ff94595c` | `92edf8305f989f9dce55fa26f4f68ef5e661a3c6` | SUPERSEDED/HISTORICAL; evidence reports are plain hashed JSON. |
| `phase3c_conf1_delegated_evidence_interfaces_binding_amendment_freeze.json` | `0257f8eac42265265f9f88b53633e56c7f9b9c6918f53988675cdcb84bd6de7d` | `23d8b3370b26ceec6a076f1061778fa43dad7100` | SUPERSEDED/HISTORICAL; evidence reports are plain hashed JSON. |
| `phase3c_conf1_direct_support_accounting_amendment_proposed_v2.md` | `1d2e5b5417a2ebadccc159e92a6c45737ae239666cf14b3b5d3962d250dd1e06` | `dd9556076ec906eff7be0c35ae11f7c73fc8d944` | SUPERSEDED (REMOVE_FROM_CONFIRMATORY_GATE). |
| `phase3c_conf1_direct_support_accounting_amendment_v2_freeze.json` | `1afa76f58bdf35601488f390e17708a62ed156e2dd0c38e59d82f3fbd3879e26` | `46d3e0b4bfddbef96a8247e69ddef7b3ef4c126d` | SUPERSEDED (REMOVE_FROM_CONFIRMATORY_GATE). |
| `phase3c_conf1_canonical_graph_v2_wire_format_binding_amendment_proposed.md` | `5891e4002696a4715e977952375bd56ca2edff0b7d3d66f6c312766de26f5a3c` | `c10b5ab107208da9847a67daa1fc6b5e442a6ce5` | REJECTED; never frozen. |

Attempts 001-003: HISTORICAL; src/self_learning_ai/conf1_v3/: non-authoritative.

### Retained numeric case-class list

| Class | Membership on valid decoded input | Status and reason |
|---|---|---|
| `SIGN_ZERO` | `n == 0` | `REQUIRED` |
| `SIGN_POSITIVE` | `n > 0` | `REQUIRED` |
| `EMPTY_LOOP` | `n == 0` | `REQUIRED`: frozen numeric traversal covers positions `1..n`, hence zero body iterations |
| `LOWER_DOMAIN_BOUNDARY` | `n == 0` | `REQUIRED`: zero is the lower bound of nonnegative integers |
| Negative-sign class | `n < 0` | `NOT_APPLICABLE`: invalid input |
| Upper-domain boundary | — | `NOT_APPLICABLE`: no finite upper bound is declared for the valid input domain |

### Retained array case-class list

| Class | Membership on valid decoded input | Status |
|---|---|---|
| `NEGATIVE_PRESENT` | At least one of four elements `< 0` | `REQUIRED` |
| `ZERO_PRESENT` | At least one of four elements `== 0` | `REQUIRED` |
| `POSITIVE_PRESENT` | At least one of four elements `> 0` | `REQUIRED` |
| `EMPTY` | No valid member | `NOT_APPLICABLE`: every valid input has exactly four numeric fields |
| `BOUNDARY` | No finite numeric input-domain endpoint is declared | `NOT_APPLICABLE` |

## §10 Unchanged elements

fresh rank-16 NF4 QLoRA adapters from the same pinned base and recipe (180 exposures, 24 optimizer steps, max length 320); five paired seeds 20280117, 20280223, 20280329, 20280411, 20280507, all primary; no retries; one greedy generation; matched budget and the 2%/5% token limits; acquisition gate (10 cells, >= 54/60); primary endpoint (mean paired COMPOSITION - ISOLATED pass@1 over the 32 primary tasks); CONFIRMATORY_SUPPORT_UNDER_CONF1 requires >= +20 pp and a 95% bootstrap lower bound > 0 (10,000 replicates, RNG seed 20290119, resampling seeds and whole blocks within domain); consumed-suite and sealed-holdout boundaries; Level B claim ceiling; model_execution_authorized absent until a separate authorized commit.

## §11 Rule-change ledger

| # | Scientific change | Classification |
|---|---|---|
| 1 | coverage semantics: catalog replaces typed keys | SCIENTIFIC |
| 2 | OR as arrangement | SCIENTIFIC |
| 3 | activity evidence replaced by §6 P4 | SCIENTIFIC |
| 4 | Sanity/Structural leave coverage gating, Structural drop rule | SCIENTIFIC |
| 5 | novelty function-level, E2 descriptive | SCIENTIFIC |
| 6 | array primary role-map repair and G3P substitution | SCIENTIFIC |
| 7 | array primary case-selection objective clarification | SCIENTIFIC |
| 8 | added descriptive OR split | SCIENTIFIC |
| 9 | removal of B1/D2/RO/wire machinery | SCIENTIFIC |

## §12 Alternatives considered and rejected

Decision A: common conjunction exposure - rejected (needs new training, changes the budget, blurs the contrast). Decision B: matched OR exposure - rejected (new training programs); dropping OR graphs - rejected (loses two of four families). Decision D: removing Structural - acceptable but not adopted. Decision F: dropping array G3 - rejected (unequal blocks, changes the estimand); substituting G3P in both domains - rejected (numeric star is non-degenerate; minimal change).

## §13 Evidence pointers

Evidence committed in `a75d62a4dc983f6abe7604c42b4841003440145b`.

| Path | SHA-256 (raw bytes) |
|---|---|
| `scripts/audit_phase3c_conf1_r1_specification_feasibility.py` | `7a30d1b733d2881fc806925e05c79c493582a65f36cd91dfdbe21ec0d124ca74` |
| `research/results/PHASE_3C_CONF1_PREFREEZE/r1_specification_feasibility.json` | `8342103fe1ce769ced87ec20b0d8ba05a733df9d1080f1d9e5b6d2b644003cf9` |
| `research/results/PHASE_3C_CONF1_PREFREEZE/r1_specification_feasibility.md` | `2c401dc9f6798f5e9e294319cc60ad6e52155b5b93fbe6efddfb11a1ca36cd30` |
