#!/usr/bin/env python3
"""Агрегация кодов наблюдения плейтеста (Python stdlib).

Использование:
  python3 aggregate_codes.py notes/*.md [--window 60] [--hot 0.5]

Формат заметок — references/playtest-method.md §2:
  файл на игрока (P1.md) или разделы `## P1` в одном файле; строка `segment: <name>` (необязательно);
  строки `[mm:ss] CODE текст`, CODE ∈ C F D S Q B A N.
Вывод: коды по игрокам, доля игроков с каждым кодом (по сегментам), «горячие» окна
(доля игроков с C/F/S в окне ≥ --hot), первое S/Q у каждого игрока, нераспознанные строки.
Выход с кодом 1, если не найдено ни одного игрока или ни одной строки с кодом.
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

CODES = "CFDSQBAN"
NAMES = {"C": "confusion", "F": "frustration", "D": "delight", "S": "stuck", "Q": "quit intent",
         "B": "bug", "A": "aha", "N": "note"}
LINE = re.compile(r"^\s*[-*]?\s*\[(\d{1,2}):(\d{2})\]\s+([A-Z])\b\s*(.*)$")
PLAYER_H = re.compile(r"^##\s+(P\d+)\b")
SEGMENT = re.compile(r"^\s*segment:\s*(\S+)", re.I)
NEGATIVE = set("CFS")


def utf8_stdout():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def parse(paths):
    players = defaultdict(lambda: {"segment": "all", "events": []})
    bad = []
    for path in paths:
        default = Path(path).stem if re.fullmatch(r"P\d+", Path(path).stem) else None
        cur = default
        for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            m = PLAYER_H.match(line)
            if m:
                cur = m.group(1)
                players[cur]
                continue
            m = SEGMENT.match(line)
            if m and cur:
                players[cur]["segment"] = m.group(1)
                continue
            m = LINE.match(line)
            if m:
                if not cur:
                    bad.append(f"{path}:{n} строка с кодом вне раздела игрока")
                    continue
                code = m.group(3)
                if code not in CODES:
                    bad.append(f"{path}:{n} неизвестный код «{code}»")
                    continue
                t = int(m.group(1)) * 60 + int(m.group(2))
                players[cur]["events"].append((t, code, m.group(4).strip()))
            elif re.match(r"^\s*[-*]?\s*\[\d", line):
                bad.append(f"{path}:{n} не по формату `[mm:ss] CODE текст`")
    return players, bad


def fmt(t):
    return f"{t // 60:02d}:{t % 60:02d}"


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("notes", nargs="+")
    ap.add_argument("--window", type=int, default=60, help="размер окна, с")
    ap.add_argument("--hot", type=float, default=0.5, help="доля игроков для «горячего» окна")
    a = ap.parse_args()

    players, bad = parse(a.notes)
    players = {p: v for p, v in players.items() if v["events"]}
    if not players:
        print("FAIL: не найдено ни одного игрока со строками `[mm:ss] CODE текст`")
        return 1
    n = len(players)
    segs = Counter(v["segment"] for v in players.values())
    print(f"Игроков: {n} · сегменты: " + ", ".join(f"{s} {c}" for s, c in segs.items()))

    print("\n## Коды по игрокам")
    print("| P | Сегмент | " + " | ".join(CODES) + " | Длит. |")
    print("|---|---|" + "---|" * len(CODES) + "---|")
    for p in sorted(players, key=lambda x: int(x[1:])):
        c = Counter(code for _, code, _ in players[p]["events"])
        last = max(t for t, _, _ in players[p]["events"])
        print(f"| {p} | {players[p]['segment']} | " + " | ".join(str(c.get(k, 0)) for k in CODES) + f" | {fmt(last)} |")

    print("\n## Доля игроков с кодом")
    for k in CODES:
        who = [p for p in players if any(code == k for _, code, _ in players[p]["events"])]
        if not who:
            continue
        by_seg = Counter(players[p]["segment"] for p in who)
        seg_txt = ", ".join(f"{s} {by_seg[s]}/{segs[s]}" for s in segs if len(segs) > 1)
        print(f"- {k} {NAMES[k]}: {len(who)}/{n} ({len(who) / n:.0%})" + (f" · {seg_txt}" if seg_txt else ""))

    print(f"\n## Горячие окна (C/F/S у ≥ {a.hot:.0%} игроков, окно {a.window} с)")
    buckets = defaultdict(set)
    notes = defaultdict(list)
    for p, v in players.items():
        for t, code, text in v["events"]:
            if code in NEGATIVE:
                b = t // a.window
                buckets[b].add(p)
                notes[b].append(f"{p} {code} {text}"[:70])
    hot = [(b, ps) for b, ps in sorted(buckets.items()) if len(ps) / n >= a.hot]
    if not hot:
        print("- нет")
    for b, ps in hot:
        print(f"- {fmt(b * a.window)}–{fmt((b + 1) * a.window)}: {len(ps)}/{n} игроков")
        for s in notes[b][:5]:
            print(f"    · {s}")

    print("\n## Первое S / Q")
    for p in sorted(players, key=lambda x: int(x[1:])):
        first = next(((t, c, x) for t, c, x in sorted(players[p]["events"]) if c in "SQ"), None)
        print(f"- {p}: " + (f"[{fmt(first[0])}] {first[1]} {first[2]}" if first else "—"))

    if bad:
        print(f"\nWARN нераспознанных строк: {len(bad)}")
        for b in bad[:10]:
            print(f"  {b}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
