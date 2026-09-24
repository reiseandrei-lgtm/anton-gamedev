#!/usr/bin/env python3
"""Cue-лист музыки против аудио-библии и файлов: состояния, длины петель, стемы, громкость, переходы (stdlib).

Использование:
  python3 check_music.py design/audio/music-cues.md --bible design/audio/audio-bible.md --root <корень путей стемов>
                         [--files design/audio/files.md] [--sr 48000] [--lufs-tol 6]
Формат music-cues.md (общий, references/music-method.md §4):
  | Cue | State | BPM | Meter | Key | Bars | Loop (samples) | Stems | Transition |
  State — одно или несколько состояний через запятую; Stems — пути WAV через запятую (от --root).
Проверки:
  MU1 состояние из «Music by state» библии без cue (FAIL)
  MU2 Loop (samples) ≠ bars × такт (sr × 60 / bpm × долей) или WAV-стем другой длины, чем Loop (FAIL)
  MU3 стемы одного cue разной длины / частоты (FAIL); стема нет на диске (FAIL)
  MU4 громкость суммы стемов вне Integrated библии ± --lufs-tol (FAIL)
  MU5 переход без длины (s / bars / beats) или точки синхронизации (FAIL)
  MU6 стем без строки в files.md (WARN)
Выход 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "sfx-design" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slice-build" / "scripts"))
import gdd_ids  # noqa: E402
import loudness  # noqa: E402

EMPTY = {"", "—", "-", "–"}
NUM = re.compile(r"-?\d+(?:[.,]\d+)?")


def num(s):
    m = NUM.search((s or "").replace("−", "-"))
    return float(m.group(0).replace(",", ".")) if m else None


def col(r, *keys):
    for k in keys:
        for h, v in r.items():
            if h.startswith(k):
                return v.strip()
    return ""


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("cues")
    ap.add_argument("--bible", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--files", default=None)
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--lufs-tol", type=float, default=6.0)
    a = ap.parse_args()

    bible = gdd_ids.read(a.bible)
    states = []
    sec = gdd_ids.find_section(gdd_ids.sections(bible), "music by state") or []
    for r in gdd_ids.table_rows(sec):
        st = col(r, "game state", "state", "состояние").strip("` ")
        if st and st not in EMPTY:
            states.append(st.lower())
    lufs_want = None
    for t in gdd_ids.all_tables(bible.splitlines()):
        for r in t:
            if num(col(r, "integrated")) is not None:
                lufs_want = num(col(r, "integrated"))
                break
        if lufs_want is not None:
            break
    listed = set()
    if a.files:
        for t in gdd_ids.all_tables(gdd_ids.read(a.files).splitlines()):
            listed |= {col(r, "file").strip("` ").replace("\\", "/") for r in t}

    cues = [r for r in gdd_ids.table_rows(gdd_ids.find_section(gdd_ids.sections(gdd_ids.read(a.cues)), "cues") or [])
            if col(r, "cue") not in EMPTY]
    if not cues:
        cues = [r for t in gdd_ids.all_tables(gdd_ids.read(a.cues).splitlines()) for r in t if col(r, "cue") not in EMPTY]
    fails, warns, lines = [], [], []
    covered = set()
    for r in cues:
        cue = col(r, "cue").strip("` ")
        covered |= {s.strip().lower() for s in col(r, "state").split(",") if s.strip()}
        bpm, bars = num(col(r, "bpm")), num(col(r, "bars"))
        meter = col(r, "meter") or "4/4"
        mm = re.match(r"(\d+)\s*/\s*(\d+)", meter)
        beats = int(mm.group(1)) * 4 / int(mm.group(2)) if mm else 4
        loop = num(col(r, "loop"))
        expect = round(a.sr * 60 / bpm * beats * bars) if bpm and bars else None
        if expect is None:
            fails.append(f"MU2 {cue}: нет BPM или Bars")
        elif loop is None or abs(loop - expect) > 1:
            fails.append(f"MU2 {cue}: Loop {loop if loop is not None else '—'} ≠ {expect} ({bars:g} тактов {meter} при {bpm:g} BPM, {a.sr} Hz)")
        tr = col(r, "transition")
        if tr in EMPTY or not re.search(r"\d", tr) or not re.search(r"\b(s|с|bar|bars|такт|beat|beats|доля)\b", tr, re.I):
            fails.append(f"MU5 {cue}: переход «{tr or '—'}» без длины (s / bars / beats) и точки синхронизации")
        stems = [s.strip().strip("`") for s in col(r, "stems").split(",") if s.strip() and s.strip() not in EMPTY]
        if not stems:
            fails.append(f"MU3 {cue}: нет стемов")
            continue
        meas, mix = [], None
        for s in stems:
            p = Path(a.root) / s
            if s.replace("\\", "/") not in listed and a.files:
                warns.append(f"MU6 {s}: нет строки в files.md")
            if not p.is_file():
                fails.append(f"MU3 {cue}: стема {s} нет на диске")
                continue
            sr, bits, ch, chans = loudness.read_wav(p)
            meas.append((s, sr, len(chans[0])))
            if sr != a.sr:
                fails.append(f"MU3 {cue}: {s} {sr} Hz ≠ {a.sr}")
            if expect and abs(len(chans[0]) - expect) > 1:
                fails.append(f"MU2 {cue}: {s} длиной {len(chans[0])} сэмплов ≠ петле {expect}")
            if mix is None:
                mix = [list(c) for c in chans]
            elif len(chans) == len(mix):
                for c, src in zip(mix, chans):
                    for i in range(min(len(c), len(src))):
                        c[i] += src[i]
        if len({m[2] for m in meas}) > 1:
            fails.append(f"MU3 {cue}: стемы разной длины: {', '.join(f'{Path(s).name} {n}' for s, _, n in meas)}")
        if mix:
            lufs, _ = loudness.integrated(mix, a.sr)
            lines.append(f"  {cue}: стемов {len(meas)} · сумма {lufs:.1f} LUFS · {meas[0][2] if meas else 0} сэмплов")
            if lufs_want is not None and abs(lufs - lufs_want) > a.lufs_tol:
                fails.append(f"MU4 {cue}: сумма стемов {lufs:.1f} LUFS вне {lufs_want:g} ±{a.lufs_tol:g}")
    for st in states:
        if st not in covered:
            fails.append(f"MU1 состояние «{st}» из библии без cue")

    print(f"Cue: {len(cues)} · состояний в библии: {len(states)} ({', '.join(states)}) · цель {lufs_want} LUFS · {a.sr} Hz")
    print("\n".join(lines))
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
