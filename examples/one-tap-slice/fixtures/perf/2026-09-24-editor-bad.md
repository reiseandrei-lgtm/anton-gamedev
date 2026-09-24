---
status: draft
updated: 2026-09-24
platform: editor (Unity 6000.3.24f1, Windows)
build: d4e5f6a
scene: Assets/_Project/Scenes/Run.unity
duration: 60
---

# Perf — негативная фикстура compare_perf.py (PF1, PF2, PF3, PF4)

## Results
| ID | Metric | Budget | p50 | p95 | max | Verdict |
|---|---|---|---|---|---|---|
| B1 | Кадр | 16.6 ms | 14.0 | 18.2 | 25.0 | fail |
| B2 | Batches | ≤ 50 | 36 | 40 | 44 | ok |
| B3 | Время рестарта | ≤ 0.3 s | 0.12 | | | |
| B4 | Размер APK | ≤ 60 MB | n/a: сборка игрока не делалась | | | |
| B9 | Draw calls | — | 10 | 12 | 14 | ? |
