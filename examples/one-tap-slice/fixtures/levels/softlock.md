---
status: draft
updated: 2026-09-24
owner: example
level: softlock
target_length: 1 min
start: N0
goal: N3
---

# Level — softlock (негативная фикстура: ключ только за своим гейтом)

## Metrics
| ID | Metric | Kind | Move | Knob | Value |
|---|---|---|---|---|---|
| LM1 | максимальный прыжок | gap_max | hop | hop#K3 | |

## Layout
| ID | From | To | Move | Gap | Height | Path | Dir |
|---|---|---|---|---|---|---|---|
| L1 | N0 | N1 | hop | 2.0 | 0 | critical | → |
| L2 | N1 | N2 | hop | 2.0 | 0 | critical | → |
| L3 | N2 | N3 | hop | 2.0 | 0 | critical | → |

## Encounters
| ID | Where | Uses | Wave | Trigger | Tension |
|---|---|---|---|---|---|
| EN1 | N1 | spark#R1 | — | — | 1 |

## Pacing
| Minute | Tension | Beat |
|---|---|---|
| 0:00 | 0 | старт |
| 0:30 | 2 | гейт |
| 1:00 | 0 | финиш |

## Gates
| ID | Link | Key | Key at |
|---|---|---|---|
| G1 | L2 | lantern_key | N2 |
