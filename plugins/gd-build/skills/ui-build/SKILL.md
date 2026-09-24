---
name: ui-build
description: >-
  Вёрстка HUD, меню, паузы и настроек в Unity на UI Toolkit по design/ux/hud.md: каждый элемент с именем из hud.md, цвета только переменными ролей палитры, строки только ключами локализации, safe area, скриншоты в 2–3 разрешениях; соответствие проверяется скриптом. Без MCP — план и файлы UXML/USS на диск.
  Триггеры RU: «сверстай HUD», «сделай меню», «экран паузы», «экран настроек», «реализуй интерфейс».
  Triggers EN: "build the HUD", "implement the menu", "pause screen", "settings screen", "implement the UI".
  Не для решения, что и где показывать (gd:ux-onboarding), не для перевода строк (loc-build), не для эффектов отклика (juice-build).
---

# ui-build

Ты верстаешь то, что решено в `design/ux/hud.md` и `art/art-bible.md`. Что показывать и где — не решаешь: элемент не помещается в зону → стоп, вопрос в `gd:ux-onboarding`.

## 0. Preflight
`../slice-build/scripts/preflight.py` + проба MCP. UI Toolkit по умолчанию (решение в `research/…production-cycle-architecture.md` §7 b); uGUI — только если ADR в `design/tech/adr/` требует (world-space, тяжёлый джус).

## 1. Вход
`design/ux/hud.md` (Info, Зона, Форма, **Name**, **Loc key**), `design/ux/accessibility.md` (размер текста, контраст, отключаемые эффекты), `design/art/art-bible.md` (роли палитры, минимальные размеры), GDD (что показывает элемент).

## 2. Алгоритм (детали — `references/ui-method.md`)
1. Тема: `Theme.uss` с переменными `--role-<role>` = HEX из арт-библии; остальные USS — только `var(--role-…)`.
2. UXML на экран (`HUD.uxml`, `Restart.uxml`, `Pause.uxml`, `Settings.uxml`): `name` элемента = колонка Name; текст — ключ из Loc key (`text="ui.again"`), числа ставит код.
3. `PanelSettings`: Scale With Screen Size, опорное разрешение цели; safe area — отступы корня по `Screen.safeArea`.
4. Контроллер (C#) подписан на события систем, пишет только числа и состояния, литералов текста нет; тач-цели не меньше минимума библии.
5. Через MCP: `manage_ui` (создать UXML/USS, прикрепить `UIDocument`), verify loop, play mode, скриншоты Game view в 2–3 разрешениях → `design/build/ui/screenshots/<W>x<H>/` — посмотри на каждый.
6. Лог `design/build/ui.log.md` (формат лога системы, `system: ui`), затем
   `python3 scripts/check_ui.py design/ux/hud.md <Assets/…/UI> --palette design/art/art-bible.md --code <Assets/…/Scripts> --shots design/build/ui/screenshots --res <список>`.

## Done
`check_ui.py` без FAIL; у каждого элемента hud.md есть реализация и скриншот; консоль чистая. Дальше — `loc-build` (строки) и `qa-run visual` (эталоны экранов).

## Правила
Язык ответа = язык запроса. Тексты интерфейса не пишешь: только ключи, значения — человек или `loc-build`. How-to API UI Toolkit — официальный Unity Plugin. Платные ассеты и генераторы иконок не использовать; иконки — CC0 или плейсхолдеры цветом роли.
