---
status: draft
updated: 2026-09-24
owner: example
level: opening
target_length: 1-1.5 min
start: N0
goal: N5
---

# Level — opening (позитивная фикстура check_level.py)

## Metrics
| ID | Metric | Kind | Move | Knob | Value |
|---|---|---|---|---|---|
| LM1 | максимальный прыжок | gap_max | hop | hop#K3 | 4.0 |
| LM2 | минимальный прыжок | gap_min | hop | hop#K1 | |

## Layout
| ID | From | To | Move | Gap | Height | Path | Dir |
|---|---|---|---|---|---|---|---|
| L1 | N0 | N1 | hop | 1.4 | 0 | critical | → |
| L2 | N1 | N2 | hop | 2.0 | 0 | critical | → |
| L3 | N2 | N3 | hop | 2.8 | 0 | critical | ↔ |
| L4 | N2 | N4 | hop | 2.5 | 0 | critical | → |
| L5 | N4 | N5 | hop | 3.0 | 0 | critical | → |
| L6 | N1 | N6 | hop | 3.8 | 0 | optional | ↔ |

## Encounters
| ID | Where | Uses | Wave | Trigger | Tension |
|---|---|---|---|---|---|
| EN1 | N2 | spark#R1 | — | приземление на N2 | 1 |
| EN2 | L5 | hop, spark#R2 ×2 | — | прыжок L5 | 3 |

## Pacing
| Minute | Tension | Beat |
|---|---|---|
| 0:00 | 0 | teach L1 |
| 0:20 | 1 | practice L2 |
| 0:40 | 3 | test: ключ на N3 |
| 0:50 | 1 | отдых на N2 |
| 1:05 | 3 | twist L5 |
| 1:15 | 0 | финиш N5 |

## Gates
| ID | Link | Key | Key at |
|---|---|---|---|
| G1 | L4 | lantern_key | N3 |
