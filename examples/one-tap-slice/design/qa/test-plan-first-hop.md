---
status: draft
updated: 2026-09-23
owner: example
slice: first-hop
---

# Test plan — first-hop

## Scope
Системы: hop, spark · Хендофф: handoff/first-hop.md · Вне плана: меню, магазин.

## Cases
| ID | Covers | Type | Priority | Given | When | Then | Auto |
|---|---|---|---|---|---|---|---|
| T-hop-01 | hop#R2, hop#F2 | editmode | P1 | K2 = 0.8 | удержание 0.4 с | charge = 0.5 ± 0.01 | yes |
| T-hop-02 | hop#E2, hop#F2 | editmode | P2 | K2 = 0.8 | удержание 2.0 с | charge = 1.0 | yes |
| T-hop-03 | hop#F1, hop#R3 | editmode | P1 | K1 = 1, K3 = 4 | charge 0 / 0.5 / 1 | distance 1.0 / 2.5 / 4.0 ± 0.001 | yes |
| T-hop-04 | hop#R4 | editmode | P1 | gap 2.5, K4 = 0.35 | distance 2.84 и 2.86 | успех, промах | yes |
| T-hop-05 | hop#E3 | editmode | P2 | K6 = 0.05 | отпускание при charge 0.04 | прыжка нет, State = Idle | yes |
| T-hop-06 | hop#R1, ED2 | playmode | P1 | Idle на фонаре | InputTestFixture: касание 0.4 с, отпускание | State: Charging → Airborne | yes |
| T-hop-07 | hop#R5, hop#E1 | playmode | P1 | Airborne | касание | State остаётся Airborne, заряд 0 | yes |
| T-hop-08 | hop#E4 | playmode | P2 | Charging | OnApplicationPause(true) | charge = 0, State = Idle | yes |
| T-hop-09 | hop#E5 | playmode | P3 | Charging первым пальцем | касание вторым пальцем, отпускание второго | заряд продолжается, прыжка нет | yes |
| T-hop-10 | hop#R6, ED4 | playmode | P1 | Dead | тап через 0.2 с после падения; тап через 0.4 с | нет рестарта; рестарт ≤ 0.3 с | yes |
| T-spark-01 | spark#R1 | editmode | P2 | K3 = 0.35, seed фиксирован | генерация 10 000 фонарей | доля искр 0.35 ± 0.02 | yes |
| T-spark-02 | spark#F1, spark#R2 | editmode | P1 | K1 = 3, K2 = 2 | приземление с distance 2.9 и 3.1 | +1 и +2 | yes |
| T-spark-03 | spark#E1 | editmode | P2 | фонарь с искрой | промах | счёт не меняется | yes |
| T-spark-04 | spark#R3, spark#E2 | editmode | P1 | рекорд 10 | конец забега со счётом 10, затем 11 | не перезаписан, затем 11 | yes |
| T-spark-05 | spark#E3, ED5 | editmode | P2 | IRecordStorage бросает исключение | конец забега со счётом 12 | игра продолжается, рекорд в памяти 12 | yes |
| T-slice-01 | ED1 | manual | P1 | mid Android | 60 с забега после 10 мин игры | 60 fps, кадр ≤ 16.6 ms | no |
| T-slice-02 | ED3 | manual | P2 | билд | 20 прыжков на дальние фонари с искрой | двойная искра видна и слышна отличимо | no |
| T-slice-03 | ED5 | manual | P1 | рекорд 5 | закрыть приложение, открыть | рекорд 5 | no |
| T-slice-10 | DD1 | playtest | P1 | новичок | первый запуск | первый прыжок ≤ 10 с без подсказки | no |
| T-slice-11 | DD2 | playtest | P1 | новичок | первые 3 прыжка | держит дольше для дальнего фонаря | no |
| T-slice-12 | DD3 | playtest | P1 | новичок | первое падение | «ещё» < 2 с | no |

## Smoke
1. Билд запускается, забег начинается ≤ 3 с после иконки
2. Короткое и долгое удержание дают разную дальность
3. Промах → падение → «ещё» → новый забег ≤ 0.3 с
4. Искра засчитывается, счёт растёт
5. Рекорд виден на экране рестарта
6. Консоль без исключений за 60 с

## Severity
S1 блокер · S2 ломает гипотезу/ED · S3 заметно, есть обход · S4 косметика

## Open questions
- hop#R3: время полёта 0.5 с — не knob; нужно ли вынести в конфиг?
