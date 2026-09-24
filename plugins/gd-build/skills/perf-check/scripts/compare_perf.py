#!/usr/bin/env python3
"""Сверка замера производительности с бюджетами и с прошлым замером (Python stdlib).

Использование:
  python3 compare_perf.py design/qa/perf/<date>.md --budgets design/tech/budgets.md [--prev design/qa/perf/<prev>.md]

Отчёт (формат — references/perf-method.md): frontmatter `platform`, `build`, `scene`, `duration`;
таблица `## Results`:
  | ID | Metric | Budget | p50 | p95 | max | Verdict |
  ID — строка tech/budgets.md (B1…). Единицы замера = единицам бюджета (ms, s, MB, штуки).
Проверки:
  PF1 строка бюджета не замерена: нет строки в Results или пустой p95 (FAIL; «n/a: причина» — WARN)
  PF2 p95 хуже бюджета (FAIL)
  PF3 p95 хуже прошлого замера больше чем на --regress % (WARN)
  PF4 замер не на целевой платформе бюджета: platform содержит editor/редактор или не упоминает устройство (WARN)
Выход 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slice-build" / "scripts"))
import gdd_ids  # noqa: E402

NUM = re.compile(r"-?\d+(?:[.,]\d+)?")
EMPTY = {"", "—", "-", "–"}


def num(s):
    m = NUM.search(s or "")
    return float(m.group(0).replace(",", ".")) if m else None


def col(row, *names):
    for n in names:
        for k, v in row.items():
            if k.startswith(n):
                return v.strip()
    return ""


def budgets(path):
    """{ID: (метрика, бюджет-текст, платформа)} из tech/budgets.md."""
    out = {}
    for table in gdd_ids.all_tables(gdd_ids.read(path).splitlines()):
        for i, r in enumerate(table, 1):
            metric = col(r, "метрика", "metric")
            budget = col(r, "бюджет", "budget")
            if not metric or not budget:
                continue
            bid = col(r, "id").strip("`* ") or f"B{i}"
            out[bid] = (metric, budget, col(r, "платформа", "platform"))
    return out


def results(path):
    rows = gdd_ids.table_rows(gdd_ids.find_section(gdd_ids.sections(gdd_ids.read(path)), "results") or [])
    return {col(r, "id").strip("`* "): r for r in rows if col(r, "id")}


def worse(measured, budget_text):
    """True, если замер хуже бюджета. «≥ N» — больше лучше, иначе — меньше лучше."""
    b = num(budget_text)
    if b is None:
        return None
    if "≥" in budget_text or ">=" in budget_text:
        return measured < b
    return measured > b


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--budgets", required=True)
    ap.add_argument("--prev", default=None)
    ap.add_argument("--regress", type=float, default=10.0)
    a = ap.parse_args()

    fm = gdd_ids.frontmatter(gdd_ids.read(a.report))
    platform = fm.get("platform", "")
    bud = budgets(a.budgets)
    res = results(a.report)
    prev = results(a.prev) if a.prev else {}
    fails, warns = [], []

    for bid, (metric, btext, bplat) in bud.items():
        r = res.get(bid)
        p95_text = col(r, "p95") if r else ""
        na = next((v.strip() for v in (r or {}).values() if v.strip().lower().startswith("n/a")), None)
        if na:
            warns.append(f"PF1 {bid} «{metric}»: {na}")
            continue
        if r is None or p95_text in EMPTY:
            fails.append(f"PF1 {bid} «{metric}»: не замерено")
            continue
        p95 = num(p95_text)
        if p95 is None:
            fails.append(f"PF1 {bid} «{metric}»: p95 «{p95_text}» не число")
            continue
        if worse(p95, btext):
            fails.append(f"PF2 {bid} «{metric}»: p95 {p95:g} хуже бюджета «{btext}»")
        pr = prev.get(bid)
        pp = num(col(pr, "p95")) if pr else None
        if pp:
            delta = (p95 - pp) / pp * 100
            if ("≥" in btext and -delta > a.regress) or ("≥" not in btext and delta > a.regress):
                warns.append(f"PF3 {bid} «{metric}»: p95 {pp:g} → {p95:g} ({delta:+.0f} %) к прошлому замеру")
        if bplat and bplat.lower() not in ("то же", "same") and re.search(r"editor|редактор", platform, re.I):
            warns.append(f"PF4 {bid}: замер в редакторе, бюджет — «{bplat}» (редактор ≠ устройство)")

    for bid in res:
        if bid not in bud:
            warns.append(f"PF1 {bid}: строка Results без строки в budgets.md (сверь ID)")
    if not platform:
        warns.append("PF4 в frontmatter нет platform")

    print(f"Бюджетов: {len(bud)} · замерено: {len(res)} · платформа: {platform or '?'}" + (f" · прошлый: {Path(a.prev).name}" if a.prev else ""))
    for w in dict.fromkeys(warns):
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(set(warns))}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
