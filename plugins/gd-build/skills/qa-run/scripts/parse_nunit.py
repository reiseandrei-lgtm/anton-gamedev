#!/usr/bin/env python3
"""Разбор результатов Unity Test Framework (NUnit 3 XML) и сопоставление с тест-планом (Python stdlib).

Использование:
  python3 parse_nunit.py TestResults/editmode-results.xml [TestResults/playmode-results.xml] [--plan design/qa/test-plan-<slice>.md]

T-ID теста берётся из [Category("T-jump-01")] (свойство Category) или из имени метода `T_jump_01_…`.
Выход: 0 — всё зелёное; 2 — есть падения; 3 — прогон пуст (0 тестов) или XML не читается.
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TID_CAT = re.compile(r"^T-[a-z0-9_\-]+-\d{2,3}$")
TID_NAME = re.compile(r"\bT_([a-z0-9]+(?:_[a-z0-9]+)*?)_(\d{2,3})(?:_|$)")


def utf8_stdout():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def plan_tests(path):
    """{T-ID: (type, auto)} из таблиц плана с колонками ID и Covers."""
    out, header = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c) or "id" not in header or "covers" not in header:
            continue
        row = dict(zip(header, cells + [""] * len(header)))
        tid = row.get("id", "").strip("` ")
        if TID_CAT.match(tid):
            out[tid] = (row.get("type", "").lower(), row.get("auto", "").lower())
    return out


def tid_of(case):
    for prop in case.iter("property"):
        if prop.get("name") == "Category" and TID_CAT.match(prop.get("value", "")):
            return prop.get("value")
    m = TID_NAME.search(case.get("name", ""))
    if m:
        return f"T-{m.group(1).replace('_', '-')}-{m.group(2)}"
    return None


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("xml", nargs="+")
    ap.add_argument("--plan", default=None)
    a = ap.parse_args()

    total = passed = failed = skipped = 0
    failures, ran_ids, untagged = [], set(), 0
    for x in a.xml:
        try:
            root = ET.parse(x).getroot()
        except (ET.ParseError, OSError) as e:
            print(f"FAIL {x}: не читается ({e}) — прогон, вероятно, не завершился; смотри лог")
            return 3
        run = root if root.tag == "test-run" else root.find(".//test-run")
        cases = list(root.iter("test-case"))
        t = int(run.get("total", len(cases))) if run is not None else len(cases)
        p = int(run.get("passed", 0)) if run is not None else sum(c.get("result") == "Passed" for c in cases)
        f = int(run.get("failed", 0)) if run is not None else sum(c.get("result") == "Failed" for c in cases)
        s = int(run.get("skipped", 0)) if run is not None else sum(c.get("result") == "Skipped" for c in cases)
        print(f"{Path(x).name}: total={t} passed={p} failed={f} skipped={s}")
        total, passed, failed, skipped = total + t, passed + p, failed + f, skipped + s
        for c in cases:
            tid = tid_of(c)
            if tid:
                ran_ids.add(tid)
            else:
                untagged += 1
            if c.get("result") == "Failed":
                msg = c.find("failure/message")
                text = (msg.text or "").strip().splitlines()[0] if msg is not None and msg.text else ""
                failures.append((c.get("fullname", c.get("name")), tid or "—", text[:160]))

    print(f"\nИтого: {passed}/{total} зелёных · падений {failed} · пропущено {skipped} · без T-ID {untagged}")
    if failures:
        print("\n| Test | T-ID | Сообщение |\n|---|---|---|")
        for name, tid, msg in failures:
            print(f"| {name} | {tid} | {msg} |")
    if a.plan:
        plan = plan_tests(a.plan)
        auto = {k for k, (typ, au) in plan.items() if au == "yes" and typ in ("editmode", "playmode")}
        missing = sorted(auto - ran_ids)
        extra = sorted(ran_ids - set(plan))
        print(f"\nПлан: автоматизируемых {len(auto)} · в прогоне {len(auto & ran_ids)}")
        for m in missing:
            print(f"WARN {m}: в плане Auto=yes, в прогоне нет")
        for e in extra:
            print(f"WARN {e}: тест с T-ID, которого нет в плане")
    if total == 0:
        print("FAIL прогон выполнил 0 тестов — это провал, а не зелёный (asmdef без TestRunner? фильтр?)")
        return 3
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
