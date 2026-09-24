---
description: "Процедурная анимация и клипы с замером в кадрах / Procedural animation and clips measured in frames"
argument-hint: "<system или asset ID> [путь к Unity-проекту]"
disable-model-invocation: true
---

Используй скилл `anim-build` для **$ARGUMENTS**

1. Preflight `--for anim` и проба MCP. Покажи режим.
2. Прочитай Game Feel GDD и строки `anim` в asset-list. Движение без цели в кадрах → стоп, предложи `gd:game-feel`.
3. Покажи план: движение → путь (пружина / Animation Rigging / клип) → цель → как замерим; дождись «да».
4. Реализация по `anim-build/references/anim-method.md`, замер PlayMode-тестом или `model-build/scripts/check_glb.py` для клипов.
5. Лог (`## Juice` / `## Anim`), итоги: таблица замеров, что не совпало с целью.

Язык ответа — язык пользователя.
