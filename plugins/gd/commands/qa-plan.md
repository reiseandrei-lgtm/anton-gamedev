---
description: Тест-план слайса из GDD и хендоффа с трассировкой покрытия / Test plan with coverage tracing
argument-hint: "<slice> [--review]"
disable-model-invocation: true
---

Используй скилл `qa-plan` для слайса **$ARGUMENTS**

1. Нет `design/handoff/<slice>.md` → сообщи и остановись: тест-план строится от хендоффа.
2. Системы слайса — из раздела Systems хендоффа; прочитай их GDD. Нет стабильных ID (R/F/E) → предупреди, предложи `gdd-author` для простановки ID.
3. Напиши `design/qa/test-plan-<slice>.md` по `qa-plan/references/qa-method.md`.
4. `check_coverage.py design/qa/test-plan-<slice>.md --gdd … --handoff design/handoff/<slice>.md` (на Windows `python`); FAIL исправь до показа.
5. `--review`: вызови субагента **qa-lead**. Передай ТОЛЬКО пути к плану, GDD слайса, хендоффу, путь к скиллу `qa-plan` и дату. Субагенты недоступны → рубрика агента самому, с предупреждением.
6. Следующий шаг: `/gd-build:slice <slice>` (Claude Code + `gd-build`) или `/gd-build:test` по готовому билду.

Язык ответа — язык пользователя.
