# Milestone handoff (Alpha / Beta)

Свой документ. Идея «гейт майлстоуна с критериями выхода» — CCGS `gate-check` (MIT, см. ATTRIBUTION.md). Формат ID и связь с логами `gd-build` — свои.

Хендофф слайса отвечает «проверяем ли гипотезу». Хендофф майлстоуна отвечает «что должно работать к Alpha / Beta и как это доказать». Он появляется после решения `advance` в `decisions-log.md` (стадия 12 → 13).

## Когда какой майлстоун
| Майлстоун | Что внутри | Плейсхолдеры | Выход (стадия 13) |
|---|---|---|---|
| Alpha | все системы с приоритетом ≤ Alpha в `systems-map.md` работают по GDD | да, отличимые (`ph_`, цвета ролей) | у каждой системы лог `build/<system>.log.md`: каждое R / F / E — ✅ или ⛔ с решением в `decisions-log.md`; ревью кода не FAIL; `qa-run` PASS |
| Beta | Alpha + весь контент из `scope.md` (Lake) | нет в ассетах `mvp` | то же + `check_import.py` без `ph_` у `mvp`, `check_audio_files.py` без `ph_` в финальных событиях |

## Шаблон `handoff/<milestone>.md`
```markdown
---
status: draft
updated: YYYY-MM-DD
type: milestone
milestone: alpha        # alpha | beta
decision: decisions-log.md, YYYY-MM-DD (advance)
---
# Handoff: <milestone>

## 1. Цель майлстоуна (одна фраза)
## 2. Системы (порядок = порядок реализации по зависимостям)
| System | GDD | Приоритет | Зависит от | Уже есть (слайс) |
|---|---|---|---|---|

## 3. Критерии по системам
### <system>
- [ ] ED-<system>-1 правила R1–Rn и edge cases E1–En работают (тесты по test-plan)
- [ ] ED-<system>-2 …
- [ ] DD-<system>-1 игрок <наблюдаемое поведение> (проверка — playtest)

## 4. Контент (только Beta; конечный список из scope.md)
| Что | Сколько | Где список |
|---|---|---|
| зоны / уровни | 4 | levels/*.md |
| ассеты mvp | N | art/asset-list.md |
| события звука | N | audio/event-map.md |

## 5. Критерии выхода
- [ ] все ED-* закрыты: ✅ или ⛔ с решением
- [ ] ревью кода каждой системы не FAIL
- [ ] qa-run PASS, нет открытых S1 / S2
- [ ] (Beta) контент по §4, без `ph_` в mvp
- [ ] сыграл кто-то, кроме разработчика

## 6. Риски и соблазнительные срезы
| Risk | Shortcut | Why it kills it |
|---|---|---|
```

## Правила
- ID критериев: `ED-<system>-N`, `DD-<system>-N` (`system` — имя файла GDD). На них ссылаются тест-план и логи `gd-build`.
- Система без GDD в `approved` / `review` в майлстоун не входит: сначала `gdd-author`.
- Порядок систем — топологический по `Depends on`; цикл → назад в `gd-systems-map`.
- Числа (сроки, объёмы) — ГИПОТЕЗА; оценка трудозатрат — `scope-check`, не хендофф.
