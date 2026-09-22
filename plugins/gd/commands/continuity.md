---
description: Проверка континуити, промисов и канона / Continuity, setup-payoff and canon check
argument-hint: "[register | check | impact <что меняется>] [пути .ink]"
disable-model-invocation: true
---

Используй скилл `narrative-continuity`: **$ARGUMENTS**

1. Режим из аргумента; по умолчанию `check`.
2. Нет `design/narrative/continuity/` → предложи создать из шаблонов (`narrative-continuity/references/continuity-model.md`) и остановись до подтверждения.
3. `check`: если есть `.ink` — сначала `scripts/check_continuity.py`, затем ручные проверки знания, присутствия и канона. Отчёт → `design/reviews/YYYY-MM-DD-continuity.md`.
4. `register`: кандидаты в промисы покажи списком, в `promises.md` вноси только подтверждённые.
5. `impact`: список затронутых промисов, строк state/canon и узлов; ничего не правь без подтверждения.
6. Покажи вердикт, ошибки, невыстрелившие ружья и вопросы автору.

Язык ответа — язык пользователя. Художественный текст не пиши.
