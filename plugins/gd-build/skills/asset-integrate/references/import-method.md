# asset-integrate: импорт и замена плейсхолдеров

Свой документ. Чеклист оптимизации — blender-skills `asset-optimization` (MIT, © 2026 blender-skills contributors), адаптирован к Unity. Шов «Blender → файл на диске → Unity» и выбор GLB — CoplayDev/unity-mcp `.claude/skills/blender-to-unity` (MIT). API Unity — официальная документация.

## 1. Папки
```
Assets/_Project/Art/Models/<ID>.glb
Assets/_Project/Art/Textures/<ID>.png
Assets/_Project/Art/Sprites/<ID>.png        (+ атлас на экран: Atlas_<screen>.spriteatlas)
Assets/_Project/Art/Materials/M_<role>.mat  (один материал на роль палитры, где возможно)
Assets/_Project/Audio/SFX|Music/<file>.wav  (имена — из design/audio/files.md)
```
Имя файла = ID из asset-list. Варианты LOD: `<ID>_LOD0.glb`… Плейсхолдер: `ph_<ID>.<ext>`.

## 2. Настройки импорта
| Тип | Настройка | Откуда число |
|---|---|---|
| Текстура | Max Size ≤ Budget px; сжатие по платформе; mipmaps для 3D, без — для UI | asset-list Budget, `tech/budgets.md` |
| Спрайт | Sprite Mode, Pixels Per Unit (единый в проекте), атлас на экран/уровень | art-bible (масштаб) |
| Модель GLB | glTFast: scale 1, материалы → заменить на `M_<role>` при роли из палитры; коллайдер отдельным мешем `_col` | asset-list Size, Budget |
| Звук | короткие SFX — Decompress On Load; музыка — Streaming; моно для 3D | audio-bible |

Изменение настроек — через MCP (`manage_texture`, `manage_asset`) и refresh; `.meta` руками не править.

## 3. Замена плейсхолдера
1. Новый файл импортирован, `check_import.py` его видит.
2. В сцене/префабе ссылка переводится на новый ассет (MCP `manage_components` / `manage_prefabs`), не удалением-созданием объекта (иначе теряются ссылки).
3. Play mode + скриншот того же кадра, что и до замены; посмотри: масштаб, цвет роли, силуэт.
4. Только после этого удалить `ph_`-файл; в asset-list Status меняет человек.

## 4. Проверка
`check_import.py`: IM1 сирота · IM2 нет файла у cc0/made · IM3 ph_ у made (и у mvp на Beta) · IM4 текстура > Budget · IM5 GLB > Budget tris · IM6 cc0 без URL · IM7 файл из files.md · IM8 на Beta ассет mvp / slice всё ещё placeholder или todo.
