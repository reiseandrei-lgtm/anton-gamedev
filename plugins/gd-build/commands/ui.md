---
description: "Сверстать HUD и экраны на UI Toolkit по ux/hud.md / Build the HUD and screens with UI Toolkit"
argument-hint: "[hud | restart | pause | settings | all] [путь к Unity-проекту]"
disable-model-invocation: true
---

Используй скилл `ui-build`: **$ARGUMENTS**

1. Preflight и проба MCP. Нет `design/ux/hud.md` с колонками Name и Loc key → стоп, предложи `/gd:ux hud`.
2. Покажи план: экраны → элементы (Name, зона, роль цвета, ключ) → разрешения для скриншотов; дождись «да».
3. Тема из арт-библии, UXML/USS по `ui-build/references/ui-method.md`, контроллеры без литералов текста.
4. Verify loop, play mode в нужных состояниях, скриншоты в 2–3 разрешениях (посмотри на каждый).
5. `ui-build/scripts/check_ui.py`, лог `design/build/ui.log.md`.
6. Итоги в числах; элементы, которые не помещаются, — вопрос в `/gd:ux hud`.

Язык ответа — язык пользователя.
