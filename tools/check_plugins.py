#!/usr/bin/env python3
"""Проверки репозитория маркетплейса перед выпуском (Python stdlib). Дополняет `claude plugin validate .`.

Использование (из корня репозитория):
  python3 tools/check_plugins.py

Проверки:
  P1 SKILL.md: frontmatter, name = имя папки, есть description с «Триггеры RU», «Triggers EN» и «Не для»
  P2 SKILL.md длиннее 60 строк (WARN)
  P3 ссылки `references/…`, `scripts/…`, `../<skill>/…`, `<skill>/references|scripts/…` существуют
  P4 команды: disable-model-invocation: true
  P5 агенты: name = имя файла, description, skills из этого же плагина существуют
  P6 пересечение триггеров между скиллами (одинаковая фраза — FAIL, вложенная — WARN)
  P7 Python-скрипты компилируются
  P8 version только в plugin.json, не в marketplace.json
Выход с кодом 1, если есть FAIL.
"""
import json
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"`((?:\.\./[a-z0-9\-]+/|[a-z0-9\-]+/)?(?:references|scripts)/[A-Za-z0-9_.\-/]+)`")
QUOTED = re.compile(r"«([^»]+)»|\"([^\"]+)\"")


def utf8_stdout():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def frontmatter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return None
    fm, key = {}, None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_\-]+):\s*(.*)$", line)
        if km:
            key = km.group(1)
            fm[key] = km.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm


def triggers(desc):
    out = set()
    for part in re.split(r"(?=Триггеры RU:|Triggers EN:|Не для|Не использовать)", desc):
        if part.startswith(("Триггеры RU:", "Triggers EN:")):
            for a, b in QUOTED.findall(part):
                phrase = (a or b).strip().lower()
                if phrase:
                    out.add(phrase)
    return out


def resolve(link, skill_dir, skills_root):
    if link.startswith("../"):
        return (skill_dir / link).resolve()
    first = link.split("/")[0]
    if first in ("references", "scripts"):
        return skill_dir / link
    return skills_root / link


def main():
    utf8_stdout()
    fails, warns = [], []
    all_triggers = {}
    for plugin in sorted((ROOT / "plugins").iterdir()):
        if not (plugin / ".claude-plugin/plugin.json").is_file():
            continue
        skills_root = plugin / "skills"
        skill_names = {d.name for d in skills_root.iterdir() if d.is_dir()} if skills_root.is_dir() else set()
        for sd in sorted(skills_root.iterdir()) if skills_root.is_dir() else []:
            if not sd.is_dir():
                continue
            sk = sd / "SKILL.md"
            rel = sk.relative_to(ROOT)
            if not sk.is_file():
                fails.append(f"P1 {rel}: нет SKILL.md")
                continue
            text = sk.read_text(encoding="utf-8")
            fm = frontmatter(text)
            if fm is None:
                fails.append(f"P1 {rel}: нет frontmatter")
                continue
            if fm.get("name") != sd.name:
                fails.append(f"P1 {rel}: name «{fm.get('name')}» ≠ папке «{sd.name}»")
            desc = fm.get("description", "")
            if not desc:
                fails.append(f"P1 {rel}: нет description")
            project_skill = "syncario" in sd.name
            for marker in ("Триггеры RU", "Triggers EN", "Не "):
                if marker not in desc and not project_skill:
                    fails.append(f"P1 {rel}: в description нет «{marker}»")
            n = len(text.splitlines())
            if n > 60 and not project_skill:
                warns.append(f"P2 {rel}: {n} строк > 60")
            trig = triggers(desc)
            all_triggers[f"{plugin.name}:{sd.name}"] = trig
            for f in [sk] + sorted(sd.glob("references/*.md")):
                for link in LINK.findall(f.read_text(encoding="utf-8")):
                    link = link.rstrip(".")
                    first = link.split("/")[0]
                    if first not in ("references", "scripts", "..") and first not in skill_names:
                        continue
                    target = resolve(link, sd, skills_root)
                    if not target.exists():
                        fails.append(f"P3 {f.relative_to(ROOT)}: ссылка `{link}` не существует")
            for py in sd.glob("scripts/*.py"):
                try:
                    py_compile.compile(str(py), doraise=True)
                except py_compile.PyCompileError as e:
                    fails.append(f"P7 {py.relative_to(ROOT)}: {e.msg.strip()[:120]}")
        for cmd in sorted((plugin / "commands").glob("*.md")):
            text = cmd.read_text(encoding="utf-8")
            fm = frontmatter(text) or {}
            if fm.get("disable-model-invocation") != "true":
                fails.append(f"P4 {cmd.relative_to(ROOT)}: нет disable-model-invocation: true")
            for link in LINK.findall(text):
                first = link.split("/")[0]
                if first in skill_names and not (skills_root / link).exists():
                    fails.append(f"P3 {cmd.relative_to(ROOT)}: ссылка `{link}` не существует")
        for ag in sorted((plugin / "agents").glob("*.md")):
            text = ag.read_text(encoding="utf-8")
            fm = frontmatter(text) or {}
            if fm.get("name") != ag.stem:
                fails.append(f"P5 {ag.relative_to(ROOT)}: name «{fm.get('name')}» ≠ имени файла")
            if not fm.get("description"):
                fails.append(f"P5 {ag.relative_to(ROOT)}: нет description")
            m = re.search(r"^skills:\s*\n((?:\s+-\s*\S+\s*\n)+)", text, re.M)
            for s in re.findall(r"-\s*(\S+)", m.group(1)) if m else []:
                if s not in skill_names:
                    fails.append(f"P5 {ag.relative_to(ROOT)}: скилл «{s}» не найден в плагине {plugin.name}")

    keys = sorted(all_triggers)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            same = all_triggers[a] & all_triggers[b]
            for t in sorted(same):
                fails.append(f"P6 триггер «{t}» у {a} и {b}")
            for ta in all_triggers[a]:
                for tb in all_triggers[b]:
                    if ta != tb and len(min(ta, tb, key=len)) >= 6 and (
                            re.search(rf"(?<!\w){re.escape(ta)}(?!\w)", tb) or re.search(rf"(?<!\w){re.escape(tb)}(?!\w)", ta)):
                        warns.append(f"P6 вложенные триггеры: {a} «{ta}» ~ {b} «{tb}»")

    mk = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    for p in mk.get("plugins", []):
        if "version" in p:
            fails.append(f"P8 marketplace.json: у {p['name']} есть version — держать только в plugin.json")

    n_tr = sum(len(v) for v in all_triggers.values())
    print(f"Скиллов: {len(all_triggers)} · триггеров: {n_tr}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
