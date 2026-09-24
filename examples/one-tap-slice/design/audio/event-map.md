---
status: draft
updated: 2026-09-23
owner: example
---

# FMOD event map — Lantern Hop

## Events
| Event | Source | Type | Params | Space | Bus | Bank | Priority | Variations | Status |
|---|---|---|---|---|---|---|---|---|---|
| event:/SFX/Player/Charge | hop#FB1 | loop | charge(0..1) | 2D | bus:/SFX | Master | 3 | — | todo |
| event:/SFX/Player/Jump | hop#FB2 | oneshot | charge(0..1) | 2D | bus:/SFX | Master | 1 | 2 | todo |
| event:/SFX/Player/Land | hop#FB3 | oneshot | — | 2D | bus:/SFX | Master | 1 | 4 | todo |
| event:/SFX/Player/Fall | hop#FB4 | oneshot | — | 2D | bus:/SFX | Master | 1 | — | todo |
| event:/SFX/Pickup/Spark | spark#FB1 | oneshot | tier[single/double] | 2D | bus:/SFX | Master | 2 | 3 | todo |
| event:/UI/Record/New | spark#FB2 | stinger | — | 2D | bus:/UI | Master | 2 | — | todo |
| event:/Music/Run/Main | music:run | music | g_intensity(0..1) | 2D | bus:/Music | Music | 5 | — | todo |
| event:/Amb/Sky/Wind | amb:sky | amb | — | 2D | bus:/Amb | Master | 5 | — | todo |
| snapshot:/Dead | state:dead | snapshot | — | — | — | — | — | — | todo |
