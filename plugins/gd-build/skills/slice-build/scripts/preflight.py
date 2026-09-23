#!/usr/bin/env python3
"""Preflight перед сборкой слайса: Unity-проект, редактор, пакеты, design/ (Python stdlib).

Использование:
  python3 preflight.py [<unity-project>] [--design design] [--slice <slice>]

Ничего не меняет. Печатает найденное и рекомендуемый режим:
  live — есть проект, редактор установлен, пакет MCP в manifest (связь всё равно проверить пробой MCP);
  plan — чего-то нет: план + чеклист, всё помечается «не проверено в редакторе».
Код выхода всегда 0 (это отчёт, а не проверка); 2 — неверные аргументы.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

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
    a = ap.parse_args()

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
    deps = {}
    if manifest.is_file():
        try:
            deps = json.loads(manifest.read_text(encoding="utf-8")).get("dependencies", {})
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
        if not handoffs:
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

    print("\n".join(lines))
    if missing:
        print("\nНе хватает:")
        for m in missing:
            print(f"  - {m}")
    mode = "live" if ok else "plan"
    print(f"\nРекомендуемый режим: {mode}" + (" (подтверди пробой MCP: чтение консоли)" if ok else
                                           " — план + чеклист, всё помечается «не проверено в редакторе»"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
