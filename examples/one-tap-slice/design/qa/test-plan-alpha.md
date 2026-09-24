---
status: draft
updated: 2026-09-24
owner: example
slice: alpha
---

# Test plan — alpha

## Scope
Системы: chain (новая), hop и spark (отклик FB, визуал), ui · Хендофф: handoff/alpha.md · Тесты first-hop (T-hop-01…10, T-spark-01…05) остаются в test-plan-first-hop.md.

## Cases
| ID | Covers | Type | Priority | Given | When | Then | Auto |
|---|---|---|---|---|---|---|---|
| T-chain-01 | chain#R1 | editmode | P1 | seed 7 | построить цепочку | фонарь 0 в x = 0, без искры | yes |
| T-chain-02 | chain#R2, chain#F1 | editmode | P1 | K1 = 1, K2 = 3.65, seed 7 | 10 000 зазоров | все в [1, 3.65]; среднее 2.325 ± 0.05 | yes |
| T-chain-03 | chain#R3, chain#E1 | editmode | P1 | K2 = 5, hop K3 = 4, K4 = 0.35 | построить цепочку | max зазор ≤ 3.65; предупреждение в лог | yes |
| T-chain-04 | chain#E2 | editmode | P2 | K1 = 3, K2 = 2 | построить цепочку | все зазоры = 2; предупреждение в лог | yes |
| T-chain-05 | chain#R4 | editmode | P1 | K3 = 8 | приземление на фонарь 5 | впереди ≥ 8 фонарей | yes |
| T-chain-06 | chain#R5, ED-chain-1 | editmode | P1 | seed 42 дважды | две цепочки по 50 фонарей | позиции и искры совпадают | yes |
| T-chain-07 | chain#E3 | editmode | P3 | seed 0 | два построения | цепочки различаются | yes |
| T-chain-08 | ED-chain-2 | playmode | P1 | сцена Run, seed 42 | старт | позиции фонарей в сцене = ChainGenerator(seed 42) | yes |
| T-chain-09 | ED-chain-3 | visual | P1 | сцена Run, seed 42, 1080×1920, пауза на кадре 5 | старт | совпадает с эталоном, diff ≤ 0.5 % (маска: счёт) | yes |
| T-chain-11 | chain#R4 | playmode | P1 | сцена Run, seed 42 | 12 точных прыжков | впереди всегда ≥ K3 фонарей, каждый фонарь цепочки есть в сцене (находка ревью кода 2026-09-24) | yes |
| T-chain-10 | DD-chain-1 | playtest | P1 | новичок | 5 промахов | объясняет промах своей ошибкой | no |
| T-hop-20 | hop#FB1 | visual | P2 | seed 42, 1080×1920, удержание до charge 1, пауза | заряд | фонарь под игроком белый (эталон) | yes |
| T-hop-21 | hop#FB2, ED-hop-1 | playmode | P2 | captureFramerate 60 | прыжок | squash 1 кадр → stretch 2 кадра (замер) | yes |
| T-hop-22 | hop#FB3, ED-hop-1 | playmode | P1 | captureFramerate 60 | приземление | частицы пыли в кадр касания (замер 0 кадров) | yes |
| T-hop-23 | hop#FB4 | visual | P2 | seed 42, промах, пауза через 0.15 с | падение | затемнение (эталон) | yes |
| T-hop-24 | hop#FB5 | visual | P2 | seed 42, Dead, пауза | экран рестарта | кнопка «ещё» на месте (эталон; пульс — T-hop-25) | yes |
| T-hop-25 | hop#FB5 | manual | P3 | Dead | 3 с | кнопка пульсирует (manual: движение во времени) | no |
| T-spark-20 | spark#FB1 | visual | P2 | seed 42, прыжок на фонарь с искрой, пауза в кадр сбора | сбор | вспышка и «+1» (эталон) | yes |
| T-spark-21 | spark#FB2 | visual | P2 | seed 42, рекорд 0, счёт 1, Dead | экран рестарта | рекорд цветом accent (эталон) | yes |
| T-spark-22 | spark#FB3 | manual | P3 | счёт растёт | сбор искры | цифра «тикает» (manual: смена во времени) | no |
| T-ui-01 | ED-ui-1 | visual | P1 | seed 42, 1080×1920 и 1440×3200 | старт | HUD: счёт top-center в safe area (эталон) | yes |
| T-ui-02 | ED-ui-1 | visual | P1 | Dead, 1080×1920 и 1440×3200 | экран рестарта | рекорд и «ещё» по ux/hud.md (эталон) | yes |
| T-slice-30 | budgets#B1 | perf | P1 | mid Android, 10 мин игры | 60 с забега | кадр p95 ≤ 16.6 ms | yes |
| T-slice-31 | budgets#B2 | perf | P2 | сцена Run | Frame Debugger | batches ≤ 50 | yes |
| T-slice-32 | budgets#B3 | perf | P1 | Dead | тап | рестарт ≤ 0.3 с | yes |
| T-slice-33 | budgets#B4 | perf | P2 | Android-сборка | Build Report | APK ≤ 60 MB | yes |

## Smoke
1. Старт с seed 42 — та же цепочка, что в эталоне T-chain-09
2. 10 прыжков подряд без неизбежного промаха (зазор ≤ максимума)
3. Промах → Dead → тап → новая цепочка
4. HUD и экран рестарта — ключи локализации, цвета ролей
5. Консоль без исключений за 60 с

## Severity
S1 блокер · S2 ломает гипотезу/ED · S3 заметно, есть обход · S4 косметика

## Open questions
