# Trigger cases: типовой запрос → ожидаемый скилл

Проверяется `tools/check_plugins.py` (P11): среди триггеров всех скиллов, входящих в запрос целиком (регистр не важен), самый длинный должен принадлежать ожидаемому скиллу. Пары — из матрицы `research/2026-09-production-cycle-architecture.md` §6. Добавляя скилл, добавь его пары сюда.

| Запрос | Скилл |
|---|---|
| как ощущается механика | game-feel |
| сочность прыжка | game-feel |
| does it feel good | game-feel |
| добавь джус на приземление | juice-build |
| add juice to the landing | juice-build |
| хитстоп при ударе | juice-build |
| тряска камеры | juice-build |
| онбординг | ux-onboarding |
| hud layout | ux-onboarding |
| сверстай hud | ui-build |
| build the hud | ui-build |
| экран паузы | ui-build |
| метрики | metrics-plan |
| какие события слать | metrics-plan |
| аудио-библия | audio-direction |
| какие звуки нужны | audio-direction |
| перенеси события в fmod | fmod-sync |
| арт-библия | art-direction |
| список ассетов | art-direction |
| импортируй ассеты | asset-integrate |
| замени плейсхолдеры | asset-integrate |
| что вырезать | scope-check |
| реализуй систему | feature-build |
| implement the system | feature-build |
| собери слайс | slice-build |
| хендофф альфы | gd-handoff |
| хендофф | gd-handoff |
| тест-план | qa-plan |
| прогони тесты | qa-run |
| сравни скриншоты с эталоном | qa-run |
| перф-бюджет | tech-design |
| замерь производительность | perf-check |
| влезаем ли в бюджет кадра | perf-check |
| profile the build | perf-check |
| собери билд игрока | build-release |
| настрой ci для unity | build-release |
| release build | build-release |
| смоделируй фонарь | model-build |
| блокаут в blender | model-build |
| export to glb | model-build |
| процедурная анимация хвоста | anim-build |
| настрой ik для ног | anim-build |
| rig in blender | anim-build |
| сделай звук для прыжка | sfx-design |
| синтезируй sfx приземления | sfx-design |
| design the sfx for landing | sfx-design |
| сделай музыку для забега | music-build |
| отрендери стемы | music-build |
| compose music for the menu | music-build |
