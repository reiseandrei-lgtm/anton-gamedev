# Замер производительности: метод и формат отчёта

Источники идей: CCGS `perf-profile` (MIT) — фазы и формат отчёта; tjboudreaux `tools-unity-profiling`, `eng-unity-mobile-optimization` (MIT) — FrameTimingManager, ProfilerMarker, бюджеты памяти. Код не копировался.

## 1. Что замерять
Каждая строка `design/tech/budgets.md` (ID `B*`) → одна строка `## Results`. Колонка «Как замерить» бюджета задаёт метод; нет её — по таблице:

| Метрика | Канал MCP (CoplayDev 10.2) | Без MCP |
|---|---|---|
| Время кадра (ms) | `manage_profiler` `get_frame_timing` — серия ≥ 30 снимков в play mode, p50/p95/max по `cpu_frame_time_ms` (или GPU, если бюджет про GPU) | `FrameTimingManager` в dev-сборке, лог в файл |
| Batches / draw calls | `manage_profiler` `get_counters` `category: Render` (`Batches Count`, `Draw Calls Count`, `SetPass Calls Count`) | Frame Debugger, Stats в Game view |
| Память (MB) | `get_counters` `category: Memory` (`Total Used Memory`, `GC Reserved Memory`); снимок — `memory_take_snapshot` (нужен `com.unity.memoryprofiler`) | Memory Profiler вручную |
| Время загрузки / рестарта (s) | PlayMode-тест с `Time.realtimeSinceStartupAsDouble` до и после, вывод в лог | секундомер по логу |
| Размер сборки (MB) | размер файла после `build-release` (APK/AAB, папка Windows) | Build Report |

## 2. Условия замера
- **Прогрев**: бюджет «после N мин игры» — сначала N минут скриптованного ввода (как `qa-run soak`), потом серия. Без прогрева — пометка в Notes.
- **Платформа**: редактор завышает и CPU, и память (редактор + MCP в том же процессе). Замер в редакторе годится для поиска регрессий, не для вердикта по бюджету устройства: `compare_perf.py` даёт PF4. Вердикт по бюджету — сборка игрока на целевом устройстве (dev build + Profiler по USB / `adb`).
- **Окно без фокуса** в Windows снижает частоту обновления редактора — время кадра завышено. Записать в `platform`.
- **Память в редакторе растёт в простое** — для утечек нужен `qa-run soak` с `--baseline`, не этот замер.

## 3. Формат отчёта `design/qa/perf/<date>.md` (общий с `qa-run soak`)
```markdown
---
status: draft
updated: YYYY-MM-DD
platform: editor (Unity 6000.3, Windows) | Android <модель> | Windows player
build: <git sha>
scene: Assets/_Project/Scenes/<scene>.unity
duration: <секунды серии>
warmup: <секунды прогрева или 0>
---
# Perf — <майлстоун>

## Results
| ID | Metric | Budget | p50 | p95 | max | Verdict |
|---|---|---|---|---|---|---|
| B1 | Кадр (ms) | 16.6 ms | 1.0 | 1.4 | 3.2 | PASS |
| B4 | Размер APK (MB) | ≤ 60 MB | n/a: сборки Android нет | | | — |

## Samples
<сырые числа или путь к JSON-выводу MCP>

## Notes
<условия, отклонения, что не замерено и почему>
```
p50/p95/max — в единицах бюджета. Для счётчиков без распределения (размер сборки) p50 = p95 = max. `n/a: причина` вместо числа — честный пропуск (WARN, не FAIL).

## 4. Проверка и возвраты
`python3 scripts/compare_perf.py <report> --budgets design/tech/budgets.md [--prev <прошлый>]`. FAIL PF2 → ADR в `gd:tech-design` (пересмотр бюджета), `asset-integrate` (сжатие, атласы, LOD) или `gd:scope-check`. PF3 — найди коммит-виновника по `build` прошлого отчёта.
