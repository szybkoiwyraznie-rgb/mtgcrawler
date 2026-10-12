"""Synthetic tests for tools/name_map.py (no game data)."""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import name_map as NM  # noqa: E402


def write_jsonl(path: Path, keys):
    with path.open("w", encoding="utf-8") as handle:
        for key in keys:
            handle.write(json.dumps({"key": key, "text": "x"}) + "\n")


def name_slot_pac(key, name, marker=True, filler=b"\x00" * 8):
    """Blob with one config-style name slot: key u32 at q, slot at q-0x14, marker at q+0x0A."""
    head = filler + name.encode("cp932") + b"\x00" + b"\x00" * (4 - 0)
    # pad so that q - 0x14 is the slot start
    q = 0x14
    blob = bytearray(b"\x11" * (q + 0x10))
    blob[q - 0x14:q - 0x14 + len(name.encode("cp932")) + 1] = name.encode("cp932") + b"\x00"
    struct.pack_into("<I", blob, q, key)
    struct.pack_into("<H", blob, q + 0x0A, 0x6401 if marker else 0x0000)
    return bytes(blob) + head


class UniverseTest(unittest.TestCase):
    def test_kinds_are_taken_from_the_file_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            dialogue = Path(tmp, "dialogue.jsonl")
            quotes = Path(tmp, "battle_quotes.jsonl")
            write_jsonl(dialogue, [10, 10, 20])
            write_jsonl(quotes, [10, 30])
            universe = NM.load_universe([dialogue, quotes])
        self.assertEqual(universe[10], {"dialogue_lines": 2, "quote_records": 1, "other_texts": 0})
        self.assertEqual(universe[20]["dialogue_lines"], 1)
        self.assertEqual(universe[30]["quote_records"], 1)

    def test_rows_without_a_key_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "dialogue.jsonl")
            path.write_text('{"text": "no key"}\n\n{"key": 5, "text": "x"}\n', encoding="utf-8")
            universe = NM.load_universe([path])
        self.assertEqual(list(universe), [5])


class ResolveTest(unittest.TestCase):
    def universe(self):
        return {10: {"dialogue_lines": 1, "quote_records": 2, "other_texts": 0},
                20: {"dialogue_lines": 0, "quote_records": 3, "other_texts": 0},
                30: {"dialogue_lines": 0, "quote_records": 4, "other_texts": 0},
                40: {"dialogue_lines": 2, "quote_records": 0, "other_texts": 0}}

    def test_charalist_wins_and_dictionary_adds_voice_and_series(self):
        charalist = {10: {"key": 10, "name_short": "剣", "name_full": "大牙剣", "name_narrow": "剣"}}
        dictionary = {10: {"key": 10, "name": "大牙剣", "nickname": "剣", "series": "SER",
                           "voice_actor": "VA", "entry": ""}}
        row = {r["key"]: r for r in NM.resolve(self.universe(), charalist, dictionary)}[10]
        self.assertEqual((row["short"], row["full"], row["name_narrow"]), ("剣", "大牙剣", "剣"))
        self.assertEqual((row["series"], row["voice_actor"], row["nickname"]), ("SER", "VA", "剣"))
        self.assertEqual(row["source"], "charalist")
        self.assertEqual(row["conflicts"], [])

    def test_empty_charalist_full_name_falls_back_to_the_dictionary(self):
        charalist = {10: {"key": 10, "name_short": "ルドルフ", "name_full": "", "name_narrow": ""}}
        dictionary = {10: {"key": 10, "name": "ルドルフ・ゲアハルト・ツェッペリンⅢ世",
                           "nickname": "ルドルフ", "series": "SER", "voice_actor": "VA", "entry": ""}}
        row = {r["key"]: r for r in NM.resolve(self.universe(), charalist, dictionary)}[10]
        self.assertEqual(row["full"], "ルドルフ・ゲアハルト・ツェッペリンⅢ世")
        self.assertEqual(row["source"], "charalist")

    def test_dictionary_only_key_is_marked_as_such(self):
        dictionary = {20: {"key": 20, "name": "NoData", "nickname": "NoData", "series": "SER",
                           "voice_actor": "", "entry": ""}}
        row = {r["key"]: r for r in NM.resolve(self.universe(), {}, dictionary)}[20]
        self.assertEqual(row["source"], "dictionary")
        self.assertEqual(row["full"], "NoData")
        self.assertIsNone(row["name_narrow"])

    def test_unresolved_key_has_no_source(self):
        rows = {r["key"]: r for r in NM.resolve(self.universe(), {}, {})}
        self.assertEqual(rows[30]["source"], None)
        self.assertEqual(rows[30]["quote_records"], 4)

    def test_width_differences_are_not_reported_as_conflicts(self):
        charalist = {10: {"key": 10, "name_short": "ＤＧ細胞", "name_full": "ＤＧ細胞", "name_narrow": ""}}
        dictionary = {10: {"key": 10, "name": "DG細胞", "nickname": "DG細胞", "series": "",
                           "voice_actor": "", "entry": ""}}
        row = {r["key"]: r for r in NM.resolve(self.universe(), charalist, dictionary)}[10]
        self.assertEqual(row["conflicts"], [])

    def test_real_difference_is_reported(self):
        charalist = {10: {"key": 10, "name_short": "勇者ラムネス", "name_full": "勇者ラムネス",
                          "name_narrow": ""}}
        dictionary = {10: {"key": 10, "name": "勇者ラムネス（馬場ラムネ）", "nickname": "ラムネス",
                           "series": "", "voice_actor": "", "entry": ""}}
        row = {r["key"]: r for r in NM.resolve(self.universe(), charalist, dictionary)}[10]
        self.assertEqual([c["field"] for c in row["conflicts"]], ["full", "short"])


class CoverageTest(unittest.TestCase):
    def test_coverage_counts_sources_and_unresolved_records(self):
        rows = [{"key": 1, "source": "charalist", "short": "a", "full": "a", "voice_actor": "v",
                 "series": "s", "dialogue_lines": 5, "quote_records": 1, "other_texts": 0,
                 "conflicts": []},
                {"key": 2, "source": None, "short": None, "full": None, "voice_actor": None,
                 "series": None, "dialogue_lines": 0, "quote_records": 7, "other_texts": 0,
                 "conflicts": []}]
        cov = NM.coverage(rows)
        self.assertEqual(cov["keys"], 2)
        self.assertEqual(cov["by_source"], {"charalist": 1, "none": 1})
        self.assertEqual(cov["unresolved"], [2])
        self.assertEqual(cov["unresolved_records"]["quote_records"], 7)
        self.assertEqual(cov["totals"]["quote"], 8)
        self.assertEqual(cov["with_short_name"], 1)

    def test_tsv_has_one_line_per_row(self):
        rows = [{"key": 1, "short": "a", "full": "b", "voice_actor": "", "series": "", "source": None,
                 "dialogue_lines": 0, "quote_records": 0, "conflicts": [{"field": "full"}]}]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp, "m.tsv")
            NM.write_tsv(out, rows)
            lines = out.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0].split("\t")[0], "key")
        self.assertEqual(lines[1].split("\t")[-1], "full")


class VerifyConfigTest(unittest.TestCase):
    def test_marker_slots_are_compared_unmarked_ignored(self):
        rows = [{"key": 10, "short": "剣"}, {"key": 20, "short": "連邦軍士官"},
                {"key": 30, "short": "ゼロ"}]
        pacs = {"config00.pac": name_slot_pac(10, "剣") + name_slot_pac(20, "連邦士官")
                + name_slot_pac(30, "ゼロ"), }
        # one unmarked slot for key 40 which is not in the universe at all
        result = NM.verify_config_markers(rows, pacs)
        self.assertEqual(result["agree"], 2)
        self.assertEqual(result["disagree"], 1)
        self.assertEqual(result["examples"][0]["slot"], "連邦士官")

    def test_unmarked_and_unknown_keys_are_counted_separately(self):
        rows = [{"key": 10, "short": "剣"}]
        pacs = {"config00.pac": name_slot_pac(10, "剣", marker=False) + name_slot_pac(99, "X")}
        result = NM.verify_config_markers(rows, pacs)
        self.assertEqual((result["agree"], result["disagree"]), (0, 0))
        self.assertEqual(result["unmarked_slots_ignored"], 1)


if __name__ == "__main__":
    unittest.main()
