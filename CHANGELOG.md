# Changelog

## [0.7.0] — 2026-09-24 · gd 0.7.0, gd-build 0.4.0 — волна C: уровни, выпуск, локализация, аналитика

Архитектура — `research/2026-09-production-cycle-architecture.md` §3, волна C (C1–C4). `netcode-build` (C5) не делался — ждёт решения (f).

### Added — gd
- `level-design` + `/gd:level`: метрики уровня только ссылками на knobs GDD, критический путь, встречи `EN…`, кривая напряжения 0–3, гейты; `check_level.py` (LV1–LV5: зазор / высота вне метрики, два пика без отдыха, гейт без ключа и soft lock, встреча с несуществующей системой или ID, длина вне цели). Шаблон `templates/design/levels/_template.md`.
- `release-plan` + `/gd:release-plan`: режимы `store` (аудит в порядке покупателя, теги с доказательствами), `launch` (вехи page → demo → fest → release, чеклист по отделам, go / no-go по файлам), `postlaunch` (метрики с порогом и адресатом, hotfix, откат). Тексты и арт для игроков пишет только человек. `check_release_plan.py` (RP1–RP4). Шаблоны `templates/design/release/`.
- `gd-router` / `pipeline.md`: треки «Уровни», «Локализация», «Аналитика в коде», эвристики и возвраты для новых проверок.

### Added — gd-build
- `loc-build` + `/gd-build:loc`: таблицы `design/loc/<Table>.csv` в формате CSV-расширения Unity Localization, `max:N` из UX, `mt` для машинного перевода, псевдо-удлинение `--pseudo`; без пакета `com.unity.localization` — режим plan. `check_loc.py` (LC1–LC5). Шаблон `templates/design/loc/UI.csv`.
- `analytics-build` + `/gd-build:analytics`: `gen_analytics.py` — `AnalyticsEvents.cs` (имена и типизированные методы) и `AnalyticsLog.cs` (локальный JSONL, `Consent` по умолчанию false, в сеть ничего не уходит); `check_analytics_calls.py` (AN1–AN4).
- `preflight.py --for loc|analytics`: без пакета Localization рекомендуемый режим — plan.

### Changed
- Порядок вех в RP2 — page → demo → fest → release (в карточке C4 было «демо → страница»): на Steam демо привязано к странице основной игры, фест требует страницу и демо. Демо на itch.io до страницы — веха `other`.
- `README.md`: команды и скиллы волн B и C.

### Tooling
- `check_plugins.py` P9: построчная сверка скопированного правила PII (`check_events.py` → `check_analytics_calls.py`, `LINE_COPIES`).
- `tools/trigger_cases.md`: +19 пар (68 запросов), в том числе развилки из §6: level-design ↔ gdd-author ↔ gd-systems-map, release-plan ↔ scope-check, metrics-plan ↔ analytics-build, loc-build ↔ ink-slice.

### Verified (один запуск каждого скрипта на данных `examples/one-tap-slice`, артефакты во временной папке)
- `check_level.py` — PASS на авторском участке «opening» (11 узлов, 10 связей, 2 встречи, 1:10 при цели 1–1.5 мин).
- `check_release_plan.py` — FAIL 1: RP1 нашёл пункт чеклиста без владельца (черновик плана запуска).
- `check_loc.py` — PASS: 2 ключа hud.md, en / ru, псевдо +35 % влезает в `max:10`; просканированы 1 UXML и 15 C# живого проекта.
- `gen_analytics.py` — 5 событий, 13 параметров; сгенерированный C# компилируется Roslyn из поставки Unity 6000.3.24f1 против `UnityEngine.CoreModule` и `netstandard` 2.1 без ошибок и предупреждений.
- `check_analytics_calls.py` — FAIL 5: AN1 на все события (вызовы в Unity-проект не вставлялись).
- `preflight.py --for loc` на one-tap-slice — «не хватает пакета Localization», режим plan.

### Not verified
- Тесты в `tools/test_scripts.py` для новых скриптов не писались (решение пользователя).
- LV3 (гейты и soft lock), LV2 / LV4 / LV5 на нарушениях, LC3 / LC4 / LC5 на нарушениях, строки Ink, AN2 / AN3 / AN4 — в данных примера срабатываний не было.
- Live-режим `loc-build` (пакет Localization не установлен), имена колонок CSV-расширения пакета, импорт в String Table Collection, привязки `LocalizedString` в UXML.
- Вызовы аналитики в игре, EditMode-тесты бэкенда, запись JSONL в play mode.

## [0.6.0] — 2026-09-24 · gd 0.6.0, gd-build 0.3.0 — волна B: контент и выпуск

Архитектура — `research/2026-09-production-cycle-architecture.md` §3, волна B (B1 — инструменты уже были, B2 — звук). Инструменты поставлены на машине разработки: ffmpeg 9.0.1, SoX 14.4.2, FluidSynth 2.6.1, FluidR3_GM, Blender MCP 2.0.4 (телеметрия выключена).

### Added — gd-build
- `perf-check` + `/gd-build:perf`: замер против `tech/budgets.md` через профайлер MCP; `compare_perf.py` (PF1–PF4: не замерено, p95 хуже бюджета, регрессия, редактор ≠ устройство).
- `build-release` + `/gd-build:release`: `check_release.py` (RL1–RL6: версия ≠ тегу, .gitignore, бинарники без LFS, секреты CI по именам, development-флаг, SteamPipe VDF), шаблон GameCI, hotfix и откат.
- `model-build` + `/gd-build:model`: `blender_blockout.py` (headless Blender: блокаут по габаритам, материалы по ролям, LOD, клип, GLB, турнтейбл 8×45°); `check_glb.py` на stdlib (GL1–GL9). Blender MCP — канал доводки формы; платные инструменты запрещены.
- `anim-build` + `/gd-build:anim`: пружины, Animation Rigging, клипы из Blender; проверка через `check_glb.py` и `check_juice.py`.
- `sfx-design` + `/gd-build:sfx`: `synth_sfx.py` (слои транзиент / тело / хвост, вариации и seed — побайтно повторяемо, нормализация по LUFS), `loudness.py` (BS.1770 на stdlib, совпадает с ffmpeg ebur128), `check_audio_files.py` (AF1–AF6: покрытие событий, вариации, формат, громкость и true peak через ffmpeg, лицензии, `ph_`).
- `music-build` + `/gd-build:music`: `midi_write.py` (SMF type 1 на stdlib, стемы), `render_cue.py` (FluidSynth, длина петли кратна такту, хвост складывается в начало, общая нормализация стемов), `check_music.py` (MU1–MU6).
- `slice-build/scripts/preflight.py`: `--for sfx|music|model|anim|fmod|release`, поиск Blender (Program Files, `<диск>:\Blender`, Steam), Blender MCP, ffmpeg, sox, FluidSynth, SoundFont, fmodstudiocl.

### Changed — gd
- Агент `art-director`: турнтейблы моделей и скриншоты билда, числа из `check_glb.py`.
- Агент `audio-director`: видит `music-cues.md` и `files.md`.
- Шаблон `templates/design/audio/music-cues.md` (общий формат).

### Tooling
- `tools/trigger_cases.md`: +18 пар (49 запросов).

### Not verified
- Тесты в `tools/test_scripts.py` для новых скриптов не добавлялись и не запускались (решение пользователя), в том числе после правки `preflight.py`.
- Живой замер профайлера сериями, сборка игрока через `manage_build`, процедурная пружина в Unity, workflow GameCI (нет секретов), импорт стемов и SFX в FMOD, звучание (слушает человек).
- Скрипты запускались по разу на данных `examples/one-tap-slice` во временной папке; в пример артефакты не добавлялись.

## [0.5.0] — 2026-09-24 · gd 0.5.0, gd-build 0.2.0 — волна A: из слайса в игру

Стадии 13–16 (продакшн по майлстоунам, полировка, релиз, после релиза) и первые скиллы продакшна. Архитектура — `research/2026-09-production-cycle-architecture.md` (утверждена). Живой прогон на `examples/one-tap-slice` (Unity 6000.3.24f1 + unity-mcp 10.2.0 + FMOD 2.03.14) — `RESULTS.md`, раздел «Волна A».

### Added — gd-build
- `feature-build` + `/gd-build:feature`: система майлстоуна из GDD, тест первым, лог по каждому R / F / E / ED; `check_build_log.py` (BL1–BL6, общий для логов слайса и систем).
- Агент `code-reviewer` + `/gd-build:review`: видит только diff, GDD, архитектуру и тест-план; Pass 0 «намерение дизайна» (по gstack-game), вердикт PASS / CONCERNS / FAIL.
- `juice-build` + `/gd-build:juice`: отклик на события с замером в кадрах; `check_juice.py` (JU1–JU4).
- `ui-build` + `/gd-build:ui`: HUD и экраны на UI Toolkit по `ux/hud.md`; `check_ui.py` (UI1–UI5: элементы, роли палитры, ключи вместо текста, скриншоты, тач-цели).
- `asset-integrate` + `/gd-build:assets`: импорт по asset-list; `check_import.py` (IM1–IM7, бюджеты PNG и GLB на stdlib).
- `qa-run`: soak `--baseline` (наклон памяти простоя вычитается: в редакторе память растёт и без игры); режимы `visual` (`diff_png.py` — PNG на zlib/struct, маски, эталоны утверждает человек, кандидаты в `_pending/`) и `soak` (`check_soak.py`: утечка памяти, деградация кадра, исключения, рост объектов, «игра простаивала»).
- `fmod-sync`: банки из колонки `Bank`, импорт файлов из `design/audio/files.md` (SingleSound / MultiSound, headless), режим `hook` — `check_fmod_calls.py` (FH1–FH4).

### Added — gd
- `gd-router` / `pipeline.md`: стадии 13–16, эвристики, новые возвраты, шаги человека (🟨).
- `gd-handoff`: режим `milestone` (Alpha / Beta, критерии `ED-<system>-N`).
- `qa-plan`: типы `visual` и `perf`; `check_coverage.py` Q9 (визуал не уходит в manual без причины) и Q10 (строка бюджета без perf-кейса), несколько планов и хендоффов за раз.
- Общие форматы: колонка `Bank` в `event-map.md`, `Budget` в asset-list, `Name` / `Loc key` в `ux/hud.md`, ID `B1…` в `tech/budgets.md`, `audio/files.md`, `qa/visual/`, `qa/perf/`.

### Fixed (найдено живым прогоном)
- `check_ui.py`: селектор `#fade` принимался за цвет. `check_fmod_calls.py`, `check_import.py`: путь проекта с `/Temp/` отключал проверку. `check_juice.py`: несколько фаз одного FB. `check_coverage.py`: план майлстоуна дополняет план слайса.
- Методика: ScriptableObject в файле с другим именем даёт ассет без скрипта; PlayMode-тесты без уборки ломают соседей; `render_ui` в play mode игнорирует размер; редактор без фокуса перестаёт тикать без `runInBackground`; кириллица в выводе CLI unity-mcp теряется.

### Tooling
- `tools/check_plugins.py`: P9 копии общего кода совпадают с оригиналом, P10 платные инструменты только в запретах, P11 `tools/trigger_cases.md` (31 запрос → ожидаемый скилл).
- `tools/test_scripts.py`: 37 тестов (было 27).

### Not verified
- Android-билд и перф на устройстве; FMOD for Unity; эталоны `qa/visual/` не утверждены (ждут человека); плейтест DD-chain-1.

## [gd-build 0.1.2, gd 0.4.1] — 2026-09-24

Первый живой прогон `gd-build`: Unity 6000.3.24f1 + CoplayDev/unity-mcp 10.2.0 + FMOD Studio 2.03.14 на `examples/one-tap-slice` (итоги и найденные дефекты — `examples/one-tap-slice/RESULTS.md`).

### Fixed — gd-build
- `run-tests-headless.ps1`: **ложный зелёный** — упавший тест давал exit 0 (PowerShell 5.1 не отдавал `ExitCode`). Теперь `failed > 0` в XML = exit 2. Новые `.meta` не вызывают предупреждение об изменённом дереве (и в `.sh`).
- `fmod-sync`: параметры больше не дублируются при повторном запуске и не получают имена вида `charge (2)`: один `ParameterPreset` на имя подключается ко всем событиям; глобальные — `isGlobal`, без ручного шага. События назначаются в мастер-банк (без банка их нет ни в сборке, ни в `GUIDs.txt`).
- `parse_nunit.py` читает T-ID из `[NUnit.Framework.Property("TID", …)]`: `[Category("T-…")]` NUnit не принимает («-» запрещён).
- `verify-loop.md`, `mcp-actions.md`: верный путь к логу редактора; не гонять тесты при ошибках компиляции (MCP прогонит старую DLL); `refresh` с `force`; ожидание моста после domain reload; `queueEventOnly: true` в InputTestFixture; `testables`; ориентация Game view; активная сцена.

### Added — gd-build
- `gd_sync_event_map.cli.js` — headless-синхронизация через `fmodstudiocl -script` (сохранение и экспорт `Build/GUIDs.txt`); `diff_fmod.py` сверяет и параметры.
- `preflight.py`: проверка `testables` для InputTestFixture и Active Input Handling.
- `mcp-actions.md`: имена инструментов проверены вживую на v10.2.0; старт сессии моста, отключение телеметрии (`DISABLE_TELEMETRY`), CLI `unity-mcp` для текущей сессии Claude Code, закрытие редактора через `File/Exit`.
- Живые фикстуры `examples/one-tap-slice/fixtures/live/` (NUnit XML Unity, `GUIDs.txt` FMOD) и 4 теста в `tools/test_scripts.py` (27 всего).

### Fixed — gd
- `qa-plan/references/qa-method.md`: T-ID в тестах — имя метода или `Property("TID", …)`, не `Category`.

### Not verified
- Android-билд и перф на устройстве; FMOD for Unity (`RuntimeManager.*`) — пакет требует входа на fmod.com; запуск JS из меню FMOD Studio GUI; MCP как инструменты сессии (использовался CLI того же сервера).

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
