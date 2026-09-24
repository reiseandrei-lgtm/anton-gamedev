#!/usr/bin/env python3
"""Проверка design/release/store.md, launch.md, postlaunch.md (Python stdlib).

Использование:
  python3 check_release_plan.py design/release [--events design/analytics/events.md]

Проверки (формат — references/release-method.md):
  RP1 пункт ## Checklist без Owner или Due (YYYY-MM-DD или R-n) (FAIL)
  RP2 вехи page → demo → fest → release вне порядка (FAIL); веха без даты (WARN)
  RP3 строка с Kind text / capsule / key-art / post / email без Author: human (FAIL)
  RP4 метрика ## Metrics без Threshold или Addressee (FAIL); метрики нет среди KPI --events (WARN)
Отсутствующий файл пропускается (режим не делался). Выход 1, если есть FAIL.
"""
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gd-router" / "scripts"))
import gdd_ids  # noqa: E402

EMPTY = {"", "—", "-", "–", "?", "tbd", "TBD"}
ORDER = ["page", "demo", "fest", "release"]
PLAYER_TEXT = {"text", "capsule", "key-art", "keyart", "post", "email"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REL = re.compile(r"^R\s*[-+]\s*\d+$", re.I)


def date(v):
    v = (v or "").strip()
    if DATE.match(v):
        try:
            return dt.date.fromisoformat(v)
        except ValueError:
            return None
    return None


def rows(path, key):
    secs = gdd_ids.sections(gdd_ids.read(path))
    return [r for r in gdd_ids.table_rows(gdd_ids.find_section(secs, key) or []) if not gdd_ids._is_placeholder(r)]


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("release_dir")
    ap.add_argument("--events", default=None)
    a = ap.parse_args()

    d = Path(a.release_dir)
    files = {n: d / f"{n}.md" for n in ("store", "launch", "postlaunch")}
    present = [n for n, p in files.items() if p.is_file()]
    fails, warns = [], []
    stats = []

    # RP3 — во всех таблицах всех трёх файлов
    n_text = 0
    for n in present:
        for t in gdd_ids.all_tables(gdd_ids.read(files[n]).splitlines()):
            for r in t:
                kind = r.get("kind", "").strip("` ").lower()
                if kind not in PLAYER_TEXT:
                    continue
                n_text += 1
                rid = r.get("id") or r.get("asset") or r.get("item") or "?"
                if r.get("author", "").strip("` ").lower() != "human":
                    fails.append(f"RP3 {n}.md {rid.strip()}: {kind} для игроков без Author: human "
                                 f"(сейчас «{r.get('author', '').strip() or '—'}»)")

    if "launch" in present:
        ms = rows(files["launch"], "milestones")
        by_kind = {}
        for r in ms:
            kind, mid = r.get("kind", "").strip("` ").lower(), r.get("id", "?").strip()
            dv = date(r.get("date", ""))
            if kind in ORDER:
                if dv is None:
                    warns.append(f"RP2 {mid} ({kind}): нет даты YYYY-MM-DD")
                else:
                    by_kind.setdefault(kind, []).append((dv, mid))
        seq = [(k, min(by_kind[k])) for k in ORDER if k in by_kind]
        for (k1, (d1, m1)), (k2, (d2, m2)) in zip(seq, seq[1:]):
            if d1 > d2:
                fails.append(f"RP2 {m1} {k1} {d1} позже {m2} {k2} {d2} — порядок page → demo → fest → release")
        release = min(by_kind["release"])[0] if "release" in by_kind else None
        cl = rows(files["launch"], "checklist")
        for r in cl:
            cid = r.get("id", "?").strip()
            owner, due = r.get("owner", "").strip(), r.get("due", "").strip()
            if owner in EMPTY:
                fails.append(f"RP1 {cid}: нет владельца (Owner)")
            if due in EMPTY:
                fails.append(f"RP1 {cid}: нет даты (Due)")
            elif not (date(due) or REL.match(due)):
                fails.append(f"RP1 {cid}: Due «{due}» — нужна дата YYYY-MM-DD или R-n")
            elif release and date(due) and date(due) > release and "post" not in r.get("dept", "").lower():
                warns.append(f"RP2 {cid}: Due {due} позже релиза {release}")
        stats.append(f"вех: {len(ms)} · пунктов чеклиста: {len(cl)}")

    if "postlaunch" in present:
        kpis = set()
        if a.events:
            for r in rows(a.events, "kpis"):
                kpis.add(r.get("kpi", "").strip("` "))
        mets = rows(files["postlaunch"], "metrics")
        for r in mets:
            name = r.get("metric", "?").strip("` ")
            if r.get("threshold", "").strip() in EMPTY:
                fails.append(f"RP4 {name}: нет порога (Threshold)")
            if r.get("addressee", "").strip() in EMPTY:
                fails.append(f"RP4 {name}: нет адресата (Addressee)")
            if a.events and name not in kpis:
                warns.append(f"RP4 {name}: нет среди KPI {Path(a.events).name}")
        stats.append(f"метрик postlaunch: {len(mets)}")

    if "store" in present:
        stats.append(f"ассетов страницы: {len(rows(files['store'], 'assets'))}")
    print(f"Файлы: {', '.join(p + '.md' for p in present) or 'нет'} · {' · '.join(stats)} · текстов и арта для игроков: {n_text}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    if not present:
        print(f"FAIL: в {d} нет store.md, launch.md или postlaunch.md")
        return 1
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
