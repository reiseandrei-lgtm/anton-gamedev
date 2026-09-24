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
| Укрепление B и C (gd 0.7.1, gd-build 0.4.1) | ✅ смёржено, тег `v0.7.1` (PR #8): +26 тестов (63 всего), фикстуры `examples/one-tap-slice/fixtures/`, 3 бага исправлены (`gen_analytics.py` писал неполный файл при ошибке; `check_audio_files.py` и `check_music.py` падали на float-WAV) |
| Решения по «Открытому» B и C (gd 0.7.2, gd-build 0.4.2) | ✅ ветка `fix/open-items-B-C` (ждёт «да» на PR) |

## Первые шаги новой сессии
1. PR `fix/open-items-B-C`: после «да» — push, PR, мёрж, тег `v0.7.2`.
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

## Решено после укрепления B и C (2026-09-24, 0.7.2)
- AF5: `made` — свой файл (как в `architecture.md` §4). Внешними считаются `cc0`, `external` и лицензия, отличная от own; URL нужен только им.
- LV3: если цель достижима только через `optional`, скрипт пишет, какие именно связи мешают, и просит пометить их `critical`. Соглашение дописано в `level-method.md`. Уровень FAIL не изменился.
- PF4: докстринг приведён к коду (проверяется только editor/редактор). Эвристика «platform не упоминает устройство» отклонена: слишком много ложных срабатываний.
- `check_audio_files.py`: если `--ffmpeg` указывает на несуществующий файл, шапка пишет «нет ffmpeg — sample peak».
- `check_release.py`: если проект не внутри `--repo`, скрипт выходит с кодом 2 и понятным сообщением вместо `ValueError`.
- Правило PII (M5 / AN3) оставлено строгим: `…_name` — FAIL. Ложное срабатывание обходится переименованием (`level_id`); пропущенные персональные данные обойти нельзя.

## Открытое
- Тестами не покрыты: `synth_sfx.py`, `render_cue.py`, `midi_write.py`, `blender_blockout.py`; true peak через ffmpeg; `check_glb.py` на GLB из Blender с бинарным буфером; режим live в `preflight.py --for model|sfx|music` (зависит от машины).

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
