# Музыка: cue-лист → MIDI → FluidSynth → стемы → FMOD

Источники: sirruf/music-gen-skill (MIT) — маршрут MIDI → FluidSynth → WAV (идея; `render.sh` не копировался, `mido` заменён записью SMF на stdlib); FluidSynth (LGPL-2.1) — внешняя программа; FluidR3_GM (MIT, Frank Wen) — SoundFont.

## 1. Из библии в cue
`audio-bible.md` → «Music by state» (состояние, поведение, триггер, переход, FMOD-параметр), sonic identity (инструменты и запреты), Loudness. На состояние — cue (одно cue может обслуживать несколько состояний через параметр или снапшот). Решения: темп (BPM), размер, тональность, число тактов петли (4 / 8 / 16), стемы = слои, которыми управляет параметр интенсивности (`g_intensity`: 0 — пэд, 1 — пэд + колокольчики).

## 2. Cue в JSON (`design/audio/music/<cue>.json` игры)
Формат — docstring `scripts/midi_write.py`, пример — `references/cue-example.json`. Программы — General MIDI (0-based); ударные — канал 9. Одна дорожка = один стем. `repeat_bars` — паттерн повторяется до конца cue. Ноты пишешь ты по гармонии и ритму из библии; это набросок / плейсхолдер, главную тему делает человек 🟨.

## 3. Рендер
1. `python3 scripts/midi_write.py <cue>.json <mid-dir> --stems` — общий `.mid` (для прослушивания) и по `.mid` на стем.
2. `python3 scripts/render_cue.py <cue>.json <mid-dir> <audio-dir> --lufs <Integrated библии> --ceiling -1` — FluidSynth → WAV 48 кГц 16 бит стерео, длина ровно `bars × такт` сэмплов, хвост ревёрба сложен в начало (бесшовная петля), одно усиление на все стемы (баланс сохраняется). Стингер / переход — `--no-fold`.
3. Слушает человек: шов петли, баланс, «то ли настроение». Скилл пишет «звучание не проверялось».

## 4. `design/audio/music-cues.md` (общий формат; шаблон — `templates/design/audio/music-cues.md`)
```markdown
## Cues
| Cue | State | BPM | Meter | Key | Bars | Loop (samples) | Stems | Transition |
|---|---|---|---|---|---|---|---|---|
| run_main | run, dead | 90 | 4/4 | D major | 4 | 512000 | Assets/_Project/Audio/Music/run_main_pad.wav, …_bells.wav | in: 0.5 s fade on bar; dead: snapshot 0.3 s |
```
Loop = round(48000 × 60 / BPM × долей в такте × Bars). Transition — длина (s / bars / beats) и точка синхронизации (on bar / on beat / immediate). Каждый стем — строка `files.md` (Event — музыкальное событие, Variation — имя стема, Source `synth`, Author `render_cue.py`).

## 5. FMOD
Музыкальное событие с multi-track: дорожка на стем, громкость дорожки стема интенсивности — автоматизация от параметра `g_intensity`; loop region на длину Loop; transition markers по Transition. Делает `fmod-sync` (импорт файлов + скрипт), в FMOD Studio проверяется `fmodstudiocl -build`.

## 6. SoundFont
По умолчанию FluidR3_GM (MIT). Другой SoundFont — `--soundfont` или `SOUNDFONT`; лицензию проверяет человек до использования в релизе (у многих бесплатных — только некоммерческое использование).
