#!/usr/bin/env python3
"""Проверка GLB против строки design/art/asset-list.md: бюджет, имена, габариты, LOD, клипы (Python stdlib).

Использование:
  python3 check_glb.py <file.glb> [--asset-list design/art/asset-list.md] [--id <ID>] [--fps 30] [--frame-tol 1]

ID по умолчанию — имя файла без расширения. Из строки asset-list берутся:
  Size (`1×2 u`, `0.5 u`) — габариты в метрах ±10 %; Budget (`800 tris`, `2 mat`) — треугольники и материалы;
  States / frames (`idle 24f, walk 32f`) — клипы и длительность в кадрах (тип anim или модель с клипами).
Проверки:
  GL1 треугольников больше бюджета (FAIL)          GL2 материалов больше бюджета (FAIL)
  GL3 ни узел, ни меш не называется ID (FAIL)      GL4 габариты вне Size ±10 % (FAIL)
  GL5 клипа из asset-list нет в файле (FAIL)       GL6 длительность клипа вне кадров ± --frame-tol (FAIL)
  GL7 LOD-цепочка с дырой или LODn не легче LODn-1 (FAIL)
  GL8 масштаб узла ≠ 1 (не применён) (WARN)       GL9 строки ID нет в asset-list (WARN)
Выход 1, если есть FAIL; 2 — файл не GLB.
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

NUM = re.compile(r"\d+(?:[.,]\d+)?")


def utf8_stdout():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def load_glb(path):
    data = Path(path).read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise ValueError("нет сигнатуры glTF")
    version, length = struct.unpack_from("<II", data, 4)
    if version != 2:
        raise ValueError(f"glTF версии {version}, нужна 2")
    clen, ctype = struct.unpack_from("<II", data, 12)
    if ctype != 0x4E4F534A:
        raise ValueError("первый чанк не JSON")
    return json.loads(data[20:20 + clen].decode("utf-8"))


def asset_row(path, aid):
    text = Path(path).read_text(encoding="utf-8")
    header = None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        row = dict(zip(header, cells))
        if row.get("id", "").strip("` ") == aid:
            return row
    return None


def get(row, *keys):
    for k in keys:
        for h, v in row.items():
            if h.startswith(k):
                return v
    return ""


def world_scales(gltf):
    """Масштаб каждого узла с учётом родителей (вращение не учитывается — габариты приблизительные)."""
    nodes = gltf.get("nodes", [])
    parent = {c: i for i, n in enumerate(nodes) for c in n.get("children", [])}
    out = {}
    for i in range(len(nodes)):
        s, j = [1.0, 1.0, 1.0], i
        while j is not None:
            ns = nodes[j].get("scale", [1, 1, 1])
            s = [s[k] * ns[k] for k in range(3)]
            j = parent.get(j)
        out[i] = s
    return out


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("glb")
    ap.add_argument("--asset-list", default=None)
    ap.add_argument("--id", default=None)
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--frame-tol", type=float, default=1.0)
    a = ap.parse_args()

    aid = a.id or Path(a.glb).stem
    try:
        g = load_glb(a.glb)
    except (OSError, ValueError, UnicodeDecodeError) as e:
        print(f"Не GLB: {a.glb}: {e}")
        return 2
    acc, meshes, nodes = g.get("accessors", []), g.get("meshes", []), g.get("nodes", [])
    fails, warns = [], []

    def tris(mi):
        t = 0
        for p in meshes[mi].get("primitives", []):
            if p.get("mode", 4) != 4:
                continue
            idx = p.get("indices")
            t += (acc[idx]["count"] if idx is not None else acc[p["attributes"]["POSITION"]]["count"]) // 3
        return t

    mesh_tris = {i: tris(i) for i in range(len(meshes))}
    scales = world_scales(g)
    lo, hi = [float("inf")] * 3, [float("-inf")] * 3
    lod = {}
    for ni, n in enumerate(nodes):
        if "mesh" not in n:
            continue
        name = n.get("name") or meshes[n["mesh"]].get("name", "")
        m = re.search(r"_LOD(\d+)$", name, re.I)
        if m:
            lod[int(m.group(1))] = mesh_tris[n["mesh"]]
        if m and int(m.group(1)) > 0:
            continue                              # габариты и бюджет — по LOD0 / единственному мешу
        s = scales[ni]
        for p in meshes[n["mesh"]].get("primitives", []):
            pa = acc[p["attributes"]["POSITION"]]
            if "min" in pa and "max" in pa:
                t = n.get("translation", [0, 0, 0])
                for k in range(3):
                    lo[k] = min(lo[k], pa["min"][k] * s[k] + t[k])
                    hi[k] = max(hi[k], pa["max"][k] * s[k] + t[k])
        if any(abs(v - 1) > 1e-4 for v in n.get("scale", [1, 1, 1])):
            warns.append(f"GL8 узел «{name}»: масштаб {n.get('scale')} не применён (Ctrl+A → Scale в Blender)")
    total_tris = lod.get(0) if lod else sum(mesh_tris.values())
    mats = len(g.get("materials", []))
    dims = [round(hi[k] - lo[k], 3) if hi[k] > lo[k] else 0.0 for k in range(3)]

    names = [n.get("name", "") for n in nodes] + [m.get("name", "") for m in meshes]
    if not any(nm == aid or re.fullmatch(rf"{re.escape(aid)}_LOD\d+", nm, re.I) for nm in names):
        fails.append(f"GL3 ни узел, ни меш не называется «{aid}» (есть: {', '.join(sorted(set(filter(None, names)))[:5])})")

    if lod:
        keys = sorted(lod)
        if keys != list(range(len(keys))):
            fails.append(f"GL7 LOD-цепочка с дырой: {keys}")
        for k in keys[1:]:
            if k - 1 in lod and lod[k] >= lod[k - 1]:
                fails.append(f"GL7 LOD{k} ({lod[k]} tris) не легче LOD{k - 1} ({lod[k - 1]} tris)")

    clips = {}
    for an in g.get("animations", []):
        ins = [acc[s["input"]] for s in an.get("samplers", [])]
        dur = (max((i.get("max", [0])[0] for i in ins), default=0.0)
               - min((i.get("min", [0])[0] for i in ins), default=0.0))
        clips[an.get("name", "")] = dur

    row = asset_row(a.asset_list, aid) if a.asset_list else None
    if a.asset_list and row is None:
        warns.append(f"GL9 строки «{aid}» нет в {a.asset_list}")
    if row:
        budget = get(row, "budget", "бюджет")
        bt = re.search(r"(\d[\d\s]*)\s*(?:tris|tri|треуг)", budget, re.I)
        bm = re.search(r"(\d+)\s*(?:mat|мат)", budget, re.I)
        if bt and total_tris > int(bt.group(1).replace(" ", "")):
            fails.append(f"GL1 {total_tris} tris > бюджета {bt.group(1).strip()}")
        if bm and mats > int(bm.group(1)):
            fails.append(f"GL2 {mats} материалов > бюджета {bm.group(1)}")
        size = get(row, "size", "размер")
        want = sorted((float(x.replace(",", ".")) for x in NUM.findall(size)), reverse=True) if re.search(r"\bu\b|\bm\b|м\b", size) else []
        have = sorted(dims, reverse=True)
        for k, w in enumerate(want[:3]):
            if w > 0 and abs(have[k] - w) / w > 0.10:
                fails.append(f"GL4 габарит {k + 1} {have[k]:g} м вне {w:g} ±10 % (Size «{size}»)")
        frames = get(row, "states", "frames", "состояния")
        for clip, fr in re.findall(r"([A-Za-z_][\w-]*)\s*[:=]?\s*(\d+)\s*f\b", frames):
            if clip not in clips:
                fails.append(f"GL5 клипа «{clip}» нет в файле (есть: {', '.join(clips) or 'нет'})")
                continue
            got = clips[clip] * a.fps
            if abs(got - int(fr)) > a.frame_tol:
                fails.append(f"GL6 клип «{clip}»: {got:.1f} кадр. при {a.fps:g} fps, нужно {fr} ±{a.frame_tol:g}")

    print(f"{Path(a.glb).name}: ID {aid} · tris {total_tris} · материалов {mats} · габариты {dims[0]:g}×{dims[1]:g}×{dims[2]:g} м"
          f" · LOD {sorted(lod) or '—'} · клипы {', '.join(f'{k} {v * a.fps:.0f}f' for k, v in clips.items()) or '—'}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
