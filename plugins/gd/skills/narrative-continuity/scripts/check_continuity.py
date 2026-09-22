#!/usr/bin/env python3
"""Статическая проверка промисов по графу diverts Ink.

Использование:
  python3 check_continuity.py --promises design/narrative/continuity/promises.md story.ink [other.ink ...]
  python3 check_continuity.py --promises promises.md --start camp.intro story.ink

Проверки: C1 узел не существует, C2 пэйофф недостижим из сетапа,
C3 пэйофф достижим в обход сетапа, C4 open без пэйоффа.
Граф приблизительный: условия, переменные и порядок внутри узла не учитываются.
Выход с кодом 1, если есть FAIL.
"""
import argparse
import re
import sys
from collections import defaultdict, deque

KNOT = re.compile(r"^\s*={2,}\s*(?:function\s+)?([\w]+)")
STITCH = re.compile(r"^\s*=\s*([\w]+)")
LABEL = re.compile(r"^\s*[-*+]+\s*(?:\{[^}]*\}\s*)?\(\s*([\w]+)\s*\)")
DIVERT = re.compile(r"(?:->|<-)\s*([\w.]+)")
SPECIAL = {"DONE", "END"}


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(line.split("//")[0] for line in text.splitlines())


def parse_ink(paths):
    nodes = {"__start__"}
    raw_edges = []  # (from, target, knot_context)
    first_stitch = {}
    knot = None
    cur = "__start__"
    for path in paths:
        with open(path, encoding="utf-8") as f:
            text = strip_comments(f.read())
        for line in text.splitlines():
            m = KNOT.match(line)
            if m:
                knot = cur = m.group(1)
                nodes.add(cur)
                continue
            m = STITCH.match(line)
            if m and not line.strip().startswith("=="):
                name = f"{knot}.{m.group(1)}" if knot else m.group(1)
                nodes.add(name)
                if knot and knot not in first_stitch:
                    first_stitch[knot] = name
                cur = name
                continue
            m = LABEL.match(line)
            if m:
                label = f"{cur}.{m.group(1)}"
                nodes.add(label)
                raw_edges.append((cur, label, knot))
            for t in DIVERT.findall(line):
                raw_edges.append((cur, t, knot))
    graph = defaultdict(set)
    for k, s in first_stitch.items():
        graph[k].add(s)
    unresolved = set()
    for src, t, ctx in raw_edges:
        if t in SPECIAL:
            continue
        tgt = resolve(t, src, ctx, nodes)
        if tgt:
            graph[src].add(tgt)
        else:
            unresolved.add(t)
    # стартовый узел: верхний уровень файла или первый узел
    return nodes, graph, unresolved


def resolve(t, src, ctx, nodes):
    candidates = [f"{src}.{t}"]
    if ctx:
        candidates.append(f"{ctx}.{t}")
    candidates.append(t)
    for c in candidates:
        if c in nodes:
            return c
    return None


def reachable(graph, start, blocked=None):
    seen = {start}
    q = deque([start])
    while q:
        n = q.popleft()
        for m in graph.get(n, ()):
            if m == blocked or m in seen:
                continue
            seen.add(m)
            q.append(m)
    return seen


def parse_promises(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
            if len(cells) < 4 or cells[0].lower() == "id" or set(cells[0]) <= set("-: "):
                continue
            rows.append({"id": cells[0], "setup": cells[1], "payoff": cells[2],
                         "status": cells[3].lower(), "note": cells[4] if len(cells) > 4 else ""})
    return rows


def is_ink_path(ref):
    return bool(ref) and "/" not in ref and "#" not in ref and " " not in ref


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--promises", required=True)
    ap.add_argument("--start", default=None, help="узел старта (по умолчанию: верх файла, иначе первый узел)")
    ap.add_argument("ink", nargs="*")
    a = ap.parse_args()

    promises = parse_promises(a.promises)
    fails, warns, infos = [], [], []

    if a.ink:
        nodes, graph, unresolved = parse_ink(a.ink)
        start = a.start or "__start__"
        if start == "__start__" and not graph.get("__start__"):
            real = sorted(n for n in nodes if n != "__start__")
            start = real[0] if real else start
        for t in sorted(unresolved):
            warns.append(f"divert на неизвестный узел: {t}")
    else:
        nodes, graph, start = set(), {}, None
        infos.append("Ink-файлы не переданы: проверяются только статусы.")

    for p in promises:
        pid, s, pay, st = p["id"], p["setup"], p["payoff"], p["status"]
        if st == "open" and not pay:
            warns.append(f"C4 {pid}: open без пэйоффа (сетап {s or '?'})")
            continue
        if st == "dropped" or not nodes:
            continue
        ink_s, ink_p = is_ink_path(s), is_ink_path(pay)
        if not (ink_s and ink_p):
            infos.append(f"{pid}: не Ink-путь, проверь вручную ({s} → {pay})")
            continue
        missing = [x for x in (s, pay) if x not in nodes]
        if missing:
            fails.append(f"C1 {pid}: нет узла {', '.join(missing)}")
            continue
        if pay not in reachable(graph, s):
            fails.append(f"C2 {pid}: {pay} недостижим из {s}")
        if start and start not in (s,) and pay in reachable(graph, start, blocked=s):
            warns.append(f"C3 {pid}: до {pay} можно дойти в обход {s}")

    print(f"Промисов: {len(promises)} · FAIL: {len(fails)} · WARN: {len(warns)}")
    for title, items in (("FAIL", fails), ("WARN", warns), ("INFO", infos)):
        for i in items:
            print(f"[{title}] {i}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
