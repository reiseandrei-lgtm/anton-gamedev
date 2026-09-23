---
status: draft
updated: 2026-09-23
slice: first-hop
mode: plan
unity: не найден (нет Unity-проекта и редактора на машине примера)
mcp: none
build: —
---

# Build log — first-hop

> Режим **plan**: preflight не нашёл ни Unity-проекта, ни редактора, ни MCP. Ниже план и чеклист. Ни один пункт не проверен в редакторе, поэтому ✅ нет.

## Engineering Done
| ED | Статус | Доказательство | Задачи |
|---|---|---|---|
| ED1 | ⚠️ | не проверено в редакторе: нужен билд на mid Android + T-slice-01 | 9 |
| ED2 | ⚠️ | не проверено в редакторе: T-hop-01…10 спроектированы, не запускались | 2, 3, 4 |
| ED3 | ⚠️ | не проверено в редакторе: T-spark-01…04 | 5 |
| ED4 | ⚠️ | не проверено в редакторе: T-hop-10 | 6 |
| ED5 | ⚠️ | не проверено в редакторе: T-spark-05, T-slice-03 | 7 |

## Tasks
| # | Задача | Модуль | Тесты | Итог | fix-циклов |
|---|---|---|---|---|---|
| 1 | Проект Unity 6 URP, asmdef Core/Hop/Spark/Presentation, тестовые asmdef, Input System, Test Framework | — | — | план | — |
| 2 | `HopConfig` (SO) по Config map, `HopLogic`: F1, F2, R4 | Hop | T-hop-01…05 (тест первым) | план | — |
| 3 | `PlayerHop`: состояния Idle/Charging/Airborne/Falling/Dead, read-only `State`, `Charge` | Hop | T-hop-06…09 (InputTestFixture) | план | — |
| 4 | Генерация цепочки фонарей: расстояние ≤ maxDistance − допуск | Hop | новый тест (см. Deviations) | план | — |
| 5 | `SparkConfig`, `SparkScore` F1, R1–R3 | Spark | T-spark-01…04 | план | — |
| 6 | Рестарт без перезагрузки сцены, задержка K5 | Hop | T-hop-10 | план | — |
| 7 | `RecordStore` + `IRecordStorage` (ADR-001) | Core | T-spark-05 | план | — |
| 8 | Presentation: примитивы цветов ролей, FB1–FB5 визуально, `FmodEvents` вызовы | Presentation | smoke 2–5 | план | — |
| 9 | Android-билд, профайлинг | — | T-slice-01 | план | — |

## Placeholders
| Что | Чем подменено | Как отличить в билде |
|---|---|---|
| персонаж, фонари, искры | капсула, цилиндры, ромбы цветов ролей палитры | метка `PLACEHOLDER` в углу |
| SFX | `gen_sfx.py`: ph_jump, ph_land, ph_fail (проверено: файлы генерируются) | префикс `ph_` |

## Deviations from handoff  (решает дизайнер)
| Что в хендоффе | Что сделано | Почему |
|---|---|---|
| генерация фонарей не описана | правило «расстояние ≤ maxDistance − допуск» в задаче 4 | иначе возможен неизбежный промах; нужен R в GDD hop и тест |

## Verify summary
Не выполнялось: нет Unity. Следующий шаг после установки Unity 6 + CoplayDev/unity-mcp — `/gd-build:slice first-hop` в режиме live.

## Open issues
- Нужен ли R7 «гарантия достижимости» в GDD hop — вопрос дизайнеру.
