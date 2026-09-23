---
description: Аудио-библия, карта событий FMOD, проверка покрытия / Audio bible, FMOD event map, coverage check
argument-hint: "[bible | events <slice> | check | review]"
disable-model-invocation: true
---

Используй скилл `audio-direction`: **$ARGUMENTS**

1. Режим из аргумента; по умолчанию: нет `design/audio/audio-bible.md` или он `template` → `bible`, иначе `check`.
2. Нет `design/audio/` → создай из шаблона после подтверждения.
3. `events <slice>`: читай Feedback, Game Feel, States GDD систем слайса; VO — `narrative/ink/`. Нейминг — `audio-direction/references/fmod-conventions.md`.
4. `check`: `check_event_map.py design/audio/event-map.md --gdd design/gdd/*.md [--ink …]` (на Windows `python`).
5. `review`: вызови субагента **audio-director**. Передай ТОЛЬКО пути к `design/audio/*.md`, `design/pillars.md`, GDD слайса, путь к скиллу и дату. Субагенты недоступны → рубрика агента самому, с предупреждением.
6. Следующий шаг после `events`: в Claude Code с плагином `gd-build` — `/gd-build:fmod`.

Язык ответа — язык пользователя. Тексты VO — только с `--text`.
