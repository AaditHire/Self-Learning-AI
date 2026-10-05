# CONF1 R2 non-model liveness-feasibility evidence

Evidence only. No methodology change, candidate construction or model use.

DOMAIN_EQUIVALENT below means equality on the task's exhaustive finite input sets; numeric n>200 and array values outside -5..5 were not exhaustively executed.

Source HEAD: `6192040a7c275a10f369461600070bd56d885130`. Interpreter caching crosscheck: {'comparisons': 3184, 'disagreements': 0}. Patterns: PASS.

## E1 equivalent mutants

| Kind | Slot | Condition | Mutant | Deleted statement | Compiler cases |
|---|---|---|---:|---|---:|
| primary | CONF1-NC-AR-G1-R3 | primary | 14 | `hitOr=0.` | 20 PASS |
| training | CONF1-TR-NU-03-V0 | isolated | 7 | `hitP=0.` | 20 PASS |
| training | CONF1-TR-NU-03-V0 | composition | 7 | `hitP=0.` | 20 PASS |
| training | CONF1-TR-NU-03-V2 | isolated | 7 | `hitP=0.` | 20 PASS |
| training | CONF1-TR-NU-03-V2 | composition | 7 | `hitP=0.` | 20 PASS |
| training | CONF1-TR-NU-03-V4 | isolated | 7 | `hitP=0.` | 20 PASS |
| training | CONF1-TR-NU-03-V4 | composition | 7 | `hitP=0.` | 20 PASS |
| training | CONF1-TR-NU-13-V1 | isolated | 7 | `hitP=0.` | 20 PASS |
| training | CONF1-TR-NU-13-V1 | composition | 7 | `hitP=0.` | 20 PASS |
| training | CONF1-TR-NU-13-V3 | isolated | 7 | `hitP=0.` | 20 PASS |
| training | CONF1-TR-NU-13-V3 | composition | 7 | `hitP=0.` | 20 PASS |
| training | CONF1-TR-NU-23-V0 | isolated | 8 | `hitQ=0.` | 20 PASS |
| training | CONF1-TR-NU-23-V0 | composition | 8 | `hitQ=0.` | 20 PASS |
| training | CONF1-TR-NU-23-V2 | isolated | 8 | `hitQ=0.` | 20 PASS |
| training | CONF1-TR-NU-23-V2 | composition | 8 | `hitQ=0.` | 20 PASS |
| training | CONF1-TR-NU-23-V4 | isolated | 8 | `hitQ=0.` | 20 PASS |
| training | CONF1-TR-NU-23-V4 | composition | 8 | `hitQ=0.` | 20 PASS |
| training | CONF1-TR-AR-03-V0 | composition | 13 | `LOOP (i>=0) { hitP=0. hitQ=0. IF (values[i]>i) { hitP=1. } IF (values[i]<0) { hitQ=1. } total+=(hitP*hitQ). i-=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V0 | composition | 16 | `IF (values[i]>i) { hitP=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V0 | composition | 17 | `hitP=1.` | 20 PASS |
| training | CONF1-TR-AR-03-V0 | composition | 18 | `IF (values[i]<0) { hitQ=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V0 | composition | 19 | `hitQ=1.` | 20 PASS |
| training | CONF1-TR-AR-03-V0 | composition | 20 | `total+=(hitP*hitQ).` | 20 PASS |
| training | CONF1-TR-AR-03-V1 | composition | 12 | `LOOP (NUMBER i=0 TILL i<4, i++) { hitP=0. hitQ=0. IF (values[i]<0) { hitP=1. } IF (values[i]>i) { hitQ=1. } total+=(hitP*hitQ). }` | 20 PASS |
| training | CONF1-TR-AR-03-V1 | composition | 15 | `IF (values[i]<0) { hitP=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V1 | composition | 16 | `hitP=1.` | 20 PASS |
| training | CONF1-TR-AR-03-V1 | composition | 17 | `IF (values[i]>i) { hitQ=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V1 | composition | 18 | `hitQ=1.` | 20 PASS |
| training | CONF1-TR-AR-03-V1 | composition | 19 | `total+=(hitP*hitQ).` | 20 PASS |
| training | CONF1-TR-AR-03-V2 | composition | 13 | `LOOP (i>=0) { hitP=0. hitQ=0. IF (values[i]>i) { hitP=1. } IF (values[i]<0) { hitQ=1. } total+=(hitP*hitQ). i-=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V2 | composition | 16 | `IF (values[i]>i) { hitP=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V2 | composition | 17 | `hitP=1.` | 20 PASS |
| training | CONF1-TR-AR-03-V2 | composition | 18 | `IF (values[i]<0) { hitQ=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V2 | composition | 19 | `hitQ=1.` | 20 PASS |
| training | CONF1-TR-AR-03-V2 | composition | 20 | `total+=(hitP*hitQ).` | 20 PASS |
| training | CONF1-TR-AR-03-V3 | composition | 12 | `LOOP (NUMBER i=0 TILL i<4, i++) { hitP=0. hitQ=0. IF (values[i]<0) { hitP=1. } IF (values[i]>i) { hitQ=1. } total+=(hitP*hitQ). }` | 20 PASS |
| training | CONF1-TR-AR-03-V3 | composition | 15 | `IF (values[i]<0) { hitP=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V3 | composition | 16 | `hitP=1.` | 20 PASS |
| training | CONF1-TR-AR-03-V3 | composition | 17 | `IF (values[i]>i) { hitQ=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V3 | composition | 18 | `hitQ=1.` | 20 PASS |
| training | CONF1-TR-AR-03-V3 | composition | 19 | `total+=(hitP*hitQ).` | 20 PASS |
| training | CONF1-TR-AR-03-V4 | composition | 13 | `LOOP (i>=0) { hitP=0. hitQ=0. IF (values[i]>i) { hitP=1. } IF (values[i]<0) { hitQ=1. } total+=(hitP*hitQ). i-=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V4 | composition | 16 | `IF (values[i]>i) { hitP=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V4 | composition | 17 | `hitP=1.` | 20 PASS |
| training | CONF1-TR-AR-03-V4 | composition | 18 | `IF (values[i]<0) { hitQ=1. }` | 20 PASS |
| training | CONF1-TR-AR-03-V4 | composition | 19 | `hitQ=1.` | 20 PASS |
| training | CONF1-TR-AR-03-V4 | composition | 20 | `total+=(hitP*hitQ).` | 20 PASS |

Prediction and compiler confirmation:

```json
{
  "prediction": {
    "primary_expected": [
      [
        "CONF1-NC-AR-G1-R3",
        14
      ]
    ],
    "primary_actual": [
      [
        "CONF1-NC-AR-G1-R3",
        14
      ]
    ],
    "primary_match": true,
    "training_nonexempt_expected": [
      [
        "CONF1-TR-NU-03-V0",
        "composition",
        7
      ],
      [
        "CONF1-TR-NU-03-V0",
        "isolated",
        7
      ],
      [
        "CONF1-TR-NU-03-V2",
        "composition",
        7
      ],
      [
        "CONF1-TR-NU-03-V2",
        "isolated",
        7
      ],
      [
        "CONF1-TR-NU-03-V4",
        "composition",
        7
      ],
      [
        "CONF1-TR-NU-03-V4",
        "isolated",
        7
      ],
      [
        "CONF1-TR-NU-13-V1",
        "composition",
        7
      ],
      [
        "CONF1-TR-NU-13-V1",
        "isolated",
        7
      ],
      [
        "CONF1-TR-NU-13-V3",
        "composition",
        7
      ],
      [
        "CONF1-TR-NU-13-V3",
        "isolated",
        7
      ],
      [
        "CONF1-TR-NU-23-V0",
        "composition",
        8
      ],
      [
        "CONF1-TR-NU-23-V0",
        "isolated",
        8
      ],
      [
        "CONF1-TR-NU-23-V2",
        "composition",
        8
      ],
      [
        "CONF1-TR-NU-23-V2",
        "isolated",
        8
      ],
      [
        "CONF1-TR-NU-23-V4",
        "composition",
        8
      ],
      [
        "CONF1-TR-NU-23-V4",
        "isolated",
        8
      ]
    ],
    "training_nonexempt_actual": [
      [
        "CONF1-TR-NU-03-V0",
        "composition",
        7
      ],
      [
        "CONF1-TR-NU-03-V0",
        "isolated",
        7
      ],
      [
        "CONF1-TR-NU-03-V2",
        "composition",
        7
      ],
      [
        "CONF1-TR-NU-03-V2",
        "isolated",
        7
      ],
      [
        "CONF1-TR-NU-03-V4",
        "composition",
        7
      ],
      [
        "CONF1-TR-NU-03-V4",
        "isolated",
        7
      ],
      [
        "CONF1-TR-NU-13-V1",
        "composition",
        7
      ],
      [
        "CONF1-TR-NU-13-V1",
        "isolated",
        7
      ],
      [
        "CONF1-TR-NU-13-V3",
        "composition",
        7
      ],
      [
        "CONF1-TR-NU-13-V3",
        "isolated",
        7
      ],
      [
        "CONF1-TR-NU-23-V0",
        "composition",
        8
      ],
      [
        "CONF1-TR-NU-23-V0",
        "isolated",
        8
      ],
      [
        "CONF1-TR-NU-23-V2",
        "composition",
        8
      ],
      [
        "CONF1-TR-NU-23-V2",
        "isolated",
        8
      ],
      [
        "CONF1-TR-NU-23-V4",
        "composition",
        8
      ],
      [
        "CONF1-TR-NU-23-V4",
        "isolated",
        8
      ]
    ],
    "training_nonexempt_match": true,
    "training_missing": [],
    "training_unexpected": []
  },
  "compiler": {
    "equivalent_mutants": 47,
    "comparisons": 940,
    "distinct_compiler_runs": 1380,
    "disagreements": 0,
    "wall_seconds": 59.573
  }
}
```

## E2 frozen-rule synthetic simulations

Counts are failed programs for P4(iii)/(iv), failed matched pairs for P4(v); unmet requirements are also recorded. All slot inputs, outputs and failures are in the JSON.

| Seed | iii programs / mutants | iv programs / requirements | v pairs | Array skips (duplicate / eval) |
|---:|---:|---:|---:|---:|
| 900001 | 8 / 8 | 0 / 0 | 0 | 0 / 0 |

Seed 900001 examples:

```json
[
  {
    "slot": "CONF1-TR-AR-01-V2",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 14,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V3",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V4",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  }
]
```

| 900002 | 9 / 9 | 0 / 0 | 0 | 0 / 0 |

Seed 900002 examples:

```json
[
  {
    "slot": "CONF1-TR-AR-02-V2",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V3",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-03-V0",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "isolated",
        "mutant_index": 14,
        "deleted_statement": "hitP=0."
      }
    ]
  }
]
```

| 900003 | 10 / 10 | 0 / 0 | 0 | 0 / 0 |

Seed 900003 examples:

```json
[
  {
    "slot": "CONF1-TR-AR-02-V0",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V2",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V3",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  }
]
```

| 900004 | 14 / 15 | 2 / 2 | 0 | 0 / 0 |

Seed 900004 examples:

```json
[
  {
    "slot": "CONF1-TR-AR-01-V0",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 14,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-01-V1",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 14,
        "deleted_statement": "hitQ=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V0",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  }
]
```

| 900005 | 9 / 9 | 0 / 0 | 0 | 0 / 0 |

Seed 900005 examples:

```json
[
  {
    "slot": "CONF1-TR-AR-01-V0",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V0",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V1",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  }
]
```

| 900006 | 11 / 11 | 0 / 0 | 0 | 0 / 0 |

Seed 900006 examples:

```json
[
  {
    "slot": "CONF1-TR-AR-01-V3",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V0",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V1",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  }
]
```

| 900007 | 11 / 11 | 0 / 0 | 0 | 0 / 0 |

Seed 900007 examples:

```json
[
  {
    "slot": "CONF1-TR-NU-02-V3",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 7,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V1",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V3",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  }
]
```

| 900008 | 10 / 10 | 2 / 2 | 0 | 0 / 0 |

Seed 900008 examples:

```json
[
  {
    "slot": "CONF1-TR-AR-01-V2",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V2",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V3",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  }
]
```

| 900009 | 9 / 9 | 2 / 2 | 0 | 0 / 0 |

Seed 900009 examples:

```json
[
  {
    "slot": "CONF1-TR-AR-02-V1",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V3",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-12-V1",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  }
]
```

| 900010 | 7 / 7 | 0 / 0 | 0 | 0 / 0 |

Seed 900010 examples:

```json
[
  {
    "slot": "CONF1-TR-NU-02-V1",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 7,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V2",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "isolated",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      },
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V3",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  }
]
```

| 900011 | 11 / 11 | 0 / 0 | 0 | 0 / 0 |

Seed 900011 examples:

```json
[
  {
    "slot": "CONF1-TR-AR-01-V3",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "isolated",
        "mutant_index": 14,
        "deleted_statement": "hitQ=0."
      },
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 14,
        "deleted_statement": "hitQ=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-01-V4",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V1",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  }
]
```

| 900012 | 11 / 11 | 0 / 0 | 0 | 0 / 0 |

Seed 900012 examples:

```json
[
  {
    "slot": "CONF1-TR-AR-01-V0",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 14,
        "deleted_statement": "hitP=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-01-V4",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 15,
        "deleted_statement": "hitQ=0."
      }
    ]
  },
  {
    "slot": "CONF1-TR-AR-02-V0",
    "unmet": [
      {
        "gate": "P4(iii)",
        "condition": "composition",
        "mutant_index": 13,
        "deleted_statement": "hitP=0."
      }
    ]
  }
]
```

## E3 kill-directed synthetic simulations

Each seed's full unmet list follows. Per-slot timings, cases, stream indices, cumulative scores and skips are in the JSON; summed worker times are not elapsed wall time.

Seed 900001: wall time 24.877 s; skips {'duplicate': 2, 'synthetic_evaluation_input': 0, 'total': 2}; summed slot time 183.869 s; maximum slot time 10.479 s.

```json
[]
```

Seed 900002: wall time 25.356 s; skips {'duplicate': 0, 'synthetic_evaluation_input': 0, 'total': 0}; summed slot time 187.919 s; maximum slot time 10.246 s.

```json
[]
```

Seed 900003: wall time 23.978 s; skips {'duplicate': 2, 'synthetic_evaluation_input': 1, 'total': 3}; summed slot time 176.833 s; maximum slot time 9.823 s.

```json
[]
```

Seed 900004: wall time 23.567 s; skips {'duplicate': 1, 'synthetic_evaluation_input': 0, 'total': 1}; summed slot time 174.181 s; maximum slot time 9.973 s.

```json
[]
```

Seed 900005: wall time 24.195 s; skips {'duplicate': 0, 'synthetic_evaluation_input': 0, 'total': 0}; summed slot time 179.163 s; maximum slot time 10.239 s.

```json
[]
```

## E4 output classes and K7

| Seed | Domain | Condition | Primary | Training | K7 |
|---:|---|---|---|---|---|
| 900001 | numeric_iteration | isolated | ZERO, POSITIVE, MULTIDIGIT | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900001 | numeric_iteration | composition | ZERO, POSITIVE, MULTIDIGIT | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900001 | array_reduction | isolated | ZERO, POSITIVE | POSITIVE, MULTIDIGIT | FAIL |
| 900001 | array_reduction | composition | ZERO, POSITIVE | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900002 | numeric_iteration | isolated | ZERO, POSITIVE, MULTIDIGIT | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900002 | numeric_iteration | composition | ZERO, POSITIVE, MULTIDIGIT | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900002 | array_reduction | isolated | ZERO, POSITIVE | POSITIVE, MULTIDIGIT | FAIL |
| 900002 | array_reduction | composition | ZERO, POSITIVE | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900003 | numeric_iteration | isolated | ZERO, POSITIVE, MULTIDIGIT | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900003 | numeric_iteration | composition | ZERO, POSITIVE, MULTIDIGIT | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900003 | array_reduction | isolated | ZERO, POSITIVE | POSITIVE, MULTIDIGIT | FAIL |
| 900003 | array_reduction | composition | ZERO, POSITIVE | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900004 | numeric_iteration | isolated | ZERO, POSITIVE, MULTIDIGIT | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900004 | numeric_iteration | composition | ZERO, POSITIVE, MULTIDIGIT | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900004 | array_reduction | isolated | ZERO, POSITIVE | POSITIVE, MULTIDIGIT | FAIL |
| 900004 | array_reduction | composition | ZERO, POSITIVE | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900005 | numeric_iteration | isolated | ZERO, POSITIVE, MULTIDIGIT | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900005 | numeric_iteration | composition | ZERO, POSITIVE, MULTIDIGIT | ZERO, POSITIVE, MULTIDIGIT | PASS |
| 900005 | array_reduction | isolated | ZERO, POSITIVE | POSITIVE, MULTIDIGIT | FAIL |
| 900005 | array_reduction | composition | ZERO, POSITIVE | ZERO, POSITIVE, MULTIDIGIT | PASS |

## E5 fixed I2 synthetic primary selection with equivalent exclusion

```json
{
  "inputs": [
    "0|0|0|0",
    "-14|16|-2|-15",
    "12|2|-1|5",
    "-16|-10|7|2",
    "-14|6|-6|4"
  ],
  "original_r1_status": "FAIL",
  "original_satisfied": 567,
  "original_total": 568,
  "compiler_runs": 2250,
  "wall_seconds": 105.131,
  "excluded": [
    [
      "CONF1-NC-AR-G1-R3",
      14
    ]
  ],
  "satisfied": 567,
  "total": 567,
  "unseparated_pairs": [],
  "remaining_unkilled": [],
  "case_classes": {
    "status": "PASS",
    "witnesses": {
      "NEGATIVE_PRESENT": [
        {
          "case": 1,
          "element_index": 0,
          "value": -14
        },
        {
          "case": 1,
          "element_index": 2,
          "value": -2
        },
        {
          "case": 1,
          "element_index": 3,
          "value": -15
        },
        {
          "case": 2,
          "element_index": 2,
          "value": -1
        },
        {
          "case": 3,
          "element_index": 0,
          "value": -16
        },
        {
          "case": 3,
          "element_index": 1,
          "value": -10
        },
        {
          "case": 4,
          "element_index": 0,
          "value": -14
        },
        {
          "case": 4,
          "element_index": 2,
          "value": -6
        }
      ],
      "ZERO_PRESENT": [
        {
          "case": 0,
          "element_index": 0,
          "value": 0
        },
        {
          "case": 0,
          "element_index": 1,
          "value": 0
        },
        {
          "case": 0,
          "element_index": 2,
          "value": 0
        },
        {
          "case": 0,
          "element_index": 3,
          "value": 0
        }
      ],
      "POSITIVE_PRESENT": [
        {
          "case": 1,
          "element_index": 1,
          "value": 16
        },
        {
          "case": 2,
          "element_index": 0,
          "value": 12
        },
        {
          "case": 2,
          "element_index": 1,
          "value": 2
        },
        {
          "case": 2,
          "element_index": 3,
          "value": 5
        },
        {
          "case": 3,
          "element_index": 2,
          "value": 7
        },
        {
          "case": 3,
          "element_index": 3,
          "value": 2
        },
        {
          "case": 4,
          "element_index": 1,
          "value": 6
        },
        {
          "case": 4,
          "element_index": 3,
          "value": 4
        }
      ]
    },
    "missing": [],
    "invalid_cases": []
  },
  "prediction_match": true,
  "interpretation": "Evidence-only equivalent exclusion; frozen R1 is unchanged."
}
```

## Timings and boundaries

```json
{
  "e1_exhaustive_wall_seconds": 1329.806,
  "e1_compiler_wall_seconds": 59.573,
  "e2_e3_combined_wall_seconds": 133.399,
  "total_audit_wall_seconds": 1631.055,
  "workers": 8,
  "budget_seconds": 5800.0
}
```

Only authorized synthetic seeds were drawn. Numeric training excludes exactly 12,13,14; array training streams exclude SYN_ARRAY_EVAL and their own accepted duplicates. The canonical numeric E3 zero has no stream index. Each condition has separate witness requirements; treatment discrimination is one requirement per matched pair. DOMAIN_DISJOINT COMPOSITION is exempt from P4(iii)-(v), and E1 equivalents are excluded from simulated P4(iii) only. No frozen numeric primary evaluation set or real array pool was run.
