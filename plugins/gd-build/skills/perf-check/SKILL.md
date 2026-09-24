---
name: perf-check
description: >-
  Замер производительности Unity-проекта против design/tech/budgets.md: время кадра, batches, память, загрузка, размер сборки через профайлер MCP; серия снимков p50/p95/max, прогрев перед замером, отчёт design/qa/perf/<date>.md и сравнение с бюджетом и прошлым замером скриптом.
  Триггеры RU: «замерь производительность», «проверь перф», «профилирование», «влезаем ли в бюджет кадра», «сколько batches».
  Triggers EN: "profile the build", "check performance", "frame budget check", "measure frame time".
  Не для составления бюджетов (gd:tech-design), не для утечек при долгой игре (qa-run soak), не для оптимизации ассетов (asset-integrate).
---

# perf-check

Ты замеряешь и сравниваешь числа. Не оптимизируешь и не меняешь бюджеты: провал бюджета — находка с адресатом.

## 0. Preflight
`python3 ../slice-build/scripts/preflight.py <unity-project>` + проба MCP (`read_console`; CLI — `slice-build/references/mcp-actions.md` п. 4). Нет MCP → режим plan: отчёт с `n/a: нет MCP` и чеклист ручного замера, ✅ нет.

## 1. Вход
`design/tech/budgets.md` (ID `B*`, метрика, бюджет, платформа, «как замерить»); сцена из `tech/architecture.md` или хендоффа; прошлый `design/qa/perf/*.md` (не `-soak`) для `--prev`.

## 2. Алгоритм (метод и формат — `references/perf-method.md`)
1. Под каждую строку бюджета — канал замера (§1 метода). Метрику, которую нечем замерить, помечай `n/a: причина`.
2. Play mode (`manage_editor play`), прогрев по бюджету (или 0 с пометкой), затем серия ≥ 30 снимков `manage_profiler get_frame_timing` и `get_counters` (Render, Memory).
3. p50/p95/max считаешь из серии скриптом или вручную по сырым числам; сырые числа — в `## Samples`.
4. `manage_editor stop`; консоль без ошибок.
5. Отчёт `design/qa/perf/<date>.md` → `python3 scripts/compare_perf.py <report> --budgets design/tech/budgets.md [--prev …]` → вывод в конец отчёта.

## Done
Каждая строка бюджета — число или `n/a: причина`; `compare_perf.py` отработал, вывод в отчёте; FAIL передан адресату (ADR в `gd:tech-design`, `asset-integrate` или `gd:scope-check`).

## Правила
Язык ответа = язык запроса. Замер в редакторе ≠ устройство: вердикт по бюджету устройства — только с устройства, иначе в отчёте PF4 и «не проверено на устройстве». Числа без условий замера (платформа, фокус окна, прогрев) не публикуй. Платные облака профилирования не использовать.
