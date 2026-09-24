# anton-gamedev

Личный маркетплейс плагинов для полного цикла инди-игры на Unity 6 + FMOD — от искры до плейтеста и продакшна по майлстоунам. Говорит на языке MDA / SDT / Flow / столпов, не пишет художественный текст без запроса и использует **только бесплатные инструменты**.

| Плагин | Где работает | Что делает |
|---|---|---|
| **`gd`** | Claude Code и Claude Cowork | Геймдизайн, нарратив и направляющие документы: арт, звук, UX, тех-дизайн, тест-план, плейтест, метрики |
| **`gd-build`** | Только Claude Code | Сборка Unity-слайса и систем майлстоуна через бесплатный Unity MCP, независимое ревью кода, отклик (juice), UI Toolkit, импорт ассетов, тесты, скриншоты против эталонов, soak, синхронизация FMOD. Без MCP — план и чеклист |

```
искра → концепт → системы → GDD → ревью → баланс → скоуп → хендофф
  → подготовка сборки (тех-дизайн, тест-план) → сборка [gd-build] → QA [gd-build] → плейтест → решение ↺
  ─advance→ продакшн: хендофф майлстоуна → система [gd-build] → ревью кода → QA → полировка и перф → релиз → после релиза ↺
параллельно: нарратив · континуити · арт (→ импорт [gd-build]) · звук (→ FMOD [gd-build]) · UX (→ UI [gd-build]) · метрики · game feel (→ juice [gd-build])
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
| `/gd:continuity [register\|check\|impact]` | Континуити: промисы (сетап → пэйофф), знание игрока, канон; проверка `.ink` скриптом |
| `/gd:art [bible\|assets\|check\|review]` | Арт-библия, список ассетов, проверка палитры (контраст, grayscale, дальтонизм); ревью агентом art-director |
| `/gd:audio [bible\|events\|check\|review]` | Аудио-библия, карта событий FMOD, покрытие Feedback из GDD; ревью агентом audio-director |
| `/gd:ux [ftue\|hud\|a11y]` | FTUE и туториал, HUD, чеклист доступности |
| `/gd:tech [<slice>\|adr\|check]` | Тех-дизайн Unity: модули, config map (knob → поле), сохранения, бюджеты, ADR |
| `/gd:qa-plan <slice> [--review]` | Тест-план из GDD и хендоффа с трассировкой покрытия; ревью агентом qa-lead |
| `/gd:playtest [plan\|analyze] <slice>` | Протокол плейтеста с порогом; независимый анализ заметок агентом playtest-analyst |
| `/gd:metrics [<slice>\|check]` | Вопросы → KPI → события → воронки |
| `/gd:level <level> [check]` | Уровень: метрики из knobs, критический путь, встречи, темп, гейты; проверка достижимости и темпа |
| `/gd:release-plan [store\|launch\|postlaunch\|check]` | Страница магазина (аудит), вехи и чеклист запуска, метрики после релиза; тексты для игроков — только человек |

**Команды `gd-build`** (`/gd-build:<имя>`, только Claude Code)

| Команда | Что делает |
|---|---|
| `/gd-build:slice <slice>` | Играбельный Unity-слайс из хендоффа: тест первым, verify loop, лог доказательств по ED |
| `/gd-build:feature <system>` | Система майлстоуна из GDD: тест первым, verify loop, лог по каждому R / F / E |
| `/gd-build:review <system>` | Независимое ревью кода агентом code-reviewer (видит только diff, GDD, архитектуру, тест-план) |
| `/gd-build:juice <system>` | Отклик на события (частицы, камера, hitstop, squash) с замером в кадрах против Game Feel |
| `/gd-build:ui [hud\|restart\|…]` | HUD и экраны на UI Toolkit по `ux/hud.md`: роли палитры, ключи локализации, скриншоты в 2–3 разрешениях |
| `/gd-build:assets [check\|import\|replace]` | Импорт ассетов по asset-list, замена плейсхолдеров, бюджеты и лицензии |
| `/gd-build:test [suite\|smoke\|input\|visual\|soak\|bug]` | EditMode / PlayMode через MCP или headless, smoke, сверка скриншотов с эталонами, долгий прогон на утечки, баг-репорты; 0 тестов = FAIL |
| `/gd-build:perf`, `/gd-build:release`, `/gd-build:model`, `/gd-build:anim`, `/gd-build:sfx`, `/gd-build:music` | Замер против бюджетов, релизная сборка, модели и анимация в Blender, синтез SFX, музыкальные петли (волна B, см. `CHANGELOG.md`) |
| `/gd-build:loc [scan\|tables\|check]` | Таблицы Unity Localization из ключей UI и Ink, лимиты длины, псевдо-удлинение; без пакета — режим plan |
| `/gd-build:analytics [gen\|wire\|check]` | `AnalyticsEvents.cs` из events.md, локальный JSONL-лог с согласием, проверка вызовов |
| `/gd-build:fmod [sync\|diff\|unity\|hook]` | Карта событий → FMOD Studio (банки, файлы звука; headless через `fmodstudiocl`) + `FmodEvents.cs`, сверка по GUIDs, проверка вызовов в коде |

**Скиллы `gd`** (срабатывают автоматически по описанию): `gd-router`, `gd-concept`, `gd-systems-map`, `gdd-author`, `gdd-review`, `game-feel`, `balance-check`, `scope-check`, `gd-handoff`, `narrative-structure`, `character-voice`, `ink-slice`, `narrative-continuity`, `art-direction`, `audio-direction`, `ux-onboarding`, `tech-design`, `qa-plan`, `playtest`, `metrics-plan`, `level-design`, `release-plan`.

**Скиллы `gd-build`**: `slice-build`, `feature-build`, `juice-build`, `ui-build`, `asset-integrate`, `qa-run`, `fmod-sync`, `perf-check`, `build-release`, `model-build`, `anim-build`, `sfx-design`, `music-build`, `loc-build`, `analytics-build`. **Агент `gd-build`**: `code-reviewer`.

У каждого нового скилла есть детерминированная проверка в `scripts/` (Python stdlib): палитра, ассеты, карта событий, knobs → конфиги, покрытие тестами (в том числе visual и perf), события аналитики, коды плейтеста, результаты NUnit, сверка с FMOD, лог сборки, тайминги отклика, UI против hud.md, импорт ассетов, diff PNG, soak, перф, релиз, GLB, звук, музыка, уровни, план выпуска, локализация, вызовы аналитики.

**Проектные скиллы**: `syncario-gamedesigner` — геймдизайн Syncario (канон, столпы, north star, якорь «Сифа», voice/social/метрики). Для своего проекта главнее общих скиллов.

**Агенты**: `design-critic` (ревью без истории создания), `narrative-designer` (структура, не проза), `producer` (скоуп и вырезание для соло / 2–4 человек). Ревьюеры, видящие только артефакт: `art-director`, `audio-director`, `qa-lead`, `playtest-analyst` (последний не видит даже GDD — чтобы не подгонять наблюдения под замысел).

## Установка в Claude Code

После того как репозиторий опубликован (например, на GitHub):

```
/plugin marketplace add reiseandrei-lgtm/anton-gamedev
/plugin install gd@anton-gamedev
/plugin install gd-build@anton-gamedev
```

Локально, до публикации:

```
/plugin marketplace add "D:/Claude Projects/MASTER GDD"
/plugin install gd@anton-gamedev
/plugin install gd-build@anton-gamedev
```

Перезапусти сессию или выполни `/reload-plugins`. Проверка: `/gd:start`.

## Установка в Cowork

1. **Customize → Plugins → Add marketplace**.
2. Вставь URL репозитория (`https://github.com/reiseandrei-lgtm/anton-gamedev`). Для приватного репозитория нужен доступ аккаунта Claude к GitHub.
3. В списке плагинов маркетплейса включи **gd**. `gd-build` в Cowork не ставь: ему нужен Unity-проект и Unity MCP.

В Cowork работают скиллы, команды и агенты `gd`. Шаги сборки и тестов роутер там отдаёт чеклистом. Папка `design/` должна быть в той папке/репозитории, которую ты открыл в Cowork.

## Обновление

1. Внеси изменения, **подними `version` в `plugins/<plugin>/.claude-plugin/plugin.json`** изменённого плагина (без этого клиенты не увидят обновление), допиши `CHANGELOG.md`, прогони проверки (см. CLAUDE.md), сделай PR, после мержа — тег.
2. Claude Code: `/plugin marketplace update anton-gamedev`, затем `/plugin update gd@anton-gamedev` и `/plugin update gd-build@anton-gamedev` (или через `/plugin` → Installed).
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

## Unity и FMOD (`gd-build`)

Только бесплатное:

| Что | Зачем | Цена |
|---|---|---|
| Unity 6 Personal | движок | бесплатно в пределах Personal |
| [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp) (MIT) | управление редактором: скрипты, сцены, тесты, консоль, скриншоты | бесплатно; инструменты генерации (`generate_*`) платные — скиллы их не вызывают |
| FMOD Studio + FMOD for Unity | звук | бесплатно по Indie-лицензии в её пределах (условия — fmod.com) |
| Официальный Unity Plugin (`/plugin marketplace add Unity-Technologies/unity-agent-plugin`, затем `/plugin install unity@unity-agent-plugin`) | справочник how-to по API Unity | бесплатно; его MCP через Unity AI требует подписки — не используется |

Проверено вживую 2026-09-24 на Unity 6000.3.24f1, CoplayDev/unity-mcp 10.2.0 и FMOD Studio 2.03.14 (`examples/one-tap-slice/RESULTS.md`). У MCP-сервера и пакета телеметрия включена по умолчанию: запускай их с `DISABLE_TELEMETRY=true`. Карта событий переносится в FMOD и без GUI: `fmodstudiocl -script gd_sync_event_map.cli.js <проект>.fspro`.

### Шаги, которые остаются за тобой (🟨)
Решения о столпах, вырезании, pivot / kill · логины и лицензии (Unity Hub, fmod.com, Steamworks, секреты CI) · пустой проект FMOD Studio · референсы · прослушивание и микс на устройстве · ощущение управления · живые плейтесты · hero-ассеты (главный персонаж, ключевой арт, главная тема) · утверждение статуса `made` и визуальных эталонов (`design/qa/visual/_pending/` → `design/qa/visual/`) · тексты для игроков · финальный Release.

Без Unity MCP `gd-build` работает в режиме **plan**: план задач, чеклист, headless-прогон тестов при закрытом редакторе (`run-tests-headless.ps1/.sh`). Всё, что не проверено в редакторе, так и помечается.

`gd` Unity-действий не делает: он пишет соглашения (нейминг событий FMOD, модули, config map, бюджеты), которые `gd-build` исполняет.

## Структура репозитория

```
.claude-plugin/marketplace.json
plugins/gd/
  .claude-plugin/plugin.json
  skills/<name>/SKILL.md (+ references/, scripts/)
  commands/*.md
  agents/*.md
plugins/gd-build/        то же для сборки и тестов
templates/design/        шаблон design/ для игр
examples/one-tap-slice/  тестовый мини-проект и результаты прогона скиллов
tools/                   проверки репозитория и тесты скриптов
research/                ресерч и архитектура
import/                  твои скиллы для интеграции
README.md CLAUDE.md ATTRIBUTION.md CHANGELOG.md
```

## Лицензии

Репозиторий и плагины — [MIT](LICENSE) © 2026 Anton. Часть методологии адаптирована из сторонних MIT-проектов; их copyright и тексты лицензий — в [ATTRIBUTION.md](ATTRIBUTION.md).
