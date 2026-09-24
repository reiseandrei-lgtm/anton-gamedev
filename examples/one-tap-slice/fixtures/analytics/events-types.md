---
status: draft
updated: 2026-09-24
owner: example
---

# Events — фикстура gen_analytics.py: enum, ключевое слово C#, событие без параметров

## Events
| Event | Params | Trigger | Serves |
|---|---|---|---|
| menu_opened | — | открытие меню | — |
| level_failed | level_index:int, cause:enum[fall,timeout], event:string | провал | MQ1 |
