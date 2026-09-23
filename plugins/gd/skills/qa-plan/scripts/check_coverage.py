#!/usr/bin/env python3
"""Трассировка покрытия: GDD и хендофф → тест-план (Python stdlib).

Использование:
  python3 check_coverage.py design/qa/test-plan-<slice>.md --gdd design/gdd/<system>.md [...] [--handoff design/handoff/<slice>.md]

Проверки: Q1 правило/формула/edge case без теста · Q2 ED без теста · Q3 ссылка на несуществующий ID ·
Q4 дубль или неверный формат ID теста · Q5 неизвестный Type · Q6 Auto=yes не у editmode/playmode ·
Q7 DD без playtest-кейса (WARN) · Q8 smoke пуст или > 10 шагов.
Формат — references/qa-method.md §1. Выход с кодом 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gd-router" / "scripts"))
import gdd_ids  # noqa: E402

TEST_ID = re.compile(r"^T-[a-z0-9_\-]+-\d{2,3}$")
TYPES = {"editmode", "playmode", "manual", "playtest"}
COVER_PREFIXES = ("R", "F", "E")  # K и FB покрываются косвенно; их проверяют tech-design и audio-direction


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--gdd", nargs="+", required=True)
    ap.add_argument("--handoff", default=None)
    a = ap.parse_args()

    fails, warns = [], []
    targets, known = {}, set()
    for g in a.gdd:
        system, ids, w = gdd_ids.gdd_ids(g)
        warns += w
        for i, desc in ids.items():
            ref = f"{system}#{i}"
            known.add(ref)
            if i.startswith(COVER_PREFIXES) and not i.startswith("FB"):
                targets[ref] = desc
    hand = gdd_ids.handoff_ids(a.handoff) if a.handoff else {}
    known |= set(hand)

    text = gdd_ids.read(a.plan)
    cases = []
    for table in gdd_ids.all_tables(text.splitlines()):
        if table and "id" in table[0] and "covers" in table[0]:
            cases += [r for r in table if r.get("id", "").strip("` ") and "<" not in r["id"]]
    covered, seen = {}, set()
    for c in cases:
        tid = c["id"].strip("` ")
        if not TEST_ID.match(tid):
            fails.append(f"Q4 {tid}: ID не по формату T-<system>-NN")
        if tid in seen:
            fails.append(f"Q4 {tid}: дубль")
        seen.add(tid)
        typ = c.get("type", "").strip().lower()
        if typ not in TYPES:
            fails.append(f"Q5 {tid}: Type «{typ}», допустимо: {', '.join(sorted(TYPES))}")
        auto = c.get("auto", "").strip().lower()
        if auto == "yes" and typ not in {"editmode", "playmode"}:
            fails.append(f"Q6 {tid}: Auto=yes, но Type={typ}")
        if typ in {"editmode", "playmode"} and auto not in {"yes", "no"}:
            warns.append(f"Q6 {tid}: не указано Auto (yes/no)")
        refs = re.findall(r"[a-z0-9_\-]+#[A-Z]{1,3}\d+|\b(?:ED|DD)\d+\b", c.get("covers", ""))
        if not refs:
            fails.append(f"Q3 {tid}: пустое Covers")
        for ref in refs:
            if ref not in known:
                fails.append(f"Q3 {tid}: ссылка {ref} не найдена в GDD/хендоффе")
            covered.setdefault(ref, []).append((tid, typ))

    for ref, desc in targets.items():
        if ref not in covered:
            fails.append(f"Q1 {ref} без теста: {desc[:60]}")
    for eid in sorted(i for i in hand if i.startswith("ED")):
        if eid not in covered:
            fails.append(f"Q2 {eid} без теста: {hand[eid][:60]}")
    for did in sorted(i for i in hand if i.startswith("DD")):
        if not any(t == "playtest" for _, t in covered.get(did, [])):
            warns.append(f"Q7 {did} без playtest-кейса: {hand[did][:60]}")

    smoke = gdd_ids.find_section(gdd_ids.sections(text), "smoke") or []
    steps = [s for s in smoke if re.match(r"^\s*(\d+[.)]|[-*])\s+\S", s) and "…" not in s]
    if not steps:
        fails.append("Q8 раздел `## Smoke` пуст")
    elif len(steps) > 10:
        fails.append(f"Q8 smoke {len(steps)} шагов > 10 — это уже не smoke")

    n_t = len(targets)
    n_c = sum(1 for r in targets if r in covered)
    print(f"Тестов: {len(cases)} · целей (R/F/E): {n_t}, покрыто {n_c} · ED: {sum(1 for i in hand if i.startswith('ED'))} · smoke: {len(steps)}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
