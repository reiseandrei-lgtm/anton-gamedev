// Сгенерировано gd-build fmod-sync (event_map_to_fmod.py) из design/audio/event-map.md. Не править руками.
// Установка: положить в папку Scripts проекта FMOD Studio → Scripts → Reload → Scripts → gd → Sync event map.
// Идемпотентно: существующие папки, события, шины, снапшоты и параметры не пересоздаются.
// Запущено на FMOD Studio 2.03.14 (fmodstudiocl -script): папки, события, шины (mixerInput.output),
// снапшоты, параметры и метки перечисления создаются; повторный запуск ничего не дублирует.
// Параметры в FMOD 2.03 — всегда ParameterPreset: один preset на имя, подключается к каждому событию
// (иначе второе событие получит «charge (2)» и setParameterByName("charge") на нём не сработает).
// Если шаг не удался, скрипт пишет строку «ВРУЧНУЮ» в консоль.
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
// В карте нет колонки Bank: по умолчанию мастер-банк (разбиение по банкам — решение аудио-дирекции).
function gdMasterBank() {
    var banks = studio.project.model.Bank.findInstances();
    for (var i = 0; i < banks.length; i++) { if (banks[i].isMasterBank) return banks[i]; }
    return null;
}

function gdEnsureInBank(ev, bank, stats) {
    if (!bank) { stats.manual.push(ev.getPath() + ": в проекте нет мастер-банка — назначить банк вручную"); return; }
    if (ev.banks && ev.banks.length) return;
    ev.relationships.banks.add(bank);
    stats.banked++;
}

function gdEventHasPreset(ev, preset) {
    var list = ev.getParameterPresets();
    for (var i = 0; i < list.length; i++) { if (list[i].id === preset.parameter.id) return true; }
    return false;
}

function gdSync() {
    var stats = { folders: 0, events: 0, buses: 0, snapshots: 0, params: 0, presets: 0, banked: 0, manual: [] };
    var master = gdMasterBank();
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
        try { gdEnsureInBank(ev, master, stats); }
        catch (e) { stats.manual.push(it.path + ": назначить банк вручную (" + e + ")"); }
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
          ", в банк +" + stats.banked);
    for (var k = 0; k < stats.manual.length; k++) { gdLog("ВРУЧНУЮ: " + stats.manual[k]); }
    gdLog("Готово. Сохраните проект и экспортируйте GUIDs (File → Export GUIDs) для diff_fmod.py.");
}

// Headless: fmodstudiocl -script gd_sync_event_map.cli.js <project>.fspro
gdSync();
studio.project.save();
studio.project.exportGUIDs();
gdLog("Проект сохранён, GUIDs экспортированы: <project>/Build/GUIDs.txt.");
