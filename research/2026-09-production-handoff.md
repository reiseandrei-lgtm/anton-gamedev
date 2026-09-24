---
status: draft
updated: 2026-09-24
owner: Anton
---

# Передача между сессиями: продакшн-цикл

Задача целиком — промпт пользователя (фазы 0–3, волны A–C). Архитектура утверждена: `research/2026-09-production-cycle-architecture.md` (решения a–k — по рекомендациям).

## Где мы
| Фаза | Статус |
|---|---|
| 0 Окружение | ✅ |
| 1 Живая проверка gd-build | ✅ смёржено, тег `v0.4.1` (PR #4) |
| 2 Архитектура | ✅ утверждена |
| Волна A (gd 0.5.0, gd-build 0.2.0) | ✅ смёржено, тег `v0.5.0` |
| Волна B1 | ✅ код на ветке `feat/production-wave-B` (7 коммитов, не запушена): `perf-check`, `build-release`, `model-build`, `anim-build`, `preflight.py --for`, агент `art-director`. Скрипты запускались один раз на данных примера; тесты в `tools/test_scripts.py` и живые прогоны в Unity по просьбе пользователя не делались |
| Волна B2 | ✅ код на той же ветке (не запушен): `sfx-design`, `music-build`; версии gd 0.6.0, gd-build 0.3.0, CHANGELOG. Скрипты запускались по разу (синтез, LUFS против ffmpeg, MIDI → FluidSynth → стемы → `check_music` PASS); тесты не писались |
| Волна C | не начата — отдельной сессией |

## Первые шаги новой сессии
1. PR #6 (`feat/production-wave-B`, B1 + B2): после «да» — push коммитов B2, мёрж, тег `v0.6.0`.
2. По желанию: тесты новых скриптов в `tools/test_scripts.py` (позитивная и негативная фикстура на каждый) и живые прогоны: серия профайлера `perf-check`, сборка игрока `build-release`, импорт стемов и SFX в FMOD.
3. Волна C (`level-design`, `release-plan`, `loc-build`, `analytics-build`) — отдельной сессией, промпт — `research/2026-09-wave-C-prompt.md`.

## Окружение (проверено 2026-09-24)
- Unity 6000.3.24f1 (`D:\Unity\Unity Hub`), лицензия Personal активна; проект `D:\Unity\Projects\one-tap-slice` (свой git, последний коммит `daf5e0b`). `PlayerSettings.runInBackground = 1`.
- unity-mcp 10.2.0: сервер `DISABLE_TELEMETRY=true uvx --from mcpforunityserver==10.2.0 mcp-for-unity --transport http --http-host 127.0.0.1 --http-port 8080`; CLI `uvx -q --from mcpforunityserver==10.2.0 unity-mcp --format json raw <tool> '<json>'`. Мост стартует сам (`Assets/_Project/Editor/McpSessionBoot.cs`).
- FMOD Studio 2.03.14 (`D:\FMOD\FMOD Studio 2.03.14`, `fmodstudiocl.exe`), проект `D:\FMOD\Projects\one-tap-slice` (свой git).
- Blender 5.2.2 (winget, `D:\Blender\blender.exe`) и 5.2.1 (Steam). Android Build Support (SDK, NDK, OpenJDK) установлен.
- Установлено 2026-09-24: ffmpeg 9.0.1 (winget `Gyan.FFmpeg.Essentials`), SoX 14.4.2 (winget `ChrisBagwell.SoX`), FluidSynth 2.6.1 (`D:\Tools\FluidSynth\…\bin`, в PATH пользователя), FluidR3_GM.sf2 (`D:\Tools\SoundFonts`, `SOUNDFONT`), Blender MCP 2.0.4 (аддон `blender_mcp` в `%APPDATA%\Blender Foundation\Blender\5.2`, сервер `blender` в user-конфиге Claude Code с `DISABLE_TELEMETRY=true`; проверено: сокет 9876 отвечает, `claude mcp list` — Connected); `git lfs` настроен глобально.
- Не установлено: FMOD for Unity (скачивание с fmod.com требует входа — шаг человека).
- Промпт следующей сессии — `research/2026-09-wave-C-prompt.md` (волна C; прошлый — `research/2026-09-next-session-prompt.md`).

## Открытое после волны A
- Эталоны `examples/one-tap-slice/design/qa/visual/_pending/` (4 снимка) ждут утверждения человеком.
- Вопросы дизайнеру в `gdd/chain.md` (нижняя граница зазора: минимальный прыжок 1.15 > K1 = 1.0; фонари в кадре).
- Headless-прогон тестов после волны A не делался (редактор был открыт; тесты шли через MCP: EditMode 18/18, PlayMode 13/13).
- Цели в кадрах для hop FB1, FB4, FB5 (JU3) — вопрос в `gd:game-feel`.
