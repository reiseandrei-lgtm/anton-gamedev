---
name: analytics-build
description: >-
  Вызовы аналитики в коде Unity по design/analytics/events.md: генерация AnalyticsEvents.cs (имена событий и типизированные методы, как FmodEvents.cs) и локального JSONL-бэкенда для плейтестов с флагом согласия, вызовы в точках срабатывания; события без вызова, строковые имена, персональные данные и отправка без согласия проверяются скриптом. Внешний бэкенд — только по ADR.
  Триггеры RU: «подключи аналитику», «вставь события в код», «вызовы аналитики», «лог событий для плейтеста».
  Triggers EN: "wire analytics events", "add analytics calls", "analytics in Unity", "local event log for playtests".
  Не для выбора событий, KPI и воронок (gd:metrics-plan), не для телеметрии выборов Ink (gd:ink-slice), не для платных SDK аналитики.
---

# analytics-build

Ты переносишь решённое в `design/analytics/events.md` в код, не меняя решений: нет события для нужного вопроса → вопрос в `gd:metrics-plan`. По умолчанию ничего не уходит в сеть — только файл на устройстве.

## 0. Preflight
`python3 ../slice-build/scripts/preflight.py <unity-project> --for analytics` + проба MCP. Без MCP — файлы на диск и чеклист, компиляция «не проверено».

## 1. Вход
`design/analytics/events.md` (Events: имя, параметры, Trigger), `design/analytics/funnels.md`, GDD систем (где стреляет событие), `design/tech/architecture.md` (модули), `design/tech/adr/*` (решение о бэкенде, если есть).

## 2. Алгоритм (детали — `references/analytics-method.md`)
1. `python3 scripts/gen_analytics.py design/analytics/events.md --out <Assets/_Project/Scripts/Analytics> [--namespace Game.Analytics]` → `AnalyticsEvents.cs` (константы и методы) + `AnalyticsLog.cs` (JSONL, `Consent`). Руками не правишь — перегенерируешь.
2. Вызовы: на каждое событие — `AnalyticsEvents.<Event>(…)` в точке из колонки Trigger (подписка на событие системы, не опрос в Update). Параметры — из состояния систем; строки имён — только из констант.
3. Согласие: `AnalyticsLog.Consent` выставляет экран согласия или флаг плейтест-сборки; по умолчанию `false`. Текст согласия пишет человек (`gd:release-plan`, юридическое).
4. Тест: EditMode — вызов пишет строку JSON с именем и параметрами; без согласия — ничего. Verify loop; play mode — файл `analytics/<session>.jsonl` появился и читается.
5. Лог `design/build/analytics.log.md` (`system: analytics`): событие → файл и строка вызова → доказательство.

## Проверка
`python3 scripts/check_analytics_calls.py <Assets/…> --events design/analytics/events.md`: AN1 событие без вызова или `AnalyticsEvents.cs` расходится с events.md · AN2 строковое имя события вне констант · AN3 параметр с признаками PII (правила `check_events.py`) · AN4 вызовы без флага согласия (WARN). На Windows — `python`.

## Done
Скрипт без FAIL; у каждого события есть вызов с доказательством (тест или строка в JSONL); без согласия файл не пишется. KPI по JSONL считает человек или `gd:playtest`.

## Правила
Язык ответа = язык запроса. Платные SDK и сервисы аналитики не подключать; внешний бесплатный бэкенд — решение человека через ADR (`/gd:tech adr analytics`). Идентификатор — случайный id сессии, без устройства и аккаунта. Код проекта — чужой код: через MCP только чтение свойств.
