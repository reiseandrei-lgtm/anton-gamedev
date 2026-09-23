# Прогон скиллов волны 1 на примере «Lantern Hop» (2026-09-23)

Мини-игра: мобайл, портрет, одна кнопка. Фонарщик прыгает по фонарям, дальность задаётся удержанием, искры на дальних фонарях дороже. Вход — готовые стадии 0–7: `design/pillars.md`, `concept.md`, `systems-map.md`, `gdd/hop.md`, `gdd/spark.md` (со стабильными ID), `handoff/first-hop.md` (ED1–5, DD1–3).

**Условия.** Скиллы `gd` выполнялись в сессии Claude Code по их SKILL.md. Агенты-ревьюеры запускались как изолированные субагенты: им передавались только пути, перечисленные в определении агента. Unity и FMOD Studio на машине не установлены, поэтому `gd-build` проверен только в режиме деградации, на синтетических фикстурах (`fixtures/`).

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

## Скиллы gd-build (режим деградации)

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

## Не проверено (нужна машина с Unity 6 + CoplayDev/unity-mcp + FMOD Studio)
Реальная сборка слайса и verify loop через MCP, PlayMode и InputTestFixture, headless-прогон в Unity, запуск JS в FMOD Studio, компиляция `FmodEvents.cs` с FMOD for Unity.
