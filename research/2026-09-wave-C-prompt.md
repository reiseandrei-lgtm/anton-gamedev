# Промпт для новой сессии: волна C (anton-gamedev)

Скопируй блок ниже в новую сессию Claude Code, открытую в `D:\Claude Projects\MASTER GDD`.

---

Продолжаем anton-gamedev: волна C. Проект — D:\Claude Projects\MASTER GDD. Прочитай CLAUDE.md, research/2026-09-production-handoff.md и в research/2026-09-production-cycle-architecture.md только §3 «Волна C» (карточки C1–C4 — это спецификация) и §6. Волна B смёржена (v0.6.0).

Правила:
- Тесты не пишем. Каждый новый скрипт — один запуск на examples/one-tap-slice, артефакты — в D:\Tools\_gdcheck (потом удалить).
- Ничего не ставь без моего «да». Push, мёрж и тег — тоже после «да».
- Python-файлы пиши с newline="\n", plugin.json меняй через json.
- Побочные расследования не дольше 15 минут, дольше — в «Открытое» хендоффа.

План: ветка feat/production-wave-C от main, по коммиту на скилл.
1. gd: `level-design`, `release-plan` (карточки C3, C4) + пары в tools/trigger_cases.md + ссылки в gd-router/pipeline.md.
2. gd-build: `loc-build` (C1; если пакета com.unity.localization нет в one-tap-slice — режим plan, спроси про установку), `analytics-build` (C2, локальный JSONL). `netcode-build` не делаем.
3. Версии gd 0.7.0, gd-build 0.4.0, CHANGELOG, ATTRIBUTION, хендофф. `python tools/check_plugins.py` и `claude plugin validate` ×3 без FAIL.
4. Стоп: коротко по-русски — файлы, что проверено (числа), что не проверено. Жди «да» на PR.
