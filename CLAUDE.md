# CLAUDE.md — anton-gamedev

Репозиторий маркетплейса Claude Code / Cowork с одним плагином `gd` (геймдизайн + нарративный дизайн).

## Правила редактирования плагина
- Схема: `.claude-plugin/marketplace.json` (маркетплейс), `plugins/gd/.claude-plugin/plugin.json` (плагин). `version` — только в `plugin.json`, не дублировать в marketplace.json.
- Каждый скилл: `plugins/gd/skills/<name>/SKILL.md` с frontmatter `name` (= имя папки) и `description` (триггеры RU + EN + «не для …»). SKILL.md короткий (≲60 строк), детали — в `references/`.
- Триггеры скиллов не должны пересекаться. Добавляя скилл, проверь описания соседей.
- Команды (`commands/*.md`) имеют `disable-model-invocation: true` — автосрабатывание делают скиллы, команды только по явному вызову.
- Во всех скиллах и агентах: ответ на языке запроса; художественный текст только по явной просьбе; без воды.
- Unity/FMOD-реализацию в плагин не добавлять (для этого официальный Unity-плагин).
- Заимствование из чужого репозитория → запись в `ATTRIBUTION.md` + шапка источника в файле.

## Выпуск версии
1. `claude plugin validate .` — без ошибок.
2. Поднять `version` в `plugins/gd/.claude-plugin/plugin.json`, запись в `CHANGELOG.md`.
3. Коммит, тег `vX.Y.Z`.

## Папки
- `vendor/` — временные клоны исходников (в .gitignore, можно удалить).
- `import/` — пользовательские скиллы для интеграции; оригиналы не изменять.
- `templates/design/` — шаблон `design/` для игровых репозиториев; держать синхронным с шаблонами в `skills/*/references/`.
