---
status: approved
updated: 2026-09-23
owner: example
pillar: P2
priority: MVP
layer: Feature
depends_on: [hop]
---

# Spark

## Summary
Над частью фонарей висят искры. Искра на дальнем фонаре стоит вдвое больше: награда там, где риск.

## Player Fantasy
Жадность против точности: «рискну ради двойной». SDT: Competence, Autonomy.

## Core Rules
R1. При генерации фонаря искра появляется с вероятностью K3.
R2. Успешное приземление на фонарь с искрой даёт очки по F1; искра исчезает.
R3. Счёт забега — сумма очков; рекорд сохраняется между запусками, если счёт строго больше.

## States & Transitions
| State | Entry | Exit | Behavior |
|---|---|---|---|
| Hanging | генерация фонаря с искрой | приземление | мерцает |
| Collected | приземление | — | исчезает, +очки |

## Interactions with Other Systems
| System | In (данные) | Out (данные) | Кто владеет |
|---|---|---|---|
| hop | событие приземления (фонарь, дистанция) | — | hop |

## Formulas
### F1 — Очки за искру
`value = distance > K1 ? K2 : 1`
| Variable | Type | Range | Source | Meaning |
|---|---|---|---|---|
| distance | float | 1..4 | hop#F1 | дистанция прыжка |
Ожидаемый диапазон: 1 или 2.

## Edge Cases
| ID | Scenario | Behavior | Why |
|---|---|---|---|
| E1 | Промах по фонарю с искрой | очков нет | R2: только успешное приземление |
| E2 | Счёт равен рекорду | рекорд не перезаписывается, нет фидбэка «новый рекорд» | R3: строго больше |
| E3 | Сохранение не удалось (нет места) | игра продолжается, рекорд держится в памяти до выхода | P3: провал сохранения не ломает забег |

## Dependencies
| System | Direction | Nature |
|---|---|---|
| hop | in | события приземления |

## Tuning Knobs
| ID | Parameter | Current | Safe range | ↑ effect | ↓ effect |
|---|---|---|---|---|---|
| K1 | farThreshold | 3.0 | 2.5..3.5 | реже двойные | двойные слишком легко |
| K2 | farMultiplier | 2 | 2..3 | сильнее тянет рисковать | риск не окупается |
| K3 | sparkChance | 0.35 | 0.2..0.5 | чаще награда | реже цель |

## Feedback (Visual / Audio)
| ID | Event | Visual | Audio (FMOD event) | Priority |
|---|---|---|---|---|
| FB1 | Искра собрана | вспышка, +1 / +2 летит в счёт | `event:/SFX/Pickup/Spark` | 2 |
| FB2 | Новый рекорд | счёт золотой 1 с | `event:/UI/Record/New` | 2 |
| FB3 | Счёт обновился | тик цифры | — | 3 |

## Game Feel
- Двойная искра звучит выше и ярче одиночной — различимо без взгляда на счёт.
- «Душа»: секунда жадности перед отпусканием.

## Open Questions

## Changes

## Ready for review
- [x] Столп указан и система ему служит
- [x] Core Rules без TBD
- [x] Все формулы с диапазонами
- [ ] Минимум 5 edge cases — 3, система маленькая
- [x] Tuning knobs с безопасными диапазонами
- [x] Game feel: цель и «душа» названы
- [x] У правил, формул, edge cases, knobs и feedback есть ID
