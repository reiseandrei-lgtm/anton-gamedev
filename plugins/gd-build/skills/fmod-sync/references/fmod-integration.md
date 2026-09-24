# FMOD: синхронизация и интеграция с Unity

Свой документ. API FMOD Studio сверено по справочнику Scripting API из поставки FMOD Studio 2.03.14 (`documentation/FMOD Studio User Manual/scripting-api-reference-*.html`) и прогоном на FMOD Studio 2.03.14 (2026-09-24, `fmodstudiocl -script`, пустой проект). Раньше — по выгрузке в raffyknowsnothing/fmod-studio-mcp (MIT) и вызовам в xDarkzx/Dans_Fmod_Studio_MCP (Apache-2.0); код не заимствован.

## 1. Что делает gd_sync_event_map.js

| Шаг | Вызов API | Проверено вживую (2.03.14) |
|---|---|---|
| Найти существующее | `studio.project.lookup(path)` | да |
| Папка событий | `studio.project.create("EventFolder")`, `.name`, `.folder = parent` | да |
| Событие | `studio.project.create("Event")`, `.name`, `.folder` | да |
| Событие → банк | `event.relationships.banks.add(masterBank)` (мастер-банк: `Bank.isMasterBank`) | да. Без банка событие не попадает ни в сборку, ни в `GUIDs.txt` |
| Шина | `studio.project.create("MixerGroup")`, `.output = masterBus` | да |
| Событие → шина | `event.mixerInput.output = bus` | да |
| Снапшот | `studio.project.create("Snapshot")`, `.name` | да |
| Параметр (любой) | `workspace.addGameParameter({name, type, min, max})` → `ParameterPreset` (`lookup("parameter:/name")`, `gameParameter.presetOwner`) | да |
| Глобальный параметр | `gameParameter.isGlobal = true` | да |
| Метки перечисления | `parameterType.UserEnumeration` + `enumerationLabels` | да |
| Параметр → событие | `event.addGameParameter(preset)`; проверка — `event.getParameterPresets()` (id = `preset.parameter.id`) | да |
| Банк по имени | `create("Bank")`, `.name`, `.folder = workspace.masterBankFolder`; Master — `Bank.isMasterBank` | да (банк `Music` создан и собран) |
| Файл звука | `project.importAudioFile(absPath)` (копируется в `Assets/` проекта FMOD); повторно — `masterAssetFolder.getAsset(name)` | да |
| Звук на событие | `event.masterTrack.addSound(event.timeline, "SingleSound", 0, audioFile.length)`, `.audioFile = af`; вариации — `"MultiSound"` + `SingleSound.owner = multi` | да (Spark: MultiSound из 2 файлов) |
| Идемпотентность | повторный запуск: папок, событий, шин, снапшотов, параметров, подключений, банков +0 | да |
| Меню GUI | `studio.menu.addMenuItem({name: "gd\Sync event map", execute})` | регистрация — да; запуск из меню GUI — **не проверено** (проверен тот же код через `.cli.js`) |

В FMOD 2.03 любой параметр события — это `ParameterPreset`. Если вызывать `event.addGameParameter({name: "charge"})` у двух событий, FMOD создаст `charge` и `charge (2)`, и `setParameterByName("charge")` на втором событии не сработает. Поэтому скрипт создаёт один preset на имя и подключает его ко всем событиям.

Первый запуск — на проекте под git или на копии. Всё, что скрипт не смог, он пишет в консоль строкой `[gd] ВРУЧНУЮ: …`.

### Headless (без GUI)
- `fmodstudiocl -script gd_sync_event_map.cli.js <project>.fspro` — синхронизирует, сохраняет, пишет `<project>/Build/GUIDs.txt`.
- `fmodstudiocl -build -platforms Desktop <project>.fspro` — собирает банки (`Build/Desktop/Master.bank`, `Master.strings.bank`).
- `fmodstudiocl -diagnostic <project>.fspro` — проверка целостности проекта.
- `fmodstudiocl` лежит рядом с `FMOD Studio.exe`. Новый проект CLI не создаёт: пустой проект создаёт человек (File → New → Save As).

## 2. Без скрипта (полностью вручную)
По `event-map.json`: создать папки и события по путям, параметры с диапазонами, шины под Master, снапшоты. Порядок тот же, что в таблице.

## 3. Чеклист FMOD for Unity
- [ ] Пакет FMOD for Unity установлен (бесплатно; скачивание с fmod.com или Asset Store требует входа в аккаунт — шаг человека).
- [ ] FMOD → Edit Settings: путь к проекту Studio или к собранным банкам; платформы (Mobile / Desktop).
- [ ] В сцене один `StudioListener` (обычно на камере) вместо `AudioListener`.
- [ ] Банки `Master` и `Master.strings` грузятся при старте (`StudioBankLoader` или загрузка в boot-сцене).
- [ ] Вызовы по константам: `RuntimeManager.PlayOneShot(FmodEvents.SFX_Player_Jump, pos)`; для loop — `RuntimeManager.CreateInstance(path)` + `start()` / `stop()` + `release()`.
- [ ] Параметры: `instance.setParameterByName(FmodEvents.Params.Charge, value)`; глобальные — `RuntimeManager.StudioSystem.setParameterByName(...)`.
- [ ] Громкость шин из настроек игрока: `RuntimeManager.GetBus("bus:/Music").setVolume(v)`.
- [ ] Строки банков (strings bank) собраны — иначе поиск по пути не работает.
- [ ] Никаких путей событий строкой вне `FmodEvents.cs`.

## 4. Проверка
- Структура: `diff_fmod.py` без D1 (события, снапшоты, шины, параметры; событие вне банка = D1).
- Код: компиляция с `FmodEvents.cs` (verify loop). Вызовы FMOD for Unity (`RuntimeManager.*`) из чеклиста §3 вживую **не проверены**: пакет не ставился (нужен вход на fmod.com).
- Звучание: только человек. В отчёте — «звучание не проверялось».
