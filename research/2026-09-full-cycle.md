---
status: approved   # template | draft | review | approved
updated: 2026-09-23
owner: Anton
---

# Ресерч: расширение anton-gamedev на полный цикл

Фаза 1 из промта «full-cycle». Здесь только чтение и анализ, код плагина не менялся. Данные собраны 2026-09-23: метаданные через GitHub API, содержимое через shallow-клоны в `vendor/`, остальное из веб-поиска. Где проверить не удалось, так и написано.

## 1. Кандидаты

Звёзды и дата последнего push взяты из GitHub API на 2026-09-23. Колонка «Качество» — оценка SKILL.md по прочитанным файлам: **A** — конкретные алгоритмы, чеклисты, полевые знания; **B** — структура и шаблоны, но много инфраструктуры и объёма; **C** — паттерны или сниппеты без процесса; **—** — не про скиллы.

| # | Кандидат | Что делает | Стадия | Лицензия | Push | ★ | Качество | Скрипты / проверки | Внешние API / платно | Решение |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) | 72 скилла, 49 агентов, иерархия студии; шаблоны `art-bible`, `sound-bible`, `test-plan`, `hud-design`, `accessibility-requirements`, `player-journey`, `ux-spec`, `release-checklist` | Весь цикл | MIT | 2026-09-23 | 25.4k | B: 150–770 строк на скилл, конкретные секции и гейты, но всё завязано на `yaml-helper.sh`, `resolve_config`, студийные роли и спринты | Хуки, `smoke-check` запускает тест-сьют | Нет | **Адаптировать** шаблоны и чеклисты: art/sound bible, test-plan (классы Logic/Integration/Visual/UI), smoke scope, UX/HUD/accessibility. Уже есть в ATTRIBUTION |
| 2 | [fagemx/gstack-game](https://github.com/fagemx/gstack-game) | 27 скиллов; `playtest` (протокол, метрики, анализ, рекрутинг, score полноты), `game-qa`, `game-visual-qa`, `asset-review`, `game-ux-review`, `game-ship` | Плейтест, QA, релиз | MIT | 2026-05-31 | 70 | B+: сильная методология в `references/` (`analysis-framework`, `metrics-and-benchmarks`, `visual-thresholds`, `naming-conventions`), но bash-преамбула, телеметрия в `~/.gstack`, 500–980 строк | bun-генератор доков | Нет | **Адаптировать** методологию плейтеста, visual QA, asset review; преамбулу и телеметрию не брать. Уже есть в ATTRIBUTION |
| 3 | [Benjamin-Curlier/unity-kit](https://github.com/Benjamin-Curlier/unity-kit) | Плагин Unity: `unity-verify` (compile → console → tests → play smoke → screenshot), `unity-playtest` (3 уровня: InputTestFixture, пробы состояния, скриншоты), `unity-ci` + `run-tests-headless.ps1/.sh`, агент `playtest-qa`, хуки | Сборка, QA | MIT | 2026-07-26 | 0 | **A**: лучшее найденное по Unity-циклу. Знания из практики: компиляцию доказывают по mtime DLL, прогон с 0 тестов считается FAIL, не больше 3 fix-циклов на проблему, тишина в консоли при нуле кадров не доказательство | Да: headless-раннер с exit-кодами 0/2/3, `gen-sfx.py`, хуки | Работает поверх CoplayDev MCP; в комплекте `elevenlabs` с API-ключом | **Адаптировать** verify loop и уровни плейтеста в build/QA-скиллы, headless-скрипт взять с шапкой источника. Риск: один автор, 0★ |
| 4 | [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp) | MCP-мост к Unity Editor: scene, gameobject, script, `run_tests`, `read_console`, `manage_camera` (скриншот), `manage_build`, `manage_profiler`, `execute_code` | Сборка, QA, перф | MIT | 2026-09-22 | 14.4k | — (MCP; есть `unity-mcp-skill`) | Тестовые проекты в репо | Бесплатно; Python 3.10+ / uv; Unity 2021.3 → 6.x. `generate_image/audio/model` — платная генерация | **Взять как зависимость** (основной MCP), код не копировать |
| 5 | [IvanMurzak/Unity-MCP](https://github.com/IvanMurzak/Unity-MCP) | MCP + CLI + около 80 скиллов-инструментов: `tests-run`, `screenshot-*`, `profiler-*`, `console-get-logs`, runtime MCP в билде | Сборка, QA, перф | Apache-2.0 | 2026-09-17 | 4.3k | B: скиллы — обёртки над инструментами, без процесса | Да | Бесплатно (так заявлено в README; поддерживаемые версии Unity в README не нашёл — **не проверено**) | **Альтернативная зависимость.** Скиллы пишем против абстрактных действий (compile, tests, play, screenshot), не против имён инструментов |
| 6 | [Unity-Technologies/unity-agent-plugin](https://github.com/Unity-Technologies/unity-agent-plugin) (официальный Unity Plugin в `claude-plugins-official`) | 31 скилл: UI (uGUI/UITK), 2D/tilemap, URP, `audio-setup-mixers`, `optimize-audio`, `localization`, IAP, LevelPlay, multiplayer, `unity-cli` | Реализация | **Unity Companion License** | 2026-09-22 | 333 | A для движковых how-to | `check-skill-frontmatter.mjs` | В репо нет `.mcp.json`. Официальный Unity MCP (AI Assistant package): Unity 6+, **нужен trial или подписка Unity AI и Unity Cloud** (блог Unity, 2026-05-11). Тестов, play mode и скриншотов в блоге нет — **не проверено** | **Не копировать** (лицензия), ставить рядом. Наши скиллы ссылаются на его скиллы для движковых деталей |
| 7 | [HermeticOrmus/claude-code-game-development](https://github.com/HermeticOrmus/claude-code-game-development) | Фактически форк общего набора (fastapi, web3, k8s…), по геймдеву 2 агента (`unity-developer`, minecraft) | — | MIT | 2026-05-25 | 62 | C | Нет | Нет | **Не брать**: геймдева почти нет |
| 8 | [HermeticOrmus/LibreGameDev-Claude-Code](https://github.com/HermeticOrmus/LibreGameDev-Claude-Code) | 20 плагинов-паттернов (playtesting, audio, save, perf, ui, localization) | Реализация | MIT | 2026-05-25 | 6 | C: сниппеты кода (в основном GDScript), без алгоритма работы, чеклистов и критериев Done | Нет | Нет | **Не брать**. Идею death heatmap можно упомянуть в analytics как метод |
| 9 | [hiddenpeopleclub/claude-code-plugins](https://github.com/hiddenpeopleclub/claude-code-plugins) | C++: 9 агентов ревью, в т.ч. adversarial-testing | QA кода | **Нет лицензии** | 2026-01-10 | 0 | — | Хуки | Нет | **Не брать**: без лицензии, и стек C++, а не Unity |
| 10 | [Randroids-Dojo/Godot-Claude-Skills](https://github.com/Randroids-Dojo/Godot-Claude-Skills) | 1 скилл + `example-project` с аддоном PlayGodot и pytest-тестами | Структура | MIT | 2026-01-19 | 44 | — | Да: e2e-тесты скилла на примере | Нет | **Взять идею структуры**: `examples/` с мини-проектом как тест скиллов. Код не нужен |
| 11 | [anthropics/skills](https://github.com/anthropics/skills) `skill-creator`, `frontend-design` | Методология написания скиллов, eval-скрипты, eval viewer | Мета | Apache-2.0 (LICENSE.txt в папке скилла) | 2026-09-22 | 178k | A | Да | Нет | **Использовать как методологию** в фазе 3 (уже установлен как `anthropic-skills:skill-creator`), не копировать |
| 12 | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Каталог; `plugin-dev`, `skill-creator`, запись `unity` | Мета | Apache-2.0 | 2026-09-22 | 36.6k | — | — | — | **Референс** схемы плагина |
| 13 | [ahujasid/blender-mcp](https://github.com/ahujasid/mcp-for-blender) (сейчас `mcp-for-blender`) | Управление Blender из LLM | Арт 3D | MIT | 2026-09-21 | 29.2k | — | — | Бесплатно; есть телеметрия (unity-kit отключает через `DISABLE_TELEMETRY`) | **Опционально, не в волне 1.** Для мобильного 2D не нужен |
| 14 | PixelLab MCP ([pixellab-code](https://github.com/pixellab-code/pixellab-mcp), [flynnsbit](https://github.com/flynnsbit/PixelLab-MCP)) | Генерация пиксель-арт спрайтов и анимаций | Арт | **Нет лицензии** у обоих | 2025-08 / 2025-10 | 41 / 1 | — | — | Платный API | **Не брать**: платно, без лицензии, заброшено |
| 15 | [freema/pixelforge-mcp](https://github.com/freema/pixelforge-mcp) | Спрайты через Gemini, кроп и нарезка | Арт | MIT | 2026-09-20 | 5 | — | — | Ключ Google Gemini | **Не брать**: нужен API-ключ, проект незрелый |
| 16 | [elevenlabs/elevenlabs-mcp](https://github.com/elevenlabs/elevenlabs-mcp) | SFX, музыка, TTS | Аудио | MIT | 2026-08-20 | 1.5k | — | — | Ключ API; на free tier только некоммерческое использование | **Не брать** в плагин. Если пользователь сам поставит — можно упомянуть |
| 17 | FMOD Studio MCP: [raffyknowsnothing/fmod-studio-mcp](https://github.com/raffyknowsnothing/fmod-studio-mcp) · [xDarkzx/Dans_Fmod_Studio_MCP](https://github.com/xDarkzx/Dans_Fmod_Studio_MCP) · jmperez127/fmod-mcp | Управление FMOD Studio через scripting terminal (TCP 3663): события, параметры, микшер, банки | Аудио | MIT · Apache-2.0 · **не проверено** (через API репо 404, есть только листинг на Glama) | 2026-09-15 · 2026-09-17 · ? | 0 · 1 · ? | — | — | Бесплатно; Script Server в FMOD включается вручную | **Опциональный путь.** Проекты незрелые (0–1★). Основной путь: карта событий как файл + детерминированная проверка; MCP — бонус при наличии |
| 18 | [alttester/AltTester-Unity-SDK](https://github.com/alttester/AltTester-Unity-SDK) | UI-автотесты игр, есть MCP-сервер | QA | **GPL-3.0** | 2026-09-21 | 122 | — | — | SDK бесплатный, облако платное | **Не брать**: GPL-SDK внутри билда — риск для коммерческой игры |

**Не проверено вовсе:** Scenario, Layer, Ludo, Meshy, AutoSprite — все платные сервисы генерации. По правилу «без платных сервисов» их не смотрел. Wwise-автоматизацию не искал: стек FMOD.

## 2. Карта пробелов

Покрытие: ✅ есть · 🟡 частично · ❌ нет.

| Стадия | Сейчас в `gd` | Пробел | Лучший источник | Как закрыть |
|---|---|---|---|---|
| Арт-дирекция | ❌ | Art bible из столпов, палитра и value-структура, силуэты и читаемость (тест силуэта и grayscale), референсы, список ассетов с нейминговыми правилами, бюджеты под мобайл | CCGS `art-bible` и шаблон; gstack-game `asset-review` (`naming-conventions`, `benchmarks`), `game-visual-qa` (`visual-thresholds`) | Написать скилл, методологию адаптировать. Контраст палитры проверяется скриптом (WCAG и контраст по яркости) |
| UI/UX и онбординг | ❌ (`game-feel` касается только отклика) | FTUE и туториал по петлям, HUD (информация → приоритет → зона), доступность (базовый уровень Game Accessibility Guidelines), лимиты текста под локализацию | CCGS `ux-design`, `hud-design`, `accessibility-requirements`, `player-journey`; gstack-game `game-ux-review` | Адаптировать в один скилл с режимами `ftue`, `hud`, `a11y` |
| Аудио | ❌ (FMOD только упоминается в README) | Audio bible от столпов, SFX-лист из feedback-цепочек GDD, **карта событий FMOD** (нейминг `event:/…`, параметры, снапшоты, шины), адаптивная музыка по состояниям, микс, VO-лист | CCGS `sound-bible`, `team-audio`; unity-kit `unity-audio` (честная проверка: «ты не слышишь»); официальный `audio-setup-mixers` (только для Unity-микшера) | **Написать с нуля** (под FMOD готового нет). Скрипт проверяет карту событий: нейминг, дубли, «feedback без события», «событие без источника» |
| Технический дизайн | ❌ | Архитектура Unity-проекта из GDD (asmdef, данные в ScriptableObject, сохранения, сцены), перф-бюджеты под мобайл, ADR | CCGS `create-architecture`, `architecture-decision`, шаблон TDD; unity-kit `gamedev-patterns` | Адаптировать. Документ-уровень, без кода: `design/tech/` |
| Сборка прототипа | ❌ (пайплайн заканчивается на `handoff/`) | Из `handoff/<slice>.md` в играбельный слайс: план задач по Engineering Done → MCP-действия → verify loop → отчёт против Design Done | unity-kit `unity-verify`, `unity-playtest`, `unity-init`; CCGS `prototype`, `vertical-slice` | Адаптировать. Работает только в Claude Code с Unity MCP; без MCP — план и чеклист |
| QA и тестирование | ❌ | Тест-план из GDD (Core Rules и Edge Cases → тест-кейсы EditMode/PlayMode/manual), трассировка покрытия, smoke-набор билда, формат баг-репорта, headless-прогон | CCGS `qa-plan`, `smoke-check`, `test-setup`, `bug-report`; unity-kit `unity-ci` и скрипт; gstack-game `game-qa` | Адаптировать. Скрипт трассировки покрытия GDD → тесты; headless-скрипт от unity-kit |
| Плейтест | 🟡 (`game-feel` по билду) | Протокол от гипотезы хендоффа, скрипт наблюдения, think-aloud, опросник, кодирование заметок, анализ по severity, возврат в `game-feel` / `balance-check` / GDD | gstack-game `playtest` (4 references); CCGS `playtest-report`; unity-kit `playtest-qa` (автоматический плейтест) | Адаптировать в один скилл с режимами `plan` и `analyze` + агент-аналитик, который видит только сырые заметки и гипотезу |
| Аналитика и метрики | 🟡 (D1/D7/D30 только в `balance-check`, телеметрия выборов в ink-refs, метрики в Syncario) | Taxonomy событий, воронки FTUE и core loop, KPI-цели, связь «гипотеза → событие → порог решения», проверка схемы | gstack-game `playtest/metrics-and-benchmarks`; syncario `social-voice-metrics` (свой) | Написать; нейминг событий проверяется скриптом |
| Релиз-готовность | ❌ | Стор-страница, бриф трейлера, чеклисты платформ (Google Play, App Store, Steam), локализация (частично есть в ink-refs) | CCGS `launch-checklist`, `release-checklist`; gstack-game `game-ship`; официальный Unity `localization` | **Волна 2.** Для прототипной стадии рано |

Сквозной вывод: у `gd` сильная дизайн-часть, но после хендоффа нет обратной петли. Билд → тест → плейтест → решение → правка GDD — именно эта петля и даёт качество игры. Приоритет волны 1: **петля прототипа** (build, QA, playtest) и **два направляющих документа**, без которых ассеты делаются вслепую (art и audio). Релиз и аналитика в полном объёме — позже.

## 3. Рекомендации по кандидатам (сводка)

- **Взять как зависимость:** CoplayDev/unity-mcp (основной MCP: MIT, бесплатно, есть `run_tests` и скриншоты). Официальный Unity Plugin ставить рядом как справочник движковых how-to.
- **Адаптировать методологию:** unity-kit (verify loop, уровни плейтеста, headless CI), gstack-game (playtest, visual/asset QA), CCGS (шаблоны art/sound bible, test-plan, UX/HUD/a11y, архитектура).
- **Писать с нуля:** аудио под FMOD (карта событий и проверка), аналитика (taxonomy и связь с гипотезами), трассировка GDD → тесты.
- **Не брать:** HermeticOrmus (оба), hiddenpeopleclub (нет лицензии), PixelLab (нет лицензии, платно), pixelforge и ElevenLabs (ключи API), AltTester (GPL), код официального Unity-плагина (Companion License).
- **Опционально, вне волны 1:** Blender MCP, FMOD Studio MCP (незрелые, но бесплатные).

## 4. Предварительная архитектура (для фазы 2)

**Два плагина в одном маркетплейсе:**

| Плагин | Где работает | Что внутри | Почему отдельно |
|---|---|---|---|
| `gd` (есть) | Claude Code + Cowork | Дизайн и направляющие документы: + art-direction, audio-direction, ux-onboarding, tech-design, playtest, metrics-plan | Всё документ-уровня, без MCP. Правило CLAUDE.md «без Unity-реализации» здесь остаётся |
| `gd-build` (новый) | Только Claude Code + Unity MCP | slice-build, qa-run (verify, tests, smoke), qa-plan, fmod-sync | Cowork не умеет Unity MCP: там эти скиллы срабатывали бы впустую. Описания не раздувают контекст в Cowork |

Дробить на `gd-art`, `gd-audio`, `gd-qa` не стоит: соло-пользователю ставить больше плагинов, а в арте и звуке по 1–2 скилла.

**Кандидаты волны 1 (10 скиллов, 4 агента-ревьюера):**

| Скилл | Плагин | Выход в `design/` | Проверка скриптом | Агент |
|---|---|---|---|---|
| `art-direction` | gd | `art/art-bible.md`, `art/asset-list.md` | контраст палитры, нейминг ассетов | `art-director` (видит только bible + столпы) |
| `audio-direction` | gd | `audio/audio-bible.md`, `audio/event-map.md` | нейминг FMOD, покрытие feedback → event | `audio-director` |
| `ux-onboarding` | gd | `ux/ftue.md`, `ux/hud.md`, `ux/accessibility.md` | — | — |
| `tech-design` | gd | `tech/architecture.md`, `tech/budgets.md`, `tech/adr/*.md` | — | — |
| `playtest` (`plan` / `analyze`) | gd | `playtest/<date>-<slice>.plan.md`, `.report.md` | — | `playtest-analyst` (видит только заметки и гипотезу) |
| `metrics-plan` | gd | `analytics/events.md`, `analytics/funnels.md` | схема и нейминг событий | — |
| `qa-plan` | gd-build | `qa/test-plan-<slice>.md` | трассировка GDD → тесты | `qa-lead` |
| `slice-build` | gd-build | `handoff/<slice>.build.md` (лог против Engineering Done) | — | — |
| `qa-run` | gd-build | `qa/runs/<date>.md`, `qa/bugs/*.md` | headless-раннер 0/2/3 | — |
| `fmod-sync` | gd-build | `audio/event-map.json` + чеклист интеграции | сверка event-map ↔ GDD | — |

Пайплайн после хендоффа: **хендофф → сборка → QA → плейтест → решение (iterate / pivot / kill) → назад в GDD или баланс**. Треки арта и звука стартуют параллельно после концепта: bible сразу после столпов, asset-list и event-map после GDD.
