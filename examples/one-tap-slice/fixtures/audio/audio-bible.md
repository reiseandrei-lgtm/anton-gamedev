---
status: draft
updated: 2026-09-24
owner: example
---

# Audio bible — фикстура check_audio_files.py и check_music.py

## Format
Все файлы — WAV 48 kHz, 16 bit.

## Music by state
| Game state | Music behavior | Trigger | Transition | FMOD |
|---|---|---|---|---|
| run | пэд | старт забега | 0.5 s | — |
| dead | пэд тише | падение | 0.3 s | — |

## Loudness
| Платформа | Integrated | True peak | Якорь | Когда менять |
|---|---|---|---|---|
| mobile | −16 LUFS | −1 dBTP | фикстура | — |
