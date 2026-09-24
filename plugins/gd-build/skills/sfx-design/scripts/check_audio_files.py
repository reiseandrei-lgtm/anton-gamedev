#!/usr/bin/env python3
"""Манифест звуковых файлов против карты событий и аудио-библии: покрытие, вариации, формат, громкость, лицензии.

Использование:
  python3 check_audio_files.py design/audio/files.md --map design/audio/event-map.md
                               [--bible design/audio/audio-bible.md] [--root <корень путей File>] [--lufs-tol 6]
                               [--ffmpeg <путь>]
--root по умолчанию: Unity-проект из `audio_root` не угадывается — передай путь; без --root берётся папка files.md.
Формат files.md (общий): | File | Event | Variation | Source | License | URL | Author | LUFS | Peak | Status |
Проверки:
  AF1 событие карты (кроме snapshot) без файла или файл из манифеста не найден на диске (FAIL)
  AF2 файлов события меньше, чем Variations в карте (FAIL)
  AF3 частота / битность ≠ библии (по умолчанию 48 кГц, 16 бит) (FAIL; у Status ph — WARN)
  AF4 громкость вне Integrated библии ± --lufs-tol или пик выше True peak библии (FAIL; ph — WARN).
      True peak — через ffmpeg (ebur128), если найден; иначе sample peak с пометкой «sample»
  AF5 внешний источник (cc0, made, license ≠ own) без License или URL (FAIL)
  AF6 `ph_` в имени файла со статусом final / made (FAIL)
Выход 1, если есть FAIL.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slice-build" / "scripts"))
import gdd_ids  # noqa: E402
import loudness  # noqa: E402

EMPTY = {"", "—", "-", "–"}
NUM = re.compile(r"-?\d+(?:[.,]\d+)?")


def num(s):
    m = NUM.search((s or "").replace("−", "-"))
    return float(m.group(0).replace(",", ".")) if m else None


def rows(path):
    out = []
    for t in gdd_ids.all_tables(gdd_ids.read(path).splitlines()):
        out += t
    return out


def bible_targets(path):
    text = gdd_ids.read(path) if path else ""
    sr = num(m.group(1)) * 1000 if (m := re.search(r"(\d{2}(?:[.,]\d)?)\s*(?:kHz|кГц)", text)) else 48000
    bits = int(m.group(1)) if (m := re.search(r"(\d{2})\s*[- ]?(?:bit|бит)", text)) else 16
    lufs = peak = None
    for r in rows(path) if path else []:
        i = next((v for k, v in r.items() if k.startswith("integrated")), None)
        p = next((v for k, v in r.items() if k.startswith("true peak")), None)
        if i and num(i) is not None:
            lufs, peak = num(i), num(p) if p else None
            break
    return int(sr), bits, lufs, peak


def find_ffmpeg(explicit):
    if explicit:
        return explicit
    hit = shutil.which("ffmpeg")
    if hit:
        return hit
    base = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
    return next((str(p) for p in base.glob("*FFmpeg*/*/bin/ffmpeg.exe")), None) if base.is_dir() else None


def true_peak(ffmpeg, path):
    try:
        r = subprocess.run([ffmpeg, "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                            "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.search(r"True peak:\s*\n\s*Peak:\s*(-?[\d.]+|-inf)", r.stderr)
    return float(m.group(1)) if m and m.group(1) != "-inf" else None


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("files")
    ap.add_argument("--map", required=True)
    ap.add_argument("--bible", default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--lufs-tol", type=float, default=6.0)
    ap.add_argument("--ffmpeg", default=None)
    a = ap.parse_args()

    root = Path(a.root) if a.root else Path(a.files).parent
    sr_want, bits_want, lufs_want, peak_want = bible_targets(a.bible)
    ff = find_ffmpeg(a.ffmpeg)
    fails, warns, table = [], [], []

    manifest = [r for r in rows(a.files) if r.get("file", "").strip() not in EMPTY]
    by_event = {}
    for r in manifest:
        by_event.setdefault(r.get("event", "").strip("` "), []).append(r)

    for e in rows(a.map):
        ev = e.get("event", "").strip("` ")
        if not ev or ev.startswith("snapshot:") or e.get("type", "").strip() == "snapshot":
            continue
        have = by_event.get(ev, [])
        if not have:
            fails.append(f"AF1 {ev}: нет файла в манифесте")
            continue
        need = num(e.get("variations", ""))
        if need and len(have) < need:
            fails.append(f"AF2 {ev}: файлов {len(have)} < вариаций {need:g} в карте")

    for r in manifest:
        rel = r["file"].strip("` ")
        status = r.get("status", "").strip().lower()
        soft = status in ("ph", "todo")
        src = r.get("source", "").strip().lower()
        lic = r.get("license", "").strip()
        if "ph_" in Path(rel).name and status in ("final", "made"):
            fails.append(f"AF6 {rel}: `ph_` в имени при статусе {status}")
        if (src in ("cc0", "made", "external") or (lic and lic.lower() not in ("own", "свой") and lic not in EMPTY)) \
                and src != "synth" and (lic in EMPTY or r.get("url", "").strip() in EMPTY):
            fails.append(f"AF5 {rel}: источник «{src}» без License или URL")
        path = root / rel
        if not path.is_file():
            fails.append(f"AF1 {rel}: файла нет на диске ({root})")
            continue
        try:
            m = loudness.measure(path)
        except (ValueError, EOFError, OSError) as ex:
            fails.append(f"AF3 {rel}: не читается как PCM WAV ({ex})")
            continue
        target = warns if soft else fails
        if m["sr"] != sr_want or m["bits"] != bits_want:
            target.append(f"AF3 {rel}: {m['sr']} Hz {m['bits']} bit, по библии {sr_want} Hz {bits_want} bit")
        tp = true_peak(ff, path) if ff else None
        peak, kind = (tp, "true") if tp is not None else (m["peak_db"], "sample")
        if lufs_want is not None and abs(m["lufs"] - lufs_want) > a.lufs_tol:
            target.append(f"AF4 {rel}: {m['lufs']:.1f} LUFS вне {lufs_want:g} ±{a.lufs_tol:g}")
        if peak_want is not None and peak > peak_want:
            target.append(f"AF4 {rel}: {kind} peak {peak:.1f} > {peak_want:g}")
        table.append(f"  {rel}: {m['lufs']:.1f} LUFS{' (short)' if m['short'] else ''} · {kind} peak {peak:.1f} · "
                     f"{m['sr']} Hz {m['bits']} bit · {m['duration']:.2f} s · {status or '?'}")

    print(f"Файлов: {len(manifest)} · событий с файлами: {len(by_event)} · библия: {sr_want} Hz {bits_want} bit, "
          f"{lufs_want if lufs_want is not None else '?'} LUFS, peak {peak_want if peak_want is not None else '?'} · "
          f"true peak: {'ffmpeg' if ff else 'нет ffmpeg — sample peak'}")
    print("\n".join(table))
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
