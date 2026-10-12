"""Synthetic tests for tools/battle_members.py and the token-aware decoder in tools/name_union.py.

No game data is used: every byte string below is built in the test.
"""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import battle_members as BM  # noqa: E402
import name_union as NU  # noqa: E402


def quote_record(key: int, flags: int = 0) -> bytes:
    # u32 0x0000 | u16 type (0x0029 | flags) | u16 key | u16 0x0001 | u16 0 | text bytes
    return (struct.pack("<HH", 0, 0x0029 | (flags << 12)) + struct.pack("<H", key)
            + struct.pack("<HH", 1, 0) + b"\x82\xa0\x00")  # 'あ' + NUL, synthetic


class BattleMembersTests(unittest.TestCase):
    def test_anchor_requires_type_field(self):
        key = 0x1144
        blob = quote_record(key) + struct.pack("<HH", 0, 0x0100) + struct.pack("<H", key) + b"\x00" * 8
        anchors = BM.record_anchors(blob, key)
        self.assertEqual(len(anchors), 1, "only the record with type 0x0029 counts")

    def test_flags_in_top_nibble_are_accepted(self):
        key = 0x0ABC
        blob = quote_record(key, flags=0x8) + b"\x00" * 8
        self.assertEqual(len(BM.record_anchors(blob, key)), 1)

    def test_key_must_be_aligned(self):
        key = 0x1144
        blob = b"\x00" + quote_record(key)  # shifts the key to an odd offset
        self.assertEqual(BM.record_anchors(blob, key), [])


class TokenDecodeTests(unittest.TestCase):
    def _slot(self, body: bytes) -> bytes:
        return body + b"\x00" * (16 - len(body))

    def test_token_kept_as_placeholder(self):
        blob = b"\x00" * 4 + self._slot(b"\x0f\x26" + "オン兵".encode("cp932"))
        self.assertEqual(NU.raw_decode_slot(blob, 4), "{0F 26}オン兵")

    def test_halfwidth_katakana_does_not_swallow_token(self):
        # 0xD7 is a single-byte half-width katakana; the following 0x0F must still start a token.
        blob = self._slot(b"\x0f\x22\xd7\x0f\x2e\xbd")
        self.assertEqual(NU.raw_decode_slot(blob, 0), "{0F 22}ラ{0F 2E}ス")

    def test_strict_filter(self):
        self.assertTrue(NU.is_name("オン兵", marker=False))
        self.assertFalse(NU.is_name("\x01", marker=False))
        self.assertFalse(NU.is_name("e", marker=False))
        self.assertTrue(NU.is_name("e", marker=True))


if __name__ == "__main__":
    unittest.main()
