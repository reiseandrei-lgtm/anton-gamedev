---
description: "План выпуска — магазин, запуск, после релиза / Release plan — store, launch, post-launch"
argument-hint: "store | launch | postlaunch | check"
disable-model-invocation: true
---

Используй скилл `release-plan`: **$ARGUMENTS**

1. Прочитай `design/pillars.md`, `concept.md`, `scope.md`, последние `qa/runs/`, `qa/bugs/` (S1 / S2), `qa/perf/`, `analytics/events.md`, `release/builds.md`.
2. Нет `design/release/` → создай из `templates/design/release/` после подтверждения.
3. `store` → аудит в порядке покупателя и `release/store.md`; текстов для игроков не пишешь — вопросы автору и находки. `launch` → вехи, чеклист по отделам, go / no-go. `postlaunch` → метрики из KPI, патчи, hotfix-путь, откат. Формат — `release-plan/references/release-method.md`.
4. Правила платформы сверяешь с текущей документацией и пишешь дату сверки; не помнишь точно — «не проверено».
5. `check` (и после записи) → `release-plan/scripts/check_release_plan.py design/release --events design/analytics/events.md` (на Windows `python`).
6. Итоги: 🟨-шаги человека с датами. Сборка RC и загрузка — `[gd-build]` `/gd-build:release`; кнопку Release нажимает человек.

Язык ответа — язык пользователя.
