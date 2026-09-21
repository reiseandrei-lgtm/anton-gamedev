---
name: gd-handoff
description: >-
  Финальная стадия пайплайна: выбор первого слайса/прототипа (гипотеза, что подделать, как выглядит провал) и пакет хендоффа в реализацию с критериями Engineering Done и Design Done. Пишет design/handoff/<slice>.md. Движок-агностично.
  Триггеры RU: «что строить первым», «план прототипа», «вертикальный слайс», «хендофф», «передать в разработку», «ТЗ для реализации».
  Triggers EN: "what to build first", "prototype plan", "vertical slice plan", "implementation handoff", "hand off to dev".
  Не для Ink-слайсов (ink-slice) и не для ревизии скоупа (scope-check).
---

# gd-handoff

## Вход
`design/scope.md`, approved/review GDD систем слайса, последние `design/reviews/`, `design/balance/`.

## Часть A — выбор слайса
1. Назови главный неподтверждённый риск дизайна (из ревью/концепта).
2. Предложи 2–3 кандидата типов из `references/slice-and-handoff.md` (Mechanic / Onboarding / Progression / Combat / Economy / Narrative / Vertical).
3. Оцени каждый по 5 осям /10, рекомендуй один. Решает пользователь.
4. Сформулируй гипотезу: «Если <слайс>, то игрок <наблюдаемое поведение> за <время>». И как выглядит провал.

## Часть B — пакет хендоффа
Заполни шаблон из `references/slice-and-handoff.md`: цель билда одной фразой · scope (MUST/SHOULD/COULD, out of scope, плейсхолдеры) · требования к опыту игрока (действие → отклик → тайминг → feel) · системы · ассеты real/placeholder · Engineering Done · **Design Done** · риски «соблазнительных срезов» · как проверять.

## Выход
`design/handoff/<slice>.md`, `status: draft`. После подтверждения — реализация вне этого плагина (в Claude Code — официальный Unity Plugin). После билда — `game-feel` (build) и сверка с гипотезой.

## Правила
Язык ответа = язык запроса. Художественный текст — только по явной просьбе. Никакого кода и движковых деталей: только что игрок должен испытать и как это проверить. «Стандартный прыжок» не существует — уточняй.
