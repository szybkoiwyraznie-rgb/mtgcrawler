"""PL4 story reader binds displayed prose only to accepted Polish source rows."""
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pl_release_package as R
from build_pl_reading_series import build_episode, PolishStorySource
from build_reading_script import render_entry


class PLReadingSeriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.polish = Path(cls.tmp.name) / "materialized-pl4"
        R.materialize(ROOT / "pakiet_EN", ROOT / "pakiet_PL", cls.polish)

    def test_dlc_mission_titles_are_in_their_source_story_episodes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            fourth = build_episode(ROOT / "pakiet_EN", self.polish, 4,
                                   out / "ep04.md", out / "ep04.audit.json")
            fifth = build_episode(ROOT / "pakiet_EN", self.polish, 5,
                                  out / "ep05.md", out / "ep05.audit.json")
            ep4 = (out / "ep04.md").read_text(encoding="utf-8")
            ep5 = (out / "ep05.md").read_text(encoding="utf-8")
        self.assertEqual(ep4.count("## Lelouch buntownik"), 3)  # base + two source variants
        self.assertIn("## Biały rycerz", ep5)
        self.assertEqual(fourth["prose_total"], 1209)
        self.assertEqual(fifth["prose_total"], 1239)
        self.assertTrue(all(span["binding"] for span in fourth["rendered_blocks"] if span.get("row")))

    def test_audited_episode_blocks_are_exact_pl_rows_and_no_english_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            audit = build_episode(ROOT / "pakiet_EN", self.polish, 4,
                                  out / "ep04.md", out / "ep04.audit.json")
            text = (out / "ep04.md").read_text(encoding="utf-8")
            source = PolishStorySource(ROOT / "pakiet_EN", self.polish, 4)
        self.assertIn("wyłącznie z polskich pól pakietu PL4", text)
        self.assertEqual(audit["prose_total"], 1209)
        checked = 0
        for block in audit["rendered_blocks"]:
            if "row" not in block:
                continue
            raw = source.by_id[block["row"]]
            self.assertEqual(block["binding"], source.bindings[raw["id"]])
            visible = text[block["start"]:block["end"]].rstrip("\n")
            expected = render_entry(source.make_entry(raw), "story", 3)
            if raw["kind"] in ("dialogue", "narration"):
                expected = re.sub(r"(?m)(^|\n\n)(\([^\n]*\))(?=\n\n|$)",
                                  lambda m: m.group(1) + "*" + m.group(2) + "*", expected)
            self.assertEqual(visible, expected, raw["id"])
            checked += 1
        self.assertGreater(checked, audit["prose_total"])

    def test_untranslated_episodes_22_and_23_are_refused_without_en_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for episode in (22, 23):
                md = out / f"ep{episode:02d}.md"
                with self.subTest(episode=episode):
                    with self.assertRaisesRegex(ValueError, "Missing Polish reading text"):
                        build_episode(ROOT / "pakiet_EN", self.polish, episode, md,
                                      out / f"audit{episode:02d}.json")
                    self.assertFalse(md.exists())

    def test_pl4_source_declares_current_story_coverage(self):
        receipt = json.loads((ROOT / "pakiet_PL/snapshot.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["merge_provenance"]["source_archive"]["story_episodes"], "00-21")
        self.assertEqual(receipt["merge_provenance"]["episode_00_21"]["visible_elements"], 28079)
        self.assertEqual(receipt["merge_provenance"]["episode_00_21"]["filled_elements"], 28078)
        self.assertEqual(receipt["merge_provenance"]["episode_00_21"]["only_empty"]["source_row_id"],
                         "dlg:eventP01.EDAT/DL105_40.bin:696")


if __name__ == "__main__":
    unittest.main()
