---
name: build-release
description: >-
  Сборка игрока и выпуск: версия из тега и CHANGELOG, сборка Windows и Android через MCP или headless, workflow GameCI, .gitignore и LFS для Unity, скрипты SteamPipe, hotfix и откат; готовность проекта проверяется скриптом. Логины, секреты и кнопка Release — человек.
  Триггеры RU: «собери билд игрока», «релизная сборка», «настрой CI для Unity», «SteamPipe», «LFS для Unity».
  Triggers EN: "build the player", "release build", "set up Unity CI", "SteamPipe upload script".
  Не для плана запуска и страницы магазина (gd:release-plan), не для тестов (qa-run), не для замеров размера и кадра (perf-check).
---

# build-release

Ты готовишь проект к выпуску и собираешь игрока. Не публикуешь: загрузка в стор, секреты CI и выпуск ветки — шаги человека 🟨.

## 0. Preflight
`python3 ../slice-build/scripts/preflight.py <unity-project> --for release`: редактор, модули платформ (Windows, Android), канал MCP. Нет MCP и редактор открыт → только файлы (workflow, .gitattributes, VDF) и чеклист.

## 1. Вход
Unity-проект игры (`<game>/unity/`), `CHANGELOG.md`, тег `vX.Y.Z`, `design/tech/budgets.md` (размер сборки), `design/release/builds.md` (если есть).

## 2. Алгоритм (детали — `references/release-method.md`)
1. `python3 scripts/check_release.py <project> --tag vX.Y.Z` → исправь FAIL до сборки (RL2/RL3 — `.gitignore` и `.gitattributes`; `git lfs migrate` переписывает историю — только после «да»).
2. Сборка: MCP `manage_build` (редактор открыт) или headless `-executeMethod` (закрыт). Development выключен.
3. Запуск собранного билда ≥ 10 с, `Player.log` без исключений; размер — в `perf-check`.
4. Строка в `design/release/builds.md`: `Version · Tag · Platform · Date · Build ID`.
5. CI: workflow GameCI из шаблона → `check_release.py` (RL4/RL5). Запуск без секретов — «не проверено».
6. Steam: VDF из шаблона → RL6; загрузку `steamcmd` делает человек.

## Done
`check_release.py` без FAIL; билд собран и запускается (лог); строка в `builds.md`; всё, что требует логина или секрета, — в чеклисте 🟨 с точной командой.

## Правила
Язык ответа = язык запроса. Значения секретов не читаешь, не печатаешь и не просишь. Платные облачные билд-сервисы не подключать; GameCI и бесплатные минуты Actions — по решению человека. Push тега и загрузка — только после «да».
