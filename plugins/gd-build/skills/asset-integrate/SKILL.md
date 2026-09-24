---
name: asset-integrate
description: >-
  Импорт ассетов в Unity по design/art/asset-list.md и design/audio/files.md: копирование в Assets, настройки импорта текстур, моделей и звука, атласы, материалы по ролям палитры, замена плейсхолдеров; ID, бюджеты, лицензии и остатки ph_ проверяются скриптом. Без MCP — план и чеклист.
  Триггеры RU: «импортируй ассеты», «замени плейсхолдеры», «настрой импорт текстур», «собери атлас», «подключи модели в Unity».
  Triggers EN: "import the assets", "replace placeholders", "texture import settings", "build the sprite atlas", "bring models into Unity".
  Не для стиля и списка ассетов (gd:art-direction), не для создания моделей (model-build), не для событий звука в FMOD (fmod-sync), не для генерации ассетов ИИ.
---

# asset-integrate

Ты заводишь в Unity готовые файлы так, как решено в asset-list, и доказываешь, что всё на месте и в бюджете. Файлы не рисуешь и не генерируешь; статус `made` и hero-ассеты утверждает человек.

## 0. Preflight
`../slice-build/scripts/preflight.py` + проба MCP. Модели — GLB через glTFast (решение c): пакет `com.unity.cloud.gltfast` в `Packages/manifest.json`. Группу MCP `asset_gen` не включать: импорт — копированием файла в `Assets/` и refresh.

## 1. Вход
`design/art/asset-list.md` (ID, Size, **Budget**, Source, License / URL, Priority, Status), `design/audio/files.md` (если есть), `design/art/art-bible.md` (роли палитры, минимальные размеры), `design/tech/budgets.md`, файлы от человека или скиллов (`model-build`, `sfx-design`).

## 2. Алгоритм (детали — `references/import-method.md`)
1. Сверка до импорта: каждый файл → строка asset-list (имя файла = ID); лицензия `cc0` с URL; чего нет в списке — вопрос `gd:art-direction`, не импорт «на всякий случай».
2. Копирование в `Assets/_Project/Art/<тип>/` и `Assets/_Project/Audio/`; refresh через MCP; `.meta` не править руками.
3. Настройки импорта по типу (текстуры: max size по Budget, сжатие; спрайты: атлас по экрану; модели GLB: масштаб, материалы; звук: load type по длине) — через MCP (`manage_asset`, `manage_texture`) или чеклист.
4. Материалы: цвета ролей палитры; новые материалы только там, где роль другая.
5. Замена плейсхолдеров: ссылки в сценах и префабах на новый ассет; `ph_`-файл удаляется, только когда замена проверена скриншотом.
6. Verify loop, play mode, скриншот (посмотри), `python3 scripts/check_import.py Assets/_Project --assets design/art/asset-list.md [--audio design/audio/files.md --audio-root <Unity-проект>] [--stage beta]`.

## Done
`check_import.py` без FAIL; консоль чистая; скриншот сцены с новыми ассетами; бюджеты кадра не ухудшились (при сомнении — `perf-check`). Модель сверх бюджета → `model-build` (LOD) или `gd:tech-design`.

## Правила
Язык ответа = язык запроса. Только CC0 или свои ассеты; CC-BY и прочее — решение человека с атрибуцией в `ATTRIBUTION`-файле игры. Платные генераторы (Coplay `generate_*`, Meshy и др.) не вызывать. Status в asset-list меняет человек.
