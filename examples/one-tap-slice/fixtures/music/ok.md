---
status: draft
updated: 2026-09-24
owner: example
---

# Music cues — позитивная фикстура check_music.py

<!-- Стемы создаёт tools/test_scripts.py (хелпер wav): 120 BPM, 4/4, 1 такт = 96000 сэмплов при 48 кГц. -->

## Cues
| Cue | State | BPM | Meter | Key | Bars | Loop (samples) | Stems | Transition |
|---|---|---|---|---|---|---|---|---|
| mus_run_main | run | 120 | 4/4 | Am | 1 | 96000 | Music/mus_run_pad.wav, Music/mus_run_bells.wav | 0.5 s fade, на следующий такт |
| mus_dead | dead | 120 | 4/4 | Am | 1 | 96000 | Music/mus_dead_pad.wav | 1 bar, на долю |
