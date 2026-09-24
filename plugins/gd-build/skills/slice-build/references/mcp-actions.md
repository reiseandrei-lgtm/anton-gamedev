# Абстрактные действия → инструменты MCP

Свой документ. Скиллы описаны через действия, чтобы работать с любым бесплатным Unity MCP. Имена инструментов CoplayDev сверены по исходникам v10.2.0 и проверены вживую 2026-09-24 (Unity 6000.3.24f1): отмечены ✅. IvanMurzak/Unity-MCP — только по исходникам 2026-09-23, вживую не проверялся. Если инструмент называется иначе — найди его в списке инструментов сервера по смыслу, не выдумывай.

| Действие | CoplayDev/unity-mcp (MIT, основной) | IvanMurzak/Unity-MCP (Apache-2.0) | Без MCP |
|---|---|---|---|
| Проба связи | `read_console` ✅; ресурс `mcpforunity://editor/state` | `ping`, `editor-application-get-state` | — |
| Состояние редактора / компиляция | `refresh_unity` (`mode: force`, `scope: all`, `compile: request`) ✅; ресурс `editor/state` (`is_compiling`) | `editor-application-get-state`, `assets-refresh` | mtime DLL в `Library/ScriptAssemblies` |
| Консоль | `read_console` (`action: get`, `types: [error]`) ✅ | `console-get-logs` | лог редактора (`verify-loop.md` §1.3) |
| Скрипты | запись файла напрямую ✅ + refresh; `manage_script`, `script_apply_edits`, `validate_script` | `script-update-or-create`, `script-read` | запись файла |
| Сцена, объекты, компоненты | `manage_scene` (`create`, `save`) ✅, `manage_gameobject` (`create`) ✅, `manage_components` (`add`) ✅, `manage_prefabs` | `scene-*`, `gameobject-*`, `gameobject-component-*`, `assets-prefab-*` | чеклист ручных шагов |
| ScriptableObject-конфиги | `manage_scriptable_object` (`create` + `patches: [{propertyPath, value}]`) ✅ | `assets-create`, `object-modify` | чеклист |
| Тесты | `run_tests` (`mode`) → `get_test_job` ✅; в v10 группа `testing` активна по умолчанию | `tests-run` | `qa-run/scripts/run-tests-headless.*` при закрытом редакторе |
| Play mode | `manage_editor` `play` / `stop` ✅ | `editor-application-set-state` | — |
| Проба состояния в игре | `execute_code` (только чтение свойств) ✅ | `script-execute`, `reflection-method-call` | — |
| Скриншот | `manage_camera` `screenshot`, `capture_source: game_view`, `output_folder` ✅ | `screenshot-game-view` | — |
| Пункт меню | `execute_menu_item` (`File/Exit` — закрыть редактор перед headless) ✅ | `editor-menu-*` | — |
| Пакеты | `manage_packages` | `package-add`, `package-list` | правка `Packages/manifest.json` ✅ |
| UI Toolkit | `manage_ui` (`create_panel_settings` c `settings`, `attach_ui_document`) ✅; `render_ui` — в play mode двухшаговый (первый вызов ставит в очередь, второй отдаёт файл), размер берёт из Game view, `width`/`height` и имя файла игнорирует | — | — |
| Профайлер | `manage_profiler` `get_frame_timing`, `get_counters` (`category: Memory` — Total Used Memory, Material Count, Game Object Count) ✅ | `profiler-*` | Profiler вручную |
| Сборка, импорт моделей | `manage_build`, `import_model`, `import_model_file` — есть в v10.2.0, вживую не проверены | — | — |

**Запрещено** (платно): Coplay `generate_image`, `generate_audio`, `generate_model` и группа `asset_gen`; официальный Unity MCP через AI Assistant (нужна подписка Unity AI).

`execute_code` блокирует опасные вызовы (`EditorApplication.Exit`, `File.Delete`, `Process.Start`). Не отключай `safety_checks`: закрыть редактор можно через `execute_menu_item` `File/Exit`.

## Установка бесплатного MCP
1. Пакет в `Packages/manifest.json`: `"com.coplaydev.unity-mcp": "https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity#v10.2.0"` (тег, а не `#main`: версия пакета должна совпадать с сервером). Сервер — Python 3.10+ через `uv`.
2. Телеметрия у сервера и у пакета включена по умолчанию. Отключение — переменная окружения `DISABLE_TELEMETRY=true` для процесса сервера и процесса Unity (по исходникам пакета есть и EditorPrefs-ключ `MCPForUnity.TelemetryDisabled`; где он в UI — не проверено).
3. Мост в редакторе стартует не сам: мастер настройки → Configure (пишет `.mcp.json`/конфиг Claude Code проекта), затем **Window → MCP for Unity → Start Session**. Проба: сервер `GET http://127.0.0.1:8080/api/instances` показывает проект.
4. MCP-сервер, добавленный в Claude Code посреди сессии, появится в инструментах только в новой сессии. В текущей сессии работает CLI того же сервера по HTTP: `uvx --from mcpforunityserver==10.2.0 unity-mcp --format json raw <tool> '<json-параметры>'` (имена параметров — camelCase, например `outputFolder`). Это тот же MCP, не обход.
5. После каждого domain reload мост переподключается несколько секунд — жди пробы, прежде чем слать следующую команду.
6. Кириллица в сообщениях и выводе тестов, пришедших через CLI на Windows, приходит как «?». Дословный текст — в NUnit XML headless-прогона; в `TestContext.WriteLine` замеров пиши ASCII.
7. `manage_scriptable_object create` отвечает success и тогда, когда класс лежит в файле с другим именем: ассет без скрипта. После создания проверь `m_Script` в `.asset` и загрузку в тесте.

Инструкции меняются: сверяйся с README репозитория, не с этим файлом.
