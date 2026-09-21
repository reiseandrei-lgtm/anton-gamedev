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
| `handoff/<slice>.md` | Пакеты хендоффа в реализацию | `gd-handoff` |
| `reviews/` | Отчёты ревью и feel-пассов | `/gd:review` |
| `decisions-log.md` | Журнал решений | все |

Статусы во frontmatter: `template` → `draft` → `review` → `approved`. Роутер (`/gd:start`) читает их, чтобы определить стадию.
