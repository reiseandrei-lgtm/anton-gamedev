#!/usr/bin/env python3
"""Проверка design/tech/architecture.md против GDD (Python stdlib).

Использование:
  python3 check_knobs.py design/tech/architecture.md --gdd design/gdd/<system>.md [...]

Проверки: T1 knob GDD без строки Config map · T2 строка Config map → несуществующий knob ·
T3 цикл зависимостей модулей · T4 система GDD без модуля / зависимость от неизвестного модуля ·
T5 диапазон Config map ≠ Safe range GDD (WARN).
Формат — references/tech-method.md §1. Выход с кодом 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gd-router" / "scripts"))
import gdd_ids  # noqa: E402

NUM = re.compile(r"-?\d+(?:[.,]\d+)?")
EMPTY = {"", "—", "-", "–"}


def nums(s):
    return [float(x.replace(",", ".")) for x in NUM.findall(s or "")]


def gdd_knobs(path):
    system, ids, warns = gdd_ids.gdd_ids(path)
    ranges = {}
    lines = gdd_ids.find_section(gdd_ids.sections(gdd_ids.read(path)), "tuning knobs") or []
    for row in gdd_ids.table_rows(lines):
        rid = row.get("id", "").strip("`* ")
        if re.fullmatch(r"K\d+", rid):
            ranges[rid] = row.get("safe range", "")
    knobs = {f"{system}#{k}": ranges.get(k, "") for k in ids if k.startswith("K")}
    return system, knobs, warns


def find_cycle(graph):
    color, stack = {}, []

    def dfs(n):
        color[n] = 1
        stack.append(n)
        for m in graph.get(n, ()):
            if color.get(m) == 1:
                return stack[stack.index(m):] + [m]
            if color.get(m) is None:
                c = dfs(m)
                if c:
                    return c
        color[n] = 2
        stack.pop()
        return None

    for n in list(graph):
        if color.get(n) is None:
            c = dfs(n)
            if c:
                return c
    return None


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("architecture")
    ap.add_argument("--gdd", nargs="+", required=True)
    a = ap.parse_args()

    secs = gdd_ids.sections(gdd_ids.read(a.architecture))
    fails, warns = [], []
    knobs, systems = {}, set()
    for g in a.gdd:
        system, k, w = gdd_knobs(g)
        systems.add(system)
        knobs.update(k)
        warns += w

    cmap = gdd_ids.table_rows(gdd_ids.find_section(secs, "config map") or [])
    cmap = [r for r in cmap if r.get("knob", "").strip("` ") and "<" not in r["knob"]]
    mapped = {}
    for r in cmap:
        ref = r["knob"].strip("` ")
        mapped[ref] = r
        if ref not in knobs:
            sys_name = ref.split("#")[0]
            if sys_name in systems:
                fails.append(f"T2 {ref}: в GDD {sys_name} нет такого knob")
            else:
                warns.append(f"T2 {ref}: GDD {sys_name} не передан — не проверено")
        for f in ("config asset", "field", "type"):
            if r.get(f, "").strip() in EMPTY:
                fails.append(f"T2 {ref}: пустое поле «{f}»")
    for ref, rng in knobs.items():
        if ref not in mapped:
            fails.append(f"T1 {ref}: knob без строки в Config map (число останется в коде)")
            continue
        g, c = nums(rng), nums(mapped[ref].get("range", ""))
        if len(g) >= 2 and len(c) >= 2 and (g[0], g[-1]) != (c[0], c[-1]):
            warns.append(f"T5 {ref}: Range {c[0]:g}..{c[-1]:g} ≠ Safe range GDD {g[0]:g}..{g[-1]:g}")

    mods = gdd_ids.table_rows(gdd_ids.find_section(secs, "modules") or [])
    mods = [r for r in mods if r.get("module", "").strip() and "<" not in r["module"]]
    graph, owned = {}, set()
    names = {r["module"].strip("` ") for r in mods}
    for r in mods:
        name = r["module"].strip("` ")
        deps = [d.strip("` ") for d in re.split(r"[,\s]+", r.get("depends on", "")) if d.strip("` ") not in EMPTY]
        graph[name] = deps
        for d in deps:
            if d not in names:
                fails.append(f"T4 {name}: зависит от неизвестного модуля «{d}»")
        owned |= {s.strip("` ") for s in re.split(r"[,\s]+", r.get("systems", "")) if s.strip("` ") not in EMPTY}
    if not mods:
        fails.append("T4 нет таблицы `## Modules`")
    for s in sorted(systems - owned):
        fails.append(f"T4 система {s}: не отнесена ни к одному модулю")
    cycle = find_cycle(graph)
    if cycle:
        fails.append(f"T3 цикл зависимостей: {' → '.join(cycle)}")

    print(f"Систем: {len(systems)} · knobs: {len(knobs)} · в Config map: {len(cmap)} · модулей: {len(mods)}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
