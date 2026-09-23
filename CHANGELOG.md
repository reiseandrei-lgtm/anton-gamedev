# Changelog

## [gd-build 0.1.1] — 2026-09-23

### Fixed
- `preflight.py` и `run-tests-headless.ps1` находят редактор в нестандартной папке Unity Hub (Settings → Installs location, `secondaryInstallPath.json`). Раньше редактор на D: считался «не найден».
- `run-tests-headless.ps1` прямо сообщает об отсутствии лицензии Unity (exit 198, `No valid Unity Editor license found`) вместо «прогон не завершился».
- `qa-run/references/qa-run-method.md`: как распознать устаревшую лицензию и нестандартную папку редакторов.

## [0.4.0] — 2026-09-23 · gd 0.4.0, gd-build 0.1.0

Полный цикл: после хендоффа — подготовка сборки, сборка, QA, плейтест, решение; параллельные треки арта, звука, UX и метрик. Только бесплатные инструменты. Ресерч и архитектура — `research/2026-09-full-cycle*.md`.

### Added — плагин gd
- Скиллы `art-direction` (арт-библия, палитра по ролям, читаемость, asset-list; `check_palette.py` — WCAG, grayscale, дальтонизм; `check_assets.py`), `audio-direction` (аудио-библия, карта событий FMOD с соглашением по неймингу; `check_event_map.py` — покрытие Feedback GDD), `ux-onboarding` (FTUE, HUD, чеклист доступности), `tech-design` (модули, config map knob → поле, сохранения, бюджеты, ADR; `check_knobs.py`), `qa-plan` (тест-план из GDD и хендоффа; `check_coverage.py` — трассировка R/F/E/ED → тесты), `playtest` (plan / analyze, коды наблюдения; `aggregate_codes.py`), `metrics-plan` (вопросы → KPI → события → воронки; `check_events.py`).
- Агенты-ревьюеры `art-director`, `audio-director`, `qa-lead`, `playtest-analyst` — видят только артефакт (аналитик плейтеста не видит GDD).
- Команды `/gd:art`, `/gd:audio`, `/gd:ux`, `/gd:tech`, `/gd:qa-plan`, `/gd:playtest`, `/gd:metrics`.
- Общий парсер `gd-router/scripts/gdd_ids.py`: стабильные ID GDD, ссылки `<system>#<ID>`, ID хендоффа.
- Шаблоны `templates/design/`: `art/`, `audio/`, `ux/`, `tech/` (+ `adr/`), `qa/` (+ `runs/`, `bugs/`), `build/`, `playtest/`, `analytics/`.

### Added — плагин gd-build (новый, только Claude Code)
- `slice-build`: хендофф → играбельный Unity-слайс через бесплатный Unity MCP; preflight, тест первым, verify loop (компиляция по mtime DLL, консоль, тесты, smoke, скриншот), максимум 3 fix-цикла, лог доказательств по ED; без MCP — режим plan. Скрипты `preflight.py`, `gen_sfx.py`.
- `qa-run`: EditMode / PlayMode через MCP или headless (`run-tests-headless.ps1/.sh`, `find-unity.*` — из unity-kit), `parse_nunit.py` с сопоставлением T-ID, 0 тестов = FAIL, smoke, баг-репорты.
- `fmod-sync`: `event_map_to_fmod.py` → идемпотентный JS для FMOD Studio + `FmodEvents.cs`; `diff_fmod.py` сверяет с экспортом GUIDs.
- Команды `/gd-build:slice`, `/gd-build:test`, `/gd-build:fmod`.

### Changed
- `gd-router`: стадии 8–12, треки арта / звука / UX / метрик, эвристики и возвраты; шаги `[gd-build]` в Cowork отдаются чеклистом. `principles.md`: «только бесплатные инструменты», «честная проверка».
- Шаблон GDD: стабильные ID `R1` / `F1` / `E1` / `K1` / `FB1`; хендофф: `ED1…`, `DD1…`. Старые GDD без ID читаются с предупреждением (нумерация по порядку).
- `game-feel`: убран триггер «плейтест-разбор» (теперь `playtest`); `narrative-structure`: убран "continuity check" (пересекался с `narrative-continuity`).
- `/gd:start` создаёт новые папки `design/`.
- CLAUDE.md: два плагина, правило бесплатности, проверки перед выпуском.

### Tooling
- `tools/check_plugins.py` (frontmatter, ссылки, пересечение триггеров, компиляция скриптов), `tools/test_scripts.py` (23 теста, позитивные и негативные).
- `examples/one-tap-slice/` — мини-игра по готовому хендоффу, прогон всех новых скиллов и агентов, `RESULTS.md`.

### Not verified
- `gd-build` против реальных Unity 6 + CoplayDev/unity-mcp и FMOD Studio: на машине разработки их нет; проверено в режиме деградации и на фикстурах.

## [0.3.0] — 2026-09-22

### Added
- Скилл `narrative-continuity` и команда `/gd:continuity`: реестр промисов (сетап → пэйофф), состояние знаний, канон мира; режимы register / check / impact; скрипт `scripts/check_continuity.py` (C1–C4 по графу diverts Ink).
- `gd-router/references/prose-failures.md` — проверки прозы для режима текста.
- `character-voice/references/voice-kit.md` — эталонные реплики, матрица отношений, правка в три прохода.
- `ink-slice/references/localization-and-telemetry.md` — дизайн выборов, локализация RU/PL/EN, телеметрия.
- Шаблоны `templates/design/narrative/continuity/` (promises, state, canon).

### Changed
- `gd-router`: блокер continuity, трек «Континуити» в пайплайне, критерий хендоффа; раздел «Дизайн выбора» в principles.
- Команды `ink`, `narrative`, `start`: таблица выборов, локализация, voice kit, prose-failures, папка `continuity/`.
- `character-voice`, `ink-slice` ссылаются на новые references; агент `narrative-designer` получил скилл `narrative-continuity`.
- README: команда `/gd:continuity` и скилл `narrative-continuity`.

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
