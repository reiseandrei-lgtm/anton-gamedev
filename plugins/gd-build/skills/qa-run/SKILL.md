---
name: qa-run
description: >-
  Прогон проверок Unity-проекта: EditMode и PlayMode тесты (через бесплатный Unity MCP или headless при закрытом редакторе), smoke-набор из тест-плана, проверка ввода через InputTestFixture, скриншоты, сравнение экранов с эталонами (visual), долгий прогон на утечки (soak), баг-репорты по шаблону. Прогон с нулём тестов = FAIL. Пишет design/qa/runs/<date>-<slice>.md и design/qa/bugs/BUG-NNN.md.
  Триггеры RU: «прогони тесты», «smoke-тест билда», «проверь билд», «запусти EditMode», «запусти PlayMode», «заведи баг», «сравни скриншоты с эталоном», «долгий прогон».
  Triggers EN: "run the tests", "smoke test the build", "verify the build", "run PlayMode tests", "file a bug", "compare screenshots to baseline", "soak test".
  Не для составления тест-плана (gd:qa-plan), не для плейтеста с людьми (gd:playtest), не для сборки слайса (slice-build).
---

# qa-run

Ты прогоняешь проверки и отчитываешься доказательствами. Вердикт без доказательства не выносишь.

## Режимы
- **suite** (по умолчанию) — все EditMode + PlayMode.
- **smoke** — smoke-набор из `design/qa/test-plan-<slice>.md`: автоматические шаги — тестами, остальное — play mode + пробы + скриншоты через MCP; без MCP — чеклист для человека.
- **input** — только PlayMode-тесты ввода (`InputTestFixture`).
- **visual** — `visual`-кейсы тест-плана: разрешение, камера и seed из Given → скриншот через MCP → `python3 scripts/diff_png.py --baseline-dir design/qa/visual --shots-dir <снимки> --out <папка diff>`. Нет эталона → снимок в `qa/visual/_pending/` (VD4): эталоном его делает человек. Отличие → баг или новый эталон — решает человек.
- **soak** — N минут play mode (по умолчанию 10; скрипт ввода или простой) с замером кадра и памяти каждые 30 с (`manage_profiler` `get_frame_timing` / `get_counters`) → `design/qa/perf/<date>-soak.md` → `python3 scripts/check_soak.py <отчёт>`: SK1 рост памяти · SK2 деградация кадра · SK3 исключения.
- **bug** — баг-репорт `design/qa/bugs/BUG-NNN.md` по шаблону `references/qa-run-method.md` §6 (тот же, что в `gd:qa-plan`), сначала падающий тест, если баг воспроизводим автоматически.

## Как запускать (детали — `references/qa-run-method.md`)
1. **Редактор открыт и MCP отвечает** → тесты через MCP (абстрактные действия → инструменты: `../slice-build/references/mcp-actions.md`).
2. **Редактор закрыт** → headless: `scripts/run-tests-headless.ps1 -ProjectPath <proj> -Platform Both` (Windows) или `bash scripts/run-tests-headless.sh --project-path <proj> --platform Both`. Exit: 0 зелёный · 2 есть падения · 3 прогон не завершился (компиляция, лицензия, открытый редактор, **0 тестов**).
3. **Разбор**: `python3 scripts/parse_nunit.py <proj>/TestResults/*.xml --plan design/qa/test-plan-<slice>.md` (на Windows `python`) — итоги, падения с сообщениями, сопоставление с T-ID плана (имя метода `T_hop_01_…` или `[NUnit.Framework.Property("TID", "T-hop-01")]`; `Category` с «-» NUnit не принимает), автоматизируемые тесты плана, которых нет в прогоне.
4. Ни MCP, ни Unity → режим plan: команды для запуска и чеклист; в отчёте «не запускалось».

## Выход
`design/qa/runs/YYYY-MM-DD-<slice>.md`: режим, билд (commit), итоги в числах (`EditMode 12/12 · PlayMode 4/5 · smoke 7/8`), падения → BUG или ссылка на существующий, T-ID плана без реализации, что пропущено и почему, скриншоты. Severity по шкале тест-плана: S1–S2 блокируют плейтест.

## Done
Отчёт с числами; каждое падение → баг или ссылка; пропущенные шаги названы; при exit 3 — причина из лога, не «тесты зелёные».

## Правила
Язык ответа = язык запроса. Headless-прогон и `run_tests` исполняют C# проекта с правами ОС — только доверенные проекты. `-AcceptApiUpdate` не использовать без согласия (переписывает исходники). Баг дизайна (edge case не описан в GDD) — не баг кода: ссылка на GDD и `gd:gdd-author --quick`. Платные облака тестирования не предлагать.
