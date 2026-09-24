#!/usr/bin/env python3
"""Сверка UI Toolkit (UXML/USS) с design/ux/hud.md и палитрой арт-библии (Python stdlib).

Использование:
  python3 check_ui.py design/ux/hud.md <папка UI в Assets> --palette design/art/art-bible.md
                      [--code <папка C#>] [--shots design/build/ui/screenshots --res 1080x1920,1440x2560] [--min-touch 48]

Проверки:
  UI1 элемент hud.md (колонка Name) не найден ни в одном UXML (FAIL)
  UI2 цвет в USS не через переменную роли: hex/rgb() вне файла темы (*theme*.uss) (FAIL);
      в теме переменная --role-<role> с цветом ≠ арт-библии или роли нет в библии (FAIL)
  UI3 литеральный текст в UXML (text="…" не ключ вида a.b) или в C# (.text = "…" с буквами) (FAIL)
  UI4 нет скриншота для разрешения из --res (WARN)
  UI5 кнопка / тач-цель из hud.md меньше --min-touch px по USS width/height (WARN)
Выход 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slice-build" / "scripts"))
import gdd_ids  # noqa: E402

EMPTY = {"", "—", "-", "–"}
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
KEY = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)+$")


def palette(path):
    roles = {}
    for table in gdd_ids.all_tables(gdd_ids.read(path).splitlines()):
        for r in table:
            role, hexv = r.get("role", "").strip("` "), r.get("hex", "").strip("` ")
            if role and HEX.fullmatch(hexv):
                roles[role.lower()] = hexv.upper()
    return roles


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("hud")
    ap.add_argument("ui_dir")
    ap.add_argument("--palette", required=True)
    ap.add_argument("--code", default=None)
    ap.add_argument("--shots", default=None)
    ap.add_argument("--res", default="")
    ap.add_argument("--min-touch", type=float, default=48)
    a = ap.parse_args()

    fails, warns = [], []
    ui = Path(a.ui_dir)
    uxml = list(ui.rglob("*.uxml"))
    uss = list(ui.rglob("*.uss"))
    roles = palette(a.palette)

    hud = []
    for table in gdd_ids.all_tables(gdd_ids.read(a.hud).splitlines()):
        if table and "name" in table[0]:
            hud += table
    names = set()
    for f in uxml:
        names |= set(re.findall(r'\bname="([^"]+)"', f.read_text(encoding="utf-8", errors="replace")))
    for r in hud:
        n = r.get("name", "").strip("` ")
        if n not in EMPTY and n not in names:
            fails.append(f"UI1 {r.get('info', '?')}: элемента name=\"{n}\" нет в UXML")

    for f in uss:
        text = re.sub(r"/\*.*?\*/", "", f.read_text(encoding="utf-8", errors="replace"), flags=re.S)
        if "theme" in f.stem.lower():
            for var, val in re.findall(r"--role-([a-z0-9\-]+)\s*:\s*([^;]+);", text):
                want = roles.get(var)
                got = HEX.search(val)
                if want is None:
                    fails.append(f"UI2 {f.name}: --role-{var} — такой роли нет в арт-библии ({', '.join(sorted(roles))})")
                elif got and got.group(0).upper() != want:
                    fails.append(f"UI2 {f.name}: --role-{var} = {got.group(0)} ≠ {want} в арт-библии")
            continue
        for n, line in enumerate(text.splitlines(), 1):
            values = " ".join(re.findall(r":\s*([^;{}]+)", line))   # цвет — только в значении свойства, не в селекторе #id
            for h in HEX.findall(values) + re.findall(r"rgba?\([^)]*\)", values):
                fails.append(f"UI2 {f.name}:{n}: цвет {h} — только var(--role-…) из темы")
            for var in re.findall(r"var\(--role-([a-z0-9\-]+)\)", line):
                if var not in roles:
                    fails.append(f"UI2 {f.name}:{n}: var(--role-{var}) — роли нет в арт-библии")

    for f in uxml:
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for txt in re.findall(r'\btext="([^"]*)"', line):
                if txt.strip() and not KEY.match(txt.strip()) and re.search(r"[^\W\d_]", txt):
                    fails.append(f"UI3 {f.name}:{n}: литеральный текст «{txt}» — нужен ключ локализации")
    if a.code:
        for f in Path(a.code).rglob("*.cs"):
            code = f.read_text(encoding="utf-8", errors="replace")
            if "using NUnit.Framework" in code:
                continue
            for n, line in enumerate(code.splitlines(), 1):
                for lit in re.findall(r'\.text\s*=\s*\$?"([^"]*)"', line):
                    if re.search(r"[^\W\d_]", re.sub(r"\{[^}]*\}", "", lit)) and not KEY.match(lit):
                        fails.append(f"UI3 {f.name}:{n}: литеральный текст «{lit}» в коде — нужен ключ")

    if a.shots and a.res:
        shots = Path(a.shots)
        for res in [r.strip() for r in a.res.split(",") if r.strip()]:
            if not list(shots.glob(f"{res}/*.png")) and not list(shots.glob(f"*{res}*.png")):
                warns.append(f"UI4 нет скриншота для {res} в {shots}")

    css = "\n".join(re.sub(r"/\*.*?\*/", "", f.read_text(encoding="utf-8", errors="replace"), flags=re.S) for f in uss)
    for r in hud:
        n = r.get("name", "").strip("` ")
        if n in EMPTY or not re.search(r"кнопк|button|тач|tap", r.get("форма", "") + r.get("form", ""), re.I):
            continue
        rule = re.search(rf"#{re.escape(n)}\s*\{{([^}}]*)\}}", css)
        if not rule:
            warns.append(f"UI5 {n}: нет USS-правила #{n} с размером — тач-цель не проверена")
            continue
        for prop in ("width", "height"):
            m = re.search(rf"(?:^|;|\s)(?:min-)?{prop}\s*:\s*([\d.]+)px", rule.group(1))
            if m and float(m.group(1)) < a.min_touch:
                warns.append(f"UI5 {n}: {prop} {m.group(1)}px < {a.min_touch:g}px — тач-цель меньше минимума")

    print(f"HUD: {len(hud)} строк · UXML: {len(uxml)} · USS: {len(uss)} · ролей палитры: {len(roles)}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
