#!/usr/bin/env python3
"""Общий парсер design/-документов для скриптов плагина gd (Python stdlib).

Импорт из скрипта другого скилла:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gd-router" / "scripts"))
    import gdd_ids

Стабильные ID в GDD (см. gdd-author/references/gdd-template.md); хендофф — ED/DD (handoff_ids);
бюджеты — B1… в tech/budgets.md (budget_ids).
Стабильные ID в GDD:
  Core Rules  R1…  ·  Formulas F1…  ·  Edge Cases E1…  ·  Tuning Knobs K1…  ·  Feedback FB1…
Ссылка на ID из других документов: `<system>#<ID>`, где system — имя файла GDD без .md.
Старые GDD без ID: элементы нумеруются по порядку, в warnings — предупреждение.

Самопроверка: python3 gdd_ids.py design/gdd/<system>.md
"""
import re
import sys
from pathlib import Path

SECTION_PREFIX = {
    "core rules": "R",
    "formulas": "F",
    "edge cases": "E",
    "tuning knobs": "K",
    "feedback": "FB",
}
ID_AT_START = re.compile(r"^\s*(?:[-*+]\s*|\d+[.)]\s*)?(?:\*\*)?`?([A-Z]{1,3}\d+)`?(?:\*\*)?\s*(?:[.:)\-—–]|\s)")
HEADING_ID = re.compile(r"^###\s+`?([A-Z]{1,3}\d+)`?\b")
NUMBERED = re.compile(r"^\s*\d+[.)]\s+\S")
REF = re.compile(r"\b([a-z0-9][a-z0-9_\-]*)#([A-Z]{1,3}\d+)\b")


def utf8_stdout():
    """Консоль Windows (cp1251/cp866) падает на «→», «✓» — переключаем вывод на UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def read(path):
    return Path(path).read_text(encoding="utf-8")


def frontmatter(text):
    """Плоский YAML-frontmatter → dict (только `key: value`)."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    out = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            out[k.strip()] = v.split("#")[0].strip().strip('"').strip("'")
    return out


def sections(text, level=2):
    """{заголовок в нижнем регистре: [строки]} для заголовков уровня level."""
    marker = "#" * level + " "
    out, cur = {}, None
    for line in text.splitlines():
        if line.startswith(marker):
            cur = line[len(marker):].strip().lower()
            out[cur] = []
        elif line.startswith("#" * (level - 1) + " ") and level > 1 and not line.startswith(marker):
            cur = None
        elif cur is not None:
            out[cur].append(line)
    return out


def find_section(secs, key):
    for name, lines in secs.items():
        if name.startswith(key):
            return lines
    return None


def table_rows(lines):
    """Строки markdown-таблицы → список dict по заголовку (ключи в нижнем регистре)."""
    rows, header = [], None
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            if header is not None and rows:
                break
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if not any(cells):
            continue
        cells += [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, cells)))
    return rows


def all_tables(lines):
    """Все таблицы в наборе строк, по порядку."""
    tables, chunk = [], []
    for line in lines + [""]:
        if line.strip().startswith("|"):
            chunk.append(line)
        elif chunk:
            tables.append(table_rows(chunk))
            chunk = []
    return tables


def _is_placeholder(row):
    vals = [v for v in row.values() if v]
    return not vals or all(re.fullmatch(r"[.…\s<>/-]*|<[^>]*>", v) for v in vals)


def gdd_ids(path):
    """Возвращает (system, {ID: краткий текст}, warnings)."""
    text = read(path)
    system = Path(path).stem
    secs = sections(text)
    ids, warnings = {}, []
    for key, prefix in SECTION_PREFIX.items():
        lines = find_section(secs, key)
        if lines is None:
            continue
        found, legacy = [], []
        if key == "formulas":
            for line in lines:
                m = HEADING_ID.match(line)
                if m:
                    found.append((m.group(1), line.strip("# ").strip()))
                elif line.startswith("### ") and "<" not in line:
                    legacy.append(line[4:].strip())
        elif key == "core rules":
            for line in lines:
                m = ID_AT_START.match(line)
                if m and m.group(1).startswith(prefix):
                    found.append((m.group(1), line.strip()))
                elif NUMBERED.match(line) and "…" not in line:
                    legacy.append(line.strip())
        else:
            for row in table_rows(lines):
                if _is_placeholder(row):
                    continue
                rid = row.get("id", "").strip("`* ")
                if re.fullmatch(prefix + r"\d+", rid):
                    found.append((rid, " · ".join(v for k, v in row.items() if k != "id" and v)[:80]))
                else:
                    legacy.append(" · ".join(v for v in row.values() if v)[:80])
        for rid, desc in found:
            if rid in ids:
                warnings.append(f"{system}: дубль ID {rid}")
            ids[rid] = desc
        if legacy:
            if found:
                warnings.append(f"{system}: в разделе '{key}' {len(legacy)} элемент(ов) без ID")
            else:
                warnings.append(f"{system}: раздел '{key}' без стабильных ID — нумерую по порядку ({prefix}1…)")
                for i, desc in enumerate(legacy, 1):
                    ids.setdefault(f"{prefix}{i}", desc)
    return system, ids, warnings


HANDOFF_ID = r"(?:ED|DD)(?:-[a-z0-9_]+-)?\d+"   # ED1 (слайс) или ED-<system>-1 (майлстоун)


def handoff_ids(path):
    """ID критериев хендоффа: ED1…, DD1… (слайс) или ED-<system>-N, DD-<system>-N (майлстоун)."""
    ids = {}
    for line in read(path).splitlines():
        m = re.match(r"^\s*[-*]\s*\[[ xX]\]\s*\**`?(" + HANDOFF_ID + r")`?\**\s*[.:—–-]?\s*(.*)", line)
        if m:
            ids[m.group(1)] = m.group(2).strip()
    return ids


def budget_ids(path):
    """Строки tech/budgets.md: {B1: метрика}. Без колонки ID — нумерация по порядку (B1…)."""
    out = {}
    for table in all_tables(read(path).splitlines()):
        if not table or not any(k in table[0] for k in ("метрика", "metric")):
            continue
        for i, row in enumerate(table, 1):
            if _is_placeholder(row):
                continue
            bid = row.get("id", "").strip("`* ") or f"B{i}"
            out[bid] = row.get("метрика") or row.get("metric") or ""
    return out


def refs(text):
    """Все ссылки `<system>#<ID>` в тексте."""
    return REF.findall(text)


if __name__ == "__main__":
    utf8_stdout()
    for p in sys.argv[1:]:
        system, ids, warns = gdd_ids(p)
        print(f"{system}: {len(ids)} ID")
        for k, v in ids.items():
            print(f"  {k}: {v}")
        for w in warns:
            print(f"  WARN {w}")
