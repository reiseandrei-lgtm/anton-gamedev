---
description: "Релизная сборка, CI, LFS, SteamPipe / Release build, CI, LFS, SteamPipe"
argument-hint: "<vX.Y.Z> [windows|android] [путь к Unity-проекту]"
disable-model-invocation: true
---

Используй скилл `build-release` для **$ARGUMENTS**

1. Preflight `--for release` и проба MCP. Покажи режим.
2. `build-release/scripts/check_release.py <project> --tag <vX.Y.Z>` → покажи FAIL и план исправлений; правки истории git (`git lfs migrate`) — только после «да».
3. Сборка через MCP или headless по `build-release/references/release-method.md`, запуск билда, строка в `design/release/builds.md`.
4. CI и SteamPipe — файлы из шаблонов и проверка скриптом; секреты, логины, загрузка — чеклист для человека.
5. Итоги: что собрано (путь, размер), что проверено, что ждёт человека.

Язык ответа — язык пользователя.
