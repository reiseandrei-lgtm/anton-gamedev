---
status: draft
updated: 2026-09-23
owner: example
engine: Unity 6000.0
platform: mobile
slice: first-hop
---

# Architecture — Lantern Hop

## Modules
| Module | Systems | Depends on | Notes |
|---|---|---|---|
| Core | — | — | время, события, сохранения |
| Hop | hop | Core | логика заряда и прыжка — чистые классы |
| Spark | spark | Core, Hop | слушает событие приземления |
| Presentation | — | Hop, Spark | камера, VFX, звук, HUD |

## Config map
| Knob | Config asset | Field | Type | Range |
|---|---|---|---|---|
| hop#K1 | HopConfig | minDistance | float | 0.5..1.5 |
| hop#K2 | HopConfig | chargeTime | float | 0.5..1.2 |
| hop#K3 | HopConfig | maxDistance | float | 3..6 |
| hop#K4 | HopConfig | landingTolerance | float | 0.2..0.6 |
| hop#K5 | HopConfig | restartDelay | float | 0.1..0.6 |
| hop#K6 | HopConfig | minCharge | float | 0..0.15 |
| spark#K1 | SparkConfig | farThreshold | float | 2.5..3.5 |
| spark#K2 | SparkConfig | farMultiplier | int | 2..3 |
| spark#K3 | SparkConfig | sparkChance | float | 0.2..0.5 |

## State & save
| Что | Сохраняем? | Где | Когда пишем | Версия |
|---|---|---|---|---|
| рекорд | да | JSON в persistentDataPath | при конце забега, если счёт > рекорда | `version: 1` |
| текущий забег | нет | — | — | — |
Ошибка записи → лог, рекорд в памяти (spark#E3).

## Scenes & flow
Boot → Run (одна сцена, рестарт без перезагрузки сцены — пересоздание цепочки фонарей).

## Test seams
| Правило | Где проверяется | Нужное свойство / точка |
|---|---|---|
| hop#R2, hop#F1, hop#F2 | EditMode: `HopLogic` | — |
| hop#R4 | EditMode: `HopLogic.IsLanding(distance, gap)` | — |
| hop#R1, hop#R5 | PlayMode + InputTestFixture | `PlayerHop.State` (read-only) |
| spark#F1, spark#R3 | EditMode: `SparkScore` | — |
| spark#R3 (сохранение) | EditMode: `RecordStore` с подменой файловой системы | интерфейс `IRecordStorage` |

## Audio integration
Presentation вызывает события по `FmodEvents`; `charge` передаётся из `PlayerHop.Charge` каждый кадр при заряде.

## Open questions
- Нужна ли генерация фонарей с гарантией достижимости? (сейчас расстояние ≤ maxDistance − допуск)
