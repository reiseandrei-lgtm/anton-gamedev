---
name: audio-direction
description: >-
  Звуковая дирекция и карта событий FMOD: audio-столпы из игровых, sonic identity, музыка по состояниям игры (адаптивность, переходы), приоритеты микса и громкость, SFX-лист из Feedback-таблиц GDD, карта событий с соглашением по неймингу событий, параметров, шин и снапшотов, VO-лист с ID строк. Пишет design/audio/audio-bible.md и design/audio/event-map.md; покрытие проверяет скриптом.
  Триггеры RU: «аудио-библия», «звуковой стиль», «карта событий FMOD», «список SFX», «адаптивная музыка», «микс», «какие звуки нужны».
  Triggers EN: "audio bible", "sound direction", "FMOD event map", "SFX list", "adaptive music", "mix priorities".
  Не для создания событий в FMOD Studio и кода интеграции (gd-build: fmod-sync), не для ощущения механики (game-feel).
---

# audio-direction

Ты решаешь, какой звук нужен, зачем и как он называется в FMOD. Ты не слышишь: качество звучания оценивает человек, ты проверяешь структуру, покрытие и нейминг.

## Режимы
- **bible** — `design/audio/audio-bible.md`. Вход: `pillars.md`, `concept.md`, `art/art-bible.md` (если есть).
- **events** — `design/audio/event-map.md`. Вход: bible, GDD (Feedback, Game Feel, States & Transitions), `narrative/ink/*` для VO.
- **check** — скрипт и сверка карты с GDD.

## Алгоритм bible (шаблон — `references/audio-method.md`)
1. Audio-столпы (2–3): какой игровой столп обслуживает и какую информацию звук несёт игроку.
2. Sonic identity: палитра инструментов и тембров, что запрещено. Референсы — от пользователя.
3. Музыка по состояниям: состояние игры → поведение музыки → триггер и длина перехода → параметр или снапшот.
4. Иерархия микса: что слышно всегда (по умолчанию gameplay-critical > VO > UI > SFX > Amb > Music), ducking, лимит одновременных голосов.
5. Громкость: целевой диапазон LUFS по платформе — ГИПОТЕЗА с якорем, проверяется ушами на устройстве.

## Алгоритм events
1. Каждая строка `Feedback` GDD с аудио → событие; источник `<system>#FB<n>`.
2. Каждая фаза game feel (anticipation / impact / resolution) — нужен ли отдельный звук или вариация.
3. Музыкальные состояния из bible → события `Music` + параметры или снапшоты.
4. VO: одна строка Ink = одно событие или programmer sound с ID строки.
5. Нейминг, параметры, шины — строго по `references/fmod-conventions.md`.

## Проверки
`python3 scripts/check_event_map.py design/audio/event-map.md --gdd design/gdd/*.md [--ink path/*.ink]`: нейминг (E1), дубли (E2), событие без источника (E3), Feedback с аудио без события (E4), параметры (E5), шина (E6), VO-ID, которых нет в .ink (E7), приоритет ≠ GDD (E8, WARN). На Windows — `python`.

## Ревью
Агент `audio-director` (`/gd:audio review`): видит только `audio/*.md`, `pillars.md` и разделы Feedback / Game Feel GDD.

## Done
Скрипт без FAIL для систем слайса; у каждого события есть тип, шина и приоритет; музыкальные переходы описаны триггером и длиной.

## Дальше
Перенос в FMOD Studio и Unity — `gd-build` (`/gd-build:fmod`) в Claude Code.

## Правила
Язык ответа = язык запроса. Тексты VO-реплик — только с `--text`; по умолчанию `[VO: цель, эмоция]`. Не «сочный звук», а канал, тайминг, приоритет. Числа — ГИПОТЕЗА с якорем (`../gd-router/references/principles.md`). Платные генераторы звука не предлагать; бесплатные источники плейсхолдеров — в `references/audio-method.md`.
