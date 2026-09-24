# Фикстуры

## Синтетические (негативные случаи)
Имитируют вывод Unity и FMOD Studio с заранее заложенными ошибками — каждый скрипт `gd-build` обязан их поймать:

- `TestResults/editmode-results.xml` — NUnit 3 XML в формате Unity Test Framework: 5 тестов, 1 падение (T-spark-02); T-ID из `[Property("TID", …)]` и из имени метода.
- `TestResults/empty-results.xml` — прогон, выполнивший 0 тестов (должен дать FAIL / exit 3).
- `fmod/GUIDs.txt` — экспорт GUIDs FMOD Studio: нет `event:/Amb/Sky/Wind`, есть лишнее `event:/SFX/Player/Jump2`.

## Волны B и C (2026-09-24, `tools/test_scripts.py` → `WaveB`, `WaveC`)
Позитивная и негативная фикстура на каждый скрипт. WAV и GLB здесь не лежат — их собирают хелперы теста (`wav`, `float_wav`, `gltf_model`) во временной папке; позитивные данные примера (`design/`) не трогаются.

| Папка | Скрипт | Позитив | Негатив |
|---|---|---|---|
| `levels/` | `check_level.py` | `opening.md` — гейт с ключом на своей ветке | `broken.md` — LV1, LV2, LV3 (гейт без ключа), LV4, LV5; `softlock.md` — ключ только за своим гейтом |
| `release/` | `check_release_plan.py` | `ok/` | `bad/` — RP1–RP4 |
| `loc/` | `check_loc.py` | `ok/` — CSV en/ru, UXML, C#, Ink с `#id` | `bad/` — LC1–LC5, строки Ink без `#id` |
| `analytics/` | `gen_analytics.py`, `check_analytics_calls.py` | `ok/RunTelemetry.cs`, `events-types.md` (enum, ключевое слово C#) | `bad/` — AN1–AN4; `events-bad.md` — неразобранный параметр и PII |
| `perf/` | `compare_perf.py` | `2026-09-24-android.md` + `--prev 2026-09-20-android.md` | `2026-09-24-editor-bad.md` — PF1–PF4 |
| `release-project/` | `check_release.py` | `ok/` | `bad/` — RL1–RL6 (см. README папки) |
| `models/` | `check_glb.py` | `asset-list.md` + GLB из теста | GLB из теста — GL1–GL9, не-GLB |
| `audio/` | `check_audio_files.py`, `loudness.py` | `ok/files.md` | `bad/files.md` — AF1–AF6, float-WAV |
| `music/` | `check_music.py` | `ok.md` | `bad.md` — MU1–MU6 |

## Живые (`live/`, 2026-09-24)
Настоящий вывод инструментов на этом примере, без правок:

- `live/TestResults/editmode-results.xml`, `playmode-results.xml` — Unity 6000.3.24f1, headless `run-tests-headless.ps1` на Unity-проекте слайса `first-hop` (сам проект — вне репозитория). EditMode 11/11; PlayMode 7/9 (5 своих + 4 теста пакета Input System из `testables`, 2 из них пропущены самим пакетом).
- `live/fmod/GUIDs.txt` — FMOD Studio 2.03.14, `fmodstudiocl -script gd_sync_event_map.cli.js` на пустом проекте: 8 событий, 1 снапшот, 4 шины, 3 параметра, мастер-банк.
