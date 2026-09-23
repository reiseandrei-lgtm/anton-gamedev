---
description: Арт-библия, список ассетов, проверка палитры / Art bible, asset list, palette check
argument-hint: "[bible | assets <slice> | check | review]"
disable-model-invocation: true
---

Используй скилл `art-direction`: **$ARGUMENTS**

1. Режим из аргумента; по умолчанию: нет `design/art/art-bible.md` или он `template` → `bible`, иначе `check`.
2. Нет `design/art/` → создай из шаблона (`templates/design/art/` маркетплейса или по `art-direction/references/art-method.md`) после подтверждения.
3. `bible`: нужны `pillars.md` в `draft`+ и референсы от пользователя — если их нет, спроси и остановись.
4. `assets <slice>`: читай GDD систем слайса и `design/handoff/<slice>.md`; список конечный, у каждой строки источник.
5. `check`: `check_palette.py` и `check_assets.py --handoff … --gdd …` (на Windows `python`); покажи FAIL и WARN с предложениями.
6. `review`: вызови субагента **art-director**. Передай ТОЛЬКО пути к `design/art/*.md`, `design/pillars.md`, скриншотам (если пользователь их дал), путь к скиллу `art-direction` и сегодняшнюю дату. Без пересказа разговора. Субагенты недоступны → примени рубрику агента сам и предупреди, что ревью не изолировано.

Язык ответа — язык пользователя. Художественные описания — только с `--text`.
