# FMOD: синхронизация и интеграция с Unity

Свой документ. API FMOD Studio сверено по справочнику Scripting API (через машиночитаемую выгрузку в raffyknowsnothing/fmod-studio-mcp, MIT) и по вызовам в xDarkzx/Dans_Fmod_Studio_MCP (Apache-2.0); код не заимствован.

## 1. Что делает gd_sync_event_map.js

| Шаг | Вызов API | Проверено |
|---|---|---|
| Найти существующее | `studio.project.lookup(path)` | да |
| Папка событий | `studio.project.create("EventFolder")`, `.name`, `.folder = parent` | да |
| Событие | `studio.project.create("Event")`, `.name`, `.folder` | да |
| Шина | `studio.project.create("MixerGroup")`, `.output = masterBus` | да |
| Снапшот | `studio.project.create("Snapshot")`, `.name` | да |
| Локальный параметр | `event.addGameParameter({name, type, min, max})` | да |
| Глобальный (preset) параметр | `studio.project.workspace.addGameParameter({...})` | да |
| Labeled-параметр | `parameterType.UserEnumeration` + `enumerationLabels` | тип — да; поле меток — **не проверено** |
| Событие → шина | `event.mixerInput.output = bus` | **не проверено**, в try/catch |
| Идемпотентность параметров | `event.parameters` | **не проверено**: если свойства нет, повторный запуск может продублировать локальный параметр — проверить после второго запуска |
| Меню | `studio.menu.addMenuItem({name: "gd\\Sync event map", execute})` | да |

Первый запуск — на проекте под git или на копии. Всё, что скрипт не смог, он пишет в консоль строкой `[gd] ВРУЧНУЮ: …`.

## 2. Без скрипта (полностью вручную)
По `event-map.json`: создать папки и события по путям, параметры с диапазонами, шины под Master, снапшоты. Порядок тот же, что в таблице.

## 3. Чеклист FMOD for Unity
- [ ] Пакет FMOD for Unity установлен (бесплатно, с сайта FMOD или Asset Store).
- [ ] FMOD → Edit Settings: путь к проекту Studio или к собранным банкам; платформы (Mobile / Desktop).
- [ ] В сцене один `StudioListener` (обычно на камере) вместо `AudioListener`.
- [ ] Банки `Master` и `Master.strings` грузятся при старте (`StudioBankLoader` или загрузка в boot-сцене).
- [ ] Вызовы по константам: `RuntimeManager.PlayOneShot(FmodEvents.SFX_Player_Jump, pos)`; для loop — `RuntimeManager.CreateInstance(path)` + `start()` / `stop()` + `release()`.
- [ ] Параметры: `instance.setParameterByName(FmodEvents.Params.Charge, value)`; глобальные — `RuntimeManager.StudioSystem.setParameterByName(...)`.
- [ ] Громкость шин из настроек игрока: `RuntimeManager.GetBus("bus:/Music").setVolume(v)`.
- [ ] Строки банков (strings bank) собраны — иначе поиск по пути не работает.
- [ ] Никаких путей событий строкой вне `FmodEvents.cs`.

## 4. Проверка
- Структура: `diff_fmod.py` без D1.
- Код: компиляция с `FmodEvents.cs` (verify loop).
- Звучание: только человек. В отчёте — «звучание не проверялось».
