---
status: draft
updated: 2026-09-23
owner: example
---

# HUD — Lantern Hop

## Information inventory
| Info | Источник (GDD) | Нужна | Приоритет | Частота | Зона | Форма |
|---|---|---|---|---|---|---|
| заряд | hop#F2 | contextual | 1 | каждый кадр при заряде | на персонаже (диегетика: фонарь разгорается) | свет |
| счёт | spark#R3 | always | 2 | на событие | top-center, safe area | число |
| рекорд | spark#R3 | contextual | 3 | при рестарте | экран рестарта | число |
| «ещё» | hop#R6 | contextual | 1 | при Dead | нижняя треть, центр | кнопка 48 dp |

## Layout notes
Нижняя треть свободна для пальца — там только кнопка «ещё» в состоянии Dead.
