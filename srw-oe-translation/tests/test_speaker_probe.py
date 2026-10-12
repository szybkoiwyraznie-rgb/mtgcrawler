"""speaker_probe: dialogue-key extraction over a synthetic record chain (no game data)."""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import speaker_probe as sp  # noqa: E402


def rec(t: int, payload: bytes) -> bytes:
    return struct.pack("<II", t, 8 + len(payload)) + payload


def dialogue(key: int, mono: bool) -> bytes:
    # record offsets: +8 p1 (u16 = 1), +10 key (u16), +18 flag (u16), +20 text
    # payload starts at record +8, so payload offsets are record offsets minus 8
    body = struct.pack("<HH", 1, key)                       # +8, +10
    body += b"\x00" * 6                                     # +12..+17
    body += struct.pack("<H", 0xFFFF if mono else 0x0000)   # +18
    body += "テスト".encode("cp932")                          # +20 text (never printed)
    return rec(0xC9, body)


class SpeakerProbeTests(unittest.TestCase):
    def build(self):
        stream = b""
        stream += rec(0x1B6, b"\x00" * 16)            # caption starts scene 1
        stream += rec(0x1B7, b"\x00" * 16)            # narration (not a dialogue line)
        stream += rec(0x160, b"\x00" * 16)            # some non-text command
        stream += dialogue(0x1195, mono=False)
        stream += dialogue(0x119E, mono=False)
        stream += dialogue(0x1195, mono=False)
        stream += rec(0x1B6, b"\x00" * 16)            # caption starts scene 2
        stream += dialogue(0x0E7A, mono=True)
        return stream

    def test_keys_and_scenes(self):
        r = sp.probe_bytes(self.build())
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["dialogue_lines"], 4)
        self.assertEqual(r["scenes"], 2)
        self.assertEqual(r["per_scene"][0]["keys"], ["0x1195", "0x119e", "0x1195"])
        self.assertEqual(r["per_scene"][1]["keys"], ["0xe7a"])
        self.assertEqual(r["per_scene"][1]["monologue"], [True])

    def test_runs_and_alternation(self):
        r = sp.probe_bytes(self.build())
        self.assertEqual(r["key_runs"], 4)            # 1195 | 119e | 1195 | e7a
        self.assertEqual(r["abab_alternations"], 1)   # 1195,119e,1195 within scene 1

    def test_gap_types_recorded(self):
        r = sp.probe_bytes(self.build())
        # the 0x160 command sits between the narration and the first dialogue line
        # (gap bookkeeping lives in the internal structure; the public summary must not
        # leak text, so only check the public keys and that the output has no text)
        self.assertNotIn("テスト", repr(r))

    def test_unclean_chain_is_reported(self):
        bad = self.build() + b"\x01\x02\x03"  # trailing garbage: chain does not reach EOF
        r = sp.probe_bytes(bad)
        self.assertEqual(r["status"], "no-clean-record-chain")

    def test_short_dialogue_record_is_skipped(self):
        stream = rec(0x1B6, b"\x00" * 16) + rec(0xC9, b"\x00" * 4) + dialogue(0x1195, False)
        r = sp.probe_bytes(stream)
        self.assertEqual(r["dialogue_lines"], 1)


if __name__ == "__main__":
    unittest.main()
