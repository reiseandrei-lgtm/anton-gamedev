#!/usr/bin/env python3
"""design/audio/event-map.md → JSON + скрипт FMOD Studio + C#-константы (Python stdlib).

Использование:
  python3 event_map_to_fmod.py design/audio/event-map.md --out build/fmod [--namespace Game.Audio] [--class FmodEvents]

Пишет в --out:
  event-map.json              — нормализованная карта (для diff_fmod.py и MCP)
  gd_sync_event_map.js        — скрипт для FMOD Studio: положить в папку Scripts проекта FMOD,
                                Scripts → Reload, затем Scripts → gd → Sync event map.
                                Идемпотентен: существующее не пересоздаёт, только добавляет недостающее.
  FmodEvents.cs               — static class с путями событий и снапшотов и именами параметров.
Формат таблицы — gd: audio-direction/references/fmod-conventions.md (колонки Event, Source, Type, Params, Space, Bus, …).
Выход с кодом 1, если в карте есть строки, которые нельзя перенести (путь не по схеме).
"""
import argparse
import json
import re
import sys
from pathlib import Path

SEG = r"[A-Z][A-Za-z0-9]*"
EVENT_RE = re.compile(rf"^event:/{SEG}(?:/{SEG}){{1,3}}$")
SNAP_RE = re.compile(rf"^snapshot:/{SEG}$")
BUS_RE = re.compile(rf"^bus:/{SEG}(?:/{SEG})*$")
RANGE = re.compile(r"^(g_)?([a-z][a-z0-9_]*)\s*\(\s*(-?[\d.]+)\s*\.\.\s*(-?[\d.]+)\s*\)$")
LABELS = re.compile(r"^(g_)?([a-z][a-z0-9_]*)\s*\[([^\]]+)\]$")
EMPTY = {"", "—", "-", "–"}


def utf8_stdout():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def table_rows(text):
    rows, header = [], None
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if "event" in header and "source" in header:
            rows.append(dict(zip(header, cells + [""] * len(header))))
    return rows


def parse_params(s):
    out, errs = [], []
    if s.strip() in EMPTY:
        return out, errs
    for p in re.split(r",\s*(?![^\[]*\])", s):
        p = p.strip()
        m = RANGE.match(p)
        if m:
            out.append({"name": (m.group(1) or "") + m.group(2), "global": bool(m.group(1)),
                        "min": float(m.group(3)), "max": float(m.group(4)), "labels": None})
            continue
        m = LABELS.match(p)
        if m:
            labels = [x.strip() for x in m.group(3).split("/") if x.strip()]
            out.append({"name": (m.group(1) or "") + m.group(2), "global": bool(m.group(1)),
                        "min": 0.0, "max": float(len(labels) - 1), "labels": labels})
            continue
        errs.append(p)
    return out, errs


def load(path):
    items, errors = [], []
    for r in table_rows(Path(path).read_text(encoding="utf-8")):
        ev = r.get("event", "").strip("` ")
        if not ev or "<" in ev:
            continue
        typ = r.get("type", "").strip().lower()
        if not (EVENT_RE.match(ev) or SNAP_RE.match(ev)):
            errors.append(f"{ev}: путь не по схеме — пропущен")
            continue
        params, perr = parse_params(r.get("params", ""))
        errors += [f"{ev}: параметр «{p}» не распознан — пропущен" for p in perr]
        bus = r.get("bus", "").strip("` ")
        items.append({
            "path": ev,
            "kind": "snapshot" if ev.startswith("snapshot:/") else "event",
            "type": typ,
            "source": r.get("source", "").strip("` "),
            "space": r.get("space", "").strip().upper(),
            "bus": bus if BUS_RE.match(bus) else None,
            "priority": r.get("priority", "").strip(),
            "params": params,
            "status": r.get("status", "").strip().lower(),
        })
    return items, errors


JS_TEMPLATE = r"""// Сгенерировано gd-build fmod-sync (event_map_to_fmod.py) из design/audio/event-map.md. Не править руками.
// Установка: положить в папку Scripts проекта FMOD Studio → Scripts → Reload → Scripts → gd → Sync event map.
// Идемпотентно: существующие папки, события, шины, снапшоты и параметры не пересоздаются.
// Проверено по документации FMOD Studio Scripting API (create, lookup, Event.addGameParameter,
// workspace.addGameParameter, mixer.masterBus). Маршрутизация события в шину — через mixerInput.output
// в try/catch: если ваша версия FMOD не поддерживает, скрипт сообщит, и шину нужно назначить вручную.
var GD_MAP = __DATA__;

function gdLog(msg) { console.log("[gd] " + msg); }

function gdChildByName(folder, name) {
    var rel = folder.relationships && folder.relationships.items;
    var kids = (rel && rel.destinations) ? rel.destinations : [];
    for (var i = 0; i < kids.length; i++) { if (kids[i].name === name) return kids[i]; }
    return null;
}

function gdEnsureFolder(segments, stats) {
    var cur = studio.project.workspace.masterEventFolder;
    for (var i = 0; i < segments.length; i++) {
        var child = gdChildByName(cur, segments[i]);
        if (!child) {
            child = studio.project.create("EventFolder");
            child.name = segments[i];
            child.folder = cur;
            stats.folders++;
        }
        cur = child;
    }
    return cur;
}

var GD_BUSES = {};

function gdEnsureBus(path, stats) {
    if (GD_BUSES[path]) return GD_BUSES[path];
    var bus = studio.project.lookup(path);
    if (bus) { GD_BUSES[path] = bus; return bus; }
    var parent = studio.project.workspace.mixer.masterBus;
    var segs = path.replace("bus:/", "").split("/");
    for (var i = 0; i < segs.length; i++) {
        var sub = studio.project.lookup("bus:/" + segs.slice(0, i + 1).join("/"));
        if (!sub) {
            sub = studio.project.create("MixerGroup");
            sub.name = segs[i];
            sub.output = parent;
            stats.buses++;
        }
        parent = sub;
    }
    GD_BUSES[path] = parent;
    return parent;
}

function gdParamDef(p) {
    var def = { name: p.name, type: studio.project.parameterType.User, min: p.min, max: p.max };
    if (p.labels) {
        def.type = studio.project.parameterType.UserEnumeration;
        def.enumerationLabels = p.labels;
    }
    return def;
}

function gdHasParam(ev, name) {
    var list = ev.parameters || [];
    for (var i = 0; i < list.length; i++) {
        var pr = list[i].preset || list[i];
        if (pr && pr.name === name) return true;
    }
    return false;
}

function gdSync() {
    var stats = { folders: 0, events: 0, buses: 0, snapshots: 0, params: 0, presets: 0, manual: [] };
    var presets = {};
    for (var i = 0; i < GD_MAP.length; i++) {
        var it = GD_MAP[i];
        if (it.kind === "snapshot") {
            if (!studio.project.lookup(it.path)) {
                var s = studio.project.create("Snapshot");
                s.name = it.path.replace("snapshot:/", "");
                stats.snapshots++;
            }
            continue;
        }
        var ev = studio.project.lookup(it.path);
        if (!ev) {
            var segs = it.path.replace("event:/", "").split("/");
            var name = segs.pop();
            ev = studio.project.create("Event");
            ev.name = name;
            ev.folder = gdEnsureFolder(segs, stats);
            stats.events++;
        }
        if (it.bus) {
            var bus = gdEnsureBus(it.bus, stats);
            try { ev.mixerInput.output = bus; }
            catch (e) { stats.manual.push(it.path + ": назначить шину " + it.bus + " вручную"); }
        }
        for (var j = 0; j < it.params.length; j++) {
            var p = it.params[j];
            if (p.global) {
                if (!presets[p.name]) {
                    try { studio.project.workspace.addGameParameter(gdParamDef(p)); stats.presets++; }
                    catch (e) { stats.manual.push("глобальный параметр " + p.name + ": создать вручную (" + e + ")"); }
                    presets[p.name] = true;
                }
                stats.manual.push(it.path + ": подключить глобальный параметр " + p.name + " к событию вручную");
            } else if (!gdHasParam(ev, p.name)) {
                try { ev.addGameParameter(gdParamDef(p)); stats.params++; }
                catch (e) { stats.manual.push(it.path + ": параметр " + p.name + " не создан (" + e + ")"); }
            }
        }
    }
    gdLog("папок +" + stats.folders + ", событий +" + stats.events + ", шин +" + stats.buses +
          ", снапшотов +" + stats.snapshots + ", параметров +" + stats.params + ", глобальных +" + stats.presets);
    for (var k = 0; k < stats.manual.length; k++) { gdLog("ВРУЧНУЮ: " + stats.manual[k]); }
    gdLog("Готово. Сохраните проект и экспортируйте GUIDs (File → Export GUIDs) для diff_fmod.py.");
}

studio.menu.addMenuItem({ name: "gd\\Sync event map", execute: gdSync });
"""


def cs_ident(s):
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return ("_" + s) if s[:1].isdigit() else s


def make_cs(items, ns, cls):
    ev_lines, snap_lines, params = [], [], {}
    for it in items:
        name = cs_ident(it["path"].split(":/", 1)[1].replace("/", "_"))
        line = f'        public const string {name} = "{it["path"]}";'
        (snap_lines if it["kind"] == "snapshot" else ev_lines).append(line)
        for p in it["params"]:
            params[p["name"]] = p
    p_lines = []
    for n, p in sorted(params.items()):
        p_lines.append(f'            public const string {cs_ident(n.title().replace("_", ""))} = "{n}";')
        if p["labels"]:
            for i, lab in enumerate(p["labels"]):
                p_lines.append(f'            public const float {cs_ident(n.title().replace("_", ""))}_{cs_ident(lab.title())} = {i};')
    return (
        "// <auto-generated> gd-build fmod-sync из design/audio/event-map.md. Не править руками. </auto-generated>\n"
        "// Использование: FMODUnity.RuntimeManager.PlayOneShot(FmodEvents.SFX_Player_Jump, transform.position);\n"
        f"namespace {ns}\n{{\n    public static class {cls}\n    {{\n"
        + "\n".join(ev_lines)
        + "\n\n        public static class Snapshots\n        {\n"
        + "\n".join(s.replace("        public", "            public") for s in snap_lines)
        + "\n        }\n\n        public static class Params\n        {\n"
        + "\n".join(p_lines)
        + "\n        }\n    }\n}\n"
    )


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("event_map")
    ap.add_argument("--out", required=True)
    ap.add_argument("--namespace", default="Game.Audio")
    ap.add_argument("--class", dest="cls", default="FmodEvents")
    a = ap.parse_args()

    items, errors = load(a.event_map)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "event-map.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    (out / "gd_sync_event_map.js").write_text(
        JS_TEMPLATE.replace("__DATA__", json.dumps(items, ensure_ascii=False)), encoding="utf-8", newline="\n")
    (out / f"{a.cls}.cs").write_text(make_cs(items, a.namespace, a.cls), encoding="utf-8", newline="\n")
    ev = sum(1 for i in items if i["kind"] == "event")
    print(f"Событий: {ev} · снапшотов: {len(items) - ev} · параметров: {sum(len(i['params']) for i in items)}")
    print(f"Записано: {out / 'event-map.json'}, {out / 'gd_sync_event_map.js'}, {out / (a.cls + '.cs')}")
    for e in errors:
        print(f"FAIL {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
