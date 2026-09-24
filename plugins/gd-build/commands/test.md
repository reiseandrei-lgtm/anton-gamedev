---
description: Прогнать тесты и smoke Unity-проекта, завести баги / Run Unity tests and smoke, file bugs
argument-hint: "[suite | smoke | input | visual | soak | bug] <slice> [путь к Unity-проекту] [--minutes N]"
disable-model-invocation: true
---

Используй скилл `qa-run`: **$ARGUMENTS**

1. Режим из аргумента; по умолчанию `suite`.
2. Проба Unity MCP. Отвечает → тесты через MCP. Нет, но Unity установлен и редактор закрыт → `scripts/run-tests-headless.ps1` (Windows) / `.sh`. Ни того, ни другого → команды и чеклист, отчёт с пометкой «не запускалось».
3. Разбор: `scripts/parse_nunit.py <xml…> --plan design/qa/test-plan-<slice>.md`. 0 тестов = FAIL.
4. `smoke`: шаги из раздела Smoke тест-плана, видимые — play mode + скриншот через MCP.
5. `visual`: снимки по `visual`-кейсам (разрешение, seed, камера из Given) → `scripts/diff_png.py --baseline-dir design/qa/visual --shots-dir <снимки> --out <diff>`; эталоны утверждает пользователь. `soak`: N минут (по умолчанию 10) с замерами каждые 30 с → `design/qa/perf/<date>-soak.md` → `scripts/check_soak.py`.
6. Каждое падение → `design/qa/bugs/BUG-NNN.md` (номер — следующий свободный) или ссылка на существующий.
7. Отчёт `design/qa/runs/YYYY-MM-DD-<slice>.md`. Покажи итоги в числах и вердикт. S1/S2 открыты → плейтест не рекомендуется.

Язык ответа — язык пользователя.
