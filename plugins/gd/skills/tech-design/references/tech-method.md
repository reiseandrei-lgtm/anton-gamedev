# Технический дизайн: шаблоны

> Приём «read-only свойства состояния для тестов и проб» — из unity-kit `unity-playtest` (MIT © 2026 Benjamin Curlier), см. ATTRIBUTION.md. Остальное своё: config map, связь с ID GDD, формат ADR.

## 1. architecture.md

Скрипт читает разделы `## Modules` и `## Config map`.

```markdown
---
status: draft
updated: YYYY-MM-DD
owner:
engine: Unity 6000.x
platform: mobile          # mobile | pc | both
slice: <slice>
---
# Architecture — <Game>

## Modules
| Module | Systems | Depends on | Notes |
|---|---|---|---|
| Core | — | — | время, события, сервис-локатор |
| Jump | jump | Core | |

## Config map
| Knob | Config asset | Field | Type | Range |
|---|---|---|---|---|
| jump#K1 | JumpConfig | jumpHeight | float | 1..4 |

## State & save
| Что | Сохраняем? | Где | Когда пишем | Версия |
|---|---|---|---|---|
Миграция: …

## Scenes & flow
Boot → … Что живёт между сценами: …

## Test seams
| Правило | Где проверяется | Нужное свойство / точка |
|---|---|---|
| jump#R1 | EditMode: JumpLogic | — |
| jump#R3 | PlayMode | `PlayerJump.IsGrounded` (read-only) |

## Audio integration
Кто вызывает события FMOD (система / компонент), откуда берутся параметры. Ссылка на `audio/event-map.md`.

## Open questions
```

Правила:
- Модуль = asmdef. `Depends on` — только модули из этой таблицы. Циклов нет (скрипт).
- Логика правил — в чистых C#-классах без `MonoBehaviour` там, где возможно: тогда она проверяется EditMode-тестом за миллисекунды.
- Компоненты отдают состояние через read-only свойства (`public bool IsGrounded => grounded;`): так его видят PlayMode-тесты и MCP-пробы, не лезя в приватные поля рефлексией.
- Knob в коде литералом — ошибка: всё, что крутит дизайнер, живёт в конфиге.

## 2. budgets.md

```markdown
| Метрика | Бюджет | Платформа / устройство | Якорь | Как замерить | Сигнал для изменения |
|---|---|---|---|---|---|
| Кадр | 16.6 ms (60 fps) | mid Android | … | Profiler, 60 с игры | стабильно > 14 ms → резать |
```

Стартовые якоря (ГИПОТЕЗА, заменить замером на своём устройстве):
- Мобайл средний: 30 или 60 fps по жанру; batches ≤ 100–150; RAM приложения ≤ 1 ГБ; стартовый APK/AAB ≤ 150 МБ (лимит базового модуля Google Play — проверить актуальный).
- PC: 60 fps на min-spec, заданном пользователем.
- Троттлинг мобильных: замер после 10 минут игры, не на холодном устройстве.

## 3. ADR (adr/NNN-<topic>.md)

```markdown
---
status: draft      # draft | accepted | superseded
updated: YYYY-MM-DD
---
# ADR-NNN: <решение>
## Context
## Options
| Вариант | Плюсы | Минусы | Стоимость |
## Decision
## Consequences
## Revisit when
```

## 4. Частые ошибки
Архитектура «на вырост» для mechanic-слайса · синглтоны вместо явных зависимостей там, где нужен тест · сохранения без версии · бюджеты без устройства · Addressables и DI-фреймворк в прототипе без причины.
