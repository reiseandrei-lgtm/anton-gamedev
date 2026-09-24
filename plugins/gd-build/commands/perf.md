---
description: "Замер производительности против бюджетов / Measure performance against budgets"
argument-hint: "[путь к Unity-проекту] [--prev design/qa/perf/<date>.md]"
disable-model-invocation: true
---

Используй скилл `perf-check` для **$ARGUMENTS**

1. Preflight (`slice-build/scripts/preflight.py`) и проба MCP. Покажи режим и платформу замера (редактор ≠ устройство).
2. Прочитай `design/tech/budgets.md`: строка → канал замера по `perf-check/references/perf-method.md`. Покажи план; дождись «да».
3. Прогрев, серия снимков профайлера, p50/p95/max; метрики без канала — `n/a: причина`.
4. Отчёт `design/qa/perf/<date>.md`, затем `perf-check/scripts/compare_perf.py`.
5. Итоги: таблица, FAIL с адресатом, что замерено не на целевой платформе.

Язык ответа — язык пользователя.
