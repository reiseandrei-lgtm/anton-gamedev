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
