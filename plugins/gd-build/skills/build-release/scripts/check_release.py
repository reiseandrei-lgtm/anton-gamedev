#!/usr/bin/env python3
"""Готовность Unity-проекта к релизной сборке: версия, .gitignore, LFS, CI-секреты, dev-флаг, SteamPipe (Python stdlib).

Использование:
  python3 check_release.py <unity-project> [--changelog CHANGELOG.md] [--tag vX.Y.Z] [--repo <корень git>] [--lfs-min-kb 500]

Ничего не меняет и не читает значения секретов — только имена `secrets.X` в workflow.
Проверки:
  RL1 PlayerSettings.bundleVersion ≠ --tag / верхней версии CHANGELOG (FAIL)
  RL2 .gitignore без Library/, Temp/, Logs/, UserSettings/ (FAIL)
  RL3 бинарные файлы (.psd .wav .fbx .glb .blend .png > --lfs-min-kb …) не под LFS в .gitattributes (FAIL)
  RL4 workflow ссылается на секреты вне ожидаемых UNITY_LICENSE / UNITY_EMAIL / UNITY_PASSWORD / STEAM_* (WARN)
  RL5 development-сборка в Build Profile или в workflow (FAIL)
  RL6 VDF SteamPipe без AppID / DepotID (FAIL)
Выход 1, если есть FAIL; 2 — не Unity-проект или проект не внутри --repo.
"""
import argparse
import fnmatch
import re
import sys
from pathlib import Path

BIN_ALWAYS = {".psd", ".wav", ".fbx", ".glb", ".gltf", ".blend", ".tga", ".tif", ".tiff", ".exr", ".mp3", ".ogg",
              ".mp4", ".mov", ".ttf", ".otf", ".bank", ".sf2", ".aif", ".aiff"}
BIN_BIG = {".png", ".jpg", ".jpeg"}
IGNORE_NEED = ("Library", "Temp", "Logs", "UserSettings")
SECRETS_OK = re.compile(r"^(UNITY_LICENSE|UNITY_EMAIL|UNITY_PASSWORD|UNITY_SERIAL|GITHUB_TOKEN|STEAM_[A-Z_]+|ANDROID_[A-Z_]+)$")
SKIP_DIRS = {"Library", "Temp", "Logs", "UserSettings", "obj", ".git", "Build", "Builds"}


def utf8_stdout():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def read(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def walk(root):
    for p in root.iterdir():
        if p.is_dir():
            if p.name not in SKIP_DIRS and not p.name.startswith("."):
                yield from walk(p)
        elif p.is_file():
            yield p


def lfs_patterns(repo):
    pats = []
    for line in read(repo / ".gitattributes").splitlines():
        parts = line.split()
        if len(parts) >= 2 and "filter=lfs" in parts[1:]:
            pats.append(parts[0])
    return pats


def under_lfs(rel, pats):
    name = rel.split("/")[-1]
    for pat in pats:
        p = pat.lstrip("/")
        if "/" in p:
            if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(rel, p.replace("**/", "")):
                return True
        elif fnmatch.fnmatch(name, p) or fnmatch.fnmatch(name.lower(), p.lower()):
            return True
    return False


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--changelog", default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--repo", default=None, help="корень git (по умолчанию — ближайший вверх от проекта с .git)")
    ap.add_argument("--lfs-min-kb", type=int, default=500)
    a = ap.parse_args()

    proj = Path(a.project).resolve()
    if not (proj / "ProjectSettings/ProjectSettings.asset").is_file():
        print(f"Не Unity-проект: {proj}")
        return 2
    repo = Path(a.repo).resolve() if a.repo else next((d for d in [proj, *proj.parents] if (d / ".git").exists()), proj)
    if repo != proj and repo not in proj.parents:
        print(f"Проект {proj} не внутри --repo {repo}")
        return 2
    fails, warns = [], []

    # RL1 версия
    m = re.search(r"^\s*bundleVersion:\s*(\S+)", read(proj / "ProjectSettings/ProjectSettings.asset"), re.M)
    bundle = m.group(1) if m else None
    want, src = None, None
    if a.tag:
        want, src = a.tag.lstrip("v"), f"тег {a.tag}"
    elif a.changelog:
        cm = re.search(r"^#+\s*\[?v?(\d+\.\d+(?:\.\d+)?)", read(a.changelog), re.M)
        want, src = (cm.group(1), f"CHANGELOG {a.changelog}") if cm else (None, None)
        if not cm:
            warns.append(f"RL1 в {a.changelog} нет заголовка с версией")
    if want and bundle != want:
        fails.append(f"RL1 bundleVersion {bundle} ≠ {want} ({src})")
    elif not want:
        warns.append(f"RL1 bundleVersion {bundle}: сверить не с чем (нет --tag и --changelog)")

    # RL2 .gitignore
    gi = read(repo / ".gitignore") + "\n" + (read(proj / ".gitignore") if proj != repo else "")
    ignored = {re.sub(r"\[(\w)\w*\]", r"\1", line.strip()).strip("/").split("/")[-1].lower()
               for line in gi.splitlines() if line.strip() and not line.startswith("#")}
    for d in IGNORE_NEED:
        if d.lower() not in ignored:
            fails.append(f"RL2 .gitignore без {d}/")

    # RL3 LFS
    pats = lfs_patterns(repo)
    unlfs = []
    for p in walk(proj):
        ext = p.suffix.lower()
        if ext in BIN_ALWAYS or (ext in BIN_BIG and p.stat().st_size > a.lfs_min_kb * 1024):
            rel = p.relative_to(repo).as_posix()
            if not under_lfs(rel, pats):
                unlfs.append(rel)
    if unlfs:
        exts = sorted({Path(u).suffix.lower() for u in unlfs})
        fails.append(f"RL3 {len(unlfs)} бинарных файлов не под LFS ({', '.join(exts)}), напр. {unlfs[0]}")

    # RL4 / RL5 workflow
    wfs = sorted((repo / ".github/workflows").glob("*.y*ml")) if (repo / ".github/workflows").is_dir() else []
    for wf in wfs:
        text = read(wf)
        for s in sorted(set(re.findall(r"secrets\.([A-Za-z0-9_]+)", text))):
            if not SECRETS_OK.match(s):
                warns.append(f"RL4 {wf.name}: секрет {s} вне ожидаемого списка — проверь, что он заведён и нужен")
        if re.search(r"-development\b|\bdevelopment:\s*true|BuildOptions\.Development", text, re.I):
            fails.append(f"RL5 {wf.name}: development-флаг в релизном workflow")
    for bp in list(proj.glob("Assets/**/*.asset")):
        t = read(bp)
        if "BuildProfile" in t or "m_BuildTarget" in t and "m_Development" in t:
            if re.search(r"^\s*m_Development:\s*1", t, re.M) and re.search(r"release|релиз", bp.stem, re.I):
                fails.append(f"RL5 {bp.relative_to(proj).as_posix()}: Development включён в релизном Build Profile")

    # RL6 SteamPipe
    for vdf in list(repo.rglob("*.vdf"))[:50]:
        t = read(vdf)
        if '"appbuild"' in t.lower() or '"depotbuild"' in t.lower():
            if not re.search(r'"appid"\s*"\d+"', t, re.I) and '"appbuild"' in t.lower():
                fails.append(f"RL6 {vdf.name}: нет AppID")
            if not re.search(r'"depotid"\s*"\d+"|"depots"\s*\{\s*"\d+"', t, re.I):
                fails.append(f"RL6 {vdf.name}: нет DepotID")

    print(f"Проект: {proj} · git: {repo} · bundleVersion: {bundle} · LFS-шаблонов: {len(pats)} · workflow: {len(wfs)}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
