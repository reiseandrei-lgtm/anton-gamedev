# juice-build: техники отклика и замер в кадрах

Свой документ. Модель anticipation → action → impact → resolution — из `gd: game-feel/references/feel-model.md` (адаптация gstack-game, MIT). Чеклист техник сверен с awesome-gamedev-agent-skills `disciplines/game-feel` (Apache-2.0, © gamedev-skills contributors), текст свой. How-to API Unity — официальный Unity Plugin.

## 1. Каналы
| Канал | Как в Unity | Параметры в конфиг | Доступность |
|---|---|---|---|
| Частицы | `ParticleSystem.Emit(n)` / `Play()` по событию; материал Unlit цвета роли | число, время жизни, скорость, цвет роли | — |
| Вспышка | материал: `_Color` / `_EmissionColor` на N кадров, или свойство шейдера через `MaterialPropertyBlock` | длительность (кадры), цвет | опция «уменьшить вспышки» |
| Тряска / толчок камеры | смещение камеры по затухающей кривой (или `CinemachineImpulseSource`, если Cinemachine в проекте) | амплитуда, частота, затухание | опция «без тряски» |
| Hitstop | `Time.timeScale = 0` на N кадров реального времени (корутина на `WaitForSecondsRealtime`/счёт кадров), затем восстановить | кадры | — |
| Squash / stretch | масштаб объекта по кривой (объём сохраняется: x·y ≈ const) | кадры фазы, коэффициент | — |
| Вибрация | `Gamepad.current.SetMotorSpeeds(lo, hi)` и сброс через N мс; `InputSystem.ResetHaptics()` на паузе | сила, длительность | опция «без вибрации» |

Правила: отклик подписан на событие системы (C# event), а не ищет состояние в `Update`; числа — в `JuiceConfig` (ScriptableObject); hitstop всегда восстанавливает `timeScale` (в `finally` / `OnDisable`).

## 2. Замер в кадрах (PlayMode)
```text
Time.captureFramerate = 60          // детерминированный шаг
вызвать событие (тот же метод, что и ввод) → f0 = Time.frameCount
ждать кадр за кадром, пока отклик не наступит: particle.isEmitting / camera.localPosition != rest / Time.timeScale == 0
→ f1 = Time.frameCount; начало = f1 − f0
длительность: пока отклик активен → f2; длительность = f2 − f1
восстановить captureFramerate = 0
```
- Тест с T-ID из тест-плана, если кейс есть (`visual`/`playmode`); иначе — свободный тест, строка в логе без T-ID.
- Скриншот кадра импакта: заморозь (`Time.timeScale = 0` после события) → `manage_camera screenshot` → восстанови.

## 3. Таблица Juice в логе
| FB | Событие | Цель (кадры) | Замер (кадры) | Допуск | Звук в том же кадре | Доказательство |
|---|---|---|---|---|---|---|
| FB3 | приземление | ≤ 1 (пыль в кадр касания) | 0 | 0 | нет FMOD (плейсхолдер AudioSource — да) | тест `Juice_land_dust_same_frame`, screenshots/land.png |

«Цель» переписывается из Game Feel GDD, не придумывается. Нет числа в GDD — `—` в цели, JU3, вопрос в `gd:game-feel`.
