# Метрики: формат, нейминг, якоря

> Свой документ: формат, связь «вопрос → KPI → событие → порог», проверки. Якоря retention — ГИПОТЕЗА по общедоступным отраслевым обзорам, без конкретного источника; уточнять под жанр.

## 1. events.md

Скрипт читает таблицы `## Questions`, `## KPIs`, `## Events`.

```markdown
---
status: draft
updated: YYYY-MM-DD
owner:
---
# Analytics events — <Game>

## Questions
| ID | Вопрос | Откуда |
|---|---|---|
| MQ1 | Доходят ли новички до первого замыкания петли? | handoff first-jump, DD1 |

## KPIs
| KPI | Question | Formula (events) | Target | Decision threshold |
|---|---|---|---|---|
| ftue_loop_rate | MQ1 | count(first_loop_closed) / count(session_started where session_index=1) | ≥ 70 % | < 50 % → переделать FTUE |

## Events
| Event | Params | Trigger | Serves |
|---|---|---|---|
| session_started | session_index:int, build:string | запуск сессии | ftue_loop_rate |
| first_loop_closed | seconds_since_start:float | первое замыкание петли | ftue_loop_rate |
```

- **Event**: `object_action`, `snake_case`, 2–4 слова, действие в прошедшем времени или состояние (`level_started`, `jump_performed`).
- **Params**: `name:type`, типы `int · float · bool · string · enum[a/b/c]`. Не больше 5 на событие.
- **Serves**: KPI или ID вопроса, ради которого событие существует.
- **Formula**: события упоминаются по имени; скрипт проверяет, что они есть в таблице Events.

## 2. funnels.md

```markdown
## ftue
| Step | Event | Expected | Alert |
|---|---|---|---|
| 1 | session_started | 100 % | — |
| 2 | jump_performed | 95 % | < 85 % |
| 3 | first_loop_closed | 70 % | < 50 % |
```
Заголовок `## <funnel_name>` на воронку. Шаги FTUE берутся из `ux/ftue.md` (колонка «Событие метрики»).

## 3. Приватность (M5)
Запрещённые параметры: `email`, `name`, `phone`, `address`, `ip`, `device_id`/`idfa`/`gaid` без хеширования, свободный текст пользователя. Возраст — только диапазоном, если нужен для рейтинга. Согласие — по требованиям стора и региона (GDPR, COPPA для детской аудитории).

## 4. Якоря retention (ГИПОТЕЗА, уточнять под жанр)
| Платформа / тип | D1 | D7 | D30 | Источник якоря |
|---|---|---|---|---|
| Мобайл казуал F2P | 30–40 % | 10–15 % | 3–6 % | публичные отраслевые отчёты, разброс по жанрам велик |
| Мобайл мидкор | 25–35 % | 8–12 % | 2–5 % | то же |
| PC премиум | retention менее показателен; смотреть медианное время игры и completion первой главы | | | |
Для слайса и плейтеста на 5–20 людей retention не считается: используй воронки и время до шага.

## 5. Бесплатная реализация
- Unity Gaming Services Analytics — есть бесплатный уровень (лимиты проверить).
- GameAnalytics — бесплатный SDK для Unity.
- Свой лог: события в JSON Lines в `persistentDataPath` + выгрузка с тест-устройств — идеален для плейтеста, ноль зависимостей.
Выбор — ADR в `tech/adr/`.
