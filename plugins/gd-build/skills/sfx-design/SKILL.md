---
name: sfx-design
description: >-
  Звуковые эффекты по карте событий FMOD: рецепт из слоёв (транзиент, тело, хвост), синтез с вариациями и seed на Python stdlib, обработка sox и ffmpeg, бесплатные CC0-источники; манифест design/audio/files.md, формат, громкость по BS.1770, пики и лицензии проверяются скриптом.
  Триггеры RU: «сделай звук для», «звуковой эффект», «вариации звука», «синтезируй SFX», «найди CC0-звук».
  Triggers EN: "make a sound for", "design the SFX", "sound variations", "synthesize SFX".
  Не для решения, какие звуки нужны (gd:audio-direction), не для музыки (music-build), не для событий в FMOD Studio (fmod-sync).
---

# sfx-design

Ты делаешь файлы для событий, которые уже есть в карте, и доказываешь формат, громкость и лицензию числами. Звучание не оцениваешь: слушает человек, в отчёте — «звучание не проверялось».

## 0. Preflight
`python3 ../slice-build/scripts/preflight.py --for sfx`: ffmpeg и sox. Без них синтез и LUFS работают (stdlib), но нет обработки и true peak — пометка «sample peak».

## 1. Вход
`design/audio/event-map.md` (события, Source FB, Variations), `design/audio/audio-bible.md` (sonic identity, запреты, Loudness, SFX rules), Feedback GDD по Source, `design/audio/files.md`.

## 2. Алгоритм (детали — `references/sfx-method.md`)
1. На событие — три слоя (транзиент / тело / хвост) под Feedback и sonic identity; покажи план до синтеза.
2. Рецепт в `design/audio/sfx-recipes.json` игры (пример — `references/recipes-example.json`).
3. `python3 scripts/synth_sfx.py design/audio/sfx-recipes.json <audio-dir> <имя> --variations <из карты> --seed <S> --lufs <цель>`; обработка sox/ffmpeg — по §3 метода.
4. Или CC0-файл: страница, лицензия, автор — в манифест.
5. Строки в `design/audio/files.md` (LUFS, Peak — из вывода скрипта).
6. `python3 scripts/check_audio_files.py design/audio/files.md --map design/audio/event-map.md --bible design/audio/audio-bible.md --root <unity-project>`.
7. Импорт в FMOD — `fmod-sync` (импорт файлов по `files.md`).

## Done
`check_audio_files.py` без FAIL для событий задачи; файлов = вариаций карты; у внешних — лицензия и URL; статус не выше `todo` (final ставит человек).

## Правила
Язык ответа = язык запроса. Не использовать Suno, ElevenLabs, MusicGen, AudioGen и другие генераторы с платным доступом или некоммерческими весами. CC-BY — только по решению человека. Громкость микса — шины FMOD, не перегруз файлов.
