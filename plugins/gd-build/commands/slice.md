---
description: Собрать играбельный Unity-слайс из хендоффа с verify loop / Build a playable Unity slice from the handoff
argument-hint: "<slice> [путь к Unity-проекту]"
disable-model-invocation: true
---

Используй скилл `slice-build` для слайса **$ARGUMENTS**

1. Preflight: `scripts/preflight.py <unity-project> --design design --slice <slice>` скилла `slice-build` (на Windows `python`), затем одна безопасная проба Unity MCP (чтение консоли или состояния редактора).
2. Покажи режим (live / plan) и чего не хватает. Не хватает хендоффа → стоп. Нет тех-дизайна или тест-плана → предложи `/gd:tech`, `/gd:qa-plan` и спроси, продолжать ли без них.
3. Покажи план задач (MUST → ED) до первой правки проекта и дождись «да».
4. Выполняй по `slice-build/references/verify-loop.md`: тест первым, после каждой задачи verify loop, максимум 3 fix-цикла на проблему.
5. Пиши `design/build/<slice>.log.md` по ходу, а не в конце.
6. В конце: итоги в числах, скриншоты, открытые вопросы к дизайнеру. Следующий шаг — `/gd-build:test smoke <slice>`.

Никогда не вызывай платные инструменты MCP (`generate_*`, Unity AI). Язык ответа — язык пользователя.
