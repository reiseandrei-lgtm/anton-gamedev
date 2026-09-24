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
| Волна B (gd 0.6.0, gd-build 0.3.0) | ✅ смёржено, тег `v0.6.0` (PR #6): `perf-check`, `build-release`, `model-build`, `anim-build`, `sfx-design`, `music-build`, агент `art-director` |
| Волна C (gd 0.7.0, gd-build 0.4.0) | ✅ код на ветке `feat/production-wave-C` (не запушена, ждёт «да» на PR): `level-design`, `release-plan`, `loc-build` (режим plan — пакета Localization нет), `analytics-build`; версии, CHANGELOG, ATTRIBUTION. Скрипты запускались по разу; тесты не писались. `netcode-build` (C5) не делался |

## Первые шаги новой сессии
1. PR `feat/production-wave-C`: после «да» — push, PR, мёрж, тег `v0.7.0`.
2. После «да» на установку `com.unity.localization` в one-tap-slice — live-прогон `loc-build`: коллекция `UI`, импорт CSV, привязки `LocalizedString`, Pseudo-Locale, скриншоты; сверить имена колонок CSV-расширения с `loc-method.md`.
3. По желанию: вставить вызовы аналитики в one-tap-slice (`/gd-build:analytics wire`), EditMode-тест бэкенда, JSONL в play mode; тесты новых скриптов волн B и C в `tools/test_scripts.py` (позитивная и негативная фикстура).
4. Живые прогоны волны B: серия профайлера `perf-check`, сборка игрока `build-release`, импорт стемов и SFX в FMOD.

## Окружение (проверено 2026-09-24)
- Unity 6000.3.24f1 (`D:\Unity\Unity Hub`), лицензия Personal активна; проект `D:\Unity\Projects\one-tap-slice` (свой git, последний коммит `daf5e0b`). `PlayerSettings.runInBackground = 1`.
- unity-mcp 10.2.0: сервер `DISABLE_TELEMETRY=true uvx --from mcpforunityserver==10.2.0 mcp-for-unity --transport http --http-host 127.0.0.1 --http-port 8080`; CLI `uvx -q --from mcpforunityserver==10.2.0 unity-mcp --format json raw <tool> '<json>'`. Мост стартует сам (`Assets/_Project/Editor/McpSessionBoot.cs`).
- FMOD Studio 2.03.14 (`D:\FMOD\FMOD Studio 2.03.14`, `fmodstudiocl.exe`), проект `D:\FMOD\Projects\one-tap-slice` (свой git).
- Blender 5.2.2 (winget, `D:\Blender\blender.exe`) и 5.2.1 (Steam). Android Build Support (SDK, NDK, OpenJDK) установлен.
- Установлено 2026-09-24: ffmpeg 9.0.1 (winget `Gyan.FFmpeg.Essentials`), SoX 14.4.2 (winget `ChrisBagwell.SoX`), FluidSynth 2.6.1 (`D:\Tools\FluidSynth\…\bin`, в PATH пользователя), FluidR3_GM.sf2 (`D:\Tools\SoundFonts`, `SOUNDFONT`), Blender MCP 2.0.4 (аддон `blender_mcp` в `%APPDATA%\Blender Foundation\Blender\5.2`, сервер `blender` в user-конфиге Claude Code с `DISABLE_TELEMETRY=true`; проверено: сокет 9876 отвечает, `claude mcp list` — Connected); `git lfs` настроен глобально.
- Не установлено: FMOD for Unity (скачивание с fmod.com требует входа — шаг человека).
- Не установлено: пакет `com.unity.localization` в one-tap-slice (ждёт «да»).
- Промпт волны C — `research/2026-09-wave-C-prompt.md` (выполнен); прошлый — `research/2026-09-next-session-prompt.md`.

## Открытое после волны C
- Карточка C4 задавала порядок вех «демо → страница → фест → релиз»; в `check_release_plan.py` — page → demo → fest → release (на Steam демо привязано к странице основной игры). Если нужен другой порядок — поменять `ORDER`.
- Не сработали на данных примера (нет нарушений или данных): LV2–LV5 на нарушениях, LV3 гейты, LC3–LC5, строки Ink, AN2–AN4. Негативные фикстуры — вместе с тестами.
- KPI по JSONL (`analytics/<session>.jsonl` → числа KPI из events.md) скриптом не считаются — кандидат в `gd:playtest` или отдельный скрипт.
- `README.md` отставал на волну B — дописан в этой волне.

## Открытое после волны A
- Эталоны `examples/one-tap-slice/design/qa/visual/_pending/` (4 снимка) ждут утверждения человеком.
- Вопросы дизайнеру в `gdd/chain.md` (нижняя граница зазора: минимальный прыжок 1.15 > K1 = 1.0; фонари в кадре).
- Headless-прогон тестов после волны A не делался (редактор был открыт; тесты шли через MCP: EditMode 18/18, PlayMode 13/13).
- Цели в кадрах для hop FB1, FB4, FB5 (JU3) — вопрос в `gd:game-feel`.
