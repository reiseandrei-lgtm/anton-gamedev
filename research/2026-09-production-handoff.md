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
| Волна C (gd 0.7.0, gd-build 0.4.0) | ✅ смёржено, тег `v0.7.0` (PR #7): `level-design`, `release-plan`, `loc-build`, `analytics-build`. `netcode-build` (C5) не делался |
| Укрепление B и C (gd 0.7.1, gd-build 0.4.1) | ✅ ветка `test/hardening-B-C` (не запушена, ждёт «да» на PR): +26 тестов (63 всего), фикстуры `examples/one-tap-slice/fixtures/`, 3 бага исправлены (`gen_analytics.py` писал неполный файл при ошибке; `check_audio_files.py` и `check_music.py` падали на float-WAV) |

## Первые шаги новой сессии
1. PR `test/hardening-B-C`: после «да» — push, PR, мёрж, тег `v0.7.1`.
2. Live-прогон `loc-build` — отложен по решению пользователя (пакет уже стоит): коллекция `UI`, импорт CSV, привязки `LocalizedString`, Pseudo-Locale, скриншоты; сверить имена колонок CSV-расширения с `loc-method.md`.
3. По желанию: вставить вызовы аналитики в one-tap-slice (`/gd-build:analytics wire`), EditMode-тест бэкенда, JSONL в play mode.
4. Живые прогоны волны B: серия профайлера `perf-check`, сборка игрока `build-release`, импорт стемов и SFX в FMOD.

## Окружение (проверено 2026-09-24)
- Unity 6000.3.24f1 (`D:\Unity\Unity Hub`), лицензия Personal активна; проект `D:\Unity\Projects\one-tap-slice` (свой git, последний коммит `5c6c0fe` — установлен `com.unity.localization` 1.5.8). `PlayerSettings.runInBackground = 1`.
- unity-mcp 10.2.0: сервер `DISABLE_TELEMETRY=true uvx --from mcpforunityserver==10.2.0 mcp-for-unity --transport http --http-host 127.0.0.1 --http-port 8080`; CLI `uvx -q --from mcpforunityserver==10.2.0 unity-mcp --format json raw <tool> '<json>'`. Мост стартует сам (`Assets/_Project/Editor/McpSessionBoot.cs`).
- FMOD Studio 2.03.14 (`D:\FMOD\FMOD Studio 2.03.14`, `fmodstudiocl.exe`), проект `D:\FMOD\Projects\one-tap-slice` (свой git).
- Blender 5.2.2 (winget, `D:\Blender\blender.exe`) и 5.2.1 (Steam). Android Build Support (SDK, NDK, OpenJDK) установлен.
- Установлено 2026-09-24: ffmpeg 9.0.1 (winget `Gyan.FFmpeg.Essentials`), SoX 14.4.2 (winget `ChrisBagwell.SoX`), FluidSynth 2.6.1 (`D:\Tools\FluidSynth\…\bin`, в PATH пользователя), FluidR3_GM.sf2 (`D:\Tools\SoundFonts`, `SOUNDFONT`), Blender MCP 2.0.4 (аддон `blender_mcp` в `%APPDATA%\Blender Foundation\Blender\5.2`, сервер `blender` в user-конфиге Claude Code с `DISABLE_TELEMETRY=true`; проверено: сокет 9876 отвечает, `claude mcp list` — Connected); `git lfs` настроен глобально.
- Не установлено: FMOD for Unity (скачивание с fmod.com требует входа — шаг человека).
- Установлено: `com.unity.localization` 1.5.8 в one-tap-slice (коммит `5c6c0fe` в репозитории проекта). Live-прогон `loc-build` на нём не делался — отложен по решению пользователя.
- Промпт волны C — `research/2026-09-wave-C-prompt.md` (выполнен); прошлый — `research/2026-09-next-session-prompt.md`.

## Открытое после укрепления B и C (2026-09-24)
Замечено при написании тестов, не исправлялось: это правила или сообщения скриптов, а не падения. Нужно решение.
- AF5 (`check_audio_files.py`) считает источник `made` внешним: свой файл с `License: own` без URL получает FAIL. В `architecture.md` §4 `made` — собственный ассет, одобренный человеком. Что делать: убрать `made` из внешних или требовать URL/путь исходника.
- LV3 (`check_level.py`): если ключ лежит на связи `optional`, а гейт — на критическом пути, скрипт пишет «goal недостижим». Достижимость считается только по связям `critical`. Соглашение сейчас такое: ветку за ключом помечать `critical`, но в `level-method.md` этого нет. Вариант: дописать это в метод или улучшить сообщение.
- PF4 (`compare_perf.py`): в докстринге обещана проверка «platform не упоминает устройство», в коде — только `editor|редактор`. Строки бюджета с платформой «то же» PF4 пропускает.
- `check_audio_files.py` пишет в шапке «true peak: ffmpeg», даже если `--ffmpeg` указывает на несуществующий файл: пик тогда считается как sample peak. На вердикт это не влияет.
- Правило PII (M5 / AN3) срабатывает на любой `…_name`, в том числе `level_name` и `skin_name`, — возможны ложные FAIL. Правка — сразу в двух плагинах (P9 `LINE_COPIES`).
- `check_release.py`: если `--repo` не предок проекта, `relative_to` выбросит `ValueError`. Видно по коду, тестом не проверялось.
- Тестами не покрыты: `synth_sfx.py`, `render_cue.py`, `midi_write.py`, `blender_blockout.py`; true peak через ffmpeg (в тестах он специально выключен); `check_glb.py` на GLB из Blender с бинарным буфером; режим live в `preflight.py --for model|sfx|music` — зависит от машины, тест проверяет только, что режим согласован со списком «Не хватает».

## Открытое после волны C
- Карточка C4 задавала порядок вех «демо → страница → фест → релиз»; в `check_release_plan.py` — page → demo → fest → release (на Steam демо привязано к странице основной игры). Если нужен другой порядок — поменять `ORDER`.
- ~~Не сработали на данных примера: LV2–LV5, LV3 гейты, LC3–LC5, строки Ink, AN2–AN4~~ — закрыто в 0.7.1: негативные фикстуры и тесты.
- KPI по JSONL (`analytics/<session>.jsonl` → числа KPI из events.md) скриптом не считаются — кандидат в `gd:playtest` или отдельный скрипт.
- `README.md` отставал на волну B — дописан в этой волне.

## Открытое после волны A
- Эталоны `examples/one-tap-slice/design/qa/visual/_pending/` (4 снимка) ждут утверждения человеком.
- Вопросы дизайнеру в `gdd/chain.md` (нижняя граница зазора: минимальный прыжок 1.15 > K1 = 1.0; фонари в кадре).
- Headless-прогон тестов после волны A не делался (редактор был открыт; тесты шли через MCP: EditMode 18/18, PlayMode 13/13).
- Цели в кадрах для hop FB1, FB4, FB5 (JU3) — вопрос в `gd:game-feel`.
