---
status: review
updated: 2026-09-24
system: hop
milestone: alpha
mode: live
unity: 6000.3.24f1
mcp: CoplayDev/unity-mcp 10.2.0 (cli)
build: Unity-проект one-tap-slice, после aad5c12 (juice-build)
---
# Build log — hop (Alpha: отклик)

Правила hop R1–R6, F1–F2, E1–E5 закрыты в слайсе: `build/first-hop.log.md` (ED2). Здесь — только критерий майлстоуна ED-hop-1 и отклик.

## Rules
| ID | Статус | Доказательство | Задачи |
|---|---|---|---|
| ED-hop-1 | ✅ | T-hop-21 и T-hop-22 зелёные (PlayMode, captureFramerate 60); таблица Juice ниже | 1, 2 |

## Juice
| FB | Событие | Цель (кадры) | Замер (кадры) | Допуск | Звук в том же кадре | Доказательство |
|---|---|---|---|---|---|---|
| FB2 | прыжок: squash | 1 | 1 | 0 | да (плейсхолдер AudioSource ph_jump в Jumped) | T-hop-21: squash 1 fr, начало +0 fr после прыжка |
| FB2 | прыжок: stretch | 2 | 2 | 0 | — | T-hop-21: stretch 2 fr |
| FB3 | приземление: пыль | ≤ 0 | 0 | 0 | да (ph_land в Landed) | T-hop-22: пыль +0 fr, 12 частиц |
| FB1 | заряд: фонарь разгорается | — | 0 | 0 | нет (событие Charge — loop в FMOD, FMOD for Unity не подключён) | кадр заряда виден в qa/visual/_pending/ (T-hop-20 не снят) |
| FB4 | падение: затемнение | — | 0 | 0 | да (ph_fail в FallStarted) | T-hop-24: снимок экрана рестарта с затемнением |
| FB5 | экран рестарта: пульс | — | 0 | 0 | — | USS transition 0.25 s, ручная проверка T-hop-25 |

## Tasks
| # | Задача | Модуль | Тесты | Итог | fix-циклов |
|---|---|---|---|---|---|
| 1 | `JuiceConfig` (SO, свой файл) + `PlayerJuice`: squash/stretch по кадрам в LateUpdate, пыль Emit в обработчике Landed | Presentation | T-hop-21, T-hop-22 | ✅ | 1 (формула замера давала «+1 кадр» — фаза читается кадром позже) |
| 2 | Подключение в GameBootstrap | Presentation | smoke | ✅ | 0 |

## Deviations from GDD
- Цели в кадрах есть только у FB2 («squash → stretch 2 кадра») и FB3 («пыль в кадр касания»). FB1, FB4, FB5 — без числа в Game Feel GDD (JU3): вопрос в `gd:game-feel`.

## Verify summary
Компиляция доказана · консоль 0 ошибок · PlayMode 9/9 своих · скриншот кадра импакта не снят отдельно (есть T-hop-24 — затемнение).
