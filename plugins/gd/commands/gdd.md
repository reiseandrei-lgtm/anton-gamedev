---
description: Черновик раздела GDD для системы по шаблону / Draft a GDD section for a system
argument-hint: "<система> [--quick]"
disable-model-invocation: true
---

Используй скилл `gdd-author` для системы: **$ARGUMENTS**

- Если аргумент пуст — возьми следующую MVP-систему без GDD из `design/systems-map.md` и спроси подтверждение.
- `--quick` → лёгкий режим (quick spec правки существующей системы).
- Файл: `design/gdd/<system-kebab-case>.md`, `status: draft`.
- Иди по секциям шаблона, задавая вопросы о решениях; не выдумывай правила. Неизвестное — в Open Questions.
- В конце — чек-лист готовности и предложение `/gd:review design/gdd/<system>.md`.

Язык ответа — язык пользователя. Художественный текст (флейвор, реплики) — только по явной просьбе, иначе плейсхолдеры.
