# Соглашение FMOD: нейминг и формат карты событий

Свой документ. Формат таблицы общий с `gd-build` (скрипт `event_map_to_fmod.py` читает ту же таблицу). Меняешь колонки — меняй оба скрипта.

## Пути

| Объект | Шаблон | Пример |
|---|---|---|
| Событие | `event:/<Category>/<Subcategory>/<Name>` | `event:/SFX/Player/Jump` |
| Категории | `SFX` · `UI` · `Music` · `Amb` · `VO` · `Stinger` | |
| Шина | `bus:/<Name>` (группа под Master) | `bus:/SFX` |
| Снапшот | `snapshot:/<State>` | `snapshot:/Pause` |
| Банк | `bank:/<Name>`: `Master` + по сцене или контенту | `bank:/Level01` |

- Сегменты пути — `PascalCase`, только `[A-Za-z0-9]`. Глубина 2–3 сегмента после категории.
- Имя — действие или предмет, без номеров вариаций: вариации живут внутри события (multi instrument), а не как `Jump2`.
- VO: `event:/VO/<Character>/<LineId>`, где `LineId` — ID строки из Ink (`#id:` тег), или одно событие `event:/VO/Dialogue` с programmer sound и ключом строки.

## Параметры

| Тип | Нейминг | Пример |
|---|---|---|
| Локальный (на событии) | `snake_case` | `speed`, `surface`, `charge` |
| Глобальный | префикс `g_` | `g_intensity`, `g_health` |
| Диапазон | всегда указан | `speed(0..10)` |
| Labeled | значения через `/` | `surface[grass/stone/water]` |

Запись в колонке Params: `speed(0..10), surface[grass/stone/water]`.

## Шины по умолчанию

`bus:/Music` · `bus:/SFX` · `bus:/UI` · `bus:/VO` · `bus:/Amb`. Громкость каждой шины — отдельная настройка игрока (доступность).

## Формат event-map.md

```markdown
## Events
| Event | Source | Type | Params | Space | Bus | Priority | Variations | Status |
|---|---|---|---|---|---|---|---|---|
| event:/SFX/Player/Jump | jump#FB1 | oneshot | charge(0..1) | 2D | bus:/SFX | 1 | 3 | todo |
| event:/Music/Level/Main | music:explore | music | g_intensity(0..1) | 2D | bus:/Music | 4 | — | todo |
| snapshot:/Pause | state:pause | snapshot | — | — | — | — | — | todo |
```

- **Source**: `<system>#FB<n>` (строка Feedback GDD) · `<system>#<ID>` (другое правило) · `music:<state>` · `state:<name>` · `ui:<screen>` · `ink:<line_id>` · `amb:<zone>`.
- **Type**: `oneshot` · `loop` · `music` · `amb` · `vo` · `stinger` · `snapshot`.
- **Space**: `2D` · `3D` (3D — мир с позицией; UI, музыка — 2D).
- **Priority**: 1 (всегда слышно, gameplay-critical) … 5 (фон). Используется для лимита голосов и ducking.
- **Variations**: число вариантов внутри события (антиповтор) или `—`.
- **Status**: `todo` · `placeholder` · `done`.

## Как GDD ссылается на событие

В таблице Feedback GDD колонка `Audio (FMOD event)` содержит путь `event:/…` или `—`. Скрипт считает FB-строку «с аудио», если в ней есть `event:/` или слово в колонке аудио не `—`.
