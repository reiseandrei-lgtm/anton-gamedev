# Фикстуры check_release.py

Не Unity-проекты, а их скелет: `ProjectSettings.asset`, `.gitignore`, `.gitattributes`, workflow, VDF SteamPipe, Build Profile.
Бинарные файлы (WAV, крупный PNG) тест создаёт во временной копии — в репозитории их нет, чтобы `.gitattributes`
фикстуры с `filter=lfs` ничего не отправил в LFS. Тест передаёт `--repo` = корень копии.

- `ok/` — версия 1.2.0 = CHANGELOG, LFS на аудио и картинки, секреты UNITY_* / STEAM_*, релизный профиль без Development, VDF с AppID и DepotID.
- `bad/` — RL1–RL6: версия 1.1.0 ≠ CHANGELOG 1.2.0, .gitignore без Logs/ и UserSettings/, нет LFS, чужой секрет, `-development` в workflow, Development в релизном профиле, VDF без AppID и DepotID.
