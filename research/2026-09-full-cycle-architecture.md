---
status: approved   # template | draft | review | approved
updated: 2026-09-23
owner: Anton
---

# Фаза 2. Архитектура расширения на полный цикл (предложение, не реализация)

Вход: `research/2026-09-full-cycle.md`. Ограничение пользователя: **только бесплатные инструменты**. Никаких платных моделей, API-ключей и подписок.

## 0. Что считаем бесплатным

| Инструмент | Статус | Как используем |
|---|---|---|
| Unity 6 Personal | Бесплатен в пределах лимитов Personal (условия проверить на unity.com) | Движок |
| CoplayDev/unity-mcp (MIT) | Бесплатен | Основной Unity MCP. **Инструменты `generate_image` / `generate_audio` / `generate_model` запрещены в скиллах**: генерация платная |
| IvanMurzak/Unity-MCP (Apache-2.0) | Бесплатен | Запасной MCP |
| Официальный Unity Plugin (скиллы) | Бесплатен, Companion License | Ставится рядом как справочник how-to. Код не копируем |
| Официальный Unity MCP (AI Assistant) | **Нужен trial или подписка Unity AI** | **Не используем** |
| FMOD Studio + FMOD for Unity | Бесплатен по Indie-лицензии для малых бюджетов (порог проверить на fmod.com) | Аудио |
| FMOD Studio MCP (raffyknowsnothing, MIT) | Бесплатен, незрелый | Опционально. Основной путь — генерируемый JS-скрипт для консоли FMOD Studio |
| Blender + blender-mcp (MIT) | Бесплатны | Опционально, не в волне 1 |
| Python 3 stdlib | Бесплатен | Все проверочные скрипты: stdlib only, без pip |
| CC0-ассеты (Kenney, OpenGameArt с проверкой лицензии) | Бесплатны | Плейсхолдеры |
| ElevenLabs, PixelLab, Scenario, Meshy, генерация Coplay, AltTester Cloud | Платно или нужен ключ | **Исключены** |

## 1. Один плагин или несколько

**Решение: два плагина в маркетплейсе `anton-gamedev`.**

| Плагин | Версия | Где работает | Содержимое |
|---|---|---|---|
| `gd` | 0.3.0 → **0.4.0** | Claude Code + Cowork | Дизайн и направляющие документы. +7 скиллов, +4 агента |
| `gd-build` (новый) | **0.1.0** | Только Claude Code (нужен доступ к файлам проекта Unity и MCP) | Сборка слайса, прогон тестов, синхронизация FMOD. 3 скилла |

Обоснование:
1. **Cowork не умеет Unity MCP.** В одном плагине скиллы сборки срабатывали бы в Cowork и не могли ничего сделать. В отдельном плагине в Cowork его просто не ставят.
2. **Контекст.** Описания всех скиллов плагина висят в контексте каждой сессии. `gd` вырастает с 14 до 21 описания. `gd-build` добавляет 3 описания только там, где он нужен.
3. **Правило CLAUDE.md** «Unity/FMOD-реализацию в плагин не добавлять» остаётся верным для `gd`. Уточнение формулировки: *«в `gd` допустимы соглашения (нейминг, бюджеты, структура), действия в Unity Editor / FMOD Studio и код — только в `gd-build`»*.
4. **Не дробить дальше** (`gd-art`, `gd-audio`, `gd-qa`): в каждом было бы по 1–2 скилла, ставить нужно было бы 5 плагинов, а маршрутизация всё равно идёт через один роутер в `gd`.
5. `gd-router` знает обо всех стадиях. Если нужен скилл из `gd-build`, а плагин не установлен или мы в Cowork, роутер пишет: «этот шаг делается в Claude Code с `gd-build`», и даёт ручной чеклист.

## 2. Расширенный пайплайн (предложение для `pipeline.md`)

Стадии 0–7 без изменений. Добавляются стадии 8–11 и треки.

| # | Стадия | Скилл | Вход | Выход (`design/`) | Критерий перехода |
|---|---|---|---|---|---|
| 7 | Хендофф | `gd-handoff` | как сейчас | `handoff/<slice>.md` | Как сейчас **+** у каждого критерия Engineering Done и Design Done стабильный ID (`ED1`, `DD1`) |
| 8 | Подготовка сборки | `tech-design`, `qa-plan` | handoff, GDD слайса | `tech/architecture.md`, `qa/test-plan-<slice>.md` | Каждый Tuning Knob слайса привязан к полю конфига; каждое Core Rule / Edge Case слайса покрыто ≥1 тест-кейсом (скрипт без ошибок); перф-бюджет указан для целевой платформы |
| 9 | Сборка слайса | `slice-build` (gd-build) | 7 + 8 | `build/<slice>.log.md` | Каждый `ED*` имеет доказательство (тест, скриншот, лог) или явную пометку «не выполнено»; компиляция чистая; нулевых прогонов нет |
| 10 | QA | `qa-run` (gd-build) | билд, test-plan | `qa/runs/YYYY-MM-DD-<slice>.md`, `qa/bugs/BUG-NNN.md` | Smoke PASS; нет открытых багов S1 (блокер) и S2 (ломает гипотезу) |
| 11 | Плейтест | `playtest` (`plan` → сессии → `analyze`), агент `playtest-analyst` | билд без S1/S2, гипотеза из handoff | `playtest/YYYY-MM-DD-<slice>.plan.md`, `.report.md` | Порог гипотезы задан **до** сессий; вердикт `confirmed / refuted / inconclusive`; у каждой находки P0/P1 есть адресат (скилл и файл) |
| 12 | Решение | `gd-router` | report плейтеста | `decisions-log.md` | Одно из `iterate` (→ 3/5/UX/арт/звук по адресатам) · `pivot` (→ 1) · `kill` (→ 7, другой слайс) · `advance` (следующий слайс или вертикаль). Записано с причиной |

### Параллельные треки (новые)

| Трек | Скилл | Когда старт | Файлы | Готов к сборке, когда |
|---|---|---|---|---|
| Арт-дирекция | `art-direction`, агент `art-director` | `bible` — после `pillars.md` (draft+); `assets` — после GDD слайса | `art/art-bible.md`, `art/asset-list.md` | Bible в `review`+; у каждого ассета слайса есть источник: `placeholder` / `cc0` / `made`; палитра проходит скрипт |
| Звук | `audio-direction`, агент `audio-director` | `bible` — после `pillars.md`; `events` — после GDD слайса | `audio/audio-bible.md`, `audio/event-map.md` | Каждая строка Feedback-таблицы GDD слайса с аудио имеет событие в карте; скрипт без ошибок |
| UX и онбординг | `ux-onboarding` | После GDD core loop | `ux/ftue.md`, `ux/hud.md`, `ux/accessibility.md` | Для слайса с онбордингом: FTUE-таймлайн и список «чему учим» |
| Метрики | `metrics-plan` | После handoff (гипотеза есть) | `analytics/events.md`, `analytics/funnels.md` | У гипотезы есть событие и порог; скрипт без ошибок |
| Game feel | `game-feel` (есть) | По билду — после стадии 10 | как сейчас | — |

### Возвраты назад (добавить)
- Плейтест `refuted` → решение в `decisions-log.md` → `iterate` или `pivot`.
- Находка плейтеста о понимании → `ux-onboarding`; о чувстве → `game-feel`; о числах → `balance-check`; о правилах → `gdd-author --quick`.
- Баг, который оказался дырой в дизайне (Edge Case не описан) → `gdd-author --quick` → `qa-plan` пересчитывает покрытие.
- `slice-build` уткнулся в неоднозначность хендоффа → стоп, вопрос в `handoff/<slice>.md` → Open Questions. Решения за дизайнера не принимает.

### Эвристики роутера (добавить)
- Есть `handoff/*.md` в `approved`, но нет `qa/test-plan-*` → стадия 8.
- Есть `build/<slice>.log.md`, но нет `qa/runs/*` новее него → стадия 10.
- Есть `qa/runs` с PASS, но нет `playtest/*.plan.md` → стадия 11.
- Есть `playtest/*.report.md` без строки в `decisions-log.md` → стадия 12.
- `pillars.md` в `review`+, а `art/art-bible.md` и `audio/audio-bible.md` ещё `template` → предложить треки параллельно (не блокер до стадии 9).

## 3. Скиллы волны 1 (10)

Общее для всех: язык ответа = язык запроса; художественный текст только с `--text`; документы в `design/` с `status: template | draft | review | approved`; решение → `decisions-log.md`; маркировка ФАКТ / РЕКОНСТРУКЦИЯ / ГИПОТЕЗА по `principles.md`; SKILL.md ≲ 60 строк, детали в `references/`, скрипты — Python stdlib.

### Плагин `gd`

#### 3.1 `art-direction`
- **Description:**
  Арт-дирекция игры: визуальные столпы из игровых, палитра с ролями, value-структура и читаемость в grayscale, силуэты и shape language, масштаб и мин. размеры на экране, список ассетов слайса с неймингом и источником (placeholder / CC0 / свой). Пишет design/art/art-bible.md и design/art/asset-list.md.
  Триггеры RU: «арт-библия», «визуальный стиль», «палитра», «читаемость», «силуэты», «референсы по арту», «список ассетов», «арт-дирекция».
  Triggers EN: "art bible", "visual style", "color palette", "readability", "silhouette", "asset list", "art direction".
  Не для отклика и джуса механики (game-feel), не для HUD и туториала (ux-onboarding), не для генерации изображений.
- **Режимы:** `bible` · `assets` · `check`.
- **Вход:** `pillars.md`, `concept.md`; для `assets` — GDD слайса (таблица Feedback / Visual) и `handoff/<slice>.md`.
- **Выход:** `art/art-bible.md`, `art/asset-list.md`.
- **Алгоритм (bible):** визуальный столп → какой игровой столп обслуживает (без связи — вырезать) → 3–5 референсов с «что берём / чего избегаем» (референсы даёт пользователь, скилл их не ищет и не генерирует) → палитра по ролям (`bg`, `gameplay-critical`, `interactive`, `danger`, `ui`, `accent`) в HEX → правило value: gameplay-critical читается в grayscale → силуэт: у ключевых сущностей узнаваемый силуэт на целевом размере → shape language (форма ↔ смысл) → мин. размер на экране для мобайла → анимационные принципы (ссылка на game-feel) → бюджеты (текстуры, атласы).
- **Скрипты:** `scripts/check_palette.py` — контраст по WCAG и дельта яркости в grayscale для обязательных пар ролей (`gameplay-critical/bg`, `danger/bg`, `ui/bg`), симуляция дейтеранопии и протанопии для пар, которые различаются только цветом. `scripts/check_assets.py` — нейминг (`<type>_<entity>_<variant>_<state>`), обязательные поля, ассеты слайса без источника, дубли ID.
- **Done:** bible в `draft`, скрипт палитры без FAIL, каждый визуальный столп связан с игровым, список ассетов слайса конечный (без «и т.д.»).
- **Агент:** `art-director` (ревьюер, `omitClaudeMd`). Видит только `art/*.md` + `pillars.md` (+ скриншоты билда, если переданы путём). Пишет `reviews/YYYY-MM-DD-art.md`.
- **Источники:** CCGS `art-bible` + шаблон; gstack-game `asset-review` (`naming-conventions`, `benchmarks`), `game-visual-qa` (`visual-thresholds`). Адаптация, MIT.

#### 3.2 `audio-direction`
- **Description:**
  Звуковая дирекция и карта событий FMOD: audio-столпы из игровых, sonic identity, музыка по состояниям игры (адаптивность, переходы), приоритеты микса и громкость, SFX-лист из Feedback-таблиц GDD, карта событий с соглашением по неймингу событий, параметров, шин и снапшотов, VO-лист с ID строк. Пишет design/audio/audio-bible.md и design/audio/event-map.md.
  Триггеры RU: «аудио-библия», «звуковой стиль», «карта событий FMOD», «список SFX», «адаптивная музыка», «микс», «какие звуки нужны».
  Triggers EN: "audio bible", "sound direction", "FMOD event map", "SFX list", "adaptive music", "mix priorities".
  Не для создания событий в FMOD Studio и кода интеграции (gd-build: fmod-sync), не для ощущения механики (game-feel).
- **Режимы:** `bible` · `events` · `check`.
- **Вход:** `pillars.md`; для `events` — GDD (разделы Feedback, Game Feel: anticipation / action / impact / resolution), `narrative/ink/*` для VO.
- **Выход:** `audio/audio-bible.md`, `audio/event-map.md` (таблица: event path · источник GDD `<system>#FB<n>` · тип one-shot / loop / music / VO · параметры · 2D/3D · шина · приоритет · вариации · статус).
- **Соглашение FMOD** (в `references/fmod-conventions.md`): `event:/<Category>/<Subcategory>/<Name>` в PascalCase, категории `SFX`, `UI`, `Music`, `Amb`, `VO`; локальные параметры `snake_case`, глобальные с префиксом `g_`; шины `bus:/Music|SFX|UI|VO|Amb`; снапшоты `snapshot:/<State>`; банки по сценам или контенту. VO: `event:/VO/<Character>/<line_id>` или programmer sound с ID из Ink.
- **Алгоритм (events):** каждая строка Feedback с аудио → событие; каждая фаза game feel (anticipation / impact) → проверить, нужен ли звук; музыкальные состояния из States & Transitions → параметр или снапшот; приоритет микса (что слышно всегда: gameplay-critical > VO > UI > SFX > Amb > Music, настраивается в bible); целевая громкость — ГИПОТЕЗА с диапазоном (мобайл тише консоли), проверять ушами.
- **Скрипт:** `scripts/check_event_map.py` — нейминг, дубли, событие без источника GDD, Feedback-строка с аудио без события (читает `gdd/*.md`), параметры, объявленные, но не используемые, VO-ID, которых нет в `.ink`.
- **Done:** скрипт без ошибок для систем слайса; у каждого события есть приоритет и шина.
- **Агент:** `audio-director` (ревьюер). Видит `audio/*.md` + `pillars.md` + Feedback-разделы GDD. Пишет `reviews/YYYY-MM-DD-audio.md`. Честное правило из unity-kit: «ты не слышишь», качество звука оценивает человек.
- **Источники:** CCGS `sound-bible` (шаблон), unity-kit `unity-audio` (честность проверки). Нейминг FMOD и скрипт — свои.

#### 3.3 `ux-onboarding`
- **Description:**
  UX игры: FTUE и туториал (чему учим, в каком порядке, как — show / do / gate, таймлайн первой сессии, первый «aha»), HUD (инвентарь информации → приоритет → частота → зона экрана, большой палец на мобайле), базовая доступность (Game Accessibility Guidelines basic). Пишет design/ux/ftue.md, hud.md, accessibility.md.
  Триггеры RU: «онбординг», «FTUE», «туториал», «первая сессия», «HUD», «интерфейс боя», «доступность», «accessibility».
  Triggers EN: "onboarding", "FTUE", "tutorial flow", "first session", "HUD layout", "accessibility".
  Не для визуального стиля (art-direction), не для отклика управления (game-feel), не для кода UI (официальный Unity Plugin).
- **Режимы:** `ftue` · `hud` · `a11y`.
- **Алгоритм (ftue):** глаголы core loop → список «игрок должен понять» → порядок по зависимостям → метод обучения на каждый пункт → таймлайн минута за минутой до первого замыкания петли → точки риска ухода → событие метрики на каждый шаг (передаётся в `metrics-plan`). **hud:** инвентарь всех показателей из GDD → нужен ли в каждый момент → приоритет и частота → зона (thumb zones, safe area) → что уходит в меню или делается диегетически. **a11y:** чеклист базового уровня (субтитры, размер текста, не только цвет — ссылка на `check_palette.py`, hold → toggle, пауза везде, ремап, чувствительность) → pass / gap / n/a.
- **Done:** FTUE-таймлайн до первого замыкания петли ≤ целевого времени (задаёт пользователь); у каждого элемента HUD есть приоритет и зона; a11y-чеклист заполнен без пустых строк.
- **Агент:** нет (при необходимости — `design-critic` по документу).
- **Источники:** CCGS `ux-design`, шаблоны `hud-design`, `accessibility-requirements`, `player-journey`; gstack-game `game-ux-review`. Адаптация, MIT.

#### 3.4 `tech-design`
- **Description:**
  Технический дизайн под Unity 6 из GDD и хендоффа, без кода: модули и asmdef из карты систем, данные и конфиги (каждый Tuning Knob → поле ScriptableObject), модель сохранений и версионирование, поток сцен, точки тестируемости, перф-бюджеты под мобайл и PC, ADR для ключевых решений. Пишет design/tech/architecture.md, budgets.md, adr/*.md.
  Триггеры RU: «архитектура проекта», «тех-дизайн», «как устроить конфиги», «сохранения», «перф-бюджет», «ADR», «data-driven».
  Triggers EN: "technical design", "project architecture", "data-driven config", "save system design", "performance budget", "ADR".
  Не для написания C# и действий в редакторе (gd-build: slice-build), не для механики и правил (gdd-author).
- **Вход:** `systems-map.md`, GDD (Tuning Knobs, States, Interactions), `handoff/<slice>.md`.
- **Выход:** `tech/architecture.md` (модули ↔ системы, зависимости без циклов, config-map knob → SO.field, save-модель, сцены, seams для тестов), `tech/budgets.md` (кадр, draw calls, память, размер билда — ГИПОТЕЗА с якорем и сигналом замера), `tech/adr/NNN-<topic>.md`.
- **Скрипт:** `scripts/check_knobs.py` — каждый Tuning Knob систем слайса есть в config-map; в config-map нет полей без knob; модульные зависимости без циклов (как у systems-map).
- **Done:** скрипт без ошибок; бюджеты указаны для целевой платформы; ≥1 ADR на решение с альтернативами.
- **Агент:** нет.
- **Референс движка:** `references/unity-profile.md` (соглашения: asmdef, SO, Addressables — только когда нужно, Input System, UTF-тесты). Ссылки на официальный Unity Plugin для how-to.
- **Источники:** CCGS `create-architecture`, `architecture-decision`, шаблон TDD; unity-kit `gamedev-patterns` (read-only state surface). Адаптация, MIT.

#### 3.5 `qa-plan`
- **Description:**
  Тест-план слайса из GDD и хендоффа: каждое Core Rule, Edge Case и формула → тест-кейсы с ID, тип (EditMode — логика, PlayMode — интеграция и ввод, manual — визуал и звук, playtest — ощущение), smoke-набор билда, формат баг-репорта с severity, трассировка покрытия скриптом. Пишет design/qa/test-plan-<slice>.md.
  Триггеры RU: «тест-план», «что тестировать», «покрытие тестами», «smoke-тесты», «тест-кейсы из GDD», «шаблон баг-репорта».
  Triggers EN: "test plan", "what should we test", "test coverage", "smoke test list", "test cases from GDD", "bug report template".
  Не для запуска тестов (gd-build: qa-run), не для плейтеста с людьми (playtest).
- **Вход:** GDD систем слайса, `handoff/<slice>.md` (ED / DD).
- **Выход:** `qa/test-plan-<slice>.md` (таблица: `T-<sys>-NN` · покрывает `R3` / `E2` / `F1` / `ED2` · тип · предусловие · шаги · ожидаемое · автоматизируем да / нет), smoke-набор (≤ 10 пунктов, критический путь), шкала severity S1–S4.
- **Скрипт:** `scripts/check_coverage.py` — читает GDD (нумерованные Core Rules, строки Edge Cases, формулы) и план; FAIL: правило или edge case без теста, тест со ссылкой на несуществующий ID, ED без теста или ручной проверки. Требует стабильных ID в GDD (см. §5).
- **Done:** скрипт покрытия без FAIL; smoke-набор есть; каждый автоматизируемый тест помечен EditMode или PlayMode.
- **Агент:** `qa-lead` (ревьюер). Видит план + GDD слайса, ищет непокрытые состояния и переходы, негативные сценарии, «тесты, которые ничего не ловят». Пишет `reviews/YYYY-MM-DD-qa-<slice>.md`.
- **Источники:** CCGS `qa-plan` (классы Logic / Integration / Visual / UI), `smoke-check`, шаблон `test-plan`, `bug-report`. Адаптация, MIT.

#### 3.6 `playtest`
- **Description:**
  Плейтест с людьми: `plan` — протокол от гипотезы хендоффа (≤ 3 вопроса, порог решения заранее, задачи, скрипт наблюдения с кодами, think-aloud, что нельзя говорить игроку, опросник); `analyze` — сырые заметки → кодирование → частота × тяжесть → вердикт по гипотезе → адресаты находок. Пишет design/playtest/<date>-<slice>.plan.md и .report.md.
  Триггеры RU: «плейтест», «протокол плейтеста», «опросник для тестеров», «разбери заметки плейтеста», «что показал плейтест», «скрипт наблюдения».
  Triggers EN: "playtest plan", "playtest protocol", "playtest questionnaire", "analyze playtest notes", "playtest results".
  Не для разбора ощущения одной механики (game-feel), не для автотестов (qa-plan / gd-build: qa-run).
- **Алгоритм (plan):** гипотеза из handoff «если X, то игрок Y за Z» → вопросы исследования → **порог**: при каком наблюдении гипотеза подтверждена или опровергнута (записать до сессий) → участники (5 на раунд; для соло — 3, свои и чужие отдельно) → задачи без подсказок → скрипт наблюдения: таймкоды + коды `C` confusion · `F` frustration · `D` delight · `S` stuck (>30 с) · `Q` quit intent · `B` bug → опросник (3–5 шкал + 3 открытых вопроса, без наводящих) → логистика (запись экрана бесплатными средствами, согласие).
- **Алгоритм (analyze):** нормализовать заметки в формат `[mm:ss] CODE note` → агрегация скриптом → находки: частота (сколько игроков) × тяжесть (P0 блок гипотезы … P3 полировка) → вердикт `confirmed / refuted / inconclusive` строго по порогу из плана → каждой находке адресат: `game-feel` / `balance-check` / `gdd-author --quick` / `ux-onboarding` / `art-direction` / `audio-direction` / баг в `qa/bugs`.
- **Скрипт:** `scripts/aggregate_codes.py` — парсит заметки по сессиям, считает коды по игрокам и по сегментам таймлайна, находит «горячие минуты» (≥ 50 % игроков с C/F/S в одном окне).
- **Done (plan):** порог задан, опросник без наводящих вопросов. **Done (analyze):** вердикт, топ-находки с адресатами, строка-предложение для `decisions-log.md` (решает пользователь).
- **Агент:** `playtest-analyst`. Видит **только** сырые заметки, опросники и `.plan.md` (гипотеза и порог), **не** видит GDD и намерения дизайнера. Так не подгоняет наблюдения под замысел. Пишет `.report.md`.
- **Источники:** gstack-game `playtest` (`analysis-framework`, `metrics-and-benchmarks`); CCGS `playtest-report`. Адаптация, MIT. Коды наблюдения и скрипт — свои.
- **Изменение соседа:** из триггеров `game-feel` убрать «плейтест-разбор», добавить в `game-feel` «не для плейтеста с людьми (playtest)».

#### 3.7 `metrics-plan`
- **Description:**
  План метрик и телеметрии: гипотезы → события → воронки → KPI с целевым значением и порогом решения; taxonomy событий (`object_action`, параметры, когда стреляет), FTUE- и core-loop-воронки, retention-цели D1 / D7 / D30 как ГИПОТЕЗЫ, без персональных данных. Пишет design/analytics/events.md и funnels.md. Вендор-агностично.
  Триггеры RU: «метрики», «аналитика», «какие события слать», «воронка», «телеметрия», «ретеншн-цели», «KPI».
  Triggers EN: "analytics plan", "telemetry events", "event taxonomy", "funnel", "KPIs", "retention targets".
  Не для расчёта экономики и кривых (balance-check), не для телеметрии выборов внутри Ink (ink-slice), не для метрик Syncario (syncario-gamedesigner).
- **Вход:** `handoff/<slice>.md` (гипотеза), `ux/ftue.md` (шаги), `balance/*.md` (проекции D1 / D7 / D30), `playtest/*.plan.md`.
- **Выход:** `analytics/events.md` (event · params · trigger · гипотеза / KPI · owner), `analytics/funnels.md` (шаги → события → ожидаемая конверсия → порог тревоги).
- **Скрипт:** `scripts/check_events.py` — нейминг `snake_case` `object_action`, дубли, шаг воронки без события, KPI без события-источника, параметры с признаками PII (`email`, `name`, `phone`, `device_id` без хеша).
- **Done:** скрипт без ошибок; у каждой гипотезы слайса есть событие и порог.
- **Агент:** нет.
- **Источники:** gstack-game `playtest/metrics-and-benchmarks`; принципы Syncario (свои). Остальное с нуля.

### Плагин `gd-build` (только Claude Code)

Общее правило деградации для всех трёх скиллов: **preflight** в начале — есть ли Unity-проект (`ProjectSettings/ProjectVersion.txt`), подключён ли Unity MCP (проба `read_console` или `editor state`), какая версия Unity. Нет MCP → режим `plan`: полный план действий + чеклист для ручного выполнения, файлы C# можно писать на диск, но в отчёте пометка **«не проверено в редакторе»**. Никогда не утверждать «проверено», если проверки не было. Инструменты генерации Coplay (`generate_*`) не вызывать.

#### 3.8 `slice-build`
- **Description:**
  Сборка играбельного слайса в Unity 6 из design/handoff/<slice>.md через Unity MCP: разбиение Engineering Done на задачи, реализация плейсхолдерами, verify loop после каждой задачи (доказанная компиляция, консоль, тесты, play-mode smoke, скриншот), лог доказательств по каждому ED. Без MCP — план и чеклист. Пишет design/build/<slice>.log.md.
  Триггеры RU: «собери слайс», «собери прототип в Unity», «реализуй хендофф», «сделай играбельную версию», «билд из хендоффа».
  Triggers EN: "build the slice", "implement the handoff", "build the prototype in Unity", "make it playable".
  Не для плана прототипа и выбора слайса (gd-handoff), не для прогона тестов (qa-run), не для дизайн-решений.
- **Алгоритм:** preflight → прочитать handoff (MUST только), `tech/architecture.md`, `qa/test-plan` → задачи по `ED*` в порядке зависимостей → на задачу: тест-first для логики (EditMode из test-plan) → реализация → verify loop (`references/verify-loop.md`) → максимум **3 fix-цикла** на проблему, потом стоп и отчёт → плейсхолдеры из handoff (примитивы, CC0, `gen_sfx.py`) → в конце play-mode smoke + скриншот Game view → лог: `ED1 ✅ тест T-move-03 зелёный` / `ED4 ⛔ не выполнено: причина`.
- **Выход:** `build/<slice>.log.md` + код и сцены в Unity-проекте.
- **Скрипты:** `scripts/gen_sfx.py` (stdlib-синтез плейсхолдерных SFX, адаптация из unity-kit, MIT).
- **Done:** все MUST `ED*` с доказательством или явной пометкой; компиляция доказана (mtime DLL); консоль без ошибок; ≥ 1 скриншот.
- **Агент:** нет (ревью кода — существующие плагины `code-review`).
- **Источники:** unity-kit `unity-verify`, `unity-playtest`, `unity-init`. Адаптация, MIT.

#### 3.9 `qa-run`
- **Description:**
  Прогон проверок Unity-проекта: EditMode и PlayMode тесты (через Unity MCP или headless при закрытом редакторе), smoke-набор из тест-плана, проверка ввода через InputTestFixture, скриншоты, баг-репорты по шаблону. Прогон с нулём тестов = FAIL. Пишет design/qa/runs/<date>-<slice>.md и design/qa/bugs/BUG-NNN.md.
  Триггеры RU: «прогони тесты», «smoke-тест билда», «проверь билд», «запусти EditMode / PlayMode», «заведи баг».
  Triggers EN: "run the tests", "smoke test the build", "verify the build", "run PlayMode tests", "file a bug".
  Не для составления тест-плана (qa-plan), не для плейтеста с людьми (playtest).
- **Режимы:** `suite` · `smoke` · `input` · `bug`.
- **Скрипты:** `scripts/run-tests-headless.ps1` / `.sh` (адаптация unity-kit, MIT: exit 0 / 2 / 3, отказ при открытом редакторе, 0 тестов = 3); `scripts/parse_nunit.py` (NUnit XML → таблица в отчёте, сопоставление с ID `T-*` из test-plan).
- **Done:** отчёт с цифрами (`EditMode 12/12, PlayMode 4/5, smoke 8/8`), каждый упавший тест → баг или ссылка на существующий; пропущенные шаги названы явно.
- **Источники:** unity-kit `unity-ci`, `unity-verify`, `unity-playtest` (Tier 1); CCGS `smoke-check`, `bug-report`. Адаптация, MIT.

#### 3.10 `fmod-sync`
- **Description:**
  Перенос карты событий из design/audio/event-map.md в FMOD Studio и Unity: генерация JS-скрипта для консоли FMOD Studio (папки, события, параметры, шины, снапшоты), C#-класса констант путей событий, чеклиста интеграции FMOD for Unity (банки, listener, параметры из геймплея). Опционально — напрямую через бесплатный FMOD Studio MCP, если подключён. Сверка «карта ↔ проект».
  Триггеры RU: «перенеси события в FMOD», «создай события FMOD», «синхронизируй FMOD», «подключи FMOD к Unity», «константы событий FMOD».
  Triggers EN: "sync FMOD events", "create FMOD events", "FMOD Unity integration", "generate FMOD event constants".
  Не для решения, какие звуки нужны (audio-direction), не для настройки Unity AudioMixer (официальный Unity Plugin).
- **Скрипты:** `scripts/event_map_to_fmod.py` (event-map.md → `event-map.json` + `.js` для FMOD Studio Scripts + `FmodEvents.cs`); `scripts/diff_fmod.py` (сверка `event-map.json` с экспортом GUIDs FMOD Studio — `GUIDs.txt`, бесплатный стандартный экспорт).
- **Деградация:** нет FMOD Studio MCP → пользователь кладёт `.js` в папку `Scripts` проекта FMOD и запускает из меню (инструкция в отчёте). Нет FMOD for Unity в проекте → только чеклист установки.
- **Done:** diff без расхождений или расхождения перечислены; `FmodEvents.cs` компилируется (через verify loop, если есть MCP).
- **Источники:** свои. FMOD Studio Scripting API — документация FMOD (ссылка, без копирования).

## 4. Агенты (4 новых, все в `gd`, все ревьюеры)

Шаблон — как у `design-critic`: `omitClaudeMd: true`; tools `Read, Glob, Grep, Write`; видят только переданные пути и перечисленный контекст; прошлые ревью читают только после своей оценки; порядок отчёта из `principles.md` (вердикт → что работает → что ломается с альтернативой → что делать); художественный текст не пишут.

| Агент | Скилл | Видит | Не видит | Отчёт |
|---|---|---|---|---|
| `art-director` | art-direction | `art/*.md`, `pillars.md`, скриншоты по путям | историю чата, GDD целиком | `reviews/YYYY-MM-DD-art.md` |
| `audio-director` | audio-direction | `audio/*.md`, `pillars.md`, Feedback / Game Feel из GDD | историю, остальной GDD | `reviews/YYYY-MM-DD-audio.md` |
| `qa-lead` | qa-plan | `qa/test-plan-<slice>.md`, GDD слайса, handoff | код, историю | `reviews/YYYY-MM-DD-qa-<slice>.md` |
| `playtest-analyst` | playtest | сырые заметки, опросники, `.plan.md` | GDD, концепт, намерения автора | `playtest/<date>-<slice>.report.md` |

Агентов-исполнителей (tech-designer, builder) не добавляю: скиллы работают в основной сессии, изоляция им не нужна.

## 5. Изменения в существующем `gd`

| Файл | Изменение | Зачем |
|---|---|---|
| `gdd-author/references/gdd-template.md`, `templates/design/gdd/_template.md` | Стабильные ID: Core Rules `R1…`, Edge Cases `E1…`, Formulas `F1…`, Tuning Knobs `K1…`, Feedback `FB1…` | Трассировка в `qa-plan`, `tech-design`, `audio-direction`. Без ID скрипты работают по номеру строки — хрупко |
| `gd-handoff` + reference | ID `ED1…`, `DD1…`; секция «Ассеты слайса» ссылается на `art/asset-list.md`, «Звук» — на `audio/event-map.md` | Лог сборки и тест-план ссылаются на критерии |
| `game-feel` description | Убрать «плейтест-разбор», добавить «не для плейтеста с людьми (playtest)» | Конфликт триггеров |
| `gd-router` SKILL + `pipeline.md` | Стадии 8–12, треки, эвристики, возвраты; карта скиллов с пометкой `[gd-build]` | Маршрутизация |
| `principles.md` | Раздел «Инструменты: только бесплатные» + правило честной проверки («не проверено» ≠ «проверено») | Сквозное правило |
| `templates/design/` | Новые папки: `art/`, `audio/`, `ux/`, `tech/adr/`, `qa/runs/`, `qa/bugs/`, `playtest/`, `analytics/`, `build/` — файлы со `status: template` | Мост Cowork ↔ Code |
| `CLAUDE.md` | Уточнённое правило про Unity/FMOD (§1.3); `gd-build` в схеме; `examples/` | Правила репо |
| `.claude-plugin/marketplace.json` | Второй плагин `gd-build` | — |
| README, CHANGELOG, ATTRIBUTION | Таблицы команд, скиллов, агентов, схема пайплайна; unity-kit в ATTRIBUTION (MIT) | — |

### Новые команды (все `disable-model-invocation: true`)
`gd`: `/gd:art [bible|assets|check]`, `/gd:audio [bible|events|check]`, `/gd:ux [ftue|hud|a11y]`, `/gd:tech`, `/gd:qa-plan <slice>`, `/gd:playtest [plan|analyze] <slice>`, `/gd:metrics`.
`gd-build`: `/gd-build:slice <slice>`, `/gd-build:test [suite|smoke|input|bug]`, `/gd-build:fmod`.

## 6. Матрица пересечения триггеров

| Новый скилл | С чем может спутаться | Разводка |
|---|---|---|
| art-direction | game-feel («сочность» — визуальный juice) | Juice и отклик → game-feel; стиль, палитра, читаемость → art |
| audio-direction | game-feel (audio feedback); fmod-sync | «Какой звук и зачем» → audio; «создай в FMOD» → fmod-sync; ощущение → game-feel |
| ux-onboarding | game-feel (отзывчивость), официальный Unity `ui-*` | Что и когда показать → ux; как сверстать → Unity Plugin |
| tech-design | gd-systems-map (зависимости систем) | Дизайн-системы → systems-map; модули и данные кода → tech |
| qa-plan | gdd-review (дыры в правилах) | Ревью качества дизайна → gdd-review; проверяемость и покрытие → qa-plan |
| playtest | game-feel («плейтест-разбор», «прогони как игрок») | Триггер убирается из game-feel; игрок-персона на бумаге → game-feel, живые люди → playtest |
| metrics-plan | balance-check (D1/D7/D30), ink-slice (телеметрия выборов), syncario | Явные «не для» в описании |
| slice-build | gd-handoff («план прототипа», «вертикальный слайс») | «План и что строить» → handoff; «собери / реализуй» → slice-build |
| qa-run | unity-kit / Unity Plugin (если стоят) | У нас привязка к `design/qa`; при наличии unity-kit роутер предупреждает о дубле |
| fmod-sync | официальный `audio-setup-mixers` (Unity AudioMixer) | FMOD ≠ AudioMixer — явно в «не для» |

В фазе 3 проверка — скрипт, который прогоняет пары «типовой запрос → ожидаемый скилл» по описаниям (ручная табличная проверка + прогон в сессии).

## 7. Проверка в фазе 3

- `claude plugin validate .` без ошибок.
- `examples/one-tap-slice/` — мини-игра с заполненным `design/` по готовому хендоффу (концепт → GDD одной системы → handoff). На нём прогоняются 7 скиллов `gd` и все скрипты; результаты — в `examples/one-tap-slice/RESULTS.md`.
- `gd-build`: **на этой машине не найдено ни Unity Hub/Editor в стандартном пути, ни FMOD Studio.** Без них скиллы проверяются только в режиме деградации (план + чеклист, скрипты на синтетических NUnit XML и GUIDs.txt). Полный прогон с Unity MCP — после установки Unity 6 + CoplayDev MCP; в PR будет написано явно.
- Юнит-тесты для каждого Python-скрипта (stdlib `unittest`) на фикстурах в `examples/`.

## 8. Решения, нужные от пользователя

1. **Два плагина (`gd` + `gd-build`)** — да / всё в `gd`.
2. **Список из 10 скиллов** — одобрить / вырезать. Если резать, кандидаты на волну 2: `metrics-plan` и `fmod-sync` (в волне 1 хватит `event-map.md` + скрипта проверки).
3. **Стабильные ID в шаблоне GDD** (`R1`, `E1`, `K1`, `FB1`) — это меняет формат существующих GDD. Старые GDD скрипты будут читать по номеру строки с предупреждением.
4. **Unity на машине:** поставить Unity 6 + CoplayDev MCP для полного теста `gd-build` или принять тест в режиме деградации.
