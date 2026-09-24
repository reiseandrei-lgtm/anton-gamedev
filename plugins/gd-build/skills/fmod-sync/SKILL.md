---
name: fmod-sync
description: >-
  Перенос карты событий из design/audio/event-map.md в FMOD Studio и Unity: генерация JS-скрипта для FMOD Studio (папки, события, параметры, шины, снапшоты — идемпотентно), C#-класса констант путей событий, чеклиста интеграции FMOD for Unity; сверка «карта ↔ проект FMOD» по экспорту GUIDs. Опционально — напрямую через бесплатный FMOD Studio MCP, если подключён.
  Триггеры RU: «перенеси события в FMOD», «создай события FMOD», «синхронизируй FMOD», «подключи FMOD к Unity», «константы событий FMOD».
  Triggers EN: "sync FMOD events", "create FMOD events", "FMOD Unity integration", "generate FMOD event constants".
  Не для решения, какие звуки нужны (gd:audio-direction), не для Unity AudioMixer (официальный Unity Plugin).
---

# fmod-sync

Ты переносишь решённое в `design/audio/event-map.md` в FMOD Studio и код, не меняя самих решений. Звук не создаёшь и не оцениваешь: файлы готовит человек, `sfx-design` или `music-build` (`design/audio/files.md`), ты раскладываешь их по событиям.

## Вход
`design/audio/event-map.md` (формат — `gd: audio-direction/references/fmod-conventions.md`), путь к проекту FMOD Studio (`.fspro`), путь к Unity-проекту. Нет карты → стоп, предложи `/gd:audio events <slice>`.

## Алгоритм (детали и чеклист — `references/fmod-integration.md`)
1. `python3 scripts/event_map_to_fmod.py design/audio/event-map.md --out design/audio/build [--files design/audio/files.md --audio-root <Unity-проект>]` (на Windows `python`) → `event-map.json`, `gd_sync_event_map.js` (+ `.cli.js`), `FmodEvents.cs`. FAIL в выводе → сначала `/gd:audio check`.
2. **FMOD Studio**:
   - есть бесплатный FMOD Studio MCP → выполни те же операции через него (создать папки, события, шины, снапшоты, параметры; существующее не трогать);
   - FMOD Studio закрыт → headless: `fmodstudiocl -script design/audio/build/gd_sync_event_map.cli.js <проект>.fspro` (синхронизирует, назначает события в банки из колонки `Bank`, кладёт файлы из `files.md` на мастер-трек — 1 файл SingleSound, несколько MultiSound; событие со своим звуком не трогает; сохраняет, пишет `<проект>/Build/GUIDs.txt`);
   - FMOD Studio открыт → положи `gd_sync_event_map.js` в папку `Scripts` рядом с `.fspro`, пользователь делает Scripts → Reload → Scripts → gd → Sync event map и сохраняет проект. Строки «ВРУЧНУЮ» в консоли FMOD — в чеклист.
3. **Сверка**: `python3 scripts/diff_fmod.py design/audio/build/event-map.json <fmod>/Build/GUIDs.txt` (после headless-запуска файл уже есть; из GUI — File → Export GUIDs). D1 (нет в FMOD или событие вне банка) — повторить шаг 2; D2 (лишнее в FMOD) — решение пользователя. Сборка банков: `fmodstudiocl -build -platforms Desktop <проект>.fspro`.
4. **Unity**: пакет FMOD for Unity (скачивание — шаг человека) импортируй и настрой без редактора: `python3 scripts/fmod_unity_setup.py <Unity-проект> --fspro <проект>.fspro --gitignore` (staging, путь к проекту Studio, кэш банков; редактор открыт → Setup Wizard вручную). `FmodEvents.cs` → `Assets/_Project/Scripts/Audio/`; чеклист FMOD for Unity (listener, загрузка банков, вызовы по константам). С Unity MCP — проверить компиляцию verify loop'ом (`../slice-build/references/verify-loop.md`).
5. Плейсхолдеры: для событий со Status `todo` — `../slice-build/scripts/gen_sfx.py` (stdlib), файлы с префиксом `ph_`, строки в `files.md` со статусом `ph`.
6. **hook** (после подключения FMOD for Unity и на каждом билде): `python3 scripts/check_fmod_calls.py <Unity-проект>/Assets --map design/audio/build/event-map.json` — FH1 строковый путь события в C# (FAIL) · FH2 событие не вызывается (WARN) · FH3 `FmodEvents.cs` расходится с картой (FAIL) · FH4 `CreateInstance` без `release()` (WARN).

## Выход
Сгенерированные файлы в `design/audio/build/`, `FmodEvents.cs` в Unity-проекте, отчёт в ответе: сколько создано, что вручную, результат diff. Status в event-map меняет только пользователь.

## Done
`diff_fmod.py` без D1; `check_fmod_calls.py` без FAIL; `FmodEvents.cs` компилируется (или помечено «не проверено в редакторе»); ручные шаги перечислены.

## Правила
Язык ответа = язык запроса. FMOD Studio бесплатен по Indie-лицензии в её пределах (условия — fmod.com); платные сервисы генерации звука не предлагать. Сгенерированный JS запускался на FMOD Studio 2.03.14 через `fmodstudiocl` (идемпотентен; банки, импорт файлов и MultiSound; `diff_fmod` PASS; банки собираются); `fmod_unity_setup.py` проверен на свежем клоне (Unity 6000.3.24f1, FMOD for Unity 2.03.14). Запуск из меню GUI и вызовы `RuntimeManager` в play mode не проверены. Первый запуск на своём проекте — под git или на копии.
