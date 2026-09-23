# Абстрактные действия → инструменты MCP

Свой документ. Скиллы описаны через действия, чтобы работать с любым бесплатным Unity MCP. Имена инструментов сверены по исходникам на 2026-09-23 (CoplayDev/unity-mcp, IvanMurzak/Unity-MCP). Если инструмент называется иначе — найди его в списке инструментов сервера по смыслу, не выдумывай.

| Действие | CoplayDev/unity-mcp (MIT, основной) | IvanMurzak/Unity-MCP (Apache-2.0) | Без MCP |
|---|---|---|---|
| Проба связи | ресурс `mcpforunity://editor/state` или `read_console` | `ping`, `editor-application-get-state` | — |
| Состояние редактора / компиляция | ресурс `editor/state` (`is_compiling`), `refresh_unity` | `editor-application-get-state`, `assets-refresh` | mtime DLL в `Library/ScriptAssemblies` |
| Консоль | `read_console` | `console-get-logs` | `Logs/Editor.log` проекта |
| Скрипты | `manage_script`, `script_apply_edits`, `validate_script`; или запись файла напрямую | `script-update-or-create`, `script-read` | запись файла |
| Сцена, объекты, компоненты | `manage_scene`, `manage_gameobject`, `manage_components`, `manage_prefabs` | `scene-*`, `gameobject-*`, `gameobject-component-*`, `assets-prefab-*` | чеклист ручных шагов |
| ScriptableObject-конфиги | `manage_scriptable_object` | `assets-create`, `object-modify` | чеклист |
| Тесты | `manage_tools` (activate group `testing`) → `run_tests` → `get_test_job` | `tests-run` | `qa-run/scripts/run-tests-headless.*` при закрытом редакторе |
| Play mode | `manage_editor` `play` / `stop` | `editor-application-set-state` | — |
| Проба состояния в игре | `execute_code` (только чтение свойств) | `script-execute`, `reflection-method-call` | — |
| Скриншот | `manage_camera` `screenshot`, `capture_source: game_view` | `screenshot-game-view` | — |
| Пакеты | `manage_packages` | `package-add`, `package-list` | правка `Packages/manifest.json` |
| Профайлер | `manage_profiler` | `profiler-*` | Profiler вручную |

**Запрещено** (платно): Coplay `generate_image`, `generate_audio`, `generate_model` и группа `asset_gen`; официальный Unity MCP через AI Assistant (нужна подписка Unity AI).

## Установка бесплатного MCP (для пользователя)
- CoplayDev/unity-mcp: пакет в Unity через Package Manager по git-URL из README проекта, сервер — Python 3.10+ через `uv`. Unity 2021.3 → 6.x.
- Подключение к Claude Code — по README MCP-сервера (HTTP или stdio). Проверка — проба связи из таблицы.
Инструкции меняются: сверяйся с README репозитория, не с этим файлом.
