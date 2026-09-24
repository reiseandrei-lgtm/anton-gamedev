# Выпуск сборки: метод, CI, LFS, SteamPipe

Источники: game-ci/unity-builder и unity-test-runner (MIT) — используются как GitHub Actions, код не копируется; CCGS `release-checklist`, `day-one-patch`, `hotfix` (MIT) — пути патча и отката (идеи).

## 1. Версия
- Источник правды — git-тег `vX.Y.Z` игры и верхняя запись `CHANGELOG.md`. `PlayerSettings.bundleVersion` = `X.Y.Z`; Android `bundleVersionCode` растёт на 1 с каждой загрузкой в стор.
- Перед сборкой: `check_release.py <project> --tag vX.Y.Z` (RL1). Версию в проекте меняет `manage_editor`/правка `ProjectSettings.asset` при закрытом редакторе — не во время сборки.

## 2. Сборка
| Путь | Когда | Как |
|---|---|---|
| MCP `manage_build` (CoplayDev 10.2) | редактор открыт | `action: build`, цель `StandaloneWindows64` / `Android`, путь вывода вне `Assets/`; Build Profiles Unity 6 — если есть. Вживую в gd-build не проверялся — сначала `action` со справкой сервера |
| headless | редактор закрыт | `Unity.exe -batchmode -quit -projectPath <p> -buildTarget Win64 -executeMethod <Class.Method> -logFile -` (метод пишет игра; скилл даёт шаблон с `BuildPipeline.BuildPlayer` и `BuildOptions.None`) |
| GameCI | CI | workflow из §4; секреты — человек |

После сборки: размер (строка бюджета «размер сборки» → `perf-check`), запуск собранного билда ≥ 10 с без падения (лог игрока `Player.log`), строка в `design/release/builds.md`: `Version · Tag · Platform · Date · Build ID`.

## 3. .gitignore и LFS (RL2, RL3)
`.gitignore` Unity: `[Ll]ibrary/`, `[Tt]emp/`, `[Oo]bj/`, `[Bb]uild*/`, `[Ll]ogs/`, `[Uu]ser[Ss]ettings/`, `*.csproj`, `*.sln`. LFS до первого бинарного коммита: `git lfs install` (один раз на машину) и `.gitattributes`:
```
*.psd filter=lfs diff=lfs merge=lfs -text
*.png filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.fbx filter=lfs diff=lfs merge=lfs -text
*.glb filter=lfs diff=lfs merge=lfs -text
*.blend filter=lfs diff=lfs merge=lfs -text
*.bank filter=lfs diff=lfs merge=lfs -text
```
Уже закоммиченные бинарники переводит `git lfs migrate import --include="*.png,…"` — **переписывает историю**, только после «да» человека.

## 4. GameCI workflow (шаблон, `.github/workflows/build.yml` игры)
```yaml
name: build
on: { push: { tags: ["v*"] }, workflow_dispatch: {} }
jobs:
  build:
    runs-on: ubuntu-latest
    strategy: { matrix: { targetPlatform: [StandaloneWindows64, Android] } }
    steps:
      - uses: actions/checkout@v4
        with: { lfs: true }
      - uses: actions/cache@v4
        with: { path: unity/Library, key: Library-${{ matrix.targetPlatform }} }
      - uses: game-ci/unity-test-runner@v4
        env: { UNITY_LICENSE: "${{ secrets.UNITY_LICENSE }}", UNITY_EMAIL: "${{ secrets.UNITY_EMAIL }}", UNITY_PASSWORD: "${{ secrets.UNITY_PASSWORD }}" }
        with: { projectPath: unity }
      - uses: game-ci/unity-builder@v4
        env: { UNITY_LICENSE: "${{ secrets.UNITY_LICENSE }}", UNITY_EMAIL: "${{ secrets.UNITY_EMAIL }}", UNITY_PASSWORD: "${{ secrets.UNITY_PASSWORD }}" }
        with: { projectPath: unity, targetPlatform: "${{ matrix.targetPlatform }}", versioning: Tag }
      - uses: actions/upload-artifact@v4
        with: { name: "build-${{ matrix.targetPlatform }}", path: build/${{ matrix.targetPlatform }} }
```
Проект игры — в `unity/` (решение i). Секреты `UNITY_LICENSE` / `UNITY_EMAIL` / `UNITY_PASSWORD` заводит человек в настройках репозитория; скилл значения не видит и не просит. Минуты Actions для приватного репозитория ограничены бесплатным лимитом GitHub. Файл проверяется `check_release.py` (RL4, RL5) — запуск workflow не проверяется без секретов.

## 5. SteamPipe (RL6)
`steam/app_build_<AppID>.vdf` и `depot_build_<DepotID>.vdf` из шаблона Steamworks SDK: `AppID`, `DepotID`, `ContentRoot`, `SetLive` пусто (выпуск ветки — руками в Steamworks). Загрузка `steamcmd +login <user> +run_app_build …` — логин и Steam Guard делает человек.

## 6. Патч и откат
- **Hotfix**: ветка от тега релиза → фикс → `qa-run smoke` → тег `vX.Y.Z+1` → сборка тем же workflow.
- **Откат**: в Steamworks — вернуть прошлую сборку на ветку `default`; в Google Play — остановить поэтапное развёртывание. Решение и кнопка — человек.
