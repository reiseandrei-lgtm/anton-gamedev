---
name: loc-build
description: >-
  Таблицы локализации для Unity из ключей UI (ux/hud.md, UXML, C#) и ID строк Ink: CSV в формате расширения CSV пакета Unity Localization, лимиты длины из UX, псевдолокализация, импорт в String Table Collection и привязка ключей в UI Toolkit; пропуски, переполнения, плейсхолдеры и литералы проверяются скриптом. Без пакета — режим plan: CSV и проверка без Unity.
  Триггеры RU: «таблицы локализации», «псевдолокализация», «подключи Unity Localization», «проверь переводы», «строки в таблицу локализации».
  Triggers EN: "localization tables", "pseudo-localize", "set up Unity Localization", "check the translations".
  Не для дизайна строк, выборов и тегов Ink (gd:ink-slice), не для вёрстки UI (ui-build), не для выбора языков магазина (gd:release-plan).
---

# loc-build

Ты переносишь ключи строк в таблицы и следишь, чтобы каждая строка влезла, была переведена и не собиралась из кусков. Исходные тексты не сочиняешь: значения базового языка — от человека (или `--text`); машинный перевод утверждённого исходника — с отметкой `mt` до проверки носителем.

## 0. Preflight
`python3 ../slice-build/scripts/preflight.py <unity-project> --for loc`: пакет `com.unity.localization` в `Packages/manifest.json`, редактор, MCP. Нет пакета → режим **plan** (CSV и проверка без Unity) и вопрос человеку об установке; ставишь только после «да».

## 1. Вход
`design/ux/hud.md` (Loc key), `design/ux/ftue.md` (`[ПОДСКАЗКА: …, ≤ N символов]`), `design/narrative/ink/*.plan.md` и `.ink` (`#id:`), UXML и C# проекта, список языков из `design/release/store.md` или решения в `decisions-log.md`.

## 2. Алгоритм (формат CSV, лимиты, live-шаги — `references/loc-method.md`)
1. **Сбор ключей**: hud.md, UXML (`text="ui.x"`, `entry="ui.x"`), C# (литералы с префиксом таблицы), Ink (`#id:`). Литерал вместо ключа → в ui-build / ink-slice, сам не правишь.
2. **CSV** `design/loc/<Table>.csv`: `Key, Shared Comments, <Язык>(<код>)…`; лимит — `max:N` в Shared Comments (из UX или плана Ink; RU/PL длиннее EN на 20–30 %). Пустые значения — честный пропуск.
3. **Проверка** с `--pseudo 0.35`: каждое `max:N` проверяется на удлинённом исходнике до перевода.
4. **Live** (пакет есть): Localization Settings, локали, String Table Collection на каждый CSV, импорт CSV расширением пакета, UXML-привязки `LocalizedString`; Pseudo-Locale — скриншоты 2–3 разрешений через `ui-build`. How-to API — официальный Unity Plugin.
5. **Лог** `design/build/loc.log.md` (формат лога системы, `system: loc`): таблицы, числа ключей, языки, `mt`, скриншоты.

## Проверка
`python3 scripts/check_loc.py design/loc --hud design/ux/hud.md [--unity <Assets/…>] [--ink <папка .ink>] [--source en] [--pseudo 0.35]`: LC1 ключ без записи или без исходника (перевода нет — WARN) · LC2 ключ таблицы не используется (WARN) · LC3 длина > `max:N` · LC4 плейсхолдеры не совпадают с исходником · LC5 литерал вместо ключа в UXML, C# или Ink. На Windows — `python`.

## Done
Скрипт без FAIL; режим (`plan` / `live`) назван; в live — таблицы в проекте и скриншоты псевдолокали без обрезки. Переводы с `mt` и значения базового языка без автора — 🟨 человека.

## Правила
Язык ответа = язык запроса. Склейки строк (`«Рекорд: » + n`) не делать — целая фраза с `{0}`. Галочки языков в магазине — только при полной локализации интерфейса (`gd:release-plan`). Платные сервисы перевода и TMS не подключать; Unity Localization — бесплатный пакет, код его не копировать.
