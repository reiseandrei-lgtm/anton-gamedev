#!/usr/bin/env python3
"""Сверка ассетов Unity-проекта с design/art/asset-list.md и design/audio/files.md (Python stdlib).

Использование:
  python3 check_import.py <Assets/_Project> --assets design/art/asset-list.md
                          [--audio design/audio/files.md --audio-root <Unity-проект>] [--stage beta]

Файл ассета находится по имени: stem = ID (допустимы суффиксы _LOD0…, _01… и префикс ph_ у плейсхолдера).
Проверки:
  IM1 файл арта (png, psd, tga, jpg, glb, gltf, fbx) без строки в asset-list — сирота (WARN)
  IM2 строка с Source cc0 / made и Status wip/done без файла в проекте (FAIL)
  IM3 плейсхолдер ph_ у ассета с Source made (FAIL); при --stage beta — любой ph_ у ассета Priority mvp/slice (FAIL)
  IM4 текстура больше Budget («≤ 1024 px» — большая сторона, из заголовка PNG) (FAIL)
  IM5 модель GLB больше Budget («≤ 800 tris») (FAIL)
  IM6 Source cc0 без URL лицензии (FAIL)
  IM7 файл из files.md отсутствует или ph_ при Status final (FAIL)
  IM8 --stage beta: ассет Priority mvp / slice всё ещё с Source placeholder / todo (FAIL — Beta без плейсхолдеров)
Выход 1, если есть FAIL.
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slice-build" / "scripts"))
import gdd_ids  # noqa: E402

ART_EXT = {".png", ".psd", ".tga", ".jpg", ".jpeg", ".glb", ".gltf", ".fbx"}
EMPTY = {"", "—", "-", "–"}
SUFFIX = re.compile(r"(_lod\d+|_\d{2,3})$")


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def glb_triangles(path):
    """Треугольники GLB: сумма count индексов / 3 по примитивам mode 4 (или вершин, если индексов нет)."""
    data = Path(path).read_bytes()
    if data[:4] != b"glTF":
        return None
    length = struct.unpack("<I", data[12:16])[0]
    doc = json.loads(data[20:20 + length].decode("utf-8"))
    acc = doc.get("accessors", [])
    tris = 0
    for mesh in doc.get("meshes", []):
        for prim in mesh.get("primitives", []):
            if prim.get("mode", 4) != 4:
                continue
            idx = prim.get("indices")
            n = acc[idx]["count"] if idx is not None else acc[prim["attributes"]["POSITION"]]["count"]
            tris += n // 3
    return tris


def budget(value):
    m = re.search(r"(\d[\d\s]*)\s*(px|tris|kb)", value.lower())
    return (int(m.group(1).replace(" ", "")), m.group(2)) if m else (None, None)


def base_id(stem):
    s = stem.lower()
    if s.startswith("ph_"):
        s = s[3:]
    return SUFFIX.sub("", s)


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--assets", required=True)
    ap.add_argument("--audio", default=None)
    ap.add_argument("--audio-root", default=None)
    ap.add_argument("--stage", choices=["alpha", "beta"], default="alpha")
    a = ap.parse_args()

    root = Path(a.root)
    fails, warns = [], []
    rows = {}
    for table in gdd_ids.all_tables(gdd_ids.read(a.assets).splitlines()):
        for r in table:
            aid = r.get("id", "").strip("` ")
            if re.fullmatch(r"[a-z0-9_]+", aid or ""):
                rows[aid] = r
    files = {}
    for f in root.rglob("*"):
        if f.suffix.lower() in ART_EXT and "/Plugins/" not in "/" + f.relative_to(root).as_posix():
            files.setdefault(base_id(f.stem), []).append(f)

    for fid, paths in sorted(files.items()):
        if fid not in rows:
            for p in paths:
                warns.append(f"IM1 {p.relative_to(root).as_posix()}: нет в asset-list (сирота)")
    for aid, r in rows.items():
        src = r.get("source", "").strip().lower()
        status = r.get("status", "").strip().lower()
        prio = r.get("priority", "").strip().lower()
        lic = r.get("license / url", r.get("license", "")).strip()
        if src == "cc0" and (lic in EMPTY or "http" not in lic):
            fails.append(f"IM6 {aid}: cc0 без URL лицензии")
        if a.stage == "beta" and prio in {"mvp", "slice"} and src in {"placeholder", "todo"}:
            fails.append(f"IM8 {aid}: Beta, а источник {src} — нужен cc0 или made")
        paths = files.get(aid, [])
        if src in {"cc0", "made"} and status in {"wip", "done"} and not paths:
            fails.append(f"IM2 {aid}: Source {src}, Status {status}, а файла в {root} нет")
        for p in paths:
            is_ph = p.stem.lower().startswith("ph_")
            if is_ph and (src == "made" or (a.stage == "beta" and prio in {"mvp", "slice"})):
                fails.append(f"IM3 {p.name}: плейсхолдер у ассета {aid} ({src}, {prio}) — заменить")
            limit, unit = budget(r.get("budget", ""))
            if limit is None:
                continue
            if unit == "px" and p.suffix.lower() == ".png":
                size = png_size(p)
                if size and max(size) > limit:
                    fails.append(f"IM4 {p.name}: {size[0]}×{size[1]} > бюджета {limit} px")
            elif unit == "tris" and p.suffix.lower() == ".glb":
                t = glb_triangles(p)
                if t is not None and t > limit:
                    fails.append(f"IM5 {p.name}: {t} tris > бюджета {limit}")
            elif unit == "kb" and p.stat().st_size > limit * 1024:
                fails.append(f"IM4 {p.name}: {p.stat().st_size // 1024} KB > бюджета {limit} KB")

    n_audio = 0
    if a.audio:
        aroot = Path(a.audio_root) if a.audio_root else Path(a.audio).parent
        for table in gdd_ids.all_tables(gdd_ids.read(a.audio).splitlines()):
            for r in table:
                f = r.get("file", "").strip("` ")
                if not f or "<" in f:
                    continue
                n_audio += 1
                p = aroot / f
                if not p.is_file():
                    fails.append(f"IM7 {f}: файла нет")
                elif Path(f).name.lower().startswith("ph_") and r.get("status", "").strip().lower() == "final":
                    fails.append(f"IM7 {f}: ph_ со статусом final")

    print(f"Asset-list: {len(rows)} · файлов арта: {sum(len(v) for v in files.values())} · аудио в files.md: {n_audio} · стадия: {a.stage}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
