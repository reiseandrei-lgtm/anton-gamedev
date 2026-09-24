---
status: draft
updated: 2026-09-24
owner: example
level: broken
target_length: 1-1.5 min
start: N0
goal: N3
---

# Level — broken (негативная фикстура: LV1, LV2, LV3 без ключа, LV4, LV5)

## Metrics
| ID | Metric | Kind | Move | Knob | Value |
|---|---|---|---|---|---|
| LM1 | максимальный прыжок | gap_max | hop | hop#K3 | 4.0 |
| LM2 | минимальный прыжок | gap_min | hop | hop#K1 | |
| LM3 | высота | height_max | hop | hop#K99 | 1.0 |

## Layout
| ID | From | To | Move | Gap | Height | Path | Dir |
|---|---|---|---|---|---|---|---|
| L1 | N0 | N1 | hop | 4.5 | 0 | critical | → |
| L2 | N1 | N2 | hop | 0.5 | 0 | critical | → |
| L3 | N2 | N3 | hop | 2.0 | 0 | critical | → |

## Encounters
| ID | Where | Uses | Wave | Trigger | Tension |
|---|---|---|---|---|---|
| EN1 | N9 | spark#R1 | — | — | 1 |
| EN2 | N1 | ghost#R1 | — | — | 2 |
| EN3 | N2 | spark#R99 | — | — | 5 |

## Pacing
| Minute | Tension | Beat |
|---|---|---|
| 0:00 | 0 | старт |
| 0:30 | 3 | пик 1 |
| 0:45 | 2 | без отдыха |
| 1:00 | 3 | пик 2 |
| 4:00 | 0 | финиш |

## Gates
| ID | Link | Key | Key at |
|---|---|---|---|
| G1 | L3 | — | — |
