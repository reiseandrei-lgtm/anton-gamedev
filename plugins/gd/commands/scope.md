---
description: Ревизия скоупа агентом producer / Scope review by the producer agent
argument-hint: "[фича | milestone | пусто = вся игра]"
disable-model-invocation: true
---

Ревизия скоупа: **$ARGUMENTS** (пусто — вся игра).

Вызови субагента **producer** (агент плагина gd) с задачей:
- объект ревизии из аргумента;
- пути: `design/systems-map.md`, `design/scope.md` (baseline, если есть), `design/gdd/`, `design/pillars.md`;
- ресурсы команды — если пользователь их называл в разговоре, передай числа; иначе агент спросит.

Когда агент вернётся — покажи вердикт, итог «оценка vs ресурсы», Must/Should/Cut и порядок вырезания. Решения о вырезании принимает пользователь; после его решения — запись в `design/decisions-log.md`.

Если субагенты недоступны — выполни то же самое сам по скиллу `scope-check`.
