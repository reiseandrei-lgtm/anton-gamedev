#!/usr/bin/env python3
"""Проверка design/levels/<level>.md: метрики, достижимость, гейты, встречи, темп (Python stdlib).

Использование:
  python3 check_level.py design/levels/<level>.md --gdd design/gdd [--gdd design/gdd/hop.md …]
                         [--systems design/systems-map.md]

Проверки (формат — references/level-method.md):
  LV1 зазор > gap_max, < gap_min, высота > height_max; knob не найден (FAIL); Value ≠ Current в GDD (WARN)
  LV2 два пика напряжения (3) без отдыха (≤ 1) между ними; напряжение вне 0–3 (FAIL)
  LV3 гейт на критическом пути без ключа; ключ достижим только через свой гейт; goal недостижим (FAIL)
  LV4 встреча ссылается на несуществующий узел, систему или ID (FAIL)
  LV5 длина уровня (конец Pacing) вне target_length (FAIL)
Выход 1, если есть FAIL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gd-router" / "scripts"))
import gdd_ids  # noqa: E402

EMPTY = {"", "—", "-", "–"}
KNOB = re.compile(r"^([a-z0-9][a-z0-9_\-]*)#(K\d+)$")
USE = re.compile(r"^([a-z0-9][a-z0-9_\-]*)(?:#([A-Z]{1,3}\d+))?(?:\s*[×x]\s*\d+)?$")


def num(v):
    v = (v or "").strip().replace(",", ".")
    if v in EMPTY:
        return None
    m = re.match(r"^-?\d+(?:\.\d+)?", v)
    return float(m.group(0)) if m else None


def minutes(v):
    v = (v or "").strip()
    m = re.match(r"^(\d+):(\d{1,2})$", v)
    return int(m.group(1)) + int(m.group(2)) / 60 if m else num(v)


def target_range(t):
    nums = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[.,]\d+)?", t or "")]
    if not nums:
        return None
    if len(nums) == 1:
        return nums[0] * 0.8, nums[0] * 1.2
    return min(nums[:2]), max(nums[:2])


def table(secs, key):
    return [r for r in gdd_ids.table_rows(gdd_ids.find_section(secs, key) or []) if not gdd_ids._is_placeholder(r)]


def load_gdds(paths):
    """{system: {knob: current}}, {system: set(ID)}"""
    files = []
    for p in paths:
        p = Path(p)
        files += sorted(p.glob("*.md")) if p.is_dir() else [p]
    knobs, ids = {}, {}
    for f in files:
        if f.name.startswith("_"):
            continue
        system, found, _ = gdd_ids.gdd_ids(f)
        ids[system] = set(found)
        knobs[system] = {}
        for r in gdd_ids.table_rows(gdd_ids.find_section(gdd_ids.sections(gdd_ids.read(f)), "tuning knobs") or []):
            kid = r.get("id", "").strip("`* ")
            if re.fullmatch(r"K\d+", kid):
                knobs[system][kid] = num(r.get("current", ""))
    return knobs, ids


def reachable(start, links, gates, skip_gate=None):
    """Узлы, достижимые от start; гейт открыт, когда посещён узел его ключа."""
    seen, changed = {start}, True
    while changed:
        changed = False
        for lid, (a, b, both) in links.items():
            g = gates.get(lid)
            if g and (lid == skip_gate or g["at"] not in seen):
                continue
            for x, y in ((a, b), (b, a)) if both else ((a, b),):
                if x in seen and y not in seen:
                    seen.add(y)
                    changed = True
    return seen


def main():
    gdd_ids.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("level")
    ap.add_argument("--gdd", action="append", default=[], required=True)
    ap.add_argument("--systems", default=None)
    a = ap.parse_args()

    text = gdd_ids.read(a.level)
    fm = gdd_ids.frontmatter(text)
    secs = gdd_ids.sections(text)
    fails, warns = [], []
    knobs, gdd_idsets = load_gdds(a.gdd)
    systems = set(knobs)
    if a.systems:
        for t in gdd_ids.all_tables(gdd_ids.read(a.systems).splitlines()):
            for r in t:
                s = (r.get("system") or r.get("система") or "").strip("`* ").lower()
                if s:
                    systems.add(s)

    # Metrics
    limits = []   # (kind, move, value, metric id)
    metrics = table(secs, "metrics")
    for r in metrics:
        mid, kind = r.get("id", "?").strip(), r.get("kind", "").strip().lower()
        move = (r.get("move", "") or "*").strip().lower() or "*"
        knob, val = r.get("knob", "").strip("` "), num(r.get("value", ""))
        cur = None
        if knob not in EMPTY:
            m = KNOB.match(knob)
            if not m or m.group(1) not in knobs or m.group(2) not in knobs[m.group(1)]:
                fails.append(f"LV1 {mid}: knob «{knob}» не найден в GDD (--gdd)")
            else:
                cur = knobs[m.group(1)][m.group(2)]
                if val is not None and cur is not None and abs(val - cur) > 1e-9:
                    warns.append(f"LV1 {mid}: Value {val:g} ≠ Current {cur:g} в {knob} — уровень считается по GDD")
        elif val is not None:
            warns.append(f"LV1 {mid}: число без knob — метрика должна ссылаться на систему")
        v = cur if cur is not None else val
        if v is None:
            fails.append(f"LV1 {mid}: нет ни knob, ни Value")
        elif kind in ("gap_max", "gap_min", "height_max"):
            limits.append((kind, move, v, mid))

    # Layout
    layout = table(secs, "layout")
    links, crit, nodes = {}, set(), set()
    for r in layout:
        lid = r.get("id", "?").strip()
        f, t = r.get("from", "").strip(), r.get("to", "").strip()
        if not f or not t:
            fails.append(f"LV3 {lid}: связь без From / To")
            continue
        nodes |= {f, t}
        links[lid] = (f, t, "↔" in r.get("dir", "") or "<->" in r.get("dir", ""))
        if "crit" in r.get("path", "").lower():
            crit.add(lid)
        move = (r.get("move", "") or "*").strip().lower() or "*"
        gap, h = num(r.get("gap")), num(r.get("height"))
        for kind, mmove, v, mid in limits:
            if mmove not in ("*", move) and move != "*":
                continue
            if kind == "gap_max" and gap is not None and gap > v:
                fails.append(f"LV1 {lid} {f}→{t}: зазор {gap:g} > {mid} ({v:g})")
            if kind == "gap_min" and gap is not None and 0 < gap < v:
                fails.append(f"LV1 {lid} {f}→{t}: зазор {gap:g} < {mid} ({v:g})")
            if kind == "height_max" and h is not None and h > v:
                fails.append(f"LV1 {lid} {f}→{t}: высота {h:g} > {mid} ({v:g})")
    if not layout:
        fails.append("LV3: нет таблицы `## Layout`")

    # Gates и достижимость
    gates = {}
    for r in table(secs, "gates"):
        gid, link = r.get("id", "?").strip(), r.get("link", "").strip()
        key, at = r.get("key", "").strip(), r.get("key at", "").strip()
        if link not in links:
            fails.append(f"LV3 {gid}: связь «{link}» нет в Layout")
            continue
        if key in EMPTY or at in EMPTY:
            if link in crit:
                fails.append(f"LV3 {gid}: гейт на критическом пути ({link}) без ключа или места ключа")
            continue
        if at not in nodes:
            fails.append(f"LV3 {gid}: узел ключа «{at}» нет в Layout")
            continue
        gates[link] = {"id": gid, "at": at}
    if layout:
        start = fm.get("start") or layout[0].get("from", "").strip()
        goal = fm.get("goal") or layout[-1].get("to", "").strip()
        for link, g in gates.items():
            if g["at"] not in reachable(start, links, gates, skip_gate=link):
                fails.append(f"LV3 {g['id']}: ключ в {g['at']} достижим только через свой гейт ({link}) — soft lock")
        crit_links = {k: v for k, v in links.items() if k in crit}
        if goal not in reachable(start, crit_links or links, gates):
            fails.append(f"LV3: goal {goal} недостижим от {start} по критическому пути")

    # Encounters
    encounters = table(secs, "encounters")
    for r in encounters:
        eid, where = r.get("id", "?").strip(), r.get("where", "").strip()
        if where not in nodes and where not in links:
            fails.append(f"LV4 {eid}: место «{where}» нет в Layout")
        uses = r.get("uses", "").strip("` ")
        if uses in EMPTY:
            fails.append(f"LV4 {eid}: не указано, какие системы или враги (Uses)")
            continue
        for u in [x.strip("` ") for x in uses.split(",") if x.strip()]:
            m = USE.match(u)
            if not m:
                fails.append(f"LV4 {eid}: «{u}» — нужен <system> или <system>#<ID>")
            elif m.group(1) not in systems:
                fails.append(f"LV4 {eid}: система «{m.group(1)}» не найдена (GDD / systems-map)")
            elif m.group(2) and m.group(2) not in gdd_idsets.get(m.group(1), set()):
                fails.append(f"LV4 {eid}: ID {m.group(1)}#{m.group(2)} нет в GDD")
        tn = num(r.get("tension", ""))
        if tn is not None and not 0 <= tn <= 3:
            fails.append(f"LV2 {eid}: напряжение {tn:g} вне 0–3")

    # Pacing
    pacing = table(secs, "pacing")
    last_peak, rested, end = None, True, None
    for r in pacing:
        mnt, tn = minutes(r.get("minute", "")), num(r.get("tension", ""))
        label = r.get("minute", "?").strip()
        if mnt is not None:
            end = mnt if end is None else max(end, mnt)
        if tn is None or not 0 <= tn <= 3:
            fails.append(f"LV2 {label}: напряжение «{r.get('tension', '')}» вне 0–3")
            continue
        if tn >= 3:
            if last_peak is not None and not rested:
                fails.append(f"LV2 пики {last_peak} и {label} без отдыха (≤ 1) между ними")
            last_peak, rested = label, False
        elif tn <= 1:
            rested = True
    if not pacing:
        fails.append("LV2: нет таблицы `## Pacing`")

    rng = target_range(fm.get("target_length", ""))
    if rng is None:
        warns.append("LV5: нет target_length во frontmatter")
    elif end is not None and not rng[0] - 1e-9 <= end <= rng[1] + 1e-9:
        fails.append(f"LV5: длина {round(end, 2):g} мин вне цели {rng[0]:g}–{rng[1]:g}")

    print(f"Уровень: {fm.get('level') or Path(a.level).stem} · метрик: {len(metrics)} · узлов: {len(nodes)} · "
          f"связей: {len(links)} (критических {len(crit)}) · встреч: {len(encounters)} · гейтов: {len(gates)} · "
          f"длина: {'—' if end is None else f'{round(end, 2):g} мин'}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
