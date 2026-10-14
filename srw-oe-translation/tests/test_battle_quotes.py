"""Synthetic tests for tools/battle_quotes.py (no game data).

The fixture rebuilds the measured framing: EVNT blocks with a self-counting size, a zero word, a
type-200 wrapper record and a nested type-201 quote record whose payload is six u16 words followed
by CP932 text (see the tool docstring).
"""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import battle_quotes as BQ  # noqa: E402


def quote_payload(key, text, anchor=0x0029, flags=1, extra=0xFFFF):
    words = struct.pack("<6H", anchor, key, flags, 0, 0, extra)
    return words + text.encode("cp932") + b"\x00"


def quote_record(key, text, **kw):
    payload = quote_payload(key, text, **kw)
    size = 8 + len(payload)
    return struct.pack("<2I", BQ.TYPE_QUOTE, size) + payload


def wrapper_record(inner):
    size = 8 + len(inner)
    return struct.pack("<2I", BQ.TYPE_WRAPPER, size) + inner


def evnt_block(records: bytes):
    payload = struct.pack("<I", 0) + records
    size = 4 + len(payload)
    return BQ.TAG + struct.pack("<I", size) + payload


class WalkMemberTest(unittest.TestCase):
    def test_single_block_single_quote(self):
        blob = evnt_block(wrapper_record(quote_record(50, "行くぞ")))
        result = BQ.walk_member(blob, "mesbtl00.cpk", "p0050.pac")
        self.assertEqual(result["blocks"], 1)
        self.assertEqual(len(result["quotes"]), 1)
        self.assertEqual(result["errors"], [])
        q = result["quotes"][0]
        self.assertEqual(q["key"], 50)
        self.assertEqual(q["text"], "行くぞ")
        self.assertEqual(q["flags"], 1)
        self.assertEqual(q["extra"], 0xFFFF)
        self.assertEqual(q["record_offset"], 20)          # tag(4) + size(4) + zero(4) + wrapper hdr(8)
        self.assertEqual(q["text_offset"], q["record_offset"] + 8 + BQ.QUOTE_HEADER)

    def test_two_blocks_chain(self):
        blob = (evnt_block(quote_record(50, "一")) + evnt_block(quote_record(60, "二")))
        result = BQ.walk_member(blob, "c", "p0050.pac")
        self.assertEqual(result["blocks"], 2)
        self.assertEqual([q["text"] for q in result["quotes"]], ["一", "二"])
        self.assertEqual(result["errors"], [])

    def test_flags_nibble_in_subtype(self):
        blob = evnt_block(quote_record(50, "三", anchor=0x8029))
        result = BQ.walk_member(blob, "c", "p0050.pac")
        self.assertEqual(len(result["quotes"]), 1)
        self.assertEqual(result["quotes"][0]["anchor"], 0x8029)

    def test_other_subtype_is_skipped_and_reported(self):
        blob = evnt_block(quote_record(50, "四", anchor=0x002A))
        result = BQ.walk_member(blob, "c", "p0050.pac")
        self.assertEqual(result["quotes"], [])
        self.assertEqual(len(result["errors"]), 1)

    def test_speaker_key_comes_from_the_record_not_the_member(self):
        blob = evnt_block(quote_record(60, "五"))
        result = BQ.walk_member(blob, "c", "p0050.pac")
        self.assertEqual(result["quotes"][0]["key"], 60)

    def test_truncated_block_is_reported(self):
        blob = evnt_block(quote_record(50, "六"))[:-4]
        result = BQ.walk_member(blob, "c", "p0050.pac")
        self.assertTrue(result["errors"])

    def test_empty_text_is_allowed(self):
        blob = evnt_block(quote_record(50, ""))
        result = BQ.walk_member(blob, "c", "p0050.pac")
        self.assertEqual(len(result["quotes"]), 1)
        self.assertEqual(result["quotes"][0]["text"], "")
        self.assertEqual(result["quotes"][0]["bytes"], 0)


class PayloadTest(unittest.TestCase):
    def test_rejects_short_payload(self):
        self.assertIsNone(BQ.payload_text(b"\x29\x00"))

    def test_rejects_private_use_text(self):
        payload = struct.pack("<6H", 0x29, 50, 1, 0, 0, 0xFFFF) + b"\x0f\xff\x00"
        self.assertIsNone(BQ.payload_text(payload))

    def test_keeps_newline(self):
        payload = struct.pack("<6H", 0x29, 50, 1, 0, 0, 0xFFFF) + "a\nb".encode("cp932") + b"\x00"
        self.assertEqual(BQ.payload_text(payload)["text"], "a\nb")


class SummariseTest(unittest.TestCase):
    def test_counts_keys_and_mismatches(self):
        rows = [
            {"container": "m00", "member": "p0050.pac", "member_key": 50, "key": 50, "bytes": 3},
            {"container": "m00", "member": "p0050.pac", "member_key": 50, "key": 60, "bytes": 4},
            {"container": "m01", "member": "p0051.pac", "member_key": 51, "key": 51, "bytes": 5},
        ]
        summary = BQ.summarise({"rows": rows, "errors": [], "members": 2, "blocks": 3,
                                "key_mismatch": 1})
        self.assertEqual(summary["quotes"], 3)
        self.assertEqual(summary["keys"], 3)
        self.assertEqual(summary["text_bytes"], 12)
        self.assertEqual(summary["quotes_per_container"], {"m00": 2, "m01": 1})
        self.assertEqual(summary["error_count"], 0)


if __name__ == "__main__":
    unittest.main()
