"""Synthetic tests for tools/mission_text.py (no game data)."""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mission_text as MT  # noqa: E402


def raw(text: str) -> bytes:
    """The bytes of one NUL-terminated CP932 slot."""
    return text.encode("cp932") + b"\x00"


def pac(*items):
    """A config .pac index: entries of 0x28 B from 0x10, data from 0x800.

    ``items`` are (name, blob) pairs; returns the archive bytes.
    """
    data_start = 0x800
    head = bytearray(data_start)
    struct.pack_into("<I", head, 0, data_start)
    body = b""
    pos = data_start
    for index, (name, blob) in enumerate(items):
        base = 0x10 + index * 0x28
        struct.pack_into("<2I", head, base, pos, len(blob))
        head[base + 8:base + 8 + len(name)] = name.encode("ascii")
        body += blob
        pos += len(blob)
    return bytes(head) + body


def bgmlist(records):
    """bgmlist<NN>.bin: header 0, stride 192, slots +20 title, +84 narrow, +144 series."""
    blob = b""
    for title, narrow, series in records:
        rec = bytearray(192)
        for offset, text in ((20, title), (84, narrow), (144, series)):
            data = raw(text)
            rec[offset:offset + len(data)] = data
        blob += bytes(rec)
    return blob


def ext_dat(note, title):
    """*_ext.dat: one 388-B record, slots +24 note_a, +184 note_b, +344 title."""
    rec = bytearray(388)
    for offset, text in ((24, note), (184, note), (344, title)):
        data = raw(text)
        rec[offset:offset + len(data)] = data
    return bytes(rec)


class DecodeTests(unittest.TestCase):
    def test_japanese_text_decodes(self):
        text, has_cjk = MT.decode("アクシズからの撤退".encode("cp932"))
        self.assertEqual(text, "アクシズからの撤退")
        self.assertTrue(has_cjk)

    def test_ascii_only_text_has_no_cjk(self):
        text, has_cjk = MT.decode(b"SCENE 01")
        self.assertEqual(text, "SCENE 01")
        self.assertFalse(has_cjk)

    def test_private_use_bytes_are_rejected(self):
        text, has_cjk = MT.decode(b"\xf0\x40\xf0\x41")
        self.assertIsNone(text)
        self.assertFalse(has_cjk)

    def test_control_bytes_are_rejected(self):
        text, _ = MT.decode(b"\x01\x02title")
        self.assertIsNone(text)

    def test_newline_is_allowed(self):
        text, _ = MT.decode("19話\nアクシズ".encode("cp932"))
        self.assertIn("\n", text)


class KindTests(unittest.TestCase):
    def test_prefix_and_suffix_both_match(self):
        self.assertEqual(MT.kind_for("milstP03.bin", "config"), "mission_title")
        self.assertEqual(MT.kind_for("DL100_01_ext.dat", "event"), "mission_note")

    def test_family_must_agree(self):
        self.assertIsNone(MT.kind_for("milstP03.bin", "event"))
        self.assertIsNone(MT.kind_for("DL100_01_ext.dat", "config"))

    def test_unknown_member(self):
        self.assertIsNone(MT.kind_for("srwDL_Item00.bin", "config"))


class ParseMemberTests(unittest.TestCase):
    def test_bgmlist_slots_and_spans(self):
        rows = MT.parse_member("bgmlist00.bin", bgmlist([("戦闘", "ｾﾝｿｳ", "シリーズA")]), "bgm_title")
        self.assertEqual(len(rows), 1)
        slots = {s["role"]: s for s in rows[0]["slots"]}
        self.assertEqual(slots["title"]["span"], 64)
        self.assertEqual(slots["title_narrow"]["span"], 60)
        self.assertEqual(slots["series"]["span"], 48)
        self.assertEqual(slots["title"]["text"], "戦闘")
        self.assertTrue(slots["title"]["has_cjk"])
        self.assertEqual(slots["title"]["bytes"], 4)

    def test_ext_dat_is_one_record_with_duplicate_notes(self):
        rows = MT.parse_member("X_ext.dat", ext_dat("母艦が変わります", "19話\n撤退"), "mission_note")
        self.assertEqual(len(rows), 1)
        slots = {s["role"]: s for s in rows[0]["slots"]}
        self.assertEqual(slots["note_a"]["text"], slots["note_b"]["text"])
        self.assertEqual(slots["note_a"]["span"], 160)
        self.assertEqual(slots["title"]["span"], 44)
        self.assertIn("19話", slots["title"]["text"])

    def test_every_record_of_a_stride_is_read(self):
        blob = bgmlist([("A", "a", "s1"), ("B", "b", "s2"), ("C", "c", "s3")])
        rows = MT.parse_member("bgmlist00.bin", blob, "bgm_title")
        self.assertEqual([r["offset"] for r in rows], [0, 192, 384])
        self.assertEqual([r["slots"][0]["text"] for r in rows], ["A", "B", "C"])

    def test_short_member_is_skipped(self):
        self.assertEqual(MT.parse_member("bgmlist00.bin", b"\x00" * 100, "bgm_title"), [])

    def test_map_name_header_is_honoured(self):
        blob = bytearray(16 + 2 * 160)
        blob[16:16 + len(raw("コロニー"))] = raw("コロニー")
        blob[176:176 + len(raw("月"))] = raw("月")
        rows = MT.parse_member("srwDL_Map_S.bin", bytes(blob), "map_name")
        self.assertEqual([r["offset"] for r in rows], [16, 176])
        self.assertEqual(rows[1]["slots"][0]["text"], "月")

    def test_bg2dlist_header_holds_the_count_word(self):
        blob = struct.pack("<I", 1) + raw("赤宇宙") + b"\x00" * (112 - len(raw("赤宇宙")))
        rows = MT.parse_member("bg2dlist.bin", blob, "bg_name")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["slots"][0]["text"], "赤宇宙")


class CollectTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, members_by_file, errors=()):
        def fake_read_members(path):
            if path.name in errors:
                raise ValueError("boom")
            return members_by_file.get(path.name, [])

        return MT.collect(self.root, read_members=fake_read_members)

    def test_config_pac_subfiles_are_read(self):
        self.root.joinpath("config00.cpk").write_bytes(b"x")
        archive = pac(("bgmlist00.bin", bgmlist([("戦闘", "ｾﾝｿｳ", "シリーズ")])),
                      ("srwDL_Item00.bin", b"not text"))
        rows, errors = self._run({"config00.cpk": [("config00.pac", archive)]})
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "bgm_title")
        self.assertEqual(rows[0]["member"], "bgmlist00.bin")

    def test_event_dat_members_are_read(self):
        self.root.joinpath("eventP00.cpk").write_bytes(b"x")
        rows, errors = self._run({"eventP00.cpk": [("DL100_01_ext.dat", ext_dat("強制出撃します", "19話\nアクシズ")),
                                                   ("DL100_01_Entry.dat", b"\x00" * 64)]})
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "mission_note")

    def test_unreadable_container_is_reported_not_fatal(self):
        self.root.joinpath("config00.cpk").write_bytes(b"x")
        rows, errors = self._run({}, errors=("config00.cpk",))
        self.assertEqual(rows, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("ValueError", errors[0])

    def test_non_container_files_are_ignored(self):
        self.root.joinpath("readme.txt").write_text("hi", encoding="utf-8")
        rows, errors = self._run({})
        self.assertEqual((rows, errors), ([], []))


class SummariseTests(unittest.TestCase):
    def test_counts_filled_slots_and_spans(self):
        rows = [
            {"kind": "bgm_title", "slots": [
                {"role": "title", "span": 64, "bytes": 6, "text": "戦闘"},
                {"role": "title_narrow", "span": 60, "bytes": 0, "text": ""},
                {"role": "series", "span": 48, "bytes": 0, "text": None}]},
            {"kind": "bgm_title", "slots": [
                {"role": "title", "span": 64, "bytes": 4, "text": "街"},
                {"role": "title_narrow", "span": 60, "bytes": 2, "text": "a"},
                {"role": "series", "span": 48, "bytes": 0, "text": ""}]},
        ]
        summary = MT.summarise(rows)
        self.assertEqual(summary["rows"], 2)
        self.assertEqual(summary["per_kind"]["bgm_title"]["filled_slots"], 3)
        self.assertEqual(summary["per_kind"]["bgm_title"]["max_bytes"], 6)
        self.assertEqual(summary["per_role"]["title"]["filled"], 2)
        self.assertEqual(summary["per_role"]["title"]["max_span"], 64)
        self.assertEqual(summary["per_role"]["series"]["filled"], 0)


class MainTests(unittest.TestCase):
    def test_main_writes_jsonl_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            drive = root / "drive"
            drive.mkdir()
            drive.joinpath("config00.cpk").write_bytes(b"x")
            record = bytearray(128)
            title = raw("19話\nアクシズからの撤退")
            record[10:10 + len(title)] = title
            archive = pac(("milstP00.bin", bytes(record)))
            out = root / "mission_text.jsonl"
            summary_path = root / "summary.json"
            import speaker_map as SM  # noqa: E402

            original = SM.read_members
            SM.read_members = lambda path: [("config00.pac", archive)]
            try:
                code = MT.main(["--dir", str(drive), "--out", str(out), "--summary", str(summary_path)])
            finally:
                SM.read_members = original
            self.assertEqual(code, 0)
            self.assertTrue(out.exists())
            rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(rows[0]["kind"], "mission_title")
            self.assertEqual(rows[0]["slots"][0]["span"], 118)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["error_count"], 0)
            self.assertEqual(summary["per_kind"]["mission_title"]["filled_slots"], 1)


if __name__ == "__main__":
    unittest.main()
