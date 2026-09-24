# Анимация: процедурный путь и клипы

Источники: arjun988/blender-skills `rigging`, `animation` (MIT); Nice-Wolf `unity-animation` (MIT); tjboudreaux `tools-unity-animation` (MIT) — идеи и чеклисты, код не копировался. How-to по API Animation Rigging — официальный Unity Plugin / документация пакета.

## 1. Какой путь
| Движение | Путь |
|---|---|
| Отклик тела на ввод, покачивание, «желе», хвосты, антенны, модульные тела (MEATFORM) | **процедурный**: пружины (damped spring) в компоненте |
| Ноги по поверхности, взгляд, дотягивание руки | **Animation Rigging** (`com.unity.animation.rigging`, в поставке Unity 6000.3): Two Bone IK, Multi-Aim, Damped Transform |
| Персонажный цикл (ходьба, атака), который нельзя вывести из физики | **клип**: риг и ключи в Blender → GLB с анимациями → Animator |

## 2. Процедурная пружина (шаблон)
Критически демпфированная пружина по времени (не по кадрам): `x'' = ω²(target − x) − 2ζω x'`, интеграция полунеявным Эйлером в `LateUpdate` (после логики, до рендера). Параметры — в ScriptableObject-конфиге (Config map из `tech/architecture.md`): `frequency` (Гц), `damping` (ζ, 1 = без перелёта), `maxOffset`. Литералы в коде — находка ревью (`code-reviewer`).

Замер: PlayMode-тест с `Time.captureFramerate = 60` — ступенчатое изменение цели → число кадров, пока `|x − target| < ε` («успокаивается за ≤ N кадров»), и максимальный перелёт в %. Цели берутся из Game Feel GDD; нет числа → стоп, `gd:game-feel`.

## 3. Клип из Blender
1. Риг: арматура с именами костей по соглашению игры; веса автоматически, затем правка. Процедурные вторичные движения (хвосты) — в Unity, не в клипе.
2. Ключи: длительность каждого клипа — из `States / frames` asset-list (`idle 24f, walk 32f`) при fps проекта (по умолчанию 30). Имя Action = имя клипа.
3. Экспорт GLB с анимациями (`export_animations=True`), проверка `../model-build/scripts/check_glb.py <ID>.glb --asset-list … --fps 30` (GL5 клип отсутствует, GL6 длительность вне ±1 кадра).
4. Проверка пути без рига: `../model-build/scripts/blender_blockout.py … --clip idle:24` даёт клип-покачивание — не финальная анимация.

## 4. Лог
Раздел `## Juice` лога системы (формат `slice-build/references/build-log.md`), строка на движение, связанное с Feedback GDD: FB, событие, цель (кадры), замер (кадры), допуск, доказательство (имя теста). Проверка — `../juice-build/scripts/check_juice.py` (JU1, JU2). Движения вне Feedback — таблица `## Anim` в том же логе: движение · цель · замер · тест.
