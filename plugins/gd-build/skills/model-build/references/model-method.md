# 3D-модели: метод, каналы, бюджеты

Источники: arjun988/blender-skills `blender-modeler`, `lod-pipeline`, `export-pipeline`, `qa-review` (MIT) — чеклисты, адаптация; CoplayDev `blender-to-unity` (MIT, в unity-mcp) — шов «файл на диске», GLB вместо FBX. Код не копировался.

## 1. Каналы (в порядке предпочтения)
| Канал | Когда | Как |
|---|---|---|
| headless Blender | всегда, если есть `blender` (preflight `--for model`) | `blender --background --factory-startup --python scripts/blender_blockout.py -- …` — блокаут, материалы ролей, LOD, GLB, турнтейбл. Детерминированно, без GUI |
| Blender MCP (ahujasid/mcp-for-blender, MIT) | Blender открыт, аддон «MCP for Blender» включён, сервер `blender` в Claude Code | `get_scene_info`, `execute_blender_code` (bpy), `get_viewport_screenshot` — доводка формы поверх блокаута; экспорт и турнтейбл — тем же `blender_blockout.py` или bpy-кодом из него |
| без Blender | нет ни того, ни другого | режим plan: спецификация (габариты, силуэт, роли цветов, бюджет), ⚠️ |

**Запрещено** в Blender MCP (платно, ключи API, лицензии моделей разные): `create_rodin_job` (Hyper3D), `create_hunyuan_job`, `download_sketchfab_model`, генерация через Poly Haven — только CC0-текстуры по решению человека. Телеметрия сервера — `DISABLE_TELEMETRY=true` в `claude mcp add … -e`.

Установка Blender MCP (один раз, 🟨 подтверждает человек): `uvx --from mcp-for-blender==<версия> mcp-for-blender install-addon --addons-dir "%APPDATA%\Blender Foundation\Blender\<X.Y>\scripts\addons"` → включить аддон (`bpy.ops.preferences.addon_enable(module='blender_mcp')` + `save_userpref`) → `claude mcp add blender --scope user -e DISABLE_TELEMETRY=true -- uvx --from mcp-for-blender==<версия> mcp-for-blender`. Инструменты появятся в новой сессии; сокет аддона — `localhost:9876` (автостарт при открытии Blender с GUI).

## 2. Шаги
1. **Спецификация из asset-list**: ID, `Size` (метры; 1 u = 1 м), `Budget` (`N tris, M mat`), роль цвета из `art-bible.md` (hex роли, не «похожий»), состояния.
2. **Блокаут**: примитив по габаритам, опора на землю (pivot внизу по центру — Unity ставит объект на пол без смещения). Силуэт читается в 64 px — проверь турнтейбл.
3. **Модель**: доводка формы (MCP `execute_blender_code` или человек). Hero-ассеты (главный персонаж, ключевой арт) — 🟨, скилл делает только блокаут.
4. **UV и материалы**: один материал на роль палитры (бюджет batches), без текстур там, где хватает цвета вершины / материала.
5. **LOD**: `--lod 0.5,0.25` (Decimate) для объектов, которые бывают далеко; LOD0 = полный меш, `<ID>_LOD0…N`. В Unity — LOD Group по именам (asset-integrate).
6. **Экспорт**: GLB, Y-up, масштаб применён, анимации только если есть клипы. Путь `Assets/_Project/Art/Models/<ID>.glb` игры; исходник `.blend` — `art-source/<ID>.blend` (под LFS).
7. **Турнтейбл**: 8 кадров по 45°, EEVEE, `design/art/models/<ID>/turntable_01…08.png` + `<ID>.md` с выводом `check_glb.py` (tris, материалы, габариты, LOD) — вход агента `gd:art-director`.

## 3. Проверка
`python3 scripts/check_glb.py <ID>.glb --asset-list design/art/asset-list.md` — GL1…GL9 (коды — в docstring скрипта). Габариты считаются по POSITION min/max × масштаб узлов без вращения: для повёрнутых узлов — приблизительно.

## 4. Возвраты
Сверх бюджета → LOD / упрощение или `gd:tech-design` (пересмотр бюджета, ADR). Силуэт не читается у ревьюера → `gd:art-direction` (правило силуэта) или доводка формы. Статус `made` в asset-list ставит человек.
