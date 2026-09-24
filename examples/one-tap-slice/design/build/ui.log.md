---
status: review
updated: 2026-09-24
system: ui
milestone: alpha
mode: live
unity: 6000.3.24f1
mcp: CoplayDev/unity-mcp 10.2.0 (cli)
build: Unity-проект one-tap-slice, после aad5c12 (ui-build)
---
# Build log — ui

## Rules
| ID | Статус | Доказательство | Задачи |
|---|---|---|---|
| ED-ui-1 | ✅ | check_ui.py PASS (4 элемента hud.md, 6 ролей палитры, ключи вместо текста); скриншоты 1080×1920 и 1440×3200 в build/ui/screenshots/ (посмотрены) | 1–3 |

## Tasks
| # | Задача | Модуль | Тесты | Итог | fix-циклов |
|---|---|---|---|---|---|
| 1 | Theme.uss (роли палитры), HUD.uxml / HUD.uss по ux/hud.md | UI | check_ui.py | ✅ | 0 |
| 2 | PanelSettings (Scale With Screen Size 1080×1920), UIDocument, HudView — через MCP manage_ui | Presentation | smoke | ✅ | 0 |
| 3 | Экран рестарта: рекорд и «ещё» | UI | скриншоты | ✅ | 1 (margin-top в % считается от ширины — в широком Game view рекорд уезжал за экран; видно только на картинке) |

## Deviations from ux/hud.md
- Отдельная метка `restart-record-value` (число) рядом с `restart-record` (ключ): число не склеивается со строкой локализации.
- Safe area применяется из `Screen.safeArea`; на устройстве не проверено.

## Verify summary
Компиляция доказана · консоль 0 ошибок · IMGUI удалён из GameBootstrap · снимки: T-ui-01 (старт), T-ui-02 (Dead, рекорд 1) в двух разрешениях; кандидаты в эталоны — qa/visual/_pending/.
