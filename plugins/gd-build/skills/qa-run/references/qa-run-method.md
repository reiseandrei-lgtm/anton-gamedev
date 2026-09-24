# QA-прогон: headless, MCP, smoke, отчёт

> Адаптировано из unity-kit `unity-ci`, `unity-verify`, `unity-playtest` (MIT © 2026 Benjamin Curlier). См. ATTRIBUTION.md. Скрипты `run-tests-headless.*` и `find-unity.*` — копии из unity-kit с шапкой источника. Сопоставление с T-ID и формат отчёта — свои.

## 1. Headless: что ломается
- **Открытый редактор = мгновенный отказ** (один редактор на проект, `Temp/UnityLockfile`). Закрой его или используй MCP. Закрыть через MCP: `manage_scene save`, затем `execute_menu_item` `File/Exit` (`EditorApplication.Exit` в `execute_code` заблокирован защитой — и правильно).
- **Не передавай `-quit` вместе с `-runTests`**: раннер завершится сам, `-quit` может убить его посреди прогона.
- **0 тестов с exit 0** — не успех: тестовая asmdef без `UnityEngine.TestRunner` / `UnityEditor.TestRunner`, ссылка на несуществующую сборку или фильтр ничего не нашёл. Скрипт возвращает 3.
- **Windows**: `Unity.exe` — GUI-бинарник, `&` возвращается сразу; скрипт ждёт процесс через `WaitForExit()`.
- **`-nographics`**: для EditMode безопасно; PlayMode с рендером — без флага.
- **Первый прогон** на чистом клоне импортирует `Library` — минуты, не секунды. Не ставь короткий таймаут.
- **Лицензия** Unity должна быть активирована на машине: Hub запущен, выполнен вход, лицензия Personal активна (бесплатно). Устаревший `UnityEntitlementLicense.xml` на диске не помогает: batchmode падает с кодом 198 и строкой `No valid Unity Editor license found` в логе — это шаг пользователя, не чинится скриптом.
- **Код выхода берётся из XML, не только от Unity**: в PowerShell 5.1 `ExitCode` процесса без заранее взятого `Handle` пустой, и до gd-build 0.1.2 упавший тест давал exit 0. Теперь любой `failed > 0` в XML = exit 2.
- **Предупреждение «run modified the working tree»** срабатывает на изменение отслеживаемых файлов. Новые `.meta` для новых ассетов — это импорт, их скрипт не считает.
- **Нестандартная папка редакторов** (Hub → Settings → Installs location) читается из `%APPDATA%/UnityHub/secondaryInstallPath.json` — `preflight.py` и `run-tests-headless.ps1` её учитывают.

## 2. Через MCP (CoplayDev)
1. В v10 группа `testing` активна по умолчанию; в старых версиях — `manage_tools` → activate group `testing`. Перед прогоном — доказанная компиляция (`slice-build/references/verify-loop.md` §1): при ошибках компиляции `run_tests` прогонит старую DLL.
2. `run_tests` `mode: EditMode` → `job_id` → `get_test_job` с ожиданием 30–60 с. Потом `PlayMode`.
3. Зависание с `completed=0` и `InitTestScene` в редакторе — упал Test Framework: вернуть рабочую сцену, повторить, при повторе — перезапуск редактора.

## 3. Smoke
Шаги smoke-набора тест-плана по порядку:
- шаг покрыт автотестом → результат теста;
- шаг видимый → play mode, проба read-only свойства, скриншот Game view, консоль на исключения, stop;
- шаг «на ощупь» → чеклист человеку, в отчёте «ручной, не выполнен ассистентом».
Сравни `Time.frameCount` в начале и конце: 0 кадров — прогон ничего не доказал.

## 4. Структурированная сессия (для поиска багов, не только smoke)
- План до игры: проверяемая цель, пробы с ожидаемыми корзинами значений (счёт 0 / 1–5 / > 5), ≤ 6 действий на уровне намерения, бюджет действий ≤ 15.
- Только действия из плана.
- 3 действия подряд без изменения проб → стоп, запиши гипотезу застревания (это доказательство, часто это и есть баг).
- Оракулы всегда: исключения в консоли каждые 2–3 действия, бюджет как предохранитель, расхождение скриншота и состояния.
- Отчёт — доказательства, а не вердикт: что сделано, что показали пробы, что видно на скриншоте, аргументы за и против цели.

## 5. Отчёт qa/runs/YYYY-MM-DD-<slice>.md

```markdown
---
status: draft
updated: YYYY-MM-DD
slice: <slice>
mode: mcp | headless | plan
build: <commit>
verdict: PASS | FAIL | INCOMPLETE
---
# QA run — <slice>
## Totals
EditMode a/b · PlayMode c/d · smoke e/f (ручных: g) · длительность
## Failures
| Test | T-ID | Сообщение | BUG |
## Plan tests not in run
T-ID автоматизируемых тестов плана без реализации.
## Smoke
| Шаг | Как проверено | Итог | Доказательство |
## Skipped & why
## Screenshots
путь — что на нём видно
```
Вердикт: PASS — всё зелёное, smoke пройден, нет S1/S2 · FAIL — есть падения или S1/S2 · INCOMPLETE — прогон не завершился или часть не запускалась.

## 6. Баг-репорт qa/bugs/BUG-NNN.md
Номер — следующий свободный в `design/qa/bugs/`.
```markdown
---
status: open        # open | fixed | wontfix | duplicate
severity: S2        # S1 блокер · S2 ломает гипотезу/ED · S3 есть обход · S4 косметика
found: YYYY-MM-DD
build: <commit>
covers: <system>#R1, T-<system>-01
---
# BUG-NNN: <что сломано, одной фразой>
## Steps
## Expected
## Actual
## Evidence
тест / лог консоли / скриншот
## Notes
частота (всегда / 1 из N), платформа
```
Воспроизводимый автоматически баг — сначала падающий тест с T-ID, потом ссылка на него в `covers`.

## 7. Soak: design/qa/perf/<date>-soak.md
```markdown
---
status: draft
updated: YYYY-MM-DD
platform: editor | <устройство>
build: <commit>
scene: <сцена>
duration: 600          # секунд
input: idle | scripted (что делает скрипт ввода)
---
# Soak — <slice>
## Samples
| t (s) | frame ms | memory MB | exceptions |
|---|---|---|---|
| 0 | 4.1 | 212 | 0 |
## Verdict
вывод check_soak.py дословно
```
Замер: `manage_profiler` `get_frame_timing` (кадр, мс) и `get_counters` категории Memory (Total Used Memory, Material Count, Game Object Count) каждые 30 с; исключения — `read_console` `types: [error, exception]`. Редактор ≠ устройство: в отчёте платформа, выводы о бюджетах — только с устройства (`perf-check`).

**Скрипт ввода обязан доказать, что играл**: колонка `progress (…)` — действия, которые подтвердила сама игра (например, состояние `Airborne` после прыжка). Проба, упавшая с ошибкой, в MCP возвращается строкой, а не исключением: без колонки progress soak может 6 минут «играть» в замершую игру (SK6).

## 8. Visual: эталоны design/qa/visual/
- `qa/visual/<T-ID>.png` — эталон, утверждённый человеком; `qa/visual/_pending/` — кандидаты; `qa/visual/README.md` — таблица `Case · Scene · Camera · Resolution · Seed · Tolerance · Approved (дата, кто)`.
- Детерминизм: фиксированный seed генерации (seam вроде `Reseed(seed)`), дождаться, пока камера догонит цель, пауза (`timeScale = 0`) перед снимком. Без seed разные забеги дают разные кадры — это не баг, а негодный кейс. Проверка: два снимка подряд с одним seed → `diff_png` 0 %.
- Разрешение цели без смены Game view: кадр игры — рендер камеры в `RenderTexture(w, h)` через `execute_code` (`cam.targetTexture = rt; cam.Render(); ReadPixels; EncodeToPNG`); UI Toolkit — `PanelSettings.targetTexture = RenderTexture(w, h)`, подождать кадр, прочитать, вернуть `null`. `render_ui` в play mode размер игнорирует (`slice-build/references/mcp-actions.md`).
- Меняющиеся области (таймер, счёт, частицы) — `--mask x,y,w,h`.
- `diff_png.py`: VD1 размер · VD2 доля отличий > допуска · VD3 макс. разница канала · VD4 нет эталона. Diff-PNG: отличия красным поверх серого снимка — посмотри на него.
