#!/usr/bin/env python3
"""Проверка design/art/asset-list.md (Python stdlib).

Использование:
  python3 check_assets.py design/art/asset-list.md [--handoff design/handoff/<slice>.md] [--gdd design/gdd/*.md]

Проверки: A1 нейминг ID · A2 дубль ID · A3 пустое обязательное поле · A4 cc0 без лицензии/URL ·
A5 неизвестный Source/Priority/Status · A6 ассет слайса в статусе todo без источника (WARN) ·
A7 ссылка For на несуществующий ID GDD/хендоффа.
Формат — references/art-method.md §4. Выход с кодом 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gd-router" / "scripts"))
import gdd_ids  # noqa: E402

TYPES = {"spr", "tex", "mdl", "anim", "ui", "icon", "vfx", "font", "bg", "tile"}
ID_RE = re.compile(r"^([a-z]+)_[a-z0-9]+(?:_[a-z0-9]+){1,3}$")
SOURCES = {"placeholder", "cc0", "made", "todo"}
PRIORITIES = {"slice", "mvp", "later"}
STATUSES = {"todo", "wip", "done"}
REQUIRED = ["id", "type", "for", "source", "priority", "status"]


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("assets")
    ap.add_argument("--handoff", action="append", default=[])
    ap.add_argument("--gdd", nargs="*", default=[])
    a = ap.parse_args()

    known = set()
    for g in a.gdd:
        system, ids, _ = gdd_ids.gdd_ids(g)
        known |= {f"{system}#{i}" for i in ids}
    for h in a.handoff:
        known |= set(gdd_ids.handoff_ids(h))

    text = gdd_ids.read(a.assets)
    rows = []
    for table in gdd_ids.all_tables(text.splitlines()):
        if table and "id" in table[0] and "source" in table[0]:
            rows += [r for r in table if r.get("id") and "<" not in r["id"] and r["id"] != "…"]
    fails, warns, seen = [], [], set()
    for r in rows:
        aid = r["id"].strip("` ")
        m = ID_RE.match(aid)
        if not m or m.group(1) not in TYPES:
            fails.append(f"A1 {aid}: ID не по схеме <type>_<entity>_<variant>_<state> (типы: {', '.join(sorted(TYPES))})")
        elif r.get("type") and r["type"].strip() != m.group(1):
            fails.append(f"A1 {aid}: префикс ID «{m.group(1)}» не совпадает с Type «{r['type']}»")
        if aid in seen:
            fails.append(f"A2 {aid}: дубль")
        seen.add(aid)
        for f in REQUIRED:
            if not r.get(f, "").strip():
                fails.append(f"A3 {aid}: пустое поле {f}")
        src = r.get("source", "").strip().lower()
        lic = r.get("license / url", r.get("license", "")).strip()
        if src == "cc0" and lic in ("", "—", "-"):
            fails.append(f"A4 {aid}: cc0 без лицензии/URL")
        for field, allowed in (("source", SOURCES), ("priority", PRIORITIES), ("status", STATUSES)):
            v = r.get(field, "").strip().lower()
            if v and v not in allowed:
                fails.append(f"A5 {aid}: {field}=«{v}», допустимо: {', '.join(sorted(allowed))}")
        if r.get("priority", "").strip().lower() == "slice" and src == "todo":
            warns.append(f"A6 {aid}: ассет слайса без источника (todo) — нужен хотя бы placeholder")
        if known:
            for ref in re.findall(r"[a-z0-9_\-]+#[A-Z]{1,3}\d+|\b(?:ED|DD)\d+\b", r.get("for", "")):
                if ref not in known:
                    fails.append(f"A7 {aid}: ссылка {ref} не найдена в GDD/хендоффе")
    print(f"Ассетов: {len(rows)} · slice: {sum(1 for r in rows if r.get('priority','').strip().lower()=='slice')}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    if not rows:
        print("FAIL: не найдено ни одной строки таблицы ассетов (нужны колонки ID и Source)")
        return 1
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
