#!/usr/bin/env python3
"""Режим hook: вызовы FMOD в C# идут через константы FmodEvents, а не строками (Python stdlib).

Использование:
  python3 check_fmod_calls.py <Unity-проект или Assets/...> --map design/audio/build/event-map.json
                              [--constants <путь к FmodEvents.cs>]

Проверки:
  FH1 строковый путь "event:/…", "snapshot:/…", "bus:/…", "vca:/…" в C# вне FmodEvents.cs (FAIL)
  FH2 событие карты ни разу не используется через FmodEvents.<Имя> (WARN: звук не подключён к игре)
  FH3 FmodEvents.cs расходится с картой: путь есть в одном и нет в другом (FAIL — перегенерировать)
  FH4 RuntimeManager.CreateInstance без release() в том же файле (WARN, эвристика: утечка экземпляров)
Папки Plugins/FMOD, Library, Packages и файлы тестов (using NUnit.Framework) пропускаются. Выход 1, если есть FAIL.
"""
import argparse
import json
import re
import sys
from pathlib import Path

PATH_LITERAL = re.compile(r'"((?:event|snapshot|bus|vca):/[^"]*)"')
CONST = re.compile(r'public\s+const\s+string\s+(\w+)\s*=\s*"((?:event|snapshot):/[^"]*)"')
SKIP = ("/Plugins/FMOD/", "/Library/", "/Packages/", "/Temp/")


def utf8_stdout():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def strip_comments(code):
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    return re.sub(r"//[^\n]*", "", code)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--map", required=True)
    ap.add_argument("--constants", default=None)
    a = ap.parse_args()

    root = Path(a.root)
    files = [p for p in root.rglob("*.cs") if not any(s in "/" + p.relative_to(root).as_posix() for s in SKIP)]
    const_file = Path(a.constants) if a.constants else next((p for p in files if p.name == "FmodEvents.cs"), None)
    items = json.loads(Path(a.map).read_text(encoding="utf-8"))
    want = {i["path"] for i in items}
    fails, warns = [], []

    consts = {}
    if const_file is None or not const_file.is_file():
        fails.append("FH3 FmodEvents.cs не найден — сгенерируй `event_map_to_fmod.py` и положи в проект")
    else:
        consts = {name: path for name, path in CONST.findall(const_file.read_text(encoding="utf-8"))}
        have = set(consts.values())
        for p in sorted(want - have):
            fails.append(f"FH3 {p}: есть в карте, нет в FmodEvents.cs — перегенерируй константы")
        for p in sorted(have - want):
            fails.append(f"FH3 {p}: есть в FmodEvents.cs, нет в карте — перегенерируй константы")

    used = set()
    for f in files:
        if const_file and f.resolve() == const_file.resolve():
            continue
        code = strip_comments(f.read_text(encoding="utf-8", errors="replace"))
        if "using NUnit.Framework" in code:
            continue  # тесты сверяют строки с константами законно и не подключают звук к игре
        rel = f.relative_to(root).as_posix() if f.is_relative_to(root) else f.as_posix()
        for n, line in enumerate(code.splitlines(), 1):
            for lit in PATH_LITERAL.findall(line):
                fails.append(f"FH1 {rel}:{n}: строковый путь \"{lit}\" — используй FmodEvents")
        for name in re.findall(r"FmodEvents(?:\.Snapshots)?\.(\w+)", code):
            used.add(name)
        if re.search(r"RuntimeManager\.CreateInstance", code) and not re.search(r"\.release\s*\(", code):
            warns.append(f"FH4 {rel}: CreateInstance без release() — экземпляры не освобождаются")

    for name, path in sorted(consts.items(), key=lambda kv: kv[1]):
        if path.startswith("event:/") and name not in used:
            warns.append(f"FH2 {path}: FmodEvents.{name} нигде не вызывается — звук не подключён")

    print(f"C#-файлов: {len(files)} · констант: {len(consts)} · используется: {len(used & set(consts))}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
