# Формат лога сборки: design/build/<slice>.log.md

Свой документ. Лог читают `qa-run` (что проверять), `playtest` (какой билд) и `gd-router` (стадия 9 завершена?).

```markdown
---
status: draft          # draft — в работе, review — все MUST закрыты или помечены
updated: YYYY-MM-DD
slice: <slice>
mode: live             # live — через MCP, plan — без MCP (ничего не проверено в редакторе)
unity: 6000.x.yf1
mcp: CoplayDev/unity-mcp <версия> | none
build: <git commit>
---
# Build log — <slice>

## Engineering Done
| ED | Статус | Доказательство | Задачи |
|---|---|---|---|
| ED1 | ✅ | EditMode 6/6 (T-jump-01…06), smoke OK 240 кадров, screenshots/boot.png | 1, 2 |
| ED3 | ⛔ | не выполнено: нет решения по двойному прыжку (вопрос в handoff) | — |
| ED4 | ⚠️ | реализовано, не проверено в редакторе (mode: plan) | 5 |

## Tasks
| # | Задача | Модуль | Тесты | Итог | fix-циклов |
|---|---|---|---|---|---|

## Placeholders
| Что | Чем подменено | Как отличить в билде |
|---|---|---|

## Deviations from handoff  (решает дизайнер)
| Что в хендоффе | Что сделано | Почему |
|---|---|---|

## Verify summary
Компиляция: DLL новее исходников (время) · Консоль: 0 ошибок, N предупреждений · EditMode a/b · PlayMode c/d · Smoke: … · Скриншоты: пути и что на них видно.

## Open issues
Стоп-факторы после 3 fix-циклов: ошибка дословно, что пробовали, гипотеза.
```

Правила:
- ✅ только с доказательством (тест, скриншот, лог). ⚠️ — сделано, но не проверено. ⛔ — не сделано, с причиной.
- В режиме `plan` ни одного ✅: максимум ⚠️.
- Скриншоты — в `design/build/<slice>/screenshots/`.

## Лог системы: design/build/<system>.log.md (feature-build, juice-build, ui-build)

ОБЩИЙ формат: пишут `feature-build`, `juice-build`, `ui-build`; читают `qa-run`, `gd-router`, `scripts/check_build_log.py`, `juice-build/scripts/check_juice.py`. Меняешь колонки — меняй во всех.

```markdown
---
status: draft
updated: YYYY-MM-DD
system: <system>          # имя файла GDD; для UI — ui
milestone: alpha          # или slice-имя
mode: live                # live | plan
unity: 6000.x.yf1
mcp: CoplayDev/unity-mcp <версия> (tools | cli) | none
build: <git commit Unity-проекта>
---
# Build log — <system>

## Rules
| ID | Статус | Доказательство | Задачи |
|---|---|---|---|
| R1 | ✅ | T-chain-01 зелёный (EditMode) | 1 |
| E2 | ⛔ | не выполнено: в GDD не описано, что при … (вопрос в Open Questions GDD) | — |
| ED-chain-1 | ✅ | EditMode 6/6, smoke: 20 фонарей без неизбежного промаха | 1–3 |

## Juice            (juice-build)
| FB | Событие | Цель (кадры) | Замер (кадры) | Допуск | Звук в том же кадре | Доказательство |
|---|---|---|---|---|---|---|

## Tasks / Deviations from GDD / Verify summary / Open issues — как у лога слайса
```

- `ID` — `R*`, `F*`, `E*` из GDD системы и `ED-<system>-*` из хендоффа майлстоуна. Каждый ID — отдельная строка.
- Красный прогон до реализации записывается в Verify summary («T-chain-01…04: 0/4 до реализации»).
