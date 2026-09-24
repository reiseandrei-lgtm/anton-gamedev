#!/usr/bin/env python3
"""Сравнение скриншота с эталоном без сторонних библиотек (Python stdlib: zlib, struct).

Использование:
  python3 diff_png.py <эталон.png> <снимок.png> [--tolerance 0.5] [--threshold 24] [--mask x,y,w,h ...] [--out diff.png]
  python3 diff_png.py --baseline-dir design/qa/visual --shots-dir <папка снимков> [те же флаги]
      снимок <ID>.png сравнивается с эталоном <ID>.png; нет эталона → копия в <baseline-dir>/_pending/

Пиксель отличается, если разница хотя бы одного канала RGB > --threshold (0–255).
Проверки:
  VD1 размеры не совпадают (FAIL) · VD2 доля отличающихся пикселей > --tolerance % (FAIL) ·
  VD3 максимальная разница канала > --max-delta (FAIL, если флаг задан) · VD4 эталона нет — снимок в _pending (WARN:
  эталон утверждает человек).
Поддержка PNG: 8 бит, grayscale / RGB / grayscale+alpha / RGBA, без interlace. Выход 1, если есть FAIL.
"""
import argparse
import shutil
import struct
import sys
import zlib
from pathlib import Path

CHANNELS = {0: 1, 2: 3, 4: 2, 6: 4}


def utf8_stdout():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def read_png(path):
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: не PNG")
    pos, idat, w = 8, [], None
    while pos < len(data):
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if ctype == b"IHDR":
            w, h, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", body)
            if depth != 8 or color not in CHANNELS or interlace:
                raise ValueError(f"{path}: поддерживается 8 бит без interlace (depth={depth}, color={color}, interlace={interlace})")
        elif ctype == b"IDAT":
            idat.append(body)
        elif ctype == b"IEND":
            break
        pos += 12 + length
    ch = CHANNELS[color]
    raw = zlib.decompress(b"".join(idat))
    stride = w * ch
    rows, prev = [], bytearray(stride)
    for y in range(h):
        base = y * (stride + 1)
        ftype = raw[base]
        line = bytearray(raw[base + 1:base + 1 + stride])
        if ftype == 1:
            for i in range(ch, stride):
                line[i] = (line[i] + line[i - ch]) & 255
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif ftype == 3:
            for i in range(stride):
                left = line[i - ch] if i >= ch else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 255
        elif ftype == 4:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                b = prev[i]
                c = prev[i - ch] if i >= ch else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else (b if pb <= pc else c))) & 255
        rows.append(line)
        prev = line
    return w, h, ch, rows


def rgb(row, x, ch):
    i = x * ch
    if ch >= 3:
        return row[i], row[i + 1], row[i + 2]
    return row[i], row[i], row[i]


def write_png(path, w, h, pixels):
    """pixels: список строк bytearray RGB."""
    raw = b"".join(b"\x00" + bytes(r) for r in pixels)

    def chunk(t, body):
        return struct.pack(">I", len(body)) + t + body + struct.pack(">I", zlib.crc32(t + body) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")
    Path(path).write_bytes(png)


def masked(x, y, masks):
    return any(mx <= x < mx + mw and my <= y < my + mh for mx, my, mw, mh in masks)


def compare(base, shot, a, out=None):
    """Возвращает (fails, warns, строка-итог)."""
    bw, bh, bch, brows = read_png(base)
    sw, sh, sch, srows = read_png(shot)
    if (bw, bh) != (sw, sh):
        return [f"VD1 {Path(shot).name}: {sw}×{sh} ≠ эталону {bw}×{bh}"], [], ""
    diff = total = maxd = 0
    img = [] if out else None
    for y in range(bh):
        br, sr = brows[y], srows[y]
        line = bytearray() if out else None
        for x in range(bw):
            if masked(x, y, a.mask):
                if out:
                    line += b"\x00\x00\x40"
                continue
            total += 1
            p, q = rgb(br, x, bch), rgb(sr, x, sch)
            d = max(abs(p[0] - q[0]), abs(p[1] - q[1]), abs(p[2] - q[2]))
            maxd = max(maxd, d)
            if d > a.threshold:
                diff += 1
                if out:
                    line += b"\xff\x00\x00"
            elif out:
                g = (q[0] + q[1] + q[2]) // 6
                line += bytes((g, g, g))
        if out:
            img.append(line)
    if out:
        write_png(out, bw, bh, img)
    pct = 100.0 * diff / max(total, 1)
    fails = []
    name = Path(shot).name
    if pct > a.tolerance:
        fails.append(f"VD2 {name}: отличается {pct:.2f}% пикселей > допуска {a.tolerance}%")
    if a.max_delta is not None and maxd > a.max_delta:
        fails.append(f"VD3 {name}: макс. разница канала {maxd} > {a.max_delta}")
    return fails, [], f"{name}: {bw}×{bh} · отличается {pct:.3f}% · макс. разница {maxd}"


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("baseline", nargs="?")
    ap.add_argument("shot", nargs="?")
    ap.add_argument("--baseline-dir")
    ap.add_argument("--shots-dir")
    ap.add_argument("--tolerance", type=float, default=0.5, help="допустимая доля отличающихся пикселей, %%")
    ap.add_argument("--threshold", type=int, default=24, help="разница канала, с которой пиксель считается другим")
    ap.add_argument("--max-delta", type=int, default=None)
    ap.add_argument("--mask", action="append", default=[], help="x,y,w,h — исключить область (можно несколько)")
    ap.add_argument("--out", default=None, help="diff-PNG (для одной пары) или папка (для --shots-dir)")
    a = ap.parse_args()
    a.mask = [tuple(int(v) for v in m.split(",")) for m in a.mask]

    pairs, fails, warns, lines = [], [], [], []
    if a.shots_dir:
        bdir = Path(a.baseline_dir or ".")
        for shot in sorted(Path(a.shots_dir).glob("*.png")):
            base = bdir / shot.name
            if base.is_file():
                pairs.append((base, shot))
            else:
                pend = bdir / "_pending"
                pend.mkdir(parents=True, exist_ok=True)
                shutil.copy2(shot, pend / shot.name)
                warns.append(f"VD4 {shot.name}: эталона нет — снимок в {pend.as_posix()}/, утвердить эталон должен человек")
    elif a.baseline and a.shot:
        if not Path(a.baseline).is_file():
            warns.append(f"VD4 {a.baseline}: эталона нет — утвердить снимок как эталон должен человек")
        else:
            pairs.append((Path(a.baseline), Path(a.shot)))
    else:
        sys.exit(__doc__)

    for base, shot in pairs:
        out = None
        if a.out:
            out = Path(a.out) / f"diff_{shot.name}" if a.shots_dir else Path(a.out)
            out.parent.mkdir(parents=True, exist_ok=True)
        try:
            f, w, line = compare(base, shot, a, out)
        except (ValueError, zlib.error, struct.error) as e:
            f, w, line = [f"VD1 {shot.name}: не читается ({e})"], [], ""
        fails += f
        warns += w
        if line:
            lines.append(line)

    print(f"Пар: {len(pairs)} · допуск {a.tolerance}% · порог канала {a.threshold}")
    for line in lines:
        print(f"  {line}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
