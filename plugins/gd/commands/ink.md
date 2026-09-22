---
description: План и драфт Ink-слайса / Plan and draft an Ink slice
argument-hint: "<слайс> [--plan-only | --text]"
disable-model-invocation: true
---

Используй скилл `ink-slice` для слайса: **$ARGUMENTS**

1. **План** → `design/narrative/ink/<slice>.plan.md` (вход/выход, переменные, выборы-намерения, повторные визиты, теги Unity/FMOD, критерии приёмки).
   Раздел «Выборы» — таблица ценность / тип / где стреляет; раздел «Локализация» — лимиты UI, строки с родом/числом. Правила — `ink-slice/references/localization-and-telemetry.md`.
2. **Замки и ключи** — таблица requires/grants, проверка soft lock и циклов.
3. Покажи план и дождись подтверждения. С `--plan-only` — остановись здесь.
4. **Драфт .ink** — по умолчанию каркас: knots/stitches, выборы, переменные, diverts, теги, плейсхолдеры `[РЕПЛИКА: …]`. Полный текст реплик — только с `--text` или по явной просьбе. Путь к `.ink` подтверди у пользователя.
5. **Проверка** — статическая (или `inklecate`, если доступен): достижимость, тупики, неиспользуемые переменные; все текстовые строки с `#id`, выборы с `#track`, нет склеек фраз. Результаты — в план.
6. **Континуити** — если есть `design/narrative/continuity/promises.md`: запусти `narrative-continuity/scripts/check_continuity.py` по этому `.ink`; новые сетапы из слайса предложи внести в промисы (с подтверждения).
7. С `--text` — перед показом правка в три прохода (`character-voice/references/voice-kit.md`) и по `gd-router/references/prose-failures.md`.

Язык ответа — язык пользователя; идентификаторы Ink — на английском.
