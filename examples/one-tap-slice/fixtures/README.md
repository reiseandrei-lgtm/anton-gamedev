# Фикстуры

## Синтетические (негативные случаи)
Имитируют вывод Unity и FMOD Studio с заранее заложенными ошибками — каждый скрипт `gd-build` обязан их поймать:

- `TestResults/editmode-results.xml` — NUnit 3 XML в формате Unity Test Framework: 5 тестов, 1 падение (T-spark-02); T-ID из `[Property("TID", …)]` и из имени метода.
- `TestResults/empty-results.xml` — прогон, выполнивший 0 тестов (должен дать FAIL / exit 3).
- `fmod/GUIDs.txt` — экспорт GUIDs FMOD Studio: нет `event:/Amb/Sky/Wind`, есть лишнее `event:/SFX/Player/Jump2`.

## Живые (`live/`, 2026-09-24)
Настоящий вывод инструментов на этом примере, без правок:

- `live/TestResults/editmode-results.xml`, `playmode-results.xml` — Unity 6000.3.24f1, headless `run-tests-headless.ps1` на Unity-проекте слайса `first-hop` (сам проект — вне репозитория). EditMode 11/11; PlayMode 7/9 (5 своих + 4 теста пакета Input System из `testables`, 2 из них пропущены самим пакетом).
- `live/fmod/GUIDs.txt` — FMOD Studio 2.03.14, `fmodstudiocl -script gd_sync_event_map.cli.js` на пустом проекте: 8 событий, 1 снапшот, 4 шины, 3 параметра, мастер-банк.
