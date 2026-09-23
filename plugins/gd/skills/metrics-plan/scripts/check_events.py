#!/usr/bin/env python3
"""Проверка design/analytics/events.md и funnels.md (Python stdlib).

Использование:
  python3 check_events.py design/analytics/events.md [--funnels design/analytics/funnels.md]

Проверки: M1 нейминг события/параметра · M2 дубль события · M3 шаг воронки без события ·
M4 KPI ссылается на несуществующее событие · M5 параметр с признаками PII ·
M6 событие без Serves (WARN) · M7 KPI без порога решения.
Формат — references/metrics-method.md. Выход с кодом 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gd-router" / "scripts"))
import gdd_ids  # noqa: E402

EVENT_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+){1,3}$")
PARAM_RE = re.compile(r"^([a-z][a-z0-9_]*)\s*:\s*(int|float|bool|string|enum\[[^\]]+\])$")
PII = re.compile(r"(^|_)(email|e_mail|name|first_name|last_name|phone|address|ip|device_id|idfa|gaid|imei|user_text)($|_)")
EMPTY = {"", "—", "-", "–"}


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("events")
    ap.add_argument("--funnels", default=None)
    a = ap.parse_args()

    secs = gdd_ids.sections(gdd_ids.read(a.events))
    fails, warns = [], []
    ev_rows = [r for r in gdd_ids.table_rows(gdd_ids.find_section(secs, "events") or [])
               if r.get("event", "").strip("` ") and "<" not in r["event"]]
    kpis = [r for r in gdd_ids.table_rows(gdd_ids.find_section(secs, "kpis") or [])
            if r.get("kpi", "").strip("` ") and "<" not in r["kpi"]]
    questions = {r.get("id", "").strip() for r in gdd_ids.table_rows(gdd_ids.find_section(secs, "questions") or [])}
    kpi_names = {r["kpi"].strip("` ") for r in kpis}
    events = set()
    for r in ev_rows:
        ev = r["event"].strip("` ")
        if not EVENT_RE.match(ev):
            fails.append(f"M1 {ev}: имя не object_action в snake_case (2–4 слова)")
        if ev in events:
            fails.append(f"M2 {ev}: дубль")
        events.add(ev)
        params = r.get("params", "").strip()
        if params not in EMPTY:
            plist = re.split(r",\s*(?![^\[]*\])", params)
            if len(plist) > 5:
                warns.append(f"M1 {ev}: {len(plist)} параметров > 5")
            for p in plist:
                m = PARAM_RE.match(p.strip())
                if not m:
                    fails.append(f"M1 {ev}: параметр «{p.strip()}» — нужен name:type (int/float/bool/string/enum[a/b])")
                elif PII.search(m.group(1)):
                    fails.append(f"M5 {ev}: параметр «{m.group(1)}» похож на персональные данные")
        serves = r.get("serves", "").strip()
        if serves in EMPTY:
            warns.append(f"M6 {ev}: не указано, какому KPI/вопросу служит")
        else:
            for s in re.split(r"[,\s]+", serves):
                if s and s not in kpi_names and s not in questions:
                    warns.append(f"M6 {ev}: Serves «{s}» — нет такого KPI или вопроса")

    for r in kpis:
        name = r["kpi"].strip("` ")
        formula = r.get("formula (events)", r.get("formula", ""))
        used = {w for w in re.findall(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b", formula)}
        if not used:
            fails.append(f"M4 {name}: формула не ссылается ни на одно событие")
        params = {p.split(":")[0].strip() for row in ev_rows for p in re.split(r",\s*", row.get("params", ""))}
        for u in sorted(used - events - params):
            fails.append(f"M4 {name}: событие «{u}» нет в таблице Events")
        if r.get("decision threshold", "").strip() in EMPTY:
            fails.append(f"M7 {name}: нет порога решения")
        q = r.get("question", "").strip()
        if questions and q and q not in questions:
            warns.append(f"M7 {name}: вопрос {q} не найден в ## Questions")

    n_steps = 0
    if a.funnels:
        fsecs = gdd_ids.sections(gdd_ids.read(a.funnels))
        for fname, lines in fsecs.items():
            for r in gdd_ids.table_rows(lines):
                ev = r.get("event", "").strip("` ")
                if not ev or "<" in ev:
                    continue
                n_steps += 1
                if ev not in events:
                    fails.append(f"M3 воронка {fname}, шаг {r.get('step', '?')}: событие «{ev}» нет в Events")

    print(f"Событий: {len(events)} · KPI: {len(kpis)} · вопросов: {len(questions - {''})} · шагов воронок: {n_steps}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    if not ev_rows:
        print("FAIL: нет таблицы `## Events`")
        return 1
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
