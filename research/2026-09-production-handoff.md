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
| Волна A (gd 0.5.0, gd-build 0.2.0) | ✅ код и живой прогон; ветка `feat/production-wave-A` (11 коммитов, **не запушена**). Итоги — `examples/one-tap-slice/RESULTS.md`, «Волна A» |
| Волна B | не начата |
| Волна C | не начата |

## Первые шаги новой сессии
1. Показать пользователю diff-сводку `git log main..feat/production-wave-A` и результаты проверок; PR, rebase-мёрж и тег `v0.5.0` — только после «да».
2. Волна B — ветка `feat/production-wave-B` от `main` после мёржа A: `anim-build`, `model-build`, `sfx-design`, `music-build`, `perf-check`, `build-release`, `preflight.py` (Blender, ffmpeg, sox, FluidSynth, SoundFont, FMOD), агент `art-director` (турнтейблы). Карточки скиллов — архитектура §3, волна B. Версии: gd 0.6.0, gd-build 0.3.0.
3. Для живого прогона волны B пользователь ставит ffmpeg, sox, FluidSynth + FluidR3_GM, Blender MCP (команды — отчёт фазы 0). Без них — режим plan и «не проверено».

## Окружение (проверено 2026-09-24)
- Unity 6000.3.24f1 (`D:\Unity\Unity Hub`), лицензия Personal активна; проект `D:\Unity\Projects\one-tap-slice` (свой git, последний коммит `daf5e0b`). `PlayerSettings.runInBackground = 1`.
- unity-mcp 10.2.0: сервер `DISABLE_TELEMETRY=true uvx --from mcpforunityserver==10.2.0 mcp-for-unity --transport http --http-host 127.0.0.1 --http-port 8080`; CLI `uvx -q --from mcpforunityserver==10.2.0 unity-mcp --format json raw <tool> '<json>'`. Мост стартует сам (`Assets/_Project/Editor/McpSessionBoot.cs`).
- FMOD Studio 2.03.14 (`D:\FMOD\FMOD Studio 2.03.14`, `fmodstudiocl.exe`), проект `D:\FMOD\Projects\one-tap-slice` (свой git).
- Blender 5.2.2 (winget, `D:\Blender\blender.exe`) и 5.2.1 (Steam). Android Build Support (SDK, NDK, OpenJDK) установлен.
- Не установлено: Blender MCP, ffmpeg, sox, FluidSynth, SoundFont, FMOD for Unity; `git lfs install` не выполнен.
- Промпт следующей сессии — `research/2026-09-next-session-prompt.md` (изменённый план: B1 / B2).

## Открытое после волны A
- Эталоны `examples/one-tap-slice/design/qa/visual/_pending/` (4 снимка) ждут утверждения человеком.
- Вопросы дизайнеру в `gdd/chain.md` (нижняя граница зазора: минимальный прыжок 1.15 > K1 = 1.0; фонари в кадре).
- Headless-прогон тестов после волны A не делался (редактор был открыт; тесты шли через MCP: EditMode 18/18, PlayMode 13/13).
- Цели в кадрах для hop FB1, FB4, FB5 (JU3) — вопрос в `gd:game-feel`.
