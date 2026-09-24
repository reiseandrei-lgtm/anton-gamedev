---
description: "Таблицы локализации и псевдолокаль / Localization tables and pseudo-localization"
argument-hint: "[scan | tables | check] [путь к Unity-проекту]"
disable-model-invocation: true
---

Используй скилл `loc-build`: **$ARGUMENTS**

1. Preflight `slice-build/scripts/preflight.py <unity-project> --for loc`. Нет пакета Localization → режим plan; спроси, ставить ли пакет, ставь только после «да».
2. `scan` → ключи из `design/ux/hud.md`, UXML, C#, Ink (`#id:`); литералы вместо ключей — список для `ui-build` / `ink-slice`.
3. `tables` → `design/loc/<Table>.csv` по `loc-build/references/loc-method.md`: `max:N` из UX, значения базового языка — от человека, машинный перевод — с `mt`. Покажи план (таблицы, языки, лимиты); дождись «да».
4. Live: коллекции, импорт CSV, привязки в UXML, Pseudo-Locale и скриншоты через `ui-build`.
5. `check` (и после записи) → `loc-build/scripts/check_loc.py design/loc --hud design/ux/hud.md --unity <Assets> --pseudo 0.35` (на Windows `python`); лог `design/build/loc.log.md`.
6. Итоги в числах: ключей, языков, пустых, `mt`, переполнений; режим plan / live.

Язык ответа — язык пользователя.
