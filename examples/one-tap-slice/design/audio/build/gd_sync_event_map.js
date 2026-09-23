// Сгенерировано gd-build fmod-sync (event_map_to_fmod.py) из design/audio/event-map.md. Не править руками.
// Установка: положить в папку Scripts проекта FMOD Studio → Scripts → Reload → Scripts → gd → Sync event map.
// Идемпотентно: существующие папки, события, шины, снапшоты и параметры не пересоздаются.
// Проверено по документации FMOD Studio Scripting API (create, lookup, Event.addGameParameter,
// workspace.addGameParameter, mixer.masterBus). Маршрутизация события в шину — через mixerInput.output
// в try/catch: если ваша версия FMOD не поддерживает, скрипт сообщит, и шину нужно назначить вручную.
var GD_MAP = [{"path": "event:/SFX/Player/Charge", "kind": "event", "type": "loop", "source": "hop#FB1", "space": "2D", "bus": "bus:/SFX", "priority": "3", "params": [{"name": "charge", "global": false, "min": 0.0, "max": 1.0, "labels": null}], "status": "todo"}, {"path": "event:/SFX/Player/Jump", "kind": "event", "type": "oneshot", "source": "hop#FB2", "space": "2D", "bus": "bus:/SFX", "priority": "1", "params": [{"name": "charge", "global": false, "min": 0.0, "max": 1.0, "labels": null}], "status": "todo"}, {"path": "event:/SFX/Player/Land", "kind": "event", "type": "oneshot", "source": "hop#FB3", "space": "2D", "bus": "bus:/SFX", "priority": "1", "params": [], "status": "todo"}, {"path": "event:/SFX/Player/Fall", "kind": "event", "type": "oneshot", "source": "hop#FB4", "space": "2D", "bus": "bus:/SFX", "priority": "1", "params": [], "status": "todo"}, {"path": "event:/SFX/Pickup/Spark", "kind": "event", "type": "oneshot", "source": "spark#FB1", "space": "2D", "bus": "bus:/SFX", "priority": "2", "params": [{"name": "tier", "global": false, "min": 0.0, "max": 1.0, "labels": ["single", "double"]}], "status": "todo"}, {"path": "event:/UI/Record/New", "kind": "event", "type": "stinger", "source": "spark#FB2", "space": "2D", "bus": "bus:/UI", "priority": "2", "params": [], "status": "todo"}, {"path": "event:/Music/Run/Main", "kind": "event", "type": "music", "source": "music:run", "space": "2D", "bus": "bus:/Music", "priority": "5", "params": [{"name": "g_intensity", "global": true, "min": 0.0, "max": 1.0, "labels": null}], "status": "todo"}, {"path": "event:/Amb/Sky/Wind", "kind": "event", "type": "amb", "source": "amb:sky", "space": "2D", "bus": "bus:/Amb", "priority": "5", "params": [], "status": "todo"}, {"path": "snapshot:/Dead", "kind": "snapshot", "type": "snapshot", "source": "state:dead", "space": "—", "bus": null, "priority": "—", "params": [], "status": "todo"}];

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
