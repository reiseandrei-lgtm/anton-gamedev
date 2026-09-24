#!/usr/bin/env python3
"""Сверка карты событий с проектом FMOD Studio по экспорту GUIDs (Python stdlib).

Использование:
  python3 diff_fmod.py build/fmod/event-map.json <FMOD-проект>/GUIDs.txt

GUIDs.txt — стандартный экспорт FMOD Studio (File → Export GUIDs), строки вида
  {01234567-89ab-cdef-0123-456789abcdef} event:/SFX/Player/Jump
В GUIDs.txt попадают только события, назначенные в банк: событие вне банка = D1 (в игре его не загрузить).
Проверки: D1 событие/снапшот/шина/параметр из карты нет в FMOD (FAIL) · D2 событие есть в FMOD, но нет в карте (WARN —
добавлено вручную, внести в event-map.md или удалить).
Выход с кодом 1, если есть D1.
"""
import json
import re
import sys
from pathlib import Path

LINE = re.compile(r"^\{[0-9a-fA-F\-]{36}\}\s+((?:event|snapshot|bus|vca|bank|parameter):/.*?)\s*$")


def utf8_stdout():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    utf8_stdout()
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    items = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    fmod = set()
    for line in Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.match(line.strip())
        if m:
            fmod.add(m.group(1))
    if not fmod:
        print("FAIL: в GUIDs.txt не найдено ни одной строки `{guid} path` — это точно экспорт GUIDs?")
        return 1
    want = {i["path"] for i in items}
    want |= {i["bus"] for i in items if i.get("bus")}
    want |= {"parameter:/" + p["name"] for i in items for p in i.get("params", [])}
    missing = sorted(want - fmod)
    extra = sorted(p for p in fmod - want if p.startswith(("event:/", "snapshot:/")))
    print(f"Карта: {len(want)} путей (события, снапшоты, шины, параметры) · FMOD: {len(fmod)} · совпало: {len(want & fmod)}")
    for m in missing:
        print(f"FAIL D1 {m}: есть в карте, нет в FMOD (или событие не в банке) — запусти Sync event map")
    for e in extra:
        print(f"WARN D2 {e}: есть в FMOD, нет в карте — внести в design/audio/event-map.md или удалить")
    print(f"Итог: {'FAIL' if missing else ('WARN' if extra else 'PASS')} · D1 {len(missing)} · D2 {len(extra)}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
