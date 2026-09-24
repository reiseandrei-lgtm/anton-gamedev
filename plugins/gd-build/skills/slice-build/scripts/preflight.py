#!/usr/bin/env python3
"""Preflight перед сборкой: Unity-проект, редактор, пакеты, design/, внешние инструменты (Python stdlib).

Использование:
  python3 preflight.py [<unity-project>] [--design design] [--slice <slice>] [--for sfx|music|model|anim|fmod|release|loc|analytics]

Ничего не меняет. Печатает найденное и рекомендуемый режим:
  live — есть всё нужное для задачи (для Unity-задач связь всё равно проверить пробой MCP);
  plan — чего-то нет: план + чеклист, всё помечается «не проверено».
Инструменты: Blender (PATH, BLENDER_PATH, Program Files, <диск>:\\Blender, библиотеки Steam), Blender MCP (аддон + сервер
в конфиге Claude Code), ffmpeg, sox, FluidSynth (PATH, пакеты WinGet, <диск>:\\Tools), SoundFont (SOUNDFONT, *.sf2 в
известных папках), FMOD Studio (fmodstudiocl). --for model/sfx/music Unity-проект не требуют.
Код выхода всегда 0 (это отчёт, а не проверка); 2 — неверные аргументы.
"""
import argparse
import json
import os
import re
import shutil
import string
import sys
from pathlib import Path

WIN = os.name == "nt"
EXE = ".exe" if WIN else ""
NEEDS = {                      # задача → (нужен Unity-проект, обязательные инструменты)
    "sfx": (False, ["ffmpeg", "sox"]),
    "music": (False, ["fluidsynth", "soundfont"]),
    "model": (False, ["blender"]),
    "anim": (True, []),
    "fmod": (True, ["fmodstudiocl"]),
    "release": (True, []),
    "loc": (True, []),
    "analytics": (True, []),
}
INSTALL = {                    # подсказки; ставит человек после «да»
    "blender": "winget install BlenderFoundation.Blender (или Steam); путь можно задать в BLENDER_PATH",
    "ffmpeg": "winget install Gyan.FFmpeg.Essentials",
    "sox": "winget install ChrisBagwell.SoX",
    "fluidsynth": "zip с github.com/FluidSynth/fluidsynth/releases (win10-x64), папку bin — в PATH",
    "soundfont": "FluidR3_GM.sf2 (MIT) с github.com/pianobooster/fluid-soundfont/releases, путь — в SOUNDFONT",
    "fmodstudiocl": "FMOD Studio с fmod.com (нужен вход на сайт — шаг человека)",
}

PACKAGES = {
    "com.unity.inputsystem": "Input System",
    "com.unity.test-framework": "Test Framework",
    "com.unity.render-pipelines.universal": "URP",
    "com.unity.localization": "Localization",
    "com.coplaydev.unity-mcp": "MCP: CoplayDev/unity-mcp",
    "com.ivanmurzak.unity.mcp": "MCP: IvanMurzak/Unity-MCP",
}
MCP_PACKAGES = {"com.coplaydev.unity-mcp", "com.ivanmurzak.unity.mcp"}


def utf8_stdout():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def hub_roots():
    """Папки редакторов Unity Hub: «Installs location» из настроек Hub + стандартные."""
    home = Path.home()
    roots = [Path("C:/Program Files/Unity/Hub/Editor"), Path("/Applications/Unity/Hub/Editor"),
             home / "Unity/Hub/Editor"]
    for cfg in (Path(os.environ.get("APPDATA", "")) / "UnityHub/secondaryInstallPath.json",
                home / "Library/Application Support/UnityHub/secondaryInstallPath.json",
                home / ".config/UnityHub/secondaryInstallPath.json"):
        try:
            custom = json.loads(cfg.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(custom, str) and custom:
            roots.insert(0, Path(custom))
    return roots


def editor_candidates(version):
    cands = []
    env = os.environ.get("UNITY_EDITOR_PATH")
    if env:
        cands.append(Path(env))
    for root in hub_roots():
        cands += [root / version / "Editor/Unity.exe", root / version / "Unity.app", root / version / "Editor/Unity"]
    return cands


def installed_editors():
    found = []
    for root in hub_roots():
        if root.is_dir():
            found += sorted(p.name for p in root.iterdir() if p.is_dir() and re.match(r"\d+\.", p.name))
    return found


def read_setting(path, key):
    try:
        m = re.search(rf"^\s*{key}:\s*(\S+)", path.read_text(encoding="utf-8", errors="replace"), re.M)
        return m.group(1) if m else None
    except OSError:
        return None


def drives():
    if not WIN:
        return []
    return [Path(f"{d}:/") for d in string.ascii_uppercase[2:] if Path(f"{d}:/").exists()]


def first(paths):
    return next((Path(p) for p in paths if p and Path(p).is_file()), None)


def steam_libraries():
    libs = []
    for root in (Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Steam",
                 Path.home() / ".steam/steam", Path.home() / "Library/Application Support/Steam"):
        vdf = root / "steamapps/libraryfolders.vdf"
        if vdf.is_file():
            libs.append(root)
            libs += [Path(p.replace("\\\\", "\\")) for p in
                     re.findall(r'"path"\s+"([^"]+)"', vdf.read_text(encoding="utf-8", errors="replace"))]
    return list(dict.fromkeys(libs))


def find_blender():
    cands = [os.environ.get("BLENDER_PATH"), shutil.which("blender")]
    pf = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Blender Foundation"
    if pf.is_dir():
        cands += sorted((str(p) for p in pf.glob("*/blender.exe")), reverse=True)
    cands += [str(d / "Blender" / "blender.exe") for d in drives()]
    cands += [str(lib / "steamapps/common/Blender" / f"blender{EXE}") for lib in steam_libraries()]
    cands += ["/Applications/Blender.app/Contents/MacOS/Blender"]
    return [Path(c) for c in dict.fromkeys(filter(None, cands)) if Path(c).is_file()]


def find_tool(name):
    hit = shutil.which(name)
    if hit:
        return Path(hit)
    roots = []
    if WIN:
        roots.append(Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages")
        roots += [d / "Tools" for d in drives()]
    for root in roots:
        if root.is_dir():
            for depth in ("*", "*/*", "*/*/*", "*/*/*/*"):
                found = next(iter(root.glob(f"{depth}/{name}{EXE}")), None)
                if found:
                    return found
    return None


def find_soundfont():
    env = os.environ.get("SOUNDFONT")
    if env and Path(env).is_file():
        return Path(env)
    dirs = [Path("/usr/share/sounds/sf2"), Path("/usr/share/soundfonts"), Path.home() / "soundfonts"]
    dirs += [d / "Tools" / "SoundFonts" for d in drives()] + [d / "SoundFonts" for d in drives()]
    for d in dirs:
        if d.is_dir():
            sf = sorted(d.glob("*.sf2"), key=lambda p: ("gm" not in p.name.lower(), p.name))
            if sf:
                return sf[0]
    return None


def find_fmodstudiocl():
    cands = [shutil.which("fmodstudiocl")]
    for base in [Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "FMOD SoundSystem",
                 Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "FMOD SoundSystem"] + \
                [d / "FMOD" for d in drives()]:
        if base.is_dir():
            cands += sorted((str(p) for p in base.glob(f"FMOD Studio*/fmodstudiocl{EXE}")), reverse=True)
    return first(cands)


def blender_mcp():
    """(аддон, сервер в конфиге Claude Code) — пути или None."""
    addon = None
    for base in (Path(os.environ.get("APPDATA", "")) / "Blender Foundation/Blender",
                 Path.home() / "Library/Application Support/Blender", Path.home() / ".config/blender"):
        if base.is_dir():
            addon = next(iter(sorted(base.glob("*/scripts/addons/blender_mcp.py"), reverse=True)), None) or addon
    server = None
    for cfg in (Path.home() / ".claude.json", Path(".mcp.json")):
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        blobs = [data.get("mcpServers", {})] + [p.get("mcpServers", {}) for p in data.get("projects", {}).values()]
        for servers in blobs:
            for name, spec in servers.items():
                if "blender" in (name + json.dumps(spec)).lower():
                    server = f"{name} ({cfg.name})"
    return addon, server


def tools_report():
    """{инструмент: путь или None} + строки отчёта."""
    blenders = find_blender()
    addon, server = blender_mcp()
    found = {
        "blender": blenders[0] if blenders else None,
        "ffmpeg": find_tool("ffmpeg"),
        "sox": find_tool("sox"),
        "fluidsynth": find_tool("fluidsynth"),
        "soundfont": find_soundfont(),
        "fmodstudiocl": find_fmodstudiocl(),
    }
    lines = ["", "Инструменты:"]
    for k, v in found.items():
        extra = f" (ещё: {', '.join(str(b) for b in blenders[1:])})" if k == "blender" and len(blenders) > 1 else ""
        lines.append(f"  {k}: {v or 'нет'}{extra}")
    lines.append(f"  Blender MCP: аддон {addon or 'нет'} · сервер {server or 'нет'}"
                 + (" — сокет аддона живёт только в открытом Blender с GUI" if addon and server else ""))
    found["blender_mcp"] = addon if (addon and server) else None
    return found, lines


def status(path):
    try:
        m = re.search(r"^status:\s*(\w+)", path.read_text(encoding="utf-8"), re.M)
        return m.group(1) if m else "?"
    except OSError:
        return None


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--design", default="design")
    ap.add_argument("--slice", default=None)
    ap.add_argument("--for", dest="task", choices=sorted(NEEDS), default=None)
    a = ap.parse_args()
    need_unity, required = NEEDS.get(a.task, (True, []))

    proj = Path(a.project)
    ok, lines, missing = True, [], []

    ver_file = proj / "ProjectSettings/ProjectVersion.txt"
    version = None
    if ver_file.is_file():
        m = re.search(r"m_EditorVersion:\s*(\S+)", ver_file.read_text(encoding="utf-8", errors="replace"))
        version = m.group(1) if m else None
        lines.append(f"Unity-проект: {proj.resolve()} · версия {version or '?'}")
    else:
        ok = False
        missing.append("Unity-проект (нет ProjectSettings/ProjectVersion.txt) — создай проект в Unity Hub (Unity 6, шаблон URP) или укажи путь")
        lines.append(f"Unity-проект: не найден в {proj.resolve()}")

    if version:
        exe = next((c for c in editor_candidates(version) if c.exists()), None)
        if exe:
            lines.append(f"Редактор {version}: {exe}")
        else:
            ok = False
            others = installed_editors()
            missing.append(f"редактор Unity {version} (установлены: {', '.join(others) or 'нет'}) — поставь через Unity Hub")
            lines.append(f"Редактор {version}: не найден (стандартные пути Hub и Installs location)")
        if (proj / "Temp/UnityLockfile").exists():
            lines.append("Temp/UnityLockfile есть — редактор, вероятно, открыт (для MCP это нужно; для headless-тестов — закрыть)")

    manifest = proj / "Packages/manifest.json"
    deps, testables = {}, []
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            deps, testables = data.get("dependencies", {}), data.get("testables", [])
        except (ValueError, OSError):
            lines.append("Packages/manifest.json не читается как JSON")
    for pkg, name in PACKAGES.items():
        if pkg in deps:
            lines.append(f"Пакет {name}: {deps[pkg][:60]}")
    has_mcp = any(p in deps for p in MCP_PACKAGES)
    if manifest.is_file() and not has_mcp:
        ok = False
        missing.append("бесплатный Unity MCP в проекте (CoplayDev/unity-mcp — см. references/mcp-actions.md)")
    if manifest.is_file():
        for pkg in ("com.unity.inputsystem", "com.unity.test-framework"):
            if pkg not in deps:
                missing.append(f"пакет {PACKAGES[pkg]} ({pkg})")
        if "com.unity.inputsystem" in deps:
            if "com.unity.inputsystem" not in testables:
                missing.append('InputTestFixture: в Packages/manifest.json нужно "testables": ["com.unity.inputsystem"] '
                               "(иначе нет сборки Unity.InputSystem.TestFramework)")
            handler = read_setting(proj / "ProjectSettings/ProjectSettings.asset", "activeInputHandler")
            if handler == "0":
                missing.append("Active Input Handling = Input Manager (Old): Input System не получает ввод — "
                               "Player Settings → Active Input Handling → Input System Package или Both, затем перезапуск редактора")
    if manifest.is_file() and a.task == "loc" and "com.unity.localization" not in deps:
        ok = False
        missing.append("пакет Localization (com.unity.localization) — без него loc-build в режиме plan (CSV и проверка без Unity); "
                       "ставится через Package Manager → Unity Registry после «да» человека")
    if has_mcp:
        lines.append("MCP: после установки пакета мост стартует не сам — Window → MCP for Unity → Start Session "
                     "(или авто-старт в настройках); проба — чтение консоли")

    assets = proj / "Assets"
    if assets.is_dir():
        fmod = assets / "Plugins/FMOD"
        lines.append(f"FMOD for Unity: {'есть' if fmod.is_dir() else 'нет (нужен, если в design/ есть event-map)'}")
        test_asm = [p for p in assets.rglob("*.asmdef")
                    if "TestRunner" in p.read_text(encoding="utf-8", errors="replace")]
        lines.append(f"Тестовые asmdef: {len(test_asm)}" + (f" ({', '.join(p.stem for p in test_asm[:5])})" if test_asm else ""))

    mcp_json = proj / ".mcp.json"
    if mcp_json.is_file():
        lines.append(f".mcp.json проекта: серверы {', '.join(json.loads(mcp_json.read_text(encoding='utf-8')).get('mcpServers', {}))}")

    d = Path(a.design)
    lines.append(f"design/: {d.resolve() if d.is_dir() else 'не найдена'}")
    if d.is_dir():
        handoffs = sorted((d / "handoff").glob("*.md")) if (d / "handoff").is_dir() else []
        if a.slice:
            handoffs = [h for h in handoffs if h.stem == a.slice]
        if not handoffs and not a.task:
            missing.append(f"design/handoff/{a.slice or '<slice>'}.md — без хендоффа сборка не начинается")
        for h in handoffs:
            lines.append(f"  handoff/{h.name}: {status(h)}")
        for rel in ("tech/architecture.md", "art/asset-list.md", "audio/event-map.md"):
            st = status(d / rel)
            lines.append(f"  {rel}: {st or 'нет'}")
            if rel == "tech/architecture.md" and st in (None, "template"):
                missing.append("design/tech/architecture.md (рекомендуется: /gd:tech)")
        plans = sorted((d / "qa").glob("test-plan-*.md")) if (d / "qa").is_dir() else []
        lines.append(f"  qa/test-plan-*: {', '.join(p.name + ' ' + str(status(p)) for p in plans) or 'нет'}")
        if not plans:
            missing.append("design/qa/test-plan-<slice>.md (рекомендуется: /gd:qa-plan)")

    if a.task == "anim" and manifest.is_file() and "com.unity.animation.rigging" not in deps:
        lines.append("Пакет Animation Rigging: нет (нужен для IK; com.unity.animation.rigging в поставке Unity 6)")
    found, tool_lines = tools_report()
    lines += tool_lines
    if not need_unity:
        ok, missing = True, []
    for t in required:
        if not found.get(t):
            ok = False
            missing.append(f"{t} — {INSTALL.get(t, 'установить')}")
    if a.task in ("model", "anim") and not found.get("blender_mcp"):
        lines.append("  Blender MCP не настроен — доводка формы и риг только headless-скриптом или руками (model-build/references/model-method.md)")

    print("\n".join(lines))
    if missing:
        print("\nНе хватает:")
        for m in missing:
            print(f"  - {m}")
    mode = "live" if ok else "plan"
    if a.task:
        print(f"\nЗадача: {a.task}")
    if ok:
        tail = " (подтверди пробой MCP: чтение консоли)" if need_unity else ""
    else:
        tail = " — план + чеклист, всё помечается «не проверено»"
    print(f"\nРекомендуемый режим: {mode}{tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
