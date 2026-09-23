---
description: План метрик — вопросы, KPI, события, воронки / Analytics plan — questions, KPIs, events, funnels
argument-hint: "[<slice> | check]"
disable-model-invocation: true
---

Используй скилл `metrics-plan`: **$ARGUMENTS**

1. `<slice>` или пусто → вопросы из гипотезы `design/handoff/<slice>.md`, шаги из `design/ux/ftue.md`, проекции из `design/balance/`.
2. Нет `design/analytics/` → создай из шаблона после подтверждения.
3. Напиши `design/analytics/events.md` и `funnels.md` по `metrics-plan/references/metrics-method.md`.
4. `check` (и после записи) → `check_events.py design/analytics/events.md --funnels design/analytics/funnels.md` (на Windows `python`).
5. Реализация — вендор-агностично; платные SDK не предлагать. Выбор — ADR через `/gd:tech adr analytics`.

Язык ответа — язык пользователя.
