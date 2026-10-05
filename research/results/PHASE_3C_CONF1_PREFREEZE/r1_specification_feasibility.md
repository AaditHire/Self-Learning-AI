# CONF1 R1 non-model specification feasibility audit

Specification enumeration only; no compiler, model, training, evaluation or candidate construction.

Numeric enumeration: n=1..400, i=1..n. Array enumeration: i=0..3, x=-40..40.
Patterns are sorted lexicographically in the predicate orders recorded below.
Per-item functions are contribution vectors over those sorted feasible patterns.
The slot audits apply QR_FEASIBLE to G1/G3P; the 24-assignment enumeration omits that requirement.

## Input identities

| Artifact | SHA-256 (raw bytes) |
|---|---|
| `scripts/audit_phase3c_conf1_r1_specification_feasibility.py` | `7a30d1b733d2881fc806925e05c79c493582a65f36cd91dfdbe21ec0d124ca74` |
| `research/protocols/phase3c_conf1_slots.json` | `5fe76fbc02e9f65174327199c2004f7e51f19a7f3866ae15709744c5274415c2` |

## Feasible patterns

### numeric_iteration

Predicate order: odd_index, residue_two, divisor_index, first_half.
Feasible patterns: **16**.

```text
0000
0001
0010
0011
0100
0101
0110
0111
1000
1001
1010
1011
1100
1101
1110
1111
```

### array_reduction

Predicate order: negative_value, even_value, large_magnitude, value_exceeds_index.
Feasible patterns: **11**.

```text
0000
0001
0010
0011
0100
0101
0111
1000
1010
1100
1110
```

## Distinct non-degenerate functions over 24 assignments (without QR_FEASIBLE)

| Domain | G1 | G2 | G3 | G3P | G4 |
|---|---:|---:|---:|---:|---:|
| numeric_iteration | 12 | 12 | 4 | 12 | 24 |
| array_reduction | 8 | 6 | 2 | 8 | 12 |

## Frozen primary slots

| Slot | P,Q,R,S | Dead terms | Non-influential roles | Pair equality | Consumed equality | QR infeasible | Degenerate | Same-domain collisions |
|---|---|---|---|---|---|---|---|---|
| CONF1-NC-NU-G1-R0 | odd_index,residue_two,divisor_index,first_half | - | - | False | False | False | False | - |
| CONF1-NC-NU-G1-R1 | residue_two,divisor_index,first_half,odd_index | - | - | False | False | False | False | - |
| CONF1-NC-NU-G1-R2 | divisor_index,first_half,odd_index,residue_two | - | - | False | False | False | False | - |
| CONF1-NC-NU-G1-R3 | first_half,odd_index,residue_two,divisor_index | - | - | False | False | False | False | - |
| CONF1-NC-NU-G2-R0 | odd_index,residue_two,divisor_index,first_half | - | - | False | False | False | False | - |
| CONF1-NC-NU-G2-R1 | residue_two,divisor_index,first_half,odd_index | - | - | False | False | False | False | - |
| CONF1-NC-NU-G2-R2 | divisor_index,first_half,odd_index,residue_two | - | - | False | False | False | False | - |
| CONF1-NC-NU-G2-R3 | first_half,odd_index,residue_two,divisor_index | - | - | False | False | False | False | - |
| CONF1-NC-NU-G3-R0 | odd_index,residue_two,divisor_index,first_half | - | - | False | False | False | False | - |
| CONF1-NC-NU-G3-R1 | residue_two,divisor_index,first_half,odd_index | - | - | False | False | False | False | - |
| CONF1-NC-NU-G3-R2 | divisor_index,first_half,odd_index,residue_two | - | - | False | False | False | False | - |
| CONF1-NC-NU-G3-R3 | first_half,odd_index,residue_two,divisor_index | - | - | False | False | False | False | - |
| CONF1-NC-NU-G4-R0 | odd_index,residue_two,divisor_index,first_half | - | - | False | False | False | False | - |
| CONF1-NC-NU-G4-R1 | residue_two,divisor_index,first_half,odd_index | - | - | False | False | False | False | - |
| CONF1-NC-NU-G4-R2 | divisor_index,first_half,odd_index,residue_two | - | - | False | False | False | False | - |
| CONF1-NC-NU-G4-R3 | first_half,odd_index,residue_two,divisor_index | - | - | False | False | False | False | - |
| CONF1-NC-AR-G1-R0 | negative_value,even_value,large_magnitude,value_exceeds_index | - | - | False | False | False | False | - |
| CONF1-NC-AR-G1-R1 | even_value,large_magnitude,value_exceeds_index,negative_value | - | - | False | False | False | False | - |
| CONF1-NC-AR-G1-R2 | large_magnitude,value_exceeds_index,negative_value,even_value | - | - | False | False | True | True | - |
| CONF1-NC-AR-G1-R3 | value_exceeds_index,negative_value,even_value,large_magnitude | P&Q | Q | True | False | False | True | - |
| CONF1-NC-AR-G2-R0 | negative_value,even_value,large_magnitude,value_exceeds_index | - | - | False | False | False | False | - |
| CONF1-NC-AR-G2-R1 | even_value,large_magnitude,value_exceeds_index,negative_value | R&S | S | False | False | False | True | - |
| CONF1-NC-AR-G2-R2 | large_magnitude,value_exceeds_index,negative_value,even_value | Q&R | - | False | True | False | True | - |
| CONF1-NC-AR-G2-R3 | value_exceeds_index,negative_value,even_value,large_magnitude | P&Q | P | False | False | False | True | - |
| CONF1-NC-AR-G3-R0 | negative_value,even_value,large_magnitude,value_exceeds_index | P&S | S | False | False | False | True | - |
| CONF1-NC-AR-G3-R1 | even_value,large_magnitude,value_exceeds_index,negative_value | - | - | False | False | False | False | - |
| CONF1-NC-AR-G3-R2 | large_magnitude,value_exceeds_index,negative_value,even_value | - | - | False | False | False | False | - |
| CONF1-NC-AR-G3-R3 | value_exceeds_index,negative_value,even_value,large_magnitude | P&Q | Q | False | False | False | True | - |
| CONF1-NC-AR-G4-R0 | negative_value,even_value,large_magnitude,value_exceeds_index | - | - | False | False | False | False | - |
| CONF1-NC-AR-G4-R1 | even_value,large_magnitude,value_exceeds_index,negative_value | - | - | False | False | False | False | - |
| CONF1-NC-AR-G4-R2 | large_magnitude,value_exceeds_index,negative_value,even_value | - | - | False | True | False | True | - |
| CONF1-NC-AR-G4-R3 | value_exceeds_index,negative_value,even_value,large_magnitude | - | - | False | False | False | False | - |

### Per-item contribution vectors

| Slot | Function over sorted feasible patterns |
|---|---|
| CONF1-NC-NU-G1-R0 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]` |
| CONF1-NC-NU-G1-R1 | `[0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1]` |
| CONF1-NC-NU-G1-R2 | `[0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1]` |
| CONF1-NC-NU-G1-R3 | `[0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]` |
| CONF1-NC-NU-G2-R0 | `[0, 0, 0, 1, 0, 0, 1, 2, 0, 0, 0, 1, 1, 1, 2, 3]` |
| CONF1-NC-NU-G2-R1 | `[0, 0, 0, 1, 0, 0, 1, 2, 0, 1, 0, 2, 0, 1, 1, 3]` |
| CONF1-NC-NU-G2-R2 | `[0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 2, 1, 2, 1, 3]` |
| CONF1-NC-NU-G2-R3 | `[0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 2, 2, 3]` |
| CONF1-NC-NU-G3-R0 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 2, 2, 3]` |
| CONF1-NC-NU-G3-R1 | `[0, 0, 0, 0, 0, 1, 1, 2, 0, 0, 0, 0, 1, 2, 2, 3]` |
| CONF1-NC-NU-G3-R2 | `[0, 0, 0, 1, 0, 0, 1, 2, 0, 0, 1, 2, 0, 0, 2, 3]` |
| CONF1-NC-NU-G3-R3 | `[0, 0, 0, 1, 0, 1, 0, 2, 0, 1, 0, 2, 0, 2, 0, 3]` |
| CONF1-NC-NU-G4-R0 | `[0, 0, 0, 0, 0, 1, 1, 2, 0, 0, 1, 1, 0, 1, 1, 2]` |
| CONF1-NC-NU-G4-R1 | `[0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 2, 0, 1, 1, 2]` |
| CONF1-NC-NU-G4-R2 | `[0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 2, 1, 2]` |
| CONF1-NC-NU-G4-R3 | `[0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 2, 2]` |
| CONF1-NC-AR-G1-R0 | `[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]` |
| CONF1-NC-AR-G1-R1 | `[0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1]` |
| CONF1-NC-AR-G1-R2 | `[0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1]` |
| CONF1-NC-AR-G1-R3 | `[0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0]` |
| CONF1-NC-AR-G2-R0 | `[0, 0, 0, 1, 0, 0, 2, 0, 0, 1, 2]` |
| CONF1-NC-AR-G2-R1 | `[0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 1]` |
| CONF1-NC-AR-G2-R2 | `[0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1]` |
| CONF1-NC-AR-G2-R3 | `[0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 2]` |
| CONF1-NC-AR-G3-R0 | `[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2]` |
| CONF1-NC-AR-G3-R1 | `[0, 0, 0, 0, 0, 1, 2, 0, 0, 1, 2]` |
| CONF1-NC-AR-G3-R2 | `[0, 0, 0, 1, 0, 0, 2, 0, 1, 0, 2]` |
| CONF1-NC-AR-G3-R3 | `[0, 0, 0, 1, 0, 1, 2, 0, 0, 0, 0]` |
| CONF1-NC-AR-G4-R0 | `[0, 0, 0, 0, 0, 1, 2, 0, 1, 0, 1]` |
| CONF1-NC-AR-G4-R1 | `[0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1]` |
| CONF1-NC-AR-G4-R2 | `[0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1]` |
| CONF1-NC-AR-G4-R3 | `[0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 2]` |

## R1 proposed array primary slots

| Slot | P,Q,R,S | Dead terms | Non-influential roles | Pair equality | Consumed equality | QR infeasible | Degenerate | Same-domain collisions |
|---|---|---|---|---|---|---|---|---|
| CONF1-NC-AR-G1-R0 | negative_value,even_value,large_magnitude,- | - | - | False | False | False | False | - |
| CONF1-NC-AR-G1-R1 | even_value,negative_value,large_magnitude,- | - | - | False | False | False | False | - |
| CONF1-NC-AR-G1-R2 | large_magnitude,even_value,value_exceeds_index,- | - | - | False | False | False | False | - |
| CONF1-NC-AR-G1-R3 | value_exceeds_index,even_value,large_magnitude,- | - | - | False | False | False | False | - |
| CONF1-NC-AR-G2-R0 | negative_value,even_value,large_magnitude,value_exceeds_index | - | - | False | False | False | False | - |
| CONF1-NC-AR-G2-R1 | negative_value,even_value,value_exceeds_index,large_magnitude | - | - | False | False | False | False | - |
| CONF1-NC-AR-G2-R2 | even_value,negative_value,large_magnitude,value_exceeds_index | - | - | False | False | False | False | - |
| CONF1-NC-AR-G2-R3 | large_magnitude,negative_value,even_value,value_exceeds_index | - | - | False | False | False | False | - |
| CONF1-NC-AR-G3P-R0 | negative_value,even_value,large_magnitude,- | - | - | False | False | False | False | - |
| CONF1-NC-AR-G3P-R1 | even_value,large_magnitude,value_exceeds_index,- | - | - | False | False | False | False | - |
| CONF1-NC-AR-G3P-R2 | large_magnitude,negative_value,even_value,- | - | - | False | False | False | False | - |
| CONF1-NC-AR-G3P-R3 | value_exceeds_index,even_value,large_magnitude,- | - | - | False | False | False | False | - |
| CONF1-NC-AR-G4-R0 | negative_value,even_value,large_magnitude,value_exceeds_index | - | - | False | False | False | False | - |
| CONF1-NC-AR-G4-R1 | even_value,large_magnitude,negative_value,value_exceeds_index | - | - | False | False | False | False | - |
| CONF1-NC-AR-G4-R2 | large_magnitude,even_value,negative_value,value_exceeds_index | - | - | False | False | False | False | - |
| CONF1-NC-AR-G4-R3 | value_exceeds_index,even_value,large_magnitude,negative_value | - | - | False | False | False | False | - |

### Per-item contribution vectors

| Slot | Function over sorted feasible patterns |
|---|---|
| CONF1-NC-AR-G1-R0 | `[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]` |
| CONF1-NC-AR-G1-R1 | `[0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1]` |
| CONF1-NC-AR-G1-R2 | `[0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1]` |
| CONF1-NC-AR-G1-R3 | `[0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0]` |
| CONF1-NC-AR-G2-R0 | `[0, 0, 0, 1, 0, 0, 2, 0, 0, 1, 2]` |
| CONF1-NC-AR-G2-R1 | `[0, 0, 0, 1, 0, 1, 2, 0, 0, 1, 1]` |
| CONF1-NC-AR-G2-R2 | `[0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 2]` |
| CONF1-NC-AR-G2-R3 | `[0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 2]` |
| CONF1-NC-AR-G3P-R0 | `[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2]` |
| CONF1-NC-AR-G3P-R1 | `[0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 1]` |
| CONF1-NC-AR-G3P-R2 | `[0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 2]` |
| CONF1-NC-AR-G3P-R3 | `[0, 0, 0, 1, 0, 1, 2, 0, 0, 0, 0]` |
| CONF1-NC-AR-G4-R0 | `[0, 0, 0, 0, 0, 1, 2, 0, 1, 0, 1]` |
| CONF1-NC-AR-G4-R1 | `[0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1]` |
| CONF1-NC-AR-G4-R2 | `[0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1]` |
| CONF1-NC-AR-G4-R3 | `[0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 2]` |

### R1 array collision breakdown

| Slot | Within graph | Cross graph |
|---|---|---|
| CONF1-NC-AR-G1-R0 | - | - |
| CONF1-NC-AR-G1-R1 | - | - |
| CONF1-NC-AR-G1-R2 | - | - |
| CONF1-NC-AR-G1-R3 | - | - |
| CONF1-NC-AR-G2-R0 | - | - |
| CONF1-NC-AR-G2-R1 | - | - |
| CONF1-NC-AR-G2-R2 | - | - |
| CONF1-NC-AR-G2-R3 | - | - |
| CONF1-NC-AR-G3P-R0 | - | - |
| CONF1-NC-AR-G3P-R1 | - | - |
| CONF1-NC-AR-G3P-R2 | - | - |
| CONF1-NC-AR-G3P-R3 | - | - |
| CONF1-NC-AR-G4-R0 | - | - |
| CONF1-NC-AR-G4-R1 | - | - |
| CONF1-NC-AR-G4-R2 | - | - |
| CONF1-NC-AR-G4-R3 | - | - |

## Array DOMAIN_DISJOINT_PAIR training slots

Unordered pair: {negative_value, value_exceeds_index}.

- CONF1-TR-AR-03-V0
- CONF1-TR-AR-03-V1
- CONF1-TR-AR-03-V2
- CONF1-TR-AR-03-V3
- CONF1-TR-AR-03-V4

## Expected versus actual

| Check | Expected | Actual | Matched |
|---|---|---|---|
| feasible_pattern_counts | `{"array_reduction": 11, "numeric_iteration": 16}` | `{"array_reduction": 11, "numeric_iteration": 16}` | True |
| frozen_numeric_degenerate_slots | `[]` | `[]` | True |
| frozen_numeric_colliding_slots | `[]` | `[]` | True |
| frozen_array_dead_terms | `["G1R3", "G2R1", "G2R2", "G2R3", "G3R0", "G3R3"]` | `["G1R3", "G2R1", "G2R2", "G2R3", "G3R0", "G3R3"]` | True |
| frozen_array_equals_pair_fn | `["G1R3"]` | `["G1R3"]` | True |
| frozen_array_equals_consumed_fn | `["G2R2", "G4R2"]` | `["G2R2", "G4R2"]` | True |
| frozen_array_degenerate | `["G1R2", "G1R3", "G2R1", "G2R2", "G2R3", "G3R0", "G3R3", "G4R2"]` | `["G1R2", "G1R3", "G2R1", "G2R2", "G2R3", "G3R0", "G3R3", "G4R2"]` | True |
| array_reduction_non_degenerate_function_counts_without_QR | `{"G1": 8, "G2": 6, "G3": 2, "G3P": 8, "G4": 12}` | `{"G1": 8, "G2": 6, "G3": 2, "G3P": 8, "G4": 12}` | True |
| numeric_iteration_non_degenerate_function_counts_without_QR | `{"G1": 12, "G2": 12, "G3": 4, "G3P": 12, "G4": 24}` | `{"G1": 12, "G2": 12, "G3": 4, "G3P": 12, "G4": 24}` | True |
| r1_array_slot_count | `16` | `16` | True |
| r1_array_degenerate_slots | `[]` | `[]` | True |
| r1_array_colliding_slots | `[]` | `[]` | True |
| domain_disjoint_array_training_slots | `["CONF1-TR-AR-03-V0", "CONF1-TR-AR-03-V1", "CONF1-TR-AR-03-V2", "CONF1-TR-AR-03-V3", "CONF1-TR-AR-03-V4"]` | `["CONF1-TR-AR-03-V0", "CONF1-TR-AR-03-V1", "CONF1-TR-AR-03-V2", "CONF1-TR-AR-03-V3", "CONF1-TR-AR-03-V4"]` | True |

All expected results matched: True.
