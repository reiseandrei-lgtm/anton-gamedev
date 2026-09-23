---
description: "Технический дизайн Unity — модули, конфиги, сохранения, бюджеты, ADR / Unity technical design"
argument-hint: "[<slice> | adr <тема> | check]"
disable-model-invocation: true
---

Используй скилл `tech-design`: **$ARGUMENTS**

1. `<slice>` или пусто → `design/tech/architecture.md` и `budgets.md` для систем слайса из `design/handoff/<slice>.md`.
2. `adr <тема>` → `design/tech/adr/NNN-<тема>.md` (следующий свободный номер).
3. `check` → `check_knobs.py design/tech/architecture.md --gdd <GDD систем слайса>` (на Windows `python`).
4. Нет `design/tech/` → создай из шаблона после подтверждения.
5. GDD без ID knobs (`K1…`) → предложи проставить через `gdd-author`, иначе config map хрупкий.
6. Код не пиши. How-to по Unity — официальный Unity Plugin; реализация — `/gd-build:slice` в Claude Code.

Язык ответа — язык пользователя.
