---
description: "Импортировать ассеты в Unity по asset-list и заменить плейсхолдеры / Import assets and replace placeholders"
argument-hint: "[check | import <ID…> | replace <ID…>] [путь к Unity-проекту] [--stage beta]"
disable-model-invocation: true
---

Используй скилл `asset-integrate`: **$ARGUMENTS**

1. Preflight и проба MCP; glTFast в проекте, если есть GLB.
2. `check` (по умолчанию): `asset-integrate/scripts/check_import.py Assets/_Project --assets design/art/asset-list.md` (+ `--audio design/audio/files.md --audio-root <Unity-проект>`), покажи FAIL/WARN.
3. `import <ID…>`: сверка файла со строкой asset-list и лицензией → копирование → настройки импорта → verify loop → скриншот.
4. `replace <ID…>`: перевод ссылок с плейсхолдера на ассет, скриншот до/после, удаление `ph_` только после проверки.
5. Итоги в числах; Status в asset-list меняет пользователь.

Язык ответа — язык пользователя.
