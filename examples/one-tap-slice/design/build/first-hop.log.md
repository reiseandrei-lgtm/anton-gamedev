---
status: review
updated: 2026-09-24
slice: first-hop
mode: live
unity: 6000.3.24f1
mcp: CoplayDev/unity-mcp 10.2.0 (HTTP, CLI unity-mcp; телеметрия выключена)
build: d3ffb9a (локальный git Unity-проекта D:\Unity\Projects\one-tap-slice, вне этого репозитория)
---

# Build log — first-hop

> Режим **live**: Unity 6000.3.24f1 + CoplayDev/unity-mcp 10.2.0. MCP-инструментов в сессии Claude Code не было (сервер добавлен посреди сессии), поэтому тот же сервер вызывался через его CLI `unity-mcp` по HTTP. Предыдущий лог (2026-09-23) был в режиме plan и заменён этим.

## Engineering Done
| ED | Статус | Доказательство | Задачи |
|---|---|---|---|
| ED1 | ⛔ | не выполнено: Android Build Support не установлен, устройства нет. В редакторе 60 с забега — 67 тыс. кадров, консоль чистая (это не замер на устройстве) | 9 |
| ED2 | ✅ | EditMode T-hop-01…05 зелёные, PlayMode T-hop-06…10 зелёные (InputTestFixture); красный прогон до реализации: 10/10 упали с NotImplementedException | 2, 3 |
| ED3 | ✅ | EditMode T-spark-01…03 зелёные; smoke: приземление на фонарь с искрой → счёт 0 → 1 (screenshots/02-after-hit.png) | 5 |
| ED4 | ✅ | T-hop-10: тап через 0.2 с после падения игнорируется, тап в Dead → Idle за ≤ 0.3 с; smoke: рестарт → lantern 0, счёт 0 | 6 |
| ED5 | ⚠️ | T-spark-04, T-spark-05 зелёные; рекорд 1 пережил перезапуск редактора (JSON в persistentDataPath). Между запусками приложения на устройстве не проверено (T-slice-03 manual) | 7 |

## Tasks
| # | Задача | Модуль | Тесты | Итог | fix-циклов |
|---|---|---|---|---|---|
| 1 | Unity-проект (batchmode `-createProject`), Input System 1.20.0 + `testables`, Test Framework 1.6.0, uGUI, MCP; Active Input Handling = Input System | — | — | ✅ | 0 |
| 2 | `HopConfig` (SO), `HopLogic` F1, F2, R4, E3 | Hop | T-hop-01…05 | ✅ | 1 (CS0104: `Property` ↔ `UnityEngine.PropertyAttribute`) |
| 3 | `HopStateMachine`, `PlayerHop` (read-only `State`, `Charge`) | Hop | T-hop-06…10 | ✅ | 1 (тесты: `queueEventOnly: true`) |
| 4 | Генерация цепочки: зазор ∈ [K1, K3 − K4] | Presentation | smoke | ✅ | 0 |
| 5 | `SparkConfig`, `SparkScore`, `SparkPlacer`, `SparkRun` | Spark | T-spark-01…03 | ✅ | 0 |
| 6 | Рестарт без перезагрузки сцены | Hop, Presentation | T-hop-10, smoke 3 | ✅ | 0 |
| 7 | `RecordStore` + `IRecordStorage`, `FileRecordStorage` (JSON, `version: 1`) | Core, Spark | T-spark-04, 05 | ✅ | 0 |
| 8 | Сцена Run, `GameBootstrap`: примитивы цветов ролей, FB1 (разгорание), FB4 (затемнение), FB5 (пульс), HUD ключами | Presentation | smoke 2–6 | ✅ | 1 (пульс рос от края — видно только на скриншоте) |
| 9 | Android-билд, профайлинг | — | T-slice-01 | ⛔ | — |
| 10 | `FmodEvents.cs` (fmod-sync) в сборке `Game.Audio` | Audio | FmodEventsTests | ✅ компилируется; вызовов FMOD нет — пакета FMOD for Unity нет | 0 |

## Placeholders
| Что | Чем подменено | Как отличить в билде |
|---|---|---|
| персонаж, фонари, искры | капсула, цилиндры, куб под 45° (ромб) цветов ролей палитры | имена объектов `… (placeholder)` |
| SFX | `gen_sfx.py`: ph_jump, ph_land, ph_fail, ph_coin (двойная искра), ph_confirm (одиночная) через `AudioSource` | префикс `ph_` |
| строки UI | ключи `[ui.record]`, `[ui.again]` | квадратные скобки |
| шрифт | IMGUI по умолчанию вместо `font_ui_main_regular` | — |

## Deviations from handoff  (решает дизайнер)
| Что в хендоффе | Что сделано | Почему |
|---|---|---|
| SHOULD: звук через FMOD (FB1–FB4 hop, FB1 spark) | `AudioSource` + `ph_*.wav`; заряд (FB1) без звука | FMOD for Unity не установлен (скачивание требует входа на fmod.com) |
| генерация фонарей не описана | зазор ∈ [K1, K3 − K4] | иначе возможен неизбежный промах; нужен R7 в GDD hop |
| HUD — top-center в safe area | IMGUI без safe area | плейсхолдер; UI по `ux/hud.md` — задача `ui-build` |
| высота дуги | `K3 · 0.25` — только визуал | в GDD высота «фиксирована», числа нет |

## Verify summary
Компиляция: все `Game.*` DLL новее исходников после каждой задачи (5 циклов) · Консоль: 0 ошибок · EditMode 11/11 (10 кейсов плана + FmodEvents) · PlayMode 5/5 своих (+ 2/4 тестов пакета Input System, 2 пропущены пакетом) · headless: те же числа, 20 с · Smoke: 6 шагов, см. `qa/runs/2026-09-24-first-hop.md` · Скриншоты:
- `first-hop/screenshots/01-start.png` — капсула на первом фонаре, две искры-ромба, счёт 0;
- `02-after-hit.png` — после точного прыжка: второй фонарь, искра собрана, счёт 1;
- `03-restart-screen.png` — после промаха: затемнение, `[ui.record] 1` цветом accent (новый рекорд), `[ui.again]`;
- `04-after-restart.png` — новый забег, счёт 0.

Game view был горизонтальным (2560×1440), слайс — портретный: скриншоты не равны кадру на телефоне.

## Open issues
- R7 «гарантия достижимости» в GDD hop — вопрос дизайнеру (генерация уже так работает).
- hop#R3: время полёта 0.5 с зашито константой — вынести в knob? (вопрос из test-plan).
- В кадре «приземление на искру» один звук вместо Land + Spark (находка audio-director) — решить в `audio-direction`.
