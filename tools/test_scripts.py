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
    f.write(textwrap.dedent(text))
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
        self.assertNotIn("WARN T-hop-02", out)  # T-ID из [Category] распознан
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


class Repo(unittest.TestCase):
    def test_check_plugins(self):
        code, out = run(ROOT / "tools/check_plugins.py")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
