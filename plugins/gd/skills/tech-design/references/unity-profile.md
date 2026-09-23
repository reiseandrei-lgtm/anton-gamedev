# Профиль Unity 6 (соглашения, не реализация)

Свой документ. How-to по конкретным API — официальный Unity Plugin (`/unity:*`, бесплатный, Unity Companion License). Действия в редакторе — `gd-build`.

## Структура проекта
```
Assets/
  _Project/
    Scripts/<Module>/<Module>.asmdef
    Configs/          ScriptableObject-ассеты конфигов (Config map)
    Scenes/           Boot, Menu, <Slice>
    Prefabs/  Art/  UI/
  Tests/
    EditMode/<Module>.Tests.asmdef   (ссылается на модуль + UnityEngine.TestRunner, UnityEditor.TestRunner)
    PlayMode/<Module>.PlayTests.asmdef
  Plugins/FMOD/       FMOD for Unity (если используется)
```
Всё своё — под `_Project`, чтобы не смешивать с пакетами и сторонними ассетами.

## Выборы по умолчанию (менять через ADR)
| Тема | По умолчанию | Когда иначе |
|---|---|---|
| Рендер | URP | — |
| Ввод | Input System (не старый Input Manager); тестируется `InputTestFixture` | — |
| Конфиги | ScriptableObject на систему | внешние таблицы — если дизайнер правит в Google Sheets |
| Зависимости | явные ссылки и конструкторы для логики; сериализованные ссылки для компонентов | DI-фреймворк — только ADR |
| Сохранения | JSON в `Application.persistentDataPath` с полем `version` | облако — ADR |
| Загрузка | обычные сцены и Resources-free ссылки | Addressables — когда контент > стартового бюджета билда |
| Аудио | FMOD for Unity; пути событий как константы (`gd-build` генерирует `FmodEvents.cs`) | Unity AudioMixer — если FMOD не используется |
| Тесты | Unity Test Framework: EditMode для логики, PlayMode для ввода и сцен | — |
| Локализация | Unity Localization package, ключи = ID строк | — |

## Бесплатность
Unity Personal, URP, Input System, Test Framework, Localization — бесплатны. FMOD for Unity — бесплатен в пределах Indie-лицензии FMOD (условия — на fmod.com). Unity AI и официальный Unity MCP требуют подписки или trial — не закладывать в архитектуру.
