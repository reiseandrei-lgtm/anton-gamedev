---
description: "Независимое ревью кода системы агентом code-reviewer / Independent code review of a system"
argument-hint: "<system> [база для diff, по умолчанию последний коммит перед системой]"
disable-model-invocation: true
---

Ревью кода системы **$ARGUMENTS** агентом `code-reviewer`.

1. Собери diff: `git diff <база>..HEAD -- <папки модуля, тестов и конфигов системы> > design/build/<system>.diff` (в Unity-проекте; путь к diff — в `design/build/`). Пустой diff → стоп, скажи об этом.
2. Запусти агента `code-reviewer` и передай **только пути**: `design/build/<system>.diff`, `design/gdd/<system>.md`, `design/tech/architecture.md`, `design/qa/test-plan-*.md`. Лог сборки и историю не передавай.
3. Покажи вердикт, главную проблему и путь к отчёту `design/reviews/<date>-code-<system>.md`.
4. FAIL → следующий шаг `/gd-build:feature <system>` с находками; CONCERNS → решение пользователя в `design/decisions-log.md` или в Open issues лога.

Язык ответа — язык пользователя.
