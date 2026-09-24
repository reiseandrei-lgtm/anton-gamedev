---
description: Перенести карту событий в FMOD Studio и Unity, сверить / Sync the event map to FMOD Studio and Unity
argument-hint: "[sync | diff <GUIDs.txt> | unity <путь к Unity-проекту> | hook <путь к Unity-проекту>]"
disable-model-invocation: true
---

Используй скилл `fmod-sync`: **$ARGUMENTS**

1. Нет `design/audio/event-map.md` → стоп, предложи `/gd:audio events <slice>`.
2. `sync` (по умолчанию): `scripts/event_map_to_fmod.py design/audio/event-map.md --out design/audio/build` (+ `--files design/audio/files.md --audio-root <Unity-проект>`, если файл есть). Есть бесплатный FMOD Studio MCP → операции через него; FMOD Studio закрыт → `fmodstudiocl -script design/audio/build/gd_sync_event_map.cli.js <проект>.fspro`; открыт → скопировать `gd_sync_event_map.js` в папку `Scripts` проекта FMOD, Scripts → Reload → Scripts → gd → Sync event map, сохранить.
3. `diff <GUIDs.txt>`: `scripts/diff_fmod.py design/audio/build/event-map.json <GUIDs.txt>` (после headless — `<проект>/Build/GUIDs.txt`).
4. `unity <путь>`: скопировать `FmodEvents.cs` в `Assets/_Project/Scripts/Audio/`, пройти чеклист из `fmod-sync/references/fmod-integration.md`, с MCP — проверить компиляцию.
5. `hook <путь>`: `scripts/check_fmod_calls.py <путь>/Assets --map design/audio/build/event-map.json` — строковые пути, неподключённые события, расхождение констант.
6. Покажи, что создано, что сделать вручную, результат сверки.

Язык ответа — язык пользователя.
