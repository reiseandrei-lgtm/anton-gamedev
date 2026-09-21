# anton-gamedev

Личный маркетплейс плагинов для геймдизайна и нарративного дизайна. Один плагин — **`gd`**: пайплайн от искры до хендоффа, который говорит на языке MDA / SDT / Flow / столпов и не пишет художественный текст без запроса.

Работает в **Claude Code** и **Claude Cowork**.

```
искра → концепт → структура систем → GDD → независимое ревью → баланс → скоуп → хендофф
```

## Что внутри

**Команды** (вызываются как `/gd:<имя>`)

| Команда | Что делает |
|---|---|
| `/gd:start` | Triage проекта по `design/` и один следующий шаг |
| `/gd:gdd <система>` | Черновик GDD системы по шаблону (`--quick` — правка) |
| `/gd:review <файл>` | Независимое ревью агентом design-critic (`--all` — кросс-ревью) |
| `/gd:narrative <сцена/ветка>` | Нарративная проработка агентом narrative-designer (`--text` — разрешить реплики) |
| `/gd:balance <система>` | Проверка баланса и таблица чисел |
| `/gd:scope` | Ревизия скоупа агентом producer |
| `/gd:ink <слайс>` | План, замки/ключи и каркас Ink-слайса (`--text` — с репликами) |

**Скиллы** (срабатывают автоматически по описанию): `gd-router`, `gd-concept`, `gd-systems-map`, `gdd-author`, `gdd-review`, `game-feel`, `balance-check`, `scope-check`, `gd-handoff`, `narrative-structure`, `character-voice`, `ink-slice`.

**Проектные скиллы**: `syncario-gamedesigner` — геймдизайн Syncario (канон, столпы, north star, якорь «Сифа», voice/social/метрики). Для своего проекта главнее общих скиллов.

**Агенты**: `design-critic` (ревью без истории создания), `narrative-designer` (структура, не проза), `producer` (скоуп и вырезание для соло / 2–4 человек).

## Установка в Claude Code

После того как репозиторий опубликован (например, на GitHub):

```
/plugin marketplace add <github-user>/anton-gamedev
/plugin install gd@anton-gamedev
```

Локально, до публикации:

```
/plugin marketplace add "D:/Claude Projects/MASTER GDD"
/plugin install gd@anton-gamedev
```

Перезапусти сессию или выполни `/reload-plugins`. Проверка: `/gd:start`.

## Установка в Cowork

1. **Customize → Plugins → Add marketplace**.
2. Вставь URL репозитория (`https://github.com/<github-user>/anton-gamedev`). Для приватного репозитория нужен доступ аккаунта Claude к GitHub.
3. В списке плагинов маркетплейса включи **gd**.

В Cowork работают скиллы, команды и агенты. Папка `design/` должна быть в той папке/репозитории, которую ты открыл в Cowork.

## Обновление

1. Внеси изменения, **подними `version` в `plugins/gd/.claude-plugin/plugin.json`** (без этого клиенты не увидят обновление), допиши `CHANGELOG.md`, сделай коммит и тег, запушь.
2. Claude Code: `/plugin marketplace update anton-gamedev`, затем `/plugin update gd@anton-gamedev` (или через `/plugin` → Installed).
3. Cowork: обнови маркетплейс в Customize → Plugins. **Если версия «залипла»** (старое поведение после обновления) — удали плагин `gd` и установи заново.

Локальный маркетплейс из папки версию не пинит: изменения подхватываются после `/reload-plugins`.

## Подключение шаблона `design/` к игровому проекту

`design/` — общий мост между Cowork и Claude Code: все документы живут в репозитории игры.

Вариант 1 — автоматически: открой папку игры и запусти `/gd:start`. Если `design/` нет, команда предложит создать её из шаблона.

Вариант 2 — вручную (Claude Code уже клонировал маркетплейс):

```bash
cp -r ~/.claude/plugins/marketplaces/anton-gamedev/templates/design ./design
```

Вариант 3 — из этого репозитория: скопируй `templates/design/` в корень игры.

У каждого документа во frontmatter есть `status: template | draft | review | approved` — по нему роутер определяет стадию.

## Свои скиллы

Положи их в `import/` (см. `import/README.md`) и попроси Claude Code: «встрой скиллы из import/». Проектные скиллы останутся отдельными, общие принципы уйдут в роутер (`gd-router/references/principles.md`).

**Syncario:** после установки плагина отключи старую копию скилла `gamedesigner` в claude.ai (Настройки → Возможности → Скиллы), иначе в Cowork/claude.ai будут срабатывать два одинаковых скилла. Главная копия теперь — `plugins/gd/skills/syncario-gamedesigner/`, оригинал хранится в `import/gamedesigner/`.

## Unity и FMOD

В этот плагин **не входят**. Для реализации в Unity поставь официальный **Unity Plugin for Claude Code** (работает только в Claude Code). Плагин `gd` заканчивается на хендоффе (`design/handoff/<slice>.md`) — это вход для реализации. FMOD упоминается только как соглашение по тегам/событиям в дизайн-документах.

## Структура репозитория

```
.claude-plugin/marketplace.json
plugins/gd/
  .claude-plugin/plugin.json
  skills/<name>/SKILL.md (+ references/)
  commands/*.md
  agents/*.md
templates/design/        шаблон design/ для игр
import/                  твои скиллы для интеграции
README.md CLAUDE.md ATTRIBUTION.md CHANGELOG.md
```

## Лицензии

Часть методологии адаптирована из MIT-проектов — см. [ATTRIBUTION.md](ATTRIBUTION.md).
