> Adapted from Claude-Code-Game-Studios `game-design-document.md` template (MIT © 2026 Donchitos). See ATTRIBUTION.md.

```markdown
---
status: draft          # template | draft | review | approved
updated: YYYY-MM-DD
owner:
pillar:                # какой столп обслуживает
priority:              # MVP | Vertical Slice | Alpha | Full
layer:                 # Foundation | Core | Feature | Presentation
depends_on: []
---

# <System Name>

## Summary
2–3 предложения: что это, что даёт игроку, зачем в ЭТОЙ игре.

## Player Fantasy
Что игрок должен чувствовать (MDA-эстетика). SDT: какая потребность — Autonomy / Competence / Relatedness.

## Core Rules
Однозначные правила со стабильными ID (не перенумеровывать при правке; удалённый ID не переиспользовать). Программист реализует без вопросов.
R1. …
R2. …

## States & Transitions
| State | Entry | Exit | Behavior |
|---|---|---|---|

## Interactions with Other Systems
| System | In (данные) | Out (данные) | Кто владеет |
|---|---|---|---|

## Formulas
### F1 — <Formula>
`result = ...`
| Variable | Type | Range | Source | Meaning |
|---|---|---|---|---|
Ожидаемый диапазон выхода: … · Клампы: …

## Edge Cases
| ID | Scenario | Behavior | Why |
|---|---|---|---|
| E1 | … | … | … |
Проверить: нулевое состояние, переполнение, несоответствие уровня, обрыв (сеть/сейв), неповиновение игрока.

## Dependencies
| System | Direction | Nature |
|---|---|---|

## Tuning Knobs
| ID | Parameter | Current | Safe range | ↑ effect | ↓ effect |
|---|---|---|---|---|---|
| K1 | … | … | … | … | … |

## Feedback (Visual / Audio)
| ID | Event | Visual | Audio (FMOD event) | Priority |
|---|---|---|---|---|
| FB1 | … | … | `event:/SFX/<Category>/<Name>` или — | … |

## Game Feel
- Reference / anti-reference: <конкретная механика конкретной игры>
- Input → response: <мс / кадры>
- Anticipation / Action / Impact / Resolution: <кадры, каналы>
- «Душа» механики: <одна вещь, без которой она становится generic>

## Narrative Hooks
Как система выражает нарратив/тему (ludonarrative). Ссылки на `narrative/`.

## Open Questions
- [ ] …

## Changes
<!-- Quick spec правки: дата · что · зачем · затронутые knobs -->

## Ready for review
- [ ] Столп указан и система ему служит
- [ ] Core Rules без TBD
- [ ] Все формулы с диапазонами
- [ ] Минимум 5 edge cases
- [ ] Tuning knobs с безопасными диапазонами
- [ ] Game feel: цель и «душа» названы
- [ ] У правил, формул, edge cases, knobs и feedback есть ID (R/F/E/K/FB) — на них ссылаются qa-plan, tech-design, audio-direction
```
