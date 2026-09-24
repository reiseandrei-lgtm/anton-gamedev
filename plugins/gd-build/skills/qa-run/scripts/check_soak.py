#!/usr/bin/env python3
"""Разбор долгого прогона (soak): утечки памяти, деградация кадра, исключения (Python stdlib).

Использование:
  python3 check_soak.py design/qa/perf/<date>-soak.md [--mem-slope 1.0] [--frame-growth 10]

Таблица `## Samples` в отчёте (формат — references/qa-run-method.md §7):
  | t (s) | frame ms | memory MB | exceptions | [materials | objects | …] | [progress (что растёт при игре)] |
Проверки:
  SK1 наклон памяти (линейная регрессия) > --mem-slope МБ/мин (FAIL)
  SK2 средний кадр последней трети длиннее первой больше чем на --frame-growth % (FAIL)
  SK3 исключения в консоли за прогон (FAIL)
  SK4 прогон короче 5 минут или меньше 6 замеров — выводы слабые (WARN)
  SK5 счётчик (materials, objects, …) растёт быстрее --count-slope в минуту — объекты не освобождаются (FAIL)
  SK6 колонка progress (…) не растёт или стоит больше чем в 1/3 интервалов — игра простаивала, прогон ничего не доказал (FAIL)
Выход 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slice-build" / "scripts"))
import gdd_ids  # noqa: E402


def num(s):
    m = re.search(r"-?\d+(?:[.,]\d+)?", s or "")
    return float(m.group(0).replace(",", ".")) if m else None


def slope(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    return 0.0 if den == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--mem-slope", type=float, default=1.0, help="МБ в минуту")
    ap.add_argument("--frame-growth", type=float, default=10.0, help="%%")
    ap.add_argument("--count-slope", type=float, default=20.0, help="штук в минуту")
    a = ap.parse_args()

    samples = gdd_ids.find_section(gdd_ids.sections(gdd_ids.read(a.report)), "samples") or []
    t, frame, mem, exc, counts, progress = [], [], [], 0, {}, []
    base_cols = {"t", "frame ms", "memory mb", "exceptions"}
    for r in gdd_ids.table_rows(samples):
        vals = {k.split("(")[0].strip(): v for k, v in r.items()}
        for k, v in vals.items():
            if k not in base_cols and num(v) is not None and num(vals.get("t")) is not None:
                (progress if k.startswith("progress") else counts.setdefault(k, [])).append((num(vals["t"]), num(v)))
        ts, fr, mb = num(vals.get("t")), num(vals.get("frame ms")), num(vals.get("memory mb"))
        if ts is None:
            continue
        t.append(ts)
        frame.append(fr)
        mem.append(mb)
        exc += int(num(vals.get("exceptions")) or 0)
    fails, warns = [], []
    if len(t) < 2:
        print("FAIL SK4 в отчёте нет таблицы ## Samples с замерами")
        return 1
    dur = t[-1] - t[0]
    if dur < 300 or len(t) < 6:
        warns.append(f"SK4 прогон {dur:.0f} с, замеров {len(t)} — меньше 5 минут / 6 замеров, выводы слабые")
    mpts = [(x, y) for x, y in zip(t, mem) if y is not None]
    ms = slope([p[0] for p in mpts], [p[1] for p in mpts]) * 60 if len(mpts) > 1 else 0.0
    if ms > a.mem_slope:
        fails.append(f"SK1 память растёт {ms:.2f} МБ/мин > {a.mem_slope} — вероятна утечка")
    fr = [x for x in frame if x is not None]
    third = max(1, len(fr) // 3)
    first, last = sum(fr[:third]) / third, sum(fr[-third:]) / third
    growth = 100 * (last - first) / first if first else 0.0
    if growth > a.frame_growth:
        fails.append(f"SK2 кадр вырос на {growth:.1f}% ({first:.2f} → {last:.2f} ms) > {a.frame_growth}%")
    if exc:
        fails.append(f"SK3 исключений в консоли: {exc}")
    for name, pts in counts.items():
        cs = slope([p[0] for p in pts], [p[1] for p in pts]) * 60 if len(pts) > 1 else 0.0
        if cs > a.count_slope:
            fails.append(f"SK5 {name}: растёт {cs:.0f} в минуту ({pts[0][1]:g} → {pts[-1][1]:g}) — объекты не освобождаются")

    if progress:
        steps = [b[1] - a_[1] for a_, b in zip(progress, progress[1:])]
        idle = sum(1 for s in steps if s <= 0)
        if progress[-1][1] <= progress[0][1]:
            fails.append(f"SK6 progress не растёт ({progress[0][1]:g} → {progress[-1][1]:g}) — ввод не двигает игру, прогон ничего не доказал")
        elif steps and idle / len(steps) > 1 / 3:
            fails.append(f"SK6 progress стоял в {idle} из {len(steps)} интервалов — игра простаивала (редактор без фокуса не тикает? "
                         "PlayerSettings.runInBackground), прогон неполный")
    elif not progress:
        warns.append("SK6 нет колонки progress — не видно, что скрипт ввода действительно играл")
    print(f"Soak: {dur:.0f} с · замеров {len(t)} · память {ms:+.2f} МБ/мин · кадр {first:.2f} → {last:.2f} ms ({growth:+.1f}%) · исключений {exc}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
