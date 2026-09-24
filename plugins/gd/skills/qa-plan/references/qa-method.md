# QA: тест-план, severity, баг-репорт

> Идея классов тестов (логика / интеграция / визуал / UI) — из Claude-Code-Game-Studios `qa-plan` (MIT © 2026 Donchitos); «0 тестов = провал» и «тест сначала для бага» — из unity-kit `unity-verify`, `unity-ci` (MIT © 2026 Benjamin Curlier). См. ATTRIBUTION.md. Трассировка по ID GDD, формат плана и баг-репорта — свои.

## 1. test-plan-<slice>.md

Скрипт читает таблицы с колонками `ID` и `Covers` и раздел `## Smoke`.

```markdown
---
status: draft
updated: YYYY-MM-DD
owner:
slice: <slice>
---
# Test plan — <slice>

## Scope
Системы: jump, … · Хендофф: handoff/<slice>.md · Вне плана: …

## Cases
| ID | Covers | Type | Priority | Given | When | Then | Auto |
|---|---|---|---|---|---|---|---|
| T-jump-01 | jump#R1, ED2 | editmode | P1 | на земле | Jump() | vy = sqrt(2·g·h), h = jump#K1 | yes |
| T-jump-02 | jump#E1 | playmode | P2 | в воздухе | тап | второй прыжок не происходит | yes |
| T-jump-10 | DD1 | playtest | P1 | новичок | первая минута | прыгает без подсказки | no |

## Smoke
1. Билд запускается, первая сцена за ≤ N с
2. …

## Severity
S1 блокер · S2 ломает гипотезу/ED · S3 заметно, есть обход · S4 косметика

## Open questions
```

- **ID**: `T-<system>-NN` (`system` — имя файла GDD или `slice` для сквозных тестов). ID не переиспользуется.
- **Covers**: через запятую `<system>#R1`, `<system>#E2`, `<system>#F1`, `<system>#FB2`, `ED3` (или `ED-<system>-3` в майлстоуне), `DD1`, `budgets#B1`.
- **Type**: `editmode` · `playmode` · `visual` · `perf` · `manual` · `playtest`.
- **Auto**: `yes` — для editmode / playmode / visual / perf.
- **visual**: в Given — сцена, камера, seed, разрешение; в Then — допуск (`diff ≤ 0.5 % пикселей`). Эталон — `design/qa/visual/<ID>.png`, его утверждает человек; до утверждения снимок лежит в `qa/visual/_pending/`.
- **perf**: Covers — строка бюджета `budgets#B1`; в Given — платформа, сцена, длительность (мобайл — после 10 минут игры); в Then — порог из бюджета.
- **manual** для визуала допустим только с причиной в строке: `manual: <почему скриншот не годится>` (анимация во времени, звук, ощущение). Иначе `check_coverage.py` даёт Q9.

В коде тестов ID ставится так, чтобы `gd-build` сопоставил результат: имя метода `T_jump_01_…` или `[NUnit.Framework.Property("TID", "T-jump-01")]` (полное имя: в Unity `Property` конфликтует с `UnityEngine.PropertyAttribute`). `[Category("T-jump-01")]` не годится: NUnit запрещает «-» в категориях, и тест падает, не начавшись.

## 2. Какой тип выбрать

| Что проверяем | Тип | Почему |
|---|---|---|
| Формула, правило без сцены | editmode | миллисекунды, детерминированно |
| Переход состояний в компоненте, таймер, физика | playmode | нужен цикл кадров |
| Ввод (тап, клавиша) доходит до геймплея | playmode + `InputTestFixture` | единственный надёжный способ симулировать ввод |
| Кадр, который можно снять: состояние экрана, HUD, эффект в фиксированный момент | visual | скриншот сравнивается с эталоном (`gd-build: qa-run visual`) |
| Строка бюджета (кадр, память, batches, загрузка) | perf | замер против `tech/budgets.md` (`gd-build: perf-check`, `qa-run soak`) |
| Движение во времени, звук, вёрстка «на глаз» | manual (+ «manual: причина») | глазами и ушами |
| «Понятно», «приятно», «хочется ещё» (DD) | playtest | только люди |

## 3. Правила хороших тестов
- Один тест — одна причина упасть.
- Ожидаемое — число с допуском или конкретное состояние.
- Для каждого бага — сначала падающий тест, потом фикс.
- Прогон, в котором выполнилось 0 тестов, — провал, а не «зелёный».
- Тест, который не падает, если сломать правило, бесполезен: мысленно сломай правило и проверь, что тест упадёт.

## 4. Баг-репорт (qa/bugs/BUG-NNN.md)

```markdown
---
status: open        # open | fixed | wontfix | duplicate
severity: S2
found: YYYY-MM-DD
build: <commit / build id>
covers: jump#R1, T-jump-01
---
# BUG-NNN: <что сломано, одной фразой>
## Steps
1. …
## Expected
## Actual
## Evidence
лог / скриншот / тест
## Notes
частота (всегда / 1 из N), платформа
```

Баг, который оказался дырой дизайна (edge case не описан), — не баг кода: ссылка на GDD и `gdd-author --quick`.
