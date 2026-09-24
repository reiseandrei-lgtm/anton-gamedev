---
description: "Звуковые эффекты по карте событий / Design SFX from the event map"
argument-hint: "<event:/…> [ещё события] [путь к Unity-проекту]"
disable-model-invocation: true
---

Используй скилл `sfx-design` для **$ARGUMENTS**

1. Preflight `--for sfx` (ffmpeg, sox). Покажи режим.
2. Прочитай строки карты событий, Feedback GDD и аудио-библию (sonic identity, запреты, Loudness). Покажи план: событие → слои (транзиент / тело / хвост) → вариации → синтез или CC0; дождись «да».
3. Рецепт в `design/audio/sfx-recipes.json`, синтез `sfx-design/scripts/synth_sfx.py`, обработка по `sfx-design/references/sfx-method.md`.
4. Строки в `design/audio/files.md`, затем `sfx-design/scripts/check_audio_files.py`.
5. Итоги: файлы, LUFS и пики, лицензии; «звучание не проверялось» — слушает человек. Следующий шаг — `fmod-sync`.

Язык ответа — язык пользователя.
