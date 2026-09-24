---
status: template   # template | draft | review | approved
updated:
owner:
---

# README — папка design/

Общий мост между Claude Code и Cowork: все дизайн-документы игры живут здесь, в репозитории игры.

| Файл / папка | Что | Скилл / команда |
|---|---|---|
| `pillars.md` | 3–5 столпов | `gd-concept` |
| `concept.md` | Искра, Fantasy / Loop / Twist, Iceberg | `gd-concept` |
| `systems-map.md` | Системы, приоритеты, зависимости | `gd-systems-map` |
| `gdd/<system>.md` | GDD по файлу на систему | `/gd:gdd` |
| `narrative/` | Мир, персонажи, ветки, голоса, Ink-планы | `/gd:narrative`, `/gd:ink` |
| `balance/<system>.md` | Таблицы чисел и расчёты | `/gd:balance` |
| `scope.md` | Инвентарь, оценки, cut-list | `/gd:scope` |
| `handoff/<slice>.md`, `handoff/<milestone>.md` | Хендофф слайса (ED / DD) и майлстоуна Alpha / Beta (`ED-<system>-N`) | `gd-handoff` |
| `art/` | Арт-библия, список ассетов | `/gd:art` |
| `audio/` | Аудио-библия, карта событий FMOD (с банками), `files.md` — файлы звука и лицензии (+ `build/` — сгенерированное) | `/gd:audio`, `/gd-build:fmod` |
| `ux/` | FTUE, HUD, доступность | `/gd:ux` |
| `tech/` | Архитектура, config map, бюджеты, ADR | `/gd:tech` |
| `qa/` | Тест-планы (`test-plan-<slice>.md`), прогоны `runs/`, баги `bugs/`, эталоны скриншотов `visual/`, замеры `perf/` | `/gd:qa-plan`, `/gd-build:test` |
| `build/<slice>.log.md`, `build/<system>.log.md` | Логи сборки: доказательства по ED и R / F / E, замеры отклика (Juice) | `/gd-build:slice`, `/gd-build:feature`, `/gd-build:juice`, `/gd-build:ui` |
| `playtest/` | Планы, заметки и отчёты плейтестов | `/gd:playtest` |
| `analytics/` | Вопросы, KPI, события, воронки | `/gd:metrics` |
| `reviews/` | Отчёты ревью и feel-пассов | `/gd:review` |
| `decisions-log.md` | Журнал решений | все |

Статусы во frontmatter: `template` → `draft` → `review` → `approved`. Роутер (`/gd:start`) читает их, чтобы определить стадию.

`/gd-build:*` — плагин `gd-build`, работает только в Claude Code с Unity-проектом (и бесплатным Unity MCP для полной проверки). В Cowork эти шаги роутер отдаёт как чеклист.
