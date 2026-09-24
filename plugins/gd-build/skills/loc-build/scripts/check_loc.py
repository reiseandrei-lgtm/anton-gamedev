#!/usr/bin/env python3
"""Сверка таблиц локализации design/loc/*.csv с ключами UI, C# и Ink (Python stdlib).

Использование:
  python3 check_loc.py design/loc [--hud design/ux/hud.md] [--unity <Assets или папка>] [--ink <папка .ink>]
                       [--source en] [--pseudo 0.35] [--ph-len 4]

CSV — формат расширения CSV пакета Unity Localization: Key, Shared Comments, <Язык>(<код>)…;
лимит — `max:N` в Shared Comments; `mt` в «<Язык>(<код>) Comments» — машинный перевод.
Проверки (references/loc-method.md):
  LC1 ключ из hud.md / UXML / C# / Ink нет в таблицах; пустой исходник (FAIL); пустой перевод (WARN)
  LC2 ключ таблицы нигде не используется (WARN)
  LC3 длина значения или псевдо-исходника (--pseudo) > max:N (FAIL)
  LC4 плейсхолдеры {…} перевода ≠ исходнику (FAIL)
  LC5 литерал вместо ключа: UXML text="…", C# .text = "…", строка Ink без #id: (FAIL)
Выход 1, если есть FAIL.
"""
import argparse
import csv
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slice-build" / "scripts"))
import gdd_ids  # noqa: E402

EMPTY = {"", "—", "-", "–"}
KEY = re.compile(r"^[a-z0-9_]+(?:\.[a-z0-9_]+)+$")
LOCALE = re.compile(r"\(([A-Za-z]{2,3}(?:[-_][A-Za-z0-9]+)*)\)\s*$")
MAX = re.compile(r"\bmax\s*:\s*(\d+)", re.I)
PH = re.compile(r"\{([^{}:]+)(?::[^{}]*)?\}")
TAG = re.compile(r"<[^<>]+>")
SKIP = ("/Library/", "/Packages/", "/Temp/", "/Plugins/", "/Tests/")
UXML_ATTR = re.compile(r'\b(text|entry)\s*=\s*"([^"]*)"')
CS_TEXT = re.compile(r'\.text\s*=\s*\$?"([^"]*)"')
CS_LIT = re.compile(r'"([a-z0-9_]+(?:\.[a-z0-9_]+)+)"')
INK_ID = re.compile(r"#\s*id\s*:\s*([A-Za-z0-9_.\-]+)")
INK_SKIP = re.compile(r"^\s*(?:===|=|->|<-|~|VAR\b|CONST\b|INCLUDE\b|EXTERNAL\b|LIST\b|TODO\b|\{|\})")


def placeholders(s):
    return sorted(m.group(1).strip() for m in PH.finditer(s or ""))


def visible_len(s, ph_len):
    s = TAG.sub("", s or "")
    return len(PH.sub("x" * ph_len, s))


def strip_cs_comments(code):
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$|(?<=[;{}])\s*//[^\n]*", "", code)


def load_tables(loc_dir, source):
    """{key: {"table", "max", "values": {code: text}, "mt": set(code)}}, [коды], исходный код, файлы"""
    entries, codes, files = {}, [], sorted(Path(loc_dir).glob("*.csv"))
    for f in files:
        with f.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))
        if not rows:
            continue
        head = [h.strip() for h in rows[0]]
        cols = {}
        for i, h in enumerate(head):
            m = LOCALE.search(h)
            if m and "comment" not in h.lower():
                cols[i] = m.group(1)
        comment_of = {}
        for i, h in enumerate(head):
            m = re.search(r"\(([^()]+)\)\s*comments?$", h, re.I)
            if m:
                comment_of[m.group(1)] = i
        for c in cols.values():
            if c not in codes:
                codes.append(c)
        ki = next((i for i, h in enumerate(head) if h.lower() == "key"), 0)
        si = next((i for i, h in enumerate(head) if h.lower() == "shared comments"), None)
        for r in rows[1:]:
            if not r or not (r[ki] if ki < len(r) else "").strip():
                continue
            r += [""] * (len(head) - len(r))
            key = r[ki].strip()
            m = MAX.search(r[si]) if si is not None else None
            e = entries.setdefault(key, {"table": f.stem, "max": None, "values": {}, "mt": set(), "dup": 0})
            e["dup"] += 1
            e["max"] = int(m.group(1)) if m else e["max"]
            for i, c in cols.items():
                e["values"][c] = r[i]
                ci = comment_of.get(c)
                if ci is not None and re.search(r"\bmt\b", r[ci], re.I):
                    e["mt"].add(c)
    src = source if source in codes else (codes[0] if codes else source)
    return entries, codes, src, files


def ink_lines(path):
    """(номер, текст, id или None) для строк Ink с текстом."""
    out, in_block = [], False
    for n, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = raw
        if in_block:
            if "*/" in line:
                line, in_block = line.split("*/", 1)[1], False
            else:
                continue
        if "/*" in line:
            line, in_block = line.split("/*", 1)[0], "*/" not in line.split("/*", 1)[1]
        line = re.sub(r"//.*$", "", line)
        if not line.strip() or INK_SKIP.match(line):
            continue
        tags = line.split("#", 1)[1] if "#" in line else ""
        m = INK_ID.search("#" + tags) if tags else None
        body = line.split("#", 1)[0]
        body = re.sub(r"^\s*(?:[*+]\s*)+|^\s*(?:-\s*)+", "", body)
        body = re.sub(r"^\s*\([A-Za-z0-9_]+\)", "", body)
        body = re.sub(r"->\s*[A-Za-z0-9_.]+|\{[^{}]*\}|<>|\[|\]", "", body)
        if re.search(r"[^\W\d_]", body):
            out.append((n, body.strip(), m.group(1) if m else None))
    return out


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("loc_dir")
    ap.add_argument("--hud", default=None)
    ap.add_argument("--unity", action="append", default=[])
    ap.add_argument("--ink", action="append", default=[])
    ap.add_argument("--source", default="en")
    ap.add_argument("--pseudo", type=float, default=None)
    ap.add_argument("--ph-len", type=int, default=4)
    a = ap.parse_args()

    fails, warns = [], []
    entries, codes, src, files = load_tables(a.loc_dir, a.source)
    used = {}   # key → откуда
    prefixes = {k.split(".")[0] for k in entries}

    if a.hud:
        for t in gdd_ids.all_tables(gdd_ids.read(a.hud).splitlines()):
            for r in t:
                k = r.get("loc key", "").strip("` ")
                if k not in EMPTY:
                    used.setdefault(k, "hud.md")
                    prefixes.add(k.split(".")[0])

    n_uxml = n_cs = 0
    for root in map(Path, a.unity):
        for p in sorted(root.rglob("*.uxml")):
            rel = "/" + p.relative_to(root).as_posix()
            if any(s in rel for s in SKIP):
                continue
            n_uxml += 1
            for attr, val in UXML_ATTR.findall(p.read_text(encoding="utf-8", errors="replace")):
                if KEY.match(val):
                    used.setdefault(val, p.name)
                elif attr == "text" and re.search(r"[^\W\d_]", val):
                    fails.append(f"LC5 {p.name}: text=\"{val}\" — литерал вместо ключа (ui-build)")
        for p in sorted(root.rglob("*.cs")):
            rel = "/" + p.relative_to(root).as_posix()
            if any(s in rel for s in SKIP):
                continue
            n_cs += 1
            code = strip_cs_comments(p.read_text(encoding="utf-8", errors="replace"))
            if "using NUnit.Framework" in code:
                continue
            for val in CS_TEXT.findall(code):
                if not KEY.match(val) and re.search(r"[^\W\d_]", val):
                    fails.append(f"LC5 {p.name}: .text = \"{val}\" — литерал вместо ключа")
            for val in CS_LIT.findall(code):
                if val.split(".")[0] in prefixes:
                    used.setdefault(val, p.name)

    n_ink = 0
    for root in map(Path, a.ink):
        for p in sorted(root.rglob("*.ink")) if root.is_dir() else [root]:
            for n, body, iid in ink_lines(p):
                n_ink += 1
                if iid:
                    used.setdefault(iid, p.name)
                else:
                    fails.append(f"LC5 {p.name}:{n}: строка с текстом без #id: «{body[:40]}» (ink-slice)")

    for k, where in sorted(used.items()):
        if k not in entries:
            fails.append(f"LC1 {k} ({where}): нет в таблицах {Path(a.loc_dir).as_posix()}/*.csv")

    n_mt = n_empty = 0
    for k, e in sorted(entries.items()):
        if e["dup"] > 1:
            fails.append(f"LC1 {k}: ключ повторяется {e['dup']} раз(а) в таблицах")
        if k not in used:
            warns.append(f"LC2 {k} ({e['table']}): нигде не используется")
        source = e["values"].get(src, "")
        if not source.strip():
            fails.append(f"LC1 {k}: пустое значение исходного языка ({src})")
        src_ph = placeholders(source)
        for c in codes:
            v = e["values"].get(c, "")
            if c != src and not v.strip():
                n_empty += 1
                warns.append(f"LC1 {k}: нет перевода ({c})")
                continue
            if c != src and placeholders(v) != src_ph:
                fails.append(f"LC4 {k} ({c}): плейсхолдеры {placeholders(v)} ≠ исходнику {src_ph}")
            if e["max"] is not None and visible_len(v, a.ph_len) > e["max"]:
                fails.append(f"LC3 {k} ({c}): {visible_len(v, a.ph_len)} символов > max:{e['max']} — «{v}»")
        n_mt += len(e["mt"])
        if a.pseudo is not None and e["max"] is not None and source.strip():
            plen = math.ceil(visible_len(source, a.ph_len) * (1 + a.pseudo)) + 2
            if plen > e["max"]:
                fails.append(f"LC3 {k} (pseudo +{a.pseudo:.0%}): {plen} символов > max:{e['max']} — «{source}»")
        elif e["max"] is None and k in used and e["table"].lower() == "ui":
            warns.append(f"LC3 {k}: нет max:N в Shared Comments — переполнение не проверяется")

    print(f"Таблиц: {len(files)} · ключей: {len(entries)} · языков: {len(codes)} ({', '.join(codes) or '—'}; исходный {src}) · "
          f"используется ключей: {len(used)} · UXML: {n_uxml} · C#: {n_cs} · строк Ink: {n_ink} · "
          f"пустых переводов: {n_empty} · mt: {n_mt}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    if not files:
        print(f"FAIL: в {a.loc_dir} нет *.csv")
        return 1
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
