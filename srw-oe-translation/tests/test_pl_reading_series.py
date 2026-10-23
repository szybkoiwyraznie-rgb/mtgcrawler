"""PL story reader binds displayed prose only to accepted Polish source rows."""
import json
from pathlib import Path
import re
import shutil
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
        cls.polish = Path(cls.tmp.name) / "materialized-pl"
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
        self.assertIn("wyłącznie z polskich pól pakietu PL", text)
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

    def test_all_late_episodes_22_through_34_build_and_blank_prose_never_falls_back_to_en(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for episode in (22, 25, 33, 34):
                audit = build_episode(ROOT / "pakiet_EN", self.polish, episode,
                                      out / f"ep{episode:02d}.md", out / f"audit{episode:02d}.json")
                self.assertGreater(audit["prose_total"], 0)
            # Clear a single prose row in a private copy to ensure missing PL never falls back to EN.
            incomplete = out / "incomplete-pl"
            shutil.copytree(self.polish, incomplete)
            lines = (incomplete / "00_dialogue.jsonl").read_text(encoding="utf-8").splitlines()
            cleared = []
            dropped = False
            for line in lines:
                row = json.loads(line)
                if not dropped and row.get("kind") == "dialogue" and (row.get("pl") or "").strip():
                    row["pl"] = ""
                    dropped = True
                cleared.append(json.dumps(row, ensure_ascii=False))
            self.assertTrue(dropped)
            (incomplete / "00_dialogue.jsonl").write_text("\n".join(cleared) + "\n", encoding="utf-8")
            missing_md = out / "missing.md"
            with self.assertRaisesRegex(ValueError, "Missing Polish reading text"):
                build_episode(ROOT / "pakiet_EN", incomplete, 0, missing_md, out / "missing.audit.json")
            self.assertFalse(missing_md.exists())

    def test_pl5_source_declares_complete_story_coverage(self):
        receipt = json.loads((ROOT / "pakiet_PL/snapshot.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["source_return"]["name"], "PL5.zip")
        self.assertEqual(receipt["merge_provenance"]["source_archive"]["story_episodes"], "00-34")
        self.assertTrue(receipt["merge_provenance"]["source_archive"]["simulator_included"])
        self.assertEqual(receipt["merge_provenance"]["scenes_all_36"]["visible_elements"], 49146)
        self.assertEqual(receipt["merge_provenance"]["scenes_all_36"]["filled_elements"], 49144)
        self.assertEqual(receipt["merge_provenance"]["battle_quotes"]["filled_elements"], 19841)


if __name__ == "__main__":
    unittest.main()
