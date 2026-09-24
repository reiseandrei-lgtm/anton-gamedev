---
description: "3D-модель в Blender по asset-list / Build a 3D model in Blender from the asset list"
argument-hint: "<asset ID> [путь к Unity-проекту]"
disable-model-invocation: true
---

Используй скилл `model-build` для **$ARGUMENTS**

1. Preflight `--for model`: Blender, Blender MCP. Покажи канал (headless / MCP / plan).
2. Прочитай строку asset-list и роли цветов из art-bible. Покажи спецификацию (габариты, бюджет, роли, LOD); дождись «да».
3. Блокаут и экспорт `model-build/scripts/blender_blockout.py`, доводка формы через MCP или человеком.
4. `model-build/scripts/check_glb.py`, турнтейбл — посмотри на него; вывод в `design/art/models/<ID>/<ID>.md`.
5. Итоги: числа, путь к GLB и турнтейблу, следующий шаг — агент `gd:art-director`, затем `asset-integrate`.

Язык ответа — язык пользователя.
