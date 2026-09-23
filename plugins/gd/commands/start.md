---
description: Triage игрового проекта по папке design/ и один рекомендованный следующий шаг / Project triage and next step
argument-hint: "[путь к проекту или пусто]"
disable-model-invocation: true
---

Выполни triage игрового проекта по скиллу `gd-router`.

Аргумент (необязательно): $ARGUMENTS — путь к корню игры; по умолчанию текущая папка.

1. Найди `design/`. Если её нет — предложи создать из шаблона и после согласия:
   - если существует `~/.claude/plugins/marketplaces/anton-gamedev/templates/design/` — скопируй его в `./design/`;
   - иначе (например, в Cowork) — создай структуру сам: `pillars.md`, `concept.md`, `systems-map.md`, `scope.md`, `decisions-log.md`, `gdd/`, `narrative/{world.md,voice-pillars.md,characters/,branches/,ink/,continuity/{promises.md,state.md,canon.md}}`, `balance/`, `reviews/`, `handoff/`, `art/{art-bible.md,asset-list.md}`, `audio/{audio-bible.md,event-map.md}`, `ux/{ftue.md,hud.md,accessibility.md}`, `tech/{architecture.md,budgets.md,adr/}`, `qa/{runs/,bugs/}`, `build/`, `playtest/`, `analytics/{events.md,funnels.md}`; в каждом `.md` — frontmatter `status: template` (форматы — в references соответствующих скиллов).
   Затем стадия «Искра» → `gd-concept`.
2. Прочитай frontmatter-статусы и обязательные разделы файлов, не весь текст.
3. Определи стадию по `gd-router/references/pipeline.md` (стадии 0–12 и треки), проверь блокеры (ESCALATE в `reviews/`, системы без столпа, открытые S1/S2 в `qa/bugs/`).
4. Ответь в формате роутера: стадия, что есть, чего не хватает, блокеры, ОДИН следующий шаг (скилл/команда → вход → файл).

Отвечай на языке, на котором пользователь писал в этом разговоре. Художественный текст не пиши.
