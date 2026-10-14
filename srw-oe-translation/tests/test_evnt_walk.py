"""Synthetic tests for tools/evnt_walk.py - both measured block variants (no game data)."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import evnt_walk as EW  # noqa: E402


def pad4(data: bytes) -> bytes:
    """Pad a record body to a 4-byte boundary - every measured record is aligned (never 0 bytes)."""
    return data + b"\x00" * ((-len(data)) % 4 or 4)


def text_payload(key, text, flags=1, anchor=0x0029, extra=0xFFFF):
    words = struct.pack("<6H", anchor, key, flags, 0, 0, extra)
    return words + pad4(text.encode("cp932") + b"\x00")


def text_record(key, text, **kw):
    payload = text_payload(key, text, **kw)
    return struct.pack("<2I", EW.TYPE_TEXT, 8 + len(payload)) + payload


def wrapper_record(inner):
    return struct.pack("<2I", EW.TYPE_WRAPPER, 8 + len(inner)) + inner


def mesbtl_block(records: bytes):
    """Measured mesbtl block: zero word, then records; size counted from the size field."""
    payload = struct.pack("<I", 0) + records
    return EW.TAG + struct.pack("<I", 4 + len(payload)) + payload


def event_block(records: bytes, kind=1, extra_words=(52, 101, 0, 1200, 1, 0)):
    """Measured event block: u32 kind, 'ECHK' chunk + header words, then the wrapped chain.

    The header grows with the block (index tables), so the chain is found by scanning, and its
    first record is always the 0xC8 wrapper -- measured on every event block of the 31 containers.
    """
    header = struct.pack("<I", kind) + b"ECHK" + struct.pack("<I", 24)
    header += b"".join(struct.pack("<I", w) for w in extra_words)
    payload = header + wrapper_record(records)
    return EW.TAG + struct.pack("<I", len(payload)) + payload


def event_file(blocks: bytes):
    return EW.FILE_HEADER + struct.pack("<2I", len(blocks), blocks.count(EW.TAG)) + blocks


class MesbtlVariantTest(unittest.TestCase):
    def test_block_end_counts_from_the_size_field(self):
        blob = mesbtl_block(wrapper_record(text_record(50, "行くぞ")))
        blocks, errors = EW.blocks(blob)
        self.assertEqual(errors, [])
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["variant"], "mesbtl")
        self.assertEqual(blocks[0]["end"], len(blob))

    def test_chain_skips_the_zero_word(self):
        blob = mesbtl_block(wrapper_record(text_record(50, "行くぞ")))
        blocks, _ = EW.blocks(blob)
        self.assertEqual(blocks[0]["chain_start"], 12)          # tag(4) + size(4) + zero word(4)
        chain = EW.walk_chain(blob, 12, len(blob))
        self.assertEqual([t for _o, t, _s in chain], [EW.TYPE_WRAPPER])
        self.assertEqual(chain[0][2], len(blob) - 12)

    def test_text_record_found_through_the_wrapper(self):
        blob = mesbtl_block(wrapper_record(text_record(50, "行くぞ")))
        result = EW.text_records(blob, "m", "p0050.pac", anchor=EW.ANCHOR_EXPECTED)
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["key"], 50)
        self.assertEqual(result["records"][0]["text"], "行くぞ")
        self.assertEqual(result["errors"], [])

    def test_anchor_filter_drops_story_dialogue_records(self):
        blob = mesbtl_block(wrapper_record(text_record(50, "行くぞ", anchor=0x0001)))
        result = EW.text_records(blob, "m", "p0050.pac", anchor=EW.ANCHOR_EXPECTED)
        self.assertEqual(result["records"], [])
        self.assertEqual(len(result["errors"]), 1)

    def test_flag_nibble_is_masked(self):
        parsed = EW.payload_text(text_payload(60, "x", anchor=0x8029), EW.ANCHOR_EXPECTED)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["anchor"], 0x8029)
        self.assertEqual(parsed["key"], 60)


class EventVariantTest(unittest.TestCase):
    def test_file_header_is_reported(self):
        blob = event_file(event_block(text_record(4501, "了解！", anchor=1)))
        header = EW.file_header(blob)
        self.assertIsNotNone(header)
        self.assertEqual(header["start"], 12)
        self.assertEqual(header["blocks"], 1)

    def test_block_end_counts_from_the_tag(self):
        blob = event_file(event_block(text_record(4501, "了解！", anchor=1)))
        blocks, errors = EW.blocks(blob)
        self.assertEqual(errors, [])
        self.assertEqual(blocks[0]["variant"], "event")
        self.assertEqual(blocks[0]["end"], len(blob))

    def test_chain_is_found_after_the_header_words(self):
        blob = event_file(event_block(text_record(4501, "了解！", anchor=1)))
        result = EW.text_records(blob, "c", "DL100_01.bin")
        self.assertEqual(result["header"]["blocks"], 1)
        self.assertEqual(result["chain_blocks"], 1)
        self.assertEqual(len(result["records"]), 1)
        record = result["records"][0]
        self.assertEqual(record["key"], 4501)
        self.assertEqual(record["text"], "了解！")
        self.assertEqual(record["header"][0], 1)          # the flag word, not the quote anchor

    def test_two_blocks_chain(self):
        blob = event_file(event_block(text_record(4501, "一", anchor=1))
                          + event_block(text_record(4510, "二", anchor=9)))
        result = EW.text_records(blob, "c", "DL100_02.bin")
        self.assertEqual([r["text"] for r in result["records"]], ["一", "二"])
        self.assertEqual(result["errors"], [])

    def test_carriage_return_is_kept(self):
        blob = event_file(event_block(text_record(4501, "ＥＮ補充、完了！\r", anchor=1)))
        result = EW.text_records(blob, "c", "DL100_01.bin")
        self.assertEqual(result["records"][0]["text"], "ＥＮ補充、完了！\r")

    def test_types_histogram_covers_every_chain_record(self):
        """Every record counts, the wrapper included: its size field has to grow with the text."""
        other = struct.pack("<2I", 0x12D, 8)
        blob = event_file(event_block(text_record(4501, "一", anchor=1) + other))
        result = EW.text_records(blob, "c", "DL100_01.bin")
        self.assertEqual(result["types"], {EW.TYPE_WRAPPER: 1, EW.TYPE_TEXT: 1, 0x12D: 1})


class FramingErrorTest(unittest.TestCase):
    def test_block_that_lands_nowhere_is_reported(self):
        blob = EW.TAG + struct.pack("<I", 999) + struct.pack("<I", 0) + b"x" * 32
        blocks, errors = EW.blocks(blob)
        self.assertEqual(len(errors), 2)           # the size mismatch and the missing chain
        self.assertIn("next EVNT tag", errors[0])
        self.assertTrue(blocks)                    # the block is still reported, with the error

    def test_chain_that_does_not_land_on_the_block_end_is_reported(self):
        records = text_record(50, "x")
        payload = struct.pack("<I", 0) + records + b"\x00" * 8      # trailing junk breaks the chain
        blob = EW.TAG + struct.pack("<I", 4 + len(payload)) + payload
        result = EW.text_records(blob, "c", "m")
        self.assertEqual(result["blocks"], 1)
        self.assertEqual(result["chain_blocks"], 0)
        self.assertTrue(result["errors"])

    def test_no_evnt_tag_yields_nothing(self):
        blocks, errors = EW.blocks(b"not an evnt member")
        self.assertEqual(blocks, [])
        self.assertEqual(errors, [])

    def test_walk_chain_rejects_escapes(self):
        blob = struct.pack("<2I", 1, 8 + 32)[:8] + struct.pack("<I", 2) + struct.pack("<I", 9999)
        self.assertEqual(EW.walk_chain(blob, 0, len(blob)), [])


class CleanTest(unittest.TestCase):
    def test_private_use_is_rejected(self):
        self.assertFalse(EW.is_clean("a\ue000b"))
        self.assertIsNone(EW.payload_text(text_payload(1, "\ue000"), EW.ANCHOR_EXPECTED))

    def test_control_characters_are_rejected(self):
        self.assertFalse(EW.is_clean("a\x07b"))
        self.assertTrue(EW.is_clean("a\tb\r\nc"))

    def test_short_payload_is_rejected(self):
        self.assertIsNone(EW.payload_text(b"\x29\x00"))


if __name__ == "__main__":
    unittest.main()
