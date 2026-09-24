---
name: anim-build
description: >-
  Анимация в Unity: процедурная (пружины, IK через Animation Rigging, физические сочленения — основной путь для модульных тел) или риг и ключи в Blender с экспортом клипов в GLB; успокоение пружин и длительности клипов в кадрах сверяются с целями Game Feel и asset-list.
  Триггеры RU: «анимируй», «процедурная анимация», «процедурная походка», «настрой IK», «риг в Blender», «анимационный клип».
  Triggers EN: "animate the", "procedural animation", "procedural walk", "set up IK", "rig in Blender".
  Не для отклика на события — частиц, тряски, хитстопа (juice-build), не для моделирования (model-build), не для оценки ощущения (gd:game-feel).
---

# anim-build

Ты реализуешь движение тела, заданное в GDD и asset-list, и доказываешь тайминг числом кадров. Ощущение не оцениваешь.

## 0. Preflight
`python3 ../slice-build/scripts/preflight.py <unity-project> --for anim`: канал MCP, пакет `com.unity.animation.rigging`, Blender для клипов. Нет MCP → компоненты и тесты на диск, ⚠️; нет Blender → клипы в режиме plan.

## 1. Вход
Game Feel GDD системы (цели в кадрах: «пружина успокаивается ≤ 12 кадров», «перелёт ≤ 10 %»), `design/art/asset-list.md` (тип `anim`, `States / frames`), `tech/architecture.md` (Config map).

## 2. Алгоритм (детали — `references/anim-method.md`)
1. Выбор пути на каждое движение: процедурный / Animation Rigging / клип (таблица §1 метода).
2. Процедурный: компонент пружины, параметры в ScriptableObject; PlayMode-тест с `captureFramerate = 60` меряет кадры успокоения и перелёт.
3. Rigging: констрейнты через `manage_components`; тест — поза достигнута за N кадров.
4. Клип: риг и ключи в Blender (MCP или человек) → GLB → `python3 ../model-build/scripts/check_glb.py <ID>.glb --asset-list design/art/asset-list.md --fps 30`.
5. Verify loop (`slice-build/references/verify-loop.md`), скриншот позы — **посмотри на него**.
6. Лог: `## Juice` (движение из Feedback) → `python3 ../juice-build/scripts/check_juice.py …`; остальное — `## Anim`.

## Done
Каждое движение из GDD/asset-list — замер в кадрах или ⛔ с причиной; `check_glb.py` / `check_juice.py` без FAIL; консоль чистая.

## Правила
Язык ответа = язык запроса. Параметры движения — только из конфигов. Платные генераторы анимации и мокапа не использовать. Главный персонаж — hero-ассет: финальная анимация 🟨.
