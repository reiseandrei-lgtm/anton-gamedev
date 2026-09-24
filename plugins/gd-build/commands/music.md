---
description: "Музыкальные петли и стемы по состояниям / Music loops and stems per game state"
argument-hint: "[состояние или cue] [путь к Unity-проекту]"
disable-model-invocation: true
---

Используй скилл `music-build` для **$ARGUMENTS**

1. Preflight `--for music` (FluidSynth, SoundFont). Покажи режим.
2. Прочитай «Music by state», sonic identity и Loudness аудио-библии, Music-события карты. Покажи план cue (BPM, размер, тональность, такты, стемы, переход); дождись «да».
3. Cue JSON → `music-build/scripts/midi_write.py --stems` → `music-build/scripts/render_cue.py --lufs …` по `music-build/references/music-method.md`.
4. Строки в `design/audio/music-cues.md` и `files.md`, затем `music-build/scripts/check_music.py`.
5. Итоги: длины петель, LUFS, что слушать человеку (шов петли, баланс). Следующий шаг — `fmod-sync`.

Язык ответа — язык пользователя.
