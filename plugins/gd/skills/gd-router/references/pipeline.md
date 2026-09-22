# Пайплайн: стадии, входы, выходы, критерии перехода

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
| 7 | Хендофф | `gd-handoff` | `scope.md`, approved GDD | `handoff/<slice>.md` | Выбран слайс с гипотезой; критерии Engineering Done и Design Done; список фейков/плейсхолдеров; для нарративного слайса — continuity-отчёт без FAIL и без C4 без решения. Дальше — реализация (Unity-плагин, вне этого пайплайна) |

## Параллельные треки

| Трек | Скилл | Когда | Файлы |
|---|---|---|---|
| Нарратив-структура | `narrative-structure` (`/gd:narrative`) | С концепта, если в столпах есть нарратив | `narrative/world.md`, `narrative/branches/*.md` |
| Голоса и персонажи | `character-voice` | После `world.md` | `narrative/voice-pillars.md`, `narrative/characters/*.md` |
| Ink-слайсы | `ink-slice` (`/gd:ink`) | После branches + voice для нужной сцены | `narrative/ink/<slice>.plan.md` (+ `.ink` в репо игры) |
| Континуити | `narrative-continuity` (`/gd:continuity`) | `register` — после первых branches; `check` — после каждого Ink-слайса и перед хендоффом; `impact` — при правке канона | `narrative/continuity/{promises,state,canon}.md`, `reviews/YYYY-MM-DD-continuity.md` |
| Game feel / playability | `game-feel` | На бумаге — после GDD системы; по билду — после прототипа | `reviews/YYYY-MM-DD-feel-<mechanic>.md` |
| Решения | любой скилл | При каждом принятом решении | `decisions-log.md` (дата, решение, почему, альтернативы) |

## Возвраты назад

- Ревью нашло противоречие со столпом → стадия 1 (пересмотреть столп) или 3 (править GDD). Решение — в `decisions-log.md`.
- Баланс требует новой системы (новый sink) → стадия 2 (обновить `systems-map.md`), затем 3.
- Скоуп FAIL → `producer` предлагает вырезание → обновить `systems-map.md` (приоритеты) и `scope.md`.
- Continuity FAIL → правка ветки (`/gd:narrative`) или слайса (`/gd:ink`), затем повторный `/gd:continuity check`.

## Эвристики определения стадии

- Нет `pillars.md` или он `template`, но есть GDD → стадия 1 (пропуск фундамента, вернуть).
- В `reviews/` нет файла новее последнего изменения GDD → стадия 4 для этого GDD.
- Есть `narrative/ink/*.plan.md`, но нет `narrative/continuity/promises.md` → предложить `/gd:continuity register` параллельно.
- Для малых правок существующей системы — не гнать весь пайплайн: `gdd-author` в лёгком режиме, затем `/gd:review`.
