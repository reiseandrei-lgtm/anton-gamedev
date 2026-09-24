#!/usr/bin/env python3
"""Вызовы аналитики в C# против design/analytics/events.md (Python stdlib).

Использование:
  python3 check_analytics_calls.py <Assets или папка> [<ещё папка> …] --events design/analytics/events.md
                                   [--constants <путь к AnalyticsEvents.cs>]

Проверки (references/analytics-method.md):
  AN1 событие без вызова AnalyticsEvents.<Event>(…) / Names.<Event>; AnalyticsEvents.cs расходится с events.md (FAIL)
  AN2 строковое имя события или AnalyticsLog.Send("…") вне AnalyticsEvents.cs (FAIL)
  AN3 параметр events.md или ключ ("key", value) в вызове похож на персональные данные (FAIL)
  AN4 вызовы есть, присваивания Consent нет; бэкенд не проверяет Consent (WARN)
Тесты (using NUnit.Framework), Library/, Packages/, Plugins/, Temp/ пропускаются. Выход 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slice-build" / "scripts"))
import gdd_ids  # noqa: E402

# Копия правила M5 из gd/skills/metrics-plan/scripts/check_events.py (сверяется tools/check_plugins.py P9).
PII = re.compile(r"(^|_)(email|e_mail|name|first_name|last_name|phone|address|ip|device_id|idfa|gaid|imei|user_text)($|_)")
EMPTY = {"", "—", "-", "–"}
SKIP = ("/Library/", "/Packages/", "/Plugins/", "/Temp/")
CONST = re.compile(r'public\s+const\s+string\s+(\w+)\s*=\s*"([^"]*)"')
SEND_LIT = re.compile(r'AnalyticsLog\s*\.\s*Send\s*\(\s*"([^"]*)"')
TUPLE_KEY = re.compile(r'\(\s*"([a-z][a-z0-9_]*)"\s*,')
CONSENT_SET = re.compile(r"\bConsent\s*=(?!=)")
CONSENT_GUARD = re.compile(r"if\s*\(\s*!\s*Consent\s*\)")


def pascal(name):
    return "".join(p[:1].upper() + p[1:] for p in name.split("_") if p)


def strip_comments(code):
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    return re.sub(r"//[^\n]*", "", code)


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="+")
    ap.add_argument("--events", required=True)
    ap.add_argument("--constants", default=None)
    a = ap.parse_args()

    fails, warns = [], []
    rows = gdd_ids.table_rows(gdd_ids.find_section(gdd_ids.sections(gdd_ids.read(a.events)), "events") or [])
    events = {}
    for r in rows:
        ev = r.get("event", "").strip("` ")
        if not ev or "<" in ev:
            continue
        params = []
        raw = r.get("params", "").strip()
        if raw not in EMPTY:
            params = [p.split(":")[0].strip() for p in re.split(r",\s*(?![^\[]*\])", raw)]
        events[ev] = params
        for p in params:
            if PII.search(p):
                fails.append(f"AN3 {ev}: параметр «{p}» похож на персональные данные (events.md → gd:metrics-plan)")

    files = []
    for root in map(Path, a.roots):
        for p in sorted(root.rglob("*.cs")):
            if not any(s in "/" + p.relative_to(root).as_posix() for s in SKIP):
                files.append(p)
    gen = Path(a.constants) if a.constants else next((p for p in files if p.name == "AnalyticsEvents.cs"), None)
    backend = next((p for p in files if p.name == "AnalyticsLog.cs"), None)

    if gen is None or not gen.is_file():
        fails.append("AN1: AnalyticsEvents.cs не найден — gen_analytics.py events.md --out <папка>")
        consts = {}
    else:
        consts = {v: k for k, v in CONST.findall(gen.read_text(encoding="utf-8"))}
        for ev in sorted(set(events) - set(consts)):
            fails.append(f"AN1 {ev}: нет в {gen.name} — перегенерировать")
        for ev in sorted(set(consts) - set(events)):
            fails.append(f"AN1 {ev}: есть в {gen.name}, нет в events.md — перегенерировать")
        gen_code = gen.read_text(encoding="utf-8")
        for ev, params in events.items():
            m = re.search(rf"void\s+{pascal(ev)}\s*\(([^)]*)\)", gen_code)
            if m and ev in consts:
                have = [x.strip().split()[-1].lstrip("@") for x in m.group(1).split(",") if x.strip()]
                want = [pascal(p)[:1].lower() + pascal(p)[1:] for p in params]
                if have != want:
                    fails.append(f"AN1 {ev}: параметры {have} ≠ events.md {want} — перегенерировать")

    used, consent_set, n_calls, n_code = set(), False, 0, 0
    for p in files:
        if gen is not None and p.resolve() == gen.resolve():
            continue
        code = strip_comments(p.read_text(encoding="utf-8", errors="replace"))
        if "using NUnit.Framework" in code:
            continue
        is_backend = backend is not None and p.resolve() == backend.resolve()
        n_code += 1
        if not is_backend and CONSENT_SET.search(code):
            consent_set = True
        for ev in events:
            name = pascal(ev)
            hits = re.findall(rf"\bAnalyticsEvents\s*\.\s*(?:{name}\s*\(|Names\s*\.\s*{name}\b)", code)
            if hits:
                used.add(ev)
                n_calls += len(hits)
            if re.search(rf'"{re.escape(ev)}"', code):
                fails.append(f"AN2 {p.name}: строка \"{ev}\" — имя события только через AnalyticsEvents.Names.{name}")
        if not is_backend:
            for lit in SEND_LIT.findall(code):
                fails.append(f"AN2 {p.name}: AnalyticsLog.Send(\"{lit}\") — вызывай AnalyticsEvents.<Event>(…)")
            if "AnalyticsLog" in code:
                for key in TUPLE_KEY.findall(code):
                    if PII.search(key):
                        fails.append(f"AN3 {p.name}: ключ «{key}» похож на персональные данные")

    for ev in sorted(set(events) - used):
        fails.append(f"AN1 {ev}: нет вызова AnalyticsEvents.{pascal(ev)}(…) — точка из колонки Trigger")
    if n_calls and not consent_set:
        warns.append("AN4: вызовы есть, а AnalyticsLog.Consent нигде не выставляется — события не пишутся или пишутся без согласия")
    if backend is not None and not CONSENT_GUARD.search(backend.read_text(encoding="utf-8", errors="replace")):
        warns.append(f"AN4 {backend.name}: Send не проверяет Consent")

    print(f"Событий: {len(events)} · с вызовом: {len(used)} · вызовов: {n_calls} · файлов C#: {n_code} · "
          f"константы: {gen.name if gen else '—'} · бэкенд: {backend.name if backend else '—'} · согласие выставляется: {'да' if consent_set else 'нет'}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    if not events:
        print("FAIL: в events.md нет таблицы ## Events")
        return 1
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
