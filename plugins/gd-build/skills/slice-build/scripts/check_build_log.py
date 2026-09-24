#!/usr/bin/env python3
"""Проверка лога сборки: каждое правило GDD и критерий хендоффа закрыты доказательством (Python stdlib).

Использование:
  python3 check_build_log.py design/build/<system>.log.md --gdd design/gdd/<system>.md
                             [--handoff design/handoff/<milestone>.md] [--plan design/qa/test-plan-*.md ...]
  (лог слайса: --gdd не обязателен, проверяются ED из --handoff)

Проверки:
  BL1 ID из GDD (R/F/E) или ED хендоффа этой системы нет в логе (FAIL)
  BL2 ✅ без доказательства (FAIL)
  BL3 доказательство ссылается на T-ID, которого нет в тест-плане (FAIL, при --plan)
  BL4 mode: plan, а в логе есть ✅ — без редактора ничего не проверено (FAIL)
  BL5 ⛔ без причины (FAIL) · ⚠️ без пояснения (WARN)
  BL6 лог старше GDD (WARN: GDD менялся после сборки)
Формат лога — references/build-log.md. Общий парсер — gdd_ids.py (копия из gd: gd-router/scripts).
Выход 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gdd_ids  # noqa: E402

TID = re.compile(r"\bT-[a-z0-9_\-]+-\d{2,3}\b")
OK, WARN_MARK, NO = "✅", "⚠️", "⛔"
EMPTY = {"", "—", "-", "–"}


def log_rows(text):
    rows = []
    for table in gdd_ids.all_tables(text.splitlines()):
        if table and ("id" in table[0] or "ed" in table[0]) and ("статус" in table[0] or "status" in table[0]):
            for r in table:
                rid = (r.get("id") or r.get("ed") or "").strip("`* ")
                if rid and "<" not in rid:
                    rows.append((rid, r.get("статус", r.get("status", "")).strip(),
                                 r.get("доказательство", r.get("evidence", "")).strip()))
    return rows


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--gdd", default=None)
    ap.add_argument("--handoff", default=None)
    ap.add_argument("--plan", nargs="*", default=[])
    a = ap.parse_args()

    text = gdd_ids.read(a.log)
    fm = gdd_ids.frontmatter(text)
    mode = fm.get("mode", "").lower()
    system = fm.get("system") or (Path(a.gdd).stem if a.gdd else None)
    rows = log_rows(text)
    ids_in_log = {r[0] for r in rows}
    fails, warns = [], []

    want = {}
    if a.gdd:
        sysname, ids, w = gdd_ids.gdd_ids(a.gdd)
        warns += w
        want.update({i: d for i, d in ids.items() if re.fullmatch(r"[RFE]\d+", i)})
        if Path(a.log).stat().st_mtime < Path(a.gdd).stat().st_mtime:
            warns.append(f"BL6 лог старше {Path(a.gdd).name} — GDD менялся после сборки, сверь правила")
    if a.handoff:
        for i, d in gdd_ids.handoff_ids(a.handoff).items():
            if not i.startswith("ED"):
                continue
            m = re.fullmatch(r"ED-([a-z0-9_]+)-\d+", i)
            if m is None or (system and m.group(1) == system):
                want[i] = d
    for i, d in want.items():
        if i not in ids_in_log:
            fails.append(f"BL1 {i} нет в логе: {d[:60]}")

    plan_ids = set()
    for p in a.plan:
        plan_ids |= set(TID.findall(gdd_ids.read(p)))

    n_ok = n_warn = n_no = 0
    for rid, status, evidence in rows:
        ev_empty = evidence in EMPTY
        if OK in status:
            n_ok += 1
            if ev_empty:
                fails.append(f"BL2 {rid}: ✅ без доказательства")
            if mode == "plan":
                fails.append(f"BL4 {rid}: ✅ в режиме plan — без редактора это ⚠️")
            if a.plan:
                for t in TID.findall(evidence):
                    if t not in plan_ids:
                        fails.append(f"BL3 {rid}: {t} нет в тест-плане")
        elif NO in status:
            n_no += 1
            if ev_empty:
                fails.append(f"BL5 {rid}: ⛔ без причины")
        elif WARN_MARK in status or "⚠" in status:
            n_warn += 1
            if ev_empty:
                warns.append(f"BL5 {rid}: ⚠️ без пояснения, что не проверено")
        else:
            fails.append(f"BL5 {rid}: статус «{status}» — нужен ✅ / ⚠️ / ⛔")

    print(f"Лог: {Path(a.log).name} · система: {system or '—'} · режим: {mode or '?'} · строк: {len(rows)} "
          f"(✅ {n_ok} · ⚠️ {n_warn} · ⛔ {n_no}) · ожидалось ID: {len(want)}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
