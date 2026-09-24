# Промпт для новой сессии: волна B (продакшн-цикл anton-gamedev)

Скопируй блок ниже в новую сессию Claude Code, открытую в `D:\Claude Projects\MASTER GDD`.

---

Продолжаем расширение маркетплейса anton-gamedev (плагины `gd` и `gd-build`) до полного цикла. Контекст и договорённости — в `research/2026-09-production-handoff.md` и `research/2026-09-production-cycle-architecture.md` (утверждена, решения a–k по рекомендациям). Прочитай оба файла, `CLAUDE.md` и `examples/one-tap-slice/RESULTS.md` (раздел «Волна A») до любых изменений.

## Правила (коротко, полностью — в CLAUDE.md и архитектуре §1)
- SKILL.md ≲ 60 строк, триггеры RU + EN + «Не для …», пары в `tools/trigger_cases.md`; проверки — Python stdlib, коды FAIL/WARN.
- Только бесплатные инструменты; запрещены Coplay `generate_*` и группа `asset_gen`, Blender MCP `create_rodin_job` / `create_hunyuan_job` / `download_sketchfab_model`, Suno, ElevenLabs, Meshy, MusicGen, Stable Audio Open.
- Телеметрия инструментов выключена (`DISABLE_TELEMETRY=true`).
- «Не проверено» — всё, что не запускалось вживую. Ничего не ставь и не качай без моего «да» (дай источник, размер, команду). Push, мёрж и тег — только после моего «да».

## Изменения плана относительно прошлой сессии
1. **Короче шаги.** Каждый скилл: SKILL.md + references + скрипт + фикстуры + тест → один живой прогон → коммит. Живой прогон — минимальный, доказывающий. Побочные расследования больше 15 минут — стоп, запиши в «Открытое» и иди дальше.
2. **Волна B делится на две части по готовности инструментов:**
   - **B1 (инструменты уже есть):** `perf-check` (Unity + manage_profiler; soak — с `--baseline` простоя), `build-release` (Windows и Android: модуль Android теперь стоит; GameCI-workflow — только файл и проверка, без секретов), `anim-build` (процедурный путь в Unity: пружины, Animation Rigging; риг в Blender — план), `model-build` (Blender 5.2.2 в `D:\Blender`; без Blender MCP — headless `blender --background --python` для блокаута и экспорта GLB + `check_glb.py`; через MCP — после установки), `preflight.py` (поиск Blender в `D:\Blender` и Steam, ffmpeg, sox, FluidSynth, SoundFont, FMOD), агент `art-director` (турнтейблы).
   - **B2 (нужны ffmpeg, sox, FluidSynth, SoundFont):** `sfx-design`, `music-build`. Если к началу B2 не установлено — делаем в режиме plan со скриптами на stdlib (LUFS по BS.1770, запись MIDI, проверка петель) и пометкой «не проверено».
3. **Точки остановки:** после B1 и после B2 — diff-сводка и результаты проверок, затем моё «да» на PR. Версии: B1 и B2 вместе — gd 0.6.0, gd-build 0.3.0 (одна ветка `feat/production-wave-B`, коммиты по скиллам).
4. **Волна C** — отдельной сессией.

## Первые шаги
1. `git status`, ветки. Ветка `feat/production-wave-A` не запушена: покажи мне `git log main..feat/production-wave-A --oneline` и результаты `claude plugin validate` ×3, `python tools/check_plugins.py`, `python -m unittest tools/test_scripts.py`. Жди «да» на PR / rebase-мёрж / тег `v0.5.0`.
2. Проверка окружения одной таблицей (что стоит, что работает): Unity + лицензия, MCP-сервер и мост, FMOD Studio, Blender (`D:\Blender\blender.exe`), Blender MCP, ffmpeg, sox, FluidSynth, SoundFont, FMOD for Unity, `git lfs install`. Для недостающего — команды (winget ID проверены: `Gyan.FFmpeg.Essentials`, `ChrisBagwell.SoX`; FluidSynth — zip с GitHub Releases v2.6.1; FluidR3_GM — `pianobooster/fluid-soundfont` v3.1, 141.5 MB, MIT).
3. После мёржа A — ветка `feat/production-wave-B` от `main`, начинаем B1.

## Окружение
- MCP-сервер: `DISABLE_TELEMETRY=true uvx --from mcpforunityserver==10.2.0 mcp-for-unity --transport http --http-host 127.0.0.1 --http-port 8080` (в фоне); CLI: `uvx -q --from mcpforunityserver==10.2.0 unity-mcp --format json raw <tool> '<json>'`.
- Unity-проект `D:\Unity\Projects\one-tap-slice` (свой git), редактор `D:\Unity\Unity Hub\6000.3.24f1\Editor\Unity.exe`, мост стартует сам.
- FMOD: `D:\FMOD\FMOD Studio 2.03.14\fmodstudiocl.exe`, проект `D:\FMOD\Projects\one-tap-slice`.
- Ответ — по-русски, отчёт после каждой части: что сделано (файлы) · что проверено и чем (числа) · что не проверено и почему · вопросы · следующий шаг.
