---
status: draft
updated: 2026-09-24
owner: example
audio_root: unity-project   # пути колонки File — от корня Unity-проекта
---

# Audio files — Lantern Hop

<!-- Общий формат (sfx-design, music-build → fmod-sync, asset-integrate). Меняешь колонки — меняй во всех. -->

| File | Event | Variation | Source | License | URL | Author | LUFS | Peak | Status |
|---|---|---|---|---|---|---|---|---|---|
| Assets/_Project/Resources/Audio/ph_jump.wav | event:/SFX/Player/Jump | 1 | synth | own | — | gen_sfx.py | — | — | ph |
| Assets/_Project/Resources/Audio/ph_land.wav | event:/SFX/Player/Land | 1 | synth | own | — | gen_sfx.py | — | — | ph |
| Assets/_Project/Resources/Audio/ph_fail.wav | event:/SFX/Player/Fall | 1 | synth | own | — | gen_sfx.py | — | — | ph |
| Assets/_Project/Resources/Audio/ph_confirm.wav | event:/SFX/Pickup/Spark | single | synth | own | — | gen_sfx.py | — | — | ph |
| Assets/_Project/Resources/Audio/ph_coin.wav | event:/SFX/Pickup/Spark | double | synth | own | — | gen_sfx.py | — | — | ph |
