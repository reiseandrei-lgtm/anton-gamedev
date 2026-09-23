---
description: FTUE, HUD, доступность / FTUE, HUD, accessibility
argument-hint: "[ftue | hud | a11y] [slice]"
disable-model-invocation: true
---

Используй скилл `ux-onboarding`: **$ARGUMENTS**

1. Режим из аргумента; по умолчанию `ftue`.
2. Нет `design/ux/` → создай из шаблона после подтверждения.
3. `ftue`: спроси целевые времена (первое действие, первое замыкание петли), если их нет в файле. Каждому шагу — событие метрики; предложи передать их в `/gd:metrics`.
4. `hud`: инвентарь информации из GDD; мин. размеры и палитра — из `design/art/art-bible.md`, если есть.
5. `a11y`: чеклист из `ux-onboarding/references/ux-method.md`; цветовые пары — `art-direction/scripts/check_palette.py`.
6. Покажи, что и куда пишешь, до записи.

Язык ответа — язык пользователя. Тексты подсказок — только с `--text`, иначе плейсхолдеры с лимитом символов.
