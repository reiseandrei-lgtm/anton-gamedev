# Пайплайн: стадии, входы, выходы, критерии перехода

```
искра → концепт → системы → GDD → ревью → баланс → скоуп → хендофф
  → подготовка сборки → сборка [gd-build] → QA [gd-build] → плейтест → решение (↺ по адресатам)
  ─advance→ продакшн: хендофф майлстоуна → на систему feature-build → code-reviewer → qa-run [gd-build]
  → полировка и перф [gd-build] → релиз → после релиза (↺ метрики ниже порога → решение)
параллельно: нарратив · континуити · арт (→ модели, анимация, импорт [gd-build]) · звук (→ SFX, музыка, FMOD [gd-build])
  · UX (→ UI [gd-build]) · метрики · game feel (→ джус [gd-build]) · уровни
```

Все пути — относительно корня игрового репозитория. `design/` — общий мост между Claude Code и Cowork.

Статусы во frontmatter каждого документа: `template` (пусто) → `draft` → `review` → `approved`.

| # | Стадия | Скилл | Вход | Выход (файл) | Критерий перехода |
|---|---|---|---|---|---|
| 0 | Искра | `gd-concept` (режим spark) | Образ, фрагмент, ощущение, механика-обрывок | `concept.md` → раздел «Искра»: charged part + imprint | Есть одна фраза imprint и названа «заряженная» часть идеи |
| 1 | Концепт | `gd-concept` (режим concept) | Искра | `pillars.md`, `concept.md` | 3–5 фальсифицируемых столпов; fantasy как чувство; core loop в одну фразу «глагол → фидбек → награда → повтор»; twist в механике, не в сеттинге; Iceberg без WEAK или риск записан |
| 2 | Структура систем | `gd-systems-map` | `pillars.md`, `concept.md` (draft+) | `systems-map.md` | Каждая система: категория, приоритет (MVP / Vertical Slice / Alpha / Full), столп, зависимости; нет циклов; порядок проработки задан |
| 3 | GDD | `gdd-author` (`/gd:gdd`) | `systems-map.md` | `gdd/<system>.md` по файлу на систему; нарративные системы → также `narrative/` | Все MVP-системы в `draft`: заполнены Core Rules, States, Interactions, Formulas, Edge Cases, Tuning Knobs; нет «TBD» в Core Rules |
| 4 | Независимое ревью | агент `design-critic` + `gdd-review` (`/gd:review`) | `gdd/*.md` в `draft`/`review` | `reviews/YYYY-MM-DD-<doc>.md` | Вердикт не FAIL; нет открытых ESCALATE; принятые решения внесены в `decisions-log.md`; документ → `review`/`approved` |
| 5 | Баланс | `balance-check` (`/gd:balance`) | GDD систем с числами (прошли ревью) | `balance/<system>.md` | Таблица чисел для каждой числовой системы; faucet/sink 0.9–1.1 или отклонение обосновано; нет доминантной стратегии без решения; проекция D1/D7/D30 (где применимо) |
| 6 | Скоуп | `scope-check`, агент `producer` (`/gd:scope`) | Все MVP GDD + balance | `scope.md` | Конечный список контента (Lake, без «и т.д.»); оценка ≤ ресурсы команды с буфером 20%; cut-list и порядок вырезания |
| 7 | Хендофф | `gd-handoff` | `scope.md`, approved GDD | `handoff/<slice>.md` | Выбран слайс с гипотезой; критерии Engineering Done и Design Done со стабильными ID (`ED1…`, `DD1…`); список фейков/плейсхолдеров; для нарративного слайса — continuity-отчёт без FAIL и без C4 без решения |
| 8 | Подготовка сборки | `tech-design` (`/gd:tech`), `qa-plan` (`/gd:qa-plan`) | handoff, GDD слайса | `tech/architecture.md`, `tech/budgets.md`, `qa/test-plan-<slice>.md` | `check_knobs.py` без FAIL (каждый Tuning Knob слайса → поле конфига); `check_coverage.py` без FAIL (каждое R / F / E и ED → ≥ 1 тест); перф-бюджет для целевой платформы |
| 9 | Сборка слайса | `slice-build` (`/gd-build:slice`, плагин `gd-build`, только Claude Code) | 7 + 8 | `build/<slice>.log.md` + Unity-проект | Каждый MUST `ED*` — ✅ с доказательством или ⛔ с причиной; компиляция доказана; режим `live` (в режиме `plan` стадия только подготовлена, не закрыта) |
| 10 | QA | `qa-run` (`/gd-build:test`) | билд, test-plan | `qa/runs/YYYY-MM-DD-<slice>.md`, `qa/bugs/BUG-NNN.md` | Вердикт PASS: smoke пройден, 0 тестов ≠ зелёный, нет открытых S1 / S2 |
| 11 | Плейтест | `playtest` (`/gd:playtest plan` → сессии → `analyze` агентом `playtest-analyst`) | билд без S1 / S2, гипотеза хендоффа | `playtest/YYYY-MM-DD-<slice>.plan.md`, `.report.md` | Порог записан до сессий; вердикт `confirmed / refuted / inconclusive` по порогу; у каждой находки P0 / P1 есть адресат |
| 12 | Решение | `gd-router` | report плейтеста, `qa/runs`, `game-feel` (build), `release/postlaunch.md` | `decisions-log.md` | Записано одно из: `iterate` (→ адресаты находок) · `pivot` (→ 1) · `kill` (→ 7, другой слайс) · `advance` (следующий слайс / вертикаль / продакшн → 13), с причиной |
| 13 | Продакшн (цикл по системам майлстоуна) | `gd-handoff` (milestone) → на систему `feature-build` → агент `code-reviewer` → `qa-run` [gd-build]; параллельно `asset-integrate`, `juice-build`, `ui-build`, `fmod-sync` [gd-build], `level-design` | `advance` в `decisions-log.md`, `scope.md`, approved GDD | `handoff/<milestone>.md` (`type: milestone`), `build/<system>.log.md`, `reviews/*-code-<system>.md`, `qa/runs/*` | **Alpha**: у каждой системы майлстоуна каждое R / F / E в логе — ✅ или ⛔ с решением в `decisions-log.md` (`check_build_log.py` без FAIL); ревью кода не FAIL; qa PASS. **Beta**: + контент по `scope.md`, `check_import.py` без `ph_` у `mvp` |
| 14 | Полировка и перф | `perf-check`, `qa-run visual/soak`, `juice-build` [gd-build]; `ux-onboarding` (a11y), `audio-direction` (микс) | Beta | `qa/perf/<date>.md`, `qa/visual/` | Перф-бюджеты PASS на целевом устройстве после 10 мин; soak без роста памяти; визуальные отличия приняты 🟨 или исправлены; a11y без `gap`; микс принят 🟨; `check_coverage.py --stage polish` без FAIL |
| 15 | Релиз | `release-plan` (store, launch · `/gd:release-plan`), `build-release` [gd-build] | стадия 14 | `release/store.md`, `release/launch.md`, `release/builds.md`, RC-сборка | Чеклист launch закрыт; RC собран из тега; 0 открытых S1 / S2; тексты для игроков — от человека; **Release нажимает человек** |
| 16 | После релиза | `release-plan` (postlaunch · `/gd:release-plan postlaunch`), `feature-build` + `build-release` (патчи) | релиз | `release/postlaunch.md`, `qa/bugs/*` | Метрика из `analytics/funnels.md` ниже порога → стадия 12; S1 → hotfix: `feature-build` → `qa-run` → `build-release` |

Стадии 13–16 используют скиллы, которые выходят волнами: `feature-build`, `code-reviewer`, `juice-build`, `ui-build`, `asset-integrate` — `gd-build` 0.2; `perf-check`, `build-release`, `model-build`, `anim-build`, `sfx-design`, `music-build` — 0.3; `level-design`, `release-plan` (`gd`) и `loc-build` — позже. Если скилла нет в установленной версии, роутер называет шаг и даёт ручной чеклист, стадию не пропускает.

## Параллельные треки

Трекам арта и звука не нужен весь пайплайн: bible стартует от столпов. Перед стадией 9 для слайса с артом и звуком (а не только примитивами): asset-list с источником у каждого ассета (`check_assets.py` без FAIL) и event-map с покрытием Feedback (`check_event_map.py` без FAIL).


| Трек | Скилл | Когда | Файлы |
|---|---|---|---|
| Нарратив-структура | `narrative-structure` (`/gd:narrative`) | С концепта, если в столпах есть нарратив | `narrative/world.md`, `narrative/branches/*.md` |
| Голоса и персонажи | `character-voice` | После `world.md` | `narrative/voice-pillars.md`, `narrative/characters/*.md` |
| Ink-слайсы | `ink-slice` (`/gd:ink`) | После branches + voice для нужной сцены | `narrative/ink/<slice>.plan.md` (+ `.ink` в репо игры) |
| Континуити | `narrative-continuity` (`/gd:continuity`) | `register` — после первых branches; `check` — после каждого Ink-слайса и перед хендоффом; `impact` — при правке канона | `narrative/continuity/{promises,state,canon}.md`, `reviews/YYYY-MM-DD-continuity.md` |
| Game feel / playability | `game-feel` | На бумаге — после GDD системы; по билду — после стадии 10 | `reviews/YYYY-MM-DD-feel-<mechanic>.md` |
| Арт-дирекция | `art-direction` (`/gd:art`), агент `art-director` | `bible` — после `pillars.md` в `draft`+; `assets` — после GDD слайса | `art/art-bible.md`, `art/asset-list.md` |
| Звук | `audio-direction` (`/gd:audio`), агент `audio-director`; перенос — `fmod-sync` (`/gd-build:fmod`) | `bible` — после `pillars.md`; `events` — после GDD слайса | `audio/audio-bible.md`, `audio/event-map.md`, `audio/build/` |
| UX и онбординг | `ux-onboarding` (`/gd:ux`) | После GDD core loop; до хендоффа onboarding-слайса | `ux/ftue.md`, `ux/hud.md`, `ux/accessibility.md` |
| Метрики | `metrics-plan` (`/gd:metrics`) | После хендоффа (есть гипотеза) и `ux/ftue.md` | `analytics/events.md`, `analytics/funnels.md` |
| Уровни | `level-design` (`/gd:level`) | После GDD систем движения (knobs) и `ux/ftue.md`; для майлстоуна — до `feature-build` систем уровня | `levels/<level>.md` |
| Реализация отклика и UI | `[gd-build]` `juice-build`, `ui-build` | После GDD с целями Game Feel и `ux/hud.md`; стадии 9–14 | `build/<system>.log.md` (раздел Juice), `build/ui.log.md` |
| Импорт ассетов | `[gd-build]` `asset-integrate` | Когда у строк asset-list есть файлы | ассеты в Unity-проекте, отчёт `check_import.py` |
| Локализация | `[gd-build]` `loc-build` (`/gd-build:loc`) | После `ui-build` (ключи в UXML) и Ink-слайсов (`#id:`); до `store` в `release-plan`, если языков больше одного | `loc/<Table>.csv`, `build/loc.log.md` |
| Решения | любой скилл | При каждом принятом решении | `decisions-log.md` (дата, решение, почему, альтернативы) |

## Возвраты назад

- Ревью нашло противоречие со столпом → стадия 1 (пересмотреть столп) или 3 (править GDD). Решение — в `decisions-log.md`.
- Баланс требует новой системы (новый sink) → стадия 2 (обновить `systems-map.md`), затем 3.
- Скоуп FAIL → `producer` предлагает вырезание → обновить `systems-map.md` (приоритеты) и `scope.md`.
- Continuity FAIL → правка ветки (`/gd:narrative`) или слайса (`/gd:ink`), затем повторный `/gd:continuity check`.
- Плейтест `refuted` → решение в `decisions-log.md` → `iterate` или `pivot`.
- Находка плейтеста: о понимании → `ux-onboarding`; об ощущении → `game-feel`; о числах → `balance-check`; о правилах → `gdd-author --quick`; о читаемости → `art-direction`; о звуке → `audio-direction`.
- Баг оказался дырой дизайна (edge case не описан) → `gdd-author --quick` → `qa-plan` пересчитывает покрытие.
- `slice-build` уткнулся в неоднозначность хендоффа → стоп, вопрос в `handoff/<slice>.md` → Open Questions; решает дизайнер (`gd-handoff`).
- Сборка вышла за перф-бюджет → `tech-design` (ADR: что режем) или `scope-check`.
- Неоднозначность в GDD при реализации (`feature-build`) → `gdd-author --quick`; реализация не решает за дизайнера.
- `code-reviewer` вынес FAIL → `feature-build` той же системы.
- Тайминг отклика не совпал с целью → `juice-build` / `anim-build` (реализация) или `game-feel` (цель нереалистична).
- Элемент UI не помещается в зону → `ux-onboarding`.
- `check_loc.py` LC3 (строка не влезает) → `ux-onboarding` (лимит, зона) или автор текста (короче); LC5 (литерал вместо ключа) → `ui-build` / `ink-slice`.
- Модель сверх бюджета → `model-build` (LOD) или `tech-design` (бюджет, ADR).
- Звук «не тот» после прослушивания → `sfx-design` / `music-build` или `audio-direction`.
- `perf-check` FAIL → ADR в `tech-design`, `asset-integrate` (сжатие, атласы) или `scope-check`.
- Отличие на скриншоте (`qa-run visual`) → баг в `qa/bugs/` или новый эталон — решает человек.
- Метрики после релиза ниже порога → стадия 12.
- `check_release_plan.py` RP3 (текст для игроков не от человека) → вернуть автору, скилл текст не переписывает; go / no-go = no-go → адресат пункта (`qa-run`, `perf-check`, `asset-integrate`, `build-release`).
- `check_level.py` LV1 (зазор вне метрики) → `level-design` (правка уровня) или `gdd-author --quick` (метрика неверна); LV4 (нет системы или врага) → `gd-systems-map` / `gdd-author`.

## Эвристики определения стадии

- Нет `pillars.md` или он `template`, но есть GDD → стадия 1 (пропуск фундамента, вернуть).
- В `reviews/` нет файла новее последнего изменения GDD → стадия 4 для этого GDD.
- Есть `narrative/ink/*.plan.md`, но нет `narrative/continuity/promises.md` → предложить `/gd:continuity register` параллельно.
- Для малых правок существующей системы — не гнать весь пайплайн: `gdd-author` в лёгком режиме, затем `/gd:review`.
- `handoff/*.md` в `review`+, но нет `qa/test-plan-<slice>.md` или `tech/architecture.md` в `template` → стадия 8.
- Есть 8, нет `build/<slice>.log.md` → стадия 9 (`/gd-build:slice`; в Cowork — сказать, что шаг делается в Claude Code с `gd-build`, и дать чеклист).
- `build/<slice>.log.md` новее последнего `qa/runs/*-<slice>.md` → стадия 10.
- Последний `qa/runs` PASS, нет `playtest/*-<slice>.plan.md` → стадия 11 (`plan`); plan есть, report нет → стадия 11 (`analyze`, после сессий).
- Есть `playtest/*.report.md` без строки в `decisions-log.md` новее отчёта → стадия 12.
- `pillars.md` в `review`+, а `art/art-bible.md` и `audio/audio-bible.md` в `template` → предложить треки параллельно (блокер только перед стадией 9, если в слайсе есть арт или звук).
- Нет ID в GDD (`R1`, `K1`, `FB1`) на стадии 8 → сначала `gdd-author` для простановки ID.
- Последнее решение в `decisions-log.md` — `advance`, нет `handoff/*.md` с `type: milestone` → стадия 13, `gd-handoff` (milestone).
- Есть milestone-хендофф, у системы из него нет `build/<system>.log.md` → стадия 13, `/gd-build:feature <system>`.
- В milestone-хендоффе или `scope.md` есть уровни или арены, а `levels/<level>.md` нет → `/gd:level <level>` до `feature-build` их систем.
- `build/<system>.log.md` новее последнего `reviews/*-code-<system>.md` → `/gd-build:review <system>` (агент `code-reviewer`).
- Ревью кода не FAIL, последний `qa/runs/*` старше лога системы → `/gd-build:test`.
- Все системы майлстоуна закрыты, нет `qa/perf/*` новее последнего лога → стадия 14.
- Стадия 14 закрыта, нет `release/launch.md` → стадия 15 (`/gd:release-plan launch`; страницу магазина — `store` — можно раньше, с вертикального слайса); есть `release/postlaunch.md` с метрикой ниже порога без решения → стадия 12.

## Шаги человека (🟨)

Скиллы их не делают и не пропускают: решения о столпах, вырезании, pivot / kill · логины и лицензии (Unity Hub, fmod.com, Steamworks, секреты CI) · пустой проект FMOD Studio · референсы · прослушивание и микс на устройстве · ощущение управления · живые плейтесты · hero-ассеты (главный персонаж, ключевой арт, главная тема) · утверждение статуса `made` и визуальных эталонов · тексты для игроков (магазин, трейлер, посты) · финальный Release.
