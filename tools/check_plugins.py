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
  P9 копии общего кода между плагинами совпадают с оригиналом побайтно (COPIES)
  P10 имена платных инструментов (generate_*, create_rodin_job, Suno, ElevenLabs, Meshy, MusicGen…) — только в строке-запрете
  P11 tools/trigger_cases.md: типовой запрос уходит в ожидаемый скилл (самый длинный совпавший триггер)
Выход с кодом 1, если есть FAIL.
"""
import json
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"`((?:\.\./[a-z0-9\-]+/|[a-z0-9\-]+/)?(?:references|scripts)/[A-Za-z0-9_.\-/]+)`")
COPIES = [
    ("plugins/gd/skills/gd-router/scripts/gdd_ids.py", "plugins/gd-build/skills/slice-build/scripts/gdd_ids.py"),
]
PAID = re.compile(r"generate_(?:image|audio|model)|create_rodin_job|create_hunyuan_job|download_sketchfab_model|"
                  r"\bsuno\b|elevenlabs|\bmeshy\b|musicgen|hyper3d", re.I)
NEGATION = re.compile(r"запрещ|не вызыва|не использ|не предлаг|не включа|не подключа|не для|нельзя|исключен|"
                      r"never|do not|don't|not use|forbidden|платн", re.I)
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

    for orig, copy in COPIES:
        o, c = ROOT / orig, ROOT / copy
        if not c.is_file() or o.read_bytes() != c.read_bytes():
            fails.append(f"P9 {copy}: не совпадает с {orig} — скопируй оригинал")

    for plugin in sorted((ROOT / "plugins").iterdir()):
        for f in sorted(plugin.rglob("*.md")):
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if PAID.search(line) and not NEGATION.search(line):
                    fails.append(f"P10 {f.relative_to(ROOT)}:{n}: платный инструмент без запрета в строке")

    cases = ROOT / "tools/trigger_cases.md"
    if cases.is_file():
        flat = {k: v for k, v in all_triggers.items()}
        for line in cases.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2 or not line.startswith("|") or cells[0].lower() in ("запрос", "request") or set(cells[0]) <= set("-: "):
                continue
            req, want = cells[0].strip("«»\"").lower(), cells[1].strip("` ")
            best = {}
            for skill, trig in flat.items():
                hits = [tr for tr in trig if re.search(rf"(?<!\w){re.escape(tr)}(?!\w)", req)]
                if hits:
                    best[skill.split(":")[1]] = max(len(h) for h in hits)
            if not best:
                fails.append(f"P11 «{req}»: ни один триггер не совпал (ожидался {want})")
                continue
            top = max(best.values())
            winners = sorted(s for s, v in best.items() if v == top)
            if winners != [want]:
                fails.append(f"P11 «{req}»: уходит в {', '.join(winners)}, ожидался {want}")

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
