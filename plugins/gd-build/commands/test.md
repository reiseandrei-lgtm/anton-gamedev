---
description: Прогнать тесты и smoke Unity-проекта, завести баги / Run Unity tests and smoke, file bugs
argument-hint: "[suite | smoke | input | bug] <slice> [путь к Unity-проекту]"
disable-model-invocation: true
---

Используй скилл `qa-run`: **$ARGUMENTS**

1. Режим из аргумента; по умолчанию `suite`.
2. Проба Unity MCP. Отвечает → тесты через MCP. Нет, но Unity установлен и редактор закрыт → `scripts/run-tests-headless.ps1` (Windows) / `.sh`. Ни того, ни другого → команды и чеклист, отчёт с пометкой «не запускалось».
3. Разбор: `scripts/parse_nunit.py <xml…> --plan design/qa/test-plan-<slice>.md`. 0 тестов = FAIL.
4. `smoke`: шаги из раздела Smoke тест-плана, видимые — play mode + скриншот через MCP.
5. Каждое падение → `design/qa/bugs/BUG-NNN.md` (номер — следующий свободный) или ссылка на существующий.
6. Отчёт `design/qa/runs/YYYY-MM-DD-<slice>.md`. Покажи итоги в числах и вердикт. S1/S2 открыты → плейтест не рекомендуется.

Язык ответа — язык пользователя.
