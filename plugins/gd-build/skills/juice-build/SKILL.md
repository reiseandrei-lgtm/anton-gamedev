---
name: juice-build
description: >-
  Отклик на игровые события в Unity по целям Game Feel из GDD: частицы, шейдерные вспышки, тряска и толчок камеры, hitstop, squash и stretch объекта, вибрация геймпада; каждый отклик замеряется в кадрах PlayMode-тестом и сверяется с целью скриптом. Пишет раздел Juice в design/build/<system>.log.md.
  Триггеры RU: «добавь джус», «сделай отклик на удар», «хитстоп», «тряска камеры», «частицы на событие», «сверь тайминги отклика».
  Triggers EN: "add juice to", "implement hitstop", "screen shake", "impact particles", "measure feedback timings".
  Не для оценки ощущения и целей в кадрах (gd:game-feel), не для анимации персонажа (anim-build), не для HUD и меню (ui-build).
---

# juice-build

Ты реализуешь отклик, который уже задан в GDD (Feedback, Game Feel), и доказываешь его тайминг числом кадров. Ощущение не оцениваешь: «приятно ли» решает человек и `gd:game-feel`.

## 0. Preflight
Как в `feature-build`: `../slice-build/scripts/preflight.py` + проба MCP (инструменты или CLI). Нет MCP → режим plan (компоненты на диск, замеров нет, ⚠️).

## 1. Вход
GDD системы: таблица Feedback (`FB*`, колонка Visual) и раздел Game Feel (цели: «отклик ≤ 1 кадр», «squash → stretch 2 кадра»); `design/art/art-bible.md` (цвета ролей, принципы анимации); `design/audio/event-map.md` (звук того же FB). Нет чисел в Game Feel → стоп по этому FB: JU3, предложи `gd:game-feel` (paper) записать цель.

## 2. Алгоритм (техники и замер — `references/juice-method.md`)
1. Для каждого визуального FB: канал (частицы / камера / hitstop / squash / вспышка / вибрация), кадр начала, длительность, цвет роли.
2. Реализация компонентом, который подписан на событие системы (не опрашивает состояние в `Update`); параметры отклика — в конфиге (ScriptableObject), не литералами.
3. Замер: PlayMode-тест с `Time.captureFramerate = 60`, событие → `Time.frameCount` события и первого кадра отклика (частица активна, камера сдвинута, `timeScale` изменён) → длительность.
4. Звук того же FB: вызывается в том же кадре (если FMOD подключён) — отметка в таблице.
5. Строка в таблице `## Juice` лога системы; скриншот кадра импакта через MCP — **посмотри на него**.
6. `python3 scripts/check_juice.py design/build/<system>.log.md --gdd design/gdd/<system>.md --map design/audio/event-map.md`.

## Done
`check_juice.py` без FAIL; у каждого визуального FB есть замер и скриншот; консоль чистая. Дальше — `gd:game-feel` (build) по билду.

## Правила
Язык ответа = язык запроса. Не «сочнее», а канал, кадр, длительность. Тряска камеры и вспышки — с настройкой отключения (доступность, `ux/accessibility.md`). Платные генераторы VFX и ассетов не использовать.
