# Attribution

Плагин `gd` частично основан на материалах четырёх репозиториев под лицензией MIT. Ниже — что откуда взято и полные тексты лицензий, как требует MIT.

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

Справочник Ink в narrative-ink-skills пересказывает документацию inkle «Writing with ink» (https://github.com/inkle/ink, MIT © inkle Ltd).

Не использовано: bash-преамбулы, телеметрия и бинарники gstack-game; оркестрация субагентов и студийная иерархия CCGS; движковые специалисты; «романные» скиллы narrative-skills; `ink-testing` и `format-ink.py` из narrative-ink-skills.

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
