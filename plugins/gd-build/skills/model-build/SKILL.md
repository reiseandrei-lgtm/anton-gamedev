---
name: model-build
description: >-
  3D-модели в Blender по строке design/art/asset-list.md: блокаут по габаритам → материалы по ролям палитры → LOD → экспорт в GLB → турнтейбл из 8 кадров для ревью; headless-скриптом Blender или через бесплатный Blender MCP. Бюджет треугольников и материалов, имена, габариты, LOD и клипы проверяются скриптом.
  Триггеры RU: «смоделируй», «сделай модель», «блокаут в Blender», «сделай LOD», «экспортируй в GLB».
  Triggers EN: "model the", "make a 3D model", "Blender blockout", "generate LODs", "export to GLB".
  Не для визуального стиля и списка ассетов (gd:art-direction), не для импорта в Unity (asset-integrate), не для генерации моделей ИИ.
---

# model-build

Ты делаешь модель, которая уже описана в asset-list, и доказываешь её параметры числами `check_glb.py`. Стиль не выбираешь: роли цветов и силуэт — из `art-bible.md`.

## 0. Preflight
`python3 ../slice-build/scripts/preflight.py --for model`: Blender (путь, версия), Blender MCP (аддон, сервер). Есть Blender → headless-канал; есть MCP → доводка формы; нет Blender → режим plan (спецификация, ⚠️).

## 1. Вход
Строка `design/art/asset-list.md` (ID, Size, Budget, States / frames), `design/art/art-bible.md` (hex ролей, силуэты), путь Unity-проекта игры.

## 2. Алгоритм (детали и каналы — `references/model-method.md`)
1. Блокаут и экспорт: `blender --background --factory-startup --python scripts/blender_blockout.py -- --id <ID> --shape … --size X×Y×Z --colors <hex ролей> --out <unity>/Assets/_Project/Art/Models/<ID>.glb --blend art-source/<ID>.blend [--lod 0.5,0.25] --turntable design/art/models/<ID>`.
2. Доводка формы — Blender MCP (`execute_blender_code`) или человек; повторный экспорт тем же путём.
3. `python3 scripts/check_glb.py <ID>.glb --asset-list design/art/asset-list.md` → вывод в `design/art/models/<ID>/<ID>.md`.
4. **Посмотри на турнтейбл**: силуэт читается, роли цветов на месте. Ревью — агент `gd:art-director` с путями на турнтейбл и `<ID>.md`.
5. Импорт в Unity — `asset-integrate` (копия GLB + refresh; группу `asset_gen` не включать).

## Done
`check_glb.py` без FAIL; 8 кадров турнтейбла; `.blend` и GLB на месте; статус в asset-list не `made` (его ставит человек).

## Правила
Язык ответа = язык запроса. Запрещено вызывать `create_rodin_job`, `create_hunyuan_job`, `download_sketchfab_model` и любые платные генераторы моделей. Hero-ассеты — только блокаут, финал 🟨. Телеметрия Blender MCP выключена (`DISABLE_TELEMETRY=true`).
