---
name: music-build
description: >-
  Музыка по состояниям игры: cue-лист → MIDI (запись на Python stdlib) → рендер FluidSynth с GM SoundFont → стемы точной длины петли с бесшовным хвостом → музыкальное событие FMOD с параметром интенсивности; длины петель, стемы, громкость и переходы проверяются скриптом.
  Триггеры RU: «сделай музыку», «музыкальная петля», «музыкальная тема для», «отрендери стемы», «адаптивный трек».
  Triggers EN: "compose music for", "music loop", "render stems", "make the music".
  Не для музыкальной дирекции и состояний (gd:audio-direction), не для SFX (sfx-design), не для событий в FMOD Studio (fmod-sync).
---

# music-build

Ты делаешь музыкальные петли и стемы под состояния из аудио-библии и доказываешь длину, стемы и громкость числами. Звучание не оцениваешь: слушает человек. Главная тема — hero-ассет 🟨, ты делаешь только набросок.

## 0. Preflight
`python3 ../slice-build/scripts/preflight.py --for music`: FluidSynth и SoundFont. Нет → режим plan: cue JSON и `.mid` (stdlib), без WAV, ⚠️.

## 1. Вход
`design/audio/audio-bible.md` (Music by state, sonic identity, Loudness), `design/audio/event-map.md` (Music-события, параметры), `design/audio/music-cues.md` (если есть).

## 2. Алгоритм (детали — `references/music-method.md`)
1. Cue на каждое состояние: BPM, размер, тональность, такты, стемы по слоям интенсивности, переход. Покажи план до нот.
2. `design/audio/music/<cue>.json` (пример — `references/cue-example.json`) → `python3 scripts/midi_write.py <cue>.json <mid-dir> --stems`.
3. `python3 scripts/render_cue.py <cue>.json <mid-dir> <audio-dir> --lufs <Integrated библии>`.
4. Строка в `design/audio/music-cues.md` (Loop — из вывода рендера), стемы — в `design/audio/files.md`.
5. `python3 scripts/check_music.py design/audio/music-cues.md --bible design/audio/audio-bible.md --files design/audio/files.md --root <unity-project>`.
6. Событие FMOD с multi-track и `g_intensity` — `fmod-sync`.

## Done
`check_music.py` без FAIL; каждое состояние библии покрыто cue; стемы одной длины = Loop; `.mid` и JSON лежат рядом с WAV (пересборка детерминирована).

## Правила
Язык ответа = язык запроса. Не использовать MusicGen, Suno, Stable Audio и другие генераторы с платным доступом или некоммерческими весами. SoundFont кроме FluidR3_GM — только после проверки лицензии человеком.
