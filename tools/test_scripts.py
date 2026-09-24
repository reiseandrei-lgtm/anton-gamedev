#!/usr/bin/env python3
"""Тесты детерминированных скриптов плагинов gd и gd-build (Python stdlib unittest).

Запуск из корня репозитория:
  python3 -m unittest tools/test_scripts.py -v

Позитивные случаи — на examples/one-tap-slice (должны проходить), негативные — на временных файлах
(каждый скрипт обязан поймать свою ошибку).
"""
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GD = ROOT / "plugins/gd/skills"
GB = ROOT / "plugins/gd-build/skills"
EX = ROOT / "examples/one-tap-slice"
D = EX / "design"
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")


def run(script, *args):
    p = subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True,
                       text=True, encoding="utf-8", env=ENV)
    return p.returncode, p.stdout + p.stderr


def tmp(text, suffix=".md", dir_=None):
    f = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8", dir=dir_)
    f.write(textwrap.dedent(text).lstrip("\n"))
    f.close()
    return f.name


GDD_HOP = [D / "gdd/hop.md", D / "gdd/spark.md"]


class Example(unittest.TestCase):
    """Пример проходит все проверки."""

    def test_palette(self):
        self.assertEqual(run(GD / "art-direction/scripts/check_palette.py", D / "art/art-bible.md")[0], 0)

    def test_assets(self):
        code, out = run(GD / "art-direction/scripts/check_assets.py", D / "art/asset-list.md",
                        "--handoff", D / "handoff/first-hop.md", "--gdd", *GDD_HOP)
        self.assertEqual(code, 0, out)

    def test_event_map(self):
        code, out = run(GD / "audio-direction/scripts/check_event_map.py", D / "audio/event-map.md", "--gdd", *GDD_HOP)
        self.assertEqual(code, 0, out)
        self.assertIn("покрыто: 6", out)

    def test_knobs(self):
        self.assertEqual(run(GD / "tech-design/scripts/check_knobs.py", D / "tech/architecture.md", "--gdd", *GDD_HOP)[0], 0)

    def test_coverage(self):
        code, out = run(GD / "qa-plan/scripts/check_coverage.py", D / "qa/test-plan-first-hop.md", "--gdd", *GDD_HOP,
                        "--handoff", D / "handoff/first-hop.md")
        self.assertEqual(code, 0, out)

    def test_events(self):
        code, out = run(GD / "metrics-plan/scripts/check_events.py", D / "analytics/events.md",
                        "--funnels", D / "analytics/funnels.md")
        self.assertEqual(code, 0, out)

    def test_aggregate(self):
        notes = sorted((D / "playtest/2026-09-23-first-hop/notes").glob("*.md"))
        code, out = run(GD / "playtest/scripts/aggregate_codes.py", *notes)
        self.assertEqual(code, 0)
        self.assertIn("Игроков: 5", out)
        self.assertIn("00:00–01:00: 4/5", out)


class Negative(unittest.TestCase):
    """Каждый скрипт ловит свою ошибку."""

    def test_legacy_gdd_numbered(self):
        sys.path.insert(0, str(GD / "gd-router/scripts"))
        import gdd_ids
        p = tmp("""
            ## Core Rules
            1. первое правило
            2. второе правило
            ## Edge Cases
            | Scenario | Behavior | Why |
            |---|---|---|
            | a | b | c |
            """)
        _, ids, warns = gdd_ids.gdd_ids(p)
        self.assertIn("R2", ids)
        self.assertIn("E1", ids)
        self.assertTrue(any("без стабильных ID" in w for w in warns))

    def test_palette_hue_only(self):
        p = tmp("""
            ## Palette
            | Role | HEX | Use |
            |---|---|---|
            | bg | #1B1F2A | |
            | gameplay | #6B8E23 | |
            | interactive | #4EC9F2 | |
            | danger | #B5651D | |
            | ui-text | #F5F5F5 | |
            """)
        code, out = run(GD / "art-direction/scripts/check_palette.py", p)
        self.assertEqual(code, 1)
        self.assertIn("дейтеранопия", out)

    def test_palette_missing_role(self):
        p = tmp("""
            ## Palette
            | Role | HEX | Use |
            |---|---|---|
            | bg | #000000 | |
            """)
        self.assertEqual(run(GD / "art-direction/scripts/check_palette.py", p)[0], 1)

    def test_assets_bad(self):
        p = tmp("""
            | ID | Type | For | Source | License / URL | Priority | Status |
            |---|---|---|---|---|---|---|
            | Hero Sprite | spr | hop#R1 | cc0 | — | slice | todo |
            | spr_hero_base_idle | tex | hop#R99 | magic | | slice | todo |
            """)
        code, out = run(GD / "art-direction/scripts/check_assets.py", p, "--gdd", *GDD_HOP)
        self.assertEqual(code, 1)
        for c in ("A1", "A4", "A5", "A7"):
            self.assertIn(c, out)

    def test_event_map_uncovered(self):
        p = tmp("""
            | Event | Source | Type | Params | Space | Bus | Priority | Variations | Status |
            |---|---|---|---|---|---|---|---|---|
            | event:/sfx/jump | hop#FB2 | oneshot | Speed | 2D | SFX | 1 | — | todo |
            """)
        code, out = run(GD / "audio-direction/scripts/check_event_map.py", p, "--gdd", *GDD_HOP)
        self.assertEqual(code, 1)
        for c in ("E1", "E4", "E5", "E6"):
            self.assertIn(c, out)

    def test_knobs_missing_and_cycle(self):
        p = tmp("""
            ## Modules
            | Module | Systems | Depends on |
            |---|---|---|
            | A | hop | B |
            | B | spark | A |
            ## Config map
            | Knob | Config asset | Field | Type | Range |
            |---|---|---|---|---|
            | hop#K1 | HopConfig | minDistance | float | 0..9 |
            | hop#K42 | HopConfig | x | float | 0..1 |
            """)
        code, out = run(GD / "tech-design/scripts/check_knobs.py", p, "--gdd", *GDD_HOP)
        self.assertEqual(code, 1)
        for c in ("T1", "T2", "T3", "T5"):
            self.assertIn(c, out)

    def test_coverage_gaps(self):
        p = tmp("""
            | ID | Covers | Type | Priority | Given | When | Then | Auto |
            |---|---|---|---|---|---|---|---|
            | T-hop-01 | hop#R1 | manual | P1 | | | | yes |
            | T-hop-01 | hop#R77 | unit | P1 | | | | |
            ## Smoke
            """)
        code, out = run(GD / "qa-plan/scripts/check_coverage.py", p, "--gdd", *GDD_HOP,
                        "--handoff", D / "handoff/first-hop.md")
        self.assertEqual(code, 1)
        for c in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q8"):
            self.assertIn(c, out)

    def test_events_pii(self):
        p = tmp("""
            ## KPIs
            | KPI | Question | Formula (events) | Target | Decision threshold |
            |---|---|---|---|---|
            | k1 | | count(ghost_event) | 1 | |
            ## Events
            | Event | Params | Trigger | Serves |
            |---|---|---|---|
            | LevelStart | email:string | x | k1 |
            """)
        code, out = run(GD / "metrics-plan/scripts/check_events.py", p)
        self.assertEqual(code, 1)
        for c in ("M1", "M4", "M5", "M7"):
            self.assertIn(c, out)


class GdBuild(unittest.TestCase):
    def test_nunit_failures_mapped(self):
        code, out = run(GB / "qa-run/scripts/parse_nunit.py", EX / "fixtures/TestResults/editmode-results.xml",
                        "--plan", D / "qa/test-plan-first-hop.md")
        self.assertEqual(code, 2)
        self.assertIn("T-spark-02", out)
        self.assertNotIn("WARN T-hop-02", out)  # T-ID из [Property("TID", …)] распознан
        self.assertNotIn("WARN T-hop-01", out)  # T-ID из имени метода распознан
        self.assertIn("WARN T-hop-04", out)     # тест плана, которого нет в прогоне

    def test_nunit_zero_tests_is_failure(self):
        self.assertEqual(run(GB / "qa-run/scripts/parse_nunit.py", EX / "fixtures/TestResults/empty-results.xml")[0], 3)

    def test_fmod_generate_and_diff(self):
        with tempfile.TemporaryDirectory() as out:
            code, log = run(GB / "fmod-sync/scripts/event_map_to_fmod.py", D / "audio/event-map.md", "--out", out)
            self.assertEqual(code, 0, log)
            items = json.loads(Path(out, "event-map.json").read_text(encoding="utf-8"))
            self.assertEqual(len(items), 9)
            cs = Path(out, "FmodEvents.cs").read_text(encoding="utf-8")
            self.assertIn('SFX_Player_Jump = "event:/SFX/Player/Jump"', cs)
            js = Path(out, "gd_sync_event_map.js").read_text(encoding="utf-8")
            self.assertIn("studio.menu.addMenuItem", js)
            code, log = run(GB / "fmod-sync/scripts/diff_fmod.py", Path(out, "event-map.json"),
                            EX / "fixtures/fmod/GUIDs.txt")
            self.assertEqual(code, 1)
            self.assertIn("D1 event:/Amb/Sky/Wind", log)
            self.assertIn("D2 event:/SFX/Player/Jump2", log)

    def test_nunit_live_unity_results(self):
        """Настоящий вывод Unity 6000.3.24f1: все автоматизируемые тесты плана найдены в прогоне."""
        live = EX / "fixtures/live/TestResults"
        code, out = run(GB / "qa-run/scripts/parse_nunit.py", live / "editmode-results.xml",
                        live / "playmode-results.xml", "--plan", D / "qa/test-plan-first-hop.md")
        self.assertEqual(code, 0, out)
        self.assertIn("План: автоматизируемых 15 · в прогоне 15", out)
        self.assertNotIn("WARN", out)

    def test_fmod_cli_variant_and_live_guids(self):
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(run(GB / "fmod-sync/scripts/event_map_to_fmod.py", D / "audio/event-map.md", "--out", out)[0], 0)
            js = Path(out, "gd_sync_event_map.js").read_text(encoding="utf-8")
            cli = Path(out, "gd_sync_event_map.cli.js").read_text(encoding="utf-8")
            self.assertNotIn("studio.menu.addMenuItem", cli)
            self.assertIn("gdSync();\nstudio.project.save();\nstudio.project.exportGUIDs();", cli)
            for api in ("getParameterPresets", "relationships.banks.add", "presetOwner", "isGlobal = true"):
                self.assertIn(api, js)
            code, log = run(GB / "fmod-sync/scripts/diff_fmod.py", Path(out, "event-map.json"),
                            EX / "fixtures/live/fmod/GUIDs.txt")
            self.assertEqual(code, 0, log)
            self.assertIn("Итог: PASS", log)

    def test_fmod_diff_missing_parameter(self):
        with tempfile.TemporaryDirectory() as out:
            run(GB / "fmod-sync/scripts/event_map_to_fmod.py", D / "audio/event-map.md", "--out", out)
            guids = (EX / "fixtures/live/fmod/GUIDs.txt").read_text(encoding="utf-8")
            g = tmp("\n".join(l for l in guids.splitlines() if "parameter:/tier" not in l), suffix=".txt")
            code, log = run(GB / "fmod-sync/scripts/diff_fmod.py", Path(out, "event-map.json"), g)
            self.assertEqual(code, 1)
            self.assertIn("D1 parameter:/tier", log)

    def test_fmod_bad_path(self):
        p = tmp("""
            | Event | Source | Type | Params | Space | Bus | Priority |
            |---|---|---|---|---|---|---|
            | event:/sfx/jump | x | oneshot | — | 2D | bus:/SFX | 1 |
            """)
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(run(GB / "fmod-sync/scripts/event_map_to_fmod.py", p, "--out", out)[0], 1)

    def test_gen_sfx(self):
        with tempfile.TemporaryDirectory() as out:
            code, log = run(GB / "slice-build/scripts/gen_sfx.py", out, "jump", "land")
            self.assertEqual(code, 0, log)
            self.assertTrue(Path(out, "ph_jump.wav").stat().st_size > 1000)
            self.assertEqual(run(GB / "slice-build/scripts/gen_sfx.py", out, "nope")[0], 2)

    def test_preflight_plan_mode(self):
        with tempfile.TemporaryDirectory() as proj:
            code, out = run(GB / "slice-build/scripts/preflight.py", proj, "--design", D, "--slice", "first-hop")
            self.assertEqual(code, 0)
            self.assertIn("Рекомендуемый режим: plan", out)

    def test_preflight_fake_unity_project(self):
        with tempfile.TemporaryDirectory() as proj:
            Path(proj, "ProjectSettings").mkdir()
            Path(proj, "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 6000.0.99f1\n", encoding="utf-8")
            Path(proj, "Packages").mkdir()
            Path(proj, "Packages/manifest.json").write_text(json.dumps(
                {"dependencies": {"com.coplaydev.unity-mcp": "git+https://x", "com.unity.inputsystem": "1.11.0"}}),
                encoding="utf-8")
            code, out = run(GB / "slice-build/scripts/preflight.py", proj, "--design", D)
            self.assertIn("версия 6000.0.99f1", out)
            self.assertIn("MCP: CoplayDev/unity-mcp", out)
            self.assertIn("Test Framework", out)  # не хватает пакета
            self.assertIn('"testables": ["com.unity.inputsystem"]', out)  # без него нет InputTestFixture

    def test_preflight_old_input_handler(self):
        with tempfile.TemporaryDirectory() as proj:
            Path(proj, "ProjectSettings").mkdir()
            Path(proj, "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 6000.0.99f1\n", encoding="utf-8")
            Path(proj, "ProjectSettings/ProjectSettings.asset").write_text("PlayerSettings:\n  activeInputHandler: 0\n", encoding="utf-8")
            Path(proj, "Packages").mkdir()
            Path(proj, "Packages/manifest.json").write_text(json.dumps(
                {"dependencies": {"com.unity.inputsystem": "1.20.0", "com.unity.test-framework": "1.6.0"},
                 "testables": ["com.unity.inputsystem"]}), encoding="utf-8")
            code, out = run(GB / "slice-build/scripts/preflight.py", proj, "--design", D)
            self.assertIn("Active Input Handling", out)
            self.assertNotIn('"testables"', out)


def png(path, w, h, color, box=None, box_color=(255, 0, 0)):
    """Простой RGB PNG через writer из diff_png.py (stdlib)."""
    sys.path.insert(0, str(GB / "qa-run/scripts"))
    import diff_png
    rows = []
    for y in range(h):
        row = bytearray()
        for x in range(w):
            inside = box and box[0] <= x < box[0] + box[2] and box[1] <= y < box[1] + box[3]
            row += bytes(box_color if inside else color)
        rows.append(row)
    diff_png.write_png(path, w, h, rows)


def glb(path, triangles):
    """Минимальный GLB: один меш, индексы на `triangles` треугольников."""
    doc = {"asset": {"version": "2.0"}, "meshes": [{"name": "m", "primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
           "accessors": [{"count": 3, "componentType": 5126, "type": "VEC3"}, {"count": triangles * 3, "componentType": 5125, "type": "SCALAR"}]}
    js = json.dumps(doc).encode()
    js += b" " * (-len(js) % 4)
    import struct
    Path(path).write_bytes(b"glTF" + struct.pack("<II", 2, 20 + len(js)) + struct.pack("<I", len(js)) + b"JSON" + js)


class WaveA(unittest.TestCase):
    """Скрипты волны A: позитив на примере, негатив на временных файлах."""

    def test_coverage_milestone_multi_plan(self):
        code, out = run(GD / "qa-plan/scripts/check_coverage.py", D / "qa/test-plan-alpha.md", D / "qa/test-plan-first-hop.md",
                        "--gdd", *GDD_HOP, D / "gdd/chain.md", "--handoff", D / "handoff/first-hop.md", D / "handoff/alpha.md",
                        "--budgets", D / "tech/budgets.md")
        self.assertEqual(code, 0, out)
        self.assertIn("Итог: PASS", out)

    def test_coverage_visual_manual_and_perf_polish(self):
        p = tmp("""
            ## Cases
            | ID | Covers | Type | Priority | Given | When | Then | Auto |
            |---|---|---|---|---|---|---|---|
            | T-hop-90 | hop#FB3 | manual | P2 | — | приземление | пыль видна | no |
            ## Smoke
            1. старт
            """)
        code, out = run(GD / "qa-plan/scripts/check_coverage.py", p, "--gdd", D / "gdd/hop.md",
                        "--budgets", D / "tech/budgets.md", "--stage", "polish")
        self.assertEqual(code, 1)
        self.assertIn("Q9 hop#FB3", out)
        self.assertIn("FAIL Q10 budgets#B1", out)

    def test_build_log_live_and_negative(self):
        code, out = run(GB / "slice-build/scripts/check_build_log.py", D / "build/first-hop.log.md",
                        "--handoff", D / "handoff/first-hop.md", "--plan", D / "qa/test-plan-first-hop.md")
        self.assertEqual(code, 0, out)
        bad = tmp("""
            ---
            system: chain
            mode: plan
            ---
            ## Rules
            | ID | Статус | Доказательство | Задачи |
            |---|---|---|---|
            | R1 | ✅ | T-chain-99 зелёный | 1 |
            | R2 | ✅ | — | 1 |
            | R3 | ⛔ | — | — |
            """)
        code, out = run(GB / "slice-build/scripts/check_build_log.py", bad, "--gdd", D / "gdd/chain.md",
                        "--handoff", D / "handoff/alpha.md", "--plan", D / "qa/test-plan-alpha.md")
        self.assertEqual(code, 1)
        for rule in ("BL1 R4", "BL1 ED-chain-1", "BL2 R2", "BL3 R1", "BL4 R1", "BL5 R3"):
            self.assertIn(rule, out)
        self.assertNotIn("BL1 ED-hop-1", out)  # чужая система майлстоуна не требуется

    def test_juice(self):
        log = tmp("""
            ## Juice
            | FB | Событие | Цель (кадры) | Замер (кадры) | Допуск | Звук в том же кадре | Доказательство |
            |---|---|---|---|---|---|---|
            | FB2 | прыжок | 2 | 2 | 0 | да | тест |
            | FB3 | приземление | ≤ 0 | 2 | 0 | нет | тест |
            """)
        code, out = run(GB / "juice-build/scripts/check_juice.py", log, "--gdd", D / "gdd/hop.md", "--map", D / "audio/event-map.md")
        self.assertEqual(code, 1)
        self.assertIn("JU2 hop#FB3", out)
        self.assertIn("JU1 hop#FB1", out)
        self.assertIn("JU4 hop#FB3", out)
        self.assertNotIn("hop#FB2:", out.replace("JU1 hop#FB2", ""))

    def test_ui(self):
        with tempfile.TemporaryDirectory() as ui:
            Path(ui, "Theme.uss").write_text(":root { --role-bg: #14172B; --role-accent: #000000; --role-neon: #FF00FF; }", encoding="utf-8")
            Path(ui, "HUD.uss").write_text("#hud-score { color: #FFFFFF; }\n#restart-again { width: 30px; height: 60px; color: var(--role-ui-text); }\n#fade { opacity: 0; }", encoding="utf-8")
            Path(ui, "HUD.uxml").write_text('<ui:UXML><ui:Label name="hud-score" text="0"/><ui:Button name="restart-again" text="Ещё раз"/></ui:UXML>', encoding="utf-8")
            code, out = run(GB / "ui-build/scripts/check_ui.py", D / "ux/hud.md", ui, "--palette", D / "art/art-bible.md")
            self.assertEqual(code, 1)
            self.assertIn("UI1", out)                     # restart-record не сверстан
            self.assertIn("--role-accent = #000000", out)  # цвет роли ≠ библии
            self.assertIn("--role-neon", out)             # роли нет в библии
            self.assertIn("UI2 HUD.uss:1", out)           # hex вне темы
            self.assertIn("UI3", out)                     # литеральный текст
            self.assertIn("UI5 restart-again: width 30px", out)
            self.assertNotIn("#fade", out)                # селектор #id — не цвет

    def test_import(self):
        with tempfile.TemporaryDirectory() as root:
            png(Path(root, "tex_sky_night_gradient.png"), 40, 20, (20, 23, 43))
            png(Path(root, "ph_mdl_player_capsule_idle.png"), 4, 4, (0, 0, 0))
            glb(Path(root, "mdl_lantern_base_lit.glb"), 900)
            png(Path(root, "orphan.png"), 4, 4, (0, 0, 0))
            assets = tmp("""
                | ID | Type | For | States / frames | Size | Budget | Source | License / URL | Priority | Status |
                |---|---|---|---|---|---|---|---|---|---|
                | tex_sky_night_gradient | tex | ED1 | — | 40x20 | ≤ 32 px | made | — | mvp | done |
                | mdl_player_capsule_idle | mdl | hop#R1 | idle | 1 u | — | made | — | slice | wip |
                | mdl_lantern_base_lit | mdl | hop#FB1 | lit | 1 u | ≤ 800 tris | cc0 | — | slice | done |
                | font_ui_main_regular | font | ux:hud | — | — | — | cc0 | https://kenney.nl | slice | done |
                """)
            code, out = run(GB / "asset-integrate/scripts/check_import.py", root, "--assets", assets)
            self.assertEqual(code, 1)
            for rule in ("IM1 orphan.png", "IM2 font_ui_main_regular", "IM3 ph_mdl_player_capsule_idle.png",
                         "IM4 tex_sky_night_gradient.png: 40×20", "IM5 mdl_lantern_base_lit.glb: 900 tris", "IM6 mdl_lantern_base_lit"):
                self.assertIn(rule, out)
            code, out = run(GB / "asset-integrate/scripts/check_import.py", root, "--assets", D / "art/asset-list.md", "--stage", "beta")
            self.assertIn("IM8 mdl_player_capsule_idle", out)   # Beta на плейсхолдерах

    def test_diff_png(self):
        shots = D / "build/first-hop/screenshots"
        code, out = run(GB / "qa-run/scripts/diff_png.py", shots / "01-start.png", shots / "01-start.png")
        self.assertEqual(code, 0, out)
        with tempfile.TemporaryDirectory() as d:
            png(Path(d, "a.png"), 50, 40, (20, 23, 43))
            png(Path(d, "b.png"), 50, 40, (20, 23, 43), box=(0, 0, 10, 10))
            png(Path(d, "c.png"), 40, 40, (20, 23, 43))
            code, out = run(GB / "qa-run/scripts/diff_png.py", Path(d, "a.png"), Path(d, "b.png"), "--out", Path(d, "diff.png"))
            self.assertEqual(code, 1)
            self.assertIn("VD2", out)
            self.assertTrue(Path(d, "diff.png").stat().st_size > 50)
            code, out = run(GB / "qa-run/scripts/diff_png.py", Path(d, "a.png"), Path(d, "b.png"), "--mask", "0,0,10,10")
            self.assertEqual(code, 0, out)
            self.assertIn("VD1", run(GB / "qa-run/scripts/diff_png.py", Path(d, "a.png"), Path(d, "c.png"))[1])
            base, shotdir = Path(d, "base"), Path(d, "shots")
            base.mkdir(); shotdir.mkdir()
            png(shotdir / "T-ui-01.png", 8, 8, (1, 2, 3))
            code, out = run(GB / "qa-run/scripts/diff_png.py", "--baseline-dir", base, "--shots-dir", shotdir)
            self.assertIn("VD4 T-ui-01.png", out)
            self.assertTrue((base / "_pending/T-ui-01.png").is_file())

    def test_soak(self):
        rows = "\n".join(f"| {t} | 5.0 | {200 + t / 20:.1f} | 0 | {10 + t} | 100 |" for t in range(0, 361, 30))
        rep = tmp("## Samples\n| t (s) | frame ms | memory MB | exceptions | materials | objects |\n|---|---|---|---|---|---|\n" + rows + "\n")
        code, out = run(GB / "qa-run/scripts/check_soak.py", rep)
        self.assertEqual(code, 1)
        self.assertIn("SK1", out)
        self.assertIn("SK5 materials", out)
        self.assertNotIn("SK5 objects", out)

    def test_fmod_bank_and_files(self):
        with tempfile.TemporaryDirectory() as out:
            audio = Path(out, "Assets/_Project/Resources/Audio")
            audio.mkdir(parents=True)
            for f in ("ph_jump", "ph_land", "ph_fail", "ph_confirm", "ph_coin"):
                Path(audio, f + ".wav").write_bytes(b"RIFF")
            code, log = run(GB / "fmod-sync/scripts/event_map_to_fmod.py", D / "audio/event-map.md", "--out", out,
                            "--files", D / "audio/files.md", "--audio-root", out)
            self.assertEqual(code, 0, log)
            items = {i["path"]: i for i in json.loads(Path(out, "event-map.json").read_text(encoding="utf-8"))}
            self.assertEqual(items["event:/Music/Run/Main"]["bank"], "Music")
            self.assertEqual(len(items["event:/SFX/Pickup/Spark"]["files"]), 2)
            self.assertIn("банков: 2 (Master, Music)", log)
            code, log = run(GB / "fmod-sync/scripts/event_map_to_fmod.py", D / "audio/event-map.md", "--out", out,
                            "--files", D / "audio/files.md", "--audio-root", Path(out, "nope"))
            self.assertEqual(code, 1)
            self.assertIn("файла нет", log)

    def test_fmod_hook(self):
        with tempfile.TemporaryDirectory() as root:
            m = Path(root, "map.json")
            m.write_text(json.dumps([{"path": "event:/SFX/Player/Jump"}, {"path": "event:/SFX/Player/Land"}]), encoding="utf-8")
            Path(root, "FmodEvents.cs").write_text('public const string SFX_Player_Jump = "event:/SFX/Player/Jump";', encoding="utf-8")
            Path(root, "Player.cs").write_text('void J(){ RuntimeManager.PlayOneShot("event:/SFX/Player/Jump"); var i = RuntimeManager.CreateInstance(FmodEvents.SFX_Player_Jump); }', encoding="utf-8")
            code, out = run(GB / "fmod-sync/scripts/check_fmod_calls.py", root, "--map", m)
            self.assertEqual(code, 1)
            self.assertIn("FH1 Player.cs:1", out)
            self.assertIn("FH3 event:/SFX/Player/Land", out)
            self.assertIn("FH4 Player.cs", out)


class Repo(unittest.TestCase):
    def test_check_plugins(self):
        code, out = run(ROOT / "tools/check_plugins.py")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
