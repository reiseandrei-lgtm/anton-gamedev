# Attribution

Плагины `gd` и `gd-build` частично основаны на материалах восьми репозиториев под лицензией MIT и одного под Apache-2.0. Ниже — что откуда взято и тексты лицензий (MIT — полностью здесь; Apache-2.0 — `licenses/Apache-2.0.txt` и `licenses/NOTICE-awesome-gamedev-agent-skills.txt`).

SKILL.md всех скиллов написаны заново (на русском, под пайплайн и структуру `design/` этого плагина). Методология в `references/` адаптирована (сокращена, переведена частично, отвязана от инфраструктуры исходников). Файлы, скопированные почти без изменений, помечены в шапке «Copied from …».

## Карта заимствований

| Файл в плагине | Источник | Характер |
|---|---|---|
| `skills/gd-router/*` | gstack-game `triage`; Claude-Code-Game-Studios `start`, `project-stage-detect`, `gate-check` | Идеи (определение стадии по артефактам, gate-критерии); текст свой |
| `skills/gd-concept/references/concept-frameworks.md` | gstack-game `spark-lens`, `game-ideation`; CCGS `brainstorm`, `game-pillars` template | Адаптация |
| `skills/gd-systems-map/references/systems-taxonomy.md` | CCGS `map-systems`, `systems-index` template | Адаптация |
| `skills/gdd-author/references/gdd-template.md`, `templates/design/gdd/_template.md` | CCGS `game-design-document` template, `quick-design` | Адаптация |
| `skills/gdd-review/references/rubric.md`, `anti-sycophancy.md` | gstack-game `game-review/references/*` | Адаптация |
| `skills/gdd-review/references/cross-gdd.md` | CCGS `review-all-gdds`, `consistency-check`, `design-review` | Адаптация |
| `skills/game-feel/references/feel-model.md` | gstack-game `feel-pass`, `build-playability-review`, `player-experience` | Адаптация |
| `skills/balance-check/references/balance-methods.md` | gstack-game `balance-review/references/*`; CCGS `balance-check` | Адаптация (+ свои разделы: карты, кооп-роли) |
| `skills/scope-check/references/estimation.md` | CCGS `scope-check`, `estimate`; gstack-game `game-review/risk` (Lake/Ocean) | Адаптация (+ своя калибровка оценок) |
| `skills/gd-handoff/references/slice-and-handoff.md` | gstack-game `prototype-slice-plan`, `implementation-handoff` | Адаптация (+ тип Narrative slice) |
| `skills/narrative-structure/references/narrative-models.md` | CCGS агенты `narrative-director`, `world-builder`; narrative-skills `if-design-structure`, `continuity-check`; gstack-game ludonarrative-таблица | Адаптация (+ таблица структур ветвления — своя) |
| `skills/character-voice/references/character-models.md` | narrative-skills `create-character-bible`, `define-style-bible`, `if-design-dialogue`; CCGS `narrative-director` | Адаптация |
| `skills/ink-slice/references/slice-plan.md` | narrative-skills `if-plan-ink-slice`, `if-design-progression`, `if-draft-ink`, `if-playtest-review` | Адаптация |
| `skills/ink-slice/references/ink-syntax.md` | narrative-ink-skills `ink-syntax/SKILL.md` | **Копия** (изменены шапка и одна ссылка) |
| `skills/ink-slice/references/ink-syntax-extended.md` | narrative-ink-skills `ink-syntax/reference.md` | **Копия** |
| `skills/ink-slice/references/ink-style-rules.md` | narrative-ink-skills `ink-style/rules.md` | **Копия** |
| `agents/design-critic.md` | gstack-game `game-review` (anti-sycophancy) | Идеи; текст свой |
| `agents/narrative-designer.md` | CCGS `narrative-director`, `writer` | Идеи; текст свой |
| `agents/producer.md` | CCGS `producer` | Идеи; текст свой |
| `skills/art-direction/references/art-method.md` | CCGS `art-bible` template; gstack-game `asset-review/naming-conventions`, `game-visual-qa/visual-thresholds` | Адаптация (роли палитры, пары проверки, формат asset-list — свои) |
| `skills/audio-direction/references/audio-method.md` | CCGS `sound-bible` template; unity-kit `unity-audio` | Адаптация (связь с Feedback GDD и FMOD-соглашение — свои) |
| `skills/ux-onboarding/references/ux-method.md` | gstack-game `game-visual-qa/visual-thresholds` (пороги тач-целей и текста) | Частично; остальное своё, чеклист доступности — пересказ публичных Game Accessibility Guidelines (Basic) |
| `skills/tech-design/references/tech-method.md` | unity-kit `unity-playtest` (read-only свойства состояния) | Идея; остальное своё |
| `skills/qa-plan/references/qa-method.md` | CCGS `qa-plan` (классы тестов); unity-kit `unity-verify`, `unity-ci` | Идеи; формат и трассировка по ID — свои |
| `skills/playtest/references/playtest-method.md` | gstack-game `playtest` (SKILL.md, analysis-framework) | Адаптация (коды наблюдения, скрипт, адресация — свои) |
| `agents/art-director.md`, `audio-director.md`, `qa-lead.md`, `playtest-analyst.md` | unity-kit `playtest-qa` (принцип «доказательства, а не вердикты») | Идея; структура — свой `design-critic`, текст свой |
| `gd-build/skills/slice-build/references/verify-loop.md` | unity-kit `unity-verify`, `unity-playtest` | Адаптация |
| `gd-build/skills/slice-build/scripts/gen_sfx.py` | unity-kit `scripts/gen-sfx.py` | Адаптация (рецепты по имени, новые звуки, префикс) |
| `gd-build/skills/qa-run/references/qa-run-method.md` | unity-kit `unity-ci`, `unity-verify`, `unity-playtest` | Адаптация |
| `gd-build/skills/qa-run/scripts/run-tests-headless.ps1`, `.sh`, `find-unity.ps1`, `.sh` | unity-kit `scripts/*` | **Копия** (изменены шапка, код выхода при падениях, фильтр `.meta`, поиск редактора) |
| `gd-build/skills/feature-build/references/code-review-checklist.md`, `gd-build/agents/code-reviewer.md` | gstack-game `gameplay-implementation-review` (Pass 0 «Design Intent Survival», `pass1-critical.md`, `pass2-informational.md`) | Адаптация (без преамбулы, телеметрии, авто-исправлений; привязка к ID GDD и Config map — своя) |
| `gd-build/skills/juice-build/references/juice-method.md` | awesome-gamedev-agent-skills `disciplines/game-feel` (Apache-2.0) | Сверка чеклиста техник; текст свой |
| `gd-build/skills/ui-build/references/ui-method.md` | CCGS агенты `ui-programmer`, `unity-ui-specialist`; Nice-Wolf-Studio/unity-claude-skills `unity-ui-patterns` | Идеи; текст свой |
| `gd-build/skills/asset-integrate/references/import-method.md` | blender-skills `asset-optimization`; CoplayDev/unity-mcp `.claude/skills/blender-to-unity` | Адаптация чеклиста; шов «файл на диске» и выбор GLB |
| `gd/skills/gd-handoff/references/milestone.md` | CCGS `gate-check` (идея гейта майлстоуна) | Идея; формат свой |
| `gd-build/skills/perf-check/references/perf-method.md` | CCGS `perf-profile`; tjboudreaux/cc-plugin-unity-gamedev `tools-unity-profiling`, `eng-unity-mobile-optimization` (MIT) | Идеи (фазы, формат отчёта, FrameTimingManager); текст и `compare_perf.py` свои |
| `gd-build/skills/build-release/references/release-method.md` | CCGS `release-checklist`, `day-one-patch`, `hotfix`; game-ci/unity-builder, unity-test-runner (MIT) — как GitHub Actions | Идеи путей патча и отката; шаблон workflow свой, Actions используются, код не копировался |
| `gd-build/skills/model-build/references/model-method.md`, `scripts/blender_blockout.py` | blender-skills `blender-modeler`, `lod-pipeline`, `export-pipeline`, `qa-review`; CoplayDev/unity-mcp `.claude/skills/blender-to-unity` | Адаптация чеклистов; скрипты `blender_blockout.py`, `check_glb.py` свои |
| `gd-build/skills/sfx-design/references/sfx-method.md`, `scripts/synth_sfx.py`, `scripts/loudness.py` | unity-kit `unity-audio` (честность проверки); CCGS `team-audio`, агент `sound-designer` (слои); ITU-R BS.1770-4 и формулы K-фильтра libebur128 / pyloudnorm (MIT) | Идеи и формулы; код свой (`gen_sfx.py` из unity-kit не менялся, v2 написан заново) |
| `gd-build/skills/music-build/references/music-method.md`, `scripts/*` | sirruf/music-gen-skill (MIT) — маршрут MIDI → FluidSynth → WAV | Идея маршрута; `render.sh` не копировался, `mido` заменён записью SMF на stdlib. FluidSynth (LGPL-2.1) — внешняя программа; FluidR3_GM (MIT, Frank Wen) — внешний файл, в репозиторий не входит |
| `gd-build/skills/anim-build/references/anim-method.md` | blender-skills `rigging`, `animation`; Nice-Wolf-Studio `unity-animation`; tjboudreaux `tools-unity-animation` (MIT) | Идеи и чеклисты; текст свой |
| `research/2026-09-production-cycle-architecture.md` | все источники из §9 документа | Ресерч; код не взят |

Проверено по документации, код не взят: FMOD Studio Scripting API (локальная документация FMOD Studio 2.03.14), `fmodstudiocl` (Advanced Topics). В `vendor/` также изучены, но пока не использованы: GarrettPetersen/indie-game-marketing-skills (волна C). ahujasid/mcp-for-blender (MIT + Terms of Use) — ставится как внешний инструмент (аддон + MCP-сервер), код не копировался; запрещённые инструменты перечислены в `model-build`.

Справочник Ink в narrative-ink-skills пересказывает документацию inkle «Writing with ink» (https://github.com/inkle/ink, MIT © inkle Ltd).

Не использовано: bash-преамбулы, телеметрия и бинарники gstack-game; оркестрация субагентов и студийная иерархия CCGS; движковые специалисты; «романные» скиллы narrative-skills; `ink-testing` и `format-ink.py` из narrative-ink-skills.

Сверено, но не заимствовано: имена инструментов CoplayDev/unity-mcp (MIT) и IvanMurzak/Unity-MCP (Apache-2.0) — только как справочник действий; API FMOD Studio — по выгрузке справочника в raffyknowsnothing/fmod-studio-mcp (MIT) и вызовам в xDarkzx/Dans_Fmod_Studio_MCP (Apache-2.0), код не взят. Официальный Unity Plugin (Unity Companion License) — не копировался. Кандидаты без лицензии или с GPL (hiddenpeopleclub/claude-code-plugins, PixelLab MCP, AltTester SDK) не использовались — см. `research/2026-09-full-cycle.md`.

---

## fagemx/gstack-game — https://github.com/fagemx/gstack-game

```
MIT License

Copyright (c) 2026 fagemx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Donchitos/Claude-Code-Game-Studios — https://github.com/Donchitos/Claude-Code-Game-Studios

```
MIT License

Copyright (c) 2026 Donchitos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## bladecoder/narrative-skills — https://github.com/bladecoder/narrative-skills

```
MIT License

Copyright (c) 2026 Rafael García Moreno

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## spaceninja/narrative-ink-skills — https://github.com/spaceninja/narrative-ink-skills

```
MIT License

Copyright (c) 2026 Scott Vandehey

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Benjamin-Curlier/unity-kit — https://github.com/Benjamin-Curlier/unity-kit

```
MIT License

Copyright (c) 2026 Benjamin Curlier

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## arjun988/blender-skills — https://github.com/arjun988/blender-skills

```
MIT License

Copyright (c) 2026 blender-skills contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## CoplayDev/unity-mcp — https://github.com/CoplayDev/unity-mcp

```
MIT License

Copyright (c) 2025 CoplayDev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Nice-Wolf-Studio/unity-claude-skills — https://github.com/Nice-Wolf-Studio/unity-claude-skills

```
MIT License

Copyright (c) 2026 Nice-Wolf-Studio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## gamedev-skills/awesome-gamedev-agent-skills — https://github.com/gamedev-skills/awesome-gamedev-agent-skills

Apache License 2.0. Полный текст — `licenses/Apache-2.0.txt`, NOTICE источника — `licenses/NOTICE-awesome-gamedev-agent-skills.txt`.
Copyright 2026 Abhishek Barali and the awesome-gamedev-agent-skills contributors. Использовано: сверка чеклиста техник game feel (`disciplines/game-feel`); текст `juice-method.md` написан заново, файлы не копировались и не изменялись.
