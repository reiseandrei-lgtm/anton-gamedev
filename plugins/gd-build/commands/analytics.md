---
description: "Вызовы аналитики в коде и локальный JSONL-лог / Wire analytics events and a local JSONL log"
argument-hint: "[gen | wire | check] [путь к Unity-проекту]"
disable-model-invocation: true
---

Используй скилл `analytics-build`: **$ARGUMENTS**

1. Preflight `slice-build/scripts/preflight.py <unity-project> --for analytics` и проба MCP. Нет `design/analytics/events.md` → стоп, предложи `/gd:metrics`.
2. `gen` → `analytics-build/scripts/gen_analytics.py design/analytics/events.md --out <Assets/_Project/Scripts/Analytics>`; бэкенд заменён по ADR → `--no-backend`.
3. `wire` → покажи план: событие → система и точка из Trigger → параметры; дождись «да». Вызовы по `analytics-build/references/analytics-method.md`, согласие — флаг `AnalyticsLog.Consent`.
4. Тесты EditMode (строка с согласием, ничего без согласия), verify loop, play mode: файл `analytics/<session>.jsonl`.
5. `check` (и после записи) → `analytics-build/scripts/check_analytics_calls.py <Assets> --events design/analytics/events.md` (на Windows `python`); лог `design/build/analytics.log.md`.
6. Итоги: событий с вызовом из N, путь к JSONL; внешний бэкенд — только через `/gd:tech adr analytics`.

Язык ответа — язык пользователя.
