# CLAUDE.md — anton-gamedev

Репозиторий маркетплейса Claude Code / Cowork с двумя плагинами:
- `gd` — геймдизайн, нарратив и направляющие документы (арт, звук, UX, тех-дизайн, тест-план, плейтест, метрики). Работает в Claude Code и Cowork.
- `gd-build` — сборка Unity-слайса и систем майлстоуна, ревью кода, отклик, UI, импорт ассетов, тесты (в том числе visual и soak), синхронизация FMOD. Только Claude Code (нужны файлы Unity-проекта и бесплатный Unity MCP).

## Правила редактирования плагинов
- Схема: `.claude-plugin/marketplace.json` (маркетплейс), `plugins/<plugin>/.claude-plugin/plugin.json` (плагин). `version` — только в `plugin.json`, не дублировать в marketplace.json.
- Каждый скилл: `plugins/<plugin>/skills/<name>/SKILL.md` с frontmatter `name` (= имя папки) и `description` (триггеры RU + EN + «не для …»). SKILL.md короткий (≲60 строк), детали — в `references/`, детерминированные проверки — в `scripts/` (Python stdlib, вывод в UTF-8).
- Триггеры скиллов не должны пересекаться — в том числе между `gd` и `gd-build`. Проверка: `python tools/check_plugins.py`; новый скилл — добавь его пары «запрос → скилл» в `tools/trigger_cases.md`.
- Команды (`commands/*.md`) имеют `disable-model-invocation: true` — автосрабатывание делают скиллы, команды только по явному вызову. Description с двоеточием — в кавычках (иначе YAML не парсится).
- Агенты-ревьюеры видят только артефакт: `omitClaudeMd: true`, в задачу передаются только пути (образцы — `gd/agents/design-critic.md`, `gd-build/agents/code-reviewer.md`).
- Во всех скиллах и агентах: ответ на языке запроса; художественный текст только по явной просьбе (`--text`); без воды.
- Только бесплатные инструменты: не подключать платные модели, сервисы генерации, подписки, API-ключи (см. `gd-router/references/principles.md`).
- `gd` — без Unity/FMOD-действий и кода: только соглашения (нейминг, бюджеты, структура). Действия в Unity Editor, FMOD Studio и код — только в `gd-build`. How-to по API Unity — официальный Unity Plugin (не копировать: Unity Companion License).
- Скрипты `gd` импортируют общий парсер `skills/gd-router/scripts/gdd_ids.py`; скрипты `gd-build` самодостаточны (другой плагин может быть не установлен) и импортируют побайтную копию `gd-build/skills/slice-build/scripts/gdd_ids.py`. Меняешь оригинал — скопируй (проверка P9 в `check_plugins.py`, список копий — `COPIES`). Общие форматы (`event-map.md`, `audio/files.md`, `art/asset-list.md`, `ux/hud.md`, `tech/budgets.md`, логи `build/`) перечислены в `research/2026-09-production-cycle-architecture.md` §4 — меняешь в одном скилле, меняй во всех и в шаблоне.
- Заимствование из чужого репозитория → запись в `ATTRIBUTION.md` + шапка источника в файле. Только MIT / Apache-2.0 / совместимые; без лицензии и GPL — не брать.

## Выпуск версии
1. `claude plugin validate .`, `claude plugin validate plugins/gd`, `claude plugin validate plugins/gd-build` — без ошибок.
2. `python tools/check_plugins.py` и `python -m unittest tools/test_scripts.py` — без FAIL.
3. Поднять `version` в `plugin.json` изменённых плагинов, запись в `CHANGELOG.md`.
4. Ветка → PR в main → после мержа тег `vX.Y.Z` (по версии `gd`).

## Папки
- `vendor/` — временные клоны исходников (в .gitignore, можно удалить).
- `import/` — пользовательские скиллы для интеграции; оригиналы не изменять.
- `templates/design/` — шаблон `design/` для игровых репозиториев; держать синхронным с шаблонами в `skills/*/references/`.
- `examples/one-tap-slice/` — тестовый мини-проект: на нём прогоняются скиллы и тесты скриптов (`RESULTS.md`).
- `tools/` — проверки репозитория и тесты скриптов (не входят в плагины).
- `research/` — ресерч и архитектурные решения по развитию маркетплейса.
