# Фикстуры (синтетические)

Unity и FMOD Studio на машине, где делался пример, не установлены. Эти файлы имитируют их вывод, чтобы проверить скрипты `gd-build` в режиме деградации:

- `TestResults/editmode-results.xml` — NUnit 3 XML, как пишет Unity Test Framework: 5 тестов, 1 падение (T-spark-02).
- `TestResults/empty-results.xml` — прогон, выполнивший 0 тестов (должен дать FAIL / exit 3).
- `fmod/GUIDs.txt` — экспорт GUIDs FMOD Studio: нет `event:/Amb/Sky/Wind`, есть лишнее `event:/SFX/Player/Jump2`.
