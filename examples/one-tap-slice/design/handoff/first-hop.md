---
status: approved
updated: 2026-09-23
owner: example
slice_type: Mechanic
hypothesis: "Если дальность прыжка задаётся удержанием с допуском 0.35, то 4 из 5 новичков сделают 5 успешных прыжков подряд за 3 минуты и нажмут «ещё» быстрее 2 с после первого падения."
failure_looks_like: "Игроки не связывают удержание с дальностью (прыгают коротко) или бросают после 2–3 падений."
---

# Handoff: first-hop

## 1. Build target (one sentence)
Бесконечная цепочка фонарей, заряжаемый прыжок, искры и рестарт — на Android-телефоне.

## 2. Scope
### In
- MUST: hop R1–R6, spark R1–R3, рестарт, рекорд.
- SHOULD: звук FB1–FB4 hop, FB1 spark.
- COULD: дуга-призрак (выключена по умолчанию).
### Out (and why)
Меню, магазин, уровни сложности — не проверяют гипотезу.
### Placeholder OK
Персонаж — капсула, фонари — цилиндры цвета роли палитры, фон — сплошной `bg`.

## 3. Player experience requirements
| Player action | Expected response (V/A/haptic) | Timing | Feel target |
|---|---|---|---|
| Удержание | фонарь разгорается, звук заряда растёт | с первого кадра | натянутая тетива |
| Отпускание | прыжок | ≤ 1 кадр | отзывчиво |
| Приземление | пыль, звук | в кадр касания | вес |

## 4. Systems
| System | Role in slice | Exists? | Notes |
|---|---|---|---|
| hop | core | нет | |
| spark | награда | нет | |

## 5. Assets and audio
| Asset | Real / Placeholder | Spec |
|---|---|---|
| персонаж, фонарь, искра | placeholder | примитивы |
Полный список — `design/art/asset-list.md`; звук — `design/audio/event-map.md`.

## 6. Acceptance
### Engineering Done
- [ ] ED1 билд запускается на Android mid-устройстве, 60 fps в забеге
- [ ] ED2 hop: правила R1–R6 и edge cases E1–E5 работают
- [ ] ED3 spark: правила R1–R3 работают, двойная искра на дальних фонарях
- [ ] ED4 рестарт: от тапа до нового забега ≤ 0.3 с
- [ ] ED5 рекорд сохраняется между запусками приложения
### Design Done
- [ ] DD1 новичок делает первый прыжок без подсказки за ≤ 10 с
- [ ] DD2 игрок связывает длительность удержания с дальностью за ≤ 3 прыжка
- [ ] DD3 после первого падения нажимает «ещё» быстрее 2 с (north star)
### Not done until
- [ ] сыграл кто-то, кроме разработчика

## 7. Tempting shortcuts that kill the experience
| Risk | Shortcut | Why it kills it |
|---|---|---|
| заряд | нелинейный заряд «чтобы было интереснее» | ломает предсказуемость (P1) |
| рестарт | экран «Game Over» с анимацией 2 с | ломает north star (P3) |

## 8. How to verify
| What | How | Pass |
|---|---|---|
| ED | тесты по qa/test-plan-first-hop.md | все P1 зелёные |
| DD | плейтест 5 новичков | порог в playtest plan |
