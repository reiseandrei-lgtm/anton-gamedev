#!/usr/bin/env python3
"""Сверка откликов (juice) с целями Game Feel: каждый визуальный Feedback замерен в кадрах (Python stdlib).

Использование:
  python3 check_juice.py design/build/<system>.log.md --gdd design/gdd/<system>.md [--map design/audio/event-map.md]

Таблица `## Juice` в логе (формат — slice-build/references/build-log.md):
  | FB | Событие | Цель (кадры) | Замер (кадры) | Допуск | Звук в том же кадре | Доказательство |
  Цель: «≤ 1», «2», «0»; допуск: «±1» или пусто (0). Замер — число кадров от события до первого кадра отклика
  (или длительность отклика — как записано в цели).
Проверки:
  JU1 визуальный Feedback GDD (колонка Visual) без строки или без замера (FAIL)
  JU2 замер вне цели с допуском (FAIL)
  JU3 цель не задана (WARN → gd:game-feel, записать цель в GDD)
  JU4 у FB есть событие в карте звука, а звук не в том же кадре / не проверен (WARN)
Выход 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slice-build" / "scripts"))
import gdd_ids  # noqa: E402

EMPTY = {"", "—", "-", "–", "нет", "none"}
NUM = re.compile(r"-?\d+(?:[.,]\d+)?")


def num(s):
    m = NUM.search(s or "")
    return float(m.group(0).replace(",", ".")) if m else None


def within(target, measured, tol):
    t = num(target)
    if t is None:
        return None
    if "≤" in target or "<=" in target:
        return measured <= t + tol
    if "≥" in target or ">=" in target:
        return measured >= t - tol
    return abs(measured - t) <= tol


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--gdd", required=True)
    ap.add_argument("--map", default=None)
    a = ap.parse_args()

    system = Path(a.gdd).stem
    fb_rows = gdd_ids.table_rows(gdd_ids.find_section(gdd_ids.sections(gdd_ids.read(a.gdd)), "feedback") or [])
    visual = {r["id"].strip("`* "): r.get("visual", "") for r in fb_rows
              if re.fullmatch(r"FB\d+", r.get("id", "").strip("`* ")) and r.get("visual", "").strip().lower() not in EMPTY}
    audio_fb = set()
    if a.map:
        for table in gdd_ids.all_tables(gdd_ids.read(a.map).splitlines()):
            for r in table:
                m = re.fullmatch(rf"{re.escape(system)}#(FB\d+)", r.get("source", "").strip("` "))
                if m:
                    audio_fb.add(m.group(1))

    juice = gdd_ids.find_section(gdd_ids.sections(gdd_ids.read(a.log)), "juice") or []
    rows = {}
    for r in gdd_ids.table_rows(juice):
        fb = r.get("fb", "").strip("`* ").split("#")[-1]
        if re.fullmatch(r"FB\d+", fb):
            rows.setdefault(fb, []).append(r)   # у одного FB может быть несколько фаз (squash, stretch)
    fails, warns = [], []
    for fb, vis in visual.items():
        phases = rows.get(fb)
        if not phases:
            fails.append(f"JU1 {system}#{fb} «{vis[:40]}»: нет строки в таблице Juice")
            continue
        for r in phases:
            what = r.get("событие", "").strip() or fb
            measured = num(r.get("замер (кадры)", r.get("замер", "")))
            target = r.get("цель (кадры)", r.get("цель", "")).strip()
            if measured is None:
                fails.append(f"JU1 {system}#{fb} ({what}): нет замера в кадрах")
            if target.lower() in EMPTY or num(target) is None:
                warns.append(f"JU3 {system}#{fb} ({what}): цель в кадрах не задана — записать в Game Feel GDD (gd:game-feel)")
            elif measured is not None:
                tol = num(r.get("допуск", "")) or 0.0
                if within(target, measured, abs(tol)) is False:
                    fails.append(f"JU2 {system}#{fb} ({what}): замер {measured:g} кадр. вне цели «{target}» (допуск ±{abs(tol):g})")
        if fb in audio_fb:
            sounds = [r.get("звук в том же кадре", "").strip().lower() for r in phases]
            if not any(s not in EMPTY and not s.startswith(("нет", "no")) for s in sounds):
                warns.append(f"JU4 {system}#{fb}: событие звука есть, а звук в том же кадре не подтверждён")
    for fb in rows:
        if fb not in visual:
            warns.append(f"JU1 {system}#{fb}: строка Juice без визуального Feedback в GDD (сверь ID)")

    print(f"Система: {system} · визуальных FB: {len(visual)} · строк Juice: {len(rows)} · FB со звуком: {len(audio_fb)}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
