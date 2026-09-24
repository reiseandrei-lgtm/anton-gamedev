---
status: review
updated: 2026-09-24
system: chain
milestone: alpha
mode: live
unity: 6000.3.24f1
mcp: CoplayDev/unity-mcp 10.2.0 (cli)
build: aad5c12 (+ правки после ревью; локальный git Unity-проекта, вне репозитория)
---
# Build log — chain

## Rules
| ID | Статус | Доказательство | Задачи |
|---|---|---|---|
| R1 | ✅ | T-chain-01 зелёный (EditMode) | 1 |
| R2 | ✅ | T-chain-02 зелёный: 10 000 зазоров в [1, 3.65], среднее 2.325 ± 0.05 | 1 |
| R3 | ✅ | T-chain-03 зелёный: maxGap 5 → 3.65 | 1 |
| R4 | ✅ | T-chain-05 (EditMode) и T-chain-11 (PlayMode, 12 прыжков в сцене) зелёные | 1, 3 |
| R5 | ✅ | T-chain-06 зелёный: seed 42 → одинаковые позиции и искры | 1 |
| F1 | ✅ | T-chain-02 зелёный | 1 |
| E1 | ✅ | T-chain-03 зелёный + ожидаемое предупреждение `[chain#E1]` | 1 |
| E2 | ✅ | T-chain-04 зелёный + ожидаемое предупреждение `[chain#E2]` | 1 |
| E3 | ✅ | T-chain-07 зелёный | 1 |
| ED-chain-1 | ✅ | EditMode 7/7 (T-chain-01…07) | 1 |
| ED-chain-2 | ✅ | T-chain-08 зелёный: позиции в сцене = ChainGenerator(seed 42); своей генерации в GameBootstrap нет (diff) | 2 |
| ED-chain-3 | ⚠️ | снимки seed 42 детерминированы (diff двух снимков 0 %), эталон ещё не утверждён человеком — `qa/visual/_pending/` | 4 |

## Tasks
| # | Задача | Модуль | Тесты | Итог | fix-циклов |
|---|---|---|---|---|---|
| 1 | `ChainConfig` (SO) по Config map, `ChainGenerator` (чистый класс) | Chain | T-chain-01…07: красный 0/7 → зелёный 7/7 | ✅ | 0 |
| 2 | GameBootstrap строит цепочку через ChainGenerator; seam `UseConfigs(…, seed)` | Presentation | T-chain-08 | ✅ | 2 (см. ниже) |
| 3 | Ревью кода → T-chain-11, фонари дочерние к GameBootstrap | Presentation, тесты | T-chain-11 | ✅ | 0 |
| 4 | Детерминированный кадр старта для эталона | — | T-chain-09 (visual) | ⚠️ | 0 |

## Deviations from GDD
Нет. Вопросы дизайнеру из ревью — в Open Questions `gdd/chain.md` (нижняя граница зазора, фонари в кадре).

## Verify summary
Компиляция: все Game.* DLL новее исходников после каждой задачи · Консоль: 0 ошибок (кроме внутреннего «On demand scheduler requested to import while stopped» при старте редактора) · Красный прогон до реализации: T-chain-01…07 — 0/7 (NotImplementedException) · EditMode 18/18 · PlayMode 7/7 своих · Ревью кода: CONCERNS (`reviews/2026-09-24-code-chain.md`).

Fix-циклы задачи 2:
1. `ChainConfig` лежал в `ChainGenerator.cs` → ассет без скрипта, `Resources.Load` → null, NRE в `ChainGenerator..ctor`. Класс ScriptableObject перенесён в `ChainConfig.cs`, ассет пересоздан через MCP.
2. После NRE тест оставлял объекты, их `Update` ронял соседний T-hop-10 → `[UnityTearDown]` с уборкой.

## Open issues
- Ревью кода, находка 4: фонари и материалы не освобождаются за забег (рост объектов) — проверяется soak (`qa/perf/2026-09-24-soak-*.md`).
