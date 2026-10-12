"""Synthetic tests for tools/event_text_apply.py (no game data).

The fixture builds a member with the same framing as the real event files, measured on them:

    "EDAT" size (= len - 8) section_count
    section x { "EVNT" size  body }
    body    = u32 1 "ECHK" u32 24 u32 52 u32 101 u32 0  chain
    chain   = { C8 size  inner-chain }
    inner   = { C9 size  six u16 words  text  NUL-padding }+
"""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import event_text_apply as A  # noqa: E402

WRAPPER = 0xC8
TEXT = 0xC9


def dialogue_record(speaker: int, text: bytes) -> bytes:
    size = A.padded_size(len(text))
    header = struct.pack("<6H", 1, speaker, 0, 0, 0, 0xFFFF)
    return (struct.pack("<II", TEXT, size) + header + text
            + b"\x00" * (size - A.TEXT_OFFSET_IN_RECORD - len(text)))


# the header of a real text block, measured: u32 1, "ECHK", then two triples of words
HEADER = (struct.pack("<I", 1) + b"ECHK" + struct.pack("<III", 24, 52, 101)
          + struct.pack("<I", 0) + struct.pack("<III", 1200, 1, 0))


def member(texts, speakers=None, table_text: bytes = None) -> tuple:
    """A member with one EVNT section holding one C8 wrapper of dialogue records.

    ``table_text`` adds a second section that is a parameter table (no record chain) holding a raw
    text run - the shape the "embedded" rows of the package come from.

    Returns (blob, [text offsets], table offset or None).
    """
    speakers = speakers or [4501] * len(texts)
    inner = b"".join(dialogue_record(sp, text) for sp, text in zip(speakers, texts))
    wrapper = struct.pack("<II", WRAPPER, len(inner) + 8) + inner
    body = HEADER + wrapper
    sections = b"EVNT" + struct.pack("<I", len(body)) + body
    table_offset = None
    if table_text is not None:
        table_body = (struct.pack("<I", 1) + b"ECHK" + struct.pack("<II", 84, 55)
                      + struct.pack("<I", len(table_text)) + table_text)
        sections += b"EVNT" + struct.pack("<I", len(table_body)) + table_body
    blob = b"EDAT" + struct.pack("<II", len(sections), 2 if table_text is not None else 1) + sections
    records, _ = A.parse_block_records(blob)
    offsets = [record["offset"] + A.TEXT_OFFSET_IN_RECORD
               for record in sorted(records, key=lambda r: r["offset"]) if record["type"] == TEXT]
    if table_text is not None:
        table_offset = blob.find(table_text)
    return blob, offsets, table_offset


def row(ident, offset, jp, en, member_name="DL100_01.bin", container="eventP00.cpk",
        kind="dialogue"):
    return {"id": ident, "category": "dialogue", "part": "dialogue", "jp": jp, "en": en,
            "kind": kind, "source": {"container": container, "member": member_name,
                                     "offset": offset}}


class FormatTest(unittest.TestCase):
    def test_padding_matches_the_measured_rule(self):
        # every record is 4-byte aligned and keeps 1..4 NUL bytes after the text
        for length, expected in ((65, 88), (61, 84), (64, 88), (62, 84), (63, 84), (60, 84)):
            size = A.padded_size(length)
            self.assertEqual(size, expected)
            self.assertEqual(size % 4, 0)
            self.assertGreaterEqual(size - A.TEXT_OFFSET_IN_RECORD - length, 1)

    def test_fixture_parses_like_a_real_member(self):
        import evnt_walk as EW
        blob, offsets, _ = member(["あいうえお".encode("cp932")])
        blocks, errors = EW.blocks(blob)
        self.assertEqual(errors, [])
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["chain_start"], 12 + 8 + len(HEADER))     # EVNT + header
        self.assertEqual(offsets[0], 12 + 8 + len(HEADER) + 8 + A.TEXT_OFFSET_IN_RECORD)


class GrowTest(unittest.TestCase):
    def setUp(self):
        self.jp = "（俺は今、宇宙貿易事業を推進する\n　民間組織『コネクト』にいる…）"
        self.blob, self.offsets, self.table = member(
            [self.jp.encode("cp932"), "了解！".encode("cp932"), "感度良好だ！".encode("cp932"),
             "ミッションをはじめよう。".encode("cp932"), "射出機、接続完了！".encode("cp932")],
            speakers=[4501] * 5, table_text="補給物資を取得".encode("cp932"))
        self.first = self.offsets[0]

    def test_a_row_lands_on_its_record(self):
        record = A.find_record(self.blob, self.first, self.jp.encode("cp932"))
        self.assertIsNotNone(record)
        self.assertEqual(record["type"], TEXT)
        self.assertEqual(A.find_record(self.blob, self.first + 1, self.jp.encode("cp932")), None)

    def test_writing_the_same_text_changes_nothing(self):
        record = A.find_record(self.blob, self.first, self.jp.encode("cp932"))
        self.assertEqual(A.grow_text(self.blob, record, self.jp.encode("cp932")), self.blob)

    def test_a_longer_text_grows_the_record_and_every_size_around_it(self):
        new = ("(I am here at Connect, a civilian organization\n"
               " promoting interstellar trade...)").encode("cp932")
        report = {}
        out, report = A.apply_member(self.blob, [row("dlg:x:1", self.first, self.jp, new.decode())])
        self.assertEqual((report["applied"], report["refused"], report["skipped"]), (1, [], []))
        self.assertEqual(report["problems"], [])
        self.assertGreater(len(out), len(self.blob))
        # the sizes that make the file walkable all moved by the same delta
        delta = len(out) - len(self.blob)
        self.assertEqual(struct.unpack_from("<I", out, 4)[0],
                         struct.unpack_from("<I", self.blob, 4)[0] + delta)      # EDAT header
        self.assertEqual(struct.unpack_from("<I", out, 12 + 4)[0],
                         struct.unpack_from("<I", self.blob, 12 + 4)[0] + delta)  # EVNT section
        wrappers = [r for r in A.parse_block_records(self.blob)[0] if r["type"] == WRAPPER]
        self.assertEqual(len(wrappers), 1)
        at = wrappers[0]["offset"] + 4
        self.assertEqual(struct.unpack_from("<I", out, at)[0],
                         struct.unpack_from("<I", self.blob, at)[0] + delta)      # wrapper record
        record = A.find_record(out, self.first, new)
        self.assertIsNotNone(record)

    def test_growing_and_shrinking_back_reproduces_the_original_byte_for_byte(self):
        new = ("(I am here at Connect, a civilian organization promoting interstellar "
               "trade...)").encode("cp932")
        grown, report = A.apply_member(self.blob, [row("dlg:x:1", self.first, self.jp, new.decode())])
        self.assertEqual(report["problems"], [])
        shrunk, report2 = A.apply_member(grown, [row("dlg:x:1", self.first, new.decode(), self.jp)])
        self.assertEqual(report2["problems"], [])
        self.assertEqual(shrunk, self.blob)

    def test_a_row_whose_text_is_not_where_the_package_says_is_skipped(self):
        out, report = A.apply_member(self.blob, [row("dlg:x:1", self.first + 2, self.jp, "Hi!")])
        self.assertEqual(out, self.blob)
        self.assertEqual(report["applied"], 0)
        self.assertIn("not at", report["skipped"][0])

    def test_a_line_wider_than_the_box_is_refused(self):
        wide = "x" * 60
        out, report = A.apply_member(self.blob, [row("dlg:x:1", self.first, self.jp, wide)])
        self.assertEqual(out, self.blob)
        self.assertEqual(report["applied"], 0)
        self.assertIn("the box fits 46", report["refused"][0])

    def test_the_record_decides_not_the_kind_label(self):
        # the label is only metadata: what matters is that a dialogue record holds the text
        out, report = A.apply_member(
            self.blob, [row("dlg:x:1", self.first, self.jp, "Check!", kind="narration")])
        self.assertEqual(report["applied"], 1)
        self.assertEqual(report["problems"], [])

    def test_a_text_that_is_not_in_a_dialogue_record_is_reported(self):
        table_text = "補給物資を取得"
        out, report = A.apply_member(
            self.blob, [row("dlg:x:2", self.table, table_text, "Obtained supplies",
                            kind="embedded")])
        self.assertEqual(out, self.blob)
        self.assertEqual(report["applied"], 0)
        self.assertEqual(report["skipped"], ["dlg:x:2: kind embedded is not a dialogue record "
                                             "(its own writer is still to come)"])

    def test_two_rows_are_applied_from_the_end_so_offsets_hold(self):
        rows = [row("dlg:x:1", self.offsets[0], self.jp, "First line!"),
                row("dlg:x:2", self.offsets[1], "了解！", "Roger!")]
        out, report = A.apply_member(self.blob, rows)
        self.assertEqual(report["applied"], 2)
        self.assertEqual(report["problems"], [])
        import event_dialogue
        texts = [item["text"] for item in event_dialogue.extract_member(out)["dialogue"]]
        self.assertEqual(texts[0], "First line!")
        self.assertEqual(texts[1], "Roger!")
        self.assertEqual(len(texts), 5)

    def test_verify_notices_a_lossy_change(self):
        self.assertTrue(A.verify(self.blob, self.blob[:-4], []))

    def test_the_report_carries_the_verification_of_the_result(self):
        out, report = A.apply_member(self.blob, [row("dlg:x:1", self.first, self.jp, "Short!")])
        self.assertEqual(report["applied"], 1)
        self.assertEqual(report["problems"], [])


class RowsTest(unittest.TestCase):
    def test_rows_for_member_filters_by_member_and_english(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            rows = [row("a", 10, "jp", "en"), row("b", 20, "jp", ""),
                    row("c", 30, "jp", "en", member_name="DL200_01.bin")]
            (package / "00_dialogue.jsonl").write_text(
                "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
            found = A.rows_for_member(package, "eventP00.cpk", "DL100_01.bin")
            self.assertEqual([r["id"] for r in found], ["a"])


if __name__ == "__main__":
    unittest.main()
