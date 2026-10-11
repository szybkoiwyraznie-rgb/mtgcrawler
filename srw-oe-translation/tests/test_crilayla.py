"""Round-trip tests for the CRILAYLA compressor used to rewrite CPK members."""
from __future__ import annotations

import random
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import crilayla  # noqa: E402


def _evnt_like() -> bytes:
    random.seed(7)
    buf = bytearray()
    for i in range(400):
        buf += struct.pack("<IIII", 0x16B, 0x177, i, 0)
        buf += "地球統一政府である地球連邦の樹立から数十年。".encode("cp932")
        buf += bytes(random.randrange(256) for _ in range(8))
    return bytes(buf) + bytes(0x100)


class CrilaylaCompressTests(unittest.TestCase):
    def _roundtrip(self, data: bytes) -> bytes:
        comp = crilayla.compress(data)
        return crilayla.decompress(comp).data

    def test_repetitive_round_trips_and_shrinks(self):
        data = (b"HELLO WORLD " * 600) + bytes(0x100)
        comp = crilayla.compress(data)
        self.assertEqual(crilayla.decompress(comp).data, data)
        self.assertLess(len(comp), len(data))

    def test_evnt_like_round_trips_and_shrinks(self):
        data = _evnt_like()
        comp = crilayla.compress(data)
        self.assertEqual(crilayla.decompress(comp).data, data)
        self.assertLess(len(comp), len(data))

    def test_random_round_trips(self):
        random.seed(1)
        data = bytes(random.randrange(256) for _ in range(5000)) + bytes(0x100)
        self.assertEqual(self._roundtrip(data), data)

    def test_zeros_round_trips(self):
        data = b"\x00" * 13000 + bytes(0x100)
        self.assertEqual(self._roundtrip(data), data)


if __name__ == "__main__":
    unittest.main()
