---
name: feature-build
description: >-
  Реализация одной системы из GDD в Unity-проекте игры на стадии продакшна: тест первым по тест-плану, verify loop после каждой задачи, числа только из конфигов, каждое правило, формула и edge case (R / F / E) и критерий майлстоуна (ED-<system>-N) — в логе с доказательством; в конце независимое ревью кода агентом code-reviewer. Без MCP — план и чеклист. Пишет design/build/<system>.log.md.
  Триггеры RU: «реализуй систему», «сделай фичу из GDD», «имплементируй механику», «собери систему в Unity», «реализуй систему майлстоуна».
  Triggers EN: "implement the system", "build the feature from the GDD", "implement this mechanic in Unity", "implement the milestone system".
  Не для первого слайса из хендоффа (slice-build), не для отклика и эффектов (juice-build), не для HUD и меню (ui-build), не для дизайн-решений (gd:gdd-author).
---

# feature-build

Ты реализуешь одну систему так, как её описал GDD, и доказываешь каждое правило. Дизайн-решений не принимаешь: неоднозначность → стоп, вопрос в Open Questions GDD и `gd:gdd-author --quick`.

## 0. Preflight
`python3 ../slice-build/scripts/preflight.py <unity-проект> --design design` (на Windows `python`) + проба MCP (инструменты или CLI `unity-mcp` — `../slice-build/references/mcp-actions.md`). Нет ни того, ни другого → режим **plan**: план, чеклист, код на диск можно, в логе максимум ⚠️.

## 1. Вход
`design/gdd/<system>.md` (с ID R / F / E / K), `design/handoff/<milestone>.md` (`ED-<system>-N`), `design/tech/architecture.md` (модуль, Config map, Test seams), `design/qa/test-plan-*.md` (T-ID системы). Нет GDD или ID → стоп: `gd:gdd-author`. Нет кейсов системы в тест-плане → предложи `gd:qa-plan` и спроси, продолжать ли.

## 2. Алгоритм (детали — `references/feature-method.md`, verify loop — `../slice-build/references/verify-loop.md`)
1. Задачи из R / F / E и ED системы в порядке зависимостей (модуль из `architecture.md`, связи с готовыми системами — через их публичные события и read-only свойства).
2. На задачу: тесты из плана пишутся первыми и **красный прогон записывается** → реализация → зелёный прогон.
3. Knobs — только поля конфига по Config map (ScriptableObject через MCP `manage_scriptable_object`); литерал-knob в коде — ошибка.
4. После каждой задачи — verify loop: компиляция доказана mtime DLL, консоль без ошибок, тесты. Тесты при ошибке компиляции не запускать.
5. Максимум 3 fix-цикла на проблему; тот же текст ошибки дважды — смени подход или стоп с отчётом.
6. Лог `design/build/<system>.log.md` по ходу (формат — `../slice-build/references/build-log.md`, «Лог системы»): каждое R / F / E / ED — ✅ доказательство · ⚠️ не проверено · ⛔ причина.
7. Ревью: `git diff <база>..HEAD -- <папки модуля и тестов> > design/build/<system>.diff` → агент `code-reviewer` (передай только пути: diff, GDD, `tech/architecture.md`, тест-план). FAIL → исправь и повтори.
8. `python3 ../slice-build/scripts/check_build_log.py design/build/<system>.log.md --gdd design/gdd/<system>.md --handoff design/handoff/<milestone>.md --plan design/qa/test-plan-*.md`.

## Done
`check_build_log.py` без FAIL; компиляция доказана; консоль чистая; ревью кода не FAIL; режим (live / plan) и канал MCP указаны в логе. Дальше — `/gd-build:test` и следующая система майлстоуна.

## Правила
Язык ответа = язык запроса. Строки UI — ключи локализации. Код проекта — чужой код с правами ОС: через `execute_code` только чтение свойств. Платные инструменты MCP (`generate_*`, группа `asset_gen`, Unity AI) не вызывать. How-to API Unity — официальный Unity Plugin (`/unity:*`), если установлен.
