# Прогон скиллов на примере «Lantern Hop» (2026-09-23; живой gd-build — 2026-09-24)

Мини-игра: мобайл, портрет, одна кнопка. Фонарщик прыгает по фонарям, дальность задаётся удержанием, искры на дальних фонарях дороже. Вход — готовые стадии 0–7: `design/pillars.md`, `concept.md`, `systems-map.md`, `gdd/hop.md`, `gdd/spark.md` (со стабильными ID), `handoff/first-hop.md` (ED1–5, DD1–3).

**Условия.** Скиллы `gd` выполнялись в сессии Claude Code по их SKILL.md. Агенты-ревьюеры запускались как изолированные субагенты: им передавались только пути, перечисленные в определении агента. На 2026-09-23 Unity и FMOD Studio на машине не было, и `gd-build` проверялся только в режиме деградации, на синтетических фикстурах (`fixtures/`). Живой прогон — в разделе «Живой прогон gd-build (2026-09-24)».

## Скиллы gd

| Скилл | Что сделано | Скрипт | Результат |
|---|---|---|---|
| `art-direction` | `art/art-bible.md`, `art/asset-list.md` | `check_palette.py`, `check_assets.py` | PASS / PASS (9 ассетов, 8 в слайсе) |
| `audio-direction` | `audio/audio-bible.md`, `audio/event-map.md` | `check_event_map.py` | покрыто 6 из 6 Feedback-строк; WARN E8 (Charge: приоритет 3 в карте ≠ 2 в GDD) — оставлен как демонстрация |
| `ux-onboarding` | `ux/ftue.md`, `ux/hud.md`, `ux/accessibility.md` | — | 4 L-пункта, таймлайн до 1:00; a11y: 3 gap с решением или отсрочкой |
| `tech-design` | `tech/architecture.md`, `tech/budgets.md`, `tech/adr/001-save-format.md` | `check_knobs.py` | PASS: 9 из 9 knobs в Config map, 4 модуля без циклов |
| `qa-plan` | `qa/test-plan-first-hop.md` (21 кейс) | `check_coverage.py` | PASS: R/F/E 20 из 20, ED 5 из 5, DD → playtest-кейсы, smoke 6 шагов |
| `playtest` (plan) | `playtest/2026-09-23-first-hop.plan.md` + 5 **синтетических** заметок | `aggregate_codes.py` | горячее окно 0:00–1:00 (4 из 5), P2 — stuck и quit intent |
| `metrics-plan` | `analytics/events.md`, `analytics/funnels.md` | `check_events.py` | PASS: 5 событий, 3 KPI с порогом, воронка FTUE 4 шага |

## Агенты-ревьюеры (изолированно)

| Агент | Вердикт | Что нашёл сверх скриптов (главное) | Отчёт |
|---|---|---|---|
| `art-director` | CONCERNS | VP2 «искра ярче всего» противоречит палитре (искра темнее персонажа) и VP1; у индикатора края нет формы и строки в asset-list; искра 6 мм < 8 мм; нумерация FB в bible ≠ asset-list | `design/reviews/2026-09-23-art.md` |
| `audio-director` | CONCERNS | в кадре «приземление на искру» конфликтуют Land (1) и Spark (2), а AP2 держится на Spark; нет перехода dead → run при рестарте; приоритет Charge расходится с GDD; вариации pitch ломают AP1 | `design/reviews/2026-09-23-audio.md` |
| `qa-lead` | CONCERNS | hop#R4 проверен только на перелёт — забытый модуль (недолёт засчитан) пройдёт все тесты; не покрыты переходы Airborne → Idle/Falling; T-hop-10 противоречит GDD; гипотеза хендоффа не стала кейсом | `design/reviews/2026-09-23-qa-first-hop.md` |
| `playtest-analyst` | confirmed (на границе) | порог считается по всем 5, а гипотеза — про новичков (среди новичков 2 из 3); F1 → ux-onboarding (новички тапают коротко), F2 → game-feel (не видно заряда), F3 → баг (фонарь дальше максимума — одно наблюдение, воспроизвести) | `design/playtest/2026-09-23-first-hop.report.md` |

Изоляция соблюдена: `playtest-analyst` не открывал GDD и хендофф, ревьюеры не читали историю создания. Находки независимы: например, «фонарь дальше максимальной дальности» из заметок совпал с вопросом из лога сборки и тех-дизайна, хотя агент их не видел.

## Скиллы gd-build (режим деградации, 2026-09-23)

| Скилл | Что проверено | Результат |
|---|---|---|
| `slice-build` | `preflight.py` на папке без Unity → режим `plan`; лог `build/first-hop.log.md` в режиме plan (ни одного ✅); `gen_sfx.py` сгенерировал ph_jump / ph_land / ph_fail | работает; **сборка в Unity не выполнялась** |
| `qa-run` | `parse_nunit.py` на фикстуре: 4 из 5, падение сопоставлено с T-spark-02, T-ID из `[Category]` и из имени метода распознаны, 11 тестов плана без реализации; пустой прогон → exit 3; `run-tests-headless.ps1` на не-Unity папке → exit 3 с понятной причиной; `.ps1` и `.sh` проходят синтаксический разбор | работает; **тесты в Unity не запускались**; отчёт `qa/runs/2026-09-23-first-hop.md` (INCOMPLETE) и `qa/bugs/BUG-001.md` — из фикстуры |
| `fmod-sync` | `event_map_to_fmod.py` → `design/audio/build/` (JSON, JS, `FmodEvents.cs`); JS прогнан в node на заглушке API FMOD (синтаксис, идемпотентность папок и шин); `diff_fmod.py` на фикстуре GUIDs → D1 Amb/Sky/Wind, D2 Jump2 | работает; **в FMOD Studio скрипт не запускался**; `mixerInput.output`, метки enum-параметров и `event.parameters` не проверены на реальном API |

## Что исправлено по итогам прогона
- `check_palette.py`: пары с ролью `accent` (агент art-director показал, что искру скрипт не проверял).
- `check_event_map.py`: проверка E8 — приоритет события ≠ приоритету Feedback в GDD (нашёл audio-director).
- `event_map_to_fmod.py`: кеш шин в JS — на заглушке шина создавалась на каждое событие.
- `gen_sfx.py`, все скрипты: вывод в UTF-8 (консоль Windows cp1251 падала на кириллице).
- `commands/tech.md`: YAML-frontmatter не парсился (двоеточие в description) — найдено `claude plugin validate`.
- Триггеры: `slice-build` «реализуй хендофф» пересекался с `gd-handoff`; старый `narrative-structure` "continuity check" пересекался с `narrative-continuity`.

## Живой прогон gd-build (2026-09-24)

**Условия.** Unity 6000.3.24f1 (лицензия Personal), CoplayDev/unity-mcp 10.2.0 (пакет по тегу, сервер `uvx mcpforunityserver==10.2.0`, HTTP, телеметрия выключена `DISABLE_TELEMETRY=true`), FMOD Studio 2.03.14. Unity-проект `D:/Unity/Projects/one-tap-slice` и проект FMOD `D:/FMOD/Projects/one-tap-slice` лежат вне репозитория, под своим git. MCP-сервер добавили посреди сессии Claude Code, поэтому его инструменты вызывались через CLI того же сервера (`unity-mcp raw <tool>`), а не как инструменты сессии. Пустой проект FMOD получен очисткой официального примера `Examples.fspackage` скриптом (новый проект `fmodstudiocl` не создаёт), `-diagnostic` — без ошибок.

| Скилл | Что сделано вживую | Результат |
|---|---|---|
| `slice-build` | preflight → тесты первым (красный прогон 0/10 на заглушках) → реализация → verify loop после каждой задачи (mtime DLL, консоль, тесты) → сцена и конфиги через MCP → play-mode smoke с пробами и скриншотами | ED2–ED4 ✅, ED5 ⚠️ (в редакторе), ED1 ⛔ (нет Android). Лог: `design/build/first-hop.log.md`, скриншоты: `design/build/first-hop/screenshots/` |
| `qa-run` suite | MCP `run_tests` и headless `run-tests-headless.ps1` → `parse_nunit.py --plan` | EditMode 11/11, PlayMode 5/5 своих; план: 15 из 15 в прогоне. Отчёт: `design/qa/runs/2026-09-24-first-hop.md` (INCOMPLETE: нет устройства) |
| `qa-run` smoke | 6 шагов smoke-набора: пробы состояния, скриншоты, 67 с забега | 4 ✅, 2 ⚠️ частично (редактор вместо устройства) |
| `fmod-sync` | `event_map_to_fmod.py` → `fmodstudiocl -script …cli.js` ×2 → `Build/GUIDs.txt` → `diff_fmod.py` → `fmodstudiocl -build` | +9 папок, +8 событий, +4 шины, +1 снапшот, +3 параметра, 4 подключения, 8 событий в мастер-банке; повторный запуск +0; diff PASS 16/16; `Master.bank` собран; `FmodEvents.cs` компилируется в Unity |

### Дефекты gd-build, найденные вживую (исправлены в 0.1.2)
| # | Где | Что было | Как нашли |
|---|---|---|---|
| 1 | `run-tests-headless.ps1` | **ложный зелёный**: упавший тест → exit 0 (в PowerShell 5.1 пустой `ExitCode` без `Handle`; падения из XML в код выхода не шли) | временный `Assert.Fail` |
| 2 | `parse_nunit.py`, `qa-run`, `gd: qa-plan` | советовали `[Category("T-hop-01")]`, а NUnit запрещает «-» в категориях: все 10 тестов упали, не начавшись | первый красный прогон |
| 3 | JS `fmod-sync` | параметры дублировались при повторном запуске (`charge (2)`); второе событие с тем же параметром получало другое имя, и `setParameterByName` на нём не сработал бы | второй запуск на FMOD 2.03.14 |
| 4 | JS `fmod-sync` | события не назначались в банк: их нет ни в сборке, ни в `GUIDs.txt` (`diff_fmod` давал 8 × D1) | экспорт GUIDs |
| 5 | `verify-loop.md`, `mcp-actions.md` | `Logs/Editor.log` проекта — такого файла нет; лог редактора общий, в `%LOCALAPPDATA%` | первая проверка компиляции |
| 6 | `verify-loop.md` | не было: тесты при ошибке компиляции гоняют старую DLL; refresh без `force` в редакторе без фокуса не компилирует; мост отключается на domain reload; `queueEventOnly` для InputTestFixture; `testables`; ориентация Game view; активная сцена после перезапуска | verify loop |
| 7 | `preflight.py` | не проверял `testables` (без них нет InputTestFixture) и Active Input Handling | настройка проекта |
| 8 | `mcp-actions.md` | не было: старт сессии моста, телеметрия по умолчанию, CLI `unity-mcp` для текущей сессии, параметры скриншота, закрытие редактора через `File/Exit` | установка MCP |
| 9 | `run-tests-headless.*` | предупреждение «working tree modified» на каждый новый `.meta` | headless-прогон |
| 10 | `fmod-sync` | не было headless-пути: добавлены `gd_sync_event_map.cli.js` (синхронизация, сохранение, экспорт GUIDs) и сверка параметров в `diff_fmod.py` | — |

Каждое исправление проверено на том, что раньше ломалось: 1 — временный падающий тест даёт exit 2; 3 и 4 — повторный запуск даёт +0, diff PASS; 2 — `parse_nunit` на живом XML находит все 15 T-ID плана. Живые выводы сохранены в `fixtures/live/` и покрыты тестами `tools/test_scripts.py` (27 тестов).

## Не проверено
- Сборка игрока на Android и перф на устройстве (ED1, T-slice-01, T-slice-03): нет Android Build Support и устройства.
- FMOD for Unity и вызовы `RuntimeManager.*`: пакет скачивается только после входа на fmod.com.
- Запуск `gd_sync_event_map.js` из меню FMOD Studio GUI (проверен тот же код через `fmodstudiocl`).
- Звучание плейсхолдеров и отличимость двойной искры — оценивает человек.
- MCP как инструменты сессии Claude Code (работали через CLI того же сервера); IvanMurzak/Unity-MCP.

## Волна A (2026-09-24): из слайса в игру — gd 0.5.0, gd-build 0.2.0

**Условия.** Те же: Unity 6000.3.24f1, unity-mcp 10.2.0 через CLI, FMOD Studio 2.03.14, headless `fmodstudiocl`. Пример переведён в продакшн: решение `advance` (помечено как пример), система `chain` (генерация цепочки — раньше жила в презентации без правил и seed), хендофф `handoff/alpha.md` в режиме milestone, тест-план `qa/test-plan-alpha.md`.

### gd
| Скилл | Что сделано | Проверка | Результат |
|---|---|---|---|
| `gd-handoff` (milestone) | `handoff/alpha.md`: 3 системы, 5 ED `ED-<system>-N`, DD-chain-1 | `check_coverage.py` | ED 10 (слайс + майлстоун) покрыты |
| `gdd-author` | `gdd/chain.md` (R1–R5, F1, E1–E3, K1–K4) | `check_knobs.py` | PASS: 13 из 13 knobs в Config map, 5 модулей |
| `qa-plan` (visual, perf) | 26 кейсов: 11 chain, visual для FB и HUD, perf для B1–B4 | `check_coverage.py` (два плана, два хендоффа, бюджеты) | PASS: R/F/E 29 из 29, Q9 и Q10 без замечаний |

### gd-build
| Скилл | Что сделано вживую | Результат |
|---|---|---|
| `feature-build` chain | тесты первым: красный 0/7 → зелёный 7/7; ChainGenerator (чистый класс), ChainConfig через MCP; GameBootstrap без своей генерации; T-chain-08 и T-chain-11 в сцене | `check_build_log.py` PASS: 12 из 12 ID (✅ 11, ⚠️ 1 — эталон ждёт человека). Лог `build/chain.log.md` |
| агент `code-reviewer` | изолированный субагент, только diff + GDD + архитектура + тест-план | **CONCERNS**, 5 главных находок: R4 в сцене без теста (закрыто T-chain-11), фонари вне пула и утечка материалов (подтверждено soak, исправлено), нижняя граница зазора и «фонари в кадре» (вопросы дизайнеру в GDD). Отчёт `reviews/2026-09-24-code-chain.md` |
| `juice-build` | FB2 squash/stretch по кадрам, FB3 пыль в кадр касания; замер PlayMode при captureFramerate 60 | T-hop-21: squash 1 / stretch 2 кадра (цель 1 / 2), T-hop-22: пыль +0 кадров, 12 частиц. `check_juice.py`: FAIL 0, WARN 4 (у FB1, FB4, FB5 нет целей в кадрах в GDD — честно) |
| `ui-build` | UI Toolkit: Theme.uss (роли), HUD.uxml/uss, PanelSettings и UIDocument через MCP, IMGUI удалён | `check_ui.py` PASS; скриншоты 1080×1920 и 1440×3200; на картинке найден дефект вёрстки (рекорд уезжал за экран), исправлен |
| `asset-integrate` | проверка проекта: арт — примитивы в коде, звук — 5 файлов из `files.md` | Alpha PASS; `--stage beta` FAIL 8 × IM8 — пример честно не готов к Beta |
| `qa-run visual` | seed 42, камера → RenderTexture 1080×1920, UI → PanelSettings.targetTexture | два снимка одного seed совпали на 0.000 %; 4 кандидата в `qa/visual/_pending/` — утверждает человек |
| `fmod-sync` банки, файлы, hook | headless: +2 банка (Music создан), 5 файлов звука, Spark — MultiSound из 2 вариаций; повторный запуск +0 | `diff_fmod` PASS 18/18, банки собраны; `check_fmod_calls.py`: FAIL 0, WARN 8 (события не вызываются — FMOD for Unity не подключён) |
| `qa-run soak` | 6 мин × 2 с драйвером прыжков (прогресс подтверждает игра) + контроль простоя 3 мин | **до** пула: FAIL SK5 материалы 190 → 540 (58/мин), SK1 +1.76 МБ/мин; **после**: материалы 199 → 199, объекты ≤ 35, 42 прыжка; SK1 +2.81 МБ/мин при простое +3.03 МБ/мин — рост даёт редактор и MCP, не игра; `check_soak --baseline` PASS. Отчёты `qa/perf/2026-09-24-soak-*.md` |

### Находки живого прогона волны A (исправлены)
ScriptableObject в файле с другим именем → ассет без скрипта (NRE); PlayMode-тест без уборки роняет соседей; `render_ui` в play mode игнорирует размер (снимки — через RenderTexture / `PanelSettings.targetTexture`); редактор без фокуса перестаёт тикать (`runInBackground`); драйвер soak «играл» 3 минуты в замершую игру — отсюда SK6; в редакторе память растёт и в простое — отсюда `check_soak --baseline`; ложные срабатывания `check_ui` (#fade), `check_fmod_calls`/`check_import` (путь с `/Temp/`), `check_juice` (несколько фаз FB); Beta на плейсхолдерах проходила — добавлен IM8. Минимальный прыжок 1.15 > chain#K1 = 1.0: подтверждает вопрос ревью о нижней границе зазора (в Open Questions GDD).

### Не проверено (волна A)
Headless-прогон после волны A (редактор был открыт — тесты шли через MCP); эталоны `qa/visual/` (ждут человека); Android и FMOD for Unity.
