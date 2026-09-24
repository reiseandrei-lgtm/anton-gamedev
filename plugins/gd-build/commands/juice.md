---
description: "Отклик на события в Unity с замером в кадрах / Implement and measure juice in Unity"
argument-hint: "<system> [FB1,FB3,…] [путь к Unity-проекту]"
disable-model-invocation: true
---

Используй скилл `juice-build` для **$ARGUMENTS**

1. Preflight и проба MCP (как в `/gd-build:feature`). Покажи режим.
2. Прочитай Feedback и Game Feel GDD системы. FB без цели в кадрах → не реализуй вслепую: JU3 и предложи `gd:game-feel`.
3. Покажи план: FB → канал → цель → как замерим; дождись «да».
4. Реализация по `juice-build/references/juice-method.md`, замер PlayMode-тестом, скриншот кадра импакта (посмотри на него).
5. Раздел Juice в `design/build/<system>.log.md`, затем `juice-build/scripts/check_juice.py`.
6. Итоги: таблица замеров, что не совпало с целью, следующий шаг — `gd:game-feel` по билду.

Язык ответа — язык пользователя.
