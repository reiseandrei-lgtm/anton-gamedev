# Changelog

## [0.2.1] — 2026-09-21

### Added
- Лицензия MIT: `LICENSE` в корне и в `plugins/gd/`, поле `license` в `plugin.json`.

## [0.2.0] — 2026-09-21

### Added
- Проектный скилл `syncario-gamedesigner` (из `import/gamedesigner`, содержимое без изменений; изменены только `name` и хвост `description` — триггеры сужены до Syncario).
- Общие принципы из него в `gd-router/references/principles.md`: уровни достоверности ФАКТ / РЕКОНСТРУКЦИЯ / ГИПОТЕЗА, north star, процесс проектирования (2–3 варианта + дешёвая проверка), правила для чисел, общие антипаттерны, стиль.
- Поле North star в шаблоне `design/pillars.md`.

### Changed
- Единый порядок ревью (`gdd-review`, `design-critic`): вердикт и главная проблема → что работает → что ломается (с альтернативами) → что делать.
- `gdd-review` и `design-critic` проверяют north star и общие антипаттерны; `gd-concept`, `gdd-author`, `balance-check` ссылаются на общие принципы.

## [0.1.0] — 2026-09-21

Первый выпуск.

### Added
- Маркетплейс `anton-gamedev` с плагином `gd`.
- 12 скиллов: `gd-router`, `gd-concept`, `gd-systems-map`, `gdd-author`, `gdd-review`, `game-feel`, `balance-check`, `scope-check`, `gd-handoff`, `narrative-structure`, `character-voice`, `ink-slice`.
- 3 агента: `design-critic`, `narrative-designer`, `producer`.
- 7 команд: `/gd:start`, `/gd:gdd`, `/gd:review`, `/gd:narrative`, `/gd:balance`, `/gd:scope`, `/gd:ink`.
- Шаблон `templates/design/` для игровых репозиториев.
- `import/` для интеграции собственных скиллов (пока пусто).
- ATTRIBUTION.md по заимствованиям из gstack-game, Claude-Code-Game-Studios, narrative-skills, narrative-ink-skills (все MIT).
