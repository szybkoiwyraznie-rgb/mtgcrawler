"""Synthetic tests for tools/event_dialogue.py (no game data)."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import event_dialogue as ED  # noqa: E402
import evnt_walk as EW  # noqa: E402


def pad4(data: bytes) -> bytes:
    """Pad a record body to a 4-byte boundary - every measured record is aligned (never 0 bytes)."""
    return data + b"\x00" * ((-len(data)) % 4 or 4)


def dialogue_record(key, text, flags=1, extra=0xFFFF):
    payload = pad4(struct.pack("<6H", flags, key, 0, 0, 0, extra) + text.encode("cp932")
                   + b"\x00")
    return struct.pack("<2I", EW.TYPE_TEXT, 8 + len(payload)) + payload


def typed_record(rtype, body):
    body = pad4(body)
    return struct.pack("<2I", rtype, 8 + len(body)) + body


def wrapper(inner):
    return struct.pack("<2I", EW.TYPE_WRAPPER, 8 + len(inner)) + inner


def event_block(records: bytes, kind=1):
    """Measured event block layout: the chain sits behind the header and starts with the wrapper.

    The header grows with the block (index tables), so nothing may hard-code its length; the first
    record of the chain is the 0xC8 wrapper in every measured event block, which is how the reader
    finds the chain (see evnt_walk.find_chain).
    """
    header = struct.pack("<I", kind) + b"ECHK" + struct.pack("<I", 24)
    header += b"".join(struct.pack("<I", w) for w in (52, 101, 0, 1200, 1, 0))
    payload = header + wrapper(records)
    return EW.TAG + struct.pack("<I", len(payload)) + payload


def event_file(blocks: bytes):
    return EW.FILE_HEADER + struct.pack("<2I", len(blocks), blocks.count(EW.TAG)) + blocks


class ExtractMemberTest(unittest.TestCase):
    def make_member(self):
        story = event_block(wrapper(dialogue_record(4501, "了解！")
                                   + dialogue_record(4510, "次に『パーツ』の回収を行ないます。")))
        narration = event_block(typed_record(0x1B7, struct.pack("<I", 0) + "数日前…".encode("cp932")
                                             + b"\x00")
                                + typed_record(0x1B5, "「エグザート」の撃墜".encode("cp932") + b"\x00")
                                + typed_record(0x1B4, "敵ユニットの全滅".encode("cp932") + b"\x00"))
        # a table block: no record chain, but a display string inside
        table = event_block(struct.pack("<4I", 1, 0, 2, 0)
                            + "＃擱座した自衛隊レイバー（ＨＡＬ－Ｘ１０）".encode("cp932") + b"\x00")
        return event_file(story + narration + table)

    def test_dialogue_records_keep_key_and_text_offset(self):
        result = ED.extract_member(self.make_member(), "eventP00.cpk", "DL100_01.bin")
        self.assertEqual([r["key"] for r in result["dialogue"]], [4501, 4510])
        self.assertEqual(result["dialogue"][0]["text"], "了解！")
        self.assertEqual(result["dialogue"][0]["text_offset"],
                         result["dialogue"][0]["record_offset"] + 8 + EW.TEXT_HEADER)
        self.assertEqual(result["dialogue"][0]["flags"], 1)
        self.assertEqual(result["errors"], [])

    def test_other_types_get_a_kind_and_a_measured_offset(self):
        result = ED.extract_member(self.make_member(), "eventP00.cpk", "DL100_01.bin")
        kinds = {r["kind"]: r for r in result["other"]}
        self.assertEqual(sorted(kinds), ["condition_defeat", "condition_victory", "narration"])
        self.assertEqual(kinds["narration"]["text"], "数日前…")
        self.assertEqual(kinds["condition_defeat"]["text"], "「エグザート」の撃墜")
        for row in result["other"]:
            self.assertNotIn(row["kind"], ("dialogue", "embedded"))

    def test_table_block_text_is_reported_as_embedded(self):
        result = ED.extract_member(self.make_member(), "eventP00.cpk", "DL100_01.bin")
        self.assertEqual(len(result["embedded"]), 1)
        embedded = result["embedded"][0]
        self.assertTrue(embedded["text"].startswith("＃擱座した"))
        self.assertEqual(result["table_blocks"], 1)
        self.assertEqual(result["chain_blocks"], 2)
        self.assertEqual(result["blocks"], 3)

    def test_container_types_are_not_scanned_for_their_own_text(self):
        section = event_block(typed_record(0x0, b"\x01\x00\x00\x00" * 8
                                           + "司令部".encode("cp932") + b"\x00")
                              + wrapper(dialogue_record(50, "「行くぞ！」")))
        result = ED.extract_member(event_file(section), "eventP00.cpk", "DL100_02.bin")
        self.assertEqual([r["text"] for r in result["dialogue"]], ["「行くぞ！」"])
        self.assertEqual(result["other"], [])
        self.assertEqual(result["embedded"], [])

    def test_narration_inside_a_wrapper_is_reported_too(self):
        # measured on eventP00.cpk/DL100_01.bin: the scene prose sits inside the same 0xC8 wrapper
        # as the dialogue, and used to be dropped here (44 narration records of eventP00 alone)
        wrapped_narration = typed_record(0x1B7, struct.pack("<I", 0) + "数日前…".encode("cp932")
                                         + b"\x00")
        section = event_block(wrapper(dialogue_record(4501, "了解！") + wrapped_narration))
        result = ED.extract_member(event_file(section), "eventP00.cpk", "DL100_01.bin")
        self.assertEqual([r["kind"] for r in result["other"]], ["narration"])
        self.assertEqual(result["other"][0]["text"], "数日前…")
        self.assertEqual(result["other"][0]["record_type"], 0x1B7)
        self.assertEqual(result["other"][0]["text_offset"],
                         result["other"][0]["record_offset"] + 8 + 4)
        self.assertEqual([r["text"] for r in result["dialogue"]], ["了解！"])

    def test_an_already_translated_narration_line_is_still_reported(self):
        # our English has no Japanese characters, so a scan for Japanese runs goes blind on it
        english = "Decades have passed since the Earth Federation was founded."
        section = event_block(typed_record(0x1B7, struct.pack("<I", 0) + english.encode("cp932")
                                           + b"\x00"))
        result = ED.extract_member(event_file(section), "c", "m")
        self.assertEqual([r["text"] for r in result["other"]], [english])
        self.assertEqual(result["other"][0]["text_offset"], result["other"][0]["record_offset"] + 12)

    def test_a_wrapper_text_is_not_reported_twice(self):
        section = event_block(wrapper(typed_record(0x1B7, struct.pack("<I", 1) + "数日前…".encode("cp932")
                                                   + b"\x00")))
        result = ED.extract_member(event_file(section), "c", "m")
        self.assertEqual(len(result["other"]), 1)
        self.assertEqual(result["embedded"], [])

    def test_unreadable_dialogue_record_is_counted_not_hidden(self):
        broken = event_block(wrapper(struct.pack("<2I", EW.TYPE_TEXT, 12) + b"\xff\xff\xff\xff"))
        result = ED.extract_member(event_file(broken), "c", "m")
        self.assertEqual(result["dialogue"], [])
        self.assertEqual(result["unreadable_dialogue"], 1)


class CleanRunsTest(unittest.TestCase):
    def test_short_runs_and_ascii_only_runs_are_skipped(self):
        payload = b"abc\x00" + "あ".encode("cp932") + b"\x00"
        self.assertEqual(ED.clean_runs(payload), [])

    def test_two_japanese_characters_are_enough(self):
        payload = "全滅".encode("cp932") + b"\x00"
        self.assertEqual(ED.clean_runs(payload)[0][1], "全滅")

    def test_private_use_is_rejected(self):
        payload = ("全滅".encode("cp932") + b"\x0f\xff" + b"\x00")
        self.assertEqual(ED.clean_runs(payload), [])

    def test_limit_caps_the_number_of_runs(self):
        payload = b"\x00".join(x.encode("cp932") for x in ("全滅", "撃墜", "勝利")) + b"\x00"
        self.assertEqual(len(ED.clean_runs(payload, limit=2)), 2)


class SummaryTest(unittest.TestCase):
    def test_summary_counts_kinds_and_bytes(self):
        member = ExtractMemberTest().make_member()
        result = ED.extract_member(member, "eventP00.cpk", "DL100_01.bin")
        scan = {"dialogue": result["dialogue"], "other": result["other"],
                "embedded": result["embedded"], "errors": [], "members": 1,
                "blocks": result["blocks"], "chain_blocks": result["chain_blocks"],
                "table_blocks": result["table_blocks"],
                "unreadable_dialogue": result["unreadable_dialogue"]}
        summary = ED.summarise(scan)
        self.assertEqual(summary["dialogue_lines"], 2)
        self.assertEqual(summary["dialogue_keys"], 2)
        self.assertEqual(summary["other_by_kind"]["narration"], 1)
        self.assertEqual(summary["embedded_texts"], 1)
        self.assertEqual(summary["error_count"], 0)
        self.assertGreater(summary["dialogue_text_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
