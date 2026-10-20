"""Three follow-up screenshot corrections stay source-bound and narrowly scoped."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pl_release_package as R
import pl_text
import translation_check as C


class SevenScreenCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan_path = ROOT / "config/pl/ui-seven-2026-10-20.json"
        cls.plan = json.loads(cls.plan_path.read_text(encoding="utf-8"))
        cls.source_rows, _ = R.I.load_rows(ROOT / "pakiet_EN")
        cls.source = {row["id"]: row for row in cls.source_rows}
        cls.snapshot = [json.loads(line) for line in
                        (ROOT / "pakiet_PL/polish.jsonl").read_text(encoding="utf-8").splitlines()]
        cls.entries = {entry["source_sha256"]: entry for entry in cls.snapshot}

    def test_five_edits_are_source_bound_control_safe_and_materialized(self):
        self.assertEqual(len(self.plan["changes"]), 5)
        for edit in self.plan["changes"]:
            with self.subTest(id=edit["id"]):
                row = self.source[edit["id"]]
                binding = R.binding(row)
                self.assertEqual(binding, edit["source_sha256"])
                entry = self.entries[binding]
                self.assertEqual(entry["file"], edit["file"])
                self.assertEqual(entry["pl"], edit["after"])
                self.assertEqual(C.tokens(edit["before"]), C.tokens(edit["after"]))
                self.assertEqual(edit["before"].count("\n"), edit["after"].count("\n"))
                for line in edit["after"].split("\n"):
                    self.assertLessEqual(pl_text.display_width(C.TOKEN_RE.sub("", line)),
                                         edit["max_cells"])
                self.assertEqual(pl_text.decode(pl_text.encode(edit["after"])), edit["after"])

    def test_unit_stats_fixed_slot_caption_is_compacted_for_both_aliases(self):
        edits = [e for e in self.plan["changes"] if e["id"].startswith("sysmes:")]
        self.assertEqual(len(edits), 2)
        self.assertEqual({e["after"] for e in edits}, {"Stat."})
        self.assertEqual({self.source[e["id"]]["jp"] for e in edits}, {"ユニット能力"})
        self.assertEqual({self.source[e["id"]]["source"]["member"] for e in edits}, {"sysmes.bin"})

    def test_trust_effect_removes_only_the_duplicate_hp_marker_in_all_aliases(self):
        edits = [e for e in self.plan["changes"] if e["id"].startswith("spirit:")]
        self.assertEqual({e["id"].rsplit(":", 1)[1] for e in edits}, {"9412", "9692", "9972"})
        for edit in edits:
            with self.subTest(id=edit["id"]):
                old = edit["before"]
                new = edit["after"]
                self.assertEqual(old.count("HP+HP5%s"), 1)
                self.assertEqual(new.count("HP+HP5%s"), 0)
                self.assertEqual(new.count("HP+5%s"), 1)
                self.assertEqual(new.replace("HP+5%s", "HP+HP5%s", 1), old)

    def test_snapshot_records_this_owner_correction_without_runtime_claim(self):
        manifest = json.loads((ROOT / "pakiet_PL/snapshot.json").read_text(encoding="utf-8"))
        history = manifest["owner_ui_corrections"]
        latest = history[-1]
        self.assertEqual(latest["plan"], self.plan_path.name)
        self.assertEqual(latest["sha256"], hashlib.sha256(self.plan_path.read_bytes()).hexdigest())
        self.assertEqual(latest["entries"], len(self.plan["changes"]))
        self.assertFalse(latest["runtime_tested"])


if __name__ == "__main__":
    unittest.main()
