# ui-build: UI Toolkit по hud.md

Свой документ. Идеи раскладки — CCGS агенты `ui-programmer`, `unity-ui-specialist` (MIT), Nice-Wolf `unity-ui-patterns` (MIT); текст свой. Инструмент — `manage_ui` в CoplayDev/unity-mcp 10.x (только UI Toolkit, умеет `render_ui` в PNG). API — по официальной документации Unity.

## 1. Файлы
```
Assets/_Project/UI/
  Theme.uss         — только :root { --role-bg: #14172B; --role-ui-text: #F4F1DE; … } и размеры шрифта
  HUD.uxml, HUD.uss — постоянный HUD
  Restart.uxml, …   — по экрану
  GamePanel.asset   — PanelSettings (Scale With Screen Size, reference resolution цели)
Assets/_Project/Scripts/Presentation/…UI.cs — контроллеры
```
- В каждом UXML: `<ui:Style src="Theme.uss" />` первым, затем свой USS (`<ui:Style>` с префиксом `ui:`, иначе стиль не подключится).
- Имена: `name` = колонка Name в hud.md (`hud-score`, `restart-again`). Классы — `kebab-case`.
- Роли: переменная `--role-<role>` на каждую роль арт-библии (`bg`, `gameplay`, `interactive`, `danger`, `ui-text`, `accent`).

## 2. Текст и локализация
- В UXML только ключ: `<ui:Label name="restart-record" text="ui.record" />`. До `loc-build` на экране виден ключ — это честный плейсхолдер.
- Числа ставит код: `label.text = score.ToString()`. Составные строки (`«Рекорд: 12»`) — формат из таблицы локализации, не конкатенация.
- Лимиты длины — из `ux/hud.md` / `ux/accessibility.md`; RU/PL длиннее EN на 20–30 %.

## 3. Раскладка
- Корень на весь экран, отступы по `Screen.safeArea` (пересчёт при смене ориентации).
- Зоны hud.md → абсолютное позиционирование в процентах (`top: 4%`) или flex-контейнеры по краям.
- Тач-цель ≥ минимума библии (обычно 48 dp); в USS — `width`/`height` в px при опорном разрешении.
- Анимации (пульс кнопки и т. п.) — USS `transition` или код; отключаемые, если это вспышки/тряска.

## 4. Проверка
1. Verify loop (компиляция, консоль).
2. Play mode в каждом состоянии, где элемент виден (например, Dead для экрана рестарта).
3. Скриншоты в 2–3 разрешениях цели (мобайл-портрет: 1080×1920 и 1440×3200; PC: 1920×1080 и 2560×1440) — `manage_ui render_ui` для панели или Game view с выставленным разрешением. Посмотри: текст не обрезан, зоны не перекрываются, safe area соблюдена.
4. `check_ui.py` — UI1–UI5.
5. Кандидаты в визуальные эталоны → `qa-run visual` (эталон утверждает человек).
