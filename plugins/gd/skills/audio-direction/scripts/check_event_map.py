#!/usr/bin/env python3
"""Проверка design/audio/event-map.md против GDD и Ink (Python stdlib).

Использование:
  python3 check_event_map.py design/audio/event-map.md --gdd design/gdd/*.md [--ink story/*.ink]

Проверки:
  E1 нейминг пути (event:/ bus:/ snapshot:/) · E2 дубль · E3 нет источника / источник не найден в GDD ·
  E4 Feedback-строка GDD с аудио без события · E5 параметр без диапазона или не по неймингу ·
  E6 тип / шина / банк / пространство · E7 VO-ID нет в .ink · E8 приоритет события ≠ приоритету Feedback в GDD (WARN).
Формат — references/fmod-conventions.md. Выход с кодом 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gd-router" / "scripts"))
import gdd_ids  # noqa: E402

CATEGORIES = {"SFX", "UI", "Music", "Amb", "VO", "Stinger"}
TYPES = {"oneshot", "loop", "music", "amb", "vo", "stinger", "snapshot"}
SEG = r"[A-Z][A-Za-z0-9]*"
EVENT_RE = re.compile(rf"^event:/({SEG})(?:/{SEG}){{1,3}}$")
SNAP_RE = re.compile(rf"^snapshot:/{SEG}$")
BUS_RE = re.compile(rf"^bus:/{SEG}(?:/{SEG})*$")
PARAM_RE = re.compile(r"^(g_)?[a-z][a-z0-9_]*\s*(\(\s*-?[\d.]+\s*\.\.\s*-?[\d.]+\s*\)|\[[^\]]+\])$")
EMPTY = {"", "—", "-", "–"}
PRIORITIES = {"1", "2", "3", "4", "5"}


def parse_map(path):
    rows = []
    for table in gdd_ids.all_tables(gdd_ids.read(path).splitlines()):
        if table and "event" in table[0] and "source" in table[0]:
            rows += [r for r in table if r.get("event", "").strip("` ") and "<" not in r["event"]]
    for r in rows:
        r["event"] = r["event"].strip("` ")
    return rows


def gdd_feedback(paths):
    """({system#FBn: путь события или ''}, {system#FBn: приоритет}, все ID GDD) для FB-строк с аудио."""
    fb, fb_priority, known = {}, {}, set()
    for p in paths:
        system, ids, _ = gdd_ids.gdd_ids(p)
        known |= {f"{system}#{i}" for i in ids}
        lines = gdd_ids.find_section(gdd_ids.sections(gdd_ids.read(p)), "feedback") or []
        for row in gdd_ids.table_rows(lines):
            rid = row.get("id", "").strip("`* ")
            audio = next((v for k, v in row.items() if k.startswith("audio")), "")
            if not re.fullmatch(r"FB\d+", rid):
                continue
            if audio.strip() in EMPTY or audio.strip() in {"…", "..."}:
                continue
            m = re.search(r"event:/[A-Za-z0-9/]+", audio)
            fb[f"{system}#{rid}"] = m.group(0) if m else ""
            fb_priority[f"{system}#{rid}"] = row.get("priority", "").strip()
    return fb, fb_priority, known


def ink_ids(paths):
    ids = set()
    for p in paths:
        ids |= set(re.findall(r"#\s*id:\s*([\w.\-]+)", gdd_ids.read(p)))
    return ids


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("event_map")
    ap.add_argument("--gdd", nargs="*", default=[])
    ap.add_argument("--ink", nargs="*", default=[])
    a = ap.parse_args()

    rows = parse_map(a.event_map)
    fb, fb_priority, known = gdd_feedback(a.gdd)
    vo_ids = ink_ids(a.ink) if a.ink else None
    fails, warns, seen = [], [], set()
    paths = {r["event"] for r in rows}
    sources = set()

    for r in rows:
        ev, typ = r["event"], r.get("type", "").strip().lower()
        src = r.get("source", "").strip("` ")
        # E1
        if ev.startswith("event:/"):
            m = EVENT_RE.match(ev)
            if not m:
                fails.append(f"E1 {ev}: путь не по схеме event:/<Category>/<Sub>/<Name>, сегменты PascalCase")
            elif m.group(1) not in CATEGORIES:
                fails.append(f"E1 {ev}: категория «{m.group(1)}», допустимо: {', '.join(sorted(CATEGORIES))}")
            if re.search(r"\d+$", ev.rsplit("/", 1)[-1]):
                warns.append(f"E1 {ev}: номер в имени — вариации держи внутри события")
        elif ev.startswith("snapshot:/"):
            if not SNAP_RE.match(ev):
                fails.append(f"E1 {ev}: снапшот не по схеме snapshot:/<State>")
        else:
            fails.append(f"E1 {ev}: путь должен начинаться с event:/ или snapshot:/")
        # E2
        if ev in seen:
            fails.append(f"E2 {ev}: дубль")
        seen.add(ev)
        # E3
        if src in EMPTY:
            fails.append(f"E3 {ev}: нет источника (Source)")
        for s in re.split(r"\s*,\s*", src):
            sources.add(s)
            gp = fb_priority.get(s, "")
            pr_map = r.get("priority", "").strip()
            if gp in PRIORITIES and pr_map in PRIORITIES and gp != pr_map:
                warns.append(f"E8 {ev}: Priority {pr_map} ≠ приоритету {gp} в GDD ({s}) — выбрать один")
            if "#" in s and known and s not in known:
                fails.append(f"E3 {ev}: источник {s} не найден в переданных GDD")
            if s.startswith("ink:") and vo_ids is not None and s[4:] not in vo_ids:
                fails.append(f"E7 {ev}: VO-ID {s[4:]} нет в .ink (#id:)")
        # E5
        params = r.get("params", "").strip()
        if params not in EMPTY:
            for p in re.split(r",\s*(?![^\[]*\])", params):
                if not PARAM_RE.match(p.strip()):
                    fails.append(f"E5 {ev}: параметр «{p.strip()}» — нужен snake_case (глобальный с g_) и диапазон (a..b) или метки [a/b]")
        # E6
        if typ not in TYPES:
            fails.append(f"E6 {ev}: Type «{typ}», допустимо: {', '.join(sorted(TYPES))}")
        if typ != "snapshot":
            bus = r.get("bus", "").strip("` ")
            if not BUS_RE.match(bus):
                fails.append(f"E6 {ev}: шина «{bus}» — нужен bus:/<Name>")
            space = r.get("space", "").strip().upper()
            if space not in {"2D", "3D"}:
                fails.append(f"E6 {ev}: Space «{space}» — 2D или 3D")
            pr = r.get("priority", "").strip()
            if pr not in PRIORITIES:
                fails.append(f"E6 {ev}: Priority «{pr}» — 1…5")
            bank = r.get("bank", "").strip("` ")
            if bank not in EMPTY and not re.fullmatch(r"[A-Z][A-Za-z0-9]*", bank):
                fails.append(f"E6 {ev}: Bank «{bank}» — PascalCase (или пусто = Master)")
            if typ in {"music", "amb"} and space == "3D":
                warns.append(f"E6 {ev}: {typ} в 3D — обычно 2D")

    # E4 — покрытие Feedback-строк GDD
    for ref, path in sorted(fb.items()):
        if ref in sources:
            continue
        if path and path in paths:
            warns.append(f"E4 {ref}: событие {path} есть, но Source не ссылается на {ref}")
            continue
        fails.append(f"E4 {ref}: Feedback с аудио{(' (' + path + ')') if path else ''} — нет события в карте")

    covered = sum(1 for ref, p in fb.items() if ref in sources or (p and p in paths))
    print(f"Событий: {len(rows)} · Feedback-строк GDD с аудио: {len(fb)} · покрыто: {covered}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    if not rows:
        print("FAIL: в карте нет строк (нужна таблица с колонками Event и Source)")
        return 1
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
