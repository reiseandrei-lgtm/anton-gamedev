---
status: draft   # template | draft | review | approved
updated: 2026-09-24
owner: Anton
---

# Фаза 2. Архитектура продакшн-цикла: из слайса в игру и релиз (предложение, не реализация)

Вход: `research/2026-09-full-cycle-architecture.md` (стадии 0–12), живой прогон `gd-build` 2026-09-24 (`examples/one-tap-slice/RESULTS.md`), пайплайн MEATFORM (`meatform/design/production-pipeline.md`, Ф0–Ф8). Ограничения пользователя: только бесплатные инструменты; `gd` — документы и соглашения, `gd-build` — всё, что трогает Unity, Blender, FMOD и файлы ассетов; честная маркировка «не проверено».

## 0. Что изменил живой прогон (факты, которые определяют архитектуру)

| Факт (2026-09-24) | Следствие для архитектуры |
|---|---|
| MCP-сервер, добавленный посреди сессии, недоступен как инструменты до новой сессии; CLI `unity-mcp raw <tool>` того же сервера работает | Все build-скиллы описывают действия абстрактно (`mcp-actions.md`) и допускают два канала: инструменты MCP или CLI. Режим `plan` — только когда нет ни того, ни другого |
| `manage_ui` в CoplayDev 10.2 работает только с UI Toolkit (UXML/USS) и умеет `render_ui` в PNG | Аргумент за UI Toolkit (решение b) |
| `manage_profiler`: frame timing, счётчики, снимки памяти (нужен `com.unity.memoryprofiler`), Frame Debugger; группа `profiling` | `perf-check` и `qa-run soak` строятся на нём; без MCP — Profiler вручную + `FrameTimingManager` в коде |
| `manage_build`: сборка игрока, платформы, Build Profiles (Unity 6) | `build-release` без своего C#-билд-скрипта; headless — `-executeMethod` как запасной путь |
| `import_model_file` лежит в группе `asset_gen` (там же платные `generate_*`) | `asset-integrate` / `model-build` импортируют копированием GLB в `Assets/` + refresh; группу `asset_gen` не включаем. Запасной путь — `batch_execute` по имени команды (по исходникам, не проверено) |
| `fmodstudiocl -script`/`-build`/`-diagnostic` работает без GUI; новый проект CLI не создаёт | Все FMOD-шаги — headless; создание пустого проекта FMOD — 🟨 шаг человека |
| В FMOD 2.03 параметр = `ParameterPreset`; событие без банка не собирается | Формат `event-map.md` расширяется колонкой `Bank` (общий формат, см. §4) |
| Ложный зелёный в `run-tests-headless.ps1` жил две версии | Каждый новый скрипт получает негативную фикстуру «должен упасть» + живую фикстуру, как `fixtures/live/` |
| Blender 5.2.1 LTS есть (Steam), ffmpeg / sox / FluidSynth / SoundFont нет | Волна B проверяется вживую только после установки (§8, решение пользователя); до этого — режим `plan` и «не проверено» |

## 1. Плагины: состав после расширения

**Решение (предложение): остаются два плагина.** `gd` +2 скилла (21 → 23), `gd-build` +10 скиллов и 1 агент (3 → 13; +1 при `netcode-build`).

| Плагин | Сейчас | Волна A | Волна B | Волна C |
|---|---|---|---|---|
| `gd` | 21 скилл, 7 агентов | доработки `gd-router`, `gd-handoff`, `qa-plan` | доработка агента `art-director` | 🆕 `level-design`, 🆕 `release-plan` |
| `gd-build` | 3 скилла | 🆕 `feature-build`, 🆕 `juice-build`, 🆕 `ui-build`, 🆕 `asset-integrate`; доработки `qa-run`, `fmod-sync`; 🆕 агент `code-reviewer` | 🆕 `anim-build`, 🆕 `model-build`, 🆕 `sfx-design`, 🆕 `music-build`, 🆕 `perf-check`, 🆕 `build-release`; доработка `preflight.py` | 🆕 `loc-build`, 🆕 `analytics-build`, (🆕 `netcode-build` — только по решению f) |

Почему не третий плагин (`gd-assets` для model/anim/sfx/music): у всех build-скиллов общий preflight, общий verify loop и общие парсеры форматов `design/`; в разных плагинах их пришлось бы копировать и держать синхронными. Цена — 13 описаний в контексте сессии Claude Code (≈ 3–4 тыс. токенов). Если после волны B это станет заметно, вынос `sfx-design`, `music-build`, `model-build`, `anim-build` в `gd-assets` — отдельное решение (§7, a).

Общие правила для новых build-скиллов (как у `slice-build`):
- **Preflight** первым шагом: проект, инструмент, канал MCP (инструменты / CLI / нет). Нет инструмента → режим `plan`: план, чеклист, файлы на диск допустимы, всё помечается «не проверено».
- **Verify loop** из `slice-build/references/verify-loop.md` после каждой правки; максимум 3 fix-цикла на проблему.
- **Лог с доказательствами**: ✅ только с тестом / скриншотом / выводом скрипта / замером; ⚠️ сделано, не проверено; ⛔ не сделано + причина. В режиме `plan` ✅ нет.
- **Запрещено вызывать**: Coplay `generate_*` и группу `asset_gen` для генерации; Blender MCP `create_rodin_job` (Hyper3D), `create_hunyuan_job`, `download_sketchfab_model` (ключ API, лицензии моделей разные); Unity AI и официальный Unity MCP; Suno, ElevenLabs, Meshy, MusicGen (веса некоммерческие); Stable Audio Open — до решения пользователя и проверки лицензии; платные облака тестов.
- **Телеметрия инструментов выключена**: `DISABLE_TELEMETRY=true` для unity-mcp (сервер и редактор) и mcp-for-blender (у него без согласия уходит минимальная анонимная запись: install id, имя инструмента, время — см. его `TERMS_AND_CONDITIONS.md`).
- Скрипты `gd-build` самодостаточны: общий код `gd` копируется в `plugins/gd-build/skills/slice-build/scripts/` (например, `gdd_ids.py`), `tools/check_plugins.py` сверяет копию с оригиналом побайтно (новая проверка «drift»).

## 2. Пайплайн: стадии 13–16

Стадии 0–12 без изменений. Решение `advance` на стадии 12 ведёт не только к следующему слайсу, но и в продакшн.

```
… → 12 решение ─advance→ 13 продакшн (цикл по системам майлстоуна: хендофф Alpha/Beta → feature-build → code-reviewer → qa-run
                                         ∥ asset-integrate · juice-build · ui-build · anim/model/sfx/music)
                        → 14 полировка и перф → 15 релиз → 16 после релиза ─метрики ниже порога→ 12
```

| # | Стадия | Скиллы | Вход | Выход (`design/` и Unity-проект) | Критерий перехода |
|---|---|---|---|---|---|
| 13 | Продакшн (цикл по системам майлстоуна) | `gd-handoff milestone` → на систему: `feature-build` → агент `code-reviewer` → `qa-run suite/smoke`; параллельно `asset-integrate`, `juice-build`, `ui-build`, `anim-build`, `model-build`, `sfx-design`, `music-build`, `fmod-sync`, `level-design` | `decisions-log.md` с `advance`; `scope.md` (Lake); approved GDD систем майлстоуна | `handoff/<milestone>.md` (`type: milestone`), `build/<system>.log.md`, `reviews/<date>-code-<system>.md`, `qa/runs/*`, код и ассеты | **Alpha**: у каждой системы майлстоуна лог, где каждое R / F / E — ✅ или ⛔ с решением в `decisions-log.md`; последнее ревью кода не FAIL; qa PASS; плейсхолдеры допустимы. **Beta**: всё то же + контент по `scope.md` на месте, `check_import.py` без `ph_` в ассетах `mvp`, `check_audio_files.py` без `ph_` в финальных событиях |
| 14 | Полировка и перф | `perf-check`, `qa-run visual/soak`, `juice-build` (сверка таймингов), `loc-build`, `ux-onboarding a11y`, `audio-direction` (микс) | Beta | `qa/perf/<date>.md`, `qa/visual/`, отчёты | `perf-check` PASS на min-spec после 10 мин игры; soak без роста памяти выше порога; визуальные отличия приняты или исправлены (решает 🟨); a11y без `gap`; микс принят 🟨; локализация (если выбрана) без пропусков |
| 15 | Релиз | `release-plan store/launch`, `build-release` | стадия 14 закрыта | `release/store.md`, `release/launch.md`, `release/builds.md`, сборка RC, CI-workflow | Чеклист `launch` без открытых пунктов; RC собран из тега; 0 открытых S1/S2; страница магазина и тексты — от человека; **Release нажимает 🟨** |
| 16 | После релиза | `release-plan postlaunch`, `analytics-build` (данные), `feature-build` (патчи), `build-release` (hotfix / day-one) | релиз | `release/postlaunch.md`, `qa/bugs/*`, патчи | Метрики из `analytics/funnels.md` ниже порога → стадия 12 (решение); S1 после релиза → hotfix-путь (`feature-build` → `qa-run` → `build-release`) |

### Эвристики роутера (добавить в `pipeline.md`)
- Последняя строка `decisions-log.md` — `advance`, нет `handoff/*.md` с `type: milestone` → стадия 13, `gd-handoff milestone`.
- Есть milestone-хендофф, у системы из него нет `build/<system>.log.md` → стадия 13, `feature-build <system>`.
- `build/<system>.log.md` новее последнего `reviews/*-code-<system>.md` → агент `code-reviewer`.
- Ревью кода не FAIL, `qa/runs/*` старше лога системы → `qa-run`.
- Все системы майлстоуна закрыты, нет `qa/perf/*` новее последнего лога → стадия 14, `perf-check`.
- Стадия 14 закрыта, нет `release/launch.md` → стадия 15, `release-plan launch`.
- Есть `release/postlaunch.md`, в нём метрика ниже порога без строки в `decisions-log.md` → стадия 12.
- В Cowork шаги `gd-build` отдаются чеклистом (как сейчас).

### Новые возвраты назад (в `pipeline.md`)
| Ситуация | Куда |
|---|---|
| Неоднозначность в GDD при реализации | → `gdd-author --quick` (вопрос в Open Questions; `feature-build` не решает за дизайнера) |
| `code-reviewer` вынес FAIL | → `feature-build` (та же система) |
| Тайминг не совпал с целью | → `juice-build` / `anim-build` (реализация) или `game-feel` (цель нереалистична) |
| Элемент UI не помещается в зону | → `ux-onboarding` |
| Модель сверх бюджета | → `model-build` (LOD) или `tech-design` (пересмотр бюджета, ADR) |
| Звук «не тот» после прослушивания | → `sfx-design` / `music-build` или `audio-direction` |
| `perf-check` FAIL | → ADR в `tech-design`, `asset-integrate` (сжатие, атласы, LOD) или `scope-check` |
| Отличие на скриншоте | → баг (`qa/bugs`) или новый эталон (решает 🟨) |
| Метрики после релиза ниже порога | → стадия 12 |
| Уровень недостижим по метрикам персонажа (`check_level.py`) | → `level-design` или `gdd-author --quick` (knob) |
| Строка не влезает в лимит локали (`check_loc.py`) | → `ux-onboarding` (лимит) или правка ключа автором текста 🟨 |

### Шаги, которые остаются за человеком (🟨, вписать в README и `pipeline.md`)
Решения о столпах, вырезании, pivot / kill; логины и лицензии (Unity Hub, fmod.com, Steamworks, GitHub-секреты для CI); создание пустого проекта FMOD; референсы; прослушивание и микс на устройстве; ощущение управления; живые плейтесты; hero-ассеты (главный персонаж, ключевой арт, главная тема); утверждение статуса `made` и визуальных эталонов; тексты для магазина, трейлера и соцсетей (агент их не пишет); финальный Release.

## 3. Скиллы и доработки

Формат карточки: **вход → выход** · алгоритм · проверка (скрипт, коды) · Done · «не для» · источник (лицензия). Коды правил новых скриптов — двухбуквенные, чтобы не пересечься с существующими (`A`, `C`, `D`, `E`, `M`, `Q`, `T`).

### Волна A (P0): из слайса в игру

#### A1. `gd-router` + `pipeline.md` (доработка, `gd`)
Стадии 13–16, эвристики и возвраты из §2, 🟨-шаги, карта скиллов с пометкой `[gd-build]`. Router-скрипт не нужен: стадия определяется по файлам.

#### A2. `gd-handoff` — режим `milestone` (доработка, `gd`)
- **Вход → выход**: `scope.md`, approved GDD, `decisions-log.md` (`advance`) → `handoff/<milestone>.md` c `type: milestone`, `milestone: alpha | beta`.
- **Алгоритм**: системы майлстоуна из `systems-map.md` (приоритет ≤ майлстоуна) → на систему блок ED/DD с ID `ED-<system>-N`, `DD-<system>-N` → контент из `scope.md` (конечный список) → критерии выхода Alpha/Beta из §2 → порядок систем по зависимостям.
- **Проверка**: `check_coverage.py` уже читает ED; расширить `gdd_ids.py` форматом `ED-<system>-N`.
- **Done**: каждая система майлстоуна есть в хендоффе; у каждой ≥1 ED; контент без «и т.д.».
- **Источник**: свой; идея «гейт майлстоуна» — CCGS `gate-check` (MIT, уже в ATTRIBUTION).

#### A3. `qa-plan` — типы `visual` и `perf` (доработка, `gd`)
- `visual`: кейс, который можно снять скриншотом (Feedback с Visual, состояния HUD, экраны меню): сцена, камера, seed, разрешение, допуск. Эталон — `qa/visual/<case>.png`, утверждает 🟨.
- `perf`: строка `tech/budgets.md` → метод замера (`manage_profiler` / FrameTimingManager), длительность, сцена, платформа.
- **`check_coverage.py`**: Q9 — Visual-строка Feedback или состояние HUD покрыто только `manual` (FAIL: визуал, который можно снять скриншотом, не уходит в `manual`; исключение — пометка `manual: reason`); Q10 — строка бюджета без `perf`-кейса (WARN на стадии 8, FAIL на стадии 14 по флагу `--stage polish`).

#### A4. `qa-run` — режимы `visual` и `soak` (доработка, `gd-build`)
- **visual**: для каждого `visual`-кейса — фиксированные разрешение (Game view по цели), seed, камера → скриншот через MCP → `scripts/diff_png.py <baseline> <shot> --tolerance --mask` → отчёт. Нет эталона → снимок кладётся в `qa/visual/_pending/`, эталоном его делает 🟨 (перенос файла + строка в `qa/visual/README.md`).
- **`diff_png.py`** (stdlib: `zlib`, `struct`; декодер PNG с фильтрами 0–4, RGB/RGBA 8 бит): VD1 размер не совпал · VD2 доля отличающихся пикселей > допуска · VD3 максимальное отклонение канала > порога · VD4 эталон отсутствует. Пишет diff-PNG (красным отличия).
- **soak**: N минут play mode со скриптом ввода (или простоем) → каждые 30 с `get_frame_timing` + память → `qa/perf/<date>-soak.md`; `compare_perf.py` (см. B5) даёт SK1 наклон памяти > порога · SK2 рост времени кадра · SK3 исключения в консоли.
- **Done**: отчёт с числами; ни одного «похоже» без diff.

#### A5. 🆕 `feature-build` (`gd-build`)
- **Description (черновик)**: Реализация одной системы из GDD в Unity-проекте игры: тест первым по тест-плану, verify loop, каждое правило, формула и edge case (R / F / E) в логе с доказательством. Пишет design/build/<system>.log.md. Триггеры RU: «реализуй систему», «сделай фичу из GDD», «имплементируй механику», «собери систему в Unity». Triggers EN: "implement the system", "build the feature from the GDD", "implement this mechanic in Unity". Не для первого слайса из хендоффа (slice-build), не для отклика и эффектов (juice-build), не для UI (ui-build).
- **Вход → выход**: `gdd/<system>.md` (с ID), `handoff/<milestone>.md` (ED системы), `tech/architecture.md` (модуль, Config map, seams), `qa/test-plan-*.md` → код + тесты в Unity-проекте, `build/<system>.log.md`.
- **Алгоритм**: preflight → задачи по R/F/E в порядке зависимостей → тест первым (красный прогон записывается) → реализация → verify loop → knobs только из конфигов (Config map) → лог по каждому ID → в конце `code-reviewer` (агент) и `qa-run suite`.
- **Проверка**: `scripts/check_build_log.py design/build/<system>.log.md --gdd design/gdd/<system>.md --plan design/qa/test-plan-*.md`: BL1 ID из GDD нет в логе · BL2 ✅ без доказательства · BL3 доказательство ссылается на T-ID, которого нет в плане · BL4 `mode: plan` и есть ✅ · BL5 ⛔ без причины · BL6 лог старше последнего изменения GDD (WARN). Этот же скрипт проверяет лог `slice-build` (формат общий).
- **Done**: скрипт без FAIL; компиляция доказана; консоль чистая; ревью кода не FAIL.
- **Источник**: свой (обобщение `slice-build`); verify loop — unity-kit (MIT, в ATTRIBUTION).

#### A6. 🆕 агент `code-reviewer` (`gd-build`)
- Видит **только**: файл diff (путь; `git diff <base>..HEAD -- <paths> > design/build/<system>.diff`), `gdd/<system>.md`, `tech/architecture.md`, `qa/test-plan-*.md`. Не видит историю и лог сборки (чтобы не верить «✅» на слово). `omitClaudeMd: true`, tools `Read, Glob, Grep, Write`.
- **Проходы** (по gstack-game `gameplay-implementation-review`, MIT): 0 — сохранилось ли намерение дизайна (каждое R/E ↔ место в коде; «душа» из Game Feel защищена тестом или конфигом); 1 — критичное (литералы-knobs вместо Config map, аллокации в `Update`, несериализуемое состояние сохранений, ввод вне Input System, связь модулей против `architecture.md`); 2 — информационное.
- **Выход**: `reviews/<date>-code-<system>.md`, вердикт `PASS / CONCERNS / FAIL`, каждая находка: файл:строка → почему → альтернатива. FAIL → `feature-build`.
- **Источник**: gstack-game `gameplay-implementation-review` (Pass 0 «Design Intent Survival», Pass 1/2) — адаптация без bash-преамбулы и телеметрии; CCGS `code-review` (MIT) — фазы ADR-compliance.

#### A7. 🆕 `juice-build` (`gd-build`)
- **Description**: Отклик на события в Unity: частицы, шейдерные вспышки, тряска и толчок камеры, hitstop, squash/stretch, вибрация геймпада; замер таймингов в кадрах против целей Game Feel из GDD. Триггеры RU: «добавь джус», «сделай отклик на удар», «хитстоп», «тряска камеры», «частицы на событие», «сверь тайминги отклика». EN: "add juice to", "implement hitstop", "screen shake", "impact particles", "measure feedback timings". Не для оценки ощущения (gd:game-feel), не для анимации персонажа (anim-build), не для UI (ui-build).
- **Вход → выход**: Feedback (`FB*`) и Game Feel GDD, `art/art-bible.md` (цвета ролей), `audio/event-map.md` (звук в том же кадре) → компоненты отклика, `build/<system>.log.md` раздел Juice (таблица событие → кадр начала, длительность в кадрах, цель, замер).
- **Замер**: PlayMode-тест фиксирует `Time.frameCount` события и первого кадра отклика (частица активна, камера сдвинута, `timeScale` hitstop) при фиксированном `captureFramerate`.
- **Проверка**: `scripts/check_juice.py design/build/<system>.log.md --gdd …`: JU1 FB с визуальным откликом без замера · JU2 замер вне допуска цели · JU3 цель в GDD без числа (WARN → `game-feel`) · JU4 отклик есть, звука в том же кадре нет при наличии события в карте.
- **Источник**: свой; модель anticipation/impact — `game-feel` (адаптация gstack-game, в ATTRIBUTION); awesome-gamedev-agent-skills `game-feel` (Apache-2.0) — чеклист техник.

#### A8. 🆕 `ui-build` (`gd-build`)
- **Description**: HUD, меню, пауза и настройки в Unity по design/ux/hud.md: вёрстка, стили только из ролей палитры, строки только ключами локализации, скриншоты в 2–3 разрешениях. Триггеры RU: «сверстай HUD», «сделай меню», «экран паузы», «экран настроек», «реализуй интерфейс». EN: "build the HUD", "implement the menu", "pause screen", "settings screen". Не для решения, что показывать (gd:ux-onboarding), не для перевода строк (loc-build), не для эффектов (juice-build).
- **Вход → выход**: `ux/hud.md`, `ux/accessibility.md`, `art/art-bible.md` → UXML/USS (или uGUI — решение b), `build/ui.log.md`, скриншоты `build/ui/screenshots/<res>/`.
- **Проверка**: `scripts/check_ui.py design/ux/hud.md <Assets/…/UI> --palette design/art/art-bible.md`: UI1 элемент `hud.md` без реализации (по `name`) · UI2 цвет в USS не из переменных ролей (`var(--role-…)`; hex допустим только в файле темы, и он должен совпасть с bible) · UI3 литеральный текст в UXML или C# вместо ключа · UI4 нет скриншота для разрешения из списка · UI5 размер тач-цели меньше минимума bible (по USS, для мобайла).
- **Источник**: свой; CCGS `ui-programmer`, `unity-ui-specialist` (MIT) — идеи; Nice-Wolf `unity-ui-patterns` (MIT) — паттерны. How-to API — официальный Unity Plugin (не копируем).

#### A9. 🆕 `asset-integrate` (`gd-build`)
- **Description**: Импорт ассетов в Unity по design/art/asset-list.md и design/audio/files.md: настройки импорта, атласы, материалы URP, замена плейсхолдеров, проверка ID, бюджетов и лицензий скриптом. Триггеры RU: «импортируй ассеты», «замени плейсхолдеры», «настрой импорт текстур», «собери атлас», «подключи модели в Unity». EN: "import the assets", "replace placeholders", "texture import settings", "build the sprite atlas". Не для списка ассетов и стиля (gd:art-direction), не для создания моделей (model-build), не для звука в FMOD (fmod-sync).
- **Проверка**: `scripts/check_import.py <Assets/_Project> --assets design/art/asset-list.md [--audio design/audio/files.md] [--budgets design/tech/budgets.md]`: IM1 файл без строки в asset-list (сирота) · IM2 строка slice/mvp без файла · IM3 `ph_` у ассета со статусом `made` · IM4 текстура больше бюджета (размер из заголовка PNG, stdlib) · IM5 модель сверх бюджета треугольников (через `check_glb`) · IM6 `cc0` без URL лицензии · IM7 имя файла ≠ ID.
- **Источник**: свой; blender-skills `asset-optimization` (MIT) — чеклист.

#### A10. `fmod-sync` — импорт файлов и режим `hook` (доработка, `gd-build`)
- **Колонка `Bank`** в `event-map.md` (общий формат с `audio-direction`, см. §4): по умолчанию `Master`; скрипт создаёт банк и назначает события.
- **Импорт**: `audio/files.md` → `studio.project.importAudioFile(path)` → инструмент на таймлайне события (single / multi для вариаций). Вызовы `Event.addGroupTrack`, `GroupTrack.addSound` — сверить по локальной документации 2.03.14 и прогнать `fmodstudiocl` до пометки «проверено».
- **hook**: `scripts/check_fmod_calls.py <Assets> --map design/audio/build/event-map.json`: FH1 строковый путь `"event:/…"` вне `FmodEvents.cs` · FH2 событие карты ни разу не вызывается через `FmodEvents.*` (WARN) · FH3 `FmodEvents.cs` расходится с картой (перегенерировать) · FH4 `CreateInstance` без `release()` в том же классе (WARN, эвристика).
- Вызовы FMOD for Unity (`RuntimeManager.*`) сверить по документации FMOD for Unity; живой прогон — после установки пакета 🟨.

### Волна B (P1): контент и выпуск

#### B1. 🆕 `anim-build` (`gd-build`)
- **Description**: Анимация в Unity: процедурная (пружины, IK через Animation Rigging, физические сочленения — основной путь для MEATFORM) или риг и ключи в Blender с экспортом в GLB; длительности фаз в кадрах сверяются с целями Game Feel. Триггеры RU: «анимируй», «процедурная анимация», «походка», «IK», «риг в Blender», «анимационный клип». EN: "animate the", "procedural animation", "procedural walk", "set up IK", "rig in Blender". Не для отклика на события (juice-build), не для моделирования (model-build).
- **Вход → выход**: `art/asset-list.md` (тип `anim`: клипы, фазы, кадры), Game Feel GDD → компоненты (`com.unity.animation.rigging` 1.4.1 в поставке Unity 6000.3) или GLB с клипами; лог.
- **Проверка**: `scripts/check_glb.py <file.glb> --asset-list …` (общий с B2): GL5 клип из asset-list отсутствует · GL6 длительность клипа (max input sampler / fps) вне допуска; для процедурной — PlayMode-замер «пружина успокаивается за ≤ N кадров», таблица в логе, `check_juice.py`-правила JU1/JU2.
- **Источник**: blender-skills `rigging`, `animation` (MIT); Nice-Wolf `unity-animation` (MIT); tjboudreaux `tools-unity-animation` (MIT).

#### B2. 🆕 `model-build` (`gd-build`)
- **Description**: 3D-модели в Blender через бесплатный Blender MCP: блокаут → модель → UV → материалы по ролям палитры → LOD → экспорт в GLB, турнтейбл для ревью; бюджеты и имена проверяются скриптом. Триггеры RU: «смоделируй», «сделай модель», «блокаут в Blender», «LOD», «экспортируй в GLB». EN: "model the", "make a 3D model", "Blender blockout", "generate LODs", "export to GLB". Не для визуального стиля и списка ассетов (gd:art-direction), не для импорта в Unity (asset-integrate), не для генерации моделей ИИ.
- **Вход → выход**: строка asset-list (ID, размер, бюджет, роль цвета), `art-bible.md` → `.blend` в `art-source/`, `Assets/_Project/Art/Models/<ID>.glb`, турнтейбл `design/art/models/<ID>/turntable_0{1..8}.png`, лог.
- **Проверка**: `scripts/check_glb.py` (stdlib: заголовок GLB, JSON-чанк, accessors): GL1 треугольники > бюджета · GL2 материалов > бюджета · GL3 имя узла/меша ≠ ID · GL4 габариты (min/max POSITION × scale узлов) вне размера из asset-list ±10 % · GL7 LOD-цепочка неполная или LOD1 не легче LOD0 · GL8 непримененный масштаб узла (WARN).
- **Правило человека**: hero-ассеты (главный персонаж, ключевой арт) — 🟨; `made` ставит 🟨.
- **Источник**: arjun988/blender-skills `blender-modeler`, `lod-pipeline`, `export-pipeline`, `qa-review` (MIT); CoplayDev `blender-to-unity` (MIT, в unity-mcp) — шов «файл на диске», GLB через glTFast.

#### B3. 🆕 `sfx-design` (`gd-build`)
- **Description**: Звуковые эффекты по карте событий: рецепт слоями (транзиент, тело, хвост), синтез с параметрами, вариациями и seed, обработка ffmpeg/sox, бесплатные CC0-источники; манифест файлов с лицензиями и громкость проверяются скриптом. Триггеры RU: «сделай звук для», «звуковой эффект», «вариации звука», «синтезируй SFX», «найди CC0-звук». EN: "make a sound for", "design the SFX", "sound variations", "synthesize SFX". Не для решения, какие звуки нужны (gd:audio-direction), не для музыки (music-build), не для событий FMOD (fmod-sync).
- **Вход → выход**: `event-map.md` (события, вариации), `audio-bible.md` (формат, LUFS, пики) → WAV в `Assets/_Project/Audio/SFX/` или папке FMOD-ассетов, `design/audio/files.md`.
- **`gen_sfx.py` v2**: рецепт = слои с параметрами (частота, огибающая, шум, фильтр), `--variations N --seed S` (детерминированно), экспорт 48 кГц.
- **Проверка**: `scripts/check_audio_files.py design/audio/files.md --map design/audio/event-map.md --bible design/audio/audio-bible.md --root <audio dir>`: AF1 событие без файла · AF2 вариаций меньше, чем в карте · AF3 формат (частота, битность, каналы) ≠ bible · AF4 громкость вне диапазона (LUFS по BS.1770 на stdlib; true peak — через `ffmpeg ebur128`, если установлен, иначе sample peak с пометкой) · AF5 нет лицензии/URL у внешнего файла · AF6 `ph_` у файла со статусом `final`.
- **Правило**: звучание оценивает 🟨; скилл пишет «звучание не проверялось».
- **Источник**: unity-kit `unity-audio` (MIT, в ATTRIBUTION) — честность проверки; CCGS `team-audio`, агент `sound-designer` (MIT) — слои и роли; music-gen-skill (MIT) — прямой синтез sox/ffmpeg.

#### B4. 🆕 `music-build` (`gd-build`)
- **Description**: Музыка по состояниям игры: cue-лист → MIDI (запись на stdlib) → рендер FluidSynth с GM SoundFont → стемы → музыкальное событие FMOD с параметром интенсивности; длины петель и стемы проверяются скриптом. Триггеры RU: «сделай музыку», «музыкальная тема», «петля для», «стемы», «адаптивный трек». EN: "compose music for", "music loop", "render stems", "adaptive music track". Не для музыкальной дирекции и состояний (gd:audio-direction), не для SFX (sfx-design).
- **Вход → выход**: `audio-bible.md` (состояния, переходы, темп, тональность), `event-map.md` (Music-события, параметры) → `design/audio/music-cues.md`, `.mid`, WAV-стемы, строки в `files.md`, событие с multi-track + параметр `g_intensity` через `fmod-sync`.
- **`midi_write.py`** (stdlib: SMF type 1, дельта-время VLQ, program change, канал 9 — ударные).
- **Проверка**: `scripts/check_music.py design/audio/music-cues.md --files design/audio/files.md`: MU1 состояние из bible без cue · MU2 длина петли (сэмплы) не кратна такту (`sr × 60 / bpm × долей`) · MU3 стемы одного cue разной длины · MU4 громкость вне bible · MU5 переход без длины/точки синхронизации.
- **Главная тема** — hero-ассет, 🟨.
- **Источник**: sirruf/music-gen-skill (MIT) — MIDI-маршрут и рендер FluidSynth (код `render.sh` не копируем; `mido` заменяем stdlib-записью); FluidSynth (LGPL-2.1) — только как внешний инструмент; FluidR3_GM (MIT, Frank Wen).

#### B5. 🆕 `perf-check` (`gd-build`)
- **Description**: Замер производительности Unity-билда против design/tech/budgets.md: профайлер через MCP, замер после 10 минут игры, память, draw calls, время загрузки; отчёт и сравнение с прошлым замером скриптом. Триггеры RU: «замерь производительность», «проверь перф», «профилирование», «влезаем ли в бюджет кадра», «утечка памяти». EN: "profile the build", "check performance", "frame budget check", "memory leak check". Не для составления бюджетов (gd:tech-design), не для оптимизации ассетов (asset-integrate).
- **Выход**: `qa/perf/<date>.md` (таблица: метрика · бюджет · замер p50/p95/max · платформа · сцена · длительность · вердикт).
- **Проверка**: `scripts/compare_perf.py design/qa/perf/<date>.md --budgets design/tech/budgets.md [--prev …]`: PF1 метрика бюджета не замерена · PF2 p95 > бюджета · PF3 регрессия > 10 % к прошлому замеру (WARN) · PF4 замер не на целевой платформе (WARN: «редактор ≠ устройство»).
- **Источник**: CCGS `perf-profile` (MIT) — фазы и формат отчёта; tjboudreaux `tools-unity-profiling`, `eng-unity-mobile-optimization` (MIT) — FrameTimingManager, ProfilerMarker, бюджеты памяти.

#### B6. 🆕 `build-release` (`gd-build`)
- **Description**: Сборка игрока и выпуск: версия из тега, changelog, сборка Windows/Android через MCP или headless, workflow GameCI, .gitignore и LFS для Unity, скрипты SteamPipe; готовность проверяется скриптом. Логины и секреты — человек. Триггеры RU: «собери билд игрока», «релизная сборка», «настрой CI для Unity», «SteamPipe», «LFS для Unity». EN: "build the player", "release build", "set up Unity CI", "SteamPipe upload script". Не для плана запуска и магазина (gd:release-plan), не для тестов (qa-run).
- **Проверка**: `scripts/check_release.py <unity-project> [--changelog CHANGELOG.md]`: RL1 `bundleVersion` ≠ тегу/верхней версии changelog · RL2 `.gitignore` без `Library/`, `Temp/`, `Logs/`, `UserSettings/` · RL3 бинарные расширения (`.psd`, `.wav`, `.fbx`, `.glb`, `.png` > порога) не под LFS в `.gitattributes` · RL4 workflow ссылается на секреты, которых нет в списке ожидаемых (`UNITY_LICENSE`, `UNITY_EMAIL`, `UNITY_PASSWORD`) — только имена, значения не читаются · RL5 в сборке development-флаг для релиза · RL6 VDF SteamPipe без `AppID`/`DepotID`.
- **Источник**: game-ci/unity-builder, unity-test-runner (MIT) — используем как Actions, код не копируем; CCGS `release-checklist`, `day-one-patch`, `hotfix` (MIT) — пути патча и отката.

#### B7. `slice-build/scripts/preflight.py` (доработка)
Поиск Blender (PATH, `%ProgramFiles%\Blender Foundation`, Steam `steamapps/common/Blender`), ffmpeg, sox, FluidSynth, SoundFont (`*.sf2` в известных местах + `SOUNDFONT` env), FMOD Studio (`fmodstudiocl`), Blender MCP (конфиг Claude + аддон). Нет инструмента → соответствующий скилл уходит в `plan`. Флаг `--for sfx|music|model|anim|fmod|release`.

#### B8. Агент `art-director` (доработка, `gd`)
Разрешить пути `design/art/models/<ID>/*.png` (турнтейблы) и `build/*/screenshots/`; проверки силуэта и роли цвета по рендеру; числа из `check_glb.py` в отчёт.

### Волна C (P2)

#### C1. 🆕 `loc-build` (`gd-build`)
- **Description**: Таблицы Unity Localization из ключей UI и ID строк Ink, псевдолокализация, лимиты длины из UX; пропуски и переполнения проверяются скриптом. Триггеры RU: «таблицы локализации», «псевдолокализация», «подключи Unity Localization», «проверь переводы». EN: "localization tables", "pseudo-localize", "set up Unity Localization". Не для дизайна локализации и выборов Ink (gd:ink-slice), не для вёрстки UI (ui-build).
- **Проверка**: `scripts/check_loc.py`: LC1 ключ из UI/Ink без записи в таблице · LC2 ключ таблицы нигде не используется (WARN) · LC3 длина перевода > лимита · LC4 плейсхолдеры `{0}` не совпадают с источником · LC5 литерал вместо ключа в UXML/C#.
- **Источник**: CCGS `localize` (MIT) — режимы scan/extract/validate; `com.unity.localization` 1.5.8 (в поставке Unity; Unity Companion License — используем как пакет, не копируем).

#### C2. 🆕 `analytics-build` (`gd-build`)
- События из `analytics/events.md` → `AnalyticsEvents.cs` (константы, как `FmodEvents.cs`) + вызовы; бэкенд по умолчанию — локальный JSONL-лог для плейтестов; внешний бесплатный бэкенд — решение пользователя (ADR).
- **Проверка**: `scripts/check_analytics_calls.py`: AN1 событие без вызова · AN2 строковое имя события вне констант · AN3 параметр с признаками PII (правила `check_events.py`, копия) · AN4 событие отправляется без согласия (эвристика по флагу) (WARN).
- **Источник**: свой; принципы — `metrics-plan`.

#### C3. 🆕 `level-design` (`gd`)
- **Description**: Дизайн уровней и встреч: метрики персонажа из GDD → блокаут-план арены, волны и встречи, кривая напряжения и отдыха, критический путь и гейты. Пишет design/levels/<level>.md; достижимость и темп проверяет скриптом. Триггеры RU: «дизайн уровня», «арена», «волны врагов», «встречи», «темп уровня», «блокаут». EN: "level design", "arena layout", "enemy waves", "encounter design", "level pacing". Не для правил систем (gdd-author), не для карты систем (gd-systems-map), не для реализации в Unity (gd-build: feature-build).
- **Проверка**: `scripts/check_level.py design/levels/<level>.md --gdd …`: LV1 разрыв/высота больше метрики персонажа (knob из GDD, например `hop#K3`) · LV2 два пика напряжения без отдыха между ними · LV3 гейт без ключа на критическом пути · LV4 встреча ссылается на несуществующего врага/систему · LV5 длина уровня вне цели.
- **Источник**: awesome-gamedev-agent-skills `level-design` (Apache-2.0, ★1129) — метрики, блокаут, темп, гейты; Nice-Wolf `unity-level-design` (MIT) — контракты встреч, чекпоинты; CCGS шаблон `level-design-document` (MIT).

#### C4. 🆕 `release-plan` (`gd`)
- **Description**: План выпуска: `store` (страница магазина, теги, капсулы, трейлер — структура и аудит, тексты пишет человек), `launch` (чеклист готовности по отделам, go/no-go), `postlaunch` (метрики, патчи, hotfix-путь). Пишет design/release/*.md. Триггеры RU: «план релиза», «страница Steam», «чеклист запуска», «что после релиза», «теги Steam». EN: "release plan", "Steam page audit", "launch checklist", "post-launch plan", "Steam tags". Не для ревизии скоупа (scope-check), не для сборки и загрузки билда (gd-build: build-release).
- **Правило human-authorship**: тексты для игроков (описание, письма, посты, капсула) не пишет и не «полирует» — только аудит и структура; ключевой арт — 🟨.
- **Проверка**: `scripts/check_release_plan.py`: RP1 пункт чеклиста без владельца или даты · RP2 даты вне порядка (демо → страница → фест → релиз) · RP3 текст для игроков без отметки `human` · RP4 метрика postlaunch без порога и адресата.
- **Источник**: GarrettPetersen/indie-game-marketing-skills (MIT) — `plan-indie-game-marketing`, `audit-steam-store-page`, `optimize-steam-tags`, `review-game-trailer`, правило human-authorship; CCGS `launch-checklist`, `release-checklist`, `day-one-patch`, `hotfix` (MIT).

#### C5. `netcode-build` (`gd-build`) — только по решению (f)
Для Syncario (мобильный кооп). Бесплатный стек: Netcode for GameObjects; relay/lobby Unity Gaming Services — бесплатный лимит, дальше платно (проверить условия); это риск для правила «только бесплатное». Не проектирую до решения.

## 4. Форматы новых документов

Помечено **ОБЩИЙ** — формат читают или пишут несколько скиллов; изменил в одном — меняй во всех перечисленных и в шаблоне `templates/design/`.

| Файл | Пишет | Читает | Формат (ключевые колонки) |
|---|---|---|---|
| `build/<system>.log.md` **ОБЩИЙ** | `feature-build`, `slice-build`, `juice-build`, `ui-build`, `anim-build` | `qa-run`, `gd-router`, `check_build_log.py`, `check_juice.py` | frontmatter как у лога слайса + `system:`; таблица `ID · Статус · Доказательство · Задачи`, где ID — `R*/F*/E*/ED*`; раздел `Juice` (событие · кадр начала · длительность · цель · замер); `Deviations`; `Open issues` |
| `build/<system>.diff` | `feature-build` | агент `code-reviewer` | вывод `git diff` (не коммитится; в `.gitignore` игры) |
| `qa/perf/<date>[-soak].md` **ОБЩИЙ** | `perf-check`, `qa-run soak` | `compare_perf.py`, `gd-router` | frontmatter: `platform`, `build`, `scene`, `duration`; таблица `Metric · Budget · p50 · p95 · max · Verdict`; имена метрик = строки `tech/budgets.md` |
| `tech/budgets.md` **ОБЩИЙ** (есть) | `tech-design` | `perf-check`, `asset-integrate`, `model-build`, `qa-plan` | добавить стабильные ID строк `B1…` и колонку `Measure` (как замерить) |
| `qa/visual/` | `qa-run visual` (снимки), 🟨 (эталоны) | `diff_png.py` | `qa/visual/<case-id>.png` — эталон; `_pending/` — кандидаты; `README.md` — таблица `Case · Scene · Camera · Resolution · Seed · Tolerance · Approved (date, who)` |
| `levels/<level>.md` | `level-design` | `feature-build`, `qa-plan`, `check_level.py` | frontmatter `level`, `target_length`; разделы Metrics (ссылки на knobs), Layout (узлы и связи критического пути), Encounters (`EN1…`: враги, волна, триггер), Pacing (таблица минута → напряжение 0–3), Gates |
| `release/store.md`, `launch.md`, `postlaunch.md`, `builds.md` | `release-plan` (первые три), `build-release` (`builds.md`) | `gd-router`, `check_release_plan.py`, `check_release.py` | store: ассеты страницы (капсулы, скриншоты, трейлер) со статусом `human / todo`; launch: чеклист `Item · Owner · Due · Status`; postlaunch: `Metric · Threshold · Action · Addressee`; builds: `Version · Tag · Platform · Date · Build ID` |
| `audio/files.md` **ОБЩИЙ** | `sfx-design`, `music-build` | `fmod-sync` (импорт), `asset-integrate`, `check_audio_files.py`, `check_music.py` | `File · Event · Variation · Source (synth/cc0/made/ph) · License · URL · Author · LUFS · Peak · Status` |
| `audio/music-cues.md` | `music-build` | `check_music.py`, `audio-director` | `Cue · State · BPM · Meter · Key · Bars · Loop (samples) · Stems · Transition` |
| `audio/event-map.md` **ОБЩИЙ** (есть) | `audio-direction` | `fmod-sync`, `sfx-design`, `music-build`, `check_event_map.py`, `event_map_to_fmod.py` | + колонка `Bank` (по умолчанию `Master`) — меняется в `audio-direction/references/fmod-conventions.md`, `check_event_map.py`, `event_map_to_fmod.py`, шаблоне |
| `art/asset-list.md` **ОБЩИЙ** (есть) | `art-direction` | `asset-integrate`, `model-build`, `anim-build`, `check_assets.py`, `check_import.py`, `check_glb.py` | + колонки `Budget` (tris / px) и тип `anim` с фазами в кадрах |
| `art/models/<ID>/` | `model-build` | агент `art-director` | `turntable_01…08.png` (EEVEE, 45°), `<ID>.md` (tris, материалы, LOD, габариты из `check_glb.py`) |
| `ux/hud.md` **ОБЩИЙ** (есть) | `ux-onboarding` | `ui-build`, `loc-build`, `check_ui.py` | + колонка `Name` (имя элемента в UXML) и `Loc key` |
| `analytics/events.md` **ОБЩИЙ** (есть) | `metrics-plan` | `analytics-build` | без изменений |
| `qa/test-plan-*.md` **ОБЩИЙ** (есть) | `qa-plan` | `qa-run`, `feature-build`, `check_build_log.py` | + типы `visual`, `perf` |

## 5. Проверки репозитория (что добавить в `tools/`)
- `check_plugins.py`: drift копий (`gd-build/.../gdd_ids.py` = `gd/.../gdd_ids.py` и т. п.); запрет имён платных инструментов в SKILL.md и references вне раздела «Запрещено» (`generate_`, `create_rodin_job`, `create_hunyuan_job`, `suno`, `elevenlabs`, `meshy`, `musicgen`).
- `tools/trigger_cases.md` + проверка: таблица «типовой запрос → ожидаемый скилл» для всех пар из §6; фраза должна входить в триггеры ожидаемого скилла и не входить в триггеры других.
- Для каждого нового скрипта: позитивная фикстура (живая, если инструмент есть) и негативная («должен упасть»), как `fixtures/live/`.

## 6. Матрица пересечения триггеров

Обязательные пары из задания + найденные.

| Пара | С чем путается | Разводка (в «Не для …» обоих) |
|---|---|---|
| `game-feel` ↔ `juice-build` | «джус», «сочность», «отклик» | оценка ощущения, цели в кадрах → `game-feel`; реализация и замер в Unity → `juice-build`. Из триггеров `juice-build` исключить «сочность», «джус» без глагола; оставить «добавь джус», «хитстоп», «тряска камеры» |
| `juice-build` ↔ `anim-build` | «анимация удара», «squash/stretch» | отклик на событие (частицы, камера, hitstop, squash объекта) → `juice-build`; движение тела и клипы персонажа → `anim-build` |
| `ux-onboarding` ↔ `ui-build` | «HUD», «меню», «интерфейс» | что и где показывать → `ux-onboarding` (триггер «HUD» остаётся за ним); вёрстка в Unity → `ui-build` («сверстай HUD», «реализуй интерфейс») |
| `metrics-plan` ↔ `analytics-build` | «аналитика», «события» | какие события и зачем → `metrics-plan`; вызовы в коде → `analytics-build` («подключи аналитику», «вставь события в код») |
| `level-design` ↔ `gdd-author` ↔ `gd-systems-map` | «дизайн», «спека», «системы» | правила системы → `gdd-author`; список систем → `gd-systems-map`; пространство, встречи, темп → `level-design` |
| `audio-direction` ↔ `sfx-design` ↔ `music-build` | «звук», «музыка», «SFX» | что нужно и зачем, карта событий → `audio-direction` («какие звуки нужны», «список SFX», «адаптивная музыка»); делать файл SFX → `sfx-design` («сделай звук для»); делать музыку → `music-build` («сделай музыку», «стемы») |
| `art-direction` ↔ `model-build` ↔ `asset-integrate` | «ассеты», «модель», «список ассетов» | решения о стиле и списке → `art-direction`; создать модель → `model-build`; завести в Unity → `asset-integrate` |
| `scope-check` ↔ `release-plan` | «что успеваем», «план» | вырезание и оценка → `scope-check`; выпуск и магазин → `release-plan` |
| `release-plan` ↔ `build-release` | «релиз», «билд» | план, магазин, чеклист → `release-plan`; сборка, CI, загрузка → `build-release` |
| `feature-build` ↔ `slice-build` | «реализуй», «собери» | первый слайс из хендоффа → `slice-build`; система майлстоуна → `feature-build` («реализуй систему») |
| `perf-check` ↔ `tech-design` | «перф-бюджет» | составить бюджет → `tech-design`; замерить → `perf-check` |
| `qa-run visual` ↔ `art-director` | «скриншот», «проверь картинку» | пиксельная сверка с эталоном → `qa-run`; оценка читаемости и стиля → агент `art-director` |
| `loc-build` ↔ `ink-slice` | «локализация» | дизайн строк и выборов → `ink-slice`; таблицы в Unity → `loc-build` |
| `code-reviewer` ↔ системный `code-review` / `/review` | «ревью кода» | агент вызывается только из `feature-build` и `/gd-build:review`; у агента нет автотриггера |

## 7. Решения, которые нужны от тебя

| # | Вопрос | Варианты | Рекомендация (ГИПОТЕЗА) и почему |
|---|---|---|---|
| a | Список скиллов | утвердить всё · вырезать часть | Утвердить волны A и B целиком; из C — `level-design`, `release-plan`, `loc-build`; `analytics-build` урезать до локального JSONL-лога для плейтестов; `netcode-build` не делать (см. f). Кандидаты на вырезание, если нужно быстрее: `ui-build` (UI можно делать `feature-build` по `hud.md`), `music-build` (главную тему всё равно делает человек) |
| b | UI по умолчанию | UI Toolkit · uGUI | **UI Toolkit**: `manage_ui` в unity-mcp работает только с ним и снимает PNG (`render_ui`); UXML/USS — текст, `check_ui.py` проверяет цвета и ключи статически. uGUI — через ADR для world-space UI и тяжёлого джуса (поддержку world-space в UI Toolkit в Unity 6000.3 **не проверял**) |
| c | Формат моделей | GLB (glTFast) · FBX | **GLB**: glTFast — Apache-2.0; несёт PBR, эмиссию и анимацию (FBX теряет эмиссию и metallic по заметкам CoplayDev `blender-to-unity`); GLB разбирается на stdlib (`check_glb.py`), FBX — нет. MEATFORM без скелетной анимации — ограничений нет |
| d | Путь к музыке | MIDI + FluidSynth · Strudel | **MIDI + FluidSynth**: детерминированно, stdlib-запись MIDI, проверяемые длины петель, SoundFont под MIT. Strudel — AGPL-3.0, репозиторий на GitHub архивирован (переехал на Codeberg), работает в браузере — headless-рендер и проверка сложнее |
| e | CI на GameCI | сейчас · позже | **Позже** (волна B пишет workflow и проверку `check_release.py` в режиме `plan`). Нужны секреты `UNITY_LICENSE` / `UNITY_EMAIL` / `UNITY_PASSWORD` в GitHub — это твой шаг; для приватного репозитория минуты Actions ограничены бесплатным лимитом (условия проверить на GitHub) |
| f | `netcode-build` для Syncario | сейчас · позже | **Позже**: Syncario не дошёл до стадии сборки; relay/lobby UGS бесплатны только в лимите — нужна отдельная проверка условий |
| g | Версии | как в задании · иначе | Сейчас вышли `gd` 0.4.1 и `gd-build` 0.1.2 (фаза 1). Волна A — `gd` 0.5.0, `gd-build` 0.2.0; B — 0.6.0 / 0.3.0; C — 0.7.0 / 0.4.0. Тег по версии `gd` |
| h | PR фазы 1 | смёржить до волны A · вести волну A поверх ветки | **Смёржить сначала**: ветка `fix/gd-build-0.1.2-live` (ложный зелёный в headless-тестах — критично для MEATFORM Ф3) |
| i | Где Unity-проект в игровом репо | `<game>/unity/` · отдельный репо | **`<game>/unity/`** рядом с `design/` (как в `meatform/design/production-pipeline.md`); build-скиллы ищут проект там по умолчанию |
| j | Установка инструментов волны B | ffmpeg, sox, FluidSynth + SoundFont, Blender MCP (аддон + `claude mcp add`) | Нужны до живого прогона волны B; без них B выходит «не проверено». Команды — в отчёте фазы 0 |
| k | Stable Audio Open | подключать · нет | **Нет** в этой архитектуре; вернуться только после твоего решения и проверки лицензии весов |

## 8. План проверки по волнам

| Волна | Что можно проверить вживую на этой машине сейчас | Что останется «не проверено» |
|---|---|---|
| A | `feature-build` на второй системе one-tap-slice (например, генерация фонарей как отдельная система), `code-reviewer` на её diff, `qa-run visual` (эталон из скриншотов фазы 1), `juice-build` (hitstop/частицы приземления, замер кадров), `ui-build` (UI Toolkit HUD), `asset-integrate` (CC0-ассеты Kenney → замена плейсхолдеров), `fmod-sync` импорт файлов в FMOD (headless) | `fmod-sync hook` на реальных вызовах FMOD for Unity (нет пакета) |
| B | `perf-check` в редакторе; `build-release` Windows-билд; `check_glb.py` на GLB из glTF-sample-models (при наличии); `model-build`/`anim-build` в Blender — после установки Blender MCP | `sfx-design`/`music-build` без ffmpeg/sox/FluidSynth; Android-перф; CI без секретов |
| C | `level-design`, `release-plan` (документы и скрипты); `loc-build` с псевдолокализацией | внешний бэкенд аналитики |

## 9. Источники (перепроверено `gh api` 2026-09-24, клоны в `vendor/`)

| Репозиторий | ★ | Лицензия | Последний пуш | Что берём | Как |
|---|---|---|---|---|---|
| fagemx/gstack-game | 71 | MIT | 2026-05-31 | `gameplay-implementation-review` (Pass 0–2) | адаптация, без преамбулы и телеметрии |
| Donchitos/Claude-Code-Game-Studios | 25 404 | MIT | 2026-09-24 | `perf-profile`, `localize`, `code-review`, `team-audio`, `launch-checklist`, `release-checklist`, `day-one-patch`, `hotfix`, шаблон `level-design-document` | адаптация идей и шаблонов |
| Benjamin-Curlier/unity-kit | 0 | MIT | 2026-07-26 | `unity-audio` (честность проверки звука) | уже в ATTRIBUTION |
| arjun988/blender-skills | 212 | MIT | 2026-07-10 | `blender-modeler`, `export-pipeline`, `lod-pipeline`, `rigging`, `animation`, `asset-optimization`, `qa-review` | адаптация чеклистов |
| CoplayDev/unity-mcp (`.claude/skills/blender-to-unity`) | 14 452 | MIT | 2026-09-22 | шов Blender → Unity через файл, GLB vs FBX | адаптация; `import_model_file` не используем (группа `asset_gen`) |
| ahujasid/mcp-for-blender | 29 276 | MIT + Terms of Use | 2026-09-24 | Blender MCP как инструмент | не копируем; запрет `create_rodin_job`, `create_hunyuan_job`, `download_sketchfab_model`; `DISABLE_TELEMETRY=true` |
| sirruf/music-gen-skill | 0 | MIT | 2026-05-30 | маршрут MIDI → FluidSynth → WAV | адаптация; `mido` заменяем stdlib |
| GarrettPetersen/indie-game-marketing-skills | 4 | MIT | 2026-09-09 | план маркетинга, аудит страницы Steam, теги, трейлер, human-authorship | адаптация |
| tjboudreaux/cc-plugin-unity-gamedev | 9 | MIT | 2026-02-06 | `tools-unity-profiling`, `eng-unity-mobile-optimization`, `tools-unity-animation` | идеи; how-to API — официальный Unity Plugin |
| Nice-Wolf-Studio/unity-claude-skills | 34 | MIT | 2026-09-15 | `unity-level-design`, `unity-ui-patterns`, `unity-animation` | идеи |
| gamedev-skills/awesome-gamedev-agent-skills | 1 129 | Apache-2.0 | 2026-09-10 | `level-design`, `game-feel` | адаптация с NOTICE в ATTRIBUTION |
| game-ci/unity-builder, unity-test-runner | 1 096 / 266 | MIT | 2026-09-16 | GitHub Actions для сборки и тестов | используем, не копируем |
| Unity-Technologies/com.unity.cloud.gltfast | 127 | Apache-2.0 (файл LICENSE.md; API GitHub показывает NOASSERTION) | 2026-08-28 | импорт GLB | пакет |
| tidalcycles/strudel | 3 032 | AGPL-3.0, архивирован | 2025-06-19 | — | не используем (решение d) |
| FluidSynth/fluidsynth | 2 494 | LGPL-2.1 | 2026-09-20 | рендер MIDI | внешний инструмент |
| pianobooster/fluid-soundfont (FluidR3_GM) | 13 | MIT | 2020-12-12 | GM SoundFont | внешний файл |

Не берём: Unity-Technologies/unity-agent-plugin (лицензия NOASSERTION, Unity Companion License — только ставится рядом как справочник); AnkleBreaker-Studio/unity-mcp-* (лицензия «Other»).

## 10. Соответствие фазам MEATFORM (`meatform/design/production-pipeline.md`)

| MEATFORM | Стадии | Новые скиллы, которые понадобятся |
|---|---|---|
| Ф3 техспайк (модульное тело, 24 существа, 60 fps) | 9–10 | `anim-build` (процедурная походка, пружины), `perf-check` (нагрузка) |
| Ф4 mechanic slice | 9–12 | `juice-build` (укус < 50 мс, перекраска ≤ 120 мс), `ui-build`, `fmod-sync` импорт |
| Ф5 vertical slice | 13 | `gd-handoff milestone`, `feature-build`, `code-reviewer`, `level-design` (4 зоны) |
| Ф6 Alpha / контент | 13 | `model-build`, `asset-integrate`, `sfx-design`, `music-build` |
| Ф7 Beta, полировка | 14 | `perf-check` (min-spec), `qa-run visual/soak`, `loc-build` (если языки) |
| Ф8 релиз | 15–16 | `release-plan`, `build-release` |
