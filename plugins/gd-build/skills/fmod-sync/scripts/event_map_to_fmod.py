#!/usr/bin/env python3
"""design/audio/event-map.md → JSON + скрипт FMOD Studio + C#-константы (Python stdlib).

Использование:
  python3 event_map_to_fmod.py design/audio/event-map.md --out build/fmod [--namespace Game.Audio] [--class FmodEvents]
                               [--files design/audio/files.md [--audio-root <папка>]]

Пишет в --out:
  event-map.json              — нормализованная карта (для diff_fmod.py и MCP)
  gd_sync_event_map.js        — скрипт для FMOD Studio: положить в папку Scripts проекта FMOD,
                                Scripts → Reload, затем Scripts → gd → Sync event map.
  gd_sync_event_map.cli.js    — то же без меню, для headless: fmodstudiocl -script <файл> <project>.fspro
                                (синхронизирует, сохраняет проект, экспортирует GUIDs.txt).
                                Идемпотентен: существующее не пересоздаёт, только добавляет недостающее.
  FmodEvents.cs               — static class с путями событий и снапшотов и именами параметров.
Формат таблицы — gd: audio-direction/references/fmod-conventions.md (колонки Event, Source, Type, Params, Space, Bus, Bank, …).
--files design/audio/files.md: файлы звука по событиям (колонки File, Event) импортируются в FMOD и кладутся
  на мастер-трек события (1 файл — SingleSound, несколько — MultiSound). Событие, где звук уже есть, не трогается.
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


def table_rows(text, need=("event", "source")):
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
        if all(k in header for k in need):
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
        bank = r.get("bank", "").strip("` ")
        if bank in EMPTY:
            bank = "Master"
        elif not re.fullmatch(r"[A-Z][A-Za-z0-9]*", bank):
            errors.append(f"{ev}: Bank «{bank}» не PascalCase — взят Master")
            bank = "Master"
        items.append({
            "path": ev,
            "kind": "snapshot" if ev.startswith("snapshot:/") else "event",
            "type": typ,
            "source": r.get("source", "").strip("` "),
            "space": r.get("space", "").strip().upper(),
            "bus": bus if BUS_RE.match(bus) else None,
            "bank": None if ev.startswith("snapshot:/") else bank,
            "files": [],
            "priority": r.get("priority", "").strip(),
            "params": params,
            "status": r.get("status", "").strip().lower(),
        })
    return items, errors


def attach_files(items, files_md, audio_root):
    """design/audio/files.md (колонки File, Event) → items[*]["files"] — абсолютные пути. Возвращает ошибки."""
    errors, by_path = [], {i["path"]: i for i in items}
    root = Path(audio_root) if audio_root else Path(files_md).parent
    for r in table_rows(Path(files_md).read_text(encoding="utf-8"), need=("file", "event")):
        f, ev = r.get("file", "").strip("` "), r.get("event", "").strip("` ")
        if not f or "<" in f or ev in EMPTY:
            continue
        p = (root / f).resolve()
        if ev not in by_path:
            errors.append(f"{f}: событие {ev} нет в карте")
        elif not p.is_file():
            errors.append(f"{f}: файла нет ({p})")
        else:
            by_path[ev]["files"].append(p.as_posix())
    return errors


JS_TEMPLATE = r"""// Сгенерировано gd-build fmod-sync (event_map_to_fmod.py) из design/audio/event-map.md. Не править руками.
// Установка: положить в папку Scripts проекта FMOD Studio → Scripts → Reload → Scripts → gd → Sync event map.
// Идемпотентно: существующие папки, события, шины, снапшоты и параметры не пересоздаются.
// Запущено на FMOD Studio 2.03.14 (fmodstudiocl -script): папки, события, шины (mixerInput.output),
// снапшоты, параметры и метки перечисления создаются; повторный запуск ничего не дублирует.
// Параметры в FMOD 2.03 — всегда ParameterPreset: один preset на имя, подключается к каждому событию
// (иначе второе событие получит «charge (2)» и setParameterByName("charge") на нём не сработает).
// Если шаг не удался, скрипт пишет строку «ВРУЧНУЮ» в консоль.
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

function gdEnsurePreset(p, stats) {
    var preset = studio.project.lookup("parameter:/" + p.name);
    if (!preset) {
        var gp = studio.project.workspace.addGameParameter(gdParamDef(p));
        if (p.global) gp.isGlobal = true;
        preset = gp.presetOwner || studio.project.lookup("parameter:/" + p.name);
        stats.presets++;
    } else if (preset.parameter.isGlobal !== p.global) {
        stats.manual.push("parameter:/" + p.name + ": в FMOD isGlobal=" + preset.parameter.isGlobal + ", в карте " + p.global);
    }
    return preset;
}

// Событие без банка не попадает ни в сборку, ни в GUIDs.txt — в игре его не загрузить.
// Банк — колонка Bank карты (пусто = Master). Master — мастер-банк проекта (isMasterBank), остальные создаются.
function gdEnsureBank(name, stats) {
    var banks = studio.project.model.Bank.findInstances();
    for (var i = 0; i < banks.length; i++) {
        if (name === "Master" ? banks[i].isMasterBank : banks[i].name === name) return banks[i];
    }
    if (name === "Master") return null;
    var b = studio.project.create("Bank");
    b.name = name;
    b.folder = studio.project.workspace.masterBankFolder;
    stats.banks++;
    return b;
}

function gdEnsureInBank(ev, bank, stats) {
    if (!bank) { stats.manual.push(ev.getPath() + ": в проекте нет мастер-банка — назначить банк вручную"); return; }
    var cur = ev.banks || [];
    for (var i = 0; i < cur.length; i++) { if (cur[i].id === bank.id) return; }
    ev.relationships.banks.add(bank);
    stats.banked++;
}

// Звук из design/audio/files.md: один файл — SingleSound, несколько — MultiSound (вариации).
// Если на мастер-треке события уже есть инструмент, событие не трогаем: звук мог положить человек.
function gdAudioFile(path) {
    var name = path.replace(/\\/g, "/").split("/").pop();
    var existing = studio.project.workspace.masterAssetFolder.getAsset(name);
    return existing || studio.project.importAudioFile(path);
}

function gdEnsureSounds(ev, files, stats) {
    if (!files || !files.length) return;
    if (ev.masterTrack.modules.length) { stats.kept++; return; }
    var afs = [];
    for (var i = 0; i < files.length; i++) {
        var af = gdAudioFile(files[i]);
        if (af) afs.push(af); else stats.manual.push(ev.getPath() + ": файл не импортирован " + files[i]);
    }
    if (!afs.length) return;
    var len = 0;
    for (var j = 0; j < afs.length; j++) { len = Math.max(len, afs[j].length || 0); }
    if (afs.length === 1) {
        var s = ev.masterTrack.addSound(ev.timeline, "SingleSound", 0, len);
        s.audioFile = afs[0];
    } else {
        var m = ev.masterTrack.addSound(ev.timeline, "MultiSound", 0, len);
        for (var k = 0; k < afs.length; k++) {
            var ss = studio.project.create("SingleSound");
            ss.audioFile = afs[k];
            ss.owner = m;
        }
    }
    stats.sounds += afs.length;
}

function gdEventHasPreset(ev, preset) {
    var list = ev.getParameterPresets();
    for (var i = 0; i < list.length; i++) { if (list[i].id === preset.parameter.id) return true; }
    return false;
}

function gdSync() {
    var stats = { folders: 0, events: 0, buses: 0, snapshots: 0, params: 0, presets: 0, banks: 0, banked: 0,
                  sounds: 0, kept: 0, manual: [] };
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
        try { gdEnsureInBank(ev, gdEnsureBank(it.bank || "Master", stats), stats); }
        catch (e) { stats.manual.push(it.path + ": назначить банк " + it.bank + " вручную (" + e + ")"); }
        try { gdEnsureSounds(ev, it.files, stats); }
        catch (e) { stats.manual.push(it.path + ": звук не добавлен (" + e + ")"); }
        if (it.bus) {
            var bus = gdEnsureBus(it.bus, stats);
            try { ev.mixerInput.output = bus; }
            catch (e) { stats.manual.push(it.path + ": назначить шину " + it.bus + " вручную"); }
        }
        for (var j = 0; j < it.params.length; j++) {
            var p = it.params[j];
            try {
                var preset = gdEnsurePreset(p, stats);
                if (!gdEventHasPreset(ev, preset)) { ev.addGameParameter(preset); stats.params++; }
            } catch (e) { stats.manual.push(it.path + ": параметр " + p.name + " не подключён (" + e + ")"); }
        }
    }
    gdLog("папок +" + stats.folders + ", событий +" + stats.events + ", шин +" + stats.buses +
          ", снапшотов +" + stats.snapshots + ", параметров (preset) +" + stats.presets + ", подключений к событиям +" + stats.params +
          ", банков +" + stats.banks + ", в банк +" + stats.banked + ", звуков +" + stats.sounds +
          (stats.kept ? " (событий со своим звуком не тронуто: " + stats.kept + ")" : ""));
    for (var k = 0; k < stats.manual.length; k++) { gdLog("ВРУЧНУЮ: " + stats.manual[k]); }
    gdLog("Готово. Сохраните проект и экспортируйте GUIDs (File → Export GUIDs) для diff_fmod.py.");
}

studio.menu.addMenuItem({ name: "gd\\Sync event map", execute: gdSync });
"""

MENU_LINE = 'studio.menu.addMenuItem({ name: "gd\\\\Sync event map", execute: gdSync });'
CLI_TAIL = """// Headless: fmodstudiocl -script gd_sync_event_map.cli.js <project>.fspro
gdSync();
studio.project.save();
studio.project.exportGUIDs();
gdLog("Проект сохранён, GUIDs экспортированы: <project>/Build/GUIDs.txt.");"""


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
    ap.add_argument("--files", default=None, help="design/audio/files.md — импорт звуков в события")
    ap.add_argument("--audio-root", default=None, help="корень путей колонки File (по умолчанию папка files.md)")
    a = ap.parse_args()

    items, errors = load(a.event_map)
    if a.files:
        errors += attach_files(items, a.files, a.audio_root)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "event-map.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    js = JS_TEMPLATE.replace("__DATA__", json.dumps(items, ensure_ascii=False))
    (out / "gd_sync_event_map.js").write_text(js, encoding="utf-8", newline="\n")
    (out / "gd_sync_event_map.cli.js").write_text(js.replace(MENU_LINE, CLI_TAIL), encoding="utf-8", newline="\n")
    (out / f"{a.cls}.cs").write_text(make_cs(items, a.namespace, a.cls), encoding="utf-8", newline="\n")
    ev = sum(1 for i in items if i["kind"] == "event")
    banks = sorted({i["bank"] for i in items if i.get("bank")})
    print(f"Событий: {ev} · снапшотов: {len(items) - ev} · параметров: {sum(len(i['params']) for i in items)}"
          f" · банков: {len(banks)} ({', '.join(banks)}) · файлов звука: {sum(len(i['files']) for i in items)}")
    print(f"Записано: {out / 'event-map.json'}, {out / 'gd_sync_event_map.js'} (+ .cli.js), {out / (a.cls + '.cs')}")
    for e in errors:
        print(f"FAIL {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
