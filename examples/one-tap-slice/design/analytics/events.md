---
status: draft
updated: 2026-09-23
owner: example
---

# Analytics events — Lantern Hop

## Questions
| ID | Вопрос | Откуда |
|---|---|---|
| MQ1 | Делают ли новички первый прыжок без подсказки? | DD1 |
| MQ2 | Связывают ли удержание с дальностью? | DD2 |
| MQ3 | Жмут ли «ещё» сразу после падения? | DD3, north star |

## KPIs
| KPI | Question | Formula (events) | Target | Decision threshold |
|---|---|---|---|---|
| first_jump_time | MQ1 | median(jump_performed.seconds_since_start where jump_index=1) | ≤ 10 s | > 15 s → подсказка-иконка раньше |
| charge_spread | MQ2 | stdev(jump_performed.charge) за первые 5 прыжков | ≥ 0.2 | < 0.1 → игроки не варьируют заряд, переделать L2 |
| retry_time | MQ3 | median(run_started.seconds_since_death where run_index=2) | ≤ 2 s | > 3 s → экран рестарта мешает |

## Events
| Event | Params | Trigger | Serves |
|---|---|---|---|
| session_started | session_index:int, build:string | запуск приложения | first_jump_time |
| jump_performed | jump_index:int, charge:float, seconds_since_start:float, landed:bool | отпускание с прыжком | first_jump_time, charge_spread |
| run_started | run_index:int, seconds_since_death:float | начало забега | retry_time |
| run_ended | run_index:int, score:int, jumps:int | падение | MQ3 |
| spark_collected | value:int, distance:float | сбор искры | MQ2 |
