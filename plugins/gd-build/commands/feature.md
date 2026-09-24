---
description: "Реализовать систему из GDD в Unity: тест первым, verify loop, лог по R/F/E / Implement a GDD system in Unity"
argument-hint: "<system> [путь к Unity-проекту] [--milestone <имя>]"
disable-model-invocation: true
---

Используй скилл `feature-build` для системы **$ARGUMENTS**

1. Preflight: `slice-build/scripts/preflight.py <unity-проект> --design design`, затем проба MCP (инструменты или CLI `unity-mcp`). Покажи режим (live / plan).
2. Нет `design/gdd/<system>.md` с ID → стоп, предложи `/gd:gdd <system>`. Нет кейсов системы в тест-плане → предложи `/gd:qa-plan` и спроси, продолжать ли.
3. Покажи план задач по R / F / E и ED системы до первой правки проекта и дождись «да».
4. Выполняй по `feature-build/references/feature-method.md`: тесты первыми (красный прогон в лог), verify loop после каждой задачи, максимум 3 fix-цикла.
5. Пиши `design/build/<system>.log.md` по ходу.
6. В конце: diff → `/gd-build:review <system>` (агент `code-reviewer`), затем `slice-build/scripts/check_build_log.py`.
7. Итоги в числах, открытые вопросы к дизайнеру. Следующий шаг — `/gd-build:test`.

Никогда не вызывай платные инструменты MCP (`generate_*`, группа `asset_gen`, Unity AI). Язык ответа — язык пользователя.
