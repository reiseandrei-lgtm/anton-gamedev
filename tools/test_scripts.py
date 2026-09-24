#!/usr/bin/env python3
"""Тесты детерминированных скриптов плагинов gd и gd-build (Python stdlib unittest).

Запуск из корня репозитория:
  python3 -m unittest tools/test_scripts.py -v

Позитивные случаи — на examples/one-tap-slice (должны проходить), негативные — на временных файлах и фикстурах
examples/one-tap-slice/fixtures/ (каждый скрипт обязан поймать свою ошибку). WAV и GLB собираются хелперами в tempdir.
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


FX = EX / "fixtures"


def wav(path, seconds=1.0, lufs=None, amp=0.1, sr=48000, freq=997.0, frames=None):
    """Моно-синус PCM 16 бит. lufs — целевая громкость по BS.1770 (моно-синус: LUFS = 20·lg(A) − 3.01)."""
    import math
    import struct
    import wave
    if lufs is not None:
        amp = 10 ** ((lufs + 3.01) / 20)
    n = frames if frames is not None else int(sr * seconds)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    data = struct.pack(f"<{n}h", *(round(32767 * amp * math.sin(2 * math.pi * freq * i / sr)) for i in range(n)))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data)


def float_wav(path, n=4800, sr=48000):
    """WAV с 32-битными float-сэмплами (формат 3) — модуль wave его не читает."""
    import struct
    data = struct.pack(f"<{n}f", *([0.1] * n))
    fmt = struct.pack("<HHIIHH", 3, 1, sr, sr * 4, 4, 32)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(b"RIFF" + struct.pack("<I", 4 + 8 + len(fmt) + 8 + len(data)) + b"WAVE"
                           + b"fmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data)


def gltf_model(path, meshes, materials=1, clips=None):
    """GLB с JSON-чанком без буфера. meshes: [(имя, треугольников, (dx, dy, dz), масштаб по Y)]; clips: {имя: секунды}."""
    import struct
    doc = {"asset": {"version": "2.0"}, "nodes": [], "meshes": [], "accessors": [],
           "materials": [{"name": f"m{i}"} for i in range(materials)]}
    for name, tris, (dx, dy, dz), sy in meshes:
        pos = len(doc["accessors"])
        doc["accessors"] += [{"count": 3, "componentType": 5126, "type": "VEC3",
                              "min": [-dx / 2, 0, -dz / 2], "max": [dx / 2, dy, dz / 2]},
                             {"count": tris * 3, "componentType": 5125, "type": "SCALAR"}]
        doc["meshes"].append({"name": name, "primitives": [{"attributes": {"POSITION": pos}, "indices": pos + 1}]})
        doc["nodes"].append({"name": name, "mesh": len(doc["meshes"]) - 1, **({"scale": [1, sy, 1]} if sy != 1 else {})})
    for clip, sec in (clips or {}).items():
        doc["accessors"].append({"count": 2, "componentType": 5126, "type": "SCALAR", "min": [0], "max": [sec]})
        doc.setdefault("animations", []).append(
            {"name": clip, "samplers": [{"input": len(doc["accessors"]) - 1, "output": 0}], "channels": []})
    js = json.dumps(doc).encode()
    js += b" " * (-len(js) % 4)
    Path(path).write_bytes(b"glTF" + struct.pack("<II", 2, 20 + len(js)) + struct.pack("<I", len(js)) + b"JSON" + js)


def fails(out):
    return [line for line in out.splitlines() if line.startswith("FAIL")]


class WaveC(unittest.TestCase):
    """Скрипты волны C: позитивная и негативная фикстуры из examples/one-tap-slice/fixtures/."""

    def level(self, name):
        return run(GD / "level-design/scripts/check_level.py", FX / f"levels/{name}.md", "--gdd", D / "gdd",
                   "--systems", D / "systems-map.md")

    def test_level_ok(self):
        code, out = self.level("opening")
        self.assertEqual(code, 0, out)
        self.assertIn("Итог: PASS", out)
        self.assertIn("гейтов: 1", out)   # гейт с ключом на достижимой ветке — не soft lock

    def test_level_broken(self):
        code, out = self.level("broken")
        self.assertEqual(code, 1)
        for rule in ("LV1 LM3: knob «hop#K99»", "LV1 L1 N0→N1: зазор 4.5 > LM1", "LV1 L2 N1→N2: зазор 0.5 < LM2",
                     "LV2 EN3: напряжение 5", "LV2 пики 0:30 и 1:00", "LV3 G1: гейт на критическом пути (L3) без ключа",
                     "LV4 EN1: место «N9»", "LV4 EN2: система «ghost»", "LV4 EN3: ID spark#R99", "LV5: длина 4 мин"):
            self.assertIn(rule, out)
        self.assertNotIn("soft lock", out)

    def test_level_softlock(self):
        code, out = self.level("softlock")
        self.assertEqual(code, 1)
        self.assertIn("LV3 G1: ключ в N2 достижим только через свой гейт (L2) — soft lock", out)
        self.assertIn("LV3: goal N3 недостижим", out)
        self.assertEqual(len(fails(out)), 2, out)   # только LV3: метрики, темп и встречи в порядке

    def test_level_key_on_optional_link(self):
        """Ключ за optional-связью при гейте на critical: FAIL с подсказкой пометить ветку critical."""
        text = (FX / "levels/opening.md").read_text(encoding="utf-8").replace(
            "| L3 | N2 | N3 | hop | 2.8 | 0 | critical | ↔ |", "| L3 | N2 | N3 | hop | 2.8 | 0 | optional | ↔ |")
        p = tmp(text)
        code, out = run(GD / "level-design/scripts/check_level.py", p, "--gdd", D / "gdd", "--systems", D / "systems-map.md")
        self.assertEqual(code, 1)
        self.assertIn("LV3: goal N5 достижим только через optional-связи (L3)", out)

    def test_release_plan_ok(self):
        code, out = run(GD / "release-plan/scripts/check_release_plan.py", FX / "release/ok",
                        "--events", D / "analytics/events.md")
        self.assertEqual(code, 0, out)
        self.assertIn("Итог: PASS", out)

    def test_release_plan_bad(self):
        code, out = run(GD / "release-plan/scripts/check_release_plan.py", FX / "release/bad",
                        "--events", D / "analytics/events.md")
        self.assertEqual(code, 1)
        for rule in ("RP1 CL1: нет владельца", "RP1 CL2: нет даты", "RP1 CL3: Due «скоро»",
                     "FAIL RP2 MS1 page 2027-02-01 позже MS2 demo", "WARN RP2 MS3 (fest): нет даты",
                     "WARN RP2 CL4: Due 2027-04-20 позже релиза", "RP3 store.md SA1", "RP3 store.md SA2",
                     "RP3 launch.md P1", "RP4 d1_retention: нет порога", "RP4 d1_retention: нет адресата",
                     "WARN RP4 d1_retention: нет среди KPI"):
            self.assertIn(rule, out)
        self.assertEqual(run(GD / "release-plan/scripts/check_release_plan.py", FX / "levels")[0], 1)  # нет файлов

    def loc(self, v, *extra):
        f = FX / "loc" / v
        return run(GB / "loc-build/scripts/check_loc.py", f / "tables", "--hud", D / "ux/hud.md", "--unity", f / "unity",
                   "--ink", f / "ink", *extra)

    def test_loc_ok(self):
        code, out = self.loc("ok", "--pseudo", "0.35")
        self.assertEqual(code, 0, out)
        self.assertIn("Итог: PASS", out)
        self.assertIn("строк Ink: 2", out)   # строка и выбор с #id; VAR, ~, -> и комментарии не считаются
        self.assertIn("mt: 1", out)

    def test_loc_bad(self):
        code, out = self.loc("bad", "--pseudo", "0.35")
        self.assertEqual(code, 1)
        for rule in ("LC1 ui.record (hud.md)", "LC1 ink_first_hop.intro_01 (first-hop.ink)", "LC1 ui.dup: ключ повторяется",
                     "LC1 ui.empty: пустое значение", "WARN LC1 ui.unused: нет перевода", "WARN LC2 ui.unused",
                     "LC3 ui.again (ru): 13 символов > max:6", "LC3 ui.pause (pseudo +35%)", "LC4 ui.score_fmt (ru)",
                     'LC5 HUD.uxml: text="Game Over"', 'LC5 Restart.cs: .text = "Try again"',
                     "LC5 first-hop.ink:3: строка с текстом без #id", "LC5 first-hop.ink:4"):
            self.assertIn(rule, out)
        self.assertNotIn("first-hop.ink:2", out)   # строка с #id
        self.assertNotIn("LC3 ui.pause", self.loc("bad")[1])   # без --pseudo длина «Pause» в пределах max:7

    def test_gen_analytics_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            for sub in ("a", "b"):
                code, out = run(GB / "analytics-build/scripts/gen_analytics.py", D / "analytics/events.md", "--out", Path(d, sub))
                self.assertEqual(code, 0, out)
            for name in ("AnalyticsEvents.cs", "AnalyticsLog.cs"):
                self.assertEqual(Path(d, "a", name).read_bytes(), Path(d, "b", name).read_bytes(), name)
            cs = Path(d, "a/AnalyticsEvents.cs").read_bytes()
            self.assertNotIn(b"\r\n", cs)
            self.assertIn(b"public static void JumpPerformed(int jumpIndex, float charge, float secondsSinceStart, bool landed)", cs)
            code, out = run(GB / "analytics-build/scripts/gen_analytics.py", FX / "analytics/events-types.md",
                            "--out", Path(d, "t"), "--no-backend")
            self.assertEqual(code, 0, out)
            cs = Path(d, "t/AnalyticsEvents.cs").read_text(encoding="utf-8")
            self.assertIn("public static void LevelFailed(int levelIndex, string cause, string @event)", cs)
            self.assertIn('<param name="cause">fall,timeout</param>', cs)
            self.assertIn("public static void MenuOpened() =>", cs)
            self.assertFalse(Path(d, "t/AnalyticsLog.cs").exists())

    def test_gen_analytics_bad_param_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            code, out = run(GB / "analytics-build/scripts/gen_analytics.py", FX / "analytics/events-bad.md", "--out", d)
            self.assertEqual(code, 1)
            self.assertIn("«session_index:integer» не разобран", out)
            self.assertEqual(list(Path(d).iterdir()), [])   # неполный AnalyticsEvents.cs не затирает рабочий

    def analytics_project(self, d, caller):
        run(GB / "analytics-build/scripts/gen_analytics.py", D / "analytics/events.md", "--out", d)
        for f in (FX / "analytics" / caller).glob("*.cs"):
            Path(d, f.name).write_bytes(f.read_bytes())

    def test_analytics_calls_ok(self):
        with tempfile.TemporaryDirectory() as d:
            self.analytics_project(d, "ok")
            code, out = run(GB / "analytics-build/scripts/check_analytics_calls.py", d, "--events", D / "analytics/events.md")
            self.assertEqual(code, 0, out)
            self.assertIn("с вызовом: 5", out)
            self.assertIn("согласие выставляется: да", out)
            self.assertIn("Итог: PASS", out)

    def test_analytics_calls_bad(self):
        with tempfile.TemporaryDirectory() as d:
            self.analytics_project(d, "bad")   # AnalyticsLog.cs фикстуры заменяет сгенерированный: Send без Consent
            code, out = run(GB / "analytics-build/scripts/check_analytics_calls.py", d, "--events", D / "analytics/events.md")
            self.assertEqual(code, 1)
            for rule in ("AN1 run_ended: нет вызова", "AN1 spark_collected: нет вызова", 'AN2 RunTelemetry.cs: строка "run_started"',
                         'AN2 RunTelemetry.cs: AnalyticsLog.Send("run_started")', "AN3 RunTelemetry.cs: ключ «player_email»",
                         "WARN AN4: вызовы есть", "WARN AN4 AnalyticsLog.cs: Send не проверяет Consent"):
                self.assertIn(rule, out)
            code, out = run(GB / "analytics-build/scripts/check_analytics_calls.py", d, "--events", FX / "analytics/events-bad.md")
            self.assertEqual(code, 1)
            self.assertIn("AN3 session_started: параметр «user_email»", out)
            self.assertIn("AN1 run_ended: есть в AnalyticsEvents.cs, нет в events.md", out)
            self.assertIn("AN1 session_started: параметры ['sessionIndex', 'build']", out)


class WaveB(unittest.TestCase):
    """Скрипты волны B: позитивная и негативная фикстуры из examples/one-tap-slice/fixtures/."""

    def test_perf_ok(self):
        code, out = run(GB / "perf-check/scripts/compare_perf.py", FX / "perf/2026-09-24-android.md",
                        "--budgets", D / "tech/budgets.md", "--prev", FX / "perf/2026-09-20-android.md")
        self.assertEqual(code, 0, out)
        self.assertIn("Итог: PASS", out)

    def test_perf_bad(self):
        code, out = run(GB / "perf-check/scripts/compare_perf.py", FX / "perf/2026-09-24-editor-bad.md",
                        "--budgets", D / "tech/budgets.md", "--prev", FX / "perf/2026-09-20-android.md")
        self.assertEqual(code, 1)
        for rule in ("FAIL PF2 B1", "FAIL PF1 B3 «Время рестарта»: не замерено", "WARN PF1 B4 «Размер APK»: n/a",
                     "WARN PF1 B9: строка Results без строки", "WARN PF3 B1", "WARN PF3 B2", "WARN PF4 B1: замер в редакторе"):
            self.assertIn(rule, out)
        self.assertNotIn("PF2 B2", out)   # 40 ≤ 50 — регресс, но не провал

    def release_project(self, d, v):
        import shutil
        proj = Path(d, v)
        shutil.copytree(FX / "release-project" / v, proj)
        Path(proj, "Assets/_Project/Audio").mkdir(parents=True)
        Path(proj, "Assets/_Project/Audio/jump.wav").write_bytes(b"RIFF" + bytes(60))
        Path(proj, "Assets/_Project/key_art.png").write_bytes(bytes(600 * 1024))   # > --lfs-min-kb 500
        Path(proj, "Assets/_Project/icon.png").write_bytes(bytes(1000))            # мелкий PNG может быть не в LFS
        return proj

    def test_release_ok(self):
        with tempfile.TemporaryDirectory() as d:
            proj = self.release_project(d, "ok")
            code, out = run(GB / "build-release/scripts/check_release.py", proj, "--changelog", proj / "CHANGELOG.md", "--repo", proj)
            self.assertEqual(code, 0, out)
            self.assertIn("Итог: PASS", out)
            self.assertEqual(run(GB / "build-release/scripts/check_release.py", proj, "--tag", "v1.2.0", "--repo", proj)[0], 0)

    def test_release_bad(self):
        with tempfile.TemporaryDirectory() as d:
            proj = self.release_project(d, "bad")
            code, out = run(GB / "build-release/scripts/check_release.py", proj, "--changelog", proj / "CHANGELOG.md", "--repo", proj)
            self.assertEqual(code, 1)
            for rule in ("RL1 bundleVersion 1.1.0 ≠ 1.2.0", "RL2 .gitignore без Logs/", "RL2 .gitignore без UserSettings/",
                         "RL3 2 бинарных файлов не под LFS (.png, .wav)", "WARN RL4 release.yml: секрет MY_DEPLOY_TOKEN",
                         "RL5 release.yml: development-флаг", "RL5 Assets/_Project/Settings/Release.asset",
                         "RL6 app_build.vdf: нет AppID", "RL6 app_build.vdf: нет DepotID"):
                self.assertIn(rule, out)
            self.assertNotIn("UNITY_LICENSE", out)
            code, out = run(GB / "build-release/scripts/check_release.py", proj, "--repo", FX / "levels")
            self.assertEqual(code, 2)
            self.assertNotIn("Traceback", out)
            self.assertIn("не внутри --repo", out)
            self.assertEqual(run(GB / "build-release/scripts/check_release.py", d)[0], 2)   # не Unity-проект

    def test_glb_ok(self):
        with tempfile.TemporaryDirectory() as d:
            lod = [(f"mdl_lantern_base_lit_LOD{i}", t, (0.5, 1, 0.5), 1) for i, t in enumerate((700, 300, 100))]
            gltf_model(Path(d, "mdl_lantern_base_lit.glb"), lod)
            gltf_model(Path(d, "anim_player_hop.glb"), [("anim_player_hop", 1200, (1, 2, 0.6), 1)], clips={"idle": 0.8, "hop": 0.4})
            for f in ("mdl_lantern_base_lit.glb", "anim_player_hop.glb"):
                code, out = run(GB / "model-build/scripts/check_glb.py", Path(d, f), "--asset-list", FX / "models/asset-list.md")
                self.assertEqual(code, 0, out)
                self.assertIn("Итог: PASS", out)

    def test_glb_bad(self):
        assets = FX / "models/asset-list.md"
        with tempfile.TemporaryDirectory() as d:
            gltf_model(Path(d, "mdl_lantern_base_lit.glb"), [("Cube_LOD0", 900, (0.5, 1, 0.5), 1.5),
                       ("Cube_LOD1", 950, (0.5, 1, 0.5), 1), ("Cube_LOD3", 100, (0.5, 1, 0.5), 1)], materials=2)
            code, out = run(GB / "model-build/scripts/check_glb.py", Path(d, "mdl_lantern_base_lit.glb"), "--asset-list", assets)
            self.assertEqual(code, 1)
            for rule in ("GL1 900 tris > бюджета 800", "GL2 2 материалов > бюджета 1", "GL3 ни узел, ни меш",
                         "GL4 габарит 1 1.5 м", "GL7 LOD-цепочка с дырой: [0, 1, 3]", "GL7 LOD1 (950 tris) не легче LOD0",
                         "WARN GL8 узел «Cube_LOD0»"):
                self.assertIn(rule, out)
            gltf_model(Path(d, "anim_player_hop.glb"), [("anim_player_hop", 1200, (1, 2, 0.6), 1)], clips={"hop": 0.666})
            code, out = run(GB / "model-build/scripts/check_glb.py", Path(d, "anim_player_hop.glb"), "--asset-list", assets)
            self.assertEqual(code, 1)
            self.assertIn("GL5 клипа «idle» нет", out)
            self.assertIn("GL6 клип «hop»: 20.0 кадр.", out)
            gltf_model(Path(d, "mdl_unknown.glb"), [("mdl_unknown", 10, (1, 1, 1), 1)])
            code, out = run(GB / "model-build/scripts/check_glb.py", Path(d, "mdl_unknown.glb"), "--asset-list", assets)
            self.assertEqual(code, 0)
            self.assertIn("WARN GL9", out)
            Path(d, "zip.glb").write_bytes(b"PK\x03\x04 not a glb")
            self.assertEqual(run(GB / "model-build/scripts/check_glb.py", Path(d, "zip.glb"))[0], 2)

    def test_loudness_reference(self):
        """Моно-синус 997 Гц амплитудой −20 dBFS — −23.0 LUFS по BS.1770; короче 400 мс — один блок (short)."""
        sys.path.insert(0, str(GB / "sfx-design/scripts"))
        import loudness
        with tempfile.TemporaryDirectory() as d:
            wav(Path(d, "ref.wav"), 1.0, amp=0.1)
            wav(Path(d, "short.wav"), 0.2, amp=0.1)
            wav(Path(d, "silence.wav"), 1.0, amp=0.0)
            m = loudness.measure(Path(d, "ref.wav"))
            self.assertAlmostEqual(m["lufs"], -23.01, delta=0.1)
            self.assertAlmostEqual(m["peak_db"], -20.0, delta=0.05)
            self.assertFalse(m["short"])
            s = loudness.measure(Path(d, "short.wav"))
            self.assertTrue(s["short"])
            self.assertAlmostEqual(s["lufs"], -23.01, delta=0.3)
            self.assertEqual(loudness.measure(Path(d, "silence.wav"))["lufs"], float("-inf"))
            code, out = run(GB / "sfx-design/scripts/loudness.py", Path(d, "ref.wav"))
            self.assertEqual(code, 0, out)
            self.assertIn("-23.0 LUFS", out)

    def test_loudness_float_wav(self):
        with tempfile.TemporaryDirectory() as d:
            float_wav(Path(d, "f.wav"))
            code, out = run(GB / "sfx-design/scripts/loudness.py", Path(d, "f.wav"))
            self.assertEqual(code, 1)
            self.assertNotIn("Traceback", out)
            self.assertIn("не читается как PCM WAV (unknown format: 3", out)

    def audio_files(self, d, v):
        return run(GB / "sfx-design/scripts/check_audio_files.py", FX / f"audio/{v}/files.md", "--map", FX / "audio/event-map.md",
                   "--bible", FX / "audio/audio-bible.md", "--root", d, "--ffmpeg", Path(d, "no-ffmpeg"))

    def test_audio_files_ok(self):
        with tempfile.TemporaryDirectory() as d:
            wav(Path(d, "Audio/sfx_jump_01.wav"), 0.3, lufs=-16)
            wav(Path(d, "Audio/sfx_land_01.wav"), 1.0, lufs=-16)
            wav(Path(d, "Audio/sfx_land_02.wav"), 1.0, lufs=-16)
            code, out = self.audio_files(d, "ok")
            self.assertEqual(code, 0, out)
            self.assertIn("Итог: PASS", out)
            self.assertIn("sfx_jump_01.wav: -16.0 LUFS (short)", out)
            self.assertIn("true peak: нет ffmpeg", out)   # --ffmpeg на несуществующий файл — sample peak
            files = tmp((FX / "audio/ok/files.md").read_text(encoding="utf-8").replace(
                "| synth | own | — | gen_sfx.py |", "| made | own | — | Anton |", 1))
            code, out = run(GB / "sfx-design/scripts/check_audio_files.py", files, "--map", FX / "audio/event-map.md",
                            "--bible", FX / "audio/audio-bible.md", "--root", d, "--ffmpeg", Path(d, "no-ffmpeg"))
            self.assertEqual(code, 0, out)   # made + own — свой файл, URL не нужен

    def test_audio_files_bad(self):
        with tempfile.TemporaryDirectory() as d:
            wav(Path(d, "Audio/ph_land.wav"), 1.0, lufs=-16, sr=44100)
            wav(Path(d, "Audio/sfx_loud.wav"), 1.0, amp=1.0)
            float_wav(Path(d, "Audio/sfx_float.wav"))
            code, out = self.audio_files(d, "bad")
            self.assertEqual(code, 1)
            self.assertNotIn("Traceback", out)
            for rule in ("AF1 event:/SFX/Player/Jump: нет файла", "AF1 Audio/sfx_missing.wav: файла нет",
                         "AF2 event:/SFX/Player/Land: файлов 1 < вариаций 2", "AF3 Audio/ph_land.wav: 44100 Hz",
                         "AF3 Audio/sfx_float.wav: не читается как PCM WAV", "AF4 Audio/sfx_loud.wav: -3.0 LUFS",
                         "AF4 Audio/sfx_loud.wav: sample peak -0.0 > -1", "AF5 Audio/ph_land.wav: источник «cc0»",
                         "AF6 Audio/ph_land.wav"):
                self.assertIn(rule, out)
            self.assertNotIn("snapshot:/Dead", out)   # снапшоту файл не нужен

    def music(self, d, v):
        return run(GB / "music-build/scripts/check_music.py", FX / f"music/{v}.md", "--bible", FX / "audio/audio-bible.md",
                   "--root", d, "--files", FX / "music/files.md")

    def test_music_ok(self):
        with tempfile.TemporaryDirectory() as d:
            for f in ("mus_run_pad", "mus_run_bells", "mus_dead_pad"):
                wav(Path(d, f"Music/{f}.wav"), lufs=-19, frames=96000, freq=220.0)
            code, out = self.music(d, "ok")
            self.assertEqual(code, 0, out)
            self.assertIn("Итог: PASS", out)

    def test_music_bad(self):
        with tempfile.TemporaryDirectory() as d:
            wav(Path(d, "Music/mus_run_pad.wav"), lufs=-19, frames=96000, freq=220.0)
            wav(Path(d, "Music/mus_run_short.wav"), lufs=-19, frames=48000, freq=220.0, sr=44100)
            wav(Path(d, "Music/mus_run_loud.wav"), amp=1.0, frames=72000, freq=220.0)
            code, out = self.music(d, "bad")
            self.assertEqual(code, 1)
            for rule in ("MU1 состояние «dead»", "MU2 mus_run_main: Loop 90000", "MU2 mus_run_main: Music/mus_run_short.wav длиной 48000",
                         "MU3 mus_run_main: Music/mus_run_short.wav 44100 Hz", "MU3 mus_run_main: стема Music/mus_run_missing.wav нет",
                         "MU3 mus_run_main: стемы разной длины", "MU4 mus_run_loud", "MU5 mus_run_main: переход «плавно»",
                         "WARN MU6 Music/mus_run_loud.wav"):
                self.assertIn(rule, out)
            self.assertNotIn("MU2 mus_run_loud", out)   # 3/4: 72000 = 48000 × 60 / 120 × 3
            self.assertNotIn("MU5 mus_run_loud", out)

    def test_music_float_stem(self):
        with tempfile.TemporaryDirectory() as d:
            float_wav(Path(d, "Music/f.wav"), n=96000)
            cues = tmp("""
                ## Cues
                | Cue | State | BPM | Meter | Key | Bars | Loop (samples) | Stems | Transition |
                |---|---|---|---|---|---|---|---|---|
                | c | run, dead | 120 | 4/4 | Am | 1 | 96000 | Music/f.wav | 1 bar |
                """)
            code, out = run(GB / "music-build/scripts/check_music.py", cues, "--bible", FX / "audio/audio-bible.md", "--root", d)
            self.assertEqual(code, 1)
            self.assertNotIn("Traceback", out)
            self.assertIn("MU3 c: Music/f.wav не читается", out)

    def fake_project(self, d, *packages):
        proj = Path(d, "p")
        Path(proj, "ProjectSettings").mkdir(parents=True)
        Path(proj, "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 6000.0.99f1\n", encoding="utf-8")
        Path(proj, "Packages").mkdir()
        deps = {"com.coplaydev.unity-mcp": "git+https://x", "com.unity.inputsystem": "1.11.0", "com.unity.test-framework": "1.6.0"}
        deps.update({p: "1.0.0" for p in packages})
        Path(proj, "Packages/manifest.json").write_text(
            json.dumps({"dependencies": deps, "testables": ["com.unity.inputsystem"]}), encoding="utf-8")
        return proj

    def test_preflight_for_loc(self):
        with tempfile.TemporaryDirectory() as d:
            code, out = run(GB / "slice-build/scripts/preflight.py", self.fake_project(d), "--design", D, "--for", "loc")
            self.assertEqual(code, 0)
            self.assertIn("Задача: loc", out)
            self.assertIn("пакет Localization (com.unity.localization)", out)
            self.assertIn("Рекомендуемый режим: plan", out)
        with tempfile.TemporaryDirectory() as d:
            proj = self.fake_project(d, "com.unity.localization")
            code, out = run(GB / "slice-build/scripts/preflight.py", proj, "--design", D, "--for", "loc")
            self.assertIn("Пакет Localization: 1.0.0", out)
            self.assertNotIn("пакет Localization (com.unity.localization)", out)

    def test_preflight_for_tools_without_unity(self):
        """model / sfx / music не требуют Unity-проекта; режим зависит только от инструментов этой машины."""
        with tempfile.TemporaryDirectory() as d:
            for task, tools in (("model", ["blender"]), ("sfx", ["ffmpeg", "sox"]), ("music", ["fluidsynth", "soundfont"])):
                code, out = run(GB / "slice-build/scripts/preflight.py", Path(d, "nope"), "--design", Path(d, "nope"), "--for", task)
                self.assertEqual(code, 0)
                self.assertIn(f"Задача: {task}", out)
                self.assertNotIn("  - Unity-проект", out)
                lacking = any(f"  - {t} — " in out for t in tools)
                self.assertIn(f"Рекомендуемый режим: {'plan' if lacking else 'live'}", out)
            code, out = run(GB / "slice-build/scripts/preflight.py", Path(d, "nope"), "--for", "anim")
            self.assertIn("  - Unity-проект", out)   # anim без проекта — plan
            self.assertIn("Рекомендуемый режим: plan", out)
            self.assertEqual(run(GB / "slice-build/scripts/preflight.py", "--for", "bogus")[0], 2)


class FmodUnitySetup(unittest.TestCase):
    """fmod_unity_setup.py без Unity: отказы с кодом 2 и dry-run. Живой прогон — CHANGELOG 0.7.3."""
    S = GB / "fmod-sync/scripts/fmod_unity_setup.py"

    def layout(self, d, fmod_plugin=True, build=False):
        proj, studio = Path(d, "unity/proj"), Path(d, "fmod/p")
        Path(proj, "ProjectSettings").mkdir(parents=True)
        Path(proj, "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 6000.0.99f1\n", encoding="utf-8")
        if fmod_plugin:
            Path(proj, "Assets/Plugins/FMOD/src").mkdir(parents=True)
        studio.mkdir(parents=True)
        Path(studio, "p.fspro").write_text("<objects/>", encoding="utf-8")
        if build:
            Path(studio, "Build").mkdir()
        unity = Path(d, "Unity.exe")
        unity.write_bytes(b"")
        return proj, studio / "p.fspro", unity

    def test_dry_run(self):
        with tempfile.TemporaryDirectory() as d:
            proj, fspro, unity = self.layout(d)
            code, out = run(self.S, proj, "--fspro", fspro, "--unity", unity, "--dry-run")
            self.assertEqual(code, 0, out)
            self.assertIn("Проект Studio: ../../fmod/p/p.fspro · банки: ../../fmod/p/Build", out)
            self.assertIn("WARN: в проекте Studio нет Build/", out)
            self.assertFalse(Path(proj, "Assets/_GdFmodSetup").exists())

    def test_refusals(self):
        with tempfile.TemporaryDirectory() as d:
            proj, fspro, unity = self.layout(d, fmod_plugin=False, build=True)
            code, out = run(self.S, proj, "--fspro", fspro, "--unity", unity)
            self.assertEqual(code, 2)
            self.assertIn("FMOD for Unity не импортирован", out)
            Path(proj, "Assets/Plugins/FMOD/src").mkdir(parents=True)
            self.assertIn("нет файла проекта FMOD Studio", run(self.S, proj, "--fspro", Path(d, "x.fspro"), "--unity", unity)[1])
            self.assertIn("не найден", run(self.S, proj, "--fspro", fspro, "--unity", Path(d, "nope.exe"))[1])
            Path(proj, "Temp").mkdir()
            Path(proj, "Temp/UnityLockfile").write_bytes(b"")
            code, out = run(self.S, proj, "--fspro", fspro, "--unity", unity)
            self.assertEqual(code, 2)
            self.assertIn("редактор открыт", out)
            self.assertEqual(run(self.S, d, "--fspro", fspro)[0], 2)   # не Unity-проект

    def test_editor_script_template(self):
        sys.path.insert(0, str(GB / "fmod-sync/scripts"))
        import fmod_unity_setup as f
        cs = f.render_cs("../../FMOD/P/p.fspro")
        self.assertIn('const string Project = "../../FMOD/P/p.fspro";', cs)
        self.assertIn('const string Banks = "../../FMOD/P/Build";', cs)
        self.assertIn("StagingSystem.Startup()", cs)
        self.assertIn("EventManager.RefreshBanks()", cs)

class Repo(unittest.TestCase):
    def test_check_plugins(self):
        code, out = run(ROOT / "tools/check_plugins.py")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
