---
description: "Дизайн уровня — метрики, путь, встречи, темп, гейты / Level design — metrics, path, encounters, pacing, gates"
argument-hint: "<level> [check]"
disable-model-invocation: true
---

Используй скилл `level-design` для **$ARGUMENTS**

1. Прочитай GDD систем уровня (`## Tuning Knobs` — метрики движения), `design/systems-map.md`, `design/ux/ftue.md`, milestone-хендофф. Нет knob для нужной метрики → стоп, вопрос в `gdd-author`.
2. Нет `design/levels/` → создай из шаблона `templates/design/levels/_template.md` после подтверждения.
3. Покажи план: метрики (ссылки на knobs) → критический путь → встречи → кривая темпа → гейты; дождись «да».
4. Напиши `design/levels/<level>.md` по `level-design/references/level-method.md`.
5. `check` (и после записи) → `level-design/scripts/check_level.py design/levels/<level>.md --gdd design/gdd --systems design/systems-map.md` (на Windows `python`).
6. Итоги: длина, пики, встречи; числа темпа — ГИПОТЕЗА до плейтеста. Дальше — `/gd:qa-plan` и `[gd-build]` `/gd-build:feature`.

Язык ответа — язык пользователя.
